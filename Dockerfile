FROM andrejreznik/python-gdal:py3.7.3-gdal3.0.0
ADD .devcontainer /.devcontainer
RUN apt-get update && apt-get install -y unzip build-essential wget virtualenv libspatialindex-dev python-rtree git
RUN pip install --upgrade pip
RUN pip install -r ./.devcontainer/requirements.dev.txt