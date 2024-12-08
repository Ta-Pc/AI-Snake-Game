from collections import deque
import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter
from Snake import Snake, Food, Direction
from Search import Node, SnakeProblem
from Constants import *
from scipy.spatial.distance import cityblock as manhattan_distance
from mpl_toolkits.axes_grid1 import make_axes_locatable

class OptimizationLandscapeVisualizer:
    def __init__(self):
        # Initialize simulation components
        self.snake = Snake((SCREEN_CENTER[0], SCREEN_CENTER[1]))
        self.food = Food(self.snake, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
        self.node = Node(self.problem.init_pos)
        
        # Create fullscreen figure with proper subplot
        plt.ion()
        self.fig = plt.figure(figsize=(12, 8))
        gs = self.fig.add_gridspec(1, 1)  # Create a 1x1 grid
        self.ax = self.fig.add_subplot(gs[0, 0], projection='3d')
        self.fig.canvas.manager.window.state('zoomed')
        
        # Initialize the surface plot
        x_coords = np.arange(0, SCREEN_WIDTH, CELL_SIZE/2)
        y_coords = np.arange(0, SCREEN_HEIGHT, CELL_SIZE/2)
        self.X, self.Y = np.meshgrid(x_coords, y_coords)
        self.Z = np.zeros_like(self.X, dtype=float)
        
        # Initialize plots
        self.surface = None
        self.snake_scatter = self.ax.scatter([], [], [], c='darkred', marker='o', 
                                           s=200, label='Snake Head')
        self.food_scatter = self.ax.scatter([], [], [], c='lime', marker='^', 
                                          s=200, label='Food')
        
        # Setup plot styling
        self.setup_plot_styling()
        
        # Initialize interaction variables
        self.paused = False
        self.running = True
        self.setup_interactions()
        
        # Initial visualization
        self.calculate_landscape()
        self.update_visualization()

    def setup_plot_styling(self):
        self.ax.set_title('Snake Navigation Cost Landscape\n'
                         'Left click + drag: Rotate | Right click + drag: Zoom | '
                         'Middle click + drag: Pan | Space: Pause | R: Reset View',
                         pad=20, size=14)
        self.ax.set_xlabel('X Position', labelpad=10)
        self.ax.set_ylabel('Y Position', labelpad=10)
        self.ax.set_zlabel('Cost', labelpad=10)
        
        self.colormap = plt.cm.viridis_r
        self.ax.grid(True, linestyle='--', alpha=0.3)
        
        # Set initial view
        self.view_angle = 45
        self.elevation = 30
        self.ax.view_init(elev=self.elevation, azim=self.view_angle)
        
        # Set axis limits
        self.ax.set_xlim(0, SCREEN_WIDTH)
        self.ax.set_ylim(0, SCREEN_HEIGHT)
        
        # Create initial surface plot
        self.surface = self.ax.plot_surface(
            self.X, self.Y, self.Z,
            cmap=self.colormap,
            antialiased=True,
            alpha=0.8,
            linewidth=0,
            rcount=100,
            ccount=100
        )
        
        # Create colorbar once and store the reference
        self.colorbar = self.fig.colorbar(self.surface, ax=self.ax, label='Cost Value')
        
        self.fig.tight_layout()

    def setup_interactions(self):
        self.fig.canvas.mpl_connect('button_press_event', self.on_mouse_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_mouse_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        self.fig.canvas.mpl_connect('close_event', self.on_close)
        
        self.mouse_pressed = False
        self.last_mouse_pos = None

    def run(self):
        while self.running:
            if not self.paused:
                self.step()
            plt.pause(0.01)

    def step(self):
        # Update snake position based on local search
        direction = self.find_solution()
        self.snake.set_direction(direction)
        self.snake.move()
        
        # Check for food collision
        if self.snake.is_eating_food(self.food):
            self.food.replace(self.snake)
            self.snake.grow(3)
            self.problem = SnakeProblem(self.snake.head.cell, self.food.cell)
            self.node = Node(self.problem.init_pos)
        
        self.update_visualization()

    def calculate_landscape(self):
        """Calculate the cost landscape"""
        snake_positions = [self.snake.head.cell] + [sbo.cell for sbo in self.snake.tail]
        
        for i in range(self.Z.shape[0]):
            for j in range(self.Z.shape[1]):
                pos = (j * CELL_SIZE/2, i * CELL_SIZE/2)
                if any(manhattan_distance(pos, sp) < CELL_SIZE for sp in snake_positions):
                    self.Z[i, j] = float('inf')
                else:
                    test_node = Node(pos)
                    self.Z[i, j] = self.cost(test_node)
        
        self.Z = gaussian_filter(self.Z, sigma=1.0)

    def update_visualization(self):
        """Update the visualization without recalculating the landscape"""
        # Calculate new landscape
        self.calculate_landscape()
        
        # Remove previous surface
        if self.surface is not None:
            self.surface.remove()
        
        # Plot new surface
        self.surface = self.ax.plot_surface(
            self.X, self.Y, self.Z,
            cmap=self.colormap,
            antialiased=True,
            alpha=0.8,
            linewidth=0,
            rcount=100,
            ccount=100
        )
        
        # Update colorbar's mappable to the new surface
        self.colorbar.mappable = self.surface
        self.colorbar.update_normal(self.surface)
        
        # Remove previous scatter plots
        # To avoid errors, ensure that scatter plots exist before removing
        if hasattr(self, 'snake_scatter') and self.snake_scatter is not None:
            self.snake_scatter.remove()
        if hasattr(self, 'food_scatter') and self.food_scatter is not None:
            self.food_scatter.remove()
        
        # Update markers
        snake_z = self.get_z_value(self.snake.head.cell)
        food_z = self.get_z_value(self.food.cell)
        
        self.snake_scatter = self.ax.scatter([self.snake.head.cell[0]], 
                                           [self.snake.head.cell[1]], 
                                           [snake_z],
                                           c='darkred', marker='o', s=200, label='Snake Head')
        self.food_scatter = self.ax.scatter([self.food.cell[0]], 
                                          [self.food.cell[1]], 
                                          [food_z],
                                          c='lime', marker='^', s=200, label='Food')
        
        # Refresh display
        self.fig.canvas.draw()

    def on_mouse_press(self, event):
        self.mouse_pressed = True
        self.last_mouse_pos = (event.xdata, event.ydata)

    def on_mouse_release(self, event):
        self.mouse_pressed = False

    def on_mouse_move(self, event):
        if self.mouse_pressed and event.inaxes and self.last_mouse_pos:
            dx = event.xdata - self.last_mouse_pos[0]
            dy = event.ydata - self.last_mouse_pos[1]
            
            if event.button == 1:  # Left click - rotate
                self.view_angle = (self.view_angle - dx) % 360
                self.elevation = min(max(self.elevation + dy, -90), 90)
                self.ax.view_init(elev=self.elevation, azim=self.view_angle)
            
            elif event.button == 3:  # Right click - zoom
                # Adjust the distance based on vertical mouse movement
                # Note: For 3D plots, zoom can be handled by changing the elevation or azimuth
                # Alternatively, you can adjust the scale or limits
                # Here, we'll adjust the elevation to simulate zoom
                self.ax.dist = max(1, self.ax.dist * (0.99 if dy > 0 else 1.01))
            
            elif event.button == 2:  # Middle click - pan
                # Panning in 3D is non-trivial; here we'll adjust the limits slightly
                xlim = self.ax.get_xlim()
                ylim = self.ax.get_ylim()
                self.ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
                self.ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
            
            self.fig.canvas.draw()
            
        self.last_mouse_pos = (event.xdata, event.ydata)

    def on_key_press(self, event):
        if event.key == ' ':
            self.paused = not self.paused
        elif event.key == 'r':
            self.reset_view()
        elif event.key == 'escape':
            self.running = False
            plt.close(self.fig)

    def on_close(self, event):
        self.running = False

    def reset_view(self):
        self.view_angle = 45
        self.elevation = 30
        self.ax.view_init(elev=self.elevation, azim=self.view_angle)
        self.ax.dist = 10
        self.fig.canvas.draw()

    def get_z_value(self, position):
        """Get interpolated Z value for any X,Y position"""
        x, y = position
        i = int(y // (CELL_SIZE/2))
        j = int(x // (CELL_SIZE/2))
        if 0 <= i < self.Z.shape[0] and 0 <= j < self.Z.shape[1]:
            return self.Z[i, j]
        return 0

    def cost(self, node):
        return self.problem.heuristic1(node.state)

    def find_solution(self):
        new_snake = list([self.snake.head.cell] + [sbo.cell for sbo in self.snake.tail])
        neighbours = self.node.expand(self.problem)
        valid_neighbours = [n for n in neighbours if n.state not in new_snake]
        self.node = min(valid_neighbours, key=self.cost) if valid_neighbours else None
        return self.node.action if self.node else Direction.NONE

import numpy as np
import matplotlib.pyplot as plt

def plot_1d_cost_landscape(snake, food, problem, cell_size=10):
    """
    Plots the 1D cost landscape for the given snake and food positions.
    
    Parameters:
    snake (Snake): The snake object
    food (Food): The food object
    problem (SnakeProblem): The problem object
    cell_size (int): The size of each cell in the landscape
    """
    # Get the snake and food positions
    snake_positions = [snake.head.cell] + [sbo.cell for sbo in snake.tail]
    food_position = food.cell
    
    # Create the 1D landscape
    x_w = np.arange(0, SCREEN_WIDTH, cell_size)
    x_h = np.arange(0, SCREEN_HEIGHT, cell_size)
    cost_landscape_w = np.array([problem.heuristic1((x_pos, 0)) for x_pos in x_w])
    cost_landscape_h = np.array([problem.heuristic1((0, y_pos)) for y_pos in x_h])
    cost_landscape = []
    x_scale = [0]
    parent_node = Node(snake.head.cell)
    frontier = deque([parent_node])
    reached = set(parent_node.state)
    
    while frontier:
        parent_node = frontier.pop()
        for child_node in ocupiable_cells(parent_node.expand(problem), snake_positions):
            
            state = child_node.state
            if state not in reached:
                cost_landscape.append(problem.heuristic1(child_node.state))
                frontier.append(child_node)
                reached.add(state)


    cost_landscape = np.array(cost_landscape)
    #cost_landscape.sort()
    x_scale = [i for i in range(len(cost_landscape))]
    
    
    # Plot the cost landscape
    plt.figure(figsize=(12, 6))
    plt.plot(x_scale, cost_landscape)
    #plt.plot(x_h, cost_landscape_h)
    plt.scatter([pos[0] for pos in snake_positions], [0] * len(snake_positions), c='darkred', marker='o', s=100, label='Snake')
    plt.scatter(food_position[0], 0, c='lime', marker='^', s=100, label='Food')
    plt.xlabel('X Position')
    plt.ylabel('Cost')
    plt.title('1D Snake Navigation Cost Landscape')
    plt.legend()
    plt.grid(True)
    plt.show()

def ocupiable_cells(nodes, parent_snake: list):
    """Return nodes that avoids the snake body"""
    return [node for node in nodes if node.state not in parent_snake]