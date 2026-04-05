### [GFXCAMP] Campfire and Chair buildings lack visible graphics

Status: FIXED

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

Status: NOT_STARTED

Expected: The game should include at least three critters with distinct stat profiles to demonstrate variability: one weak (25 strength, speed, endurance), one strong (75 each), and one average (50 each).

Actual: All critters currently start with uniform stats (likely 50/50/50 by default). There's no mechanism to spawn critters with specific preset stat ranges.

Reproduce:
- Create a new game.
- Observe any newly spawned critters have default stats (50/50/50). No weak or strong variants exist.

Desired fix:
- Modify the initial world generation or spawning logic to create three specific critters with the desired stat profiles.
- Could be done by explicitly constructing Critter instances with those stats in `main.py` new game setup, or by adding a weighted random distribution that can produce such variants.
- Also ensure these stats are visible in the CritterInspector so the user can distinguish them.
- Consider naming or visual differentiation (optional) to make them easily identifiable.

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

### [GFXMISSING_METHOD] MatingHut missing find_resource_in_radius causing crash when critter assigned and enters GATHER state

Status: FIXED

Expected: When a critter assigned to a MatingHut enters GATHER state, it should not attempt to call `find_resource_in_radius`, because MatingHut is not meant to provide gather resources. The critter's behavior should either be prevented from transitioning to GATHER while assigned to a MatingHut, or the method should exist and handle appropriately (e.g., no resource, transition back to IDLE).

Actual: Crash with `AttributeError: 'MatingHut' object has no attribute 'find_resource_in_radius'` when a critter assigned to a MatingHut starts gathering.

Reproduce:
1. Build a MatingHut.
2. Assign at least 2 critters to the MatingHut (via follow+E or future UI).
3. Wait for an assigned critter to transition from IDLE to GATHER (after idle timer expires).
4. The critter's `_update_gather` calls `self.assigned_hut.find_resource_in_radius(world, self)`.
5. Since MatingHut does not define this method, Python raises AttributeError and the game crashes.

Desired fix (several options, choose one):
- **Option A (Preferred)**: Override `start_gather` in Critter to check if `assigned_hut` is a MatingHut and prevent transitioning to GATHER; instead transition to IDLE or a custom BREED state if conditions are appropriate. This keeps the critter from trying to gather from a MatingHut.
- **Option B**: Add a `find_resource_in_radius` method to Building base class that returns `None` by default, and have MatingHut inherit it without override. This would make `_update_gather` handle `None` gracefully (already does: `if self.target_resource is None: self.start_idle()`). This is a minimal fix that uses existing code path.
- **Option C**: Change `_update_gather` to check `hasattr(self.assigned_hut, 'find_resource_in_radius')` before calling, but this is less clean.

Recommendation: Implement Option B for simplicity and robustness. Ensure that when `target_resource` is None, the critter returns to IDLE. Verify that critters assigned to MatingHut do not get stuck in a loop attempting to gather repeatedly. Add regression tests covering a critter assigned to a MatingHut and ensuring no crash occurs when it updates.

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

Status: NOT_STARTED

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

Status: NOT_STARTED

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
EOF
