FROM quay.io/openai/gym:latest
ENV PYTHONPATH=$PYTHONPATH:/usr/local/gym
RUN sudo apt-get update && \
    apt-get install libmysqlclient-dev -y

WORKDIR /app
COPY worker/Requirements.txt /app
RUN pip install -r Requirements.txt
RUN rm Requirements.txt

ENV LOGGING_LEVEL=DEBUG

ENV TASK_ADDRESS=127.0.0.1:5000
ENV RESULT_ADDRESS=127.0.0.1:6000

COPY worker/ /app
COPY common/ /app/common
CMD ["python", "test_worker.py"]
