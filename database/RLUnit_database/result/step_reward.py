import os
import peewee
from playhouse.db_url import connect
from RLUnit_database.db_base import sql_base
from RLUnit_database.task.experiment import Experiment

class StepReward(sql_base):
    trial = peewee.ForeignKeyField(Experiment)
    episode = peewee.BigIntegerField()
    reset = peewee.BigIntegerField()
    step = peewee.BigIntegerField()
    reward = peewee.DoubleField()
    
    class Meta():
        indexes = (
            (('trial', 'episode','reset','step'), True),
        )
