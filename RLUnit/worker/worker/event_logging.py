import threading
import zmq
import logging
import os
import json
import time
from RLUnit_database.result import EpisodeReward

class EventPublisher(threading.Thread):
    """
        This class implements a thread that takes care of logging the
        communication between the agent and the environment. It does so in a
        stateless fassion by tracking the experiment, episode, step, ...
        and decorating the communication with this before broadcasting it.
    """
    def __init__(self, context):
        super(EventPublisher, self).__init__()

        self.process_another_message = True

        # setup logger
        self.logger = logging.getLogger()
        self.logger.setLevel("INFO")

        # publish event messages
        self.push = context.socket(zmq.PUSH)
        self.push.connect(os.environ["HUB_ADDRESS"])

        # subscribe to internal events
        self.sub = context.socket(zmq.PULL)
        self.sub.bind("inproc://experiment_events")

        # worker events -- control
        self.rep = context.socket(zmq.REP)
        self.rep.connect("inproc://logging_control")

        self.poller = zmq.Poller()
        self.poller.register(self.sub, zmq.POLLIN)
        self.poller.register(self.rep, zmq.POLLIN)

        # episode reward buffer
        self.finished_reward_buffer = list()
        self.pending_ep_rewards = dict()
        self.last_insert = time.time()

    def run(self):
        self.logger.debug("Event Queue listening for messages")
        while self.process_another_message:
            sock = dict(self.poller.poll(100))

            # if communication happned handle it
            if self.sub in sock:
                topic, msg = self.sub.recv_multipart()
                self.handle_communication_message(topic, msg)

            # if command msg handle it
            if self.rep in sock:
                cmd, msg = self.rep.recv_multipart()
                self.handle_command_message(cmd, msg)
        self.logger.debug("Event Queue is exiting")

    def handle_communication_message(self, topic, msg):
        if topic == "step":
            msg = json.loads(msg)

            result = dict()
            result["trial"] = msg["experiment"]
            result["episode"] = msg["episode"]
            result["reset"] = msg["reset"]
            result["step"] = msg["step"]
            result["reward"] = msg["reward"]
            result["done"] = msg["done"]

            self.push.send_multipart(("step", json.dumps(result)))

            # terrible hack -- since we only measure reward per episode
            # instead of using the proper pipeline process it directly to save
            # the overhead

            if result["trial"] not in self.pending_ep_rewards:
                self.pending_ep_rewards[result["trial"]] = dict()
            trial = self.pending_ep_rewards[result["trial"]]

            if result["episode"] not in trial:
                trial[result["episode"]] = {
                    "steps":set(),
                    "final_step":float("Inf"),
                    "accumulated_reward":0
                }
            episode = trial[result["episode"]]

            if result["step"] not in episode["steps"]:
                episode["steps"].add(result["step"])
                episode["accumulated_reward"] += result["reward"]

            if result["done"]:
                episode["final_step"] = result["step"]

            if len(episode["steps"]) >= episode["final_step"]:
                ep = {  "trial":result["trial"],
                        "episode":result["episode"],
                        "reward":episode["accumulated_reward"]}
                self.finished_reward_buffer.append(ep)
                trial.pop(result["episode"], None)

                if len(self.finished_reward_buffer) >= 100:
                    bulk = self.finished_reward_buffer[:100]
                    self.finished_reward_buffer = self.finished_reward_buffer[100:]

                    try:
                        EpisodeReward._meta.database.close()
                    except:
                        pass # was already closed
                    EpisodeReward._meta.database.connect()
                    with EpisodeReward._meta.database.atomic():
                        EpisodeReward.insert_many(bulk).upsert().execute()
                    EpisodeReward._meta.database.close()
                    self.last_insert = time.time()

            if time.time() - self.last_insert > int(os.environ["FORCE_INSERT"]):
                self.logger.info("Forced Insert")
                num_inserts = min(len(self.finished_reward_buffer),100)
                if num_inserts == 0:
                    self.last_insert = time.time()
                    return
                bulk = self.finished_reward_buffer[:num_inserts]
                self.finished_reward_buffer = self.finished_reward_buffer[num_inserts:]

                try:
                    EpisodeReward._meta.database.close()
                except:
                    pass # was already closed
                EpisodeReward._meta.database.connect()
                with EpisodeReward._meta.database.atomic():
                    EpisodeReward.insert_many(bulk).upsert().execute()
                EpisodeReward._meta.database.close()
                self.last_insert = time.time()

    def handle_command_message(self, cmd, msg):
        if cmd == "stop":
            self.process_another_message = False
            self.rep.send("OK")
        elif cmd == "debug_level":
            self.logger.setLevel(msg)
            self.logger.debug("Set logging level to %s" % msg)
