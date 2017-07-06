import peewee
from common.db_base import sql_base
from common.task.experiment import Experiment

class EpisodeReward(sql_base):
    trial = peewee.ForeignKeyField(Experiment)
    episode = peewee.BigIntegerField()
    reward = peewee.DoubleField()
