import logging
import peewee
import zmq
import os
import time
import sys
import gym
import random

from common.task.experiment import Experiment

class Worker(object):

    def __init__(self, queue_address, db_address, logging_level):
        self.queue_address = queue_address
        
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

        self.task_address = queue_address
        self.task_server = self.context.socket(zmq.REQ)
        self.task_server.setsockopt(zmq.LINGER,1)
        self.task_server.connect(queue_address)
        self.logger.info("Connected to %s to get work." % queue_address)

    def loop(self):
        try:
            while True:
                self.logger.debug("Sending request to server")
                self.task_server.send("more")
                self.logger.debug("Waiting for work...")
                experiment_id = self.task_server.recv_json()
                
                if experiment_id == "no work":
                    self.logger.debug("There is no work at this time. Sleeping for a while...")
                    time.sleep(random.randint(1,7))
                else:
                    self.logger.debug("Fetching experiment with ID: %s" % experiment_id)
                    
                    exp = Experiment.get(Experiment.id == experiment_id)
                    exp.setup()
                    exp.run()
                    self.logger.debug("Finished Task %s" % experiment_id)
                
        except SystemExit:
            self.logger.debug("System Exit caught by main loop")
            sys.exit(0)
        finally:
            self.logger.debug("Disconnecting Task Server")
            self.task_server.disconnect(self.task_address)
        
        
        
