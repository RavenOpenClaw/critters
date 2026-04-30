# Interaction & Timed Progress Design

This document records the finalized design decisions for the interaction system and timed progress mechanics.

## 1. Timed Interactions
All world interactions (Gathering, Depositing, Obstacle Clearing, etc.) now require a "charge time" instead of being instantaneous.

*   **Mechanic:** Hold 'E' or 'Space' to fill a progress circle.
*   **Visuals:** 
    *   A clockwise-filling circle appears above the entity's head.
    *   **Player Color:** Lime Green (normal saturation).
    *   **Critter Color:** Muted Green (half saturation/greyer, smaller size).
*   **Interruption:** Releasing the key or moving out of range resets progress immediately to 0. No progress is saved.
*   **Sticky Targeting:** The interaction "sticks" to the current target until completion, depletion, or interruption.
*   **Continuous Action:** If the key is held, the action repeats automatically as long as the target has resources and the player is in range.
*   **Variable Timings:** Base interaction times vary by task (e.g., Food: 2.0s, Wood: 4.0s, Deposit: 1.5s).

## 2. Critter AI Integration
*   **Automation:** Critters automatically perform the "timed hold" logic when they arrive at their target.
*   **Failure Recovery:** If a resource is depleted by another entity mid-cycle, the critter resets progress and immediately seeks a new target if they still have carry capacity.
*   **Stats (from Bible):**
    *   **SPD:** Determines how fast the circle fills.
    *   **STR:** Determines quantity gathered/work applied per cycle completion.

## 3. Obstacle Requirements
*   **Minimum Strength:** Complex tasks (like clearing a log or building a bridge) can have a total STR requirement.
*   **Summation:** The progress bar only advances if `sum(STR of assigned critters) >= requirement`.
*   **Feedback:** The player sees a progress indicator like "12/200 STR" when mousing over or near the obstacle.

## 4. Controls
*   **Interaction:** `E` or `Space Bar`.
*   **Menus:** `B` (Build Menu), `R` (Crafting Menu). HUD buttons exist for both.
*   **Logic:** Menu keys are for UI; interaction keys are for world-space physical actions.
