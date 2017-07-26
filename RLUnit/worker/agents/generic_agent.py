import random

class RandomAgent(object):
    def __init__(self):
        self.random = random.Random()
        self.env = None
        
    def seed(self, seed):
        self.random.seed(seed)
        
    def set_environment(self, env):
        self.env = env
        
    def train_episode(self):
        if self.env is None:
            raise RuntimeError("Environment not defined")
        
        self.env.reset()
        done = False
        while not done:
            action = self.env.getActions().sample()
            a, b, done, d = self.env.step(action)
