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

### Option B: Quick play script
On Linux/macOS you can run the game directly:
```bash
./PLAY.sh
```
(Ensure the script is executable: `chmod +x PLAY.sh`)

### Option C: Manual Setup
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

## 🎮 Controls

- **WASD**: Move player
- **E**: Interact with nearby objects (tap once, or hold for auto-repeat)
  - Hold threshold: 0.5 s before auto-repeat begins
  - Base auto-repeat rate: 2 interactions per second (configurable via code)
- **F3**: Toggle debug overlay (FPS, position, interaction radius)
- **B**: Toggle build menu
- **G**: Select Gathering Hut (when build menu is open)
- **Mouse Click**: Place selected building (when build menu is open)

## 🤖 Agent Workflow (Mandatory)

Agents must follow this strict workflow to maintain code quality and visibility:

1. Task Selection: Choose a task from the **primary task list** (`.kiro/specs/critters-game-prototype/tasks.md`). Optionally cross-check with `doc/HIGH_LEVEL_TASKS.md` for guardrails. Update status to "In Progress."
2. Branching: Create a new feature branch from `mainline`.
3. Development: Implement the feature in `src/`.
4. Testing:
   - Run all existing tests in `tst/`.
   - Add new tests for the current feature.
   - Ensure all tests pass before merging.
5. Merging: Merge the branch into `mainline`.
6. Updating Docs:
   - Update both task files to mark completed items (checkboxes in `.kiro/specs/.../tasks.md` and `doc/HIGH_LEVEL_TASKS.md`).
   - If new libraries were added, update `doc/dependencies.md`.
7. Bug Reporting: If you discover bugs during development or testing, add them to `.kiro/specs/critters-game-prototype/bugs.md` with the required format (ID, Expected, Actual, Reproduce, Desired fix). See `DOCUMENTATION_INDEX.md` for more on the bug tracking process.

## 📜 Source of Truth

- **Detailed implementation plan**: `.kiro/specs/critters-game-prototype/tasks.md` (the Kiro task file) is the authoritative source for what to build next.
- **High-level vision and guardrails**: `doc/HIGH_LEVEL_TASKS.md` outlines major phases and should be used to avoid misalignment with the overall project goals.
- **Initial directives**: `doc/INITIAL_DIRECTIVES.md` contains the original philosophy and constraints.

## 📌 Documentation Index

New to the project? Start with `DOCUMENTATION_INDEX.md` at the repository root. It's a quick lookup guide to all critical documents (tasks, design, requirements, save system guide) and explains common pitfalls like the hidden `.kiro` directory.

## 🐛 Bug Tracking and Fixes

Bugs are reported and tracked in `.kiro/specs/critters-game-prototype/bugs.md`. When a bug is fixed, the same entry is updated with:
- `Status: FIXED`
- `Fix commit: <short-sha>`
- A `Fix Details` section containing **Plan**, **Implementation**, and **Testing**.

This unified file serves as the single source of truth for both bug reports and their resolutions.

## 📊 Commit Traceability

`COMMIT_ACCOUNTING.md` maps every commit on `mainline` to its associated task number, bug ID, or category (Feature, Test, Documentation, etc.). This matrix ensures full auditability. Agents must update this file (or confirm entries exist) when merging work.

## ✅ Pre-Report Checklist

Before reporting completion to the user, agents must verify:
- [ ] Bug fixes: updated `bugs.md` with fix details and commit ID.
- [ ] Task completions: marked in `.kiro/specs/critters-game-prototype/tasks.md` (with checkmark) and referenced commit ID.
- [ ] Branch merged to `mainline` and pushed.
- [ ] `COMMIT_ACCOUNTING.md` updated if new commit types appear.
- [ ] Full test suite passes.
- [ ] Any changed workflows documented in relevant READMEs or skills.

(Full checklist also in `AGENTS.md` under "Pre-Report Documentation Checklist".)

## 🤖 Agent Onboarding

Agents should:
1. Read `README.md` (this file).
2. Consult `DOCUMENTATION_INDEX.md` for quick lookups.
3. Select the next task from `.kiro/specs/critters-game-prototype/tasks.md`.
4. Follow the workflow above and checklist.

The `critters-implement` skill automates this orientation—use it to quickly start the next task.