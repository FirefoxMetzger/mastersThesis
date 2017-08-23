import peewee
import zmq
import playhouse.db_url
import logging
import Queue
import os
import sys
import random
import time

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
scheduled = dict()
context = zmq.Context()

# fill queue with stuff
def refill_queue():
    for experiment in Experiment.select():
        if experiment.id not in scheduled:
            q.put( (experiment.trial.id, experiment.id) )
        elif (time.time() - scheduled[experiment.id]
                > int(os.environ["RESCHEDULE_TIME"])):
            q.put( (experiment.id,experiment.id) )

refill_queue()

# setup sockets
task_address = os.environ["QUEUE_ADDRESS"]
logger.debug("Address set to: %s" % task_address)
task_server = context.socket(zmq.REP)
task_server.setsockopt(zmq.LINGER, 2000)
task_server.bind(task_address)
logger.info("Bound to %s to distribute work." % task_address)

while True:
    #wait for worker to poll
    logger.debug("Waiting for worker to send request")
    msg = task_server.recv()
    logger.debug("Received: %s" %msg)
    # hand out work if present
    try:
        exp_id = q.get_nowait()[1]
        while exp_id in scheduled:
            if (time.time() - scheduled[exp_id]
                    < int(os.environ["RESCHEDULE_TIME"])):
                    logger.info("Task has been scheduled before, discarding...")
                    exp_id = q.get_nowait()[1]
            else:
                break
        scheduled[exp_id] = time.time()
    except Queue.Empty:
        exp_id = "no work"
        refill_queue()

    logger.info("Sending experiment: %s" % exp_id)
    task_server.send_json(exp_id)
