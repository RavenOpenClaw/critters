# Wood & Forestry System Design

## 1. Overview
The Wood & Forestry system introduces a complete lifecycle for trees, shifting from infinite nodes to a renewable resource management loop. Players and critters can now chop down trees, collect saplings, and replant them to create sustainable tree farms.

## 2. Tree Lifecycle

### Fully Grown Tree
*   **Size:** 1x1 grid tile.
*   **Capacity:** Contains a finite amount of Wood.
*   **Harvesting:** Standard interaction duration.
*   **Depletion:** When the inventory reaches 0:
    *   The harvester (Player or Critter) receives a **Bonus** of 3-5 Wood.
    *   There is a **80% chance for 1 Sapling** and a **20% chance for 2 Saplings**.
    *   The Tree object is **removed** from the world.

### Sapling
*   **Resource:** Saplings are items in the inventory.
*   **Planting:** "Built" from the Build Menu at the cost of 1 Sapling.
*   **Size:** 1x1 grid tile.
*   **Placement Requirement:** Must have 8 empty squares surrounding it (horizontal, vertical, diagonal).
*   **Growth:**
    *   Randomized timer between **2 and 3 minutes** (120-180 seconds).
    *   Debug mode displays the countdown timer.
    *   On completion, the Sapling is replaced by a Fully Grown Tree.

## 3. Automation: The Lumber Mill
*   **Function:** Dedicated hub for wood gathering, similar to the Gathering Hut.
*   **Workers:** Assigned critters seek out the nearest non-depleted Trees within radius.
*   **Chapping:** Critters follow the same depletion logic as players (bonus wood and saplings).
*   **Overburdening:** If a critter receives bonus wood that exceeds their capacity, they become "Overburdened." 
    *   *Note:* Currently, there is no movement penalty for overburdening, but this is a future TODO.
*   **Interaction:** Players can withdraw stored wood from the Lumber Mill.

## 4. Implementation Phases

### Phase 1: UI & Altar Fixes
*   Update `src/constants.py` with `BUILDING_RELEASE_ALTAR_COST = {'stone': 15}`.
*   Remove Release button from `src/critter_inspector.py`.
*   Unbind deconstruction from range in `src/game_engine.py`.

### Phase 2: Tree Lifecycle & Saplings
*   Refactor `Tree` class (1x1 size, finite wood, deletion drops).
*   Create `Sapling` class (1x1 size, growth timer, tree replacement).
*   Add `Sapling` to constants and HUD.

### Phase 3: The Lumber Mill
*   Create `LumberMill` building class.
*   Update `Critter` and `LumberMill` logic to handle wood gathering and overburdening.
*   Add `LumberMill` to Build Menu.

### Phase 4: Debug & Testing
*   Implement inventory overlays for Huts/Mills in `World.draw_debug`.
*   Create and run `tst/test_forestry.py`.

## 5. Future Roadmap (TODO)
*   Building for automated sapling planting.
*   Movement speed penalty for "Overburdened" critters.
