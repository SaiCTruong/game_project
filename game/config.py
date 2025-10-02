# game/config.py

MAZE_COLS = 20
MAZE_ROWS = 11
CELL_SIZE = 32
FPS = 60

# --- CẤU HÌNH ĐỊA HÌNH VÀ CHI PHÍ DI CHUYỂN ---
# 0: Đường đi bình thường (cost 1)
# 1: Tường (không thể đi qua)
# 2: Bùn (đi chậm, cost 5)
# 3: Nước (đi rất chậm, cost 10)
TERRAIN_COSTS = {
    0: 1,
    2: 5,
    3: 10,
}

# --- CẤU HÌNH ĐỘ KHÓ CỦA GUARD ---
DIFFICULTY_SETTINGS = {
    "EASY": {
        "DISPLAY_NAME": "EASY (1 Guard)",
        "GUARD_COUNT": 1,
        "ALGORITHM_MODE": "UCS", 
        "CHASE_SPEED": 2,
        "DETECT_RADIUS": 4
    },
    "NORMAL": {
        "DISPLAY_NAME": "NORMAL (2 Guards)",
        "GUARD_COUNT": 2,
        "ALGORITHM_MODE": "UCS", 
        "CHASE_SPEED": 3,
        "DETECT_RADIUS": 5
    },
    "HARD": {
        "DISPLAY_NAME": "HARD (3 Guards, A*)",
        "GUARD_COUNT": 3,
        "ALGORITHM_MODE": "A_STAR", 
        "CHASE_SPEED": 3,
        "DETECT_RADIUS": 5
    },
    "EXPERT": {
        "DISPLAY_NAME": "EXPERT (2 Guards, Max Speed)",
        "GUARD_COUNT": 2,
        "ALGORITHM_MODE": "A_STAR", 
        "CHASE_SPEED": 4,
        "DETECT_RADIUS": 6
    },
}
DIFFICULTY_LEVELS = list(DIFFICULTY_SETTINGS.keys())