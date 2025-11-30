import pygame # type: ignore
import os
import sys 

# Đảm bảo thư mục data nằm trong PATH hoặc sử dụng đường dẫn tương đối
# from data.classes.Board import Board # Giả định lớp Board tồn tại
# Nếu bạn chưa có lớp Board, bạn cần tạo nó hoặc thay thế bằng một dummy class.
class Board:
    def __init__(self, width, height):
        # Đây là một lớp giả định (dummy) để mã có thể chạy
        print("Board object initialized. Assume piece images are loaded.")
        self.width = width
        self.height = height
        self.turn = 'white'
        self.selected_piece = None
        self.last_move = None

    def draw(self, display):
        # Vẽ một bàn cờ đơn giản 8x8
        square_size = self.width // 8
        colors = [(240, 217, 181), (181, 136, 99)] # Màu bàn cờ gỗ
        
        for row in range(8):
            for col in range(8):
                color = colors[(row + col) % 2]
                pygame.draw.rect(display, color, (col * square_size, row * square_size, square_size, square_size))
        
        # Thêm Placeholder Text
        font = pygame.font.SysFont('arial', 70)
        text = font.render("CHESS BOARD", True, (0, 0, 0, 50))
        text.set_alpha(50) 
        display.blit(text, text.get_rect(center=(self.width // 2, self.height // 2)))

    def handle_click(self, mx, my):
        # Logic xử lý click (chọn/di chuyển quân cờ)
        print(f"Click at: ({mx}, {my})")
        pass

    def is_in_checkmate(self, color):
        # Trả về False để game chạy liên tục trong ví dụ này
        return False
        
# --- Khởi tạo Pygame ---
pygame.init()

# --- Thiết lập Cấu hình Cửa sổ ---
WINDOW_SIZE = (1000, 1000)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Cờ Vua Chuyên Nghiệp")

# --- Hằng số Màu sắc & Font ---
# Cố gắng sử dụng Font có sẵn hoặc fallback
def get_font(size):
    try:
        # Thử sử dụng một font phổ biến (cần có trong hệ thống)
        return pygame.font.SysFont('Arial', size)
    except:
        return pygame.font.SysFont('sans', size)

FONT = get_font(40)
HEADER_FONT = get_font(60)
SMALL_FONT = get_font(30)

# Bảng màu đẹp hơn (Material Design Inspired)
PRIMARY_COLOR = (38, 166, 154)   # Màu Xanh Teal đậm
ACCENT_COLOR = (255, 179, 0)      # Màu Vàng Cam
BACKGROUND_COLOR = (236, 239, 241) # Xám Sáng
HOVER_COLOR = (84, 182, 172)     # Xanh Teal Nhạt hơn
WHITE = (255, 255, 255)
BLACK = (33, 33, 33)             # Đen Đậm

# --- Trạng thái Game ---
GAME_STATE = "MENU"
board = Board(WINDOW_SIZE[0], WINDOW_SIZE[1])

# --- Khai báo Rects (Sẽ được gán giá trị trong các hàm draw_*) ---
# Sử dụng global để các hàm handle_* có thể truy cập được các Rect này
machine_button = None
player_button = None
# ... và các nút khác


# --- Chức năng Vẽ Nút Tương tác ---
def draw_interactive_button(surface, rect, text, font, base_color, hover_color, text_color, mouse_pos, border_radius=8):
    """Vẽ nút, thay đổi màu khi di chuột và thêm bo góc."""
    is_hovering = rect and rect.collidepoint(mouse_pos)
    color = hover_color if is_hovering else base_color
    
    # Vẽ nền nút
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)
    # Vẽ viền
    pygame.draw.rect(surface, BLACK, rect, 2, border_radius=border_radius)
    
    # Vẽ chữ
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
    return is_hovering # Trả về trạng thái hover (nếu cần)

# --- Chức năng Xử lý Menu ---
def handle_menu_click(mouse_x, mouse_y):
    global GAME_STATE, board, machine_button, player_button
    
    if machine_button and machine_button.collidepoint(mouse_x, mouse_y):
        GAME_STATE = "LEVEL_SELECTION"
    
    elif player_button and player_button.collidepoint(mouse_x, mouse_y):
        GAME_STATE = "MODE_SELECTION"

def handle_level_selection_click(mouse_x, mouse_y):
    global GAME_STATE, board, novice_button, skilled_button, expert_button, master_button, back_level_button
    
    level_buttons = {
        'Novice': novice_button,
        'Skilled': skilled_button,
        'Expert': expert_button,
        'Master': master_button
    }
    
    for level_name, button in level_buttons.items():
        if button and button.collidepoint(mouse_x, mouse_y):
            print(f"Bắt đầu game với AI cấp độ: {level_name}")
            board = Board(WINDOW_SIZE[0], WINDOW_SIZE[1]) 
            GAME_STATE = "GAME_AI"
            return 
            
    if back_level_button and back_level_button.collidepoint(mouse_x, mouse_y):
        GAME_STATE = "MENU"

def handle_mode_selection_click(mouse_x, mouse_y):
    global GAME_STATE, board, random_button, create_room_button, back_mode_button
    
    if random_button and random_button.collidepoint(mouse_x, mouse_y):
        print("Đang tìm kiếm người chơi ngẫu nhiên...")
        board = Board(WINDOW_SIZE[0], WINDOW_SIZE[1])
        GAME_STATE = "GAME_LOCAL" 
    
    elif create_room_button and create_room_button.collidepoint(mouse_x, mouse_y):
        print("Mở giao diện Tạo phòng...")
        board = Board(WINDOW_SIZE[0], WINDOW_SIZE[1])
        GAME_STATE = "GAME_LOCAL"

    elif back_mode_button and back_mode_button.collidepoint(mouse_x, my):
        GAME_STATE = "MENU"
		
def draw_menu(display, mouse_pos):
    global machine_button, player_button
    display.fill(BACKGROUND_COLOR)
    
    # Tiêu đề
    title_text = HEADER_FONT.render("CHESS VIETNAM", True, BLACK)
    display.blit(title_text, title_text.get_rect(center=(WINDOW_SIZE[0] // 2, 150)))
    
    # Định nghĩa và Vẽ các nút
    button_width, button_height = 400, 80
    center_x = WINDOW_SIZE[0] // 2
    
    machine_button = pygame.Rect(center_x - button_width // 2, 350, button_width, button_height)
    player_button = pygame.Rect(center_x - button_width // 2, 500, button_width, button_height)
    
    draw_interactive_button(display, machine_button, "Đánh với Máy (AI)", FONT, PRIMARY_COLOR, HOVER_COLOR, WHITE, mouse_pos)
    draw_interactive_button(display, player_button, "Đánh với Người", FONT, PRIMARY_COLOR, HOVER_COLOR, WHITE, mouse_pos)
    
    # Footer
    footer_text = SMALL_FONT.render("Made with Pygame", True, (100, 100, 100))
    display.blit(footer_text, footer_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] - 50)))

def draw_level_selection(display, mouse_pos):
    global novice_button, skilled_button, expert_button, master_button, back_level_button
    display.fill(BACKGROUND_COLOR)
    
    # Tiêu đề
    title_text = HEADER_FONT.render("CHỌN CẤP ĐỘ AI", True, BLACK)
    display.blit(title_text, title_text.get_rect(center=(WINDOW_SIZE[0] // 2, 100)))
    
    # Dữ liệu cấp độ
    levels = [
        ("Nhập Môn", "Novice", WHITE),
        ("Thành Thạo", "Skilled", WHITE),
        ("Cao Thủ", "Expert", ACCENT_COLOR),
        ("Kiện Tướng", "Master", (200, 0, 0)) # Đỏ để làm nổi bật
    ]
    
    button_width, button_height = 350, 65
    center_x = WINDOW_SIZE[0] // 2
    y_start = 250
    spacing = 85

    novice_button = pygame.Rect(center_x - button_width // 2, y_start, button_width, button_height)
    skilled_button = pygame.Rect(center_x - button_width // 2, y_start + spacing, button_width, button_height)
    expert_button = pygame.Rect(center_x - button_width // 2, y_start + 2 * spacing, button_width, button_height)
    master_button = pygame.Rect(center_x - button_width // 2, y_start + 3 * spacing, button_width, button_height)
    
    buttons = [novice_button, skilled_button, expert_button, master_button]

    for i, (text, _, color) in enumerate(levels):
        draw_interactive_button(display, buttons[i], text, SMALL_FONT, color, HOVER_COLOR if color == WHITE else (color[0] + 30, color[1] + 30, color[2] + 30), BLACK, mouse_pos)

    # Nút Quay lại
    back_level_button = pygame.Rect(50, WINDOW_SIZE[1] - 80, 150, 50)
    draw_interactive_button(display, back_level_button, "Quay lại", SMALL_FONT, (150, 150, 150), (180, 180, 180), BLACK, mouse_pos)

def draw_mode_selection(display, mouse_pos):
    global random_button, create_room_button, back_mode_button
    display.fill(BACKGROUND_COLOR)
    
    # Tiêu đề
    title_text = HEADER_FONT.render("ĐÁNH VỚI NGƯỜI", True, BLACK)
    display.blit(title_text, title_text.get_rect(center=(WINDOW_SIZE[0] // 2, 150)))
    
    # Định nghĩa và Vẽ các nút
    button_width, button_height = 400, 80
    center_x = WINDOW_SIZE[0] // 2
    
    random_button = pygame.Rect(center_x - button_width // 2, 350, button_width, button_height)
    create_room_button = pygame.Rect(center_x - button_width // 2, 500, button_width, button_height)
    
    draw_interactive_button(display, random_button, "Ngẫu nhiên (Online)", FONT, PRIMARY_COLOR, HOVER_COLOR, WHITE, mouse_pos)
    draw_interactive_button(display, create_room_button, "Tạo phòng / Gia nhập", FONT, PRIMARY_COLOR, HOVER_COLOR, WHITE, mouse_pos)
    
    # Ghi chú về mạng
    note_text = SMALL_FONT.render("Tính năng Online yêu cầu triển khai Server/Client.", True, (150, 0, 0))
    display.blit(note_text, note_text.get_rect(center=(center_x, 650)))
    
    # Nút Quay lại
    back_mode_button = pygame.Rect(50, WINDOW_SIZE[1] - 80, 150, 50)
    draw_interactive_button(display, back_mode_button, "Quay lại", SMALL_FONT, (150, 150, 150), (180, 180, 180), BLACK, mouse_pos)

def draw_game(display, mouse_pos):
    """Vẽ màn hình Game (Bàn cờ và Bảng thông tin)."""
    display.fill(BACKGROUND_COLOR) 
    
    # Bàn cờ chiếm gần hết màn hình
    board.draw(display) 

    # --- Bảng Thông tin (Menu trong Game) ---
    
    # Hiển thị Lượt đi
    turn_text = FONT.render(f"Lượt đi: {board.turn.capitalize()}", True, BLACK)
    display.blit(turn_text, (50, 10))
    
    # Nút Quay lại Menu
    quit_button = pygame.Rect(WINDOW_SIZE[0] - 200, 10, 150, 50)
    draw_interactive_button(display, quit_button, "MENU", SMALL_FONT, (200, 50, 50), (255, 70, 70), WHITE, mouse_pos)
    
    return quit_button
# --- Vòng lặp Chính ---
running = True
clock = pygame.time.Clock() # Dùng clock để kiểm soát FPS

while running:
    # Lấy vị trí chuột
    mx, my = pygame.mouse.get_pos()
    quit_rect = None

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Xử lý click dựa trên trạng thái game
                if GAME_STATE == "MENU":
                    handle_menu_click(mx, my)
                
                elif GAME_STATE == "LEVEL_SELECTION":
                    handle_level_selection_click(mx, my)

                elif GAME_STATE == "MODE_SELECTION":
                    handle_mode_selection_click(mx, my)
                
                elif GAME_STATE.startswith("GAME"): 
                    # Kiểm tra nút Quay lại Menu
                    if quit_rect and quit_rect.collidepoint(mx, my):
                        GAME_STATE = "MENU"
                        print("Quay lại Menu.")
                        continue 
                        
                    # Xử lý click bàn cờ
                    board.handle_click(mx, my)

    # --- Cập nhật Trạng thái Game và Vẽ ---
    
    if GAME_STATE == "MENU":
        draw_menu(screen, (mx, my))
    
    elif GAME_STATE == "LEVEL_SELECTION":
        draw_level_selection(screen, (mx, my))
    
    elif GAME_STATE == "MODE_SELECTION":
        draw_mode_selection(screen, (mx, my))

    elif GAME_STATE.startswith("GAME"):
        quit_rect = draw_game(screen, (mx, my))

        # Kiểm tra điều kiện thắng
        if board.is_in_checkmate('black'):
            print('White wins!')
            # Có thể chuyển sang màn hình "Game Over" thay vì Menu
            GAME_STATE = "MENU" 
        elif board.is_in_checkmate('white'):
            print('Black wins!')
            GAME_STATE = "MENU" 
    
    pygame.display.update()
    clock.tick(60) # Giới hạn 60 FPS để giảm tải CPU

pygame.quit()
sys.exit()