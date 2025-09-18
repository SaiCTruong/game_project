# Main.py
import pygame
import time
import os
from Maze import Maze
from ControlPanel import ControlPanel
from AI import Player, Chaser
from Algorithms import ALGO_MAP
import random
from pygame.locals import *

def spawn_chasers(maze, num, algo_name, detection_radius=8):
    chasers = []
    for _ in range(num):
        c = Chaser(maze, algo_name=algo_name, detection_radius=detection_radius)
        chasers.append(c)
    return chasers

def main():
    pygame.init()
    width, height = 1000, 500
    screen = pygame.display.set_mode((width, height))
    pygame.mixer.init()

    current_dir = os.path.dirname(__file__)
    music_dir = os.path.join(current_dir, "..", "Music")
    picture_dir = os.path.join(current_dir, "..", "Picture")

    # initial music
    try:
        pygame.mixer.music.load(os.path.join(music_dir, "nhac.mp3"))
        pygame.mixer.music.set_volume(0.5)
    except Exception:
        pass

    # initial config
    control_panel = ControlPanel(300, 500)
    maze = Maze(control_panel.maze_width, control_panel.maze_height)
    player = Player(maze)
    chasers = spawn_chasers(maze, control_panel.num_chasers, control_panel.selected_algo, detection_radius=8)

    auto_play = False
    shortest_path = None
    start_time = None
    countdown_time = 120
    running = True
    game_over = False
    maze_completed = False

    cell_size = 20

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            else:
                actions = control_panel.handle_event(event)
                if actions:
                    # handle returned actions
                    if "algo" in actions:
                        for ch in chasers:
                            ch.update_algorithm(actions["algo"])
                    if "num_chasers" in actions:
                        # respawn chasers to match number
                        chasers = spawn_chasers(maze, actions["num_chasers"], control_panel.selected_algo, detection_radius=8)
                    if "maze_size" in actions:
                        w, h = actions["maze_size"]
                        maze = Maze(w, h)
                        player = Player(maze)
                        chasers = spawn_chasers(maze, control_panel.num_chasers, control_panel.selected_algo, detection_radius=8)
                    if "reset_btn" in actions:
                        maze = Maze(control_panel.maze_width, control_panel.maze_height)
                        player = Player(maze)
                        chasers = spawn_chasers(maze, control_panel.num_chasers, control_panel.selected_algo, detection_radius=8)
                        start_time = None
                        game_over = False
                    if "exit_btn" in actions:
                        running = False
                    if "auto_play_btn" in actions:
                        # start timer, but in escape game auto_play irrelevant — we keep for compatibility
                        start_time = time.time()
                    if "ai_play_btn" in actions:
                        # for compatibility: spawn chasers and start timer
                        start_time = time.time()

            # Player movement via keys
            if event.type == KEYDOWN:
                if event.key == K_UP:
                    player.move(0, -1)
                elif event.key == K_DOWN:
                    player.move(0, 1)
                elif event.key == K_LEFT:
                    player.move(-1, 0)
                elif event.key == K_RIGHT:
                    player.move(1, 0)

        # update chasers each tick
        for ch in chasers:
            ch.tick(player)
            # if chaser catches player -> game over
            if (ch.x, ch.y) == (player.x, player.y):
                game_over = True

        # draw
        screen.fill((0,0,0))
        maze.display_maze(screen, player if hasattr(player, 'path') else None)
        # draw player icon
        try:
            player_img = pygame.image.load(os.path.join(picture_dir, "icon.png"))
            player_img = pygame.transform.scale(player_img, (cell_size, cell_size))
            screen.blit(player_img, (player.x * cell_size, player.y * cell_size))
        except Exception:
            pygame.draw.rect(screen, (0, 0, 200), (player.x * cell_size, player.y * cell_size, cell_size, cell_size))

        # draw chasers
        for c in chasers:
            c.draw(screen, cell_size)
            # optionally draw detection radius (semi-transparent circle)
            # translate grid coords -> pixel
            try:
                s = pygame.Surface((cell_size* (2*c.detection_radius+1), cell_size*(2*c.detection_radius+1)), pygame.SRCALPHA)
                s.fill((0,0,0,0))
                pygame.draw.circle(s, (255,0,0,30), (s.get_width()//2, s.get_height()//2), cell_size*c.detection_radius)
                screen.blit(s, ((c.x - c.detection_radius) * cell_size, (c.y - c.detection_radius) * cell_size))
            except Exception:
                pass

        control_panel.display(screen)

        # HUD: instructions
        font = pygame.font.Font(None, 24)
        txt = font.render("Use arrows to move. Avoid red chasers!", True, (255,255,255))
        screen.blit(txt, (10, height - 30))

        if game_over:
            font2 = pygame.font.Font(None, 72)
            text = font2.render("CAUGHT! Game Over", True, (255, 0, 0))
            rect = text.get_rect(center=(width//2, height//2))
            screen.blit(text, rect)

        pygame.display.flip()
        pygame.time.delay(120)

    pygame.quit()

if __name__ == "__main__":
    main()
