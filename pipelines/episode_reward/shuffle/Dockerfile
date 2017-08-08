FROM firefoxmetzger/rlunit-pipeline-base

ENV REDUCER_REQUEST_ADDRESS_IN="tcp://*:4100"
ENV REDUCER_REQUEST_ADDRESS_OUT="tcp://*:6100"
ENV MAPPER_REPLY_ADDRESS_IN="tcp://*:4200"
ENV MAPPER_REPLY_ADDRESS_OUT="tcp://*:6200"
ENV SCHEDULER_ADDRESS_IN="tcp://*:5000"
ENV SCHEDULER_ADDRESS_OUT="tcp://*:6000"
ENV TOPIC_TIMEOUT=300

ADD pipelines/episode_reward/shuffle/main.py .
ADD pipelines/episode_reward/shuffle/scheduler.py .
ENTRYPOINT ["python", "main.py"]
