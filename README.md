# AI-Powered Snake Game with Search Algorithm Visualizations

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Code Style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python-based implementation of the classic Snake game, featuring AI agents powered by various search algorithms and interactive visualizations of their exploration process.

---

### **✨ Core AI Visualization in Action**

*(This is where your most impressive GIF will go. A recruiter should see this first!)*

![A* Search Algorithm Visualization](YOUR_AI_VISUALIZATION_GIF_HERE)

---

### 🚀 Features

This project is more than just a game; it's a comprehensive tool for exploring and understanding AI search algorithms.

| Feature                      | Description                                                                                                                              |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 🧠 **Multiple AI Agents**    | Switch between seven different AI algorithms, from simple heuristics like Greedy Best-First Search to complex pathfinding like A*.       |
| 📊 **Real-Time Visualization** | Watch the AI's "thought process" in real-time as it explores the game board, providing a clear visual understanding of how each algorithm works. |
| 🕹️ **Full Joystick Support** | Play the game or navigate all menus using a standard joystick, in addition to keyboard controls.                                         |
| 🧑‍💻 **Human Playable Mode**   | Take control yourself and try to beat the high scores in a classic, polished Snake experience.                                            |
| ⚙️ **Customizable Difficulty** | Adjust the game speed across four difficulty levels to provide a challenge for both human players and the AI agents.                     |
| 🏆 **Persistent High Scores**  | Your best scores for each difficulty level are saved and displayed, encouraging replayability.                                          |
| 🎨 **Polished UI/UX**          | A clean and intuitive user interface with a full main menu, level selection, and in-game pause functionality.                          |

---

### 📸 Gallery

<p align="center">
  <strong>Main Menu & Level Select</strong><br>
  <img src="https://github.com/user-attachments/assets/1002e2fb-b6da-4c99-9860-256dbd33c9b5" alt="Main Menu" width="45%"/>
  <img src="https://github.com/user-attachments/assets/44b2d9f1-6923-4ada-a37f-7c76a53ff034" alt="Levels" width="45%"/>
</p>
<p align="center">
  <strong>Gameplay & High Scores</strong><br>
  <img src="https://github.com/user-attachments/assets/13a4198c-fa81-434a-a913-2ce5796de000" alt="Human Player" width="45%"/>
  <img src="https://github.com/user-attachments/assets/582f744e-b3c3-4616-b8b6-bf5bece632d4" alt="High Scores" width="45%"/>
</p>

---

### 🛠️ Tech Stack

| Component                | Technologies                                                                                             |
| ------------------------ | -------------------------------------------------------------------------------------------------------- |
| **Core Language**        | `Python 3.7+`                                                                                            |
| **Libraries & Frameworks** | `Pygame` (for game logic, rendering, controls), `NumPy` (numerical operations), `Matplotlib` (visualizations) |
| **Development Tools**    | `Pyinstrument` (for optional code profiling), `black` (for code formatting)                              |

<br>

<details>
  <summary><strong>🧠 Click to see Detailed Algorithm Explanations</strong></summary>
  
  ### AI Play Algorithms
  * **Online Search (Reinforcement Learning with Danger/Success Memory):** This agent learns by experience, remembering dangerous locations and successful paths. It uses a custom heuristic incorporating learned danger to guide its decisions, dynamically adapting to the game environment.
  * **A* Search (with Dynamic Difficulty Adjustment):** Employs the A* search algorithm with Manhattan distance as the heuristic. To manage search complexity and adapt to the game's dynamics, it incorporates a DFS component.
  * **Breadth-First Search (BFS):** A systematic algorithm that guarantees finding the shortest path to the food but can be computationally expensive.
  * **Depth-First Search (DFS):** Explores a single branch as deeply as possible before backtracking. While potentially faster than BFS, it doesn't guarantee finding the shortest path.
  * **Greedy Best-First Search:** A heuristic-driven approach that prioritizes the move seemingly closest to the food, which can miss optimal solutions.
  * **Hamiltonian Cycle (Demonstration):** A deterministic approach following a pre-calculated path that visits every grid cell exactly once.

  ### AI Vision Algorithms (Visualization)
  * These algorithms focus on visualizing the search process itself, providing insights into how different strategies explore the game board to find a path to the food for A*, BFS, DFS, Greedy, and Online Search.

</details>

---

### ⚙️ Getting Started

<details>
  <summary><strong>Installation Instructions</strong></summary>
  
  1. **Prerequisites:** Ensure you have Python 3.7+ installed.
  2. **Clone the repository:**
      ```bash
      git clone https://github.com/Ta-Pc/AI-Snake-Game.git
      cd AI-Snake-Game
      ```
  3. **Set up a virtual environment:**
      *   On **Linux/macOS**:
          ```bash
          python3 -m venv .venv
          source .venv/bin/activate
          ```
      *   On **Windows**:
          ```bash
          python -m venv .venv
          .venv\Scripts\activate
          ```
  4. **Install dependencies:**
      ```bash
      pip install -r requirements.txt
      ```
</details>

<details>
  <summary><strong>Running the Game & Controls</strong></summary>

  * **To run the main game:**
      ```bash
      python main.py
      ```
  
  * **Controls:**
    | Control      | Action                                          |
    |--------------|-------------------------------------------------|
    | `Arrow Keys` | Control snake direction & navigate menus        |
    | `Joystick`   | Control snake direction & navigate menus        |
    | `SPACE`      | Pause / Resume the game                         |
    | `ESC`        | Return to the main menu or exit the visualiser |

</details>

---

### 🌱 Future Enhancements
*   Implementing more advanced AI techniques (e.g., Q-learning, Deep Reinforcement Learning).
*   Adding more sophisticated game elements and levels.
*   Improving the user interface and visualization tools.
*   Incorporating sound effects and music.

###🤝 Contributing
Contributions are welcome! Feel free to submit pull requests for bug fixes, new features, or improved documentation.

### 📄 License
This project is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for details.
