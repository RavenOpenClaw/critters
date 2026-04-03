# Deconstruction Feature Design

## Overview
Allows players to remove buildings they no longer need and recover a portion of the resources invested. Adds strategic resource management and base planning.

## Core Mechanics

### Deconstruction Mode
- Toggle with `X` key (separate from build menu)
- Visual indicator: Buildings highlight with a distinct outline when hovered (e.g., bright yellow or cyan)
- Only buildings can be deconstructed (not bushes, trees, rocks, obstacles, etc.)

### Deconstruction Process
1. Player presses `X` to enter deconstruction mode (toggle on/off)
2. When mode active:
   - Build menu (if open) hides or shows a deconstruction panel
   - Mouse hover over a building shows highlight and potential refund preview
3. Click on a building within interaction range:
   - Check: Building must be a `Building` subclass
   - Check: Player must be within interaction radius (same as `interact`)
   - Calculate refund: `ceil(0.5 * cost)` for each resource
   - Award resources to player inventory
   - Unassign all critters assigned to the building (set `assigned_critters.clear()`)
   - Remove building from world
   - Play a sound/effect (optional)

### Refund Rate
- 50% of building resource cost, rounded up (so at least 1 of each resource type)

### Edge Cases
- Building has no cost? Treat cost as empty dict → refund none, but still allowed (free removal)
- Cancel deconstruction: press `X` again to exit mode
- Cannot deconstruct while build menu is in placement mode? Actually, deconstruction is global, independent of build menu. Build menu only for building placement.

## User Interface

### HUD
- Show current mode in top-right: "Mode: BUILD" or "Mode: DECONSTRUCT"
- When deconstruct mode active, show instructions: "Click a building to deconstruct"

### Build Menu
- The build menu (`B` toggle) is for building selection and placement.
- Deconstruction mode (`X`) is orthogonal; both can be active but placement is disabled while deconstruction mode is on.

## Input Mapping

| Key | Action |
|-----|--------|
| B | Toggle build menu |
| X | Toggle deconstruction mode |
| E | Interact (unchanged) |

(Mouse click handling in main.py: if deconstruct mode active and clicked on world coordinate, attempt deconstruct instead of place)

## Implementation Plan

1. **BuildMenu changes** (`src/build_menu.py`):
   - Add `deconstruct_mode` boolean flag
   - Modify render to show mode indicator (maybe text overlay or change color scheme when deconstruct active)
   - Optionally hide build menu UI when deconstruct mode active (cleaner), or show a decon mode banner

2. **Building base class** (`src/building.py`):
   - Add `deconstruct(world, player)` method:
     - Calculate refund: `ceil(cost * 0.5)` for each resource
     - Add refunded resources to `player.inventory`
     - Unassign critters: for each critter in `self.assigned_critters`, set `critter.assigned_hut = None`
     - Call `world.remove_object(self)`
   - Keep method generic; works for any `Building` subclass.

3. **main.py integration**:
   - In `InputHandler`, add `deconstruct_mode` flag, set on `K_x` toggle
   - In main loop:
     - If `deconstruct_mode` is True and mouse clicked:
       - Convert mouse position to grid coordinates
       - Find any building at that grid cell (via `world.get_objects_at(grid_x, grid_y)` or iterate)
       - Check player is within interaction range (circle-circle: player pos to building center)
       - Call `building.deconstruct(world, player)`
       - Set `mouse_clicked = False` to avoid build placement
   - If build menu placement mode active, placement should be disabled when deconstruct mode is on? Simpler: allow both flags but in main loop, deconstruct takes precedence; if deconstruct mode, ignore build placement clicks.

4. **Tests** (`tst/test_deconstruction.py`):
   - Unit test: `Building.deconstruct()` refunds half cost correctly (round up)
   - Unit test: deconstruction removes building from world
   - Unit test: deconstruction unassigns all critters
   - Unit test: deconstruct fails if player out of range
   - Unit test: deconstruct works on any Building subclass (GatheringHut, Chair, Campfire)
   - Property test: deconstruct + rebuild costs net zero over infinite cycles? Not necessary.

5. **Existing test updates**:
   - If any tests assume build menu only uses B key, they may need adjustment for X key toggles. BuildMenu tests should still pass as they focus on build mode; the deconstruct flag shouldn't break existing behavior.

## Notes
- The existing `interact` method already handles Building interaction (e.g., GatheringHut withdraw). That's separate from deconstruction. We'll keep that functionality intact.
- Deconstruction mode does not interfere with normal interaction (E key).
- The feature aligns with the project's philosophy of emergent strategy and player agency.

## Success Criteria
- Toggle deconstruction mode with X
- Click on a building to remove it and get refund
- All tests pass (including new deconstruction tests and existing suite)
- No regressions in build menu or interaction systems
