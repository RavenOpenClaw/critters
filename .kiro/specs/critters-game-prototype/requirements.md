# Requirements Document

## Introduction

Critters is a creature collector incremental game with a focus on exploration, building, and simulation. The player explores a hand-crafted grid-based world to find resources and secrets, builds structures, and manages autonomous Critters that gather resources and perform work. The game features smooth player movement, manual resource gathering, building placement, Critter AI with stat-based behavior, resource regeneration, and breeding mechanics for progression.

## Glossary

- **Player**: The human-controlled character that can move, gather resources, craft items, and place buildings
- **Critter**: An autonomous AI-controlled creature that gathers resources and performs work tasks
- **Grid**: The discrete coordinate system where buildings and world objects are aligned
- **World_Object**: Any placeable entity in the world (trees, bushes, rocks, buildings) that occupies grid cells
- **Gathering_Hut**: A building that serves as a task hub for assigned Critters and stores collected resources
- **Resource**: Collectible materials (berries, wood, stone, plants) used for crafting and building
- **Work_Unit**: A measure of progress toward completing large-scale obstacles
- **State_Machine**: The AI system controlling Critter behavior (IDLE, GATHER, RETURN states)
- **Buff**: A temporary or persistent enhancement to character stats
- **Inventory**: The storage system for collected resources and items
- **Equipment**: Unlockable tools that enhance player capabilities
- **Mating_Hut**: A building where Critters can breed to produce offspring
- **Stat**: A numeric attribute (Strength, Speed, Endurance) affecting performance
- **Obstacle**: A large-scale blockage requiring significant Work_Units to clear

## Requirements

### Requirement 1: Player Movement

**User Story:** As a player, I want to move my character smoothly across the world, so that I can explore and interact with the environment.

#### Acceptance Criteria

1. WHEN the player presses WASD keys, THE Player SHALL move in the corresponding direction at a consistent speed
2. THE Player SHALL move smoothly across the grid without snapping to grid positions
3. THE Game SHALL render Player movement at 60 frames per second
4. WHEN the Player collides with a World_Object, THE Player SHALL stop movement in that direction
5. THE Player SHALL have a circular collision boundary for collision detection

### Requirement 2: Resource Gathering

**User Story:** As a player, I want to manually gather resources from world objects, so that I can collect materials for crafting and building.

#### Acceptance Criteria

1. WHEN the player presses the interact key (E) within interaction radius of a World_Object, THE Player SHALL attempt to interact with the nearest World_Object
2. THE Player SHALL have an interaction radius of approximately 1.5 times the Player collision radius
3. WHEN the Player interacts with a resource-bearing World_Object, THE World_Object SHALL transfer one resource to the Player Inventory
4. WHEN a resource is collected, THE Game SHALL convert the item into raw currency (food, wood, stone, or plants)
5. THE Player SHALL have infinite Inventory capacity

### Requirement 3: Grid-Based World

**User Story:** As a developer, I want a grid-based world system, so that objects can be placed consistently and pathfinding can be efficient.

#### Acceptance Criteria

1. THE Game SHALL organize the world using a discrete grid coordinate system
2. THE World_Object SHALL occupy one or more grid cells based on its dimensions
3. THE Game SHALL store World_Object positions in a dictionary indexed by grid coordinates
4. WHEN a World_Object occupies a grid cell, THE Game SHALL prevent other entities from occupying the same cell
5. THE Game SHALL divide the world into multiple maps that can be traveled between
6. THE Player SHALL move smoothly without grid alignment constraints
7. THE Critter SHALL use the grid for pathfinding calculations

### Requirement 4: World Objects

**User Story:** As a player, I want to interact with various world objects, so that I can gather different types of resources.

#### Acceptance Criteria

1. THE World_Object SHALL have dimensions defining grid space occupation
2. THE World_Object SHALL have an internal inventory that can hold items
3. THE World_Object SHALL have an interact function defining interaction behavior
4. WHEN a World_Object is placed, THE Game SHALL align it to the grid
5. THE World_Object SHALL provide collision boundaries for Player and Critter pathfinding
6. THE Game SHALL support multiple World_Object types (berry bushes, trees, rocks, grass, sticks)

### Requirement 5: Building Placement

**User Story:** As a player, I want to place buildings in the world, so that I can create structures that provide benefits and enable automation.

#### Acceptance Criteria

1. WHEN the player presses the build key (B), THE Game SHALL display the build menu
2. THE Build_Menu SHALL display available buildings with selection shortcuts
3. WHEN the player selects a building, THE Game SHALL enter building placement mode
4. WHEN the player clicks a grid location in placement mode, THE Game SHALL place the building at that location if valid
5. THE Game SHALL prevent building placement on occupied grid cells
6. THE Building SHALL occupy multiple grid cells based on its dimensions
7. THE Game SHALL deduct required resources from Player Inventory when placing a building

### Requirement 6: Gathering Hut

**User Story:** As a player, I want to build a Gathering Hut, so that I can assign Critters to automate resource collection.

#### Acceptance Criteria

1. THE Gathering_Hut SHALL occupy a 3x3 grid area
2. THE Gathering_Hut SHALL store resources deposited by assigned Critters
3. THE Gathering_Hut SHALL support assignment of multiple Critters
4. WHEN a Critter is assigned to a Gathering_Hut, THE Critter SHALL use the Gathering_Hut as its home base
5. THE Gathering_Hut SHALL define a gathering radius for assigned Critters

### Requirement 7: Critter AI State Machine

**User Story:** As a player, I want Critters to autonomously gather resources, so that I can automate resource collection.

#### Acceptance Criteria

1. THE Critter SHALL operate using a State_Machine with three states: IDLE, GATHER, and RETURN
2. WHEN in IDLE state, THE Critter SHALL remain at its assigned Gathering_Hut
3. WHEN transitioning from IDLE to GATHER, THE Critter SHALL identify a random resource within the gathering radius
4. WHEN in GATHER state, THE Critter SHALL pathfind to the target resource and collect it
5. WHEN a resource is collected, THE Critter SHALL transition to RETURN state
6. WHEN in RETURN state, THE Critter SHALL pathfind back to the Gathering_Hut
7. WHEN the Critter reaches the Gathering_Hut, THE Critter SHALL deposit the resource and transition to IDLE state
8. THE Game SHALL display the current state label above each Critter

### Requirement 8: Critter Stats

**User Story:** As a player, I want Critters to have individual stats, so that different Critters have varying performance characteristics.

#### Acceptance Criteria

1. THE Critter SHALL have three stats: Strength, Speed, and Endurance
2. THE Stat SHALL have a value range from 1 to 100
3. THE Strength stat SHALL determine work speed for gathering actions
4. THE Speed stat SHALL determine movement speed
5. THE Endurance stat SHALL determine food consumption frequency and IDLE duration
6. WHEN a Critter is Well_Fed, THE Game SHALL apply a 10% bonus to all Critter stats

### Requirement 9: Resource Regeneration

**User Story:** As a player, I want resources to regenerate over time, so that the world remains sustainable for long-term gameplay.

#### Acceptance Criteria

1. WHEN a tree is fully harvested, THE Game SHALL schedule the tree to regrow after a time period
2. THE Game SHALL spread grass to adjacent empty grid cells over time
3. WHEN a grid cell is frequently traversed, THE Game SHALL mark it as trampled
4. WHILE a grid cell is trampled, THE Game SHALL prevent grass regrowth on that cell
5. THE Game SHALL remove trampled status after a period without traversal

### Requirement 10: Work Obstacles

**User Story:** As a player, I want large-scale obstacles that require significant effort to clear, so that progression is gated and encourages building a larger workforce.

#### Acceptance Criteria

1. THE Obstacle SHALL require a specific number of Work_Units to clear
2. WHEN a Critter interacts with an Obstacle, THE Game SHALL apply Work_Units based on the Critter Strength stat
3. WHEN an Obstacle reaches zero remaining Work_Units, THE Game SHALL remove the Obstacle from the world
4. THE Game SHALL display remaining Work_Units for each Obstacle
5. THE Obstacle SHALL block Player and Critter movement until cleared

### Requirement 11: Critter Breeding

**User Story:** As a player, I want to breed Critters, so that I can create offspring with improved stats.

#### Acceptance Criteria

1. THE Mating_Hut SHALL enable breeding of assigned Critters
2. WHEN two Critters breed, THE Game SHALL create offspring Critter with inherited stats
3. THE Offspring SHALL inherit base stats from parent Critters
4. WHEN calculating offspring stats, THE Game SHALL apply a chance for random mutations
5. THE Stat mutation SHALL allow progression toward the maximum stat value of 100
6. THE Offspring SHALL start in IDLE state at the Mating_Hut

### Requirement 12: Building Buffs

**User Story:** As a player, I want buildings to provide buffs, so that I can enhance my character's capabilities.

#### Acceptance Criteria

1. WHEN the Player interacts with a Chair building, THE Game SHALL apply a Rested buff increasing movement speed
2. WHEN the Player interacts with a Campfire building, THE Game SHALL apply a Strength buff
3. THE Buff SHALL persist for a defined duration
4. THE Game SHALL display active buffs to the player

### Requirement 13: Equipment System

**User Story:** As a player, I want to craft and equip tools, so that I can improve my manual gathering efficiency.

#### Acceptance Criteria

1. THE Equipment SHALL be unlockable rather than inventory items
2. WHEN Equipment is unlocked, THE Player SHALL have the option to equip it
3. WHEN gathering Equipment is equipped, THE Player SHALL have increased gathering speed
4. THE Game SHALL track which Equipment items are unlocked and equipped

### Requirement 14: Crafting System

**User Story:** As a player, I want to craft items and equipment, so that I can create useful tools and structures.

#### Acceptance Criteria

1. THE Game SHALL provide a menu-based crafting interface
2. THE Crafting_Menu SHALL display available recipes and required resources
3. WHEN the player selects a recipe with sufficient resources, THE Game SHALL create the crafted item
4. THE Game SHALL deduct required resources from Player Inventory when crafting
5. THE Crafting system SHALL not require a physical crafting bench

### Requirement 15: Debug Information

**User Story:** As a developer, I want to toggle debug information, so that I can monitor game state during development.

#### Acceptance Criteria

1. WHEN the player presses F3, THE Game SHALL toggle debug information display
2. THE Debug_Display SHALL show frame rate information
3. THE Debug_Display SHALL show Player position coordinates
4. THE Debug_Display SHALL show relevant game state information

### Requirement 16: Visual Rendering

**User Story:** As a player, I want clear visual representation of game entities, so that I can understand the game state.

#### Acceptance Criteria

1. THE Game SHALL render the Player as a blue circle
2. THE Game SHALL render Critters as red circles
3. THE Game SHALL render berry bushes as green squares
4. THE Game SHALL render the world background as light gray
5. THE Game SHALL support simple 2-frame idle and action sprite animations for Critters
6. THE Game SHALL render at 60 frames per second

### Requirement 17: Persistence and Save System

**User Story:** As a player, I want my game progress to be saved, so that I can continue playing across sessions.

#### Acceptance Criteria

1. THE Game SHALL save Player position, inventory, and unlocked equipment
2. THE Game SHALL save all placed buildings and their states
3. THE Game SHALL save all Critters with their stats and assignments
4. THE Game SHALL save world state including resource availability
5. WHEN the game loads, THE Game SHALL restore all saved state

### Requirement 18: Multi-Map World

**User Story:** As a player, I want to travel between different map areas, so that I can explore a larger world.

#### Acceptance Criteria

1. THE Game SHALL divide the world into discrete map regions
2. WHEN the Player reaches a map boundary, THE Game SHALL transition to the adjacent map
3. THE Game SHALL only load and simulate entities in the current map
4. THE Game SHALL preserve entity states when transitioning between maps
