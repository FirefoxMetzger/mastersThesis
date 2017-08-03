from gym import spaces
from generic_agent import RandomAgent
import logging
import numpy as np
import math

class Agent(RandomAgent):
    def __init__(self):
        super(Agent, self).__init__()
        self.logger = logging.getLogger()
        self.logger.debug("Using Q-Learning with binning")
        self.episode = 0

    def seed(self, seed):
        super(Agent, self).seed(seed)
        np.random.seed(seed)

    def set_environment(self, env):
        self.env = env

        NUM_BUCKETS = (3, 3, 6, 3)
        self.NUM_BUCKETS = NUM_BUCKETS
        NUM_ACTIONS = env.getActions().n

        STATE_BOUNDS = zip(env.getObservations().low, env.getObservations().high)
        STATE_BOUNDS[1] = [-0.5, 0.5]
        STATE_BOUNDS[3] = [-math.radians(50), math.radians(50)]

        ## Creating a Q-Table for each state-action pair
        self.q_table = np.zeros( (np.prod(NUM_BUCKETS), NUM_ACTIONS) )

        ## Learning related constants
        self.MIN_EXPLORE_RATE = 0.01
        self.MIN_LEARNING_RATE = 0.2

        ## Defining the simulation related constants
        NUM_EPISODES = 1000
        MAX_T = 250
        STREAK_TO_END = 120
        SOLVED_T = 199

        BINS = list()
        for i, bound in enumerate(STATE_BOUNDS):
            buckets, step = np.linspace(bound[0], bound[1],NUM_BUCKETS[i], retstep=True)
            buckets = buckets - 0.5 * step
            BINS.append(buckets)

        self.BINS = BINS

    def train_episode(self):
        # -- setup --
        # in MDPs observation == state
        current_state = self.env.reset()
        current_state = self.discretize(current_state)

        done = False
        rand_rate = self.get_explore_rate(self.episode)

        # -- execute episode --
        while not done:
            if self.random.random() < rand_rate:
                action = self.env.getActions().sample()
            else:
                action = np.argmax(self.q_table[current_state])

            next_state, reward, done, _ = self.env.step(action)
            next_state = self.discretize(next_state)

            self.update_table(current_state, next_state, action, reward)

            # end of step updates
            current_state = next_state

        self.episode += 1

    def update_table(self, old_state, new_state, action, reward):
        alpha = self.get_learning_rate(self.episode)
        gamma = 0.99

        # get the best action for the new state
        q_values = self.q_table[new_state]
        best_action = np.argmax(q_values)

        # compute update
        old_value = self.q_table[old_state, action]
        old_value_decayed = (1 - alpha) * old_value
        update = reward + gamma * self.q_table[new_state, best_action]
        self.q_table[old_state, action] = old_value_decayed + alpha * update

    def get_explore_rate(self, t):
        rate = max(self.MIN_EXPLORE_RATE, min(1.0, 1.0 - math.log10((t+1)/25.0)))
        return rate

    def get_learning_rate(self, t):
        rate = max(self.MIN_LEARNING_RATE, min(1.0, 1.0 - math.log10((t+1)/25.0)))
        return rate

    def discretize(self, state):
        bucket_indice = []
        for i in range(len(state)):
            bucket_idx = max(0, np.digitize(state[i],self.BINS[i]) - 1)
            bucket_indice.append(bucket_idx)

        return np.ravel_multi_index(bucket_indice, self.NUM_BUCKETS)
