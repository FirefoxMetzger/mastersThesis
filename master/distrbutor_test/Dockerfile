FROM python:2.7-slim

WORKDIR /app
COPY . /app
RUN pip install -r Requirements.txt

ENV LOGGING_LEVEL=DEBUG

ENV TASK_ADDRESS=127.0.0.1:5000

CMD ["python", "test.py"]
