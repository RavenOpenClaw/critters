# Design Document: Critters Game Prototype

## Overview

The Critters game prototype is a Python-based creature collector incremental game featuring grid-based world management, smooth player movement, autonomous AI-controlled creatures, and resource gathering mechanics. The design prioritizes modularity, testability, and portability to enable future migration to other languages or game engines like Godot.

### Core Design Principles

1. **Separation of Concerns**: Game logic, rendering, and state management are decoupled
2. **Grid-Based Spatial Organization**: World objects align to a discrete grid for efficient spatial queries and pathfinding
3. **Smooth Continuous Movement**: Player and Critter movement operates in continuous space while respecting grid-based collision
4. **State Machine Architecture**: Critter AI uses explicit state machines for predictable, testable behavior
5. **Data-Driven Design**: Game entities are defined by data structures that can be easily serialized and ported

### Technology Stack

- **Language**: Python 3.10+
- **Rendering**: Pygame (chosen for simplicity and portability)
- **Pathfinding**: A* algorithm with grid-based navigation
- **Testing**: pytest for unit tests, Hypothesis for property-based testing
- **Serialization**: JSON for save/load functionality

## Architecture

### High-Level System Architecture

The game follows a layered architecture with clear boundaries between systems:

```
┌─────────────────────────────────────────────────────────┐
│                    Game Loop (Main)                      │
│  - Input handling                                        │
│  - Update cycle (60 FPS)                                 │
│  - Render cycle                                          │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Game State │   │   Renderer   │   │ Input Handler│
│              │   │              │   │              │
│ - World      │   │ - Sprites    │   │ - Keyboard   │
│ - Entities   │   │ - UI         │   │ - Mouse      │
│ - Resources  │   │ - Debug      │   │ - Events     │
└──────────────┘   └──────────────┘   └──────────────┘
        │
        ├─────────────┬─────────────┬─────────────┐
        ▼             ▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  World   │  │  Player  │  │ Critters │  │Buildings │
│  System  │  │  System  │  │  System  │  │  System  │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  Grid System │
                    │              │
                    │ - Spatial    │
                    │   queries    │
                    │ - Collision  │
                    │ - Pathfinding│
                    └──────────────┘
```

### Core Systems

#### 1. Game Loop System
- Manages the main update/render cycle at 60 FPS
- Processes input events
- Coordinates system updates in correct order
- Handles frame timing and delta time calculation

#### 2. World System
- Manages the grid-based world structure
- Handles multi-map organization and transitions
- Tracks world objects and their grid positions
- Manages resource regeneration and trampling mechanics

#### 3. Entity System
- Manages all game entities (Player, Critters, World_Objects, Buildings)
- Handles entity lifecycle (creation, update, destruction)
- Provides entity lookup and spatial queries

#### 4. Grid System
- Provides discrete coordinate system for spatial organization
- Maintains occupancy data structure for collision detection
- Supports efficient spatial queries (nearest object, path validation)
- Handles coordinate transformations between grid and world space

#### 5. Pathfinding System
- Implements A* pathfinding on the grid
- Caches paths for performance
- Handles dynamic obstacle updates
- Provides path smoothing for natural movement

#### 6. AI System
- Manages Critter state machines
- Coordinates task assignment and execution
- Handles resource gathering logic
- Manages Critter-to-building assignments

#### 7. Inventory System
- Tracks player and building resource storage
- Handles resource transfers between entities
- Provides infinite capacity for player inventory

#### 8. Building System
- Manages building placement validation
- Handles building interactions and buffs
- Coordinates Critter assignments to buildings
- Manages building-specific logic (Gathering_Hut, Mating_Hut)

#### 9. Crafting System
- Validates recipe requirements
- Handles resource consumption
- Unlocks equipment and buildings

#### 10. Save/Load System
- Serializes game state to JSON
- Restores game state from saved data
- Handles versioning for future compatibility

## Components and Interfaces

### Grid System

```python
class GridSystem:
    """Manages discrete grid coordinates and spatial queries."""
    
    def __init__(self, cell_size: float):
        self.cell_size = cell_size
        self.occupancy: Dict[Tuple[int, int], WorldObject] = {}
    
    def world_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        """Convert world coordinates to grid coordinates."""
        pass
    
    def grid_to_world(self, grid_x: int, grid_y: int) -> Tuple[float, float]:
        """Convert grid coordinates to world coordinates (cell center)."""
        pass
    
    def is_occupied(self, grid_x: int, grid_y: int) -> bool:
        """Check if a grid cell is occupied."""
        pass
    
    def get_neighbors(self, grid_x: int, grid_y: int) -> List[Tuple[int, int]]:
        """Get adjacent grid cells (4-directional)."""
        pass
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find A* path from start to goal."""
        pass
```

### Entity Base Class

```python
class Entity:
    """Base class for all game entities."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.radius = 0.0  # Collision radius
    
    def update(self, dt: float):
        """Update entity state."""
        pass
    
    def render(self, renderer):
        """Render entity to screen."""
        pass
    
    def to_dict(self) -> dict:
        """Serialize entity to dictionary."""
        pass
    
    @classmethod
    def from_dict(cls, data: dict):
        """Deserialize entity from dictionary."""
        pass
```

### Player System

```python
class Player(Entity):
    """Player character with smooth movement and interaction."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.radius = 0.5
        self.speed = 5.0  # Units per second
        self.interaction_radius = 1.5 * self.radius
        self.inventory: Dict[str, int] = {}
        self.equipped: Set[str] = set()
        self.active_buffs: List[Buff] = []
    
    def move(self, dx: float, dy: float, dt: float, world):
        """Move player with collision detection."""
        pass
    
    def interact(self, world) -> Optional[WorldObject]:
        """Find and interact with nearest object in range."""
        pass
    
    def add_resource(self, resource_type: str, amount: int):
        """Add resources to inventory."""
        pass
```

### World Object System

```python
class WorldObject(Entity):
    """Base class for objects placed in the world."""
    
    def __init__(self, x: float, y: float, width: int, height: int):
        super().__init__(x, y)
        self.width = width  # Grid cells
        self.height = height  # Grid cells
        self.inventory: Dict[str, int] = {}
        self.grid_cells: List[Tuple[int, int]] = []
    
    def interact(self, actor: Entity) -> bool:
        """Handle interaction from actor. Returns True if successful."""
        pass
    
    def get_occupied_cells(self, grid: GridSystem) -> List[Tuple[int, int]]:
        """Get all grid cells occupied by this object."""
        pass
```

### Critter AI System

```python
class CritterState(Enum):
    IDLE = "IDLE"
    GATHER = "GATHER"
    RETURN = "RETURN"

class Critter(Entity):
    """Autonomous AI-controlled creature."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
        self.radius = 0.4
        self.strength = 50  # 1-100
        self.speed_stat = 50  # 1-100
        self.endurance = 50  # 1-100
        self.state = CritterState.IDLE
        self.assigned_hut: Optional[GatheringHut] = None
        self.target_resource: Optional[WorldObject] = None
        self.held_resource: Optional[str] = None
        self.path: List[Tuple[int, int]] = []
        self.is_well_fed = False
    
    def update(self, dt: float, world):
        """Update state machine and movement."""
        pass
    
    def transition_to(self, new_state: CritterState):
        """Transition to new state with entry logic."""
        pass
    
    def get_movement_speed(self) -> float:
        """Calculate movement speed from speed stat."""
        multiplier = 1.1 if self.is_well_fed else 1.0
        return (self.speed_stat / 50.0) * 3.0 * multiplier
    
    def get_gather_speed(self) -> float:
        """Calculate gathering speed from strength stat."""
        multiplier = 1.1 if self.is_well_fed else 1.0
        return (self.strength / 50.0) * multiplier
```

### Building System

```python
class Building(WorldObject):
    """Base class for player-placed buildings."""
    
    def __init__(self, x: float, y: float, width: int, height: int):
        super().__init__(x, y, width, height)
        self.cost: Dict[str, int] = {}
    
    def can_place(self, grid: GridSystem) -> bool:
        """Check if building can be placed at current position."""
        pass

class GatheringHut(Building):
    """Building that coordinates Critter resource gathering."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, width=3, height=3)
        self.assigned_critters: List[Critter] = []
        self.gathering_radius = 10.0  # Grid cells
        self.storage: Dict[str, int] = {}
    
    def assign_critter(self, critter: Critter):
        """Assign a critter to this hut."""
        pass
    
    def find_resource_in_radius(self, world) -> Optional[WorldObject]:
        """Find a random resource within gathering radius."""
        pass

class MatingHut(Building):
    """Building that enables Critter breeding."""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, width=2, height=2)
        self.assigned_critters: List[Critter] = []
    
    def breed(self) -> Optional[Critter]:
        """Create offspring from two assigned critters."""
        pass
```

### Pathfinding System

```python
class PathfindingSystem:
    """A* pathfinding on grid."""
    
    def __init__(self, grid: GridSystem):
        self.grid = grid
        self.path_cache: Dict[Tuple[Tuple[int, int], Tuple[int, int]], List[Tuple[int, int]]] = {}
    
    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Find shortest path using A* algorithm."""
        pass
    
    def heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        """Manhattan distance heuristic."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def invalidate_cache(self):
        """Clear path cache when world changes."""
        pass
```

## Data Models

### Core Data Structures

#### Position
```python
@dataclass
class Position:
    x: float
    y: float
    
    def distance_to(self, other: 'Position') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
```

#### Stats
```python
@dataclass
class Stats:
    strength: int  # 1-100
    speed: int  # 1-100
    endurance: int  # 1-100
    
    def apply_buff(self, multiplier: float) -> 'Stats':
        """Return new stats with multiplier applied."""
        return Stats(
            strength=min(100, int(self.strength * multiplier)),
            speed=min(100, int(self.speed * multiplier)),
            endurance=min(100, int(self.endurance * multiplier))
        )
```

#### Inventory
```python
class Inventory:
    """Resource storage with optional capacity limit."""
    
    def __init__(self, capacity: Optional[int] = None):
        self.resources: Dict[str, int] = {}
        self.capacity = capacity
    
    def add(self, resource_type: str, amount: int) -> bool:
        """Add resources. Returns False if capacity exceeded."""
        pass
    
    def remove(self, resource_type: str, amount: int) -> bool:
        """Remove resources. Returns False if insufficient."""
        pass
    
    def has(self, resource_type: str, amount: int) -> bool:
        """Check if inventory contains amount of resource."""
        pass
```

#### Buff
```python
@dataclass
class Buff:
    name: str
    stat_multiplier: float
    duration: float  # Seconds
    remaining: float  # Seconds
    
    def update(self, dt: float) -> bool:
        """Update buff timer. Returns True if still active."""
        self.remaining -= dt
        return self.remaining > 0
```

#### Recipe
```python
@dataclass
class Recipe:
    name: str
    result: str
    cost: Dict[str, int]
    unlocks_equipment: bool = False
```

### World Data Model

```python
class World:
    """Container for all world state."""
    
    def __init__(self, width: int, height: int, cell_size: float):
        self.width = width
        self.height = height
        self.grid = GridSystem(cell_size)
        self.current_map = "main"
        self.maps: Dict[str, MapData] = {}
        self.player: Player = None
        self.critters: List[Critter] = []
        self.world_objects: List[WorldObject] = []
        self.buildings: List[Building] = []
    
    def update(self, dt: float):
        """Update all world systems."""
        pass
    
    def add_object(self, obj: WorldObject):
        """Add object to world and register in grid."""
        pass
    
    def remove_object(self, obj: WorldObject):
        """Remove object from world and grid."""
        pass

@dataclass
class MapData:
    """Data for a single map region."""
    name: str
    width: int
    height: int
    objects: List[WorldObject]
    critters: List[Critter]
    buildings: List[Building]
    trampled_cells: Set[Tuple[int, int]]
```

### Save Data Model

```python
@dataclass
class SaveData:
    """Complete game state for serialization."""
    version: str
    player_data: dict
    world_data: dict
    critters_data: List[dict]
    buildings_data: List[dict]
    objects_data: List[dict]
    current_map: str
    
    def to_json(self) -> str:
        """Serialize to JSON string."""
        pass
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SaveData':
        """Deserialize from JSON string."""
        pass
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property Reflection

After analyzing all acceptance criteria, I identified several areas of redundancy:

- Properties 1.2 and 3.6 both test smooth continuous movement (consolidated into Property 1)
- Properties 3.2 and 5.6 both test grid cell occupation by dimensions (consolidated into Property 2)
- Properties 3.4 and 5.5 both test mutual exclusion of grid cells (consolidated into Property 3)
- Properties 17.1-17.4 all test save/load round-trip behavior (consolidated into Property 28)
- Multiple stat-to-behavior relationships (8.3, 8.4, 8.5) can be tested together as monotonic properties

### Core Properties

### Property 1: Smooth Continuous Movement
*For any* player position and movement input, the player position should remain in continuous coordinate space (not quantized to grid cell boundaries).

**Validates: Requirements 1.2, 3.6**

### Property 2: Grid Occupation by Dimensions
*For any* world object with dimensions W × H, the object should occupy exactly W × H grid cells when placed.

**Validates: Requirements 3.2, 5.6**

### Property 3: Grid Cell Mutual Exclusion
*For any* grid cell occupied by a world object, attempting to place another object in that cell should fail.

**Validates: Requirements 3.4, 5.5**

### Property 4: Collision Detection Circularity
*For any* player position and world object, collision detection should use distance-based calculations consistent with circular boundaries (distance ≤ player.radius + object.radius).

**Validates: Requirements 1.5**

### Property 5: Movement Collision Response
*For any* player attempting to move into an occupied grid cell, the player position should not change in the direction of the obstacle.

**Validates: Requirements 1.4**

### Property 6: Interaction Targets Nearest Object
*For any* player position and set of world objects within interaction radius, the interact action should target the object with minimum distance to the player.

**Validates: Requirements 2.1**

### Property 7: Resource Transfer Conservation
*For any* player interaction with a resource-bearing world object, the total resources (player inventory + object inventory) should remain constant before and after the interaction.

**Validates: Requirements 2.3**

### Property 8: Inventory Unbounded Capacity
*For any* amount of resources added to player inventory, the addition should succeed (never fail due to capacity limits).

**Validates: Requirements 2.5**

### Property 9: Building Placement Resource Deduction
*For any* building placement with cost C, the player inventory should decrease by exactly C after successful placement.

**Validates: Requirements 5.7, 14.4**

### Property 10: Critter Assignment Establishes Home Reference
*For any* critter assigned to a gathering hut, the critter's assigned_hut reference should point to that hut.

**Validates: Requirements 6.4**

### Property 11: Gathering Hut Unbounded Assignment
*For any* number of critters assigned to a gathering hut, all assignments should succeed (no capacity limit).

**Validates: Requirements 6.3**

### Property 12: IDLE State Spatial Constraint
*For any* critter in IDLE state with an assigned hut, the critter position should remain within a small radius of the hut position.

**Validates: Requirements 7.2**

### Property 13: GATHER Target Within Radius
*For any* critter transitioning from IDLE to GATHER, the selected target resource should be within the gathering hut's gathering radius.

**Validates: Requirements 7.3**

### Property 14: Resource Collection Triggers RETURN
*For any* critter in GATHER state that successfully collects a resource, the critter state should transition to RETURN.

**Validates: Requirements 7.5**

### Property 15: RETURN Navigation to Hut
*For any* critter in RETURN state, the critter should move toward its assigned hut position (distance to hut should decrease over time).

**Validates: Requirements 7.6**

### Property 16: Deposit Completes Cycle
*For any* critter reaching its assigned hut while in RETURN state with a held resource, the resource should transfer to the hut inventory and the critter should transition to IDLE.

**Validates: Requirements 7.7, 6.2**

### Property 17: Stat Bounds
*For any* critter stat (strength, speed, endurance), the value should be within the range [1, 100].

**Validates: Requirements 8.2**

### Property 18: Strength Affects Gather Speed Monotonically
*For any* two critters with strength values S1 and S2 where S1 > S2, the critter with S1 should have a gather speed ≥ the critter with S2.

**Validates: Requirements 8.3**

### Property 19: Speed Stat Affects Movement Speed Monotonically
*For any* two critters with speed stat values V1 and V2 where V1 > V2, the critter with V1 should have movement speed ≥ the critter with V2.

**Validates: Requirements 8.4**

### Property 20: Endurance Affects Idle Duration Monotonically
*For any* two critters with endurance values E1 and E2 where E1 > E2, the critter with E1 should have idle duration ≥ the critter with E2.

**Validates: Requirements 8.5**

### Property 21: Well-Fed Buff Multiplier
*For any* critter with base stats (S, V, E), applying well-fed status should result in effective stats of (S × 1.1, V × 1.1, E × 1.1), capped at 100.

**Validates: Requirements 8.6**

### Property 22: Tree Regeneration After Depletion
*For any* tree that is fully harvested (inventory reaches zero), the tree should eventually respawn with replenished resources after a time period.

**Validates: Requirements 9.1**

### Property 23: Grass Propagation to Empty Neighbors
*For any* grass tile with at least one empty adjacent grid cell, grass should eventually spread to at least one empty neighbor over time.

**Validates: Requirements 9.2**

### Property 24: Trampling Prevents Grass Growth
*For any* grid cell marked as trampled, grass should not grow on that cell while the trampled status persists.

**Validates: Requirements 9.4**

### Property 25: Obstacle Work Unit Depletion
*For any* obstacle with initial work units W and critter with strength S, after N interactions, the remaining work units should be W - (N × f(S)) where f(S) is the work function based on strength.

**Validates: Requirements 10.2**

### Property 26: Obstacle Removal at Zero Work Units
*For any* obstacle that reaches zero remaining work units, the obstacle should be removed from the world and no longer block movement.

**Validates: Requirements 10.3, 10.5**

### Property 27: Offspring Stat Inheritance
*For any* two parent critters with stats (S1, V1, E1) and (S2, V2, E2), the offspring stats should be derived from parent stats (within a reasonable range of parent averages, accounting for mutations).

**Validates: Requirements 11.2, 11.3**

### Property 28: Offspring Stat Bounds After Mutation
*For any* offspring stat after mutation, the value should remain within [1, 100].

**Validates: Requirements 11.5**

### Property 29: Offspring Initial State
*For any* newly created offspring from a mating hut, the offspring state should be IDLE and position should be at the mating hut location.

**Validates: Requirements 11.6**

### Property 30: Buff Expiration
*For any* buff with duration D, after time T > D has elapsed, the buff should no longer be active.

**Validates: Requirements 12.3**

### Property 31: Equipment Unlock Enables Equipping
*For any* equipment that has been unlocked, the player should be able to equip it (equip action should succeed).

**Validates: Requirements 13.2**

### Property 32: Equipped Gathering Tool Increases Speed
*For any* player with gathering equipment equipped, the gathering speed should be greater than the same player without equipment equipped.

**Validates: Requirements 13.3**

### Property 33: Crafting Success with Sufficient Resources
*For any* recipe with cost C, if player inventory contains at least C resources, crafting should succeed and create the item.

**Validates: Requirements 14.3**

### Property 34: Save/Load Round Trip Preservation
*For any* game state, serializing to JSON and then deserializing should produce an equivalent game state (player position, inventory, critters, buildings, world objects all preserved).

**Validates: Requirements 17.1, 17.2, 17.3, 17.4**

### Property 35: Map Transition at Boundary
*For any* player position at a map boundary, moving beyond the boundary should change the current_map to the adjacent map.

**Validates: Requirements 18.2**

### Property 36: Inactive Map Entity Preservation
*For any* map transition, entities in the previous map should maintain their state (position, inventory, stats) when the player returns to that map.

**Validates: Requirements 18.4**

### Edge Cases and Examples

The following criteria are best tested as specific examples or edge cases rather than universal properties:

**Example Test: Interaction Radius Constant**
- Verify that player.interaction_radius == 1.5 × player.radius
- **Validates: Requirements 2.2**

**Example Test: Gathering Hut Dimensions**
- Verify that GatheringHut has width=3 and height=3
- **Validates: Requirements 6.1**

**Example Test: Critter State Machine States**
- Verify that CritterState enum contains exactly IDLE, GATHER, and RETURN
- **Validates: Requirements 7.1**

**Example Test: Critter Stat Attributes**
- Verify that Critter has strength, speed, and endurance attributes
- **Validates: Requirements 8.1**

**Example Test: World Object Structure**
- Verify that WorldObject has dimensions, inventory, and interact method
- **Validates: Requirements 4.1, 4.2, 4.3**

**Example Test: Object Type Instantiation**
- Verify that each object type (berry bush, tree, rock, grass, stick) can be instantiated
- **Validates: Requirements 4.6**

**Example Test: Build Menu Toggle**
- Verify that pressing 'B' key displays the build menu
- **Validates: Requirements 5.1**

**Example Test: Building Placement Mode**
- Verify that selecting a building enters placement mode
- **Validates: Requirements 5.3**

**Example Test: Chair Buff Application**
- Verify that interacting with a Chair adds a Rested buff to the player
- **Validates: Requirements 12.1**

**Example Test: Campfire Buff Application**
- Verify that interacting with a Campfire adds a Strength buff to the player
- **Validates: Requirements 12.2**

**Example Test: Debug Toggle**
- Verify that pressing F3 toggles debug display on/off
- **Validates: Requirements 15.1**

**Example Test: Obstacle Work Units Attribute**
- Verify that Obstacle has a work_units attribute
- **Validates: Requirements 10.1**

## Error Handling

### Input Validation

**Invalid Movement Input**
- Out-of-bounds movement attempts should clamp player position to world boundaries
- Invalid key inputs should be ignored without crashing

**Invalid Interaction Attempts**
- Interacting with no objects in range should be a no-op
- Interacting with objects that don't support interaction should log a warning

**Invalid Building Placement**
- Placement on occupied cells should display an error message and cancel placement
- Placement with insufficient resources should display an error message and cancel placement
- Placement out of world bounds should be prevented

### State Machine Error Handling

**Critter AI Errors**
- If pathfinding fails (no valid path), critter should return to IDLE state
- If target resource is destroyed before collection, critter should return to IDLE state
- If assigned hut is destroyed, critter should become unassigned and remain IDLE

**Invalid State Transitions**
- Attempting invalid state transitions should log an error and maintain current state
- State machine should never enter an undefined state

### Resource Management Errors

**Insufficient Resources**
- Crafting with insufficient resources should fail gracefully with error message
- Building placement with insufficient resources should fail gracefully with error message

**Invalid Resource Operations**
- Removing more resources than available should clamp to zero and log a warning
- Adding resources to a destroyed object should be prevented

### Save/Load Errors

**Corrupted Save Data**
- Invalid JSON should display error message and prevent loading
- Missing required fields should use default values and log warnings
- Version mismatches should attempt migration or display compatibility error

**File System Errors**
- Save file write failures should display error message to user
- Missing save file on load should start a new game

### Collision and Pathfinding Errors

**Pathfinding Failures**
- No valid path should result in entity remaining stationary
- Pathfinding timeout should return partial path or no path

**Collision Edge Cases**
- Entities spawned inside obstacles should be moved to nearest valid position
- Simultaneous collision from multiple directions should resolve deterministically

## Testing Strategy

### Dual Testing Approach

The Critters game prototype requires both unit testing and property-based testing for comprehensive coverage:

**Unit Tests** focus on:
- Specific examples and edge cases (interaction radius constant, building dimensions)
- Integration points between systems (player-world interaction, critter-hut assignment)
- Error conditions (invalid placement, insufficient resources, pathfinding failures)
- State machine transitions (specific IDLE→GATHER→RETURN sequences)

**Property-Based Tests** focus on:
- Universal properties across all inputs (collision detection, resource conservation)
- Stat relationships (monotonic speed/strength effects)
- Round-trip properties (save/load, serialization)
- Invariants (grid occupation, stat bounds)

Together, unit tests catch concrete bugs in specific scenarios while property tests verify general correctness across the input space.

### Property-Based Testing Configuration

**Library Selection**: Hypothesis (Python's leading property-based testing library)

**Test Configuration**:
- Minimum 100 iterations per property test (due to randomization)
- Each property test must include a comment tag referencing the design property
- Tag format: `# Feature: critters-game-prototype, Property {number}: {property_text}`

**Example Property Test Structure**:
```python
from hypothesis import given, strategies as st

# Feature: critters-game-prototype, Property 8: Inventory Unbounded Capacity
@given(st.lists(st.tuples(st.text(), st.integers(min_value=1, max_value=1000))))
def test_inventory_unbounded_capacity(resources):
    """For any amount of resources, player inventory should accept additions."""
    player = Player(0, 0)
    for resource_type, amount in resources:
        result = player.add_resource(resource_type, amount)
        assert result == True  # Should never fail due to capacity
```

### Test Organization

**Unit Tests** (`tests/unit/`):
- `test_player.py` - Player movement, interaction, inventory
- `test_critter.py` - Critter AI state machine, stats, behavior
- `test_world.py` - World object placement, grid system, collision
- `test_buildings.py` - Building placement, hut assignment, breeding
- `test_pathfinding.py` - A* algorithm, path validation
- `test_save_load.py` - Serialization, deserialization
- `test_crafting.py` - Recipe validation, resource deduction

**Property Tests** (`tests/properties/`):
- `test_movement_properties.py` - Properties 1, 4, 5
- `test_grid_properties.py` - Properties 2, 3
- `test_resource_properties.py` - Properties 7, 8, 9
- `test_critter_properties.py` - Properties 10-21
- `test_world_properties.py` - Properties 22-26
- `test_breeding_properties.py` - Properties 27-29
- `test_system_properties.py` - Properties 30-36

### Integration Testing

**System Integration Tests**:
- Complete gameplay loop (player moves, gathers, builds, assigns critters)
- Multi-map transitions with entity preservation
- Long-running simulation (resource regeneration, critter automation)
- Save/load full game state

### Performance Testing

**Performance Benchmarks**:
- Frame rate stability at 60 FPS with 100+ entities
- Pathfinding performance with large maps (100×100 grid)
- Save/load time for large game states
- Memory usage over extended play sessions

### Test Data Generation

**Hypothesis Strategies**:
```python
# Position strategy
positions = st.tuples(
    st.floats(min_value=0, max_value=100),
    st.floats(min_value=0, max_value=100)
)

# Stat strategy (bounded 1-100)
stats = st.integers(min_value=1, max_value=100)

# Critter strategy
critters = st.builds(
    Critter,
    x=st.floats(min_value=0, max_value=100),
    y=st.floats(min_value=0, max_value=100),
    strength=stats,
    speed=stats,
    endurance=stats
)

# Grid coordinate strategy
grid_coords = st.tuples(
    st.integers(min_value=0, max_value=50),
    st.integers(min_value=0, max_value=50)
)
```

### Continuous Integration

**CI Pipeline**:
1. Run all unit tests (fast feedback)
2. Run property-based tests with 100 iterations
3. Run integration tests
4. Generate coverage report (target: >80% coverage)
5. Run performance benchmarks (regression detection)

### Manual Testing Checklist

**Gameplay Testing**:
- [ ] Player movement feels smooth and responsive
- [ ] Collision detection prevents walking through objects
- [ ] Resource gathering provides visual feedback
- [ ] Critters autonomously gather and return resources
- [ ] Building placement shows valid/invalid locations
- [ ] Breeding produces offspring with visible stat inheritance
- [ ] Buffs provide noticeable gameplay effects
- [ ] Save/load preserves all game progress
- [ ] Map transitions work smoothly
- [ ] Debug display shows accurate information

## Future Optimization: Offline Building Simulation

To avoid simulating all maps when only one is active, we can approximate resource generation for suspended maps:

- Each building measures its **average resource production rate** over a sliding window (e.g., last 3 minutes).
- When a map is **suspended** (player leaves), store:
  - `last_update_time` (game time or real time)
  - `accumulated_production` since last update
- When the map is **restored**, compute:
  - `elapsed = restore_time - suspend_time`
  - `added = min(rate * elapsed, building_capacity - current_storage)`
  - Increase building storage by `added`
- This allows buildings to generate resources while the player is away without running full simulation on inactive maps.
- Benefits: performance, lower CPU usage; Downsides: less precise; acceptable for incremental gameplay.
- Implementation note: `Building` could gain `get_production_rate()` and `suspend()`/`resume()` methods. The `World` would call these on map switches.

**Edge Case Testing**:
- [ ] Game handles 0 resources gracefully
- [ ] Game handles 100+ critters without performance issues
- [ ] Pathfinding works with complex obstacle layouts
- [ ] Resource regeneration works correctly over long periods
- [ ] Breeding with extreme stat values (1 and 100) works correctly

