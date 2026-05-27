import pygame
from abc import ABC, abstractmethod
import os

class BaseEntity(pygame.sprite.Sprite, ABC):
    BASE_SIZE = (40, 40)

    def __init__(self, x: float, y: float, visual):
        super().__init__()
        
        # KIỂM TRA BA TRƯỜNG HỢP CỦA THAM SỐ 
        if isinstance(visual, pygame.Surface):
            self.image = visual
            
        elif isinstance(visual, str) and "." in visual:
            
            try:
                raw_image = pygame.image.load(visual).convert_alpha()
                self.image = pygame.transform.scale(raw_image, self.BASE_SIZE)
            except pygame.error as e:
                print(f"Lỗi load ảnh {visual}: {e}")
                self.image = pygame.Surface(self.BASE_SIZE)
                self.image.fill((255, 0, 255)) 
        else:
            # 3. NẾU LÀ MÀU SẮC 
            self.image = pygame.Surface(self.BASE_SIZE)
            self.image.fill(visual)

        # Cập nhật vị trí và Vector hệ thống
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.Vector2(x, y)
        self.direction = pygame.Vector2(0, 0)
        self.speed = 200 

    @abstractmethod
    def update(self, dt: float):
        pass

    def draw(self, surface: pygame.Surface):
        """Hàm vẽ thực thể lên màn hình (Player và Enemy đều dùng)"""
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        surface.blit(self.image, self.rect)