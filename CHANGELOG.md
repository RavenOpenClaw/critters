# Critters Project Changelog

This file enumerates all commits on the `mainline` branch to maintain a complete audit trail.
It is generated from git log; do not edit manually. Instead, add additional cross-references in other documentation files (tasks.md, bugs.md, fixes.md) as needed.

| Date | Commit | Message | Associated Task/Bug |
|------|--------|---------|----------------------|
| 2026-04-06 | `0adb9db` | 13:10:11 +0000 Fix STATVAR: enforce discrete critter stat tiers (25/50/75) in breeding |  |
| 2026-04-06 | `722f63d` | 02:52:36 +0000 test: add regression tests for QA fixes and follow capacity |  |
| 2026-04-06 | `ad61a5b` | 00:40:44 +0000 fix: update tests to match follow capacity=2 and proper test setup; add pathfinding stub |  |
| 2026-04-05 | `acd5fcd` | 16:18:30 +0000 Squash: bugfixes and improvements from fix/bugs-2026-04-05 |  |
| 2026-04-05 | `2597017` | 08:12:55 +0000 feat: add critter follow feature and refine assignment |  |
| 2026-04-05 | `487b695` | 07:22:25 +0000 refactor: remove dedicated assignment button/shortcut; use existing E interact |  |
| 2026-04-05 | `56d2a2d` | 06:58:41 +0000 feat: add CritterInspector assignment integration |  |
| 2026-04-05 | `df6b95d` | 06:48:14 +0000 feat: add following critter assignment via building interaction |  |
| 2026-04-05 | `c7260ae` | 06:21:22 +0000 feat: complete Mating Hut integration |  |
| 2026-04-05 | `9cecf8e` | 06:04:56 +0000 feat: add second map (north_woods) and boundary travel |  |
| 2026-04-05 | `8203bd9` | 06:03:45 +0000 chore: add Phase 8 tasks (40-44) and Phase 9 task 45 for follow/assign feature | Task 45 |
| 2026-04-05 | `d2aab2d` | 05:46:49 +0000 feat: implement building costs for all buildings; add UI display; add tests |  |
| 2026-04-05 | `e301345` | 04:43:51 +0000 refactor: rename berry resource to 'food' for consistency |  |
| 2026-04-05 | `6cbbd9e` | 04:26:07 +0000 docs: update bug statuses and fix entries |  |
| 2026-04-05 | `fbbcf7c` | 04:21:12 +0000 fix: include Tree in world object update loop to enable regeneration |  |
| 2026-04-05 | `a4664e7` | 03:51:55 +0000 docs: mark DUPLICATE_HUD as FIXED and add fix entry |  |
| 2026-04-05 | `94fbc40` | 03:40:28 +0000 test(critter): add regression tests for buff system and stats |  |
| 2026-04-05 | `27de310` | 03:31:27 +0000 ui: clicking outside CritterInspector now dismisses it (click-away to close) |  |
| 2026-04-05 | `e158491` | 03:23:10 +0000 feat(ui): add CritterInspector for viewing critter stats |  |
| 2026-04-04 | `33b1e3f` | 23:54:56 +0000 feat(campfire): implement aura buff for player and critters |  |
| 2026-04-04 | `57f56c6` | 23:35:19 +0000 feat(critter): implement endurance-based carry capacity and fix gathering flow |  |
| 2026-04-04 | `1f0e683` | 14:49:18 +0000 fix: resolve STICK_RESOURCE, RESOURCE_DEPLETION, BUFF_STACKING |  |
| 2026-04-04 | `177d8c0` | 10:53:47 +0000 docs: add TRAMPLING_SYSTEM.md explaining grass condition and trampling mechanics |  |
| 2026-04-04 | `33f0362` | 10:28:36 +0000 feat(trampling): add grass condition system with gradual degradation |  |
| 2026-04-04 | `da6c96c` | 10:21:14 +0000 feat(trampling): remove grass on trampled cells to create bare paths |  |
| 2026-04-04 | `900532a` | 10:10:33 +0000 fix(debug): correct trampled cells reference in debug display and add overlay |  |
| 2026-04-04 | `8db1b2c` | 06:58:55 +0000 fix(ui): correct HUD rendering order and remove duplicate inventory |  |
| 2026-04-04 | `98aa11b` | 01:17:49 +0000 fix(gathering-hut): restrict find_resource_in_radius to BerryBush only |  |
| 2026-04-04 | `0869754` | 00:01:45 +0000 test(berry_bush): add regression test for partial regrowth (BERRY_REGROW) |  |
| 2026-04-03 | `b8f42c3` | 23:34:03 +0000 docs: update tracking after bug review |  |
| 2026-04-03 | `6e45d96` | 17:05:12 +0000 Fix WGFBKAX: grass duplicate spread causing performance issue; also randomize grass spread threshold (30-120s); add test to prevent regression |  |
| 2026-04-03 | `e8d43d2` | 17:01:28 +0000 Fix grass interaction, slow grass spread, and critter tree-gathering oscillation |  |
| 2026-04-03 | `9884ced` | 16:29:51 +0000 Fix grass exponential growth, berry bush partial regrowth, and critter return pathfinding oscillation |  |
| 2026-04-03 | `f8806e4` | 16:12:23 +0000 bug: add [WGFBKAX] performance degrades over time\n\n- Symptom: FPS drops and lag increases the longer the game runs\n- Root cause unknown; may require binary search to isolate\n- Potential areas: pathfinding cache, object list growth, trampled cells, entity duplication, memory leaks\n- Status: NOT_STARTED | Bug WGFBKAX |
| 2026-04-03 | `ac2b4a2` | 03:08:32 +0000 docs: add UAT/QA checklist for manual testing\n\n- Comprehensive checklist covering all implemented features\n- Organized by area: movement, resources, buildings, critters, breeding, crafting, multi-map, save/load, deconstruction, UI, edge cases\n- Helps Shams exercise the prototype and catch regressions |  |
| 2026-04-03 | `92d0965` | 01:08:24 +0000 docs: add Documentation Index reference to README\n\n- New section pointing to DOCUMENTATION_INDEX.md as the starting point\n- Helps new contributors quickly locate key files and avoid common pitfalls |  |
| 2026-04-03 | `6105b7f` | 00:54:52 +0000 docs: add DOCUMENTATION_INDEX.md as central lookup for all project docs\n\n- Points to .kiro specs (tasks, design, requirements)\n- Highlights SAVE_SYSTEM_EXTENSION.md\n- Clarifies doc/ vs docs/ structure\n- Prevents common pitfalls (hidden .kiro, tasks location)\n- Serves as the single source of truth for "where is X?" |  |
| 2026-04-03 | `16bcc0d` | 00:51:41 +0000 Update WORKING_ON.md: reflect recent completions (deconstruction, code index), update test count to 179, note merged commits. |  |
| 2026-04-03 | `bc58120` | 00:50:11 +0000 docs: add comprehensive code index and architecture guide (Code Index task)\n\n- Documents critical file locations, especially .kiro/tasks.md\n- Module reference with descriptions\n- Data flow and entity relationships\n- Testing and extension points\n- Common pitfalls (grid bounds, save system, tasks discovery)\n\nAims to prevent future orientation issues and speed up development. |  |
| 2026-04-03 | `b1cd726` | 00:46:06 +0000 Merge: Deconstruction feature (Task Backlog)\n\n- Building.deconstruct, InputHandler X toggle, HUD indicator\n- Tests added, 179 passing\n- Documentation and tracking updates |  |
| 2026-04-03 | `59c7a51` | 00:45:57 +0000 feat: implement deconstruction feature (Task Backlog)\n\n- Design doc: DECONSTRUCTION_DESIGN.md\n- Building.deconstruct method\n- InputHandler deconstruct_mode toggle (X key)\n- main.py integration with HUD indicator\n- Tests: 5 new unit tests in test_deconstruction.py\n- All 179 tests pass\n- Updated workspace TASKS.md, MEMORY.md, WORKING_ON.md\n\nCo-authored-by: Raven <raven.open.claw@gmail.com> |  |
| 2026-04-01 | `4c3b214` | 23:54:25 +0000 test: add BuildMenu mouse handling tests to prevent accidental placement regression |  |
| 2026-04-01 | `2ab6443` | 23:33:13 +0000 Update WORKING_ON.md: mark Tasks 38-39 completed |  |
| 2026-04-01 | `77d53d1` | 23:30:53 +0000 Merge branch 'feature/ui-input-improvements' into mainline |  |
| 2026-04-01 | `dff2d27` | 23:30:47 +0000 feat: change save/load to F5/F6; add mouse support to build menu - InputHandler: K_s/K_l -> K_F5/K_F6 - BuildMenu: clickable building buttons; HUD build toggle button - main.py: integrate HUD build button, refined mouse placement logic - All 168 tests pass |  |
| 2026-04-01 | `a97352f` | 23:12:05 +0000 Merge branch 'feature/task-37-title-screen' into mainline |  |
| 2026-04-01 | `793651d` | 23:12:02 +0000 feat: add title screen with New Game/Continue (Task 37) - Added TitleScreen class with simple menu, overwrite confirmation - Integrated into main.py: title screen shown on launch - Continue loads existing save; New Game starts fresh - All 168 tests pass | Task 37 |
| 2026-04-01 | `888f02b` | 22:42:33 +0000 Merge branch 'feature/task-35-ui-polish' into mainline |  |
| 2026-04-01 | `923a1dd` | 22:42:30 +0000 feat: enhance debug display with entity and trampled counts (Task 35.2) | Task 35.2 |
| 2026-04-01 | `30c02ff` | 22:32:51 +0000 feat: add 2-frame sprite animation for critters (Task 34.1) | Task 34.1 |
| 2026-04-01 | `c4cdc32` | 14:45:00 +0000 feat: add Tree, Rock, Stick world objects (Task 33) | Task 33 |
| 2026-04-01 | `861a9f0` | 14:40:08 +0000 feat: add Tree, Rock, and Stick world objects (Task 33)\n\n- Tree: 2x2 renewable wood resource with regeneration\n- Rock: 1x1 stone resource (non-renewable)\n- Stick: 1x1 collectible stick (non-renewable)\n- Comprehensive unit and property tests for all three\n\nAll 157 tests pass. | Task 33 |
| 2026-04-01 | `fd68a3b` | 09:51:42 +0000 docs: add Save System Extension Guide |  |
| 2026-04-01 | `9b5b921` | 00:19:46 +0000 Task 31: Save/Load System | Task 31 |
| 2026-03-31 | `bcd0e23` | 10:15:22 +0000 docs: add future optimization idea for offline building simulation (rate-based accumulation) |  |
| 2026-03-31 | `eb8a570` | 08:00:00 +0000 feat: multi-map world system (Task 30) with transitions and preservation; add tests | Task 30 |
| 2026-03-31 | `b6534fc` | 01:23:03 +0000 docs: mark Task 28 as complete and Task 29 checkpoint as done | Task 28 |
| 2026-03-31 | `45c8c6a` | 01:22:52 +0000 feat: crafting system (Task 28) with Recipe, CraftingMenu UI; add tests | Task 28 |
| 2026-03-31 | `09f6029` | 01:16:12 +0000 feat: equipment system (Task 27) with unlock/equip mechanics; add comprehensive tests | Task 27 |
| 2026-03-31 | `3d1ecc1` | 01:04:48 +0000 docs: mark Task 24 (Buff System) as complete in tasks.md | Task 24 |
| 2026-03-31 | `ee0682b` | 01:03:32 +0000 feat: buff system (Task 24) with Chair and Campfire; add tests; integrate into main | Task 24 |
| 2026-03-31 | `16af11b` | 00:34:21 +0000 feat: implement critter breeding (Task 23) with MatingHut.breed(); add comprehensive tests | Task 23 |
| 2026-03-31 | `51a98e3` | 00:25:58 +0000 test: fix interaction targeting test tolerance to match implementation |  |
| 2026-03-31 | `9f87931` | 00:22:42 +0000 feat: implement Mating Hut (Task 22) with assignment system; add unit and property tests; update tasks documentation | Task 22 |
| 2026-03-31 | `f6d842b` | 00:19:41 +0000 docs: mark Task 25 (Berry Economy UI) as complete; fix duplicated task numbers (25.5→25.6, 26 duplicate) | Task 25 |
| 2026-03-30 | `1068c23` | 13:27:23 +0000 feat: add berry economy HUD (Task 25) with red square icon and player inventory display; implement GatheringHut withdraw interaction on E key; fix interaction logic to use circle-rectangle intersection for large objects; add comprehensive tests. All 101 tests passing. | Task 25 |
| 2026-03-30 | `9591501` | 12:48:57 +0000 feat: add Berry Economy UI (Task 25) | Task 25 |
| 2026-03-29 | `86be7c3` | 14:45:09 +0000 Improve critter behavior: smooth loiter movement; debug path logging; and non-blocking movement. Loiter now uses smooth animation towards target cell instead of teleporting. Added DEBUG prints for pathfinding in GATHER/RETURN states to help diagnose long paths. Critters remain non-blocking (blocks_movement=False) to prevent pathfinding circles. |  |
| 2026-03-29 | `2bc80cd` | 10:34:33 +0000 Fix: prevent critter pathfinding circles by making Critter non-blocking (blocks_movement=False). Critters can now overlap, reducing aggressive avoidance while keeping random spread around targets. Closes circling bug. |  |
| 2026-03-28 | `52bc61d` | 16:16:58 +0000 fix(bugs-3-10): address QA observations for critter behavior and visuals |  |
| 2026-03-29 | `9b4d5d4` | 00:33:11 +0900 Moved test gathering hut and added test grass |  |
| 2026-03-29 | `1a1af7f` | 00:31:29 +0900 Fixed a crash on unimplemented interact() |  |
| 2026-03-27 | `9d5bc28` | 02:18:22 +0000 test: add boundary tests for GridSystem and trample decay test |  |
| 2026-03-27 | `2aed7c8` | 01:55:57 +0000 feat(phase3): implement resource regeneration, grass propagation, trampling, and obstacles |  |
| 2026-03-26 | `4aaa4d0` | 14:52:14 +0000 feat(ui): add colored state labels for critters (Task 15) | Task 15 |
| 2026-03-26 | `27094bd` | 01:23:28 +0000 feat: implement critter AI state machine (Task 14) | Task 14 |
| 2026-03-22 | `667b617` | 16:06:03 +0000 docs: update README with controls and PLAY.sh |  |
| 2026-03-22 | `3757487` | 19:03:51 +0900 Added simple script and updated Makefile to run the game |  |
| 2026-03-22 | `94cbf32` | 19:02:51 +0900 Added feature, hold E to interact at configurable rate |  |
| 2026-03-22 | `5bdaeec` | 02:02:02 +0000 fix(pathfinding): add bounds to GridSystem to prevent infinite search |  |
| 2026-03-20 | `c51d915` | 08:16:31 +0000 ux: set interaction radius to fixed 45px; raise interaction prompt |  |
| 2026-03-20 | `d45008c` | 08:09:44 +0000 balance: increase player interaction radius to 2× radius |  |
| 2026-03-20 | `8ed857b` | 08:05:16 +0000 ux: remove spawn-trap bush; add interact prompts |  |
| 2026-03-20 | `b3ed53d` | 07:53:27 +0000 testability: add bush near player start; draw debug interaction radius |  |
| 2026-03-20 | `56af220` | 07:47:24 +0000 fix(ui): add missing pygame import to BuildMenu; improve inventory HUD |  |
| 2026-03-20 | `3e0085b` | 07:41:24 +0000 docs(tasks): mark Task 13 (A* pathfinding) as complete | Task 13 |
| 2026-03-20 | `dbf5946` | 07:41:12 +0000 fix(build-menu): add missing pygame import; add inventory HUD display (player can see berries count) |  |
| 2026-03-20 | `5b97193` | 07:28:04 +0000 docs(tasks): mark Task 12 (Critter assignment) as complete | Task 12 |
| 2026-03-20 | `387ad33` | 07:27:37 +0000 feat(gathering-hut): implement assign_critter method and tests (Task 12) | Task 12 |
| 2026-03-20 | `ec155cd` | 07:26:08 +0000 docs(tasks): mark Task 11 (Critter entity) as complete; all subtasks implemented and tested | Task 11 |
| 2026-03-20 | `2b45806` | 07:25:18 +0000 feat(critter): implement Critter entity with stats and behavior methods (Task 11) | Task 11 |
| 2026-03-20 | `3ce7a3e` | 07:22:13 +0000 feat(world): add multiple test berry bushes to enable collision and interaction testing |  |
| 2026-03-20 | `d6af579` | 16:11:29 +0900 Tested bugfix DLKJSIEQ. Works as expected. |  |
| 2026-03-20 | `0d25d22` | 05:37:30 +0000 docs(working): update Task 9 completion; prepare for Task 11 (Phase 2) | Task 9 |
| 2026-03-20 | `978578a` | 05:37:05 +0000 docs(tasks): mark Task 9 and Checkpoint 10 as complete | Task 9 |
| 2026-03-20 | `c77c06f` | 05:36:26 +0000 feat(building): implement Building base class, GatheringHut, BuildMenu UI, and tests |  |
| 2026-03-20 | `181d0b4` | 05:04:24 +0000 docs(readme): clarify task files and their paths; note Kiro tasks as primary |  |
| 2026-03-20 | `72b1c9e` | 04:49:53 +0000 docs(tasks): mark tasks 7 and 8 as complete in Kiro and high-level tracking |  |
| 2026-03-20 | `b38b3cd` | 04:48:33 +0000 docs(working): mark Task 8 inventory complete; update test count to 31 | Task 8 |
| 2026-03-20 | `dc6f852` | 04:47:51 +0000 feat(inventory): implement Inventory class and integrate into Player/WorldObject |  |
| 2026-03-20 | `3a6c52f` | 04:41:13 +0000 docs(working): update task tracking; mark Task 7 complete, start Task 8 inventory system | Task 7 |
| 2026-03-20 | `8cef0dc` | 04:40:14 +0000 feat(interaction): implement player interaction system |  |
| 2026-03-20 | `02d75de` | 04:36:01 +0000 test(collision): fix corner case test; use obstacle at (1,1) and adjust player y to 0.3 to properly test both axes blocked |  |
| 2026-03-20 | `34fbd67` | 04:25:10 +0000 feat(dev): add Makefile for setup/test; update README with simpler workflow |  |
| 2026-03-20 | `56777ff` | 04:09:01 +0000 docs(environment): update status to reflect proper venv setup; tests 19/20 passing |  |
| 2026-03-16 | `3f37a4d` | 00:17:19 +0000 fix: implement sliding collision for player movement |  |
| 2026-03-15 | `099e9c6` | 11:27:09 +0900 Added bugs.md and fixes.md as a way to report and fix bugs in the project |  |
| 2026-03-15 | `492484d` | 01:01:45 +0000 feat(critters): Phase 1 foundation — tasks 2.1-6.3 |  |
| 2026-03-14 | `26eb462` | 19:46:31 +0900 Adding all specs and documentation from initial Kiro init |  |
| 2026-03-14 | `628427e` | 18:04:35 +0900 Initial commit |  |