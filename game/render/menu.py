import pygame
import os 
from game import config
from game.ai.pathfinding import PATHFINDING_ALGORITHMS

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        pygame.font.init()
        font_path = "game/assets/fonts/PressStart2P-Regular.ttf"
        try:
            self.font_large = pygame.font.Font(font_path, 42)
            self.font_button_title = pygame.font.Font(font_path, 18)
            self.font_button_main = pygame.font.Font(font_path, 16)
            self.font_medium = pygame.font.Font(font_path, 11)
            self.font_credit_title = pygame.font.Font(font_path, 10)
            self.font_credit_member = pygame.font.SysFont('Segoe UI', 16, bold=True)
        except pygame.error:
            # Font dự phòng
            print(f"Font not found at {font_path}. Falling back to Arial.")
            self.font_large = pygame.font.SysFont('Arial', 60, bold=True)
            self.font_button_title = pygame.font.SysFont('Arial', 28, bold=True)
            self.font_button_main = pygame.font.SysFont('Arial', 24, bold=True)
            self.font_medium = pygame.font.SysFont('Arial', 18)
            self.font_credit_title = pygame.font.SysFont('Arial', 14)
            self.font_credit_member = pygame.font.SysFont('Segoe UI', 16, bold=True)

        # --- DỮ LIỆU CHO MENU ---
        self.options = [
            config.DIFFICULTY_LEVELS, # <<< Sửa lại như thế này
            list(PATHFINDING_ALGORITHMS.keys()),
            config.MAP_THEMES
        ]

        self.option_titles = ["Difficulty", "Algorithm", "Map Theme"]
        
        # --- LƯU TRẠNG THÁI LỰA CHỌN ---
        self.current_difficulty = "NORMAL"
        self.current_algorithm = self.options[1][0]
        self.current_map_index = 0
        
        self.buttons = {}
        self.algo_buttons = {}
        self.map_buttons = {}

        self.background_scrollable = self._load_scrolling_background("game/assets/images/background-menu.png")
        self.bg_x = 0
        self.bg_scroll_speed = 0.3 

    def _load_scrolling_background(self, path):
        if not os.path.exists(path): return None
        original_bg = pygame.image.load(path).convert_alpha()
        scaled_bg = pygame.transform.scale(original_bg, (self.width, self.height))
        double_bg = pygame.Surface((self.width * 2, self.height), pygame.SRCALPHA)
        double_bg.blit(scaled_bg, (0, 0))
        double_bg.blit(scaled_bg, (self.width, 0))
        return double_bg

    def _update_and_draw_background(self):
        if self.background_scrollable:
            self.bg_x -= self.bg_scroll_speed
            if self.bg_x <= -self.width: self.bg_x = 0
            self.screen.blit(self.background_scrollable, (self.bg_x, 0))
        else:
            self.screen.fill((15, 25, 35))

    def _draw_pixel_button(self, rect, text, font, colors, is_selected, is_hovered):
        base_color = colors["base"]; light_edge_color = colors["light"]; dark_edge_color = colors["dark"]; text_color = colors["text"]
        effective_hover = is_hovered and not is_selected
        if is_selected or effective_hover:
            pygame.draw.rect(self.screen, base_color, rect)
            pygame.draw.line(self.screen, dark_edge_color, rect.topleft, rect.topright, 2); 
            pygame.draw.line(self.screen, dark_edge_color, rect.topleft, rect.bottomleft, 2)
            pygame.draw.line(self.screen, light_edge_color, rect.bottomleft, rect.bottomright, 2); 
            pygame.draw.line(self.screen, light_edge_color, rect.topright, rect.bottomright, 2)
            text_offset = 2 if is_selected else 0
        else:
            pygame.draw.rect(self.screen, (0,0,0), rect.move(0, 4)); 
            pygame.draw.rect(self.screen, base_color, rect)
            pygame.draw.line(self.screen, light_edge_color, rect.topleft, rect.topright, 2); 
            pygame.draw.line(self.screen, light_edge_color, rect.topleft, rect.bottomleft, 2)
            pygame.draw.line(self.screen, dark_edge_color, rect.bottomleft, rect.bottomright, 2); 
            pygame.draw.line(self.screen, dark_edge_color, rect.topright, rect.bottomright, 2)
            text_offset = 0
        text_surf = font.render(text, True, text_color); text_rect = text_surf.get_rect(center=rect.center); self.screen.blit(text_surf, text_rect.move(0, text_offset))

    def _draw_credit_banner(self):
        project_title = "Maze Escape Project"; members = ["Võ Tấn Tài - 23110150", "Phạm Công Trường - 23110163"]; margin = 15
        line_height = self.font_credit_member.get_height() + 5; 
        title_surf = self.font_credit_title.render(project_title, True, (220, 220, 220))
        title_rect = title_surf.get_rect(bottomright=(self.width - margin, self.height - margin - (len(members) * line_height))); 
        self.screen.blit(title_surf, title_rect)
        for i, member_text in enumerate(members):
            member_surf = self.font_credit_member.render(member_text, True, (255, 255, 255))
            y_position = self.height - margin - ((len(members) - 1 - i) * line_height)
            member_rect = member_surf.get_rect(bottomright=(self.width - margin, y_position)); self.screen.blit(member_surf, member_rect)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if self.buttons.get("PLAY") and self.buttons["PLAY"].collidepoint(mouse_pos): return "PLAY", self.current_difficulty, self.current_algorithm, self.current_map_index
            if self.buttons.get("EXIT") and self.buttons["EXIT"].collidepoint(mouse_pos): return "QUIT", None, None, None
            for level in config.DIFFICULTY_LEVELS:
                if self.buttons.get(level) and self.buttons[level].collidepoint(mouse_pos):
                    self.current_difficulty = level; return "DIFFICULTY_SELECTED", level, None, None
            for algo, rect in self.algo_buttons.items():
                if rect.collidepoint(mouse_pos): self.current_algorithm = algo; return "ALGO_SELECTED", None, algo, None
            for idx, rect in self.map_buttons.items():
                if rect.collidepoint(mouse_pos): self.current_map_index = idx; return "MAP_SELECTED", None, None, idx
        return None, None, None, None

    def draw(self):
        self._update_and_draw_background()
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA); 
        overlay.fill((0, 0, 0, 120)); self.screen.blit(overlay, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        center_x = self.width // 2

        # 1. Tiêu đề chính
        title_text = self.font_large.render("MAZE ESCAPE", True, (255, 100, 100))
        self.screen.blit(title_text, title_text.get_rect(center=(center_x, self.height * 0.15)))

        # 2. Nút Start và Quit
        start_quit_w, start_quit_h = 220, 70; gap = 40; total_width = start_quit_w * 2 + gap
        start_x = (self.width - total_width) / 2; y_pos = self.height * 0.3
        start_colors = {"base": (65, 165, 75), "light": (125, 205, 130), "dark": (35, 105, 45), "text": (255, 255, 255)}
        quit_colors = {"base": (195, 75, 75), "light": (225, 130, 130), "dark": (125, 40, 40), "text": (255, 255, 255)}
        
        start_rect = pygame.Rect(start_x, y_pos, start_quit_w, start_quit_h)
        self._draw_pixel_button(start_rect, "START", self.font_button_main, start_colors, False, start_rect.collidepoint(mouse_pos))
        self.buttons["PLAY"] = start_rect
        
        quit_rect = pygame.Rect(start_x + start_quit_w + gap, y_pos, start_quit_w, start_quit_h)
        self._draw_pixel_button(quit_rect, "QUIT", self.font_button_main, quit_colors, False, quit_rect.collidepoint(mouse_pos))
        self.buttons["EXIT"] = quit_rect

        # 3. Ba cột tùy chọn - Căn theo hàng ngang
        col_margin = 0.05
        col_width = (self.width * (1 - 2 * col_margin)) / 3
        col_xs = [self.width * col_margin + col_width / 2, center_x, self.width * (1 - col_margin) - col_width / 2]
        
        button_width = col_width * 0.9
        button_height = 45
        button_spacing = 55
        
        start_y_cols = self.height * 0.45
        title_offset_y = 40

        default_colors = {"base": (100, 100, 100), "light": (160, 160, 160), "dark": (60, 60, 60), "text": (220, 220, 220)}
        diff_colors = {"base": (65, 165, 75), "light": (125, 205, 130), "dark": (35, 105, 45), "text": (255, 255, 255)}
        algo_colors = {"base": (75, 85, 195), "light": (130, 140, 225), "dark": (40, 50, 125), "text": (255, 255, 255)}
        map_colors = {"base": (195, 75, 75), "light": (225, 130, 130), "dark": (125, 40, 40), "text": (255, 255, 255)}
        color_sets = [diff_colors, algo_colors, map_colors]

        # Vẽ tiêu đề cột
        for i, title in enumerate(self.option_titles):
            title_surf = self.font_button_title.render(title, True, (255, 255, 100))
            self.screen.blit(title_surf, title_surf.get_rect(center=(col_xs[i], start_y_cols)))

        # Vẽ các nút theo từng hàng
        max_rows = max(len(col) for col in self.options)
        for r in range(max_rows):
            y_pos = start_y_cols + title_offset_y + r * button_spacing
            
            # Cột 1: Difficulty
            if r < len(self.options[0]):
                level = self.options[0][r]
                rect = pygame.Rect(0, 0, button_width, button_height); rect.center = (col_xs[0], y_pos)
                is_selected = self.current_difficulty == level
                self._draw_pixel_button(rect, config.DIFFICULTY_SETTINGS[level]["DISPLAY_NAME"], self.font_medium, 
                                      color_sets[0] if is_selected else default_colors, is_selected, rect.collidepoint(mouse_pos))
                self.buttons[level] = rect
                
            # Cột 2: Algorithm
            if r < len(self.options[1]):
                algo = self.options[1][r]
                rect = pygame.Rect(0, 0, button_width, button_height); 
                rect.center = (col_xs[1], y_pos)
                is_selected = self.current_algorithm == algo
                self._draw_pixel_button(rect, algo, self.font_medium,
                                      color_sets[1] if is_selected else default_colors, is_selected, rect.collidepoint(mouse_pos))
                self.algo_buttons[algo] = rect
                
            # Cột 3: Map Theme
            if r < len(self.options[2]):
                theme_index = r
                rect = pygame.Rect(0, 0, button_width, button_height); rect.center = (col_xs[2], y_pos)
                is_selected = self.current_map_index == theme_index
                self._draw_pixel_button(rect, self.options[2][theme_index].replace("_", " ").capitalize(), self.font_medium,
                                      color_sets[2] if is_selected else default_colors, is_selected, rect.collidepoint(mouse_pos))
                self.map_buttons[theme_index] = rect
        
        self._draw_credit_banner()