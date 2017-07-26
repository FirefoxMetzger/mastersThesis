import zmq
from zmq.devices import ProcessProxy
from scheduler import Scheduler
import os
import time
import logging

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel("DEBUG")
logger.debug("Set logging level to DEBUG")

reduce_to_map = zmq.devices.ProcessProxy(zmq.PULL, zmq.PUB, zmq.PUB)
reduce_to_map.bind_in(os.environ["REDUCER_REQUEST_ADDRESS_IN"])
reduce_to_map.bind_out(os.environ["REDUCER_REQUEST_ADDRESS_OUT"])
reduce_to_map.bind_mon("tcp://127.0.0.1:9988")

map_to_reduce = zmq.devices.ProcessProxy(zmq.PULL, zmq.PUB)
map_to_reduce.bind_in(os.environ["MAPPER_REPLY_ADDRESS_IN"])
map_to_reduce.bind_out(os.environ["MAPPER_REPLY_ADDRESS_OUT"])

scheduler = Scheduler(zmq.PULL, zmq.REP)
scheduler.bind_in(os.environ["SCHEDULER_ADDRESS_IN"])
scheduler.bind_out(os.environ["SCHEDULER_ADDRESS_OUT"])

reduce_to_map.start()
map_to_reduce.start()
scheduler.start()

ctx = zmq.Context.instance()
mon = ctx.socket(zmq.SUB)
mon.setsockopt(zmq.SUBSCRIBE, "")
mon.connect("tcp://127.0.0.1:9988")

poller = zmq.Poller()
poller.register(mon, zmq.POLLIN)

try:
    while True:
        avi = dict(poller.poll(100))
        if mon in avi:
            topic, msg = mon.recv_multipart()
            logger.debug("The topic: "+ topic)
            logger.debug("The message: " + msg)
except KeyboardInterrupt:
    pass
finally:
    reduce_to_map.context_factory().destroy()
    map_to_reduce.context_factory().destroy()
    scheduler.context_factory().destroy()
