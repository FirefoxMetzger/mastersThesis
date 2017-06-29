import peewee
from common.db_base import sql_base
from common.task.environment import Environment
from common.task.agent import Agent
from common.task.trial import Trial

class Experiment(sql_base):
    environment = ForeignKeyField(Environment, related_name="Environment")
    agent = ForeignKeyField(Agent, related_name="Agent")
    trial = ForeignKeyField(Trial, related_name="Trial")
