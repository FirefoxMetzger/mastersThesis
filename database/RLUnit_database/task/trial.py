import peewee
from RLUnit_database.db_base import sql_base

class Trial(sql_base):
    agent_seed = peewee.BigIntegerField()
    environment_seed = peewee.BigIntegerField()
    num_episodes = peewee.BigIntegerField()
