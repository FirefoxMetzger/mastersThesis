from generic_agent import RandomAgent
import numpy as np
from gym.spaces import prng
import math
import cProfile
import gym
import time

class Agent(RandomAgent):
    def __init__(self):
        super(Agent, self).__init__()

        self.episode = 0

    def seed(self, seed):
        super(Agent, self).seed(seed)
        np.random.seed(seed)

    def set_environment(self, env):
        self.env = env

        # state space
        NUM_BUCKETS = (1, 1, 5, 2)  # (x, x', theta, theta')
        self.NUM_BUCKETS = NUM_BUCKETS

        STATE_BOUNDS = zip(env.getObservations().low, env.getObservations().high)
        STATE_BOUNDS[1] = [-0.5, 0.5]
        STATE_BOUNDS[3] = [-math.radians(50), math.radians(50)]
        BINS = list()
        for i, bound in enumerate(STATE_BOUNDS):
            buckets, step = np.linspace(bound[0], bound[1],NUM_BUCKETS[i], retstep=True)
            if not np.isnan(step):
                buckets = buckets - 0.5 * step
            BINS.append(buckets)

        #manualy specify buckets -- work a lot better than linear spacing
        #BINS[2] = np.array([-0.62831853, -0.20943951,  0.20943951])
        #BINS[2] = np.array([-0.62831853, -0.20943951, -0.01471976,  0.01471976,  0.20943951])
        BINS[2] = np.array([-0.62831853, -0.20943951, 0,  0.20943951])
        self.BINS = BINS

        NUM_STATES = np.prod(NUM_BUCKETS)
        self.NUM_STATES = NUM_STATES

        # action space
        NUM_ACTIONS = env.getActions().n
        self.NUM_ACTIONS = NUM_ACTIONS

        # option space
        NUM_OPTIONS = (NUM_ACTIONS + 1) ** NUM_STATES
        self.NUM_OPTIONS = NUM_OPTIONS

        # Create option Q-Table (NUM_OPTIONS < intmax)
        self.q_table = -0.0 * np.ones((NUM_STATES, NUM_OPTIONS ))

        POLICY_BOUNDARY = (self.NUM_ACTIONS + 1) * np.ones( self.NUM_STATES,
                                                            dtype="int64")
        self.POLICY_BOUNDARY = POLICY_BOUNDARY

        legal_policies = list()
        for state in range(NUM_STATES):
            policy_dimensions = POLICY_BOUNDARY.copy()
            policy_dimensions[state] = self.NUM_ACTIONS

            def legal_space_to_option_space(idx):
                policy = np.unravel_index(idx, policy_dimensions)
                idx = np.ravel_multi_index(policy, POLICY_BOUNDARY)
                return idx

            num_policies =( (self.NUM_ACTIONS + 1) ** (self.NUM_STATES - 1)
                            * self.NUM_ACTIONS)
            legal_policies.append(legal_space_to_option_space(xrange(num_policies)))
        self.legal_policies = legal_policies
        self.running_avg = np.zeros(100)

    def train_episode(self):
        # -- setup --
        current_state = self.env.reset()
        current_state = self.discretize(current_state)
        current_option = None
        done = False
        option_stack = list()   # save the list of (s,o) pairs; once done
                                # update inversed for compliance with semi-MDP

        # -- execute episode --
        acc_reward = 0

        while not done:
            #self.env.render()
            #time.sleep(0.05)
            # current policy from index
            if current_option == None:
                current_option = self.new_policy(current_state)

            policy = np.array(  np.unravel_index(   current_option,
                                                    self.POLICY_BOUNDARY),
                                dtype="int64")

            # action according to the current policy
            action = policy[current_state]
            next_state, reward, done, _ = self.env.step(action)
            next_state = self.discretize(next_state)
            acc_reward += reward

            # generate the option for next_state
            # aka. end policy if current_state is visited again
            new_policy = policy.copy()
            new_policy[current_state] = self.NUM_ACTIONS
            next_option = np.ravel_multi_index(new_policy, self.POLICY_BOUNDARY)

            # save the option into stack
            elem = (current_state, current_option, reward)
            option_stack.append(elem)

            if new_policy[next_state] == self.NUM_ACTIONS or done:
                # pick greedy option (argmax Q(s',o))
                self.inter_option_update(next_state, next_option)

                # unroll stack and update -- propagates discounted reward
                # all the way back to where the option was initiated
                prev_state = next_state
                prev_option = next_option
                while option_stack:
                    state, option, reward = option_stack.pop()
                    self.intra_option_update(   state, option,
                                                prev_state, prev_option,
                                                reward)
                    prev_state = state
                    prev_option = option

                # unravel the option stack
                current_option = None
            else:
                # update termination condition of option
                current_option = next_option

            current_state = next_state

        self.episode += 1

    def intra_option_update(self, old_state, old_policy, new_state, new_policy, reward):
        alpha = self.get_learning_rate(self.episode)
        gamma = 0.99

        # compute update
        old_Q = self.q_table[old_state, old_policy]
        old_Q_decayed = (1 - alpha) * old_Q

        update = reward + gamma * self.q_table[new_state, new_policy]
        self.q_table[old_state, old_policy] = old_Q_decayed + alpha * update

    def inter_option_update(self, state, option):
        self.q_table[state, option] = np.amax(self.q_table[state])

    def new_policy(self, current_state):
        exploration_chance = self.get_explore_rate(self.episode)
        if self.random.random() < exploration_chance:
            policy_idx = self.random.sample(self.legal_policies[current_state], 1)
            return policy_idx[0]
        else:
            best_option_idx = np.argmax(self.q_table[current_state,
                                        self.legal_policies[current_state]])
            best_option = self.legal_policies[current_state][best_option_idx]
            return best_option

    def get_explore_rate(self, t):
        MIN_EXPLORE_RATE = 0
        rate = max(MIN_EXPLORE_RATE, min(1.0, 1.0 - math.log10((t+1)/15.0)))
        return rate

    def get_learning_rate(self, t):
        MIN_LEARNING_RATE = 0.75
        rate = max(MIN_LEARNING_RATE, min(1.0, 1.0 - math.log10((t+1)/20.0)))
        return rate

    def discretize(self, state):
        bucket_indice = []
        for i in range(len(state)):
            bucket_idx = max(0, np.digitize(state[i],self.BINS[i]) - 1)
            bucket_indice.append(bucket_idx)

        return np.ravel_multi_index(bucket_indice, self.NUM_BUCKETS)

def main():
    env = gym.make("CartPole-v0")
    env.seed(1337)
    prng.seed(1337)
    agent = Agent()
    agent.set_environment(env)
    agent.seed(1337)

    for idx in range(2501):
        agent.train_episode()

if __name__ == "__main__":
    main()
    #cProfile.run("main()")
