import zmq
from zmq.devices import Proxy
import os
import logging

# just forward to mappers

logger = logging.getLogger()
proxy = Proxy(zmq.SUB, zmq.PUSH)
proxy.connect_in(os.environ["EXPERIMENT_EVENTS"])
logger.info("Collecting step from: %s" % os.environ["EXPERIMENT_EVENTS"])
proxy.setsockopt_in(zmq.SUBSCRIBE, "step")
proxy.bind_out(os.environ["ENTRYPOINT_ADDRESS"])
logger.info("Pushing to: %s" % os.environ["ENTRYPOINT_ADDRESS"])
proxy.start()
