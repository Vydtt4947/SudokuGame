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
DARK_LINE = (52, 72, 97)
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
    img = pygame.image.load(f"assets/{i}.png")
    img = pygame.transform.scale(img, (CELL_SIZE - 10, CELL_SIZE - 10))  # co ảnh cho vừa ô
    number_images[i] = img

# ---CÁC RECT VỊ TRÍ CHO CÁC NÚT VÀ HIỂN THỊ TRÊN BẢNG ĐIỀU KHIỂN BÊN PHẢI ---
RIGHT_PANEL_X = GAME_WIDTH + 20  # Bắt đầu vẽ các phần tử bên phải từ đây, có một khoảng đệm
RIGHT_PANEL_WIDTH = TOTAL_WIDTH - GAME_WIDTH - 30  # Chiều rộng của khu vực điều khiển
BUTTON_MARGIN = 15

# Vị trí nút new và exit,hint
# Lấy kích thước ảnh các nút chức năng
ICON_SIZE = 95 # Kích thước cho icon
hint_rect = pygame.Rect(RIGHT_PANEL_X + 5, 50, ICON_SIZE, ICON_SIZE)
# Tải và thay đổi kích thước icon
icon_hint = pygame.transform.scale(pygame.image.load("assets/hint.png"), (ICON_SIZE, ICON_SIZE))
new_game_button_rect = pygame.Rect(RIGHT_PANEL_X + (RIGHT_PANEL_WIDTH - 300) // 4, TOTAL_HEIGHT - 80, 200, 50)
exit_game_button_rect = pygame.Rect(TOTAL_WIDTH - 120 - 20, TOTAL_HEIGHT - 80, 100, 50)  # Giữ nút Exit ở vị trí cũ (góc dưới phải)

# Vị trí các nút lựa chọn
NUMBER_BUTTON_W = (RIGHT_PANEL_WIDTH + 60 - BUTTON_MARGIN * 2) / 4
NUMBER_BUTTON_H = NUMBER_BUTTON_W  # Làm cho các nút số hình vuông
number_button_rects = []
start_num_y = hint_rect.bottom + 30 # Khoảng cách từ nút hint đến bàn phím số

for i in range(9):
    row = i // 3
    col = i % 3
    x = RIGHT_PANEL_X + col * (NUMBER_BUTTON_W + BUTTON_MARGIN)
    y = start_num_y + row * (NUMBER_BUTTON_H + BUTTON_MARGIN)
    number_button_rects.append(pygame.Rect(x, y, NUMBER_BUTTON_W, NUMBER_BUTTON_H))

# HÀM PHỤ
def draw_button(screen, text, x, y, w, h, inactive_color, active_color, radius, text_color, text_size, icon=None):
    mouse = pygame.mouse.get_pos()
    color = active_color if x + w > mouse[0] > x and y + h > mouse[1] > y else inactive_color
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=radius)
    if icon:
        icon_rect = icon.get_rect(center=(x + w // 2, y + h // 2))
        screen.blit(icon, icon_rect)
    else:
        font = pygame.font.SysFont(None, text_size)
        text_surf = font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=(x + w // 2, y + h // 2))
        screen.blit(text_surf, text_rect)

def draw_grid():  # vẽ lưới
    for i in range(ROWS + 1):
        line_width = 3 if i % 3 == 0 else 1  # độ dày đường kẻ
        pygame.draw.line(window, DARK_LINE, (0, i * CELL_SIZE), (GAME_WIDTH, i * CELL_SIZE), line_width)  # ngang
        pygame.draw.line(window, DARK_LINE, (i * CELL_SIZE, 0), (i * CELL_SIZE, 600), line_width)  # dọc

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
                    x = c * CELL_SIZE + (CELL_SIZE - img.get_width()) // 2
                    y = r * CELL_SIZE + (CELL_SIZE - img.get_height()) // 2
                    window.blit(img, (x, y))

def highlight_cell(row, col):  # dùng để tô sáng ô mà người chơi đang chọn
    pygame.draw.rect(window, HIGHLIGHT_COLOR, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_timer():  # Vẽ đồng hồ
    if game_won and game_over_time:
        elapsed_time = (game_over_time - start_time) // 1000
    else:
        elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    time_text = small_font.render(f"Time: {minutes:02}:{seconds:02}", True, (0, 0, 0))
    # Đặt ở vị trí bên phải
    window.blit(time_text, (RIGHT_PANEL_X + RIGHT_PANEL_WIDTH - time_text.get_width() - 5, 20))  # Góc trên phải của panel

def draw_wrong_attempts():  # hiển thị số lần sai
    max_wrong = MAX_WRONG[difficulty]
    text = small_font.render(f"Mistakes: {wrong_attempts}/{max_wrong}", True, (200, 0, 0))
    # Đặt ở vị trí mới, bên phải
    window.blit(text, (RIGHT_PANEL_X + 5, 20))  # Góc trên trái của panel

def draw_number_buttons():  # vẽ bàn phím chọn icon bên phải
    for i, rect in enumerate(number_button_rects):
        num = i + 1
        draw_button(window, "", rect.x, rect.y, rect.w, rect.h,
                    NUMBER_BUTTON_COLOR, NUMBER_BUTTON_HOVER, 10, NUMBER_BUTTON_COLOR, 40)  # Font lớn hơn cho số

        img = number_images.get(num)
        if img:  # Kiểm tra xem hình ảnh có tồn tại không
            # Tính toán vị trí để căn giữa hình ảnh trong nút bấm.
            # Logic này giống hệt cách bạn căn giữa ảnh trong hàm 'draw_numbers'.
            image_x = rect.x + (rect.w - img.get_width()) // 2
            image_y = rect.y + (rect.h - img.get_height()) // 2

            # Vẽ hình ảnh lên cửa sổ.
            window.blit(img, (image_x, image_y))

def draw_new_exit_buttons():  # vẽ nút new với exit
    draw_button(window, "New Game", new_game_button_rect.x, new_game_button_rect.y, new_game_button_rect.w, new_game_button_rect.h,
                BUTTON_COLOR, BUTTON_HOVER, 10, BLACK, 28)
    draw_button(window, "Exit", exit_game_button_rect.x, exit_game_button_rect.y, exit_game_button_rect.w, exit_game_button_rect.h,
                (255, 120, 120), (255, 80, 80), 10, BLACK, 24)
    draw_button(window, "", hint_rect.x, hint_rect.y, hint_rect.w, hint_rect.h,
                CONTROL_BUTTON_COLOR, CONTROL_BUTTON_HOVER, 8, BLACK, 24, icon=icon_hint)

def draw_menu():  # vẽ nút mức độ ở màn hình bắt đầu
    window.fill((255, 228, 225))
    title = pygame.font.SysFont("Comic Sans MS", 60).render("SUDOKU FRUIT", True, (50, 50, 50))
    window.blit(title, (GAME_WIDTH // 2 - title.get_width() // 2, 100))  # Canh giữa theo GAME_WIDTH
    draw_button(window, "Easy", 200, 200, 200, 60, (144, 238, 144), (124, 218, 124), 10, BLACK, 32)
    draw_button(window, "Medium", 200, 300, 200, 60, (255, 255, 153), (235, 235, 100), 10, BLACK, 32)
    draw_button(window, "Hard", 200, 400, 200, 60, (255, 160, 122), (255, 100, 72), 10, BLACK, 32)

# kiểm tra số nhập vào có đúng quy tắc ko
def is_valid(board, row, col, num):
    for i in range(9):  # kiểm tra hàng với cột
        if board[row][i] == num or board[i][col] == num:
            return False
    sr, sc = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):  # kiểm tra ô trong khối
        for j in range(3):
            if board[sr + i][sc + j] == num:
                return False
    return True

def solve_board(board):  # dùng (backtracking) để tự động giải một bảng Sudoku.
    # duyệt dừng ô
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                nums = list(range(1, 10))  # thử số từ 1-9
                random.shuffle(nums)
                for num in nums:  # thử từng số
                    if is_valid(board, r, c, num):
                        board[r][c] = num
                        if solve_board(board):  # gọi đệ quy để giải tiếp ô sau
                            return True
                        board[r][c] = 0  # ko đc thì lui lại
                return False
    return True

def generate_full_board():  # bảng full
    board = [[0] * 9 for _ in range(9)]
    solve_board(board)
    return board

def generate_sudoku(difficulty="easy"):  # ẩn các ô theo độ khó
    full_board = generate_full_board()  # bảng full ban đầu
    board = [row[:] for row in full_board]
    cells_to_remove = {"easy": 30, "medium": 40, "hard": 60}.get(difficulty, 30)  # xác định số ô bị xóa
    while cells_to_remove:  # xóa ngẫu nhiên
        r, c = random.randint(0, 8), random.randint(0, 8)
        if board[r][c] != 0:
            board[r][c] = 0
            cells_to_remove -= 1
    return board, full_board

def is_board_complete():  # kiểm tra ng chơi đã hoàn thành bảng chưa
    for r in range(9):
        for c in range(9):
            if board[r][c] != solution[r][c]:
                return False
    return True

# KHỞI TẠO
board, solution = None, None
fixed_cells = [[False] * 9 for _ in range(9)]
selected_cell = None
hint_used = 0
wrong_attempts = 0
game_won = False
game_over_time = None
show_hint_warning = False
hint_warning_time = 0
sidebar_bg = pygame.image.load("assets/25.jpg").convert()
sidebar_bg = pygame.transform.scale(sidebar_bg, (TOTAL_WIDTH - GAME_WIDTH, TOTAL_HEIGHT))

# VÒNG LẶP CHÍNH
running = True
while running:
    window.fill(WHITE)
    current_time = pygame.time.get_ticks()
    # trả về số mili-giây (ms) đã trôi qua kể từ khi gọi pygame.init()

    if game_state == "menu":
        draw_menu()
        # bên phải là hình
        window.blit(sidebar_bg, (GAME_WIDTH, 0))

    elif game_state == "play":
        pygame.draw.rect(window, LIGHT_GRAY, (GAME_WIDTH, 0, TOTAL_WIDTH - GAME_WIDTH, TOTAL_HEIGHT))

        if selected_cell:
            highlight_cell(*selected_cell)
        draw_grid()
        draw_numbers()

        # Vẽ các phần tử UI bên phải
        draw_timer()
        draw_wrong_attempts()
        draw_number_buttons()  # Vẽ các nút số 1-9
        draw_new_exit_buttons()  # Vẽ nút New Game và Exit

        # Cảnh báo hết hint (2s rồi biến mất)
        if show_hint_warning and current_time - hint_warning_time <= 2000:
            warning = pygame.font.SysFont("Georgia", 30, bold=True).render("NO HINTS LEFT!", True, (255, 0, 0), (255, 255, 255))
            # Cảnh báo này có thể đặt ở vị trí cụ thể trong bảng điều khiển bên phải
            window.blit(warning, (RIGHT_PANEL_X +105, GAME_HEIGHT - 525))
        else:
            show_hint_warning = False

        # Kiểm tra thắng thua
        if (is_board_complete() or wrong_attempts >= MAX_WRONG[difficulty]) and not game_won:
            game_won = True
            game_over_time = current_time

        #hiển thị thông báo thắng thua
        if game_won:
            result_text = ""
            if is_board_complete():
                result_text = " YOU WIN!"
            elif wrong_attempts >= MAX_WRONG[difficulty]:
                result_text = "YOU LOSE!"
            if result_text:
                display_text =pygame.font.SysFont("Georgia", 30, bold=True).render(result_text, True, (255, 0, 0), (255, 255, 255))
                window.blit(display_text,(RIGHT_PANEL_X +135, GAME_HEIGHT - 525))
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # CLICK TRÁI
                x, y = pygame.mouse.get_pos()
                # Kiểm tra click trong khu vực Sudoku (0 đến GAME_WIDTH)
                if x <= GAME_WIDTH:  # Chỉ phản ứng với click trong khu vực game chính
                    if 200 <= x <= 400:  # Phạm vi X cho các nút Difficulty
                        if 200 <= y <= 260:
                            difficulty = "easy"
                        elif 300 <= y <= 360:
                            difficulty = "medium"
                        elif 400 <= y <= 460:
                            difficulty = "hard"
                        if difficulty:
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
                x, y = pygame.mouse.get_pos()

                # Xử lý click trong khu vực chơi Sudoku (bên trái)
                if x < GAME_WIDTH and y < GAME_HEIGHT:
                    row, col = y // CELL_SIZE, x // CELL_SIZE
                    if not fixed_cells[row][col] and not game_won:
                        selected_cell = (row, col)
                # Xử lý click trong khu vực điều khiển bên phải
                else:
                    # Các nút chức năng (Undo, Eraser, Pencil, Hint)
                    if hint_rect.collidepoint(x, y) and not game_won:
                        if hint_used < MAX_HINTS:
                            empty_cells = [(r, c) for r in range(9) for c in range(9) if board[r][c] == 0]
                            if empty_cells:
                                r, c = random.choice(empty_cells)
                                board[r][c] = solution[r][c]
                                hint_used += 1
                                selected_cell = None
                        else:
                            show_hint_warning = True
                            hint_warning_time = pygame.time.get_ticks()
                    # TODO: Thêm logic cho nút Undo, Eraser, Pencil ở đây

                    # Các nút số (1-9)
                    for i, rect in enumerate(number_button_rects):
                        if rect.collidepoint(x, y) and selected_cell and not game_won:
                            r, c = selected_cell
                            num = i + 1
                            if not fixed_cells[r][c]:
                                board[r][c] = num
                                if num != solution[r][c]:
                                    wrong_attempts += 1
                            break  # Đảm bảo chỉ xử lý một nút số

                    # Nút New Game
                    if new_game_button_rect.collidepoint(x, y):
                    # tạo game mới
                        board, solution = generate_sudoku(difficulty)
                        fixed_cells = [[board[r][c] != 0 for c in range(COLS)] for r in range(ROWS)]
                        selected_cell = None
                        start_time = pygame.time.get_ticks()
                        hint_used = 0
                        wrong_attempts = 0
                        game_won = False
                        game_over_time = None
                        show_hint_warning = False

                    # Nút Exit
                    elif exit_game_button_rect.collidepoint(x, y):
                        game_state = "menu"

            # Xử lý phím bấm (chỉ khi ô được chọn trong khu vực game chính)
            if event.type == pygame.KEYDOWN and selected_cell and not game_won:
                r, c = selected_cell
                if event.unicode.isdigit():  # Xử lý khi player nhập một chữ số
                    num = int(event.unicode)
                    if 1 <= num <= 9 and not fixed_cells[r][c]:
                        board[r][c] = num
                        if num != solution[r][c]:
                            wrong_attempts += 1
                elif event.key == pygame.K_BACKSPACE and not fixed_cells[r][c]:  # Xử lý khi player nhấn phím Backspace (xóa số):
                    board[r][c] = 0

pygame.quit()
sys.exit()
