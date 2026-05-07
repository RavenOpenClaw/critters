# Implementation Plan: Critters Game Prototype

## Overview

This implementation plan follows a phased approach starting with minimal graphics (blue circle for player, red circles for critters, green squares for bushes, light gray background) and building incrementally with tests. The implementation uses Python 3.10+ with Pygame for rendering and Hypothesis for property-based testing.

## Task List

### Phased Implementation

- [x] 1. Basic Pygame window and player movement
- [x] 2. Grid system for world objects
- [x] 3. Simple resource gathering (Berry Bushes)
- [x] 4. Critter state machine (IDLE, GATHER, RETURN)
- [x] 5. Pathfinding (A*) for critters
- [x] 6. Save/Load system (JSON)
- [x] 7. Interaction UI (hover tooltips, progress bars)
- [x] 8. Resource inventory system (Player and Huts)
- [x] 9. Implement building system and Gathering Hut
- [x] 10. Stat-based gathering and movement
- [x] 11. Breeding system (Mating Hut)
- [x] 12. Camera system for large worlds
- [x] 13. Multiple map system and map transitions
- [x] 14. Performance optimizations (quadtree or spatial partitioning) - _Partial (Grid-based optimizations)_
- [x] 15. Sound effects and music - _Delayed (Focus on core mechanics)_
- [x] 16. Polished graphics and animations - _Partial (Procedural wobble/jiggle)_

### Recent Task Tracking

- [x] 56. Stat-based Critter Coloring (RGB)
  - [x] Critter color calculated as `(STR*2.55, SPD*2.55, END*2.55)`.
  - [x] High STR critters appear Red.
  - [x] High SPD critters appear Green.
  - [x] High END critters appear Blue.
  - [x] Pure White for max stats, Grey for balanced mid-stats.

### Task 57: Strength-based Obstacle Requirements
**Priority**: Medium
**Status**: COMPLETED (2026-05-01)

**Description**:
Implement "Minimum Strength Requirements" for clearing obstacles, allowing groups of critters to work together.

**Acceptance Criteria**:
- [x] Obstacles can be assigned a `min_strength` requirement.
- [x] Work progress only advances if `sum(assigned_critter_str) >= min_strength`.
- [x] STR determines "work units" applied per cycle once requirement is met.
- [x] Visual feedback if requirement is not met (e.g., progress bar stays grey/locked).

### Task 58: Implement Crafting Menu HUD Button
**Priority**: Low
**Status**: COMPLETED (2026-04-26)

Implementation:
- Added `HUD_CRAFT_BUTTON` to constants.
- Initialized `hud_craft_button_rect` and implemented click/render logic in `main.py`.
- Toggles the crafting menu correctly.

### Task 59: Advanced Probabilistic Breeding System
**Priority**: High
**Status**: COMPLETED (2026-05-01)

**Description**:
Implement a genetic inheritance system (40/40/20) and a skewed mutation model.

**Acceptance Criteria**:
- [x] Implement 40% inheritance from Parent A, 40% from Parent B, 20% Wildcard per stat.
- [x] Implement "Wildcard" distribution: 80% Log-Normal (mode 15), 20% Uniform (1-100).
- [x] Apply ±10% final mutation to all resulting stats.
- [x] All breeding parameters (weights, log-normal params, mutation range) centralized in `constants.py`.
- [x] Create `make breed` target that runs a 1000-cycle simulation and prints a report.

### Task 60: Critter Recycling (Release & Candies)
**Priority**: Medium
**Status**: COMPLETED (2026-05-01)

**Description**:
Allow releasing critters to get "Stat Candies" that permanently buff other critters.

**Acceptance Criteria**:
- [x] Add "Release" button to Critter Inspector.
- [x] Releasing a critter removes it and adds a candy to inventory (based on its highest stat).
- [x] Add Strength/Speed/Endurance Candy items to inventory/constants.
- [x] Implement "Use" logic: clicking a candy in inventory/inspector applies +1 to that stat on the selected critter.
- [x] Stat boosts are permanent and hereditary.

### Task 61: Dedicated Release Building (Release Altar)
**Priority**: Medium
**Status**: COMPLETED (2026-05-01)

**Description**:
Create a dedicated 2x2 building that formalizes the critter-to-candy conversion.

**Acceptance Criteria**:
- [x] New building type `ReleaseBuilding` (2x2, black square).
- [x] Added to Build Menu (Cost: 10 Wood, 10 Stone).
- [x] Critters can be assigned to it via Right-Click or Player Interaction.
- [x] Assigned critters are instantly "released" into Stat Candies based on their highest stat.
- [x] Visual feedback: Message "Critter released at Altar. Received [Stat] Candy."

### Task 62: MatingHut Inspector and Enhanced Critter Stats
**Priority**: Medium
**Status**: COMPLETED (2026-05-01)

**Description**:
Enhance critter stat visibility with a dual-column MatingHut inspector and color-coded stats in the Critter inspector.

**Acceptance Criteria**:
- [x] Critter Inspector shows "Stat Total" (STR + SPD + END).
- [x] Critter Inspector color-codes stat labels: STR (Red), SPD (Green), END (Blue).
- [x] Implement MatingHut Inspector:
    - [x] Displays info for both assigned parents in two columns.
    - [x] Shows individual stats and stat totals per parent.
    - [x] Displays calculated average stats of the two parents below the columns.
- [x] MatingHut Inspector updates dynamically when critters are assigned/evicted.

### Task 63: Click-and-Drag Multi-Select Selection Square
**Priority**: High
**Status**: NOT_STARTED

**Description**:
Allow mass management of critters using a selection marquee.

**Acceptance Criteria**:
- [ ] Click and drag on empty ground to draw a selection rectangle.
- [ ] All critters inside the rectangle become "selected".
- [ ] Multi-select Inspector appears:
    - [ ] Shows count of selected critters.
    - [ ] Shows average STR, SPD, END.
    - [ ] "Follow" button makes all selected critters follow (no hard limit).
- [ ] Right-clicking a building with multiple critters selected assigns as many as possible to that building (FIFO if full).

## Technical Notes

- The project uses `pygame` for graphics and input.
- Testing is done via `pytest` and `hypothesis`.
- All code should be committed to feature branches and merged after tests pass
- The phased approach ensures basic functionality works before adding complexity
- Graphics start minimal (circles and squares) to focus on core mechanics first
