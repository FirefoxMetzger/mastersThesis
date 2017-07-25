import zmq
from zmq.devices import Proxy
import os
import logging

logger = logging.getLogger()

hub = Proxy(zmq.PULL, zmq.PUB)
hub.bind_in(os.environ["WORKER_EVENT_ADDRESS"])
logger.info("Collecting step from: %s" % os.environ["WORKER_EVENT_ADDRESS"])
hub.bind_out(os.environ["PIPELINE_PUBLISHER_ADDRESS"])
logger.info("Pushing to: %s" % os.environ["PIPELINE_PUBLISHER_ADDRESS"])
hub.start()
