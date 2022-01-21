import numpy as np
import random

from settings.constants import DIRECTIONS, SNAKE_SIZE, DEAD_REWARD, \
    MOVE_REWARD, EAT_REWARD, FOOD_BLOCK, WALL
from .snake import Snake


class World(object):
    def __init__(self, size, custom, start_position, start_direction_index, food_position):
        """
        @param size: tuple
        @param custom: bool
        @param start_position: tuple
        @param start_direction_index: int
        @param food_position: tuple
        """
        # for custom init
        self.custom = custom
        self.start_position = start_position
        self.start_direction_index = start_direction_index
        self.food_position = food_position
        # rewards
        self.DEAD_REWARD = DEAD_REWARD
        self.MOVE_REWARD = MOVE_REWARD
        self.EAT_REWARD = EAT_REWARD
        self.FOOD = FOOD_BLOCK
        self.WALL = WALL
        self.DIRECTIONS = DIRECTIONS
        # Init a numpy matrix with zeros of predefined size
        self.size = size
        self.world = np.zeros(size)
        # Fill in the indexes gaps to add walls to the grid world
        self.world[0] = self.WALL  # ADDED BY STUDENT
        self.world[-1] = self.WALL  # ADDED BY STUDENT
        self.world[1:, 0] = self.WALL  # ADDED BY STUDENT
        self.world[1:, -1] = self.WALL  # ADDED BY STUDENT
        # Get available positions for placing food (choose all positions where world block = 0)
        self.available_food_positions = set(zip(*np.where(self.world == 0)))
        # Init snake
        self.snake = self.init_snake()
        # Set food
        self.init_food()

    def init_snake(self):
        """
        Initialize a snake
        """
        if not self.custom:
            # choose a random position between [SNAKE_SIZE and SIZE - SNAKE_SIZE]
            start_position = (random.randint(SNAKE_SIZE, self.size[0] - SNAKE_SIZE),
                              random.randint(SNAKE_SIZE, self.size[1] - SNAKE_SIZE))  # ADDED BY STUDENT
            # choose a random direction index
            start_direction_index = random.randint(0,3)  # ADDED BY STUDENT              !
            new_snake = Snake(start_position, start_direction_index, SNAKE_SIZE)
        else:
            new_snake = Snake(self.start_position, self.start_direction_index, SNAKE_SIZE)
        return new_snake

    def init_food(self):
        """
        Initialize a piece of food
        """
        snake = self.snake if self.snake.alive else None
        # Update available positions for food placement considering snake location
        available_food_positions = list(zip(*np.where(self.world == 0))) # ADDED BY STUDENT
        for i in available_food_positions:
            for j in self.snake.blocks:
                if list(i) == j:
                    available_food_positions.remove(i)

        #self.snake.blocks
        if not self.custom:
            # Choose a random position from available
            chosen_position = random.sample(available_food_positions, 1)[0]  # ADDED BY STUDENT
        else:
            chosen_position = self.food_position
            # Code needed for checking your project. Just leave it as it is
            try:
                available_food_positions.remove(chosen_position)
            except:
                if (self.food_position[0] - 1, self.food_position[1]) in available_food_positions:
                    chosen_position = (self.food_position[0] - 1, self.food_position[1])
                else:
                    chosen_position = (self.food_position[0] - 1, self.food_position[1] + 1)
                available_food_positions.remove(chosen_position)
        self.world[chosen_position[0], chosen_position[1]] = self.FOOD
        self.food_position = chosen_position

    def get_observation(self):
        """
        Get observation of current world state
        """
        obs = self.world.copy()
        snake = self.snake if self.snake.alive else None
        if snake:
            for block in snake.blocks:
                obs[block[0], block[1]] = snake.snake_block
            # snakes head
            obs[snake.blocks[0][0], snake.blocks[0][1]] = snake.snake_block + 1
        return obs

    def move_snake(self, action):
        """
        Action executing
        """
        # define reward variable
        reward = 0
        # food needed flag
        new_food_needed = False
        # check if snake is alive
        if self.snake.alive:
            # perform a step (from Snake class)
            new_snake_head, old_snake_tail = self.snake.step(action)
            # Check if snake is outside bounds
            if abs(new_snake_head[0] - 32) > 31 or abs(new_snake_head[1] - 32) > 31 or abs(new_snake_head[0]) - 31 == 0 or abs(new_snake_head[1]) - 31 == 0:  # ADDED BY STUDENT
                self.snake.alive = False
            # Check if snake eats itself
            if len(self.snake.blocks) == 4:
                future_head = [self.snake.blocks[0][i] + DIRECTIONS[abs(self.snake.current_direction_index - 3)][j] for i in
                            range(len(self.snake.blocks[0])) for j in range(len(DIRECTIONS[self.snake.current_direction_index])) if
                            i == j]
                #print("self.snake.blocks", self.snake.blocks)
                #print("future_head", future_head)
                #print("self.snake.blocks[-1]", self.snake.blocks[-1])
                if future_head == self.snake.blocks[-1]:
                    self.snake.alive = False
            else:
                if new_snake_head in self.snake.blocks[1:]:
                    self.snake.alive = False
            #  Check if snake eats the food
            if new_snake_head[0] == self.food_position[0] and new_snake_head[1] == self.food_position[1]:  # ADDED BY STUDENT
                # Remove old food
                self.snake.blocks.append(self.food_position)
                self.world[self.food_position[0]][self.food_position[1]] = 0 # ADDED BY STUDENT
                # Add tail again
                #new_tail = [self.snake.blocks[-1][i] - DIRECTIONS[self.snake.current_direction_index][j] for i in
                #            range(len(self.snake.blocks[0])) for j in range(len(DIRECTIONS[self.snake.current_direction_index])) if
                #            i == j]  # ADDED BY STUDENT
                #self.snake.blocks.append(self.food_position)
                #print("self.snake.blocks", self.snake.blocks)
                #print("type(self.snake.blocks)", type(self.snake.blocks))
                #print("len(self.snake.blocks)", len(self.snake.blocks))

                # Request to place new food
                new_food_needed = True  # ADDED BY STUDENT
                reward += 1  # ADDED BY STUDENT
            elif self.snake.alive:
                # Didn't eat anything, move reward
                reward = self.MOVE_REWARD
        # Compute done flag and assign dead reward
        done = not self.snake.alive
        reward = reward if self.snake.alive else self.DEAD_REWARD
        # Adding new food
        if new_food_needed:
            self.init_food()
        return reward, done, self.snake.blocks