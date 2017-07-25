import zmq
from zmq.devices import ProcessProxy
from scheduler import Scheduler
import os
import time

reduce_to_map = zmq.devices.ProcessProxy(zmq.XPUB, zmq.XSUB)
reduce_to_map.bind_in(os.environ["REDUCER_REQUEST_ADDRESS_IN"])
reduce_to_map.bind_out(os.environ["REDUCER_REQUEST_ADDRESS_OUT"])

map_to_reduce = zmq.devices.ProcessProxy(zmq.XPUB, zmq.XSUB)
map_to_reduce.bind_in(os.environ["MAPPER_REPLY_ADDRESS_IN"])
map_to_reduce.bind_out(os.environ["MAPPER_REPLY_ADDRESS_OUT"])

scheduler = Scheduler(zmq.PULL, zmq.REP)
scheduler.bind_in(os.environ["SCHEDULER_ADDRESS_IN"])
scheduler.bind_in(os.environ["SCHEDULER_ADDRESS_OUT"])

reduce_to_map.start()
map_to_reduce.start()
scheduler.start()

try:
    while True:
        time.sleep(2)
except KeyboardInterrupt:
    pass
finally:
    reduce_to_map.context_factory().destroy()
    map_to_reduce.context_factory().destroy()
    scheduler.context_factory().destroy()
