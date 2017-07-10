import peewee
from common.db_base import sql_base
import zmq
import gym
import json

class Environment(sql_base):
    name = peewee.CharField(max_length=255)
    
    def __init__(self, *args, **kwargs):
        super(Environment, self).__init__(*args, **kwargs)
        
        if self.name is None:
            self.env = None
        else:
            self.env = gym.make(self.name)
            
        self.context = None
        self.pub = None
        
    @classmethod
    def get(self, cls, *query, **kwargs):
        self = super(Environment, self).get(cls, *query, **kwargs)
        self.env = gym.make(self.name)
        return self
        
    def set_context(self, context):
        self.context = context
        self.pub = context.socket(zmq.PUB)
        self.pub.connect("inproc://experiment_events")
        

    def seed(self, seed):
        self.env.seed(seed)

    def reset(self):
        if self.context is None:
            raise RuntimeError("Initialize context before calling reset()")
        
        obs = self.env.reset()
        msg = ""
        self.pub.send_multipart(["reset", msg])
        return obs

    def step(self, action):
        if self.context is None:
            raise RuntimeError("Initialize context before calling step()")
        observation, reward, done, info = self.env.step(action)
        
        msg = json.dumps((reward, done, info))
        self.pub.send_multipart(["step", msg])
        return (observation, reward, done, info)
        
    def render(self):
        self.env.render()

    def close(self):
        self.env.close()

    def getObservations(self):
        return self.env.observation_space

    def getActions(self):
        return self.env.action_space
