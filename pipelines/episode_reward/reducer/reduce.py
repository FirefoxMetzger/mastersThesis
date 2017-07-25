import zmq
import os
import json
from OrderedSet import OrderedSet as OrderedSet
from common.result.episode_reward import EpisodeReward
def create_socket(type_, address):
    ctx = zmq.Context.instance()
    sock = ctx.socket(type_)
    sock.connect(os.environ[address])
    
reduce_req = create_socket(zmq.PUB, "REDUCER_REQUEST_ADDRESS")
mapper_rep = create_socket(zmq.SUB, "MAPPER_REPLY_ADDRESS")
scheduler = create_socket(zmq.REQ, "SCHEDULER_ADDRESS")

poller = zmq.Poller()
poller.register(mapper_rep, zmq.POLLIN)

active_topic = ""
steps_received = OrderedSet()
accumulated_reward = 0
final_step = -1

while not zmq.Context.instance().closed:
    if active_topic == "":
        # get a new task
        scheduler.send("")
        topic = scheduler.recv()
        active_topic = topic
        mapper_rep.setsockopt(zmq.SUBSCRIBE, topic)
    
    aviable = dict(poller.poll())
    if mapper_rep in aviable:
        topic, msg_json = mapper_rep.recv_multipart()
        steps = json.reads(msg_json)
        for step in steps:
            if step["stepcount"] not in steps_received:
                accumulated_reward += step["reward"]
                steps_received.add(step["stepcount"])
            
            if step["done"]:
                final_step_count = step["stepcount"]
        
        if len(steps_received) == final_step_count:
            trial, episode = active_topic.split(",")
            EpisodeReward.get_or_create(
                trial=int(trial),
                episode=int(episode),
                reward = accumulated_reward)
            print active_topic, accumulated_reward
            
            mapper_rep.setsockopt(zmq.UNSUBSCRIBE, topic)
            active_topic = ""
            steps_received = OrderedSet()
            accumulated_reward = 0
            final_step = -1
    else:
        reduce_req.send_multipart(active_topic, "")
        
        
