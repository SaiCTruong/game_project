import pygame
import math
import time
from game import config
from game.ai.pathfinding import PATHFINDING_ALGORITHMS, find_path

class Player:
    def __init__(self, start_x, start_y, tiles, algorithm_name="A* (An toàn)"):
        # --- (Các thuộc tính cũ giữ nguyên) ---
        self.tiles = tiles
        self.x, self.y = start_x, start_y
        self.size = config.CELL_SIZE
        
        sprite_sheet = pygame.image.load("game/assets/images/player.png").convert_alpha()
        sheet_w, sheet_h = sprite_sheet.get_size()
        frame_w, frame_h = sheet_w // 4, sheet_h // 4
        self.animations = {
            "down":  [pygame.transform.scale(sprite_sheet.subsurface(pygame.Rect(i*frame_w, 0*frame_h, frame_w, frame_h)), (self.size, self.size)) for i in range(4)],
            "left":  [pygame.transform.scale(sprite_sheet.subsurface(pygame.Rect(i*frame_w, 1*frame_h, frame_w, frame_h)), (self.size, self.size)) for i in range(4)],
            "right": [pygame.transform.scale(sprite_sheet.subsurface(pygame.Rect(i*frame_w, 2*frame_h, frame_w, frame_h)), (self.size, self.size)) for i in range(4)],
            "up":    [pygame.transform.scale(sprite_sheet.subsurface(pygame.Rect(i*frame_w, 3*frame_h, frame_w, frame_h)), (self.size, self.size)) for i in range(4)],
        }
        self.direction = "down"
        self.frame_index = 0
        self.last_anim_time = 0
        self.anim_speed = 150 
        self.move_delay = 100 
        self.last_move_time = 0 
        self.is_moving = False
        
        self.ai_mode = False       
        self.ai_path = []          
        self.ai_path_index = 0
        
        self.algorithm_name = algorithm_name
        self.pathfinding_algorithm = PATHFINDING_ALGORITHMS[algorithm_name]
        self.pathfinding_stats = None
        self.footprints = []

        # <<< THAY ĐỔI 1: Thêm các biến cho logic né tránh mới >>>
        self.is_evading = False
        self.evasion_path = []
        self.evasion_path_index = 0

    def move(self, dx, dy, direction):
        new_x, new_y = self.x + dx, self.y + dy
        if 0 <= new_y < len(self.tiles) and 0 <= new_x < len(self.tiles[0]) and self.tiles[new_y][new_x] == 0:
            old_pos = (self.x, self.y)
            if not self.footprints or self.footprints[-1] != old_pos:
                self.footprints.append(old_pos)
            self.x, self.y = new_x, new_y
            self.direction = direction
            self.is_moving = True
            return True
        self.is_moving = False
        return False

    def get_tile_position(self): 
        return (self.x, self.y)

    def check_collision_with_guard(self, guard):
        player_rect = pygame.Rect(self.x * self.size, self.y * self.size, self.size, self.size)
        guard_rect = pygame.Rect(guard.pixel_x, guard.pixel_y, guard.size, guard.size)
        return player_rect.inflate(-self.size * 0.4, -self.size * 0.4).colliderect(
               guard_rect.inflate(-guard.size * 0.4, -guard.size * 0.4))

    def is_tile_dangerous(self, tile, guards):
        """Kiểm tra xem một ô có nguy hiểm không (lính gác ở trên hoặc ngay cạnh)."""
        if not guards:
            return False
        for guard in guards:
            dist = abs(tile[0] - guard.tile_x) + abs(tile[1] - guard.tile_y)
            if dist <= 1:
                return True
        return False

    def find_best_evasion_spot(self, current_tile, guards):
        """Tìm điểm né tốt nhất ở gần, ưu tiên xa lính gác."""
        best_spot, max_score, scan_radius = None, -float('inf'), 10
        for y in range(max(0, current_tile[1] - scan_radius), min(len(self.tiles), current_tile[1] + scan_radius)):
            for x in range(max(0, current_tile[0] - scan_radius), min(len(self.tiles[0]), current_tile[0] + scan_radius)):
                if self.tiles[y][x] != 0: continue
                spot = (x, y)
                dist_to_g = min([abs(spot[0] - g.tile_x) + abs(spot[1] - g.tile_y) for g in guards]) if guards else float('inf')
                dist_from_p = abs(spot[0] - current_tile[0]) + abs(spot[1] - current_tile[1])
                score = 1.5 * dist_to_g - dist_from_p
                if score > max_score:
                    max_score, best_spot = score, spot
        return best_spot if best_spot else current_tile

    # <<< THAY ĐỔI 2: Viết lại hoàn toàn hàm handle_ai_move >>>
    def handle_ai_move(self, tiles, exit_tile, guards):
        AI_MOVE_DELAY = 80
        now = pygame.time.get_ticks()
        if now - self.last_move_time < AI_MOVE_DELAY:
            return

        current_tile = (self.x, self.y)
        next_move = None

        # --- Logic né tránh (Ưu tiên cao nhất) ---
        if self.is_evading:
            if self.evasion_path and self.evasion_path_index < len(self.evasion_path):
                # Nếu đang trong quá trình né, tiếp tục đi theo đường né
                next_move = self.evasion_path[self.evasion_path_index]
                self.evasion_path_index += 1
            else:
                # Đã đến điểm né an toàn, thoát khỏi chế độ né tránh
                self.is_evading = False
                self.ai_path = [] # Xóa đường đi chính để buộc tính toán lại
                self.is_moving = False
                return
        
        # --- Logic tìm đường chính ---
        else:
            if not self.ai_path or self.ai_path_index >= len(self.ai_path):
                # Nếu không có đường đi chính, tìm một đường mới đến lối ra
                path, stats = find_path(tiles, current_tile, exit_tile, self.pathfinding_algorithm)
                if stats:
                    stats["name"] = self.algorithm_name
                    self.pathfinding_stats = stats
                
                if path and len(path) > 1:
                    self.ai_path = path
                    self.ai_path_index = 1
                else:
                    self.is_moving = False
                    return

            # Lấy bước đi tiếp theo trong đường đi chính
            next_tile_in_path = self.ai_path[self.ai_path_index]

            if self.is_tile_dangerous(next_tile_in_path, guards):
                # Nếu nguy hiểm -> Bật chế độ né tránh
                self.is_evading = True
                evasion_goal = self.find_best_evasion_spot(current_tile, guards)
                
                # Tìm đường đi ngắn hạn đến điểm né
                evasion_path, _ = find_path(tiles, current_tile, evasion_goal, self.pathfinding_algorithm)

                if evasion_path and len(evasion_path) > 1:
                    self.evasion_path = evasion_path
                    self.evasion_path_index = 1 # Bắt đầu đi từ bước thứ 2 (bước 1 là vị trí hiện tại)
                    next_move = self.evasion_path[self.evasion_path_index] 
                    self.evasion_path_index += 1 # Chuẩn bị cho lượt đi tiếp theo
                else:
                    # Không tìm được đường né, đứng yên
                    self.is_moving = False
                    return
            else:
                # Nếu an toàn, tiếp tục đi theo đường đi chính
                next_move = next_tile_in_path
                self.ai_path_index += 1

        # --- Thực hiện di chuyển ---
        if next_move:
            dx = next_move[0] - current_tile[0]
            dy = next_move[1] - current_tile[1]
            
            if dx != 0 or dy != 0:
                direction = "up" if dy < 0 else "down" if dy > 0 else "left" if dx < 0 else "right"
                if self.move(dx, dy, direction):
                    self.last_move_time = now
            else:
                self.is_moving = False
        else:
            self.is_moving = False

    def handle_input(self):
        if self.ai_mode: return
        keys = pygame.key.get_pressed(); now = pygame.time.get_ticks()
        self.is_moving = False
        if now - self.last_move_time > self.move_delay:
            moved = False
            if keys[pygame.K_UP] or keys[pygame.K_w]: moved = self.move(0, -1, "up")
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]: moved = self.move(0, 1, "down")
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]: moved = self.move(-1, 0, "left")
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]: moved = self.move(1, 0, "right")
            if moved: self.last_move_time = now

    def update_animation(self):
        if self.is_moving:
            now = pygame.time.get_ticks()
            if now - self.last_anim_time > self.anim_speed:
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.direction])
                self.last_anim_time = now
        else: self.frame_index = 0

    def draw(self, screen):
        self.update_animation()
        frame = self.animations[self.direction][self.frame_index]
        screen.blit(frame, (self.x * self.size, self.y * self.size))