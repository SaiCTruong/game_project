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
        self.COLOR_GREEN_BTN = (50, 200, 50) 
        self.COLOR_RED_BTN = (200, 50, 50)   

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

        # --- Tải Hình ảnh Nút Bấm MỚI ---
        # Kích thước tải ảnh: START và EXIT có kích thước khác nhau
        self.button_size_play = (self.buttons["PLAY"].width, self.buttons["PLAY"].height)
        self.button_size_exit = (self.buttons["EXIT"].width, self.buttons["EXIT"].height)
        
        # 1. Nút START (Green)
        self.button_green_normal = self._load_button_image("button_green_hover.png", self.button_size_play)
        self.button_green_hover = self._load_button_image("BlueStandartStart.png", self.button_size_play) or self.button_green_normal
        
        # 2. Nút EXIT (Red) - Sử dụng tên file mới (ví dụ: quit_normal.png)
        # Tải ảnh cho nút EXIT/QUIT
        self.button_quit_normal = self._load_button_image("RedStandartQuit.png", self.button_size_exit)
        self.button_quit_hover = self._load_button_image("BlueStandartQuit.png", self.button_size_exit) or self.button_quit_normal

        # --- Logic Fallback ---
        if self.button_green_normal == None:
             self.button_green_normal = pygame.Surface(self.button_size_play, pygame.SRCALPHA); self.button_green_normal.fill(self.COLOR_GREEN_BTN)
        if self.button_green_hover == None:
             self.button_green_hover = self.button_green_normal
        
        if self.button_quit_normal == None: # Fallback cho nút EXIT
             self.button_quit_normal = pygame.Surface(self.button_size_exit, pygame.SRCALPHA); self.button_quit_normal.fill(self.COLOR_RED_BTN)
        if self.button_quit_hover == None:
             self.button_quit_hover = self.button_quit_normal
        # ----------------------------------------------

    def _load_button_image(self, filename, size):
        """Hàm trợ giúp để tải và scale hình ảnh nút."""
        path = f"game/assets/images/{filename}"
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, size)
        else:
            print(f"Cảnh báo: Không tìm thấy hình ảnh nút {filename}.")
            return None

    def _setup_buttons(self):
        """Khởi tạo vị trí các nút PLAY, EXIT và 4 nút Độ Khó (Tối ưu hóa khoảng cách)."""
        center_x = self.width // 2
        
        # Bắt đầu cao hơn (self.height // 10)
        start_y = self.height // 10 
        
        # --- Kích thước LỚN cho START và EXIT ---
        LARGE_BUTTON_WIDTH = 200
        LARGE_BUTTON_HEIGHT = 150
        
        # --- Kích thước CHUNG cho DIFFICULTY ---
        NORMAL_BUTTON_HEIGHT = 60
        NORMAL_BUTTON_WIDTH = 420
        
        spacing = 5 # Khoảng cách giữa các nút Độ Khó (giữ 5px)
        
        buttons = {}
        
        # 1. Nút PLAY (START)
        buttons["PLAY"] = pygame.Rect(
            center_x - (LARGE_BUTTON_WIDTH // 2), 
            start_y, 
            LARGE_BUTTON_WIDTH, 
            LARGE_BUTTON_HEIGHT
        )
        
        # 2. Nút EXIT
        # FIX QUAN TRỌNG: Khoảng cách giữa START và EXIT
        EXIT_SPACING = 0 # <--- Đặt khoảng cách về 0px (Sát nhau nhất)
        
        # Vị trí Y mới: start_y + (Chiều cao PLAY) + 0
        exit_y = start_y + LARGE_BUTTON_HEIGHT + EXIT_SPACING
        buttons["EXIT"] = pygame.Rect(
            center_x - (LARGE_BUTTON_WIDTH // 2), 
            exit_y, 
            LARGE_BUTTON_WIDTH, 
            LARGE_BUTTON_HEIGHT
        )
        
        # 3. Nút Chọn độ khó
        # Bắt đầu sau nút EXIT + spacing (Sử dụng spacing 5px)
        diff_start_y = exit_y + LARGE_BUTTON_HEIGHT + spacing 
        
        for i, level in enumerate(config.DIFFICULTY_LEVELS):
            buttons[level] = pygame.Rect(
                center_x - (NORMAL_BUTTON_WIDTH // 2), 
                diff_start_y + i * (NORMAL_BUTTON_HEIGHT + spacing), 
                NORMAL_BUTTON_WIDTH, 
                NORMAL_BUTTON_HEIGHT
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
        """Vẽ toàn bộ Menu lên màn hình, sử dụng ảnh cho PLAY/EXIT và vẽ hình cho Difficulty."""
        
        # ... (Vẽ Background và Overlay giữ nguyên) ...
        if self.background_menu:
            self.bg_x -= self.scroll_speed
            if self.bg_x < -self.bg_width:
                self.bg_x = 0
            self.screen.blit(self.background_menu, (self.bg_x, 0))
            self.screen.blit(self.background_menu, (self.bg_x + self.bg_width, 0))
        else:
            self.screen.fill(self.COLOR_BLACK) 
        
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
        # --- 5. VẼ NÚT EXIT (DÙNG ẢNH PIXEL ART) ---
        # ----------------------------------------------------
        rect_exit = self.buttons["EXIT"]
        
        # Sử dụng ảnh nút QUIT/EXIT
        button_image_exit = self.button_quit_hover if rect_exit.collidepoint(mouse_pos) else self.button_quit_normal
        self.screen.blit(button_image_exit, rect_exit)
        
        # ----------------------------------------------------
        # --- 6. Vẽ Khung Chọn Độ Khó (QUAY LẠI CODE CŨ: HÌNH HỌC) ---
        # ----------------------------------------------------
        
       
        label_y = self.buttons[config.DIFFICULTY_LEVELS[0]].top - 30 
        

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