FROM firefoxmetzger/rlunit-pipeline-base

ENV ENTRYPOINT_ADDRESS="tcp://127.0.0.1:4135"
ENV REDUCER_REQUEST_ADDRESS="tcp://127.0.0.1:4100"
ENV MAPPER_REPLY_ADDRESS="tcp://127.0.0.1:4200"
ENV SCHEDULER_ADDRESS="tcp://127.0.0.1:5000"

ADD pipelines/episode_reward/mapper/map.py .
ENTRYPOINT ["python", "map.py"]
