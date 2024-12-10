# AI Snake Game

This project implements an AI agent to play the classic Snake game using various search algorithms. It provides both AI-controlled gameplay and visualizations of search algorithms exploring the game space. This project was developed as a practical application of AI concepts, offering a hands-on understanding of search algorithms in a game environment.

## Implementation Details

The AI agent can be controlled using different search algorithms, each with its own characteristics:

**AI Play Algorithms:**

* **Online Search (Reinforcement Learning with Danger/Success Memory):**  This agent learns by experience, remembering dangerous locations and successful paths. It uses a custom heuristic incorporating learned danger to guide its decisions, dynamically adapting to the game environment.  This exemplifies a simple reinforcement learning approach.
* **A* Search (with Dynamic Difficulty Adjustment):** Employs the A* search algorithm with Manhattan distance as the heuristic.  To manage search complexity and adapt to the game's dynamics, it incorporates a depth-first search (DFS) component. Parameters like DFS depth and a randomization factor are adjusted based on the snake's performance (e.g., increasing DFS depth if the snake consistently performs well).
* **Breadth-First Search (BFS):**  A systematic algorithm that guarantees finding the shortest path to the food but can be computationally expensive in larger or complex game states.
* **Depth-First Search (DFS):** Explores a single branch as deeply as possible before backtracking.  While potentially faster than BFS, it doesn't guarantee finding the shortest path.
* **Greedy Best-First Search:**  A heuristic-driven approach that prioritizes the move seemingly closest to the food.  While efficient, it might miss optimal solutions due to its lack of broader exploration.
* **Hamiltonian Cycle (Demonstration):** This agent showcases a deterministic approach by following a pre-calculated Hamiltonian cycle, a path that visits every grid cell exactly once. This strategy provides a safe but not always the most efficient way to reach the food.


**AI Vision Algorithms (Visualization):**

These algorithms focus on visualizing the search process itself, providing insights into how different strategies explore the game board to find a path to the food:

* **A* Search:** Visualizes A* using a combined heuristic considering distance to food, distance to walls (avoiding collisions), and available space to provide a more comprehensive evaluation of possible moves.
* **Breadth-First Search (BFS):**  Visualizes the layer-by-layer exploration of BFS.
* **Depth-First Search (DFS):** Visualizes the deep exploration and backtracking behavior of DFS.
* **Greedy Best-First Search:**  Visualizes the heuristic-driven, locally optimal choices of Greedy Best-First Search.
* **Online Search:** Visualizes the real-time learning process of the online search agent as it explores, encounters dangers, and refines its internal map of the environment.

**Technical Details:**

*   **Programming Language:** Python
*   **Libraries:** Pygame (for game logic and rendering), NumPy (for numerical operations), Matplotlib (for visualizations)  ,  Pyinstrument (used for optional code profiling during development.)
*   **Game State Representation:** Utilizes a grid-based representation of the game board to facilitate search algorithms.

## How to Run

1.  **Prerequisites:** Python 3.12 (recommended to use a virtual environment)
2.  **Installation:**

    ```bash
    git clone https://github.com/Ta-Pc/Snake-Game.git 
    cd ai-snake-game
    python3 -m venv .venv
    source .venv/bin/activate  # Activate virtual environment (Linux/macOS)
    .venv\Scripts\activate      # Activate virtual environment (Windows)
    pip install -r requirements.txt
    ```
3.  **Running the Game:**
    ```bash
    python main.py
    ```
4. **Running the Visualization:**
    ```bash
    python visualization.py
    ```


## Controls

*   **Arrow Keys:** Control the snake's direction (in human play mode).
*   **SPACE:** Pause/Resume the game.
*   **ESC:** Return to the main menu.  (Exits the visualiser)
* **Visualizer Mouse Interactions:**
    * **Left click + drag:** Rotate the 3D view.
    * **Right click + drag:** Zoom in/out.
    * **Middle click + drag:** Pan the view.
    * **Space:** Pause/Resume the simulation.
    * **R:** Reset the view to the default angle.




## Features

*   AI agents using various search algorithms.
*   Real-time visualization of AI search processes.
*   Human playable mode.
*   Multiple difficulty levels corresponding to AI speed.
*   Big food for bonus points and AI triggering events.
*   Pause/resume functionality.
*   High score tracking.
*   Main menu for selecting game modes and options.


## Future Enhancements

*   Implementing more advanced AI techniques (e.g., Q-learning, Deep Reinforcement Learning).
*   Adding more sophisticated game elements and levels.
*   Improving the user interface and visualization tools.
*   Incorporating sound effects and music.


## Contributing

Contributions are welcome! Feel free to submit pull requests for bug fixes, new features, or improved documentation.


## License

This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.

You may obtain a copy of the License at:

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)
