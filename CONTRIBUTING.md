# Contributing to AI Snake Game

Thank you for your interest in contributing to the AI Snake Game project! We welcome contributions from everyone, whether you're fixing bugs, adding new features, improving the visualizations, or experimenting with new AI algorithms. These guidelines will help you get started.

## Ways to Contribute

We appreciate all contributions, but here are some areas where we could particularly use your help:

*   **Reporting Bugs:** If you encounter any bugs or unexpected behavior, please open an issue on GitHub. Be sure to include:
    *   A clear and descriptive title.
    *   A detailed description of the bug.
    *   Steps to reproduce the bug.
    *   Information about your environment (operating system, Python version, etc.).
*   **Suggesting Enhancements:** Have an idea for a new feature, a better visualization, or an improvement to an existing algorithm? Please open an issue on GitHub to discuss your suggestion.
*   **Improving Documentation:** Help us make the README, code comments, or other documentation clearer, more accurate, or more comprehensive.
*   **Implementing AI Algorithms:** We're particularly interested in contributions that implement new search algorithms or improve existing ones (see "AI Algorithms" section below).
*   **Creating Visualizations:** Help us visualize the search algorithms in a more informative and engaging way.
*   **Writing Code:** Contribute new features, fix bugs, refactor code, or improve performance.
*   **Testing:** Help us test new features or bug fixes to ensure they work correctly on different systems and configurations.

## AI Algorithms

This project focuses on implementing and visualizing various search algorithms for the Snake game. We encourage contributions of new algorithms or improvements to existing ones. Here are some ideas:

*   **Implement New Algorithms:** Consider adding algorithms like:
    *   Iterative Deepening A* (IDA*)
    *   Bidirectional Search
    *   Monte Carlo Tree Search (MCTS)
    *   Other relevant search or reinforcement learning algorithms
*   **Improve Existing Algorithms:**
    *   Optimize the performance of existing algorithms.
    *   Add more sophisticated heuristics for A* or Greedy Best-First Search.
    *   Refine the online learning agent's exploration/exploitation strategy.
*   **Enhance Visualizations:**
    *   Create more informative or visually appealing visualizations of the search process.
    *   Visualize the agent's internal state (e.g., danger memory, learned paths).

## Getting Started

1. **Fork the repository:** Click the "Fork" button on the top-right of the [repository page](https://github.com/Ta-Pc/AI-Snake-Game) to create your own copy.

2. **Clone your fork:**
    ```bash
    git clone https://github.com/your-username/AI-Snake-Game.git
    cd AI-Snake-Game
    ```

3. **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    .venv\Scripts\activate      # Windows
    ```

4. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Development Workflow

1. **Create a branch:** Always create a new branch for your work, based on the `main` branch:
    ```bash
    git checkout main
    git pull origin main # Make sure your main branch is up to date first
    git checkout -b feature/your-feature-name  # For new features
    git checkout -b bugfix/your-bugfix-name   # For bug fixes
    ```

2. **Follow the Style Guide:** This project follows the [PEP 8 style guide](https://www.python.org/dev/peps/pep-0008/) for Python code. Use a linter like `flake8` to check your code:
    ```bash
    pip install flake8
    flake8 .
    ```

3. **Write Tests:** If you're adding new code or fixing bugs, please write tests to ensure the correctness of your changes. We use `pytest` for testing.

4. **Commit Your Changes:**
    *   Write clear and concise commit messages that explain the purpose of your changes. Use imperative mood (e.g., "Add feature X" instead of "Added feature X").
    *   Follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification where possible (e.g., `feat: add new feature`, `fix: resolve bug #123`, `docs: update README`).

5. **Push Your Branch:**
    ```bash
    git push origin your-branch-name
    ```

6. **Open a Pull Request (PR):**
    *   Go to the original repository on GitHub ([Ta-Pc/AI-Snake-Game](https://github.com/Ta-Pc/AI-Snake-Game)).
    *   Click "Pull requests" -> "New pull request".
    *   Select your branch (the one with your changes) and the `main` branch as the base.
    *   Provide a clear and descriptive title for your PR.
    *   Explain the changes you've made in detail.
    *   Link to any relevant issues by including the issue number (e.g., "Fixes #123") in the PR description.
    *   Submit the PR.

## Code of Conduct

Please review our [Code of Conduct](CODE_OF_CONDUCT.md). All contributors are expected to follow the guidelines outlined in this document to ensure a positive and inclusive community.

## Issue and Pull Request Guidelines

### Issues:

*   **Search First:** Before opening a new issue, please search existing issues to see if someone else has already reported the same problem or made a similar suggestion.
*   **Be Descriptive:** Use a clear and descriptive title for your issue.
*   **Provide Details:** Include as much information as possible about the bug, enhancement, or question. For bug reports, provide steps to reproduce the issue, your operating system, Python version, and any error messages.
*   **Use Labels:** If you have the necessary permissions, you can add relevant labels to your issue to help categorize it.

### Pull Requests:

*   **Code Style:** Ensure your code adheres to the PEP 8 style guide and is well-documented.
*   **Tests:** Include tests for any new code or bug fixes.
*   **Small, Focused PRs:** Keep your PRs focused on a single feature or bug fix. Smaller PRs are easier to review and merge.
*   **Descriptive Title and Description:** Provide a clear and informative title for your PR. In the description, explain:
    *   The purpose of your changes.
    *   How you implemented the changes.
    *   Any relevant background information or context.
    *   Any limitations or potential issues.
*   **Reference Issues:** If your PR addresses an existing issue, reference it in the description using the `#` followed by the issue number (e.g., "Fixes #123").
*   **Review and Feedback:** Be responsive to feedback from maintainers and other contributors. Be prepared to make changes or improvements based on the feedback you receive.

## License

By contributing to this project, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).

## Getting Help

If you have any questions about contributing, need help getting started, or want to discuss your ideas, feel free to:

*   **Open an issue** on GitHub.
*   **Contact me directly** at [your-email@example.com] (replace with your actual email).

We look forward to your contributions!
