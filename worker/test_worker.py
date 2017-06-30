from worker import Worker
import os

queue = os.environ["QUEUE_ADDRESS"]
db = os.environ["DB_ADDRESS"]
log_lv = os.environ["LOGGING_LEVEL"]
worker = Worker(queue, db, log_lv)
worker.loop()
