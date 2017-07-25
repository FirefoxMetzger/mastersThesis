from worker.worker import Worker
import os
import time

queue = os.environ["QUEUE_ADDRESS"]
db = os.environ["DB_ADDRESS"]
log_lv = os.environ["LOGGING_LEVEL"]
worker = Worker(queue, db, log_lv)

try:
    worker.start()
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    worker.stop()

