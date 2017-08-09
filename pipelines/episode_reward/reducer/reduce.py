import zmq
import os
import sys
import json
from RLUnit_database.result import EpisodeReward
import logging
import time

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel("INFO")
logger.debug("Set logging level to DEBUG")

def create_socket(type_, address):
    ctx = zmq.Context.instance()
    sock = ctx.socket(type_)
    sock.hwm = 100000
    sock.connect(os.environ[address])
    return sock

reduce_req = create_socket(zmq.PUSH, "REDUCER_REQUEST_ADDRESS")
mapper_rep = create_socket(zmq.SUB, "MAPPER_REPLY_ADDRESS")
mapper_rep.setsockopt(zmq.SUBSCRIBE, "")
scheduler = create_socket(zmq.REQ, "SCHEDULER_ADDRESS")

poller = zmq.Poller()
poller.register(mapper_rep, zmq.POLLIN)

class ActiveTopic(object):
    def __init__(self, topic):
        self.topic = topic
        self.last_update = time.time()
        self.steps_received = set()
        self.accumulated_reward = 0
        self.steps_in_ep = sys.maxint

        self.trial, self.episode = topic.split(",")

    def add_steps(self, steps):
        for step in steps:
            if step["step"] not in self.steps_received:
                self.accumulated_reward += step["reward"]
                self.steps_received.add(step["step"])
            if step["done"]:
                self.steps_in_ep = step["step"] + 1 # 0 indexed
            if self.is_done():
                break   # all other steps will provide redundant information
                        # from the same ep being rescheduled upstream
        self.last_update = time.time()

    def __eq__(self, other):
        return self.topic == other

    def __len__(self):
        return len(self.steps_received)

    def __repr__(self):
        return self.topic

    def __add__(self, other):
        return self.topic + other

    def __radd__(self, other):
        return other + self.topic

    def is_done(self):
        return len(self) >= self.steps_in_ep

active_topic = None
episode_buffer = list()
store_messages = False
storage_counter = 0
storage_cap = 200

while not zmq.Context.instance().closed:
    if active_topic is not None:
        scheduler.send_multipart(("heartbeat",active_topic.topic))
        scheduler.recv()

    aviable = dict(poller.poll(100))
    if mapper_rep in aviable:
        topic, msg_json = mapper_rep.recv_multipart()
        if not topic == active_topic:
            logger.debug("This is not my current topic ...")
            continue

        steps = json.loads(msg_json)
        active_topic.add_steps(steps)
        logger.debug("Topic %s -- collected %d steps." %
                        (active_topic, len(active_topic)))

        if active_topic.is_done():
            episode_buffer.append(  {"trial":active_topic.trial,
                                    "episode":active_topic.episode,
                                    "reward":active_topic.accumulated_reward})
            logger.info(("Experiment %s, Episode %s, Reward %d, Steps: %d"+
                        "  -- Buffered %d/200") %
                        (active_topic.trial, active_topic.episode,
                        active_topic.accumulated_reward,
                        len(active_topic), len(episode_buffer)))

            scheduler.send_multipart(("done", str(active_topic)))
            scheduler.recv()

            active_topic = None

    elif active_topic is not None:
        if time.time() - active_topic.last_update > int(os.environ["DROP_DELAY"]):
            logger.error(("%s seconds without update. Dropping Task."+
                " This is usually caused by a dropped message in the pipe.")
                % (os.environ["DROP_DELAY"]))
            active_topic = None
        else:
            logger.debug("Requesting more packets for topic: " + active_topic)
            reduce_req.send_multipart((active_topic.topic, active_topic.topic))

    elif active_topic is None:
        logger.debug("requesting a new topic to work on")
        scheduler.send_multipart(("new topic",""))
        logger.debug("waiting for a reply from scheduler")
        topic = scheduler.recv()
        if topic == "no work":
            logger.debug("I am supposed to do nothing.")
        else:
            active_topic = ActiveTopic(topic)

        # every so many episodes, store them in bulk
        # "no work" is included in counting to store the last eps when no new
        # work is submitted
        storage_counter += 1
        if storage_counter >= storage_cap:

            if episode_buffer:
                try:
                    EpisodeReward._meta.database.close()
                except:
                    pass # was already disconnected

                EpisodeReward._meta.database.connect()
                logger.info("Storing %d new accumulated rewards" % len(episode_buffer))
                EpisodeReward.insert_many(episode_buffer).upsert().execute()
                EpisodeReward._meta.database.close()
            episode_buffer = list()
            storage_counter = 0
