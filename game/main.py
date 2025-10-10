import os
import sys
import pygame
import math
from collections import deque
from game import config
from game.maze.generator import generate_maze, maze_to_tiles
from game.render.renderer import render_maze
from game.entities.player import Player
from game.controllers.guard_manager import GuardManager
from game.render.menu import Menu
from game.render.in_game_menu import InGameMenu
from game.ai.pathfinding import PATHFINDING_ALGORITHMS

# =======================================================================================
# KHAI BÁO BIẾN TOÀN CỤC VÀ TRẠNG THÁI
# =======================================================================================

# Định nghĩa các trạng thái của game
GAME_STATE = "MENU"
PAUSE_STATE = "GAME"
WIN_STATE = "WIN"
LOSE_STATE = "LOSE"
EDIT_STATE = "EDIT_MODE"
REPLAY_SELECT_STATE = "REPLAY_SELECT"
SELECTED_DIFFICULTY = "NORMAL"

# Biến toàn cục cho các đối tượng và dữ liệu game
player = None
guard_manager = None
in_game_menu = None
game_assets = {}
tiles = None
current_map_index = 0
current_maze_tiles = None
replay_stats_history = []
is_path_blocked = False
path_warning_timer = 0
reachable_tiles_from_player = set()
# Biến cho các nút bấm và bảng thông tin
STATS_BUTTON_RECT = None
STATS_PANEL_VISIBLE = False
REPLAY_BUTTON_RECT = None
GEAR_SIZE, EDIT_BUTTON_SIZE, HIDE_GUARDS_BUTTON_SIZE, AI_BUTTON_SIZE = 30, 30, 30, 30
GEAR_RECT, EDIT_BUTTON_RECT, HIDE_GUARDS_BUTTON_RECT, AI_BUTTON_RECT, EXIT_EDIT_BUTTON_RECT = None, None, None, None, None
GUARDS_VISIBLE = True

# Phím tắt và tọa độ
EDIT_TOGGLE_KEY = pygame.K_e
EXIT_TILE_X = (config.MAZE_COLS * 2) - 2
EXIT_TILE_Y = (config.MAZE_ROWS * 2) - 1


# =======================================================================================
# CÁC HÀM TIỆN ÍCH
# =======================================================================================

def invalidate_all_ai_paths():
    """Reset đường đi của AI khi bản đồ bị chỉnh sửa."""
    if player:
        player.ai_path, player.ai_path_index = [], 0
    if guard_manager:
        for guard in guard_manager.guards:
            guard.path, guard.path_index = [], 0
    print("AI paths invalidated due to map edit.")

def load_image(path, size=None):
    """Tải một hình ảnh từ đường dẫn, xử lý lỗi và thay đổi kích thước nếu cần."""
    if not os.path.exists(path):
        print(f"ERROR: File not found: {path}")
        pygame.quit()
        sys.exit(1)
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.scale(img, size)
    return img

def load_game_assets(screen):
    """Tải tất cả các tài nguyên hình ảnh cần thiết cho game."""
    global game_assets
    size = (config.CELL_SIZE, config.CELL_SIZE)
    screen_w, screen_h = screen.get_size()
    
    game_assets['maps'] = [load_image(f"game/assets/images/{theme}.png", size) for theme in config.MAP_THEMES]
    game_assets['backgrounds'] = [
        pygame.transform.scale(pygame.image.load(f"game/assets/images/bg_{theme}.png").convert_alpha(), (screen_w, screen_h)) 
        for theme in config.MAP_THEMES
    ]
    game_assets['in'] = load_image("game/assets/images/in.png", size)
    game_assets['out'] = load_image("game/assets/images/out.png", size)

    # Load ảnh dấu chân và thu nhỏ một chút
    footprint_size = (config.CELL_SIZE // 2, config.CELL_SIZE // 2) 
    game_assets['footprint'] = load_image("game/assets/images/footprint.png", footprint_size)

# =======================================================================================
# CÁC HÀM VẼ UI (NÚT BẤM, BẢNG, LỚP PHỦ)
# =======================================================================================

def draw_gear_button(screen):
    """Vẽ nút Pause (bánh răng)."""
    global GEAR_RECT
    screen_w, _ = screen.get_size()
    margin = 10
    GEAR_RECT = pygame.Rect(screen_w - GEAR_SIZE - margin, margin, GEAR_SIZE, GEAR_SIZE)
    pygame.draw.circle(screen, (150, 150, 150), GEAR_RECT.center, GEAR_SIZE // 2, 0)
    pygame.draw.circle(screen, (50, 50, 50), GEAR_RECT.center, GEAR_SIZE // 2, 2)
    font = pygame.font.SysFont('Arial', 18, bold=True)
    text = font.render("II", True, (0, 0, 0))
    screen.blit(text, text.get_rect(center=GEAR_RECT.center))

def draw_edit_button(screen):
    """Vẽ nút Edit (chữ E)."""
    global EDIT_BUTTON_RECT
    screen_w, _ = screen.get_size()
    margin = 10
    edit_button_x = screen_w - GEAR_SIZE - margin - EDIT_BUTTON_SIZE - margin
    EDIT_BUTTON_RECT = pygame.Rect(edit_button_x, margin, EDIT_BUTTON_SIZE, EDIT_BUTTON_SIZE)
    pygame.draw.circle(screen, (150, 150, 150), EDIT_BUTTON_RECT.center, EDIT_BUTTON_SIZE // 2, 0)
    pygame.draw.circle(screen, (50, 50, 50), EDIT_BUTTON_RECT.center, EDIT_BUTTON_SIZE // 2, 2)
    font = pygame.font.SysFont('Arial', 18, bold=True)
    text = font.render("E", True, (0, 0, 0))
    screen.blit(text, text.get_rect(center=EDIT_BUTTON_RECT.center))

def draw_hide_guards_button(screen):
    """Vẽ nút ẩn/hiện lính gác (chữ G)."""
    global HIDE_GUARDS_BUTTON_RECT
    screen_w, _ = screen.get_size()
    margin = 10
    hide_button_x = screen_w - GEAR_SIZE - margin - EDIT_BUTTON_SIZE - margin - HIDE_GUARDS_BUTTON_SIZE - margin
    HIDE_GUARDS_BUTTON_RECT = pygame.Rect(hide_button_x, margin, HIDE_GUARDS_BUTTON_SIZE, HIDE_GUARDS_BUTTON_SIZE)
    color = (150, 150, 150) if GUARDS_VISIBLE else (80, 80, 80)
    pygame.draw.circle(screen, color, HIDE_GUARDS_BUTTON_RECT.center, HIDE_GUARDS_BUTTON_SIZE // 2, 0)
    pygame.draw.circle(screen, (50, 50, 50), HIDE_GUARDS_BUTTON_RECT.center, HIDE_GUARDS_BUTTON_SIZE // 2, 2)
    font = pygame.font.SysFont('Arial', 18, bold=True)
    text = font.render("G", True, (0, 0, 0))
    screen.blit(text, text.get_rect(center=HIDE_GUARDS_BUTTON_RECT.center))
    if not GUARDS_VISIBLE:
        pygame.draw.line(screen, (255, 0, 0), HIDE_GUARDS_BUTTON_RECT.topleft, HIDE_GUARDS_BUTTON_RECT.bottomright, 3)

def draw_ai_button(screen):
    """Vẽ nút bật/tắt AI."""
    global AI_BUTTON_RECT
    screen_w, _ = screen.get_size()
    margin = 10
    ai_button_x = screen_w - GEAR_SIZE - margin - EDIT_BUTTON_SIZE - margin - HIDE_GUARDS_BUTTON_SIZE - margin - AI_BUTTON_SIZE - margin
    AI_BUTTON_RECT = pygame.Rect(ai_button_x, margin, AI_BUTTON_SIZE, AI_BUTTON_SIZE)
    color = (100, 180, 255) if player and player.ai_mode else (80, 80, 80)
    pygame.draw.circle(screen, color, AI_BUTTON_RECT.center, AI_BUTTON_SIZE // 2, 0)
    pygame.draw.circle(screen, (50, 50, 50), AI_BUTTON_RECT.center, AI_BUTTON_SIZE // 2, 2)
    font = pygame.font.SysFont('Arial', 14, bold=True)
    text = font.render("AI", True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=AI_BUTTON_RECT.center))
    
def draw_edit_mode_overlay(screen):
    """Vẽ lớp phủ khi ở chế độ Edit."""
    global EXIT_EDIT_BUTTON_RECT
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((255, 200, 0, 100))
    screen.blit(overlay, (0, 0))
    
    font_large = pygame.font.SysFont('Arial', 30, bold=True)
    font_small = pygame.font.SysFont('Arial', 20)
    
    text = font_large.render("EDIT MODE", True, (0, 0, 0))
    screen.blit(text, text.get_rect(center=(screen.get_width() // 2, 30)))
    
    text2 = font_small.render("Click to toggle walls", True, (0, 0, 0))
    screen.blit(text2, text2.get_rect(center=(screen.get_width() // 2, 70)))
    
    btn_w, btn_h = 120, 50
    EXIT_EDIT_BUTTON_RECT = pygame.Rect((screen.get_width() - btn_w) // 2, screen.get_height() - btn_h - 20, btn_w, btn_h)
    pygame.draw.rect(screen, (50, 200, 50), EXIT_EDIT_BUTTON_RECT, border_radius=8)
    
    done_text = font_large.render("DONE", True, (255, 255, 255))
    screen.blit(done_text, done_text.get_rect(center=EXIT_EDIT_BUTTON_RECT.center))

def draw_pause_menu(screen, in_game_menu):
    """Vẽ menu tạm dừng game."""
    menu_rect = in_game_menu.menu_rect
    buttons = in_game_menu.buttons
    
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
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
    """Vẽ màn hình kết thúc game chung (Thắng/Thua)."""
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    font_end = pygame.font.SysFont('Arial', 70, bold=True)
    font_small = pygame.font.SysFont('Arial', 40)
    
    title_text = font_end.render(message, True, color)
    title_rect = title_text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 3))
    screen.blit(title_text, title_rect)
    
    btn_w, btn_h = 300, 60
    center_x = screen.get_width() // 2
    menu_button_rect = pygame.Rect(center_x - (btn_w // 2), screen.get_height() // 2, btn_w, btn_h)
    
    is_hover = menu_button_rect.collidepoint(pygame.mouse.get_pos())
    btn_color = (100, 100, 100) if is_hover else (50, 50, 50)
    pygame.draw.rect(screen, btn_color, menu_button_rect, border_radius=10)
    
    text = font_small.render("BACK TO MENU", True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=menu_button_rect.center))
    
    return menu_button_rect

def draw_win_screen(screen):
    """Vẽ màn hình chiến thắng."""
    return draw_game_end_screen(screen, "ESCAPE SUCCESS!", (50, 255, 50))

def draw_stats_button(screen):
    """Vẽ nút 'i' (Info) để xem thông tin thuật toán."""
    global STATS_BUTTON_RECT
    margin = 15
    size = 40
    STATS_BUTTON_RECT = pygame.Rect(margin, margin, size, size)
    pygame.draw.rect(screen, (200, 200, 200), STATS_BUTTON_RECT, border_radius=5)
    pygame.draw.rect(screen, (50, 50, 50), STATS_BUTTON_RECT, 3, 5)
    font = pygame.font.SysFont('Arial', 30, bold=True)
    text = font.render("i", True, (0, 0, 0))
    screen.blit(text, text.get_rect(center=STATS_BUTTON_RECT.center))

def draw_stats_panel(screen, stats_history):
    """Vẽ bảng so sánh thông tin của các thuật toán đã chạy."""
    panel_w, panel_h = 850, 400  # <<< Tăng chiều rộng bảng
    panel_rect = pygame.Rect((screen.get_width() - panel_w) / 2, (screen.get_height() - panel_h) / 2, panel_w, panel_h)

    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))
    
    pygame.draw.rect(screen, (30, 30, 30), panel_rect, border_radius=10)
    pygame.draw.rect(screen, (200, 200, 200), panel_rect, 4, 10)

    font_title = pygame.font.SysFont('Arial', 32, bold=True)
    font_header = pygame.font.SysFont('Arial', 22, bold=True)
    font_row = pygame.font.SysFont('Arial', 20)

    title_text = font_title.render("Algorithm Comparison", True, (255, 255, 0))
    screen.blit(title_text, title_text.get_rect(centerx=panel_rect.centerx, y=panel_rect.top + 20))

    # <<< THAY ĐỔI 1: Cập nhật header và vị trí các cột >>>
    headers = ["Algorithm", "Steps", "Time (ms)", "Generated", "Expanded"]
    col_positions = [
        panel_rect.left + 30,   # Algorithm
        panel_rect.left + 320,  # Steps
        panel_rect.left + 430,  # Time
        panel_rect.left + 590,  # Generated
        panel_rect.left + 720   # Expanded
    ]
    
    # Vẽ header
    header_y = panel_rect.top + 80
    for i, header in enumerate(headers):
        header_surf = font_header.render(header, True, (255, 255, 255))
        screen.blit(header_surf, (col_positions[i], header_y))
        
    pygame.draw.line(screen, (150, 150, 150), (panel_rect.left + 20, header_y + 30), (panel_rect.right - 20, header_y + 30), 2)

    # Vẽ các dòng dữ liệu
    row_y_start = header_y + 50
    for i, stats in enumerate(stats_history):
        row_y = row_y_start + i * 35
        
      
        data = [
            str(stats.get('name', 'N/A')),
            str(stats.get('path_length', 0)),
            f"{stats.get('time', 0) * 1000:.2f}",
            str(stats.get('nodes_generated', 'N/A')),
            str(stats.get('nodes_expanded', 'N/A'))
        ]
        
        for j, item in enumerate(data):
            item_surf = font_row.render(item, True, (210, 210, 210))
            screen.blit(item_surf, (col_positions[j], row_y))
            
    # Nút đóng 'X' (giữ nguyên)
    close_btn_size = 30
    close_btn_rect = pygame.Rect(panel_rect.right - close_btn_size - 10, panel_rect.top + 10, close_btn_size, close_btn_size)
    pygame.draw.rect(screen, (200, 50, 50), close_btn_rect, border_radius=5)
    close_text = font_title.render("X", True, (255, 255, 255))
    screen.blit(close_text, close_text.get_rect(center=close_btn_rect.center))
    
    return close_btn_rect

def draw_replay_button(screen):
    """Vẽ nút Replay để chơi lại trên cùng mê cung."""
    global REPLAY_BUTTON_RECT
    btn_w, btn_h = 180, 50
    center_y = screen.get_height() // 2 + 70
    center_x = screen.get_width() // 2
    REPLAY_BUTTON_RECT = pygame.Rect(center_x - (btn_w / 2), center_y, btn_w, btn_h)
    
    is_hover = REPLAY_BUTTON_RECT.collidepoint(pygame.mouse.get_pos())
    btn_color = (60, 120, 200) if is_hover else (40, 80, 150)
    pygame.draw.rect(screen, btn_color, REPLAY_BUTTON_RECT, border_radius=10)
    
    font = pygame.font.SysFont('Arial', 30, bold=True)
    text = font.render("Replay", True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=REPLAY_BUTTON_RECT.center))


def draw_replay_menu(screen):
    
    algorithms = list(PATHFINDING_ALGORITHMS.keys())
    num_algos = len(algorithms)


    top_padding = 80  # Khoảng trống cho tiêu đề
    bottom_padding = 40 # Khoảng trống ở dưới
    button_spacing = 55 # Khoảng cách giữa các nút
    
    panel_w = 500
    # Tính chiều cao cần thiết: top + (số nút * khoảng cách) + bottom
    panel_h = top_padding + (num_algos * button_spacing) + bottom_padding
    
    # Đảm bảo panel không cao hơn màn hình
    panel_h = min(panel_h, screen.get_height() * 0.95)

    panel_rect = pygame.Rect((screen.get_width() - panel_w) / 2, (screen.get_height() - panel_h) / 2, panel_w, panel_h)
    
    # Phần code vẽ còn lại giữ nguyên
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 220))
    screen.blit(overlay, (0, 0))
    
    pygame.draw.rect(screen, (40, 40, 40), panel_rect, border_radius=10)
    pygame.draw.rect(screen, (180, 180, 180), panel_rect, 4, 10)
    
    font_title = pygame.font.SysFont('Arial', 32, bold=True)
    font_button = pygame.font.SysFont('Arial', 24)
    
    title_text = font_title.render("Select New Algorithm", True, (255, 255, 0))
    screen.blit(title_text, title_text.get_rect(centerx=panel_rect.centerx, y=panel_rect.top + 20))
    
    button_rects = {}
    mouse_pos = pygame.mouse.get_pos()
    
    for i, algo_name in enumerate(algorithms):
        btn_rect = pygame.Rect(panel_rect.left + 50, panel_rect.top + 80 + i * button_spacing, panel_w - 100, 45)
        
        # Chỉ vẽ nút nếu nó nằm trong phạm vi panel (phòng trường hợp quá nhiều nút)
        if panel_rect.contains(btn_rect):
            is_hover = btn_rect.collidepoint(mouse_pos)
            btn_color = (100, 100, 100) if is_hover else (70, 70, 70)
            pygame.draw.rect(screen, btn_color, btn_rect, border_radius=8)
            text_surf = font_button.render(algo_name, True, (255, 255, 255))
            screen.blit(text_surf, text_surf.get_rect(center=btn_rect.center))
            button_rects[algo_name] = btn_rect
            
    return button_rects


def draw_footprints(screen, player, footprint_img):
    """Vẽ tất cả dấu chân đã được lưu lại của người chơi."""
    if not player or not player.footprints:
        return

    for pos in player.footprints:
        # Tính toán vị trí để vẽ dấu chân ở giữa ô
        pos_x = pos[0] * config.CELL_SIZE + (config.CELL_SIZE - footprint_img.get_width()) / 2
        pos_y = pos[1] * config.CELL_SIZE + (config.CELL_SIZE - footprint_img.get_height()) / 2
        
        screen.blit(footprint_img, (pos_x, pos_y))

# trong file main.py

def update_path_validity():

    global is_path_blocked, path_warning_timer, reachable_tiles_from_player
    if not player or not tiles:
        return

    # Reset lại tập hợp
    reachable_tiles_from_player.clear()
    
    # Sử dụng BFS để thực hiện flood-fill
    queue = deque([player.get_tile_position()])
    visited = {player.get_tile_position()}
    
    rows, cols = len(tiles), len(tiles[0])

    while queue:
        current = queue.popleft()
        reachable_tiles_from_player.add(current)
        
        x, y = current
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            if (0 <= neighbor[1] < rows and 0 <= neighbor[0] < cols and 
                tiles[neighbor[1]][neighbor[0]] == 0 and neighbor not in visited):
                visited.add(neighbor)
                queue.append(neighbor)

    # Kiểm tra xem lối ra có nằm trong các ô có thể đến không
    exit_pos = (EXIT_TILE_X, EXIT_TILE_Y + 1)
    if exit_pos not in reachable_tiles_from_player:
        # Nếu đường đi vừa bị chặn, bắt đầu đếm giờ
        if not is_path_blocked: 
            path_warning_timer = pygame.time.get_ticks()
        is_path_blocked = True
    else:
        is_path_blocked = False

def draw_blocked_path_warning(screen):
    """Vẽ cảnh báo và tô đỏ toàn bộ khu vực bị chặn."""
    WARNING_DURATION = 2500 # Thời gian hiển thị text cảnh báo

    if is_path_blocked:
        # --- Vẽ text cảnh báo ở trên ---
        if pygame.time.get_ticks() - path_warning_timer < WARNING_DURATION:
            font = pygame.font.SysFont('Arial', 24, bold=True)
            text_surf = font.render("WARNING: Path to exit is blocked!", True, (255, 255, 255))
            panel_rect = text_surf.get_rect(center=(screen.get_width() / 2, 30))
            panel_rect.inflate_ip(20, 10)
            panel_surf = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
            panel_surf.fill((200, 0, 0, 180))
            screen.blit(panel_surf, panel_rect)
            screen.blit(text_surf, text_surf.get_rect(center=panel_rect.center))

        # --- Tô đỏ toàn bộ khu vực không thể tiếp cận ---
        rows, cols = len(tiles), len(tiles[0])
        highlight_surf = pygame.Surface((config.CELL_SIZE, config.CELL_SIZE), pygame.SRCALPHA)
        
        # Tạo hiệu ứng nhấp nháy cho màu highlight
        alpha = 100 + 60 * math.sin(pygame.time.get_ticks() * 0.005)
        highlight_surf.fill((255, 0, 0, alpha))

        for y in range(rows):
            for x in range(cols):
                # Nếu là ô đi được NHƯNG không nằm trong danh sách có thể đến
                if tiles[y][x] == 0 and (x, y) not in reachable_tiles_from_player:
                    screen.blit(highlight_surf, (x * config.CELL_SIZE, y * config.CELL_SIZE))
                    
# =======================================================================================
# LOGIC CHÍNH CỦA GAME
# =======================================================================================

def setup_new_game(tiles_data, difficulty_name, algorithm_name, map_idx, screen):
    """Khởi tạo hoặc reset các đối tượng cho một màn chơi mới."""
    global player, guard_manager, SELECTED_DIFFICULTY, in_game_menu, current_map_index, tiles
    tiles = tiles_data
    SELECTED_DIFFICULTY = difficulty_name
    current_map_index = map_idx
    player = Player(1, 1, tiles, algorithm_name=algorithm_name)
    guard_manager = GuardManager(tiles, difficulty=difficulty_name)
    guard_manager.spawn_guards()
    in_game_menu = InGameMenu(screen)

def run_game_loop(screen):
    """Vòng lặp chính xử lý logic khi đang trong màn chơi."""
    global GAME_STATE, STATS_PANEL_VISIBLE, tiles, GUARDS_VISIBLE
    running = True
    clock = pygame.time.Clock()
    last_edited_tile = None

    while running:
        clock.tick(config.FPS)
        
        # --- XỬ LÝ SỰ KIỆN (INPUT) ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    last_edited_tile = None
            
            if GAME_STATE == REPLAY_SELECT_STATE:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    algo_buttons = draw_replay_menu(screen)
                    for algo_name, rect in algo_buttons.items():
                        if rect.collidepoint(event.pos):
                            setup_new_game(current_maze_tiles, SELECTED_DIFFICULTY, algo_name, current_map_index, screen)
                            GAME_STATE = "GAME"
                            break
                continue

            if GAME_STATE in [WIN_STATE, LOSE_STATE]:
                if player and player.pathfinding_stats:
                    is_duplicate = any(p_stat['name'] == player.pathfinding_stats['name'] for p_stat in replay_stats_history)
                    if not is_duplicate:
                        replay_stats_history.append(player.pathfinding_stats)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if STATS_PANEL_VISIBLE:
                        close_rect = draw_stats_panel(screen, replay_stats_history)
                        if close_rect.collidepoint(event.pos):
                            STATS_PANEL_VISIBLE = False
                    else:
                        if GAME_STATE == WIN_STATE:
                            menu_rect = draw_win_screen(screen)
                        else:
                            menu_rect = draw_game_end_screen(screen, "YOU WERE CAUGHT!", (255, 50, 50))
                        
                        draw_stats_button(screen)
                        draw_replay_button(screen)
                        
                        if STATS_BUTTON_RECT and STATS_BUTTON_RECT.collidepoint(event.pos):
                            STATS_PANEL_VISIBLE = True
                        elif REPLAY_BUTTON_RECT and REPLAY_BUTTON_RECT.collidepoint(event.pos):
                            GAME_STATE = REPLAY_SELECT_STATE
                        elif menu_rect.collidepoint(event.pos):
                            STATS_PANEL_VISIBLE = False
                            return "BACK_TO_MENU"
                continue
            
            if event.type == pygame.KEYDOWN:
                if event.key == EDIT_TOGGLE_KEY:
                    GAME_STATE = EDIT_STATE if GAME_STATE == "GAME" else "GAME"
                if event.key == pygame.K_ESCAPE:
                    GAME_STATE = "PAUSED" if GAME_STATE == "GAME" else "GAME"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if GAME_STATE == "GAME":
                    if GEAR_RECT and GEAR_RECT.collidepoint(event.pos): GAME_STATE = "PAUSED"
                    elif EDIT_BUTTON_RECT and EDIT_BUTTON_RECT.collidepoint(event.pos): GAME_STATE = EDIT_STATE
                    elif HIDE_GUARDS_BUTTON_RECT and HIDE_GUARDS_BUTTON_RECT.collidepoint(event.pos): GUARDS_VISIBLE = not GUARDS_VISIBLE
                    elif AI_BUTTON_RECT and AI_BUTTON_RECT.collidepoint(event.pos):
                        if player: player.ai_mode = not player.ai_mode
                elif GAME_STATE == EDIT_STATE:
                    if EXIT_EDIT_BUTTON_RECT and EXIT_EDIT_BUTTON_RECT.collidepoint(event.pos):
                        GAME_STATE = "GAME"
                    else:
                        mx, my = pygame.mouse.get_pos()
                        tile_x, tile_y = mx // config.CELL_SIZE, my // config.CELL_SIZE
                        if 0 <= tile_y < len(tiles) and 0 <= tile_x < len(tiles[0]):
                            if (tile_x, tile_y) not in [(1,1), (EXIT_TILE_X, EXIT_TILE_Y), (EXIT_TILE_X, EXIT_TILE_Y + 1)]:
                                tiles[tile_y][tile_x] = 1 - tiles[tile_y][tile_x]
                                invalidate_all_ai_paths()
                                update_path_validity()
                                last_edited_tile = (tile_x, tile_y)

            if GAME_STATE == "PAUSED":
                action = in_game_menu.handle_input(event)
                if action == "RESUME":
                    GAME_STATE = "GAME"
                elif action == "BACK_TO_MENU":
                    return "BACK_TO_MENU"
            
            if GAME_STATE == "GAME" and player and not player.ai_mode:
                player.handle_input()
        
        if GAME_STATE == EDIT_STATE:
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:
                mx, my = pygame.mouse.get_pos()
                tile_x, tile_y = mx // config.CELL_SIZE, my // config.CELL_SIZE
                current_tile = (tile_x, tile_y)
                if current_tile != last_edited_tile:
                    if 0 <= tile_y < len(tiles) and 0 <= tile_x < len(tiles[0]):
                        if current_tile not in [(1,1), (EXIT_TILE_X, EXIT_TILE_Y), (EXIT_TILE_X, EXIT_TILE_Y + 1)]:
                            tiles[tile_y][tile_x] = 1 - tiles[tile_y][tile_x]
                            invalidate_all_ai_paths()
                            update_path_validity()
                            last_edited_tile = current_tile

        # --- CẬP NHẬT LOGIC GAME ---
        if GAME_STATE == "GAME":
            guard_list = guard_manager.guards if GUARDS_VISIBLE else []
            if player.ai_mode:
                player.handle_ai_move(tiles, (EXIT_TILE_X, EXIT_TILE_Y + 1), guard_list)
            
            if GUARDS_VISIBLE:
                guard_manager.update(player)
                for guard in guard_list:
                    if player.check_collision_with_guard(guard):
                        GAME_STATE = LOSE_STATE
                        break
            
            player_tile_x = int(round(player.x))
            player_tile_y = int(round(player.y))
            if player_tile_x == EXIT_TILE_X and player_tile_y == (EXIT_TILE_Y + 1):
                GAME_STATE = WIN_STATE

        # --- VẼ MỌI THỨ LÊN MÀN HÌNH ---
        screen.blit(game_assets['backgrounds'][current_map_index], (0, 0))
        render_maze(screen, tiles, game_assets['maps'][current_map_index])
        
        if player:
            draw_footprints(screen, player, game_assets['footprint'])

        screen.blit(game_assets['in'], (1 * config.CELL_SIZE, 0))
        screen.blit(game_assets['out'], (EXIT_TILE_X * config.CELL_SIZE, (EXIT_TILE_Y + 1) * config.CELL_SIZE))
        
        if GUARDS_VISIBLE and guard_manager:
            guard_manager.draw(screen)
        if player:
            player.draw(screen)
        
        # Vẽ các lớp phủ và UI theo trạng thái game
        if GAME_STATE == "GAME":
            draw_gear_button(screen)
            draw_edit_button(screen)
            draw_hide_guards_button(screen)
            draw_ai_button(screen)
        elif GAME_STATE == "PAUSED":
            draw_pause_menu(screen, in_game_menu)
        elif GAME_STATE == EDIT_STATE:
            draw_edit_mode_overlay(screen)
            draw_blocked_path_warning(screen)
        elif GAME_STATE in [WIN_STATE, LOSE_STATE]:
            message = "ESCAPE SUCCESS!" if GAME_STATE == WIN_STATE else "YOU WERE CAUGHT!"
            color = (50, 255, 50) if GAME_STATE == WIN_STATE else (255, 50, 50)
            
            if not STATS_PANEL_VISIBLE:
                draw_game_end_screen(screen, message, color)
                draw_stats_button(screen)
                draw_replay_button(screen)
            else:
                draw_stats_panel(screen, replay_stats_history)
        
        elif GAME_STATE == REPLAY_SELECT_STATE:
            draw_replay_menu(screen)

        pygame.display.flip()
        
    return "QUIT"

def main():
    """Hàm chính, khởi tạo Pygame và quản lý vòng lặp chính."""
    global GAME_STATE, STATS_PANEL_VISIBLE, current_maze_tiles, replay_stats_history
    pygame.init()
    pygame.key.set_repeat(100, 50)
    
    # Tạo mê cung ban đầu để xác định kích thước màn hình
    grid = generate_maze(config.MAZE_COLS, config.MAZE_ROWS)
    initial_tiles = maze_to_tiles(grid, config.MAZE_COLS, config.MAZE_ROWS)
    screen_w = len(initial_tiles[0]) * config.CELL_SIZE
    screen_h = len(initial_tiles) * config.CELL_SIZE
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
                action, difficulty, algorithm, map_idx = menu.handle_input(event)
                if action == "PLAY":
                    replay_stats_history.clear() # Xóa lịch sử so sánh khi bắt đầu game mới
                    new_grid = generate_maze(config.MAZE_COLS, config.MAZE_ROWS)
                    new_tiles = maze_to_tiles(new_grid, config.MAZE_COLS, config.MAZE_ROWS)
                    if (EXIT_TILE_Y + 1) < len(new_tiles):
                        new_tiles[EXIT_TILE_Y + 1][EXIT_TILE_X] = 0
                    current_maze_tiles = [row[:] for row in new_tiles] # Lưu lại mê cung để chơi lại
                    setup_new_game(new_tiles, difficulty, algorithm, map_idx, screen)
                    GAME_STATE = "GAME"
                elif action == "QUIT":
                    running = False

        if GAME_STATE == "MENU":
            menu.draw()
        else:
            result = run_game_loop(screen)
            if result == "QUIT":
                running = False
            elif result == "BACK_TO_MENU":
                GAME_STATE = "MENU"
                STATS_PANEL_VISIBLE = False
        
        pygame.display.flip()
        
    pygame.quit()

if __name__ == "__main__":
    main()