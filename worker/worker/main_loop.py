import threading
import zmq
import logging

from common.task.experiment import Experiment

class WorkerLoop(threading.Thread):
    def __init__(self, context, queue_address):
        super(WorkerLoop, self).__init__()
        
        # setup logger
        self.logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
                '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel("DEBUG")
        self.logger.debug("Set logging level to %s" % logging_level)
        
        # setup class
        self.context = context
        self.process_another_experiment = True
        
        #setup command communication
        self.rep_work = context.socket(zmq.REP)
        self.rep_work.connect(queue_address)
        
        #setup worker communication
        self.task_server = self.context.socket(zmq.REQ)
        self.task_server.setsockopt(zmq.LINGER,1)
        self.task_server.connect(queue_address)
        self.logger.info("Connected to %s to get work." % queue_address)
        
        # init poller
        self.poller = zmq.Poller()
        self.poller.register(self.rep_cmd, zmq.POLLIN)

    def run(self):
        while process_another_experiment:                
            # process another experiment
            self.task_server.send("more")
            experiment_id = self.task_server.recv_json()
            
            if experiment_id == "no work":
                self.logger.debug("There is no work at this time. Sleeping for a while...")
                time.sleep(random.randint(1,7))
            else:
                self.logger.debug("Fetching experiment with ID: %s" % experiment_id)

                exp = Experiment.get(Experiment.id == experiment_id)
                exp.setup(self.context)
                time.sleep(2) # -- ugly, rather wait for msg from logger
                exp.run()
                
                self.logger.debug("Finished Task %s" % experiment_id)
            
            # if command msg handle it
            sock = dict(self.poller.poll(100))
            if self.rep in sock:
                cmd, msg = self.rep.recv_multipart()
                self.handle_command_message(cmd, msg)
            
    def handle_command_message(self, topic, msg):
        if cmd == "stop":
            self.process_another_experiment = False
            self.rep.send("OK")
        elif cmd == "debug_level":
            self.logger.setLevel(msg)
            self.logger.debug("Set logging level to %s" % msg)
