import os
import peewee
from playhouse.db_url import connect
from db_base import sql_base
from experiment import Experiment

class EpisodeReward(sql_base):
    trial = peewee.ForeignKeyField(Experiment)
    episode = peewee.BigIntegerField()
    reward = peewee.DoubleField()
    
    class Meta():
        db = connect(os.environ["DB_ADDRESS"])
        indexes = (
            (('trial', 'episode','reward'), True),
        )
