# Critters UAT/QA Checklist

This checklist covers manual testing for all implemented features. Use it to verify the prototype is functioning correctly and to catch regressions.

**How to use:** Mark items as ✅ when verified. Perform in order for a complete playthrough, or cherry-pick areas after changes.

---

## Preflight

- [ ] Game launches and displays title screen (800x600 window)
- [ ] Title screen shows "New Game" and "Continue" buttons
- [ ] Continue button is disabled/hidden if no save exists
- [ ] Quit button exits cleanly

---

## New Game Start

- [ ] Click "New Game" → world loads
- [ ] Player (blue circle) appears centered
- [ ] HUD displays at top-left (Food: X, etc.)
- [ ] Build button appears at bottom-left
- [ ] Inventory starts empty (or only default items if any)
- [ ] Debug overlay (F3) shows FPS, player position, counts
- [ ] Interaction radius (green circle) visible when debug on

---

## Movement & Collision

- [ ] WASD moves player smoothly (not grid-aligned)
- [ ] Player cannot move through berry bushes (green squares)
- [ ] Player cannot move through trees (2x2), rocks (1x1), sticks (1x1)
- [ ] Player collides with buildings (Gathering Hut 3x3, etc.)
- [ ] Movement respects window boundaries
- [ ] Sliding collision: moving diagonally against obstacle slides along it

---

## Resource Gathering

- [ ] Approach a berry bush (green square) within interaction radius
- [ ] Prompt appears: "Press E to pick berry"
- [ ] Press E once → Food count increases by 1, bush inventory decreases by 1
- [ ] Hold E → auto-repeat gathering (multiple berries per hold)
- [ ] Bush disappears when berries deplete? (Check: does it have regeneration?)
- [ ] Find a tree (2x2 brown area) → "Press E to chop wood"
- [ ] Chop wood → Wood count increases, tree wood decreases
- [ ] Tree shows depletion? (Does it regenerate after timer?)
- [ ] Rock (gray 1x1) → "Press E to mine stone"
- [ ] Mine stone → Stone count increases, rock stone decreases (rock is non-renewable)
- [ ] Stick (tan 1x1) → "Press E to collect stick"
- [ ] Collect stick → Plant count increases, stick count decreases (non-renewable)

---

## Building System

### Build Menu

- [ ] Press B → build menu appears with building buttons
- [ ] Build menu shows: Gathering Hut (G), Chair (C?), Campfire (F?) – check actual keys
- [ ] Click "Build" button at bottom-left → toggles build menu
- [ ] Build menu buttons highlight on hover and selection

### Placement

- [ ] Select Gathering Hut; cost displayed (check in build menu?)
- [ ] Insufficient resources → click placement shows error message
- [ ] Sufficient resources → click on valid grid cell places hut
- [ ] Cannot place overlapping existing objects (collision enforced)
- [ ] Cannot place on grass? (Check: does grass block? Should be walkable)
- [ ] Placed hut appears as a 3x3 structure; unassigned critters don't spawn automatically in new game (only initial ones)

---

## Critters & AI

### Initial Setup (New Game)

- [ ] New game spawns a Gathering Hut and 3 critters (red circles)
- [ ] Critters start assigned to hut (check via debug? or observe behavior)
- [ ] Critters show state label above head: "IDLE" (gray)

### Critter Behavior

- [ ] IDLE critters stay near hut; after some time transition to GATHER (green label)
- [ ] GATHER critters move toward a resource (berry bush/tree/rock) within gathering radius
- [ ] GATHER critters label changes to "GATHER"
- [ ] Critter reaches resource → collects one unit → transitions to RETURN (blue label)
- [ ] RETURN critters pathfind back to hut
- [ ] Critter arrives at hut → deposits resource into hut storage → returns to IDLE
- [ ] Hut storage updates (interact with hut to withdraw to see)
- [ ] Critters can work through obstacles using pathfinding (detour around walls)

### Stats & Buffs

- [ ] Critters have stats (not directly visible, but equipment/gathering speed hints?)
- [ ] Chair and Campfire buffs affect player, not critters (check design)
- [ ] Well-fed buff applies when? (Maybe from food? Check implementation; not in current tasks)

---

## Breeding (Mating Hut)

- [ ] Build a Mating Hut (2x2) with required resources (see recipe/cost)
- [ ] Assign at least 2 critters to Mating Hut (how? via build menu? Actually assignment pattern: likely interact with hut to assign nearby critters? Check implementation)
- [ ] Mechanism to trigger breeding: maybe interact with hut? Look at MatingHut implementation
- [ ] After breeding, offspring critter appears at hut center
- [ ] Offspring stats are average of parents ± mutation (can't see directly, but new critter appears)
- [ ] Offspring starts in IDLE state

---

## Equipment & Crafting

### Crafting Menu

- [ ] Press R → crafting menu opens
- [ ] Shows list of recipes with costs
- [ ] Select recipe via number key (1-9)
- [ ] Insufficient resources → error message
- [ ] Successful craft → resources deducted, equipment unlocked (if applicable)
- [ ] Some equipment may be equippable? Check if player has equip UI

---

## Multi-Map World

- [ ] Travel to map edge (right/bottom/left/top depending on portal placement)
- [ ] Loading message? Actually seamless transition
- [ ] Player appears on adjacent map
- [ ] Objects/critters on previous map persist when returning
- [ ] Map boundary should be visible or marked? Check portal implementation

---

## Save/Load

- [ ] Press F5 → "Game saved." message appears (console)
- [ ] Save file created at `saves/save.json`
- [ ] Make changes: move player, gather resources, place building, assign critters
- [ ] Press F6 → "Game loaded." message appears
- [ ] Loaded state matches saved state exactly:
  - Player position restored
  - Inventory counts restored
  - Buildings and world objects restored
  - Critter positions and states restored?
  - Active buffs restored?
- [ ] Loading a non-existent or corrupted save falls back to new game? (Check error handling)

---

## Deconstruction (New)

- [ ] Press X → deconstruction mode toggles on
- [ ] HUD indicator appears: "Deconstruction Mode (X to exit)" at bottom-right
- [ ] Hover over a building (any building) → highlight/outline? (Current implementation: no hover visual, just click)
- [ ] Click on a building within interaction radius → building removed
- [ ] Player inventory receives refund: 50% of building cost rounded up
- [ ] If building had assigned critters (e.g., Gathering Hut), they become unassigned (check via UI or behavior)
- [ ] Press X again → deconstruction mode off, indicator disappears
- [ ] Cannot deconstruct non-buildings (trees, bushes, etc.) – click does nothing
- [ ] Cannot deconstruct from out of range – click does nothing

---

## UI & HUD

- [ ] Resource HUD (top-left) shows icons and counts for each resource in player inventory
- [ ] Adding/removing resources updates HUD in real-time
- [ ] Buff display (top-right) shows active buffs with remaining time
- [ ] Debug overlay (F3) shows:
  - FPS
  - Player coordinates
  - Critter count, building count
  - Entity count and trampled cell count
  - Interaction radius circle
- [ ] Build menu overlay appears above world; toggles with B or Build button
- [ ] Crafting menu overlay toggles with R

---

## Regression & Edge Cases

- [ ] Rapidly toggle build/deconstruct modes – no crashes
- [ ] Place building exactly on map boundary – works or correctly rejected?
- [ ] Deconstruct a building that costs nothing – removes without error
- [ ] Save immediately after deconstruction – load restores removed building (and refunds not re-refunded)
- [ ] Load game while in deconstruction mode – mode state resets? (probably not saved)
- [ ] Pathfinding with many obstacles: A* completes quickly, no hangs (ensure grid bounds set)
- [ ] Grass spreading: over time, grass creates new patches in empty adjacent cells
- [ ] Trampling: player walking repeatedly over a cell prevents grass growth; effect decays over time
- [ ] Obstacle work units: assign critters to work obstacle; work units decrease; obstacle removed when zero
- [ ] Tree regeneration: after depleting a tree, it regrows after respawn_duration

---

## Performance & Stability

- [ ] Game runs at ~60 FPS with 3+ critters and several objects
- [ ] No memory leaks over extended play (monitor if possible)
- [ ] All menus open/close smoothly
- [ ] No crashes when clicking rapidly or pressing keys repeatedly
- [ ] Holding E for extended period produces steady auto-interactions

---

## Documentation & Build

- [ ] `make test` runs all 179 tests and passes
- [ ] `python src/main.py` starts the game from repo root
- [ ] No import errors or missing module issues

---

**Notes:**
