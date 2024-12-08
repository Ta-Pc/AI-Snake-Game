"""Copyright 2024 Sipho Zuma

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

from Game import Game
from GameState import GameState
from Constants import *
from Snake import *
from Search import *

#*************************************************************************************************************************
# Human Playing Snake
#*************************************************************************************************************************

class PlayingState(GameState):
    def enter(self, game: Game):
        self.eat_count = 0
    
    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)

    def _handle_actions(self, game: Game):
        for direction in game.controls.just_pressed:
            game.snake.set_direction(direction)
            break
        if game.controls.is_just_pressed('ESCAPE'):
            from GameUI import MenuState
            game.change_state(MenuState())
        elif game.controls.is_just_pressed('SPACE'):
            from GameUI import PauseState
            game.change_state(PauseState())
    
    def update(self, game: Game):
        game.manage_food_and_score()
        if game.snake:
            game.snake.move()

        if game.snake.is_eating_self():
                game.game_hud.update_high_score()
                from GameUI import GameOverState
                game.change_state(GameOverState())
        game.clock.tick(game.game_update_rate)
    
    def draw(self, game: Game):
        game.draw_game()
    
    def exit(self, game: Game):
        game.previous_state = self



class PlayingWithAIState(GameState):
    def enter(self, game: Game):
        self.eat_count = 0
        self.state = "PLAYING"
        self.actions = []
        game.start_game(new_game=True)
    
    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)

    def _handle_actions(self, game: Game):
        for direction in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            if game.controls.is_pressed(direction):
                game.snake.set_direction(direction)
                break
        if game.controls.is_just_pressed('ESCAPE'):
            from GameUI import MenuState
            game.change_state(MenuState())
        elif game.controls.is_just_pressed('SPACE'):
            from GameUI import PauseState
            game.change_state(PauseState())
    
    def update(self, game: Game):
        if self.state == "AI":
            pass

        if game.snake.is_eating_food(game.big_food):
            game.display_message("BIG FOOD ATE!", 2000)
            if self.state == "PLAYING":
                self.state = "AI"
            else:
                self.state = "PLAYING"
        if self.actions:
            action = self.actions.pop(0)
            game.snake.set_direction(action)

        game.manage_food_and_score()

        if game.snake:
            game.snake.move()

        if game.snake.is_eating_self():
                game.game_hud.update_high_score()
                from GameUI import GameOverState
                game.change_state(GameOverState())
        game.clock.tick(game.game_update_rate)
    
    def draw(self, game: Game):
        game.draw_game()
    
    def exit(self, game: Game):
        game.previous_state = self
