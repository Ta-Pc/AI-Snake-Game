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