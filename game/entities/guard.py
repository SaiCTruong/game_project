# game/entities/guard.py (Đã sửa lỗi TypeError)
import pygame, random, math
from game import config
from game.ai.astar import astar_path # Sử dụng astar_path cho tuần tra

class Guard:
    # THÊM THAM SỐ algorithm_mode VÀO __init__
    def __init__(self, start_x, start_y, tiles, patrol_speed=1, chase_speed=3, detect_radius=5, algorithm_mode="A_STAR"):
        self.tiles = tiles
        self.size = config.CELL_SIZE

        # Tile coords
        self.tile_x = start_x
        self.tile_y = start_y
        # Pixel coords
        self.pixel_x = self.tile_x * self.size
        self.pixel_y = self.tile_y * self.size

        self.patrol_speed = patrol_speed
        self.chase_speed = chase_speed
        self.speed = patrol_speed
        
        # LƯU MODE THUẬT TOÁN ĐÃ CHỌN
        self.algorithm_mode = algorithm_mode 

        # Target pixel
        self.target_pixel_x = self.pixel_x
        self.target_pixel_y = self.pixel_y

        # Pathfinding
        self.path = []
        self.path_index = 0

        # Detection
        self.detect_radius = detect_radius
        self.chasing = False

        # Load sprite sheet... (giữ nguyên)
        sprite_sheet = pygame.image.load("game/assets/images/guard.png").convert_alpha()
        sheet_w, sheet_h = sprite_sheet.get_size()
        frame_w = sheet_w // 4
        frame_h = sheet_h // 4
        self.animations = {
            "down":  [pygame.transform.scale(sprite_sheet.subsurface(pygame.Rect(i*frame_w, 0, frame_w, frame_h)), (self.size, self.size)) for i in range(4)],
            "right": [pygame.transform.scale(sprite_sheet.subsurface(pygame.Rect(i*frame_w, frame_h, frame_w, frame_h)), (self.size, self.size)) for i in range(4)],
            "left":  [pygame.transform.scale(sprite_sheet.subsurface(pygame.Rect(i*frame_w, 2*frame_h, frame_w, frame_h)), (self.size, self.size)) for i in range(4)],
            "up":    [pygame.transform.scale(sprite_sheet.subsurface(pygame.Rect(i*frame_w, 3*frame_h, frame_w, frame_h)), (self.size, self.size)) for i in range(4)],
        }

        self.direction = "down"
        self.frame_index = 0
        self.last_anim_time = 0
        self.anim_speed = 200

        # Khởi tạo tuần tra
        self.random_patrol()

    # --- Khoảng cách đến player ---
    def distance_to_player(self, player):
        dx = player.x - self.tile_x
        dy = player.y - self.tile_y
        return math.sqrt(dx*dx + dy*dy)

    # --- Chọn tile ngẫu nhiên để tuần tra ---
    def random_patrol(self):
        free_tiles = [
            (x, y)
            for y in range(len(self.tiles))
            for x in range(len(self.tiles[0]))
            if self.tiles[y][x] == 0
        ]
        if not free_tiles:
            return

        target = random.choice(free_tiles)

        # GỌI A* VỚI MODE ĐÃ LƯU
        path = astar_path(self.tiles, (self.tile_x, self.tile_y), target, 
                          algorithm_mode=self.algorithm_mode)
        if path:
            self.set_path(path)

    # --- Set path và target pixel ---
    def set_path(self, path):
        if path:
            self.path = path[1:]
            self.path_index = 0
            if self.path:
                tx, ty = self.path[0]
                self.target_pixel_x = tx * self.size
                self.target_pixel_y = ty * self.size

    # --- Di chuyển theo path (giữ nguyên logic đã sửa) ---
    def move_along_path(self):
        if not self.path or self.path_index >= len(self.path):
            if not self.chasing:
                 self.random_patrol()
            return

        tx, ty = self.path[self.path_index]
        self.target_pixel_x = tx * self.size
        self.target_pixel_y = ty * self.size

        dx = self.target_pixel_x - self.pixel_x
        dy = self.target_pixel_y - self.pixel_y
        
        if abs(dx) > abs(dy):
            step = self.speed if dx > 0 else -self.speed
            if abs(step) > abs(dx): step = dx
            self.pixel_x += step
            self.direction = "right" if dx > 0 else "left"
        elif abs(dy) > 0:
            step = self.speed if dy > 0 else -self.speed
            if abs(step) > abs(dy): step = dy
            self.pixel_y += step
            self.direction = "down" if dy > 0 else "up"

        if abs(self.pixel_x - self.target_pixel_x) < 1 and abs(self.pixel_y - self.target_pixel_y) < 1:
            self.pixel_x = self.target_pixel_x
            self.pixel_y = self.target_pixel_y
            self.tile_x = tx
            self.tile_y = ty
            self.path_index += 1

    # --- Tách riêng Update Movement ---
    def update_movement(self):
        self.move_along_path()
        self.update_animation()

    # --- Update (Logic AI được chuyển sang GuardManager) ---
    def update(self, player=None):
        pass

    # --- Animation ---
    def update_animation(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim_time > self.anim_speed:
            self.frame_index = (self.frame_index + 1) % len(self.animations[self.direction])
            self.last_anim_time = now

    # --- Draw ---
    def draw(self, screen):
        # Vẽ vòng tròn detection
        radius_px = self.detect_radius * self.size
        surface = pygame.Surface((radius_px*2, radius_px*2), pygame.SRCALPHA)
        pygame.draw.circle(surface, (255,0,0,50), (radius_px, radius_px), radius_px)
        screen.blit(surface, (self.pixel_x - radius_px + self.size//2, self.pixel_y - radius_px + self.size//2))

        # Vẽ guard
        frame = self.animations[self.direction][self.frame_index]
        screen.blit(frame, (self.pixel_x, self.pixel_y))