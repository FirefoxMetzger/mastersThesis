import zmq
import thread
import numpy as np
from optparse import OptionParser
from logging import Logger

class Agent(object):
    def __init__(self, socket_ip):
        self.context = zmq.Context()
        self.recieve_commands = True
        self.socket_ip = socket_ip

        self.observation_space = observation_space
        self.action_space = action_space
        self.reward = 0
        
        thread.start_new_thread(self.commandThread,(self.context,))

    def commandThread(self, context):
        socket = context.socket(zmq.REP)
        socket.bind(self.socket_ip)

        while self.recieve_commands:
            cmd = socket.recv_json()
            cmd_name = cmd[0]
            msg = "OK"
            
            if cmd_name == "seed":
                self.seed(cmd[1])
            elif cmd_name == "reset":
                action =  self.reset(cmd[1])
                msg = action
            elif cmd_name == "close":
                self.close()
            elif cmd_name == "step":
                msg = list()

                observation = np.asarray(msg[0])
                reward = msg[1]
                done = msg[2]

                action = self.step(observation, reward, done)
                msg.append(action)
            elif cmd_name == "setObservation":
                self.observation_space = msg[1]
            elif cmd_name == "setActions":
                self.action_space = msg[1]

            socket.send_json(msg)

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
    if options.version:
        print "0.0.1"
    
    if options.verbose and options.quiet:
        parser.error("-v and -q are mutually exclusive")

    socket_ip = "tcp://%s:%s" % (options.ip, options.port)

    agent = Agent(socket_ip)
    
    alive = True
    while alive:
        try:
            sleep(0.1)
        except KeyboardInterrupt:
            alive = False

    

    
