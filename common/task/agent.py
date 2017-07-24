import peewee
import random
from common.db_base import sql_base
import common.agents as agents

class Agent(sql_base):
    name = peewee.CharField(max_length=255)
    subtable_id = peewee.BigIntegerField()
    
    def __init__(self, *args, **kwargs):
        super(Agent, self).__init__(*args, **kwargs)
        
        if self.name is None or self.subtable_id is None:
            self.agent = None
        else:
            self.load_agent(self.name)
        
    @classmethod
    def get(self, cls, *query, **kwargs):
        self = super(Agent, self).get(cls, *query, **kwargs)
        self.load_agent()
        return self
        
    def seed(self, seed):
        self.agent.seed(seed)
        
    def set_environment(self, env):
        self.agent.set_environment(env)
        
    def train_episode(self):
        self.agent.train_episode()
    
    def load_agent(self):
        if self.name == "random":
            self.agent = agents.RandomAgent()
        elif self.name == "QAgent":
            self.agent = agents.QAgent.get(agents.QAgent.id == self.subtable_id)
        else:
            raise RuntimeError("Agent unknown.")
