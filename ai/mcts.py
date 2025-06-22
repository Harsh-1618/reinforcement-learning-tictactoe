'''
Code for MCTS algorithm for 2D and Infinite 2D tictactoe with any 2D grid size.
Unlike MiniMax, MCTS does not depend highly on the grid size, rather it depends on the 
search size, meaning it can be used even for 9x9 grids with appropriate search size.
It's needless to say that the AI is not that strong for a small value of search size.
A value of 1000 should be sufficient for our games.
While this implementation is tailored for tictactoe, it can be easily generalized to any adversarial game.
'''

import random
import numpy as np
from copy import deepcopy


class MCTS_TicTacToe:
    def __init__(self, ttt_dim):
        self.ttt_dim = ttt_dim

    @staticmethod
    def get_next_state(state, action, player):
        state[action] = player
        return state

    @staticmethod
    def get_valid_moves(state):
        zero_places = np.where(state==0)
        return list(zip(zero_places[0], zero_places[1]))

    @staticmethod
    def check_win(state, action, ttt_dim):
        if action is None: # will happen for the root Node and we know that no one has won on the root node since no one has played yet
            return False
        row_val, col_val = action
        player = state[action]

        return np.sum(state[row_val,:]) == player * ttt_dim or \
        np.sum(state[:,col_val]) == player * ttt_dim or \
        np.sum(np.diag(np.flip(state, axis=0))) == player * ttt_dim or \
        np.sum(np.diag(state)) == player * ttt_dim

    def get_value_and_terminated(self, state, action):
        if MCTS_TicTacToe.check_win(state, action, self.ttt_dim): # someone won
            return 1, True
        if len(MCTS_TicTacToe.get_valid_moves(state)) == 0: # game tied
            return 0, True
        return 0, False # game continuing

    @staticmethod
    def get_opponent(player):
        return -player

    @staticmethod
    def get_opponent_value(value):
        return -value

    @staticmethod
    def change_perspective(state, player):
        return state*player


class Node:
    def __init__(self, game, args, state, parent=None, action_taken=None): # None, None for the root node
        self.game = game
        self.args = args
        self.state = state
        self.parent = parent
        self.action_taken = action_taken
        
        self.children = [] # children of the node
        self.expandable_moves = game.get_valid_moves(state)

        self.visit_count = 0
        self.value_sum = 0

    def is_fully_expanded(self):
        # if the node has terminated we can't select past it cause the game has ended already
        return (len(self.expandable_moves) == 0) and (len(self.children) > 0)

    def get_ucb(self, child):
        # the way we have implemented the game, we can have both -ve and +ve value_sum. making the range of value_sum between -1 and 1.
        # but we want the range to be between 0 and 1 to interpret them like probabilities. to doing that.
        q_value = ((child.value_sum/child.visit_count) + 1)/2 # between 0 and 1
        # this q_value is what the child thinks of itself and not how it should be perceived by it's parent.
        # cause in tictactoe, the child and parent are two different players, so as a parent, we would like to 
        # select a child that itself has a very low value because as an opponent we would like to place them in a bad situation.
        q_value = 1 - q_value # so if q_value of child is close to 0, we would like to pick that! 
        return q_value + self.args["C"] * np.sqrt(np.log(self.visit_count)/child.visit_count)
        
    def select(self):
        # we loop over all the children in our node and return the child node having highest UCB score
        best_child = None
        best_ucb = -np.inf

        for child in self.children:
            ucb = self.get_ucb(child)
            if ucb > best_ucb:
                best_ucb = ucb
                best_child = child
        return best_child

    def expand(self):
        action = random.choice(self.expandable_moves)
        self.expandable_moves.remove(action)

        child_state = self.game.get_next_state(self.state.copy(), action, 1)
        # the way we will program MCTS is that we will never change the player and we will never give the information about the player to the node
        # rather we will change the state of our child so that it is perceived by the opponent's player. this makes the logic much easier.
        # it also makes the code valid for single player games so thats very NICE!
        child_state = self.game.change_perspective(child_state, player=-1) # turning +1 to -1 and viceversa

        child = Node(self.game, self.args, child_state, self, action)
        self.children.append(child)
        return child

    def simulate(self):
        value, is_terminated = self.game.get_value_and_terminated(self.state, self.action_taken)
        value = self.game.get_opponent_value(value)

        if is_terminated:
            return value

        rollout_state = self.state.copy()
        rollout_player = 1

        while True:
            valid_moves = self.game.get_valid_moves(rollout_state)
            action = random.choice(valid_moves)
            rollout_state = self.game.get_next_state(rollout_state, action, rollout_player)
            value, is_terminated = self.game.get_value_and_terminated(rollout_state, action)

            if is_terminated: 
                if rollout_player == -1:
                    value = self.game.get_opponent_value(value)
                return value

            rollout_player = self.game.get_opponent(rollout_player)

    def backpropagate(self, value):
        self.value_sum += value
        self.visit_count += 1

        value = self.game.get_opponent_value(value)

        if self.parent is not None:
            self.parent.backpropagate(value)


class MCTS:
    def __init__(self, ttt_dim):
        self.game = MCTS_TicTacToe(ttt_dim)
        self.args = {"C":1.41, "num_searches":1000}

    def search(self, state):
        # define root:
        root = Node(self.game, self.args, state)

        for search in range(self.args["num_searches"]):
            node = root
            
            # selection
            while node.is_fully_expanded():
                node = node.select()
            
            # expansion
            # so we have reached a leaf node or a terminal one
            value, is_terminated = self.game.get_value_and_terminated(node.state, node.action_taken)
            # note that the 'action_taken' of a node is the action taken by the parent of the node and not by the node itself
            # so it was the action taken by the opponent of the node
            # so if we have reached a terminal state with a win, then it would be the parent that has won and not the node
            # to read the value as per the node's perspective, we will have to change it
            value = self.game.get_opponent_value(value)

            if not is_terminated:
                node = node.expand()

                # simulation
                # we perform random actions until we have reached a terminal node and then we look at the value/final outcome of the game and
                # return that to back propagate
                value = node.simulate()
                
            # backpropagation
            node.backpropagate(value)

        # return visit counts of children of root node (shouldn't it be win ratio?)
        best_visit_count = -float("inf") # instead of child with max visit count, you can also pick child with max win ratio (value_sum/visit_count)
        best_action = None
        for child in root.children: # we can normalize the visit_counts of all childrens to get probability dist., but we want max, so skipping that
            if child.visit_count > best_visit_count:
                best_visit_count = child.visit_count
                best_action = child.action_taken
        return best_action

    def get_action(self, logic_grid, player):
        mcts_logic_grid = deepcopy(logic_grid)
        if player == -1:
            mcts_logic_grid = self.game.change_perspective(mcts_logic_grid, player) # player is -1
        action = self.search(mcts_logic_grid)
        return action