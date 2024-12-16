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

# experiments/graph_creation_vision_local_search_exp.py
import pygame
import logging
from game.game import Game
from utils.snake import Snake, Food, BigFood
from utils.search import Node, SnakeProblem
from utils.constants import *
from experiments.state_creation import CreateState
from game.game_save_manager import GameSaveManager
from experiments.core import *

# ANSI escape codes for colors
ANSIRESET = "\033[0m"
ANSIRED = "\033[91m"
ANSIGREEN = "\033[92m"
ANSIYELLOW = "\033[93m"
ANSIBLUE = "\033[94m"
ANSICYAN = "\033[96m"
ANSIWHITE = "\033[97m" 

# Function to apply color
def color_text(text, color):
    return f"{color}{text}{ANSIRESET}"

logger = logging.getLogger("Experimental Log")
logger.setLevel(logging.DEBUG)
formater = logging.Formatter('%(asctime)s - %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formater)
logger.addHandler(ch)

class GraphCreationVisionLocalSearch_Exp(ExperimentState):
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        if game.previous_state and isinstance(game.previous_state, CreateState):
             self.state = game.previous_state.state
             GameSaveManager.restore_state(self.state, self)
        self.big_food = BigFood(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT), 2)
        self.node_size = self.compute_node_size()
        self.game_hud = game.game_hud
        self.rand_fact = 0
        self.initialize()

    def cost(self, node):
        return self.problem.heuristic1(node.state) + self.problem.heuristic2(node.state)

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
        if game.controls.is_just_pressed("S"): # s to save state
            state = GameSaveManager.capture_state(self)
            GameSaveManager.save_state(state) # save to json
        if game.controls.is_just_pressed("L"): # l to load state
            state = GameSaveManager.load_state()
            if state:
                GameSaveManager.restore_state(state, self) # restore to game
                self.initialize()
            else: game.display_message("There is nothing to load, pleas save with S", duration=4000)
    

    def draw(self, game: Game):
        time = pygame.time.get_ticks() / 1000
        game.window.fill(BLACK)  # White background
        self.draw_grid(game.window)
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
        self.node.draw_solution(window, LIGHT_GRAY)

    def update(self, game: Game):
        pass

    def step(self, game: Game):
        # Get solution and move snake
        next_node = self.find_solution()
        if next_node == None:
            state = GameSaveManager.capture_state(self)
            GameSaveManager.save_state(state) # save to json
            from ui.game_ui import GameOverState
            game.change_state(GameOverState())
        else: self.snake.set_direction(next_node.action)
        self.snake.move()

        if self.snake.is_eating_food(self.food):
            self.food.replace(self.snake)
            self.snake.grow(3)
            self.initialize()

        game.clock.tick(game.game_update_rate)

    def find_solution(self):
        # Remove the plotting from here and keep only the solution finding logic
        new_snake = list([self.snake.head.cell] + [sbo.cell for sbo in self.snake.tail])
        neighbours = ocupiable_cells(self.node.expand(self.problem), new_snake)
        self.node = self.select_best_amoungst(neighbours)
        return self.node

    def initialize(self):
        self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
        self.node = Node(self.problem.init_pos)
        self.updates = 1

    def select_best_amoungst(self, neighbours: list):
        if neighbours:
            best_node = neighbours.pop()
            best_cost = self.cost(best_node)

            for child_node in neighbours:
                child_cost = self.cost(child_node)
                logger.debug(f"{color_text("Child node", ANSIWHITE)}: {child_node} has cost: {child_cost}")
                if child_cost <= best_cost:
                    logger.debug(f"{color_text("Chosen node", ANSICYAN)}: {child_node} has cost: {child_cost} < {best_cost}")
                    best_node = child_node
                    best_cost = child_cost
            return best_node
        return None