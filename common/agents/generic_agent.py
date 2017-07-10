import random

from common.db_base import sql_base

class RandomAgent(sql_base):
    def __init__(self):
        self.random = random.Random()
        self.env = None
        
    def seed(self, seed):
        self.random.seed(seed)
        
    def set_environment(self, env):
        self.env = env
        
    def reset(self, observation):
        return self.env.getActions().sample()
        
    def train_episode(self):
        if self.env is None:
            raise RuntimeError("Environment not defined")
        
        done = False
        while not done:
            action = self.env.getActions().sample()
            a, b, done, d = self.env.step(action)
