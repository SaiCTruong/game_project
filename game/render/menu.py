# game/render/menu.py
import pygame
import os 
from game import config
from game.ai.pathfinding import PATHFINDING_ALGORITHMS

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        pygame.font.init()
        # ... (khởi tạo font không đổi)
        self.font_large = pygame.font.SysFont('Arial', 60, bold=True)
        self.font_button = pygame.font.SysFont('Arial', 28, bold=True) 
        self.font_medium = pygame.font.SysFont('Arial', 25)
        self.font_small = pygame.font.SysFont('Arial', 22)

        self.current_difficulty = "NORMAL"
        self.algorithms = list(PATHFINDING_ALGORITHMS.keys())
        self.current_algorithm = self.algorithms[0]
        
        # <<< THÊM BIẾN CHO VIỆC CHỌN MAP >>>
        self.map_themes = config.MAP_THEMES
        self.current_map_index = 0
        
        self.buttons = {}
        self.algo_buttons = {}
        self.map_buttons = {} # Rects cho các nút chọn map

        # ... (load ảnh background và nút không đổi)
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
        # ... (hàm này không đổi)
        path = f"game/assets/images/{filename}"
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        return None

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            if self.buttons["PLAY"].collidepoint(mouse_pos):
                # <<< TRẢ VỀ CẢ MAP ĐÃ CHỌN >>>
                return "PLAY", self.current_difficulty, self.current_algorithm, self.current_map_index
            
            if self.buttons["EXIT"].collidepoint(mouse_pos):
                return "QUIT", None, None, None
            
            for level in config.DIFFICULTY_LEVELS:
                if self.buttons[level].collidepoint(mouse_pos):
                    self.current_difficulty = level
                    return "DIFFICULTY_SELECTED", level, None, None
            
            for algo, rect in self.algo_buttons.items():
                if rect.collidepoint(mouse_pos):
                    self.current_algorithm = algo
                    return "ALGO_SELECTED", None, algo, None

            # <<< XỬ LÝ CLICK CHỌN MAP >>>
            for idx, rect in self.map_buttons.items():
                if rect.collidepoint(mouse_pos):
                    self.current_map_index = idx
                    return "MAP_SELECTED", None, None, idx
                    
        return None, None, None, None

    def draw(self):
        # ... (vẽ background, title, nút play/exit không đổi)
        if self.background_menu: self.screen.blit(self.background_menu, (0, 0))
        else: self.screen.fill((0, 0, 0))
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA); overlay.fill((0,0,0,100)); self.screen.blit(overlay, (0,0))
        mouse_pos = pygame.mouse.get_pos(); center_x = self.width//2
        title_text = self.font_large.render("MAZE ESCAPE", True, (255,100,100)); self.screen.blit(title_text, title_text.get_rect(center=(center_x, self.height*0.1)))
        
        # <<< DỊCH CÁC NÚT PLAY/EXIT LÊN CAO HƠN MỘT CHÚT >>>
        play_rect = pygame.Rect(center_x-100, self.height*0.15, 200, 100)
        self.buttons["PLAY"] = play_rect
        img_play = self.button_green_hover if play_rect.collidepoint(mouse_pos) else self.button_green_normal
        if img_play: self.screen.blit(img_play, play_rect)

        exit_rect = pygame.Rect(center_x-100, self.height*0.15 + 105, 200, 100)
        self.buttons["EXIT"] = exit_rect
        img_exit = self.button_quit_hover if exit_rect.collidepoint(mouse_pos) else self.button_quit_normal
        if img_exit: self.screen.blit(img_exit, exit_rect)

        # Ba cột lựa chọn
        col_1_x = self.width * 0.20
        col_2_x = self.width * 0.50
        col_3_x = self.width * 0.80
        start_y = self.height * 0.5

        # Cột 1: Chọn độ khó
        diff_title = self.font_button.render("Difficulty", True, (255,255,100)); self.screen.blit(diff_title, diff_title.get_rect(center=(col_1_x, start_y-30)))
        for i, level in enumerate(config.DIFFICULTY_LEVELS):
            rect = pygame.Rect(col_1_x-125, start_y + i*55, 250, 50)
            # ... (logic vẽ nút độ khó không đổi)
            is_selected = self.current_difficulty == level; color = (50,200,50) if is_selected else (80,80,80)
            if rect.collidepoint(mouse_pos): color = (120,120,120)
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            if is_selected: pygame.draw.rect(self.screen, (255,255,0), rect, 3, 5)
            text_surf = self.font_medium.render(config.DIFFICULTY_SETTINGS[level]["DISPLAY_NAME"], True, (255,255,255)); self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))
            self.buttons[level] = rect

        # Cột 2: Chọn thuật toán
        algo_title = self.font_button.render("Algorithm", True, (255,255,100)); self.screen.blit(algo_title, algo_title.get_rect(center=(col_2_x, start_y-30)))
        for i, algo in enumerate(self.algorithms):
            rect = pygame.Rect(col_2_x-125, start_y + i*55, 250, 50)
            # ... (logic vẽ nút thuật toán không đổi)
            is_selected = self.current_algorithm == algo; color = (100,100,180) if is_selected else (80,80,80)
            if rect.collidepoint(mouse_pos): color = (120,120,120)
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            if is_selected: pygame.draw.rect(self.screen, (255,255,0), rect, 3, 5)
            text_surf = self.font_small.render(algo, True, (255,255,255)); self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))
            self.algo_buttons[algo] = rect

        # <<< Cột 3: Chọn Map >>>
        map_title = self.font_button.render("Map Theme", True, (255, 255, 100))
        self.screen.blit(map_title, map_title.get_rect(center=(col_3_x, start_y-30)))
        for i, theme in enumerate(self.map_themes):
            rect = pygame.Rect(col_3_x-125, start_y + i*55, 250, 50)
            is_selected = self.current_map_index == i
            color = (180, 100, 100) if is_selected else (80, 80, 80)
            if rect.collidepoint(mouse_pos): color = (120, 120, 120)
            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            if is_selected: pygame.draw.rect(self.screen, (255,255,0), rect, 3, 5)
            text_surf = self.font_medium.render(theme.capitalize(), True, (255,255,255))
            self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))
            self.map_buttons[i] = rect