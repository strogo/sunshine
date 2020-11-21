from datetime import datetime
from . import SunshineDetector

class NaiveSunshineDetector(SunshineDetector):
    def __init__(self) -> None:
        SunshineDetector.__init__(self)
    
    def is_sunny(self, lng: float, lat: float, ts: datetime) -> bool:
        return False