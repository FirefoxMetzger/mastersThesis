import peewee
from common.db_base import sql_base
import zmq
import gym

class Environment(sql_base):
    name = peewee.CharField(max_length=255)
    
    def __init__(self, *args, **kwargs):
        super(Environment, self).__init__(*args, **kwargs)
        
        self.env = gym.make(self.name)

    def seed(self, seed):
        self.env.seed(seed)

    def reset(self):
        obs = self.env.reset()
        return obs

    def step(self, action):
        [observation, reward, done, info] = self.env.step(action)
        return (observation, reward, done)
        
    def render(self):
        self.env.render()

    def close(self):
        self.env.close()

    def load(self, env_name):
        self.env_name = env_name
        self.env = gym.make(env_name)

    def getObservations(self):
        return self.env.ObservationSpace

    def getActions(self):
        return self.env.ActionSpace
