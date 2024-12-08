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

from visualization import plot_1d_cost_landscape
import matplotlib.pyplot as plt
from Snake import Snake, Food
from Search import Node, SnakeProblem
from Constants import*

def main():
    snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
    food = Food(snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
    problem = SnakeProblem(snake.head.cell, food.cell)
    plot_1d_cost_landscape(snake, food, problem, CELL_SIZE)


if __name__ == "__main__":
    main()
