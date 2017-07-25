FROM quay.io/openai/gym:latest
ENV PYTHONPATH=$PYTHONPATH:/usr/local/gym

# peewee dependency
RUN sudo apt-get update && \
    apt-get install libmysqlclient-dev -y

WORKDIR /app
COPY RLUnit/worker/Requirements.txt /app
RUN pip install -r Requirements.txt && rm Requirements.txt

WORKDIR /database
COPY database/ .
RUN python setup.py install && cd .. && rm -rf /database

WORKDIR /app

ENV LOGGING_LEVEL=DEBUG
ENV QUEUE_ADDRESS=tcp://127.0.0.1:5000
ENV DB_ADDRESS=mysql://root:password@127.0.0.1/reinforcement_learning

COPY RLUnit/worker/ /app
CMD ["python", "main.py"]
