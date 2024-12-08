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

from Game import Game
from GameState import *
from Constants import *
from Snake import *
from Search import *

#*************************************************************************************************************************
# Computer Playing Snake
#*************************************************************************************************************************


class AIPlayerOnlineState(GameState):
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.big_food = BigFood(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT), 2)
        
        # Online learning parameters
        self.exploration_rate = 0.2  # Chance to explore new paths
        self.learning_rate = 0.1     # Rate at which we update our knowledge
        self.danger_memory = {}      # Remember dangerous positions
        self.success_memory = {}     # Remember successful paths
        self.current_path = []       # Track current path being taken
        self.consecutive_successes = 0
        
        self.find_path_to_food(self.food)
        self.eat_count = 0
        game.game_hud.score = 0
        game.display_message("Computer is playing with Online Learning", duration=4000)

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

    def update(self, game: Game):
        if not self.actions:
            # If we run out of actions, recalculate path
            self.find_path_to_food(self.food if not self.big_food.active else self.big_food)
        
        if self.actions:
            action = self.actions.pop(0)
            self.snake.set_direction(action)
            self.current_path.append(action)

        self.snake.move()
        current_head = self.snake.head.cell
        
        # Check if current position is dangerous (near walls or snake body)
        self.update_danger_memory(current_head)

        self.big_food.update()
        if self.snake.is_eating_food(self.food):
            self.handle_food_eaten(game, regular_food=True)
                
        elif self.snake.is_eating_food(self.big_food):
            self.handle_food_eaten(game, regular_food=False)

        if self.snake.is_eating_self():
            self.handle_collision(game)

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

    def handle_food_eaten(self, game, regular_food=True):
        """Handle successful food consumption and update learning parameters"""
        self.consecutive_successes += 1
        
        # Store successful path
        path_key = self.get_path_key(
            self.current_path[0], 
            self.food.cell if regular_food else self.big_food.cell
        )
        self.success_memory[path_key] = self.current_path.copy()
        
        # Adjust learning parameters based on success
        self.exploration_rate = max(0.05, self.exploration_rate * 0.95)
        self.learning_rate = max(0.05, self.learning_rate * 0.98)
        
        # Regular game logic
        if regular_food:
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
        else:
            game.game_hud.increase_score(self.big_food.score_incriment)
            self.snake.grow(size=5)
            self.big_food.is_active(False)
            self.find_path_to_food(self.food)
        
        self.current_path = []

    def handle_collision(self, game):
        """Handle collision events and update learning parameters"""
        # Mark the path that led to collision as dangerous
        if self.current_path:
            path_key = self.get_path_key(
                self.current_path[0],
                self.snake.head.cell
            )
            self.danger_memory[path_key] = True
        
        # Reset learning parameters on collision
        self.exploration_rate = min(0.3, self.exploration_rate * 1.5)
        self.learning_rate = min(0.2, self.learning_rate * 1.5)
        self.consecutive_successes = 0
        
        game.game_hud.update_high_score()
        from GameUI import GameOverState
        game.change_state(GameOverState())

    def update_danger_memory(self, position):
        """Update knowledge about dangerous positions"""
        # Check proximity to walls
        wall_danger = (
            position[0] <= CELL_SIZE or
            position[0] >= SCREEN_WIDTH - CELL_SIZE or
            position[1] <= CELL_SIZE or
            position[1] >= SCREEN_HEIGHT - CELL_SIZE
        )
        
        # Check proximity to snake body
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

    def get_path_key(self, initial_action, target_pos):
        """Generate a unique key for a path based on initial action and target"""
        return f"{initial_action}_{target_pos[0]}_{target_pos[1]}"

    def find_path_to_food(self, food):
        """Find path to food using online learning and exploration"""
        self.problem = SnakeProblem(self.snake.head.cell, food.cell)
        
        # Check if we have a successful path for this scenario
        path_key = self.get_path_key(
            self.snake.direction,
            food.cell
        )
        
        if random.random() > self.exploration_rate and path_key in self.success_memory:
            # Use previously successful path
            self.actions = self.success_memory[path_key].copy()
        else:
            # Use A* search with modified heuristic based on danger memory
            def custom_heuristic(node):
                path_key = self.get_path_key(
                    self.snake.direction,
                    node.state
                )
                danger_penalty = 100 if path_key in self.danger_memory else 0
                return (
                    self.problem.heuristic2(node.state) + 
                    danger_penalty +
                    len(self.snake.tail) * 0.1  # Increase caution with length
                )
            
            self.f = lambda node: node.depth + custom_heuristic(node)
            self.actions = a_star_search_with_bfs(
                self.problem,
                self.f,
                self.snake,
                25,
                self.exploration_rate,
            )
        
        self.current_path = []


class AIPlayerBFSState(GameState):
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.big_food = BigFood(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT), 2)
        self.f = lambda node: node.depth
        self.find_path_to_food(self.food)
        self.eat_count = 0
        game.game_hud.score = 0
        things = [self.big_food, self.food]
        agents = [self.snake]
        self.env = SnakeEnvironment(things, agents)
        game.display_message("Computer is playing, it implements BFSearch", duration=4000)
    

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
    
    def update(self, game: Game):
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
        self.problem = SnakeProblem(self.snake.head.cell, food)
        self.actions = uniform_cost_search(self.problem, self.snake)

class AIPlayerDFSState(GameState):
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.big_food = BigFood(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT), 2)
        self.find_path_to_food(self.food)
        self.eat_count = 0
        game.game_hud.score = 0
        game.display_message("Computer is playing, it implements DFSearch", duration=4000)
    

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
    
    def update(self, game: Game):
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
        self.problem = SnakeProblem(self.snake.head.cell, food.cell)
        self.actions = depth_first_search(self.problem, self.snake)

class AIPlayerAStarSearchState(GameState):
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.big_food = BigFood(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT), 2)
        self.rand_fact = 0
        self.dfs_depth = 3
        self.find_path_to_food(self.food)
        self.eat_count = 0
        game.game_hud.score = 0
        game.display_message("Computer is playing, it implements AStarSearch", duration=4000)
    

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
    
    def update(self, game: Game):
        # In the case that it fails to find food a counter measure must be taken
        # Actions must always exist
        if self.actions:
            action = self.actions.popleft()
            self.snake.set_direction(action)
            
        self.snake.move()

        self.big_food.update()
        if self.snake.is_eating_food(self.food):
            self.a_star_variables_update()
            self.snake.grow(size=1)
            self.food.replace(self.snake)
            self.eat_count += 1
            if self.eat_count == REWARD_TRIGER_SCORE:
                self.eat_count = 0
                if not self.big_food.active:
                    self.big_food.is_active(True)
                    self.big_food.replace(self.snake)
                self.find_path_to_food(self.big_food)
            else:
                self.find_path_to_food(self.food)
            game.game_hud.increase_score(self.food.score_incriment)
                
        elif self.snake.is_eating_food(self.big_food):
            self.a_star_variables_update()
            game.game_hud.increase_score(self.big_food.score_incriment)
            self.snake.grow(size=5)
            self.big_food.is_active(False)
            self.find_path_to_food(self.food)

        if self.snake.is_eating_self():
                game.game_hud.update_high_score()
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

    def a_star_variables_update(self):
        if self.dfs_depth < 25: self.dfs_depth += 1
        if self.rand_fact < 0.2 : self.rand_fact += 0.002

    def find_path_to_food(self, food):
        self.problem = SnakeProblem(self.snake.head.cell, food.cell)
        self.f = lambda node: node.depth + (self.problem.heuristic2(node.state))
        self.actions = a_star_search_with_bfs(self.problem, self.f, self.snake, self.dfs_depth, self.rand_fact)


class AIPlayerGreedyState(GameState):
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.big_food = BigFood(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT), 2)
        self.find_path_to_food(self.food)
        self.eat_count = 0
        game.game_hud.score = 0
        game.display_message("Computer is playing, it implements GreedySearch", duration=4000)
    

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
    
    def update(self, game: Game):  
        if self.actions:
            action = self.actions.popleft()
            self.snake.set_direction(action)

        self.snake.move()

        #game.manage_food_and_score()

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
        self.problem = SnakeProblem(self.snake.head.cell, food.cell)
        self.f = lambda node: self.problem.heuristic1(node.state)
        self.actions = greedy_search(self.problem, self.f, self.snake)

class AIPlayerHamiltonianState(GameState):
    def enter(self, game: Game):
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.big_food = BigFood(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT), 2)
        self.eat_count = 0
        self.current_path_index = 0
        game.game_hud.score = 0
        # Generate the Hamiltonian cycle path
        self.generate_hamiltonian_path()
        game.display_message("Computer is playing using Hamiltonian cycle", duration=4000)

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

    def generate_hamiltonian_path(self):
        # Calculate grid dimensions based on screen size
        grid_width = SCREEN_WIDTH // CELL_SIZE
        grid_height = SCREEN_HEIGHT // CELL_SIZE
        
        # Generate the Hamiltonian cycle path
        self.path = []
        for y in range(grid_height):
            # Going right
            if y % 2 == 0:
                for x in range(grid_width):
                    self.path.append((x, y))
            # Going left
            else:
                for x in range(grid_width - 1, -1, -1):
                    self.path.append((x, y))
        
        # Connect back to start (close the cycle)
        self.path.append(self.path[0])
        
        # Pre-calculate the directions between consecutive points
        self.directions = []
        for i in range(len(self.path) - 1):
            current = self.path[i]
            next_point = self.path[i + 1]
            
            # Calculate direction
            dx = next_point[0] - current[0]
            dy = next_point[1] - current[1]
            
            if dx > 0:
                self.directions.append('RIGHT')
            elif dx < 0:
                self.directions.append('LEFT')
            elif dy > 0:
                self.directions.append('DOWN')
            else:
                self.directions.append('UP')

    def update(self, game: Game):
        # Get next direction from the pre-calculated path
        next_direction = self.directions[self.current_path_index]
        self.snake.set_direction(next_direction)
        
        # Move to next position in the cycle
        self.current_path_index = (self.current_path_index + 1) % len(self.directions)
        
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
            game.game_hud.increase_score(self.food.score_incriment)
                
        elif self.snake.is_eating_food(self.big_food):
            game.game_hud.increase_score(self.big_food.score_incriment)
            self.snake.grow(size=5)
            self.big_food.is_active(False)

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
