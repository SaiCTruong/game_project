# game/ai/astar.py
import heapq
import math

# --- 1. Hàm Heuristic: Manhattan Distance (h(n)) ---
def manhattan_distance(a, b):
    """Tính khoảng cách Manhattan (heuristic cho A*)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# --- 2. Hàm Heuristic: UCS/BFS Mode ---
def zero_heuristic(a, b):
    """Heuristic bằng 0. Khi h=0, A* trở thành Uniform Cost Search (UCS/BFS)."""
    return 0

# --- 3. Hàm A* (Thuật toán Đa năng) ---
def astar_path(tiles, start, goal, algorithm_mode="A_STAR"):
    """
    Thuật toán tìm đường A* linh hoạt.
    :param tiles: Ma trận map (0 = đường, 1 = tường)
    :param start: Tọa độ (x, y) bắt đầu
    :param goal: Tọa độ (x, y) mục tiêu
    :param algorithm_mode: "UCS" (dễ, trung bình) hoặc "A_STAR" (khó, rất khó)
    :return: List các tile trong đường đi, bao gồm cả start và goal.
    """
    
    rows = len(tiles)
    cols = len(tiles[0])
    
    # ----------------------------------------------------
    # QUYẾT ĐỊNH HEURISTIC DỰA TRÊN CHẾ ĐỘ (Mức độ Khó)
    # ----------------------------------------------------
    if algorithm_mode == "UCS": 
        # Mức DỄ/TRUNG BÌNH: Không có hướng dẫn, chỉ tìm đường ngắn nhất (g(n)).
        h_func = zero_heuristic
    else: 
        # Mức KHÓ/RẤT KHÓ: Có hướng dẫn, tìm đường thông minh (g(n) + h(n)).
        h_func = manhattan_distance
    # ----------------------------------------------------
    
    # Hàng đợi Ưu tiên: (f_score, node)
    open_set = [(0, start)]  
    
    # g_score: Chi phí thực tế đã đi từ start đến node
    g_score = {start: 0}
    
    # came_from: Map để truy vết đường đi
    came_from = {start: None}

    while open_set:
        f, current = heapq.heappop(open_set)

        if current == goal:
            # Truy vết và trả về path
            path = []
            while current is not None:
                path.append(current)
                current = came_from.get(current)
            return path[::-1]

        x, y = current
        
        # Duyệt 4 hướng lân cận
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            nx, ny = neighbor

            # Kiểm tra biên và tường
            if 0 <= ny < rows and 0 <= nx < cols and tiles[ny][nx] == 0:
                
                # Chi phí thực tế đến nút lân cận (chi phí luôn là 1)
                tentative_g_score = g_score.get(current, float('inf')) + 1
                
                # Nếu tìm thấy đường đi tốt hơn (g thấp hơn)
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    
                    g_score[neighbor] = tentative_g_score
                    came_from[neighbor] = current
                    
                    # Tính f_score = g + h, sử dụng h_func đã chọn
                    h_score = h_func(neighbor, goal) 
                    f_score = tentative_g_score + h_score
                    
                    # Thêm vào hàng đợi ưu tiên
                    heapq.heappush(open_set, (f_score, neighbor))

    return None # Không tìm thấy đường đi