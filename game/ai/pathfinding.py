# game/ai/pathfinding.py
import heapq
from collections import deque
import time # <<< Import thư viện time

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

# <<< THÊM HÀM WRAPPER NÀY ĐỂ ĐO THỜI GIAN VÀ STATS >>>
def find_path(tiles, start, goal, algorithm_func, guards=None):
    """
    Hàm này gọi một thuật toán tìm đường cụ thể, đo thời gian và trả về kết quả cùng với các thông số.
    """
    start_time = time.time()
    
    # Gọi hàm thuật toán thực tế (ví dụ: astar_path, bfs_path,...)
    # và nhận lại path cùng số node đã duyệt
    result = algorithm_func(tiles, start, goal, guards=guards)
    
    end_time = time.time()

    # Xử lý kết quả trả về
    if result:
        path, nodes_expanded = result
    else: # Trường hợp không tìm thấy đường đi
        path, nodes_expanded = None, 0

    time_taken = end_time - start_time
    path_length = len(path) if path else 0
    
    # Tạo từ điển chứa các thông số
    stats = {
        "time": time_taken,
        "path_length": path_length,
        "nodes_expanded": nodes_expanded,
    }
    
    return path, stats


# --- CÁC THUẬT TOÁN TÌM ĐƯỜNG (Giữ nguyên như phiên bản trước) ---

def astar_path(tiles, start, goal, guards=None):
    rows, cols = len(tiles), len(tiles[0])
    open_set = [(0, start)]
    g_score = {start: 0}
    came_from = {start: None}
    nodes_expanded = 0

    while open_set:
        f, current = heapq.heappop(open_set)
        nodes_expanded += 1

        if current == goal:
            return reconstruct_path(came_from, current), nodes_expanded

        x, y = current
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            nx, ny = neighbor
            if not (0 <= ny < rows and 0 <= nx < cols and tiles[ny][nx] == 0):
                continue
            
            avoid_cost = 0
            if guards:
                for guard in guards:
                    dist = abs(nx - guard.tile_x) + abs(ny - guard.tile_y)
                    if dist <= 1: avoid_cost += 50000
                    elif dist <= 2: avoid_cost += 5000
            
            tentative_g_score = g_score.get(current, float('inf')) + 1 + avoid_cost
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                g_score[neighbor] = tentative_g_score
                came_from[neighbor] = current
                f_score = tentative_g_score + manhattan_distance(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))
                
    return None, nodes_expanded

def dijkstra_path(tiles, start, goal, guards=None):
    rows, cols = len(tiles), len(tiles[0])
    open_set = [(0, start)]
    g_score = {start: 0}
    came_from = {start: None}
    nodes_expanded = 0

    while open_set:
        cost, current = heapq.heappop(open_set)
        nodes_expanded += 1

        if current == goal:
            return reconstruct_path(came_from, current), nodes_expanded

        x, y = current
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            nx, ny = neighbor
            if not (0 <= ny < rows and 0 <= nx < cols and tiles[ny][nx] == 0):
                continue

            new_cost = g_score.get(current, float('inf')) + 1
            if neighbor not in g_score or new_cost < g_score[neighbor]:
                g_score[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(open_set, (new_cost, neighbor))
                
    return None, nodes_expanded

def greedy_bfs_path(tiles, start, goal, guards=None):
    rows, cols = len(tiles), len(tiles[0])
    open_set = [(0, start)]
    came_from = {start: None}
    visited = {start}
    nodes_expanded = 0

    while open_set:
        _, current = heapq.heappop(open_set)
        nodes_expanded += 1
        
        if current == goal:
            return reconstruct_path(came_from, current), nodes_expanded

        x, y = current
        neighbors = sorted([(x+dx, y+dy) for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]], 
                           key=lambda n: manhattan_distance(n, goal))

        for neighbor in neighbors:
            nx, ny = neighbor
            if not (0 <= ny < rows and 0 <= nx < cols and tiles[ny][nx] == 0):
                continue
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                priority = manhattan_distance(neighbor, goal)
                heapq.heappush(open_set, (priority, neighbor))
                
    return None, nodes_expanded

def bfs_path(tiles, start, goal, guards=None):
    rows, cols = len(tiles), len(tiles[0])
    queue = deque([start])
    visited = {start}
    came_from = {start: None}
    nodes_expanded = 0

    while queue:
        current = queue.popleft()
        nodes_expanded += 1
        
        if current == goal:
            return reconstruct_path(came_from, current), nodes_expanded

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
                
    return None, nodes_expanded

def dfs_path(tiles, start, goal, guards=None):
    rows, cols = len(tiles), len(tiles[0])
    stack = [start]
    visited = {start}
    came_from = {start: None}
    nodes_expanded = 0

    while stack:
        current = stack.pop()
        nodes_expanded += 1

        if current == goal:
            return reconstruct_path(came_from, current), nodes_expanded

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
                
    return None, nodes_expanded

# --- DICTIONARY TRUY CẬP CÁC THUẬT TOÁN ---
PATHFINDING_ALGORITHMS = {
    "A* (An toàn)": astar_path,
    "Dijkstra (UCS)": dijkstra_path,
    "Greedy Best-First": greedy_bfs_path,
    "Breadth-First (BFS)": bfs_path,
    "Depth-First (DFS)": dfs_path,
}