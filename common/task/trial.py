import peewee
from db_base import sql_base

class Trial(sql_base):
    agent_seed = peewee.DoubleField()
    environment_seed = peewee.DoubleField()
    
