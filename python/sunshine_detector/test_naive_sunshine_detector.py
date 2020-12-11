from datetime import datetime
from .naive_sunshine_detector import NaiveSunshineDetector
from . import get_coordinates

PATH = "layers/dem/dem_sunshine.tiff"
OUTPUT_PATH = "layers/dem/dem_sunshine_out.tiff"
# (y, x) = (345006, 3622216)
shady_point = (316092, 3626916)
light_point = (307899, 3624823)


def test_shade():
    detector = NaiveSunshineDetector(PATH)
    ts = datetime(2020, 12, 4, 17)
    assert detector.is_sunny(shady_point[0], shady_point[1], ts) is False
    ts = datetime(2020, 12, 4, 12)
    assert detector.is_sunny(light_point[0], light_point[1], ts) is True
    assert detector.get_todays_sunsets(shady_point[0], shady_point[1]) == 0


def test_get_coordinates():
    detector = NaiveSunshineDetector(PATH)
    lnglat1 = get_coordinates(1, 1, detector.cell_x, detector.cell_y, detector.x_min, detector.y_max)
    lnglat2 = get_coordinates(2, 2, detector.cell_x, detector.cell_y, detector.x_min, detector.y_max)
    assert lnglat1[0] < lnglat2[0]
    assert lnglat1[1] > lnglat2[1]
    # assert detector.is_sunny(shady_point[0], shady_point[1], ts) is False