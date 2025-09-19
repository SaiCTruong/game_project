import pygame
from Maze import Maze
from pygame.locals import *
from queue import PriorityQueue
import time
from ControlPanel import ControlPanel
from AI import AI
from Algorithms import dijkstra, heuristic

def main():
    pygame.init()  # Khởi tạo pygame
    width, height = 1000, 500
    screen = pygame.display.set_mode((width, height))
    pygame.mixer.init()
    
    # --- Load nhạc --- #
    pygame.mixer.music.load(r"D:\game1\GameTTNT\src\Music\nhac.mp3")
    pygame.mixer.music.set_volume(0.5)
    
    # --- Load icon 1 lần ngoài vòng lặp --- #
    cell_size = 20
    player_image = pygame.image.load(r"D:\game1\GameTTNT\src\Picture\icon.png")
    player_image = pygame.transform.scale(player_image, (cell_size, cell_size))
    
    control_panel = ControlPanel(300, 500)
    maze = Maze(35, 25)
    ai = AI(maze)
    ai.maze = maze
    
    auto_play = False
    shortest_path = None
    start_time = None
    countdown_time = 59
    running = True
    game_over = False
    game_over_time = None
    maze_completed = False
    congrats_display_time = None
    game_over_display_time = None

    while running:
        current_time = pygame.time.get_ticks()
        
        # Kiểm tra hoàn thành maze
        if ai.x == maze.end_x and ai.y == maze.end_y:
            maze_completed = True
            if not game_over:
                game_over_time = time.time()
                game_over = True
                total_time = game_over_time - start_time
                start_time = None
                pygame.mixer.music.load(r"D:\game1\GameTTNT\src\Music\dendich.mp3")
                pygame.mixer.music.play()
                congrats_display_time = pygame.time.get_ticks()
        
        # --- Xử lý sự kiện --- #
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            
            elif event.type == MOUSEBUTTONDOWN:
                maze, ai = control_panel.handle_event(event, maze, ai)
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Auto Play
                if 750 <= mouse_x <= 950 and 50 <= mouse_y <= 100:
                    auto_play = True
                    start_time = time.time()
                    pygame.mixer.music.load(r"D:\game1\GameTTNT\src\Music\nhac.mp3")
                    pygame.mixer.music.play()
                
                # AI Play (Dijkstra)
                elif 750 <= mouse_x <= 950 and 150 <= mouse_y <= 200:
                    auto_play = True
                    shortest_path = dijkstra(maze)
                    start_time = time.time()
                    pygame.mixer.music.load(r"D:\game1\GameTTNT\src\Music\nhac.mp3")
                    pygame.mixer.music.play()
                
                # Reset Maze
                elif 750 <= mouse_x <= 950 and 250 <= mouse_y <= 300:
                    maze = Maze(35, 25)
                    ai = AI(maze)
                    ai.maze = maze
                    auto_play = False
                    shortest_path = None
                    start_time = None
                    game_over = False
                    game_over_time = None
                    pygame.mixer.music.stop()
                
                # Thoát game
                elif 750 <= mouse_x <= 950 and 350 <= mouse_y <= 400:
                    running = False
            
            elif event.type == KEYDOWN and auto_play:
                if not game_over:
                    if event.key == K_UP:
                        ai.move_towards(ai.x, ai.y - 1)
                    elif event.key == K_DOWN:
                        ai.move_towards(ai.x, ai.y + 1)
                    elif event.key == K_LEFT:
                        ai.move_towards(ai.x - 1, ai.y)
                    elif event.key == K_RIGHT:
                        ai.move_towards(ai.x + 1, ai.y)

            # --- Cho phép ControlPanel xử lý phím giữ/nhả ---
            maze, ai = control_panel.handle_event(event, maze, ai)

        # 🔑 GỌI HÀM LIÊN TỤC Ở ĐÂY (QUAN TRỌNG)
        maze, ai = control_panel.handle_continuous_movement(maze, ai)

        # --- Auto Play Dijkstra --- #
        if auto_play and shortest_path:
            if len(shortest_path) > 1:
                next_step = shortest_path.pop(1)
                ai.move_towards(next_step[0], next_step[1])
        
        # --- Xử lý rewards --- #
        rewards_to_remove = []
        play_reward_music = False
        for reward in maze.rewards:
            if (ai.x, ai.y) == reward:
                if start_time: start_time += 3
                rewards_to_remove.append(reward)
                play_reward_music = True
        for reward in rewards_to_remove:
            maze.rewards.remove(reward)
        if play_reward_music:
            pygame.mixer.music.load(r"D:\game1\GameTTNT\src\Music\trungthuong.mp3")
            pygame.mixer.music.play()
            pygame.mixer.music.set_endevent(pygame.USEREVENT)
            pygame.mixer.music.queue(r"D:\game1\GameTTNT\src\Music\nhac.mp3")
        
        # --- Hiển thị --- #
        screen.fill((0, 0, 0))
        maze.display_maze(screen, ai)
        screen.blit(player_image, (ai.x * cell_size, ai.y * cell_size))  # Vẽ icon
        control_panel.display(screen)
        
        # --- Đếm ngược thời gian --- #
        if start_time and not game_over:
            elapsed_time = countdown_time - int(time.time() - start_time)
            elapsed_time = max(0, elapsed_time)
            font = pygame.font.Font(None, 36)
            time_text = font.render(f"TIME: {elapsed_time} S", True, (0, 0, 0))
            text_rect = time_text.get_rect()
            text_rect.topright = (width - 100, 10)
            screen.blit(time_text, text_rect)
            
            if elapsed_time == 0 and not maze_completed:
                game_over = True
                game_over_time = time.time()
                game_over_display_time = pygame.time.get_ticks()
                pygame.mixer.music.load(r"D:\game1\GameTTNT\src\Music\gameover.mp3")
                pygame.mixer.music.play()
        
        # --- Thông báo Chúc mừng --- #
        if congrats_display_time:
            elapsed_congrats_time = current_time - congrats_display_time
            if elapsed_congrats_time < 3000:
                pygame.draw.rect(screen, (0, 128, 0), (width//2 -150, height//2 -50, 300, 100))
                font = pygame.font.Font(None, 48)
                congrats_text = font.render("Congratulations!", True, (255, 255, 255))
                text_rect = congrats_text.get_rect(center=(width//2, height//2))
                screen.blit(congrats_text, text_rect)
            else:
                congrats_display_time = None
        
        # --- Thông báo Game Over --- #
        if game_over_display_time:
            elapsed_game_over_time = current_time - game_over_display_time
            if elapsed_game_over_time < 3000:
                pygame.draw.rect(screen, (128, 0, 0), (width//2 -150, height//2 -50, 300, 100))
                font = pygame.font.Font(None, 48)
                game_over_text = font.render("Game Over!", True, (255, 255, 255))
                text_rect = game_over_text.get_rect(center=(width//2, height//2))
                screen.blit(game_over_text, text_rect)
            else:
                game_over_display_time = None
        
        pygame.display.flip()
        pygame.time.delay(100)
    
    pygame.quit()

if __name__ == "__main__":
    main()
