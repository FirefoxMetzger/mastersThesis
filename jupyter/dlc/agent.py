import peewee
import random
from db_base import sql_base

class Agent(sql_base):
    name = peewee.CharField(max_length=255)
