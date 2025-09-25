# game/main.py

import os
import sys
import pygame
from game import config
from game.maze.generator import generate_maze, maze_to_tiles
from game.render.renderer import render_maze
from game.entities.player import Player
from game.controllers.guard_manager import GuardManager
from game.render.menu import Menu
from game.render.in_game_menu import InGameMenu

# Định nghĩa Trạng thái Game
GAME_STATE = "MENU" 
PAUSE_STATE = "GAME"
SELECTED_DIFFICULTY = "NORMAL" 

# Biến để lưu các đối tượng game (Global)
player = None
guard_manager = None
in_game_menu = None 
game_assets = {} 

# Kích thước nút Bánh Răng (Global)
GEAR_SIZE = 30 
GEAR_RECT = None 

# --- HÀM TIỆN ÍCH CẦN THIẾT ---

def load_image(path, size=None):
    """Load ảnh, kiểm tra file tồn tại, nếu không thì báo lỗi và thoát."""
    if not os.path.exists(path):
        print(f"ERROR: File not found: {path}")
        pygame.quit()
        sys.exit(1)
    img = pygame.image.load(path).convert_alpha() 
    if size:
        img = pygame.transform.scale(img, size)
    return img

def load_game_assets():
    """Tải tất cả ảnh cần thiết, chỉ chạy một lần."""
    global game_assets
    size = (config.CELL_SIZE, config.CELL_SIZE)
    game_assets['wall'] = load_image("game/assets/images/wall.png", size)
    game_assets['in'] = load_image("game/assets/images/in.png", size)
    game_assets['out'] = load_image("game/assets/images/out.png", size)
    game_assets['background'] = pygame.image.load("game/assets/images/background.png").convert_alpha()


def draw_gear_button(screen):
    """Vẽ nút Bánh Răng (Tạm dừng) ở góc trên bên phải của Game Area."""
    global GEAR_RECT
    
    screen_w, screen_h = screen.get_size()
    margin = 10
    
    GEAR_RECT = pygame.Rect(screen_w - GEAR_SIZE - margin, margin, GEAR_SIZE, GEAR_SIZE)
    
    # Vẽ hình tròn đơn giản (thay thế cho icon bánh răng)
    pygame.draw.circle(screen, (150, 150, 150), GEAR_RECT.center, GEAR_SIZE // 2, 0)
    pygame.draw.circle(screen, (50, 50, 50), GEAR_RECT.center, GEAR_SIZE // 2, 2)
    
    # Vẽ biểu tượng
    font = pygame.font.SysFont('Arial', 18, bold=True)
    text = font.render("II", True, (0, 0, 0)) # Biểu tượng Tạm dừng
    screen.blit(text, text.get_rect(center=GEAR_RECT.center))


def draw_pause_menu(screen, in_game_menu):
    """
    Vẽ menu PAUSED ở layer trên cùng (Modal Centered).
    """
    menu_rect = in_game_menu.menu_rect
    buttons = in_game_menu.buttons
    
    # 1. Hiệu ứng làm mờ nền game (Vẽ lớp phủ mờ toàn màn hình)
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180)) 
    screen.blit(overlay, (0, 0))

    # 2. Vẽ nền Menu Modal chính
    pygame.draw.rect(screen, (50, 50, 50), menu_rect, border_radius=10) 
    pygame.draw.rect(screen, (255, 255, 255), menu_rect, 5, border_radius=10) # Viền

    # 3. Vẽ Tiêu đề
    font_title = in_game_menu.font_title
    font_button = in_game_menu.font_button
    
    title_text = font_title.render("GAME PAUSED", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(screen.get_width() // 2, menu_rect.top + 40)) 
    screen.blit(title_text, title_rect)

    # 4. Vẽ các Nút bấm
    
    # Nút RESUME
    rect_r = buttons["RESUME"]
    pygame.draw.rect(screen, (50, 200, 50), rect_r, border_radius=5)
    text_r = font_button.render("RESUME (ESC)", True, (0, 0, 0))
    screen.blit(text_r, text_r.get_rect(center=rect_r.center)) 

    # Nút BACK TO MENU
    rect_m = buttons["TO_MENU"]
    pygame.draw.rect(screen, (200, 50, 50), rect_m, border_radius=5)
    text_m = font_button.render("BACK TO MENU", True, (255, 255, 255))
    screen.blit(text_m, text_m.get_rect(center=rect_m.center))


# --- HÀM KHỞI TẠO GAME ---

def setup_new_game(tiles, difficulty_name, screen):
    """Khởi tạo Player, GuardManager và InGameMenu dựa trên độ khó đã chọn."""
    global player, guard_manager, SELECTED_DIFFICULTY, in_game_menu
    
    SELECTED_DIFFICULTY = difficulty_name
    
    player = Player(1, 1, tiles)
    guard_manager = GuardManager(tiles, difficulty=difficulty_name)
    guard_manager.spawn_guards()
    
    in_game_menu = InGameMenu(screen)


def run_game_loop(screen, tiles):
    """
    Game Loop chính, xử lý trạng thái GAME và PAUSED.
    """
    global GAME_STATE, PAUSE_STATE 
    
    running = True
    clock = pygame.time.Clock()
    
    screen_w, screen_h = screen.get_size()
    background_img = pygame.transform.scale(game_assets['background'], (screen_w, screen_h))

    while running:
        clock.tick(config.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT" 
            
            # --- Xử lý Tạm dừng ---
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if GAME_STATE == "GAME":
                    GAME_STATE = "PAUSED"
                elif GAME_STATE == "PAUSED":
                    GAME_STATE = "GAME" 

            # Xử lý Click Nút Bánh Răng
            if event.type == pygame.MOUSEBUTTONDOWN and GAME_STATE == "GAME":
                if GEAR_RECT and GEAR_RECT.collidepoint(event.pos):
                    GAME_STATE = "PAUSED"


            # Xử lý input menu khi đang PAUSED
            if GAME_STATE == "PAUSED":
                action = in_game_menu.handle_input(event)
                
                if action == "RESUME":
                    GAME_STATE = "GAME"
                elif action == "BACK_TO_MENU":
                    return "BACK_TO_MENU" 

        # --- CẬP NHẬT & VẼ GAME LOGIC ---
        
        screen.blit(background_img, (0, 0))
        
        if GAME_STATE == "GAME":
            player.handle_input()
            guard_manager.update(player)
        
        render_maze(screen, tiles, game_assets['wall'])
        screen.blit(game_assets['in'], (1 * config.CELL_SIZE, 0))
        screen.blit(game_assets['out'], ((len(tiles[0]) - 2) * config.CELL_SIZE,
                                         (len(tiles) - 1) * config.CELL_SIZE))
        guard_manager.draw(screen)
        player.draw(screen)

        # Vẽ Nút Bánh Răng chỉ khi game đang chạy
        if GAME_STATE == "GAME":
            draw_gear_button(screen) 

        # Vẽ Menu PAUSED (luôn ở layer trên cùng)
        if GAME_STATE == "PAUSED":
            draw_pause_menu(screen, in_game_menu)

        pygame.display.flip()
        
    return "QUIT"


def main():
    global GAME_STATE, SELECTED_DIFFICULTY
    
    # --- 1. Khởi tạo Pygame & Assets ---
    pygame.init()
    
    # Sinh mê cung (tạo map tĩnh để dễ quản lý)
    grid = generate_maze(config.MAZE_COLS, config.MAZE_ROWS)
    tiles = maze_to_tiles(grid, config.MAZE_COLS, config.MAZE_ROWS)

    # Kích thước màn hình CHỈ THEO KÍCH THƯỚC MÊ CUNG
    screen_w = len(tiles[0]) * config.CELL_SIZE
    screen_h = len(tiles) * config.CELL_SIZE
    
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Maze Escape")
    
    load_game_assets() 

    menu = Menu(screen)
    clock = pygame.time.Clock()

    # --- 2. Main Loop ---
    running = True
    while running:
        clock.tick(config.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if GAME_STATE == "MENU":
                action, level = menu.handle_input(event)
                
                if action == "PLAY":
                    # Khởi tạo game mới
                    setup_new_game(tiles, menu.current_difficulty, screen) 
                    GAME_STATE = "GAME"
                elif action == "QUIT":
                    running = False
                elif action == "DIFFICULTY_SELECTED":
                    print(f"Mức độ đã chọn: {level}")


        if GAME_STATE == "MENU":
            menu.draw()
            
        elif GAME_STATE == "GAME" or GAME_STATE == "PAUSED": 
            result = run_game_loop(screen, tiles)
            
            if result == "QUIT":
                running = False
            elif result == "BACK_TO_MENU":
                GAME_STATE = "MENU"

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()