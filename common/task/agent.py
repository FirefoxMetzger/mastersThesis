import peewee
from common.db_base import sql_base

class Agent(sql_base):
    name = peewee.CharField(max_length=255)
    
    def __init__(self, *args, **kwargs):
        super(Agent, self).__init__(*args, **kwargs)
