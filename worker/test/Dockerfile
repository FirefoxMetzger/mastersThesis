FROM python2.7-slim

WORKDIR /app
ADD . /app
RUN pip install -r Requirements.txt


ENV LOGGING_LEVEL=DEBUG

ENV TASK_ADDRESS=localhost:5000
ENV RESULT_ADDRESS=localhost:6000
