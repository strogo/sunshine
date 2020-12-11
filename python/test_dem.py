import math
import georasters as gr
from pyproj import CRS, Transformer
import ephem
import math
from datetime import datetime

PATH = "layers/dem/dem_sunshine.tiff"
OUTPUT_PATH = "layers/dem/dem_sunshine_out.tiff"
(y, x) = (345006, 3622216)


def test_dem():
    data = gr.load_tiff(PATH)
    NDV, xsize, ysize, GeoT, Projection, DataType = gr.get_geo_info(PATH)
    print(NDV)
    print(xsize)
    print(ysize)
    print(Projection)
    print(DataType)
    print(GeoT)

    # (x,y)=(318902, 3624782)
    col, row = gr.map_pixel(y, x, GeoT[1], GeoT[-1], GeoT[0], GeoT[3])
    col, row
    assert xsize == 1347
    assert ysize == 983
    assert data[col, row] == 26
    print(data[col, row])


def test_save_dem():
    data = gr.load_tiff(PATH)

    NDV, xsize, ysize, GeoT, Projection, DataType = gr.get_geo_info(PATH)

    # (x,y)=(318902, 3624782)
    col, row = gr.map_pixel(y, x, GeoT[1], GeoT[-1], GeoT[0], GeoT[3])
    col, row
    assert xsize == 1347
    assert ysize == 983
    assert data[col, row] == 26
    for i in range(0, xsize):
        for j in range(0, ysize):
            data[j, i] = 300 * int(data[j, i] / 300)
    raster = gr.GeoRaster(data, GeoT, nodata_value=-1000, projection=Projection, datatype=DataType)
    raster.to_tiff(OUTPUT_PATH)


def get_degree(x, y, offset, tr, tr_i):
    wy, wx = tr.transform(y, x)
    ny, nx = tr_i.transform(wy - offset, wx)
    dx = x - nx
    dy = y - ny
    r = math.sqrt(dx * dx + dy * dy)
    deg = math.acos(dx / r) * 2 * 360 / math.pi
    return (dx, dy, r, deg)


def get_angle():
    porto = CRS.from_epsg(3061)
    wgs = CRS.from_epsg(4326)
    tr = Transformer.from_crs(porto, wgs)
    tr_i = Transformer.from_crs(wgs, porto)
    print(get_degree(x, y, 0.001, tr, tr_i))
    print(get_degree(x, y, 0.01, tr, tr_i))
    print(get_degree(x, y, 0.1, tr, tr_i))


def test_proj_from_wkt():
    NDV, xsize, ysize, GeoT, Projection, DataType = gr.get_geo_info(PATH)
    wkt_proj = """PROJCS["Porto Santo 1995 / UTM zone 28N",
GEOGCS["Porto Santo 1995",
    DATUM["Porto_Santo_1995",
        SPHEROID["International 1924",6378388,297,
            AUTHORITY["EPSG","7022"]],
        AUTHORITY["EPSG","6663"]],
    PRIMEM["Greenwich",0,
        AUTHORITY["EPSG","8901"]],
    UNIT["degree",0.0174532925199433,
        AUTHORITY["EPSG","9122"]],
    AUTHORITY["EPSG","4663"]],
PROJECTION["Transverse_Mercator"],
PARAMETER["latitude_of_origin",0],
PARAMETER["central_meridian",-15],
PARAMETER["scale_factor",0.9996],
PARAMETER["false_easting",500000],
PARAMETER["false_northing",0],
UNIT["metre",1,
    AUTHORITY["EPSG","9001"]],
AXIS["Easting",EAST],
AXIS["Northing",NORTH],
AUTHORITY["EPSG","3061"]]
    """
    wkt_proj = str(Projection)

    # crs_porto = CRS.from_epsg(3061)
    # print(crs_porto.to_wkt())
    print(CRS.from_wkt(wkt_proj))


def test_azimuthh():
    home = ephem.Observer()
    # Set up
    home.date = datetime.now()  # "2020-11-29 23:59:00"
    home.lat = "51.5073"
    home.lon = "-0.12755"
    sun = ephem.Sun(home)
    print((math.degrees(sun.az), math.degrees(sun.alt)))
    print(math.sin(sun.alt))
    x_step = math.sin(sun.az)
    y_step = math.cos(sun.az)
    print((x_step, y_step))


if __name__ == "__main__":
    get_angle()