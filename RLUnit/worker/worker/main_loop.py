import threading
import zmq
import logging
import time
import random

from orm import Experiment

class WorkerLoop(threading.Thread):
    def __init__(self, context, queue_address):
        super(WorkerLoop, self).__init__()
        
        # setup logger
        self.logger = logging.getLogger()
        
        # setup class
        self.context = context
        self.process_another_experiment = True
        self.work_request_send = False
        
        #setup command communication
        self.rep_cmd = context.socket(zmq.REP)
        self.rep_cmd.connect("inproc://loop_control")
        
        #setup worker communication
        self.req_work = self.context.socket(zmq.REQ)
        self.req_work.setsockopt(zmq.LINGER,1)
        self.req_work.connect(queue_address)
        self.logger.info("Connected to %s to get work." % queue_address)
        
        # init poller
        self.poller = zmq.Poller()
        self.poller.register(self.rep_cmd, zmq.POLLIN)
        self.poller.register(self.req_work, zmq.POLLIN)

    def run(self):
        while self.process_another_experiment:
            if not self.work_request_send:
                self.req_work.send("more")
                self.work_request_send = True
                
            else:
                sock = dict(self.poller.poll(100))
                
                # process another experiment
                if self.req_work in sock:
                    experiment_id = self.req_work.recv_json()
                    self.work_request_send = False
                    if experiment_id == "no work":
                        self.logger.debug("There is no work at this time. Sleeping for a while...")
                        time.sleep(random.randint(1,7))
                    else:
                        self.logger.debug("Fetching experiment with ID: %s" % experiment_id)

                        exp = Experiment(experiment_id, self.context)
                        exp.run()
                        
                        self.logger.debug("Finished Task %s" % experiment_id)
                
                # if command msg handle it
                if self.rep_cmd in sock:
                    cmd, msg = self.rep_cmd.recv_multipart()
                    self.handle_command_message(cmd, msg)
            
    def handle_command_message(self, cmd, msg):
        if cmd == "stop":
            self.process_another_experiment = False
            self.rep_cmd.send("OK")
        elif cmd == "debug_level":
            self.logger.setLevel(msg)
            self.logger.debug("Set logging level to %s" % msg)
