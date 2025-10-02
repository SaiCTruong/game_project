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
WIN_STATE = "WIN" 
LOSE_STATE = "LOSE" 
EDIT_STATE = "EDIT_MODE"
SELECTED_DIFFICULTY = "NORMAL" 

# Biến để lưu các đối tượng game (Global)
player = None
guard_manager = None
in_game_menu = None 
game_assets = {} 

# <<< THÊM BIẾN RECT CHO CÁC NÚT MỚI >>>
GEAR_SIZE = 30 
GEAR_RECT = None 
EDIT_BUTTON_SIZE = 30
EDIT_BUTTON_RECT = None
EXIT_EDIT_BUTTON_RECT = None # Nút để thoát chế độ Edit

# --- BIẾN AI MỚI ---
AI_TOGGLE_KEY = pygame.K_f
EDIT_TOGGLE_KEY = pygame.K_e 

# --- CÁC BIẾN CHO LOGIC WIN/LOSE ---
EXIT_TILE_X = (config.MAZE_COLS * 2) - 2 
EXIT_TILE_Y = (config.MAZE_ROWS * 2) - 1

tiles = None

# --- HÀM TIỆN ÍCH CẦN THIẾT ---

def invalidate_all_ai_paths():
    if player:
        player.ai_path = []
        player.ai_path_index = 0
    if guard_manager:
        for guard in guard_manager.guards:
            guard.path = []
            guard.path_index = 0
    print("AI paths invalidated due to map edit.")

# <<< CẬP NHẬT HÀM VẼ OVERLAY ĐỂ CÓ NÚT BẤM "XONG" >>>
def draw_edit_mode_overlay(screen):
    global EXIT_EDIT_BUTTON_RECT # Sử dụng biến toàn cục
    
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((255, 200, 0, 100))
    screen.blit(overlay, (0, 0))

    font = pygame.font.SysFont('Arial', 30, bold=True)
    text = font.render("EDIT MODE", True, (0, 0, 0))
    screen.blit(text, text.get_rect(center=(screen.get_width() // 2, 30)))
    
    font_small = pygame.font.SysFont('Arial', 20)
    text2 = font_small.render("Click to toggle walls", True, (0, 0, 0))
    screen.blit(text2, text2.get_rect(center=(screen.get_width() // 2, 70)))

    # Vẽ nút "DONE"
    btn_w, btn_h = 120, 50
    EXIT_EDIT_BUTTON_RECT = pygame.Rect(
        (screen.get_width() - btn_w) // 2,
        screen.get_height() - btn_h - 20,
        btn_w, btn_h
    )
    pygame.draw.rect(screen, (50, 200, 50), EXIT_EDIT_BUTTON_RECT, border_radius=8)
    done_text = font.render("DONE", True, (255, 255, 255))
    screen.blit(done_text, done_text.get_rect(center=EXIT_EDIT_BUTTON_RECT.center))


def load_image(path, size=None):
    if not os.path.exists(path):
        print(f"ERROR: File not found: {path}")
        pygame.quit(); sys.exit(1)
    img = pygame.image.load(path).convert_alpha() 
    if size:
        img = pygame.transform.scale(img, size)
    return img

current_map_index = 0

def load_game_assets(screen):
    # ... (Hàm này giữ nguyên)
    global game_assets
    size = (config.CELL_SIZE, config.CELL_SIZE)
    game_assets['maps'] = [
        load_image("game/assets/images/wooden.png", size),
        load_image("game/assets/images/wall.png", size),
        load_image("game/assets/images/ice.png", size),
        load_image("game/assets/images/tree_wooden.png", size)
    ]
    game_assets['in'] = load_image("game/assets/images/in.png", size)
    game_assets['out'] = load_image("game/assets/images/out.png", size)
    screen_w, screen_h = screen.get_size()
    game_assets['backgrounds'] = [
        pygame.transform.scale(pygame.image.load("game/assets/images/bg_wooden.png").convert_alpha(), (screen_w, screen_h)),
        pygame.transform.scale(pygame.image.load("game/assets/images/bg_wall.png").convert_alpha(), (screen_w, screen_h)),
        pygame.transform.scale(pygame.image.load("game/assets/images/bg_ice.png").convert_alpha(), (screen_w, screen_h)),
        pygame.transform.scale(pygame.image.load("game/assets/images/bg_tree_wooden.png").convert_alpha(), (screen_w, screen_h))
    ]


# <<< TẠO HÀM VẼ NÚT EDIT MỚI >>>
def draw_edit_button(screen):
    global EDIT_BUTTON_RECT
    screen_w, screen_h = screen.get_size()
    margin = 10
    
    # Đặt nút Edit bên trái nút Gear
    edit_button_x = screen_w - GEAR_SIZE - margin - EDIT_BUTTON_SIZE - margin
    EDIT_BUTTON_RECT = pygame.Rect(edit_button_x, margin, EDIT_BUTTON_SIZE, EDIT_BUTTON_SIZE)
    
    pygame.draw.circle(screen, (150, 150, 150), EDIT_BUTTON_RECT.center, EDIT_BUTTON_SIZE // 2, 0)
    pygame.draw.circle(screen, (50, 50, 50), EDIT_BUTTON_RECT.center, EDIT_BUTTON_SIZE // 2, 2)
    
    font = pygame.font.SysFont('Arial', 18, bold=True)
    text = font.render("E", True, (0, 0, 0)) # Biểu tượng Edit
    screen.blit(text, text.get_rect(center=EDIT_BUTTON_RECT.center))


def draw_gear_button(screen):
    # ... (Hàm này giữ nguyên)
    global GEAR_RECT
    screen_w, screen_h = screen.get_size()
    margin = 10
    GEAR_RECT = pygame.Rect(screen_w - GEAR_SIZE - margin, margin, GEAR_SIZE, GEAR_SIZE)
    pygame.draw.circle(screen, (150, 150, 150), GEAR_RECT.center, GEAR_SIZE // 2, 0)
    pygame.draw.circle(screen, (50, 50, 50), GEAR_RECT.center, GEAR_SIZE // 2, 2)
    font = pygame.font.SysFont('Arial', 18, bold=True)
    text = font.render("II", True, (0, 0, 0))
    screen.blit(text, text.get_rect(center=GEAR_RECT.center))
    
def draw_pause_menu(screen, in_game_menu):
    # ... (Hàm này giữ nguyên)
    menu_rect = in_game_menu.menu_rect
    buttons = in_game_menu.buttons
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180)) 
    screen.blit(overlay, (0, 0))
    pygame.draw.rect(screen, (50, 50, 50), menu_rect, border_radius=10) 
    pygame.draw.rect(screen, (255, 255, 255), menu_rect, 5, border_radius=10)
    font_title = in_game_menu.font_title
    font_button = in_game_menu.font_button
    title_text = font_title.render("GAME PAUSED", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(screen.get_width() // 2, menu_rect.top + 40)) 
    screen.blit(title_text, title_rect)
    rect_r = buttons["RESUME"]
    pygame.draw.rect(screen, (50, 200, 50), rect_r, border_radius=5)
    text_r = font_button.render("RESUME (ESC)", True, (0, 0, 0))
    screen.blit(text_r, text_r.get_rect(center=rect_r.center)) 
    rect_m = buttons["TO_MENU"]
    pygame.draw.rect(screen, (200, 50, 50), rect_m, border_radius=5)
    text_m = font_button.render("BACK TO MENU", True, (255, 255, 255))
    screen.blit(text_m, text_m.get_rect(center=rect_m.center))

def draw_game_end_screen(screen, message, color):
    # ... (Hàm này giữ nguyên)
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200)) 
    screen.blit(overlay, (0, 0))
    font_end = pygame.font.SysFont('Arial', 70, bold=True)
    font_small = pygame.font.SysFont('Arial', 40)
    title_text = font_end.render(message, True, color)
    title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 3))
    screen.blit(title_text, title_rect)
    BUTTON_WIDTH, BUTTON_HEIGHT = 300, 60
    center_x = screen.get_width() // 2
    menu_button_rect = pygame.Rect(center_x - (BUTTON_WIDTH // 2), screen.get_height() // 2, BUTTON_WIDTH, BUTTON_HEIGHT)
    mouse_pos = pygame.mouse.get_pos()
    is_hover = menu_button_rect.collidepoint(mouse_pos)
    button_color = (100, 100, 100) if is_hover else (50, 50, 50)
    pygame.draw.rect(screen, button_color, menu_button_rect, border_radius=10)
    text = font_small.render("BACK TO MENU", True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=menu_button_rect.center))
    return menu_button_rect

def draw_win_screen(screen):
    # ... (Hàm này giữ nguyên)
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200)) 
    screen.blit(overlay, (0, 0))
    font_end = pygame.font.SysFont('Arial', 70, bold=True)
    font_small = pygame.font.SysFont('Arial', 40)
    title_text = font_end.render("ESCAPE SUCCESS!", True, (50, 255, 50))
    title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 3))
    screen.blit(title_text, title_rect)
    subtext = font_small.render("Press ENTER to continue", True, (255, 255, 255))
    subtext_rect = subtext.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(subtext, subtext_rect)

def setup_new_game(tiles, difficulty_name, screen):
    # ... (Hàm này giữ nguyên)
    global player, guard_manager, SELECTED_DIFFICULTY, in_game_menu
    SELECTED_DIFFICULTY = difficulty_name
    player = Player(1, 1, tiles)
    guard_manager = GuardManager(tiles, difficulty=difficulty_name)
    guard_manager.spawn_guards()
    in_game_menu = InGameMenu(screen)

def run_game_loop(screen):
    global GAME_STATE, PAUSE_STATE, current_map_index, tiles
    
    running = True
    clock = pygame.time.Clock()
    
    while running:
        clock.tick(config.FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT" 
            
            if GAME_STATE == WIN_STATE or GAME_STATE == LOSE_STATE:
                # ... (Logic này giữ nguyên)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    menu_button_rect = draw_game_end_screen(screen, "", (0, 0, 0)) 
                    if menu_button_rect.collidepoint(event.pos):
                        return "BACK_TO_MENU"
                if GAME_STATE == WIN_STATE and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    current_map_index = (current_map_index + 1) % len(game_assets['maps'])
                    grid = generate_maze(config.MAZE_COLS, config.MAZE_ROWS)
                    tiles = maze_to_tiles(grid, config.MAZE_COLS, config.MAZE_ROWS)
                    setup_new_game(tiles, SELECTED_DIFFICULTY, screen)
                    GAME_STATE = "GAME"
                continue

            # --- Xử lý Input bằng phím ---
            if event.type == pygame.KEYDOWN:
                if event.key == AI_TOGGLE_KEY:
                    player.ai_mode = not player.ai_mode
                    print(f"Player AI mode: {'ON' if player.ai_mode else 'OFF'}")
                if event.key == EDIT_TOGGLE_KEY:
                    GAME_STATE = EDIT_STATE if GAME_STATE == "GAME" else "GAME"
                if event.key == pygame.K_ESCAPE:
                    if GAME_STATE == "GAME": GAME_STATE = "PAUSED"
                    elif GAME_STATE == "PAUSED": GAME_STATE = "GAME"

            # --- Xử lý Input bằng chuột ---
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Nút trái
                    # <<< XỬ LÝ CLICK CÁC NÚT KHI ĐANG CHƠI >>>
                    if GAME_STATE == "GAME":
                        if GEAR_RECT and GEAR_RECT.collidepoint(event.pos):
                            GAME_STATE = "PAUSED"
                        elif EDIT_BUTTON_RECT and EDIT_BUTTON_RECT.collidepoint(event.pos):
                            GAME_STATE = EDIT_STATE
                    
                    # <<< XỬ LÝ CLICK KHI ĐANG EDIT MAP >>>
                    elif GAME_STATE == EDIT_STATE:
                        if EXIT_EDIT_BUTTON_RECT and EXIT_EDIT_BUTTON_RECT.collidepoint(event.pos):
                            GAME_STATE = "GAME"
                        else: # Click vào map để sửa
                            mx, my = pygame.mouse.get_pos()
                            tile_x = mx // config.CELL_SIZE
                            tile_y = my // config.CELL_SIZE
                            if 0 <= tile_y < len(tiles) and 0 <= tile_x < len(tiles[0]):
                                start_pos = (1, 1)
                                exit_pos = (EXIT_TILE_X, EXIT_TILE_Y)
                                clicked_pos = (tile_x, tile_y)
                                if clicked_pos != start_pos and clicked_pos != exit_pos:
                                    tiles[tile_y][tile_x] = 1 - tiles[tile_y][tile_x]
                                    invalidate_all_ai_paths()
            
            # --- Xử lý input menu khi PAUSED ---
            if GAME_STATE == "PAUSED":
                action = in_game_menu.handle_input(event)
                if action == "RESUME": GAME_STATE = "GAME"
                elif action == "BACK_TO_MENU": return "BACK_TO_MENU" 
            
            # --- Input di chuyển của người chơi ---
            if GAME_STATE == "GAME" and not player.ai_mode:
                player.handle_input()

        # --- CẬP NHẬT LOGIC GAME ---
        if GAME_STATE == "GAME":
            if player.ai_mode:
                exit_tile = (EXIT_TILE_X, EXIT_TILE_Y)
                guard_list = guard_manager.guards
                player.handle_ai_move(tiles, exit_tile, guard_list) 
            guard_manager.update(player)
            
            for guard in guard_manager.guards:
                if player.check_collision_with_guard(guard):
                    GAME_STATE = LOSE_STATE
                    break
            # ... (phần code kiểm tra va chạm với guard)

            # --- KIỂM TRA ĐIỀU KIỆN THẮNG BẰNG VA CHẠM ---
            # 1. Tạo hitbox cho người chơi
            player_rect = pygame.Rect(
                player.x * config.CELL_SIZE, 
                player.y * config.CELL_SIZE, 
                player.size, 
                player.size
            )
            # Tạo hitbox nhỏ hơn một chút để cảm giác "chạm" thật hơn
            player_hitbox = player_rect.inflate(-player_rect.width * 0.5, -player_rect.height * 0.5)

            # 2. Tạo hitbox cho cửa ra
            exit_rect = pygame.Rect(
                (EXIT_TILE_X) * config.CELL_SIZE, # <<< THÊM +1 VÀO ĐÂY
                (EXIT_TILE_Y) * config.CELL_SIZE, # <<< VÀ VÀO ĐÂY
                config.CELL_SIZE, 
                config.CELL_SIZE
            )

            # 3. Kiểm tra nếu hitbox người chơi va chạm với cửa ra
            if player_hitbox.colliderect(exit_rect):
                GAME_STATE = WIN_STATE
                
        # --- VẼ CÁC THÀNH PHẦN ---
        background_img = game_assets['backgrounds'][current_map_index]
        screen.blit(background_img, (0, 0))
        render_maze(screen, tiles, game_assets['maps'][current_map_index])
        screen.blit(game_assets['in'], (1 * config.CELL_SIZE, 0))
        screen.blit(game_assets['out'], ((EXIT_TILE_X) * config.CELL_SIZE, (EXIT_TILE_Y + 1) * config.CELL_SIZE)) 
        guard_manager.draw(screen)
        player.draw(screen)

        # --- VẼ CÁC LỚP PHỦ VÀ NÚT BẤM LÊN TRÊN CÙNG ---
        if GAME_STATE == "GAME":
            draw_gear_button(screen) 
            draw_edit_button(screen) # <<< VẼ NÚT EDIT >>>
        elif GAME_STATE == "PAUSED":
            draw_pause_menu(screen, in_game_menu)
        elif GAME_STATE == EDIT_STATE:
            draw_edit_mode_overlay(screen)
        elif GAME_STATE == LOSE_STATE:
            draw_game_end_screen(screen, "YOU WERE CAUGHT!", (255, 50, 50))
        elif GAME_STATE == WIN_STATE:
            draw_win_screen(screen)

        pygame.display.flip()
        
    return "QUIT"

def main():
    # ... (Hàm này giữ nguyên)
    global GAME_STATE, SELECTED_DIFFICULTY, tiles
    pygame.init()
    pygame.key.set_repeat(100, 50) 
    grid = generate_maze(config.MAZE_COLS, config.MAZE_ROWS)
    tiles = maze_to_tiles(grid, config.MAZE_COLS, config.MAZE_ROWS)
    screen_w = len(tiles[0]) * config.CELL_SIZE
    screen_h = len(tiles) * config.CELL_SIZE
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Maze Escape")
    load_game_assets(screen) 
    menu = Menu(screen)
    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(config.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if GAME_STATE == "MENU":
                action, level = menu.handle_input(event)
                if action == "PLAY":
                    setup_new_game(tiles, menu.current_difficulty, screen) 
                    GAME_STATE = "GAME"
                elif action == "QUIT":
                    running = False
                elif action == "DIFFICULTY_SELECTED":
                    print(f"Mức độ đã chọn: {level}")
        if GAME_STATE == "MENU":
            menu.draw()
        else:
            result = run_game_loop(screen)
            if result == "QUIT":
                running = False
            elif result == "BACK_TO_MENU":
                GAME_STATE = "MENU"
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()