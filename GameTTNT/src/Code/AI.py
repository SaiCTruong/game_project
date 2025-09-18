# AI.py
import pygame
import threading
import os
import random
from Algorithms import ALGO_MAP

class Player:
    def __init__(self, maze, x=None, y=None):
        self.maze = maze
        self.x = x if x is not None else maze.start_x
        self.y = y if y is not None else maze.start_y
        self.path = []

    def move(self, dx, dy):
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < self.maze.width and 0 <= ny < self.maze.height and self.maze.grid[ny][nx] == 0:
            self.x, self.y = nx, ny

class Chaser:
    def __init__(self, maze, algo_name="BFS", detection_radius=8, speed=1):
        self.maze = maze
        self.x, self.y = self._spawn_free_cell()
        self.algo_name = algo_name
        self.detection_radius = detection_radius
        self.speed = speed  # cells per tick (int, normally 1)
        self.path = []
        self.chasing = False
        self.patrol_target = None

    def _spawn_free_cell(self):
        # random free cell not start/end
        attempts = 0
        while True:
            attempts += 1
            x = random.randint(1, self.maze.width - 2)
            y = random.randint(1, self.maze.height - 2)
            if self.maze.grid[y][x] == 0 and (x, y) not in self.maze.obstacles and (x, y) != (self.maze.start_x, self.maze.start_y) and (x, y) != (self.maze.end_x, self.maze.end_y):
                return x, y
            if attempts > 1000:
                return self.maze.start_x + 1, self.maze.start_y + 1

    def distance_to(self, px, py):
        return abs(self.x - px) + abs(self.y - py)

    def update_algorithm(self, name):
        if name in ALGO_MAP:
            self.algo_name = name

    def compute_path_to(self, target):
        algo = ALGO_MAP.get(self.algo_name, ALGO_MAP["BFS"])
        # Some algorithms (ids, dfs) accept different args; handle ids with max_depth param if needed
        if self.algo_name == "IDS":
            path = algo(self.maze, start=(self.x, self.y), goal=target, max_depth=100)
        elif self.algo_name == "DFS":
            path = algo(self.maze, start=(self.x, self.y), goal=target)
        else:
            path = algo(self.maze, start=(self.x, self.y), goal=target)
        return path

    def step_along_path(self):
        # move up to self.speed steps along path
        if len(self.path) > 1:
            # keep first element as current pos, next is next step
            # Remove first if matches current
            if self.path[0] == (self.x, self.y):
                self.path.pop(0)
            steps = min(self.speed, max(1, len(self.path)-0))
            for _ in range(steps):
                if len(self.path) > 0:
                    nx, ny = self.path.pop(0)
                    # ensure valid
                    if 0 <= nx < self.maze.width and 0 <= ny < self.maze.height and self.maze.grid[ny][nx] == 0:
                        self.x, self.y = nx, ny
                    else:
                        break

    def tick(self, player):
        # detect player
        if self.distance_to(player.x, player.y) <= self.detection_radius:
            # begin chase
            if not self.chasing:
                self.chasing = True
            # compute path to player's current pos
            self.path = self.compute_path_to((player.x, player.y))
            # ensure path starts at self pos
            if not self.path or self.path[0] != (self.x, self.y):
                # prepend current position
                self.path = [(self.x, self.y)] + self.path
            # move along path
            self.step_along_path()
        else:
            # out of detection radius
            if self.chasing:
                self.chasing = False
                self.path = []
            # simple patrol: move randomly occasionally
            if random.random() < 0.02:
                # pick a random reachable cell nearby as patrol target
                tx = max(1, min(self.maze.width - 2, self.x + random.randint(-5,5)))
                ty = max(1, min(self.maze.height - 2, self.y + random.randint(-5,5)))
                if self.maze.grid[ty][tx] == 0:
                    p = self.compute_path_to((tx, ty))
                    if p:
                        self.path = p
            # follow patrol path if any
            if self.path:
                if self.path[0] == (self.x, self.y):
                    self.path.pop(0)
                if self.path:
                    nx, ny = self.path.pop(0)
                    if self.maze.grid[ny][nx] == 0:
                        self.x, self.y = nx, ny

    def draw(self, screen, cell_size):
        # draw chaser as red square or icon if you have one
        try:
            current_dir = os.path.dirname(__file__)
            picture_dir = os.path.join(current_dir, "..", "Picture")
            icon = pygame.image.load(os.path.join(picture_dir, "chaser_icon.png"))
            icon = pygame.transform.scale(icon, (cell_size, cell_size))
            screen.blit(icon, (self.x * cell_size, self.y * cell_size))
        except Exception:
            pygame.draw.rect(screen, (200, 0, 0), (self.x * cell_size, self.y * cell_size, cell_size, cell_size))
