import pygame  # thư viện xây dựng game
import sys  # thư viện để tương tác với hệ thống
import random  # thư viện sinh ra giá trị ngẫu nhiên

# BIẾN TOÀN CỤC
hint_used = 0  # số lượng gợi ý tối đa là 3 lần
MAX_HINTS = 3
game_won = False
wrong_attempts = 0  # số lượng lỗi sai tùy theo cấp độ
MAX_WRONG = {"easy": 5, "medium": 3, "hard": 3}

pygame.init()  # khởi tạo module
pygame.mixer.init()  # Khởi tạo module âm thanh

# Load nhạc
try:
    music_menu = pygame.mixer.Sound("assets/music1.mp3")
    music_game = pygame.mixer.Sound("assets/music2.mp3")
    music_menu.set_volume(0.5)
    music_game.set_volume(0.5)
    current_music = None
except:
    print("Could not load music files")

# Hàm quản lý nhạc
def play_music(new_music):
    global current_music
    if new_music != current_music:
        if current_music:
            current_music.stop()
        if new_music:
            new_music.play(-1)  # -1 để phát lặp vô hạn
        current_music = new_music

# CẤU HÌNH CƠ BẢN
game_state = "menu"
difficulty = None

# Kích thước cửa sổ
TOTAL_WIDTH, TOTAL_HEIGHT = 1000, 600

# Kích thước khu vực chơi Sudoku (phần bên trái)
GAME_WIDTH, GAME_HEIGHT = 600, 600
ROWS, COLS = 9, 9  # 9x9 ô
CELL_SIZE = GAME_WIDTH // COLS  # kt mỗi ô

# Màu
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (220, 220, 220)
# DARK_LINE = (52, 72, 97) # Định nghĩa lại bên dưới draw_button
LIGHT_RED = (255, 200, 200)
LIGHT_BLUE = (173, 216, 230)
HIGHLIGHT_COLOR = (255, 255, 153)
BUTTON_COLOR = (100, 200, 255)
BUTTON_HOVER = (70, 170, 230)

# Màu cho các nút điều khiển bên phải
CONTROL_BUTTON_COLOR = (200, 220, 240)
CONTROL_BUTTON_HOVER = (170, 190, 210)
NUMBER_BUTTON_COLOR = (230, 240, 250)
NUMBER_BUTTON_HOVER = (200, 210, 220)

# cửa sổ game vs tiêu đề
window = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
pygame.display.set_caption("Sudoku Game")

# font
small_font = pygame.font.SysFont(None, 28)
selected_cell = None
start_time = pygame.time.get_ticks()  # tính time từ lúc bắt đầu chơi

number_images = {}
for i in range(1, 10):
    try: # Thêm try-except để tránh lỗi nếu file không tồn tại
        img = pygame.image.load(f"assets/{i}.png")
        img = pygame.transform.scale(img, (CELL_SIZE - 10, CELL_SIZE - 10))  # co ảnh cho vừa ô, tăng padding 1 chút
        number_images[i] = img
    except pygame.error as e:
        print(f"Cannot load image assets/{i}.png: {e}")
        # Có thể tạo một surface thay thế hoặc bỏ qua
        # For now, we'll just print and continue, items might be missing.

# ---CÁC RECT VỊ TRÍ CHO CÁC NÚT VÀ HIỂN THỊ TRÊN BẢNG ĐIỀU KHIỂN BÊN PHẢI ---
RIGHT_PANEL_X = GAME_WIDTH + 20  # Bắt đầu vẽ các phần tử bên phải từ đây, có một khoảng đệm
RIGHT_PANEL_WIDTH = TOTAL_WIDTH - GAME_WIDTH - 30  # Chiều rộng của khu vực điều khiển
BUTTON_MARGIN = 15 # Khoảng cách giữa các nút

# Vị trí nút hint (sẽ được căn giữa)
ICON_SIZE = 95 # Kích thước cho icon
hint_rect_x = RIGHT_PANEL_X + (RIGHT_PANEL_WIDTH - ICON_SIZE) // 2
hint_rect_y = 65 # Đẩy xuống một chút để không quá sát với text Mistakes/Time
hint_rect = pygame.Rect(hint_rect_x, hint_rect_y, ICON_SIZE, ICON_SIZE)

try: # Thêm try-except
    icon_hint = pygame.transform.scale(pygame.image.load("assets/hint.png"), (ICON_SIZE, ICON_SIZE))
except pygame.error as e:
    print(f"Cannot load image assets/hint.png: {e}")
    icon_hint = None # Để chương trình không crash nếu thiếu icon


# Vị trí các nút lựa chọn số (3x3 grid)
# Giữ nguyên công thức của bạn nếu nó cho ra NUMBER_BUTTON_W = 100 như mong muốn
NUMBER_BUTTON_W = (RIGHT_PANEL_WIDTH + 60 - BUTTON_MARGIN * 2) // 4 # Should result in 100
NUMBER_BUTTON_H = NUMBER_BUTTON_W  # Làm cho các nút số hình vuông

num_buttons_per_row = 3
num_block_actual_width = num_buttons_per_row * NUMBER_BUTTON_W + (num_buttons_per_row - 1) * BUTTON_MARGIN
num_block_start_x = RIGHT_PANEL_X + (RIGHT_PANEL_WIDTH - num_block_actual_width) // 2

number_button_rects = []
start_num_y = hint_rect.bottom + 25 # Khoảng cách từ nút hint đến bàn phím số

for i in range(9):
    row = i // num_buttons_per_row
    col = i % num_buttons_per_row
    x = num_block_start_x + col * (NUMBER_BUTTON_W + BUTTON_MARGIN)
    y = start_num_y + row * (NUMBER_BUTTON_H + BUTTON_MARGIN)
    number_button_rects.append(pygame.Rect(x, y, NUMBER_BUTTON_W, NUMBER_BUTTON_H))

# Vị trí nút New Game và Exit (căn dưới các nút số)
NG_BTN_W = 190 # Chiều rộng nút New Game
EX_BTN_W = 100 # Chiều rộng nút Exit
NG_EX_TOTAL_CONTENT_W = NG_BTN_W + EX_BTN_W + BUTTON_MARGIN
NEW_EXIT_Y_POS = number_button_rects[-1].bottom + BUTTON_MARGIN + 10 # +10 để có thêm khoảng trống

ng_ex_block_start_x = RIGHT_PANEL_X + (RIGHT_PANEL_WIDTH - NG_EX_TOTAL_CONTENT_W) // 2

new_game_button_rect = pygame.Rect(ng_ex_block_start_x, NEW_EXIT_Y_POS, NG_BTN_W, 50)
exit_game_button_rect = pygame.Rect(ng_ex_block_start_x + NG_BTN_W + BUTTON_MARGIN, NEW_EXIT_Y_POS, EX_BTN_W, 50)


# HÀM PHỤ
def draw_button(screen, text, x, y, w, h, inactive_color, active_color, radius, text_color, text_size, icon=None):
    mouse = pygame.mouse.get_pos()
    is_hovering = x + w > mouse[0] > x and y + h > mouse[1] > y
    color = active_color if is_hovering else inactive_color
    
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=radius)
    if icon:
        icon_rect = icon.get_rect(center=(x + w // 2, y + h // 2))
        screen.blit(icon, icon_rect)
    else:
        font = pygame.font.SysFont(None, text_size) #Sử dụng SysFont cho đơn giản
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=(x + w // 2, y + h // 2))
        screen.blit(text_surf, text_rect)

# Màu sắc nên sử dụng (đã được định nghĩa ở trên, nhưng đảm bảo sử dụng đúng)
DARK_LINE = (50, 50, 50)     # Màu đen đậm cho viền và khung 3x3
LIGHT_LINE = (200, 200, 200) # Màu xám nhạt cho đường kẻ ô

def draw_grid():
    pygame.draw.rect(window, DARK_LINE, (0, 0, GAME_WIDTH, GAME_HEIGHT), 3)

    for i in range(1, ROWS):
        if i % 3 != 0:
            pygame.draw.line(window, LIGHT_LINE, (0, i * CELL_SIZE), (GAME_WIDTH, i * CELL_SIZE), 1)
            pygame.draw.line(window, LIGHT_LINE, (i * CELL_SIZE, 0), (i * CELL_SIZE, GAME_HEIGHT), 1)

    for i in range(1, COLS // 3):
        pygame.draw.line(window, DARK_LINE, (0, i * 3 * CELL_SIZE), (GAME_WIDTH, i * 3 * CELL_SIZE), 3)
        pygame.draw.line(window, DARK_LINE, (i * 3 * CELL_SIZE, 0), (i * 3 * CELL_SIZE, GAME_HEIGHT), 3)


def draw_numbers(): #vẽ các hoa quả ở play screen
    for r in range(ROWS):
        for c in range(COLS):
            num = board[r][c]
            if num != 0:
                rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                # Tô màu nền nếu là số người dùng điền
                if not fixed_cells[r][c]:
                    if num == solution[r][c]:
                        pygame.draw.rect(window, LIGHT_BLUE, rect)
                    else:
                        pygame.draw.rect(window, LIGHT_RED, rect)
                # Vẽ ảnh số
                img = number_images.get(num)
                if img:
                    x_pos = c * CELL_SIZE + (CELL_SIZE - img.get_width()) // 2
                    y_pos = r * CELL_SIZE + (CELL_SIZE - img.get_height()) // 2
                    window.blit(img, (x_pos, y_pos))

def highlight_cell(row, col):  # dùng để tô sáng ô mà người chơi đang chọn
    pygame.draw.rect(window, HIGHLIGHT_COLOR, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 3) # Thêm độ dày cho highlight

def draw_timer():  # Vẽ đồng hồ
    if game_won and game_over_time:
        elapsed_time = (game_over_time - start_time) // 1000
    else:
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    time_text = small_font.render(f"Time: {minutes:02}:{seconds:02}", True, (0,0,0)) # Màu đen cho dễ đọc
    # Đặt ở vị trí bên phải
    window.blit(time_text, (RIGHT_PANEL_X + RIGHT_PANEL_WIDTH - time_text.get_width() - 10, 20)) # Góc trên phải của panel, thêm padding 10

def draw_wrong_attempts():  # hiển thị số lần sai
    max_wrong = MAX_WRONG[difficulty]
    text = small_font.render(f"Mistakes: {wrong_attempts}/{max_wrong}", True, (200,0,0)) # Màu đỏ
    # Đặt ở vị trí mới, bên phải
    window.blit(text, (RIGHT_PANEL_X + 10, 20))  # Góc trên trái của panel, thêm padding 10

def draw_number_buttons():  # vẽ bàn phím chọn icon bên phải
    for i, rect in enumerate(number_button_rects):
        num = i + 1
        # Kiểm tra xem nút có được hover không để đổi màu
        mouse_pos = pygame.mouse.get_pos()
        is_hovering = rect.collidepoint(mouse_pos)
        button_bg_color = NUMBER_BUTTON_HOVER if is_hovering else NUMBER_BUTTON_COLOR
        
        pygame.draw.rect(window, button_bg_color, rect, border_radius=10) # Vẽ nền nút trước

        img = number_images.get(num)
        if img:  # Kiểm tra xem hình ảnh có tồn tại không
            # Tính toán vị trí để căn giữa hình ảnh trong nút bấm.
            image_x = rect.x + (rect.w - img.get_width()) // 2
            image_y = rect.y + (rect.h - img.get_height()) // 2
            window.blit(img, (image_x, image_y))

def draw_new_exit_buttons():  # vẽ nút new với exit
    draw_button(window, "New Game", new_game_button_rect.x, new_game_button_rect.y, new_game_button_rect.w, new_game_button_rect.h,
                BUTTON_COLOR, BUTTON_HOVER, 10, BLACK, 28)
    draw_button(window, "Exit", exit_game_button_rect.x, exit_game_button_rect.y, exit_game_button_rect.w, exit_game_button_rect.h,
                (255, 120, 120), (255, 80, 80), 10, BLACK, 24)
    if icon_hint: # Chỉ vẽ nếu icon_hint được load thành công
        draw_button(window, "", hint_rect.x, hint_rect.y, hint_rect.w, hint_rect.h,
                    CONTROL_BUTTON_COLOR, CONTROL_BUTTON_HOVER, 10, BLACK, 24, icon=icon_hint) # Radius 10 cho đồng bộ

def draw_menu():  # vẽ nút mức độ ở màn hình bắt đầu
    window.fill((255, 228, 225)) # Màu nền hồng phấn
    try:
        title_font = pygame.font.SysFont("Comic Sans MS", 60) # Tăng kích thước font
    except:
        title_font = pygame.font.SysFont(None, 80) # Font mặc định nếu Comic Sans MS không có
    title = title_font.render("SUDOKU FRUIT", True, (220, 20, 60)) # Màu đỏ thẫm cho tiêu đề
    
    # Canh giữa tiêu đề cho toàn bộ cửa sổ TOTAL_WIDTH
    title_rect = title.get_rect(center=(TOTAL_WIDTH // 3, 120)) # Đẩy tiêu đề xuống chút
    window.blit(title, title_rect)

    # Nút Difficulty - căn giữa trong khu vực GAME_WIDTH
    button_w, button_h = 220, 65 # Tăng kích thước nút
    button_x = (GAME_WIDTH - button_w) // 2 # Căn giữa trong phần game area
    
    draw_button(window, "Easy", button_x, 220, button_w, button_h, (144, 238, 144), (104, 198, 104), 15, BLACK, 36) # Greenish
    draw_button(window, "Medium", button_x, 310, button_w, button_h, (255, 215, 0), (235, 195, 0), 15, BLACK, 36)   # Goldish
    draw_button(window, "Hard", button_x, 400, button_w, button_h, (255, 105, 97), (235, 85, 77), 15, BLACK, 36)    # Reddish


# kiểm tra số nhập vào có đúng quy tắc ko
def is_valid(board_to_check, row, col, num): # đổi tên biến board để tránh nhầm lẫn với global
    # kiểm tra hàng
    for i in range(COLS):
        if board_to_check[row][i] == num and i != col: # Thêm điều kiện i != col
            return False
    # kiểm tra cột
    for i in range(ROWS):
        if board_to_check[i][col] == num and i != row: # Thêm điều kiện i != row
            return False
    # kiểm tra ô trong khối 3x3
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            current_r, current_c = start_row + i, start_col + j
            if board_to_check[current_r][current_c] == num and (current_r != row or current_c != col):
                return False
    return True


def solve_board(board_to_solve):  # dùng (backtracking) để tự động giải một bảng Sudoku.
    # duyệt dừng ô
    for r in range(ROWS):
        for c in range(COLS):
            if board_to_solve[r][c] == 0:
                nums = list(range(1, 10))  # thử số từ 1-9
                random.shuffle(nums)
                for num_to_try in nums:  # thử từng số
                    if is_valid(board_to_solve, r, c, num_to_try):
                        board_to_solve[r][c] = num_to_try
                        if solve_board(board_to_solve):  # gọi đệ quy để giải tiếp ô sau
                            return True
                        board_to_solve[r][c] = 0  # ko đc thì lui lại (backtrack)
                return False # Không có số nào hợp lệ cho ô này
    return True # Bảng đã được giải hoặc không còn ô trống

def generate_full_board():  # bảng full
    new_board = [[0] * COLS for _ in range(ROWS)]
    solve_board(new_board)
    return new_board

def generate_sudoku(difficulty_level="easy"):  # ẩn các ô theo độ khó
    full_board = generate_full_board()  # bảng full ban đầu
    playable_board = [row[:] for row in full_board] # Tạo bản sao sâu
    
    # Đảm bảo có ít nhất một giải pháp duy nhất (phần này phức tạp, tạm thời bỏ qua để đơn giản)
    # Thay vào đó, chỉ cần đảm bảo số lượng ô trống phù hợp
    
    cells_to_remove_map = {"easy": 35, "medium": 45, "hard": 55} # Điều chỉnh số ô trống
    cells_to_remove = cells_to_remove_map.get(difficulty_level, 35)
    
    attempts = 0 # Tránh vòng lặp vô hạn nếu logic phức tạp
    removed_count = 0
    
    while removed_count < cells_to_remove and attempts < ROWS * COLS * 2: # Giới hạn số lần thử
        r, c = random.randint(0, ROWS - 1), random.randint(0, COLS - 1)
        if playable_board[r][c] != 0:
            # Tạm thời không kiểm tra giải pháp duy nhất khi xóa, chỉ xóa ngẫu nhiên
            temp = playable_board[r][c]
            playable_board[r][c] = 0
            removed_count += 1
        attempts += 1
        
    return playable_board, full_board


def is_board_complete():  # kiểm tra ng chơi đã hoàn thành bảng chưa
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] == 0 or board[r][c] != solution[r][c]: # Kiểm tra cả ô trống
                return False
    return True

# KHỞI TẠO
board, solution = None, None
fixed_cells = [[False] * COLS for _ in range(ROWS)]
selected_cell = None
hint_used = 0
wrong_attempts = 0
game_won = False
game_over_time = None
show_hint_warning = False
hint_warning_time = 0

try: # Thêm try-except
    sidebar_bg = pygame.image.load("assets/25.jpg").convert()
    sidebar_bg = pygame.transform.scale(sidebar_bg, (TOTAL_WIDTH - GAME_WIDTH, TOTAL_HEIGHT))
except pygame.error as e:
    print(f"Cannot load image assets/25.jpg: {e}")
    sidebar_bg = None # Để chương trình không crash

# VÒNG LẶP CHÍNH
running = True
while running:
    window.fill(WHITE)
    current_time_ticks = pygame.time.get_ticks() # Đổi tên biến để tránh xung đột

    # Điều khiển nhạc dựa trên trạng thái game
    if game_state == "menu":
        play_music(music_menu)
        draw_menu()
        # bên phải là hình
        if sidebar_bg: # Chỉ vẽ nếu sidebar_bg được load
             window.blit(sidebar_bg, (GAME_WIDTH, 0))

    elif game_state == "play":
        play_music(music_game)
        # Vẽ nền cho panel bên phải (nếu không có sidebar_bg hoặc muốn màu nền đồng nhất)
        pygame.draw.rect(window, LIGHT_GRAY, (GAME_WIDTH, 0, TOTAL_WIDTH - GAME_WIDTH, TOTAL_HEIGHT))
        if sidebar_bg: # Vẽ sidebar_bg nếu có, đè lên màu nền xám
            window.blit(sidebar_bg, (GAME_WIDTH, 0))


        draw_grid() # Vẽ lưới trước
        if selected_cell: # Vẽ highlight sau lưới, trước số
            highlight_cell(*selected_cell)
        draw_numbers() # Vẽ số sau highlight

        # Vẽ các phần tử UI bên phải
        draw_timer()
        draw_wrong_attempts()
        draw_number_buttons()  # Vẽ các nút số 1-9
        draw_new_exit_buttons()  # Vẽ nút New Game, Exit và Hint

        # Cảnh báo hết hint (2s rồi biến mất)
        if show_hint_warning and current_time_ticks - hint_warning_time <= 2000:
            warning_font = pygame.font.SysFont("Georgia", 28, bold=True) # Giảm kích thước font một chút
            warning = warning_font.render("NO HINTS LEFT!", True, (255, 0, 0), LIGHT_GRAY) # Nền LIGHT_GRAY cho dễ đọc
            # Căn giữa cảnh báo phía trên nút hint
            warn_rect = warning.get_rect(center=(hint_rect.centerx, hint_rect.top - 20))
            window.blit(warning, warn_rect)
        else:
            show_hint_warning = False

        # Kiểm tra thắng thua
        # Chỉ cập nhật game_won và game_over_time một lần
        if not game_won: # Kiểm tra nếu game chưa kết thúc
            if is_board_complete():
                game_won = True
                game_over_time = current_time_ticks
                # Không cần đặt result_text ở đây, sẽ xử lý ở phần hiển thị
            elif wrong_attempts >= MAX_WRONG[difficulty]:
                game_won = True
                game_over_time = current_time_ticks
                # Không cần đặt result_text ở đây

        # hiển thị thông báo thắng thua
        if game_won:
            result_text_content = ""
            text_color = (0,0,0) # Màu chữ mặc định
            if is_board_complete() and wrong_attempts < MAX_WRONG[difficulty]: # Phải hoàn thành VÀ chưa thua
                result_text_content = "YOU WIN!"
                text_color = (0, 128, 0) # Màu xanh lá
            elif wrong_attempts >= MAX_WRONG[difficulty]:
                result_text_content = "GAME OVER!" # Thay "YOU LOSE!" bằng "GAME OVER!"
                text_color = (200, 0, 0) # Màu đỏ
            
            if result_text_content:
                # Hiển thị ở cùng vị trí với cảnh báo hint (hoặc tương tự)
                result_font = pygame.font.SysFont("Georgia", 32, bold=True)
                display_text_surf = result_font.render(result_text_content, True, text_color, LIGHT_GRAY)
                display_rect = display_text_surf.get_rect(center=(hint_rect.centerx, hint_rect.top - 25)) # Điều chỉnh vị trí
                window.blit(display_text_surf, display_rect)

    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # CLICK TRÁI
                x_mouse, y_mouse = pygame.mouse.get_pos()
                
                # Xác định các rect cho nút difficulty một cách linh động hơn
                btn_w, btn_h = 220, 65
                btn_x = (GAME_WIDTH - btn_w) // 2
                easy_btn_rect = pygame.Rect(btn_x, 220, btn_w, btn_h)
                medium_btn_rect = pygame.Rect(btn_x, 310, btn_w, btn_h)
                hard_btn_rect = pygame.Rect(btn_x, 400, btn_w, btn_h)

                temp_difficulty = None
                if easy_btn_rect.collidepoint(x_mouse, y_mouse):
                    temp_difficulty = "easy"
                elif medium_btn_rect.collidepoint(x_mouse, y_mouse):
                    temp_difficulty = "medium"
                elif hard_btn_rect.collidepoint(x_mouse, y_mouse):
                    temp_difficulty = "hard"
                
                if temp_difficulty:
                    difficulty = temp_difficulty
                    board, solution = generate_sudoku(difficulty)
                    fixed_cells = [[board[r][c] != 0 for c in range(COLS)] for r in range(ROWS)]
                    selected_cell = None
                    start_time = pygame.time.get_ticks()
                    hint_used = 0
                    wrong_attempts = 0
                    game_won = False
                    game_over_time = None
                    show_hint_warning = False
                    game_state = "play"

        elif game_state == "play":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x_mouse, y_mouse = pygame.mouse.get_pos()

                # Xử lý click trong khu vực chơi Sudoku (bên trái)
                if x_mouse < GAME_WIDTH and y_mouse < GAME_HEIGHT:
                    row_clicked, col_clicked = y_mouse // CELL_SIZE, x_mouse // CELL_SIZE
                    # Chỉ cho phép chọn nếu game chưa thắng/thua và ô không cố định
                    if not game_won and not fixed_cells[row_clicked][col_clicked]:
                        selected_cell = (row_clicked, col_clicked)
                    else:
                        selected_cell = None # Bỏ chọn nếu click vào ô cố định hoặc game đã kết thúc
                # Xử lý click trong khu vực điều khiển bên phải
                else:
                    selected_cell = None # Click ra ngoài lưới thì bỏ chọn ô
                    # Nút Hint
                    if hint_rect.collidepoint(x_mouse, y_mouse) and not game_won:
                        if hint_used < MAX_HINTS:
                            empty_cells = [(r_idx, c_idx) for r_idx in range(ROWS) for c_idx in range(COLS) if board[r_idx][c_idx] == 0]
                            if empty_cells:
                                r_hint, c_hint = random.choice(empty_cells)
                                board[r_hint][c_hint] = solution[r_hint][c_hint]
                                # Không cần đặt fixed_cells[r_hint][c_hint] = True vì hint là số người dùng có thể thay đổi
                                hint_used += 1
                        else:
                            show_hint_warning = True
                            hint_warning_time = pygame.time.get_ticks()

                    # Các nút số (1-9)
                    if not game_won and selected_cell: # Cần selected_cell trước khi điền số
                        for i, rect_button in enumerate(number_button_rects):
                            if rect_button.collidepoint(x_mouse, y_mouse):
                                r_sel, c_sel = selected_cell
                                num_chosen = i + 1
                                if not fixed_cells[r_sel][c_sel]: # Double check
                                    board[r_sel][c_sel] = num_chosen
                                    if num_chosen != solution[r_sel][c_sel]:
                                        wrong_attempts += 1
                                # selected_cell = None # Bỏ chọn sau khi điền
                                break

                    # Nút New Game (trong màn hình play)
                    if new_game_button_rect.collidepoint(x_mouse, y_mouse):
                        # Reset game với difficulty hiện tại
                        if difficulty: # Phải có difficulty đã được chọn
                            board, solution = generate_sudoku(difficulty)
                            fixed_cells = [[board[r][c] != 0 for c in range(COLS)] for r in range(ROWS)]
                            selected_cell = None
                            start_time = pygame.time.get_ticks()
                            hint_used = 0
                            wrong_attempts = 0
                            game_won = False
                            game_over_time = None
                            show_hint_warning = False
                        else: # Nếu chưa có difficulty (trường hợp hiếm), quay về menu
                            game_state = "menu"


                    # Nút Exit (trong màn hình play)
                    elif exit_game_button_rect.collidepoint(x_mouse, y_mouse):
                        game_state = "menu" # Quay về menu chính
                        play_music(music_menu) # Chuyển nhạc ngay


            # Xử lý phím bấm (chỉ khi ô được chọn trong khu vực game chính)
            if event.type == pygame.KEYDOWN and selected_cell and not game_won:
                r_sel, c_sel = selected_cell
                if not fixed_cells[r_sel][c_sel]: # Chỉ cho phép nhập vào ô không cố định
                    if event.unicode.isdigit():  # Xử lý khi player nhập một chữ số
                        num_typed = int(event.unicode)
                        if 1 <= num_typed <= 9:
                            board[r_sel][c_sel] = num_typed
                            if num_typed != solution[r_sel][c_sel]:
                                wrong_attempts += 1
                            # selected_cell = None # Bỏ chọn sau khi nhập
                    elif event.key == pygame.K_BACKSPACE:  # Xóa số
                        board[r_sel][c_sel] = 0
                    # Di chuyển ô chọn bằng phím mũi tên
                    elif event.key == pygame.K_LEFT:
                        new_c = max(0, c_sel - 1)
                        while new_c > 0 and fixed_cells[r_sel][new_c]: new_c -=1 # bỏ qua ô fixed
                        if not fixed_cells[r_sel][new_c]: selected_cell = (r_sel, new_c)
                    elif event.key == pygame.K_RIGHT:
                        new_c = min(COLS - 1, c_sel + 1)
                        while new_c < COLS -1 and fixed_cells[r_sel][new_c]: new_c +=1
                        if not fixed_cells[r_sel][new_c]: selected_cell = (r_sel, new_c)
                    elif event.key == pygame.K_UP:
                        new_r = max(0, r_sel - 1)
                        while new_r > 0 and fixed_cells[new_r][c_sel]: new_r -=1
                        if not fixed_cells[new_r][c_sel]: selected_cell = (new_r, c_sel)
                    elif event.key == pygame.K_DOWN:
                        new_r = min(ROWS - 1, r_sel + 1)
                        while new_r < ROWS - 1 and fixed_cells[new_r][c_sel]: new_r +=1
                        if not fixed_cells[new_r][c_sel]: selected_cell = (new_r, c_sel)


# Dọn dẹp khi thoát
if current_music:
    current_music.stop()
pygame.mixer.quit()
pygame.quit()
sys.exit()
