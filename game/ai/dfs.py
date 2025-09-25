# game/ai/dfs.py
# DFS thường dùng recursion hoặc stack (list.pop())

def dfs_path(tiles, start, goal):
    """
    Thuật toán DFS: Tìm đường đi bằng cách đi sâu vào một nhánh.
    Lưu ý: Không đảm bảo tối ưu.
    """
    rows = len(tiles)
    cols = len(tiles[0])
    
    # Ngăn xếp: (node)
    stack = [start] 
    
    # Tập hợp các nút đã thăm
    visited = {start} 
    
    # Map để truy vết đường đi
    came_from = {start: None}

    while stack:
        current = stack.pop() # Lấy nút cuối cùng (LIFO)

        if current == goal:
            # Truy vết và trả về path
            path = []
            while current is not None:
                path.append(current)
                current = came_from.get(current)
            return path[::-1]

        x, y = current
        
        # Duyệt 4 hướng lân cận (thứ tự duyệt có thể ảnh hưởng)
        # DFS cần kiểm tra visited trước khi thêm vào stack để tránh vòng lặp vô hạn
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            nx, ny = neighbor

            if 0 <= ny < rows and 0 <= nx < cols and tiles[ny][nx] == 0 and neighbor not in visited:
                
                visited.add(neighbor)
                came_from[neighbor] = current
                stack.append(neighbor)

    return None # Không tìm thấy đường đi