"""
Save/Load system for Critters game.

Provides SaveData class and functions to serialize/deserialize the entire game state to/from JSON.
"""
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from entity import Entity, Player
from world_object import WorldObject
from critter import Critter, CritterState
from map_data import MapData, Portal
from inventory import Inventory
from buff import Buff
from building import Building
from berry_bush import BerryBush
from gathering_hut import GatheringHut
from mating_hut import MatingHut
from chair import Chair
from campfire import Campfire
from obstacle import Obstacle
from grass import Grass
from tree import Tree
from rock import Rock
from stick import Stick
from world import World


@dataclass
class SaveData:
    """Complete serializable game state."""
    version: str
    current_map_name: str
    maps: List[Dict[str, Any]]
    player: Dict[str, Any]


def _serialize_inventory(inv: Inventory) -> Dict[str, int]:
    return inv.items.copy() if inv.items else {}

def _deserialize_inventory(data: Dict[str, int]) -> Inventory:
    inv = Inventory()
    inv.items = data.copy()
    return inv

def _serialize_buff(buff: Buff) -> Dict[str, Any]:
    return {
        "name": buff.name,
        "multipliers": buff.multipliers.copy(),
        "duration": buff.duration,
        "remaining": buff.remaining,
    }

def _deserialize_buff(data: Dict[str, Any]) -> Buff:
    buff = Buff(data["name"], data["multipliers"], data["duration"])
    buff.remaining = data["remaining"]
    return buff

def _serialize_entity(entity: Entity) -> Dict[str, Any]:
    return {
        "x": entity.x,
        "y": entity.y,
        "radius": entity.radius,
    }

def _deserialize_entity(data: Dict[str, Any]) -> Entity:
    return Entity(data["x"], data["y"], data["radius"])

def _serialize_player(player: Player) -> Dict[str, Any]:
    return {
        "type": "Player",
        "x": player.x,
        "y": player.y,
        "radius": player.radius,
        "base_speed": player.base_speed,
        "speed": player.speed,
        "inventory": _serialize_inventory(player.inventory),
        "active_buffs": [_serialize_buff(b) for b in player.active_buffs],
        "unlocked_equipment": list(player.unlocked_equipment),
        "equipped": list(player.equipped),
    }

def _deserialize_player(data: Dict[str, Any]) -> Player:
    player = Player(
        x=data["x"],
        y=data["y"],
        radius=data["radius"],
        speed=data["base_speed"],
    )
    player.speed = data["speed"]
    player.inventory = _deserialize_inventory(data["inventory"])
    player.active_buffs = [_deserialize_buff(bdata) for bdata in data.get("active_buffs", [])]
    player.unlocked_equipment = set(data.get("unlocked_equipment", []))
    player.equipped = set(data.get("equipped", []))
    return player

def _serialize_critter(critter: Critter) -> Dict[str, Any]:
    # Reference for assigned_hut: if set, use (gx, gy) and type
    assigned_hut_ref = None
    if critter.assigned_hut is not None:
        hut = critter.assigned_hut
        assigned_hut_ref = {
            "type": hut.__class__.__name__,
            "gx": hut.gx,
            "gy": hut.gy,
        }
    # Reference for target_resource
    target_resource_ref = None
    if critter.target_resource is not None:
        obj = critter.target_resource
        target_resource_ref = {
            "type": obj.__class__.__name__,
            "gx": obj.gx,
            "gy": obj.gy,
        }
    # loiter_target
    loiter_target = None
    if critter.loiter_target is not None:
        loiter_target = [critter.loiter_target[0], critter.loiter_target[1]]
    # Path as list of [gx, gy]
    path = []
    if hasattr(critter, 'path') and critter.path:
        path = [[gx, gy] for gx, gy in critter.path]
    path_index = getattr(critter, 'path_index', 0)

    # Follow state serialization
    following_player_id = None
    if critter.following_player is not None:
        following_player_id = id(critter.following_player)
    follow_goal = None
    if critter.follow_goal is not None:
        follow_goal = [critter.follow_goal[0], critter.follow_goal[1]]

    return {
        "type": "Critter",
        "x": critter.x,
        "y": critter.y,
        "cell_size": critter.cell_size,
        "strength": critter.strength,
        "speed_stat": critter.speed_stat,
        "endurance": critter.endurance,
        "state": critter.state.name,
        "is_well_fed": critter.is_well_fed,
        "assigned_hut_ref": assigned_hut_ref,
        "target_resource_ref": target_resource_ref,
        "inventory": _serialize_inventory(critter.inventory),
        "loiter_timer": critter.loiter_timer,
        "loiter_target": loiter_target,
        "idle_timer": critter.idle_timer,
        "path": path,
        "path_index": path_index,
        # Follow state
        "following_player_id": following_player_id,
        "follow_timer": critter.follow_timer,
        "follow_recalc_interval": critter.follow_recalc_interval,
        "follow_goal": follow_goal,
    }

def _deserialize_critter(data: Dict[str, Any]) -> Critter:
    critter = Critter(
        x=data["x"],
        y=data["y"],
        cell_size=data["cell_size"],
        strength=data["strength"],
        speed_stat=data["speed_stat"],
        endurance=data["endurance"],
    )
    critter.state = CritterState[data["state"]]
    critter.is_well_fed = data["is_well_fed"]
    critter.loiter_timer = data["loiter_timer"]
    lt = data["loiter_target"]
    critter.loiter_target = tuple(lt) if lt is not None else None
    critter.idle_timer = data["idle_timer"]
    critter.path = [tuple(p) for p in data.get("path", [])]
    critter.path_index = data.get("path_index", 0)
    
    # Restore inventory with fallback to old held_resource format
    if "inventory" in data:
        critter.inventory = _deserialize_inventory(data["inventory"])
    elif data.get("held_resource"):
        critter.inventory.add(data["held_resource"], data.get("held_quantity", 0))
        
    # Follow state deserialization
    critter.following_player = None
    critter.follow_timer = data.get("follow_timer", 0.0)
    critter.follow_recalc_interval = data.get("follow_recalc_interval", 1.0)
    fg = data.get("follow_goal")
    critter.follow_goal = tuple(fg) if fg is not None else None
    # Defer resolution of assigned_hut and target_resource until world is built.
    critter.assigned_hut = None
    critter.target_resource = None
    # Store raw ref data for resolution later
    critter._assigned_hut_ref = data.get("assigned_hut_ref")
    critter._target_resource_ref = data.get("target_resource_ref")
    return critter

def _serialize_world_object(obj: WorldObject) -> Dict[str, Any]:
    data = {
        "type": obj.__class__.__name__,
        "gx": obj.gx,
        "gy": obj.gy,
        "width": obj.width,
        "height": obj.height,
        "cell_size": obj.cell_size,
        "inventory": _serialize_inventory(obj.inventory),
        "blocks_movement": obj.blocks_movement,
    }
    if isinstance(obj, Building):
        data["cost"] = obj.cost
    if isinstance(obj, GatheringHut):
        data["storage"] = _serialize_inventory(obj.storage)
        data["gathering_radius"] = obj.gathering_radius
    if isinstance(obj, Obstacle):
        data["work_units"] = obj.work_units
    if isinstance(obj, Grass):
        data["spread_threshold"] = obj.spread_threshold
        data["time_accumulator"] = obj.time_accumulator
    if isinstance(obj, Tree):
        data["max_wood"] = obj.max_wood
        data["respawn_duration"] = obj.respawn_duration
        data["depleted"] = obj.depleted
        data["time_depleted"] = obj.time_depleted
    return data

def _deserialize_world_object(data: Dict[str, Any]) -> WorldObject:
    classname = data["type"]
    gx = data["gx"]
    gy = data["gy"]
    width = data["width"]
    height = data["height"]
    cell_size = data["cell_size"]
    inventory = _deserialize_inventory(data.get("inventory", {}))
    blocks_movement = data.get("blocks_movement", True)

    if classname == "BerryBush":
        # Bushes must always have max_food=5; inventory is restored from save, but regrowth target is fixed
        obj = BerryBush(gx, gy, cell_size=cell_size, berries=5)
        obj.inventory = inventory
        obj.blocks_movement = blocks_movement
        return obj
    elif classname == "GatheringHut":
        obj = GatheringHut(gx, gy, cell_size)
        # Override default storage if provided
        if "storage" in data:
            obj.storage = _deserialize_inventory(data["storage"])
        if "cost" in data:
            obj.cost = data["cost"]
        if "gathering_radius" in data:
            obj.gathering_radius = data["gathering_radius"]
        obj.inventory = inventory  # may be unused
        obj.blocks_movement = blocks_movement
        return obj
    elif classname == "MatingHut":
        obj = MatingHut(gx, gy, cell_size)
        if "cost" in data:
            obj.cost = data["cost"]
        obj.inventory = inventory
        obj.blocks_movement = blocks_movement
        return obj
    elif classname == "Obstacle":
        work_units = data["work_units"]
        obj = Obstacle(gx, gy, width, height, cell_size, work_units)
        obj.inventory = inventory
        obj.blocks_movement = blocks_movement
        return obj
    elif classname == "Grass":
        spread_threshold = data["spread_threshold"]
        time_accumulator = data["time_accumulator"]
        obj = Grass(gx, gy, cell_size, spread_threshold=spread_threshold)
        obj.time_accumulator = time_accumulator
        obj.inventory = inventory
        obj.blocks_movement = blocks_movement
        return obj
    elif classname == "Tree":
        max_wood = data.get("max_wood", 10)
        respawn_duration = data.get("respawn_duration", 30.0)
        obj = Tree(gx, gy, cell_size, wood=max_wood, respawn_duration=respawn_duration)
        obj.inventory = inventory
        obj.blocks_movement = blocks_movement
        obj.depleted = data.get("depleted", False)
        obj.time_depleted = data.get("time_depleted", 0.0)
        return obj
    elif classname == "Rock":
        obj = Rock(gx, gy, cell_size)  # default stone count, will override inventory
        obj.inventory = inventory
        obj.blocks_movement = blocks_movement
        return obj
    elif classname == "Stick":
        obj = Stick(gx, gy, cell_size)  # default sticks count, will override inventory
        obj.inventory = inventory
        obj.blocks_movement = blocks_movement
        return obj
    elif classname == "Chair":
        obj = Chair(gx, gy, cell_size)
        if "cost" in data:
            obj.cost = data["cost"]
        obj.inventory = inventory
        obj.blocks_movement = blocks_movement
        return obj
    elif classname == "Campfire":
        obj = Campfire(gx, gy, cell_size)
        if "cost" in data:
            obj.cost = data["cost"]
        obj.inventory = inventory
        obj.blocks_movement = blocks_movement
        return obj
    else:
        raise ValueError(f"Unknown world object type: {classname}")

def _serialize_portal(portal: Portal) -> Dict[str, Any]:
    return {
        "gx": portal.gx,
        "gy": portal.gy,
        "target_map": portal.target_map,
        "target_portal": portal.target_portal,
    }

def _deserialize_portal(data: Dict[str, Any]) -> Portal:
    return Portal(
        gx=data["gx"],
        gy=data["gy"],
        target_map=data["target_map"],
        target_portal=data["target_portal"],
    )

def _serialize_map(map_data: MapData) -> Dict[str, Any]:
    # Separate world objects and critters from the combined objects list
    world_objects = []
    critters = []
    for obj in map_data.objects:
        if isinstance(obj, Critter):
            critters.append(obj)
        else:
            world_objects.append(obj)
    # Serialize trampled dictionary to list of [gx, gy, remaining]
    trampled_list = []
    for (gx, gy), remaining in map_data.trampled.items():
        trampled_list.append([gx, gy, remaining])
    # Serialize portals dict
    portals_serialized = {pid: _serialize_portal(p) for pid, p in map_data.portals.items()}
    return {
        "name": map_data.name,
        "width": map_data.width,
        "height": map_data.height,
        "cell_size": map_data.cell_size,
        "objects": [_serialize_world_object(obj) for obj in world_objects],
        "critters": [_serialize_critter(c) for c in critters],
        "trampled": trampled_list,
        "portals": portals_serialized,
        "neighbors": map_data.neighbors,
    }

def _deserialize_map(data: Dict[str, Any]) -> MapData:
    map_obj = MapData(
        name=data["name"],
        width=data["width"],
        height=data["height"],
        cell_size=data["cell_size"],
    )
    # Deserialize world objects and add to map.objects
    for obj_data in data.get("objects", []):
        obj = _deserialize_world_object(obj_data)
        map_obj.objects.append(obj)
    # Deserialize critters
    for c_data in data.get("critters", []):
        c = _deserialize_critter(c_data)
        map_obj.critters.append(c)
        map_obj.objects.append(c)  # also add to objects list for consistency
    # Trampled: list -> dict
    for gx, gy, remaining in data.get("trampled", []):
        map_obj.trampled[(gx, gy)] = remaining
    # Portals
    for pid, p_data in data.get("portals", {}).items():
        map_obj.portals[pid] = _deserialize_portal(p_data)
    # Neighbors
    map_obj.neighbors = data.get("neighbors", {})
    return map_obj

def serialize_world(world: World) -> Dict[str, Any]:
    """Serialize the entire World state (all maps) into a JSON-serializable dict."""
    maps_data = [_serialize_map(m) for m in world.maps.values()]
    return {
        "version": "1.0",
        "current_map_name": world.current_map.name,
        "maps": maps_data,
    }

def deserialize_world(data: Dict[str, Any]) -> World:
    """Deserialize world state from dict and return a World instance."""
    # Create all MapData objects first
    maps_by_name = {}
    for map_data in data["maps"]:
        m = _deserialize_map(map_data)
        maps_by_name[m.name] = m
    # Identify current map
    current_name = data["current_map_name"]
    if current_name not in maps_by_name:
        raise ValueError(f"Current map '{current_name}' not found in saved maps")
    current_map = maps_by_name[current_name]
    # Build World with current map; this will set maps = {current: current_map} and rebuild grid
    world = World(current_map)
    # Add additional maps
    for name, m in maps_by_name.items():
        if name != current_name:
            world.add_map(m)
    # Set world reference for all objects and ensure critters are in critters lists.
    # After adding maps, we need to set obj.world for all objects in all maps.
    # We'll also resolve critter references (assigned_hut, target_resource) after all objects are loaded.
    for m in world.maps.values():
        for obj in m.objects:
            obj.world = world
        # Ensure m.critters list matches the critters in m.objects (should already be populated from deserialization because we appended both).
    # Resolve critter references now
    _resolve_critter_references(world)
    # Rebuild assigned_critters lists for GatheringHut and MatingHut
    _rebuild_assigned_critters(world)
    return world

def _resolve_critter_references(world: World):
    """Replace critters' stored object references (by position) with actual object references."""
    # Build lookup: For each map, index all world objects (excluding critters) by (type, gx, gy)
    lookup_by_map: Dict[str, Dict[Tuple[str, int, int], Any]] = {}
    for m in world.maps.values():
        lookup = {}
        for obj in m.objects:
            if not isinstance(obj, Critter):
                key = (obj.__class__.__name__, obj.gx, obj.gy)
                lookup[key] = obj
        lookup_by_map[m.name] = lookup
    # For each critter in each map, resolve references using that map's lookup
    for m in world.maps.values():
        for critter in m.critters:
            # Assigned hut
            ref = getattr(critter, "_assigned_hut_ref", None)
            if ref:
                key = (ref["type"], ref["gx"], ref["gy"])
                obj = lookup_by_map[m.name].get(key)
                if obj:
                    critter.assigned_hut = obj
                else:
                    # Missing referenced object; clear reference
                    critter.assigned_hut = None
            # Target resource
            ref2 = getattr(critter, "_target_resource_ref", None)
            if ref2:
                key = (ref2["type"], ref2["gx"], ref2["gy"])
                obj = lookup_by_map[m.name].get(key)
                if obj:
                    critter.target_resource = obj
                else:
                    critter.target_resource = None

def _rebuild_assigned_critters(world: World):
    """Populate assigned_critters lists for all GatheringHut and MatingHut based on critters' assigned_hut."""
    for m in world.maps.values():
        # Collect all huts
        huts = [obj for obj in m.objects if isinstance(obj, (GatheringHut, MatingHut))]
        for hut in huts:
            hut.assigned_critters = []  # ensure clear
        # Assign critters
        for critter in m.critters:
            if critter.assigned_hut is not None and isinstance(critter.assigned_hut, (GatheringHut, MatingHut)):
                critter.assigned_hut.assigned_critters.append(critter)

def save_game(world: World, player: Player, filepath: str | Path) -> None:
    """Save the current game state to a JSON file."""
    world_dict = serialize_world(world)
    player_dict = _serialize_player(player)
    save_data = SaveData(
        version=world_dict["version"],
        current_map_name=world_dict["current_map_name"],
        maps=world_dict["maps"],
        player=player_dict,
    )
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(asdict(save_data), f, indent=2)

def load_game(filepath: str | Path) -> Tuple[World, Player]:
    """Load game state from a JSON file and return (world, player)."""
    path = Path(filepath)
    with open(path, 'r') as f:
        data = json.load(f)
    # Validate required fields
    required = ["version", "current_map_name", "maps", "player"]
    for field in required:
        if field not in data:
            raise ValueError(f"Save file missing required field: {field}")
    # Construct SaveData instance from dict
    save_data = SaveData(
        version=data["version"],
        current_map_name=data["current_map_name"],
        maps=data["maps"],
        player=data["player"],
    )
    world = deserialize_world({
        "version": save_data.version,
        "current_map_name": save_data.current_map_name,
        "maps": save_data.maps,
    })
    player = _deserialize_player(save_data.player)
    return world, player
