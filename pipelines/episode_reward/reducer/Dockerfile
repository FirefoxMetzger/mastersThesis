FROM firefoxmetzger/rlunit-pipeline-base

ENV PYTHONPATH="/app/common"

ENV REDUCER_REQUEST_ADDRESS="tcp://127.0.0.1:6100"
ENV MAPPER_REPLY_ADDRESS="tcp://127.0.0.1:6200"
ENV SCHEDULER_ADDRESS=tcp://127.0.0.1:6000
ENV DB_ADDRESS=mysql://root:password@mysql/reinforcement_learning
ENV DROP_DELAY=5

ADD pipelines/episode_reward/reducer/reduce.py .
ADD pipelines/episode_reward/reducer/OrderedSet.py .
ENTRYPOINT ["python", "reduce.py"]
