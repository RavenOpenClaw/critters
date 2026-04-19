# Critters Documentation Index

**Purpose:** This index provides quick reference to all critical project documents. Use it to locate requirements, design, tasks, and guidelines.

---

## 📌 Master Documents

| Document | Path | Purpose |
|----------|------|---------|
| **Master Task List** | `.kiro/specs/critters-game-prototype/tasks.md` | **The definitive task list.** All implementation work should reference this file. |
| **Design & Architecture** | `.kiro/specs/critters-game-prototype/design.md` | Full system architecture, design principles, data flow, and module relationships. |
| **Requirements** | `.kiro/specs/critters-game-prototype/requirements.md` | Detailed requirements and acceptance criteria. |
| **Bug Tracking** | `.kiro/specs/critters-game-prototype/bugs.md` | Unified bug reports and fix details (when fixed). |
| **Commit Accounting** | `COMMIT_ACCOUNTING.md` | Traceability matrix mapping every commit to tasks/bugs/categories. |
| **Full Changelog** | `CHANGELOG.md` | Complete audit trail of all commits on `mainline` with task/bug associations. |

---

## 📚 Supporting Documentation

### In `doc/` (lowercase)

- `REQUIREMENTS.md` – Condensed requirements overview
- `HIGH_LEVEL_TASKS.md` – Phase-based task summary (less detailed than Kiro tasks)
- `INITIAL_DIRECTIVES.md` – Early project directives
- `dependencies.md` – Python dependencies and setup
- `DECONSTRUCTION_DESIGN.md` – Specific design notes for deconstruction feature

### In `docs/` (uppercase)

- `SAVE_SYSTEM_EXTENSION.md` – **Essential guide** for adding new serializable types. Read before extending world objects.

---

## 🗂️ Repository Structure (Quick Reference)

```
critters/
├── .kiro/specs/critters-game-prototype/
│   ├── tasks.md          ← **START HERE** for what to implement next
│   ├── design.md         ← Deep architecture
│   ├── requirements.md   ← Full requirements
│   ├── bugs.md           ← Unified bug tracking and fix documentation (includes fixes)
├── doc/                  ← Additional design and notes
├── src/                  ← Source code modules
├── tst/                  ← Test suite
├── README.md             ← Project overview
├── COMMIT_ACCOUNTING.md  ← Mapping of every commit to task/bug/category
└── DOCUMENTATION_INDEX.md ← This file
```

---

## 🧩 Common Lookups

- **What should I work on next?** → `.kiro/specs/critters-game-prototype/tasks.md`
- **How does the system fit together?** → `.kiro/specs/critters-game-prototype/design.md`
- **How to add a new building/object and make it savable?** → `docs/SAVE_SYSTEM_EXTENSION.md`
- **What are the exact requirements for feature X?** → `.kiro/specs/critters-game-prototype/requirements.md`
- **Dependencies and setup?** → `doc/dependencies.md`
- **Where are the tests?** → `tst/test_*.py` (match name to module)
- **Which commit corresponds to which task/bug?** → `COMMIT_ACCOUNTING.md` (traceability matrix)
- **What bugs are known and how are they fixed?** → `.kiro/specs/critters-game-prototype/bugs.md` (unified bug reports and fix details)
- **Which commit introduced change Y?** → `CHANGELOG.md` (search by commit or message)

---

## ⚠️ Critical Notes for Agents

- **Hidden `.kiro` directory**: This contains the most important planning documents. The dot prefix means `ls` may not show it by default; use `ls -a` or explicitly list `.kiro/`.
- **Two doc folders**: Both `doc/` and `docs/` exist; check both when searching. `.kiro` holds the master specs.
- **Tasks file location**: Many agents mistakenly look for `TASKS.md` in the root. The true master task list is at `.kiro/specs/critters-game-prototype/tasks.md`—always check there first.
- **Save system changes**: Any new `WorldObject` subclass must be added to the serialization dispatcher in `src/save_system.py`. See `docs/SAVE_SYSTEM_EXTENSION.md` for the exact steps.

---

## 🔄 Quick Commands

```bash
# Show all markdown documentation files (including hidden directories)
find . -name "*.md" -not -path "./venv/*" | sort

# View the master tasks file (use less or cat)
cat .kiro/specs/critters-game-prototype/tasks.md

# Run the full test suite
PYTHONPATH=src venv/bin/python -m pytest tst/ -v
```

---

_Keep this index up to date as documentation evolves._
