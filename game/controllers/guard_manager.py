# game/controllers/guard_manager.py
import random 
import pygame
from game.entities.guard import Guard
from game.config import CELL_SIZE, DIFFICULTY_SETTINGS
from game.ai.astar import astar_path

class GuardManager:
    def __init__(self, tiles, difficulty="NORMAL"): 
        self.tiles = tiles
        self.guards = []
        self.difficulty = difficulty
        self.settings = DIFFICULTY_SETTINGS[difficulty]
        self.algorithm_mode = self.settings["ALGORITHM_MODE"]
        self.guard_count = self.settings["GUARD_COUNT"]

    def add_guard(self, x, y):
        patrol_speed = self.settings["CHASE_SPEED"] - 1 
        chase_speed = self.settings["CHASE_SPEED"]
        detect_radius = self.settings["DETECT_RADIUS"]
        
        guard = Guard(x, y, tiles=self.tiles, 
                      patrol_speed=patrol_speed, 
                      chase_speed=chase_speed, 
                      detect_radius=detect_radius,
                      algorithm_mode=self.algorithm_mode) 
        self.guards.append(guard)
        return guard

    def spawn_guards(self):
        self.guards = [] 
        
        free_tiles = [
            (x, y)
            for y in range(len(self.tiles))
            for x in range(len(self.tiles[0]))
            if self.tiles[y][x] == 0 
        ]
        
        if (1, 1) in free_tiles: free_tiles.remove((1, 1))

        if len(free_tiles) < self.guard_count:
             print(f"CẢNH BÁO: Chỉ có thể spawn {len(free_tiles)} guards.")
             spawn_count = len(free_tiles)
        else:
             spawn_count = self.guard_count

        spawn_positions = random.sample(free_tiles, spawn_count)
        
        for pos in spawn_positions:
            self.add_guard(pos[0], pos[1])

    def compute_player_tile(self, player):
        cols = len(self.tiles[0])
        rows = len(self.tiles)
        
        px, py = player.get_tile_position() 
        
        tx = int(px)
        ty = int(py) 

        tx = max(0, min(cols - 1, tx))
        ty = max(0, min(rows - 1, ty))
        return (tx, ty)

    def update(self, player, always_recompute=True, debug=False):
        player_tile = self.compute_player_tile(player)
        
        for guard in self.guards:
            dist = guard.distance_to_player(player) 

            if dist <= guard.detect_radius:
                # CHASE
                guard.chasing = True
                guard.speed = self.settings["CHASE_SPEED"]
                
                path = astar_path(self.tiles, (guard.tile_x, guard.tile_y), player_tile)
                if path: guard.set_path(path)
                
            elif dist > guard.detect_radius + 2:
                # PATROL
                guard.chasing = False
                guard.speed = self.settings["CHASE_SPEED"] - 1 
                
                if not guard.path or guard.path_index >= len(guard.path):
                    guard.random_patrol()
            
            guard.update_movement()

    def draw(self, screen):
        for g in self.guards:
            g.draw(screen)