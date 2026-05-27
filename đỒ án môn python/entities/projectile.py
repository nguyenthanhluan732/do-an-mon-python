import pygame
import math
import os
from entities.base import BaseEntity

class Projectile(BaseEntity):
    # Biến Class-level dùng chung để lưu trữ ảnh đã nạp vào RAM
    _cached_frames = None  

    def __init__(self, x: float, y: float, target_x: float, target_y: float, damage: int, speed: float, pierce: int):
        target_size = (70, 35) # Kích thước đạn hiển thị trên màn hình
        
        #CƠ CHẾ CACHE TỐI ƯU: CHỈ NẠP ẢNH TỪ Ổ CỨNG ĐÚNG 1 LẦN DUY NHẤT 
        if Projectile._cached_frames is None:
            Projectile._cached_frames = []
            anim_path = os.path.join("assets", "images", "projectiles", "bullet")
            
            for i in range(1, 9):
                file_name = f"Fire Arrow_Frame_{i:02d}.png" 
                full_path = os.path.join(anim_path, file_name)
                try:
                    frame_image = pygame.image.load(full_path).convert_alpha()
                    scaled_frame = pygame.transform.scale(frame_image, target_size)
                    Projectile._cached_frames.append(scaled_frame)
                except Exception as e:
                    print(f"Lỗi nạp frame {file_name}: {e}")
            
            # Phương án dự phòng nếu sai đường dẫn assets hoặc thiếu ảnh
            if not Projectile._cached_frames:
                fallback_surface = pygame.Surface(target_size, pygame.SRCALPHA)
                pygame.draw.rect(fallback_surface, (255, 100, 0), (0, 0, target_size[0], target_size[1]))
                Projectile._cached_frames.append(fallback_surface)

        # Lấy trực tiếp danh sách ảnh đã cache trong RAM, không đọc ổ cứng nữa
        self.frames = Projectile._cached_frames
        
        # Khởi tạo Sprite lớp cha an toàn
        super().__init__(x, y, self.frames[0])
        
        # Khởi tạo thông số hoạt ảnh
        self.current_frame = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.08 

        # Đồng bộ chỉ số chiến đấu
        self.speed = speed
        self.damage = damage
        self.pierce = pierce        
        self.hit_enemies = set()

        # Xác định vector góc hướng bay đến chuột
        target_pos = pygame.Vector2(target_x, target_y)
        self.direction = (target_pos - self.pos).normalize() if (target_pos - self.pos).length() > 0 else pygame.Vector2(1, 0)
        
        self._update_rotation()

    def _update_rotation(self):
        """Xoay viên đạn khớp chính xác góc bắn của chuột"""
        current_base_image = self.frames[self.current_frame]
        angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))
        angle_offset = -180 

        self.image = pygame.transform.rotate(current_base_image, angle + angle_offset)
        self.rect = self.image.get_rect(center=(round(self.pos.x), round(self.pos.y)))
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, dt: float):
        # Di chuyển viên đạn theo thời gian thực
        self.pos += self.direction * self.speed * dt
        
        # Hoạt ảnh đạn rực cháy chuyển động liên tục từ RAM cực mượt
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self._update_rotation()
        
        self.rect.center = (round(self.pos.x), round(self.pos.y))