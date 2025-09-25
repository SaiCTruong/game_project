# game/entities/goal.py
import pygame
from game.config import CELL_SIZE

class Goal:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.color = (50, 200, 50)  # xanh lá

    def draw(self, screen):
        px = self.x * CELL_SIZE
        py = self.y * CELL_SIZE
        pygame.draw.rect(screen, self.color, (px, py, CELL_SIZE, CELL_SIZE))
