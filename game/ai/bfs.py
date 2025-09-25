# game/ai/bfs.py
from collections import deque

def bfs_path(tiles, start, goal):
    """
    Thuật toán BFS: Tìm đường đi ngắn nhất (về số bước) trong đồ thị không trọng số.
    """
    rows = len(tiles)
    cols = len(tiles[0])
    
    # Hàng đợi: (node)
    queue = deque([start]) 
    
    # Tập hợp các nút đã được thêm vào queue
    visited = {start} 
    
    # Map để truy vết đường đi
    came_from = {start: None}

    while queue:
        current = queue.popleft() # Lấy nút đầu tiên (FIFO)

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

            # Kiểm tra biên, tường và nút đã thăm
            if 0 <= ny < rows and 0 <= nx < cols and tiles[ny][nx] == 0 and neighbor not in visited:
                
                visited.add(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)

    return None # Không tìm thấy đường đi