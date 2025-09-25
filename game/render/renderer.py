# -*- coding: utf-8 -*-
import pygame
from game import config


def render_maze(screen, tiles, wall_img):
    for y in range(len(tiles)):
        for x in range(len(tiles[0])):
            if tiles[y][x] == 1:  # Tường
                rect = (x * config.CELL_SIZE, y * config.CELL_SIZE,
                        config.CELL_SIZE, config.CELL_SIZE)
                screen.blit(wall_img, rect)
