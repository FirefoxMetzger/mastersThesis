import logging
import peewee
import zmq
import os
import time
import sys
import gym
import random
import json
import threading

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
        self.context = zmq.Context()

        # queue communication
        self.task_address = queue_address
        self.task_server = self.context.socket(zmq.REQ)
        self.task_server.setsockopt(zmq.LINGER,1)
        self.task_server.connect(queue_address)
        self.logger.info("Connected to %s to get work." % queue_address)

        
        # threads
        self.event_queue = EventPublisher(self.context, queue_address)
        self.event_queue_req = zmq.socket(zmq.REQ)
        self.event.queue_req.bind("inproc://logging_control")
        
        self.loop = WorkerLoop(self.context)
        self.loop_req = zmq.socket(zmq.REQ)
        self.loop_req.bind("inproc://loop_control")
        
    def start():
        self.logger.info("Starting worker threads")

        self.logger.debug("Start event queue")
        self.event_queue.start()

        self.logger.debug("Start main loop")
        self.loop.start()
    
    def stop():
        self.logger.info("Stopping threads")
        multi_msg = ["stop", ""]
        self.event_queue_req.send_multipart(multi_msg)
        self.loop.req.send_multipart(multi_msg)
        self.logger.info("Shutting down")
            
        
        
        
        
