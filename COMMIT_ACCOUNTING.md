# Commit Accounting

This file maps every commit on `mainline` to its associated task, bug, or category.

| Commit | Type | Reference | Subject |
|--------|------|-----------|---------|
| `2dea84d6` | Documentation |  | docs: add comprehensive CHANGELOG and update DOCUMENTATION_INDEX; fix STATVAR tracking |
| `0adb9dbd` | Unassigned |  | Fix STATVAR: enforce discrete critter stat tiers (25/50/75) in breeding |
| `722f63d3` | Test |  | test: add regression tests for QA fixes and follow capacity |
| `ad61a5b9` | Bugfix |  | fix: update tests to match follow capacity=2 and proper test setup; add pathfinding stub |
| `acd5fcdd` | Unassigned |  | Squash: bugfixes and improvements from fix/bugs-2026-04-05 |
| `2597017a` | Feature |  | feat: add critter follow feature and refine assignment |
| `487b695a` | Unassigned |  | refactor: remove dedicated assignment button/shortcut; use existing E interact |
| `56d2a2df` | Feature |  | feat: add CritterInspector assignment integration |
| `df6b95d7` | Feature |  | feat: add following critter assignment via building interaction |
| `c7260aee` | Feature |  | feat: complete Mating Hut integration |
| `9cecf8e1` | Feature |  | feat: add second map (north_woods) and boundary travel |
| `8203bd9d` | Task | 45 | chore: add Phase 8 tasks (40-44) and Phase 9 task 45 for follow/assign feature |
| `d2aab2dc` | Feature |  | feat: implement building costs for all buildings; add UI display; add tests |
| `e3013457` | Unassigned |  | refactor: rename berry resource to 'food' for consistency |
| `6cbbd9e4` | Documentation |  | docs: update bug statuses and fix entries |
| `fbbcf7ca` | Bugfix |  | fix: include Tree in world object update loop to enable regeneration |
| `a4664e74` | Documentation |  | docs: mark DUPLICATE_HUD as FIXED and add fix entry |
| `94fbc40e` | Test |  | test(critter): add regression tests for buff system and stats |
| `27de310c` | Unassigned |  | ui: clicking outside CritterInspector now dismisses it (click-away to close) |
| `e1584910` | Feature |  | feat(ui): add CritterInspector for viewing critter stats |
| `33b1e3f4` | Feature |  | feat(campfire): implement aura buff for player and critters |
| `57f56c65` | Feature |  | feat(critter): implement endurance-based carry capacity and fix gathering flow |
| `1f0e6833` | Bugfix |  | fix: resolve STICK_RESOURCE, RESOURCE_DEPLETION, BUFF_STACKING |
| `177d8c0b` | Documentation |  | docs: add TRAMPLING_SYSTEM.md explaining grass condition and trampling mechanics |
| `33f0362b` | Feature |  | feat(trampling): add grass condition system with gradual degradation |
| `da6c96cc` | Feature |  | feat(trampling): remove grass on trampled cells to create bare paths |
| `900532a2` | Bugfix |  | fix(debug): correct trampled cells reference in debug display and add overlay |
| `8db1b2ce` | Bugfix |  | fix(ui): correct HUD rendering order and remove duplicate inventory |
| `98aa11b9` | Bugfix |  | fix(gathering-hut): restrict find_resource_in_radius to BerryBush only |
| `08697549` | Test |  | test(berry_bush): add regression test for partial regrowth (BERRY_REGROW) |
| `b8f42c3d` | Documentation |  | docs: update tracking after bug review |
| `6e45d96e` | Unassigned |  | Fix WGFBKAX: grass duplicate spread causing performance issue; also randomize grass spread threshold (30-120s); add test to prevent regression |
| `e8d43d21` | Unassigned |  | Fix grass interaction, slow grass spread, and critter tree-gathering oscillation |
| `9884cede` | Unassigned |  | Fix grass exponential growth, berry bush partial regrowth, and critter return pathfinding oscillation |
| `f8806e4b` | Bug | WGFBKAX | bug: add [WGFBKAX] performance degrades over time\n\n- Symptom: FPS drops and lag increases the longer the game runs\n- Root cause unknown; may require binary search to isolate\n- Potential areas: pathfinding cache, object list growth, trampled cells, entity duplication, memory leaks\n- Status: NOT_STARTED |
| `ac2b4a2f` | Documentation |  | docs: add UAT/QA checklist for manual testing\n\n- Comprehensive checklist covering all implemented features\n- Organized by area: movement, resources, buildings, critters, breeding, crafting, multi-map, save/load, deconstruction, UI, edge cases\n- Helps Shams exercise the prototype and catch regressions |
| `92d0965d` | Documentation |  | docs: add Documentation Index reference to README\n\n- New section pointing to DOCUMENTATION_INDEX.md as the starting point\n- Helps new contributors quickly locate key files and avoid common pitfalls |
| `6105b7fd` | Documentation |  | docs: add DOCUMENTATION_INDEX.md as central lookup for all project docs\n\n- Points to .kiro specs (tasks, design, requirements)\n- Highlights SAVE_SYSTEM_EXTENSION.md\n- Clarifies doc/ vs docs/ structure\n- Prevents common pitfalls (hidden .kiro, tasks location)\n- Serves as the single source of truth for "where is X?" |
| `16bcc0d0` | Improvement |  | Update WORKING_ON.md: reflect recent completions (deconstruction, code index), update test count to 179, note merged commits. |
| `bc58120c` | Documentation |  | docs: add comprehensive code index and architecture guide (Code Index task)\n\n- Documents critical file locations, especially .kiro/tasks.md\n- Module reference with descriptions\n- Data flow and entity relationships\n- Testing and extension points\n- Common pitfalls (grid bounds, save system, tasks discovery)\n\nAims to prevent future orientation issues and speed up development. |
| `b1cd7267` | Merge |  | Merge: Deconstruction feature (Task Backlog)\n\n- Building.deconstruct, InputHandler X toggle, HUD indicator\n- Tests added, 179 passing\n- Documentation and tracking updates |
| `59c7a514` | Feature |  | feat: implement deconstruction feature (Task Backlog)\n\n- Design doc: DECONSTRUCTION_DESIGN.md\n- Building.deconstruct method\n- InputHandler deconstruct_mode toggle (X key)\n- main.py integration with HUD indicator\n- Tests: 5 new unit tests in test_deconstruction.py\n- All 179 tests pass\n- Updated workspace TASKS.md, MEMORY.md, WORKING_ON.md\n\nCo-authored-by: Raven <raven.open.claw@gmail.com> |
| `4c3b2144` | Test |  | test: add BuildMenu mouse handling tests to prevent accidental placement regression |
| `2ab64433` | Improvement |  | Update WORKING_ON.md: mark Tasks 38-39 completed |
| `77d53d15` | Merge |  | Merge branch 'feature/ui-input-improvements' into mainline |
| `dff2d272` | Feature |  | feat: change save/load to F5/F6; add mouse support to build menu - InputHandler: K_s/K_l -> K_F5/K_F6 - BuildMenu: clickable building buttons; HUD build toggle button - main.py: integrate HUD build button, refined mouse placement logic - All 168 tests pass |
| `a97352f0` | Merge |  | Merge branch 'feature/task-37-title-screen' into mainline |
| `793651d1` | Task | 37 | feat: add title screen with New Game/Continue (Task 37) - Added TitleScreen class with simple menu, overwrite confirmation - Integrated into main.py: title screen shown on launch - Continue loads existing save; New Game starts fresh - All 168 tests pass |
| `888f02bd` | Merge |  | Merge branch 'feature/task-35-ui-polish' into mainline |
| `923a1dd0` | Task | 35.2 | feat: enhance debug display with entity and trampled counts (Task 35.2) |
| `30c02ff7` | Task | 34.1 | feat: add 2-frame sprite animation for critters (Task 34.1) |
| `c4cdc32a` | Task | 33 | feat: add Tree, Rock, Stick world objects (Task 33) |
| `861a9f0d` | Task | 33 | feat: add Tree, Rock, and Stick world objects (Task 33)\n\n- Tree: 2x2 renewable wood resource with regeneration\n- Rock: 1x1 stone resource (non-renewable)\n- Stick: 1x1 collectible stick (non-renewable)\n- Comprehensive unit and property tests for all three\n\nAll 157 tests pass. |
| `fd68a3b2` | Documentation |  | docs: add Save System Extension Guide |
| `9b5b9211` | Task | 31 | Task 31: Save/Load System |
| `bcd0e23a` | Documentation |  | docs: add future optimization idea for offline building simulation (rate-based accumulation) |
| `eb8a5709` | Task | 30 | feat: multi-map world system (Task 30) with transitions and preservation; add tests |
| `b6534fcb` | Task | 28 | docs: mark Task 28 as complete and Task 29 checkpoint as done |
| `45c8c6ae` | Task | 28 | feat: crafting system (Task 28) with Recipe, CraftingMenu UI; add tests |
| `09f60295` | Task | 27 | feat: equipment system (Task 27) with unlock/equip mechanics; add comprehensive tests |
| `3d1ecc1c` | Task | 24 | docs: mark Task 24 (Buff System) as complete in tasks.md |
| `ee0682be` | Task | 24 | feat: buff system (Task 24) with Chair and Campfire; add tests; integrate into main |
| `16af11bd` | Task | 23 | feat: implement critter breeding (Task 23) with MatingHut.breed(); add comprehensive tests |
| `51a98e36` | Test |  | test: fix interaction targeting test tolerance to match implementation |
| `9f87931d` | Task | 22 | feat: implement Mating Hut (Task 22) with assignment system; add unit and property tests; update tasks documentation |
| `f6d842b7` | Task | 25 | docs: mark Task 25 (Berry Economy UI) as complete; fix duplicated task numbers (25.5→25.6, 26 duplicate) |
| `1068c234` | Task | 25 | feat: add berry economy HUD (Task 25) with red square icon and player inventory display; implement GatheringHut withdraw interaction on E key; fix interaction logic to use circle-rectangle intersection for large objects; add comprehensive tests. All 101 tests passing. |
| `95915017` | Task | 25 | feat: add Berry Economy UI (Task 25) |
| `86be7c33` | Improvement |  | Improve critter behavior: smooth loiter movement; debug path logging; and non-blocking movement. Loiter now uses smooth animation towards target cell instead of teleporting. Added DEBUG prints for pathfinding in GATHER/RETURN states to help diagnose long paths. Critters remain non-blocking (blocks_movement=False) to prevent pathfinding circles. |
| `2bc80cd1` | Bugfix |  | Fix: prevent critter pathfinding circles by making Critter non-blocking (blocks_movement=False). Critters can now overlap, reducing aggressive avoidance while keeping random spread around targets. Closes circling bug. |
| `52bc61d7` | Bugfix |  | fix(bugs-3-10): address QA observations for critter behavior and visuals |
| `9b4d5d4b` | Unassigned |  | Moved test gathering hut and added test grass |
| `1a1af7f5` | Unassigned |  | Fixed a crash on unimplemented interact() |
| `9d5bc283` | Test |  | test: add boundary tests for GridSystem and trample decay test |
| `2aed7c85` | Feature |  | feat(phase3): implement resource regeneration, grass propagation, trampling, and obstacles |
| `4aaa4d05` | Task | 15 | feat(ui): add colored state labels for critters (Task 15) |
| `27094bd2` | Task | 14 | feat: implement critter AI state machine (Task 14) |
| `667b6178` | Documentation |  | docs: update README with controls and PLAY.sh |
| `37574876` | Unassigned |  | Added simple script and updated Makefile to run the game |
| `94cbf32a` | Unassigned |  | Added feature, hold E to interact at configurable rate |
| `5bdaeecf` | Bugfix |  | fix(pathfinding): add bounds to GridSystem to prevent infinite search |
| `c51d9152` | Unassigned |  | ux: set interaction radius to fixed 45px; raise interaction prompt |
| `d45008c3` | Unassigned |  | balance: increase player interaction radius to 2× radius |
| `8ed857b9` | Unassigned |  | ux: remove spawn-trap bush; add interact prompts |
| `b3ed53d4` | Unassigned |  | testability: add bush near player start; draw debug interaction radius |
| `56af2200` | Bugfix |  | fix(ui): add missing pygame import to BuildMenu; improve inventory HUD |
| `3e0085ba` | Task | 13 | docs(tasks): mark Task 13 (A* pathfinding) as complete |
| `dbf59462` | Bugfix |  | fix(build-menu): add missing pygame import; add inventory HUD display (player can see berries count) |
| `5b971936` | Task | 12 | docs(tasks): mark Task 12 (Critter assignment) as complete |
| `387ad335` | Task | 12 | feat(gathering-hut): implement assign_critter method and tests (Task 12) |
| `ec155cd9` | Task | 11 | docs(tasks): mark Task 11 (Critter entity) as complete; all subtasks implemented and tested |
| `2b458065` | Task | 11 | feat(critter): implement Critter entity with stats and behavior methods (Task 11) |
| `3ce7a3e3` | Feature |  | feat(world): add multiple test berry bushes to enable collision and interaction testing |
| `d6af5797` | Unassigned |  | Tested bugfix DLKJSIEQ. Works as expected. |
| `0d25d228` | Task | 9 | docs(working): update Task 9 completion; prepare for Task 11 (Phase 2) |
| `978578aa` | Task | 9 | docs(tasks): mark Task 9 and Checkpoint 10 as complete |
| `c77c06f8` | Feature |  | feat(building): implement Building base class, GatheringHut, BuildMenu UI, and tests |
| `181d0b4b` | Unassigned |  | docs(readme): clarify task files and their paths; note Kiro tasks as primary |
| `72b1c9e7` | Unassigned |  | docs(tasks): mark tasks 7 and 8 as complete in Kiro and high-level tracking |
| `b38b3cd0` | Task | 8 | docs(working): mark Task 8 inventory complete; update test count to 31 |
| `dc6f8523` | Feature |  | feat(inventory): implement Inventory class and integrate into Player/WorldObject |
| `3a6c52f9` | Task | 7 | docs(working): update task tracking; mark Task 7 complete, start Task 8 inventory system |
| `8cef0dce` | Feature |  | feat(interaction): implement player interaction system |
| `02d75de5` | Test |  | test(collision): fix corner case test; use obstacle at (1,1) and adjust player y to 0.3 to properly test both axes blocked |
| `34fbd670` | Feature |  | feat(dev): add Makefile for setup/test; update README with simpler workflow |
| `56777ff4` | Unassigned |  | docs(environment): update status to reflect proper venv setup; tests 19/20 passing |
| `3f37a4d1` | Bugfix |  | fix: implement sliding collision for player movement |
| `099e9c65` | Unassigned |  | Added bugs.md and fixes.md as a way to report and fix bugs in the project |
| `492484dc` | Feature |  | feat(critters): Phase 1 foundation — tasks 2.1-6.3 |
| `26eb462f` | Unassigned |  | Adding all specs and documentation from initial Kiro init |
| `628427e3` | Unassigned |  | Initial commit |