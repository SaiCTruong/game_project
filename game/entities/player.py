# -*- coding: utf-8 -*-
import pygame
from game import config

class Player:
    def __init__(self, start_x, start_y, tiles):
        self.tiles = tiles
        self.x = start_x
        self.y = start_y
        self.size = config.CELL_SIZE

        # ⚡ Load sprite sheet
        sprite_sheet = pygame.image.load("game/assets/images/player.png").convert_alpha()
        sheet_w, sheet_h = sprite_sheet.get_size()
        frame_w = sheet_w // 4   # 4 cột
        frame_h = sheet_h // 4   # 4 hàng

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
        self.anim_speed = 150  # ms/frame

        # Cooldown di chuyển
        self.move_cooldown = 150
        self.last_move_time = 0

        # Trạng thái di chuyển
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
            else:
                self.is_moving = False
        else:
            self.is_moving = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        now = pygame.time.get_ticks()

        self.is_moving = False  # reset, chỉ true nếu thực sự di chuyển

        if now - self.last_move_time > self.move_cooldown:
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.move(0, -1, "up")
                self.last_move_time = now
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.move(0, 1, "down")
                self.last_move_time = now
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.move(-1, 0, "left")
                self.last_move_time = now
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.move(1, 0, "right")
                self.last_move_time = now

    def update_animation(self):
        if self.is_moving:  # chỉ animate khi di chuyển
            now = pygame.time.get_ticks()
            if now - self.last_anim_time > self.anim_speed:
                self.frame_index = (self.frame_index + 1) % len(self.animations[self.direction])
                self.last_anim_time = now
        else:
            self.frame_index = 0  # đứng yên thì về frame đầu


    def draw(self, screen):
        self.update_animation()
        frame = self.animations[self.direction][self.frame_index]
        screen.blit(frame, (self.x * self.size, self.y * self.size))
