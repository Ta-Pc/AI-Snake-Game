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
from Search import Node
from Search import SnakeProblem
from utils import PriorityQueue
from Snake import Snake
from Snake import Food
from Constants import SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE
from Game import Game
import pygame
from Controls import Controls
from agents import Environment

def move(head_cell, parent_snake):
    """Add head, remove tail, return child that moved"""
    return list([head_cell] + parent_snake[:-1])

def eat(head_cell, parent_snake):
    """Add head, return child that grew an inch"""
    return list([head_cell] + parent_snake)

def ocupiable_cells(nodes, parent_snake: list):
    """Return nodes that avoids the snake body"""
    return [node for node in nodes if node.state not in parent_snake]

def search(snake: Snake, func, problem: SnakeProblem):
    # The snake changes with each action performed
    def _f(items):
        node, _ = items
        return func(node)
    
    init_snake = list([snake.head.cell] + [sbo.cell for sbo in snake.tail])
    node = Node(problem.init_pos)
    frontier = PriorityQueue('min', _f)
    frontier.append((node, init_snake))
    reached = {node.state: node}

    while frontier:
        node, parent_snake = frontier.pop()

        if problem.is_goal(node.state):
            return node.solution()
        
        # For now let us ignore eating
        for child in ocupiable_cells(node.expand(problem), parent_snake):
            state = child.state
            if state not in reached:
                child_snake = move(state, parent_snake)
                frontier.append((child, child_snake))
                reached[state] = node


class Park(Environment):
    def percept(self, agent: Snake):
        things = self.list_things_at(agent.location, Food)
        return things
    
    def execute_action(self, agent:Snake, action):
        if action in ["UP", "DOWN", "LEFT", "RIGHT"]:
            agent.set_direction(action)
            agent.move()
        elif action == "EAT":
            agent.grow(size=1)
            items = self.list_things_at(agent.location)
            if len(items) != 0:
                if agent.is_eating_food(items[0]): #Have the snake eat the first item
                    print('{} ate {} at location: {}'
                          .format(str(agent)[1:-1], str(items[0])[1:-1], agent.location))
                    self.delete_thing(items[0]) #Delete it from the Park after.
                    items[0].replace(agent)
                    self.add_thing(items[0], items[0].cell)

    def is_done(self):
        no_food = not any(isinstance(items, Food) for items in self.things)
        dead_agents = not any(agent.is_alive() for agent in self.agents)
        return no_food or dead_agents

class SnakeInThePark:

    def __init__(self):
        self.actions = deque()
        def snake_program(precepts):
            items = len(precepts)
            for p in precepts:
                if isinstance(p, Food):
                    return "EAT"
            else:
                if len(self.actions) != 0:
                    return self.actions.popleft()
                else: return ""
        self.snake = Snake((200, 200), snake_program) # Top left corner
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.park = Park()
        self.park.add_thing(self.snake, self.snake.location)
        self.park.add_thing(self.food, self.food.cell)
        self.problem = SnakeProblem(self.snake.location, self.food.location)
        self.actions = deque(search(self.snake, lambda node: node.depth, self.problem))
        print(self.actions)
        self.background = self.create_background()

        pygame.init()
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game")

        self.controls = Controls()

        self.running = True

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
    
    def update(self):
        if len(self.actions) == 0:
            self.problem = SnakeProblem(self.snake.location, self.food.cell)
            solution = search(self.snake, lambda node: node.depth, self.problem)
            if solution != None:
                if len(solution) != 0:
                    self.actions = deque(solution)
                    print(self.actions)
            else:
                print("No solution")

    def handle_events(self):
        events = pygame.event.get()
        self.controls.update(events)
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.controls.is_just_pressed(self.controls.ESCAPE):
                    self.park.run(10)
            elif self.controls.is_pressed(self.controls.SPACE):
                self.park.step()

    def draw(self):
        time = pygame.time.get_ticks() / 1000
        self.window.blit(self.background, (0, 0))
        self.snake.draw(self.window, time)
        self.food.draw(self.window)
        pygame.display.flip()

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

experiment = SnakeInThePark()
experiment.run()

pygame.quit()
import sys
sys.exit()
