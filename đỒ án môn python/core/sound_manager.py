import pygame
import os

class SoundManager:
    def __init__(self):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        
        # Dictionary để chứa các Sound Effect (SFX) ngắn
        self.sfx = {}
        
        self.audio_path = os.path.join("assets", "audio")
        
    def load_music(self, filename):
        """Nạp nhạc nền (Background Music - Stream từ ổ cứng)"""
        path = os.path.join(self.audio_path, filename)
        try:
            pygame.mixer.music.load(path)
        except Exception as e:
            print(f"Lỗi nạp nhạc: {e}")

    def play_music(self, loops=-1, volume=0.5):
        """Phát nhạc nền"""
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)

    def load_sfx(self, name, filename):
        """Nạp hiệu ứng âm thanh (SFX - Lưu vào RAM để phát nhanh)"""
        path = os.path.join(self.audio_path, filename)
        try:
            self.sfx[name] = pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Lỗi nạp SFX {name}: {e}")

    def play_sfx(self, name, volume=0.6):
        """Phát hiệu ứng âm thanh theo tên"""
        if name in self.sfx:
            self.sfx[name].set_volume(volume)
            self.sfx[name].play()

    def set_music_volume(self, volume):
        pygame.mixer.music.set_volume(volume)

    def stop_music(self):
        pygame.mixer.music.stop()