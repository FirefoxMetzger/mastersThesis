

class Agent(object):
    def __init__(self, observation_space, action_space):
        self.observation_space = observation_space
        self.action_space = action_space
        self.reward = 0

    def seed(self, seed):
        pass

    def reset(self, observation):
        self.reward = 0
        return self.action_space.sample()

    def step(self, observation, reward, done):
        self.reward += reward
        if done:
            print "Acumulated reward: %i" % self.reward
        return self.action_space.sample()

    def close(self):
        pass
