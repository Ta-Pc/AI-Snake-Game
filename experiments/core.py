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
from game.game import Game
from game.game_state import GameState
from utils.constants import *

class ExperimentState(GameState):
    def enter(self, game: Game):
        game.display_message("This is an experiment", duration=4000)

    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed(game.controls.ESCAPE):
            from ui.game_ui import ExperimentSelectState
            game.change_state(ExperimentSelectState())
        elif game.controls.is_just_pressed(game.controls.SPACE):
            from ui.game_ui import PauseState
            game.change_state(PauseState())

    def update(self, game: Game):
        game.clock.tick(game.game_update_rate)
    
    def draw(self, game: Game):
        time = pygame.time.get_ticks() / 1000
        game.window.fill(BLACK)
        game.draw_message()
    
    def exit(self, game: Game):
        game.previous_state = self

def move(head_cell, parent_snake):
    """Add head, remove tail, return child that moved"""
    return list([head_cell] + parent_snake[:-1])

def eat(head_cell, parent_snake):
    """Add head, return child that grew an inch"""
    return list([head_cell] + parent_snake)

def ocupiable_cells(nodes, parent_snake: list):
    """Return nodes that avoids the snake body"""
    return list([node for node in nodes if node.state not in parent_snake])

def ocupiable_cells2(nodes, dir):
    """Return nodes that avoid going in the direction opposing dir"""

    opp_direction_map = {
            'UP': 'DOWN',
            'RIGHT': 'LEFT',
            'DOWN': 'UP',
            'LEFT': 'RIGHT'
        }
    accepteble = list([node for node in nodes if node.action != opp_direction_map[dir]])
    return accepteble