import gym
import zmq

class Environment(object):
    def __init__(self):
        self.env_name = ""
        self.env = None

    def seed(self, seed):
        self.env.seed(seed)

    def reset(self):
        obs = self.env.reset()
        return obs

    def step(self, action):
        [observation, reward, done, info] = self.env.step(action)
        return (observation, reward, done)

    def close(self):
        self.env.close()

    def load(self, env_name):
        self.env_name = env_name
        self.env = gym.make(env_name)

    def getObservations(self):
        return self.env.ObservationSpace

    def getActions(self):
        return self.env.ActionSpace

if __name__ == "__main__":
    # run as standalone
    env = Environment()
    
    def process_msg(msg, env):
        cmd = msg[0]
        ret_msg = "OK"

        if cmd == "getObservation":
            ret_msg = env.getObservations()
        elif cmd == "getActions":
            ret_msg = env.getActions()
        elif cmd == "load":
            env_name = msg[1]
            env.load(env_name)
        elif cmd == "close":
            env.close()
        elif cmd == "step":
            action = msg[1]
            [observation, reward, done] = env.step(action)
            ret_msg = list()
            ret_msg.append(observation.tolist())
            ret_msg.append(reward)
            ret_msg.append(done)
        elif cmd == "reset":
            env.reset()
        elif cmd == "seed":
            seed = msg[1]
            env.seed(seed)
        else:
            ret_msg = "Command %s unknown" % cmd

        return ret_msg
            

    context = zmq.Context()

    socket = context.socket(zmq.REP)
    socket.bind("tcp://localhost:4567")

    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)

    stopped = False
    while not stopped:
        try:
            socks = dict(poller.poll())

            if socket in socks:
                msg = socket.recv_json()
                repl = process_msg(msg)
                socket.send_json(repl)
        except KeyboardInterrupt:
            stopped = True

    socket.close()
    context.destroy() 
