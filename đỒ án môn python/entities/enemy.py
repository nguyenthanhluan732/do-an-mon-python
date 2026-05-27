import pygame
from entities.base import BaseEntity

class Enemy(BaseEntity):
    def __init__(self, x, y, game, image_path):
        super().__init__(x, y, image_path)
        self.game = game
        
        # KÍCH THƯỚC QUÁI 
        self.display_size = (45, 45) 
        
        # Phân loại chỉ số gốc theo màu sắc
        if "red" in image_path.lower():
            base_hp, base_speed = 150, 60
        elif "green" in image_path.lower():
            base_hp, base_speed = 125, 80
        else:
            base_hp, base_speed = 75, 140
            
        # MỖI ROUND QUÁI TRÂU HƠN
        # Lấy số Wave hiện tại 
        current_wave = getattr(self.game.spawner, 'current_wave', 1)
        
        # TĂNG TIẾN SỨC MẠNH THEO LEVEL 
        hp_multiplier = 1.0 + (current_wave - 1) * 0.60
        speed_multiplier = 1.0 + (current_wave - 1) * 0.05
        
        self.max_health = int(base_hp * hp_multiplier)
        self.speed = base_speed * speed_multiplier
        self.current_health = self.max_health
        
        from core.constants import WAYPOINTS
        self.waypoints = WAYPOINTS
        self.current_waypoint_index = 0
        
        # Animation logic
        self.frames_right, self.frames_left = [], []
        self.current_frame = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.14
        self.facing_right = True
        
        self._setup_animation(image_path)

        if self.frames_right:
            self.image = self.frames_right[0]
            self.rect = self.image.get_rect(center=(x, y))
            self.mask = pygame.mask.from_surface(self.image)

    def _setup_animation(self, path):
        try:
            sheet = pygame.image.load(path).convert_alpha()
            h = sheet.get_height()
            num_frames = sheet.get_width() // h
            
            min_x, min_y = h, h
            max_x, max_y = 0, 0
            
            for i in range(num_frames):
                rect = pygame.Rect(i * h, 0, h, h)
                raw_frame = sheet.subsurface(rect)
                b_rect = raw_frame.get_bounding_rect()
                
                if b_rect.width > 0: 
                    if b_rect.left < min_x: min_x = b_rect.left
                    if b_rect.right > max_x: max_x = b_rect.right
                    if b_rect.top < min_y: min_y = b_rect.top
                    if b_rect.bottom > max_y: max_y = b_rect.bottom
            
            global_w = max_x - min_x
            global_h = max_y - min_y
            canvas_size = max(global_w, global_h)
            
            offset_x = (canvas_size - global_w) // 2
            offset_y = (canvas_size - global_h) // 2
            
            for i in range(num_frames):
                rect = pygame.Rect(i * h, 0, h, h)
                raw_frame = sheet.subsurface(rect)
                
                canvas = pygame.Surface((canvas_size, canvas_size), pygame.SRCALPHA)
                blit_x = offset_x - min_x
                blit_y = offset_y - min_y
                canvas.blit(raw_frame, (blit_x, blit_y))
                
                final_f = pygame.transform.scale(canvas, self.display_size)
                self.frames_right.append(final_f)
                self.frames_left.append(pygame.transform.flip(final_f, True, False))
                
        except Exception as e:
            print(f"Lỗi nạp ảnh: {e}")

    def take_damage(self, amount):
        self.current_health -= amount
        if self.current_health <= 0:
            self.kill()
    def update(self, dt):
        # Logic di chuyển
        if self.current_waypoint_index < len(self.waypoints):
            target = pygame.Vector2(self.waypoints[self.current_waypoint_index])
            dir_vec = target - self.pos
            if dir_vec.length() < 5:
                self.current_waypoint_index += 1
            else:
                dir_vec = dir_vec.normalize()
                self.pos += dir_vec * self.speed * dt
                self.facing_right = dir_vec.x >= 0
        else:
            self.game.base_health -= 3
            self.kill()

        if self.frames_right:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames_right)
                
                self.image = self.frames_right[self.current_frame] if self.facing_right else self.frames_left[self.current_frame]
                self.mask = pygame.mask.from_surface(self.image)
            
            self.rect.center = (round(self.pos.x), round(self.pos.y))

    def draw(self, surface):
        super().draw(surface)
        if self.current_health < self.max_health:
            bar_w, bar_h = 40, 5 
            bar_x, bar_y = self.rect.centerx - (bar_w // 2), self.rect.top - 8
            pygame.draw.rect(surface, (100, 0, 0), (bar_x, bar_y, bar_w, bar_h))
            fill = (self.current_health / self.max_health) * bar_w
            # Đảm bảo máu không bị âm làm lỗi vẽ thanh máu
            fill = max(0, fill) 
            pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, fill, bar_h))