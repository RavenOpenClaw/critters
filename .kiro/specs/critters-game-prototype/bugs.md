# Bug reports

## Overview

This doc describes bugs that the user found when testing (UAT).

Key principles:
- For each bug report, create a new entry in fixes.md
- Carefully consider the state before and after your fix. Prevent regression.
- Test your changes with automated test cases
- Tests must pass before merging

Bug report format:
1. A descriptive title of the format [<ID>] <TITLE>
2. Status - current status of this bug in the code base, (NOT_STARTED, IN_PROGRESS, PENDING_REVIEW, FIXED)
3. Expected - description of expected behavior
4. Actual - description of what actual behavior
5. Reproduce - a procedure to reproduce the bug
6. Desired fix - guidance about what/how to fix

## Reports

### [DLKJSIEQ] Collision between objects and the player seizes movement

Status: FIXED

Expected: As a player, if I'm moving to the right and colide with a world object like a bush, I should stop. While still moving to the right, I should be able to press "down" (the S key) to move diagonally down and to the right. The object prevents the movement to the right due to collision, but should not prevent the movement downwards. In other words, the player slides along the edge of the bush until clear of the collision box.

Actual: When the player collides with a world object, vertical movement is prevented even when colliding from the side, or vice versa. Sliding along an object is not possible as long as the player is holding a key that tries to push the player toward the object. Objects in the world are "sticky" and hold the player until they let go of the movement key that pushes them toward the object.

Reproduce: Start the game. Move toward a world object from the left (pressing right). Collide with the object. Press down or up while still holding down the right key.

Desired fix: Make it so the component of the blocked movement (the movement that would push the player into the collision box of the object) is canceled, but do not cancel the other component of movement.

### [WGFBKAX] Performance degrades over time during gameplay

Status: NOT_STARTED

Expected: The game should maintain a stable framerate (~60 FPS) and consistent responsiveness throughout extended play sessions.

Actual: The game becomes progressively slower; FPS drops and input/rendering lag increases the longer the game runs.

Reproduce: Start a new game and play for an extended period (10-30 minutes). Observe FPS counter (enable debug with F3). Note that FPS declines steadily or in steps. Performance does not recover upon saving/loading.

Desired fix: Identify and fix the underlying cause of resource/performance degradation. Potential areas to investigate:
- Pathfinding cache growth (does it invalidate correctly?)
- World object list growth (are new objects being added without old ones being removed?)
- Trampled cells set growing indefinitely?
- Entity count increasing (are critters or objects being duplicated?)
- Memory leaks (e.g., event queues, timers)
- Any per-frame allocations that accumulate

Note: User suggests binary search approach to isolate the cause by disabling subsystems until performance stabilizes.
