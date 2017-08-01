from gym import spaces
from generic_agent import RandomAgent
import logging
import numpy as np

class QAgent(RandomAgent):
    def __init__(self):
        super(QAgent, self).__init__()
        self.action_space_supported = False
        self.observation_space_supported = False
        self.logger = logging.getLogger()
        
        # parameters
        self.alpha = 0.5
        self.gamma = 0.5
        self.rand_rate = 0.7
        self.rand_decay = 0.99
        # -- box space parameters --
        self.num_bins = 10

    def seed(self, seed):
        super(QAgent, self).seed(seed)
        np.random.seed(seed)

    def set_environment(self, env):
        self.env = env

        # figure out of the action space is discrete or not
        if isinstance(self.env.getActions(), spaces.Discrete):
            self.action_space_supported = True

            self.num_actions = self.env.getActions().n

        else:
            self.action_space_supported = False
            self.logger.error("This agent does only support discrete action spaces.")

        # check if state is discrete or not
        if isinstance(self.env.getObservations(), spaces.Discrete):
            self.observation_space_supported = True
            self.observation_space_discrete = True

            self.num_observations = self.env.getObservations().n

        elif isinstance(self.env.getObservations(), spaces.Box):
            self.observation_space_supported = True
            self.observation_space_discrete = False

            # use binning as dimensionality reduction strategy
            low = self.env.getObservations().low
            high = self.env.getObservations().high
            self.bins = list()
            self.bin_idx = list()
            self.num_observations = 1
            for idx in range(len(low)): # assume equal length low - high
                self.bins.append(np.linspace(low[idx],high[idx],self.num_bins))
                self.bin_idx.append(self.num_bins)
                self.num_observations *= self.num_bins

        else:
            self.observation_space_supported = False
            self.logger.error("This agent only supports discrete or box observation spaces.")

        # if observation and action are discrete, use table
        if self.action_space_supported and self.observation_space_supported:
            self.q_table = np.random.uniform(low=-1, high=1, size=(self.num_observations, self.num_actions))

    def train_episode(self):
        if not self.action_space_supported or not self.observation_space_supported:
            self.logger.error("Can't run episode. A space is unsupported.")

        # -- setup --
        # in MDPs observation == state
        current_state = self.env.reset()
        if not self.observation_space_discrete:
            current_state = self.discretize(current_state)

        done = False
        rand_rate = self.rand_rate

        # -- execute episode --
        while not done:
            if self.random.random() > rand_rate:
                action = np.argmax(self.q_table[current_state,:])
                if not self.env.getActions().contains(action):
                    self.logger.error("Action outside of space !!!")
            else:
                action = self.env.getActions().sample()

            next_state, reward, done, info = self.env.step(action)
            if not self.observation_space_discrete:
                next_state = self.discretize(next_state)

            self.update_table(current_state, next_state, action, reward)

            # end of step updates
            current_state = next_state
            rand_rate *= self.rand_decay

    def update_table(self, old_state, new_state, action, reward):
        # get the best action for the new state
        q_values = self.q_table[new_state,:]
        best_action = np.argmax(q_values)

        # compute update
        old_value = self.q_table[old_state, action]
        old_value_decayed = (1 - self.alpha) * old_value
        update = reward + self.gamma * self.q_table[new_state, best_action]
        self.q_table[old_state, action] = old_value_decayed + self.alpha * update

    def discretize(self, observation):
        # digitize the observation into a bin
        indices = list([0] * len(observation))
        for idx, obs in enumerate(observation):
            indices[idx] = np.digitize(obs, self.bins[idx])

        # for the resulting bin compute it's index
        return np.ravel_multi_index(indices, self.bin_idx)
