import random
import os

class UpgradeManager:
    def __init__(self, game):
        self.player = game.player
        self.game = game
        icon_path = os.path.join("assets", "images", "upgrades")

        self.available_upgrades = [
            {"name": "🔥 Tang Sat Thuong",
             "type": "damage",
             "value": 15,
             "icon": os.path.join(icon_path, "tangsatthuong.png")},

            {"name": "🏹 Tang Toc Đo Đan", 
            "type": "b_speed",
            "value": 120,
            "icon": os.path.join(icon_path, "tocdodan.png")},

            {"name": "👟 Tang Toc Chay",
            "type": "p_speed",
            "value": 40,
            "icon": os.path.join(icon_path, "tocchay.png")},

            {"name": "💎 Đan Xuyen Thau", 
             "type": "pierce", 
             "value": 1,
             "icon": os.path.join(icon_path, "percing.png")},
            {"name": "🔱 Ban Nhieu Tia (Multi-shot)", 
             "type": "multi", 
             "value": 1,
             "icon": os.path.join(icon_path, "multi shot.png")},
            {"name": "❤️ Hoi Mau Base", 
             "type": "heal_base", 
             "value": 5,
             "icon": os.path.join(icon_path, "hoimaubase.png")}
        ]

    def get_random_options(self, n=3):
        """Lấy ra n lựa chọn ngẫu nhiên."""
        return random.sample(self.available_upgrades, n)

    def apply_upgrade(self, upgrade):
        """Áp dụng nâng cấp trực tiếp vào chỉ số trò chơi."""
        u_type = upgrade["type"]
        val = upgrade["value"]
        
        if u_type == "damage":
            self.player.bullet_damage += val
        elif u_type == "b_speed":
            self.player.bullet_speed += val
        elif u_type == "p_speed":
            self.player.speed += val
        elif u_type == "pierce":
            self.player.pierce_count += val
        elif u_type == "multi":
            self.player.multi_shot += val
        elif u_type == "heal_base":
            self.game.base_health += val
        
        print(f"Đã áp dụng nâng cấp: {upgrade['name']}")