# Bug reports

## Overview

This doc describes bugs that the user found when testing (UAT).

Key principles:
- For each bug report, create a new entry in fixes.md
- Carefully consider the state before and after your fix. Prevent regression.
- Test your changes with automated test cases
- Tests must pass before merging

Bug report format:
1. A descriptive title of the format [<ID>] <TITLE>
2. Status - current status of this bug in the code base, (NOT_STARTED, IN_PROGRESS, PENDING_REVIEW, FIXED)
3. Expected - description of expected behavior
4. Actual - description of what actual behavior
5. Reproduce - a procedure to reproduce the bug
6. Desired fix - guidance about what/how to fix

## Reports

### [DLKJSIEQ] Collision between objects and the player seizes movement

Status: FIXED

Expected: As a player, if I'm moving to the right and colide with a world object like a bush, I should stop. While still moving to the right, I should be able to press "down" (the S key) to move diagonally down and to the right. The object prevents the movement to the right due to collision, but should not prevent the movement downwards. In other words, the player slides along the edge of the bush until clear of the collision box.

Actual: When the player collides with a world object, vertical movement is prevented even when colliding from the side, or vice versa. Sliding along an object is not possible as long as the player is holding a key that tries to push the player toward the object. Objects in the world are "sticky" and hold the player until they let go of the movement key that pushes them toward the object.

Reproduce: Start the game. Move toward a world object from the left (pressing right). Collide with the object. Press down or up while still holding down the right key.

Desired fix: Make it so the component of the blocked movement (the movement that would push the player into the collision box of the object) is canceled, but do not cancel the other component of movement.

### [WGFBKAX] Performance degrades over time during gameplay

Status: FIXED

Root cause: Grass was spreading into occupied cells, leading to exponential growth (millions of grass objects). Fix: Added duplicate prevention in `World.add_object` (track `grass_cells`), and improved spread check to use `world.is_cell_free`. After fix, performance remains stable. Fixed in commit 9884ced.

Expected: The game should maintain a stable framerate (~60 FPS) and consistent responsiveness throughout extended play sessions.

Actual: The game becomes progressively slower; FPS drops and input/rendering lag increases the longer the game runs.

Reproduce: Start a new game and play for an extended period (10-30 minutes). Observe FPS counter (enable debug with F3). Note that FPS declines steadily or in steps. Performance does not recover upon saving/loading.

Desired fix: Identify and fix the underlying cause of resource/performance degradation. Potential areas to investigate:
- Pathfinding cache growth (does it invalidate correctly?)
- World object list growth (are new objects being added without old ones being removed?)
- Trampled cells set growing indefinitely?
- Entity count increasing (are critters or objects being duplicated?)
- Memory leaks (e.g., event queues, timers)
- Any per-frame allocations that accumulate

Note: User suggests binary search approach to isolate the cause by disabling subsystems until performance stabilizes.

### [GRASS_SPREAD] Grass spreads into occupied cells causing exponential object count

Status: NOT_STARTED

Expected: Grass should only spread to empty grid cells (no other object occupying that cell). When a grass object attempts to spread, it should check if the target cell is completely free of any world objects (including other grass). This prevents exponential growth from multiple grass objects spawning on the same cell.

Actual: Grass spread check uses `grid.is_occupied(nx, ny)` which only checks for blocking objects (those with `blocks_movement=True`). Since grass itself has `blocks_movement=False`, it does not register in the grid's occupancy map. Therefore, grass can spread onto cells that already contain other grass objects, creating duplicates and leading to millions of grass objects rapidly.

Reproduce: Start game with initial grass spread enabled. Let the game run for a few minutes. Observe that grass count grows exponentially as grass spreads onto already-occupied grass cells.

Desired fix: Replace occupancy check with a check for ANY object in the target cell. Use `world.is_cell_free(nx, ny)` (if available) or iterate over all world objects to see if any occupies the cell. Ensure only one grass object per cell.

### [BERRY_REGROW] Berry bushes only regrow when completely depleted

Status: NOT_STARTED (fix implemented in commit 9884ced but needs verification)

Expected: Berry bushes should gradually regrow berries over time whenever the berry count is below maximum, regardless of whether they are completely depleted or just partially harvested. This creates a more natural and forgiving resource regeneration.

Actual: The original code only started regeneration after the bush became depleted (zero berries). Partially harvested bushes (e.g., 1 out of 3 berries taken) would not regenerate until they were completely empty. This is overly strict and makes resource management less forgiving.

Reproduce: Harvest a berry bush partially (leave at least 1 berry). Observe that the berry count does not increase over time. Only after removing the last berry does the bush enter depletion mode and start respawn timer.

Desired fix: Modify `BerryBush.update()` to always accumulate time when `berry_count < max_berries` and replenish when enough time has passed, regardless of depletion state.

### [RESOURCE_DEPLETION] Sticks and rocks should be removed from world when their inventory is depleted

Status: NOT_STARTED

Expected: When the player harvests all resources from a stick or rock object (i.e., its inventory becomes empty), the object should be removed from the world map. This keeps the world clean and prevents interacting with depleted resources.

Actual: Currently, stick and rock objects remain in the world even after their inventory is empty. The player can still "interact" with them (no effect) and they still appear on the map.

Reproduce: Find a rock or stick pile. Harvest all resources (stone/wood). The object remains visible and interactive prompt still appears, but interaction yields nothing.

Desired fix: After inventory becomes empty, remove the object from the world (call `world.remove_object(obj)`). Could be done in the object's `update()` or after interaction if it empties the inventory.

### [STICK_RESOURCE] Stick objects add "stick" resource, but should add "wood"

Status: NOT_STARTED

Expected: All wooden resources (from trees and stick piles) should contribute to the same "wood" inventory type. "stick" should not be a separate resource type.

Actual: Stick piles currently add "stick" to the player's inventory, while trees add "wood". This creates confusion and two separate resource stacks for essentially the same material.

Reproduce: Harvest a stick pile; observe inventory increases "stick" count. Harvest a tree; observe inventory increases "wood" count.

Desired fix: Change Stick object's inventory to use "wood" instead of "stick". Adjust any tests accordingly. Ensure HUD and UI display only "wood" for both sources.

### [DUPLICATE_HUD] Two inventory displays on screen (top-left and top-right) causing confusion

Status: NOT_STARTED

Expected: There should be a single, clear inventory display. Either the top-left or top-right HUD element should be the sole inventory viewer, not both.

Actual: Both a top-left HUD and a top-right HUD show inventory content. They may be redundant or show different views, which confuses the player about which one reflects the actual inventory.

Reproduce: Start game; observe two separate inventory displays.

Desired fix: Determine which HUD element is intended (likely top-right is the main inventory; top-left might be debug or something else). Remove or hide the duplicate display to have a single source of truth.

### [TREE_REGROW] Trees should respawn wood inventory over time (like berry bushes)

Status: NOT_STARTED

Expected: For prototyping simplicity, trees should automatically regenerate their wood supply after a configurable duration (e.g., 30 seconds) once depleted. This allows continued gameplay without manual tree planting.

Actual: Trees currently do not regenerate wood once harvested to zero. They remain depleted forever unless the player reloads the game or manually adds wood via debug.

Reproduce: Chop a tree until all wood is harvested. Wait arbitrarily long; the tree never regrows wood.

Desired fix: Implement regeneration logic similar to BerryBush: track `depleted` flag, `time_depleted`, and `respawn_duration`. When `time_depleted >= respawn_duration`, replenish wood to `max_wood`.

### [BUFF_STACKING] Chair rested buff and campfire strength buff can be stacked multiple times

Status: NOT_STARTED

Expected: Each buff type should be unique per player. Applying the same buff again should reset its timer to full duration, not stack the effect multiplicatively. Only one `rested` buff and one `strength` buff should be active at a time.

Actual: The buff system allows stacking: sitting on a chair repeatedly applies the `rested` buff each time, causing the movement speed to increase multiplicatively (hyper speed). Similarly, multiple campfires can be added (or the same campfire re-applied?) to stack `strength` buff.

Reproduce: Sit on a chair; note speed. Sit on another chair (or same chair again) while still having the buff; speed increases again. Repeat to get extreme speed. Same for campfire strength.

Desired fix: When adding a buff, check if player already has that buff type. If yes, replace it (or reset its timer) rather than appending a new one. Use a dictionary keyed by buff name in the player's active buffs for easy lookup/update.

### [ICON_COLOR] Berry icon is dark grey instead of red

Status: NOT_STARTED

Expected: The berry icon should be visually red (or at least a distinct reddish color) to match typical berry imagery.

Actual: The berry icon currently renders as dark grey in the inventory HUD.

Reproduce: Open inventory HUD; observe berry icon color.

Desired fix: Adjust berry icon color in the rendering code (likely in `hud.py` or wherever icon colors are defined) to use a red RGB value such as (200, 0, 0) or similar.
