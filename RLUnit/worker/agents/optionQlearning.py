from generic_agent import RandomAgent
import logging
import numpy as np
import combinatorics_library as comb
from simple_maze import SimpleMaze
from gym.spaces import prng

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

        # bin the environment
        #NUM_BUCKETS = (3, 3, 6, 3)
        #self.NUM_BUCKETS = NUM_BUCKETS

        #STATE_BOUNDS = zip(env.getObservations().low, env.getObservations().high)
        #STATE_BOUNDS[1] = [-0.5, 0.5]
        #STATE_BOUNDS[3] = [-math.radians(50), math.radians(50)]

        ## Learning related constants
        #self.MIN_EXPLORE_RATE = 0.01
        #self.MIN_LEARNING_RATE = 0.2

        #BINS = list()
        #for i, bound in enumerate(STATE_BOUNDS):
        #    buckets, step = np.linspace(    bound[0],
        #                                    bound[1],
        #                                    NUM_BUCKETS[i],
        #                                    retstep=True)
        #    buckets = buckets - 0.5 * step
        #    BINS.append(buckets)

        #self.BINS = BINS
        #NUM_STATES = np.prod(NUM_BUCKETS)
        NUM_STATES = 9
        self.NUM_STATES = NUM_STATES

        # option space size
        NUM_ACTIONS = env.action_space.n
        self.NUM_ACTIONS = NUM_ACTIONS
        NUM_OPTIONS = (NUM_ACTIONS + 1) ** NUM_STATES
        self.NUM_OPTIONS = NUM_OPTIONS

        ## Creating a Q-Table for each state-action pair
        self.q_table = np.zeros((   NUM_STATES,
                                    NUM_OPTIONS ))

        POLICY_BOUNDARY = (self.NUM_ACTIONS + 1) * np.ones(self.NUM_STATES)
        self.POLICY_BOUNDARY = POLICY_BOUNDARY

    def train_episode(self):
        # -- setup --
        current_state = self.env.reset()
        current_state = self.discretize(current_state)
        current_option = None
        done = False

        # -- execute episode --
        while not done:
            # current policy from index
            if current_option == None:
                current_option = self.new_policy(current_state)

            policy = np.unravel_index(current_option, self.POLICY_BOUNDARY)

            # action according to the current policy
            action = policy[current_state]
            next_state, reward, done, _ = self.env.step(action)
            next_state = self.discretize(next_state)

            # generate the option for next_state
            # aka. end policy if current_state is visited again
            new_policy = policy.copy()
            new_policy[current_state] = self.NUM_ACTIONS
            new_policy_idx = ravel_multi_index(new_policy, self.POLICY_BOUNDARY)

            self.intra_option_update(   current_state, current_option,
                                        next_state, new_option_idx,
                                        reward)

            # if the current policy ends in this state, end it
            if new_policy[next_state] == self.NUM_ACTIONS:
                self.inter_option_update(current_state, current_option)
                current_option = None
            else:
                # still follow the originally selected policy
                # but with updated termination condition
                current_option = new_policy_idx
            current_state = next_state

        self.episode += 1

    def intra_option_update(self, old_state, old_policy, new_state, new_policy, reward):
        alpha = self.get_learning_rate(self.episode)
        gamma = 0.99

        # compute update
        old_Q = self.q_table[old_state, old_policy]
        old_Q_decayed = (1 - alpha) * old_value

        update = reward + gamma * self.q_table[new_state, new_policy]
        self.q_table[old_state, action] = old_value_decayed + alpha * update

    def inter_option_update(self, state, option):
        self.q_table[state, option] = np.amax(self.q_table[state])

    def new_policy(self, current_state):
        # eligable policies that don't terminate in current_state
        # legal spaces
        policy_dimensions = self.POLICY_BOUNDARY.copy()
        policy_dimensions[current_state] = self.NUM_ACTIONS
        num_policies =( (self.NUM_ACTIONS + 1) ** (self.NUM_STATES - 1)
                        * self.NUM_ACTIONS)

        def legal_space_to_option_space(idx):
            policy = np.unravel_index(idx, policy_dimensions)
            idx = np.ravel_multi_index(policy, self.POLICY_BOUNDARY)
            return idx

        if self.random.random() < self.get_explore_rate(self.episode):
            policy_idx = self.random.randint(0, num_policies-1)
            return legal_space_to_option_space(policy_idx)
        else:
            best_option = None
            best_value = float("-Inf")
            for option in xrange(0,num_policies):
                option = legal_space_to_option_space(option)
                q_value = self.q_table[current_state, option]
                if best_option is None or best_value < q_value:
                    best_option = option
                    best_value = q_value
            return best_option

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

def OptionSpace(object):
    def __init__(max_actions, NUM_ACTIONS, NUM_STATES):
        self.BINS = [0] # to map idx to number of actions in option
        self.NUM_ACTIONS = NUM_ACTIONS
        self.NUM_STATES = NUM_STATES

    def policy_from_idx(self, idx):
        N = np.digitize(idx, self.BINS)     # number of actions in option
        idx = idx - self.BINS[N-1]            # lex. index of sub-option
        [mask_idx, action_idx] = np.unravel_index(idx,
                            (self.BINS[N],self.NUM_ACTIONS ** N))

        # mask from mask_idx
        policy = (self.NUM_ACTIONS + 1) * np.ones(self.NUM_STATES)
        positions = comb.idx_to_combination(mask_idx, N)
        actions = np.unravel_index(action_idx,[])
        np.put(policy,positions,)

if __name__ == "__main__":
    env = SimpleMaze()
    env.seed(42)
    prng.seed(1337)
    agent = Agent()
    agent.set_environment(env)
    agent.seed(1337)
    for idx = range(10):
        agent.train_episode()
