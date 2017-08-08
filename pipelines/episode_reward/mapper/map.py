import zmq
import json
import os
import logging

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel("DEBUG")
logger.debug("Set logging level to DEBUG")

# declare sockets
def get_socket(type_, address):
    ctx = zmq.Context.instance()
    sock = ctx.socket(type_)
    sock.connect(os.environ[address])
    return sock

entrypoint = get_socket(zmq.PULL, "ENTRYPOINT_ADDRESS")
reducer_req = get_socket(zmq.PULL, "REDUCER_REQUEST_ADDRESS")
#reducer_req.setsockopt(zmq.SUBSCRIBE,"") # subscribe to all
reducer_rep = get_socket(zmq.PUSH, "MAPPER_REPLY_ADDRESS")
scheduler = get_socket(zmq.PUSH, "SCHEDULER_ADDRESS")

# setup local partitioning
partitions = dict()

# the actual mapper
poller = zmq.Poller()
poller.register(entrypoint, zmq.POLLIN)
poller.register(reducer_req, zmq.POLLIN)

ctx = zmq.Context.instance()
while not ctx.closed:
    aviable = dict(poller.poll())
    if entrypoint in aviable:
        _, msg_json = entrypoint.recv_multipart()
        # extract from the message what is needed downstream to save bandwidth
        msg = json.loads(msg_json)
        topic = str(msg["trial"]) + "," + str(msg["episode"])

        small_msg = {"step":msg["step"], "reward":msg["reward"] , "done":msg["done"]}

        if topic not in partitions:
            logger.info("New Topic: "+topic)
            partitions[topic] = set()

            # inform scheduler of aviable episode
            scheduler.send(topic)

        #logger.debug("Storing step %s for topic %s" % (msg["step"], topic))
        partitions[topic].add(json.dumps(small_msg))

    if reducer_req in aviable:
        # handle data request if suitable data is present
        topic, msg = reducer_req.recv_multipart()
        if topic in partitions:
            logger.debug("Sending out topic: " + topic)
            steps = [json.loads(s) for s in partitions.pop(topic)]
            msg = json.dumps(steps)
            reducer_rep.send_multipart((topic, msg))
        else:
            logger.debug("Topic %s unknown. Ignoring request" % topic)
