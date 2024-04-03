import pygame
import random

class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
        #  đại diện cho người chơi mà nhân vật
        self.player = player

        # Kích thước của hình ảnh của nhân vật, được lấy từ dữ liệu (data) truyền vào
        self.size = data[0]
        
        # Hệ số tỉ lệ để tỉ lệ lại kích thước hình ảnh của nhân vật.
        self.image_scale = data[1]
        
        #  Dịch chuyển (offset) của hình ảnh, có thể được sử dụng để căn chỉnh vị trí hiển thị của nhân vật.
        self.offset = data[2]

        # xem nhân vật có bị lật ngược hay không
        self.flip = flip

        # Một danh sách các hình ảnh được tải từ sprite_sheet và được sử dụng để tạo các hoạt cảnh (animations) của nhân vật.
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0 #0: idle #1 run #2 jump #3 attack1 #4 attack2 #5 hit #6 death
        
        # Chỉ số của frame hình ảnh đang được hiển thị trong hoạt cảnh hiện tại.
        self.frame_index = 0
        
        # Hình ảnh hiện tại của nhân vật, được cập nhật từ danh sách hoạt cảnh (animation_list).
        self.image = self.animation_list[self.action][self.frame_index]
        
        # Thời gian cuối cùng mà hình ảnh của nhân vật được cập nhật.
        self.update_time = pygame.time.get_ticks()
        
        #  Đối tượng pygame.Rect đại diện cho vị trí và kích thước của nhân vật trong trò chơi.
        self.rect = pygame.Rect((x,y, 80, 180))
        
        # Vận tốc theo trục y của nhân vật, được sử dụng cho việc nhảy và rơi.
        self.vel_y = 0
        
        self.running = False
        self.jump = False
        
        # Một biến boolean xác định xem nhân vật đang thực hiện hành động tấn công hay không.
        self.attacking = False
        self.attack_type = 0
        
        # Thời gian cooldown giữa các hành động tấn công.
        self.attack_cooldown = 0
        self.attack_sound = sound
        
        #  Một biến boolean xác định xem nhân vật có đang bị tấn công hay không.
        self.hit = False
        self.health = 100
        self.alive = True


    # sprite_sheet chứa tất cả các frames của hoạt ảnh cho nhân vật hoặc đối tượng trong trò chơi.
    # animation_steps chứa các hành động idle, run,...
    def load_images(self, sprite_sheet, animation_steps):
        #trích xuất các hình ảnh từ sprite sheet
        animation_list = []
        # y = index, animation = animation_steps
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            # lặp qua số lượng frames cho mỗi hành động trong animation
            for x in range(animation):
                # cắt ra một phần của sprite_sheet, tức là một frame hình ảnh cụ thể, để tạo thành một frame của hoạt ảnh 
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list


    def move_left(self, screen_width, screen_height, surface, target, round_over):
        SPEED = 10
        dx = -SPEED

        if self.attacking == False and self.alive == True and round_over == False:
            self.running = True
            self.rect.x -= SPEED
        # đảm bảo người chơi vẫn ở trên màn hình
        # nhân vật di chuyển qua biên trái của màn hình
        if self.rect.left + dx < 0:
            # chuyển nhân vật đến biên trái của màn hình.
            dx = -self.rect.left
        # nếu vị trí cạnh phải của nhân vật cộng với khoảng cách di chuyển
        if self.rect.right + dx > screen_width:
            # chuyển nhân vật đến biên phải của màn hình.
            dx = screen_width - self.rect.right
        #đảm bảo người chơi đối mặt với nhau
        #target đang nằm bên phải của nhân vật.
        if target.rect.centerx > self.rect.centerx:
            # nhân vật không cần phải được lật ngược theo trục hoành để hướng về target
            self.flip = False
        else:
            self.flip = True

         # Xác định khoảng cách giữa nhân vật của máy tính và đối tượng mục tiêu
        distance_to_target = abs(target.rect.centerx - self.rect.centerx)
        # Nếu khoảng cách lớn hơn một ngưỡng nhất định, di chuyển lại gần đối tượng mục tiêu
        if distance_to_target > 200:
            if target.rect.centerx > self.rect.centerx:
                dx = SPEED
            self.running = True

        #áp dụng thời gian hồi chiêu tấn công
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        #cập nhật vị trí người chơi
        self.rect.x += dx

    def move_right(self, screen_width, screen_height, surface, target, round_over):
        SPEED = 10
        dx = SPEED

        if self.attacking == False and self.alive == True and round_over == False:
            self.running = True
            self.rect.x += SPEED
        # đảm bảo người chơi vẫn ở trên màn hình
        # nhân vật di chuyển qua biên trái của màn hình
        if self.rect.left + dx < 0:
            # chuyển nhân vật đến biên trái của màn hình.
            dx = -self.rect.left
        # nếu vị trí cạnh phải của nhân vật cộng với khoảng cách di chuyển
        if self.rect.right + dx > screen_width:
            # chuyển nhân vật đến biên phải của màn hình.
            dx = screen_width - self.rect.right
        if target.rect.centerx > self.rect.centerx:
            # nhân vật không cần phải được lật ngược theo trục hoành để hướng về target
            self.flip = False
        else:
            self.flip = True

        # Xác định khoảng cách giữa nhân vật của máy tính và đối tượng mục tiêu
        distance_to_target = abs(target.rect.centerx - self.rect.centerx)
        # Nếu khoảng cách lớn hơn một ngưỡng nhất định, di chuyển lại gần đối tượng mục tiêu
        if distance_to_target > 200:
            if target.rect.centerx < self.rect.centerx:
                dx = -SPEED
            self.running = True

        #áp dụng thời gian hồi chiêu tấn công
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        #cập nhật vị trí người chơi
        self.rect.x += dx   

    # def move_up(self, screen_width, screen_height, screen, round_over):
    #     GRAVITY = 2
    #     dy = 0
    #     if self.attacking == False and self.alive == True and round_over == False:
    #         if self.jump == False:
    #             self.vel_y = -30
    #             self.jump = True
    #         self.vel_y += GRAVITY
    #         dy += self.vel_y
    #         # Kiểm tra xem nếu vị trí cạnh dưới của nhân vật cộng với khoảng cách di chuyển dy lớn hơn chiều cao của màn hình trừ 110
    #         if self.rect.bottom + dy > screen_height - 110:
    #             # ngăn nhân vật rơi xuống
    #             self.vel_y = 0
    #             self.jump = False
    #             # điều chỉnh dy để nhân vật không thể vượt ra ngoài biên dưới của màn hình
    #             dy = screen_height - 110 - self.rect.bottom
    #         self.rect.y += dy
        
    def npc_attack(self, attack_cooldown_max, target):
        self.attack_cooldown_max = 60
        
        # Kiểm tra xem nhân vật của máy tính có đang ở gần đối tượng mục tiêu hay không
        distance_to_target = abs(target.rect.centerx - self.rect.centerx)
        if distance_to_target < 300:  # Điều kiện này có thể được điều chỉnh tùy thuộc vào khoảng cách mong muốn
            #áp dụng thời gian hồi chiêu tấn công
            # Kiểm tra xem đã hết thời gian cooldown chưa
            if self.attack_cooldown == 0:
                # Chọn ngẫu nhiên loại tấn công
                self.attack_type = random.choice([1, 2])  # Chọn ngẫu nhiên giữa loại tấn công 1 và 2
                
                # Thực hiện tấn công
                self.attacking = True
                self.attack_sound.play()
                attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
                if attacking_rect.colliderect(target.rect):
                    target.health -= 10
                    target.hit = True
                # Thiết lập thời gian cooldown lại
                self.attack_cooldown = self.attack_cooldown_max
                
            else:
                # Giảm thời gian cooldown đi 1 trong mỗi vòng lặp
                self.attack_cooldown -= 1


    def move(self, screen_width, screen_height, surface, target, round_over):
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        #lấy phím bấm
        key = pygame.key.get_pressed()

        #k tấn công, còn sống, chưa hết round
        if self.attacking == False and self.alive == True and round_over == False:
            #check player 1 controls
            if self.player == 1:
                #movement
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True

                #jump
                if key[pygame.K_w] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True

                #attack
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)
                    #determine which attack type was used
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    if key[pygame.K_t]:
                        self.attack_type = 2


            #check player2 controls
            if self.player == 2:
            #movement
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True

                #jump
                if key[pygame.K_UP] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True

                #attack
                if key[pygame.K_j] or key[pygame.K_k]:
                    self.attack(target)
                    #determine which attack type was used
                    if key[pygame.K_j]:
                        self.attack_type = 1
                    if key[pygame.K_k]:
                        self.attack_type = 2

        #áp dụng trong lực
        self.vel_y += GRAVITY
        dy += self.vel_y

        #đảm bảo người chơi vẫn ở trên màn hình
        # nhân vật di chuyển qua biên trái của màn hình
        if self.rect.left + dx < 0:
            # chuyển nhân vật đến biên trái của màn hình.
            dx = -self.rect.left
        # nếu vị trí cạnh phải của nhân vật cộng với khoảng cách di chuyển
        if self.rect.right + dx > screen_width:
            # chuyển nhân vật đến biên phải của màn hình.
            dx = screen_width - self.rect.right

        # Kiểm tra xem nếu vị trí cạnh dưới của nhân vật cộng với khoảng cách di chuyển dy lớn hơn chiều cao của màn hình trừ 110
        if self.rect.bottom + dy > screen_height - 110:
            # ngăn nhân vật rơi xuống
            self.vel_y = 0
            self.jump = False
            # điều chỉnh dy để nhân vật không thể vượt ra ngoài biên dưới của màn hình
            dy = screen_height - 110 - self.rect.bottom

        #đảm bảo người chơi đối mặt với nhau
        #target đang nằm bên phải của nhân vật.
        if target.rect.centerx > self.rect.centerx:
            # nhân vật không cần phải được lật ngược theo trục hoành để hướng về target
            self.flip = False
        else:
            self.flip = True

        #áp dụng thời gian hồi chiêu tấn công
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        #cập nhật vị trí người chơi
        self.rect.x += dx
        self.rect.y += dy

    #xử lý cập nhật hoạt ảnh
    def update(self):
        #kiểm tra xem người chơi đang thực hiện hành động gì
        #máu < 0
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6) #6: death
        #máu > 0 và đang bị tấn công
        elif self.hit == True:
            self.update_action(5) #5: hit
        #máu > 0, k bị tấn công và đang tấn công 
        elif self.attacking == True:
            # nếu đang tấn công loại 1
            if self.attack_type == 1:
                self.update_action(3) #3: attack1
            # nếu đang tấn công loại 2
            elif self.attack_type == 2:
                self.update_action(4) #4: attack2
        # nếu máu > 0, k bị tấn công, k tấn công và đang nhảy
        elif self.jump == True:
            self.update_action(2) #2: jump
        elif self.running == True:
            self.update_action(1) #1: run
        else:
            self.update_action(0) #0: idle

        # thời gian cooldown giữa các bước cập nhật hình ảnh của nhân vật trong hoạt cảnh.
        animation_cooldown = 50
        #cập nhật hình ảnh 
        # là hình ảnh hiện tại của nhân vật, dựa trên hành động và frame hiện tại.
        self.image = self.animation_list[self.action][self.frame_index]
        
        # ------------------------------------------
        #kiểm tra xem đã đủ thời gian trôi qua kể từ lần cập nhật cuối cùng chưa
        # pygame.time.get_ticks: thời gian hiện tại trong trò chơi
        # self.update_time: biến này lưu thời điểm cuối cùng mà frame của nhân vật đã được cập nhật.
        # Khi thời gian hiện tại trừ đi self.update_time lớn hơn animation_cooldown, có nghĩa là đã đủ thời gian để cập nhật frame mới. Khi đó, chỉ số frame (self.frame_index) được tăng lên một đơn vị. Sau đó, self.update_time được cập nhật với thời điểm hiện tại, để chu kỳ cooldown mới bắt đầu tính toán từ thời điểm hiện tại.
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        # -----------------------------------------------------
        #kiểm tra nếu animation kết thúc
        #  kiểm tra xem chỉ số của frame hiện tại đã vượt quá số lượng frame có trong hoạt cảnh của hành động đang thực hiện hay chưa.
        if self.frame_index >= len(self.animation_list[self.action]):
            #nếu người chơi chết và kết thúc hoạt ảnh
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) -1
            else:
                self.frame_index = 0
                #kiểm tra xem một cuộc tấn công đã được thực hiện chưa
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                #nếu nhân vật đã nhận sát thương
                #check if an attack was executed
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                #check if damage was taken
                if self.action == 5:
                    self.hit = False
                    #nếu người chơi đang ở giữa một cuộc tấn công thì cuộc tấn công sẽ dừng lại
                    self.attacking = False  
                    self.attacking_cooldown = 20    

    def attack(self, target):
        # nếu đã thực hiện tấn công xong
        if self.attack_cooldown == 0:
            #thực hiện tấn công
            self.attacking = True
            self.attack_sound.play()
            # Tạo một hình chữ nhật attacking_rect để đại diện cho khu vực của cuộc tấn công. Khu vực này được xác định bằng cách lấy tọa độ trung tâm của nhân vật, sau đó mở rộng ra phía trước và sau nhân vật với chiều dài là gấp đôi chiều rộng của nhân vật (dựa trên hướng nhân vật đang hướng).
            attacking_rect = pygame.Rect(self.rect.centerx - (2* self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)

            # Kiểm tra va chạm giữa attacking_rect và target.rect (vùng cơ bản của mục tiêu). Nếu hai hình chữ nhật này chồng lấn (collide), tức là cuộc tấn công đã đạt đến mục tiêu.
            # Nếu cuộc tấn công đã trúng mục tiêu, mục tiêu sẽ mất một lượng máu và bị đánh trúng 
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

    def update_action(self, new_action):
        #kiểm tra xem hành động mới có khác với hành động trước không
        if new_action != self.action:
            self.action = new_action
            #cập nhật cài đặt hoạt ảnh
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    # vẽ nhân vật lên một bề mặt cụ thể (surface), chẳng hạn như màn hình trò chơi.
    def draw(self, surface):
        # self.image là hình ảnh của nhân vật.
        # self.flip là một cờ chỉ ra xem nhân vật có đang hướng về phải hay không (nếu là False) hoặc hướng về trái (nếu là True).
        img = pygame.transform.flip(self.image, self.flip, False)
        # blit() được sử dụng để vẽ hình ảnh của nhân vật lên bề mặt được chỉ định (surface).
        # img là hình ảnh của nhân vật đã được lật nếu cần.
        # (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)) là tọa độ (x, y) của hình ảnh trên bề mặt. Tọa độ này được tính dựa trên tọa độ của hình chữ nhật giới hạn của nhân vật (self.rect), và được điều chỉnh bởi offset và tỉ lệ hình ảnh (self.image_scale).
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))

