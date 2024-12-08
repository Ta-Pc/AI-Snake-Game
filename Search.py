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

# This class is responsible for handling all the snake brain processes
import pygame
import numpy as np
from Constants import*
from collections import deque
from collections import defaultdict
from utils import*
import logging

logger = logging.getLogger("Search log")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

class RatProblem:
    
    def __init__(self, init_state: tuple, state_space: dict, goal_state: tuple):
        self.init_pos = init_state
        self.snake_map = state_space
        self.goal_pos = goal_state

    def actions(self, state: tuple):
        """Returns actions possible in a state by looking at adjacent nodes"""
        return self.snake_map.get(state, {}).items()

    def result(self, state: tuple, action: str):
        """Returns the resulting state from applying an action to a state"""
        disp = {
            'UP': (0, -CELL_SIZE),
            'DOWN': (0, CELL_SIZE),
            'LEFT': (-CELL_SIZE, 0),
            'RIGHT': (CELL_SIZE, 0)
        }[action]
        next_state = ((state[0] + disp[0]) % SCREEN_WIDTH, 
                      (state[1] + disp[1]) % SCREEN_HEIGHT)
        return next_state

    def heuristic1(self, state: tuple):
        """Using NumPy for faster computations."""
        state_np = np.array(state)
        goal_np = np.array(self.goal_pos)
        return np.abs(state_np - goal_np).sum()
    
    def heuristic2(self, state: tuple):
        state_np = np.array(state)
        goal_np = np.array(self.goal_pos)
        return np.abs(np.sqrt((state_np[0] - goal_np[0]) ** 2 + (state_np[1] - goal_np[1]) ** 2))

    def is_goal(self, state: tuple):
        """Check if the state is the goal state"""
        return state == self.goal_pos

class SnakeProblem:
    
    def __init__(self, init_state: tuple, goal_state: tuple):
        self.init_pos = init_state
        self.goal_pos = goal_state
        self.direction_map = {
            "UP": (0, -CELL_SIZE),
            "DOWN": (0, CELL_SIZE),
            "LEFT": (-CELL_SIZE, 0),
            "RIGHT": (CELL_SIZE, 0)
        }

    def actions(self, state: tuple):
        """Returns actions possible in a state by looking at possible actions"""
        return self.direction_map.items()

    def result(self, state: tuple, action: str):
        """Returns the resulting state from applying an action to a state"""
        disp = {
            'UP': (0, -CELL_SIZE),
            'DOWN': (0, CELL_SIZE),
            'LEFT': (-CELL_SIZE, 0),
            'RIGHT': (CELL_SIZE, 0)
        }[action]
        next_state = ((state[0] + disp[0]) % SCREEN_WIDTH, 
                      (state[1] + disp[1]) % SCREEN_HEIGHT)
        return next_state

    def heuristic1(self, state: tuple):
        """Using NumPy for faster computations. Returns Manhattan distance from the given state to the goal"""
        state_np = np.array(state)
        goal_np = np.array(self.goal_pos)
        return np.abs(state_np - goal_np).sum()
    
    def heuristic2(self, state: tuple, goal: tuple = None):
        """Pythegorean distance: if 'goal' is not provided, the goal will be the goal_pos"""
        state_np = np.array(state)
        if goal:
            goal_np = np.array(goal)
        else:
            goal_np = np.array(self.goal_pos)
        return np.abs(np.sqrt((state_np[0] - goal_np[0]) ** 2 + (state_np[1] - goal_np[1]) ** 2))

    def is_goal(self, state: tuple):
        """Check if the state is the goal state"""
        return state == self.goal_pos
    
    def path_cost(self, node):
        # A single action has a cost of 1
        return node.path_cost + 1

    def is_goal(self, state: tuple):
        return state == self.goal_pos
    
    def get_next_goal(self):
        return self.next_goal



class Graph:
    """Optimized graph using defaultdict for faster access and allows creation of values with assignment"""
    def __init__(self, graph_dict=None, directed=True):
        self.graph_dict = defaultdict(dict, graph_dict or {})
        self.directed = directed
        if not directed:
            self.make_undirected()

    def make_undirected(self):
        """Make a digraph into an undirected graph by adding symmetric edges."""
        for a in list(self.graph_dict.keys()):
            for (b, dist) in self.graph_dict[a].items():
                self.connect1(b, a, dist)

    def connect(self, A, B, distance=1):
        """Add a link from A and B of given distance, and also add the inverse
        link if the graph is undirected."""
        self.connect1(A, B, distance)
        if not self.directed:
            self.connect1(B, A, distance)

    def connect1(self, A, B, distance):
        """Add a link from A to B of given distance, in one direction only."""
        self.graph_dict[A][B] = distance

    def get(self, a, b=None):
        """Return a link distance or a dict of {node: distance} entries.
        .get(a,b) returns the distance or None;
        .get(a) returns a dict of {node: distance} entries, possibly {}."""
        links = self.graph_dict[a]
        if b is None:
            return links
        else:
            return links.get(b)
        
    def remove_node(self, node):
        """
        Removes a node and all its connections from the graph.

        Args:
            node (tuple): The node to be removed from the graph.

        Behavior:
            - Removes all outgoing edges from the node.
            - Removes all incoming edges to the node.
            - For directed graphs, removes any nodes that become isolated as a result.
        """
        self.clear_connections(node)

    def nodes(self):
        """Return a list of nodes in the graph."""
        return list(self.graph_dict.keys())

    def clear_connections(self, node):
        """Remove all connections to and from the given node."""
        # Remove all outgoing connections
        self.graph_dict.pop(node, None)
        
        # Remove all incoming connections
        for other_node in self.graph_dict:
            self.graph_dict[other_node].pop(node, None)
            
        # If the graph is undirected, we're done.
        # If it's directed, we need to check for any remaining references to the node
        if self.directed:
            for other_node in list(self.graph_dict.keys()):
                if not self.graph_dict[other_node]:
                    del self.graph_dict[other_node]

class Node:
    """A node in a search tree."""

    def __init__(self, state: tuple, parent = None, action: str = None, path_cost: int = 0):
        self.parent = parent
        self.action = action
        self.state = state
        self.path_cost = path_cost
        self.depth = parent.depth + 1 if parent else 0

    def __repr__(self):
        return f"<Node {self.state}> {self.action}"

    def expand(self, problem: SnakeProblem):
        """Expands parent node and creates new children nodes"""
        children = []
        for action, disp in problem.actions(self.state):
            child_state = _next(self.state, disp)
            child_node = Node(state=child_state, parent=self, action=action, path_cost=problem.path_cost(self))
            children.append(child_node)
        return children

    def path(self):
        """Return a list of nodes forming the path from the root to this node."""
        node, path_back = self, []
        while node:
            path_back.append(node)
            node = node.parent
        return list(reversed(path_back))

    def solution(self):
        """Return the sequence of actions that lead to this node."""
        return [node.action for node in self.path()[1:]]  # Exclude the root node's action
    
    def draw_solution(self, window: pygame.Surface, color=BLUE):
        for node in self.path()[1:]:
            node.draw_s(window, color)

    def draw_s(self, window: pygame.Surface, color=BLUE):
        x, y = self.state
        pygame.draw.rect(window, color, (x, y, CELL_SIZE, CELL_SIZE))
    
    def draw(self, offset: tuple, window: pygame.Surface, color=BLUE, radius=CELL_SIZE // 4, font_size=20):
        """Draw the node on the given window at the specified position."""
        x, y = self.state

        pygame.draw.circle(window, color, (x + offset[0], y + offset[1]), radius)

        font = pygame.font.Font(None, font_size)
        text = font.render(f"{self.state}", True, WHITE)
        text_rect = text.get_rect(center=(x + offset[0], y + offset[1]))
        window.blit(text, text_rect)

    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state

    def __hash__(self):
        return hash(self.state)

    def __lt__(self, other):
        """Define less-than for heapq to compare Nodes."""
        return self.path_cost < other.path_cost
    


def best_first_search(problem: SnakeProblem, func, snake):
    """Computes a solution based on the evaluation function

    The order of the solutions matter so pop left"""

    # 3 data structures that will handle the search
    def f(items):
        node, _ = items
        randomness = random.uniform(1 - 0.2, 1 + 0.2)
        return func(node) * randomness
    
    init_snake = list([snake.head.cell] + [sbo.cell for sbo in snake.tail])
    node = Node(problem.init_pos) # The root node
    frontier = PriorityQueue('min', f) # Stores unexpanded nodes
    reached = {node.state : node} # Stores the states of all generated nodes
    frontier.append((node, init_snake))

    while frontier:
        node, parent_snake = frontier.pop() # Realeaseng a node so that it can be expanded
        # Cheacking if a node matches with the goal
        if problem.is_goal(node.state):
            # Returning actions that lead to this solution
            return deque(node.solution())

        for child in ocupiable_cells(node.expand(problem), parent_snake):
            state = child.state
            if state not in reached or child.path_cost < reached[state].path_cost:
                child_snake = move(state, parent_snake)
                reached[state] = child # Once a node is generated the state must be stored
                frontier.append((child, child_snake)) # A child has not been unexpanded so it is a frontier



def depth_first_search(problem: SnakeProblem, snake):
    """Computes a solution by expanding the deppest nodes first
    
    The order of the solutions matter so pop left"""

    init_snake = list([snake.head.cell] + [sbo.cell for sbo in snake.tail])
    node = Node(problem.init_pos)

    if problem.is_goal(node.state):
        return deque(node.solution())
    
    frontier = deque([(node, init_snake)])
    reached = {node.state}
    
    while frontier:
        node, parent_snake = frontier.pop()

        for child in ocupiable_cells(node.expand(problem), parent_snake):
            state = child.state

            if problem.is_goal(state):
                return deque(child.solution())
            
            if state not in reached:
                child_snake = move(state, parent_snake)
                frontier.append((child, child_snake))
                reached.add(state)

def a_star_search_with_bfs(problem: SnakeProblem, func, snake, bfs_depth, rand_fact):
    """"Computes the solution but starts with a breadth frist search and then switches to a star search
    
    The order of the solutions matter so pop left
    """

    breadth_first_func = lambda node: node.depth + (problem.heuristic2(node.state) * 0.05)
    orig_func = func
    func = breadth_first_func

    def f(items):
        node, rev_snake = items
        randomness = random.uniform(1 - rand_fact, 1 + rand_fact)
        return func(node) * randomness
    
    init_snake = list([snake.head.cell] + [sbo.cell for sbo in snake.tail])
    node = Node(problem.init_pos) # The root node
    frontier = PriorityQueue('min', f) # Stores unexpanded nodes
    reached = {node.state : node} # Stores the states of all generated nodes
    frontier.append((node, init_snake))

    while frontier:
        node, parent_snake = frontier.pop() # Realeaseng a node so that it can be expanded
        # After searching and reaching a certain depth revert to a star search
        if node.depth == bfs_depth:
            func = orig_func

        # Cheacking if a node matches with the goal
        if problem.is_goal(node.state):
            # Returning actions that lead to this solution
            return deque(node.solution())

        for child in ocupiable_cells(node.expand(problem), parent_snake):
            state = child.state
            if state not in reached or child.path_cost < reached[state].path_cost:
                child_snake = move(state, parent_snake)
                reached[state] = child # Once a node is generated the state must be stored
                frontier.append((child, child_snake)) # A child has not been unexpanded so it is a frontier

def a_star_search(problem: SnakeProblem, func, snake, rand_fact):
    """"Computes the solution using a heurestic sum with the cost

    The order of the solutions matter so pop left"""
    def f(items):
        node, _ = items
        randomness = random.uniform(1 - rand_fact, 1 + rand_fact)
        return func(node) * randomness
    
    init_snake = list([snake.head.cell] + [sbo.cell for sbo in snake.tail])
    node = Node(problem.init_pos) # The root node
    frontier = PriorityQueue('min', f) # Stores unexpanded nodes
    reached = {node.state : node} # Stores the states of all generated nodes
    frontier.append((node, init_snake))

    while frontier:
        node, parent_snake = frontier.pop() # Realeaseng a node so that it can be expanded

        # Cheacking if a node matches with the goal
        if problem.is_goal(node.state):
            # Returning actions that lead to this solution
            return node.solution()

        for child in ocupiable_cells(node.expand(problem), parent_snake):
            state = child.state
            if state not in reached or child.path_cost < reached[state].path_cost:
                child_snake = move(state, parent_snake)
                reached[state] = child # Once a node is generated the state must be stored
                frontier.append((child, child_snake)) # A child has not been unexpanded so it is a frontier

def bidirectional_best_first_search(self, problemF: SnakeProblem, funcF, problemB: SnakeProblem, funcB, snake):
    # Forward and back

    def fF(items):
        return funcF(items[0])
    
    def fB(items):
        return funcB(items[0])
    
    snake_reversed = list(reversed(snake.tail))
    snake_positions = deque([segment.cell for segment in snake_reversed] + [snake.head.cell])
    nodeF = Node(problemF.init_pos)
    nodeB = Node(problemB.init_pos)
    frontierF = PriorityQueue('min', fF)
    frontierB = PriorityQueue('min', fB)
    frontierF.append((nodeF, snake_positions))
    frontierB.append((nodeB, snake_positions))
    reachedF = {nodeF.state: nodeF}
    reachedB = {nodeB.state: nodeB}
    solution = None

    while not terminated(solution, frontierF, frontierB):
        if fF(frontierF[0]) < fB(frontierB[0]):
            solution = proceed("F", problemF, frontierF, reachedF, reachedB, solution)
        else:
            solution = proceed("B", problemB, frontierB, reachedB, reachedF, solution)

    return solution

    
def terminated(solution, frontierF, frontierB):
    return solution in frontierF and solution in frontierB

def proceed(dir, problem, frontier, reached, reached2, solution):

    node, current_snake = frontier.pop()
    new_snake = list(current_snake)
    for child in node.expand(problem):
        state = child.state
        if state not in new_snake:
            if state not in reached or child.path_cost < reached[state].path_cost:
                reached[state] = child
                frontier.append((child, new_snake[1:] + list([state])))
                if state in reached2:
                    solution2 = join_nodes(dir, child, reached2[state])
                    if solution2.path_cost < solution.path_cost:
                        solution = solution2
    return solution

def join_nodes(dir, node1: Node, node2):
    if dir == "F":
        reversed_sol2 = reversed(node2.path())
        node = node1
        for node2 in reversed_sol2:
            node2.parent = node
            node = node2
    else:
        reversed_sol1 = reversed(node1.path())
        node = node2
        for node1 in reversed_sol1:
            node1.parent = node
            node = node1
    return node



def greedy_search(problem: SnakeProblem, f, snake):
    return best_first_search(problem, f, snake)

def uniform_cost_search(problem: SnakeProblem, snake):
    return best_first_search(problem, problem.path_cost, snake)

def generate_environment_graph_for_snake(snake, f):
    graph = Graph(directed=True)
    visited = set()
    snake_reverse = list(reversed(snake.tail))
    snake_positions = deque([segment.cell for segment in snake_reverse] + [snake.head.cell]) # sorted in reverse last tail segmnt to head
    queue = PriorityQueue('min', lambda items: items[0])  # (cell, parent_action, snake_positions)
    queue.append([(snake.head.cell, snake_positions)])
    
    #logging.debug(f"Starting graph generation from head position: {self.snake.head.cell}")
    #logging.debug(f"Initial snake positions: {snake_positions}")

    while queue:
        current_cell, current_snake = queue.popleft()
        #logging.debug(f"Processing cell: {current_cell}")
        
        if current_cell in visited:
            #logging.debug(f"Cell {current_cell} already visited, skipping")
            continue
        visited.add(current_cell)
        # Simulate snake movement
        new_snake = deque(current_snake)
        new_snake.popleft()  # Remove last tail segment first

        for action, disp in snake.direction_map.items():
            next_cell = _next(current_cell, disp)
            #logging.debug(f"Considering next cell: {next_cell} with action {action}")
            
            # Check if next_cell is valid (not occupied by new snake body)
            if next_cell not in set(new_snake):
                #logging.debug(f"Adding edge: {current_cell} -> {next_cell} with action {action}")
                graph.connect(current_cell, next_cell, action)
                #new_snake.append()  # Add new head position
                queue.append((next_cell, new_snake + deque([next_cell])))
            else:
                continue
                #logging.debug(f"Cell {next_cell} is occupied by snake, skipping")
    
    #logging.debug(f"Graph generation complete. Nodes: {len(graph.graph_dict)}, Edges: {sum(len(edges) for edges in graph.graph_dict.values())}")
    return graph

def _next(cell, disp):
    return ((cell[0] + disp[0]) % SCREEN_WIDTH,
            (cell[1] + disp[1]) % SCREEN_HEIGHT)


def generate_environment_graph_for_rat(rat):
    graph = Graph(directed=True)
    frontier = deque([rat.head.cell]) 
    reached = set(rat.head.cell)

    while frontier:
        cell = frontier.popleft()
        
        if cell in reached:
            continue

        reached.add(cell)
        
        for action, disp in rat.direction_map.items():
            next_cell = _next(cell, disp)  
            graph.connect(cell, next_cell, action)
            frontier.append(next_cell)

    return graph

# ______________________________________________________________________________
# Utility functions

def move(head_cell, parent_snake):
    """Add head, remove tail, return child that moved"""
    return list([head_cell] + parent_snake[:-1])

def eat(head_cell, parent_snake):
    """Add head, return child that grew an inch"""
    return list([head_cell] + parent_snake)

def ocupiable_cells(nodes, parent_snake: list):
    """Return nodes that avoids the snake body"""
    return [node for node in nodes if node.state not in parent_snake]

def count_actions(solution):
    up = 0
    down = 0
    left = 0
    right = 0
    for action in solution:
        if action == "UP":
            up += 1
        elif action == "DOWN":
            down += 1
        elif action == "LEFT":
            left += 1
        elif action == "RIGHT":
            right += 1
    return up, down, left, right

def altenative_goal(current_head_pos, true_goal, snake_body_set):
    """Returns an alternative problem, moving the snake to a random position whilst keeping the true goal in mind
    to cheack if the alternative goal allows it to get to the true goal once it is able to  the snake will go to the alternative goal
    or else will search for another alternative goal"""
    problem = SnakeProblem(current_head_pos, (0, 0))
    available_accessible_positions = [
            (x, y)
            for x in range(0, SCREEN_WIDTH, CELL_SIZE)
            for y in range(0, SCREEN_HEIGHT, CELL_SIZE)
            if best_first_search_verify(problem, lambda node: node.path_cost + problem.heuristic1(node.state), snake_body_set)
        ] # Use this to compute if 80% of the map is accessible to the snake
    x, y = random.choice(available_accessible_positions) if available_accessible_positions else (0, 0)
    
    alt_goal = (x, y)
    return SnakeProblem(current_head_pos, alt_goal)

def best_first_search_verify(problem: SnakeProblem, func, snake_position: list):
    """
    Checks if the previously found solution allows the snake to find the next solution.
    Returns true if snake can move to next goal, false when it cannot
    Complex but necessary

    The order of the solutions matter so pop left
    """

    # 3 data structures that will handle the search
    def f(items):
        node, _ = items
        randomness = random.uniform(1 - 0.2, 1 + 0.2)
        return func(node) * randomness
    
    node = Node(problem.init_pos) # The root node
    frontier = PriorityQueue('min', f) # Stores unexpanded nodes
    reached = {node.state : node} # Stores the states of all generated nodes
    init_snake_position = list(snake_position)
    frontier.append((node, init_snake_position))

    while frontier:
        node, parent_snake = frontier.pop() # Realeaseng a node so that it can be expanded
        # Cheacking if a node matches with the goal
        if problem.is_goal(node.state):
            return True # The previous solution allows the snake to find the next solution

        for child in ocupiable_cells(node.expand(problem), parent_snake):
            state = child.state
            if state not in reached or child.path_cost < reached[state].path_cost:
                child_snake = move(state, parent_snake)
                reached[state] = child # Once a node is generated the state must be stored
                frontier.append((child, child_snake)) # A child has not been unexpanded so it is a frontier
    return False # The previous solution deny's the snake from finding the next solution
    
