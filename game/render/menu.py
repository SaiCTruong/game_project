# game/render/menu.py
import pygame
import os 
from game import config
# <<< IMPORT THƯ VIỆN THUẬT TOÁN MỚI >>>
from game.ai.pathfinding import PATHFINDING_ALGORITHMS

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        pygame.font.init()
        try:
            self.font_large = pygame.font.SysFont('Arial', 60, bold=True)
            self.font_button = pygame.font.SysFont('Arial', 28, bold=True) 
            self.font_medium = pygame.font.SysFont('Arial', 25)
            self.font_algo = pygame.font.SysFont('Arial', 22) # Font cho thuật toán
        except Exception:
            self.font_large = pygame.font.Font(None, 60)
            self.font_button = pygame.font.Font(None, 28)
            self.font_medium = pygame.font.Font(None, 25)
            self.font_algo = pygame.font.Font(None, 22)

        self.current_difficulty = "NORMAL"

        # <<< THÊM BIẾN CHO THUẬT TOÁN >>>
        self.algorithms = list(PATHFINDING_ALGORITHMS.keys())
        self.current_algorithm = self.algorithms[0]
        
        # Sẽ setup button trong hàm draw để linh hoạt hơn
        self.buttons = {}
        self.algo_buttons = {}

        # ... (Phần load background và ảnh nút giữ nguyên)
        bg_path = "game/assets/images/background-menu.png"
        self.background_menu = None
        if os.path.exists(bg_path):
            original_bg = pygame.image.load(bg_path).convert_alpha()
            self.background_menu = pygame.transform.scale(original_bg, (self.width, self.height))
        
        self.button_size_play = (200, 150)
        self.button_size_exit = (200, 150)
        self.button_green_normal = self._load_button_image("button_green_hover.png", self.button_size_play)
        self.button_green_hover = self._load_button_image("BlueStandartStart.png", self.button_size_play)
        self.button_quit_normal = self._load_button_image("RedStandartQuit.png", self.button_size_exit)
        self.button_quit_hover = self._load_button_image("BlueStandartQuit.png", self.button_size_exit)

    def _load_button_image(self, filename, size):
        path = f"game/assets/images/{filename}"
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        return None

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            if self.buttons["PLAY"].collidepoint(mouse_pos):
                # <<< TRẢ VỀ CẢ THUẬT TOÁN ĐÃ CHỌN >>>
                return "PLAY", self.current_difficulty, self.current_algorithm
            
            if self.buttons["EXIT"].collidepoint(mouse_pos):
                return "QUIT", None, None
            
            for level in config.DIFFICULTY_LEVELS:
                if self.buttons[level].collidepoint(mouse_pos):
                    self.current_difficulty = level
                    return "DIFFICULTY_SELECTED", level, None
            
            # <<< XỬ LÝ CLICK CHỌN THUẬT TOÁN >>>
            for algo, rect in self.algo_buttons.items():
                if rect.collidepoint(mouse_pos):
                    self.current_algorithm = algo
                    return "ALGO_SELECTED", None, algo
                    
        return None, None, None

    def draw(self):
        # Vẽ Background
        if self.background_menu:
            self.screen.blit(self.background_menu, (0, 0))
        else:
            self.screen.fill((0, 0, 0))
        
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100)); self.screen.blit(overlay, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        center_x = self.width // 2

        # Vẽ Tiêu đề
        title_text = self.font_large.render("MAZE ESCAPE", True, (255, 100, 100))
        self.screen.blit(title_text, title_text.get_rect(center=(center_x, self.height * 0.1)))

        # Nút PLAY và EXIT
        play_rect = pygame.Rect(center_x - 100, self.height * 0.2, 200, 150)
        self.buttons["PLAY"] = play_rect
        img_play = self.button_green_hover if play_rect.collidepoint(mouse_pos) else self.button_green_normal
        if img_play: self.screen.blit(img_play, play_rect)

        exit_rect = pygame.Rect(center_x - 100, self.height * 0.2 + 155, 200, 150)
        self.buttons["EXIT"] = exit_rect
        img_exit = self.button_quit_hover if exit_rect.collidepoint(mouse_pos) else self.button_quit_normal
        if img_exit: self.screen.blit(img_exit, exit_rect)

        # Cột bên trái: Chọn độ khó
        diff_col_x = self.width * 0.25
        diff_title = self.font_button.render("Difficulty", True, (255, 255, 100))
        self.screen.blit(diff_title, diff_title.get_rect(center=(diff_col_x, self.height * 0.6)))
        
        start_y_diff = self.height * 0.6 + 50
        for i, level in enumerate(config.DIFFICULTY_LEVELS):
            rect = pygame.Rect(diff_col_x - 150, start_y_diff + i * 60, 300, 50)
            is_selected = self.current_difficulty == level
            color = (50, 200, 50) if is_selected else (80, 80, 80)
            if rect.collidepoint(mouse_pos): color = (120, 120, 120)
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            if is_selected: pygame.draw.rect(self.screen, (255,255,0), rect, 3, 5)
            text_surf = self.font_medium.render(config.DIFFICULTY_SETTINGS[level]["DISPLAY_NAME"], True, (255,255,255))
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))
            self.buttons[level] = rect

        # <<< Cột bên phải: Chọn thuật toán >>>
        algo_col_x = self.width * 0.75
        algo_title = self.font_button.render("Player Algorithm", True, (255, 255, 100))
        self.screen.blit(algo_title, algo_title.get_rect(center=(algo_col_x, self.height * 0.6)))
        
        start_y_algo = self.height * 0.6 + 50
        for i, algo in enumerate(self.algorithms):
            rect = pygame.Rect(algo_col_x - 150, start_y_algo + i * 55, 300, 50)
            is_selected = self.current_algorithm == algo
            color = (100, 100, 180) if is_selected else (80, 80, 80)
            if rect.collidepoint(mouse_pos): color = (120, 120, 120)
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            if is_selected: pygame.draw.rect(self.screen, (255,255,0), rect, 3, 5)
            text_surf = self.font_algo.render(algo, True, (255,255,255))
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))
            self.algo_buttons[algo] = rect