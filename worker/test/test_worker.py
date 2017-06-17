import logging
import zmq
import os
import thread
import time
import sys

# setup logger
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(os.environ["LOGGING_LEVEL"])
logger.debug("Set logging level to %s" % os.environ["LOGGING_LEVEL"])

# setup sockets
context = zmq.Context()

task_address = "tcp://" + os.environ["TASK_ADDRESS"]
task_server = context.socket(zmq.REQ)
task_server.setsockopt(zmq.LINGER,1)
task_server.connect(task_address)
logger.info("Connected to %s to get work." % task_address)

result_address = "tcp://" + os.environ["RESULT_ADDRESS"]
result_server = context.socket(zmq.REQ)
result_server.setsockopt(zmq.LINGER,1)
result_server.connect(result_address)
logger.info("Connected to %s to post results" % result_address)

def solve_complicated_experiment(experiment):
    result = experiment["a"] + experiment["b"]
    return result

# run a test and report the result
try:
    while True:
        logger.debug("Sending request to server")
        task_server.send("more")
        logger.debug("Waiting for work...")
        experiment = task_server.recv_json()
        logger.debug("Received: %s" % experiment)
        if experiment == "no work":
            logger.debug("There is no work at this time.")
            time.sleep(3)
        else:
            logger.debug("working")
            experiment_result = solve_complicated_experiment(experiment)
            logger.debug("Done Working. Result: %s" % experiment_result)

            logger.debug("Sending result to DB")
            result_server.send_json(experiment_result)
            result_server.recv()
         
except SystemExit:
    logger.debug("System Exit caught by main loop")
    sys.exit(0)
finally:
    logger.debug("Disconnecting Task Server")
    task_server.disconnect(task_address)
    logger.debug("Disconnecting Result Server")
    result_server.disconnect(result_address)
    logger.debug("Terminating Context")
    context.term()
