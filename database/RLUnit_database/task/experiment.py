import peewee
import zmq
from RLUnit_database.db_base import sql_base
from RLUnit_database.task.environment import Environment
from RLUnit_database.task.agent import Agent
from RLUnit_database.task.trial import Trial

import time
import json
import logging

class Experiment(sql_base):
    environment = peewee.ForeignKeyField(Environment, related_name="Environment")
    agent = peewee.ForeignKeyField(Agent, related_name="Agent")
    trial = peewee.ForeignKeyField(Trial, related_name="Trial")
    
    def __init__(self, *args, **kwargs):
        super(Experiment, self).__init__(*args, **kwargs)
        self.logger = logging.getLogger()
        
    def setup(self, context):
        env_seed = self.trial.environment_seed
        agent_seed = self.trial.agent_seed
        
        self.environment.context = context
        self.environment.seed(env_seed)
        self.environment.experiment_id = self.id
        
        self.agent.seed(agent_seed)
        self.agent.set_environment(self.environment)
                
    def run(self):
        num_episodes = self.trial.num_episodes
        for ep in range(num_episodes):
            # send new episode message
            self.environment.episode = ep
            
            # perform episode
            self.agent.train_episode()
