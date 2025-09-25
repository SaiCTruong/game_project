# game/entities/teleport_wall.py
import pygame
import random
import math
from game.config import CELL_SIZE

class TeleportWall:
    def __init__(self, x, y, grid, guards, color=(0, 200, 255)):
        self.x, self.y = x, y
        self.grid = grid
        self.guards = guards
        self.color = color

        cell = grid[y][x]
        closed_sides = [d for d, w in cell.walls.items() if w]  # chỉ cạnh là tường
        if closed_sides:
            self.side = random.choice(closed_sides)
        else:
            self.side = "N"  # fallback

    def draw(self, screen):
        x = self.x * CELL_SIZE
        y = self.y * CELL_SIZE
        c = self.color
        arrow_color = (255, 255, 0)

        if self.side == "N":
            pygame.draw.line(screen, c, (x, y), (x + CELL_SIZE, y), 3)
            points = [
                (x + CELL_SIZE // 2, y + 6),
                (x + CELL_SIZE // 2 - 5, y + 12),
                (x + CELL_SIZE // 2 + 5, y + 12)
            ]
            pygame.draw.polygon(screen, arrow_color, points)

        elif self.side == "S":
            pygame.draw.line(screen, c, (x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE), 3)
            points = [
                (x + CELL_SIZE // 2, y + CELL_SIZE - 6),
                (x + CELL_SIZE // 2 - 5, y + CELL_SIZE - 12),
                (x + CELL_SIZE // 2 + 5, y + CELL_SIZE - 12)
            ]
            pygame.draw.polygon(screen, arrow_color, points)

        elif self.side == "W":
            pygame.draw.line(screen, c, (x, y), (x, y + CELL_SIZE), 3)
            points = [
                (x + 6, y + CELL_SIZE // 2),
                (x + 12, y + CELL_SIZE // 2 - 5),
                (x + 12, y + CELL_SIZE // 2 + 5)
            ]
            pygame.draw.polygon(screen, arrow_color, points)

        elif self.side == "E":
            pygame.draw.line(screen, c, (x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE), 3)
            points = [
                (x + CELL_SIZE - 6, y + CELL_SIZE // 2),
                (x + CELL_SIZE - 12, y + CELL_SIZE // 2 - 5),
                (x + CELL_SIZE - 12, y + CELL_SIZE // 2 + 5)
            ]
            pygame.draw.polygon(screen, arrow_color, points)

    def try_teleport(self, player, keys):
        # Tọa độ trung tâm player (pixel)
        px = player.x * CELL_SIZE + CELL_SIZE // 2
        py = player.y * CELL_SIZE + CELL_SIZE // 2

        # Tọa độ trung tâm ô teleport (pixel)
        wx = self.x * CELL_SIZE + CELL_SIZE // 2
        wy = self.y * CELL_SIZE + CELL_SIZE // 2

        near = CELL_SIZE // 3  # độ gần để tính là "chạm vào"

        if abs(px - wx) < near and abs(py - wy) < near:
            # Check phím bấm đúng hướng cạnh
            if self.side == "N" and keys[pygame.K_UP]:
                nx, ny = random_safe_cell(self.grid, self.guards)
                player.x, player.y = nx, ny
            elif self.side == "S" and keys[pygame.K_DOWN]:
                nx, ny = random_safe_cell(self.grid, self.guards)
                player.x, player.y = nx, ny
            elif self.side == "E" and keys[pygame.K_RIGHT]:
                nx, ny = random_safe_cell(self.grid, self.guards)
                player.x, player.y = nx, ny
            elif self.side == "W" and keys[pygame.K_LEFT]:
                nx, ny = random_safe_cell(self.grid, self.guards)
                player.x, player.y = nx, ny

# ==== tìm ngõ cụt (deadends) ====
def find_deadends(grid):
    deadends = []
    for row in grid:
        for cell in row:
            open_neighbors = 0
            for dx, dy, wall_key, opp_wall in [
                (1, 0, "E", "W"),
                (-1, 0, "W", "E"),
                (0, 1, "S", "N"),
                (0, -1, "N", "S"),
            ]:
                nx, ny = cell.x + dx, cell.y + dy
                if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
                    neighbor = grid[ny][nx]
                    if not cell.walls[wall_key] and not neighbor.walls[opp_wall]:
                        open_neighbors += 1
            if open_neighbors == 1:
                deadends.append(cell)
    return deadends


# ==== chọn ô ngẫu nhiên an toàn ====
def random_safe_cell(grid, guards, min_dist=5):
    rows = len(grid)
    cols = len(grid[0])
    while True:
        nx = random.randint(0, cols - 1)
        ny = random.randint(0, rows - 1)
        safe = True
        for g in guards:
            dist = math.hypot(nx - g.x, ny - g.y)
            if dist < min_dist:
                safe = False
                break
        if safe:
            return nx, ny


# ==== tạo danh sách TeleportWalls từ deadends ====
def create_teleport_walls(deadends, grid, guards, max_walls=5):
    """Chỉ chọn ngẫu nhiên một số ngõ cụt để tạo cổng dịch chuyển"""
    walls = []
    if not deadends:
        return walls

    # Giới hạn số lượng teleport walls
    chosen = random.sample(deadends, min(max_walls, len(deadends)))

    for cell in chosen:
        walls.append(TeleportWall(cell.x, cell.y, grid, guards))
    return walls

