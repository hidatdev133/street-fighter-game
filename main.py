import pygame
from fighter import Fighter
import random

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
WARRIOR_SIZE = 162
WARRIOR_SCALE = 4
WARRIOR_OFFSET = [72, 56]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]

WIZARD_SIZE = 250
WIZARD_SCALE = 3
WIZARD_OFFSET = [112, 107]
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]

# Âm nhạc và âm thanh
pygame.mixer.init()
pygame.mixer.music.load("assets/audio/music.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)
sword_fx = pygame.mixer.Sound("assets/audio/sword.wav")
sword_fx.set_volume(0.5)
magic_fx = pygame.mixer.Sound("assets/audio/magic.wav")
magic_fx.set_volume(0.75)


# Hàm vẽ văn bản
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Font
count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)

# Chọn chế độ chơi trước khi chọn background
def select_mode():
    global selected_mode
    selected_mode = None
    draw_text("Select Mode", count_font, RED, SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 3)
    draw_text("1 - Player vs Player", score_font, RED, SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 2)
    draw_text("2 - Player vs Computer", score_font, RED, SCREEN_WIDTH / 2 - 150, SCREEN_HEIGHT / 2 + 50)
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
                elif event.key == pygame.K_2:
                    selected_mode = "player_vs_computer"
                    selected = True
                  

# Chọn chế độ chơi
select_mode()

# Hàm chọn hành động của nhân vật thứ hai (NPC)
def select_npc_action():
    actions = ["UP", "LEFT", "RIGHT", "ATTACK"]
    return random.choice(actions)

# Biến hình nền
backgrounds = ["assets/images/background/background01.jpg",
               "assets/images/background/background02.jpg",
               "assets/images/background/background03.jpg",
               "assets/images/background/background04.jpg",
               "assets/images/background/background05.jpg"]
selected_background = 1  # Chỉ số của background mặc định
bg_images = [pygame.image.load(bg).convert_alpha() for bg in backgrounds]
bg_image = bg_images[selected_background]

# Biến spritesheets
warrior_sheet = pygame.image.load("assets/images/warrior/Sprites/warrior.png").convert_alpha()
wizard_sheet = pygame.image.load("assets/images/wizard/Sprites/wizard.png").convert_alpha()

# Biến hình ảnh chiến thắng
victory_img = pygame.image.load("assets/images/icons/victory.png").convert_alpha()
drawn_img = pygame.image.load("assets/images/icons/drawn.png").convert_alpha()
fighter1 = pygame.image.load("assets/images/icons/fighter1win.png").convert_alpha()
fighter2 = pygame.image.load("assets/images/icons/fighter2win.png").convert_alpha()

# Số bước trong mỗi animation
WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]

# Font
count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)

# Biến lựa chọn nhân vật của người chơi 1
selected_fighter_1 = None
selected_fighter_2 = None
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
    text_width, text_height = score_font.size(text)  # Lấy kích thước của văn bản
    # Tạo một font mới với kích thước lớn hơn
    bigger_font = pygame.font.Font("assets/fonts/turok.ttf", 70)
    draw_text(text, bigger_font, RED, 470, 0)  # Vẽ văn bản lớn hơn lên màn hình

# Hàm chọn nhân vật của người chơi 1
def select_fighter_1():
    screen.fill((0, 0, 0))  # Xóa màn hình bằng màu đen
    pygame.display.update()  # Cập nhật màn hình
    global selected_fighter_1
    draw_text("Player 1: Select your fighter", score_font, RED, SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 3)
    draw_text("Press '1' for Warrior or '2' for Wizard", score_font, RED, SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2)
    pygame.display.update()
    selected = False
    while not selected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    selected_fighter_1 = 1  # Chọn nhân vật Warrior
                    selected = True
                elif event.key == pygame.K_2:
                    selected_fighter_1 = 2  # Chọn nhân vật Wizard
                    selected = True

# Hàm chọn nhân vật của người chơi 2
def select_fighter_2():
    screen.fill((0, 0, 0))  # Xóa màn hình bằng màu đen
    pygame.display.update()  # Cập nhật màn hình
    global selected_fighter_2
    draw_text("Player 2: Select your fighter", score_font, RED, SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 3)
    draw_text("Press '1' for Warrior or '2' for Wizard", score_font, RED, SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2)
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

# Chọn background
def select_background():
    global selected_background, bg_image
    selected_background = 0
    bg_image = pygame.transform.scale(bg_images[selected_background], (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(bg_image, (0, 0))
    draw_text("Select Background", count_font, RED, SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 3)
    draw_text("Press LEFT/RIGHT arrow keys to select", score_font, RED, SCREEN_WIDTH / 2 - 250, SCREEN_HEIGHT / 2)
    draw_text("Press ENTER to start", score_font, RED, SCREEN_WIDTH / 2 - 200, SCREEN_HEIGHT / 2 + 50)
    pygame.display.update()
    selected = False
    while not selected:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_background = (selected_background - 1) % len(bg_images)
                    bg_image = pygame.transform.scale(bg_images[selected_background], (SCREEN_WIDTH, SCREEN_HEIGHT))
                    screen.blit(bg_image, (0, 0))
                    pygame.display.update()
                elif event.key == pygame.K_RIGHT:
                    selected_background = (selected_background + 1) % len(bg_images)
                    bg_image = pygame.transform.scale(bg_images[selected_background], (SCREEN_WIDTH, SCREEN_HEIGHT))
                    screen.blit(bg_image, (0, 0))
                    pygame.display.update()
                elif event.key == pygame.K_RETURN:
                    selected = True
    return selected_background

# Chọn background và nhân vật của người chơi 1 và người chơi 2
selected_background = select_background()
bg_image = bg_images[selected_background]
select_fighter_1()
select_fighter_2()

# Tạo nhân vật cho người chơi 1
if selected_fighter_1 == 1:
    fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
elif selected_fighter_1 == 2:
    fighter_1 = Fighter(1, 200, 310, False, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

# Tạo nhân vật cho người chơi 2
if selected_fighter_2 == 1:
    fighter_2 = Fighter(2, 700, 310, True, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
elif selected_fighter_2 == 2:
    fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

# Game loop
time_remaining = 60   # Thời gian ban đầu
while True:
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
        fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_2, round_over)
        if selected_mode == "player_vs_player":
            fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
        elif selected_mode == "player_vs_computer":
            npc_action = select_npc_action()
            # Xử lý hành động của NPC
            # if npc_action == "UP":
            #     fighter_2.move_up(SCREEN_WIDTH, SCREEN_HEIGHT)
            if fighter_1.alive:
                if npc_action == "LEFT":
                    fighter_2.move_left(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
                elif npc_action == "RIGHT":
                    fighter_2.move_right(SCREEN_WIDTH, SCREEN_HEIGHT, screen, fighter_1, round_over)
                elif npc_action == "ATTACK":
                    fighter_2.npc_attack(60, fighter_1)
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
                screen.blit(fighter2, (300, 150))
            elif fighter_1.health > fighter_2.health:
                screen.blit(fighter1, (300, 150))
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
                    fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS,
                                        sword_fx)
                elif selected_fighter_1 == 2:
                    fighter_1 = Fighter(1, 200, 310, False, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
                if selected_fighter_2 == 1:
                    fighter_2 = Fighter(2, 700, 310, True, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS,
                                        sword_fx)
                elif selected_fighter_2 == 2:
                    fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

    # Kiểm tra người chơi thua
    if round_over == False:
        if fighter_1.alive == False:
            score[1] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
        elif fighter_2.alive == False:
            score[0] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
    else:
        # Hiển thị hình ảnh chiến thắng
        screen.blit(victory_img, (360, 150))
        if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
            round_over = False
            intro_count = 3
            time_remaining = 60
            # Khởi tạo lại nhân vật
            if selected_fighter_1 == 1:
                fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS,
                                    sword_fx)
            elif selected_fighter_1 == 2:
                fighter_1 = Fighter(1, 200, 310, False, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)
            if selected_fighter_2 == 1:
                fighter_2 = Fighter(2, 700, 310, True, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS,
                                    sword_fx)
            elif selected_fighter_2 == 2:
                fighter_2 = Fighter(2, 700, 310, True, WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

    # Xử lý sự kiện
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()  # Thoát khỏi chương trình khi người chơi đóng cửa sổ

    # Cập nhật màn hình
    pygame.display.update()

# Kết thúc pygame
pygame.quit()
