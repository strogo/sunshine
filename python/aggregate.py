from os import listdir
from os.path import isfile, join
from argparse import ArgumentParser
import georasters as gr
import logging

logging.basicConfig(level="INFO")
log = logging.getLogger(__file__)


def get_parser():
    args = ArgumentParser()
    args.add_argument("input_directory", help="Directory containing input tiffs")
    args.add_argument("output_file", help="Tiff file where to store the final data")
    return args


def main(input_path, output_file):
    log.info(f"Processing {input_path}")
    tiff_list = [join(input_path, f) for f in listdir(input_path) if isfile(join(input_path, f))]
    log.info(f"Found {len(tiff_list)} files")
    data = gr.load_tiff(tiff_list[0])
    NDV, xsize, ysize, GeoT, Projection, DataType = gr.get_geo_info(tiff_list[0])

    # log.info("Clea")
    # for i in range(0, xsize):
    #    for j in range(0, ysize):
    #        data[j, i] = 0

    for f in tiff_list[1:]:
        log.info(f"Processing {f}")
        d = gr.load_tiff(f)
        for i in range(0, xsize):
            for j in range(0, ysize):
                if data.data[j, i] > 0:
                    pass
                data[j, i] = data.data[j, i] + d.data[j, i]
    raster = gr.GeoRaster(data, GeoT, nodata_value=0, projection=Projection, datatype=DataType)
    raster.to_tiff(output_file)
    log.info(f"Done processing {len(tiff_list)} files")


if __name__ == "__main__":
    args = get_parser().parse_args()
    # main("layers/sunshine/", "layers/dem/annual_sunsets")
    main(args.input_directory, args.output_file)