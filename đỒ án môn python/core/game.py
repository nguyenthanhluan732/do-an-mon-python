import pygame
import random
import os
from core.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from entities.player import Player
from entities.projectile import Projectile
from systems.spawner import WaveSpawner
from systems.upgrades import UpgradeManager
from core.sound_manager import SoundManager

class Game:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TOWER DEFENSE")
        self.clock = pygame.time.Clock()
        self.running: bool = True
        self.dt: float = 0.0 
        
        # --- THÔNG SỐ CƠ BẢN ---
        self.base_health = 20 
        self.state = "MENU" 
        button_w, button_h = 220, 55
        center_x = SCREEN_WIDTH // 2 - button_w // 2
        try:
            raw_menu_img = pygame.image.load(os.path.join("assets", "menu_bg.png")).convert_alpha()
            self.menu_bg_image = pygame.transform.scale(raw_menu_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Không tìm thấy ảnh menu, sử dụng nền tối mặc định: {e}")
            self.menu_bg_image = None
        button_w, button_h = 220, 55
        self.play_btn_rect = pygame.Rect(center_x, 420, button_w, button_h)
        self.settings_btn_rect = pygame.Rect(center_x, 490, button_w, button_h)
        self.quit_btn_rect = pygame.Rect(center_x, 560, button_w, button_h)
        
        # --- THỰC THỂ ---
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        
        # HỆ THỐNG TRUYỀN ĐỐI TƯỢNG GAME ĐỂ SỬA MÁU BASE 
        self.spawner = WaveSpawner(self)
        self.upgrade_manager = UpgradeManager(self) 
        self.current_options = []
        
        # Khởi tạo Âm thanh hiệu ứng
        self.sounds = SoundManager()
        self.sounds.load_music("bgm_battle.mp3")
        self.sounds.play_music(volume=0.4)
        try:
            bg_path = os.path.join("assets", "images", "map.png")
            self.bg_image = pygame.image.load(bg_path).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.bg_image = None
            print("Lỗi: Không tìm thấy ảnh map.png")
            self.reset_game()

    def reset_game(self):
        self.base_health = 20
        self.state = "PLAYING"
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.spawner = WaveSpawner(self)
        self.upgrade_manager = UpgradeManager(self)
        self.current_options = []

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: 
                    mx, my = pygame.mouse.get_pos()
                    
                    # Kiểm tra bấm trúng nút nào
                    if self.play_btn_rect.collidepoint(mx, my):
                        self.state = "PLAYING" 
                    elif self.settings_btn_rect.collidepoint(mx, my):
                        print("Đang mở bảng Cài đặt... (Bạn có thể thêm tính năng sau)")
                    elif self.quit_btn_rect.collidepoint(mx, my):
                        self.running = False 
                continue
                
            if self.state == "GAMEOVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game() 
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                continue 

            if self.state == "UPGRADE" and event.type == pygame.KEYDOWN:
                selection = None
                if event.key == pygame.K_1: selection = 0
                elif event.key == pygame.K_2: selection = 1
                elif event.key == pygame.K_3: selection = 2
                
                if selection is not None and selection < len(self.current_options):
                    self.upgrade_manager.apply_upgrade(self.current_options[selection])
                    self.state = "PLAYING" 
            
            # LOGIC BẮN NHIỀU TIA (MULTI-SHOT) HÌNH QUẠT 
            elif self.state == "PLAYING" and event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    if self.player.can_shoot():
                        
                        mx, my = pygame.mouse.get_pos()
                        spawn_x, spawn_y = self.player.get_shoot_pos()
            
                        self.sounds.play_sfx("shoot")
                        base_vec = pygame.Vector2(mx - spawn_x, my - spawn_y)
                        
                        # Sinh ra số lượng tia dựa trên nâng cấp multi_shot
                        for i in range(self.player.multi_shot):
                            # Tính góc nghiêng lệch nhau 10 độ đối xứng tâm
                            angle = (i - (self.player.multi_shot - 1) / 2) * 10
                            rotated_vec = base_vec.rotate(angle)
                            target_pos = pygame.Vector2(spawn_x, spawn_y) + rotated_vec
                            
                            new_bullet = Projectile(
                                spawn_x, spawn_y, 
                                target_pos.x, target_pos.y,
                                self.player.bullet_damage,
                                self.player.bullet_speed,
                                self.player.pierce_count
                            ) 
                            self.bullets.add(new_bullet)

    def _update(self) -> None:
        if self.state == "MENU" or self.state == "UPGRADE":
            return 
        
        old_level = self.player.level
        
        self.player.handle_input()
        self.player.update(self.dt)
        self.enemies.update(self.dt)
        self.bullets.update(self.dt)
        self.spawner.update(self.dt)

        # - CƠ CHẾ VA CHẠM: XUYÊN THẤU VA CHỈ CỘNG EXP KHI QUÁI CHẾT HẲN 
        hits = pygame.sprite.groupcollide(self.bullets, self.enemies, False, False)
        
        for bullet in hits:
            for enemy in hits[bullet]:
                
                # 1. KIỂM TRA TRÍ NHỚ ĐẠN: Nếu đạn đã gây sát thương cho con này rồi thì bay xuyên qua tiếp!
                if hasattr(bullet, 'hit_enemies'):
                    if enemy in bullet.hit_enemies:
                        continue 
                    bullet.hit_enemies.add(enemy)

                # 2. XỬ LÝ SÁT THƯƠNG
                if hasattr(enemy, 'take_damage'):
                    enemy.take_damage(bullet.damage)
                    
                    is_dead = False
                    if not enemy.alive():
                        is_dead = True
                    elif hasattr(enemy, 'health') and enemy.health <= 0:
                        is_dead = True
                        enemy.kill()
                    elif hasattr(enemy, 'hp') and enemy.hp <= 0:
                        is_dead = True
                        enemy.kill()
                    if is_dead:
                        self.player.gain_xp(25) 
                    else:
                        break
                    # 3. TRỪ ĐIỂM XUYÊN THẤU
                    if hasattr(bullet, 'pierce'):
                        bullet.pierce -= 1
                        if bullet.pierce <= 0:
                            bullet.kill()
                            break 
                    else:
                        bullet.kill()
                        break

        # Kiểm tra thăng cấp để hiển thị bảng nâng cấp kĩ năng
        if self.player.level > old_level:
            self.state = "UPGRADE"
            self.current_options = self.upgrade_manager.get_random_options(3)
            
        # Tự động hủy đạn bay ra khỏi màn hình
        for bullet in self.bullets:
            if not self.screen.get_rect().collidepoint(bullet.rect.center):
                bullet.kill()
                
        # Điều kiện thất bại
        if self.base_health <= 0:
            self.base_health = 0
            self.state = "GAMEOVER"
            return 

    def _render(self) -> None:
        if self.state == "MENU":
            if self.menu_bg_image:
                self.screen.blit(self.menu_bg_image, (0, 0))
            elif self.bg_image:
                self.screen.blit(self.bg_image, (0, 0))
            else:
                self.screen.fill((20, 20, 20))
            
            # Lấy vị trí chuột thực tế để làm hiệu ứng phát sáng (Hover) khi trỏ vào nút
            mx, my = pygame.mouse.get_pos()
            font_btn = pygame.font.SysFont("Arial", 26, bold=True)
            
            # 1. Vẽ nút PLAY 
            play_color = (0, 230, 90) if self.play_btn_rect.collidepoint(mx, my) else (0, 170, 60)
            pygame.draw.rect(self.screen, play_color, self.play_btn_rect, border_radius=12)
            play_txt = font_btn.render("PLAY", True, (255, 255, 255))
            self.screen.blit(play_txt, play_txt.get_rect(center=self.play_btn_rect.center))
            
            # 2. Vẽ nút SETTINGS
            set_color = (255, 190, 0) if self.settings_btn_rect.collidepoint(mx, my) else (190, 140, 0)
            pygame.draw.rect(self.screen, set_color, self.settings_btn_rect, border_radius=12)
            set_txt = font_btn.render("SETTINGS", True, (255, 255, 255))
            self.screen.blit(set_txt, set_txt.get_rect(center=self.settings_btn_rect.center))
            
            # 3. Vẽ nút QUIT
            quit_color = (255, 70, 70) if self.quit_btn_rect.collidepoint(mx, my) else (180, 40, 40)
            pygame.draw.rect(self.screen, quit_color, self.quit_btn_rect, border_radius=12)
            quit_txt = font_btn.render("QUIT", True, (255, 255, 255))
            self.screen.blit(quit_txt, quit_txt.get_rect(center=self.quit_btn_rect.center))
            
            pygame.display.flip()
            return

        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        else:
            self.screen.fill((30, 30, 30))

        for enemy in self.enemies:
            enemy.draw(self.screen)
        self.player.draw(self.screen)
        self.bullets.draw(self.screen)

        font = pygame.font.SysFont("Arial", 24, bold=True)
        hp_surf = font.render(f"BASE HP: {self.base_health}", True, (255, 200, 0))
        self.screen.blit(hp_surf, (SCREEN_WIDTH // 2 - 80, 20))
        
        info_txt = font.render(f"Level: {self.player.level} | XP: {int(self.player.xp)}/{self.player.xp_next_level} | Wave: {self.spawner.current_wave}", True, (255, 255, 255))
        self.screen.blit(info_txt, (20, 20))

        if self.state == "UPGRADE":
            # 1. Vẽ lớp phủ tối màu 
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200)) 
            self.screen.blit(overlay, (0, 0))
            
            # 2. Vẽ Tiêu đề
            font_title = pygame.font.SysFont("Arial", 40, bold=True)
            title = font_title.render("LEVEL UP! CHON KY NANG", True, (255, 215, 0))
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
            self.screen.blit(title, title_rect)
            
            # 3. Tính toán vị trí để vẽ 3 lựa chọn ảnh
            icon_size = 400 # Kích thước ảnh nâng cấp 
            gap = 60       # Khoảng cách giữa các ảnh
            total_width = (icon_size * 3) + (gap * 2)
            start_x = (SCREEN_WIDTH - total_width) // 2
            y_pos = 200     # Vị trí y của các ảnh
            
            font_name = pygame.font.SysFont("Arial", 22, bold=True)
            font_note = pygame.font.SysFont("Arial", 18)

            # Khởi tạo cache ảnh trong Class Game nếu chưa có
            if not hasattr(self, 'upgrade_icons_cache'):
                self.upgrade_icons_cache = {}

            # 4. Vòng lặp vẽ 3 lựa chọn
            for i, opt in enumerate(self.current_options):
                # Tính x_pos cho mỗi lựa chọn
                x_pos = start_x + (icon_size + gap) * i
                
                # A. XỬ LÝ VÀ VẼ ẢNH 
                icon_image = None
                icon_path = opt['icon']

                # Lấy ảnh từ cache, nếu chưa có thì nạp và scale
                if icon_path in self.upgrade_icons_cache:
                    icon_image = self.upgrade_icons_cache[icon_path]
                else:
                    try:
                        raw_img = pygame.image.load(icon_path).convert_alpha()
                        icon_image = pygame.transform.scale(raw_img, (icon_size, icon_size))
                        self.upgrade_icons_cache[icon_path] = icon_image # Lưu vào cache
                    except:
                        # Nếu lỗi không nạp được ảnh, tạo surface màu tạm thời
                        icon_image = pygame.Surface((icon_size, icon_size))
                        icon_image.fill((255, 0, 255)) # Màu tím lỗi
                        self.upgrade_icons_cache[icon_path] = icon_image
                        print(f"Lỗi: Không tìm thấy ảnh nâng cấp tại {icon_path}")

                # Vẽ ảnh lên màn hình
                icon_rect = icon_image.get_rect(topleft=(x_pos, y_pos))
                self.screen.blit(icon_image, icon_rect)

                # --- B. VẼ TEXT GHI CHÚ 
                # Về tên nâng cấp ngay dưới ảnh
                name_txt = font_name.render(opt['name'], True, (255, 255, 255))
                name_rect = name_txt.get_rect(center=(icon_rect.centerx, y_pos + icon_size + 25))
                self.screen.blit(name_txt, name_rect)

                # Vẽ ghi chú phím bấm (1, 2, 3)
                note_txt = font_note.render(f"(Bấm phím {i+1})", True, (200, 200, 200))
                note_rect = note_txt.get_rect(center=(icon_rect.centerx, y_pos + icon_size + 50))
                self.screen.blit(note_txt, note_rect)
                
        if self.state == "GAMEOVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180)) 
            self.screen.blit(overlay, (0, 0))

            font_big = pygame.font.SysFont("Arial", 64, bold=True)
            msg = font_big.render("GAME OVER", True, (255, 50, 50))
            self.screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50)))
            
            retry_txt = font.render("Bam 'R' đe choi lai hoac 'ESC' đe thoat", True, (255, 255, 255))
            self.screen.blit(retry_txt, retry_txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30)))

        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.dt = self.clock.tick(FPS) / 1000.0
            if self.dt > 0.1: self.dt = 0.1 
            self._handle_events()
            self._update()
            self._render()
        pygame.quit()