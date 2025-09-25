# game/ai/greedy.py
import heapq
import math

# --- Hàm Heuristic: Manhattan Distance (h(n)) ---
def manhattan_distance(a, b):
    """Tính khoảng cách Manhattan (ước lượng)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def greedy_path(tiles, start, goal):
    """
    Thuật toán Greedy Best-First Search: Chỉ sử dụng heuristic h(n).
    Lưu ý: Rất nhanh nhưng KHÔNG đảm bảo tối ưu.
    """
    rows = len(tiles)
    cols = len(tiles[0])
    
    # Hàng đợi Ưu tiên: (h_score, node)
    h_start = manhattan_distance(start, goal)
    open_set = [(h_start, start)]  
    
    # Tập hợp các nút đã được xử lý/thăm
    visited = {start}
    
    # Map để truy vết đường đi
    came_from = {start: None}

    while open_set:
        # Lấy nút có h_score thấp nhất ra (tham lam!)
        h, current = heapq.heappop(open_set)

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

            if 0 <= ny < rows and 0 <= nx < cols and tiles[ny][nx] == 0 and neighbor not in visited:
                
                visited.add(neighbor)
                came_from[neighbor] = current
                
                # Tính h_score và thêm vào PQ
                h_score = manhattan_distance(neighbor, goal)
                heapq.heappush(open_set, (h_score, neighbor))
                
    return None