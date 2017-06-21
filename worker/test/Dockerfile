FROM python:2.7-slim

WORKDIR /app
COPY . /app
RUN pip install -r Requirements.txt
RUN rm Requirements.txt


ENV LOGGING_LEVEL=DEBUG

ENV TASK_ADDRESS=localhost:5000
ENV RESULT_ADDRESS=localhost:6000

CMD ["python", "test_worker.py"]
