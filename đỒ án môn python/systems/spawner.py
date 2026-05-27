import pygame
import random
from entities.enemy import Enemy
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT
from core.constants import WAYPOINTS
class WaveSpawner:
    def __init__(self, game):
        # Lưu trữ tham chiếu đến Game để có thể gọi player và nhóm enemies
        self.game = game 
        self.current_wave = 1
        self.enemies_to_spawn = 10 # Số lượng quái đợt 1
        self.spawn_timer = 0.0
        self.spawn_delay = 3.0 # Thời gian (giây) giữa mỗi lần sinh quái
        
        print(f"--- BẮT ĐẦU ĐỢT {self.current_wave} ---")

    def update(self, dt: float):
        # KIỂM TRA CHUYỂN ĐỢT: Nếu đã sinh hết quái và trên màn hình không còn quái
        if self.enemies_to_spawn <= 0 and len(self.game.enemies) == 0:
            self.current_wave += 1
            # Tăng độ khó: Nhiều quái hơn, sinh ra nhanh hơn
            self.enemies_to_spawn = 10 + (self.current_wave * 20) 
            self.spawn_delay = max(0.2, self.spawn_delay - 0.15) 
            print(f"--- BẮT ĐẦU ĐỢT {self.current_wave} ---")

        # LOGIC SINH QUÁI: Dựa trên bộ đếm thời gian
        if self.enemies_to_spawn > 0:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_timer = 0.0
                self.spawn_enemy()
                self.enemies_to_spawn -= 1


    def spawn_enemy(self):
        from core.constants import WAYPOINTS
        x, y = WAYPOINTS[0] # Xuất hiện tại điểm đầu tiên của đường đi
        
        skins = [
            "assets/images/enemy_blue slime.png",
            "assets/images/enemy_green slime.png",
            "assets/images/enemy_red slime.png"
        ]
        chosen_skin = random.choice(skins)
            
        # Truyền 'self.game' để Enemy có thể truy cập base_health
        new_enemy = Enemy(x, y, self.game, chosen_skin)
        self.game.enemies.add(new_enemy)