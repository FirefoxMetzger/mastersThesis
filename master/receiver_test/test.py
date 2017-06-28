import zmq
import logging
import Queue
import os
import sys
import peewee
import playhouse.db_url

# setup logger
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(os.environ["LOGGING_LEVEL"])
logger.debug("Set logging level to %s" % os.environ["LOGGING_LEVEL"])

# setup MySQL
ip = os.environ["MYSQL_ADDRESS"]
db = playhouse.db_url.connect(ip)

class Experiment(peewee.Model):
    a = peewee.DoubleField()
    b = peewee.DoubleField()
    result = peewee.DoubleField(null=True)
    last_modified = peewee.TimestampField()
    class Meta:
        database = db

if not Experiment.table_exists():
    db.create_tables([Experiment])

# local variables
context = zmq.Context()

# setup sockets
result_address = "tcp://" + os.environ["RESULT_ADDRESS"]
result_server = context.socket(zmq.REP)
result_server.setsockopt(zmq.LINGER, 2000)
result_server.bind(result_address)
logger.info("Bound to %s to receive results." % result_address)

try:
    while True:
        #wait for worker to submit result
        logger.debug("Waiting for worker to send result")
        msg = result_server.recv_json()        
        # store result (or print it =) ) 
        logger.info("Storing: %s" % msg)
        msg.save()

        logger.debug("Sending reply: success")
        result_server.send_json("success")
except KeyboardInterrupt:
    logger.info("Keyboard interrupt. Shutting down.")
finally:
    result_server.unbind(result_address)
    context.term()
