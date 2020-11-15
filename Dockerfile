FROM andrejreznik/python-gdal:py3.7.3-gdal3.0.0
RUN apt-get update && apt-get install -y unzip build-essential wget virtualenv libspatialindex-dev python-rtree