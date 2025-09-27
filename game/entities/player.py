# game/entities/player.py
# -*- coding: utf-8 -*-
import pygame
import math
import random
from game import config
from game.ai.astar import astar_path 

# Hằng số cho logic Né tránh
EVASION_RADIUS = 7 
EVASION_BUFFER = 10 

class Player:
    def __init__(self, start_x, start_y, tiles):
        self.tiles = tiles
        self.x = start_x
        self.y = start_y
        self.size = config.CELL_SIZE

        # --- Load Sprite & Animation (Không thay đổi) ---
        sprite_sheet = pygame.image.load("game/assets/images/player.png").convert_alpha()
        sheet_w, sheet_h = sprite_sheet.get_size()
        frame_w = sheet_w // 4 
        frame_h = sheet_h // 4 

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

        # --- Thuộc tính AI ---
        self.ai_mode = False        
        self.ai_path = []          
        self.ai_path_index = 0
        self.is_evading = False 

    def move(self, dx, dy, direction):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_y < len(self.tiles) and 0 <= new_x < len(self.tiles[0]):
            if self.tiles[new_y][new_x] == 0:
                self.x = new_x
                self.y = new_y
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
        player_hitbox = player_rect.inflate(-player_rect.width * 0.2, -player_rect.height * 0.2)
        guard_hitbox = guard_rect.inflate(-guard_rect.width * 0.2, -guard_rect.height * 0.2)
        return player_hitbox.colliderect(guard_hitbox)
    
    def check_if_path_is_unsafe(self, guards):
        if not self.ai_path or self.ai_path_index >= len(self.ai_path):
            return False
        next_tile_x, next_tile_y = self.ai_path[self.ai_path_index]
        for guard in guards:
            dist = abs(next_tile_x - guard.tile_x) + abs(next_tile_y - guard.tile_y)
            if dist <= 1:
                return True
        return False

    def handle_ai_move(self, tiles, exit_tile, guards):
        AI_MOVE_DELAY = 80 
        now = pygame.time.get_ticks()
        
        if now - self.last_move_time < AI_MOVE_DELAY:
            return

        current_tile = self.get_tile_position()
        ai_goal = exit_tile
        
        # --- 1. XÁC ĐỊNH TRẠNG THÁI NÉ TRÁNH ---
        nearest_guard_dist = float('inf')
        if guards:
            nearest_guard = min(guards, key=lambda g: abs(current_tile[0] - g.tile_x) + abs(current_tile[1] - g.tile_y))
            nearest_guard_dist = abs(current_tile[0] - nearest_guard.tile_x) + abs(current_tile[1] - nearest_guard.tile_y)
            
            if nearest_guard_dist <= EVASION_RADIUS:
                if not self.is_evading:
                    self.ai_path = []
                self.is_evading = True
                gx, gy = nearest_guard.tile_x, nearest_guard.tile_y
                escape_vector_x, escape_vector_y = current_tile[0] - gx, current_tile[1] - gy
                magnitude = math.sqrt(escape_vector_x**2 + escape_vector_y**2) or 1
                TARGET_DISTANCE = 25 
                target_x = current_tile[0] + int(TARGET_DISTANCE * (escape_vector_x / magnitude))
                target_y = current_tile[1] + int(TARGET_DISTANCE * (escape_vector_y / magnitude))
                target_x = max(1, min(len(tiles[0]) - 2, target_x))
                target_y = max(1, min(len(tiles) - 2, target_y))
                ai_goal = (target_x, target_y)
            elif self.is_evading and nearest_guard_dist > EVASION_RADIUS + 5:
                self.is_evading = False
                self.ai_path = [] 
        
        if not self.is_evading:
            ai_goal = exit_tile

        # --- 2. TÍNH TOÁN LẠI ĐƯỜNG ĐI ---
        is_path_empty = not self.ai_path or self.ai_path_index >= len(self.ai_path)
        is_current_path_unsafe = self.check_if_path_is_unsafe(guards) 
        
        if is_path_empty or is_current_path_unsafe:
            self.ai_path_index = 0
            new_path = None
            
            if self.is_evading:
                # Khi né tránh, cứ tìm đường nhanh nhất đến điểm an toàn
                new_path = astar_path(tiles, current_tile, ai_goal) 
            else:
                # Khi bình thường, CHỈ tìm đường đi an toàn
                new_path = astar_path(tiles, current_tile, ai_goal, guards=guards) 

            # Xử lý kết quả tìm đường
            if new_path and len(new_path) > 1:
                self.ai_path = new_path
                self.ai_path_index = 1
            else:
                # Nếu không tìm thấy đường (an toàn), hãy đứng im và chờ
                self.is_moving = False
                self.ai_path = [] # Xóa đường đi cũ để buộc tìm lại ở lần sau
                return 

        # --- 3. THỰC HIỆN DI CHUYỂN ---
        if self.ai_path and self.ai_path_index < len(self.ai_path):
            next_tile_x, next_tile_y = self.ai_path[self.ai_path_index]
            dx = next_tile_x - current_tile[0]
            dy = next_tile_y - current_tile[1]

            if abs(dx) > 1 or abs(dy) > 1:
                self.ai_path = []
                self.is_moving = False
                return

            direction = "up" if dy == -1 else "down" if dy == 1 else "left" if dx == -1 else "right"
            if self.move(dx, dy, direction):
                self.ai_path_index += 1
                self.last_move_time = now
        else:
             self.is_moving = False

    def handle_input(self):
        if self.ai_mode: return 
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()
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
        else:
            self.frame_index = 0 

    def draw(self, screen):
        self.update_animation()
        frame = self.animations[self.direction][self.frame_index]
        screen.blit(frame, (self.x * self.size, self.y * self.size))