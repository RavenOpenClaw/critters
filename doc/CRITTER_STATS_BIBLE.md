# Critter Stats Bible

This document defines the roles of Critter stats and how they impact gameplay mechanics. Stats range from 1 to 100.

## Core Stats

### 1. Strength (STR)
Strength represents the raw power and physical capability of the critter.
*   **Gather Amount:** Higher strength allows a critter to harvest more resources in a single "action" (once the timed interaction circle fills).
    *   *Scale:* 1-40 (1 item), 41-80 (2 items), 81-100 (3 items).
*   **Obstacle Requirements:** Large obstacles or complex projects (like bridges) may have a **Minimum Strength Requirement**. 
    *   The sum of STR of all critters assigned to the task must meet or exceed this value before any work progress can be made.
    *   This encourages breeding either a high volume of critters or a few very powerful specialists.
*   **Work Application:** Once requirements are met, STR determines how many "work units" are applied to an obstacle per interaction cycle.

### 2. Speed (SPD)
Speed represents the dexterity and movement capability of the critter.
*   **Movement Speed:** Determines how fast the critter walks between the hut and resources.
*   **Interaction Speed:** Determines how fast the interaction circle fills. High SPD critters are more "nimble" and finish the gathering/depositing cycle faster.
    *   *Formula:* Base duration (varies by task, e.g., Wood vs Food) reduced by a factor of SPD.
    *   *Visual Link:* Interaction circles are Green, matching the SPD stat color.

### 3. Endurance (END)
Endurance represents the stamina and storage capacity of the critter.
*   **Carry Capacity:** Determines the maximum number of items a critter can hold for *each* resource type before returning to the hut.
    *   *Current Formula:* `max(1, (endurance + 19) // 20)` (1 to 6 items).
*   **Idle/Rest Duration:** Determines how long the critter rests at the hut between gathering trips.
    *   *Current Formula:* `8.0 + (endurance - 1) * (4.0 / 99.0)` seconds.

## Visual Appearance: Stat-based Coloring
A critter's body color is a direct representation of its stats using RGB mapping (0-255 range). 
*   **Red (R):** Scaled Strength (`STR * 2.55`)
*   **Green (G):** Scaled Speed (`SPD * 2.55`)
*   **Blue (B):** Scaled Endurance (`END * 2.55`)

**Examples:**
*   **Pure Specialist:** A 100 STR critter with 0 in others is Bright Red.
*   **Fast Gatherer:** High STR and high SPD results in **Yellow** tones.
*   **Stamina Runner:** High SPD and high END results in **Cyan** tones.
*   **The "Perfect" Critter:** 100/100/100 stats result in a **Pure White** critter.
*   **Balanced/Starting:** Mid-range balanced stats result in **Grey** tones.

## Buff Multipliers
*   **Well-Fed:** Applies a 1.1x multiplier to STR and SPD (capped at 100).
*   **Environmental Buffs:** (e.g., Warmth) Can apply temporary multipliers to specific actions like gathering or movement.

## Evolution & Breeding
Stats are inherited from parents with a small random mutation (±5), ensuring that selective breeding can lead to more efficient worker colonies.
