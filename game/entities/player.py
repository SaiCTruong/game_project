# game/entities/player.py
# -*- coding: utf-8 -*-
import pygame
from game import config

class Player:
    def __init__(self, start_x, start_y, tiles):
        self.tiles = tiles
        self.x = start_x
        self.y = start_y
        self.size = config.CELL_SIZE

        # ⚡ Load sprite sheet (Giữ nguyên)
        sprite_sheet = pygame.image.load("game/assets/images/player.png").convert_alpha()
        sheet_w, sheet_h = sprite_sheet.get_size()
        frame_w = sheet_w // 4 
        frame_h = sheet_h // 4 

        # Cắt frame
        self.animations = {
            "down":  [sprite_sheet.subsurface(pygame.Rect(i*frame_w, 0*frame_h, frame_w, frame_h)) for i in range(4)],
            "left":  [sprite_sheet.subsurface(pygame.Rect(i*frame_w, 1*frame_h, frame_w, frame_h)) for i in range(4)],
            "right": [sprite_sheet.subsurface(pygame.Rect(i*frame_w, 2*frame_h, frame_w, frame_h)) for i in range(4)],
            "up":    [sprite_sheet.subsurface(pygame.Rect(i*frame_w, 3*frame_h, frame_w, frame_h)) for i in range(4)],
        }

        # Scale về kích thước ô
        for key in self.animations:
            self.animations[key] = [
                pygame.transform.scale(frame, (self.size, self.size))
                for frame in self.animations[key]
            ]

        # Trạng thái ban đầu
        self.direction = "down"
        self.frame_index = 0
        self.last_anim_time = 0
        self.anim_speed = 150 
        
        # FIX: Tinh chỉnh tham số cho trượt dài
        self.move_delay = 100 # Độ trễ (ms) giữa các lần di chuyển
        self.last_move_time = 0 
        
        self.is_moving = False

    def move(self, dx, dy, direction):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_y < len(self.tiles) and 0 <= new_x < len(self.tiles[0]):
            if self.tiles[new_y][new_x] == 0:
                self.x = new_x
                self.y = new_y
                self.direction = direction
                self.is_moving = True
                return True # Báo hiệu di chuyển thành công
            else:
                self.is_moving = False
                return False
        else:
            self.is_moving = False
            return False
        
    # --- LOGIC THẮNG/THUA giữ nguyên ---

    def get_tile_position(self):
        """Trả về tọa độ tile (x, y) hiện tại của Player."""
        return (self.x, self.y)

    def check_collision_with_guard(self, guard):
        """Kiểm tra xem Player có va chạm (ở cùng một tile) với Guard không."""
        return self.get_tile_position() == (guard.tile_x, guard.tile_y)
    
    # ----------------------------

    def handle_input(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()

        self.is_moving = False 

        # Cơ chế trượt dài: Chỉ cho phép di chuyển nếu đã qua move_delay
        if now - self.last_move_time > self.move_delay:
            moved = False
            
            # Thực hiện di chuyển theo thứ tự ưu tiên
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                moved = self.move(0, -1, "up")
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                moved = self.move(0, 1, "down")
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                moved = self.move(-1, 0, "left")
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                moved = self.move(1, 0, "right")

            # Chỉ reset thời gian nếu di chuyển thành công
            if moved:
                self.last_move_time = now

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