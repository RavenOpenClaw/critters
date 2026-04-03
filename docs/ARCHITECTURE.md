# Critters Code Index & Architecture

_Maintained for agents and developers. This document indexes critical files, explains code structure, and clarifies common pitfalls._

## 📂 Critical Documents Index

Many important files are hidden or in non-standard locations. Here is a definitive index.

| Document | Path | Purpose |
|----------|------|---------|
| **Master Task List** | `.kiro/specs/critters-game-prototype/tasks.md` | **This is the authoritative task list.** All feature work should reference this file. Agents often miss this because `.kiro` is a hidden dot-directory. |
| Design Requirements | `doc/REQUIREMENTS.md` | High-level feature requirements and design goals. |
| High-Level Task Summary | `doc/HIGH_LEVEL_TASKS.md` | Summary view of phases and tasks. Less detailed than the Kiro tasks; defer to `.kiro/specs/.../tasks.md`. |
| Save System Extension Guide | `docs/SAVE_SYSTEM_EXTENSION.md` | Guidelines for extending serialization to new types. Critical when adding new WorldObject subclasses. |
| Deconstruction Design | `doc/DECONSTRUCTION_DESIGN.md` | Design notes for deconstruction mechanic. |
| Dependencies | `doc/dependencies.md` | Python package dependencies and setup instructions. |
| README | `README.md` | Project overview and quick start. |
| WORKING\_ON.md | `WORKING_ON.md` | Current task tracking; what’s in progress and completed tasks list. |
| Infrastructure Notes (workspace) | `~/.../workspace/INFRASTRUCTURE.md` | OpenClaw deployment details (cron config, logs, Docker). Not critters-specific but useful. |

### ⚠️ Common Pitfall: Missing Tasks File

Several agents assumed no tasks file existed because they looked for `TASKS.md` or `tasks.md` in the repository root. The **actual** file lives at:

```
.kiro/specs/critters-game-prototype/tasks.md
```

Always check this location when orienting a new session. It is the definitive source for implementation order.

---

## 🗂️ Repository Structure

```
critters/
├── .kiro/
│   └── specs/critters-game-prototype/
│       └── tasks.md          ← Master task list (hidden .kiro dir)
├── doc/
│   ├── DEPENDENCIES.md
│   ├── HIGH_LEVEL_TASKS.md
│   ├── INITIAL_DIRECTIVES.md
│   ├── REQUIREMENTS.md
│   └── SAVE_SYSTEM_EXTENSION.md
├── src/                      ← Source code modules
├── tst/                      ← Unit and property tests
├── venv/                     ← Virtual environment (gitignored)
├── WORKING_ON.md             ← Current task tracking
├── README.md
└── ARCHITECTURE.md           ← This file (once committed)
```

---

## 📦 Source Module Reference

All source files are in `src/`.

| Module | Description | Key Classes / Functions |
|--------|-------------|--------------------------|
| `main.py` | Core game loop, rendering, input integration, world setup. | `main()`, title screen, HUD, debug display, build/deconstruct handling |
| `entity.py` | Base `Entity` class and `Player` class. | `Entity`, `Player` (movement, interaction, buffs, equipment) |
| `inventory.py` | Inventory management (resource storage). | `Inventory` (add, remove, has) |
| `grid_system.py` | Spatial grid for world organization and collision. | `GridSystem` (world↔grid conversion, occupancy, bounds) |
| `world.py` | Container for all world entities; supports multiple maps. | `World`, `MapData`, portal handling, object management |
| `world_object.py` | Base class for grid-aligned objects with inventories. | `WorldObject` (occupancy, interaction stub) |
| `building.py` | Base class for buildings with cost and placement validation. | `Building` (can\_place, deconstruct) |
| `gathering_hut.py` | Gathering Hut: storage, critter assignment, resource collection. | `GatheringHut` (assign\_critter, find\_resource\_in\_radius, withdraw) |
| `critter.py` | Critter entity with stats, state machine, pathfinding integration. | `Critter`, `CritterState` (IDLE, GATHER, RETURN), stat-based behavior |
| `pathfinding.py` | A* pathfinding on the grid. | `PathfindingSystem` (find\_path, cache) |
| `mating_hut.py` | Mating Hut for critter breeding. | `MatingHut` (breed method) |
| `buff.py` | Buff data class (stat multipliers with duration). | `Buff` (update) |
| `chair.py` | Chair building: applies Rested buff on interaction. | `Chair` |
| `campfire.py` | Campfire building: applies Strength buff on interaction. | `Campfire` |
| `equipment.py` | Equipment tracking in player. | `Equipment` (unlock/equip logic) |
| `crafting_menu.py` | UI for crafting recipes. | `CraftingMenu` (render, craft\_selected) |
| `recipe.py` | Recipe data class. | `Recipe` |
| `recipes.py` | Recipe definitions. | `RECIPES` (list) |
| `berry_bush.py` | Berry bush: renewable food source. | `BerryBush` (interact) |
| `tree.py` | Tree: renewable wood source with regeneration. | `Tree` (respawn timer) |
| `rock.py` | Rock: non-renewable stone source. | `Rock` |
| `stick.py` | Stick: non-renewable plant resource. | `Stick` |
| `grass.py` | Grass: spreads over time, trampling prevents growth. | `Grass` (spread logic) |
| `obstacle.py` | Work obstacle: requires work units to clear. | `Obstacle` (apply work) |
| `input_handler.py` | Keyboard and mouse input processing. | `InputHandler` (movement flags, build toggle, deconstruct mode, hold-to-interact) |
| `build_menu.py` | Build menu UI for selecting and placing buildings. | `BuildMenu` (toggle, building selection, attempt\_placement, mouse clicks) |
| `title_screen.py` | Title screen with New Game/Continue/Quit. | `TitleScreen` |
| `save_system.py` | Serialization and deserialization for game state. | `save\_game`, `load\_game`, `SaveData` |
| `map_data.py` | Map data container with portals and per-map entity lists. | `MapData`, `Portal` |

---

## 🔗 How It All Fits Together

### Core Loop (main.py)

1. **Initialization**: Pygame setup → Title screen → World creation (`World` + `MapData`) → Player creation → Input handler → Build menu → Pathfinding.
2. **Per Frame**:
   - Read input (`InputHandler.handle_events`, `update`, `update_movement`)
   - Handle save/load requests
   - Update player (`Player.update`)
   - Move player with collision (`Player.move` → `GridSystem` occupancy checks)
   - Handle map transitions (`World.handle_map_transition`)
   - Process interactions (loop `input_handler.interact_count` → `Player.interact` → `WorldObject.interact`)
   - Build menu: if mouse click and build mode → `BuildMenu.attempt_placement` (cost validation, placement)
   - Deconstruct mode: if mouse click and `deconstruct_mode` → find building under cursor → `Building.deconstruct`
   - Update critters (`Critter.update` → state machine, pathfinding)
   - Mark trampled cells, decay trample
   - Update world objects (regeneration, grass spread)
   - Render everything (HUD, world, player, critters, menus)

### Entity Relationships

- `World` contains one `MapData` as `current_map`. `MapData` holds lists: `objects`, `critters`, `portals`, `trampled`.
- `GridSystem` is rebuilt from `current_map.objects` via `World._rebuild_grid()`; used for collision queries.
- `Player` has `inventory` (Inventory) and `active_buffs` (list of Buff). Equipment affects gathering speed.
- `Building` extends `WorldObject`; adds `cost` dict and `can_place()` method. Subclasses: `GatheringHut`, `MatingHut`, `Chair`, `Campfire`.
- `GatheringHut` has `assigned_critters` list and `storage` inventory; `find_resource_in_radius()` locates berry bushes within `gathering_radius`.
- `Critter` has stats (`strength`, `speed_stat`, `endurance`), `state` (CritterState), `assigned_hut` reference, and `held_resource`. State machine: IDLE → GATHER → RETURN.
- `PathfindingSystem` uses `GridSystem.is_occupied` for obstacle avoidance; caches paths by `(start, goal)`.

### Interaction Range

- Player uses `interaction_radius = 45.0` pixels.
- `Player.interact()` finds nearest `WorldObject` within radius using circle-circle distance.
- Deconstruction also requires player within interaction radius to target building center.

---

## 🧪 Testing

- Run all tests: `PYTHONPATH=src venv/bin/python -m pytest tst/ -v`
- Current passing: 179 tests (unit + property).
- Property tests use Hypothesis; check for `# Feature: critters-game-prototype, Property {N}: {title}` comments.
- Tests are colocated in `tst/` with the module they test (e.g., `tst/test_critter.py`, `tst/test_world.py`).

---

## 🔧 Common Pitfalls & Gotchas

1. **Tasks file location**: The master task list is `.kiro/specs/critters-game-prototype/tasks.md`, **not** `TASKS.md` or `tasks.md` in the root. Always check `.kiro/`.
2. **GridSystem bounds**: A* pathfinding hangs if `width`/`height` are not set. Ensure bounds are provided when constructing `GridSystem` in tests.
3. **World object registration**: `World.add_object()` registers the object with the grid and sets `obj.world = self`. Forgetting to add to world means no collision/ rendering.
4. **Saving new object types**: When adding a new `WorldObject` subclass, you must:
   - Ensure it is serializable (primitive fields or other serializable objects).
   - Update `SaveData` if needed (often not required if contained in `world.current_map.objects`).
   - Write round-trip tests in `tst/test_save_load.py` to verify preservation.
   - See `docs/SAVE_SYSTEM_EXTENSION.md`.
5. **Movement collision**: `Player.move` uses axis-separate checks with `_would_collide` helper; new obstacles should respect `blocks_movement` flag.
6. **Critter stats bounds**: Stats must stay in [1, 100]. Any modification (breeding, buffs) must clamp.
7. **Hold-to-interact**: Interaction count is computed in `InputHandler.update`; tests that fire interact events should call `update(dt)` appropriately.

---

## 📝 Extension Points

- **New Buildings**: Subclass `Building`. Set `cost`, dimensions, and override `interact()` for special behavior. Add to `BuildMenu.building_classes` and `RECIPES` if craftable.
- **New Resources**: Add to `RESOURCE_COLORS` in `main.py` for HUD; update inventory usage everywhere; ensure recipes and costs use the new key.
- **New Critter States**: Extend `CritterState` enum and update `Critter.update` state machine.
- **Multi-map**: Add `MapData` to `World.maps` and create `Portal` links; ensure portal cells are passable.
- **Save System**: Follow `SAVE_SYSTEM_EXTENSION.md`; implement `to_dict`/`from_dict` if custom; otherwise inclusion in world objects is automatic.

---

## 📚 Quick Reference

- **Task tracking**: `.kiro/specs/critters-game-prototype/tasks.md`
- **Current status**: `WORKING_ON.md`
- **Design notes**: `doc/*.md`
- **Tests**: `tst/test_*.py`
- **Run game**: `PYTHONPATH=src venv/bin/python src/main.py` (or use `make run` if defined)

---

_Keep this document up to date as the codebase evolves._
