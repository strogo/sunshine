from abc import ABC, ABCMeta, abstractmethod
import math
from datetime import datetime
from georasters import georasters, GeoRaster
from pyproj import CRS, Transformer

DEFAULT_PROJECTION_EPSG = 4326


class SunshineDetector(ABCMeta):
    def __init__(self):
        self.raster: GeoRaster = None

    @abstractmethod
    def is_sunny(self, lng: float, lat: float, ts: datetime) -> bool:
        return False


def compute_proj_transform(wkt_proj, destination_proj=DEFAULT_PROJECTION_EPSG) -> Transformer:
    destination_proj = CRS.from_epsg(4326)
    source_proj = CRS.from_wkt(wkt_proj)
    tr = Transformer.from_crs(source_proj, destination_proj)
    tr_i = Transformer.from_crs(destination_proj, source_proj)
    return tr, tr_i


def get_coordinates(x, y, cellx, celly, xmin, ymax):
    lng = xmin + x * cellx
    lat = ymax + y * celly
    return lng, lat


def get_projection_rotation(x, y, offset, tr, tr_i):
    wy, wx = tr.transform(y, x)
    ny, nx = tr_i.transform(wy - offset, wx)
    dx = x - nx
    dy = y - ny
    r = math.sqrt(dx * dx + dy * dy)
    deg = math.acos(dx / r)
    return (dx, dy, r, deg)