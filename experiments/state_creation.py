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

# experiments/state_creation.py
import pygame
from game.game import Game
from experiments.core import ExperimentState
from utils.constants import *
from game.game_save_manager import GameSaveManager

class CreateState(ExperimentState):
    """A state for interactively creating a game state using mouse input."""

    def enter(self, game: Game):
        self.game = game
        self.phase = 1 # 1 for head, 2 for food, 3 for tail
        self.snake_head = None
        self.snake_tail = []
        self.food = None
        self.snake_length = self.get_snake_length() # ask for snake length
        self.current_tail_pos = 0 # Current number of tail segments
        self.state = None
        game.display_message(self.get_prompt(), duration=4000)

    def get_snake_length(self):
      while True:
          try:
            length = int(input("Enter the length of the snake you want: "))
            if length >= 0: return length
            else:
              print("Please enter a positive number")
          except ValueError:
              print("Invalid input, please enter an integer")

    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_actions(game)
            

    def _handle_actions(self, game: Game):
      if game.controls.is_just_pressed(game.controls.ESCAPE):
          from ui.game_ui import ExperimentSelectState
          game.change_state(ExperimentSelectState())
      elif game.controls.is_just_pressed(game.controls.SELECT): # Select to complete phase
         if self.phase == 3 and self.current_tail_pos == self.snake_length:
             self._finalize_state(game) # Move to experiment phase
      elif game.controls.is_just_pressed(game.controls.MOUSE_LEFT):
         self._handle_mouse_click(game)

    def update(self, game: Game):
        game.clock.tick(game.menu_update_rate)
    
    def draw(self, game: Game):
        game.window.fill(BLACK)  # White background
        self.draw_grid(game.window)
        if self.snake_head:
           self.draw_snake_head(game.window)
        if self.snake_tail:
           self.draw_snake_tail(game.window)
        if self.food:
           self.draw_food(game.window)
        game.draw_message()

    def draw_grid(self, window):
      # Draw grid lines here
      for x in range(0, SCREEN_WIDTH, CELL_SIZE):
          pygame.draw.line(window, WHITE, (x, 0), (x, SCREEN_HEIGHT))
      for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
          pygame.draw.line(window, WHITE, (0, y), (SCREEN_WIDTH, y))

    def draw_snake_head(self, window):
       rect = (self.snake_head[0], self.snake_head[1], CELL_SIZE, CELL_SIZE)
       pygame.draw.rect(window, BRIGHT_MAGENTA, rect)
    
    def draw_snake_tail(self, window):
       for pos in self.snake_tail:
            rect = (pos[0], pos[1], CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(window, BRIGHT_LIME, rect)

    def draw_food(self, window):
       pygame.draw.circle(window, BRIGHT_GOLD, 
                       (self.food[0] + CELL_SIZE//2, self.food[1] + CELL_SIZE//2), CELL_SIZE//2)

    def get_prompt(self):
      if self.phase == 1: return "Place the snake head by clicking on screen"
      if self.phase == 2: return "Place the food by clicking on screen"
      if self.phase == 3: return "Place the snake tail by clicking on screen, press SELECT when done"

    def _handle_mouse_click(self, game: Game):
        """Handle mouse clicks to place snake head, tail, and food."""
        mouse_x, mouse_y = game.controls.mouse_pos
        cell_x = (mouse_x // CELL_SIZE) * CELL_SIZE
        cell_y = (mouse_y // CELL_SIZE) * CELL_SIZE
        
        click_pos = (cell_x, cell_y)

        if self.phase == 1:
           self.snake_head = click_pos
           self.phase = 2
        elif self.phase == 2:
           if click_pos != self.snake_head:
               self.food = click_pos
               self.phase = 3
        elif self.phase == 3:
            if self.current_tail_pos == 0:
                #If it's the first tail segment, check against the head
                 if self.is_valid_neighbor(click_pos, self.snake_head) and self.current_tail_pos < self.snake_length:
                      self.snake_tail.append(click_pos)
                      self.current_tail_pos += 1
            elif self.current_tail_pos > 0 and self.current_tail_pos < self.snake_length:
                if self.is_valid_neighbor(click_pos, self.snake_tail[-1]) and self.current_tail_pos < self.snake_length:
                  self.snake_tail.append(click_pos)
                  self.current_tail_pos += 1

        game.display_message(self.get_prompt(), duration=4000)

    def is_valid_neighbor(self, click_pos, prev_pos):
      """Check if the click_pos is a valid neighbor of the previous segment"""
      dx = click_pos[0] - prev_pos[0]
      dy = click_pos[1] - prev_pos[1]
      return (abs(dx) == CELL_SIZE and dy == 0) or (abs(dy) == CELL_SIZE and dx == 0)

    def _finalize_state(self, game):
        self.state = GameSaveManager.create_state(self.snake_head, self.snake_tail, "UP", self.food, 0)
        from ui.game_ui import GraphCreationVisionLocalSearch_Exp
        game.change_state(GraphCreationVisionLocalSearch_Exp())
    
    def exit(self, game: Game):
      game.previous_state = self