# game/config.py

# ... (Cấu hình FPS, kích thước ô, v.v. giữ nguyên) ...
MAZE_COLS = 22
MAZE_ROWS = 11
CELL_SIZE = 32
FPS = 60

# --- CẤU HÌNH ĐỘ KHÓ CỦA GUARD ---

# Định nghĩa các thông số kỹ thuật cho thuật toán
# Lưu ý: "UCS" sẽ được triển khai bằng A* với h=0.
DIFFICULTY_SETTINGS = {
    "EASY": {
        "DISPLAY_NAME": "EASY (1 Guard)",
        "GUARD_COUNT": 1,
        "ALGORITHM_MODE": "UCS",         # A* với h=0 (tìm đường đi ngắn nhất, nhưng không có hướng)
        "CHASE_SPEED": 2,                # Tốc độ đuổi bắt thấp
        "DETECT_RADIUS": 4               # Bán kính phát hiện nhỏ
    },
    "NORMAL": {
        "DISPLAY_NAME": "NORMAL (2 Guards)",
        "GUARD_COUNT": 2,
        "ALGORITHM_MODE": "UCS",         # Vẫn là UCS/BFS để cân bằng tốc độ tìm kiếm
        "CHASE_SPEED": 3,
        "DETECT_RADIUS": 5
    },
    "HARD": {
        "DISPLAY_NAME": "HARD (3 Guards, A*)",
        "GUARD_COUNT": 3,
        "ALGORITHM_MODE": "A_STAR",       # A* với h=Manhattan (Tìm đường thông minh)
        "CHASE_SPEED": 3,
        "DETECT_RADIUS": 5
    },
    "EXPERT": {
        "DISPLAY_NAME": "VERY HARD (3 Guards, Max Speed)",
        "GUARD_COUNT": 3,
        "ALGORITHM_MODE": "A_STAR",       # A* với h=Manhattan (Tìm đường thông minh)
        "CHASE_SPEED": 5,                # Tốc độ cực cao
        "DETECT_RADIUS": 7               # Phạm vi phát hiện lớn
    },
}

# Danh sách các tên độ khó để hiển thị trong Menu
DIFFICULTY_LEVELS = list(DIFFICULTY_SETTINGS.keys())