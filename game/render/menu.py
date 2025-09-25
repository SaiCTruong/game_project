# game/render/menu.py
import pygame
import os 
from game import config

class Menu:
    def __init__(self, screen):
        self.screen = screen
        self.width, self.height = screen.get_size()
        
        # --- Font Initialization ---
        pygame.font.init()
        try:
            self.font_large = pygame.font.SysFont('Arial', 60, bold=True)
            self.font_button = pygame.font.SysFont('Arial', 28, bold=True) 
            self.font_medium = pygame.font.SysFont('Arial', 25)
        except:
            self.font_large = pygame.font.Font(None, 60)
            self.font_button = pygame.font.Font(None, 28)
            self.font_medium = pygame.font.Font(None, 25)
            
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_BLACK = (0, 0, 0)
        self.COLOR_RED_TEXT = (255, 100, 100) 
        self.COLOR_GREEN_BTN = (50, 200, 50) # Màu xanh cũ cho nút vẽ
        self.COLOR_RED_BTN = (200, 50, 50)   # Màu đỏ cũ cho nút vẽ

        self.current_difficulty = "NORMAL"
        self.buttons = self._setup_buttons()

        # --- Tải Background Menu ---
        bg_path = "game/assets/images/background-menu.png"
        self.background_menu = None
        if os.path.exists(bg_path):
            original_bg = pygame.image.load(bg_path).convert_alpha()
            scale_factor = self.height / original_bg.get_height()
            self.background_menu = pygame.transform.scale(
                original_bg, 
                (int(original_bg.get_width() * scale_factor), self.height)
            )
            self.bg_width = self.background_menu.get_width()
        else:
            print("Cảnh báo: Không tìm thấy background_menu.png. Dùng nền đen.")
            
        self.bg_x = 0  
        self.scroll_speed = 0.5  

        # --- Tải Hình ảnh Nút Bấm (CHỈ CẦN DÙNG CHO START) ---
        button_size = (self.buttons["PLAY"].width, self.buttons["PLAY"].height) 
        
        # Nút Xanh (PLAY)
        self.button_green_normal = self._load_button_image("button_green_normal.png", button_size)
        self.button_green_hover = self._load_button_image("button_green_hover.png", button_size) or self.button_green_normal
        
        # Tạo Surface thay thế (Fallback) cho START nếu ảnh không có
        if self.button_green_normal == None:
             self.button_green_normal = pygame.Surface(button_size, pygame.SRCALPHA)
             self.button_green_normal.fill(self.COLOR_GREEN_BTN)
        if self.button_green_hover == None:
             self.button_green_hover = self.button_green_normal
        # ----------------------------------------------

    def _load_button_image(self, filename, size):
        """Hàm trợ giúp để tải và scale hình ảnh nút."""
        path = f"game/assets/images/{filename}"
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        else:
            # Chỉ trả về None, logic fallback sẽ xử lý việc tạo Surface thay thế ở __init__
            return None

    def _setup_buttons(self):
        """Khởi tạo vị trí các nút PLAY, EXIT và 4 nút Độ Khó (Kích thước lớn hơn)."""
        center_x = self.width // 2
        start_y = self.height // 3
        
        button_height = 60
        spacing = 25 
        
        BUTTON_WIDTH = 420 
        
        buttons = {}
        
        buttons["PLAY"] = pygame.Rect(center_x - (BUTTON_WIDTH // 2), start_y, BUTTON_WIDTH, button_height)
        buttons["EXIT"] = pygame.Rect(center_x - (BUTTON_WIDTH // 2), start_y + button_height + spacing, BUTTON_WIDTH, button_height)
        
        diff_start_y = start_y + 2 * (button_height + spacing) + 30
        
        for i, level in enumerate(config.DIFFICULTY_LEVELS):
            buttons[level] = pygame.Rect(
                center_x - (BUTTON_WIDTH // 2), 
                diff_start_y + i * (button_height + spacing), 
                BUTTON_WIDTH, 
                button_height
            )
        return buttons

    def handle_input(self, event):
        """Xử lý sự kiện click chuột trên Menu."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            if self.buttons["PLAY"].collidepoint(mouse_pos):
                return "PLAY", self.current_difficulty
            
            elif self.buttons["EXIT"].collidepoint(mouse_pos):
                return "QUIT", None
            
            for level in config.DIFFICULTY_LEVELS:
                if self.buttons[level].collidepoint(mouse_pos):
                    self.current_difficulty = level
                    return "DIFFICULTY_SELECTED", level
                
        return None, None

    def draw(self):
        """Vẽ toàn bộ Menu lên màn hình, sử dụng ảnh cho PLAY và vẽ hình cho EXIT/Difficulty."""
        
        # --- 1. Vẽ Background Chuyển Động ---
        if self.background_menu:
            self.bg_x -= self.scroll_speed
            if self.bg_x < -self.bg_width:
                self.bg_x = 0
            self.screen.blit(self.background_menu, (self.bg_x, 0))
            self.screen.blit(self.background_menu, (self.bg_x + self.bg_width, 0))
        else:
            self.screen.fill(self.COLOR_BLACK) 
        
        # --- 2. Vẽ Overlay mờ ---
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100)) 
        self.screen.blit(overlay, (0, 0))
        
        mouse_pos = pygame.mouse.get_pos()

        # --- 3. Vẽ Tiêu đề Game ---
        title_text = self.font_large.render("MAZE ESCAPE", True, self.COLOR_RED_TEXT) 
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 8))
        self.screen.blit(title_text, title_rect)

        # ----------------------------------------------------
        # --- 4. VẼ NÚT START (DÙNG ẢNH PIXEL ART) ---
        # ----------------------------------------------------
        
        # Nút PLAY
        button_image = self.button_green_hover if self.buttons["PLAY"].collidepoint(mouse_pos) else self.button_green_normal
        self.screen.blit(button_image, self.buttons["PLAY"])
        
        # ----------------------------------------------------
        # --- 5. VẼ NÚT EXIT (QUAY LẠI CODE CŨ: HÌNH HỌC) ---
        # ----------------------------------------------------
        rect_exit = self.buttons["EXIT"]
        
        # Màu nền: Đỏ và sáng hơn khi hover
        color_exit = (230, 80, 80) if rect_exit.collidepoint(mouse_pos) else self.COLOR_RED_BTN
        
        pygame.draw.rect(self.screen, color_exit, rect_exit, border_radius=10)
        
        # Vẽ chữ EXIT
        text_exit = self.font_button.render("EXIT GAME", True, self.COLOR_WHITE)
        self.screen.blit(text_exit, text_exit.get_rect(center=rect_exit.center))


        # --- 6. Vẽ Khung Chọn Độ Khó (QUAY LẠI CODE CŨ: HÌNH HỌC) ---
        
        label_text = self.font_medium.render("SELECT DIFFICULTY LEVEL:", True, self.COLOR_WHITE) 
        label_y = self.buttons[config.DIFFICULTY_LEVELS[0]].top - 30 
        self.screen.blit(label_text, label_text.get_rect(center=(self.width // 2, label_y)))

        for level in config.DIFFICULTY_LEVELS:
            rect = self.buttons[level]
            settings = config.DIFFICULTY_SETTINGS[level]
            
            # Màu nền: Xanh lá (được chọn) hoặc Xám (mặc định)
            if rect.collidepoint(mouse_pos):
                color = (70, 70, 70) # Xám sáng khi hover
            elif level == self.current_difficulty:
                color = self.COLOR_GREEN_BTN # Xanh khi được chọn
            else:
                color = (50, 50, 50) # Xám mặc định
                
            pygame.draw.rect(self.screen, color, rect, border_radius=10) 
            
            # Vẽ viền màu vàng cho mức độ đang được chọn
            if level == self.current_difficulty:
                pygame.draw.rect(self.screen, (255, 255, 0), rect, width=3, border_radius=10)

            # Vẽ chữ (DISPLAY_NAME)
            text = self.font_button.render(settings["DISPLAY_NAME"], True, self.COLOR_WHITE)
            self.screen.blit(text, text.get_rect(center=rect.center))