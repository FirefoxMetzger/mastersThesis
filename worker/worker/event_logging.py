import threading
import zmq
import logging
import os
import json
import peewee

from common.result.step_reward import StepReward
from common.task.experiment import Experiment

class EventPublisher(threading.Thread):
    """
        This class implements a thread that takes care of logging the
        communication between the agent and the environment. It does so in a 
        stateless fassion by tracking the experiment, episode, step, ...
        and decorating the communication with this before broadcasting it.
    """
    def __init__(self, context):
        super(EventPublisher, self).__init__()
        
        self.process_another_message = True
        
        self.experiment_id = None
        self.episodes = 0
        self.resets = 0
        self.steps = 0
        
        # setup logger
        self.logger = logging.getLogger()
        
        # subscribe to internal events
        self.sub = context.socket(zmq.SUB)
        self.sub.setsockopt(zmq.SUBSCRIBE, "experiment")
        self.sub.setsockopt(zmq.SUBSCRIBE, "episode")
        self.sub.setsockopt(zmq.SUBSCRIBE, "reset")
        self.sub.setsockopt(zmq.SUBSCRIBE, "step")
        self.sub.bind("inproc://experiment_events")
        
        # worker events -- control
        self.rep = context.socket(zmq.REP)
        self.rep.connect("inproc://logging_control")
        
        self.poller = zmq.Poller()
        self.poller.register(self.sub, zmq.POLLIN)
        self.poller.register(self.rep, zmq.POLLIN)

    def run(self):
        self.logger.debug("Event Queue listening for messages")
        while self.process_another_message:
            sock = dict(self.poller.poll(100))
            
            # if communication happned handle it
            if self.sub in sock:
                topic, msg = self.sub.recv_multipart()
                self.handle_communication_message(topic, msg)

            # if command msg handle it
            if self.rep in sock:
                cmd, msg = self.rep.recv_multipart()
                self.handle_command_message(cmd, msg)
        self.logger.debug("Event Queue is exiting")
                
    def handle_communication_message(self, topic, msg):
        if topic == "experiment":
            self.logger.debug("A new experiment has been created")
            self.experiment_id = msg
            self.experiment = Experiment.get(Experiment.id == self.experiment_id)
            
            self.reset_episodes()
            # broadcast new experiment??
            self.logger.info("Now broadcasting experiment %s" % msg)
            
        elif topic == "episode":
            if self.experiment_id is None:
                raise RuntimeError("No experiment defined")
        
            self.episodes += 1
            self.reset_resets()
            # broadcast 
        
        elif topic == "reset":
            self.resets += 1
            self.reset_steps()
            
        elif topic == "step":
            self.steps += 1
            msg = json.loads(msg)
            
            result = dict()
            result["trial"] = self.experiment
            result["episode"] = self.episodes
            result["reset"] = self.resets
            result["step"] = self.steps
            result["reward"] = msg[0]
            
            try:
                StepReward.create(**result)
            except peewee.IntegrityError:
                self.logger.info("Step already in the database " + 
                    "-- should have been updated")
            # eventually broadcast
            
    def _experiment(self, experiment):
        self.experiment_id = experiment
        self.reset_episodes()
        
    def reset_episodes(self):
        self.episodes = 0
        self.reset_resets()
        
    def reset_resets(self):
        self.resets = 0
        self.reset_steps()
        
    def reset_steps(self):
        self.steps = 0
                    
    def handle_command_message(self, cmd, msg):
        if cmd == "stop":
            self.process_another_message = False
            self.rep.send("OK")
        elif cmd == "debug_level":
            self.logger.setLevel(msg)
            self.logger.debug("Set logging level to %s" % msg)
            
if __name__ == "__main__":
    ctx = zmq.Context()
    a = EventPublisher(ctx)
    a.start()
