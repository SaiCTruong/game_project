# game/render/in_game_menu.py
import pygame
from game import config

class InGameMenu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        pygame.font.init()
        try:
            self.font_button = pygame.font.SysFont('Arial', 30, bold=True)
            self.font_title = pygame.font.SysFont('Arial', 45, bold=True)
        except:
            self.font_button = pygame.font.Font(None, 30)
            self.font_title = pygame.font.Font(None, 45)
            
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_RED = (200, 50, 50)
        self.COLOR_GREEN = (50, 200, 50)
        
        # --- Kích thước và vị trí Menu Modal ---
        MENU_W = 400
        MENU_H = 300
        self.menu_rect = pygame.Rect(
            (self.width // 2) - (MENU_W // 2), 
            (self.height // 2) - (MENU_H // 2), 
            MENU_W, 
            MENU_H
        )
        
        # Tạo vị trí cho các nút
        self.buttons = self._setup_buttons(MENU_W, MENU_H)

    def _setup_buttons(self, menu_w, menu_h):
        """Khởi tạo các nút bấm trong menu modal."""
        # Vị trí tâm x của các nút (tương đối với tâm màn hình)
        center_x_abs = self.width // 2
        
        button_height = 50
        spacing = 30
        start_y = self.menu_rect.top + 100 # Bắt đầu từ 100px so với đỉnh menu
        BUTTON_WIDTH = 250
        
        buttons = {
            "RESUME": pygame.Rect(center_x_abs - (BUTTON_WIDTH // 2), start_y, BUTTON_WIDTH, button_height),
            "TO_MENU": pygame.Rect(center_x_abs - (BUTTON_WIDTH // 2), start_y + button_height + spacing, BUTTON_WIDTH, button_height),
        }
        return buttons

    def handle_input(self, event):
        """Xử lý sự kiện click chuột."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            if self.buttons["RESUME"].collidepoint(mouse_pos):
                return "RESUME"
            
            elif self.buttons["TO_MENU"].collidepoint(mouse_pos):
                return "BACK_TO_MENU"
                
        return None

    def draw(self):
        """Vẽ menu modal và các nút."""
        
        # 1. Hiệu ứng làm mờ nền (Overlay)
        # Tạo một Surface trong suốt to bằng màn hình
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # Màu đen mờ (làm mờ toàn bộ game)
        self.screen.blit(overlay, (0, 0))

        # 2. Vẽ nền Menu Modal chính
        pygame.draw.rect(self.screen, (50, 50, 50), self.menu_rect, border_radius=10) # Nền xám
        pygame.draw.rect(self.screen, self.COLOR_WHITE, self.menu_rect, 5, border_radius=10) # Viền

        # 3. Vẽ Tiêu đề
        title_text = self.font_title.render("GAME PAUSED", True, self.COLOR_WHITE)
        title_rect = title_text.get_rect(center=(self.width // 2, self.menu_rect.top + 40)) 
        self.screen.blit(title_text, title_rect)

        # 4. Vẽ các Nút bấm
        
        # Nút RESUME
        rect_r = self.buttons["RESUME"]
        pygame.draw.rect(self.screen, self.COLOR_GREEN, rect_r, border_radius=5)
        text_r = self.font_button.render("RESUME (ESC)", True, self.COLOR_BLACK)
        self.screen.blit(text_r, text_r.get_rect(center=rect_r.center)) 

        # Nút BACK TO MENU
        rect_m = self.buttons["TO_MENU"]
        pygame.draw.rect(self.screen, self.COLOR_RED, rect_m, border_radius=5)
        text_m = self.font_button.render("BACK TO MENU", True, self.COLOR_WHITE)
        self.screen.blit(text_m, text_m.get_rect(center=rect_m.center))