"""
A* pathfinding system for grid-based navigation.
"""
import heapq

class PathfindingSystem:
    """Finds paths on a GridSystem using A* with Manhattan heuristic."""
    def __init__(self):
        self._cache = {}

    def find_path(self, start, goal, grid):
        """
        Find a path from start to goal grid coordinates.

        Args:
            start: (gx, gy) tuple
            goal: (gx, gy) tuple
            grid: GridSystem instance providing is_occupied and get_neighbors

        Returns:
            List of (gx, gy) tuples representing the path from start to goal,
            or None if no path exists.
        """
        # Validate start/goal not occupied
        if grid.is_occupied(*start) or grid.is_occupied(*goal):
            return None

        key = (start, goal)
        if key in self._cache:
            return self._cache[key]

        # A* algorithm
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self._heuristic(start, goal)}

        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == goal:
                path = self._reconstruct_path(came_from, current, start)
                self._cache[key] = path
                return path

            for neighbor in grid.get_neighbors(*current):
                if grid.is_occupied(*neighbor):
                    continue
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + self._heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f, neighbor))

        # No path found
        self._cache[key] = None
        return None

    def _heuristic(self, a, b):
        """Manhattan distance between two grid points."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _reconstruct_path(self, came_from, current, start):
        """Build path by backtracking from current to start."""
        path = []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.append(start)
        path.reverse()
        return path

    def invalidate_cache(self):
        """Clear the path cache because the grid has changed."""
        self._cache.clear()
