import peewee
from RLUnit_database.db_base import sql_base

class Agent(sql_base):
    name = peewee.CharField(max_length=255)
    subtable_id = peewee.BigIntegerField()
