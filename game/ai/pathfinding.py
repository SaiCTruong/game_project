import heapq
from collections import deque
import time
import random
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

# --- CÁC THUẬT TOÁN TÌM ĐƯỜNG ---


def astar_path(tiles, start, goal, guards=None):
    rows, cols = len(tiles), len(tiles[0])
    open_set = [(0, start)]
    g_score = {start: 0}
    came_from = {start: None}
    nodes_expanded = 0
    nodes_generated = 1
    while open_set:
        f, current = heapq.heappop(open_set)
        if g_score[current] < (f - manhattan_distance(current, goal)):
            continue
        nodes_expanded += 1
        if current == goal:
            return reconstruct_path(came_from, current), nodes_expanded, nodes_generated
        x, y = current
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            nx, ny = neighbor
            if not (0 <= ny < rows and 0 <= nx < cols and tiles[ny][nx] == 0):
                continue
            # 1. Chi phí di chuyển cơ bản là 1
            movement_cost = 1
            # 2. Tính toán "chi phí nguy hiểm"
            danger_cost = 0
            if guards:
                for guard in guards:
                    dist = manhattan_distance(neighbor, (guard.tile_x, guard.tile_y))
                    if dist == 0: danger_cost += 1000 # Rất nguy hiểm: Đè lên lính gác
                    elif dist == 1: danger_cost += 50   # Nguy hiểm: Ngay cạnh lính gác
                    elif dist == 2: danger_cost += 20   # Cẩn trọng: Gần lính gác
                    elif dist == 3: danger_cost += 5    # Hơi gần
            # 3. Tổng chi phí để đi đến ô hàng xóm
            tentative_g_score = g_score.get(current, float('inf')) + movement_cost + danger_cost
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                g_score[neighbor] = tentative_g_score
                came_from[neighbor] = current
                f_score = tentative_g_score + manhattan_distance(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))
                nodes_generated += 1
    return None, nodes_expanded, nodes_generated

def UCS_path(tiles, start, goal, guards=None):
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


def hill_climbing_path(tiles, start, goal, guards=None):
    rows, cols = len(tiles), len(tiles[0])
    current = start
    path = [current]
    visited = {current}
    nodes_expanded = 0
    nodes_generated = 1
    max_steps = rows * cols * 2 # Tăng giới hạn số bước
    restart_count = 0

    for _ in range(max_steps):
        if current == goal:
            return path, nodes_expanded, nodes_generated

        nodes_expanded += 1
        x, y = current
        
        neighbors = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            if (0 <= neighbor[1] < rows and 0 <= neighbor[0] < cols and 
                tiles[neighbor[1]][neighbor[0]] == 0 and neighbor not in visited):
                neighbors.append(neighbor)
                nodes_generated += 1
        if not neighbors: # Bị kẹt
            if restart_count < 5 and len(path) > 1: # Giới hạn số lần restart
                restart_count += 1
                current = random.choice(path[:-1]) # Quay lại 1 điểm ngẫu nhiên
                continue
            else:
                return None, nodes_expanded, nodes_generated
        best_neighbor = min(neighbors, key=lambda n: manhattan_distance(n, goal))

        if manhattan_distance(best_neighbor, goal) >= manhattan_distance(current, goal):
             # Bị kẹt ở local minimum
            if restart_count < 5 and len(path) > 1:
                restart_count += 1
                current = random.choice(path[:-1])
                continue
            else:
                return None, nodes_expanded, nodes_generated
        current = best_neighbor
        path.append(current)
        visited.add(current)
    return None, nodes_expanded, nodes_generated

def beam_search_path(tiles, start, goal, guards=None):
    BEAM_WIDTH = 3
    rows, cols = len(tiles), len(tiles[0])
    
    # Sử dụng hàng đợi ưu tiên để luôn lấy nút tốt nhất từ chùm tia
    open_set = [(manhattan_distance(start, goal), start)]
    came_from = {start: None}

    nodes_expanded = 0
    nodes_generated = 1

    while open_set:
        # Tập hợp các nút sẽ được xét ở bước tiếp theo
        successors = []
        
        # Mở rộng tất cả các nút trong chùm tia hiện tại
        for _ in range(len(open_set)):
            _, current = heapq.heappop(open_set)
            nodes_expanded += 1

            if current == goal:
                return reconstruct_path(came_from, current), nodes_expanded, nodes_generated
            
            x, y = current
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = (x + dx, y + dy)
                if (0 <= neighbor[1] < rows and 0 <= neighbor[0] < cols and
                    tiles[neighbor[1]][neighbor[0]] == 0 and neighbor not in came_from):
                    
                    came_from[neighbor] = current # Ghi lại đường đi
                    priority = manhattan_distance(neighbor, goal)
                    heapq.heappush(successors, (priority, neighbor))
                    nodes_generated += 1
        
        # Cắt tỉa: chỉ giữ lại BEAM_WIDTH nút tốt nhất từ tất cả các successors
        open_set = heapq.nsmallest(BEAM_WIDTH, successors)
        if not open_set:
            break # Không còn đường để đi

    return None, nodes_expanded, nodes_generated

# --- DICTIONARY TRUY CẬP CÁC THUẬT TOÁN ---
PATHFINDING_ALGORITHMS = {
    "A* (An toàn)": astar_path,
    "Uniform Cost Search (UCS)": UCS_path,
    "Greedy Best-First": greedy_bfs_path,
    "Breadth-First (BFS)": bfs_path,
    "Depth-First (DFS)": dfs_path,
    "Hill Climbing": hill_climbing_path,
    "Beam Search": beam_search_path,
}