# game/config.py

MAZE_COLS = 20
MAZE_ROWS = 11
CELL_SIZE = 32
FPS = 60

# <<< THÊM DANH SÁCH CÁC THEME MAP Ở ĐÂY >>>
# Tên phải khớp với tên file ảnh (ví dụ: wooden.png, bg_wooden.png)
MAP_THEMES = ["wooden", "wall", "ice", "tree_wooden"]

# --- CẤU HÌNH ĐỊA HÌNH VÀ CHI PHÍ DI CHUYỂN ---
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
        "DISPLAY_NAME": "EXPERT (4 Guards, Max Speed)",
        "GUARD_COUNT": 4,
        "ALGORITHM_MODE": "A_STAR", 
        "CHASE_SPEED": 4,
        "DETECT_RADIUS": 6
    },
}
DIFFICULTY_LEVELS = list(DIFFICULTY_SETTINGS.keys())