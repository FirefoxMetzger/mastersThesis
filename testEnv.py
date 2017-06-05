import random
import gym
import zmq
from Agent import Agent

random.seed(19930802)

num_trials = 100
random_seed_environment = [random.randint(0,2^32) for s in range(1,num_trials+1)]
random_seed_agent = [random.random() for s in range(1,num_trials+1)]

#setup
max_steps = 10000

context = zmq.Context()
action_socket = context.socket(zmq.REQ)
action_socket.connect("tcp://127.0.0.1:12345")

command_socket = context.socket(zmq.REQ)
command_socket.connect("tcp://127.0.0.1:12346")

env_name="CartPole-v0"
env = gym.make(env_name)

agent = Agent(env.observation_space, env.action_space)

for trial in range(1,num_trials+1):
    #reset environment
    env.seed(random_seed_environment[trial-1])
    observation = env.reset()
    reward = 0
    done = False

    #reset agent
    cmd = list()
    cmd.append("seed")
    cmd.append(random_seed_agent[trial-1])
    command_socket.send_json(cmd)
    command_socket.recv_json()

    cmd = list()
    cmd.append("reset")
    cmd.append(observation.tolist())
    
    command_socket.send_json(cmd)
    action = command_socket.recv_json()

    while not done:
        # update environment
        [observation, reward, done, info] = env.step(action)
        env.render()

        msg = list()
        msg.append(observation.tolist())
        msg.append(reward)
        msg.append(done)

        #update agent
        action_socket.send_json(msg)
        action = action_socket.recv_json()

env.close()

msg = list()
msg.append("close")
command_socket.send_json(msg)
command_socket.recv_json()
