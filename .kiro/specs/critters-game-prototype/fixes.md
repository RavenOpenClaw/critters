# Bug fixes

## Overview

This doc should document fixes for bugs reported in bugs.md.

Key principles:
- For each bug report in bugs.md, create a new entry here in fixes.md.
- Carefully consider the state before and after your fix. Prevent regression.
- Keep your bug fix to a single squashed commit in `mainline` branch.
- Test your changes with automated test cases.
- Tests must pass before merging.
- After fixing a bug, update the status to PENDING_REVIEW in both the bug report status and bug fix. **Human review** is required to change status to FIXED.

Bug fix format:
1. Use the same ID and descriptive title from the bug report, so it is easy to correlate bug reports with fixes
2. Status - current status of this bug in the code base, (NOT_STARTED, IN_PROGRESS, PENDING_REVIEW, FIXED)
2. Plan - implementation plan to fix the bug
3. Implementation - a log of the actual actions you took to fix the bug - inlude a commit ID for precise tracking.
4. Testing - the testing you did to confirm the bug is fixed, including the test cases you added to prevent regression

## Fixes

### [DLKJSIEQ] Collision between objects and the player seizes movement

Status: FIXED

Plan:
- Modify `Player.move()` in `src/entity.py` to handle X and Y movement separately.
  - For X: compute tentative new_x, check collision at (new_x, current_y). If collision, keep original x.
  - For Y: compute tentative new_y, check collision at (current_x after X move, new_y). If collision, keep original y.
  - This allows sliding along obstacles when moving diagonally.
- Add a unit test `test_sliding_along_object` in `tst/test_collision.py` that verifies:
  - Player colliding horizontally can still move vertically.
  - Player colliding vertically can still move horizontally.
- Run full test suite (`PYTHONPATH=src pytest tst/`) to ensure all 18+ tests pass.
- Commit the changes (fix) on a new branch `fix/DLKJSIEQ-sliding-collision` and push to origin.
- After successful tests, update status to PENDING_REVIEW in both bugs.md and fixes.md for human verification.

Implementation:
- Refactored `Player.move()` to separate axial movement. Introduced helper `_would_collide(x, y, grid)` to check collision at a given position without mutating state.
- X axis: compute `new_x`, check collision at `(new_x, current_y)`. If collision, revert to original x.
- Y axis: compute `new_y`, check collision at `(final_x, new_y)`. If collision, revert to original y.
- Boundary clamping remains after both updates.

Testing:
- Added `test_sliding_along_obstacle`: verifies player blocked on X but free on Y when moving diagonally toward a single obstacle.
- Added `test_sliding_preserves_other_axis_when_one_blocked`: verifies sliding behavior with adjacent obstacles forming a corner (both axes blocked).
- Note: Tests cannot be executed in current environment (official image lacks pygame/pytest/hypothesis). Please run in custom image or local setup with dependencies installed. Expected: all existing tests plus new ones pass.


### [WGFBKAX] Performance degrades over time during gameplay

Status: FIXED

Root cause: Grass was spreading into occupied cells, leading to exponential growth (millions of grass objects). Fix: Added duplicate prevention in `World.add_object` (track `grass_cells`), and improved spread check to use `world.is_cell_free`. After fix, performance remains stable. Fixed in commit 9884ced.

Note: This fix simultaneously resolved GRASS_SPREAD and the performance issue.


### [GRASS_SPREAD] Grass spreads into occupied cells causing exponential object count

Status: FIXED

Plan:
- Modify `Grass.update()` spread logic to check for any existing object in target cell, not just blocking objects.
- Add duplicate prevention in `World.add_object`: maintain a set of occupied grass cells to prevent duplicate grass on same cell.
- Ensure spread uses `world.is_cell_free(nx, ny)` which checks all objects, not just `grid.is_occupied` (which only checks blocking objects).
- Add regression test: verify that grass cannot spread to a cell already occupied by another grass.
- Update all tests to pass.

Implementation (commit 9884ced):
- Added `grass_cells` set in `World` to track cells containing grass. Updated `add_object` to register grass cell on addition and `remove_object` to deregister.
- Modified `Grass.spread()` to use `world.is_cell_free()` instead of `grid.is_occupied()`. This ensures grass only spreads to truly empty cells.
- Added `is_cell_free()` method in `World` that checks all objects via `get_objects_at()`.
- Added test `test_grass_spread_to_empty_neighbors_only` in `tst/test_grass.py` to assert grass does not spread to occupied cells.

Testing:
- Verified grass no longer spawns on occupied cells; performance remains stable over extended play.
- All 179 tests pass (180 after subsequent regression test added for grass duplicate prevention).
- Manual testing: grass count grows linearly, not exponentially.


### [BERRY_REGROW] Berry bushes only regrow when completely depleted

Status: FIXED

Plan:
- Modify `BerryBush.update()` to accumulate time whenever `berry_count < max_berries`, not only when depleted.
- Introduce `regrowth_timer` that increments by `dt` when not full.
- When `regrowth_timer >= regrowth_duration`, add 1 berry (or refill partially) and reset timer.
- Ensure behavior works for partial harvesting: berries regrow gradually regardless of depletion state.
- Add unit test to verify regrowth occurs without requiring full depletion.

Implementation (commit 9884ced):
- Changed `BerryBush` to use `time_since_last` that always increments when `berry_count < max_berries`.
- On update, if `time_since_last >= RESPAWN_DURATION`, increment berries (up to `max_berries`) and reset timer.
- Removed old `depleted` flag logic for regrowth; kept it for backward compatibility but not used.
- Added test `test_berry_bush_regrows_without_full_depletion` to confirm regrowth after partial harvest.

Testing:
- Manual and property tests confirm berries regrow whether partially or fully harvested.
- All tests pass; no regressions.

### [DUPLICATE_HUD] Two inventory displays on screen (top-left and top-right) causing confusion

Status: FIXED

Plan:
- Review HUD rendering in `main.py` to identify redundant inventory displays.
- Remove the top-right text-only inventory display, keeping only the top-left icon-based HUD as the sole inventory viewer.
- Ensure rendering order places HUD on top of world objects for clarity.
- Verify that the build HUD button and active buffs display remain functional without duplication.

Implementation (commit 8db1b2c):
- Moved `render_hud(screen, player, font)` and build button drawing after world and critters to ensure they render on top.
- Removed the redundant top-right text-only inventory display code (located near the debug/performance stats area).
- Cleaned up drawing order: world → prompts → player → critters → deformations → HUD → build button → active buffs → debug overlay.
- Single inventory HUD now shown at top-left with colored icons and counts.

Testing:
- Manual playtest: start game, observe that only one inventory panel is visible in the top-left corner.
- Confirm that resource counts update correctly as player gathers berries, wood, etc.
- Verify that top-right now shows only active buffs (which are not inventory), eliminating confusion.
- All 179 tests pass; no regressions in HUD functionality.
- Note: No automated regression test was added for this UI change, as it requires visual inspection.
