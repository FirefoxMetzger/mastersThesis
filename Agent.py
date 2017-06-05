

class Agent(object):
    def __init__(self, observation_space, action_space):
        self.observation_space = observation_space
        self.action_space = action_space

    def seed(self, seed):
        pass

    def reset(self, observation):
        pass

    def step(self, observation, reward, done):
        return self.action_space.sample()
