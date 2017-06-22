import zmq
import logging
import Queue
import os
import sys
import MySQLdb

# setup logger
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(os.environ["LOGGING_LEVEL"])
logger.debug("Set logging level to %s" % os.environ["LOGGING_LEVEL"])

# local variables
context = zmq.Context()
connection = MySQLdb.connect(host="mysql",
        user="root",
        passwd="password",
        db="dummy")
x = connection.cursor()

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
        try:
            x.execute("""UPDATE dummy SET result=%s WHERE ID=%s""",(msg, task_id))
            connection.commit()
        except:
            conn.rollback()


        logger.debug("Sending reply: success")
        result_server.send_json("success")
except KeyboardInterrupt:
    logger.info("Keyboard interrupt. Shutting down.")
finally:
    conn.close() 
    result_server.unbind(result_address)
    context.term()
