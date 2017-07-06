import peewee
import random
from common.db_base import sql_base
#from common.agent.generic_agent import RandomAgent

class Agent(sql_base):
    name = peewee.CharField(max_length=255)
    
    def __init__(self, *args, **kwargs):
        super(Agent, self).__init__(*args, **kwargs)
        
        if self.name is None:
            self.agent = None
        else:
            self.load_agent(self.name)
        
    @classmethod
    def get(self, cls, *query, **kwargs):
        self = super(Agent, self).get(cls, *query, **kwargs)
        self.load_agent(self.name)
        return self
        
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
    
    def load_agent(self, name):
        if name == "random":
            self.agent = RandomAgent()
        else:
            raise RuntimeError("Agent unknown.")
