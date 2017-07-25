import peewee
import zmq
from RLUnit_database.task import Experiment as rawExperiment
from environment import Environment
from agent import Agent
from RLUnit_database.task import Trial

import json
import logging

class Experiment(object):
    def __init__(self, experiment_id, context):
        self.logger = logging.getLogger()
        
        # incredible hack -- however inheritance of RLUnit_database.Experiment
        # fails and I can't work your why
        # this will do for now, since the worker is not supposed to modify the
        # experiment anyway
        experiment = rawExperiment.get(rawExperiment.id == experiment_id)
        self.trial = Trial.get(Trial.id == experiment.trial)
        
        self.environment = Environment.get(Environment.id == experiment.environment)
        self.environment.context = context
        
        self.agent = Agent(experiment.agent)
        
        env_seed = self.trial.environment_seed
        self.environment.seed(env_seed)
        self.environment.experiment_id = experiment.id
        
        agent_seed = self.trial.agent_seed
        self.agent.seed(agent_seed)
        self.agent.set_environment(self.environment)
                
    def run(self):
        num_episodes = self.trial.num_episodes
        for ep in range(num_episodes):
            # send new episode message
            self.environment.episode = ep
            
            # perform episode
            self.agent.train_episode()
