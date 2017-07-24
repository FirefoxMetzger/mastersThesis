import peewee
from playhouse.db_url import connect
from common.task.experiment import Experiment
import os

class EpisodeReward(peewee.Model):
    trial = peewee.ForeignKeyField(Experiment)
    episode = peewee.BigIntegerField()
    reward = peewee.DoubleField()
    
    class Meta():
        db = connect(os.environ["DB_ADDRESS"])
        indexes = (
            (('trial', 'episode','reward'), True),
        )
