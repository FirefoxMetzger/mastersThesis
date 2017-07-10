import peewee
import random
from common.db_base import sql_base
from common.agents import RandomAgent

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
        self.agent.seed(seed)
        
    def set_environment(self, env):
        self.agent.set_environment(env)
        
    def reset(self, observation):
        return self.agent.reset(observation)
        
    def train_episode(self):
        self.agent.train_episode()
    
    def load_agent(self, name):
        if name == "random":
            self.agent = RandomAgent()
        else:
            raise RuntimeError("Agent unknown.")
