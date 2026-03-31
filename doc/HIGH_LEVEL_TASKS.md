# **Project Tasks: Critters Prototype**

Remember to refer to doc/REQUIREMENTS.md to see high level vision and details about how these features should work.

NOTE: this file was created initially, but is less detailed than `.kiro/specs/critters-game-prototype/tasks.md`. We should always defer to the Kiro tasks.md, but we can also consult this file HIGH_LEVEL_TASKS.md as a kind of high level task list and general guidance. As we check off tasks in the Kiro tasks.md, we can come back here to check our overall progress and mark things as COMPLETE as we make progress.

## **Phase 1: Foundation (The "Hello World" of Critters)**

* [COMPLETE] **Task 1.1:** Initialize project structure and Git repository. Create mainline branch.
* [x] **Task 1.2:** Create first src/ file and tst/ file. Run it to make sure it works.
* [x] **Task 1.3:** Implement game window and make sure it can render a player. For now, it should just be a blue circle on a light gray background.
* [x] **Task 1.4:** Implement player controller. "Player" character can move (WASD). This also tests that the rendering works in 60fps. Toggle display debug data when pressing F3 key.
* [x] **Task 1.5:** Implement basic grid system for the world. Goal here is to Objects in the world should have dimensions (how much space it takes on the grid, e.g. 1x2), internal inventory list that can hold items (e.g. berry bush can hold a berry), and should have some interact function (e.g. interact with bush to harvest a berry, interact with a try to chop). Please note that the player can move smoothly around the world, but objects must be placed aligned to the grid. Critters will also use the grid for pathfinding (player/critters cannot occupy the grid space that is taken by an object, i.e. they should collide with grid spaces that are occupied). The world grid system should NOT be implemented as a 2D array because it isn't efficient enough. But we will lock objects to be aligned to the grid. We should register objects in a dict/map with their grid locations, so it is easy to search for objects to collide with. We only have to load/search/pathfind inside the current map. The world should be broken up into multiple map that we can travel between. For this task in particular, if you know of more efficient ways to organize the world and implement collision and path finding, please ask me about it, and we can update the requirements doc accordingly.
* [x] **Task 1.6:** Create an initial test world object, "Berry bush". It should be placeable in the world. This is the first world object, but there will be many more like trees and rocks and grass. The bush should know its own position, but more importantly other entities like players and critters should be able to detect other objects so they can path find and collide with them. For now let it be a 1x1 green square, graphically. Make sure the player can actually collide with it. Interacting with the bush is not possible yet. That's for the next task.
* [x] **Task 1.7:** Implement manual resource gathering (Interact (e) with a "Tree" or "Bush" object). Player controller should link key press with interact action (user presses "e", player character tries the "interact" action). Then the interact action should be attempted on the nearest world object, within a reasonable radius (probably roughly 1.5x the radius of the player themselves, btu this should be configurable).
* [x] **Task 1.8:** Create a basic objects for Inventory system. We need items and equipment. Equipment is not treated as an item, it's merely unlocked and equipped. Items are viewed in the inventory. The goal is to be able to represent many different items like berry, grass, log, stick, etc. When those items are **picked up by the player**, they are converted into raw currency like "food", "wood", "stone", "plants". Those raw resources can be spent to build buildings, unblock paths, craft equipment, purchase upgrades, etc.
* [x] **Task 1.9:** Create objects to support buildings. First building is the "Gathering Hut" building. Buildings should be placable in the world on the grid. This should use the same system as the berry bush, i.e. the gathering hut building is a world object placed in the world. We will need a way for the player to select the gathering hut building and place it into the world. For now, let's let the player press (b) to access the "build" menu, then they can click "Gathering Hut" or press (g) to select gathering hut. Then they can click a grid square to place the hut. They hut can be 3x3.

## **Phase 2: The First Critter**

* [x] **Task 2.1:** Implement the Critter class with Base Stats (Strength, Speed, Endurance). Critter should just be a red circle for now to keep rendering basic.
* [x] **Task 2.2:** Implement the State Machine AI loop (IDLE, GATHER, RETURN).
* [x] **Task 2.3:** Add UI labels above Critters showing their current State.
* [x] **Task 2.4:** Implement "Assignment" logic (Link a Critter to a Gathering Hut).

## **Phase 3: World Simulation & Growth**

* [ ] **Task 3.1:** Implement resource regeneration (Trees regrowing over time).
* [ ] **Task 3.2:** Add "Work Obstacles" (e.g., a Fallen Tree requiring 500 "chops" to clear).
* [ ] **Task 3.3:** Implement simple "Path Trampling" (changing tile types based on movement frequency).

## **Phase 4: Breeding & Scaling**

* [x] **Task 4.1:** Create the Mating Hut building.
* [ ] **Task 4.2:** Implement inheritance logic for Critter breeding.
* [ ] **Task 4.3:** Add "Buff" systems from buildings (Chair/Campfire).
