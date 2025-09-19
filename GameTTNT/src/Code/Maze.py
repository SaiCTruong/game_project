# Maze.py
import pygame
import random
class Maze:
    def __init__(self, width, height):
        # Các thuộc tính của lớp Maze
        self.width = width
        self.height = height
        self.grid = [[1] * width for _ in range(height)]  
        self.start_x, self.start_y = 1, 1
        self.end_x, self.end_y = width - 2, height - 2
        self.generate_maze()
        self.grid[self.start_y][self.start_x] = 0  
        self.grid[self.end_y][self.end_x] = 0  
        self.path = []  # Khởi tạo danh sách các bước trong đường đi
        # Thêm chướng ngại vật hố sâu
        self.obstacles = set()  # Danh sách các chướng ngại vật
        self.create_obstacles()  # Tạo chướng ngại vật hố sâu
        self.obstacle_image = pygame.image.load(r"D:\game1\GameTTNT\src\Picture\iconbom.png")
        # Thay đổi kích thước của hình ảnh chướng ngại vật để phù hợp với kích thước ô trong mê cung
        cell_size = 20  # Kích thước của mỗi ô trong mê cung
        self.obstacle_image = pygame.transform.scale(self.obstacle_image, (cell_size, cell_size))  # Đổi kích thước của hình ảnh
        self.reward_image = pygame.image.load(r"D:\game1\GameTTNT\src\Picture\selectbackground.jpg")
        self.rewards = set()  # Danh sách các phần thưởng
        self.create_rewards()  # Tạo phần thưởng
    # Tạo 10 chướng ngại vật
    def create_rewards(self):
        reward_count = 0
        while reward_count < 10:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            if self.grid[y][x] == 0 and (x, y) not in self.rewards and not self.has_adjacent_reward(x, y):
                self.rewards.add((x, y))
                reward_count += 1

    def has_adjacent_reward(self, x, y):
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                if (dx != 0 or dy != 0) and (x + dx, y + dy) in self.rewards:
                    return True
        return False
    
    def create_obstacles(self):
        # Tạo 20 chướng ngại vật nằm trong tường màu xanh
        obstacle_count = 0  # Đếm số lượng chướng ngại vật đã được tạo
        while obstacle_count < 20:  # Tạo chướng ngại vật cho đến khi đủ 20
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            # Kiểm tra xem ô tại vị trí (x, y) có đủ xa so với các chướng ngại vật hiện có không
            if self.grid[y][x] == 1 and (x, y) != (self.start_x, self.start_y) and (x, y) != (self.end_x, self.end_y) and self.is_far_from_obstacles(x, y):
                self.obstacles.add((x, y))
                obstacle_count += 1  # Tăng biến đếm lên 1 khi tạo thành công một chướng ngại

    def is_far_from_obstacles(self, x, y):
        min_distance = 5  # Khoảng cách tối thiểu giữa các chướng ngại vật
        for obstacle in self.obstacles:
            obstacle_x, obstacle_y = obstacle
            # Tính khoảng cách Manhattan giữa ô (x, y) và các chướng ngại vật hiện có
            distance = abs(x - obstacle_x) + abs(y - obstacle_y)
            if distance < min_distance:
                return False  # Nếu ô (x, y) quá gần một chướng ngại vật, trả về False
        return True  # Nếu không gần chướng ngại vật nào, trả về True
    def generate_maze(self):
        for x in range(self.width):
            self.grid[0][x] = 1
            self.grid[self.height - 1][x] = 1
        for y in range(self.height):
            self.grid[y][0] = 1
            self.grid[y][self.width - 1] = 1
        
        stack = [(1, 1)]
        while stack:
            x, y = stack[-1]
            neighbors = [(x + dx, y + dy) for dx, dy in [(0, -2), (0, 2), (-2, 0), (2, 0)] if 0 < x + dx < self.width - 1 and 0 < y + dy < self.height - 1]
            unvisited_neighbors = [neighbor for neighbor in neighbors if self.grid[neighbor[1]][neighbor[0]] == 1]
            if unvisited_neighbors:
                nx, ny = random.choice(unvisited_neighbors)
                self.grid[ny][nx] = 0
                self.grid[y + (ny - y) // 2][x + (nx - x) // 2] = 0
                stack.append((nx, ny))
            else:
                stack.pop()
 
    def display_maze(self, screen, ai):
        cell_size = 20
        obstacle_image = pygame.image.load(r"D:\game1\GameTTNT\src\Picture\hangrao.jpg")
        obstacle_image = pygame.transform.scale(obstacle_image, (cell_size, cell_size))
        end_image = pygame.image.load(r"D:\game1\GameTTNT\src\Picture\dautay.jpg")
        end_image = pygame.transform.scale(end_image, (cell_size, cell_size))
        reward_image = pygame.image.load(r"D:\game1\GameTTNT\src\Picture\phanthuong.jpg")
        reward_image = pygame.transform.scale(reward_image, (cell_size, cell_size))

        # Vẽ mê cung trên màn hình
        for y in range(self.height):
            for x in range(self.width):
                # Vẽ ô bắt đầu
                if (x, y) == (self.start_x, self.start_y):
                    pygame.draw.rect(screen, (0, 0, 0), (x * cell_size, y * cell_size, cell_size, cell_size))
                # Vẽ ô kết thúc
                elif (x, y) == (self.end_x, self.end_y):
                    screen.blit(end_image, (x * cell_size, y * cell_size))
                # Vẽ đường đi của người chơi
                elif (x, y) in self.path:
                    pygame.draw.rect(screen, (255, 0, 0), (x * cell_size, y * cell_size, cell_size, cell_size))
                # Vẽ đường đi của AI
                elif (x, y) in ai.path:
                    pygame.draw.rect(screen, (255, 0, 0), (x * cell_size, y * cell_size, cell_size, cell_size))
                # Vẽ các chướng ngại vật
                elif (x, y) in self.obstacles:
                    screen.blit(obstacle_image, (x * cell_size, y * cell_size))
                # Vẽ các phần thưởng
                elif (x, y) in self.rewards:
                    screen.blit(reward_image, (x * cell_size, y * cell_size))
                # Vẽ các ô trống
                elif self.grid[y][x] == 1:
                    screen.blit(obstacle_image, (x * cell_size, y * cell_size))
                else:
                    pygame.draw.rect(screen, (255, 255, 255), (x * cell_size, y * cell_size, cell_size, cell_size))
        # Vẽ chướng ngại vật hố sâu
        for obstacle in self.obstacles:
            x, y = obstacle
            # Trong phương thức display_maze của lớp Maze, thay thế dòng vẽ hình ảnh chướng ngại vật
            pygame.draw.circle(screen, (255, 165, 0), (x * cell_size + cell_size // 2, y * cell_size + cell_size // 2), cell_size // 3)
            # bằng
            screen.blit(self.obstacle_image, (x * cell_size, y * cell_size))
        
        # Vẽ đường đã đi qua thành màu vàng
        path_color = (148, 0, 211)  # Màu vàng cho đường đã đi qua
        if ai.x == self.end_x and ai.y == self.end_y:  # Kiểm tra xem con AI đã đến điểm cuối chưa
            for step in ai.path:  # Vẽ màu vàng trên tất cả các ô đã đi qua của con AI
                x, y = step
                pygame.draw.rect(screen, path_color, (x * cell_size, y * cell_size, cell_size, cell_size))
        else:  # Nếu chưa đến điểm cuối, vẽ đường đã đi qua như bình thường
            for step in self.path:
                x, y = step
                pygame.draw.rect(screen, path_color, (x * cell_size, y * cell_size, cell_size, cell_size))

    
    def get_neighbors(self, x, y):
            neighbors = []
            # Duyệt qua các hướng lân cận của ô hiện tại
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                # Kiểm tra xem ô lân cận có nằm trong phạm vi của mê cung và không phải là ô chướng ngại vật
                if 0 <= nx < self.width and 0 <= ny < self.height and self.grid[ny][nx] == 0:
                    # Nếu thỏa mãn điều kiện, thêm ô vào danh sách các ô lân cận
                    neighbors.append((nx, ny))
            return neighbors