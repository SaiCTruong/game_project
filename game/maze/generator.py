# -*- coding: utf-8 -*-
import random
from .grid import Cell


def generate_maze(cols, rows, extra_prob=0.15):
    """Sinh mê cung bằng DFS backtracker + thêm đường phụ"""
    grid = [[Cell(x, y) for x in range(cols)] for y in range(rows)]
    stack = []

    current = grid[0][0]
    current.visited = True
    stack.append(current)

    while stack:
        current = stack[-1]
        neighbors = get_unvisited_neighbors(current, grid, cols, rows)
        if neighbors:
            nxt = random.choice(neighbors)
            remove_wall(current, nxt)
            nxt.visited = True
            stack.append(nxt)
        else:
            stack.pop()

    # 🔧 Đục thêm một số tường để tạo nhiều lối đi
    add_extra_passages(grid, cols, rows, extra_prob)

    return grid


def get_unvisited_neighbors(cell, grid, cols, rows):
    neighbors = []
    x, y = cell.x, cell.y
    if y > 0 and not grid[y - 1][x].visited:
        neighbors.append(grid[y - 1][x])  # North
    if y < rows - 1 and not grid[y + 1][x].visited:
        neighbors.append(grid[y + 1][x])  # South
    if x < cols - 1 and not grid[y][x + 1].visited:
        neighbors.append(grid[y][x + 1])  # East
    if x > 0 and not grid[y][x - 1].visited:
        neighbors.append(grid[y][x - 1])  # West
    return neighbors


def remove_wall(c1, c2):
    dx = c2.x - c1.x
    dy = c2.y - c1.y

    if dx == 1:   # c2 bên phải
        c1.walls["E"] = False
        c2.walls["W"] = False
    elif dx == -1:  # c2 bên trái
        c1.walls["W"] = False
        c2.walls["E"] = False
    elif dy == 1:   # c2 bên dưới
        c1.walls["S"] = False
        c2.walls["N"] = False
    elif dy == -1:  # c2 bên trên
        c1.walls["N"] = False
        c2.walls["S"] = False


def add_extra_passages(grid, cols, rows, extra_prob=0.15):
    """Đục thêm ngẫu nhiên một số tường để tạo nhiều đường đi"""
    for y in range(rows):
        for x in range(cols):
            cell = grid[y][x]
            if random.random() < extra_prob:  # xác suất đục thêm
                neighbors = []
                if y > 0:
                    neighbors.append(grid[y - 1][x])
                if y < rows - 1:
                    neighbors.append(grid[y + 1][x])
                if x > 0:
                    neighbors.append(grid[y][x - 1])
                if x < cols - 1:
                    neighbors.append(grid[y][x + 1])

                if neighbors:
                    nxt = random.choice(neighbors)
                    remove_wall(cell, nxt)


def maze_to_tiles(grid, cols, rows, wide_prob=0.1):
    """Chuyển mê cung sang ma trận tiles (0 = đường, 1 = tường),
       với một số đoạn hành lang rộng 2 ô"""
    h = rows * 2 + 1
    w = cols * 2 + 1
    tiles = [[1 for _ in range(w)] for _ in range(h)]

    for y in range(rows):
        for x in range(cols):
            cell = grid[y][x]
            cx, cy = x * 2 + 1, y * 2 + 1

            # Tâm ô -> đường
            tiles[cy][cx] = 0  

            # Kiểm tra tường mở và tạo đường (chỉ vẽ nếu trong khung an toàn)
            if not cell.walls["N"] and cy - 1 > 0:
                tiles[cy - 1][cx] = 0
            if not cell.walls["S"] and cy + 1 < h - 1:
                tiles[cy + 1][cx] = 0
            if not cell.walls["W"] and cx - 1 > 0:
                tiles[cy][cx - 1] = 0
            if not cell.walls["E"] and cx + 1 < w - 1:
                tiles[cy][cx + 1] = 0

    # 🔒 Ép viền ngoài = tường
    for x in range(w):
        tiles[0][x] = 1
        tiles[h - 1][x] = 1
    for y in range(h):
        tiles[y][0] = 1
        tiles[y][w - 1] = 1

    # 🟢 Mở rộng ngẫu nhiên hành lang
    for y in range(1, h-1):
        for x in range(1, w-1):
            if tiles[y][x] == 0 and random.random() < wide_prob:
                # Chọn ngẫu nhiên 1 hướng để mở rộng
                direction = random.choice([(0,1),(0,-1),(1,0),(-1,0)])
                nx, ny = x + direction[0], y + direction[1]
                if 0 <= nx < w and 0 <= ny < h:
                    tiles[ny][nx] = 0  # mở rộng thêm 1 ô bên cạnh

    tiles[0][1] = 0
    tiles[1][1] = 0
    exit_x = cols * 2 - 2
    exit_y = rows * 2 - 1
    
    if exit_y < h and exit_x < w:
        tiles[exit_y][exit_x] = 0
    if (exit_y + 1) < h and exit_x < w:
        tiles[exit_y + 1][exit_x] = 0

    return tiles

