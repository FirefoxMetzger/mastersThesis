FROM python:2.7

RUN apt-get update && \
    apt-get install libmysqlclient-dev -y

WORKDIR /app
COPY Requirements.txt /app
RUN pip install -r Requirements.txt
RUN rm Requirements.txt
