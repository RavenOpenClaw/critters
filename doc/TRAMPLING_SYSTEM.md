# Grass Condition & Trampling System

This document describes the grass condition system and how repeated trampling degrades and eventually removes grass, creating natural paths.

## Overview

Grass tiles have a **condition** value (0–100). Condition affects both visual appearance and survival:

- **Full condition (100)**: Bright green, healthy.
- **Partial damage**: Color dulls proportionally.
- **Condition ≤ 0**: Grass is removed, leaving bare dirt.

## Mechanisms

### Condition Decay (Trampling)

When any entity (player or critter) occupies a grid cell containing grass, `World.mark_trampled(gx, gy)` is called every frame. Each call reduces the grass’s condition by `World.trample_decay` (default **5.0** points.

- Multiple entities or continuous occupation compound the decay quickly.
- Example: A single entity standing on one tile for 20 seconds (5×20 = 100) will completely kill the grass if undisturbed.

### Condition Recovery

When a cell is **not trampled** for at least one frame, the grass slowly recovers:

- Recovery rate: `Grass.recovery_rate` (default **2.0** per second).
- Recovery is capped at `Grass.max_condition` (100).
- This allows lightly used areas to heal over time.

### Removal

When `condition <= 0`, `Grass.update()` removes the grass object from the world during the next update cycle. The cell becomes bare and will not regrow until:

1. The grass is completely gone, and
2. A neighbor grass spreads back into the cell (which can only happen if the cell is no longer “trampled” – see below).

### Spread Blocking

Each cell that has been trampled gets a temporary flag (`World.trampled`) with duration `World.trample_duration` (default **5.0** seconds). This timer is refreshed every frame the cell is stepped on.

- While a cell is marked as trampled, **no new grass may spread onto it**.
- This ensures that active paths stay bare even if the grass condition is still positive.
- When the trample timer expires, spreading can occur again from adjacent grass.

Combined with condition decay, this yields:

- **Heavy traffic**: Condition drops rapidly to 0, grass dies. Trampled timer keeps cell bare. The path remains visible as long as traffic continues.
- **Light/occasional traffic**: Condition may never reach 0, but the cell is periodically bare (trampled timer) and grass color dims during use, then recovers.
- **Abandoned paths**: Traffic stops → trampled timer expires → if any grass remains (condition > 0), it continues recovering; if grass was removed, adjacent grass can eventually spread back in.

## Parameters

You can tune the system by editing these constants:

- `World.trample_decay` (default 5.0): Condition points lost per trample event. Higher = faster wear.
- `Grass.recovery_rate` (default 2.0): Condition points gained per second when undisturbed. Higher = faster healing.
- `World.trample_duration` (default 5.0): Seconds a cell remains “trampled” after last step. Controls how long a bare path persists after traffic ceases.

## Visual Feedback

Grass color is interpolated based on current condition:

```python
factor = condition / max_condition
r, g, b = (144, 238, 144) * factor
```

- Full condition → (144, 238, 144) light green.
- 50% condition → (72, 119, 72) darker green.
- Near 0 → very dim, almost black.

Dead grass (condition ≤ 0) is removed; the cell shows the background color (light gray) or any underlying terrain.

## Debug Overlay

Press **F3** to show:

- Trampled cells as a semi‑transparent red overlay.
- Trampled count in the debug HUD.
- This helps verify that trampling logic is working and paths form as expected.

## Design Notes

- Simulates ecological impact of repeated foot traffic.
- Encourages player (and critter) movement along established routes; heavily traveled areas become permanent (until abandoned) dirt paths.
- Recovery mechanic gives the world a sense of dynamism: nature reclaims unused areas.
- The system is cheap computationally (per‑frame updates only for entities and grass objects) and requires no additional data structures beyond the existing `trampled` dict.

Future extensions could include different ground types (mud, sand) with different decay/recovery rates, or visual overlays for dirt paths.
