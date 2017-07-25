FROM python:2.7

RUN apt-get update && \
    apt-get install libmysqlclient-dev -y

WORKDIR /app
COPY pipelines/base_image/Requirements.txt /app
RUN pip install -r Requirements.txt && rm Requirements.txt

WORKDIR /database
COPY /database .
RUN python setup.py install && cd .. && rm -rf /database

WORKDIR /app
