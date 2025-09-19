import pygame
from Maze import Maze
from pygame.locals import *
import time
from ControlPanel import ControlPanel
from AI import AI
from Algorithms import bfs, dfs, ucs, ids, astar, greedy, dijkstra

def main():
    pygame.init()
    width, height = 1000, 500
    screen = pygame.display.set_mode((width, height))
    pygame.mixer.init()

    # --- Load nhạc nền --- #
    pygame.mixer.music.load(r"D:\game1\GameTTNT\src\Music\nhac.mp3")
    pygame.mixer.music.set_volume(0.5)

    # --- Icon nhân vật --- #
    cell_size = 20
    player_image = pygame.image.load(r"D:\game1\GameTTNT\src\Picture\icon.png")
    player_image = pygame.transform.scale(player_image, (cell_size, cell_size))

    # --- Khởi tạo --- #
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

    # --- Thuật toán AI --- #
    ai_menu_open = False
    selected_algorithm = None
    algorithms = {
        "BFS": bfs,
        "DFS": dfs,
        "UCS": ucs,
        "IDS": ids,
        "A*": astar,
        "Greedy": greedy,
        "Dijkstra": dijkstra
    }

    font = pygame.font.Font(None, 28)

    while running:
        current_time = pygame.time.get_ticks()

        # Kiểm tra hoàn thành mê cung
        if ai.x == maze.end_x and ai.y == maze.end_y:
            maze_completed = True
            if not game_over:
                game_over_time = time.time()
                if start_time is not None:
                    total_time = game_over_time - start_time
                start_time = None
                game_over = True
                pygame.mixer.music.load(r"D:\game1\GameTTNT\src\Music\dendich.mp3")
                pygame.mixer.music.play()
                congrats_display_time = pygame.time.get_ticks()

        # --- Xử lý sự kiện --- #
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # --- Nút Auto Play --- #
                if 750 <= mouse_x <= 950 and 50 <= mouse_y <= 100:
                    auto_play = True
                    start_time = time.time()
                    pygame.mixer.music.load(r"D:\game1\GameTTNT\src\Music\nhac.mp3")
                    pygame.mixer.music.play()

                # --- Nút AI Play: mở/đóng menu --- #
                elif 750 <= mouse_x <= 950 and 150 <= mouse_y <= 200:
                    ai_menu_open = not ai_menu_open

                # --- Reset Maze --- #
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

                # --- Thoát game --- #
                elif 750 <= mouse_x <= 950 and 350 <= mouse_y <= 400:
                    running = False

                # --- Chọn thuật toán trong menu --- #
                if ai_menu_open:
                    algo_y_start = 200
                    for i, algo_name in enumerate(algorithms.keys()):
                        if 750 <= mouse_x <= 950 and algo_y_start + i * 40 <= mouse_y <= algo_y_start + (i + 1) * 40:
                            selected_algorithm = algo_name
                            auto_play = True
                            shortest_path = algorithms[algo_name](maze)
                            start_time = time.time()
                            pygame.mixer.music.load(r"D:\game1\GameTTNT\src\Music\nhac.mp3")
                            pygame.mixer.music.play()
                            ai_menu_open = False
                            break

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

            # --- ControlPanel xử lý thêm --- #
            maze, ai, _ = control_panel.handle_event(event, maze, ai)

        # --- Di chuyển liên tục khi giữ phím --- #
        maze, ai = control_panel.handle_continuous_movement(maze, ai)

        # --- Auto Play --- #
        if auto_play and shortest_path:
            if len(shortest_path) > 1:
                next_step = shortest_path.pop(1)
                ai.move_towards(next_step[0], next_step[1])

        # --- Rewards --- #
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

        # --- Vẽ màn hình --- #
        screen.fill((0, 0, 0))
        maze.display_maze(screen, ai)
        screen.blit(player_image, (ai.x * cell_size, ai.y * cell_size))  # icon nhân vật
        control_panel.display(screen)

        # --- Menu chọn thuật toán --- #
        if ai_menu_open:
            algo_y_start = 200
            for i, algo_name in enumerate(algorithms.keys()):
                rect = pygame.Rect(750, algo_y_start + i * 40, 200, 40)
                pygame.draw.rect(screen, (200, 200, 200), rect)
                text = font.render(algo_name, True, (0, 0, 0))
                screen.blit(text, (rect.x + 10, rect.y + 10))

        # --- Đếm ngược thời gian --- #
        if start_time and not game_over:
            elapsed_time = countdown_time - int(time.time() - start_time)
            elapsed_time = max(0, elapsed_time)
            time_text = font.render(f"TIME: {elapsed_time} S", True, (0, 0, 0))
            screen.blit(time_text, (width - 200, 10))

            if elapsed_time == 0 and not maze_completed:
                game_over = True
                game_over_time = time.time()
                game_over_display_time = pygame.time.get_ticks()
                pygame.mixer.music.load(r"D:\game1\GameTTNT\src\Music\gameover.mp3")
                pygame.mixer.music.play()

        # --- Chúc mừng --- #
        if congrats_display_time:
            elapsed_congrats_time = current_time - congrats_display_time
            if elapsed_congrats_time < 3000:
                pygame.draw.rect(screen, (0, 128, 0), (width//2 - 150, height//2 - 50, 300, 100))
                congrats_text = pygame.font.Font(None, 48).render("Congratulations!", True, (255, 255, 255))
                screen.blit(congrats_text, (width//2 - 100, height//2 - 20))
            else:
                congrats_display_time = None

        # --- Game Over --- #
        if game_over_display_time:
            elapsed_game_over_time = current_time - game_over_display_time
            if elapsed_game_over_time < 3000:
                pygame.draw.rect(screen, (128, 0, 0), (width//2 - 150, height//2 - 50, 300, 100))
                game_over_text = pygame.font.Font(None, 48).render("Game Over!", True, (255, 255, 255))
                screen.blit(game_over_text, (width//2 - 100, height//2 - 20))
            else:
                game_over_display_time = None

        pygame.display.flip()
        pygame.time.delay(100)

    pygame.quit()

if __name__ == "__main__":
    main()
