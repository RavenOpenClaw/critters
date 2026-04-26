# Implementation Plan: Critters Game Prototype

## Overview

This implementation plan follows a phased approach starting with minimal graphics (blue circle for player, red circles for critters, green squares for bushes, light gray background) and building incrementally with tests. The implementation uses Python 3.10+ with Pygame for rendering and Hypothesis for property-based testing.

Key principles:
- Get basic rendering working first
- Build incrementally with tests
- Start with simple graphics before adding complexity
- Each task should be completable on a feature branch
- Tests must pass before merging

## Tasks

## Phase 1: Foundation (The "Hello World" of Critters)

- [x] 1. Initialize project structure and dependencies
  - Create project directory structure (src/, tst/, doc/)
  - Set up Python virtual environment
  - Install dependencies (pygame, pytest, hypothesis)
  - Create .gitignore for Python projects
  - Initialize Git repository with mainline branch
  - _Requirements: N/A (project setup)_

- [x] 2. Create minimal game window with rendering
  - [x] 2.1 Implement basic game loop with 60 FPS timing
    - Create main.py with game loop
    - Implement delta time calculation
    - Set up Pygame window (800x600 initial size)
    - Render light gray background
    - _Requirements: 1.3, 16.4, 16.6_

  - [x] 2.2 Implement Player entity and render as blue circle
    - Create Entity base class with position and radius
    - Create Player class extending Entity
    - Render player as blue circle at center of screen
    - _Requirements: 1.5, 16.1_

  - [x]* 2.3 Write unit tests for Entity and Player classes
    - Test entity initialization with position
    - Test player default attributes (radius, speed)
    - _Requirements: 1.5, 16.1_

- [x] 3. Implement player movement with WASD controls
  - [x] 3.1 Implement input handling system
    - Create InputHandler class to process keyboard events
    - Map WASD keys to movement directions
    - Implement F3 key toggle for debug display
    - _Requirements: 1.1, 15.1_

  - [x] 3.2 Implement Player.move() method with smooth movement
    - Add velocity-based movement using delta time
    - Implement movement in continuous coordinate space
    - Clamp player position to world boundaries
    - _Requirements: 1.1, 1.2, 1.3_

  - [x]* 3.3 Write property test for smooth continuous movement
    - **Property 1: Smooth Continuous Movement**
    - **Validates: Requirements 1.2, 3.6**
    - Test that player position remains in continuous space (not grid-aligned)
    - _Requirements: 1.2, 3.6_

  - [x] 3.4 Implement debug display (F3 toggle)
    - Display FPS counter
    - Display player position coordinates
    - Toggle visibility with F3 key
    - _Requirements: 15.1, 15.2, 15.3_

- [x] 4. Implement grid system for world organization
  - [x] 4.1 Create GridSystem class with coordinate conversion
    - Implement world_to_grid() coordinate conversion
    - Implement grid_to_world() coordinate conversion
    - Set cell_size to 1.0 unit
    - Create occupancy dictionary for spatial queries
    - _Requirements: 3.1, 3.3_

  - [x] 4.2 Implement spatial query methods
    - Implement is_occupied() for collision detection
    - Implement get_neighbors() for 4-directional adjacency
    - _Requirements: 3.3, 3.4_

  - [x]* 4.3 Write unit tests for grid coordinate conversion
    - Test world_to_grid() with various positions
    - Test grid_to_world() returns cell centers
    - Test round-trip conversion accuracy
    - _Requirements: 3.1_

- [x] 5. Create WorldObject base class and berry bush
  - [x] 5.1 Implement WorldObject base class
    - Extend Entity with width and height (grid cells)
    - Add inventory dictionary for resource storage
    - Implement get_occupied_cells() method
    - Add interact() method (to be overridden by subclasses)
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 5.2 Create BerryBush class as first world object
    - Extend WorldObject with 1x1 dimensions
    - Initialize with berries in inventory
    - Render as green square aligned to grid
    - _Requirements: 4.6, 16.3_

  - [x] 5.3 Implement World class to manage entities
    - Create World container with entity lists
    - Implement add_object() to register objects in grid
    - Implement remove_object() to unregister from grid
    - Place test berry bush in world
    - _Requirements: 3.3, 4.4_

  - [x]* 5.4 Write property test for grid occupation by dimensions
    - **Property 2: Grid Occupation by Dimensions**
    - **Validates: Requirements 3.2, 5.6**
    - Test that W×H object occupies exactly W×H cells
    - _Requirements: 3.2, 5.6_

  - [x]* 5.5 Write property test for grid cell mutual exclusion
    - **Property 3: Grid Cell Mutual Exclusion**
    - **Validates: Requirements 3.4, 5.5**
    - Test that occupied cells prevent new placements
    - _Requirements: 3.4, 5.5_

- [x] 6. Implement collision detection between player and world objects
  - [x] 6.1 Implement collision detection in Player.move()
    - Check grid cells in movement direction
    - Prevent movement into occupied cells
    - Use circular collision boundaries
    - _Requirements: 1.4, 1.5_

  - [x]* 6.2 Write property test for collision detection circularity
    - **Property 4: Collision Detection Circularity**
    - **Validates: Requirements 1.5**
    - Test distance-based collision with circular boundaries
    - _Requirements: 1.5_

  - [x]* 6.3 Write property test for movement collision response
    - **Property 5: Movement Collision Response**
    - **Validates: Requirements 1.4**
    - Test that player stops when colliding with obstacles
    - _Requirements: 1.4_

- [x] 7. Implement player interaction with world objects
  - [x] 7.1 Implement Player.interact() method
    - Find nearest object within interaction radius (1.5 × player radius)
    - Call object's interact() method
    - Handle 'E' key press for interaction
    - _Requirements: 2.1, 2.2_

  - [x] 7.2 Implement BerryBush.interact() to transfer resources
    - Transfer one berry from bush to player inventory
    - Remove berry from bush inventory
    - Return success/failure status
    - _Requirements: 2.3_

  - [x] 7.3 Write property test for interaction targeting nearest object
    - **Property 6: Interaction Targets Nearest Object**
    - **Validates: Requirements 2.1**
    - Test that interact() selects minimum distance object
    - _Requirements: 2.1_

  - [x] 7.4 Write property test for resource transfer conservation
    - **Property 7: Resource Transfer Conservation**
    - **Validates: Requirements 2.3**
    - Test that total resources remain constant during transfer
    - _Requirements: 2.3_

  - [x] 7.5 Write unit test for interaction radius constant
    - Verify player.interaction_radius == 1.5 × player.radius
    - _Requirements: 2.2_

- [x] 8. Implement inventory system
  - [x] 8.1 Create Inventory class with resource management
    - Implement add() method for adding resources
    - Implement remove() method with validation
    - Implement has() method to check availability
    - Support optional capacity limits (None for infinite)
    - _Requirements: 2.5_

  - [x] 8.2 Integrate Inventory into Player and WorldObject
    - Replace dictionary with Inventory instance
    - Set player inventory to infinite capacity
    - Update resource transfer to use Inventory methods
    - _Requirements: 2.5_

  - [x] 8.3 Write property test for inventory unbounded capacity
    - **Property 8: Inventory Unbounded Capacity**
    - **Validates: Requirements 2.5**
    - Test that player inventory never fails due to capacity
    - _Requirements: 2.5_

- [x] 9. Implement building system and Gathering Hut
  - [x] 9.1 Create Building base class
    - Extend WorldObject with cost dictionary
    - Implement can_place() validation method
    - _Requirements: 5.5, 5.7_

  - [x] 9.2 Create GatheringHut class
    - Set dimensions to 3×3 grid cells
    - Initialize storage inventory
    - Add assigned_critters list
    - Set gathering_radius to 10.0 grid cells
    - _Requirements: 6.1, 6.2, 6.3, 6.5_

  - [x] 9.3 Implement building placement UI
    - Create BuildMenu class to display available buildings
    - Handle 'B' key to toggle build menu
    - Implement building selection (keyboard shortcuts)
    - Implement placement mode with mouse click
    - Validate placement location and resources
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 9.4 Implement resource deduction on building placement
    - Check player inventory for required resources
    - Deduct cost from player inventory on successful placement
    - Display error message if insufficient resources
    - _Requirements: 5.7_

  - [x] 9.5 Write property test for building placement resource deduction
    - **Property 9: Building Placement Resource Deduction**
    - **Validates: Requirements 5.7, 14.4**
    - Test that inventory decreases by exactly building cost
    - _Requirements: 5.7, 14.4_

  - [x] 9.6 Write unit test for gathering hut dimensions
    - Verify GatheringHut has width=3 and height=3
    - _Requirements: 6.1_

- [x] 10. Checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify player can move, collide, interact, and place buildings
  - Ask user if questions arise before proceeding to Phase 2


## Phase 2: The First Critter

- [x] 11. Implement Critter entity with stats
  - [x] 11.1 Create CritterState enum
    - Define IDLE, GATHER, and RETURN states
    - _Requirements: 7.1_

  - [x] 11.2 Create Critter class with base stats
    - Extend Entity with radius=0.4
    - Add strength, speed_stat, endurance attributes (1-100 range)
    - Add state attribute (default IDLE)
    - Add assigned_hut, target_resource, held_resource attributes
    - Add is_well_fed boolean flag
    - Render as red circle
    - _Requirements: 7.1, 8.1, 8.2, 16.2_

  - [x] 11.3 Implement stat-based behavior methods
    - Implement get_movement_speed() based on speed_stat
    - Implement get_gather_speed() based on strength
    - Apply 1.1× multiplier when is_well_fed is True
    - _Requirements: 8.3, 8.4, 8.6_

  - [x]* 11.4 Write property test for stat bounds
    - **Property 17: Stat Bounds**
    - **Validates: Requirements 8.2**
    - Test that all stats remain in [1, 100] range
    - _Requirements: 8.2_

  - [x]* 11.5 Write property tests for stat monotonicity
    - **Property 18: Strength Affects Gather Speed Monotonically**
    - **Property 19: Speed Stat Affects Movement Speed Monotonically**
    - **Property 20: Endurance Affects Idle Duration Monotonically**
    - **Validates: Requirements 8.3, 8.4, 8.5**
    - Test that higher stats produce higher performance
    - _Requirements: 8.3, 8.4, 8.5_

  - [x]* 11.6 Write property test for well-fed buff multiplier
    - **Property 21: Well-Fed Buff Multiplier**
    - **Validates: Requirements 8.6**
    - Test that well-fed applies 1.1× multiplier, capped at 100
    - _Requirements: 8.6_

  - [x]* 11.7 Write unit test for critter state machine states
    - Verify CritterState enum has IDLE, GATHER, RETURN
    - _Requirements: 7.1_

  - [x]* 11.8 Write unit test for critter stat attributes
    - Verify Critter has strength, speed, endurance attributes
    - _Requirements: 8.1_

- [x] 12. Implement Critter assignment to Gathering Hut
  - [x] 12.1 Implement GatheringHut.assign_critter() method
    - Add critter to assigned_critters list
    - Set critter.assigned_hut reference to this hut
    - Support unlimited assignments
    - _Requirements: 6.3, 6.4_

  - [x]* 12.2 Write property test for critter assignment establishes home reference
    - **Property 10: Critter Assignment Establishes Home Reference**
    - **Validates: Requirements 6.4**
    - Test that assigned critter references the hut
    - _Requirements: 6.4_

  - [x]* 12.3 Write property test for gathering hut unbounded assignment
    - **Property 11: Gathering Hut Unbounded Assignment**
    - **Validates: Requirements 6.3**
    - Test that any number of critters can be assigned
    - _Requirements: 6.3_

- [x] 13. Implement A* pathfinding system
  - [x] 13.1 Create PathfindingSystem class
    - Implement A* algorithm with Manhattan heuristic
    - Use grid occupancy for obstacle detection
    - Return list of grid coordinates as path
    - _Requirements: 3.7_

  - [x] 13.2 Add path caching for performance
    - Cache paths by (start, goal) tuple
    - Implement invalidate_cache() for world changes
    - _Requirements: N/A (performance optimization)_

  - [x]* 13.3 Write unit tests for pathfinding
    - Test path finding with no obstacles
    - Test path finding around obstacles
    - Test pathfinding failure when no path exists
    - _Requirements: 3.7_

- [x] 14. Implement Critter AI state machine
  - [x] 14.1 Implement IDLE state behavior
    - Critter remains at assigned hut position
    - After idle duration, transition to GATHER
    - Display "IDLE" label above critter
    - _Requirements: 7.2_

  - [x] 14.2 Implement GATHER state behavior
    - Select random resource within gathering radius on entry
    - Pathfind to target resource
    - Move along path toward resource
    - Collect resource when reached
    - Transition to RETURN after collection
    - Display "GATHER" label above critter
    - _Requirements: 7.3, 7.4, 7.5_

  - [x] 14.3 Implement RETURN state behavior
    - Pathfind back to assigned hut
    - Move along path toward hut
    - Deposit held resource to hut storage on arrival
    - Transition to IDLE after deposit
    - Display "RETURN" label above critter
    - _Requirements: 7.6, 7.7, 6.2_

  - [x] 14.4 Implement Critter.update() to run state machine
    - Call appropriate state handler based on current state
    - Update movement along path
    - Handle state transitions
    - _Requirements: 7.1_

  - [x] 14.5 Implement GatheringHut.find_resource_in_radius()
    - Search world objects within gathering_radius
    - Return random resource-bearing object
    - _Requirements: 6.5, 7.3_

  - [x]* 14.6 Write property test for IDLE state spatial constraint
    - **Property 12: IDLE State Spatial Constraint**
    - **Validates: Requirements 7.2**
    - Test that IDLE critters stay near their hut
    - _Requirements: 7.2_

  - [x]* 14.7 Write property test for GATHER target within radius
    - **Property 13: GATHER Target Within Radius**
    - **Validates: Requirements 7.3**
    - Test that selected targets are within gathering radius
    - _Requirements: 7.3_

  - [x]* 14.8 Write property test for resource collection triggers RETURN
    - **Property 14: Resource Collection Triggers RETURN**
    - **Validates: Requirements 7.5**
    - Test that collecting resource transitions to RETURN
    - _Requirements: 7.5_

  - [x]* 14.9 Write property test for RETURN navigation to hut
    - **Property 15: RETURN Navigation to Hut**
    - **Validates: Requirements 7.6**
    - Test that distance to hut decreases over time
    - _Requirements: 7.6_

  - [x]* 14.10 Write property test for deposit completes cycle
    - **Property 16: Deposit Completes Cycle**
    - **Validates: Requirements 7.7, 6.2**
    - Test that deposit transfers resource and returns to IDLE
    - _Requirements: 7.7, 6.2_

- [x] 15. Add UI for state labels above critters
  - Render current state text above each critter
  - Use different colors for different states
  - _Requirements: 7.8_

- [x] 16. Checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify critters can be assigned and autonomously gather resources
  - Test complete IDLE→GATHER→RETURN cycle
  - Ask user if questions arise before proceeding to Phase 3


## Phase 3: World Simulation & Growth

- [x] 17. Implement resource regeneration system
  - [x] 17.1 Add regeneration timer to resource objects
    - Add depleted flag and respawn_timer to WorldObject
    - Track time since depletion
    - _Requirements: 9.1_

  - [x] 17.2 Implement tree regrowth logic
    - When tree inventory reaches zero, mark as depleted
    - Start respawn timer (configurable duration)
    - Replenish inventory when timer expires
    - _Requirements: 9.1_

  - [x]* 17.3 Write property test for tree regeneration after depletion
    - **Property 22: Tree Regeneration After Depletion**
    - **Validates: Requirements 9.1**
    - Test that depleted trees eventually respawn
    - _Requirements: 9.1_

- [x] 18. Implement grass propagation system
  - [x] 18.1 Create Grass world object type
    - Extend WorldObject with 1×1 dimensions
    - Implement spread logic to adjacent cells
    - _Requirements: 9.2_

  - [x] 18.2 Implement grass spreading over time
    - Check adjacent empty cells periodically
    - Create new grass in random empty neighbor
    - _Requirements: 9.2_

  - [x]* 18.3 Write property test for grass propagation to empty neighbors
    - **Property 23: Grass Propagation to Empty Neighbors**
    - **Validates: Requirements 9.2**
    - Test that grass spreads to adjacent empty cells
    - _Requirements: 9.2_

- [x] 19. Implement path trampling system
  - [x] 19.1 Track traversal frequency in World
    - Add trampled_cells set to MapData
    - Increment traversal counter when entities move through cells
    - Mark cells as trampled above threshold
    - _Requirements: 9.3_

  - [x] 19.2 Prevent grass growth on trampled cells
    - Check trampled status before grass spreading
    - Block grass creation on tramppled cells
    - _Requirements: 9.4_

  - [x] 19.3 Implement trampled status decay
    - Decrease traversal counter over time
    - Remove trampled status when counter reaches zero
    - _Requirements: 9.5_

  - [x]* 19.4 Write property test for trampling prevents grass growth
    - **Property 24: Trampling Prevents Grass Growth**
    - **Validates: Requirements 9.4**
    - Test that trampled cells block grass growth
    - _Requirements: 9.4_

- [x] 20. Implement work obstacles
  - [x] 20.1 Create Obstacle class
    - Extend WorldObject with work_units attribute
    - Track remaining work required to clear
    - Block movement while work_units > 0
    - _Requirements: 10.1, 10.5_

  - [x] 20.2 Implement work application from critters
    - Calculate work applied based on critter strength
    - Decrease obstacle work_units on interaction
    - Remove obstacle when work_units reaches zero
    - _Requirements: 10.2, 10.3_

  - [x] 20.3 Display remaining work units on obstacles
    - Render work_units value above obstacle
    - _Requirements: 10.4_

  - [x]* 20.4 Write property test for obstacle work unit depletion
    - **Property 25: Obstacle Work Unit Depletion**
    - **Validates: Requirements 10.2**
    - Test that work_units decrease by strength-based function
    - _Requirements: 10.2_

  - [x]* 20.5 Write property test for obstacle removal at zero work units
    - **Property 26: Obstacle Removal at Zero Work Units**
    - **Validates: Requirements 10.3, 10.5**
    - Test that obstacles are removed and unblock movement
    - _Requirements: 10.3, 10.5_

  - [x]* 20.6 Write unit test for obstacle work units attribute
    - Verify Obstacle has work_units attribute
    - _Requirements: 10.1_

- [x] 21. Checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify resource regeneration, grass spreading, trampling, and obstacles work
  - Ask user if questions arise before proceeding to Phase 4


## Phase 4: Breeding & Scaling

- [x] 22. Implement Mating Hut building
  - [x] 22.1 Create MatingHut class
    - Extend Building with 2×2 dimensions
    - Add assigned_critters list
    - _Requirements: 11.1_

  - [x] 22.2 Implement critter assignment to Mating Hut
    - Reuse assignment pattern from Gathering Hut
    - Support multiple critter assignments
    - _Requirements: 11.1_

- [x] 23. Implement critter breeding mechanics
  - [x] 23.1 Implement MatingHut.breed() method
    - Require at least two assigned critters
    - Calculate offspring stats from parent averages
    - Apply random mutations to offspring stats ( ±5 )
    - Clamp offspring stats to [1, 100] range
    - _Requirements: 11.2, 11.3, 11.4, 11.5_

  - [x] 23.2 Initialize offspring at Mating Hut
    - Set offspring position to hut center
    - Set offspring state to IDLE
    - Add offspring to world
    - Set assigned_hut reference
    - _Requirements: 11.6_

  - [x]* 23.3 Write property test for offspring stat inheritance (Property 27)
    - Test that offspring stats equal rounded parent averages plus mutation
    - _Requirements: 11.2, 11.3_

  - [x]* 23.4 Write property test for offspring stat bounds after mutation (Property 28)
    - Test that mutated stats remain within [1, 100]
    - _Requirements: 11.5_

  - [x]* 23.5 Write property test for offspring initial state (Property 29)
    - Test that offspring start in IDLE at hut center location
    - _Requirements: 11.6_

- [x] 24. Implement building buff system
  - [x] 24.1 Create Buff data class
    - Add name, stat_multiplier, duration, remaining attributes
    - Implement update() method to decrease timer
    - _Requirements: 12.3_

  - [x] 24.2 Create Chair and Campfire buildings
    - Implement Chair with Rested buff (movement speed)
    - Implement Campfire with Strength buff
    - _Requirements: 12.1, 12.2_

  - [x] 24.3 Implement buff application on interaction
    - Add active_buffs list to Player
    - Apply buff when interacting with Chair/Campfire
    - Update buffs each frame to decrease timers
    - Remove expired buffs
    - _Requirements: 12.1, 12.2, 12.3_

  - [x] 24.4 Display active buffs to player
    - Render buff names and remaining time
    - _Requirements: 12.4_

  - [x]* 24.5 Write property test for buff expiration (Property 30)
    - Test that buffs expire after duration
    - _Requirements: 12.3_

  - [x]* 24.6 Write unit tests for Chair and Campfire buff application
    - Test Chair adds Rested buff
    - Test Campfire adds Strength buff
    - _Requirements: 12.1, 12.2_
       
- [x] 25. Implement Berry Economy UI
  - [x] 25.1 Design HUD layout for resources
    - Plan top-left corner, left-aligned horizontal layout for multiple resources
    - Each resource shows: icon (colored square for now) + count
    - Position with margin from top-left corner
    - _Requirements: UI layout, scalability_
  - [x] 25.2 Implement Gathering Hut withdraw interaction (E key)
    - Add get_interaction_text() to GatheringHut: show prompt when storage has items
    - Implement interact() on GatheringHut: transfer all storage contents to player inventory
    - After interaction, clear hut storage
    - _Requirements: economy loop, player agency_
  - [x] 25.3 Render food (berry) count in HUD
    - Draw red square (15×15 px?) as icon
    - Display "Food: X" where X = player.inventory.get("food", 0)
    - Update every frame based on player inventory
    - _Requirements: HUD rendering, inventory integration_
  - [x] 25.4 Ensure all resource-modifying actions update HUD
    - Player picking berries: HUD updates automatically via inventory change
    - Withdrawing from Gathering Hut: when player takes resources, inventory changes → HUD updates
    - Spending resources (breeding/crafting): deduct from player inventory → HUD updates
    - _Requirements: real-time synchronization_
  - [x]* 25.5 Write unit test for HUD shows correct inventory count
    - Test that HUD displays player.inventory.get("food") correctly
    - Simulate inventory changes (add/remove) and verify HUD updates
    - _Requirements: UI consistency_
  - [x]* 25.6 Write property test for HUD reflects only player inventory
    - Validate HUD does NOT reflect critter or building inventories
    - _Requirements: scope clarity_
       
- [x] 26. Checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify breeding mechanics, buff system, and berry economy UI work correctly
  - Ask user if questions arise before proceeding to Phase 5


## Phase 5: Equipment & Crafting

- [x] 27. Implement equipment system
  - [x] 27.1 Create Equipment tracking in Player
    - Add unlocked_equipment set to track unlocked items
    - Add equipped set to track currently equipped items
    - _Requirements: 13.1, 13.2_

  - [x] 27.2 Implement equipment effects on gathering
    - Modify gathering speed when equipment is equipped
    - Apply multiplier to player gather actions
    - _Requirements: 13.3_

  - [x]* 27.3 Write property test for equipment unlock enables equipping (Property 31)
    - Test that unlocked equipment can be equipped
    - _Requirements: 13.2_

  - [x]* 27.4 Write property test for equipped gathering tool increases speed (Property 32)
    - Test that equipped tools improve gathering speed
    - _Requirements: 13.3_

- [x] 28. Implement crafting system
  - [x] 28.1 Create Recipe data class
    - Define name, result, cost, unlocks_equipment attributes
    - _Requirements: 14.2_

  - [x] 28.2 Create CraftingMenu UI
    - Display available recipes
    - Show required resources for each recipe
    - Handle recipe selection via number keys (1-9)
    - Render overlay and craft result messages
    - _Requirements: 14.1, 14.2_

  - [x] 28.3 Implement crafting logic
    - Validate player has sufficient resources
    - Deduct resources from player inventory
    - Unlocks equipment when recipe.unlocks_equipment is True
    - Display success or error message
    - _Requirements: 14.3, 14.4_

  - [x]* 28.4 Write property test for crafting success with sufficient resources (Property 33)
    - Test that crafting succeeds when resources available
    - Includes hypothesis property test for sufficiency condition
    - _Requirements: 14.3_

- [x] 29. Checkpoint - Ensure all tests pass
  - Run all unit tests and property tests
  - Verify equipment and crafting systems work correctly
  - Ask user if questions arise before proceeding to Phase 6


## Phase 6: Multi-Map World & Persistence

- [x] 30. Implement multi-map world system
  - [x] 30.1 Extend World to support multiple maps
    - Create MapData class for individual map regions
    - Store maps in dictionary by name
    - Track current_map
    - _Requirements: 3.5, 18.1_

  - [x] 30.2 Implement map transitions
    - Detect when player reaches map boundary
    - Transition to adjacent map
    - Update current_map reference
    - _Requirements: 18.2_

  - [x] 30.3 Implement entity state preservation across maps
    - Only update entities in current map
    - Preserve entity state when switching maps
    - _Requirements: 18.3, 18.4_

  - [x]* 30.4 Write property test for map transition at boundary
    - **Property 35: Map Transition at Boundary**
    - **Validates: Requirements 18.2**
    - Test that crossing boundary changes current_map
    - _Requirements: 18.2_

  - [x]* 30.5 Write property test for inactive map entity preservation
    - **Property 36: Inactive Map Entity Preservation**
    - **Validates: Requirements 18.4**
    - Test that entities maintain state across map transitions
    - _Requirements: 18.4_

- [x] 31. Implement save/load system
  - [x] 31.1 Create SaveData class
    - Define structure for complete game state
    - Include version field for compatibility
    - _Requirements: 17.1, 17.2, 17.3, 17.4_

  - [x] 31.2 Implement serialization methods
    - Implement to_dict() for all entity classes
    - Implement from_dict() class methods for deserialization
    - Implement SaveData.to_json() for file writing
    - _Requirements: 17.1, 17.2, 17.3, 17.4_

  - [x] 31.3 Implement save functionality
    - Collect all game state into SaveData
    - Serialize to JSON
    - Write to save file
    - Handle file system errors gracefully
    - _Requirements: 17.1, 17.2, 17.3, 17.4_

  - [x] 31.4 Implement load functionality
    - Read save file
    - Parse JSON to SaveData
    - Restore all game state
    - Handle missing/corrupted save files
    - _Requirements: 17.5_

  - [x]* 31.5 Write property test for save/load round trip preservation
    - **Property 34: Save/Load Round Trip Preservation**
    - **Validates: Requirements 17.1, 17.2, 17.3, 17.4**
    - Test that save→load preserves all game state
    - _Requirements: 17.1, 17.2, 17.3, 17.4_

- [x] 32. Final checkpoint - Ensure all tests pass
  - Run complete test suite (all unit and property tests)
  - Verify multi-map transitions work correctly
  - Verify save/load preserves game state
  - Test complete gameplay loop from start to finish
  - Ask user if questions arise

## Phase 7: Polish & Additional Content

- [x] 33. Add additional world object types
  - [x] 33.1 Create Tree world object
    - Extend WorldObject with appropriate dimensions
    - Initialize with wood resources
    - Implement interaction to harvest wood
    - _Requirements: 4.6_

  - [x] 33.2 Create Rock world object
    - Extend WorldObject with appropriate dimensions
    - Initialize with stone resources
    - Implement interaction to harvest stone
    - _Requirements: 4.6_

  - [x] 33.3 Create Stick world object
    - Extend WorldObject as small collectible
    - Initialize with plant resources
    - _Requirements: 4.6_

  - [x]* 33.4 Write unit test for object type instantiation
    - Verify all object types can be instantiated
    - _Requirements: 4.6_

- [x] 34. Enhance rendering with simple animations
  - [x] 34.1 Implement 2-frame sprite animation for critters
    - Create idle animation (2 frames)
    - Create action animation (2 frames)
    - Alternate frames based on state
    - _Requirements: 16.5_

- [x] 35. Add additional UI and polish
  - [x] 35.1 Implement inventory display UI
    - Show player resources
    - Update in real-time
    - _Requirements: N/A (UI enhancement)_

  - [x] 35.2 Enhance debug display
    - Add critter count
    - Add building count
    - Add performance metrics
    - _Requirements: 15.4_

- [x] 36. Final integration and testing
  - Run complete test suite one final time
  - Perform manual playtesting of all features
  - Verify all requirements are met
  - Document any known issues or future enhancements

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and provide opportunities for user feedback
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples, edge cases, and integration points
- All code should be committed to feature branches and merged after tests pass
- The phased approach ensures basic functionality works before adding complexity
- Graphics start minimal (circles and squares) to focus on core mechanics first

## Git Workflow

For each task or group of related tasks:
1. Create a feature branch from mainline (e.g., `feature/player-movement`)
2. Implement the task(s)
3. Write and run tests (if not marked optional)
4. Ensure all tests pass
5. Commit changes with descriptive messages
6. Merge back to mainline
7. Delete feature branch

## Testing Guidelines

- Use pytest for running all tests
- Use Hypothesis for property-based tests with minimum 100 iterations
- Property tests must include comment tags: `# Feature: critters-game-prototype, Property {N}: {title}`
- Run tests frequently during development
- All tests must pass before merging to mainline
- Optional tests (marked with `*`) can be skipped but are recommended for robustness

## Dependencies

Required Python packages:
- pygame >= 2.5.0 (rendering and input)
- pytest >= 7.4.0 (unit testing)
- hypothesis >= 6.82.0 (property-based testing)

Install with: `pip install pygame pytest hypothesis`


## Phase 9: Companion & Follow System

**Goal**: Add a "Follow" button to the critter inspector to make a critter follow the player and enable quick assignment to buildings.

### Task 45: Implement Critter Follow & Assign Feature
**Priority**: Medium
**Status**: COMPLETED (2026-04-05)

Implementation:
- Added FOLLOW state to Critter; start_follow/stop_follow manage exclusive following.
- Follow movement: every `follow_recalc_interval` (1s), pick a random free cell within 2-3 tiles of player; move directly toward it.
- CritterInspector: added "Follow"/"Stop Following" button; also shows assignment status; assignment via E press continues to work.
- Hut interactions already check `player.following_critter`; now also call `critter.stop_follow()` on assignment.
- Tests: 5 new follow tests in `tst/test_critter.py`; all 221 tests pass.

Acceptance satisfied: Player can select a critter and toggle Follow; critter trails player; interacting with a hut while following assigns that critter.
- The critter then moves to stay near the player, updating its destination periodically
- When the player presses E on a building, the following critter becomes assigned to that building
- The inspector updates to show the new assignment
- Tests added and passing

---

## Phase 10: Code Structure & Maintainability

**Goal**: Improve code structure, separation of concerns, and maintainability.

### Task 46: Refactor Game State Management into Dedicated Module
**Priority**: Medium
**Status**: NOT_STARTED

**Description**:
Refactor the game state management logic (loading and starting a new game) into a dedicated module, `game_state.py`. This will improve separation of concerns and reusability.

**Acceptance Criteria**:
- Create a new module `src/game_state.py` with functions:
  - `load_game(save_path)`: Loads a saved game and returns `(world, player)`.
  - `new_game()`: Starts a new game and returns `(world, player)`.
- Update `TitleScreen` to use `game_state.load_game` for the Continue action.
- Update `main.py` to use `game_state.load_game` and `game_state.new_game` based on `selected_action`.
- Ensure all existing tests pass after refactoring.
- Update any relevant documentation.

**Design Notes**:
- The `TitleScreen` class should remain focused on UI and action selection.
- The `main.py` loop should remain focused on running the game.
- The new `game_state.py` module should encapsulate all game initialization logic.

---


## Phase 8: Missing Features & Polish

**Goal**: Address gaps identified during QA to bring the prototype to full feature parity with the original design vision.

### Task 37: Implement Building Costs
**Priority**: High
**Status**: COMPLETED (2026-04-05)

Implementation:
- Defined building costs: GatheringHut (wood=10, stone=5), Chair (wood=2), Campfire (wood=5, stone=2), MatingHut (wood=15, stone=10)
- Updated subclasses to pass costs to `Building.__init__`
- BuildMenu displays costs on buttons and enforces resource deduction on placement
- Added unit tests verifying correct deduction and rejection when resources insufficient

All tests pass at completion.

Acceptance satisfied: Buildings now require resources; costs are visible; placement respects affordability; tests cover behavior.

### Task 38: Add Second Map and Enable Travel
**Priority**: High
**Status**: COMPLETED (2026-04-05)

Implementation:
- Created second `MapData` "north_woods" with resources and a GatheringHut
- Registered map with world and configured neighbor links (main.north → north_woods, north_woods.south → main)
- Verified boundary crossing triggers map transitions and entity state is preserved
- Added tests for map switching and state preservation

All tests pass.

Acceptance satisfied: Player can walk north to enter north_woods; second map contains resources; returning south restores main map with player position intact.

### Task 39: Complete Mating Hut Integration
**Priority**: Medium
**Status**: COMPLETED (2026-04-05)

Implementation:
- MatingHut cost already defined (wood=15, stone=10).
- Implemented `MatingHut.interact(player)` with food cost (5 food) and message feedback.
- Added world.message system and integrated into main.py.
- Created tests in `tst/test_breeding.py` (4 new tests).
- All tests pass (208).

Acceptance satisfied: player can press E on MatingHut with ≥2 assigned critters and enough food to breed; offspring appears; costs enforced; feedback shown.

### Task 40: Implement Critter Assignment UI
**Priority**: Medium
**Status**: COMPLETED (2026-04-05)

Implementation:
- Assignment via existing E interaction: When player has a `following_critter` and presses E near a hut (GatheringHut or MatingHut), the critter is assigned to that hut. Works for both hut types.
- Modified `Building.assign_critter` to auto-unassign from previous hut; both `GatheringHut.interact` and `MatingHut.interact` prioritize assignment when `player.following_critter` exists, else perform their normal actions (withdraw or breed).
- `CritterInspector` UI shows assignment status ("Assigned: <Hut>")
- Added tests for assignment flows in `tst/test_hud_and_hut.py` (`TestGatheringHutAssignmentViaInteract`) and `tst/test_breeding.py` (`TestMatingHutAssignmentViaInteract`)
- All 216 tests pass.

Acceptance satisfied: Player can select a critter via inspector, walk near a hut with 'E' to assign; unassign/reassign works by moving to another hut; tests cover these flows.

### Task 41: Balance and Testing
**Priority**: Medium
**Status**: COMPLETED (2026-04-05)

Verification:
- Playtested core loop: gather → build → assign via follow+E → withdraw → breed → travel.
- Building costs enforced & shown; assignment status visible.
- Test suite: 216/216 passing. No regressions.
- No critical balance issues; parameters within playable ranges.

---

## Phase 11: Critter Intelligence & UX Improvements

**Goal**: Improve critter autonomy and streamline the interaction flow for managing critters.

### Task 47: Improve Critter Gathering Intelligence
**Priority**: Medium
**Status**: COMPLETED (2026-04-25)

Implementation:
- Modified `_harvest_target` to accept `world`.
- Implemented `_continue_gathering_or_return` to seek new resources if capacity isn't full and the current resource is depleted.
- Critters now visit multiple bushes in one trip if they have space.
- Added regression test `test_critter_gathering_intelligence` in `tst/test_critter.py`.
- All 227 tests pass.

### Task 48: Streamline Follow Interaction with 'F' Key
**Priority**: Low
**Status**: NOT_STARTED

**Description**:
Add a keyboard shortcut 'F' that toggles follow status for the currently inspected critter and automatically closes the inspector menu.

**Acceptance Criteria**:
- In `src/input_handler.py`, detect 'F' key press.
- If `CritterInspector` is active and has a selected critter:
  - Toggle follow for that critter.
  - Close the `CritterInspector`.
- Ensure appropriate feedback messages are shown.

### Task 49: Direct Assignment via Right-Click
**Priority**: Medium
**Status**: NOT_STARTED

**Description**:
Allow players to assign a selected critter directly to a building by right-clicking the building while the critter's inspector is open. This bypasses the need for the "Follow" step.

**Acceptance Criteria**:
- In `main.py`, detect right-click events.
- If a critter is currently selected in `CritterInspector`:
  - Check if the right-click is over a `Building` (GatheringHut or MatingHut).
  - If yes, assign the selected critter to that building.
  - Show a feedback message (e.g., "Critter assigned to <Building>").
- This should work regardless of player distance to the building (since it's a UI-driven management action).

---

## Phase 12: World Expansion & Camera System

**Goal**: Make the game world feel larger and more open by increasing map size and implementing a scrolling camera that follows the player.

### Task 50: Implement Large Map and Scrolling Camera
**Priority**: High
**Status**: NOT_STARTED

**Description**:
Increase the map size and implement a camera system that follows the player, allowing for exploration of a world larger than the screen.

**Requirements**:
1. **Smaller Grid Size**: Reduce `cell_size` from 32 to a slightly smaller value (e.g., 24) to fit more on screen and feel more open.
2. **Larger Map Dimensions**: Increase map size to be 3x to 4x the current size (e.g., 80x60 or 100x75 grid cells).
3. **Scrolling Camera**:
   - Only show a subset of the map (viewport) at a time.
   - The camera should follow the player.
   - **Scroll Logic**: The camera stays still while the player is in the center 50% of the screen. When the player enters the outer 25% "deadzone" on any edge, the camera scrolls in that direction to keep the player within the center 50%.
   - **Boundary Clamping**: The camera should not scroll beyond the map boundaries.
4. **Coordinate Mapping**: Update all rendering and mouse interaction to correctly map between screen coordinates and world/grid coordinates using camera offsets.
5. **Preserve Mechanics**: Ensure critter navigation, pathfinding, and object placement remain functional and unaffected by the visual scrolling.

**Acceptance Criteria**:
- Map is significantly larger than the screen.
- Camera smoothly follows the player using the 25%/50%/25% deadzone logic.
- Mouse clicks for building placement, inspection, and deconstruction correctly target the world objects at their scrolled positions.
- All HUD elements (inventory, build buttons, active buffs) remain fixed to the screen.
- Debug display and interaction prompts correctly follow world objects.

---

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and provide opportunities for user feedback
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples, edge cases, and integration points
- All code should be committed to feature branches and merged after tests pass
- The phased approach ensures basic functionality works before adding complexity
- Graphics start minimal (circles and squares) to focus on core mechanics first
