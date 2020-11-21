import georasters as gr

PATH = "layers/dem/dem_sunshine.tiff"


def test_dem():
    data = gr.load_tiff(PATH)
    NDV, xsize, ysize, GeoT, Projection, DataType = gr.get_geo_info(PATH)
    (x, y) = (345006, 3622216)
    # (x,y)=(318902, 3624782)
    col, row = gr.map_pixel(x, y, GeoT[1], GeoT[-1], GeoT[0], GeoT[3])
    col, row
    assert data[col, row] == 26
    print(data[col, row])


if __name__ == "__main__":
    test_dem()