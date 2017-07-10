import peewee
import zmq
from common.db_base import sql_base
from common.task.environment import Environment
from common.task.agent import Agent
from common.task.trial import Trial

import time

class Experiment(sql_base):
    environment = peewee.ForeignKeyField(Environment, related_name="Environment")
    agent = peewee.ForeignKeyField(Agent, related_name="Agent")
    trial = peewee.ForeignKeyField(Trial, related_name="Trial")
    
    def __init__(self, *args, **kwargs):
        super(Experiment, self).__init__(*args, **kwargs)
        
    def setup(self, context):
        env_seed = self.trial.environment_seed
        agent_seed = self.trial.agent_seed
        
        #connect to event queue
        self.pub = context.socket(zmq.PUB)
        self.pub.connect("inproc://experiment_events")
        
        self.environment.set_context(context)
        
        self.environment.seed(env_seed)
        self.agent.seed(agent_seed)
        self.agent.set_environment(self.environment)
        
        # send new experiment message
        topic = "experiment"
        msg = str(self.id)
        self.pub.send_multipart( [topic, msg] )
                
    def run(self):
        num_episodes = self.trial.num_episodes
        for ep in range(1, num_episodes + 1):
            # send new episode message
            topic = "episode"
            msg = ""
            self.pub.send_multipart( [topic, msg] )
            
            # perform episode
            obs = self.environment.reset()
            action = self.agent.reset(obs)
            
            self.agent.train_episode()
                
