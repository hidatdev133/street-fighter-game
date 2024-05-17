import pygame
import socket
import pickle
pygame.init()

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

def setup_server_connections():
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

    return player1_socket, player2_socket, server_socket

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
                    try:
                        player1_socket, player2_socket, server_socket = setup_server_connections()

                        # -----------------------------------------------
                        # Gửi tín hiệu cho player1.py để yêu cầu chọn nhân vật và background
                        player1_socket.sendall(b'select_fighter_and_bg')

                        # Nhận thông tin về lựa chọn của player1.py
                        fighter1_info = player1_socket.recv(1024)
                        background_info = player1_socket.recv(1024)

                        # Gửi thông tin cho player2.py
                        player2_socket.sendall(fighter1_info)
                        player2_socket.sendall(background_info)
                        # -----------------------------------------------
                        
                        # Nhận thông tin về lựa chọn của player2.py
                        fighter2_info = player2_socket.recv(1024)
                        # Gửi thông tin cho player1.py
                        player1_socket.sendall(fighter2_info)

                        # Gửi thông tin socket cho player1.py
                        pickled_player1_socket = pickle.dumps(player1_socket)
                        player1_socket.sendall(pickled_player1_socket)

                        # Gửi thông tin socket cho player2.py
                        pickled_player2_socket = pickle.dumps(player2_socket)
                        player2_socket.sendall(pickled_player2_socket)

                        # Đóng kết nối
                        player1_socket.close()
                        player2_socket.close()
                        server_socket.close()
                    except Exception as e:
                        print("Lỗi khi kết nối:", e)
                elif event.key == pygame.K_2:
                    selected_mode = "player_vs_computer"
                    selected = True
                    try:
                        # Khởi tạo socket server
                        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        server_socket.bind(('127.0.0.1', 8001))
                        server_socket.listen(1)
                        print("Đang chờ kết nối từ client...")
                        client_socket, client_address = server_socket.accept()

                        # Vẽ văn bản khi kết nối thành công
                        screen.fill(WHITE)
                        draw_text("player_vs_computer", count_font, RED, SCREEN_WIDTH / 2 - 450, SCREEN_HEIGHT / 3)
                        pygame.display.update()
                        
                        # Gửi dữ liệu cho client (nếu cần)
                        data = "Dữ liệu từ server"
                        client_socket.sendall(data)
                        
                        # Đóng kết nối
                        client_socket.close()
                        server_socket.close()
                    except Exception as e:
                        print("Lỗi khi kết nối:", e)

# Chọn chế độ chơi
select_mode()

# Game loop
time_remaining = 60   # Thời gian ban đầu
while True:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    pygame.display.update()

