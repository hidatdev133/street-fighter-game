import pygame
import socket
pygame.init()
import socket
import pickle

# Thiết lập cửa sổ
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Street Fighter")

# Thiết lập framerate
clock = pygame.time.Clock()
FPS = 60

# Màu sắc
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)


# Font
count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)



# Hàm vẽ văn bản
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def send_fighter_data(conn, fighter):
    data = {
        'x': fighter.rect.x,
        'y': fighter.rect.y,
        'health': fighter.health,
        'action': fighter.action,
        # Thêm các thông tin khác của nhân vật nếu cần
    }
    conn.sendall(pickle.dumps(data))

# Chọn chế độ chơi trước khi chọn background
def select_mode():
    global selected_mode
    selected_mode = None
    draw_text("Select Mode", count_font, RED, SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 3)
    draw_text("1 - Player vs Player", score_font, RED, SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2)
    draw_text("2 - Player vs Computer", score_font, RED, SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2 + 50)
    pygame.display.update()
    selected = False
    while not selected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_mode = "player_vs_player"
                    selected = True
                    # Khởi tạo socket server
                    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_socket.bind(('localhost', 8000))
                    server_socket.listen(2)  # Chờ kết nối từ 2 client

                    print("Đang chờ kết nối từ player 1...")
                    player1_socket, player1_address = server_socket.accept()
                    print(f"Player 1 đã kết nối từ {player1_address}")

                    print("Đang chờ kết nối từ player 2...")
                    player2_socket, player2_address = server_socket.accept()
                    print(f"Player 2 đã kết nối từ {player2_address}")

                    # Vẽ văn bản khi kết nối thành công
                    screen.fill(WHITE)
                    draw_text("player_player", count_font, RED, SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 3)
                    pygame.display.update()

                    # Đóng kết nối
                    player1_socket.close()
                    player2_socket.close()
                    server_socket.close()
                elif event.key == pygame.K_2:
                    selected_mode = "player_vs_computer"
                    selected = True
                    # Khởi tạo socket server
                    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    server_socket.bind(('localhost', 8000))
                    server_socket.listen(1)
                    print("Đang chờ kết nối từ client...")
                    client_socket, client_address = server_socket.accept()

                    # Vẽ văn bản khi kết nối thành công
                    screen.fill(WHITE)
                    draw_text("player_vs_computer", count_font, RED, SCREEN_WIDTH / 2 - 450, SCREEN_HEIGHT / 3)
                    pygame.display.update()
                    
                    # Gửi dữ liệu cho client (nếu cần)
                    data = "Dữ liệu từ server"
                    client_socket.sendall(data.encode())
                    
                    # Đóng kết nối
                    client_socket.close()
                    server_socket.close()
                  
# Chọn chế độ chơi
select_mode()

# Game loop
time_remaining = 60   # Thời gian ban đầu
while True:
    

    clock.tick(FPS)

    # Xử lý sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()  # Thoát khỏi chương trình khi người chơi đóng cửa sổ

    # Cập nhật màn hình
    pygame.display.update()

# Kết thúc pygame
pygame.quit()
