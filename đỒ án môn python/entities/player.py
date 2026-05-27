import pygame
import os
from entities.base import BaseEntity

class Player(BaseEntity):
    def __init__(self, x: float, y: float):
        self.flip = False
        self.base_path = os.path.join("assets", "images", "player")
        
        # Khởi tạo lớp cha 
        super().__init__(x, y, os.path.join(self.base_path, "dung im.png"))
        
        # Các biến điều khiển di chuyển
        self.speed = 100
        self.direction = pygame.Vector2(0, 0)
        self.display_size = (80, 80) 
        self.attack_cooldown = 250  # Thời gian chờ giữa 2 phát bắn (300ms = 0.3 giây)
        self.last_shot_time = 0

        # Quản lý Animation
        self.animations = {'idle': [], 'up': [], 'down': [], 'right': [], 'left': []}
        self.current_state = 'idle'
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.12
        
        self._load_all_animations()
        
        # Stats cấp độ va nhân vật
        self.level = 1
        self.xp = 0
        self.xp_next_level = 200
        self.max_health = 100
        self.current_health = 100
        
        # CHỈ SỐ VŨ KHÍ GỐC 
        self.bullet_damage = 15    # Sát thương đạn ban đầu
        self.bullet_speed = 400   # Tốc độ đạn ban đầu
        self.pierce_count = 1       # Số mục tiêu xuyên qua mặc định (1 = không xuyên, biến mất khi chạm con đầu tiên)
        self.multi_shot = 1         # Số tia đạn bắn ra mặc định

    def can_shoot(self):
        """Kiểm tra xem súng đã làm mát xong chưa"""
        current_time = pygame.time.get_ticks() 
        if current_time - self.last_shot_time >= self.attack_cooldown:
            self.last_shot_time = current_time 
            return True
        return False
    
    def _extract_frames(self, path):
        frames = []
        if not os.path.exists(path): return frames
        try:
            sheet = pygame.image.load(path).convert_alpha()
            h = sheet.get_height()
            num_frames = sheet.get_width() // h
            for i in range(num_frames):
                rect = pygame.Rect(i * h, 0, h, h)
                frame = sheet.subsurface(rect)
                frames.append(pygame.transform.scale(frame, self.display_size))
        except: 
            pass
        return frames

    def _load_all_animations(self):
        self.animations['idle'] = self._extract_frames(os.path.join(self.base_path, "dung im.png"))
        self.animations['down'] = self._extract_frames(os.path.join(self.base_path, "di xuong.png")) 
        self.animations['up'] = self._extract_frames(os.path.join(self.base_path, "di len.png")) 
        self.animations['right'] = self._extract_frames(os.path.join(self.base_path, "di chuyen.png")) 

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.direction.x = keys[pygame.K_d] - keys[pygame.K_a]
        self.direction.y = keys[pygame.K_s] - keys[pygame.K_w]
        
        if self.direction.length() > 0:
            self.direction = self.direction.normalize()

    def update(self, dt):
        old_state = self.current_state
    
        # 1. Xác định hướng lật ảnh nhân vật
        if self.direction.x > 0:
            self.flip = False
        elif self.direction.x < 0:
            self.flip = True

        # 2. Xử lý di chuyển và trạng thái hoạt ảnh
        if self.direction.length() > 0:
            self.pos += self.direction * self.speed * dt 
            if abs(self.direction.y) > abs(self.direction.x):
                self.current_state = 'up' if self.direction.y < 0 else 'down' 
            else:
                self.current_state = 'right' 
        else:
            self.current_state = 'idle' 

        # 3. Đổi trạng thái animation thì reset frame
        if old_state != self.current_state:
            self.current_frame = 0 

        # 4. Hiển thị chuyển động mượt mà
        anim_list = self.animations.get(self.current_state, [])
        if anim_list:
            if self.current_state == 'idle':
                self.current_frame = 0
            else:
                self.animation_timer += dt
                if self.animation_timer >= self.animation_speed:
                    self.animation_timer = 0
                    self.current_frame = (self.current_frame + 1) % len(anim_list)
            
            raw_image = anim_list[self.current_frame] 
            self.image = pygame.transform.flip(raw_image, self.flip, False)
            self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y))) 
            self.mask = pygame.mask.from_surface(self.image) 

    def gain_xp(self, amount: int):
        self.xp += amount
        if self.xp >= self.xp_next_level:
            self.level_up()

    def level_up(self):
        self.xp -= self.xp_next_level
        self.level += 1
        self.xp_next_level = int(self.xp_next_level * 1.5)
        self.max_health += 20
        self.current_health = self.max_health

    def get_shoot_pos(self):
        """Tính vị trí bắn ra đạn ngay tại tầm tay/vũ khí"""
        base_x, base_y = self.rect.center
        offset_x = -5  
        offset_y = 20   
        spawn_x = base_x + offset_x
        spawn_y = base_y + offset_y
        return spawn_x, spawn_y