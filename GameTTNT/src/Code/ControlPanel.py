import pygame
import os

class ControlPanel:
    def __init__(self, width, height):
        current_dir = os.path.dirname(__file__)
        picture_dir = os.path.join(current_dir, "..", "Picture")
        self.background_image = pygame.image.load(os.path.join(picture_dir, "selectbackground.jpg"))
        self.background_image = pygame.transform.scale(self.background_image, (300, 500))
        self.font = pygame.font.Font('freesansbold.ttf', 20)

        # Algorithm menu
        self.algo_list = ["BFS", "DFS", "IDS", "A*", "Greedy", "UCS"]
        self.selected_algo = "BFS"
        self.show_algo_menu = False

        # Difficulty
        self.num_chasers = 1
        self.maze_width = 35
        self.maze_height = 25

    def display(self, screen):
        x = 700
        screen.blit(self.background_image, (x, 0))
        text_color = (255, 255, 255)

        title = self.font.render("Control Panel", True, text_color)
        screen.blit(title, (x + 20, 10))

        # Algorithm dropdown
        algo_button = pygame.Rect(x+20, 50, 200, 30)
        pygame.draw.rect(screen, (0,153,204), algo_button)
        txt = self.font.render(f"Algorithm: {self.selected_algo}", True, (0,0,0))
        screen.blit(txt, (x+25, 55))

        if self.show_algo_menu:
            for i, name in enumerate(self.algo_list):
                opt_rect = pygame.Rect(x+20, 80+i*30, 200, 30)
                pygame.draw.rect(screen, (100,100,100), opt_rect)
                opt_txt = self.font.render(name, True, (255,255,255))
                screen.blit(opt_txt, (x+25, 85+i*30))

        # Number of chasers
        nch_txt = self.font.render(f"Chasers: {self.num_chasers}", True, text_color)
        screen.blit(nch_txt, (x + 20, 220))
        plus_rect = pygame.Rect(x+150, 220, 30, 30)
        minus_rect = pygame.Rect(x+190, 220, 30, 30)
        pygame.draw.rect(screen, (0,153,204), plus_rect)
        pygame.draw.rect(screen, (0,153,204), minus_rect)
        screen.blit(self.font.render("+", True, (0,0,0)), (x+158, 225))
        screen.blit(self.font.render("-", True, (0,0,0)), (x+198, 225))

        # Maze size
        size_txt = self.font.render(f"Maze: {self.maze_width}x{self.maze_height}", True, text_color)
        screen.blit(size_txt, (x+20, 270))
        plus2_rect = pygame.Rect(x+150, 270, 30, 30)
        minus2_rect = pygame.Rect(x+190, 270, 30, 30)
        pygame.draw.rect(screen, (0,153,204), plus2_rect)
        pygame.draw.rect(screen, (0,153,204), minus2_rect)
        screen.blit(self.font.render("+", True, (0,0,0)), (x+158, 275))
        screen.blit(self.font.render("-", True, (0,0,0)), (x+198, 275))

        # Reset & Exit
        reset_text = self.font.render("Reset Maze", True, text_color)
        exit_text = self.font.render("Exit", True, text_color)
        buttons = [
            (750, 340, 200, 40, reset_text, "reset_btn"),
            (750, 400, 200, 40, exit_text, "exit_btn"),
        ]
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for bx, by, bw, bh, text, action in buttons:
            color = (0,153,204)
            if bx < mouse_x < bx + bw and by < mouse_y < by + bh:
                color = (0,102,153)
            pygame.draw.rect(screen, color, (bx, by, bw, bh))
            pygame.draw.rect(screen, (255,255,255), (bx, by, bw, bh), 3)
            text_rect = text.get_rect(center=(bx + bw // 2, by + bh // 2))
            screen.blit(text, text_rect)

    def handle_event(self, event):
        actions = {}
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            x = 700
            # Algorithm button
            algo_button = pygame.Rect(x+20, 50, 200, 30)
            if algo_button.collidepoint((mx,my)):
                self.show_algo_menu = not self.show_algo_menu
                return actions
            if self.show_algo_menu:
                for i, name in enumerate(self.algo_list):
                    opt_rect = pygame.Rect(x+20, 80+i*30, 200, 30)
                    if opt_rect.collidepoint((mx,my)):
                        self.selected_algo = name
                        self.show_algo_menu = False
                        actions["algo"] = name
                        return actions

            # Chasers
            if pygame.Rect(x+150, 220, 30, 30).collidepoint((mx,my)):
                self.num_chasers = min(10, self.num_chasers+1)
                actions["num_chasers"] = self.num_chasers
                return actions
            if pygame.Rect(x+190, 220, 30, 30).collidepoint((mx,my)):
                self.num_chasers = max(0, self.num_chasers-1)
                actions["num_chasers"] = self.num_chasers
                return actions

            # Maze size
            if pygame.Rect(x+150, 270, 30, 30).collidepoint((mx,my)):
                self.maze_width = min(151, self.maze_width+4)
                self.maze_height = min(101, self.maze_height+4)
                actions["maze_size"] = (self.maze_width, self.maze_height)
                return actions
            if pygame.Rect(x+190, 270, 30, 30).collidepoint((mx,my)):
                self.maze_width = max(15, self.maze_width-4)
                self.maze_height = max(11, self.maze_height-4)
                actions["maze_size"] = (self.maze_width, self.maze_height)
                return actions

            # Reset & Exit
            if 750 <= mx <= 950 and 340 <= my <= 380:
                actions["reset_btn"] = True
                return actions
            if 750 <= mx <= 950 and 400 <= my <= 440:
                actions["exit_btn"] = True
                return actions
        return actions
