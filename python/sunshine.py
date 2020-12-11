from typing import Callable
import georasters as gr
from argparse import ArgumentParser
from datetime import datetime, timedelta
import logging
from sunshine_detector import get_coordinates
from sunshine_detector.naive_sunshine_detector import NaiveSunshineDetector

logging.basicConfig(level="INFO")
log = logging.getLogger(__file__)


def process_image(input_tiff, output_tiff, op: Callable[[float, float], int], nodata_value=0):
    data = gr.load_tiff(input_tiff)
    NDV, xsize, ysize, GeoT, Projection, DataType = gr.get_geo_info(input_tiff)

    for i in range(0, xsize):
        if not i % 100:
            log.info(f"Row number {i} out of {xsize}")
        for j in range(0, ysize):
            lng, lat = get_coordinates(i, j, GeoT[1], GeoT[-1], GeoT[0], GeoT[3])
            value = int(op(lng, lat))
            # if value != 1:
            #    log.info(f"Coordinates for {i}, {j} are ({lng}, {lat}) and value is {value}")
            # log.info(f"{j}, {i} -> {value}")
            data[j, i] = value
    raster = gr.GeoRaster(data, GeoT, nodata_value=nodata_value, projection=Projection, datatype=DataType)
    raster.to_tiff(output_tiff)


def get_parser():
    args = ArgumentParser()
    args.add_argument("input_map", help="Input elevation tiff")
    args.add_argument("output_map", help="Output prefix")
    args.add_argument("date_from", help="Date from", type=lambda x: datetime.strptime(x, "%Y-%m-%d"))
    args.add_argument("date_to", help="Date to", type=lambda x: datetime.strptime(x, "%Y-%m-%d"))
    return args


if __name__ == "__main__":
    args = get_parser().parse_args()
    detector = NaiveSunshineDetector(args.input_map)
    d: datetime = args.date_from
    while d < args.date_to:
        # func = lambda lng, lat: detector.get_sunsets(d, lng, lat)
        func = lambda lng, lat: int(detector.is_sunny(lng, lat, d))
        out_date_suffix = d.strftime("%Y_%m_%d_%H")
        out = f"{args.output_map}__{out_date_suffix}"
        log.info(f"Processing time {d}")
        process_image(args.input_map, out, func)
        d += timedelta(hours=1)
