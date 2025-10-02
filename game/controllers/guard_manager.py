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
        
        # <<< BẮT ĐẦU THAY ĐỔI >>>
        
        # 1. Định nghĩa khoảng cách an toàn tối thiểu (tính bằng số ô)
        #    Bạn có thể thay đổi số 8 này để game dễ hơn hoặc khó hơn.
        MIN_SPAWN_DISTANCE = 8
        player_start_pos = (1, 1) # Vị trí bắt đầu của người chơi

        # 2. Lấy tất cả các ô có thể đi được như cũ
        free_tiles = [
            (x, y)
            for y in range(len(self.tiles))
            for x in range(len(self.tiles[0]))
            if self.tiles[y][x] == 0 
        ]
        
        # 3. Lọc ra danh sách các vị trí spawn "an toàn"
        #    Chỉ giữ lại những ô có khoảng cách (Manhattan distance) >= khoảng cách tối thiểu
        safe_spawn_locations = [
            tile for tile in free_tiles
            if (abs(tile[0] - player_start_pos[0]) + abs(tile[1] - player_start_pos[1])) >= MIN_SPAWN_DISTANCE
        ]
        
        # 4. Xác định số lượng guard cần spawn
        spawn_count = self.guard_count

        # 5. Kiểm tra xem có đủ vị trí an toàn để spawn không
        if len(safe_spawn_locations) < spawn_count:
            print(f"CẢNH BÁO: Không đủ vị trí spawn an toàn. Cố gắng spawn từ tất cả các vị trí có thể.")
            # Nếu không đủ, dùng lại danh sách cũ và loại bỏ vị trí người chơi
            if player_start_pos in free_tiles:
                free_tiles.remove(player_start_pos)
            
            # Đảm bảo không spawn nhiều hơn số ô trống có
            num_to_spawn = min(spawn_count, len(free_tiles))
            if num_to_spawn > 0:
                spawn_positions = random.sample(free_tiles, num_to_spawn)
            else:
                spawn_positions = [] # Không có chỗ để spawn

        else:
            # Nếu đủ, chọn ngẫu nhiên từ danh sách các vị trí an toàn
            spawn_positions = random.sample(safe_spawn_locations, spawn_count)

        # <<< KẾT THÚC THAY ĐỔI >>>
        
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