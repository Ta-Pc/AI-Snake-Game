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

class MenuButton:
    def __init__(self, text, font, color=WHITE, selected_color=BRIGHT_GOLD):
        self.menu_button_text = self._render_text(text, font, color)
        self.menu_button_selected_text = self._render_text(text, font, selected_color)
        self.button_background = self._create_button_background()
        self.font = font
        self.animation = 0

    def _render_text(self, text, font, color):
        return font.render(text, True, color)
    
    def _create_button_background(self):
        button_bg = pygame.Surface((300, 60), pygame.SRCALPHA)
        pygame.draw.rect(button_bg, (255, 255, 255, 50), button_bg.get_rect(), border_radius=10)
        return button_bg 
    
    @staticmethod
    def _interpolate_color(color1, color2, factor):
        return tuple(int(color1[i] + (color2[i] - color1[i]) * factor) for i in range(3))
    
    def draw(self, window, index, selected=False):
        ## Button Background
            # Slelect the y coordinate starting from the top for the bautton backgrouund
            # Render the background of the button on the window
            button_y = SCREEN_HEIGHT // 2 + index * 80 - 190
            window.blit(self.button_background, (SCREEN_WIDTH // 2 - 150, button_y))
            
            ## Button Text
            # Select the color of the text based on thether it is selected
            color = BRIGHT_GOLD if selected else WHITE
            # Change the center of the the text to the position and render it to the window
            text_rect = self.menu_button_text.get_rect(center=(SCREEN_WIDTH // 2, button_y + 30))
            window.blit(self.menu_button_text, text_rect)

            ## Button Animation
            # If the item is slelcted animate it
            if selected:
                # Compute and update a new value for animation that lies between [0, 2pi)
                self.animation = (self.animation + 0.1) % (2 * math.pi)
                
                # Compute the glow factor [0, 1] using the animation angle [0, 2pi)
                glow_factor = (math.sin(self.animation) + 1) / 2
                # Determine the glow color, shoud it be mostly BRIGHT_GOLD or WHITE (determined by glow factor)
                glow_color = self._interpolate_color(BRIGHT_GOLD, WHITE, glow_factor)
                # Create a transparent surface larger than the button surface (10 x 10)
                glow_surf = pygame.Surface((310, 70), pygame.SRCALPHA)
                # Draw the surface as a rectangle with a smaller border radius radius (15/20)
                pygame.draw.rect(glow_surf, (*glow_color, 100), glow_surf.get_rect(), border_radius=15)
                # Render the surface on the window
                window.blit(glow_surf, (SCREEN_WIDTH // 2 - 155, button_y - 5))
    
class Menu:
    def __init__(self, window, items, tittle_text):
        self.window = window
        self.items = items
        self.font = self._load_fonts()
        self.tittle = MenuButton(tittle_text, self.font['title'], BRIGHT_GOLD)
        self.selected_menu_item = 0
        self.menu_buttons = [MenuButton(item_text, self.font['large']) for index, item_text in enumerate(items)]

    def _load_fonts(self):
        return {
            'small': pygame.font.Font(None, 32),
            'medium': pygame.font.Font(None, 48),
            'large': pygame.font.Font(None, 72),
            'title': pygame.font.Font(None, 96)
        }
    
    @staticmethod
    def _interpolate_color(color1, color2, factor):
        return tuple(int(color1[i] + (color2[i] - color1[i]) * factor) for i in range(3))

    def _create_gradient_background(self):
        background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        for y in range(SCREEN_HEIGHT):
            color = self._interpolate_color(BRIGHT_CYAN, BRIGHT_MAGENTA, y / SCREEN_HEIGHT)
            pygame.draw.line(background, color, (0, y), (SCREEN_WIDTH, y))
        return background

    def _create_menu_background(self):
        menu_bg = pygame.Surface((SCREEN_WIDTH * 0.8, SCREEN_HEIGHT * 0.8), pygame.SRCALPHA)
        pygame.draw.rect(menu_bg, (0, 0, 0, 180), menu_bg.get_rect(), border_radius=20)
        return menu_bg
    
    def _draw_centered_text(self, text_surface, y_offset=0):
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + y_offset))
        self.window.blit(text_surface, text_rect)
    
    def draw(self):
        # Create the backgrounds and render them on screen
        surface_background = self._create_gradient_background()
        menu_background = self._create_menu_background()
        self.window.blit(surface_background, (0, 0))
        self.window.blit(menu_background, (SCREEN_WIDTH * 0.1, SCREEN_HEIGHT * 0.1))

        # Render the title
        self._draw_centered_text(self.tittle.menu_button_text, -250)

        #Iterate through each button and render them on screen
        for index, button in enumerate(self.menu_buttons):
            if self.selected_menu_item == index:
                button.draw(self.window, index, True)
            else: button.draw(self.window, index)

    def navigate_menu(self, direction):
        self.selected_menu_item = (self.selected_menu_item + direction) % len(self.items)

class HUD:
    def __init__(self, window: pygame.Surface):
        """
        Initialize the HUD with necessary components.

        Args:
            window (pygame.Surface): The main game window surface for rendering.
        """
        self.window = window
        self.score = 0 
        self.menu_lists = {
            "main_menu": Menu(self.window, ["New Game", "Continue", "Level", "AI", "High Scores", "Quit"], "Snake Game"),
            "game_level_menu": Menu(self.window, ["EASY", "MEDIUM", "HARD", "VERY HARD"], "Snake Game"),
            "ai_vision_menu": Menu(self.window, ["AI Vision", "AI Play", "AI Experiment"], "Snake Game"),
            "ai_play_menu": Menu(self.window, ["Breadth First", "Depth First", "A Star", "Greedy"], "Snake Game"),
            "high_scores_menu": [[0] * MAX_HIGH_SCORES for _ in range(4)]
        }
        self.current_menu = self.menu_lists['main_menu']

    def draw_menu(self):
        self.current_menu.draw()

    def navigate_menu(self, dir):
        self.current_menu.navigate_menu(dir)

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
