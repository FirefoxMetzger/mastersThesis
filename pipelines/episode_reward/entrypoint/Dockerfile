FROM firefoxmetzger/pipline-base

ENV EXPERIMENT_EVENTS=tcp://127.0.0.1:1337
ENV ENTRYPOINT_ADDRESS=tcp://*:4135

ADD entrypoint.py .
ENTRYPOINT ["python" , "entrypoint.py"]
