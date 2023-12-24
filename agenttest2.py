import torch
import random
import numpy as np
from snake_game_ai import SnakeGameAI, Direction, Point
from collections import deque   #double-end queue
from plot import plot
from model import Linear_QNet, QTrainer
import os
from itertools import islice

Max_Memory = 100000
Batch_size = 1024
LR = 0.001      #learning rate 

class Agent:
    def __init__(self):
        self.n_games = 0    #number of game
        self.epsilon = 0    #randomness control
        self.gamma = 0.9      #discount rate
        self.memory = deque(maxlen=Max_Memory)  #when the memory was exceeded, auto popleft()
        self.model = Linear_QNet(14, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.record = 0              #best score

    def is_danger_left(self,game):
        new_pt = game.snake[0]
        count = 0
        while not game.is_collision(new_pt):
            new_pt = Point(new_pt.x - 20, new_pt.y) 
            count +=1
            # if new_pt in game.snake[1:]:    
            #     return True
            # else: 
            #     continue
        return count/game.w
        # return False
    
    def is_danger_right(self,game):
        new_pt = game.snake[0]
        count = 0
        while not game.is_collision(new_pt):
            new_pt = Point(new_pt.x + 20, new_pt.y)
            count +=1 
            # if new_pt in game.snake[1:]:    
            #     return True
            # else: 
            #     continue
        return count/game.w
        # return False
    
    def is_danger_up(self,game):
        new_pt = game.snake[0]
        count = 0
        while not game.is_collision(new_pt):
            new_pt = Point(new_pt.x, new_pt.y - 20)
            count +=1 
            # if new_pt in game.snake[1:]:    
            #     return True
            # else: 
            #     continue
        return count/game.h
        # return False
    
    def is_danger_down(self,game):
        new_pt = game.snake[0]
        count = 0
        while not game.is_collision(new_pt):
            new_pt = Point(new_pt.x, new_pt.y + 20) 
            count +=1          
        #     if new_pt in game.snake[1:]:    
        #         return True
        #     else: 
        #         continue

        # return False
        
        return count/game.h

    def get_state(self, game):
        head = game.snake[0]

        # check 1 block in each direction
        point_l = Point(head.x - 20, head.y)
        point_r = Point(head.x + 20, head.y)
        point_u = Point(head.x, head.y - 20)
        point_d = Point(head.x, head.y + 20)
        
        # the current direction of the snake    
        # return True or False
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        if dir_l:
            danger_straight_dist =
            danger_right_dist =
            danger_sleft_dist =

        state = [
            # Length of the snake
            # len(game.snake),

            # Danger:  body ahead
            # Danger straight
            (dir_l and Agent.is_danger_left(head,game)) or
            (dir_r and Agent.is_danger_right(head,game)) or
            (dir_u and Agent.is_danger_up(head,game)) or
            (dir_d and Agent.is_danger_down(head,game)),
            # Danger right
            (dir_u and Agent.is_danger_right(head,game)) or 
            (dir_d and Agent.is_danger_left(head,game)) or 
            (dir_l and Agent.is_danger_up(head,game)) or 
            (dir_r and Agent.is_danger_down(head,game)),
            # Danger left
            (dir_d and Agent.is_danger_right(head,game)) or 
            (dir_u and Agent.is_danger_left(head,game)) or 
            (dir_r and Agent.is_danger_up(head,game)) or 
            (dir_l and Agent.is_danger_down(head,game)),


            # danger in 1 block
            # Danger straight
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            # Danger right
            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)),

            # Danger left
            (dir_d and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)),

            # Current direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y  # food down
            ]

        return np.array(state, dtype=int)   #dtype int turn True to 1 and False to 0

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > Batch_size:
            # mini_sample = list(islice(self.memory,len(self.memory)-Batch_size,len(self.memory))) # list of tuples
            mini_sample = random.sample(self.memory, Batch_size)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)    #unzip the ele from mini_sample
        self.trainer.train_step(states, actions, rewards, next_states, dones)


    def train_short_memory(self,state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
         #random moves: exploration/exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            #explporation
            move = random.randint(0, 2) #chose randomly the direction to go
            final_move[move] = 1
        else:
            #explotation
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)         # put state0 into forward in modal 
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

    def exploit_act(self,state):
        final_move = [0,0,0]
        state0 = torch.tensor(state, dtype=torch.float)
        prediction = self.model(state0)         # put state0 into forward in modal 
        move = torch.argmax(prediction).item()
        final_move[move] = 1

        return final_move

def train():
    plot_scores=[]          #keep track of the scores
    plot_mean_scores = []    #mean of scores
    total_score = 0
    agent = Agent()
    game = SnakeGameAI()


    if os.path.exists('model/checkpoint_3.pth'):
        load_checkpoint = torch.load('model/checkpoint_3.pth')
        # print(load_checkpoint)

        agent.n_games = load_checkpoint["n_games"]
        agent.record = load_checkpoint["record"]
        agent.model.load_state_dict(load_checkpoint["model_state"])
        agent.trainer.optimizer.load_state_dict(load_checkpoint["optim_state"])

        # print(agent.record)
        # print(agent.n_games)

    while True:
        # get old state
        state_old = agent.get_state(game)

        #get move
        final_move = agent.get_action(state_old)
        # final_move = agent.exploit_act(state_old)

        #perform move and get new state
        reward, game_over, score = game.play_step(final_move)

        state_new = agent.get_state(game)

        # train short memo
        agent.train_short_memory(state_old, final_move, reward, state_new, game_over)

        # remember
        agent.remember(state_old, final_move, reward, state_new, game_over)

        if game_over:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > agent.record:
                agent.record = score
                # save the best record
                model_folder_path = './model'
                if not os.path.exists(model_folder_path):
                    os.makedirs(model_folder_path)

                file_name = os.path.join(model_folder_path, 'model_3.pth')

                save_best = {
                    "model_state": agent.model.state_dict(),
                    "optim_state": agent.trainer.optimizer.state_dict()
                }

                torch.save(save_best, file_name) 


            print('Game', agent.n_games, 'Score', score, 'Record:', agent.record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / len(plot_scores)
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

        #checkpoint
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)

        file_name = os.path.join(model_folder_path, 'checkpoint_3.pth')

        checkpoint = {
            "n_games": agent.n_games,
            "record": agent.record,
            "model_state": agent.model.state_dict(),
            "optim_state": agent.trainer.optimizer.state_dict()
        }

        torch.save(checkpoint, file_name) 

def run():
    agent = Agent()
    game = SnakeGameAI()
    agent.record = 0              #best score

    if os.path.exists('.model/model_3.pth'):
            load_save = torch.load('.model/model_3.pth')
            agent.model.load_state_dict(load_save["model_state"])
            agent.trainer.optimizer.load_state_dict(load_save["optim_state"])

    while True:
        # get old state
        state_old = agent.get_state(game)
        print(state_old)

        #get move
        final_move = agent.exploit_act(state_old)
        # final_move = agent.exploit_act(state_old)

        #perform move and get new state
        reward, game_over, score = game.play_step(final_move)

        state_new = agent.get_state(game)
        print(state_new)

        if game_over:
            print('Game', agent.n_games, 'Score', score, 'Record:', agent.record, 'Frame_iteration', game.frame_iteration)
            # break


if __name__=='__main__':

    train()
    # run()
