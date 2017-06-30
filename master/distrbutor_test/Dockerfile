FROM quay.io/openai/gym:latest
ENV PYTHONPATH=$PYTHONPATH:/usr/local/gym
RUN sudo apt-get update && \
    apt-get install libmysqlclient-dev -y

WORKDIR /app
COPY master/distrbutor_test /app
COPY common /app/common

RUN pip install -r Requirements.txt && rm Requirements.txt

ENV LOGGING_LEVEL=DEBUG
ENV TASK_ADDRESS=tcp://*:5000

CMD ["python", "test.py"]
