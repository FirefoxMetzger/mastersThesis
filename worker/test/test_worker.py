import logging
import zmq
import os
import thread
import time
import signal
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
task_server.connect(task_address)
logger.info("Connected to %s to get work." % task_address)

result_address = "tcp://" + os.environ["RESULT_ADDRESS"]
result_server = context.socket(zmq.REQ)
result_server.connect(result_address)
logger.info("Connected to %s to post results" % result_address)

compute_thread_address = "inproc://result"
compute_thread = context.socket(zmq.PAIR)
compute_thread.bind(compute_thread_address)

def solve_complicated_experiment(context, experiment):
    signals = context.socket(zmq.PAIR)
    signals.connect("inproc://result")

    result = experiment["a"] + experiment["b"]

    signals.send_pyobj(result)
    signals.disconnect("inproc://result")

def gracefull_shutdown(signum, frame):
    logger.info("Received Signal: %s" % signum)
    if has_task == True:
        logger.info("Waiting for active experiment to finish")
        experiment_result = signals.recv_pyobj()
        result_server.send_json(experiment_result)
        result_server.recv()

    logger.info("Shutting down Worker - NOW")
    sys.exit(0)

# run a test and report the result
has_task = False
signal.signal(signal.SIGTERM, gracefull_shutdown)
signal.signal(signal.SIGINT, gracefull_shutdown)
signal.signal(signal.SIGQUIT, gracefull_shutdown)
try:
    while True:
        task_server.send("more")
        experiment = task_server.recv_json()
        thread.start_new_thread(solve_complicated_experiment,
                                    (context, experiment))
        has_task = True
        experiment_result = compute_thread.recv_pyobj()
        has_task = False
        result_server.send_json(experiment_result)
        result_server.recv()
         
        logger.debug("ANOTHER!")
except SystemExit:
    logger.debug("System Exit caught by main loop")
    sys.exit(0)
finally:
    logger.debug("Disconnecting Task Server")
    task_server.disconnect(task_address)
    logger.debug("Disconnecting Result Server")
    result_server.disconnect(result_address)
    logger.debug("Unbinding computation thread")
    compute_thread.unbind(compute_thread_address)
    logger.debug("Terminating Context")
    context.term()

# worker done clean up
logger.info("Worker is now exiting.")
