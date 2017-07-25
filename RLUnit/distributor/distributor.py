import zmq
import peewee
import playhouse.db_url
import logging
import Queue
import os
import sys
import random

from RLUnit_database.task import Experiment

# setup logger
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(os.environ["LOGGING_LEVEL"])
logger.debug("Set logging level to %s" % os.environ["LOGGING_LEVEL"])

# local variables
q = Queue.PriorityQueue(-1)
context = zmq.Context()

# fill queue with stuff
def refill_queue():
    for experiment in Experiment.select():
        q.put( (random.randint(0,500),experiment.id) )

refill_queue()

# setup sockets
task_address = os.environ["QUEUE_ADDRESS"]
logger.debug("Address set to: %s" % task_address)
task_server = context.socket(zmq.REP)
task_server.setsockopt(zmq.LINGER, 2000)
task_server.bind(task_address)
logger.info("Bound to %s to distribute work." % task_address)

try:
    while True:
        #wait for worker to poll
        logger.debug("Waiting for worker to send request")
        msg = task_server.recv()
        logger.debug("Received: %s" %msg)
        # hand out work if present
        if msg == "more":
            try:
                ret_msg = q.get_nowait()[1]
            except Queue.Empty:
                ret_msg = "no work"
                refill_queue()
        else:
            ret_msg = "not understood"

        logger.info("Sending experiment: %s" % ret_msg)
        task_server.send_json(ret_msg)
except KeyboardInterrupt:
    logger.info("Keyboard interrupt. Shutting down.")
finally:
    task_server.unbind(task_address)
    context.term()
            
