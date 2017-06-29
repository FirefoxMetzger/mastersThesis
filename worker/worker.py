import logging
import peewee
import playhouse.db_url.connect as db_connect
import zmq
import os
import thread
import time
import sys
import gym

class Worker(object):

    def __init__(self, queue_address, db_address, logging_level):
        self.queue_address = queue.address
        
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

        self.task_server = self.context.socket(zmq.REQ)
        self.task_server.setsockopt(zmq.LINGER,1)
        self.task_server.connect(queue_address)
        self.logger.info("Connected to %s to get work." % queue_address)
        
    def solve_task(self):
        raise NotImplementedError
        
    def send_results(self):
        raise NotImplementedError
        
        
    def loop(self):
        try:
            while True:
                self.logger.debug("Sending request to server")
                self.task_server.send("more")
                self.logger.debug("Waiting for work...")
                experiment = self.task_server.recv_json()
                self.logger.debug("Received: %s" % experiment)
                if experiment == "no work":
                    self.logger.debug("There is no work at this time.")
                    time.sleep(3)
                else:
                    self.logger.debug("working")
                    experiment_result = self.solve_task(experiment)
                    self.logger.debug("Done Working. Result: %s" % experiment_result)

                    
                    self.logger.debug("Sending result to DB")
                    self.send_results(experiment)
                 
        except SystemExit:
            logger.debug("System Exit caught by main loop")
            sys.exit(0)
        finally:
            logger.debug("Disconnecting Task Server")
            task_server.disconnect(task_address)
            logger.debug("Disconnecting Result Server")
            result_server.disconnect(result_address)
            logger.debug("Terminating Context")
            context.term()
        
        
        
