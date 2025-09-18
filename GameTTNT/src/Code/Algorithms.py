# Algorithms.py
# Các thuật toán tìm đường: BFS, DFS, IDS, A*, Greedy, UCS (Dijkstra)
import heapq
from collections import deque

def reconstruct_path(came_from, start, goal):
    path = []
    cur = goal
    while cur != start:
        path.append(cur)
        cur = came_from.get(cur)
        if cur is None:
            return []  # no path
    path.append(start)
    path.reverse()
    return path

# BFS
def bfs(maze, start=None, goal=None):
    if start is None:
        start = (maze.start_x, maze.start_y)
    if goal is None:
        goal = (maze.end_x, maze.end_y)
    frontier = deque([start])
    came_from = {start: None}
    while frontier:
        current = frontier.popleft()
        if current == goal:
            return reconstruct_path(came_from, start, goal)
        for n in maze.get_neighbors(current[0], current[1]):
            if n not in came_from:
                came_from[n] = current
                frontier.append(n)
    return []

# DFS (iterative, stack)
def dfs(maze, start=None, goal=None, depth_limit=None):
    if start is None:
        start = (maze.start_x, maze.start_y)
    if goal is None:
        goal = (maze.end_x, maze.end_y)
    stack = [(start, [start])]
    visited = set([start])
    while stack:
        current, path = stack.pop()
        if current == goal:
            return path
        # optionally depth-limited
        if depth_limit is not None and len(path) - 1 >= depth_limit:
            continue
        for n in maze.get_neighbors(current[0], current[1]):
            if n not in visited:
                visited.add(n)
                stack.append((n, path + [n]))
    return []

# IDS (iterative deepening DFS)
def ids(maze, start=None, goal=None, max_depth=50):
    if start is None:
        start = (maze.start_x, maze.start_y)
    if goal is None:
        goal = (maze.end_x, maze.end_y)
    for depth in range(max_depth + 1):
        path = dfs(maze, start, goal, depth_limit=depth)
        if path:
            return path
    return []

# Heuristic (Manhattan)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# A* (manhattan)
def astar(maze, start=None, goal=None):
    if start is None:
        start = (maze.start_x, maze.start_y)
    if goal is None:
        goal = (maze.end_x, maze.end_y)
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal:
            return reconstruct_path(came_from, start, goal)
        for n in maze.get_neighbors(current[0], current[1]):
            new_cost = cost_so_far[current] + 1
            if n not in cost_so_far or new_cost < cost_so_far[n]:
                cost_so_far[n] = new_cost
                priority = new_cost + heuristic(goal, n)
                heapq.heappush(frontier, (priority, n))
                came_from[n] = current
    return []

# Greedy Best-First (heuristic only)
def greedy(maze, start=None, goal=None):
    if start is None:
        start = (maze.start_x, maze.start_y)
    if goal is None:
        goal = (maze.end_x, maze.end_y)
    frontier = []
    heapq.heappush(frontier, (heuristic(start, goal), start))
    came_from = {start: None}
    visited = set([start])
    while frontier:
        _, current = heapq.heappop(frontier)
        if current == goal:
            return reconstruct_path(came_from, start, goal)
        for n in maze.get_neighbors(current[0], current[1]):
            if n not in visited:
                visited.add(n)
                heapq.heappush(frontier, (heuristic(n, goal), n))
                came_from[n] = current
    return []

# UCS (Dijkstra)
def ucs(maze, start=None, goal=None):
    if start is None:
        start = (maze.start_x, maze.start_y)
    if goal is None:
        goal = (maze.end_x, maze.end_y)
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    while frontier:
        cost, current = heapq.heappop(frontier)
        if current == goal:
            return reconstruct_path(came_from, start, goal)
        for n in maze.get_neighbors(current[0], current[1]):
            new_cost = cost_so_far[current] + 1
            if n not in cost_so_far or new_cost < cost_so_far[n]:
                cost_so_far[n] = new_cost
                heapq.heappush(frontier, (new_cost, n))
                came_from[n] = current
    return []

# Map string name -> function
ALGO_MAP = {
    "BFS": bfs,
    "DFS": dfs,
    "IDS": ids,
    "A*": astar,
    "Greedy": greedy,
    "UCS": ucs
}
