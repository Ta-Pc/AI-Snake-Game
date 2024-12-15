import json
from collections import deque
from utils.snake import Snake, SnakeBody, Food
from utils.constants import *

class GameSaveManager:
    """
    Manages game states, allowing for capturing, creating, modifying, and restoring game states.
    """
    @staticmethod
    def capture_state(game):
        """Captures the current game state."""
        return {
            "snake_head": game.snake.head.cell,
            "snake_tail": [(sbo.cell[0], sbo.cell[1]) for sbo in game.snake.tail],
            "snake_direction": game.snake.direction,
            "food": game.food.get_state(),
            "score": game.game_hud.score
        }

    @staticmethod
    def create_state(snake_head: tuple, snake_tail: list, snake_direction: str, food: tuple, score: int):
        """Creates a new game state dictionary."""
        return {
           "snake_head": snake_head,
           "snake_tail": snake_tail,
           "snake_direction": snake_direction,
           "food": food,
           "score": score
        }


    @staticmethod
    def modify_state(state, snake_head = None, snake_tail = None, snake_direction = None, food = None, score = None):
        """Creates a modified game state from an existing state."""
        new_state = state.copy()
        if snake_head: new_state["snake_head"] = snake_head
        if snake_tail: new_state["snake_tail"] = snake_tail
        if snake_direction: new_state["snake_direction"] = snake_direction
        if food: new_state["food"] = food
        if score: new_state["score"] = score
        return new_state


    @staticmethod
    def restore_state(state, game):
        """Restores the game state from a given state."""
        if not state: return
        game.snake = Snake(state["snake_head"], program = game.snake.program)
        game.snake.tail = deque([SnakeBody(cell) for cell in state["snake_tail"]])
        game.snake.direction = state["snake_direction"]
         # Check if the 'game_hud' attribute exists before assigning 'score'
        if hasattr(game, 'game_hud') and hasattr(game.game_hud, 'score'):
            game.game_hud.score = state["score"]
        
        if game.food:
            game.food.set_food_cell(state["food"])
        else:
            game.food = Food(game.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
            game.food.set_food_cell(state["food"])


    @staticmethod
    def save_state(state, filename="custom_game_state.json"):
        """Saves a game state to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(state, file)

    @staticmethod
    def load_state(filename="custom_game_state.json"):
        """Loads a game state from a JSON file."""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return None