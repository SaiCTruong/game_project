# -*- coding: utf-8 -*-
class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Tường bao quanh ô: True = còn tường
        self.walls = {"N": True, "S": True, "E": True, "W": True}
        self.visited = False
