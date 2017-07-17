import peewee
from common.db_base import sql_base
import zmq
import gym
import json
import logging

class Environment(sql_base):
    name = peewee.CharField(max_length=255)
    
    def __init__(self, *args, **kwargs):
        super(Environment, self).__init__(*args, **kwargs)
        
        if self.name is None:
            self.env = None
        else:
            self.env = gym.make(self.name)
            
        self.logger = logging.getLogger()
        self._context = None
        self.pub = None
        self._experiment_id = None
        self._episode = None
        self._resets = 0
        self._steps = 0
        
    @classmethod
    def get(self, cls, *query, **kwargs):
        self = super(Environment, self).get(cls, *query, **kwargs)
        self.env = gym.make(self.name)
        return self
        
    @property
    def context(self):
        return self._context
        
    @context.setter
    def context(self, context):
        self._context = context
        self.pub = context.socket(zmq.PUSH)
        self.pub.connect("inproc://experiment_events")
    
    @property
    def experiment_id(self):
        return self._experiment_id
    
    @experiment_id.setter
    def experiment_id(self, ex):
        self._experiment_id = ex
        self.episode = 0
        
    @property
    def episode(self):
        return self._episode
    
    @episode.setter
    def episode(self, ep):
        self._episode = ep
        self._resets = 0
        self._steps = 0

    def seed(self, seed):
        self.env.seed(seed)

    def reset(self):
        if self.context is None:
            raise RuntimeError("Initialize context before calling reset()")
        elif self.experiment_id == None:
            raise RuntimeError("Which experiment does this environment belong to?")
        elif self.episode == None:
            raise RuntimeError("An episode has not started yet")
        
        obs = self.env.reset()
        self._resets += 1
        return obs

    def step(self, action):
        if self.context is None:
            raise RuntimeError("Initialize context before calling step()")
        elif self.experiment_id == None:
            raise RuntimeError("Which experiment does this environment belong to?")
        elif self.episode == None:
            raise RuntimeError("An episode has not started yet")
            
        # the actual step
        observation, reward, done, info = self.env.step(action)
        
        # send a step message
        msg = dict()
        msg["experiment"] = self._experiment_id
        msg["episode"] = self._episode
        msg["reset"] = self._resets
        msg["step"] = self._steps
        msg["reward"] = reward
        msg["done"] = done
        msg["info"] = info
        self.pub.send_multipart(["step", json.dumps(msg)])
        
        self._steps += 1
        return (observation, reward, done, info)
        
    def render(self):
        self.env.render()

    def close(self):
        self.env.close()

    def getObservations(self):
        return self.env.observation_space

    def getActions(self):
        return self.env.action_space
