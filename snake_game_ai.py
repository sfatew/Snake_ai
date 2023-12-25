import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np
import time

pygame.init()
font = pygame.font.Font('arial.ttf', 25)
#font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)
GREEN = (0 , 255 , 0 )

BLOCK_SIZE = 20
SPEED = 999999

class SnakeGameAI:
    
    def __init__(self, w=720, h=480):
        #dimensions
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))    #left=0, top=0
        pygame.display.set_caption('Snake game')
        # FPS (frames per second) controller
        self.fps = pygame.time.Clock()
        self.reset()

    def reset(self):            
        # set the game to its init game state
        self.direction = Direction.RIGHT
        
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        
        self.lensnake=len(self.snake)
        
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_interation=0     # number of step travel till now

    def _place_food(self):
        #x, y are the left and top edge the food block
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
        
    def play_step(self, action):
        self.frame_interation+=1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head) #insert the new position of the head at the beginning of the list

        # 3. check if game over
        reward=0
        game_over = False
        if self.is_collision() or self.frame_interation > 100*len(self.snake):
        # game over when there is a collision or the snake havent improve for too long
        # get addition 100 more step each time eat a food
            game_over = True
            reward=-10
            return reward,game_over, self.score
            
        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self.lensnake += 1
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.fps.tick(SPEED)
        # 6. return game over and score
        return reward,game_over, self.score
    
    def is_collision(self, pt=None):
        if pt==None:
            pt=self.head
        # hits boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            # print(self.head)
            # time.sleep(2)
            return True
        # hits itself
        if pt in self.snake[1:]:
            return True
        
        return False
        
    def _update_ui(self):   #update the display of the game
        self.display.fill(BLACK)
        
        for pt in self.snake:   #display the snake(with darker color on the outer of the block)
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE)) #draw a rectangle: (on plane, color, (left,top,widht,height))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))

        pygame.draw.rect(self.display, GREEN, pygame.Rect(self.head.x, self.head.y, BLOCK_SIZE, BLOCK_SIZE))
        #display the food 
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()
        
    def _move(self, action):
        #action= [straight, turn right, turn left]

        clock_wise = [Direction.RIGHT,Direction.DOWN,Direction.LEFT,Direction.UP] #direction order when do a clock wise turn
        idx= clock_wise.index(self.direction)   #find index of current direction in clock_wise

        if np.array_equal(action, [1,0,0]): #no change
            new_dir = clock_wise[idx]       
        elif np.array_equal(action, [0,1,0]): #right turn r->d->l->u
            next_idx = (idx+1)%4    #go to the start of the list when exceed the end
            new_dir = clock_wise[next_idx]       
        else:   #left turn
            next_idx = (idx-1)%4    
            new_dir = clock_wise[next_idx]  

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)
            
