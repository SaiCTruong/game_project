from queue import PriorityQueue, deque

# Heuristic (dùng cho A* và Greedy)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# =============================
#  BFS - Breadth First Search
# =============================
def bfs(maze):
    start = (maze.start_x, maze.start_y)
    goal = (maze.end_x, maze.end_y)

    queue = deque([start])
    came_from = {start: None}

    while queue:
        current = queue.popleft()

        if current == goal:
            break

        for next in maze.get_neighbors(current[0], current[1]):
            if next not in came_from:
                queue.append(next)
                came_from[next] = current

    return reconstruct_path(came_from, start, goal)


# =============================
#  DFS - Depth First Search
# =============================
def dfs(maze):
    start = (maze.start_x, maze.start_y)
    goal = (maze.end_x, maze.end_y)

    stack = [start]
    came_from = {start: None}

    while stack:
        current = stack.pop()

        if current == goal:
            break

        for next in maze.get_neighbors(current[0], current[1]):
            if next not in came_from:
                stack.append(next)
                came_from[next] = current

    return reconstruct_path(came_from, start, goal)


# =============================
#  UCS - Uniform Cost Search
# =============================
def ucs(maze):
    start = (maze.start_x, maze.start_y)
    goal = (maze.end_x, maze.end_y)

    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while not frontier.empty():
        _, current = frontier.get()

        if current == goal:
            break

        for next in maze.get_neighbors(current[0], current[1]):
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                frontier.put((new_cost, next))
                came_from[next] = current

    return reconstruct_path(came_from, start, goal)


# =============================
#  IDS - Iterative Deepening Search
# =============================
def ids(maze, max_depth=50):
    start = (maze.start_x, maze.start_y)
    goal = (maze.end_x, maze.end_y)

    for depth in range(max_depth):
        found, came_from = dls(maze, start, goal, depth)
        if found:
            return reconstruct_path(came_from, start, goal)

    return []


def dls(maze, start, goal, depth):
    stack = [(start, 0)]
    came_from = {start: None}

    while stack:
        current, d = stack.pop()

        if current == goal:
            return True, came_from

        if d < depth:
            for next in maze.get_neighbors(current[0], current[1]):
                if next not in came_from:
                    stack.append((next, d + 1))
                    came_from[next] = current

    return False, came_from


# =============================
#  Greedy Best-First Search
# =============================
def greedy(maze):
    start = (maze.start_x, maze.start_y)
    goal = (maze.end_x, maze.end_y)

    frontier = PriorityQueue()
    frontier.put((heuristic(start, goal), start))
    came_from = {start: None}

    while not frontier.empty():
        _, current = frontier.get()

        if current == goal:
            break

        for next in maze.get_neighbors(current[0], current[1]):
            if next not in came_from:
                priority = heuristic(goal, next)
                frontier.put((priority, next))
                came_from[next] = current

    return reconstruct_path(came_from, start, goal)


# =============================
#  A* Search
# =============================
def astar(maze):
    start = (maze.start_x, maze.start_y)
    goal = (maze.end_x, maze.end_y)

    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while not frontier.empty():
        _, current = frontier.get()

        if current == goal:
            break

        for next in maze.get_neighbors(current[0], current[1]):
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put((priority, next))
                came_from[next] = current

    return reconstruct_path(came_from, start, goal)


# =============================
#  Dijkstra
# =============================
def dijkstra(maze):
    start = (maze.start_x, maze.start_y)
    goal = (maze.end_x, maze.end_y)

    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while not frontier.empty():
        _, current = frontier.get()

        if current == goal:
            break

        for next in maze.get_neighbors(current[0], current[1]):
            new_cost = cost_so_far[current] + 1
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                frontier.put((new_cost, next))
                came_from[next] = current

    return reconstruct_path(came_from, start, goal)


# =============================
#  Helper: reconstruct path
# =============================
def reconstruct_path(came_from, start, goal):
    if goal not in came_from:
        return []

    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.append(start)
    path.reverse()
    return path
