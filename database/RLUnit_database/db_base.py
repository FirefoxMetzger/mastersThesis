import peewee
from playhouse.db_url import connect
import os

class sql_base(peewee.Model):
    class Meta:
        database = connect(os.environ["DB_ADDRESS"])
