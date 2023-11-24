FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

# RUN apt-get update -y && apt-get install -y cmake libcrypto++-dev proj-bin libjpeg-dev liblzma-dev liblz-dev zlib1g-dev

# RUN apt-get install make g++ gcc make autoconf automake libtool

# WORKDIR /mylibtiff

# RUN wget http://download.osgeo.org/libtiff/tiff-4.0.10.tar.gz \
#     && tar -zxvf tiff-4.0.10.tar.gz  

# WORKDIR /mylibtiff/tiff-4.0.10
# RUN ls \
#     && bash ./configure  \
#     && make. \
#     && make install && \
#     && ldconfig \
#     && tiffinfo

# WORKDIR /mygdal

# RUN wget http://download.osgeo.org/gdal/3.8.0/gdal-3.8.0.tar.gz \
#     && tar -xvzf gdal-3.8.0.tar.gz \
#     && cd gdal-3.8.0 \
#     && mkdir build 

# WORKDIR /mygdal/gdal-3.8.0/build
# RUN cmake .. \
#     && cmake --build . \
#     && cmake --build . --target install \
#     && echo $(gdal-config --version)

RUN apt-get update -y \
    && apt-get install libgdal-dev libgl1 build-essential -y \
    && echo $(gdal-config --version)


WORKDIR /app/

COPY ./requirements.txt /app/requirements.txt

RUN gdal-config --version
RUN pip install --no-cache-dir --upgrade --timeout=10000 -r /app/requirements.txt
RUN pip install GDAL==$(gdal-config --version)
COPY ./app .

EXPOSE 80



COPY ./start.sh /
RUN chmod +x /start.sh

ENV PYTHONPATH=/app