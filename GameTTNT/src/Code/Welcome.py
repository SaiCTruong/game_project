import pygame
import sys
import subprocess
import os

# Khởi tạo Pygame
pygame.init()

# Lấy thư mục hiện tại (nơi chứa file Welcome.py)
current_dir = os.path.dirname(__file__)

# Đường dẫn file nhạc và ảnh
music_path = os.path.join(current_dir, "..", "Music", "nenstart.mp3")
image_path = os.path.join(current_dir, "..", "Picture", "wellcome.jpg")
main_py_path = os.path.join(current_dir, "Main.py")

# Kích thước màn hình
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("WELCOME THE MAZE GAME")

# Phát nhạc
pygame.mixer.music.load(music_path)
pygame.mixer.music.play()

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Font
font = pygame.font.SysFont(None, 36)

# Định nghĩa biến start_button
start_button = pygame.Rect(300, 300, 200, 50)

def draw_start_screen():
    # Load hình nền
    background = pygame.image.load(image_path).convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Vẽ hình nền
    screen.blit(background, (0, 0))
    
    # Vẽ văn bản và nút bắt đầu trên hình nền
    text = font.render("Welcome to the maze game", True, BLACK)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(text, text_rect)
    
    pygame.draw.rect(screen, BLACK, start_button)
    start_text = font.render("START", True, WHITE)
    start_text_rect = start_text.get_rect(center=start_button.center)
    screen.blit(start_text, start_text_rect)

    pygame.display.flip()

def main_game():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)
        pygame.display.flip()

def main():
    running = True
    game_started = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    subprocess.Popen(["python", "-u", main_py_path])
                    pygame.quit()
                    sys.exit()

        draw_start_screen()

    pygame.quit()

if __name__ == "__main__":
    main()
