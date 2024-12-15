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

from collections import deque
from utils.constants import *
from game.agents import *
import pygame
import random
import math
from enum import Enum

class Direction(Enum):
    """Enum class representing possible movement directions."""
    NONE = (0, 0)
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    
    def __init__(self, x, y):
        self.dx = x
        self.dy = y
    
    @property
    def vector(self):
        """Return direction as a tuple of (dx, dy)."""
        return (self.dx, self.dy)
    
    def opposite(self):
        """Return the opposite direction."""
        if self == Direction.NONE:
            return Direction.NONE
        return Direction((-self.dx, -self.dy))
    
    @staticmethod
    def from_vector(vector):
        """Convert a vector (dx, dy) to a Direction."""
        for direction in Direction:
            if direction.vector == vector:
                return direction
        return Direction.NONE


class SnakeBody:
    """
    Represents a segment of the snake's body.

    Attributes:
        cell (tuple): The current position of the segment.
        trail (tuple): The previous position of the segment.
    """

    def __init__(self, cell: tuple, program = None):
        """
        Initialize a SnakeBody segment.

        Args:
            cell (tuple): The initial position of the segment.
        """
        self.alive = True
        self.bump = False
        self.holding = []
        self.performance = 0
        self.cell = cell
        self.trail = cell
        self.active = True
        
    def move(self, disp: tuple):
        """
        Move the segment by a given displacement.

        Args:
            disp (tuple): The displacement to move the segment by.
        """
        self.trail = self.cell
        self.cell = ((self.cell[0] + disp[0]) % SCREEN_WIDTH, 
                     (self.cell[1] + disp[1]) % SCREEN_HEIGHT)
        
    def follow(self, new_trail: tuple):
        """
        Make the segment follow a new position.

        Args:
            new_trail (tuple): The new position to follow.
        """
        self.trail = self.cell
        self.cell = new_trail

class Rat(Agent):
    """
    Represents the Rat in the game.

    Attributes:
        head (SnakeBody): The head segment of the Rat.
        tail (deque): The Rat's tail.
        direction (str): The current direction of the Rats's movement.
        direction_map (dict): A mapping of directions to displacement tuples.
    """

    def __init__(self, initial_position: tuple):
        """
        Initialize a Rat object.

        Args:
            initial_position (tuple): The starting position of the snake's head.
        """
        self.head = SnakeBody(initial_position)
        
        self.head.trail = (initial_position[0] - CELL_SIZE, initial_position[1])
        self.direction = "UP"
        self.active = True
        self.direction_map = {
            "UP": (0, -CELL_SIZE),
            "DOWN": (0, CELL_SIZE),
            "LEFT": (-CELL_SIZE, 0),
            "RIGHT": (CELL_SIZE, 0)
        }
    
    def move(self):
        """Move the Rat in its current direction."""
        disp = self.direction_map[self.direction]
        self.head.move(disp)
    
    def set_direction(self, new_direction):
        """
        Set a new direction for the Rat.

        Args:
            new_direction (str): The new direction to set.
        """
        if new_direction in self.direction_map:
            self.direction = new_direction
    
    
    def actionable_directions_map(self):
        return self.direction_map.items()

    def is_eating_food(self, food):
        """
        Check if the Rat is eating food.

        Args:
            food (Food): The food object to check against.

        Returns:
            bool: True if the Rat's head is on the food, False otherwise.
        """
        if food.active:
            return self.head.cell == food.cell
        return False

    def draw(self, surface, time):
        """
        Draw the snake on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw on.
            time (float): The current game time, used for visual effects.
        """
        # Draw head
        head_rect = pygame.Rect(self.head.cell[0], self.head.cell[1], CELL_SIZE, CELL_SIZE)
        VisualEffects.draw_rounded_rectangle(surface, BRIGHT_MAGENTA, head_rect, 5)
        
        # Draw eyes
        eye_radius = CELL_SIZE // 6
        left_eye = (self.head.cell[0] + CELL_SIZE // 3, self.head.cell[1] + CELL_SIZE // 3)
        right_eye = (self.head.cell[0] + 2 * CELL_SIZE // 3, self.head.cell[1] + CELL_SIZE // 3)
        pygame.draw.circle(surface, WHITE, left_eye, eye_radius)
        pygame.draw.circle(surface, WHITE, right_eye, eye_radius)
        
        # Draw pupils
        pupil_radius = eye_radius // 2
        pygame.draw.circle(surface, BLACK, left_eye, pupil_radius)
        pygame.draw.circle(surface, BLACK, right_eye, pupil_radius)

class Snake(Agent):
    """
    Represents the snake in the game.

    Attributes:
        head (SnakeBody): The head segment of the snake.
        tail (deque): A deque of SnakeBody segments representing the snake's tail.
        direction (str): The current direction of the snake's movement.
        direction_map (dict): A mapping of directions to displacement tuples.
        body_colors (list): A list of colors for the snake's body segments.
        length (int): The current length of the snake.
        opp_direction_map (dict): A mapping of directions to their opposites.
        time (int): A time counter for the snake.
    """

    def __init__(self, initial_position: tuple, program = None):
        """
        Initialize a Snake object.

        Args:
            initial_position (tuple): The starting position of the snake's head.
        """
        super().__init__(program)
        self.head = SnakeBody(initial_position)
        self.head.trail = (initial_position[0], initial_position[1] + CELL_SIZE)
        self.tail = deque([SnakeBody(self.head.trail)])
        self.direction = "UP"  # Up corelates with the snakes head trail
        self.active = True
        self.direction_map = {
            "UP": (0, -CELL_SIZE),
            "DOWN": (0, CELL_SIZE),
            "LEFT": (-CELL_SIZE, 0),
            "RIGHT": (CELL_SIZE, 0)
        }
        self.body_colors = [BRIGHT_MAGENTA] + [self.get_gradient_color(i) for i in range(1, 20)]
        self.length = len(self.tail) + 1
        self.opp_direction_map = {
            'UP': 'DOWN',
            'RIGHT': 'LEFT',
            'DOWN': 'UP',
            'LEFT': 'RIGHT'
        }
        self.time = 0
        self.location = self.head.cell
        
    @classmethod
    def from_saved_state(cls, saved_state, direction):
        """
        Create a Snake object from a saved state.

        Args:
            saved_state (list): A list of positions representing the snake's body.
            direction (str): The direction the snake was facing in the saved state.

        Returns:
            Snake: A new Snake object initialized with the saved state.
        """
        if not saved_state or len(saved_state) < 1:
            return cls((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        
        snake = cls(tuple(saved_state[0]))
        snake.tail = deque([SnakeBody(tuple(cell)) for cell in saved_state[1:]])
        snake.direction = direction
        return snake

    def get_state(self):
        """
        Get the current state of the snake.

        Returns:
            list: A list of tuples representing the positions of the snake's body segments.
        """
        return [(self.head.cell[0], self.head.cell[1])] + [(segment.cell[0], segment.cell[1]) for segment in self.tail]
    
    def move(self):
        """Move the snake in its current direction."""
        if self.direction:
            disp = self.direction_map[self.direction]
            self.head.move(disp)
            self.location = self.head.cell
            if self.tail:
                self.tail[0].follow(self.head.trail)
                for i in range(1, len(self.tail)):
                    self.tail[i].follow(self.tail[i - 1].trail)
    
    def set_direction(self, new_direction):
        """
        Set a new direction for the snake.

        Args:
            new_direction (str): The new direction to set.
        """
        if self.direction:
            if new_direction in self.direction_map and new_direction != self.opp_direction_map[self.direction]:
                self.direction = new_direction
        else:
            if new_direction in self.direction_map:
                self.direction = new_direction
    
    def grow(self, size: int):
        """
        Grow the snake by a specified number of segments.

        Args:
            size (int): The number of segments to grow by.
        """
        if self.tail:
            for _ in range(size):
                self.tail.append(SnakeBody(self.tail[-1].trail))
        else:
            self.tail.append(SnakeBody(self.head.trail))
        self.length += size
    
    def is_eating_self(self):
        """
        Check if the snake is eating itself.

        Returns:
            bool: True if the snake's head is touching its body, False otherwise.
        """
        return any(self.head.cell == segment.cell for segment in self.tail)
    
    def actionable_directions_map(self):
        """Returns direction and disp"""
        return [(direction, displacement) for direction, displacement in self.direction_map.items() if direction != self.opp_direction_map[self.direction]]

    def is_eating_food(self, food):
        """
        Check if the snake is eating food.

        Args:
            food (Food): The food object to check against.

        Returns:
            bool: True if the snake's head is on the food, False otherwise.
        """
        if food.active:
            return self.head.cell == food.cell
        return False

    def get_gradient_color(self, index):
        """
        Get a color for a body segment based on its index.

        Args:
            index (int): The index of the body segment.

        Returns:
            list: An RGB color value.
        """
        start_color = BRIGHT_MAGENTA
        end_color = BRIGHT_ORANGE
        t = index / 20
        return [
            int(start_color[i] + (end_color[i] - start_color[i]) * t)
            for i in range(3)
        ]

    def draw(self, surface, time):
        """
        Draw the snake on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw on.
            time (float): The current game time, used for visual effects.
        """
        # Draw head
        head_rect = pygame.Rect(self.head.cell[0], self.head.cell[1], CELL_SIZE, CELL_SIZE)
        VisualEffects.draw_rounded_rectangle(surface, BRIGHT_MAGENTA, head_rect, 5)
        
        # Draw eyes
        eye_radius = CELL_SIZE // 6
        left_eye = (self.head.cell[0] + CELL_SIZE // 3, self.head.cell[1] + CELL_SIZE // 3)
        right_eye = (self.head.cell[0] + 2 * CELL_SIZE // 3, self.head.cell[1] + CELL_SIZE // 3)
        pygame.draw.circle(surface, WHITE, left_eye, eye_radius)
        pygame.draw.circle(surface, WHITE, right_eye, eye_radius)
        
        # Draw pupils
        pupil_radius = eye_radius // 2
        pygame.draw.circle(surface, BLACK, left_eye, pupil_radius)
        pygame.draw.circle(surface, BLACK, right_eye, pupil_radius)

        # Draw body segments with gradient effect
        for i, segment in enumerate(self.tail):
            color = self.body_colors[min(i, len(self.body_colors) - 1)]
            segment_rect = pygame.Rect(segment.cell[0], segment.cell[1], CELL_SIZE, CELL_SIZE)
            VisualEffects.draw_shimmering_effect(surface, segment_rect, color, BRIGHT_GOLD, time)

class Cheese(Thing):
    """
    Represents cheese in the game.

    Attributes:
        bound_x (int): The x-bound of the game area.
        bound_y (int): The y-bound of the game area.
        rat (Rat): The rat object, used to avoid placing cheese on the rat.
        radius (int): The radius of the cheese item.
        cell (tuple): The current position of the cheese.
        score_increment (int): The score value of the cheese.
        active (bool): Whether the cheese is currently active.
    """

    def __init__(self, rat: Snake, bounds: tuple):
        """
        Initialize a Food object.

        Args:
            snake (Snake): The snake object in the game.
            bounds (tuple): The bounds of the game area.
        """
        self.bound_x, self.bound_y = bounds
        self.rat = rat
        self.radius = CELL_SIZE // 2
        self.cell = self.place()
        self.score_incriment = 2
        self.active = True

    def draw(self, surface):
        """
        Draw the cheese on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw on.
        """
        VisualEffects.draw_gradient_circle(
            surface,
            (self.cell[0] + CELL_SIZE // 2, self.cell[1] + CELL_SIZE // 2),
            self.radius,
            YELLOW,
            BRIGHT_GOLD
        )
        
    def place(self):
        """
        Place the cheese in a random position not occupied by the rat.

        Returns:
            tuple: The new position of the cheese.
        """
        snake_body_set = {self.rat.head.cell}
        available_positions = [
            (x, y)
            for x in range(0, self.bound_x, CELL_SIZE)
            for y in range(0, self.bound_y, CELL_SIZE)
            if (x, y) not in snake_body_set
        ]
        x, y = random.choice(available_positions) if available_positions else (0, 0)
        self.rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        self.center = (x + self.radius, y + self.radius)
        self.locatoion = (x, y)
        return (x, y)
    
    def replace(self):
        """Reposition the cheese to a new random location."""
        self.cell = self.place()

class Food(Thing):
    """
    Represents food in the game.

    Attributes:
        bound_x (int): The x-bound of the game area.
        bound_y (int): The y-bound of the game area.
        snake (Snake): The snake object, used to avoid placing food on the snake.
        radius (int): The radius of the food item.
        cell (tuple): The current position of the food.
        score_increment (int): The score value of the food.
        active (bool): Whether the food is currently active.
    """

    def __init__(self, snake: Snake, bounds: tuple):
        """
        Initialize a Food object.

        Args:
            snake (Snake): The snake object in the game.
            bounds (tuple): The bounds of the game area.
        """
        self.bound_x, self.bound_y = bounds
        self.radius = CELL_SIZE // 2
        self.cell = self.place(snake)
        self.score_incriment = 2
        self.active = True

    def draw(self, surface):
        """
        Draw the food on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw on.
        """
        VisualEffects.draw_gradient_circle(
            surface,
            (self.cell[0] + CELL_SIZE // 2, self.cell[1] + CELL_SIZE // 2),
            self.radius,
            BRIGHT_LIME,
            BRIGHT_GOLD
        )
        
    def place(self, snake):
        """
        Place the food in a random position not occupied by the snake. Update location center and rect

        Returns:
            tuple: The new position of the food.
        """
        snake_body_set = {(segment.cell[0], segment.cell[1]) for segment in [snake.head] + list(snake.tail)}
        available_positions = [
            (x, y)
            for x in range(0, self.bound_x, CELL_SIZE)
            for y in range(0, self.bound_y, CELL_SIZE)
            if (x, y) not in snake_body_set
        ]
        x, y = random.choice(available_positions) if available_positions else (0, 0)
        self.rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        self.center = (x + self.radius, y + self.radius)
        self.location = (x, y)
        return (x, y)
    
    def set_food_cell(self, location):
        x, y = location
        self.rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
        self.center = (x + self.radius, y + self.radius)
        self.location = (x, y)
        self.cell = (x, y)
    
    def replace(self, snake):
        """Reposition the food to a new random location."""
        self.cell = self.place(snake)

    @classmethod
    def from_saved_state(cls, saved_state, snake, screen_size):
        """
        Create a Food object from a saved state.

        Args:
            saved_state (tuple): The saved position of the food.
            snake (Snake): The snake object in the game.
            screen_size (tuple): The size of the game screen.

        Returns:
            Food: A new Food object initialized with the saved state.
        """
        food = cls(snake, screen_size)
        if saved_state:
            food.cell = tuple(saved_state)
            food.center = (food.cell[0] + CELL_SIZE // 2, food.cell[1] + CELL_SIZE // 2)
        return food

    def get_state(self):
        """
        Get the current state of the food.

        Returns:
            tuple: The current position of the food.
        """
        return self.cell

class BigFood(Food):
    """
    Represents a special, high-value food item in the game.

    Inherits from Food and adds time-limited activation and visual effects.

    Additional Attributes:
        max_time_active (float): The maximum time the big food can remain active.
        enabled_time (int): The time when the big food was last activated.
    """

    def __init__(self, snake: Snake, bounds: tuple, sec):
        """
        Initialize a BigFood object.

        Args:
            snake (Snake): The snake object in the game.
            bounds (tuple): The bounds of the game area.
            sec (float): The time used to calculate the maximum active time.
        """
        super().__init__(snake, bounds)
        self.max_time_active = self._get_max_active_time(sec)
        self.score_incriment = 10
        self.radius = int(CELL_SIZE // 1.5)
        self.is_active(False)
        
    def _get_max_active_time(self, sec):
        """
        Calculate the maximum time the big food can remain active.

        Args:
            sec (float): The time used in the calculation.

        Returns:
            float: The maximum active time for the big food.
        """
        return (math.sqrt(SCREEN_WIDTH**2 + SCREEN_HEIGHT**2) / CELL_SIZE) / sec + 2

    def draw(self, surface, time):
        """
        Draw the big food on the given surface with a pulsating effect.

        Args:
            surface (pygame.Surface): The surface to draw on.
            time (float): The current game time, used for the pulsating effect.
        """
        if self.active:
            pulse = (math.sin(time * 2 * math.pi) + 1) / 2  # Oscillates between 0 and 1
            radius = int(self.radius * (0.8 + 0.2 * pulse))  # Pulsates between 80% and 100% of original size
            VisualEffects.draw_gradient_circle(
                surface,
                (self.cell[0] + CELL_SIZE // 2, self.cell[1] + CELL_SIZE // 2),
                radius,
                RED,
                WHITE
            )

    def is_active(self, state: bool):
        """
        Set the active state of the big food.

        Args:
            state (bool): The new active state.
        """
        if state:
            self.score_incriment = 10
            self.active = True
            self.enabled_time = pygame.time.get_ticks() // 1000
        else:
            self.score_incriment = 0
            self.active = False

    def update(self):
        """Update the state of the big food, deactivating it if its time has expired."""
        if self.active:
        # Check if food should disappear
            if self.enabled_time + self.max_time_active < pygame.time.get_ticks() // 1000:
                self.is_active(False)

class VisualEffects:
    """A utility class for creating various visual effects in the game."""

    @staticmethod
    def draw_rounded_rectangle(surface, color, rect, corner_radius):
        """
        Draw a rounded rectangle on the given surface.

        Args:
            surface (pygame.Surface): The surface to draw on.
            color (tuple): The color of the rectangle.
            rect (pygame.Rect): The rectangle to draw.
            corner_radius (int): The radius of the rounded corners.
        """
        pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

    @staticmethod
    def draw_gradient_circle(surface, center, radius, inner_color, outer_color):
        """
        Draw a circle with a color gradient from inner to outer color.

        Args:
            surface (pygame.Surface): The surface to draw on.
            center (tuple): The center position of the circle.
            radius (int): The radius of the circle.
            inner_color (tuple): The color at the center of the circle.
            outer_color (tuple): The color at the edge of the circle.
        """
        for i in range(radius, 0, -1):
            alpha = int(255 * (i / radius))
            color = [
                inner_color[j] + (outer_color[j] - inner_color[j]) * (1 - i / radius)
                for j in range(3)
            ]
            color.append(alpha)
            pygame.draw.circle(surface, color, center, i)

    @staticmethod
    def draw_shimmering_effect(surface, rect, base_color, shimmer_color, time):
        """
        Draw a rectangle with a shimmering effect.

        Args:
            surface (pygame.Surface): The surface to draw on.
            rect (pygame.Rect): The rectangle to draw.
            base_color (tuple): The base color of the rectangle.
            shimmer_color (tuple): The color of the shimmer effect.
            time (float): The current time, used to animate the shimmer.
        """
        shimmer_intensity = (math.sin(time * 5) + 1) / 2  # Oscillates between 0 and 1
        color = [
            base_color[i] + (shimmer_color[i] - base_color[i]) * shimmer_intensity
            for i in range(3)
        ]
        pygame.draw.rect(surface, color, rect, border_radius=10)

class SnakeEnvironment(Environment):
    """
    Represents the environment in which the snake game takes place.
    """
    def __init__(self, things, agents):
        """
        Initialize the SnakeEnvironment.

        Args:
            food (Food): The regular food object.
            big_food (BigFood): The big food object.
            snake (Snake): The snake object.
            hud (HUD): The heads-up display object.
        """
        self.things = things
        self.agents = agents
        self.eat_count = 0
    
    def percept(self, agent):
        things = None
        for agent in self.agents:
            if isinstance(agent, Snake):
                things = self.list_things_at(agent.head.cell)
        return things
    
    def execute_action(self, agent, action):
        """Change the state of an environment based on what the agent does"""
        if action in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            print(f"{str(agent)[1:-1]} decided to move its head {action} at location: {agent.head.cell}")
            agent.set_direction(action)
            agent.move()
        elif action == "EAT":
            items = self.list_things_at(agent.head.cell)
            if len(items) != 0:
                if isinstance(items[0], Food):
                    agent.grow(size=1)
                    items[0].replace()
                    self.eat_count += 1
                if self.eat_count == REWARD_TRIGER_SCORE:
                    self.eat_count = 0
                    for thing in self.things:
                        if isinstance(thing, BigFood):
                            if not thing.active:
                                thing.replace()
                                thing.is_active(True)
                

    def get_game_map(self):
        """
        Returns a 2D list representing the current game map.

        The map uses the following encoding:
        0: Empty cell
        1: Snake body
        2: Snake head
        3: Food
        4: Big Food

        Returns:
            list of lists: A 2D list representing the game map.
        """
        # Initialize the game map with empty cells
        game_map = [[0 for _ in range(SCREEN_HEIGHT // CELL_SIZE)] for _ in range(SCREEN_HEIGHT // CELL_SIZE)]
        
        # Place the snake body
        for segment in self.snake.tail:
            x, y = segment.cell
            game_map[y // CELL_SIZE][x // CELL_SIZE] = 1
        
        # Place the snake head
        head_x, head_y = self.snake.head.cell
        game_map[head_y // CELL_SIZE][head_x // CELL_SIZE] = 2
        
        # Place the regular food if active
        if self.food.active:
            food_x, food_y = self.food.cell
            game_map[food_y // CELL_SIZE][food_x // CELL_SIZE] = 3
        
        # Place the big food if active
        if self.big_food.active:
            big_food_x, big_food_y = self.big_food.cell
            game_map[big_food_y // CELL_SIZE][big_food_x // CELL_SIZE] = 4
        
        return game_map
