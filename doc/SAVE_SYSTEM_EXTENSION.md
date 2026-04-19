# Save System Extension Guide

## Overview

The save system serializes the entire game state (world maps, objects, critters, player) to JSON and deserializes it on load. Understanding how to safely extend it is critical to avoid breaking saved games.

## Current Architecture

- `src/save_system.py` contains:
  - `SaveData` dataclass (top-level container)
  - `serialize_world(world)` → dict
  - `deserialize_world(data)` → `World`
  - Per-class helpers: `_serialize_*`, `_deserialize_*`
- Type dispatch for `WorldObject` subclasses uses an **if/elif chain** in `_deserialize_world_object`.
- Critter references (`assigned_hut`, `target_resource`) are stored as `(type, gx, gy)` tuples and resolved after all objects are loaded.

## Adding a New WorldObject Subclass

When introducing a new building or entity that inherits from `WorldObject` (or a subclass like `Building`), you must:

1. **Define the class normally** with all its attributes and behavior.
2. **Ensure it has `get_occupied_cells()`** if it blocks movement (otherwise grid registration will fail).
3. **Add serialization** in `_serialize_world_object`:
   - Include the class name in `"type"` field.
   - Serialize all necessary attributes (position, dimensions, cell_size, and any custom state).
   - For buildings, include `cost` if present.
4. **Add deserialization** in `_deserialize_world_object`:
   - Add an `elif classname == "YourClass":` branch.
   - Call the constructor with required args (`gx, gy, width, height, cell_size` etc.).
   - Restore custom fields from `data`.
   - Set `obj.world = self` happens later; do not set here.
5. **Write a round-trip test** in `tst/test_save_load.py` (or a new test file) that:
   - Creates your object in a world.
   - Serializes and deserializes.
   - Asserts key attributes match.
   - Asserts `obj.world` is set after `deserialize_world` completes.

### Example Pattern

```python
# In _serialize_world_object:
elif isinstance(obj, YourClass):
    data = {
        "type": "YourClass",
        "gx": obj.gx,
        "gy": obj.gy,
        "width": obj.width,
        "height": obj.height,
        "cell_size": obj.cell_size,
        # ... your fields ...
    }
    return data

# In _deserialize_world_object:
elif classname == "YourClass":
    obj = YourClass(gx, gy, width, height, cell_size, ...)
    # restore fields
    return obj
```

## Adding New Fields to Existing Classes

1. Update `_serialize_<class>` to include the new field in the returned dict.
2. Update `_deserialize_<class>` to read the field from `data` and apply it during construction or assignment.
3. Make the deserialization **tolerant of missing keys** (use `.get()` with defaults) if you want old saves to still load.
4. Add tests verifying round-trip with the new field.

## Critter Subclasses

If you add a new `Critter` subclass (e.g., `WorkerCritter`), you must:

- Update `_serialize_critter` to include discriminator (e.g., `"type": "WorkerCritter"` or a `subtype` field). Currently it hardcodes `"type": "Critter"`.
- Update `_deserialize_critter` to handle the subtype and construct the correct class.
- Ensure any critter-specific fields are serialized/deserialized.
- Add reference resolution in `_resolve_critter_references` if the new critter uses `assigned_hut` or `target_resource`.

## Breaking Changes and Backwards Compatibility

- **Never change a class name** without keeping the old string in the deserializer as an alias.
- **Never remove fields** from serialization; instead, deprecate them gracefully.
- If you must change the save format significantly, consider **versioned migrations** (see Future Improvements).

## Testing Requirements

- **Every new saveable type must have a round-trip test.**
- Run the full test suite (`make test`) before committing changes affecting serialization.
- If you modify `_deserialize_world_object`, ensure all existing tests still pass.

## Future Improvements (Not Yet Implemented)

- **Registry Pattern**: Replace the if/elif chain with a decorator-based registry to make adding types self-contained.
- **Versioned Schema**: Add explicit `schema_version` and migration functions to evolve saves safely across releases.
- **Self-Describing Classes**: Each class could provide `to_dict()` and `from_dict()` methods, reducing central boilerplate.

## Common Pitfalls

- Forgetting to add a new building to `_deserialize_world_object` → “Unknown type” error on load.
- Changing constructor signature without updating deserializer → `TypeError`.
- Not setting `obj.world = self` after deserialization (handled by `deserialize_world` loop) → `AttributeError` when objects expect `world` to exist.
- Critters not appearing in `world.current_map.critters` after load (handled by deserialization appending to both `objects` and `critters` lists).
- Reference resolution failing if object coordinates changed between save and load (the `(type, gx, gy)` lookup must still find the object).

## Checklist for New Building/Object

- [ ] Class defined with `get_occupied_cells()` if it blocks movement.
- [ ] `_serialize_world_object` branch added (test by inspecting output of `serialize_world`).
- [ ] `_deserialize_world_object` branch added (handle all required fields).
- [ ] Round-trip test added and passing.
- [ ] Full test suite (`make test`) passes with new changes.
- [ ] No hardcoded class names in other parts of save system (only in dispatcher).

---

**Remember**: When in doubt, write a test first. It will force you to think about the serialization contract and protect against regressions.
