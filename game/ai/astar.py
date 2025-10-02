# game/ai/astar.py
import heapq
import math

def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def zero_heuristic(a, b):
    return 0

def astar_path(tiles, start, goal, algorithm_mode="A_STAR", guards=None):
    rows = len(tiles)
    cols = len(tiles[0])
    
    if algorithm_mode == "UCS": 
        h_func = zero_heuristic
    else: 
        h_func = manhattan_distance
    
    open_set = [(0, start)]  
    g_score = {start: 0}
    came_from = {start: None}

    while open_set:
        f, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current is not None:
                path.append(current)
                current = came_from.get(current)
            return path[::-1]

        x, y = current
        
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            nx, ny = neighbor

            if 0 <= ny < rows and 0 <= nx < cols and tiles[ny][nx] == 0:
                
                avoid_cost = 0
                if guards:
                    for guard in guards:
                        gx, gy = guard.tile_x, guard.tile_y
                        dist = abs(nx - gx) + abs(ny - gy)
                        
                        # <<< NÂNG CẤP 3: CHI PHÍ ĐỘNG >>>
                        # 1. Dự đoán vị trí tiếp theo của guard
                        guard_next_pos = None
                        if guard.path and guard.path_index < len(guard.path):
                            guard_next_pos = guard.path[guard.path_index]

                        # 2. Phạt cực nặng nếu ô đang xét là điểm đến tiếp theo của guard
                        if guard_next_pos and neighbor == guard_next_pos:
                            avoid_cost += 200000 

                        # 3. Áp dụng chi phí tĩnh như cũ
                        if dist == 0:
                            avoid_cost += 100000
                        elif dist == 1:
                            avoid_cost += 50000 
                        elif dist == 2:
                            avoid_cost += 5000  
                
                tentative_g_score = g_score.get(current, float('inf')) + 1 + avoid_cost
                
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    g_score[neighbor] = tentative_g_score
                    came_from[neighbor] = current
                    h_score = h_func(neighbor, goal) 
                    f_score = tentative_g_score + h_score
                    heapq.heappush(open_set, (f_score, neighbor))

    return None