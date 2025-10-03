import heapq
from collections import deque
import time

# --- HÀM HEURISTIC (Dùng chung) ---
def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# --- HÀM TIỆN ÍCH ---
def reconstruct_path(came_from, current):
    path = []
    while current is not None:
        path.append(current)
        current = came_from.get(current)
    return path[::-1]

# --- HÀM WRAPPER ĐỂ ĐO THỜI GIAN VÀ STATS ---
def find_path(tiles, start, goal, algorithm_func, guards=None):
    """
    Hàm này gọi một thuật toán tìm đường cụ thể, đo thời gian và trả về kết quả cùng với các thông số.
    """
    start_time = time.time()
    
    # Hàm thuật toán giờ sẽ trả về path, nodes_expanded, và nodes_generated
    result = algorithm_func(tiles, start, goal, guards=guards)
    
    end_time = time.time()

    if result:
        path, nodes_expanded, nodes_generated = result
    else:
        path, nodes_expanded, nodes_generated = None, 0, 0

    time_taken = end_time - start_time
    
    stats = {
        "time": time_taken,
        "path_length": len(path) if path else 0,
        "nodes_expanded": nodes_expanded,
        "nodes_generated": nodes_generated,
    }
    
    return path, stats

# --- CÁC THUẬT TOÁN TÌM ĐƯỜNG (ĐÃ CẬP NHẬT ĐẦY ĐỦ) ---


def astar_path(tiles, start, goal, guards=None):
    rows, cols = len(tiles), len(tiles[0])
    open_set = [(0, start)]
    g_score = {start: 0}
    came_from = {start: None}
    nodes_expanded = 0
    nodes_generated = 1

    while open_set:
        f, current = heapq.heappop(open_set)
        nodes_expanded += 1

        if current == goal:
            return reconstruct_path(came_from, current), nodes_expanded, nodes_generated

        x, y = current
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            nx, ny = neighbor
            if not (0 <= ny < rows and 0 <= nx < cols and tiles[ny][nx] == 0):
                continue
            
            # <<< XÓA BỎ KHỐI LOGIC `avoid_cost` Ở ĐÂY >>>
            
            tentative_g_score = g_score.get(current, float('inf')) + 1
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = tentative_g_score
                came_from[neighbor] = current
                f_score = tentative_g_score + manhattan_distance(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))
                nodes_generated += 1
                
    return None, nodes_expanded, nodes_generated

def dijkstra_path(tiles, start, goal, guards=None):
    rows, cols = len(tiles), len(tiles[0])
    open_set = [(0, start)]
    g_score = {start: 0}
    came_from = {start: None}
    nodes_expanded = 0
    nodes_generated = 1

    while open_set:
        cost, current = heapq.heappop(open_set)
        nodes_expanded += 1

        if current == goal:
            return reconstruct_path(came_from, current), nodes_expanded, nodes_generated

        x, y = current
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            nx, ny = neighbor
            if not (0 <= ny < rows and 0 <= nx < cols and tiles[ny][nx] == 0):
                continue

            new_cost = g_score.get(current, float('inf')) + 1
            if new_cost < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(open_set, (new_cost, neighbor))
                nodes_generated += 1
                
    return None, nodes_expanded, nodes_generated

def greedy_bfs_path(tiles, start, goal, guards=None):
    rows, cols = len(tiles), len(tiles[0])
    open_set = [(manhattan_distance(start, goal), start)]
    came_from = {start: None}
    visited = {start}
    nodes_expanded = 0
    nodes_generated = 1

    while open_set:
        _, current = heapq.heappop(open_set)
        nodes_expanded += 1
        
        if current == goal:
            return reconstruct_path(came_from, current), nodes_expanded, nodes_generated

        x, y = current
        # Sắp xếp neighbor không cần thiết nếu dùng priority queue, nhưng giữ lại để logic không đổi
        neighbors = [(x+dx, y+dy) for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]]

        for neighbor in neighbors:
            nx, ny = neighbor
            if not (0 <= ny < rows and 0 <= nx < cols and tiles[ny][nx] == 0):
                continue
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                priority = manhattan_distance(neighbor, goal)
                heapq.heappush(open_set, (priority, neighbor))
                nodes_generated += 1
                
    return None, nodes_expanded, nodes_generated

def bfs_path(tiles, start, goal, guards=None):
    rows, cols = len(tiles), len(tiles[0])
    queue = deque([start])
    visited = {start}
    came_from = {start: None}
    nodes_expanded = 0
    nodes_generated = 1

    while queue:
        current = queue.popleft()
        nodes_expanded += 1
        
        if current == goal:
            return reconstruct_path(came_from, current), nodes_expanded, nodes_generated

        x, y = current
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            nx, ny = neighbor
            if not (0 <= ny < rows and 0 <= nx < cols and tiles[ny][nx] == 0):
                continue
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)
                nodes_generated += 1
                
    return None, nodes_expanded, nodes_generated

def dfs_path(tiles, start, goal, guards=None):
    rows, cols = len(tiles), len(tiles[0])
    stack = [start]
    visited = {start}
    came_from = {start: None}
    nodes_expanded = 0
    nodes_generated = 1

    while stack:
        current = stack.pop()
        nodes_expanded += 1

        if current == goal:
            return reconstruct_path(came_from, current), nodes_expanded, nodes_generated

        x, y = current
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            nx, ny = neighbor
            if not (0 <= ny < rows and 0 <= nx < cols and tiles[ny][nx] == 0):
                continue
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                stack.append(neighbor)
                nodes_generated += 1
                
    return None, nodes_expanded, nodes_generated

# --- DICTIONARY TRUY CẬP CÁC THUẬT TOÁN ---
PATHFINDING_ALGORITHMS = {
    "A* (An toàn)": astar_path,
    "Dijkstra (UCS)": dijkstra_path,
    "Greedy Best-First": greedy_bfs_path,
    "Breadth-First (BFS)": bfs_path,
    "Depth-First (DFS)": dfs_path,
}