import pygame #thư viện xây dựng game
import sys #thư viện để tương tác với hệ thống
import random #thư viện sinh ra giá trị ngẫu nhiên

# BIẾN TOÀN CỤC
hint_used = 0 #số lượng gợi ý tối đa là 3 lần
MAX_HINTS = 3 
game_won = False
wrong_attempts = 0 # số lượng lỗi sai tùy theo cấp độ
MAX_WRONG = {"easy": 5, "medium": 3, "hard": 3}

pygame.init() #khởi tạo module

# CẤU HÌNH CƠ BẢN
game_state = "menu" # start hiện menu / chưa chọn độ khó
difficulty = None
WIDTH, HEIGHT = 600, 700 #kt cửa sổ
ROWS, COLS = 9, 9 # 9x9 ô
CELL_SIZE = WIDTH // COLS #kt mỗi ô
# màu
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (220, 220, 220)
DARK_LINE = (52, 72, 97)
FIXED_COLOR = (0, 0, 0)
USER_COLOR = (0, 0, 255)
HIGHLIGHT_COLOR = (255, 255, 153)
BUTTON_COLOR = (100, 200, 255)
BUTTON_HOVER = (70, 170, 230)
# cửa sổ game vs tiêu đề
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Game")
# font chữ
font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 28)

selected_cell = None
start_time = pygame.time.get_ticks() #tính time từ lúc bắt đầu chơi
#nút chức năng
new_game_rect = pygame.Rect(WIDTH - 280, HEIGHT - 80, 120, 40)
exit_game_rect = pygame.Rect(WIDTH - 140, HEIGHT - 80, 120, 40)
hint_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT - 80, 90, 40)

# HÀM PHỤ
def draw_button(screen, text, x, y, w, h, inactive_color, active_color, radius, text_color, text_size):
    # inactive màu khi ko hover chuột >< active, radius độ bo góc nút
    mouse = pygame.mouse.get_pos() #lấy vị trí chuột hiện tại
    #kiểm tra chuột đang ở nút nào thì gắn  active ko thì inactive
    color = active_color if x + w > mouse[0] > x and y + h > mouse[1] > y else inactive_color
    #nút hình chữ nhật
    pygame.draw.rect(screen, color, (x, y, w, h), border_radius=radius)
    font = pygame.font.SysFont(None, text_size)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=(x + w // 2, y + h // 2))
    screen.blit(text_surf, text_rect)

def draw_grid(): #vẽ lưới
    for i in range(ROWS + 1): 
        line_width = 3 if i % 3 == 0 else 1 #độ dày đường kẻ
        pygame.draw.line(window, DARK_LINE, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), line_width) #ngang
        pygame.draw.line(window, DARK_LINE, (i * CELL_SIZE, 0), (i * CELL_SIZE, WIDTH), line_width) #dọc

def draw_numbers(): #vẽ số duyệt từng ô
    for r in range(ROWS):
        for c in range(COLS):
            num = board[r][c]
            if num != 0:
                if fixed_cells[r][c]:
                    color = FIXED_COLOR # Số cố định ban đầu – màu đen
                elif num != solution[r][c]:
                    color = (255, 0, 0)  # Số do người chơi nhập sai – màu đỏ
                else:
                    color = USER_COLOR # Số người chơi nhập đúng – màu xanh
                text = font.render(str(num), True, color) #vẽ sô và canh giữa ô
                x = c * CELL_SIZE + (CELL_SIZE - text.get_width()) // 2
                y = r * CELL_SIZE + (CELL_SIZE - text.get_height()) // 2
                window.blit(text, (x, y))

def highlight_cell(row, col): #dùng để tô sáng ô mà người chơi đang chọn
    pygame.draw.rect(window, HIGHLIGHT_COLOR, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def draw_timer(): #hiển thị đồng hồ
    elapsed = (pygame.time.get_ticks() - start_time) // 1000 #trả về số millisecond hiển thị thời gian trôi qua
    mins, secs = divmod(elapsed, 60) # 60s -> 1p
    time_text = f"Time: {mins:02}:{secs:02}"  
    text = small_font.render(time_text, True, BLACK)
    window.blit(text, (10, HEIGHT - 70))

def draw_wrong_attempts(): #hiển thị số lần sai
    max_wrong = MAX_WRONG[difficulty]
    text = small_font.render(f"Mistakes: {wrong_attempts}/{max_wrong}", True, (200, 0, 0))
    window.blit(text, (10, HEIGHT - 50))

def draw_new_exit_buttons(): #vẽ nút
    draw_button(window, "New Game", new_game_rect.x, new_game_rect.y, new_game_rect.w, new_game_rect.h,
                BUTTON_COLOR, BUTTON_HOVER, 10, BLACK, 24)
    draw_button(window, "Exit", exit_game_rect.x, exit_game_rect.y, exit_game_rect.w, exit_game_rect.h,
                (255, 120, 120), (255, 80, 80), 10, BLACK, 24)
    draw_button(window, "Hint", hint_button.x, hint_button.y, hint_button.w, hint_button.h,
                (173, 216, 230), (100, 180, 210), 10, BLACK, 24)

def draw_menu(): #vẽ nút mức độ ở màn hình bắt đầu
    window.fill((240, 240, 240))
    title = pygame.font.SysFont(None, 60).render("Select Difficulty", True, (50, 50, 50))
    window.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
    draw_button(window, "Easy", 220, 200, 200, 60, (144, 238, 144), (124, 218, 124), 10, BLACK, 32)
    draw_button(window, "Medium", 220, 300, 200, 60, (255, 255, 153), (235, 235, 100), 10, BLACK, 32)
    draw_button(window, "Hard", 220, 400, 200, 60, (255, 160, 122), (255, 100, 72), 10, BLACK, 32)
#kiểm tra số nhập vào có đúng quy tắc ko
def is_valid(board, row, col, num):
    for i in range(9):#kiểm tra hàng với cột
        if board[row][i] == num or board[i][col] == num:
            return False
    sr, sc = 3 * (row // 3), 3 * (col // 3)
    for i in range(3): #kiểm tra ô trong khối
        for j in range(3):
            if board[sr + i][sc + j] == num:
                return False
    return True

def solve_board(board): #dùng (backtracking) để tự động giải một bảng Sudoku. 
    #duyeeth dừng ô
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                nums = list(range(1, 10)) #thử số từ 1-9
                random.shuffle(nums)
                for num in nums: #thử từng số
                    if is_valid(board, r, c, num):
                        board[r][c] = num
                        if solve_board(board): #gọi đệ quy để giải tiếp ô sau
                            return True
                        board[r][c] = 0 #ko đc thì lui lại
                return False
    return True

def generate_full_board():
    board = [[0] * 9 for _ in range(9)]
    solve_board(board)
    return board

def generate_sudoku(difficulty="easy"): #vẽ cái đề theo độ khó
    full_board = generate_full_board() #bảng full ban đầu
    board = [row[:] for row in full_board]
    cells_to_remove = {"easy": 30, "medium": 40, "hard": 60}.get(difficulty, 30) #xác định số ô bị xóa
    while cells_to_remove: #xóa ngẫu nhiên
        r, c = random.randint(0, 8), random.randint(0, 8)
        if board[r][c] != 0:
            board[r][c] = 0
            cells_to_remove -= 1
    return board, full_board

def is_board_complete(): #kiểm tra ng chơi đã hoàn thành bảng chưa
    for r in range(9):
        for c in range(9):
            if board[r][c] != solution[r][c]:
                return False
    return True

# KHỞI TẠO
board, solution = None, None 
fixed_cells = [[False] * 9 for _ in range(9)]

# VÒNG LẶP CHÍNH
running = True
while running:#giữ cho game chạy liên tục đến khi quit
    window.fill(WHITE) #xóa màn hình bằng màu trắng trước khi vẽ lại
    if game_state == "menu":
        draw_menu()
    elif game_state == "play":
        if selected_cell:
            highlight_cell(*selected_cell)
        draw_grid()
        draw_numbers()
        draw_timer()
        draw_new_exit_buttons()
        draw_wrong_attempts()
        if is_board_complete():#kiểm tra thắng hay thua, gợi ý
            game_won = True
            win_text = font.render("\U0001F389 YOU WIN! \U0001F389", True, (200, 0, 0))
            window.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT - 130))
        elif hint_used >= MAX_HINTS:
            warning = small_font.render("NO HINTS LEFT!", True, (200, 0, 0))
            window.blit(warning, (WIDTH // 2 - warning.get_width() // 2, HEIGHT - 120))
        elif wrong_attempts >= MAX_WRONG[difficulty]:
            lose_text = font.render("YOU LOSE!", True, (200, 0, 0))
            window.blit(lose_text, (WIDTH // 2 - lose_text.get_width() // 2, HEIGHT - 130))
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT: #thoát game
            running = False

        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN: #chọn độ khó qua click chuột
                x, y = pygame.mouse.get_pos()
                if 220 <= x <= 420:
                    if 200 <= y <= 260:
                        difficulty = "easy"
                    elif 300 <= y <= 360:
                        difficulty = "medium"
                    elif 400 <= y <= 460:
                        difficulty = "hard"
                    if difficulty: #chọn rồi thì gọi gen() để tạo game mới
                        board, solution = generate_sudoku(difficulty)
                        fixed_cells = [[board[r][c] != 0 for c in range(COLS)] for r in range(ROWS)]
                        selected_cell = None
                        start_time = pygame.time.get_ticks()
                        hint_used = 0
                        wrong_attempts = 0
                        game_won = False
                        game_state = "play"

        elif game_state == "play": 
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if y < WIDTH:
                    row, col = y // CELL_SIZE, x // CELL_SIZE
                    if not fixed_cells[row][col]:
                        selected_cell = (row, col)
                elif new_game_rect.collidepoint(x, y):
                    board, solution = generate_sudoku(difficulty)
                    fixed_cells = [[board[r][c] != 0 for c in range(COLS)] for r in range(ROWS)]
                    selected_cell = None
                    start_time = pygame.time.get_ticks()
                    hint_used = 0
                    wrong_attempts = 0
                    game_won = False
                elif exit_game_rect.collidepoint(x, y):
                    game_state = "menu"
                elif hint_button.collidepoint(x, y):
                    if hint_used < MAX_HINTS:
                        for r in range(9):
                            for c in range(9):
                                if board[r][c] == 0:
                                    board[r][c] = solution[r][c]
                                    hint_used += 1
                                    selected_cell = None
                                    break
                            else:
                                continue
                            break

            if event.type == pygame.KEYDOWN and selected_cell:
                r, c = selected_cell
                if event.unicode.isdigit():
                    num = int(event.unicode)
                    if 1 <= num <= 9:
                        if not fixed_cells[r][c]:
                            if num == solution[r][c]:
                                board[r][c] = num
                            else:
                                board[r][c] = num
                                wrong_attempts += 1
                elif event.key == pygame.K_BACKSPACE:
                    board[r][c] = 0

pygame.quit()
sys.exit()
