from abc import ABC, ABCMeta, abstractmethod
from datetime import datetime
from georasters import georasters, GeoRaster

class SunshineDetector(ABCMeta):
    def __init__(self) -> None:
        self.raster: GeoRaster = None
    
    def load(self, raster: GeoRaster):
        self.raster = raster


    @abstractmethod
    def is_sunny(self, lng: float, lat: float, ts: datetime) -> bool:
        return False


