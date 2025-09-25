# game/controllers/guard_manager.py
import random # <--- CẦN THIẾT cho random.sample()
from game.entities.guard import Guard
from game.config import CELL_SIZE, DIFFICULTY_SETTINGS
from game.ai.astar import astar_path
# from game.maze.generator import maze_to_tiles # Tùy chọn, không cần thiết nếu tiles đã được tạo

class GuardManager:
    # Nhận tên độ khó đã chọn
    def __init__(self, tiles, difficulty="NORMAL"): 
        self.tiles = tiles
        self.guards = []
        self.difficulty = difficulty
        self.settings = DIFFICULTY_SETTINGS[difficulty]
        self.algorithm_mode = self.settings["ALGORITHM_MODE"]
        self.guard_count = self.settings["GUARD_COUNT"]

    def add_guard(self, x, y):
        # Sử dụng các giá trị từ cấu hình đã chọn
        patrol_speed = self.settings["CHASE_SPEED"] - 1 
        chase_speed = self.settings["CHASE_SPEED"]
        detect_radius = self.settings["DETECT_RADIUS"]
        
        guard = Guard(x, y, tiles=self.tiles, 
                      patrol_speed=patrol_speed, 
                      chase_speed=chase_speed, 
                      detect_radius=detect_radius,
                      algorithm_mode=self.algorithm_mode) # Truyền mode cho Guard
        self.guards.append(guard)
        return guard

    def spawn_guards(self):
        """Hàm mới: Sinh ra số lượng Guard dựa trên cấu hình độ khó."""
        self.guards = [] # Đảm bảo danh sách guard trống rỗng trước khi sinh mới
        
        free_tiles = [
            (x, y)
            for y in range(len(self.tiles))
            for x in range(len(self.tiles[0]))
            if self.tiles[y][x] == 0 
        ]
        
        # Loại trừ vị trí spawn của Player (giả sử Player luôn ở (1, 1))
        if (1, 1) in free_tiles: free_tiles.remove((1, 1))

        # Kiểm tra nếu số ô trống không đủ để spawn Guard
        if len(free_tiles) < self.guard_count:
             print(f"CẢNH BÁO: Chỉ có thể spawn {len(free_tiles)} guards.")
             spawn_count = len(free_tiles)
        else:
             spawn_count = self.guard_count

        spawn_positions = random.sample(free_tiles, spawn_count)
        
        for pos in spawn_positions:
            self.add_guard(pos[0], pos[1])


    # --- LOGIC CẦN THIẾT KHÔI PHỤC ---

    def compute_player_tile(self, player):
        """Lấy tọa độ Tile (lưới) của Player."""
        cols = len(self.tiles[0])
        rows = len(self.tiles)
        
        tx = int(player.x)
        ty = int(player.y) 

        tx = max(0, min(cols - 1, tx))
        ty = max(0, min(rows - 1, ty))
        return (tx, ty)

    def update(self, player, always_recompute=True, debug=False):
        player_tile = self.compute_player_tile(player)
        
        for guard in self.guards:
            dist = guard.distance_to_player(player) # Khoảng cách tính bằng Tile

            if dist <= guard.detect_radius:
                # 1. CHASE (Đuổi bắt)
                guard.chasing = True
                guard.speed = self.settings["CHASE_SPEED"]
                
                # Gọi A* với mode đã chọn (UCS hoặc A_STAR)
                path = astar_path(self.tiles, (guard.tile_x, guard.tile_y), player_tile, 
                                  algorithm_mode=self.algorithm_mode)
                if path: guard.set_path(path)
                
            elif dist > guard.detect_radius + 2:
                # 2. PATROL (Quay lại Tuần tra)
                guard.chasing = False
                guard.speed = self.settings["CHASE_SPEED"] - 1 # Tốc độ tuần tra
                
                # Nếu path cũ đã hết, chọn đường tuần tra mới
                if not guard.path or guard.path_index >= len(guard.path):
                    # Guard tự gọi random_patrol() bên trong để tìm đường A* mới
                    guard.random_patrol()
            else:
                # 3. Giữ trạng thái hiện tại (vùng đệm)
                pass

            guard.update_movement() # Gọi hàm update riêng để chỉ xử lý di chuyển

    def draw(self, screen):
        for g in self.guards:
            g.draw(screen)