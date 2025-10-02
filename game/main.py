# game/main.py
import os, sys, pygame
from game import config
from game.maze.generator import generate_maze, maze_to_tiles
from game.render.renderer import render_maze
from game.entities.player import Player
from game.controllers.guard_manager import GuardManager
from game.render.menu import Menu
from game.render.in_game_menu import InGameMenu

GAME_STATE = "MENU"; PAUSE_STATE = "GAME"; WIN_STATE = "WIN"; LOSE_STATE = "LOSE"; EDIT_STATE = "EDIT_MODE"
SELECTED_DIFFICULTY = "NORMAL" 
player = None; guard_manager = None; in_game_menu = None; game_assets = {} 

# <<< THÊM BIẾN RECT CHO NÚT MỚI >>>
GEAR_SIZE = 30; GEAR_RECT = None 
EDIT_BUTTON_SIZE = 30; EDIT_BUTTON_RECT = None
HIDE_GUARDS_BUTTON_SIZE = 30; HIDE_GUARDS_BUTTON_RECT = None
EXIT_EDIT_BUTTON_RECT = None

# <<< THÊM BIẾN TRẠNG THÁI CHO LÍNH >>>
GUARDS_VISIBLE = True

AI_TOGGLE_KEY = pygame.K_f; EDIT_TOGGLE_KEY = pygame.K_e 
EXIT_TILE_X = (config.MAZE_COLS * 2) - 2 
EXIT_TILE_Y = (config.MAZE_ROWS * 2) - 1
tiles = None; current_map_index = 0

def invalidate_all_ai_paths():
    if player: player.ai_path, player.ai_path_index = [], 0
    if guard_manager:
        for guard in guard_manager.guards: guard.path, guard.path_index = [], 0
    print("AI paths invalidated.")

def draw_edit_mode_overlay(screen):
    # ...
    global EXIT_EDIT_BUTTON_RECT
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA); overlay.fill((255, 200, 0, 100)); screen.blit(overlay, (0, 0))
    font_large = pygame.font.SysFont('Arial', 30, bold=True); font_small = pygame.font.SysFont('Arial', 20)
    text = font_large.render("EDIT MODE", True, (0,0,0)); screen.blit(text, text.get_rect(center=(screen.get_width()//2, 30)))
    text2 = font_small.render("Click to toggle walls", True, (0,0,0)); screen.blit(text2, text2.get_rect(center=(screen.get_width()//2, 70)))
    btn_w, btn_h = 120, 50
    EXIT_EDIT_BUTTON_RECT = pygame.Rect((screen.get_width()-btn_w)//2, screen.get_height()-btn_h-20, btn_w, btn_h)
    pygame.draw.rect(screen, (50, 200, 50), EXIT_EDIT_BUTTON_RECT, border_radius=8)
    done_text = font_large.render("DONE", True, (255,255,255)); screen.blit(done_text, done_text.get_rect(center=EXIT_EDIT_BUTTON_RECT.center))

def load_image(path, size=None):
    if not os.path.exists(path): print(f"ERROR: File not found: {path}"); pygame.quit(); sys.exit(1)
    img = pygame.image.load(path).convert_alpha()
    if size: img = pygame.transform.scale(img, size)
    return img

def load_game_assets(screen):
    # ...
    global game_assets; size = (config.CELL_SIZE, config.CELL_SIZE)
    game_assets['maps'] = [load_image(f"game/assets/images/{n}.png", size) for n in ["wooden", "wall", "ice", "tree_wooden"]]
    game_assets['in'] = load_image("game/assets/images/in.png", size)
    game_assets['out'] = load_image("game/assets/images/out.png", size)
    screen_w, screen_h = screen.get_size()
    game_assets['backgrounds'] = [pygame.transform.scale(pygame.image.load(f"game/assets/images/bg_{n}.png").convert_alpha(), (screen_w, screen_h)) for n in ["wooden", "wall", "ice", "tree_wooden"]]

# <<< TẠO HÀM VẼ NÚT ẨN/HIỆN LÍNH >>>
def draw_hide_guards_button(screen):
    global HIDE_GUARDS_BUTTON_RECT
    screen_w, _ = screen.get_size(); margin = 10
    hide_button_x = screen_w - GEAR_SIZE - margin - EDIT_BUTTON_SIZE - margin - HIDE_GUARDS_BUTTON_SIZE - margin
    HIDE_GUARDS_BUTTON_RECT = pygame.Rect(hide_button_x, margin, HIDE_GUARDS_BUTTON_SIZE, HIDE_GUARDS_BUTTON_SIZE)
    color = (150, 150, 150) if GUARDS_VISIBLE else (80, 80, 80)
    pygame.draw.circle(screen, color, HIDE_GUARDS_BUTTON_RECT.center, HIDE_GUARDS_BUTTON_SIZE // 2, 0)
    pygame.draw.circle(screen, (50, 50, 50), HIDE_GUARDS_BUTTON_RECT.center, HIDE_GUARDS_BUTTON_SIZE // 2, 2)
    font = pygame.font.SysFont('Arial', 18, bold=True); text = font.render("G", True, (0, 0, 0))
    screen.blit(text, text.get_rect(center=HIDE_GUARDS_BUTTON_RECT.center))
    if not GUARDS_VISIBLE:
        pygame.draw.line(screen, (255, 0, 0), HIDE_GUARDS_BUTTON_RECT.topleft, HIDE_GUARDS_BUTTON_RECT.bottomright, 3)

def draw_edit_button(screen):
    # ...
    global EDIT_BUTTON_RECT; screen_w, _ = screen.get_size(); margin = 10
    edit_button_x = screen_w - GEAR_SIZE - margin - EDIT_BUTTON_SIZE - margin
    EDIT_BUTTON_RECT = pygame.Rect(edit_button_x, margin, EDIT_BUTTON_SIZE, EDIT_BUTTON_SIZE)
    pygame.draw.circle(screen, (150,150,150), EDIT_BUTTON_RECT.center, EDIT_BUTTON_SIZE//2, 0)
    pygame.draw.circle(screen, (50,50,50), EDIT_BUTTON_RECT.center, EDIT_BUTTON_SIZE//2, 2)
    font = pygame.font.SysFont('Arial', 18, bold=True); text = font.render("E", True, (0,0,0))
    screen.blit(text, text.get_rect(center=EDIT_BUTTON_RECT.center))

def draw_gear_button(screen):
    # ...
    global GEAR_RECT; screen_w, _ = screen.get_size(); margin = 10
    GEAR_RECT = pygame.Rect(screen_w - GEAR_SIZE - margin, margin, GEAR_SIZE, GEAR_SIZE)
    pygame.draw.circle(screen, (150,150,150), GEAR_RECT.center, GEAR_SIZE//2, 0)
    pygame.draw.circle(screen, (50,50,50), GEAR_RECT.center, GEAR_SIZE//2, 2)
    font = pygame.font.SysFont('Arial', 18, bold=True); text = font.render("II", True, (0,0,0))
    screen.blit(text, text.get_rect(center=GEAR_RECT.center))

def draw_pause_menu(screen, in_game_menu):
    # ...
    menu_rect = in_game_menu.menu_rect; buttons = in_game_menu.buttons
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA); overlay.fill((0,0,0,180)); screen.blit(overlay, (0,0))
    pygame.draw.rect(screen, (50,50,50), menu_rect, border_radius=10); pygame.draw.rect(screen, (255,255,255), menu_rect, 5, border_radius=10)
    font_title = in_game_menu.font_title; font_button = in_game_menu.font_button
    title_text = font_title.render("GAME PAUSED", True, (255,255,255)); title_rect = title_text.get_rect(center=(screen.get_width()//2, menu_rect.top+40)); screen.blit(title_text, title_rect)
    rect_r = buttons["RESUME"]; pygame.draw.rect(screen, (50,200,50), rect_r, border_radius=5)
    text_r = font_button.render("RESUME (ESC)", True, (0,0,0)); screen.blit(text_r, text_r.get_rect(center=rect_r.center))
    rect_m = buttons["TO_MENU"]; pygame.draw.rect(screen, (200,50,50), rect_m, border_radius=5)
    text_m = font_button.render("BACK TO MENU", True, (255,255,255)); screen.blit(text_m, text_m.get_rect(center=rect_m.center))

def draw_game_end_screen(screen, message, color):
    # ...
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA); overlay.fill((0,0,0,200)); screen.blit(overlay, (0,0))
    font_end = pygame.font.SysFont('Arial', 70, bold=True); font_small = pygame.font.SysFont('Arial', 40)
    title_text = font_end.render(message, True, color); title_rect = title_text.get_rect(center=(screen.get_width()//2, screen.get_height()//3)); screen.blit(title_text, title_rect)
    btn_w, btn_h = 300, 60; center_x = screen.get_width()//2
    menu_button_rect = pygame.Rect(center_x-(btn_w//2), screen.get_height()//2, btn_w, btn_h)
    is_hover = menu_button_rect.collidepoint(pygame.mouse.get_pos()); btn_color = (100,100,100) if is_hover else (50,50,50)
    pygame.draw.rect(screen, btn_color, menu_button_rect, border_radius=10)
    text = font_small.render("BACK TO MENU", True, (255,255,255)); screen.blit(text, text.get_rect(center=menu_button_rect.center))
    return menu_button_rect

def draw_win_screen(screen):
    # ...
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA); overlay.fill((0,0,0,200)); screen.blit(overlay, (0,0))
    font_end = pygame.font.SysFont('Arial', 70, bold=True); font_small = pygame.font.SysFont('Arial', 40)
    title_text = font_end.render("ESCAPE SUCCESS!", True, (50,255,50)); title_rect = title_text.get_rect(center=(screen.get_width()//2, screen.get_height()//3)); screen.blit(title_text, title_rect)
    subtext = font_small.render("Press ENTER to continue", True, (255,255,255)); subtext_rect = subtext.get_rect(center=(screen.get_width()//2, screen.get_height()//2)); screen.blit(subtext, subtext_rect)

def setup_new_game(tiles, difficulty_name, algorithm_name, screen):
    global player, guard_manager, SELECTED_DIFFICULTY, in_game_menu
    SELECTED_DIFFICULTY = difficulty_name
    player = Player(1, 1, tiles, algorithm_name=algorithm_name)
    guard_manager = GuardManager(tiles, difficulty=difficulty_name)
    guard_manager.spawn_guards()
    in_game_menu = InGameMenu(screen)

def run_game_loop(screen):
    global GAME_STATE, PAUSE_STATE, current_map_index, tiles, GUARDS_VISIBLE
    running = True; clock = pygame.time.Clock()
    
    while running:
        clock.tick(config.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            if GAME_STATE in [WIN_STATE, LOSE_STATE]:
                if event.type == pygame.MOUSEBUTTONDOWN and draw_game_end_screen(screen, "",(0,0,0)).collidepoint(event.pos): return "BACK_TO_MENU"
                if GAME_STATE == WIN_STATE and event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    current_map_index = (current_map_index+1) % len(game_assets['maps'])
                    grid = generate_maze(config.MAZE_COLS, config.MAZE_ROWS); tiles = maze_to_tiles(grid, config.MAZE_COLS, config.MAZE_ROWS)
                    setup_new_game(tiles, SELECTED_DIFFICULTY, player.algorithm_name, screen); GAME_STATE = "GAME"
                continue
            if event.type == pygame.KEYDOWN:
                if event.key == AI_TOGGLE_KEY: player.ai_mode = not player.ai_mode
                if event.key == EDIT_TOGGLE_KEY: GAME_STATE = EDIT_STATE if GAME_STATE == "GAME" else "GAME"
                if event.key == pygame.K_ESCAPE: GAME_STATE = "PAUSED" if GAME_STATE == "GAME" else "GAME"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if GAME_STATE == "GAME":
                    if GEAR_RECT and GEAR_RECT.collidepoint(event.pos): GAME_STATE = "PAUSED"
                    elif EDIT_BUTTON_RECT and EDIT_BUTTON_RECT.collidepoint(event.pos): GAME_STATE = EDIT_STATE
                    elif HIDE_GUARDS_BUTTON_RECT and HIDE_GUARDS_BUTTON_RECT.collidepoint(event.pos): GUARDS_VISIBLE = not GUARDS_VISIBLE
                elif GAME_STATE == EDIT_STATE:
                    if EXIT_EDIT_BUTTON_RECT and EXIT_EDIT_BUTTON_RECT.collidepoint(event.pos): GAME_STATE = "GAME"
                    else:
                        mx, my = pygame.mouse.get_pos(); tile_x, tile_y = mx//config.CELL_SIZE, my//config.CELL_SIZE
                        if 0 <= tile_y < len(tiles) and 0 <= tile_x < len(tiles[0]) and (tile_x, tile_y) not in [(1,1), (EXIT_TILE_X, EXIT_TILE_Y)]:
                            tiles[tile_y][tile_x] = 1 - tiles[tile_y][tile_x]; invalidate_all_ai_paths()
            if GAME_STATE == "PAUSED":
                action = in_game_menu.handle_input(event)
                if action == "RESUME": GAME_STATE = "GAME"
                elif action == "BACK_TO_MENU": return "BACK_TO_MENU"
            if GAME_STATE == "GAME" and not player.ai_mode: player.handle_input()

        if GAME_STATE == "GAME":
            guard_list = guard_manager.guards if GUARDS_VISIBLE else []
            if player.ai_mode:
                player.handle_ai_move(tiles, (EXIT_TILE_X, EXIT_TILE_Y), guard_list)
            if GUARDS_VISIBLE:
                guard_manager.update(player)
                for guard in guard_list:
                    if player.check_collision_with_guard(guard): GAME_STATE = LOSE_STATE; break
            
            player_rect = pygame.Rect(player.x*config.CELL_SIZE, player.y*config.CELL_SIZE, player.size, player.size)
            exit_rect = pygame.Rect(EXIT_TILE_X*config.CELL_SIZE, EXIT_TILE_Y*config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE)
            if player_rect.inflate(-player.size*0.5, -player.size*0.5).colliderect(exit_rect): GAME_STATE = WIN_STATE

        background_img = game_assets['backgrounds'][current_map_index]; screen.blit(background_img, (0, 0))
        render_maze(screen, tiles, game_assets['maps'][current_map_index])
        screen.blit(game_assets['in'], (1*config.CELL_SIZE, 0))
        screen.blit(game_assets['out'], (EXIT_TILE_X*config.CELL_SIZE, EXIT_TILE_Y*config.CELL_SIZE))
        if GUARDS_VISIBLE: guard_manager.draw(screen)
        player.draw(screen)
        
        if GAME_STATE == "GAME": draw_gear_button(screen); draw_edit_button(screen); draw_hide_guards_button(screen)
        elif GAME_STATE == "PAUSED": draw_pause_menu(screen, in_game_menu)
        elif GAME_STATE == EDIT_STATE: draw_edit_mode_overlay(screen)
        elif GAME_STATE == LOSE_STATE: draw_game_end_screen(screen, "YOU WERE CAUGHT!", (255, 50, 50))
        elif GAME_STATE == WIN_STATE: draw_win_screen(screen)
        pygame.display.flip()
    return "QUIT"

def main():
    global GAME_STATE, SELECTED_DIFFICULTY, tiles
    pygame.init(); pygame.key.set_repeat(100, 50)
    grid = generate_maze(config.MAZE_COLS, config.MAZE_ROWS); tiles = maze_to_tiles(grid, config.MAZE_COLS, config.MAZE_ROWS)
    screen_w, screen_h = len(tiles[0]) * config.CELL_SIZE, len(tiles) * config.CELL_SIZE
    screen = pygame.display.set_mode((screen_w, screen_h)); pygame.display.set_caption("Maze Escape")
    load_game_assets(screen); menu = Menu(screen); clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(config.FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if GAME_STATE == "MENU":
                action, difficulty, algorithm = menu.handle_input(event)
                if action == "PLAY":
                    setup_new_game(tiles, difficulty, algorithm, screen); GAME_STATE = "GAME"
                elif action == "QUIT": running = False
        if GAME_STATE == "MENU":
            menu.draw()
        else:
            result = run_game_loop(screen)
            if result == "QUIT": running = False
            elif result == "BACK_TO_MENU": GAME_STATE = "MENU"
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()