# Bug fixes

## Overview

This doc should document fixes for bugs reported in bugs.md.

Key principles:
- For each bug report in bugs.md, create a new entry here in fixes.md.
- Carefully consider the state before and after your fix. Prevent regression.
- Keep your bug fix to a single squashed commit in `mainline` branch.
- Test your changes with automated test cases.
- Tests must pass before merging.
- After fixing a bug, update the status to PENDING_REVIEW in both the bug report status and bug fix. **Human review** is required to change status to FIXED.

Bug fix format:
1. Use the same ID and descriptive title from the bug report, so it is easy to correlate bug reports with fixes
2. Status - current status of this bug in the code base, (NOT_STARTED, IN_PROGRESS, PENDING_REVIEW, FIXED)
2. Plan - implementation plan to fix the bug
3. Implementation - a log of the actual actions you took to fix the bug - inlude a commit ID for precise tracking.
4. Testing - the testing you did to confirm the bug is fixed, including the test cases you added to prevent regression

## Fixes

### [DLKJSIEQ] Collision between objects and the player seizes movement

Status: NOT_STARTED

Plan:

Implementation:

Testing: