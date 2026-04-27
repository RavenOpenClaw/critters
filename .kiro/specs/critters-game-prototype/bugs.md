### [GFXCAMP] Campfire and Chair buildings lack visible graphics

Status: FIXED

Fix commit: `1f0e683` (along with other GFX fixes integrated in mainline)

Expected: Campfires should be rendered as a visible red graphic; chairs should be rendered as a visible brown graphic. These buildings should be easily distinguishable on the map.

Actual: Campfires and chairs have no graphic (invisible or placeholder). The player cannot see them in the world.

Reproduce:
- Place a Campfire or Chair using the build menu.
- Observe that no visible shape or color appears at the building location.

Desired fix:
- Assign distinct colors: Campfire = red; Chair = brown.
- Update rendering code in `main.py` or building-specific render methods to draw these buildings with the appropriate fill color and possibly a simple shape (e.g., campfire as 2x2 red square, chair as 3x2 brown rectangle).
- Ensure they appear above grass but below HUD elements.

---

### [DCNIL] Deconstruct mode fails to remove buildings on mouse click

Status: FIXED

Expected: When deconstruct mode is active (X key), clicking on a building within interaction range should deconstruct it, refund half the cost, and remove it from the world.

Actual: Clicking in deconstruct mode does nothing; the building remains.

Reproduce:
1. Place a building (e.g., GatheringHut).
2. Press X to enter deconstruct mode (HUD indicator shows).
3. Ensure player is within interaction radius of the building.
4. Left-click on the building.
5. Observe: building is not removed, no refund, no feedback.

Desired fix:
- Verify the deconstruction click handling in `src/main.py` (around lines 348-360) correctly identifies building under mouse and checks range.
- Ensure the building's `deconstruct` method is called and that `world.remove_object` is invoked.
- Add visual feedback (optional) like a highlight or message when deconstruction succeeds.
- Add tests for deconstruction success and failure cases (out of range, non-building objects).

---

### [GFXMATING] MatingHut lacks a visible graphic

Status: FIXED

Expected: MatingHut should be rendered as a pink building (2x2) to distinguish it from other structures.

Actual: MatingHut is either invisible or uses a default color that doesn't match the design.

Reproduce:
- Build a MatingHut.
- Observe it does not appear as pink on the map.

Desired fix:
- In the MatingHut rendering path (either in `main.py` building rendering loop or MatingHut-specific render method), set a pink fill color (e.g., (255, 105, 180) or similar) and ensure it draws with the correct dimensions (2x2).
- Update any build menu button color to reflect pink for consistency.

---

### [STATVAR] Critter stats variation: create weak (25/25/25), strong (75/75/75), and average (50/50/50) critters

Status: FIXED

**Plan:**
- Modify breeding in `MatingHut._breed` to produce offspring with discrete stat tiers instead of continuous distribution with mutation.
- Offspring stats should be exactly one of: weak (25,25,25), average (50,50,50), strong (75,75,75).
- Tier inheritance rule: if both parents share the same tier, offspring inherits that tier; if parents differ, offspring is average.
- Remove random mutation that previously caused drift.
- Update tests: replace old average+mutation test with tier inheritance tests; add property test to assert offspring stats ∈ {25,50,75}.

Implementation (commit 0adb9db):
- Added tier determination helper: average of three stats maps to tier 25 (<37.5), 50 (37.5-62.5), or 75 (≥62.5).
- Set offspring strength, speed_stat, endurance uniformly to the computed `offspring_tier`.
- Removed the previous random mutation logic entirely.
- Updated `src/mating_hut.py` accordingly.

**Implementation:**


**Testing:**
- Added `test_offspring_stats_are_parent_average_plus_mutation` with table-driven cases covering same-tier, cross-tier, and edge values.
- Added Hypothesis property test `test_offspring_stats_always_within_bounds` generating random parent stats; asserts each offspring stat is exactly 25, 50, or 75.
- Updated existing test that expected mutation to reflect new deterministic behavior.
- All 225 tests pass after the change.
- Manual verification: breeding two weak critters produces weak offspring; strong+strong produces strong; mixed pairs produce average.


Expected: The game should include at least three critters with distinct stat profiles to demonstrate variability: one weak (25 strength, speed, endurance), one strong (75 each), and one average (50 each).

Actual (pre-fix): All critters previously started with uniform stats (50/50/50 by default) and breeding used continuous distribution with mutation, producing non-discrete values.

Fix implemented (commit 0adb9db):
- Modified `MatingHut._breed` to enforce tier-based inheritance:
  - Determine tier from average of parent stats: weak (<37.5), average (37.5-62.5), strong (≥62.5)
  - If both parents share the same tier, offspring inherits that tier.
  - If parents have different tiers, offspring becomes average (50).
  - Offspring stats are uniform across all three attributes.
- Removed random mutation to prevent drift from discrete tiers.
- Added comprehensive tests: `test_offspring_stats_are_parent_average_plus_mutation` with table-driven cases and property test `test_offspring_stats_always_within_bounds` using Hypothesis to assert all offspring stats ∈ {25,50,75}.
- Verified: All 225 tests pass.

Result: Breeding now reliably produces offspring in one of three discrete tiers (weak, average, strong), matching the intended variability.

---

### [TRAMPDMG] Grass trampling damage applies every frame while standing, should only apply on first entry

Status: FIXED

Expected: When an entity (player or critter) moves onto a grass cell, that cell's grass condition should decrease once (by `trample_decay`, e.g., 5). Further updates while still standing on that cell should not cause additional damage. Damage should only occur when the entity first enters the cell (i.e., on transition from a different cell).

Actual: The code likely calls `World.mark_trampled` every update for any entity currently occupying a grass cell, causing rapid degradation as long as the entity remains there.

Reproduce:
- Find a grass cell.
- Move the player onto it and stand still.
- Observe the grass condition dropping continuously frame-by-frame until it disappears quickly (within a second).
- Expected: condition should drop once on entry, then stabilize while the player remains there.

Desired fix:
- Track which cells have already been trampled by a given entity in the current frame or since last entry. One approach: maintain a set of recently trampled cells per entity or globally, and only call `mark_trampled` when an entity moves into a new grass cell (i.e., its grid coordinate changes).
- Alternatively, modify `World.update` or entity movement code to mark trampled only when an entity's position changes to a new cell that hasn't been trampled by that entity recently.
- Ensure the fix preserves the intended mechanic: repeated traffic over time (multiple entries) compounds damage, but idling on a cell does not.

---

### [BUFFNAME] Campfire buff should be called "Warm" instead of "Strength"

Status: FIXED

Expected: The buff granted by the Campfire should display as "Warm" in the active buffs UI and internal labeling, to better reflect the thematic benefit (being warm by the fire).

Actual: The Campfire currently applies a buff named "Strength" (with a 2x gather multiplier). This name is misleading; the campfire should convey warmth.

Reproduce:
- Interact with or stand near a Campfire (depending on implementation).
- Observe the active buffs display shows "Strength".

Desired fix:
- Change the buff name from "Strength" to "Warm" in the Campfire's `interact` method (and any aura-based application in `main.py` if present).
- Update any tests that reference the buff name.
- Ensure the render of active buffs shows "Warm".
- No change to the actual multiplier effect (still 2x gather during campfire proximity).

---

### [GFXMISSING_METHOD] MatingHut missing find_resource_in_radius and can_gather causing crash when critter assigned

Status: FIXED

Expected: When a critter assigned to a MatingHut enters GATHER state or checks for gathering support while IDLE, it should not crash. MatingHut is not meant to provide gather resources, so it should handle these calls gracefully (e.g., returning None or False).

Actual: Crash with `AttributeError: 'MatingHut' object has no attribute 'find_resource_in_radius'` or `AttributeError: 'MatingHut' object has no attribute 'can_gather'`.

Fix implemented:
- Added a default `can_gather()` method to the `Building` base class in `src/building.py` that returns `False`.
- Added a default `find_resource_in_radius()` method (already present but now more robustly inherited) to the `Building` base class that returns `None`.
- These changes ensure that all buildings support these queries by default, and critters assigned to non-gathering buildings like `MatingHut` will correctly fallback to IDLE state.
- Also cleaned up `src/critter.py` by removing a duplicate definition of `_is_adjacent_to_hut`.

Testing:
- Added `test_mating_hut_assigned_critter_idle_safety` to `tst/test_critter.py` to specifically test the `_update_idle` transition without crash.
- Verified that all breeding and critter tests pass (53/53).

---

---

### [FOLLOWCAP] Increase maximum following critters from 1 to 2

Status: FIXED

Expected: The player should be able to have up to 2 critters following simultaneously. This enables carrying two critters to the MatingHut for breeding in a single trip.

Actual: Currently only one critter can follow at a time (exclusive following enforced by `start_follow` stopping any existing follower).

Reproduce:
- Select a critter and press the Follow button in the inspector.
- The critter begins following.
- Select another critter and press Follow. The first critter stops following (only one allowed).

Desired fix:
- Modify the following system to maintain a list of following critters (capacity 2).
- Update `start_follow` to add to the list without automatically stopping others, but enforce a maximum of 2.
- Update `stop_follow` to remove from the list.
- Update exclusive logic: when assigning a following critter to a building via interaction, only assign one (maybe the first or the one that was selected). Or allow assignment of any following critter.
- Update CritterInspector button to reflect the following state appropriately (maybe per-critter toggle still works).
- Ensure assignment interaction still works: when player has following critters and presses E near a hut, assign one of them (perhaps the one selected in inspector, or the most recent). Clarify intended UX; likely the inspector selection should determine which critter gets assigned.
- Update any code that assumes a single `player.following_critter` to instead use a list `player.following_critters` and iterate/handle accordingly.
- Add tests for multiple following behavior and assignment from multiple followers.

---

### [INTERACTCLR] Critter interaction via mouse and E key should work consistently; remove distance restriction for mouse clicks

Status: FIXED

Expected:
- Clicking on a critter with the mouse should select it (open inspector) regardless of player distance.
- Pressing E near a critter should also select it (or follow/assign depending on mode), but should respect interaction radius (current behavior).
- The interaction method should be unified: both actions should perform the same logical "interact" on the critter.

Actual:
- Mouse click on critters is restricted to when the player is within interaction radius (`player.interaction_radius**2`). This forces the player to walk close to click, which feels bad.
- Pressing E near a critter may also have other behaviors (like starting follow) but may be confused by assignment logic.
- There may be inconsistency between click and E press.

Reproduce:
- Try to click a critter from across the screen. Nothing happens due to distance check.
- Have to walk up to the critter to click it.
- E key behavior may also be context-dependent but not clearly mapped.

Desired fix:
- Remove the distance check for mouse clicks on critters in `main.py`'s click handling. Allow clicks on critters at any distance.
- Keep the distance check for E key interactions (since that's a "nearby" action) as is, or unify if desired.
- Ensure that both click and E on a critter trigger the same outcome (e.g., toggle follow or open inspector). Currently click toggles inspector; E might be used for assignment or follow. Clarify: likely click should open inspector regardless of distance; E should either start follow (if not following) or stop follow (if following), and also be used for building interaction.
- Add tests or manual verification that clicks can select distant critters.

---

### [EINTERACT] Pressing E should make critters follow the player, not swallow the action

Status: FIXED

Fix commit: `e02b15f`

Expected: When the player presses E while targeting a critter (within interaction radius), the critter should begin following the player (toggle follow). This is more intuitive than the current behavior where E may be consumed by other systems or not map to follow clearly.

Actual: Critters may be consuming or "swallowing" the interact action in a way that prevents the intended follow behavior. The user reports: "critters are swallowing interact actions, similar to how grass used to."

Reproduce:
- Have a critter selected or nearby.
- Press E.
- Observe that follow does not toggle reliably; the action may do nothing or be consumed by another system (e.g., world interaction).

Desired fix:
- Clarify the E key interaction priority. In `InputHandler.update`, `interact_count` is used. In `main.py`, interact is processed for various objects. Ensure that when the player is within interaction radius of a critter and presses E, the critter's follow is toggled (or the inspector's follow button logic is invoked).
- Possibly restructure the interaction handling order: first check for critter interaction (toggle follow), then check for object interaction (trees, bushes, buildings), to avoid swallowing.
- If the issue is that world object interaction is consuming the event before critter, adjust order or conditions so both can happen appropriately.
- Add tests to verify that pressing E on a critter toggles follow state and does not trigger unintended actions.

---

### [MODEEXCL] Build mode and deconstruct mode should be mutually exclusive; Escape should close all overlays

Status: FIXED

Expected:
- Toggling build mode (B) should automatically exit deconstruct mode if active.
- Toggling deconstruct mode (X) should automatically exit build mode if active.
- Pressing Escape should close the build menu (if open), exit deconstruct mode, and close the critter inspector (if open). It should be a universal "back/close" key.

Actual:
- Build and deconstruct modes can be active simultaneously, leading to undefined behavior (e.g., both responding to clicks).
- Escape key is not bound to any of these closure actions.

Reproduce:
1. Press X to enter deconstruct mode (HUD shows).
2. Press B to open build menu. Both modes appear active.
3. Clicking leads to ambiguous behavior (both building placement and deconstruction may try to run).
4. Pressing Escape does nothing to close overlays or exit modes.

Desired fix:
- In `main.py` or input handling:
  - When B is pressed to toggle build menu, set `input_handler.deconstruct_mode = False` if it was True.
  - When X is pressed to toggle deconstruct mode, close build menu if open (e.g., set build_menu open flag to False) and also set `build_menu_selected` to None perhaps.
- Add Escape key handling in `InputHandler.handle_events`:
  - If build menu open, close it.
  - If deconstruct mode active, set `deconstruct_mode = False`.
  - If critter_inspector visible, hide it.
- Ensure these state changes are consistent and tested.
- Add tests for mode exclusivity and Escape key behavior (may be manual/UI tests).

---

### [FOLLOWCAP] Increase maximum following critters from 1 to 2

...

---

### [INTERACTCLR] Critter interaction via mouse and E key should work consistently; remove distance restriction for mouse clicks

...

---

### [EINTERACT] Pressing E should make critters follow the player, not swallow the action

...

---

### [MODEEXCL] Build mode and deconstruct mode should be mutually exclusive; Escape should close all overlays

...

---

### [PRAISE] Critter assignment to Gathering Hut works great

...

---

### [INTERACTTEXT] Show "Assign: E" when following critter is near a building

Status: FIXED

Expected: When the player has a critter following (in the following list) and is within interaction range of a building, the interaction prompt should indicate that pressing E will assign the critter (e.g., "Assign: E" or "Assign critter (E)"). This makes the assignment affordance clear.

Actual: Buildings currently show their native interaction text (e.g., "Build", "Withdraw", etc.) even when a following critter is present. The assignment option is not advertised, leading to confusion about how to assign.

Reproduce:
- Have a critter following the player.
- Approach a GatheringHut or MatingHut.
- Observe the interaction prompt does not mention assignment; pressing E may still assign depending on current code, but the prompt is missing.

Desired fix:
- Modify `Building.get_interaction_text()` (or specific subclasses) to check if the player has any following critters.
- If following critters exist and the building supports assignment (GatheringHut, MatingHut), return a combined or alternate string: "Assign: E" (or similar).
- Keep consistency: if both building-specific action and assignment are possible, decide which takes precedence. Likely assignment should take priority when a following critter is present to make the affordance clear.
- Ensure the text updates dynamically as following status changes.
- Add tests to verify interaction text varies based on `player.following_critters` content.

---

### [CONSTANTS] Centralize all in-game text strings in a Constants module

Status: FIXED

Fix commit: `abb097c`

Expected: All user-facing text strings (UI prompts, button labels, HUD text, messages, buff names) should be defined in a single `constants.py` module. Game code should reference these constants by variable names. This improves maintainability and consistency.

Actual: Text strings are scattered throughout the codebase (hardcoded in `main.py`, building classes, HUD rendering, etc.). This makes updating language and ensuring consistency difficult.

Reproduce:
- Search for string literals in src/: many appear directly in render calls and `get_interaction_text` methods.

Desired fix:
- Create `src/constants.py` (or similar) with clearly named constants for every UI text string, e.g.:
  - `INTERACT_ASSIGN = "Assign: E"`
  - `INTERACT_REST = "Rest on Chair (E)"`
  - `INTERACT_WITHDRAW = "Withdraw (E)"`
  - `INTERACT_BREED = "Breed (E)"`
  - `BUFF_WARM = "Warm"`
  - etc.
- Replace all hardcoded strings in the codebase with references to these constants.
- Update any tests that assert on specific string values to use the constants.
- This change is largely refactoring; no functional changes expected beyond potential consistency improvements.
- Ensure that the new constants are imported where needed.

---

### [SAVE_CHAIR] Unknown world object type: Chair (and Campfire) when loading saved game

Status: FIXED

Expected: Saved games containing Chair or Campfire buildings should load successfully.

Actual: Loading fails with `ValueError: Unknown world object type: Chair` (or Campfire) because these types were not registered in the save system's deserialization dispatcher.

Reproduce:
1. Place a Chair or Campfire in the world.
2. Save the game.
3. Attempt to load the save.
4. Observe the "Load failed" error message.

Fix implemented:
- Added `Chair` and `Campfire` to the `_deserialize_world_object` dispatcher in `src/save_system.py`.
- Added missing imports for `Chair` and `Campfire` in `src/save_system.py`.
- Verified fix with new round-trip tests in `tst/test_chair_campfire_save.py`.

Testing:
- Added `test_chair_serialization_roundtrip` and `test_campfire_serialization_roundtrip`.
- All save/load tests pass.

---

### [UI_BUILD_MENU_SIZE] Build menu buttons and background are too small

Status: FIXED

Fix commit: (current session)

Expected: 
- Build menu buttons should be wide enough to contain their labels without clipping.
- The build menu background box should be tall enough to contain all building buttons and the instructions text without overflow.

Actual: 
- Buttons were too narrow for some labels (e.g., "Gathering Hut" and cost strings).
- The menu height (150px) was insufficient for 4 buttons (4x40px + margins) and instructions, causing the last button and instructions to draw outside the menu background.

Implementation:
- Increased `menu_width` to 320 in `BuildMenu.__init__`.
- Changed `menu_height` to be calculated dynamically based on the number of buildings: `self.header_height + len(self.buildings) * (self.button_height + self.button_margin) + self.footer_height`.
- Updated `render` method to use these constants and improve vertical centering of text.
- Verified with automated tests in `tst/test_build_menu_ui.py`.

---

### [UI_CAMERA_LOAD_CENTER] Camera resets to (0,0) on game load

Status: FIXED

Fix commit: (current session)

Expected: 
The camera should center on the player's position immediately after loading a saved game.

Actual: 
On load, the camera was scrolled as far up and to the left as possible (offset 0,0), regardless of the player's position.

Implementation:
- Added `Camera.center_on(x, y)` method to `src/camera.py`.
- Called `camera.center_on(player.x, player.y)` in `main.py` after camera initialization and after in-game load.
