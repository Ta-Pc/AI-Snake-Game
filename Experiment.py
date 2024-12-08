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

from Game import Game
import pygame
from Snake import *
from Search import *
from Constants import *
from GameState import GameState
import logging
import os
os.system('color')  # Enable ANSI colors in Windows terminal

# ANSI escape codes for colors
ANSIRESET = "\033[0m"
ANSIRED = "\033[91m"
ANSIGREEN = "\033[92m"
ANSIYELLOW = "\033[93m"
ANSIBLUE = "\033[94m"
ANSICYAN = "\033[96m"
ANSIWHITE = "\033[97m" 

# Function to apply color
def color_text(text, color):
    return f"{color}{text}{ANSIRESET}"

logger = logging.getLogger("Experimental Log")
logger.setLevel(logging.DEBUG)
formater = logging.Formatter('%(asctime)s - %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formater)
logger.addHandler(ch)

class ExperimentState(GameState):
    def enter(self, game: Game):
        game.display_message("This is an experiment", duration=4000)

    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed(game.controls.ESCAPE):
            from GameUI import AIGameSelectState
            game.change_state(AIGameSelectState())
        elif game.controls.is_just_pressed(game.controls.SPACE):
            from GameUI import PauseState
            game.change_state(PauseState())
    
    def update(self, game: Game):
        game.clock.tick(game.game_update_rate)
    
    def draw(self, game: Game):
        time = pygame.time.get_ticks() / 1000
        game.window.fill(BLACK)
        game.draw_message()
    
    def exit(self, game: Game):
        game.previous_state = self


class GraphCreationVisionLocalSearch_Exp(ExperimentState):
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.big_food = BigFood(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT), 2)
        self.node_size = self.compute_node_size()
        self.rand_fact = 0
        self.initialize()

    def cost(self, node):
        return self.problem.heuristic1(node.state) + self.problem.heuristic2(node.state)

    def compute_node_size(self):
        self.offset = (CELL_SIZE // 2, CELL_SIZE // 2)
        return self.offset[0] - 5

    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)
            elif game.controls.is_pressed(game.controls.SPACE):
                self.step(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed(game.controls.ESCAPE):
            game.running = False
        elif game.controls.is_pressed(game.controls.SELECT):
            self.step(game)
        elif game.controls.is_just_pressed(game.controls.UP):
            game.game_update_rate += 2
        elif game.controls.is_just_pressed(game.controls.DOWN):
            game.game_update_rate -= 2

    def draw(self, game: Game):
        time = pygame.time.get_ticks() / 1000
        game.window.fill(BLACK)  # White background
        self.draw_grid(game.window)
        self.draw_nodes(game.window)
        self.food.draw(game.window)
        self.snake.draw(game.window, time)

    def draw_grid(self, window):
        # Draw grid lines here
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(window, WHITE, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(window, WHITE, (0, y), (SCREEN_WIDTH, y))

    def draw_nodes(self, window):
        # Draw nodes here, using different colors for different types
        self.node.draw_solution(window, LIGHT_GRAY)

    def update(self, game: Game):
        pass

    def step(self, game: Game):
        # Get solution and move snake
        self.snake.set_direction(self.find_solution())
        self.snake.move()

        if self.snake.is_eating_food(self.food):
            self.food.replace(self.snake)
            self.snake.grow(3)
            self.initialize()

        game.clock.tick(game.game_update_rate)

    def find_solution(self):
        # Remove the plotting from here and keep only the solution finding logic
        new_snake = list([self.snake.head.cell] + [sbo.cell for sbo in self.snake.tail])
        neighbours = ocupiable_cells(self.node.expand(self.problem), new_snake)
        self.node = self.select_best_amoungst(neighbours)
        return self.node.action

    def initialize(self):
        self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
        self.node = Node(self.problem.init_pos)
        self.updates = 1

    def select_best_amoungst(self, neighbours: list):
        if neighbours:
            best_node = neighbours.pop()
            best_cost = self.cost(best_node)

            for child_node in neighbours:
                child_cost = self.cost(child_node)
                logger.debug(f"{color_text("Child node", ANSIWHITE)}: {child_node} has cost: {child_cost}")
                if child_cost < best_cost:
                    logger.debug(f"{color_text("Chosen node", ANSICYAN)}: {child_node} has cost: {child_cost} < {best_cost}")
                    best_node = child_node
                    best_cost = child_cost
            return best_node
        return None




#********************************************************************************************************************
# Past Experiments
#********************************************************************************************************************
# This advancement has not yet been implemented
class GraphCreationVisionBFS_Exp_Origional(ExperimentState):
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.big_food = BigFood(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT), 2)
        self.node_size = self.compute_node_size()
        self.rand_fact = 0
        self.f = self.f
        self.initialize()

    def f(self, items):
        node, _ = items
        randomness = random.uniform(1 - self.rand_fact, 1 + self.rand_fact)
        
        return self.problem.path_cost(node) + self.problem.heuristic1(node.state) * randomness
    
    def compute_node_size(self):
        self.offset = (CELL_SIZE // 2, CELL_SIZE // 2)
        return self.offset[0] - 5

    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)
            elif game.controls.is_pressed(game.controls.SPACE):
                self.step(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed(game.controls.ESCAPE):
            game.running = False
        elif game.controls.is_pressed(game.controls.SELECT):
            self.step(game)
        elif game.controls.is_just_pressed(game.controls.UP):
            game.game_update_rate += 2
        elif game.controls.is_just_pressed(game.controls.DOWN):
            game.game_update_rate -= 2

    def draw(self, game: Game):
        time = pygame.time.get_ticks() / 1000
        game.window.fill(BLACK)  # White background
        #self.draw_map(game.window)
        self.draw_grid(game.window)
        self.draw_edges(game.window)
        self.draw_step_count(game.window)
        self.draw_nodes(game.window)
        self.food.draw(game.window)
        self.snake.draw(game.window, time)

    def draw_grid(self, window):
        # Draw grid lines here
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(window, WHITE, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(window, WHITE, (0, y), (SCREEN_WIDTH, y))

    def draw_nodes(self, window):
        # Draw nodes here, using different colors for different types
        if self.solution:
            self.node.draw_solution(window, LIGHT_GRAY)
        else:
            #return
            if self.reached:
                for _, node in self.reached.items():
                    node.draw(self.offset, window, BLUE, self.node_size, 5)

            for item in self.frontier.heap:
                item[1][0].draw(self.offset, window, RED, self.node_size, 15)


    def draw_edges(self, window):
        # Draw edges between nodes here
        pass

    def draw_step_count(self, window):
        # Draw the step count on the screen
        pass

    def draw_map(self, window):
        surface = self.graph.graph_dict
        for x, y in surface:
            rect = (x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(window, DARK_GRAY, rect)

    def update(self, game: Game):
        pass

    def step(self, game: Game):
        # Simulating a star algorithm
        for _ in range(self.updates):
            self.solution = self.find_solution(game)
            if self.solution: break

        self.plot_1d_cost_landscape(self.snake, self.food, self.problem, CELL_SIZE)

        if self.solution:
            action = self.solution.popleft()
            self.snake.set_direction(action)
            self.snake.move()

        if self.snake.is_eating_food(self.food):
            self.food.replace(self.snake)
            self.snake.grow(3)
            self.initialize()

        game.clock.tick(game.game_update_rate)

    def exit(self, game: Game):
        pass

    def find_solution(self, game: Game):
        if self.frontier and not self.solution:
            self.node, parent_snake = self.frontier.pop()

            if  self.problem.is_goal(self.node.state):
                self.updates = 0
                return deque(self.node.solution())
            else:
                for child in ocupiable_cells(self.node.expand(self.problem), parent_snake):
                    state = child.state
                    if state not in self.reached or child.path_cost < self.reached[state].path_cost:
                        child_snake = move(state, parent_snake)
                        self.reached[state] = child
                        self.frontier.append((child, child_snake))
        return None
    
    def initialize(self):
        init_snake = list([self.snake.location] + [sbo.cell for sbo in self.snake.tail])
        self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
        self.node = Node(self.problem.init_pos)
        self.frontier = PriorityQueue('min', self.f)
        self.frontier.append((self.node, init_snake))
        self.reached = {self.node.state : self.node}
        self.solution = deque()
        self.updates = 1

class AIPlayerBFSStateExp(ExperimentState):
    """Depricated experiment, this does not work because I removed next food out of the picture"""
    def enter(self, game: Game):

        def program(precept):
            for p in precept:
                if isinstance(p, Food):
                    return "EAT"
                elif isinstance(p, BigFood):
                    return "EAT"
            else: return self.actions.pop(0)

        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.big_food = BigFood(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT), sec=2)
        self.f = lambda node: node.depth
        self.find_path_to_food(self.food)
        self.eat_count = 0
        game.game_hud.score = 0
        things = [self.big_food, self.food]
        agents = [self.snake]
        #self.env = SnakeEnvironment(things, agents)
        game.display_message("Computer is playing, it implements BFSearch", duration=4000)
    
    def update(self, game):
        pass

    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)
            elif game.controls.is_pressed('SPACE'):
                self.step(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed(game.controls.ESCAPE):
            game.running = False
        elif game.controls.is_just_pressed(game.controls.SELECT):
            self.step(game)
    
    def step(self, game: Game):
        if self.actions:
            action = self.actions.popleft()
            self.snake.set_direction(action)
            self.snake.move()

        self.big_food.update()
        if self.snake.is_eating_food(self.food):
            self.snake.grow(size=1)
            self.food.replace(self.snake)
            self.eat_count += 1
            if self.eat_count == REWARD_TRIGER_SCORE:
                self.eat_count = 0
                if not self.big_food.active:
                    self.big_food.replace(self.snake)
                    self.big_food.is_active(True)
                self.find_path_to_food(self.big_food)
            else:
                self.find_path_to_food(self.food)
            game.game_hud.increase_score(self.food.score_incriment)
                
        elif self.snake.is_eating_food(self.big_food):
            game.game_hud.increase_score(self.big_food.score_incriment)
            self.snake.grow(size=5)
            self.big_food.is_active(False)
            self.find_path_to_food(self.food)

        if self.snake.is_eating_self():
                game.game_hud.update_high_score()
                print("--------------------------------------------------------------------------------------------")
                print("SNAKE ATE ITSELF")
                print(logger.name)

                # Get the tail positions and find which one matches the head
                head_pos = self.snake.head.cell
                tail_positions = [sbo.cell for sbo in self.snake.tail]
                collision_pos = next(pos for pos in tail_positions if pos == head_pos)
                
                # Format the tail list with colored matching position
                colored_tail = []
                for pos in tail_positions:
                    if pos == collision_pos:
                        colored_tail.append(f"\033[92m{pos}\033[0m")  # Green color
                    else:
                        colored_tail.append(str(pos))
                
                logger.debug(f"Snake: head - \033[92m{head_pos}\033[0m, tail - [{', '.join(colored_tail)}] - len = {len(self.snake.tail)}")
                logger.debug(f"Food: current food pos - {self.food.cell}")
                logger.debug(f"Problem: curent state - {self.problem.init_pos}, goal state - {self.problem.goal_pos}")
                print("--------------------------------------------------------------------------------------------")
                from GameUI import GameOverState
                game.change_state(GameOverState())

        game.clock.tick(game.game_update_rate)
    
    def draw(self, game: Game):
        time = pygame.time.get_ticks() / 1000
        if self.food:
            self.food.draw(game.window)
        if self.big_food:
            self.big_food.draw(game.window, time)
        if self.snake:
            self.snake.draw(game.window, time)
        game.draw_message()
        game.game_hud.draw_score()
        pygame.draw.rect(game.window, BRIGHT_AQUA, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 3)
    
    def exit(self, game: Game):
        game.previous_state = self

    def find_path_to_food(self, food):
        self.problem = SnakeProblem(self.snake.location, food.location)
        func = lambda node: node.depth + (self.problem.heuristic2(node.state))
        self.actions = best_first_search(self.problem, func, self.snake)


class ExperimentState1(ExperimentState):
    """This is a bidirectional search experiment"""
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        snake_reverse = list(reversed(self.snake.tail))
        snake_positions = deque([segment.cell for segment in snake_reverse] + [self.snake.head.cell])
        def a_star(items):
            node, _ = items
            #randomness = random.uniform(1 - 0.2, 1 + 0.2) # I want to try adding some randomness
            return (node.path_cost + self.problemF.heuristic2(node.state))
        
        def best_first(items):
            node, _ = items
            #randomness = random.uniform(1 - 0.2, 1 + 0.2)
            return node.path_cost
        
        self.fF = best_first
        self.fB = best_first
        self.problemF = SnakeProblem(self.snake.head.cell, self.food.cell)
        self.problemB = SnakeProblem(self.food.cell, self.snake.head.cell)
        self.nodeF = Node(self.problemF.init_pos)
        self.nodeB = Node(self.problemB.init_pos)
        self.frontierF = PriorityQueue('min', self.fF)
        self.frontierB = PriorityQueue('min', self.fB)
        self.frontierF.append((self.nodeF, snake_positions))
        self.frontierB.append((self.nodeB, snake_positions))
        self.reachedF = {self.nodeF.state: self.nodeF}
        self.reachedB = {self.nodeB.state: self.nodeB}
        self.offset = (CELL_SIZE // 2, CELL_SIZE // 2)
        self.node_size = self.offset[0] - 5
        self.solution = None
        self.actions = deque()
        self.updates = 20
        game.display_message("Bidirectional breadth first search experiment", duration=4000)

    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed('ESCAPE'):
            game.running = False
        elif game.controls.is_just_pressed('SPACE'):
            from GameUI import PauseState
            game.change_state(PauseState())

    def next_step(self):
        # Implement your graph expansion logic here
        # Update self.graph, self.frontier, self.reached, and self.current_node
        self.step_count += 1

    def draw(self, game: Game):
        time = pygame.time.get_ticks() / 1000
        game.window.fill(BLACK)
        self.draw_grid(game.window)
        self.draw_nodes(game.window)
        game.draw_message()
        
        self.food.draw(game.window)
        self.snake.draw(game.window, time)

    def draw_grid(self, window):
        # Draw grid lines here
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(window, WHITE, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(window, WHITE, (0, y), (SCREEN_WIDTH, y))

    def draw_nodes(self, window):
        # Draw nodes here, using different colors for different types
        if self.actions:
            self.solution.draw_solution(window, LIGHT_GRAY)
        else:
            for _, node in self.reachedF.items():
                node.draw(self.offset, window, RED, self.node_size, 5)

            for _, node in self.reachedB.items():
                node.draw(self.offset, window, BRIGHT_LIME, self.node_size, 5)


            for item in self.frontierF.heap:
                item[1][0].draw(self.offset, window, BLUE, self.node_size, 15)

            for item in self.frontierB.heap:
                item[1][0].draw(self.offset, window, BRIGHT_GOLD, self.node_size, 15)


    def draw_map(self, window):
        surface = self.graph.graph_dict
        for x, y in surface:
            rect = (x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(window, DARK_GRAY, rect)

    def update(self, game: Game):
        # Simulating bidirectional breadth first search
        for _ in range(self.updates):
            if not self.terminated(self.solution, self.frontierF, self.frontierB) and not self.actions:
                if self.fF(self.frontierF.heap[0][1]) < self.fB(self.frontierB.heap[0][1]):
                    self.solution = self.proceed("F", self.problemF, self.frontierF, self.reachedF, self.reachedB, self.solution)
                else:
                    self.solution = self.proceed("B", self.problemB, self.frontierB, self.reachedB, self.reachedF, self.solution)
            else:
                self.actions = self.solution.solution()
                self.updates = 0

        if self.actions:
            action = self.actions.pop() #This is the problem the order in whoch actions are performed matters
            self.snake.set_direction(action)
            self.snake.move()

        if self.snake.is_eating_food(self.food):
            self.food.replace(self.snake)
            self.snake.grow(3)
            snake_reverse = list(reversed(self.snake.tail))
            snake_positions = deque([segment.cell for segment in snake_reverse] + [self.snake.head.cell])
            self.problemF = SnakeProblem(self.snake.head.cell, self.food.cell)
            self.problemB = SnakeProblem(self.food.cell, self.snake.head.cell)
            self.nodeF = Node(self.problemF.init_pos)
            self.nodeB = Node(self.problemB.init_pos)
            self.frontierF = PriorityQueue('min', self.fF)
            self.frontierB = PriorityQueue('min', self.fB)
            self.frontierF.append((self.nodeF, snake_positions))
            self.frontierB.append((self.nodeB, snake_positions))
            self.reachedF = {self.nodeF.state: self.nodeF}
            self.reachedB = {self.nodeB.state: self.nodeB}
            self.updates = 50

        game.clock.tick(game.game_update_rate)

    def terminated(self, solution, frontierF, frontierB):
        return solution is not None or not frontierF or not frontierB
    
    def proceed(self, dir, problem, frontier, reached, reached2, solution):

        node, current_snake = frontier.pop()
        new_snake = current_snake
        new_snake.pop()
        for child in node.expand(problem):
            state = child.state
            if state not in new_snake:
                if state not in reached or child.path_cost < reached[state].path_cost:
                    reached[state] = child
                    frontier.append((child, new_snake + deque([state])))
                    if state in reached2:
                        solution2 = self.join_nodes(dir, child, reached[state])
                        if solution:
                            if solution2.path_cost < solution.path_cost:
                                solution = solution2
                        else:
                            solution = solution2
        return solution

    def join_nodes(self, dir: str, node1: Node, node2: Node):
        if dir == "F":
            forward_node, backward_node = node1, node2
        else:
            forward_node, backward_node = node2, node1

        # Combine the forward path with the reversed backward path
        forward_path = forward_node.path()
        backward_path = backward_node.path()
        combined_path = forward_path[:-1] + list(reversed(backward_path))

        # Create a new node representing the combined path
        start_node = Node(combined_path[0].state)
        current_node = start_node

        for i, next_state in enumerate(combined_path[1:]):
            action = self.get_action(combined_path[i].state, next_state.state)
            next_node = Node(next_state.state, parent=current_node, action=action,
                             path_cost=current_node.path_cost + 1)
            current_node = next_node

        return start_node

    def get_action(self, current_state, next_state):
        dx = next_state[0] - current_state[0]
        dy = next_state[1] - current_state[1]
        if dx == 1:
            return 'RIGHT'
        elif dx == -1:
            return 'LEFT'
        elif dy == 1:
            return 'DOWN'
        elif dy == -1:
            return 'UP'
        else:
            return None  # This should not happen in a valid path

    def exit(self, game: Game):
        game.previous_state = self


def move(head_cell, parent_snake):
    """Add head, remove tail, return child that moved"""
    return list([head_cell] + parent_snake[:-1])

def eat(head_cell, parent_snake):
    """Add head, return child that grew an inch"""
    return list([head_cell] + parent_snake)

def ocupiable_cells(nodes, parent_snake: list):
    """Return nodes that avoids the snake body"""
    return list([node for node in nodes if node.state not in parent_snake])

def ocupiable_cells2(nodes, dir):
    """Return nodes that avoid going in the direction opposing dir"""

    opp_direction_map = {
            'UP': 'DOWN',
            'RIGHT': 'LEFT',
            'DOWN': 'UP',
            'LEFT': 'RIGHT'
        }
    accepteble = list([node for node in nodes if node.action != opp_direction_map[dir]])
    return accepteble
