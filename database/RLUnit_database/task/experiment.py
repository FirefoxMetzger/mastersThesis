import peewee
from RLUnit_database.db_base import sql_base
from RLUnit_database.task.environment import Environment
from RLUnit_database.task.agent import Agent
from RLUnit_database.task.trial import Trial

class Experiment(sql_base):
    environment = peewee.ForeignKeyField(Environment, related_name="Environment")
    agent = peewee.ForeignKeyField(Agent, related_name="Agent")
    trial = peewee.ForeignKeyField(Trial, related_name="Trial")
