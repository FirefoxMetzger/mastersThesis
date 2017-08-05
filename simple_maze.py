from gym.envs.toy_text.discrete import DiscreteEnv
import numpy as np
from gym.envs.registration import register

class SimpleMaze(DiscreteEnv):
    def __init__(self):
        shape = [3,3]
        P = list()
        for state in range(9):
            actions = list()
            x,y = np.unravel_index(state, shape)
            for action in range(4):
                # deterministic state transition
                if action == 0: #up
                    x_next = max(min(x + 0,2),0)
                    y_next = max(min(y + 1,2),0)
                elif action == 1: #down
                    x_next = max(min(x + 0,2),0)
                    y_next = max(min(y - 1,2),0)
                elif action == 2: #left
                    x_next = max(min(x + 1,2),0)
                    y_next = max(min(y + 0,2),0)
                elif action == 3: #right
                    x_next = max(min(x - 1,2),0)
                    y_next = max(min(y + 0,2),0)
                next_state = np.ravel_multi_index((x_next,y_next),[3,3])

                if next_state == 8:
                    transitions = [(1.0,next_state,1,True)]
                else:
                    transitions = [(1.0,next_state,-0.1,False)]

                actions.append(transitions)
            P.append(actions)

        isd = 1/8.0 * np.ones(9)
        isd[8] = 0.0
        isd = np.zeros(9)
        isd[0] = 1.0

        super(SimpleMaze, self).__init__(9,4,P,isd)
