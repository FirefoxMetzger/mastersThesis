import zmq
from zmq.devices import ProcessProxy as Proxy
import os
import logging

hub = Proxy(zmq.PULL, zmq.PUB, zmq.PUB)
hub.bind_in(os.environ["WORKER_EVENT_ADDRESS"])
hub.bind_out(os.environ["PIPELINE_PUBLISHER_ADDRESS"])
hub.bind_mon("tcp://127.0.0.1:4008")
hub.start()

ctx = zmq.Context.instance()
sock = ctx.socket(zmq.SUB)
sock.connect("tcp://127.0.0.1:4008")
sock.setsockopt(zmq.SUBSCRIBE, "step")
msg_counter = 0
while True:
    sock.recv()
    msg_counter += 1
    print "Received %d messages" % (msg_counter)
