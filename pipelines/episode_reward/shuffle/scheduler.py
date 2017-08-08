import zmq
from zmq.devices import ProcessProxy
import logging
import time
import os

class Scheduler(ProcessProxy):
    def __init__(self, in_type, out_type):
        super(Scheduler, self).__init__(in_type, out_type, zmq.PUB)

        self.logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
                '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel("DEBUG")
        self.logger.debug("Set logging level to DEBUG")

        self.pending_episodes = list()
        self.processing_episodes = dict()

    def _run(self):
        mapper, reducer, _ = self._setup_sockets()
        poller = zmq.Poller()
        poller.register(mapper, zmq.POLLIN)
        poller.register(reducer, zmq.POLLIN)

        while not self.context_factory().closed:
            active = dict(poller.poll())

            if mapper in active:
                # append the list of episodes (topics) that have steps
                # in partition if necessary
                topic = mapper.recv()
                if (topic not in self.pending_episodes and
                    topic not in self.processing_episodes.keys()):
                    self.logger.info("%s is now aviable on a worker" % topic)
                    self.pending_episodes.append(topic)

            if reducer in active:
                # hand out a new episode to a reducer for processing
                msg, topic = reducer.recv_multipart()
                if msg == "new topic":
                    if not self.pending_episodes:
                        self.logger.debug("A reducer requested work, but there is nothing to do.")
                        topic = "no work"
                    else:
                        topic = self.pending_episodes.pop(0)
                        self.logger.debug("Sending %s to a reducer" % topic)
                        self.processing_episodes[topic] = time.time()
                    reducer.send(topic)

                elif msg == "done":
                    self.processing_episodes.pop(topic, None)
                    self.logger.debug("Reducer said he finished: "+topic)
                    reducer.send("OK")

                elif msg == "heartbeat":
                    self.processing_episodes[topic] = time.time()
                    self.logger.debug("Renewing watchdog for topic "+topic)
                    reducer.send("OK")

            # check heartbeat
            # if we didn't hear from the reducer within 10 seconds assume it died
            toc = time.time()
            for key in self.processing_episodes.keys():
                if toc - self.processing_episodes[key] > int(os.environ["TOPIC_TIMEOUT"]):
                    self.logger.warn("Rescheduling topic %s. Potentially a reducer died.")
                    #self.pending_episodes.append(key)
                    self.processing_episodes.pop(key, 'None')


    def run_device(self):
        try:
            self._run()
        except zmq.ZMQError as e:
            if e.errno == zmq.ETERM:
                pass
            else:
                raise e
        finally:
            self.done = True
