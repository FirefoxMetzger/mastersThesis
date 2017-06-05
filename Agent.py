import zmq
import thread
import numpy as np

class Agent(object):
    def __init__(self, observation_space, action_space):
        self.context = zmq.Context()
        self.recieve_commands = True
        self.recieve_step = True

        self.observation_space = observation_space
        self.action_space = action_space
        self.reward = 0

        
        #thread.start_new_thread(self.commandThread,(self.context,))
        thread.start_new_thread(self.stepThread,(self.context,))

    def commandThread(self, context):
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://127.0.0.1:12346")

        while self.recieve_commands:
            cmd = socket.recv_json()
            cmd_name = cmd[0]
            
            if cmd_name == "seed":
                self.seed(int(cmd[1]))
            elif cmd_name == "reset":
                self.reset(cmd[1])
            elif cmd_name == "close":
                self.close()

            socket.send_json("OK")

        socket.close()

    def stepThread(self, context):
        socket = context.socket(zmq.REP)
        socket.connect("tcp://127.0.0.1:12345")

        while self.recieve_step:
            msg = socket.recv_json()
            return_msg = list()

            observation = np.asarray(msg[0])
            reward = msg[1]
            done = msg[2]

            action = self.step(observation, reward, done)
            return_msg.append(action)

            socket.send_json(action)

        socket.disconnect("tcp://127.0.0.1:12345")

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
        return action

    def close(self):
        self.recieve_commands = False
        self.recieve_step = False
