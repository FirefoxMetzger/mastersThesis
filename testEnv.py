import random
import zmq

random.seed(19930802)

num_trials = 100
random_seed_environment = [random.randint(0,2^32) for s in range(1,num_trials+1)]
random_seed_agent = [random.random() for s in range(1,num_trials+1)]

#setup
max_steps = 10000

context = zmq.Context()
agent = context.socket(zmq.REQ)
agent.connect("tcp://127.0.0.1:12345")

env = context.socket(zmq.REQ)
env.connect("tcp://localhost:4567")

env_name="CartPole-v0"
msg = ["load", env_name]
env.send_json(msg)
env.recv_json()

obs_space = env.send_json(["getObservation"])
env.recv_json()

msg = ["setObservation"]
msg.append(obs_space)
agent.send_json(msg)
agent.recv_json()

act_space = env.send_json(["getActions"])
env.recv_json()
msg = ["getActions"]
msg.append(act_space)
agent.send_json(msg)
agent.recv_json()

for trial in range(1,num_trials+1):
    #reset environment
    msg = ["seed", random_seed_environment[trial-1]]
    env.send_json(msg)
    env.recv_json()

    msg = ["reset"]
    env.send_json(msg)
    observation = env.recv_json()
    
    reward = 0
    done = False

    #reset agent
    cmd = ["seed", random_seed_agent[trial-1]]
    agent.send_json(cmd)
    agent.recv_json()

    cmd = ["reset", observation]
    command_socket.send_json(cmd)
    action = command_socket.recv_json()

    while not done:
        # update environment
        env.send_json(["step", action])
        [observation, reward, done, info] = env.recv_json(action)

        #update agent
        msg = [observation, reward, done]
        agent.send_json(msg)
        action = agent.recv_json()

msg = ["close"]
env.send_json(msg)
env.recv_json()

msg = list()
msg.append("close")
command_socket.send_json(msg)
command_socket.recv_json()
