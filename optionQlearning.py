from generic_agent import RandomAgent
import logging
import numpy as np
import combinatorics_library as comb
from simple_maze import SimpleMaze
from gym.spaces import prng
import math
import cProfile
import re

class Agent(RandomAgent):
    def __init__(self):
        super(Agent, self).__init__()
        self.logger = logging.getLogger()
        self.logger.debug("Using Q-Learning with binning")
        self.episode = 0
        self.MIN_EXPLORE_RATE = 0.01
        self.MIN_LEARNING_RATE = 0.2

    def seed(self, seed):
        super(Agent, self).seed(seed)
        np.random.seed(seed)

    def set_environment(self, env):
        self.env = env

        # state space
        NUM_STATES = 9
        self.NUM_STATES = NUM_STATES

        # action space
        NUM_ACTIONS = env.action_space.n
        self.NUM_ACTIONS = NUM_ACTIONS

        # option space
        NUM_OPTIONS = (NUM_ACTIONS + 1) ** NUM_STATES
        self.NUM_OPTIONS = NUM_OPTIONS

        # Create option Q-Table (NUM_OPTIONS < intmax)
        self.q_table = 0.0 * np.ones((   NUM_STATES, NUM_OPTIONS ))

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

    def train_episode(self):
        # -- setup --
        current_state = self.env.reset()
        current_option = None
        done = False
        option_stack = list()   # save the list of (s,o) pairs; once done
                                # update inversed for compliance with semi-MDP

        # -- execute episode --
        acc_reward = 0
        #print "Starting State: %s" % str(np.unravel_index(current_state,[3,3]))
        while not done:
            # current policy from index
            if current_option == None:
                current_option = self.new_policy(current_state)

            policy = np.array(  np.unravel_index(   current_option,
                                                    self.POLICY_BOUNDARY),
                                dtype="int64")

            # action according to the current policy
            action = policy[current_state]
            #print(action, policy)
            next_state, reward, done, _ = self.env.step(action)
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

        print "Accumulated Reward %f" % acc_reward
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
        rate = max(self.MIN_EXPLORE_RATE, min(1.0, 1.0 - math.log10((t+1)/25.0)))
        return rate

    def get_learning_rate(self, t):
        rate = max(self.MIN_LEARNING_RATE, min(1.0, 1.0 - math.log10((t+1)/25.0)))
        return rate

def main():
    env = SimpleMaze()
    env.seed(42)
    prng.seed(1337)
    agent = Agent()
    agent.set_environment(env)
    agent.seed(1337)

    for idx in range(1000):
        agent.train_episode()
        V = np.amax(agent.q_table, 1)
        V = np.reshape(V,[3,3])
        #print(str(V))

if __name__ == "__main__":
    main()
    #cProfile.run("main()")
