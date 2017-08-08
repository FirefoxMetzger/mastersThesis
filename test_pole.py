import gym
import numpy as np
import random
import math
from time import sleep
from gym.spaces import prng

## Initialize the "Cart-Pole" environment
env = gym.make('CartPole-v0')
env.seed(1337)
random.seed(48)
prng.seed(48)


NUM_BUCKETS = (3, 3, 6, 3)  # (x, x', theta, theta')
NUM_ACTIONS = env.action_space.n # (left, right)

STATE_BOUNDS = zip(env.observation_space.low, env.observation_space.high)
STATE_BOUNDS[1] = [-0.5, 0.5]
STATE_BOUNDS[3] = [-math.radians(50), math.radians(50)]

## Creating a Q-Table for each state-action pair
q_table = np.zeros( (np.prod(NUM_BUCKETS), NUM_ACTIONS) )

## Learning related constants
MIN_EXPLORE_RATE = 0.01
MIN_LEARNING_RATE = 0.2

## Defining the simulation related constants
NUM_EPISODES = 1000
MAX_T = 250
SOLVED_T = 199

BINS = list()
for i, bound in enumerate(STATE_BOUNDS):
    buckets, step = np.linspace(bound[0], bound[1],NUM_BUCKETS[i], retstep=True)
    buckets = buckets - 0.5 * step
    BINS.append(buckets)

def simulate():
    ## Instantiating the learning related parameters
    learning_rate = get_learning_rate(0)
    explore_rate = get_explore_rate(0)
    discount_factor = 0.99  # since the world is unchanging

    num_streaks = 0

    for episode in range(1,NUM_EPISODES+1):

        # Reset the environment
        obv = env.reset()

        # the initial state
        state_0 = discretize(obv)

        acc_reward = 0

        done = False
        while not done:
            #env.render()

            # Select an action
            action = select_action(state_0, episode)

            # Execute the action
            obv, reward, done, _ = env.step(action)
            acc_reward += reward

            # Observe the result
            learning_rate = get_learning_rate(episode)
            state = discretize(obv)
            V = np.amax(q_table[state])
            q_table[state_0, action] += learning_rate*(reward + discount_factor*V - q_table[state_0 , action])

            # Setting up for the next iteration
            state_0 = state

            if done:
               print("Episode %d finished after %f time steps." % (episode, acc_reward))

def select_action(state, episode):
    # Select a random action
    explore_rate = get_explore_rate(episode)
    if random.random() < explore_rate:
        action = env.action_space.sample()
    # Select the action with the highest q
    else:
        action = np.argmax(q_table[state])
    return action


def get_explore_rate(t):
    rate = max(MIN_EXPLORE_RATE, min(1.0, 1.0 - math.log10((t+1)/25.0)))
    return rate

def get_learning_rate(t):
    rate = max(MIN_LEARNING_RATE, min(1.0, 1.0 - math.log10((t+1)/25.0)))
    return rate

def discretize(state):
    bucket_indice = []
    for i in range(len(state)):
        bucket_idx = max(0, np.digitize(state[i],BINS[i]) - 1)
        bucket_indice.append(bucket_idx)

    return np.ravel_multi_index(bucket_indice, NUM_BUCKETS)

if __name__ == "__main__":
    simulate()
