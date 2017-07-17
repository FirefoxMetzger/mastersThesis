import peewee
from db_base import sql_base

class Environment(sql_base):
    name = peewee.CharField(max_length=255)
