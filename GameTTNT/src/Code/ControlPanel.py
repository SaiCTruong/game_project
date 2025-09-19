import pygame
import sys

class ControlPanel:
    def __init__(self, width=300, height=500):
        # Kích thước panel
        self.width = width
        self.height = height

        # Màu sắc
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.GRAY = (200, 200, 200)
        self.BLUE = (0, 102, 204)

        # Font
        self.font = pygame.font.SysFont(None, 28)

        # Vị trí panel
        self.rect = pygame.Rect(700, 0, self.width, self.height)

        # Nút
        self.buttons = {
            "Auto Play": pygame.Rect(750, 50, 200, 50),
            "AI Play": pygame.Rect(750, 150, 200, 50),
            "Reset": pygame.Rect(750, 250, 200, 50),
            "Exit": pygame.Rect(750, 350, 200, 50)
        }

        # Trạng thái phím di chuyển
        self.keys_pressed = {
            pygame.K_UP: False,
            pygame.K_DOWN: False,
            pygame.K_LEFT: False,
            pygame.K_RIGHT: False,
        }

    # ============ VẼ NÚT ============
    def draw_button(self, screen, rect, text, color_bg, color_text=None):
        if color_text is None:
            color_text = self.WHITE
        pygame.draw.rect(screen, color_bg, rect)
        text_render = self.font.render(text, True, color_text)
        text_rect = text_render.get_rect(center=rect.center)
        screen.blit(text_render, text_rect)

    # ============ HIỂN THỊ PANEL ============
    def display(self, screen):
        # Vẽ nền panel
        pygame.draw.rect(screen, self.GRAY, self.rect)

        # Vẽ các nút
        self.draw_button(screen, self.buttons["Auto Play"], "Auto Play", self.BLUE)
        self.draw_button(screen, self.buttons["AI Play"], "AI Play", self.BLUE)
        self.draw_button(screen, self.buttons["Reset"], "Reset", self.BLUE)
        self.draw_button(screen, self.buttons["Exit"], "Exit", self.BLUE)

    # ============ XỬ LÝ SỰ KIỆN ============
    def handle_event(self, event, maze, ai):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key in self.keys_pressed:
                self.keys_pressed[event.key] = True

        elif event.type == pygame.KEYUP:
            if event.key in self.keys_pressed:
                self.keys_pressed[event.key] = False

        return maze, ai, None

    # ============ XỬ LÝ DI CHUYỂN LIÊN TỤC ============
    def handle_continuous_movement(self, maze, ai):
        if self.keys_pressed[pygame.K_UP]:
            ai.move_towards(ai.x, ai.y - 1)
        if self.keys_pressed[pygame.K_DOWN]:
            ai.move_towards(ai.x, ai.y + 1)
        if self.keys_pressed[pygame.K_LEFT]:
            ai.move_towards(ai.x - 1, ai.y)
        if self.keys_pressed[pygame.K_RIGHT]:
            ai.move_towards(ai.x + 1, ai.y)

        return maze, ai
