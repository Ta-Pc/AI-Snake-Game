Copyright 2024 Sipho Zuma

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

# Game dimensions
GRID_WIDTH = 96  # Number of cells horizontally
GRID_HEIGHT = 54  # Number of cells vertically
CELL_SIZE = 20  # Size of each cell in pixels
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)



# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
# Bright colors
BRIGHT_ORANGE = (255, 165, 0)
BRIGHT_CYAN = (0, 255, 255)
BRIGHT_MAGENTA = (255, 0, 255)
BRIGHT_LIME = (0, 255, 0)
BRIGHT_GOLD = (255, 215, 0)
BRIGHT_AQUA = (0, 255, 255)

# Game settings
DEFAULT_UPDATE_RATE = 10
MAX_HIGH_SCORES = 5
LEVEL_UP_TRESHOLD = 50
MAX_COUNTDOWN = 3
REWARD_TRIGER_SCORE = 15

# Game states
AI = "AI"
MENU = "MENU"
PAUSE = "PAUSE"
PLAYING = "PLAYING"
RESUMING = "RESUMING"
GAME_OVER = "GAME_OVER"
CONTINUING = "CONTINUING"
HIGH_SCORES = "HIGH_SCORES"
LEVEL_SELECT = "LEVEL_SELECT"
PROGRESS_WARNING = "PROGRESS_WARNING"
SHOW_MESSAGE = "SHOW_MESSAGE"

# Game Update Rates
LEVEL_1 = 8
LEVEL_2 = 10
LEVEL_3 = 12
LEVEL_4 = 14
LEVEL_5 = 16
LEVEL_6 = 18
LEVEL_7 = 20
LEVEL_8 = 22
GOD_MODE = 80
MENUE_RATE = 8

# Constants.py

EMPTY = 0
SNAKE_BODY = 1
SNAKE_HEAD = 2
FOOD = 3
BIG_FOOD = 4

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
FPS = 60
