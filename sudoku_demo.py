import pygame  # Nhập thư viện Pygame để phát triển game
import sys     # Nhập thư thư viện sys để truy cập các chức năng liên quan đến hệ thống (ví dụ: thoát game)
import random  # Nhập thư viện random để tạo số ngẫu nhiên (dùng cho tạo bảng Sudoku)
import copy    # Nhập thư viện copy để tạo bản sao sâu của các đối tượng (ví dụ: bảng Sudoku)
from typing import Optional, Tuple, Dict, Any # Nhập các kiểu dữ liệu từ thư viện typing để chú thích kiểu (giúp code dễ đọc và kiểm tra lỗi)

# ==============================================================================
# 1. CẤU HÌNH & HẰNG SỐ
# ==============================================================================
pygame.init()       # Khởi tạo tất cả các module cần thiết của Pygame
pygame.mixer.init() # Khởi tạo module âm thanh của Pygame

# Kích thước cửa sổ game và bảng Sudoku
ROWS, COLS = 9, 9                                 # Số hàng và cột của bảng Sudoku (9x9)
CELL_SIZE = 70                                    # Kích thước cố định của mỗi ô (pixel)
GAME_WIDTH = COLS * CELL_SIZE                     # Chiều rộng của khu vực bảng game (9 * 70 = 630 pixels)
GAME_HEIGHT = ROWS * CELL_SIZE                    # Chiều cao của khu vực bảng game (9 * 70 = 630 pixels)

TOTAL_WIDTH = GAME_WIDTH + 370                    # Tổng chiều rộng cửa sổ game (bảng game + panel bên phải)
TOTAL_HEIGHT = GAME_HEIGHT                        # Tổng chiều cao cửa sổ game (bằng chiều cao bảng game)

# Màu sắc được sử dụng trong game, định nghĩa dưới dạng RGB hoặc mã hex
COLORS = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "light_gray": (220, 220, 220),
    "dark_line": (50, 50, 50),     # Màu cho các đường kẻ đậm của lưới
    "light_line": (200, 200, 200),  # Màu cho các đường kẻ mảnh của lưới
    "light_red": (255, 200, 200),   # Màu nền ô sai
    "light_blue": (173, 216, 230),  # Màu nền ô đúng do người chơi nhập
    "highlight": "#009966",        # Màu viền ô được chọn
    "highlight_bg": (220, 230, 245), # Màu nền highlight hàng/cột/khối
    "button": (100, 200, 255),      # Màu nút bình thường
    "button_hover": (70, 170, 230), # Màu nút khi di chuột qua
    "exit_button": (255, 120, 120), # Màu nút thoát
    "exit_button_hover": (255, 80, 80), # Màu nút thoát khi di chuột qua
    "menu_bg": (255, 228, 225),    # Màu nền menu (màu hồng nhạt)
    "panel_bg": "#FBD6E3",         # Màu nền panel bên phải
    "win_text": (0, 128, 0),       # Màu chữ khi thắng
    "lose_text": (200, 0, 0),      # Màu chữ khi thua hoặc cảnh báo
    "overlay": (0, 0, 0, 150),     # Màu lớp phủ mờ khi game over (RGB + Alpha)
    "outline_color": (0, 0, 0),    # Màu cho viền chữ (outline)
}

# Fonts (Tải một lần để tránh tải lại nhiều lần)
try:
    FONTS = {
        "title": pygame.font.SysFont("Comic Sans MS", 65, bold=True), # Font tiêu đề
        "button": pygame.font.SysFont(None, 36),                     # Font nút bấm
        "timer": pygame.font.SysFont(None, 28),                      # Font cho bộ đếm thời gian và số lỗi
        "warning": pygame.font.SysFont("Georgia", 28, bold=True),     # Font cho các cảnh báo (ví dụ: hết gợi ý)
        "game_over": pygame.font.SysFont("Arial", 75, bold=True),    # Font cho màn hình Game Over
        "hint_warning_font": pygame.font.SysFont("Arial", 30, bold=True), # Font cho cảnh báo gợi ý
    }
except: # Fallback nếu không tìm thấy font hệ thống
    FONTS = {
        "title": pygame.font.SysFont(None, 65, bold=True),
        "button": pygame.font.SysFont(None, 36),
        "timer": pygame.font.SysFont(None, 28),
        "warning": pygame.font.SysFont(None, 28, bold=True),
        "game_over": pygame.font.SysFont(None, 75, bold=True),
        "hint_warning_font": pygame.font.SysFont(None, 30, bold=True),
    }

# Cửa sổ game chính
window = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT)) # Tạo cửa sổ Pygame với kích thước đã định
pygame.display.set_caption("Sudoku Fruit") # Đặt tiêu đề cho cửa sổ game

# ==============================================================================
# 2. HÀM TẢI TÀI NGUYÊN
# ==============================================================================
def load_sound(path: str, volume: float = 0.5) -> Optional[pygame.mixer.Sound]:
    """Tải một file âm thanh và xử lý lỗi nếu không tìm thấy."""
    try:
        sound = pygame.mixer.Sound(path) # Tải âm thanh từ đường dẫn
        sound.set_volume(volume)         # Đặt âm lượng cho âm thanh
        return sound
    except pygame.error as e:
        print(f"Lỗi: không thể tải âm thanh '{path}'. {e}") # In thông báo lỗi
        return None # Trả về None nếu không tải được

def load_image(path: str, size: Optional[Tuple[int, int]] = None) -> pygame.Surface:
    """Tải một file ảnh, thay đổi kích thước và xử lý lỗi."""
    try:
        img = pygame.image.load(path).convert_alpha() # Tải ảnh và chuyển đổi định dạng pixel (giữ kênh alpha)
        if size: # Nếu có kích thước được cung cấp
            img = pygame.transform.scale(img, size) # Thay đổi kích thước ảnh
        return img
    except pygame.error as e:
        print(f"Lỗi: không thể tải ảnh '{path}'. {e}") # In thông báo lỗi
        # Trả về một Surface trống (trong suốt) với kích thước mặc định hoặc kích thước yêu cầu nếu lỗi
        return pygame.Surface(size if size else (50, 50), pygame.SRCALPHA)

# Tải tất cả các tài nguyên âm thanh và hình ảnh cần thiết
SOUNDS: Dict[str, Optional[pygame.mixer.Sound]] = {
    "menu": load_sound("assets/music1.mp3"),  # Nhạc nền menu
    "game": load_sound("assets/music2.mp3"),  # Nhạc nền khi chơi game
    "click_key": load_sound("assets/bubble.mp3"), # Âm thanh khi nhập số hoặc click nút
    "click_cell": load_sound("assets/left.mp3"), # Âm thanh khi chọn ô
    "win": load_sound("assets/win.mp3", volume=0.7),   # Âm thanh khi thắng
    "lose": load_sound("assets/lose.mp3", volume=0.7), # Âm thanh khi thua
}

IMAGES: Dict[str, Any] = {
    "hint_icon": None, # Sẽ được đặt kích thước sau khi biết kích thước nút gợi ý
    "sidebar_bg": load_image("assets/25.png", (TOTAL_WIDTH - GAME_WIDTH, TOTAL_HEIGHT)), # Ảnh nền panel bên phải
    "numbers": { # Các ảnh cho số từ 1 đến 9
        i: load_image(f"assets/{i}.png", (CELL_SIZE - 10, CELL_SIZE - 10))
        for i in range(1, 10)
    }
}
current_music: Optional[pygame.mixer.Sound] = None # Biến toàn cục để theo dõi nhạc đang phát

def play_music(sound_key: str):
    """Phát nhạc nền, tránh phát lại nếu đang phát cùng một bài nhạc."""
    global current_music
    new_music = SOUNDS.get(sound_key) # Lấy đối tượng âm thanh từ dictionary
    if new_music is not current_music: # Nếu nhạc mới khác nhạc đang phát
        if current_music:
            current_music.stop() # Dừng nhạc hiện tại
        if new_music:
            new_music.play(-1) # Phát nhạc mới lặp lại vô hạn (-1)
        current_music = new_music # Cập nhật nhạc đang phát

# ==============================================================================
# 3. LỚP SUDOKU GAME
# ==============================================================================
class SudokuGame:
    def __init__(self, difficulty: str):
        self.difficulty = difficulty # Độ khó của game ("easy", "medium", "hard")
        self.solution = self._generate_full_board() # Tạo bảng Sudoku đã giải hoàn chỉnh
        self.board = self._generate_puzzle(copy.deepcopy(self.solution)) # Tạo bảng câu đố từ bảng đã giải
        # Ma trận boolean đánh dấu các ô ban đầu (không thể thay đổi)
        self.fixed_cells = [[self.board[r][c] != 0 for c in range(COLS)] for r in range(ROWS)]
        
        self.selected_cell: Optional[Tuple[int, int]] = None # Ô đang được chọn (hàng, cột)
        self.start_time = pygame.time.get_ticks() # Thời điểm bắt đầu game (dùng cho bộ đếm thời gian)
        
        self.max_hints = 3 # Số lượng gợi ý tối đa
        self.hint_used = 0 # Số gợi ý đã sử dụng
        
        # Số lần sai tối đa cho từng độ khó
        self.max_wrong: int = {"easy": 5, "medium": 3, "hard": 3}[difficulty]
        self.wrong_attempts = 0 # Số lần sai hiện tại
        
        self.is_over = False # Trạng thái game đã kết thúc hay chưa
        self.is_won = False # Trạng thái thắng/thua
        self.game_over_time: Optional[int] = None # Thời điểm game kết thúc
        self.game_over_sound_played = False # Cờ để đảm bảo âm thanh kết thúc game chỉ phát một lần
        
        self.show_hint_warning = False # Cờ để hiển thị cảnh báo hết gợi ý
        self.hint_warning_time = 0 # Thời điểm cảnh báo gợi ý được hiển thị
        
        self._setup_ui_rects() # Thiết lập các hình chữ nhật cho UI

    def _setup_ui_rects(self):
        """Thiết lập các hình chữ nhật (Rect) cho các phần tử UI như nút bấm."""
        panel_start_x = GAME_WIDTH
        panel_width = TOTAL_WIDTH - GAME_WIDTH
        margin = 15 # Lề chung

        # Tính toán kích thước nút New Game và Exit
        new_game_text_w, _ = FONTS["button"].size("New Game")
        exit_text_w, _ = FONTS["button"].size("Exit")

        new_game_btn_w = new_game_text_w + 40 # Thêm padding cho nút
        exit_btn_w = exit_text_w + 40
        button_h = 45 # Chiều cao cố định cho các nút này
        button_spacing = 15 # Khoảng cách giữa các nút

        total_buttons_group_width = new_game_btn_w + exit_btn_w + button_spacing
        
        # Căn giữa nhóm nút trong panel bên phải
        start_x_buttons_group = panel_start_x + (panel_width - total_buttons_group_width) // 2

        # Thiết lập Rect cho nút New Game và Exit Game
        self.new_game_button_rect = pygame.Rect(start_x_buttons_group, TOTAL_HEIGHT - button_h - 40, new_game_btn_w, button_h)
        self.exit_game_button_rect = pygame.Rect(start_x_buttons_group + new_game_btn_w + button_spacing, TOTAL_HEIGHT - button_h - 40, exit_btn_w, button_h)

        # Kích thước nút gợi ý
        hint_button_size = 70 
        self.hint_rect = pygame.Rect(0, 0, hint_button_size, hint_button_size) # X, Y sẽ được đặt khi vẽ để căn chỉnh
        # Tải và thay đổi kích thước icon gợi ý để vừa với nút
        IMAGES["hint_icon"] = load_image("assets/hint.png", (hint_button_size - 10, hint_button_size - 10)) 

        # Nút số (lưới 3x3) trên panel bên phải
        num_btn_w = (panel_width - margin * 4) // 3 # Tính chiều rộng mỗi nút số
        num_btn_h = num_btn_w # Nút số là hình vuông
        
        num_block_total_width = num_btn_w * 3 + margin * 2 # Tổng chiều rộng khối nút số
        num_block_start_x = panel_start_x + (panel_width - num_block_total_width) // 2 # Vị trí X bắt đầu để căn giữa
        
        self.number_button_rects: list[pygame.Rect] = [] # Danh sách lưu trữ Rect của 9 nút số
        temp_num_block_start_y = 180 # Tạm thời đặt Y để ước lượng, Y thực tế sẽ được điều chỉnh trong _draw_number_buttons

        for i in range(9): # Tạo Rect cho từng nút số
            row_idx, col_idx = i // 3, i % 3
            x = num_block_start_x + col_idx * (num_btn_w + margin)
            y = temp_num_block_start_y + row_idx * (num_btn_h + margin)
            self.number_button_rects.append(pygame.Rect(x, y, num_btn_w, num_btn_h))

        # --- Cập nhật logic cho nút Game Over New Game và Exit ---
        # Tính toán kích thước dựa trên text và padding cho các nút trên màn hình Game Over
        go_new_game_text_w, go_new_game_text_h = FONTS["button"].size("New Game")
        go_exit_text_w, go_exit_text_h = FONTS["button"].size("Exit")
        
        go_button_padding_x = 30 # Padding ngang
        go_button_padding_y = 15 # Padding dọc

        self.game_over_new_game_rect = pygame.Rect(0, 0, go_new_game_text_w + go_button_padding_x * 2, go_new_game_text_h + go_button_padding_y * 2)
        self.game_over_exit_rect = pygame.Rect(0, 0, go_exit_text_w + go_button_padding_x * 2, go_exit_text_h + go_button_padding_y * 2)
        # --------------------------------------------------------

    def _is_valid(self, board: list[list[int]], row: int, col: int, num: int) -> bool:
        """Kiểm tra xem việc đặt số 'num' vào ô (row, col) có hợp lệ không."""
        # Kiểm tra hàng
        if any(board[row][c] == num for c in range(COLS)): return False
        # Kiểm tra cột
        if any(board[r][col] == num for r in range(ROWS)): return False
        # Kiểm tra khối 3x3
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                if board[start_row + i][start_col + j] == num:
                    return False
        return True

    def _solve_board(self, board: list[list[int]]) -> bool:
        """Giải bảng Sudoku bằng thuật toán quay lui (backtracking)."""
        for r in range(ROWS):
            for c in range(COLS):
                if board[r][c] == 0: # Tìm ô trống
                    nums = list(range(1, 10))
                    random.shuffle(nums) # Xáo trộn thứ tự các số để tạo nhiều lời giải khác nhau
                    for num in nums:
                        if self._is_valid(board, r, c, num):
                            board[r][c] = num # Đặt số vào ô
                            if self._solve_board(board): # Gọi đệ quy để giải tiếp
                                return True
                            board[r][c] = 0 # Quay lui (backtrack) nếu không tìm được lời giải
                    return False # Không tìm được số nào hợp lệ cho ô này
        return True # Bảng đã được giải hoàn chỉnh

    def _generate_full_board(self) -> list[list[int]]:
        """Tạo một bảng Sudoku đã giải hoàn chỉnh."""
        board = [[0] * COLS for _ in range(ROWS)] # Tạo bảng rỗng 9x9
        self._solve_board(board) # Giải bảng rỗng để tạo ra một lời giải
        return board

    def _generate_puzzle(self, board: list[list[int]]) -> list[list[int]]:
        """Tạo câu đố Sudoku từ một bảng đã giải bằng cách loại bỏ các số."""
        # Số ô cần loại bỏ tùy thuộc vào độ khó
        cells_to_remove: int = {"easy": 35, "medium": 45, "hard": 55}[self.difficulty]
        removed_count = 0 # Số ô đã loại bỏ
        attempts = 0 # Số lần thử (để tránh vòng lặp vô hạn)
        while removed_count < cells_to_remove and attempts < 200:
            r, c = random.randint(0, 8), random.randint(0, 8) # Chọn ngẫu nhiên một ô
            if board[r][c] != 0: # Nếu ô đó chưa trống
                board[r][c] = 0 # Xóa số ở ô đó (đặt thành 0)
                removed_count += 1
            attempts += 1
        return board

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Xử lý các sự kiện đầu vào (chuột, bàn phím) trong game."""
        if self.is_over: # Nếu game đã kết thúc, chuyển việc xử lý cho màn hình game over
            return self._handle_game_over_click(event)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Xử lý click chuột trái
            x, y = event.pos
            if x < GAME_WIDTH and y < GAME_HEIGHT: # Nếu click trong khu vực bảng Sudoku
                row, col = y // CELL_SIZE, x // CELL_SIZE # Tính toán hàng và cột của ô được click
                # Đảm bảo row/col nằm trong giới hạn hợp lệ (0-8)
                row = min(row, ROWS - 1)
                col = min(col, COLS - 1)

                if not self.fixed_cells[row][col]: # Nếu ô không phải là ô cố định
                    self.selected_cell = (row, col) # Đặt ô này là ô được chọn
                    if SOUNDS["click_cell"]: SOUNDS["click_cell"].play() # Phát âm thanh click
            else: # Nếu click ngoài khu vực bảng Sudoku (trên panel phải)
                return self._handle_button_click(event.pos) # Xử lý click nút

        if event.type == pygame.KEYDOWN and self.selected_cell: # Xử lý nhấn phím khi có ô được chọn
            r, c = self.selected_cell
            
            if event.key == pygame.K_BACKSPACE: # Nếu nhấn phím Backspace
                self.board[r][c] = 0 # Xóa số trong ô
            elif event.unicode.isdigit() and 1 <= int(event.unicode) <= 9: # Nếu nhấn phím số từ 1-9
                num = int(event.unicode)
                self.board[r][c] = num # Đặt số vào ô

                if num != self.solution[r][c]: # Nếu số đặt vào sai
                    self.wrong_attempts += 1 # Thay đổi: Tăng số lỗi mỗi lần nhập sai
            
            if SOUNDS["click_key"]: SOUNDS["click_key"].play() # Phát âm thanh click phím
            return None # Trả về None sau khi xử lý phím
        return None # Trả về None nếu không có sự kiện nào được xử lý

    def _handle_button_click(self, pos: Tuple[int, int]) -> Optional[str]:
        """Xử lý click chuột trên các nút ở panel bên phải."""
        if SOUNDS["click_key"]: SOUNDS["click_key"].play() # Phát âm thanh click nút
        
        if self.hint_rect.collidepoint(pos): # Nếu click vào nút gợi ý
            self._use_hint() # Sử dụng gợi ý
        for i, rect in enumerate(self.number_button_rects): # Duyệt qua các nút số
            if rect.collidepoint(pos) and self.selected_cell: # Nếu click vào nút số và có ô đang chọn
                r, c = self.selected_cell
                if not self.fixed_cells[r][c]: # Chỉ cho phép nhập nếu không phải ô cố định
                    num = i + 1 # Số tương ứng với nút
                    self.board[r][c] = num # Đặt số vào ô được chọn
                    if num != self.solution[r][c]: # Nếu số đặt vào sai
                        self.wrong_attempts += 1 # Thay đổi: Tăng số lỗi mỗi lần nhập sai
                break # Thoát vòng lặp sau khi xử lý
        if self.new_game_button_rect.collidepoint(pos): # Nếu click vào nút "New Game"
            return "new_game" # Trả về "new_game" để thay đổi trạng thái
        if self.exit_game_button_rect.collidepoint(pos): # Nếu click vào nút "Exit"
            return "exit" # Trả về "exit" để thay đổi trạng thái
        return None # Trả về None nếu không có nút nào được click

    def _handle_game_over_click(self, event: pygame.event.Event) -> Optional[str]:
        """Xử lý các sự kiện click chuột khi game đang ở trạng thái Game Over."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.game_over_new_game_rect.collidepoint(event.pos):
                if SOUNDS["click_key"]: SOUNDS["click_key"].play()
                print("New Game button clicked on Game Over screen!") # Debug print
                return "new_game_over" # Báo hiệu để bắt đầu game mới sau khi game over
            elif self.game_over_exit_rect.collidepoint(event.pos):
                if SOUNDS["click_key"]: SOUNDS["click_key"].play()
                print("Exit button clicked on Game Over screen! Returning to menu.") # Debug print
                return "return_to_menu_from_game_over" # THAY ĐỔI: Signal để quay về menu
        return None

    def _use_hint(self):
        """Sử dụng một gợi ý, điền một số đúng vào một ô trống ngẫu nhiên."""
        if self.hint_used < self.max_hints: # Kiểm tra còn gợi ý không
            empty_cells = [(r, c) for r in range(ROWS) for c in range(COLS) if self.board[r][c] == 0] # Lấy danh sách các ô trống
            if empty_cells: # Nếu có ô trống
                r, c = random.choice(empty_cells) # Chọn ngẫu nhiên một ô trống
                
                self.board[r][c] = self.solution[r][c] # Điền số đúng vào ô đó
                self.fixed_cells[r][c] = True # Đánh dấu ô này là ô cố định
                self.hint_used += 1 # Tăng số gợi ý đã dùng
                self.selected_cell = None # Bỏ chọn ô
        else: # Nếu hết gợi ý
            self.show_hint_warning = True # Đặt cờ để hiển thị cảnh báo
            self.hint_warning_time = pygame.time.get_ticks() # Ghi lại thời gian hiển thị cảnh báo

    def update(self):
        """Cập nhật trạng thái game (kiểm tra thắng/thua, thời gian)."""
        if self.is_over: # Nếu game đã kết thúc
            if not self.game_over_sound_played: # Nếu âm thanh kết thúc game chưa phát
                pygame.mixer.stop() # Dừng tất cả nhạc nền
                if self.is_won and SOUNDS["win"]: # Nếu thắng
                    if SOUNDS["win"]: SOUNDS["win"].play() # Phát nhạc thắng
                elif not self.is_won and SOUNDS["lose"]: # Nếu thua
                    if SOUNDS["lose"]: SOUNDS["lose"].play() # Phát nhạc thua
                self.game_over_sound_played = True # Đánh dấu đã phát âm thanh
            return # Thoát hàm update

        is_full = not any(self.board[r][c] == 0 for r in range(ROWS) for c in range(COLS)) # Kiểm tra bảng đã đầy chưa
        
        is_correctly_filled = True
        if is_full:
            for r in range(ROWS):
                for c in range(COLS):
                    if self.board[r][c] != self.solution[r][c]:
                        is_correctly_filled = False
                        break
                if not is_correctly_filled:
                    break

        if is_full and is_correctly_filled: # Win condition: board is full AND all cells are correct
            self.is_over = True
            self.is_won = True
            self.game_over_time = pygame.time.get_ticks()
        elif self.wrong_attempts >= self.max_wrong: # Nếu số lần sai vượt quá giới hạn (thua)
            self.is_over = True
            self.is_won = False
            self.game_over_time = pygame.time.get_ticks()

    def draw(self, window: pygame.Surface):
        """Vẽ tất cả các thành phần của game lên cửa sổ."""
        # Tô toàn bộ khu vực bảng game với màu trắng
        pygame.draw.rect(window, COLORS["white"], (0, 0, GAME_WIDTH, GAME_HEIGHT))
        
        # Vẽ nền panel bên phải
        pygame.draw.rect(window, COLORS["panel_bg"], (GAME_WIDTH, 0, TOTAL_WIDTH - GAME_WIDTH, TOTAL_HEIGHT))
        
        # Highlight nền hàng/cột/khối nếu có ô được chọn
        if self.selected_cell:
            self._draw_selection_highlight(window)
        
        self._draw_numbers(window) # Vẽ các số trên bảng
        self._draw_grid(window) # Vẽ lưới Sudoku (sau khi vẽ số để đường kẻ nằm trên số)
        
        # Highlight ô được chọn (viền)
        if self.selected_cell:
            self._highlight_cell(window, *self.selected_cell)
        
        self._draw_timer(window) # Vẽ bộ đếm thời gian
        self._draw_wrong_attempts(window) # Vẽ số lần sai
        self._draw_control_buttons(window) # Vẽ các nút điều khiển (New Game, Exit, Hint)
        self._draw_number_buttons(window) # Vẽ các nút số (1-9)
        self._draw_messages(window) # Vẽ các thông báo (ví dụ: cảnh báo hết gợi ý)

        if self.is_over: # Nếu game đã kết thúc, vẽ màn hình game over
            self._draw_game_over_screen(window)

    def _draw_selection_highlight(self, window: pygame.Surface):
        """Vẽ phần highlight nền cho hàng, cột và khối 3x3 chứa ô được chọn."""
        if not self.selected_cell: return # Không làm gì nếu không có ô nào được chọn

        row, col = self.selected_cell
        color = COLORS["highlight_bg"] # Màu nền highlight
        
        # Highlight hàng
        pygame.draw.rect(window, color, (0, row * CELL_SIZE, GAME_WIDTH, CELL_SIZE))

        # Highlight cột
        pygame.draw.rect(window, color, (col * CELL_SIZE, 0, CELL_SIZE, GAME_HEIGHT))

        # Highlight khối 3x3
        start_row, start_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(3):
            for j in range(3):
                current_r = start_row + i
                current_c = start_col + j
                pygame.draw.rect(window, color, (current_c * CELL_SIZE, current_r * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    def _draw_grid(self, window: pygame.Surface):
        """Vẽ lưới Sudoku (các đường kẻ mảnh và đậm)."""
        # 1. Vẽ các đường kẻ mảnh (1px) trước
        for i in range(1, ROWS):
            if i % 3 != 0: # Chỉ vẽ đường mảnh nếu không phải biên của khối 3x3
                # Đường ngang
                pygame.draw.line(window, COLORS["light_line"], (0, i * CELL_SIZE), (GAME_WIDTH, i * CELL_SIZE), 1)
                # Đường dọc
                pygame.draw.line(window, COLORS["light_line"], (i * CELL_SIZE, 0), (i * CELL_SIZE, GAME_HEIGHT), 1)

        # 2. Vẽ các đường kẻ đậm (3px) của khối 3x3 bằng rect để kiểm soát chính xác hơn
        line_thickness = 3
        # Đường ngang đậm
        for i in range(1, ROWS):
            if i % 3 == 0: 
                # Vẽ hình chữ nhật làm đường kẻ ngang đậm, căn giữa tại vị trí đường kẻ
                pygame.draw.rect(window, COLORS["dark_line"], (0, i * CELL_SIZE - line_thickness // 2, GAME_WIDTH, line_thickness))
        
        # Đường dọc đậm
        for i in range(1, COLS):
            if i % 3 == 0:
                # Vẽ hình chữ nhật làm đường kẻ dọc đậm, căn giữa tại vị trí đường kẻ
                pygame.draw.rect(window, COLORS["dark_line"], (i * CELL_SIZE - line_thickness // 2, 0, line_thickness, GAME_HEIGHT))

        # 3. Vẽ đường viền ngoài cùng của toàn bộ lưới với độ dày 3px (luôn vẽ sau cùng để đảm bảo hiển thị rõ ràng)
        pygame.draw.rect(window, COLORS["dark_line"], (0, 0, GAME_WIDTH, GAME_HEIGHT), 3)

    def _draw_numbers(self, window: pygame.Surface):
        """Vẽ các số trên bảng Sudoku."""
        for r in range(ROWS):
            for c in range(COLS):
                num = self.board[r][c]
                if num != 0: # Chỉ vẽ nếu ô có số
                    rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                    # Thay đổi: highlight ô sai nếu giá trị hiện tại không khớp với solution
                    if not self.fixed_cells[r][c] and num != self.solution[r][c]: 
                        color = COLORS["light_red"]
                        pygame.draw.rect(window, color, rect)
                    # Thay đổi: highlight ô đúng do người chơi nhập
                    elif not self.fixed_cells[r][c] and num == self.solution[r][c]:
                         color = COLORS["light_blue"]
                         pygame.draw.rect(window, color, rect)

                    img = IMAGES["numbers"].get(num) # Lấy ảnh số tương ứng
                    if img:
                        img_rect = img.get_rect(center=rect.center) # Lấy hình chữ nhật của ảnh và căn giữa
                        window.blit(img, img_rect) # Vẽ ảnh số lên màn hình

    def _highlight_cell(self, window: pygame.Surface, row: int, col: int):
        """Vẽ viền highlight xung quanh ô đang được chọn."""
        highlight_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(window, COLORS["highlight"], highlight_rect, 3) # Vẽ viền với độ dày 3px

    def _draw_timer(self, window: pygame.Surface):
        """Vẽ bộ đếm thời gian."""
        time_to_show = self.game_over_time if self.is_over else pygame.time.get_ticks() # Thời gian để hiển thị
        elapsed_time = (time_to_show - self.start_time) // 1000 # Thời gian trôi qua (giây)
        mins, secs = divmod(elapsed_time, 60) # Chuyển đổi giây thành phút và giây
        time_text = FONTS["timer"].render(f"Time: {mins:02}:{secs:02}", True, COLORS["black"]) # Render văn bản thời gian
        
        # Vị trí cho thời gian (căn phải với một lề)
        panel_start_x = GAME_WIDTH
        panel_width = TOTAL_WIDTH - GAME_WIDTH
        
        time_x = panel_start_x + panel_width - time_text.get_width() - 15 # Tính toán vị trí X để căn phải
        window.blit(time_text, (time_x, 20)) # Vẽ văn bản thời gian

    def _draw_wrong_attempts(self, window: pygame.Surface):
        """Vẽ số lần người chơi đã mắc lỗi."""
        text = FONTS["timer"].render(f"Mistakes: {self.wrong_attempts}/{self.max_wrong}", True, COLORS["lose_text"]) # Render văn bản số lần sai
        
        # Vị trí cho số lỗi (căn trái với một lề)
        panel_start_x = GAME_WIDTH
        mistakes_x = panel_start_x + 15 # Vị trí X để căn trái
        window.blit(text, (mistakes_x, 20)) # Vẽ văn bản số lần sai

    def _draw_number_buttons(self, window: pygame.Surface):
        """Vẽ 9 nút số (1-9) trên panel bên phải."""
        mouse_pos = pygame.mouse.get_pos() # Lấy vị trí chuột
        
        num_block_start_y = self.hint_rect.bottom + 25 + 20 # Bắt đầu vẽ các nút số bên dưới nút gợi ý và text hint
        
        for i, rect in enumerate(self.number_button_rects): # Duyệt qua các Rect của nút số
            row_idx, col_idx = i // 3, i % 3
            current_x = rect.x # Giữ nguyên vị trí X đã tính từ _setup_ui_rects
            rect.y = num_block_start_y + row_idx * (rect.height + 15) # Cập nhật vị trí Y dựa trên num_block_start_y
            rect.x = current_x # Gán lại vị trí X

            is_hovering = rect.collidepoint(mouse_pos) # Kiểm tra chuột có đang hover không
            color = (200, 210, 220) if is_hovering else (230, 240, 250) # Chọn màu nút
            pygame.draw.rect(window, color, rect, border_radius=10) # Vẽ nút với bo góc
            
            img = IMAGES["numbers"].get(i + 1) # Lấy ảnh số
            if img:
                img_rect = img.get_rect(center=rect.center) # Căn giữa ảnh trong nút
                window.blit(img, img_rect) # Vẽ ảnh lên nút

    def _draw_control_buttons(self, window: pygame.Surface):
        """Vẽ các nút điều khiển chính: Hint, New Game, Exit."""
        panel_start_x = GAME_WIDTH
        hint_x_pos = panel_start_x + 15 # Vị trí X của nút gợi ý
        hint_y_pos = 50 + 20 # Vị trí Y của nút gợi ý (cố định)

        self.hint_rect.topleft = (hint_x_pos, hint_y_pos) # Đặt vị trí top-left của nút gợi ý

        # Vẽ nút gợi ý
        draw_button(window, "", self.hint_rect, (200, 220, 240), (170, 190, 210), icon=IMAGES["hint_icon"]) 
        
        # HIỂN THỊ SỐ GỢI Ý CÒN LẠI
        hint_count_text = FONTS["timer"].render(f"Hints: {self.max_hints - self.hint_used}/{self.max_hints}", True, COLORS["black"])
        hint_count_rect = hint_count_text.get_rect(midtop=(self.hint_rect.centerx, self.hint_rect.bottom + 5))
        window.blit(hint_count_text, hint_count_rect)

        # Vẽ nút New Game
        draw_button(window, "New Game", self.new_game_button_rect, COLORS["button"], COLORS["button_hover"], text_font=FONTS["button"])
        # Vẽ nút Exit
        draw_button(window, "Exit", self.exit_game_button_rect, COLORS["exit_button"], COLORS["exit_button_hover"], text_font=FONTS["button"])

    def _draw_messages(self, window: pygame.Surface):
        """Vẽ các thông báo tạm thời trên màn hình (ví dụ: cảnh báo hết gợi ý)."""
        if self.show_hint_warning and pygame.time.get_ticks() - self.hint_warning_time <= 2000: # Nếu cần hiển thị cảnh báo gợi ý và chưa quá 2 giây
            text = "NO HINTS LEFT!"
            font = FONTS["hint_warning_font"]
            color = COLORS["lose_text"]
            outline_color = COLORS["outline_color"]
            outline_thickness = 2 

            x_pos = self.hint_rect.right + 10 # Vị trí X của cảnh báo (bên phải nút gợi ý)
            y_pos = self.hint_rect.centery # Vị trí Y của cảnh báo (căn giữa theo nút gợi ý)
            
            # Vẽ cảnh báo với viền
            draw_text_with_outline(window, text, font, color, outline_color, x_pos, y_pos, "midleft", outline_thickness)
        else:
            self.show_hint_warning = False # Dừng hiển thị cảnh báo nếu đã quá thời gian

    def _draw_game_over_screen(self, window: pygame.Surface):
        """Vẽ màn hình Game Over khi game kết thúc (thắng hoặc thua)."""
        overlay = pygame.Surface((TOTAL_WIDTH, TOTAL_HEIGHT), pygame.SRCALPHA) # Tạo một surface trong suốt
        overlay.fill(COLORS["overlay"]) # Tô màu overlay (đen mờ)
        window.blit(overlay, (0, 0)) # Vẽ overlay lên toàn màn hình

        msg = "YOU WIN!" if self.is_won else "GAME OVER!" # Thông báo thắng/thua
        color = COLORS["win_text"] if self.is_won else COLORS["lose_text"] # Màu chữ thông báo
        
        font = FONTS["game_over"]
        outline_color = COLORS["outline_color"]
        outline_thickness = 3 

        text_center_x = TOTAL_WIDTH // 2
        text_center_y = TOTAL_HEIGHT // 2 - 80
        
        # Vẽ thông báo game over với viền
        draw_text_with_outline(window, msg, font, color, outline_color, text_center_x, text_center_y, "center", outline_thickness)

        button_spacing = 30 # Khoảng cách giữa các nút trên màn hình game over
        total_width_buttons = self.game_over_new_game_rect.width + self.game_over_exit_rect.width + button_spacing
        
        start_x_group = (TOTAL_WIDTH - total_width_buttons) // 2
        button_y = TOTAL_HEIGHT // 2 + 50

        # Đặt vị trí nút New Game
        self.game_over_new_game_rect.topleft = (start_x_group, button_y - self.game_over_new_game_rect.height // 2)
        # Đặt vị trí nút Exit
        self.game_over_exit_rect.topleft = (start_x_group + self.game_over_new_game_rect.width + button_spacing, button_y - self.game_over_exit_rect.height // 2)

        # Vẽ nút New Game
        draw_button(window, "New Game", self.game_over_new_game_rect, COLORS["button"], COLORS["button_hover"], text_font=FONTS["button"])
        # Vẽ nút Exit
        draw_button(window, "Exit", self.game_over_exit_rect, COLORS["exit_button"], COLORS["exit_button_hover"], text_font=FONTS["button"])

# ==============================================================================
# 4. HÀM CHO MENU & HÀM TIỆN ÍCH
# ==============================================================================
def draw_button(window: pygame.Surface, text: str, rect: pygame.Rect, inactive_color: Tuple[int, int, int] | str, active_color: Tuple[int, int, int] | str, radius: int = 10, text_color: Tuple[int, int, int] = COLORS["black"], text_font: Optional[pygame.font.Font] = None, icon: Optional[pygame.Surface] = None):
    """
    Hàm tiện ích để vẽ một nút bấm với hiệu ứng hover và bo góc.
    Có thể có văn bản hoặc icon.
    """
    mouse_pos = pygame.mouse.get_pos() # Lấy vị trí chuột
    is_hovering = rect.collidepoint(mouse_pos) # Kiểm tra chuột có đang hover không
    color = active_color if is_hovering else inactive_color # Chọn màu nút dựa trên trạng thái hover
    
    pygame.draw.rect(window, color, rect, border_radius=radius) # Vẽ hình chữ nhật cho nút
    
    if icon: # Nếu có icon
        icon_rect = icon.get_rect(center=rect.center) # Căn giữa icon trong nút
        window.blit(icon, icon_rect) # Vẽ icon
    elif text and text_font: # Nếu có văn bản và font
        text_surf = text_font.render(text, True, text_color) # Render văn bản
        text_rect = text_surf.get_rect(center=rect.center) # Căn giữa văn bản trong nút
        window.blit(text_surf, text_rect) # Vẽ văn bản

def draw_text_with_outline(surface: pygame.Surface, text: str, font: pygame.font.Font, text_color: Tuple[int, int, int], outline_color: Tuple[int, int, int], x: int, y: int, anchor_type: str = "center", outline_thickness: int = 2):
    """
    Vẽ văn bản với một viền (outline).
    anchor_type: "center", "midleft", "topleft", v.v. (tương tự pygame.Rect)
    """
    # Vẽ outline bằng cách vẽ văn bản outline xung quanh vị trí chính
    outline_surf = font.render(text, True, outline_color) # Render văn bản với màu outline
    
    outline_rect = outline_surf.get_rect()
    setattr(outline_rect, anchor_type, (x, y)) # Đặt vị trí Rect dựa trên loại neo (anchor_type)
    
    for dx in range(-outline_thickness, outline_thickness + 1): # Duyệt xung quanh để vẽ outline
        for dy in range(-outline_thickness, outline_thickness + 1):
            if dx != 0 or dy != 0: # Bỏ qua điểm giữa (vị trí chữ chính)
                offset_rect = outline_rect.copy() 
                offset_rect.move_ip(dx, dy) # Dịch chuyển Rect để vẽ các điểm outline
                surface.blit(outline_surf, offset_rect) # Vẽ outline
    
    # Vẽ chữ chính
    text_surf = font.render(text, True, text_color) # Render văn bản với màu chính
    text_rect = text_surf.get_rect()
    setattr(text_rect, anchor_type, (x, y)) 
    surface.blit(text_surf, text_rect) # Vẽ chữ chính

def draw_menu(window: pygame.Surface):
    """Vẽ màn hình menu chính của game."""
    window.fill(COLORS["menu_bg"]) # Tô nền menu
    if IMAGES["sidebar_bg"]:
        window.blit(IMAGES["sidebar_bg"], (GAME_WIDTH, 0)) # Vẽ nền sidebar (nếu có)
    
    title_surf = FONTS["title"].render("SUDOKU FRUIT", True, (220, 20, 60)) # Render tiêu đề
    title_rect = title_surf.get_rect(center=(GAME_WIDTH / 2, 120)) # Căn giữa tiêu đề
    window.blit(title_surf, title_rect) # Vẽ tiêu đề
    
    btn_w, btn_h = 220, 65
    btn_x = (GAME_WIDTH - btn_w) // 2 # Căn giữa các nút theo chiều ngang
    
    # Vẽ các nút lựa chọn độ khó và nút Exit
    draw_button(window, "Easy", pygame.Rect(btn_x, 220, btn_w, btn_h), (144, 238, 144), (104, 198, 104), 15, COLORS["black"], FONTS["button"])
    draw_button(window, "Medium", pygame.Rect(btn_x, 310, btn_w, btn_h), (255, 215, 0), (235, 195, 0), 15, COLORS["black"], FONTS["button"])
    draw_button(window, "Hard", pygame.Rect(btn_x, 400, btn_w, btn_h), (255, 105, 97), (235, 85, 77), 15, COLORS["black"], FONTS["button"])
    
    exit_menu_btn_rect = pygame.Rect(btn_x, 500, btn_w, btn_h)
    draw_button(window, "Exit Game", exit_menu_btn_rect, COLORS["exit_button"], COLORS["exit_button_hover"], 15, COLORS["black"], FONTS["button"])

def handle_menu_click(pos: Tuple[int, int]) -> Optional[str]:
    """Xử lý click chuột trên màn hình menu."""
    btn_w, btn_h = 220, 65
    btn_x = (GAME_WIDTH - btn_w) // 2 # Tính toán vị trí X tương tự khi vẽ

    # Kiểm tra xem vị trí click có nằm trong Rect của nút nào không và trả về độ khó/hành động tương ứng
    if pygame.Rect(btn_x, 220, btn_w, btn_h).collidepoint(pos): return "easy"
    if pygame.Rect(btn_x, 310, btn_w, btn_h).collidepoint(pos): return "medium"
    if pygame.Rect(btn_x, 400, btn_w, btn_h).collidepoint(pos): return "hard"
    if pygame.Rect(btn_x, 500, btn_w, btn_h).collidepoint(pos): return "quit_game"
    return None # Không có nút nào được click

# ==============================================================================
# 5. VÒNG LẶP CHÍNH
# ==============================================================================
def main():
    """Hàm chính để chạy game Sudoku."""
    running = True # Biến điều khiển vòng lặp chính của game
    game_state: str = "menu" # Trạng thái game hiện tại ("menu" hoặc "play")
    game: Optional[SudokuGame] = None # Đối tượng game Sudoku hiện tại

    while running: # Vòng lặp chính của game
        for event in pygame.event.get(): # Duyệt qua tất cả các sự kiện đang chờ xử lý
            if event.type == pygame.QUIT: # Nếu người dùng click nút đóng cửa sổ
                running = False # Đặt biến running thành False để thoát vòng lặp

            if game_state == "menu": # Nếu game đang ở trạng thái menu
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Nếu có sự kiện click chuột trái
                    action = handle_menu_click(event.pos) # Gọi hàm xử lý click trên menu
                    if action in ["easy", "medium", "hard"]: # Nếu người dùng chọn một độ khó
                        if SOUNDS["click_key"]: SOUNDS["click_key"].play() # Phát âm thanh click
                        game = SudokuGame(action) # Tạo một đối tượng game Sudoku mới với độ khó đã chọn
                        game_state = "play" # Chuyển trạng thái game sang "play"
                    elif action == "quit_game": # Nếu người dùng chọn "Exit Game" từ menu
                        running = False # Thoát vòng lặp chính
            
            elif game_state == "play" and game: # Nếu game đang ở trạng thái "play" và đối tượng game tồn tại
                action = game.handle_event(event) # Gọi phương thức handle_event của đối tượng game để xử lý sự kiện
                if action == "exit": # Nếu click nút "Exit" trong game
                    pygame.mixer.stop() # Dừng nhạc game trước khi quay lại menu
                    game_state = "menu" # Chuyển trạng thái game về "menu"
                    game = None # Xóa đối tượng game hiện tại
                    print("Switched to Menu from in-game Exit.") # Debug print
                elif action == "new_game": # Nếu click nút "New Game"
                    game = SudokuGame(game.difficulty) # Tạo một game mới với độ khó hiện tại
                    print("Started new game from in-game New Game button.") # Debug print
                elif action == "new_game_over": # Nếu click "New Game" từ màn hình Game Over
                    game = SudokuGame(game.difficulty) # Tạo game mới
                    game_state = "play" # Chuyển trạng thái game sang "play"
                    print("Started new game from Game Over New Game button.") # Debug print
                elif action == "return_to_menu_from_game_over": # Nếu click "Exit" từ màn hình Game Over
                    pygame.mixer.stop() # Dừng nhạc game
                    game_state = "menu" # Chuyển trạng thái game về "menu"
                    game = None # Xóa đối tượng game hiện tại
                    print("Returned to Menu from Game Over screen.") # Debug print

        if game_state == "play" and game: # Nếu game đang chơi và đối tượng game tồn tại
            game.update() # Cập nhật trạng thái game
            
        window.fill(COLORS["white"]) # Xóa màn hình bằng cách tô màu trắng mỗi khung hình

        if game_state == "menu": # Nếu ở trạng thái menu
            play_music("menu") # Phát nhạc nền menu
            draw_menu(window) # Vẽ menu
        elif game_state == "play" and game: # Nếu ở trạng thái chơi
            play_music("game") # Phát nhạc nền game
            game.draw(window) # Vẽ game
            
        pygame.display.flip() # Cập nhật toàn bộ màn hình hiển thị lên cửa sổ

    pygame.quit() # Hủy khởi tạo tất cả các module Pygame
    sys.exit()    # Thoát chương trình

if __name__ == "__main__":
    main() # Gọi hàm main để bắt đầu game khi script được chạy trực tiếp
