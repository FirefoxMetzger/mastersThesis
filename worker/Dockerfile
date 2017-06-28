FROM quay.io/openai/gym:latest
ENV PYTHONPATH=$PYTHONPATH:/usr/local/gym

WORKDIR /app
COPY . /app
RUN pip install -r Requirements.txt
RUN rm Requirements.txt


ENV LOGGING_LEVEL=DEBUG

ENV TASK_ADDRESS=127.0.0.1:5000
ENV RESULT_ADDRESS=127.0.0.1:6000

CMD ["python", "test_worker.py"]
