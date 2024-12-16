"""Copyright 2024 Sipho Zuma

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import pygame
import random
from collections import deque
from game.game import Game
from utils.snake import Snake, Food, BigFood
from utils.search import Node, SnakeProblem, PriorityQueue
from utils.constants import *
from experiments.core import *

class GraphCreationVisionBFS_Exp_Origional(ExperimentState):
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.big_food = BigFood(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT), 2)
        self.node_size = self.compute_node_size()
        self.rand_fact = 0
        self.f = self.f
        self.initialize()

    def f(self, items):
        node, _ = items
        randomness = random.uniform(1 - self.rand_fact, 1 + self.rand_fact)
        
        return self.problem.path_cost(node) + self.problem.heuristic1(node.state) * randomness
    
    def compute_node_size(self):
        self.offset = (CELL_SIZE // 2, CELL_SIZE // 2)
        return self.offset[0] - 5

    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)
            elif game.controls.is_pressed(game.controls.SPACE):
                self.step(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed(game.controls.ESCAPE):
            from ui.game_ui import ExperimentSelectState
            game.change_state(ExperimentSelectState())
        elif game.controls.is_pressed(game.controls.SELECT):
            self.step(game)
        elif game.controls.is_just_pressed(game.controls.UP):
            game.game_update_rate += 2
        elif game.controls.is_just_pressed(game.controls.DOWN):
            game.game_update_rate -= 2

    def draw(self, game: Game):
        time = pygame.time.get_ticks() / 1000
        game.window.fill(BLACK)  # White background
        #self.draw_map(game.window)
        self.draw_grid(game.window)
        self.draw_edges(game.window)
        self.draw_step_count(game.window)
        self.draw_nodes(game.window)
        self.food.draw(game.window)
        self.snake.draw(game.window, time)

    def draw_grid(self, window):
        # Draw grid lines here
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(window, WHITE, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(window, WHITE, (0, y), (SCREEN_WIDTH, y))

    def draw_nodes(self, window):
        # Draw nodes here, using different colors for different types
        if self.solution:
            self.node.draw_solution(window, LIGHT_GRAY)
        else:
            #return
            if self.reached:
                for _, node in self.reached.items():
                    node.draw(self.offset, window, BLUE, self.node_size, 5)

            for item in self.frontier.heap:
                item[1][0].draw(self.offset, window, RED, self.node_size, 15)


    def draw_edges(self, window):
        # Draw edges between nodes here
        pass

    def draw_step_count(self, window):
        # Draw the step count on the screen
        pass

    def draw_map(self, window):
        surface = self.graph.graph_dict
        for x, y in surface:
            rect = (x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(window, DARK_GRAY, rect)

    def update(self, game: Game):
        pass

    def step(self, game: Game):
        # Simulating a star algorithm
        for _ in range(self.updates):
            self.solution = self.find_solution(game)
            if self.solution: break

        self.plot_1d_cost_landscape(self.snake, self.food, self.problem, CELL_SIZE)

        if self.solution:
            action = self.solution.popleft()
            self.snake.set_direction(action)
            self.snake.move()

        if self.snake.is_eating_food(self.food):
            self.food.replace(self.snake)
            self.snake.grow(3)
            self.initialize()

        game.clock.tick(game.game_update_rate)

    def exit(self, game: Game):
        pass

    def find_solution(self, game: Game):
        if self.frontier and not self.solution:
            self.node, parent_snake = self.frontier.pop()

            if  self.problem.is_goal(self.node.state):
                self.updates = 0
                return deque(self.node.solution())
            else:
                for child in ocupiable_cells(self.node.expand(self.problem), parent_snake):
                    state = child.state
                    if state not in self.reached or child.path_cost < self.reached[state].path_cost:
                        child_snake = move(state, parent_snake)
                        self.reached[state] = child
                        self.frontier.append((child, child_snake))
        return None
    
    def initialize(self):
        init_snake = list([self.snake.location] + [sbo.cell for sbo in self.snake.tail])
        self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
        self.node = Node(self.problem.init_pos)
        self.frontier = PriorityQueue('min', self.f)
        self.frontier.append((self.node, init_snake))
        self.reached = {self.node.state : self.node}
        self.solution = deque()
        self.updates = 1