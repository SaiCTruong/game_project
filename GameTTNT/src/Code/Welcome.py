import pygame
import sys
import subprocess
import os
# Khởi tạo Pygame
pygame.init()
# Đường dẫn đến file nhạc   
music_path = r"D:\game1\GameTTNT\src\Music\nenstart.mp3"
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

# Định nghĩa biến start_button ở đây để trở thành biến toàn cục
start_button = pygame.Rect(300, 300, 200, 50)

def draw_start_screen():
    # Load hình nền
    background = pygame.image.load(r"D:\game1\GameTTNT\src\Picture\wellcome.jpg").convert()
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
        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Cập nhật trạng thái của trò chơi
        # Điều này bao gồm việc vẽ mê cung, xử lý di chuyển của nhân vật, xử lý va chạm, vv.

        # Vẽ màn hình
        screen.fill(WHITE)
        # Vẽ mê cung, nhân vật, vv. ở đây

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
                    # Chạy tệp main.py
                    main_py_path = os.path.join(os.path.dirname(__file__), "main.py")
                    subprocess.Popen(["python", "-u", main_py_path])
                    # Thoát khỏi tệp hiện tại
                    pygame.quit()
                    sys.exit()

        draw_start_screen()

    pygame.quit()

if __name__ == "__main__":
    main()
