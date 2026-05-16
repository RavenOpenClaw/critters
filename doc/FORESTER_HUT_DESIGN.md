# Forester's Hut Design & Implementation Plan

## 1. Overview
The Forester's Hut completes the sustainable forestry cycle by automating the replanting of saplings. Critters assigned here will take saplings from local storage and plant them in valid locations within their radius.

## 2. Building Details: Forester's Hut
*   **Size:** 3x3 grid tile.
*   **Cost:** 15 Wood, 5 Stone.
*   **Storage:** Internal storage for **Saplings only**.
*   **Function:**
    *   Accepts Saplings from the player (Interaction).
    *   Assigned critters look for `ITEM_SAPLING` in the hut's storage.
    *   If they have a sapling, they seek a valid planting location (using `Sapling.can_place_at` logic).
    *   If no saplings are in storage, they idle near the hut.

## 3. Automation Logic
*   **Worker State:** `GATHER` (modified for Forester).
    *   If critter inventory is empty:
        *   Go to Forester's Hut and take 1 Sapling.
    *   If critter has 1 Sapling:
        *   Seek the nearest valid 1x1 tile within radius (20 tiles) that satisfies `Sapling.can_place_at`.
        *   Move to tile and "Interact" (Plant).
*   **Intelligence:** Forester huts can pull saplings from nearby Lumber Mills if they are within a shared radius (Future Refinement, for now manual transfer or specific storage).

## 4. Implementation Phases

### Phase 1: Building & Constants
*   Add `BUILDING_FORESTER_HUT_COST` to `src/constants.py`.
*   Add `ForesterHut` class in `src/forester_hut.py` (inherits from `Building`).
*   Update `BuildMenu` to include the Forester's Hut.

### Phase 2: Forester AI
*   Update `Critter.update` or create a specialized logic branch for Forester workers.
*   Implement `_seek_planting_spot` in `Critter` or `ForesterHut`.
*   Ensure critters transition correctly between Hut (fetching saplings) and World (planting).

### Phase 3: Robustness & UI
*   Update `World.draw_debug` to show Sapling counts in Forester Huts.
*   Add serialization support in `src/save_system.py`.

### Phase 4: Overburdened Penalty (TODO 64b)
*   Implement 50% movement speed penalty in `Critter.get_movement_speed()` if `inventory.get_total_quantity() > carry_capacity`.

## 5. Verification Plan
*   `tst/test_forester.py`:
    *   Verify critter takes sapling from hut.
    *   Verify critter plants sapling at a valid location.
    *   Verify placement constraints are respected by the AI.
    *   Verify speed penalty for overburdened critters.
