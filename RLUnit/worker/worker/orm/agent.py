import peewee
import random
from gym.spaces import prng
from RLUnit_database.task import Agent as AgentData
import os

def my_import(name):
    components = name.split('.')
    mod = __import__(name)
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

class Agent(object): 
    def __init__(self, agent_id):
        agent_data = AgentData.get(AgentData.id == agent_id)
        
        filename = agent_data.subtable_id
        agent_name = os.path.splitext(filename)[0]
        agent_module = my_import('agents.'+agent_name)
        self.agent = agent_module.Agent()
        
    def seed(self, seed):
        prng.seed(seed)
        self.agent.seed(seed)
        
    def set_environment(self, env):
        self.agent.set_environment(env)
        
    def train_episode(self):
        self.agent.train_episode()
