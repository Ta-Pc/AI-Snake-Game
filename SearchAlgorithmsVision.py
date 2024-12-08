from Game import Game
from GameState import *
from Constants import *
from Snake import *
from Search import *

class GraphCreationVisionDFS(GameState):
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        snake_reverse = list(reversed(self.snake.tail))
        snake_positions = deque([segment.cell for segment in snake_reverse] + [self.snake.head.cell])
        self.offset = (CELL_SIZE // 2, CELL_SIZE // 2)
        self.node_size = self.offset[0] - 5
        self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
        self.solution = deque()
        self.node = Node(self.problem.init_pos)
        if  self.problem.is_goal(self.node.state):
            self.solution = deque(self.node.solution())
            self.updates = 0
        else:
            self.frontier = deque([(self.node, snake_positions)])
            self.reached = {self.node.state : self.node} #I must be able to see the nodes that have been reached
        self.updates = 60

    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed('ESCAPE'):
            from GameUI import AIVisionSelectState
            game.change_state(AIVisionSelectState())
        elif game.controls.is_just_pressed('SPACE'):
            from GameUI import PauseState
            game.change_state(PauseState())

    def next_step(self):
        # Implement your graph expansion logic here
        # Update self.graph, self.frontier, self.reached, and self.current_node
        self.step_count += 1

    def draw(self, game: Game):
        time = pygame.time.get_ticks() / 1000
        game.window.fill(BLACK)  # White background
        #self.draw_map(game.window)
        self.draw_grid(game.window)
        self.draw_edges(game.window)
        self.draw_step_count(game.window)
        self.draw_nodes(game.window)
        
        if self.food.active:
            self.food.draw(game.window)
        if self.snake.active:
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

            for item in self.frontier:
                item[0].draw(self.offset, window, RED, self.node_size, 15)


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
        # Simulating a star algorithm
        for _ in range(self.updates):
            if self.frontier and not self.solution:
                self.node, current_snake = self.frontier.pop()
                new_snake = list(current_snake)
                for child in self.node.expand(self.problem):
                    state = child.state
                    if  self.problem.is_goal(state):
                        self.solution = deque(child.solution())
                        self.updates = 0
                    else:
                        if state not in new_snake:
                            if state not in self.reached or child.path_cost < self.reached[state].path_cost:
                                self.reached[state] = child
                                self.frontier.append((child, new_snake[1:] + list([state])))

        if self.solution:
            action = self.solution.popleft()
            self.snake.set_direction(action)
            self.snake.move()

        if self.snake.is_eating_food(self.food):
            self.food.replace(self.snake)
            self.snake.grow(3)
            snake_reverse = list(reversed(self.snake.tail))
            snake_positions = deque([segment.cell for segment in snake_reverse] + [self.snake.head.cell])
            self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
            self.node = Node(self.problem.init_pos)
            if  self.problem.is_goal(self.node.state):
                self.solution = deque(self.node.solution())
                self.updates = 0
            else:
                self.frontier = deque([(self.node, snake_positions)])
                self.reached = {self.node.state : self.node}
            self.updates = 60

        game.clock.tick(game.game_update_rate)

    def exit(self, game: Game):
        pass


class GraphCreationVisionBFS(GameState):
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.snake.active = True
        self.food.active = True
        def f(items):
            node, _ = items
            return node.path_cost
        self.f = f
        snake_reverse = list(reversed(self.snake.tail))
        snake_positions = deque([segment.cell for segment in snake_reverse] + [self.snake.head.cell])
        self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
        self.node = Node(self.problem.init_pos)
        self.frontier = PriorityQueue('min', self.f)
        self.frontier.append((self.node, snake_positions))
        self.reached = {self.node.state : self.node}
        self.offset = (CELL_SIZE // 2, CELL_SIZE // 2)
        self.node_size = self.offset[0] - 5
        self.solution = deque()
        self.updates = 60

    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed('ESCAPE'):
            from GameUI import AIVisionSelectState
            game.change_state(AIVisionSelectState())
        elif game.controls.is_just_pressed('SPACE'):
            from GameUI import PauseState
            game.change_state(PauseState())

    def next_step(self):
        # Implement your graph expansion logic here
        # Update self.graph, self.frontier, self.reached, and self.current_node
        self.step_count += 1

    def draw(self, game: Game):
        time = pygame.time.get_ticks() / 1000
        game.window.fill(BLACK)  # White background
        #self.draw_map(game.window)
        self.draw_grid(game.window)
        self.draw_edges(game.window)
        self.draw_step_count(game.window)
        self.draw_nodes(game.window)
        
        if self.food.active:
            self.food.draw(game.window)
        if self.snake.active:
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
        # Simulating a star algorithm
        for _ in range(self.updates):
            if self.frontier and not self.solution:
                self.node, current_snake = self.frontier.pop()

                if  self.problem.is_goal(self.node.state):
                    self.food.active = True
                    self.snake.active = True
                    self.solution = deque(self.node.solution())
                    self.updates = 0
                else:
                    new_snake = list(current_snake)
                    for child in self.node.expand(self.problem):
                        state = child.state
                        if state not in new_snake:
                            if state not in self.reached or child.path_cost < self.reached[state].path_cost:
                                self.reached[state] = child
                                self.frontier.append((child, new_snake[1:] + list([state])))

        if self.solution:
            action = self.solution.popleft()
            self.snake.set_direction(action)
            self.snake.move()

        if self.snake.is_eating_food(self.food):
            self.food.replace(self.snake)
            self.snake.grow(3)
            #self.graph = generate_environment_graph_for_snake(self.snake) # Your graph structure
            self.graph = Graph()
            snake_reverse = list(reversed(self.snake.tail))
            snake_positions = deque([segment.cell for segment in snake_reverse] + [self.snake.head.cell])
            self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
            self.node = Node(self.problem.init_pos)
            self.frontier = PriorityQueue('min', self.f)
            self.frontier.append((self.node, snake_positions))
            self.reached = {self.node.state : self.node}
            self.updates = 60

        game.clock.tick(game.game_update_rate)

    def exit(self, game: Game):
        pass


class GraphCreationVisionAStarSearch(GameState):
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.snake.active = True
        self.food.active = True
        # There are some huge limitations with this algoritm in the snake game context and thus needs improvement
        # Maybe ch 4 Search in complex enviroments will help with such a situation
        self.bfs_func = lambda node: node.depth + (self.problem.heuristic2(node.state) * 0.05) + (self.problem.heuristic2(node.state, (SCREEN_WIDTH - (CELL_SIZE * 4), SCREEN_CENTER[1]))
                                                    + self.problem.heuristic2(node.state, ((CELL_SIZE * 4), SCREEN_CENTER[1]))
                                                    + self.problem.heuristic2(node.state, (SCREEN_CENTER[0], SCREEN_HEIGHT - (CELL_SIZE * 4)))
                                                    + self.problem.heuristic2(node.state, (SCREEN_CENTER[0], (CELL_SIZE * 4)))) * 0.2
        self.a_star_func = lambda node: node.depth + (self.problem.heuristic2(node.state))
        self.func = self.bfs_func
        self.rand_factor = 0
        self.dfs_depth = 3

        def f(items):
            node, rev_snake = items
            randomness = random.uniform(1 - self.rand_factor, 1 + self.rand_factor)
            return self.func(node) * randomness
        
        
        self.f = f
        #self.f = memoize(f, 'f')
        snake_reverse = list(reversed(self.snake.tail))
        snake_positions = deque([segment.cell for segment in snake_reverse] + [self.snake.head.cell])
        self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
        self.node = Node(self.problem.init_pos)
        self.frontier = PriorityQueue('min', self.f)
        self.frontier.append((self.node, snake_positions))
        self.reached = {self.node.state : self.node}
        self.offset = (CELL_SIZE // 2, CELL_SIZE // 2)
        self.node_size = self.offset[0] - 5
        self.solution = deque()
        self.updates = 5

    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed('ESCAPE'):
            from GameUI import AIVisionSelectState
            game.change_state(AIVisionSelectState())
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
        self.draw_edges(game.window)
        self.draw_step_count(game.window)
        self.draw_nodes(game.window)
        
        if self.food.active:
            self.food.draw(game.window)
        if self.snake.active:
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
        # Simulating a star algorithm
        for _ in range(self.updates):
            if self.frontier and not self.solution:
                self.node, current_snake = self.frontier.pop()

                if self.node.depth == self.dfs_depth:
                    self.func = self.a_star_func

                if  self.problem.is_goal(self.node.state):
                    self.food.active = True
                    self.snake.active = True
                    self.solution = deque(self.node.solution())
                    self.updates = 0
                else:
                    new_snake = list(current_snake)
                    for child in self.node.expand(self.problem):
                        state = child.state
                        if state not in new_snake:
                            if state not in self.reached or child.path_cost < self.reached[state].path_cost:
                                self.reached[state] = child
                                self.frontier.append((child, new_snake[1:] + list([state])))

        if self.solution:
            action = self.solution.popleft()
            self.snake.set_direction(action)
            self.snake.move()

        if self.snake.is_eating_food(self.food):
            self.food.replace(self.snake)
            self.snake.grow(3)
            #self.graph = generate_environment_graph_for_snake(self.snake) # Your graph structure
            self.graph = Graph()
            snake_reverse = list(reversed(self.snake.tail))
            snake_positions = deque([segment.cell for segment in snake_reverse] + [self.snake.head.cell])
            self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
            self.node = Node(self.problem.init_pos)
            self.frontier = PriorityQueue('min', self.f)
            self.frontier.append((self.node, snake_positions))
            self.reached = {self.node.state : self.node}
            self.updates = 15
            self.func = self.bfs_func
            if self.rand_factor < 0.2 : self.rand_factor += 0.002
            if self.dfs_depth < 25: self.dfs_depth += 1


        game.clock.tick(game.game_update_rate)

    def exit(self, game: Game):
        pass



class GraphCreationVisionGreedySearch(GameState):
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.snake.active = True
        self.food.active = True
        #self.graph = generate_environment_graph_for_snake(self.snake) # Your graph structure
        def f(items):
            node, _ = items
            return self.problem.heuristic1(node.state)
        
        #self.f = memoize(f, 'f')
        self.f = f
        snake_reverse = list(reversed(self.snake.tail))
        snake_positions = deque([segment.cell for segment in snake_reverse] + [self.snake.head.cell])
        self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
        self.node = Node(self.problem.init_pos)
        self.frontier = PriorityQueue('min', self.f)
        self.frontier.append((self.node, snake_positions))
        self.reached = {self.node.state : self.node}
        self.offset = (CELL_SIZE // 2, CELL_SIZE // 2)
        self.node_size = self.offset[0] - 5
        self.solution = deque()
        self.updates = 1

    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed('ESCAPE'):
            from GameUI import AIVisionSelectState
            game.change_state(AIVisionSelectState())
        elif game.controls.is_just_pressed('SPACE'):
            from GameUI import PauseState
            game.change_state(PauseState())

    def next_step(self):
        # Implement your graph expansion logic here
        # Update self.graph, self.frontier, self.reached, and self.current_node
        self.step_count += 1

    def draw(self, game: Game):
        time = pygame.time.get_ticks() / 1000
        game.window.fill(BLACK)  # White background
        #self.draw_map(game.window)
        self.draw_grid(game.window)
        self.draw_edges(game.window)
        self.draw_step_count(game.window)
        self.draw_nodes(game.window)
        
        if self.food.active:
            self.food.draw(game.window)
        if self.snake.active:
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
        # Simulating a star algorithm
        for _ in range(self.updates):
            if self.frontier and not self.solution:
                self.node, current_snake = self.frontier.pop()

                if  self.problem.is_goal(self.node.state):
                    self.food.active = True
                    self.snake.active = True
                    self.solution = deque(self.node.solution())
                    self.updates = 0
                else:
                    new_snake = list(current_snake)
                    for child in self.node.expand(self.problem):
                        state = child.state
                        if state not in new_snake:
                            if state not in self.reached or child.path_cost < self.reached[state].path_cost:
                                self.reached[state] = self.node
                                self.frontier.append((child, new_snake[1:] + list([state])))

        if self.solution:
            action = self.solution.popleft()
            self.snake.set_direction(action)
            self.snake.move()

        if self.snake.is_eating_food(self.food):
            self.food.replace(self.snake)
            self.snake.grow(3)
            #self.graph = generate_environment_graph_for_snake(self.snake) # Your graph structure
            self.graph = Graph()
            snake_reverse = list(reversed(self.snake.tail))
            snake_positions = deque([segment.cell for segment in snake_reverse] + [self.snake.head.cell])
            self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
            self.node = Node(self.problem.init_pos)
            self.frontier = PriorityQueue('min', self.f)
            self.frontier.append((self.node, snake_positions))
            self.reached = {self.node.state : self.node}
            self.updates = 1

        game.clock.tick(game.game_update_rate)

    def exit(self, game: Game):
        pass

class GraphCreationVisionAStarSearchUpdated(GameState):
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.snake.active = True
        self.food.active = True
        
        # Modified heuristic weights
        self.distance_weight = 1.0
        self.space_weight = 2.0
        self.min_space_threshold = 0.8  # 80% minimum accessible space
        
        # Improved heuristic functions
        self.bfs_func = lambda node: node.depth + (self.calculate_combined_heuristic(node.state) * 0.05)
        self.a_star_func = lambda node: node.depth + self.calculate_combined_heuristic(node.state)
        self.func = self.bfs_func
        self.rand_factor = 0
        self.dfs_depth = 3

        self.grid_height = GRID_HEIGHT
        self.grid_width = GRID_WIDTH

        def f(items):
            node, rev_snake = items
            randomness = random.uniform(1 - self.rand_factor, 1 + self.rand_factor)
            # Only apply randomness if the space is safe
            if self.is_safe_move(node.state, rev_snake):
                return self.func(node) * randomness
            return float('inf')  # Discourage unsafe moves
        
        self.f = f
        snake_reverse = list(reversed(self.snake.tail))
        snake_positions = deque([segment.cell for segment in snake_reverse] + [self.snake.head.cell])
        self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
        self.node = Node(self.problem.init_pos)
        self.frontier = PriorityQueue('min', self.f)
        self.frontier.append((self.node, snake_positions))
        self.reached = {self.node.state: self.node}
        self.offset = (CELL_SIZE // 2, CELL_SIZE // 2)
        self.node_size = self.offset[0] - 5
        self.solution = deque()
        self.updates = 5
        
        # Calculate grid dimensions for flood fill
        self.grid_width = SCREEN_WIDTH // CELL_SIZE
        self.grid_height = SCREEN_HEIGHT // CELL_SIZE

    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed('ESCAPE'):
            from GameUI import AIPlaySelectState
            game.change_state(AIPlaySelectState())
        elif game.controls.is_just_pressed('SPACE'):
            from GameUI import PauseState
            game.change_state(PauseState())


    def calculate_combined_heuristic(self, state):
        """Combines distance to food with accessibility heuristic"""
        manhattan_distance = self.manhattan_distance(state, self.food.cell)
        space_score = self.calculate_space_score(state)
        
        # Combine the heuristics with their weights
        return (self.distance_weight * manhattan_distance + 
                self.space_weight * (1.0 - space_score))

    def manhattan_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def calculate_space_score(self, position):
        """Calculate the percentage of accessible space using flood fill"""
        grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Mark snake body
        for segment in self.snake.tail:
            x, y = segment.cell[0] // CELL_SIZE, segment.cell[1] // CELL_SIZE
            grid[y][x] = 1
            
        # Perform flood fill from the given position
        accessible_cells = self.flood_fill(grid, 
                                         position[0] // CELL_SIZE,
                                         position[1] // CELL_SIZE)
        
        # Calculate percentage of accessible space
        total_cells = self.grid_width * self.grid_height - len(self.snake.tail)
        return accessible_cells / total_cells

    def flood_fill(self, grid, x, y):
        """Perform flood fill to count accessible cells"""
        if (not (0 <= x < self.grid_width and 0 <= y < self.grid_height) or
            grid[y][x] == 1):
            return 0
            
        grid[y][x] = 1  # Mark as visited
        count = 1  # Count current cell
        
        # Check all four directions
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        for dx, dy in directions:
            count += self.flood_fill(grid, x + dx, y + dy)
            
        return count

    def is_safe_move(self, new_pos, snake_positions):
        """Check if the move maintains sufficient accessible space"""
        # Create a temporary new snake position list
        new_snake = deque(list(snake_positions)[1:] + [new_pos])
        
        # Calculate accessible space from the new position
        space_score = self.calculate_space_score(new_pos)
        
        # Check if the move maintains minimum required accessible space
        return space_score >= self.min_space_threshold

    def update(self, game: Game):
        for _ in range(self.updates):
            if self.frontier and not self.solution:
                self.node, current_snake = self.frontier.pop()

                if self.node.depth == self.dfs_depth:
                    self.func = self.a_star_func

                if self.problem.is_goal(self.node.state):
                    self.food.active = True
                    self.snake.active = True
                    self.solution = deque(self.node.solution())
                    self.updates = 0
                else:
                    new_snake = list(current_snake)
                    for child in self.node.expand(self.problem):
                        state = child.state
                        if state not in new_snake:
                            # Only add moves that maintain sufficient accessible space
                            if self.is_safe_move(state, new_snake):
                                if (state not in self.reached or 
                                    child.path_cost < self.reached[state].path_cost):
                                    self.reached[state] = child
                                    self.frontier.append((child, new_snake[1:] + list([state])))

        if self.solution:
            action = self.solution.popleft()
            self.snake.set_direction(action)
            self.snake.move()

        if self.snake.is_eating_food(self.food):
            self.food.replace(self.snake)
            self.snake.grow(3)
            self.graph = Graph()
            snake_reverse = list(reversed(self.snake.tail))
            snake_positions = deque([segment.cell for segment in snake_reverse] + 
                                  [self.snake.head.cell])
            self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
            self.node = Node(self.problem.init_pos)
            self.frontier = PriorityQueue('min', self.f)
            self.frontier.append((self.node, snake_positions))
            self.reached = {self.node.state: self.node}
            self.updates = 15
            self.func = self.bfs_func
            
            # Gradually increase randomness and search depth as snake grows
            if self.rand_factor < 0.2:
                self.rand_factor += 0.002
            if self.dfs_depth < 25:
                self.dfs_depth += 1

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

class GraphVisionOnlineSearchState(GameState):
    def enter(self, game: Game):
        # Initialize game objects
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.snake.active = True
        self.food.active = True
        
        # Online learning parameters
        self.exploration_rate = 0.2
        self.learning_rate = 0.1
        self.danger_memory = {}
        self.success_memory = {}
        self.current_path = []
        self.consecutive_successes = 0
        
        # Visualization parameters
        self.offset = (CELL_SIZE // 2, CELL_SIZE // 2)
        self.node_size = self.offset[0] - 5
        self.solution = deque()
        self.updates = 5
        
        # Search parameters
        snake_reverse = list(reversed(self.snake.tail))
        snake_positions = deque([segment.cell for segment in snake_reverse] + [self.snake.head.cell])
        self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
        self.node = Node(self.problem.init_pos)
        
        # Initialize frontier and reached sets
        def custom_heuristic(node):
            path_key = self.get_path_key(self.snake.direction, node.state)
            danger_penalty = 100 if path_key in self.danger_memory else 0
            return (
                self.problem.heuristic2(node.state) + 
                danger_penalty +
                len(self.snake.tail) * 0.1
            )
        
        self.f = lambda items: items[0].depth + custom_heuristic(items[0])
        self.frontier = PriorityQueue('min', self.f)
        self.frontier.append((self.node, snake_positions))
        self.reached = {self.node.state: self.node}

    def get_path_key(self, initial_action, target_pos):
        """Generate a unique key for a path based on initial action and target"""
        return f"{initial_action}_{target_pos[0]}_{target_pos[1]}"

    def update_danger_memory(self, position):
        """Update knowledge about dangerous positions"""
        wall_danger = (
            position[0] <= CELL_SIZE or
            position[0] >= SCREEN_WIDTH - CELL_SIZE or
            position[1] <= CELL_SIZE or
            position[1] >= SCREEN_HEIGHT - CELL_SIZE
        )
        
        body_danger = any(
            abs(position[0] - segment.cell[0]) <= CELL_SIZE and
            abs(position[1] - segment.cell[1]) <= CELL_SIZE
            for segment in self.snake.tail
        )
        
        if wall_danger or body_danger:
            path_key = self.get_path_key(
                self.current_path[0] if self.current_path else "NONE",
                position
            )
            self.danger_memory[path_key] = True

    def handle_food_eaten(self, game):
        """Handle successful food consumption and update learning parameters"""
        self.consecutive_successes += 1
        
        # Store successful path
        path_key = self.get_path_key(self.current_path[0], self.food.cell)
        self.success_memory[path_key] = self.current_path.copy()
        
        # Adjust learning parameters
        self.exploration_rate = max(0.05, self.exploration_rate * 0.95)
        self.learning_rate = max(0.05, self.learning_rate * 0.98)
        
        # Update game state
        self.snake.grow(1)
        self.food.replace(self.snake)
        game.game_hud.increase_score(self.food.score_incriment)
        
        # Reset search state
        snake_reverse = list(reversed(self.snake.tail))
        snake_positions = deque([segment.cell for segment in snake_reverse] + [self.snake.head.cell])
        self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
        self.node = Node(self.problem.init_pos)
        self.frontier = PriorityQueue('min', self.f)
        self.frontier.append((self.node, snake_positions))
        self.reached = {self.node.state: self.node}
        self.solution = deque()
        self.current_path = []
        self.updates = 15

    def update(self, game: Game):
        # Search update
        for _ in range(self.updates):
            if self.frontier and not self.solution:
                self.node, current_snake = self.frontier.pop()
                
                if self.problem.is_goal(self.node.state):
                    self.food.active = True
                    self.snake.active = True
                    self.solution = deque(self.node.solution())
                    self.updates = 0
                else:
                    new_snake = list(current_snake)
                    for child in self.node.expand(self.problem):
                        state = child.state
                        if state not in new_snake:
                            if state not in self.reached or child.path_cost < self.reached[state].path_cost:
                                self.reached[state] = child
                                self.frontier.append((child, new_snake[1:] + list([state])))

        # Movement update
        if self.solution:
            action = self.solution.popleft()
            self.snake.set_direction(action)
            self.current_path.append(action)
            self.snake.move()
            
            current_head = self.snake.head.cell
            self.update_danger_memory(current_head)

            if self.snake.is_eating_food(self.food):
                self.handle_food_eaten(game)
            
            if self.snake.is_eating_self():
                game.game_hud.update_high_score()
                from GameUI import GameOverState
                game.change_state(GameOverState())

        game.clock.tick(game.game_update_rate)

    def draw(self, game: Game):
        time = pygame.time.get_ticks() / 1000
        game.window.fill(BLACK)
        
        # Draw grid
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(game.window, WHITE, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
            pygame.draw.line(game.window, WHITE, (0, y), (SCREEN_WIDTH, y))
        
        # Draw nodes
        if self.solution:
            self.node.draw_solution(game.window, LIGHT_GRAY)
        else:
            if self.reached:
                for _, node in self.reached.items():
                    node.draw(self.offset, game.window, BLUE, self.node_size, 5)

            for item in self.frontier.heap:
                item[1][0].draw(self.offset, game.window, RED, self.node_size, 15)
        
        # Draw game objects
        if self.food.active:
            self.food.draw(game.window)
        if self.snake.active:
            self.snake.draw(game.window, time)
        
        # Draw UI elements
        game.draw_message()
        game.game_hud.draw_score()
        pygame.draw.rect(game.window, BRIGHT_AQUA, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 3)

    def handle_events(self, game: Game, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                self._handle_actions(game)

    def _handle_actions(self, game: Game):
        if game.controls.is_just_pressed('ESCAPE'):
            from GameUI import AIVisionSelectState
            game.change_state(AIVisionSelectState())
        elif game.controls.is_just_pressed('SPACE'):
            from GameUI import PauseState
            game.change_state(PauseState())

    def exit(self, game: Game):
        game.previous_state = self