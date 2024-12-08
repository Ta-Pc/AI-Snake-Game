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

import json
import pygame
import pygame.time
from Constants import *
from Snake import *
from HUD import HUD
from collections import deque
from Controls import Controls
    

class Game:
    """
    Main game class that handles the game loop, state management, and overall game logic.
    """
    def __init__(self):
        """
        Initialize the game with all necessary components and settings.
        """
        # Initialization
        pygame.init()
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game")

        # Game state and settings
        self.game_update_rate = LEVEL_1
        self.menu_update_rate = MENUE_RATE
        
        # Game components
        self.game_hud = HUD(self.window)
        self.controls = Controls()
        self.snake = None
        self.food = None
        self.big_food = None
        self.env = None
        self.eat_count = 0
        
        # Load general game settings
        self.load_game_settings()
        
        # Create background
        self.background = self.create_background()

        self.running = True

        # Message display variables
        self.message = ""
        self.message_duration = 0
        self.message_start_time = 0
        self.showing_message = False

        # AI-related attributes
        self.ai_mode = False  # Flag to indicate if AI mode is active
        self.ai_path = deque()  # Queue to store the AI's planned path
        self.ai_update_interval = 0.1  # Time interval between AI updates in seconds
        self.last_ai_update = 0  # Timestamp of the last AI update

        self.previous_state = None
        from GameUI import MenuState
        from Experiment import GraphCreationVisionLocalSearch_Exp
        from Experiment import AIPlayerBFSStateExp
        self.state = GraphCreationVisionLocalSearch_Exp()
        self.state.enter(self)

    def change_state(self, new_state):
        self.state.exit(self)
        self.state = new_state
        self.state.enter(self)

    def run(self):
        """
        Main game loop that handles events, updates game state, and draws the game.
        """
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            
        self.cleanup()

    def handle_events(self):
        """
        Handle all game events including user input and game state changes.
        """
        events = pygame.event.get()
        self.controls.update(events)
        self.state.handle_events(self, events)
        for event in events:
            if event.type == pygame.QUIT:
                self.save_game_state()
                self.running = False

    def draw(self):
        """
        Draw the game screen based on the current game state.
        """
        self.window.blit(self.background, (0, 0))
        self.state.draw(self)
        pygame.display.flip()

    def update(self):
        """
        Update game logic, including environment, snake movement, and game over conditions.
        """
        self.state.update(self)
        

    def start_game(self, new_game=False):
        """
        Start a new game or continue from a saved state.

        Args:
            new_game (bool): If True, start a new game. If False, attempt to load a saved game.
        """
        if new_game:
            # Initialize new game elements
            self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
            self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.game_hud.score = 0
        else:
            # Load snake-specific data
            snake_data = self.load_snake_data()

            if snake_data:
                # Restore saved snake state
                self.snake = Snake.from_saved_state(snake_data.get('snake'), snake_data.get('direction', "RIGHT"))
                self.food = Food.from_saved_state(snake_data.get('food'), self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.game_hud.score = snake_data.get('score', 0)
            else:
                # Initialize new game elements if no saved data
                self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
                self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.game_hud.score = 0

        self.big_food = BigFood(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT), self.game_update_rate)



    def draw_game(self):
        """
        Draw the main game elements: food, big food, snake, score, and border.
        """
        time = pygame.time.get_ticks() / 1000
        if self.food:
            self.food.draw(self.window)
        if self.big_food:
            self.big_food.draw(self.window, time)
        if self.snake:
            self.snake.draw(self.window, time)
        self.game_hud.draw_score()
        pygame.draw.rect(self.window, BRIGHT_AQUA, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 3)


    def draw_message(self):
        """
        Draw a message on the screen.
        """
        if not self.message_timeout():
            prompt = self.game_hud._render_text(self.message, self.game_hud.fonts['medium'], BRIGHT_AQUA)
            self.game_hud._draw_centered_text(prompt, 280)

    def display_message(self, message, duration):
        """
        Display a message for a specified duration.

        Args:
            message (str): The message to display.
            duration (int): Duration in milliseconds to display the message.
        """
        self.message = message
        self.message_duration = duration
        self.message_start_time = pygame.time.get_ticks()

    def message_timeout(self):
        """
        Check if the current message has timed out and should be dismissed.
        """
        current_time = pygame.time.get_ticks()
        if current_time - self.message_start_time >= self.message_duration:
            return True
        return False

    @staticmethod
    def draw_rounded_rectangle(surface, color, rect, corner_radius):
        """
        Draw a rounded rectangle on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw on.
            color (tuple): RGB color tuple.
            rect (pygame.Rect): The rectangle to draw.
            corner_radius (int): Radius of the rounded corners.
        """
        pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

    def create_background(self):
        """
        Create and return the game background surface.

        Returns:
            pygame.Surface: The created background surface.
        """
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
                color = (60, 60, 60) if (x + y) // CELL_SIZE % 2 == 0 else (40, 40, 40)
                pygame.draw.rect(background, color, (x, y, CELL_SIZE, CELL_SIZE))
        return background

    def save_game_state(self):
        """
        Save the current game state to a JSON file.
        """
        game_state = {
            'score': self.game_hud.score,
            'high_scores': self.game_hud.high_scores,
            'snake': self.snake.get_state() if self.snake else None,
            'food': self.food.get_state() if self.food else None,
            'direction': self.snake.direction if self.snake else "RIGHT",
            'game_level': self.game_hud.current_level  # Save the current level as a string
        }
        with open('game_state.json', 'w', encoding='utf-8') as file:
            json.dump(game_state, file)

    def load_game_settings(self):
        """
        Load game settings from a JSON file or initialize with default values.
        """
        try:
            with open('game_state.json', 'r', encoding='utf-8') as file:
                game_state = json.load(file)
                self.game_hud.high_scores = game_state.get('high_scores', [])
                saved_level = game_state.get('game_level', "EASY")
                self.game_hud.memorise_game_level(saved_level)
                self.game_update_rate = self.get_update_rate(self.game_hud.current_level)
        except (FileNotFoundError, json.JSONDecodeError):
            # Initialize with default values if no save file exists or if it's corrupted
            self.game_hud.high_scores = []
            self.game_hud.update_game_level("EASY")
            self.game_update_rate = LEVEL_1

    def load_snake_data(self):
        """
        Load snake-specific data from a JSON file.

        Returns:
            dict: A dictionary containing snake data, or None if loading fails.
        """
        try:
            with open('game_state.json', 'r', encoding='utf-8') as file:
                game_state = json.load(file)
                return {
                    'snake': game_state.get('snake'),
                    'food': game_state.get('food'),
                    'direction': game_state.get('direction', "RIGHT"),
                    'score': game_state.get('score', 0)
                }
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            return None

    def get_update_rate(self, level):
        """
        Get the update rate based on the game level.

        Args:
            level (str): The game level.

        Returns:
            int: The update rate for the given level.
        """
        return {
            "EASY": LEVEL_1,
            "MEDIUM": LEVEL_4,
            "HARD": LEVEL_7,
            "VERY HARD": GOD_MODE
        }.get(level, LEVEL_1)

    def cleanup(self):
        """
        Perform cleanup operations before exiting the game.
        """
        self.save_game_state()
        pygame.quit()

    def manage_food_and_score(self):
        self.big_food.update()
        if self.snake.is_eating_food(self.food):
            self.game_hud.increase_score(self.food.score_incriment)
            self.snake.grow(size=1)
            self.food.replace(self.snake)
            self.eat_count += 1
            
            if self.eat_count == REWARD_TRIGER_SCORE:
                self.eat_count = 0
                if not self.big_food.active:
                    self.big_food.replace(self.snake)
                    self.big_food.is_active(True)
        elif self.snake.is_eating_food(self.big_food):
            self.game_hud.increase_score(self.big_food.score_incriment)
            self.snake.grow(size=5)
            self.big_food.is_active(False)
    # Add other Game class methods as needed
