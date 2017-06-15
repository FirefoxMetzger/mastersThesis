import logging
import zmq
import os
import thread
import time
import signal

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

task_address = os.environ["TASK_ADDRESS"]
task_server = context.socket(zmq.REQ)
task_server.connect("tcp://%s" % task_address)
logger.info("Connected to %s to get work." % task_address)

result_address = os.environ["RESULT_ADDRESS"]
result_server = context.socket(zmq.REQ)
result_server.connect("tcp://%s" % result_address)
logger.info("Connected to %s to post results" % result_address)

compute_thread = context.scket(zmq.PAIR)
compute_thread.bind("inproc://result")

def solve_complicated_experiment(context, experiment):
    signals = context.socket(zmq.PAIR)
    signals.connect("inproc://result")

    result = experiment["a"] + experiment["b"]

    signals.send_pyobj(result)
    signals.disconnect()

def gracefull_shutdown(signum, frame):
    logger.info("Received Signal: %s" % signum)
    if has_task == True:
        logger.info("Waiting for active experiment to finish")
        experiment_result = signals.recv_pyobj()
        result_server.send_json(experiment_result)
        result_server.recv()

    logger.info("Shutting down Worker - NOW")
    task_server.disconnect()
    result_server.disconnect()
    compute_thread.close()
    context.term()
    sys.exit(0)

# run a test and report the result
has_task = False
signals.signal(signal.SIGTERM, gracefull_shutdown)
signals.signal(signal.SIGINT, gracefull_shutdown)
signals.signal(signal.SIGQUIT, gracefull_shutdown)
while True:
    task_address.send("more")
    experiment = task_server.recv_json()
    thread.start_new_thread(solve_complicated_experiment,
                                (context, experiment))
    has_task = True
    experiment_result = signals.recv_pyobj()
    has_task = False
    result_server.send_json(experiment_result)
    result_server.recv()
     
    logger.debug("ANOTHER!")


# worker done clean up
logger.info("Worker is now exiting.")
