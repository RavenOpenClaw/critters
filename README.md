# Critters (Working Title)

Critters is a creature collector incremental game with a focus on exploration, building, and simulation. Explore the hand-crafted world to find resources and secrets. Build a home. Watch your critters grow!

## 🛠 Project Foundations

This project is a prototype designed to explore the core simulation and creature mechanics of "Critters." The logic is written in Python to ensure it is easily understandable and portable to other platforms or engines (like Godot) in the future.

### Tech Stack

- Language: Python 3.x
- OS: Windows 11 (Native)
- Ubuntu (WSL)
- Version Control: Git (installed only on WSL)

#### Note about path

On the native Windows hardware, the path to this project is `C:\Users\Sean\Desktop\dev\kiro\critters`.

On WSL the path to this project is `/mnt/c/Users/Sean/Desktop/dev/kiro/critters`.mnt/c/Users/Sean/Desktop/dev/kiro/critters`.

### 📁 Directory Structure

- src/: All source code and game logic.
- doc/: Documentation including requirements, design, and architecture.
- tst/: Unit and integration tests (Critical for agent reliability).
- config/: Configuration and balancing files.
- README.md: This file.

## 🚀 Getting Started

### Option A: Using Make (simplest)
```bash
make setup   # First time only: creates venv and installs deps
make test    # Run the test suite
```

### Option B: Manual Setup
Refer to `doc/dependencies.md` for required libraries.

1. Create virtual environment:
```bash
python3 -m venv venv
```

2. Install dependencies:
```bash
venv/bin/pip install pygame pytest hypothesis
```

3. Run the prototype:
```bash
# Activate the venv first (optional but convenient):
source venv/bin/activate   # On Linux/macOS
# venv\Scripts\activate   # On Windows PowerShell
python src/main.py
```

4. Run tests:
```bash
PYTHONPATH=src venv/bin/python -m pytest tst/
```

## 📦 Notes
- The project includes a `Makefile` to automate setup (`make setup`), testing (`make test`), and cleanup (`make clean`).
- If you prefer not to use Make, follow the manual steps above.
- The `venv/` directory is gitignored; dependencies are not committed.

## 🤖 Agent Workflow (Mandatory)

Agents must follow this strict workflow to maintain code quality and visibility:

1. Task Selection: Choose a task from doc/TASKS.md. Update status to "In Progress."
1. Branching: Create a new feature branch from mainline.
1. Development: Implement the feature in src/.
1. Testing:
    1. Run all existing tests in tst/.
    1. Add new tests for the current feature.
    1. Ensure all tests pass before merging.
1. Merging: Merge the branch into main.
1. Updating Docs: - Update tasks.md to "Completed."
    1. If new libraries were added, update doc/dependencies.md.

## 📜 Source of Truth

For the original vision and philosophy behind this setup, refer to /doc/INITIAL_DIRECTIVES.md.