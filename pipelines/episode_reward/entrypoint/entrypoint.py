import zmq
from zmq.devices import ProcessProxy as Proxy
import os
import logging

# just forward to mappers

logger = logging.getLogger()
proxy = Proxy(zmq.SUB, zmq.PUSH, zmq.PUB)
proxy.setsockopt_in(zmq.RCVHWM, int(1e6))
proxy.connect_in(os.environ["EXPERIMENT_EVENTS"])
proxy.setsockopt_in(zmq.SUBSCRIBE, "step")
proxy.bind_out(os.environ["ENTRYPOINT_ADDRESS"])
proxy.bind_mon("tcp://127.0.0.1:4008")
proxy.start()

ctx = zmq.Context.instance()
sock = ctx.socket(zmq.SUB)
sock.connect("tcp://127.0.0.1:4008")
sock.setsockopt(zmq.SUBSCRIBE, "")
msg_counter = 0
while True:
    sock.recv()
    msg_counter += 1
    print "Received %d messages" % (msg_counter)
