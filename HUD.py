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

import pygame
import math
from Constants import *

class HUD:
    """
    Heads-Up Display (HUD) class for managing and rendering game interface elements.

    This class handles the creation and display of various game screens, menus, and visual elements.
    It manages the game's graphical user interface, including the main menu, level selection,
    score display, and other game-related information.

    Attributes:
        window (pygame.Surface): The main game window surface for rendering.
        fonts (dict): A dictionary of pygame Font objects for different text sizes.
        score (int): The current game score.
        menu_items (list): List of main menu options.
        game_level_items (list): List of available game difficulty levels.
        high_scores (list): 2D list storing high scores for each difficulty level.
        selected_level_item (int): Index of the currently selected difficulty level.
        selected_menu_item (int): Index of the currently selected menu item.
        current_level (str): The currently selected game difficulty level.
        animations (dict): Stores animation states for menu items.
        background (pygame.Surface): The game's gradient background surface.
        menu_bg (pygame.Surface): Background surface for menu screens.
        button_bg (pygame.Surface): Background surface for menu buttons.

        Consider:
        items
        selected_item
        select_item() -> (item from items)
        navigate_items(int)
    """

    def __init__(self, window: pygame.Surface):
        """
        Initialize the HUD with necessary components.

        Args:
            window (pygame.Surface): The main game window surface for rendering.
        """
        self.window = window
        self.fonts = self._load_fonts()
        self.score = 0
        self.menu_items = ["New Game", "Continue", "Level", "AI", "High Scores", "Quit"]
        self.game_level_items = ["EASY", "MEDIUM", "HARD", "VERY HARD"]
        self.ai_items = ["AI Vision", "AI Play", "AI Experiment"]
        self.ai_vision_items = ["Breadth First", "Depth First", "A Star", "Greedy"]
        self.ai_play_items = ["Breadth First", "Depth First", "A Star", "Greedy"]
        self.high_scores = [[0] * MAX_HIGH_SCORES for _ in self.game_level_items]
        self.selected_level_item = 0
        self.selected_ai_play_item = 0
        self.selected_ai_vision_item = 0
        self.selected_ai_item = 0
        self.selected_menu_item = 0
        self.current_level = self.game_level_items[self.selected_level_item]
        self.animations = {}
        self.load_assets()

    # --- Initialization Methods ---
    def _load_fonts(self):
        """
        Load and return a dictionary of pygame Font objects for different text sizes.

        Returns:
            dict: A dictionary of pygame Font objects.
        """
        return {
            'small': pygame.font.Font(None, 32),
            'medium': pygame.font.Font(None, 48),
            'large': pygame.font.Font(None, 72),
            'title': pygame.font.Font(None, 96)
        }

    def load_assets(self):
        """
        Load and create necessary graphical assets for the HUD.
        """
        self.background = self._create_gradient_background()
        self.menu_bg = self._create_menu_background()
        self.button_bg = self._create_button_background()

    # --- Asset Creation Methods ---
    def _create_gradient_background(self):
        """
        Create and return a gradient background surface.

        Returns:
            pygame.Surface: A surface with a vertical gradient from cyan to magenta.
        """
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            color = self._interpolate_color(BRIGHT_CYAN, BRIGHT_MAGENTA, y / SCREEN_HEIGHT)
            pygame.draw.line(background, color, (0, y), (SCREEN_WIDTH, y))
        return background

    def _create_menu_background(self):
        """
        Create and return a semi-transparent background surface for menus.

        Returns:
            pygame.Surface: A semi-transparent surface for menu backgrounds.
        """
        menu_bg = pygame.Surface((SCREEN_WIDTH * 0.8, SCREEN_HEIGHT * 0.8), pygame.SRCALPHA)
        pygame.draw.rect(menu_bg, (0, 0, 0, 180), menu_bg.get_rect(), border_radius=20)
        return menu_bg

    def _create_button_background(self):
        """
        Create and return a semi-transparent background surface for buttons.

        Returns:
            pygame.Surface: A semi-transparent surface for button backgrounds.
        """
        button_bg = pygame.Surface((300, 60), pygame.SRCALPHA)
        pygame.draw.rect(button_bg, (255, 255, 255, 50), button_bg.get_rect(), border_radius=10)
        return button_bg

    # --- Utility Methods ---
    @staticmethod
    def _interpolate_color(color1, color2, factor):
        """
        Interpolate between two colors.

        Args:
            color1 (tuple): The first color (R, G, B).
            color2 (tuple): The second color (R, G, B).
            factor (float): Interpolation factor between 0 and 1.

        Returns:
            tuple: The interpolated color (R, G, B).
        """
        return tuple(int(color1[i] + (color2[i] - color1[i]) * factor) for i in range(3))

    def _render_text(self, text, font, color):
        """
        Render text using the specified font and color.

        Args:
            text (str): The text to render.
            font (pygame.font.Font): The font to use for rendering.
            color (tuple): The color of the text (R, G, B).

        Returns:
            pygame.Surface: A surface containing the rendered text.
        """
        return font.render(text, True, color)

    def _draw_centered_text(self, text_surface, y_offset=0):
        """
        Draw text centered on the screen with a vertical offset.

        Args:
            text_surface (pygame.Surface): The rendered text surface to draw.
            y_offset (int, optional): Vertical offset from the center of the screen. Defaults to 0.
        """
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
        self.window.blit(text_surface, text_rect)

    # --- Score Management ---
    def draw_score(self):
        """
        Draw the current score on the game window.
        """
        score_text = self._render_text(f"Score: {self.score}", self.fonts['medium'], WHITE)
        score_bg = pygame.Surface((score_text.get_width() + 20, score_text.get_height() + 10), pygame.SRCALPHA)
        pygame.draw.rect(score_bg, (0, 0, 0, 150), score_bg.get_rect(), border_radius=10)
        self.window.blit(score_bg, (10, 10))
        self.window.blit(score_text, (20, 15))

    def increase_score(self, increment):
        """
        Increase the current score by the given increment.

        Args:
            increment (int): The amount to increase the score by.
        """
        self.score += increment

    def update_high_score(self):
        """
        Update the high scores list with the current score if it qualifies.
        """
        self.high_scores[self.selected_level_item].append(self.score)
        self.high_scores[self.selected_level_item] = sorted(
            self.high_scores[self.selected_level_item], reverse=True
        )[:MAX_HIGH_SCORES]

    # --- Drawing Methods ---
    def draw_game_over(self):
        """
        Draw the game over screen.
        """
        self.window.blit(self.background, (0, 0))
        game_over_text = self._render_text("Game Over", self.fonts['title'], RED)
        self._draw_centered_text(game_over_text, -100)
        
        score_text = self._render_text(f"Your Score: {self.score}", self.fonts['large'], WHITE)
        self._draw_centered_text(score_text, 50)

        restart_text = self._render_text("Press ENTER to Restart", self.fonts['medium'], BRIGHT_GOLD)
        self._draw_centered_text(restart_text, 150)

    def draw_exit_prompt(self):
        """
        Draw the exit confirmation prompt.
        """
        self.window.blit(self.background, (0, 0))
        prompt_text = self._render_text("Are you sure?", self.fonts['title'], RED)
        self._draw_centered_text(prompt_text, -50)
        
        instruction_text = self._render_text("Select 'Quit' in MENU to Exit", self.fonts['medium'], BRIGHT_GOLD)
        self._draw_centered_text(instruction_text, 150)

    def draw_progress_prompt(self):
        """
        Draw the progress warning prompt when starting a new game.
        """
        self.window.blit(self.background, (0, 0))
        warning_text = self._render_text(
            "Are you sure, you will lose existing progress?", self.fonts['medium'], RED
        )
        self._draw_centered_text(warning_text, -50)
        
        instruction_text = self._render_text(
            "Select 'ENTER' to continue, ESC to return to menu", self.fonts['small'], BRIGHT_GOLD
        )
        self._draw_centered_text(instruction_text, 150)

    def draw_countdown(self, countdown_value):
        """
        Draw the countdown screen before starting a game.

        Args:
            countdown_value (int): The current countdown number to display.
        """
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.window.blit(overlay, (0, 0))
    
        font = pygame.font.Font(None, 200)
        text = font.render(str(countdown_value), True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.window.blit(text, text_rect)
    
        font_small = pygame.font.Font(None, 50)
        ready_text = font_small.render("Get Ready!", True, (255, 255, 255))
        ready_rect = ready_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.window.blit(ready_text, ready_rect)

    def draw_pause(self):
        """
        Draw the pause screen overlay.
        """
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.window.blit(overlay, (0, 0))
        
        pause_text = self._render_text("Paused", self.fonts['title'], YELLOW)
        self._draw_centered_text(pause_text)

        resume_text = self._render_text("Press SPACE to Resume", self.fonts['medium'], WHITE)
        self._draw_centered_text(resume_text, 100)

    def draw_level_select(self):
        """
        Draw the level selection screen.
        """
        self.window.blit(self.background, (0, 0))
        self.window.blit(self.menu_bg, (SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.1 + 25))

        title_text = self._render_text("Select Level", self.fonts['title'], BRIGHT_GOLD)
        self._draw_centered_text(title_text, -250)

        for index, item in enumerate(self.game_level_items):
            color = BRIGHT_GOLD if index == self.selected_level_item else WHITE
            menu_text = self._render_text(item, self.fonts['large'], color)
            
            button_y = SCREEN_HEIGHT // 2 + index * 80 - 150
            self.window.blit(self.button_bg, (SCREEN_WIDTH // 2 - 150, button_y))
            
            text_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, button_y + 30))
            self.window.blit(menu_text, text_rect)

            level_text = self._render_text(f"Current level: {self.current_level}", self.fonts['medium'], BRIGHT_AQUA)
            self._draw_centered_text(level_text, 280)

            if index == self.selected_level_item:
                animation = self.animations.get(f'menu_{index}', 0)
                animation = (animation + 0.1) % (2 * math.pi)
                self.animations[f'menu_{index}'] = animation
                
                glow_factor = (math.sin(animation) + 1) / 2
                glow_color = self._interpolate_color(BRIGHT_GOLD, WHITE, glow_factor)
                glow_surf = pygame.Surface((310, 70), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*glow_color, 100), glow_surf.get_rect(), border_radius=15)
                self.window.blit(glow_surf, (SCREEN_WIDTH // 2 - 155, button_y - 5))

    def draw_ai_select(self):
        """
        Draw the AI selection screen.
        """
        self.window.blit(self.background, (0, 0))
        self.window.blit(self.menu_bg, (SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.1 + 25))

        title_text = self._render_text("Select AI", self.fonts['title'], BRIGHT_GOLD)
        self._draw_centered_text(title_text, -250)

        for index, item in enumerate(self.ai_items):
            color = BRIGHT_GOLD if index == self.selected_ai_item else WHITE
            menu_text = self._render_text(item, self.fonts['large'], color)
            
            button_y = SCREEN_HEIGHT // 2 + index * 80 - 150
            self.window.blit(self.button_bg, (SCREEN_WIDTH // 2 - 150, button_y))
            
            text_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, button_y + 30))
            self.window.blit(menu_text, text_rect)

            if index == self.selected_ai_item:
                animation = self.animations.get(f'menu_{index}', 0)
                animation = (animation + 0.1) % (2 * math.pi)
                self.animations[f'menu_{index}'] = animation
                
                glow_factor = (math.sin(animation) + 1) / 2
                glow_color = self._interpolate_color(BRIGHT_GOLD, WHITE, glow_factor)
                glow_surf = pygame.Surface((310, 70), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*glow_color, 100), glow_surf.get_rect(), border_radius=15)
                self.window.blit(glow_surf, (SCREEN_WIDTH // 2 - 155, button_y - 5))

    def draw_ai_vision_select(self):
        """"
        Draw the AI vision selection screen.
        """
        self.window.blit(self.background, (0, 0))
        self.window.blit(self.menu_bg, (SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.1 + 25))

        title_text = self._render_text("Select AI Vision", self.fonts['title'], BRIGHT_GOLD)
        self._draw_centered_text(title_text, -250)

        for index, item in enumerate(self.ai_vision_items):
            color = BRIGHT_GOLD if index == self.selected_ai_vision_item else WHITE
            menu_text = self._render_text(item, self.fonts['large'], color)
            
            button_y = SCREEN_HEIGHT // 2 + index * 80 - 150
            self.window.blit(self.button_bg, (SCREEN_WIDTH // 2 - 150, button_y))
            
            text_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, button_y + 30))
            self.window.blit(menu_text, text_rect)

            if index == self.selected_ai_vision_item:
                animation = self.animations.get(f'menu_{index}', 0)
                animation = (animation + 0.1) % (2 * math.pi)
                self.animations[f'menu_{index}'] = animation
                
                glow_factor = (math.sin(animation) + 1) / 2
                glow_color = self._interpolate_color(BRIGHT_GOLD, WHITE, glow_factor)
                glow_surf = pygame.Surface((310, 70), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*glow_color, 100), glow_surf.get_rect(), border_radius=15)
                self.window.blit(glow_surf, (SCREEN_WIDTH // 2 - 155, button_y - 5))

    def draw_ai_play_select(self):
        """"
        Draw the AI play selection screen.
        """
        self.window.blit(self.background, (0, 0))
        self.window.blit(self.menu_bg, (SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.1 + 25))

        title_text = self._render_text("Select AI Play", self.fonts['title'], BRIGHT_GOLD)
        self._draw_centered_text(title_text, -250)

        for index, item in enumerate(self.ai_play_items):
            color = BRIGHT_GOLD if index == self.selected_ai_play_item else WHITE
            menu_text = self._render_text(item, self.fonts['large'], color)
            
            button_y = SCREEN_HEIGHT // 2 + index * 80 - 150
            self.window.blit(self.button_bg, (SCREEN_WIDTH // 2 - 150, button_y))
            
            text_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, button_y + 30))
            self.window.blit(menu_text, text_rect)

            if index == self.selected_ai_play_item:
                animation = self.animations.get(f'menu_{index}', 0)
                animation = (animation + 0.1) % (2 * math.pi)
                self.animations[f'menu_{index}'] = animation
                
                glow_factor = (math.sin(animation) + 1) / 2
                glow_color = self._interpolate_color(BRIGHT_GOLD, WHITE, glow_factor)
                glow_surf = pygame.Surface((310, 70), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*glow_color, 100), glow_surf.get_rect(), border_radius=15)
                self.window.blit(glow_surf, (SCREEN_WIDTH // 2 - 155, button_y - 5))

    def draw_menu(self):
        """
        Draw the main menu screen.
        """
        self.window.blit(self.background, (0, 0))
        self.window.blit(self.menu_bg, (SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.1))
        
        title_text = self._render_text("Snake Game", self.fonts['title'], BRIGHT_GOLD)
        self._draw_centered_text(title_text, -250)

        for index, item in enumerate(self.menu_items):
            color = BRIGHT_GOLD if index == self.selected_menu_item else WHITE
            menu_text = self._render_text(item, self.fonts['large'], color)
            
            button_y = SCREEN_HEIGHT // 2 + index * 80 - 190
            self.window.blit(self.button_bg, (SCREEN_WIDTH // 2 - 150, button_y))
            
            text_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, button_y + 30))
            self.window.blit(menu_text, text_rect)

            if index == self.selected_menu_item:
                animation = self.animations.get(f'menu_{index}', 0)
                animation = (animation + 0.1) % (2 * math.pi)
                self.animations[f'menu_{index}'] = animation
                
                glow_factor = (math.sin(animation) + 1) / 2
                glow_color = self._interpolate_color(BRIGHT_GOLD, WHITE, glow_factor)
                glow_surf = pygame.Surface((310, 70), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*glow_color, 100), glow_surf.get_rect(), border_radius=15)
                self.window.blit(glow_surf, (SCREEN_WIDTH // 2 - 155, button_y - 5))

    def draw_high_scores(self):
        """
        Draw the high scores screen.
        """
        self.window.blit(self.background, (0, 0))
        self.window.blit(self.menu_bg, (SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.1))
        
        title_text = self._render_text("High Scores", self.fonts['title'], BRIGHT_GOLD)
        self._draw_centered_text(title_text, -200)

        details_text = self._render_text(f"Level: {self.current_level}", self.fonts['small'], WHITE)
        self._draw_centered_text(details_text, -120)

        category = self.selected_level_item
        for index, score in enumerate(self.high_scores[category]):
            score_text = self._render_text(f"{index + 1}. {score}", self.fonts['large'], WHITE)
            self._draw_centered_text(score_text, -100 + (index + 1) * 60)

        back_text = self._render_text("Press ESC to go back", self.fonts['medium'], BRIGHT_AQUA)
        self._draw_centered_text(back_text, 280)

    # --- Menu Navigation Methods ---
    def navigate_menu(self, direction):
        """
        Navigate through the main menu items.

        Args:
            direction (int): The direction to move (-1 for up, 1 for down).
        """
        self.selected_menu_item = (self.selected_menu_item + direction) % len(self.menu_items)

    def navigate_level_select(self, direction):
        """
        Navigate through the level selection items.

        Args:
            direction (int): The direction to move (-1 for up, 1 for down).
        """
        self.selected_level_item = (self.selected_level_item + direction) % len(self.game_level_items)

    def navigate_ai_select(self, direction):
        """
        Navigate through the ai selection items.

        Args:
            direction (int): The direction to move (-1 for up, 1 for down).
        """
        self.selected_ai_item = (self.selected_ai_item + direction) % len(self.ai_items)

    def navigate_ai_vision_select(self, direction):
        """
        Navigate through the ai vision selection items.

        Args:
            direction (int): The direction to move (-1 for up, 1 for down).
        """
        self.selected_ai_vision_item = (self.selected_ai_vision_item + direction) % len(self.ai_vision_items)

    def navigate_ai_play_select(self, direction):
        """
        Navigate through the ai selection items.

        Args:
            direction (int): The direction to move (-1 for up, 1 for down).
        """
        self.selected_ai_play_item = (self.selected_ai_play_item + direction) % len(self.ai_play_items)

    def select_menu_item(self):
        """
        Get the currently selected menu item.

        Returns:
            str: The name of the currently selected menu item.
        """
        return self.menu_items[self.selected_menu_item]

    def select_level_item(self):
        """
        Get the currently selected level item.

        Returns:
            str: The name of the currently selected level.
        """
        return self.game_level_items[self.selected_level_item]
    
    def select_ai_item(self):
        """
        Get the currently selected AI item.

        Returns:
            str: The name of the currently selected AI.
        """
        return self.ai_items[self.selected_ai_item]
    
    def select_ai_play_item(self):
        """
        Get the currently selected AI play item.

        Returns:
            str: The name of the currently selected AI.
        """
        return self.ai_play_items[self.selected_ai_play_item]
    
    def select_ai_vision_item(self):
        """
        Get the currently selected AI play item.

        Returns:
            str: The name of the currently selected AI.
        """
        return self.ai_vision_items[self.selected_ai_vision_item]

    def memorise_game_level(self, game_level=None):
        """
        Memorise the current game level.

        Args:
            game_level (str or int, optional): The new game level to set. Can be a string (level name) or an integer (level index).
        """
        if game_level is not None:
            if isinstance(game_level, str):
                try:
                    self.selected_level_item = self.game_level_items.index(game_level)
                except ValueError:
                    self.selected_level_item = 0
            elif isinstance(game_level, int):
                self.selected_level_item = max(0, min(game_level, len(self.game_level_items) - 1))
        self.current_level = self.game_level_items[self.selected_level_item]

    # --- Icon Drawing Methods ---
    def draw_snake_icon(self, x, y, size):
        """
        Draw a snake icon at the specified position.

        Args:
            x (int): The x-coordinate of the top-left corner of the icon.
            y (int): The y-coordinate of the top-left corner of the icon.
            size (int): The size of the icon (width and height).
        """
        points = [
            (x, y + size // 2),
            (x + size // 2, y),
            (x + size, y + size // 2),
            (x + size // 2, y + size)
        ]
        pygame.draw.polygon(self.window, BRIGHT_LIME, points)
        pygame.draw.circle(self.window, BLACK, (x + size // 4, y + size // 4), size // 8)
        pygame.draw.circle(self.window, BLACK, (x + 3 * size // 4, y + size // 4), size // 8)

    def draw_food_icon(self, x, y, size):
        """
        Draw a food icon at the specified position.

        Args:
            x (int): The x-coordinate of the top-left corner of the icon.
            y (int): The y-coordinate of the top-left corner of the icon.
            size (int): The size of the icon (diameter).
        """
        pygame.draw.circle(self.window, BRIGHT_MAGENTA, (x + size // 2, y + size // 2), size // 2)
