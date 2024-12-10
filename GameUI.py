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

from pygame.event import Event
from Game import Game
from GameState import *
from Constants import *
from Snake import *
from Search import *
from HumanPlayer import *
from Experiment import *
from SearchAlgorithmsVision import *
from SearchAlgorithmsPlaySnake import *

class MenuState(GameState):
    def enter(self, game: Game):
        game.game_hud.current_menu = game.game_hud.menu_lists['main_menu']

    def handle_events(self, game: Game, events: list[pygame.event.Event]):

        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)
                

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed(game.controls.UP):
            game.game_hud.navigate_menu(-1)
        elif game.controls.is_just_pressed(game.controls.DOWN):
            game.game_hud.navigate_menu(1)
        elif game.controls.is_just_pressed(game.controls.SELECT):
            self._handle_menu_select(game)

    
    def update(self, game: Game):
        game.clock.tick(game.menu_update_rate)
    
    def draw(self, game: Game):
        game.game_hud.draw_menu()
    
    def exit(self, game: Game):
        pass

    def _handle_menu_select(self, game: Game):
        selected_item = game.game_hud.get_selected_item()
        if selected_item == "Quit":
            game.running = False
        elif selected_item == "New Game":
            self._start_new_or_continue_game(game)
        elif selected_item == "Continue":
            game.change_state(ContinuingState())
        elif selected_item == "AI":
            game.change_state(AIGameSelectState())
        elif selected_item == "Level":
            game.change_state(LevelSelectState())
        elif selected_item == "High Scores":
            game.change_state(HighScoresState())

    def _start_new_or_continue_game(self, game: Game):
        if game.game_hud.score > 0:
            #game.start_game(new_game=False)
            game.change_state(ProgressWarningState())
        else:
            game.start_game(new_game=True)
            game.change_state(PlayingState())

class PauseState(GameState):
    def enter(self, game: Game):
        pass

    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed('ESCAPE'):
            game.change_state(MenuState())
        elif game.controls.is_just_pressed('SPACE'):
            game.change_state(StartingGameState())
            
    def update(self, game: Game):
        game.clock.tick(game.menu_update_rate)
    
    def draw(self, game: Game):
        game.game_hud.draw_pause()
    
    def exit(self, game: Game):
        pass

class StartingGameState(GameState):
    def enter(self, game: Game):
        self.countdown_max = MAX_COUNTDOWN
        self.countdown_value = 3
        self.countdown_start_time = None
        self.is_counting_down = False
        
    
    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        pass

    def _handle_actions(self, game: Game):
        pass
    
    def update(self, game: Game):
        self._handle_countdown(game)
        game.clock.tick(game.menu_update_rate)   
    
    def draw(self, game: Game):
        self._draw_resume_countdown(game)
    
    def exit(self, game: Game):
        pass

    def _draw_resume_countdown(self, game: Game):
        """
        Draw the countdown when resuming the game.
        """
        game.draw_game()
        game.game_hud.draw_countdown(self.countdown_value)

    def _handle_countdown(self, game: Game):
        """
        Handle the countdown before resuming the game.
        """

        current_time = pygame.time.get_ticks()

        if not self.is_counting_down:
            self.countdown_start_time = current_time
            self.is_counting_down = True
        
        elapsed_time = (current_time - self.countdown_start_time) // 1000
        self.countdown_value = max(0, 3 - elapsed_time)
        
        if self.countdown_value == 0:
            if game.previous_state:
                game.state = game.previous_state
            else:
                game.change_state(PlayingState())

class GameOverState(GameState):
    def enter(self, game: Game):
        pass
    
    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed('ESCAPE'):
            game.change_state(MenuState())
        elif game.controls.is_just_pressed('SELECT'):
            game.change_state(PlayingState())

    
    def update(self, game: Game):
        game.clock.tick(game.menu_update_rate)
    
    def draw(self, game: Game):
        game.game_hud.draw_game_over()
    
    def exit(self, game: Game):
        game.start_game(new_game=True)
    
class ContinuingState(GameState):
    def enter(self, game: Game):
        if game.game_hud.score == 0:
            game.display_message("No game to continue", duration=2000)
        else:
            game.change_state(StartingGameState())
    
    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed('ESCAPE'):
            game.change_state(MenuState())
    
    def update(self, game: Game):
        if game.message_timeout():
            game.change_state(MenuState())
        game.clock.tick(game.menu_update_rate)
    
    def draw(self, game: Game):
        game.draw_message()

    def exit(self, game: Game):
        pass
    
class HighScoresState(GameState):
    def enter(self, game: Game):
        pass
    
    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        if game.controls.is_just_pressed('ESCAPE'):
            game.change_state(MenuState())
    
    def update(self, game: Game):
        game.clock.tick(game.menu_update_rate)

    def _handle_actions(self, game: Game):
        pass
    
    def draw(self, game: Game):
        game.game_hud.draw_high_scores()
    
    def exit(self, game: Game):
        pass

class LevelSelectState(GameState):
    def enter(self, game: Game):
        game.game_hud.current_menu = game.game_hud.menu_lists['game_level_menu']
    
    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)
    
    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed('UP'):
            game.game_hud.navigate_menu(-1)
        elif game.controls.is_just_pressed('DOWN'):
            game.game_hud.navigate_menu(1)
        elif game.controls.is_just_pressed('ESCAPE'):
            game.change_state(MenuState())
        elif game.controls.is_just_pressed('SELECT'):
            self._handle_level_select(game)
    
    def update(self, game: Game):
        game.clock.tick(game.menu_update_rate)
    
    def draw(self, game: Game):
        game.game_hud.draw_menu()
    

    def exit(self, game: Game):
        pass

    def _handle_level_select(self, game: Game):
        selected_level = game.game_hud.get_selected_item()
        game.game_hud.memorise_game_level(selected_level)
        if selected_level == "EASY":
            game.game_update_rate = LEVEL_2
        elif selected_level == "MEDIUM":
            game.game_update_rate = LEVEL_5
        elif selected_level == "HARD":
            game.game_update_rate = LEVEL_8
        elif selected_level == "VERY HARD":
            game.game_update_rate = GOD_MODE
        game.start_game(new_game=True)

class AIGameSelectState(GameState):
    def enter(self, game: Game):
        pass
    
    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)
    
    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed('UP'):
            game.game_hud.navigate_menu(-1)
        elif game.controls.is_just_pressed('DOWN'):
            game.game_hud.navigate_menu(1)
        elif game.controls.is_just_pressed('ESCAPE'):
            game.change_state(MenuState())
        elif game.controls.is_just_pressed('SELECT'):
            self._handle_ai_select(game)
    
    def update(self, game: Game):
        game.clock.tick(game.menu_update_rate)
    
    def draw(self, game: Game):
        game.game_hud.draw_menu()
    

    def exit(self, game: Game):
        pass

    def _handle_ai_select(self, game: Game):
        selected_ai = game.game_hud.get_selected_item()
        if selected_ai == "AI Vision":
            game.change_state(AIVisionSelectState())
        elif selected_ai == "AI Play":
            game.change_state(AIPlaySelectState())
        elif selected_ai == "AI Experiment":
            game.change_state(ExperimentState())
        game.start_game(new_game=True)

class AIPlaySelectState(GameState):
    def enter(self, game: Game):
        game.game_hud.current_menu = game.game_hud.menu_lists['ai_play_menu']
    
    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)
    
    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed('UP'):
            game.game_hud.navigate_menu(-1)
        elif game.controls.is_just_pressed('DOWN'):
            game.game_hud.navigate_menu(1)
        elif game.controls.is_just_pressed('ESCAPE'):
            game.change_state(AIGameSelectState())
        elif game.controls.is_just_pressed('SELECT'):
            self._handle_ai_play_select(game)
    
    def update(self, game: Game):
        game.clock.tick(game.menu_update_rate)
    
    def draw(self, game: Game):
        game.game_hud.draw_menu()
    

    def exit(self, game: Game):
        pass

    def _handle_ai_play_select(self, game: Game):
        selected_ai = game.game_hud.get_selected_item()
        if selected_ai == "Breadth First":
            game.change_state(AIPlayerBFSState())
        elif selected_ai == "Depth First":
            game.change_state(AIPlayerDFSState())
        elif selected_ai == "A Star":
            game.change_state(AIPlayerAStarSearchState())
        elif selected_ai == "Greedy":
            game.change_state(AIPlayerGreedyState())
        game.start_game(new_game=True)

class ExperimentSelectState(GameOverState):
    def enter(self, game: Game):
        pass

    def handle_events(self, game: Game, events: list[Event]):
        self._handle_actions(game)
    
    def _handle_actions(self, game: Game):
        return super()._handle_actions(game)
    
    def update(self, game: Game):
        return super().update(game)
    
    def draw(self, game: Game):
        return super().draw(game)
    
    def exit(self, game: Game):
        return super().exit(game)
    


class AIVisionSelectState(GameState):
    def enter(self, game: Game):
        game.game_hud.current_menu = game.game_hud.menu_lists['ai_vision_menu']
    
    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)
    
    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed('UP'):
            game.game_hud.navigate_menu(-1)
        elif game.controls.is_just_pressed('DOWN'):
            game.game_hud.navigate_menu(1)
        elif game.controls.is_just_pressed('ESCAPE'):
            game.change_state(AIGameSelectState())
        elif game.controls.is_just_pressed('SELECT'):
            self._handle_ai_select(game)
    
    def update(self, game: Game):
        game.clock.tick(game.menu_update_rate)
    
    def draw(self, game: Game):
        game.game_hud.draw_menu()
    

    def exit(self, game: Game):
        pass

    def _handle_ai_select(self, game: Game):
        selected_ai = game.game_hud.get_selected_item()
        if selected_ai == "Breadth First":
            game.change_state(GraphCreationVisionBFS())
        elif selected_ai == "Depth First":
            game.change_state(GraphCreationVisionDFS())
        elif selected_ai == "A Star":
            game.change_state(GraphCreationVisionAStarSearch())
        elif selected_ai == "Greedy":
            game.change_state(GraphCreationVisionGreedySearch())
        game.start_game(new_game=True)

    
class ProgressWarningState(GameState):
    def enter(self, game: Game):
        pass
    
    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed('ESCAPE'):
            game.change_state(MenuState())
        elif game.controls.is_just_pressed('SELECT'):
            game.start_game(new_game=True)
            game.change_state(PlayingState())
    
    def update(self, game: Game):
        game.clock.tick(game.menu_update_rate)
    
    def draw(self, game: Game):
        game.game_hud.draw_progress_prompt()
    
    def exit(self, game: Game):
        pass
    
class ShowMessageState(GameState):
    def enter(self, game: Game):
        pass
    
    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        pass
    
    def update(self, game: Game):
        game.clock.tick(game.menu_update_rate)
    
    def draw(self, game: Game):
        game.draw_game()
        game.draw_message()
    
    def exit(self, game: Game):
        pass
