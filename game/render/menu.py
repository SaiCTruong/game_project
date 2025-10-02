import pygame
import os 
from game import config
from game.ai.pathfinding import PATHFINDING_ALGORITHMS

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        pygame.font.init()
        # <<< THAY ĐỔI 1: Tải font pixel chuyên dụng >>>
        font_path = "game/assets/fonts/PressStart2P-Regular.ttf"
        try:
            self.font_large = pygame.font.Font(font_path, 40)
            self.font_button = pygame.font.Font(font_path, 16)
            self.font_medium = pygame.font.Font(font_path, 11) # Font nhỏ gọn cho các nút
            self.font_credit = pygame.font.Font(font_path, 8)
            self.font_credit_member = pygame.font.SysFont('Segoe UI', 16, bold=True)

        except pygame.error:
            print(f"Font not found at {font_path}. Falling back to Arial.")
            # Font dự phòng nếu không tìm thấy file
            self.font_large = pygame.font.SysFont('Arial', 60, bold=True)
            self.font_button = pygame.font.SysFont('Arial', 28, bold=True)
            self.font_medium = pygame.font.SysFont('Arial', 18)
            self.font_credit = pygame.font.SysFont('Arial', 12)
            self.font_credit_member = pygame.font.SysFont('Arial', 14)

        self.current_difficulty = "NORMAL"
        self.algorithms = list(PATHFINDING_ALGORITHMS.keys())
        self.current_algorithm = self.algorithms[0]
        
        self.map_themes = config.MAP_THEMES
        self.current_map_index = 0
        
        self.buttons = {}
        self.algo_buttons = {}
        self.map_buttons = {}

        self.background_scrollable = self._load_scrolling_background("game/assets/images/background-menu.png")
        self.bg_x = 0
        self.bg_scroll_speed = 0.3 
        
        self.button_size_play = (200, 150)
        self.button_size_exit = (200, 150)
        self.button_green_normal = self._load_button_image("button_green_hover.png", self.button_size_play)
        self.button_green_hover = self._load_button_image("BlueStandartStart.png", self.button_size_play)
        self.button_quit_normal = self._load_button_image("RedStandartQuit.png", self.button_size_exit)
        self.button_quit_hover = self._load_button_image("BlueStandartQuit.png", self.button_size_exit)

    def _load_button_image(self, filename, size):
        # (Hàm này giữ nguyên)
        path = f"game/assets/images/{filename}"
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        return None

    def _load_scrolling_background(self, path):
        # (Hàm này giữ nguyên)
        if not os.path.exists(path): return None
        original_bg = pygame.image.load(path).convert_alpha()
        scaled_bg = pygame.transform.scale(original_bg, (self.width, self.height))
        double_bg = pygame.Surface((self.width * 2, self.height), pygame.SRCALPHA)
        double_bg.blit(scaled_bg, (0, 0))
        double_bg.blit(scaled_bg, (self.width, 0))
        return double_bg

    def _update_and_draw_background(self):
        # (Hàm này giữ nguyên)
        if self.background_scrollable:
            self.bg_x -= self.bg_scroll_speed
            if self.bg_x <= -self.width: self.bg_x = 0
            self.screen.blit(self.background_scrollable, (self.bg_x, 0))
        else:
            self.screen.fill((15, 25, 35))

    # <<< THAY ĐỔI 2: Hàm vẽ nút theo phong cách Pixel Art 3D >>>
    def _draw_pixel_button(self, rect, text, font, colors, is_selected, is_hovered):
        base_color = colors["base"]
        light_edge_color = colors["light"]
        dark_edge_color = colors["dark"]
        text_color = colors["text"]
        
        # Hiệu ứng khi được chọn hoặc di chuột vào -> nút bị "nhấn xuống"
        if is_selected or is_hovered:
            # Đảo màu viền sáng/tối và không có bóng
            pygame.draw.rect(self.screen, base_color, rect)
            pygame.draw.line(self.screen, dark_edge_color, rect.topleft, rect.topright, 2)
            pygame.draw.line(self.screen, dark_edge_color, rect.topleft, rect.bottomleft, 2)
            pygame.draw.line(self.screen, light_edge_color, rect.bottomleft, rect.bottomright, 2)
            pygame.draw.line(self.screen, light_edge_color, rect.topright, rect.bottomright, 2)
            text_offset = 2 # Chữ dịch xuống khi bị nhấn
        else:
            # Vẽ bóng đổ
            pygame.draw.rect(self.screen, (0,0,0), rect.move(0, 4))
            # Vẽ thân nút
            pygame.draw.rect(self.screen, base_color, rect)
            # Vẽ viền sáng/tối tạo cảm giác nổi
            pygame.draw.line(self.screen, light_edge_color, rect.topleft, rect.topright, 2)
            pygame.draw.line(self.screen, light_edge_color, rect.topleft, rect.bottomleft, 2)
            pygame.draw.line(self.screen, dark_edge_color, rect.bottomleft, rect.bottomright, 2)
            pygame.draw.line(self.screen, dark_edge_color, rect.topright, rect.bottomright, 2)
            text_offset = 0

        # Vẽ chữ
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect.move(0, text_offset))

       #hàm vẽ banner 
    def _draw_credit_banner(self):
        """Vẽ banner thông tin của 2 người làm ở góc dưới bên phải."""
        project_title = "Maze Escape Project"
        members = [
            "Võ Tấn Tài - 23110150",
            "Phạm Công Trường - 23110163"
        ]

        margin = 15
        line_height = self.font_credit_member.get_height() + 5

        # <<< THAY ĐỔI 1: Vẽ tiêu đề dự án bằng font pixel lớn hơn cho rõ >>>
        title_surf = self.font_medium.render(project_title, True, (240, 240, 240))
        title_rect = title_surf.get_rect(bottomright=(self.width - margin, self.height - margin - (len(members) * line_height)))
        self.screen.blit(title_surf, title_rect)

        # Vẽ tên từng thành viên
        for i, member_text in enumerate(members):
            # <<< THAY ĐỔI 2: Dùng màu trắng sáng hơn cho tên >>>
            member_surf = self.font_credit_member.render(member_text, True, (255, 255, 255))
            
            y_position = self.height - margin - ((len(members) - 1 - i) * line_height)
            member_rect = member_surf.get_rect(bottomright=(self.width - margin, y_position))
            
            self.screen.blit(member_surf, member_rect)

    def handle_input(self, event):
        # (Hàm này giữ nguyên)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if self.buttons["PLAY"].collidepoint(mouse_pos): return "PLAY", self.current_difficulty, self.current_algorithm, self.current_map_index
            if self.buttons["EXIT"].collidepoint(mouse_pos): return "QUIT", None, None, None
            for level in config.DIFFICULTY_LEVELS:
                if self.buttons[level].collidepoint(mouse_pos):
                    self.current_difficulty = level
                    return "DIFFICULTY_SELECTED", level, None, None
            for algo, rect in self.algo_buttons.items():
                if rect.collidepoint(mouse_pos):
                    self.current_algorithm = algo
                    return "ALGO_SELECTED", None, algo, None
            for idx, rect in self.map_buttons.items():
                if rect.collidepoint(mouse_pos):
                    self.current_map_index = idx
                    return "MAP_SELECTED", None, None, idx
        return None, None, None, None

    def draw(self):
        self._update_and_draw_background()
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        self.screen.blit(overlay, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()
        center_x = self.width // 2

        title_text = self.font_large.render("MAZE ESCAPE", True, (255, 100, 100))
        self.screen.blit(title_text, title_text.get_rect(center=(center_x, self.height * 0.12)))
        
        # --- Code mới cho nút Play/Exit nằm ngang ---
        button_w, button_h = self.button_size_play # Lấy kích thước đã định nghĩa ở trên
        gap = 20  # Khoảng cách giữa 2 nút
        total_width = button_w * 2 + gap

        # Tính toán vị trí bắt đầu để cả cụm nút được căn giữa
        start_x = (self.width - total_width) / 2
        y_pos = self.height * 0.22 # Đẩy nút lên cao một chút

        # Vẽ nút PLAY (START)
        play_rect = pygame.Rect(start_x, y_pos, button_w, button_h)
        self.buttons["PLAY"] = play_rect
        img_play = self.button_green_hover if play_rect.collidepoint(mouse_pos) else self.button_green_normal
        if img_play: self.screen.blit(img_play, play_rect.topleft)

        # Vẽ nút EXIT (QUIT)
        exit_rect = pygame.Rect(start_x + button_w + gap, y_pos, button_w, button_h)
        self.buttons["EXIT"] = exit_rect
        img_exit = self.button_quit_hover if exit_rect.collidepoint(mouse_pos) else self.button_quit_normal
        if img_exit: self.screen.blit(img_exit, exit_rect.topleft)

        col_margin, col_width = 0.08, (self.width * (1 - 2 * 0.08)) / 3
        col_1_x = self.width * col_margin + col_width / 2
        col_2_x = col_1_x + col_width
        col_3_x = col_2_x + col_width

        button_width, button_height = col_width * 0.9, 50
        start_y_cols, button_spacing, title_offset_y = self.height * 0.55, 65, 50

        # <<< THAY ĐỔI 3: Bộ màu mới cho các nút pixel >>>
        difficulty_colors = {"base": (65, 165, 75), "light": (125, 205, 130), "dark": (35, 105, 45), "text": (255, 255, 255)}
        algorithm_colors = {"base": (75, 85, 195), "light": (130, 140, 225), "dark": (40, 50, 125), "text": (255, 255, 255)}
        map_colors = {"base": (195, 75, 75), "light": (225, 130, 130), "dark": (125, 40, 40), "text": (255, 255, 255)}
        default_colors = {"base": (100, 100, 100), "light": (160, 160, 160), "dark": (60, 60, 60), "text": (220, 220, 220)}

        # Cột 1: Difficulty
        diff_title = self.font_button.render("Difficulty", True, (255, 255, 100))
        self.screen.blit(diff_title, diff_title.get_rect(center=(col_1_x, start_y_cols - title_offset_y)))
        for i, level in enumerate(config.DIFFICULTY_LEVELS):
            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.center = (col_1_x, start_y_cols + i * button_spacing)
            self._draw_pixel_button(rect, config.DIFFICULTY_SETTINGS[level]["DISPLAY_NAME"], self.font_medium, 
                                  difficulty_colors if self.current_difficulty == level else default_colors, 
                                  self.current_difficulty == level, rect.collidepoint(mouse_pos))
            self.buttons[level] = rect

        # Cột 2: Algorithm
        algo_title = self.font_button.render("Algorithm", True, (255, 255, 100))
        self.screen.blit(algo_title, algo_title.get_rect(center=(col_2_x, start_y_cols - title_offset_y)))
        for i, algo in enumerate(self.algorithms):
            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.center = (col_2_x, start_y_cols + i * button_spacing)
            self._draw_pixel_button(rect, algo, self.font_medium,
                                  algorithm_colors if self.current_algorithm == algo else default_colors,
                                  self.current_algorithm == algo, rect.collidepoint(mouse_pos))
            self.algo_buttons[algo] = rect

        # Cột 3: Map Theme
        map_title = self.font_button.render("Map Theme", True, (255, 255, 100))
        self.screen.blit(map_title, map_title.get_rect(center=(col_3_x, start_y_cols - title_offset_y)))
        for i, theme in enumerate(self.map_themes):
            rect = pygame.Rect(0, 0, button_width, button_height)
            rect.center = (col_3_x, start_y_cols + i * button_spacing)
            self._draw_pixel_button(rect, theme.replace("_", " ").capitalize(), self.font_medium,
                                  map_colors if self.current_map_index == i else default_colors,
                                  self.current_map_index == i, rect.collidepoint(mouse_pos))
            self.map_buttons[i] = rect
        
        self._draw_credit_banner()