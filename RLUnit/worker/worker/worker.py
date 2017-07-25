import logging
import zmq

from event_logging import EventPublisher
from main_loop import WorkerLoop

class Worker(object):

    def __init__(self, queue_address, db_address, logging_level):
        # setup logger
        self.logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
                '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging_level)
        self.logger.debug("Set logging level to %s" % logging_level)
        
        # setup queue communication
        self.context = zmq.Context.instance()
    
        # threads
        self.event_queue = EventPublisher(self.context)
        self.event_queue_req = self.context.socket(zmq.REQ)
        self.event_queue_req.bind("inproc://logging_control")
        
        self.loop = WorkerLoop(self.context, queue_address)
        self.loop_req = self.context.socket(zmq.REQ)
        self.loop_req.bind("inproc://loop_control")
        
    def start(self):
        self.logger.info("Starting worker threads")

        self.logger.debug("Start event queue")
        self.event_queue.start()

        self.logger.debug("Start main loop")
        self.loop.start()
    
    def stop(self):
        self.logger.info("Stopping threads")
        multi_msg = ["stop", ""]
        self.event_queue_req.send_multipart(multi_msg)
        self.loop_req.send_multipart(multi_msg)
        self.logger.info("Shutting down")
            
        
        
        
        
