import peewee
import zmq
from db_base import sql_base
from environment import Environment
from agent import Agent
from trial import Trial

import time

class Experiment(sql_base):
    environment = peewee.ForeignKeyField(Environment, related_name="Environment")
    agent = peewee.ForeignKeyField(Agent, related_name="Agent")
    trial = peewee.ForeignKeyField(Trial, related_name="Trial")
                
