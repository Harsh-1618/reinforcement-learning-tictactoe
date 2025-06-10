'''
Code for minimax algorithm with alpha-beta pruning for 2D and Infinite 2D tictactoe with any 2D grid size.
Even though you can use it for any grid size, you should NOT use it for grid size other than 3x3 since it's still too slow!
Hence, i am not generalizing it for 3D tictactoe variants.
While this implementation is tailored for tictactoe, it can be easily generalized to any adversarial game.

Note:
x is max player and is denoted by '1' in logic grid. it'll want to maximize the value and would prefer this order of values 1->0->-1.
o is min player and is denoted by '-1' in logic grid. it'll want to minimize the value and would prefer this order of values -1->0->1.
A value of 1 denotes x wins, value of -1 denotes o wins and a value of 0 denotes a tie.
It does not matter with what value you denote x or o in logic grid, you could have used -1 and 1 resply,
but what matters is max player (x in this case) should have a value higher than min player (o in this case) when it wins, and tie value should be in between.
'''

import numpy as np
from copy import deepcopy


class Minimax:
    def __init__(self, ttt_dim):
        self.ttt_dim = ttt_dim

    @staticmethod
    def get_available_actions(state):
        zero_places = np.where(state==0)
        return list(zip(zero_places[0], zero_places[1]))

    @staticmethod
    def get_next_state(state, player, action):
        state[action] = player
        return state

    # I can use tictactoe's check_win by making it staticmethod
    # and i would have if i were to be using minimax for 3D tictactoe as well
    def check_win(self, state, player, row_val, col_val):
        return np.sum(state[row_val,:]) == player * self.ttt_dim or \
        np.sum(state[:,col_val]) == player * self.ttt_dim or \
        np.sum(np.diag(np.flip(state, axis=0))) == player * self.ttt_dim or \
        np.sum(np.diag(state)) == player * self.ttt_dim

    def terminal(self, state, player, action):
        is_win = self.check_win(state, player, action[0], action[1])
        if is_win:
            return 1 if player == 1 else -1
        return 0 if (len(np.where(state==0)[0]) == 0) else None

    def get_state_action_value(self, state, player, prev_action=None, alpha=-float("inf"), beta=float("inf")):
        state_copy = deepcopy(state)

        if prev_action is not None:
            state_copy = self.get_next_state(state_copy, player, prev_action)
            value = self.terminal(state_copy, player, prev_action)
            if value is not None:
                return value, None
            
            player = -player

        if player == 1:
            best_value = -float("inf")
            best_action = None
            for action in self.get_available_actions(state_copy):
                candidate_value, _ = self.get_state_action_value(state_copy, player, action, alpha, beta)
                if candidate_value > best_value:
                    best_value = candidate_value
                    best_action = action

                alpha = max(alpha, candidate_value)
                if beta <= alpha:
                    break
        else:
            best_value = float("inf")
            best_action = None
            for action in self.get_available_actions(state_copy):
                candidate_value, _ = self.get_state_action_value(state_copy, player, action, alpha, beta)
                if candidate_value < best_value:
                    best_value = candidate_value
                    best_action = action

                beta = min(beta, candidate_value)
                if beta <= alpha:
                    break

        return best_value, best_action

    def get_action(self, logic_grid, player):
        minimax_logic_grid = deepcopy(logic_grid)
        result = self.get_state_action_value(minimax_logic_grid, player)[1]
        return result
