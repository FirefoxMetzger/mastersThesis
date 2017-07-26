import zmq
import os
import json
from RLUnit_database.result import EpisodeReward
import logging

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel("DEBUG")
logger.debug("Set logging level to DEBUG")

def create_socket(type_, address):
    ctx = zmq.Context.instance()
    sock = ctx.socket(type_)
    sock.connect(os.environ[address])
    return sock
    
reduce_req = create_socket(zmq.PUSH, "REDUCER_REQUEST_ADDRESS")
mapper_rep = create_socket(zmq.SUB, "MAPPER_REPLY_ADDRESS")
scheduler = create_socket(zmq.REQ, "SCHEDULER_ADDRESS")

poller = zmq.Poller()
poller.register(mapper_rep, zmq.POLLIN)

active_topic = ""
steps_received = set()
accumulated_reward = 0
steps_in_ep = -1

while not zmq.Context.instance().closed:
    aviable = dict(poller.poll(3000))
    
    if active_topic == "":
        logger.debug("requesting a new topic to work on")
        scheduler.send("")
        logger.debug("waiting for a reply from scheduler")
        topic = scheduler.recv()
        if topic == "no work":
            logger.debug("I am supposed to do nothing.")
        else:
            logger.info("Now collecting topic: " + topic)
            active_topic = topic
            mapper_rep.setsockopt(zmq.SUBSCRIBE, topic)
            
    if mapper_rep in aviable:
        topic, msg_json = mapper_rep.recv_multipart()
        if not topic == active_topic:
            logger.debug("Received outdated topic")
            continue
        
        steps = json.loads(msg_json)
        logger.debug(steps)
        for step in steps:
            if step["step"] not in steps_received:
                accumulated_reward += step["reward"]
                steps_received.add(step["step"])
            
            if step["done"]:
                logger.debug(step)
                steps_in_ep = step["step"] + 1 # 0 indexed
            
            if steps_in_ep == -1:
                logger.debug("Topic %s -- collected %d/X steps." % (topic, len(steps_received)))
            else:
                logger.debug("Topic %s -- collected %d/%d steps." % (topic, len(steps_received), steps_in_ep))
        
        if len(steps_received) >= steps_in_ep:
            trial, episode = active_topic.split(",")
            EpisodeReward.get_or_create(
                trial=int(trial),
                episode=int(episode),
                reward = accumulated_reward)
            logger.info("Episode %s of Experiment %s complete: Reward is %d after %d steps." % (trial, episode, accumulated_reward, len(steps_received)))
            
            mapper_rep.setsockopt(zmq.UNSUBSCRIBE, topic)
            active_topic = ""
            steps_received = set()
            accumulated_reward = 0
            steps_in_ep = -1
            
    elif not active_topic == "":
        logger.debug("Requesting more packets for topic: " + active_topic)
        reduce_req.send_multipart((active_topic, active_topic))
