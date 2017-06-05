import zmq
import thread
import numpy as np
from optparse import OptionParser

class Agent(object):
    def __init__(self, observation_space, action_space):
        self.context = zmq.Context()
        self.recieve_commands = True
        self.recieve_step = True

        self.observation_space = observation_space
        self.action_space = action_space
        self.reward = 0
        
        thread.start_new_thread(self.commandThread,(self.context,))
        thread.start_new_thread(self.stepThread,(self.context,))

    def commandThread(self, context):
        socket = context.socket(zmq.REP)
        socket.bind("tcp://127.0.0.1:12346")

        while self.recieve_commands:
            cmd = socket.recv_json()
            cmd_name = cmd[0]
            
            if cmd_name == "seed":
                self.seed(cmd[1])
                msg = "OK"
            elif cmd_name == "reset":
                action =  self.reset(cmd[1])
                msg = action
            elif cmd_name == "close":
                self.close()
                msg="OK"

            socket.send_json(msg)

        socket.close()

    def stepThread(self, context):
        socket = context.socket(zmq.REP)
        socket.bind("tcp://127.0.0.1:12345")

        while self.recieve_step:
            msg = socket.recv_json()
            return_msg = list()

            observation = np.asarray(msg[0])
            reward = msg[1]
            done = msg[2]

            action = self.step(observation, reward, done)
            return_msg.append(action)

            socket.send_json(action)

        socket.close()

    def seed(self, seed):
        pass

    def reset(self, observation):
        self.reward = 0
        return self.action_space.sample()

    def step(self, observation, reward, done):
        self.reward += reward
        if done:
            print "Acumulated reward: %i" % self.reward
        action = self.action_space.sample()
        return  action

    def close(self):
        self.recieve_commands = False
        self.recieve_step = False

if __name__ == "__main__":
    # run agent as standalone

    parser = OptionParser()

    parser.add_option("--IP", dest="ip", help="Set IP to listen on", default="localhost")
    parser.add_option("--PORT", dest="port", help="Set Port to listen on", 
            default="12345")
    parser.add_option("-v", dest="verbose", action="store_true",
            help="Set logging level to DEBUG", 
            default=False)
    parser.add_option("-q", dest="quiet", action="store_true",
            help="Set logging level to CRITICAL",
            default=False)
    parser.add_option("--VERSION", dest="version", 
            help="Print the current version, then exit", default=False)

    (options, args) = parser.parse_args()

    print options
    if options.verbose and options.quiet:
        parser.error("-v and -q are mutually exclusive")
