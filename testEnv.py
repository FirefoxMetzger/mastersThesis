import random
import gym
from Agent import Agent

random.seed(19930802)

num_trials = 100
random_seed_environment = [random.randint(0,2^32) for s in range(1,num_trials+1)]
random_seed_agent = [random.random() for s in range(1,num_trials+1)]

#setup
max_steps = 10000

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
    agent.seed(random_seed_agent[trial-1])
    action = agent.reset(observation)

    while not done:
        # update environment
        [observation, reward, done, info] = env.step(action)
        env.render()

        #update agent
        action = agent.step(observation, reward, done)

env.close()
agent.close()
