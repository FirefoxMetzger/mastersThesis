import zmq
from zmq.devices import ProcessProxy

class Scheduler(ProcessProxy):
    def __init__(self, in_type, out_type):
        super(Scheduler, self).__init__(in_type, out_type, zmq.PUB)
        
        self.pending_episodes = list()

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
                if topic not in self.pending_episodes:
                    self.pending_episodes.append(topic)
                    
            if reducer in active:
                # hand out a new episode to a reducer for processing
                reducer.recv()
                if not self.pending_episodes:
                    topic = "no work"
                else:
                    topic = self.pending_episodes.pop(0)
                reducer.send(topic)

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
