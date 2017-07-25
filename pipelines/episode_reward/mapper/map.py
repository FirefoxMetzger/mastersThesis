import zmq
import json
import os

# declare sockets
def get_socket(type_, address):
    ctx = zmq.Context.instance()
    sock = ctx.socket(type_)
    sock.connect(os.environ[address])
    return sock

entrypoint = get_socket(zmq.PULL, "ENTRYPOINT_ADDRESS")
reducer_req = get_socket(zmq.SUB, "REDUCER_REQUEST_ADDRESS")
reducer_rep = get_socket(zmq.PUB, "MAPPER_REPLY_ADDRESS")
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
        _, msg_json = pull.recv_multipart()
        # extract from the message what is needed downstream to save bandwidth
        msg = json.reads(msg_json)
        topic = str(msg["experiment"]) + "," + str(msg["episode"])
        small_msg = json.dumps({"step":msg["step"], "reward":msg["reward"] , "done":msg["done"]})
        
        if topic not in partitions:
            partitions[topic] = list()

        # inform scheduler of aviable episode           
        scheduler.send(topic)  
        partitions[topic].append(small_msg)
        
    if reducer_req in aviable:
        # handle data request if suitable data is present
        topic = reducer_req.recv()
        if topic in partitions:
            steps = partitions[topic]
            msg = json.dumps(steps)
            reducer_rep.send_multipart((topic, msg))
