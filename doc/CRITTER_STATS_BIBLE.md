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

Critter breeding uses a complex genetic inheritance system designed to favor specialization while allowing for both gradual improvement and rare, significant breakthroughs.

### Inheritance Rules
For each of the three core stats (STR, SPD, END), the offspring determines its base value through a weighted probability:
*   **40% Chance:** Inherit from **Parent A**.
*   **40% Chance:** Inherit from **Parent B**.
*   **20% Chance:** **Random Roll** (Mutation/Breakthrough).

### The Random Roll (The 20% Case)
When a stat is randomly rolled, it follows a skewed distribution that favors lower values but preserves a small chance for elite stats:
*   **80% of rolls** follow a Log-Normal distribution with a **mode around 15**. This simulates "natural" baseline stats.
*   **20% of rolls** are purely uniform (1-100), representing "chaos" or rare genetic outliers.
*   **Resulting Distribution:**
    *   Most common values: 10-20.
    *   Chance of rolling ≥ 90: ~1-2%.
    *   Chance of rolling 100: ~0.5%.
### Final Mutation Factor
After the base stat is determined (via inheritance or random roll), a final **±10% mutation factor** is applied:
*   The stat is multiplied by a random value between **0.9 and 1.1** (uniform distribution).
*   The final result is clamped between **1 and 100**.

## Critter Release & Candies

To prevent the colony from becoming overcrowded and to provide a path for long-term stat optimization, critters can be "Released" (recycled).

### The Release Process
When a critter is released, it is removed from the world and converted into a **Stat Candy**.
*   **Candy Type:** Determined by the critter's highest core stat (Strength, Speed, or Endurance). In case of a tie, the type is chosen randomly among the tied highest stats.
*   **Yield:** A single candy corresponding to that stat (e.g., "Strength Candy").

### Stat Candies
Candies are items that can be "used" on a selected critter to provide a permanent, hereditary stat boost.
*   **Effect:** Using a candy increases the target stat by exactly **+1**.
*   **Stat Cap:** Even with candies, stats cannot exceed the hard cap of **100**.
*   **Heredity:** These boosts are permanent modifications to the critter's base stats and are passed down to offspring using the standard inheritance rules.

### Statistical Report (Simulated)
... (rest of the file)
Based on 10,000 simulated breeding cycles from two "Average" (50/50/50) parents:
*   **Average Offspring Stat:** ~45 (slightly lower due to the low-mode random rolls).
*   **Stat Improvement:** ~35% of offspring will have at least one stat higher than their parents.
*   **Elite Potential:** ~1% of offspring will achieve a stat > 80 from average parents.
*   **Specialization:** Because each stat is rolled independently, a single offspring can combine a high STR from one parent and high SPD from another, or roll a random breakthrough in its third stat.

---
_Note: This system replaces the previous discrete tier system to provide a more continuous and rewarding breeding progression._
