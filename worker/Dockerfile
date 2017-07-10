FROM quay.io/openai/gym:latest
ENV PYTHONPATH=$PYTHONPATH:/usr/local/gym
RUN sudo apt-get update && \
    apt-get install libmysqlclient-dev -y

WORKDIR /app
COPY worker/Requirements.txt /app
RUN pip install -r Requirements.txt
RUN rm Requirements.txt

ENV LOGGING_LEVEL=DEBUG

ENV QUEUE_ADDRESS=tcp://127.0.0.1:5000
ENV DB_ADDRESS=mysql://root:password@127.0.0.1/reinforcement_learning

COPY worker/ /app
COPY common/ /app/common
CMD ["python", "test_worker.py"]
