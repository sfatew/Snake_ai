import torch
import random
import numpy as numpy
from snake_game_ai import SnakeGameAI, Direction, Point
from collections import deque   #double-end queue

Max_Memory = 100000
Batch_size = 1000
LR = 0.001      #learning rate 

class Agent:
    def __init__(self):
        self.n_games = 0    #number of game
        self.epsilon = 0    #randomness control
        self.gamma = 0      #discount rate
        self.memory = deque(maxlen=Max_Memory)  #when the memory was exceeded, auto popleft()
        #model, trainer


    def get_state(self, game):
        pass

    def remember(self, state, action, reward, next_state, game_over):
        pass

    def train_long_memory(self):
        pass

    def train_short_memory(self,state, action, reward, next_state, game_over):
        pass

    def get_action(self, state):
        pass


def train():
    plot_scores=[]          #keep track of the scores
    plot_mean_score = []    #mean of scores
    total_score = 0
    record = 0              #best score
    agent = Agent()
    game = SnakeGameAI
    while True:
        # get old state
        state_old = agent.get_state(game)

        #get move
        final_move = agent.get_action(state_old)

        #perform move and get new state
        reward, game_over, score = game.play_step(final_move)

        state_new = agent.get_state(game)

        # train short memo
        agent.train_short_memory(state_old, final_move, reward, state_new, game_over)

if __name__=='__main__':
    train()