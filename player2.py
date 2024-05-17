import pygame
from fighter import Fighter
import socket
import sys
import pickle
import threading

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

# Biến trò chơi
intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]  # điểm của người chơi. [p1, p2]
round_over = False
round_drawn = False
ROUND_OVER_COOLDOWN = 2000  # thời gian chờ đợi để bắt đầu game mới

# Biến nhân vật
# -----------------------------------------------------------
#warrior
WARRIOR_SIZE = 162
WARRIOR_SCALE = 4
WARRIOR_OFFSET = [72, 56]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
#xác định số bước của mỗi animation
WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
# Biến spritesheets
warrior_sheet = pygame.image.load("assets/images/warrior/Sprites/warrior.png").convert_alpha()

# -----------------------------------------------------------
#wizard
WIZARD_SIZE = 250
WIZARD_SCALE = 3
WIZARD_OFFSET = [112, 107]
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]
WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]
wizard_sheet = pygame.image.load("assets/images/wizard/Sprites/wizard.png").convert_alpha()

# -----------------------------------------------------------
#samurai
SAMURAI_SIZE = 200
SAMURAI_SCALE = 3.5
SAMURAI_OFFSET = [90, 75]
SAMURAI_DATA = [SAMURAI_SIZE, SAMURAI_SCALE, SAMURAI_OFFSET]
SAMURAI_ANIMATION_STEPS = [4, 8, 2, 4, 4, 3, 7]
samurai_sheet = pygame.image.load("assets/images/samurai/Sprites/samurai.png").convert_alpha()

# -----------------------------------------------------------
#lancer
LANCER_SIZE = 150
LANCER_SCALE = 4.5
LANCER_OFFSET = [67, 54]
LANCER_DATA = [LANCER_SIZE, LANCER_SCALE, LANCER_OFFSET]
LANCER_ANIMATION_STEPS = [8, 8, 2, 5, 5, 3, 8]
lancer_sheet = pygame.image.load("assets/images/lancer/Sprites/lancer.png").convert_alpha()


# Âm nhạc và âm thanh
pygame.mixer.init()
pygame.mixer.music.load("assets/audio/music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)

#chiến binh
sword_fx = pygame.mixer.Sound("assets/audio/sword.wav")
sword_fx.set_volume(0.5)

#pháp sư
magic_fx = pygame.mixer.Sound("assets/audio/magic.wav")
magic_fx.set_volume(0.75)

# Font
count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)

# Hàm vẽ văn bản
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


# Biến hình nền
backgrounds = ["assets/images/background/background01.jpg",
               "assets/images/background/background02.jpg",
               "assets/images/background/background03.jpg",
               "assets/images/background/background04.jpg",
               "assets/images/background/background05.jpg"]
selected_background = 1  # Chỉ số của background mặc định
bg_images = [pygame.image.load(bg).convert_alpha() for bg in backgrounds]
bg_image = bg_images[selected_background]

# Biến hình ảnh chiến thắng
victory_img = pygame.image.load("assets/images/icons/victory.png").convert_alpha()
drawn_img = pygame.image.load("assets/images/icons/drawn.png").convert_alpha()
fighter1_win = pygame.image.load("assets/images/icons/fighter1win.png").convert_alpha()
fighter2_win= pygame.image.load("assets/images/icons/fighter2win.png").convert_alpha()

# Hàm vẽ văn bản
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Hàm vẽ background
def draw_bg():
    scale_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scale_bg, (0, 0))

# Hàm vẽ thanh máu cho nhân vật
def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(screen, WHITE, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(screen, RED, (x, y, 400, 30))
    pygame.draw.rect(screen, YELLOW, (x, y, 400 * ratio, 30))

# Hàm vẽ thời gian còn lại
def draw_timer(time_remaining):
    text = str(int(time_remaining))  # Chỉ hiển thị phần nguyên của thời gian
    # text_width, text_height = score_font.size(text)  # Lấy kích thước của văn bản
    # Tạo một font mới với kích thước lớn hơn
    bigger_font = pygame.font.Font("assets/fonts/turok.ttf", 70)
    draw_text(text, bigger_font, RED, 470, 0)  # Vẽ văn bản lớn hơn lên màn hình

# Biến lựa chọn nhân vật của người chơi 1
selected_fighter_1 = None
selected_fighter_2 = None

# Hàm để gửi dữ liệu
def send_data(received_socket):
    while True:
        fighter_state = fighter_2.get_state()
        data = pickle.dumps(fighter_state)
        try:
            received_socket.sendall(data)
        except socket.error as e:
            print(f"Socket error (send): {e}")
            break

# Hàm để nhận dữ liệu
def receive_data(received_socket):
    while True:
        try:
            data = received_socket.recv(1024)
            if data:
                fighter_state = pickle.loads(data)
                fighter_1.rect = fighter_state['rect']
                fighter_1.action = fighter_state['action']
                fighter_1.health = fighter_state['health']
                fighter_1.alive = fighter_state['alive']
                print(f"Data received: {fighter_state}")  # Thêm lệnh in để kiểm tra dữ liệu
            else:
                print("Connection closed by the other player.")
                break
        except socket.error as e:
            print(f"Socket error (recv): {e}")
            break

# Tạo socket client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('127.0.0.1', 8000))  # Kết nối với server

while True:
    received_socket_data = client_socket.recv(1024)
    if received_socket_data:
        break
local_addr = pickle.loads(received_socket_data)

# Tạo socket mới từ địa chỉ nhận được
received_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
received_socket.bind(local_addr)

# Nhận dữ liệu từ server (nếu có)
data = client_socket.recv(1024)
print(f"Nhận dữ liệu từ server: {data.decode()}")


# Hàm chọn nhân vật của người chơi 2
def select_fighter_2():
    screen.fill((0, 0, 0))  # Xóa màn hình bằng màu đen
    pygame.display.update()  # Cập nhật màn hình
    global selected_fighter_2
    draw_text("Player 2: Select your fighter", score_font, RED, SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 3)
    draw_text("Press '1' for Warrior or '2' for Wizard", score_font, RED, SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2 + 50)
    draw_text("Press '3' for Samurai or '4' for Lancer", score_font, RED, SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2 + 100)

    pygame.display.update()
    selected = False
    while not selected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_fighter_2 = 1  # Chọn nhân vật Warrior
                    selected = True
                elif event.key == pygame.K_2:
                    selected_fighter_2 = 2  # Chọn nhân vật Wizard
                    selected = True
                elif event.key == pygame.K_3:
                    selected_fighter_2 = 3  # Chọn nhân vật Samurai
                    selected = True
                elif event.key == pygame.K_4:
                    selected_fighter_2 = 4  # Chọn nhân vật Lancer
                    selected = True

# Nhận thông tin về lựa chọn của player1.py từ menu.py
fighter1_info = client_socket.recv(1024)
background_info = client_socket.recv(1024)
# Khởi tạo nhân vật và background dựa trên thông tin nhận được
fighter1 = pickle.loads(fighter1_info)
background = pickle.loads(background_info)
select_fighter_2()
# Cập nhật biến bg_image dựa trên background đã chọn
bg_image = pygame.transform.scale(bg_images[selected_background], (SCREEN_WIDTH, SCREEN_HEIGHT))

# Tạo nhân vật cho người chơi 1
if selected_fighter_1 == 1:
    fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
elif selected_fighter_1 == 2:
    fighter_1 = Fighter(1, 200, 310, False, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
elif selected_fighter_1 == 3:
    fighter_1 = Fighter(1, 200, 310, False, SAMURAI_DATA, samurai_sheet, SAMURAI_ANIMATION_STEPS, sword_fx)
elif selected_fighter_1 == 4:
    fighter_1 = Fighter(1, 200, 310, False, LANCER_DATA, lancer_sheet, LANCER_ANIMATION_STEPS, sword_fx)

# Tạo nhân vật cho người chơi 2
if selected_fighter_2 == 1:
    fighter_2 = Fighter(2, 700, 310, True, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
elif selected_fighter_2 == 2:
    fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
elif selected_fighter_2 == 3:
    fighter_2 = Fighter(2, 700, 310, True, SAMURAI_DATA, samurai_sheet, SAMURAI_ANIMATION_STEPS, sword_fx)
elif selected_fighter_2 == 4:
    fighter_2 = Fighter(2, 700, 310, True, LANCER_DATA, lancer_sheet, LANCER_ANIMATION_STEPS, sword_fx)
    

# Tạo luồng cho việc gửi và nhận dữ liệu
send_thread = threading.Thread(target=send_data, args=(received_socket,))
receive_thread = threading.Thread(target=receive_data, args=(received_socket,))

# Khởi chạy luồng
send_thread.start()
receive_thread.start()


# Game loop
try:
    running = True
    time_remaining = 60   # Thời gian ban đầu
    while running:
        clock.tick(FPS)

        # Vẽ background
        draw_bg()

        # Hiển thị thanh máu
        draw_health_bar(fighter_1.health, 20, 20)
        draw_health_bar(fighter_2.health, 580, 20)
        draw_text("P1: " + str(score[0]), score_font, RED, 20, 60)
        draw_text("P2: " + str(score[1]), score_font, RED, 580, 60)

        # Hiển thị thời gian còn lại
        draw_timer(int(time_remaining))

        # Cập nhật countdown
        if intro_count <= 0:
            time_remaining -= 1 / FPS
            # Di chuyển nhân vật
            
            send_data(received_socket)
            receive_data(received_socket)

        else:
            # Hiển thị đồng hồ đếm
            draw_text(str(intro_count), count_font, RED, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 3)
            # Cập nhật đồng hồ đếm
            if (pygame.time.get_ticks() - last_count_update) >= 1000:
                intro_count -= 1
                last_count_update = pygame.time.get_ticks()

        # Cập nhật nhân vật
        fighter_1.update()
        fighter_2.update()

        # Vẽ nhân vật
        fighter_1.draw(screen)
        fighter_2.draw(screen)

        # Kiểm tra thời gian còn lại
        if time_remaining <= 1:
            time_remaining = 0
            if round_drawn == False:
                if fighter_1.alive and fighter_2.alive:
                    round_drawn = True
                    round_over_time = pygame.time.get_ticks()
            else:
                # So sánh máu của hai nhân vật và tăng điểm cho nhân vật có máu ít hơn
                if fighter_1.health < fighter_2.health:
                    screen.blit(fighter2_win, (300, 150))
                elif fighter_1.health > fighter_2.health:
                    screen.blit(fighter1_win, (300, 150))
                else:
                    screen.blit(drawn_img, (310, 150))
                if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                    if fighter_1.health < fighter_2.health:
                        score[1] += 1
                    elif fighter_1.health > fighter_2.health:
                        score[0] += 1
                    round_drawn = False
                    intro_count = 3
                    time_remaining = 60
                    
                    # Khởi tạo lại nhân vật
                    if selected_fighter_1 == 1:
                        fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
                    elif selected_fighter_1 == 2:
                        fighter_1 = Fighter(1, 200, 310, False, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
                    elif selected_fighter_1 == 3:
                        fighter_1 = Fighter(1, 200, 310, False, SAMURAI_DATA, samurai_sheet, SAMURAI_ANIMATION_STEPS, sword_fx)
                    elif selected_fighter_1 == 4:
                        fighter_1 = Fighter(1, 200, 310, False, LANCER_DATA, lancer_sheet, LANCER_ANIMATION_STEPS, sword_fx)

                    if selected_fighter_2 == 1:
                        fighter_2 = Fighter(2, 700, 310, True, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
                    elif selected_fighter_2 == 2:
                        fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
                    elif selected_fighter_2 == 3:
                        fighter_2 = Fighter(2, 700, 310, True, SAMURAI_DATA, samurai_sheet, SAMURAI_ANIMATION_STEPS, sword_fx)
                    elif selected_fighter_2 == 4:
                        fighter_2 = Fighter(2, 700, 310, True, LANCER_DATA, lancer_sheet, LANCER_ANIMATION_STEPS, sword_fx)

        # Kiểm tra người chơi thua
        if round_over == False:
            if fighter_1.alive == False and fighter_2.alive == False:
                round_over = True
                round_over_time = pygame.time.get_ticks()
            elif fighter_1.alive == False and fighter_2.alive == True:
                score[1] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
            elif fighter_2.alive == False and fighter_1.alive == True:
                score[0] += 1
                round_over = True
                round_over_time = pygame.time.get_ticks()
                
        else:
            if fighter_1.alive == False and fighter_2.alive == False:
                # Hiển thị hình ảnh chiến thắng
                screen.blit(drawn_img, (360, 150))
            else: screen.blit(victory_img, (360, 150))
            if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
                round_over = False
                intro_count = 3
                time_remaining = 60

                if selected_fighter_1 == 1:
                    fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
                elif selected_fighter_1 == 2:
                    fighter_1 = Fighter(1, 200, 310, False, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
                elif selected_fighter_1 == 3:
                    fighter_1 = Fighter(1, 200, 310, False, SAMURAI_DATA, samurai_sheet, SAMURAI_ANIMATION_STEPS, sword_fx)
                elif selected_fighter_1 == 4:
                    fighter_1 = Fighter(1, 200, 310, False, LANCER_DATA, lancer_sheet, LANCER_ANIMATION_STEPS, sword_fx)

                if selected_fighter_2 == 1:
                    fighter_2 = Fighter(2, 700, 310, True, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
                elif selected_fighter_2 == 2:
                    fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
                elif selected_fighter_2 == 3:
                    fighter_2 = Fighter(2, 700, 310, True, SAMURAI_DATA, samurai_sheet, SAMURAI_ANIMATION_STEPS, sword_fx)
                elif selected_fighter_2 == 4:
                    fighter_2 = Fighter(2, 700, 310, True, LANCER_DATA, lancer_sheet, LANCER_ANIMATION_STEPS, sword_fx)

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()  # Thoát khỏi chương trình khi người chơi đóng cửa sổ

        # Gửi và nhận dữ liệu trong mỗi vòng lặp game loop
        send_data(received_socket)
        receive_data(received_socket)

        # Cập nhật màn hình
        pygame.display.update()
finally:
    if client_socket:
        client_socket.close()
    send_thread.join()
    receive_thread.join()
    pygame.quit()
    sys.exit()