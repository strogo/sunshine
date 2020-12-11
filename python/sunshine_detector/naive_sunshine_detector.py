from typing import Tuple, Callable, Optional
import logging
import math
from datetime import datetime, timedelta, date
import georasters as gr
import ephem
from functools import lru_cache
from pyproj import CRS, Transformer
from . import SunshineDetector, compute_proj_transform, get_projection_rotation

logging.basicConfig(level="DEBUG")
log = logging.getLogger(__file__)

HORIZON_METERS = 10000
THIS_YEAR = datetime(datetime.today().year, 1, 1)
NEXT_YEAR = datetime(datetime.today().year + 1, 1, 1)


class NaiveSunshineDetector:
    def __init__(self, path: str) -> None:
        # SunshineDetector.__init__(self)
        self.dem_data = gr.load_tiff(path)
        NDV, xsize, ysize, GeoT, Projection, DataType = gr.get_geo_info(path)
        self.x_size = xsize
        self.y_size = ysize
        self.geo_t = GeoT
        self.cell_x, self.cell_y, self.x_min, self.y_max = (GeoT[1], GeoT[-1], GeoT[0], GeoT[3])
        self.proj_transform, self.proj_transform_inverse = compute_proj_transform(str(Projection))
        self.projection_offset = get_projection_rotation(
            self.x_min, self.y_max, 50, self.proj_transform, self.proj_transform_inverse
        )[3]
        self.max_elevation = self.dem_data.max()

    # @lru_cache(maxsize=10000)
    def get_elevation(self, lng: float, lat: float) -> Optional[int]:
        col, row = gr.map_pixel(lng, lat, self.geo_t[1], self.geo_t[-1], self.geo_t[0], self.geo_t[3])
        if col < 0 or row >= self.x_size or row < 0 or col >= self.y_size:
            # log.debug(f"({lng}, {lat}) is ({col}, {row}) miss")
            return None
        return self.dem_data[col, row]

    @lru_cache(maxsize=None)
    def get_sun_position_base(self, ts: datetime) -> Tuple[float, float]:
        """
        Get suns position for the beginning of the map at a given time. This one is done for speed reasons
        Also, azimuth is in local projection (related to lat-1 )
        """
        log.info(f"Asking for sun position for {ts}")
        point = ephem.Observer()
        (x, y) = self.proj_transform.transform(self.y_max, self.x_min)
        point.lon = str(x)
        point.lat = str(y)
        point.elevation = 0
        point.date = ts
        sun = ephem.Sun(point)
        azimuth = sun.az + self.projection_offset
        xyz_vector = (math.sin(azimuth), math.cos(azimuth), math.sin(sun.alt))
        log.info(xyz_vector)
        return xyz_vector

    def get_sunrise_sunset_ts(self, lng: float, lat: float, ts: datetime) -> bool:
        point = ephem.Observer()
        (x, y) = self.proj_transform.transform(lat, lng)
        point.lon = str(x)
        point.lat = str(y)
        point.date = ts
        point.elevation = self.get_elevation(lng, lat) or 0
        sun = ephem.Sun(point)
        sunset_ts = point.next_setting(sun).datetime() + timedelta(minutes=-3)  # just to make sure sun is still visible
        sunrise_ts = point.next_rising(sun).datetime() + timedelta(minutes=3)  # just to make sure sun is still visible
        # log.info(f"sunset time is {sunset_ts}")
        return sunrise_ts, sunset_ts

    @lru_cache(maxsize=None)
    def get_sunrise_sunset_base(self, ts: datetime) -> bool:
        lat = self.y_max
        lng = self.x_min
        return self.get_sunrise_sunset_ts(lng, lat, ts)

    def get_sun_position(self, lng: float, lat: float, ts: datetime) -> Tuple[float, float]:
        """
        Get suns position (azimuth and degree) at a given time. lng, lat are the coordinates of the local projection.
        Also, azimuth is in local projection (related to lat-1 )
        """
        real_ts = ts.replace(microsecond=0)
        # log.info(f"Asking for sun position for {real_ts}")
        return self.get_sun_position_base(real_ts)

        """
        point = ephem.Observer()
        (x, y) = self.proj_transform.transform(lat, lng)
        point.lon = str(x)
        point.lat = str(y)
        point.elevation = self.get_elevation(lng, lat) or 0
        point.date = ts
        sun = ephem.Sun(point)
        azimuth = sun.az + self.projection_offset
        xyz_vector = (math.sin(azimuth), math.cos(azimuth), math.sin(sun.alt))
        return xyz_vector
        """

    # @lru_cache(maxsize=10000)
    def is_sunny(self, lng: float, lat: float, ts: datetime) -> bool:
        xyz_vector = self.get_sun_position(lng, lat, ts)
        if xyz_vector[2] < 0:
            return False
        base_elevation = self.get_elevation(lng, lat) or 0
        if base_elevation == 0:
            return False
        for step in range(0, HORIZON_METERS, int(self.cell_x)):
            x = int(lng + xyz_vector[0] * step)
            y = int(lat + xyz_vector[1] * step)
            elevation = self.get_elevation(x, y)
            if elevation is None:  # we have left the boundaries
                return True
            max_allowed_elevation = base_elevation + xyz_vector[2] * step
            if elevation > max_allowed_elevation:
                return False
            if max_allowed_elevation > self.max_elevation:
                return True
        return True

    def is_sunset_visible(self, lng: float, lat: float, ts: datetime) -> bool:
        sunset_ts = self.get_sunrise_sunset_base(ts)[1]
        # log.info(f"sunset time of {ts} is {sunset_ts}")
        return self.is_sunny(int(lng), int(lat), sunset_ts)

    def is_sunrise_visible(self, lng: float, lat: float, ts: datetime) -> bool:
        sunrise_ts = self.get_sunrise_sunset_base(ts)[0]
        return self.is_sunny(int(lng), int(lat), sunrise_ts)

    def get_num_sunsets(self, lng: float, lat: float, from_ts: datetime, to_ts: datetime) -> int:
        count: int = 0
        ts = from_ts
        while ts < to_ts:
            # log.info(ts)
            if self.is_sunset_visible(lng, lat, ts):
                count += 1
            ts += timedelta(days=1)
        return count

    def get_sunny_hours(self, lng: float, lat: float, from_ts: datetime, to_ts: datetime) -> int:
        count: int = 0
        ts = from_ts
        while ts < to_ts:
            if self.is_sunny(int(lng), int(lat), ts):
                count += 1
            ts += timedelta(hours=1)
        return count

    def get_annual_sunny_hours(self, lng: float, lat: float) -> int:
        base_elevation = self.get_elevation(lng, lat) or 0
        if base_elevation == 0:
            return 0
        return self.get_sunny_hours(lng, lat, THIS_YEAR, NEXT_YEAR)

    def get_annual_sunsets(self, lng: float, lat: float) -> int:
        base_elevation = self.get_elevation(lng, lat) or 0
        if base_elevation == 0:
            return 0
        return self.get_num_sunsets(lng, lat, THIS_YEAR, NEXT_YEAR)

    def get_sunsets(self, day: datetime, lng: float, lat: float) -> int:
        base_elevation = self.get_elevation(lng, lat) or 0
        if base_elevation == 0:
            return 0
        return self.get_num_sunsets(lng, lat, day, day + timedelta(days=1))

    def get_todays_sunsets(self, lng: float, lat: float) -> int:
        base_elevation = self.get_elevation(lng, lat) or 0
        if base_elevation == 0:
            return 0
        today = datetime.combine(date.today(), datetime.min.time())
        return self.get_num_sunsets(lng, lat, today, today + timedelta(days=1))