FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

RUN apt-get update -y
RUN apt-get install libgdal-dev  libgl1 -y
# https://download.osgeo.org/gdal/3.8.0/gdal-3.8.0.tar.gz

WORKDIR /app/

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade --timeout=10000 -r /app/requirements.txt

COPY ./app .

EXPOSE 80



COPY ./start.sh /
RUN chmod +x /start.sh

ENV PYTHONPATH=/app