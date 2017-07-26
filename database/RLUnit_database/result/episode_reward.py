import peewee
from playhouse.db_url import connect
from RLUnit_database.task.experiment import Experiment
from RLUnit_database.db_base import sql_base
import os

class EpisodeReward(sql_base):
    trial = peewee.ForeignKeyField(Experiment)
    episode = peewee.BigIntegerField()
    reward = peewee.DoubleField()
    
    class Meta:
        indexes = (
            (('trial', 'episode','reward'), True),
        )
