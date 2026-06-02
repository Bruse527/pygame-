import pygame
import random
import math
import os

#--- 遊戲初始化與音效設定 ---
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space War")
clock = pygame.time.Clock()
FPS = 80


# 顏色定義
BLACK = (10, 10, 15)
BLUE = (0, 200, 255)
RED = (255, 20, 80)
YELLOW = (255, 255, 0)
PURPLE = (200, 50, 255)
WHITE = (255, 255, 255)
GRAY = (100, 100, 110)
GREEN = (0, 255, 100)
ORANGE = (255, 150, 0)
CARD_COLOR = (30, 30, 40)


# 優先尋找微軟正黑體，若無則找蘋方體(Mac)或黑體
CHINESE_FONTS = "microsoftjhenghei,pingfangtc,stheiti,simhei"
font = pygame.font.SysFont(CHINESE_FONTS, 28)       # 一般大小字體
large_font = pygame.font.SysFont(CHINESE_FONTS, 48) # 大字體標題
small_font = pygame.font.SysFont(CHINESE_FONTS, 22) # 小字體 UI

# --- 音效系統 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sounds = {}

def load_sound(name, filename):
    try:
        full_path = os.path.join(BASE_DIR, filename)
        sounds[name] = pygame.mixer.Sound(full_path)
        sounds[name].set_volume(0.3)
        print(f"成功載入: {filename}")
    except Exception as e:
        sounds[name] = None 
        print(f"載入失敗 {filename}，原因: {e}")
#音效檔案
load_sound("shoot", "shoot.wav")
load_sound("dash", "dash.wav")
load_sound("hit", "hit.wav")
load_sound("levelup", "levelup.wav")
load_sound("hurt", "hurt.wav")
load_sound("boss_bgm", "boss.wav") 
load_sound("gameover", "gameover.wav")
load_sound("exp", "exp.wav") 

def play_sound(name, loop=0):
    if sounds.get(name):
        sounds[name].play(loops=loop)
def stop_sound(name):
    if sounds.get(name):
        sounds[name].stop()

# --- 2. 類別定義 ---

class Player:
    def __init__(self):
        self.bullet_count = 1      # 每次射擊的子彈數量
        self.bullet_spread = 15
        self.bullet_damage_bonus = 0
        self.pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
        self.size = 30
        self.base_speed = 5
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        
        self.exp, self.level, self.max_exp = 0, 1, 100
        self.magnet_radius, self.shoot_delay = 60, 8
        self.is_aiming = False
        
        self.max_hp, self.hp = 100, 100
        self.invincible_timer = 0
        self.invincible_duration = 120
        self.damage_reduction = 0
        
        self.max_stamina, self.stamina = 100, 100
        self.dash_cost, self.stamina_regen = 35, 0.5   
        
        self.is_dashing = False
        self.dash_speed, self.dash_duration = 22, 8
        self.dash_timer = 0
        self.dash_direction = pygame.math.Vector2(0, 0)
        self.last_camera_shift = pygame.math.Vector2(0, 0)

    def update(self):
        mouse_btns = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()
        self.is_aiming = mouse_btns[2] 
        move_vector = pygame.math.Vector2(0, 0)
        
        if keys[pygame.K_w]: move_vector.y -= 1
        if keys[pygame.K_s]: move_vector.y += 1
        if keys[pygame.K_a]: move_vector.x -= 1
        if keys[pygame.K_d]: move_vector.x += 1
        if move_vector.length() > 0: move_vector.normalize_ip()

        if self.invincible_timer > 0: self.invincible_timer -= 1
        if not self.is_dashing and self.stamina < self.max_stamina:
            self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen)

        if keys[pygame.K_SPACE] and not self.is_dashing and self.stamina >= self.dash_cost:
            self.stamina -= self.dash_cost
            self.is_dashing = True
            self.dash_timer = self.dash_duration
            play_sound("dash") 
            
            if move_vector.length() > 0: self.dash_direction = move_vector.copy()
            else:
                mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())
                self.dash_direction = mouse_pos - self.pos
                if self.dash_direction.length() > 0: self.dash_direction.normalize_ip()

        if self.is_dashing:
            self.pos += self.dash_direction * self.dash_speed
            self.dash_timer -= 1
            if self.dash_timer <= 0: self.is_dashing = False
        else:
            current_speed = self.base_speed / 2 if self.is_aiming else self.base_speed
            self.pos += move_vector * current_speed
            
        self.last_camera_shift = self.pos - pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
        self.pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def draw(self, surface):
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0: pass
        else:
            pygame.draw.rect(surface, BLUE, self.rect)
            if self.stamina < self.dash_cost: pygame.draw.rect(surface, GRAY, self.rect, 3)
            if self.is_aiming and not self.is_dashing:
                pygame.draw.line(surface, RED, self.rect.center, pygame.mouse.get_pos(), 2)

class DashTrail:
    def __init__(self, x, y, size):
        self.pos = pygame.math.Vector2(x, y); self.size, self.life = size, 12
    def update(self): self.life -= 1; self.size -= 1.5
    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            rect = pygame.Rect(0, 0, self.size, self.size)
            rect.center = (round(self.pos.x), round(self.pos.y))
            pygame.draw.rect(surface, BLUE, rect, max(1, int(self.life / 3)))

class Bullet:
    def __init__(self, x, y, target_x, target_y, is_piercing=False):
        self.pos = pygame.math.Vector2(x, y)
        self.is_piercing = is_piercing
        if self.is_piercing: self.radius, self.speed, self.color = 15, 25, PURPLE
        else: self.radius, self.speed, self.color = 6, 18, YELLOW
        target = pygame.math.Vector2(target_x, target_y)
        self.direction = target - self.pos
        if self.direction.length() > 0: self.direction.normalize_ip()
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = (round(self.pos.x), round(self.pos.y))
    def draw(self, surface): pygame.draw.circle(surface, self.color, self.rect.center, self.radius)

class EnemyBullet:
    def __init__(self, x, y, dir_x, dir_y):
        self.pos = pygame.math.Vector2(x, y)
        self.direction = pygame.math.Vector2(dir_x, dir_y)
        if self.direction.length() > 0: self.direction.normalize_ip()
        self.radius, self.speed, self.color = 8, 7, ORANGE
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = (round(self.pos.x), round(self.pos.y))
    def draw(self, surface): pygame.draw.circle(surface, self.color, self.rect.center, self.radius)

class Enemy:
    def __init__(self, is_elite=False, level=1):
        self.is_elite = is_elite
        self.level = level
        self.size = 42 if self.is_elite else 25
        speed_bonus = min(level * 0.03, 1.2)
        self.speed = (random.uniform(1.1, 2.2) if self.is_elite else random.uniform(1.5, 3.5)) + speed_bonus
        base_hp = 5 if self.is_elite else 1
        self.max_hp = base_hp + level // 6
        self.hp = self.max_hp
        self.shield = level // 4 + (2 if self.is_elite else 0)
        self.max_shield = self.shield
        self.damage = 35 if self.is_elite else 20
        self.exp_drop_chance = 0.85 if self.is_elite else 0.4
        self.health_drop_chance = 0.25 if self.is_elite else 0.08
        self.color = PURPLE if self.is_elite else RED
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top': x, y = random.randint(0, WIDTH), -self.size
        elif edge == 'bottom': x, y = random.randint(0, WIDTH), HEIGHT + self.size
        elif edge == 'left': x, y = -self.size, random.randint(0, HEIGHT)
        else: x, y = WIDTH + self.size, random.randint(0, HEIGHT)
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, self.size, self.size)
    def update(self, target_pos):
        direction = target_pos - self.pos
        if direction.length() > 0: direction.normalize_ip()
        self.pos += direction * self.speed
        self.rect.center = (round(self.pos.x), round(self.pos.y))
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        if self.shield > 0:
            pygame.draw.rect(surface, BLUE, self.rect.inflate(8, 8), 2)
        if self.is_elite:
            pygame.draw.rect(surface, WHITE, self.rect, 3)
            hp_bar = pygame.Rect(self.rect.x, self.rect.y - 10, self.size, 5)
            pygame.draw.rect(surface, GRAY, hp_bar)
            pygame.draw.rect(surface, GREEN, (hp_bar.x, hp_bar.y, hp_bar.width * (self.hp / self.max_hp), hp_bar.height))
            if self.max_shield > 0:
                shield_bar = pygame.Rect(self.rect.x, self.rect.y - 16, self.size, 4)
                pygame.draw.rect(surface, GRAY, shield_bar)
                pygame.draw.rect(surface, BLUE, (shield_bar.x, shield_bar.y, shield_bar.width * (self.shield / self.max_shield), shield_bar.height))

class Boss:
    def __init__(self, spawn_level=5):
        self.pos = pygame.math.Vector2(WIDTH/2, -60) 
        self.size = 60
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.spawn_level = spawn_level
        self.max_hp = 500 + spawn_level * 120
        self.hp = self.max_hp
        self.speed = 4.0
        
        self.state = "ENTRANCE"  # 改為出場狀態
        self.state_timer = 0
        self.defeat_timer = 0
        self.color = YELLOW
        self.entrance_duration = 120  # 出場動畫持續時間(秒數)

    def update(self, player_pos, bullets):
        self.state_timer += 1
        
        if self.state == "ENTRANCE":
            # 出場動畫:從上往下
            progress = self.state_timer / self.entrance_duration
            # 出場位址從60至150之間平滑移動
            self.pos.y = -60 + (150 + 60) * progress
            self.color = (100 + 155 * progress, 100 + 155 * progress, 0)  # 顏色暗黄到黄
            
            if self.state_timer >= self.entrance_duration:
                self.state = "EVADE"
                self.state_timer = 0
        
        elif self.state == "EVADE":
            self.color = YELLOW
            direction = player_pos - self.pos
            if direction.length() > 0:
                direction.normalize_ip()
                tangent = pygame.math.Vector2(-direction.y, direction.x) 
                
                dodged = False
                for b in bullets:
                    if self.pos.distance_to(b.pos) < 150:
                        flee_dir = self.pos - b.pos
                        if flee_dir.length() > 0: flee_dir.normalize_ip()
                        self.pos += flee_dir * (self.speed * 1.8)
                        dodged = True
                        break 
                
                if not dodged:
                    self.pos += tangent * self.speed
                    dist = self.pos.distance_to(player_pos)
                    if dist > 250: self.pos += direction * self.speed
                    elif dist < 150: self.pos -= direction * self.speed

            if self.state_timer > 120:
                self.state = "CHARGE"
                self.state_timer = 0
                
        elif self.state == "CHARGE":
            self.color = (255, 100, 0)
            if self.state_timer > 60: 
                self.state = "SHOOT"
                self.state_timer = 0
        
        elif self.state == "DEFEAT":
            self.defeat_timer += 1
            self.color = (255, max(0, 150 - self.defeat_timer * 3), 0)
            # 慢慢向上爆散
            self.pos.y -= 1
            self.pos.x += math.sin(self.defeat_timer * 0.2) * 1.5
            
        self.pos.x = max(self.size, min(WIDTH-self.size, self.pos.x))
        self.pos.y = max(self.size, min(HEIGHT-self.size, self.pos.y))
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def draw(self, surface):
        # 出場階段的特殊彩繪
        if self.state == "ENTRANCE":
            # 脈衝效果
            pulse = abs(math.sin(self.state_timer * 0.1))
            current_size = int(self.size * (0.8 + pulse * 0.4))
            
            # 繪製外圈光環）
            for i in range(3):
                ring_size = current_size // 2 + 20 + i * 15
                alpha_val = int(200 * (1 - i/3) * (1 - pulse))
                if alpha_val > 0:
                    pygame.draw.circle(surface, WHITE, self.rect.center, ring_size, 2)
            
            # 繪製主體
            draw_rect = pygame.Rect(0, 0, current_size, current_size)
            draw_rect.center = self.rect.center
            pygame.draw.rect(surface, self.color, draw_rect)
            pygame.draw.circle(surface, WHITE, self.rect.center, current_size//2 + 15, 3)
            
            # 繪製能量粒子
            for i in range(8):
                angle = (self.state_timer * 0.05 + i * math.pi / 4)
                px = self.rect.centerx + math.cos(angle) * (self.size + 30)
                py = self.rect.centery + math.sin(angle) * (self.size + 30)
                pygame.draw.circle(surface, YELLOW, (int(px), int(py)), 3)
        elif self.state == "DEFEAT":
            # 爆炸特效
            progress = min(1, self.defeat_timer / 60)
            for i in range(5):
                radius = int(self.size + progress * 120 + i * 12)
                pygame.draw.circle(surface, (255, 180, 0), self.rect.center, radius, 3)
            core_size = int(self.size * (1 - progress * 0.7))
            core_rect = pygame.Rect(0, 0, max(1, core_size), max(1, core_size))
            core_rect.center = self.rect.center
            pygame.draw.rect(surface, (255, 100, 0), core_rect)
            
            burst = int(progress * 10)
            for i in range(burst):
                angle = i * (math.pi * 2 / max(1, burst)) + self.defeat_timer * 0.3
                px = self.rect.centerx + math.cos(angle) * (self.size + 30 + progress * 80)
                py = self.rect.centery + math.sin(angle) * (self.size + 30 + progress * 80)
                pygame.draw.circle(surface, RED, (int(px), int(py)), 4)
        else:
            # 正常繪制
            pygame.draw.rect(surface, self.color, self.rect)
            if self.state == "EVADE":
                pygame.draw.circle(surface, WHITE, self.rect.center, self.size//2 + 15, 3)
            elif self.state == "CHARGE":
                shrink = max(0, 30 - (self.state_timer // 2))
                pygame.draw.circle(surface, RED, self.rect.center, self.size//2 + shrink, 2)

class Particle:
    def __init__(self, x, y, color=RED):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(random.uniform(-6, 6), random.uniform(-6, 6))
        self.timer, self.size, self.color = random.randint(15, 30), random.randint(4, 8), color
    def update(self):
        self.pos += self.vel; self.timer -= 1; self.size = max(0, self.size - 0.25)
    def draw(self, surface):
        if self.size > 0: pygame.draw.rect(surface, self.color, (self.pos.x, self.pos.y, self.size, self.size))

class Gem:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y); self.rect = pygame.Rect(0, 0, 10, 10)
    def update(self, p_pos, mag_rad):
        if self.pos.distance_to(p_pos) < mag_rad:
            dir = p_pos - self.pos
            if dir.length() > 0: dir.normalize_ip()
            self.pos += dir * 8 
        self.rect.center = (round(self.pos.x), round(self.pos.y))
    def draw(self, surface):
        pts =[(self.pos.x, self.pos.y-6), (self.pos.x+6, self.pos.y), (self.pos.x, self.pos.y+6), (self.pos.x-6, self.pos.y)]
        pygame.draw.polygon(surface, BLUE, pts)

class HealthPack:
    def __init__(self, x, y, heal_amount=25):
        self.pos = pygame.math.Vector2(x, y)
        self.heal_amount = heal_amount
        self.size = 18
        self.rect = pygame.Rect(0, 0, self.size, self.size)

    def update(self, p_pos, mag_rad):
        if self.pos.distance_to(p_pos) < mag_rad:
            direction = p_pos - self.pos
            if direction.length() > 0:
                direction.normalize_ip()
            self.pos += direction * 6
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def draw(self, surface):
        pygame.draw.rect(surface, GREEN, self.rect, border_radius=4)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=4)
        pygame.draw.rect(surface, WHITE, (self.rect.centerx - 2, self.rect.y + 4, 4, self.size - 8))
        pygame.draw.rect(surface, WHITE, (self.rect.x + 4, self.rect.centery - 2, self.size - 8, 4))

def choose_upgrade_cards():
    global current_upgrade_choices, selected_upgrade_position
    card_count = min(3, len(upgrade_options))
    current_upgrade_choices = random.sample(range(len(upgrade_options)), card_count)
    selected_upgrade_position = None

def add_chosen_upgrade(choice):
    title = upgrade_options[choice]["title"]
    for upgrade in chosen_upgrades:
        if upgrade["title"] == title:
            upgrade["count"] += 1
            return
    chosen_upgrades.append({"title": title, "count": 1})

def apply_upgrade(choice):
    global game_state, selected_upgrade_position
    if choice == 0: player.max_hp += 50; player.hp += 50 
    elif choice == 1: player.shoot_delay = max(2, player.shoot_delay - 2) 
    elif choice == 2: player.stamina_regen += 0.3
    elif choice == 3: player.bullet_count += 1
    elif choice == 4: player.bullet_damage_bonus += 2
    elif choice == 5: player.max_stamina += 25; player.stamina += 25
    elif choice == 6: player.dash_cost = max(15, player.dash_cost - 8)
    elif choice == 7: player.base_speed += 0.7
    elif choice == 8: player.magnet_radius += 45
    elif choice == 9: player.bullet_spread = max(6, player.bullet_spread - 3)
    elif choice == 10: player.dash_duration += 2
    elif choice == 11: player.hp = min(player.max_hp, player.hp + 60)
    elif choice == 12: player.invincible_duration += 30
    elif choice == 13: player.damage_reduction += 3
    elif choice == 14: player.dash_speed += 3
    elif choice == 15:
        player.max_hp += 25
        player.max_stamina += 15
        player.hp += 25
        player.stamina += 15
    elif choice == 16: player.magnet_radius += 25; player.stamina_regen += 0.15
    elif choice == 17: player.bullet_spread += 5; player.bullet_count += 1
    add_chosen_upgrade(choice)
    current_upgrade_choices.clear()
    selected_upgrade_position = None
    game_state = "PLAYING"             

# ==========================================
# 🛑 中文化升級選項系統 (用陣列方便換行)
# ==========================================
upgrade_options =[
    {"title": "生命躍升", "desc": ["最大血量 +50", "並恢復當前血量"]},
    {"title": "超頻運轉", "desc": ["機槍射速提升", "子彈連發加快"]},
    {"title": "能量飲料", "desc": ["體力恢復加快", "衝刺更加頻繁"]},
    {"title": "彈幕擴張", "desc": ["子彈發射數 +1", "形成扇形擴散"]},
    {"title": "高能彈芯", "desc": ["子彈傷害增加", "打精英更有效"]},
    {"title": "備用電池", "desc": ["最大體力 +25", "衝刺資源增加"]},
    {"title": "輕量推進", "desc": ["衝刺消耗降低", "更容易連續閃避"]},
    {"title": "離子靴", "desc": ["移動速度提升", "走位更加靈活"]},
    {"title": "磁吸核心", "desc": ["經驗吸取範圍", "大幅增加"]},
    {"title": "穩定槍管", "desc": ["散射角度縮小", "彈幕更集中"]},
    {"title": "延長燃燒", "desc": ["衝刺時間增加", "位移距離更遠"]},
    {"title": "急救模組", "desc": ["立即恢復血量", "最多恢復 60"]},
    {"title": "相位護盾", "desc": ["受傷免傷延長", "更能脫離包圍"]},
    {"title": "裝甲鍍層", "desc": ["受到傷害降低", "硬扛能力提升"]},
    {"title": "爆燃推進", "desc": ["衝刺速度增加", "瞬間拉開距離"]},
    {"title": "戰術背包", "desc": ["血量與體力上限", "小幅同步提升"]},
    {"title": "回收矩陣", "desc": ["吸取範圍增加", "體力恢復小幅提升"]},
    {"title": "寬幅槍口", "desc": ["多一顆子彈", "但散射更寬"]}
]
cards =[
    pygame.Rect(WIDTH//2 - 360, 260, 220, 280),
    pygame.Rect(WIDTH//2 - 110, 260, 220, 280),
    pygame.Rect(WIDTH//2 + 140, 260, 220, 280)
]
confirm_upgrade_button = pygame.Rect(WIDTH//2 - 110, 590, 220, 60)
current_upgrade_choices = []
selected_upgrade_position = None
chosen_upgrades = []

# 退出遊戲按鈕
exit_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 60)

# 開始遊戲按鈕
start_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 60)

# 更新日誌按鈕
changelog_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 130, 200, 60)
changelog_close_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 320, 200, 55)

# 重新開始按鈕
restart_button = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 + 100, 200, 60)

# 回到選單按鈕
menu_button = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 100, 200, 60)

def draw_upgrade_summary(surface, x, y, max_items=6, title="已選強化"):
    panel_width = 260
    row_height = 28
    hidden_count = max(0, len(chosen_upgrades) - max_items)
    row_count = max(1, min(len(chosen_upgrades), max_items))
    panel_height = 44 + row_count * row_height + (row_height if hidden_count else 0)
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((18, 20, 30, 185))
    surface.blit(panel, (x, y))
    pygame.draw.rect(surface, WHITE, (x, y, panel_width, panel_height), 2, border_radius=8)

    total_count = sum(upgrade["count"] for upgrade in chosen_upgrades)
    title_label = f"{title} ({total_count})" if chosen_upgrades else title
    title_txt = small_font.render(title_label, True, YELLOW)
    surface.blit(title_txt, (x + 14, y + 10))

    if not chosen_upgrades:
        empty_txt = small_font.render("尚未選擇", True, GRAY)
        surface.blit(empty_txt, (x + 14, y + 42))
        return

    visible_upgrades = chosen_upgrades[-max_items:]
    for i, upgrade in enumerate(visible_upgrades):
        suffix = f" x{upgrade['count']}" if upgrade["count"] > 1 else ""
        line = small_font.render(f"{upgrade['title']}{suffix}", True, WHITE)
        surface.blit(line, (x + 14, y + 42 + i * row_height))

    if hidden_count:
        hidden_txt = small_font.render(f"還有 {hidden_count} 種...", True, GRAY)
        surface.blit(hidden_txt, (x + 14, y + 42 + len(visible_upgrades) * row_height))

def shift_rect_object(obj, offset):
    obj.pos -= offset
    if hasattr(obj, "rect"):
        obj.rect.center = (round(obj.pos.x), round(obj.pos.y))

def apply_camera_follow(offset):
    if offset.length_squared() == 0:
        return
    for group in (bullets, enemy_bullets, enemies, particles, gems, health_packs, trails):
        for obj in group:
            shift_rect_object(obj, offset)
    if boss_active and boss:
        shift_rect_object(boss, offset)

def wrap_text(text, text_font, max_width):
    lines = []
    current = ""
    for char in text:
        test = current + char
        if text_font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = char
    if current:
        lines.append(current)
    return lines

def draw_changelog_popup(surface):
    popup = pygame.Rect(WIDTH//2 - 420, HEIGHT//2 - 300, 840, 660)
    panel = pygame.Surface((popup.width, popup.height), pygame.SRCALPHA)
    panel.fill((18, 20, 32, 235))
    surface.blit(panel, popup.topleft)
    pygame.draw.rect(surface, WHITE, popup, 3, border_radius=12)

    title = large_font.render("更新日誌", True, YELLOW)
    surface.blit(title, (popup.centerx - title.get_width()//2, popup.y + 35))

    content_rect = pygame.Rect(popup.x + 60, popup.y + 110, popup.width - 120, popup.height - 205)
    content_lines = []
    for line in CHANGELOG:
        color = YELLOW if line.startswith("v") else WHITE
        wrapped = wrap_text(line, font, content_rect.width - 20)
        for wrapped_line in wrapped:
            content_lines.append((wrapped_line, color))
        content_lines.append(("", WHITE))

    content_height = max(content_rect.height, len(content_lines) * 34 + 10)
    max_scroll = max(0, content_height - content_rect.height)
    scroll_y = min(changelog_scroll, max_scroll)
    content_surface = pygame.Surface((content_rect.width, content_height), pygame.SRCALPHA)

    for i, (line, color) in enumerate(content_lines):
        if line:
            text = font.render(line, True, color)
            content_surface.blit(text, (0, 6 + i * 34))

    surface.blit(content_surface, content_rect.topleft, pygame.Rect(0, scroll_y, content_rect.width, content_rect.height))
    pygame.draw.rect(surface, GRAY, content_rect, 1)

    if max_scroll > 0:
        bar_h = max(40, int(content_rect.height * content_rect.height / content_height))
        bar_y = content_rect.y + int((content_rect.height - bar_h) * (scroll_y / max_scroll))
        pygame.draw.rect(surface, GRAY, (content_rect.right + 8, content_rect.y, 8, content_rect.height), border_radius=4)
        pygame.draw.rect(surface, YELLOW, (content_rect.right + 8, bar_y, 8, bar_h), border_radius=4)

    close_color = RED if changelog_close_button.collidepoint(pygame.mouse.get_pos()) else (150, 50, 50)
    pygame.draw.rect(surface, close_color, changelog_close_button, border_radius=10)
    pygame.draw.rect(surface, WHITE, changelog_close_button, 3, border_radius=10)
    close_txt = font.render("關閉", True, WHITE)
    surface.blit(close_txt, (
        changelog_close_button.centerx - close_txt.get_width()//2,
        changelog_close_button.centery - close_txt.get_height()//2
    ))

CHANGELOG = [
    "v1.152",
    "- 更新日誌改為可用滑鼠滾輪滑動",
    "- 更新日誌文字自動換行，避免超出邊框",
    "v1.151",
    "- 移除追蹤彈，新增更多強化卡牌",
    "- 小兵會隨玩家等級獲得血量、速度與護盾成長",
    "- 加入跟隨視角感，玩家更接近畫面中心",
    "v1.051",
    "- 暫停畫面新增回到主選單",
    "v1.05",
    "- Boss 強化：血量提高，高等 Boss 彈幕加密",
    "- 追蹤晶片下修：降低鎖定距離與轉向速度",
    "- 精英小怪出生率降低",
    "- 初始頁新增可點開的更新日誌",
    "v1.04",
    "- 新增回血包、精英小怪、Boss 每 5 等出現",
    "- 新增強化卡牌紀錄與碰撞後短暫免傷",
    "v1.03",
    "- 擴大強化卡牌牌庫，加入選取後確認功能",
]
show_changelog = False
changelog_scroll = 0

# --- 遊戲狀態重置系統 ---
def reset_game(initial_state="PLAYING"):
    global player, bullets, enemy_bullets, enemies, particles, gems, health_packs, trails
    global boss, boss_active, boss_defeated, next_boss_level, game_state, current_upgrade_choices, selected_upgrade_position, chosen_upgrades, show_changelog, changelog_scroll
    player = Player()
    bullets, enemy_bullets, enemies, particles, gems, health_packs, trails = [], [], [], [], [], [], []
    boss = None
    boss_active = False
    boss_defeated = False
    next_boss_level = 5
    current_upgrade_choices = []
    selected_upgrade_position = None
    chosen_upgrades = []
    show_changelog = False
    changelog_scroll = 0
    stop_sound("boss_bgm")
    game_state = initial_state
    
    

reset_game("MENU")
shoot_cooldown = 0 
SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY_EVENT, 600)
dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
dim_surface.fill((0, 0, 0, 180))

# Boss 警告計時器
boss_warning_timer = 0

# --- 4. 遊戲主迴圈 ---
running = True
while running:
    for event in pygame.event.get():
        if game_state == "MENU" and show_changelog and event.type == pygame.MOUSEWHEEL:
            changelog_scroll = max(0, changelog_scroll - event.y * 45)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if game_state == "PLAYING":
                game_state = "PAUSED"
            elif game_state == "PAUSED":
                game_state = "PLAYING"
        
        if game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_button.collidepoint(event.pos):
                    reset_game()
                elif menu_button.collidepoint(event.pos):
                    reset_game("MENU")
        elif game_state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_changelog:
                    if changelog_close_button.collidepoint(event.pos):
                        show_changelog = False
                        changelog_scroll = 0
                elif start_button.collidepoint(event.pos):
                    game_state = "PLAYING"
                elif changelog_button.collidepoint(event.pos):
                    show_changelog = True
                    changelog_scroll = 0
        elif game_state == "PAUSED":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pause_resume_btn = pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 70, 220, 60)
                pause_menu_btn = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 70, 220, 60)
                pause_restart_btn = pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 150, 220, 60)
                pause_exit_btn = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 150, 220, 60)
                if pause_resume_btn.collidepoint(event.pos):
                    game_state = "PLAYING"
                elif pause_menu_btn.collidepoint(event.pos):
                    reset_game("MENU")
                elif pause_restart_btn.collidepoint(event.pos):
                    reset_game()
                elif pause_exit_btn.collidepoint(event.pos):
                    running = False
        elif game_state == "LEVEL_UP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected_upgrade_position is not None and confirm_upgrade_button.collidepoint(event.pos):
                    apply_upgrade(current_upgrade_choices[selected_upgrade_position])
                    break
                for i, card in enumerate(cards):
                    if i < len(current_upgrade_choices) and card.collidepoint(event.pos):
                        selected_upgrade_position = i
                        break
        elif game_state == "PLAYING":
            if event.type == SPAWN_ENEMY_EVENT:
                elite_chance = min(0.03 + player.level * 0.006, 0.15)
                enemies.append(Enemy(is_elite=random.random() < elite_chance, level=player.level))

    if game_state == "PLAYING":
        if player.level >= next_boss_level and not boss_active:
            boss = Boss(next_boss_level)
            boss_active = True
            boss_defeated = False
            boss_warning_timer = 120  # boss警告時常(秒數)
            play_sound("boss_bgm", loop=-1) 

        mouse_btns = pygame.mouse.get_pressed()
        if mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            is_piercing = player.is_aiming
            # 計算基礎向量
            base_dir = pygame.math.Vector2(mouse_x - player.pos.x, mouse_y - player.pos.y)
            if base_dir.length() > 0: base_dir.normalize_ip()
            # 根據 bullet_count 產生子彈
            start_angle = -(player.bullet_count - 1) * player.bullet_spread / 2
            for i in range(player.bullet_count):
                angle = start_angle + (i * player.bullet_spread)
                # 旋轉基礎向量來產生散彈效果
                shot_dir = base_dir.rotate(angle)
                target_pos = player.pos + shot_dir * 100
                bullets.append(Bullet(
                    player.rect.centerx,
                    player.rect.centery,
                    target_pos.x,
                    target_pos.y,
                    is_piercing
                ))
            shoot_cooldown = 30 if is_piercing else player.shoot_delay
            play_sound("shoot")

        if shoot_cooldown > 0: shoot_cooldown -= 1
        player.update()
        apply_camera_follow(player.last_camera_shift)
        
        if player.is_dashing: trails.append(DashTrail(player.rect.centerx, player.rect.centery, player.size))
        for t in trails[:]:
            t.update()
            if t.life <= 0: trails.remove(t)
            
        for b in bullets[:]:
            b.update()
            if not screen.get_rect().inflate(500, 500).colliderect(b.rect): bullets.remove(b)
            
        for eb in enemy_bullets[:]:
            eb.update()
            if not screen.get_rect().inflate(500, 500).colliderect(eb.rect): enemy_bullets.remove(eb)
            
        for e in enemies: e.update(player.pos)
        for p in particles[:]:
            p.update()
            if p.timer <= 0: particles.remove(p)

        if boss_active:
            boss.update(player.pos, bullets) 
            if boss.state == "SHOOT":
                for i in range(12):
                    angle = math.radians(i * 30)
                    dir_x, dir_y = math.cos(angle), math.sin(angle)
                    enemy_bullets.append(EnemyBullet(boss.rect.centerx, boss.rect.centery, dir_x, dir_y))
                if boss.spawn_level >= 10:
                    for i in range(12):
                        angle = math.radians(i * 30 + 15)
                        dir_x, dir_y = math.cos(angle), math.sin(angle)
                        enemy_bullets.append(EnemyBullet(boss.rect.centerx, boss.rect.centery, dir_x, dir_y))
                boss.state = "EVADE"
                play_sound("shoot")

        # 更新Boss警告計時器
        if boss_warning_timer > 0:
            boss_warning_timer -= 1

        if boss_active and boss.state == "DEFEAT" and boss.defeat_timer > 60:
            boss_active = False
            boss_defeated = True
            next_boss_level += 5
            stop_sound("boss_bgm")

        for b in bullets[:]:
            hit_something = False
            for e in enemies[:]:
                if b.rect.colliderect(e.rect):
                    damage = (3 if b.is_piercing else 1) + player.bullet_damage_bonus
                    shield_damage = min(e.shield, damage)
                    e.shield -= shield_damage
                    damage -= shield_damage
                    e.hp -= damage
                    for _ in range(8): particles.append(Particle(e.pos.x, e.pos.y, e.color))
                    hit_something = True
                    play_sound("hit")

                    if e.hp <= 0:
                        for _ in range(12 if e.is_elite else 6): particles.append(Particle(e.pos.x, e.pos.y, e.color))
                        if random.random() < e.exp_drop_chance:
                            gem_count = 3 if e.is_elite else 1
                            for _ in range(gem_count):
                                gems.append(Gem(e.pos.x + random.randint(-12, 12), e.pos.y + random.randint(-12, 12)))
                        if random.random() < e.health_drop_chance:
                            health_packs.append(HealthPack(e.pos.x, e.pos.y, heal_amount=40 if e.is_elite else 25))
                        enemies.remove(e)
            
            if boss_active and b.rect.colliderect(boss.rect):
                hit_something = True
                if boss.state == "EVADE":
                    for _ in range(5): particles.append(Particle(boss.pos.x, boss.pos.y, GRAY))
                elif boss.state != "DEFEAT":
                    damage = (30 if b.is_piercing else 8) + player.bullet_damage_bonus
                    boss.hp -= damage
                    for _ in range(8): particles.append(Particle(boss.pos.x, boss.pos.y, YELLOW))
                    play_sound("hit")
                    
                    if boss.hp <= 0:
                        boss.state = "DEFEAT"
                        boss.defeat_timer = 0
                        for _ in range(40): gems.append(Gem(boss.pos.x + random.randint(-60,60), boss.pos.y + random.randint(-60,60)))
                        for _ in range(50): particles.append(Particle(boss.pos.x, boss.pos.y, YELLOW))
                        
            if hit_something and not b.is_piercing and b in bullets: bullets.remove(b)

        def player_take_damage(dmg):
            if player.invincible_timer <= 0 and not player.is_dashing:
                player.hp -= max(1, dmg - player.damage_reduction)
                player.invincible_timer = player.invincible_duration 
                play_sound("hurt")
                
                if player.hp <= 0:
                    global game_state
                    game_state = "GAME_OVER"
                    play_sound("gameover")  
                    stop_sound("boss_bgm")  

        for e in enemies:
            if player.rect.colliderect(e.rect): player_take_damage(e.damage)
        for eb in enemy_bullets[:]:
            if player.rect.colliderect(eb.rect):
                player_take_damage(25)
                if eb in enemy_bullets: enemy_bullets.remove(eb)
        if boss_active and boss.state != "DEFEAT" and player.rect.colliderect(boss.rect):
            player_take_damage(40) 

        for g in gems[:]:
            g.update(player.pos, player.magnet_radius)
            if player.rect.colliderect(g.rect):
                gems.remove(g)
                player.exp += 15
                play_sound("exp") 
                
                if player.exp >= player.max_exp:
                    player.level += 1; player.exp = 0; player.max_exp = int(player.max_exp * 1.5)
                    choose_upgrade_cards()
                    game_state = "LEVEL_UP" 
                    play_sound("levelup") 

        for hp in health_packs[:]:
            hp.update(player.pos, player.magnet_radius)
            if player.rect.colliderect(hp.rect):
                health_packs.remove(hp)
                player.hp = min(player.max_hp, player.hp + hp.heal_amount)
                play_sound("exp")

    # --- 畫面繪製 ---
    screen.fill(BLACK)
    
    for g in gems: g.draw(screen)
    for hp in health_packs: hp.draw(screen)
    for p in particles: p.draw(screen)
    for b in bullets: b.draw(screen)
    for eb in enemy_bullets: eb.draw(screen) 
    for e in enemies: e.draw(screen)
    for t in trails: t.draw(screen)
    
    if boss_active: boss.draw(screen) 
    player.draw(screen)
    
<<<<<<< HEAD
    #UI 面板 
=======
    # === UI 面板 (中文化) ===
>>>>>>> 5fe3c3b9a6cb6e15508d0cc26521ee2ec490b8fd
    pygame.draw.rect(screen, GRAY, (20, 20, 250, 15))
    pygame.draw.rect(screen, BLUE, (20, 20, 250 * (player.exp / player.max_exp), 15))
    # 顯示等級
    screen.blit(font.render(f"等級: {player.level}", True, WHITE), (280, 15))

    pygame.draw.rect(screen, GRAY, (20, 45, 200, 15))
    pygame.draw.rect(screen, GREEN if player.hp > 30 else RED, (20, 45, 200 * (max(0, player.hp) / player.max_hp), 15))
    # 顯示血量
    screen.blit(font.render(f"血量", True, WHITE), (230, 40))

    pygame.draw.rect(screen, GRAY, (20, 70, 150, 10))
    pygame.draw.rect(screen, ORANGE, (20, 70, 150 * (player.stamina / player.max_stamina), 10))
    # 顯示體力
    screen.blit(font.render("體力", True, WHITE), (180, 62))

    draw_upgrade_summary(screen, WIDTH - 290, 20, max_items=5)

    if boss_active:
        bar_w = WIDTH - 100
        pygame.draw.rect(screen, GRAY, (50, HEIGHT - 40, bar_w, 20))
        pygame.draw.rect(screen, YELLOW, (50, HEIGHT - 40, bar_w * (max(0, boss.hp) / boss.max_hp), 20))
        boss_level_txt = font.render(f"BOSS Lv.{boss.spawn_level}", True, YELLOW)
        screen.blit(boss_level_txt, (50, HEIGHT - 75))
        
        # Boss 狀態資訊
        if boss.state == "ENTRANCE":
            # 出場顯示倒計時器
            entrance_text = font.render(f"✦ BOSS 入场 ✦", True, YELLOW)
            screen.blit(entrance_text, (WIDTH//2 - entrance_text.get_width()//2, HEIGHT//2 - 200))
            
            # 顯示警告文本
            warning_lines = [
<<<<<<< HEAD
                " BOSS 出現！",
=======
                "⚠️ BOSS 出現！",
>>>>>>> 5fe3c3b9a6cb6e15508d0cc26521ee2ec490b8fd
                "黄色 = 謢盾模式(無敵）  |  紅色 = 虛弱模式",
                "觀察型態轉換,把握攻擊時機！"
            ]
            for i, line in enumerate(warning_lines):
                warning = font.render(line, True, RED)
                screen.blit(warning, (WIDTH//2 - warning.get_width()//2, HEIGHT//2 - 150 + i * 40))
        elif boss_warning_timer > 0:
<<<<<<< HEAD
            warning_txt = font.render(" BOSS 出現！觀察顏色變化攻擊時機", True, RED)
=======
            warning_txt = font.render("⚠️ BOSS 出現！觀察顏色變化攻擊時機", True, RED)
>>>>>>> 5fe3c3b9a6cb6e15508d0cc26521ee2ec490b8fd
            screen.blit(warning_txt, (WIDTH//2 - warning_txt.get_width()//2, HEIGHT - 90))
        else:
            if boss.state == "EVADE":
                state_txt = font.render(" 閃避階段 - 無敵狀態 (黃色)", True, YELLOW)
            elif boss.state == "CHARGE":
                state_txt = font.render(" 蓄力階段 - 可攻擊 (橙紅色)", True, ORANGE)
            else:
                state_txt = font.render(" 發射階段 - 可攻擊", True, RED)
            screen.blit(state_txt, (WIDTH//2 - state_txt.get_width()//2, HEIGHT - 90))

    if game_state == "LEVEL_UP":
        screen.blit(dim_surface, (0, 0)) 
        title = large_font.render("升級！選擇強化後按確認", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        for i, card in enumerate(cards):
            if i >= len(current_upgrade_choices):
                continue
            upgrade = upgrade_options[current_upgrade_choices[i]]
            is_selected = selected_upgrade_position == i
            color = GREEN if is_selected else BLUE if card.collidepoint(pygame.mouse.get_pos()) else CARD_COLOR
            pygame.draw.rect(screen, color, card, border_radius=10)
            border_color = YELLOW if is_selected else WHITE
            border_width = 6 if is_selected else 3
            pygame.draw.rect(screen, border_color, card, border_width, border_radius=10) 
            
            # 卡牌標題
            opt_title = font.render(upgrade["title"], True, WHITE)
            screen.blit(opt_title, (card.centerx - opt_title.get_width()//2, card.y + 30))
            
            # 卡牌敘述 (現在分為兩行自動置中)
            desc1 = font.render(upgrade["desc"][0], True, YELLOW)
            desc2 = font.render(upgrade["desc"][1], True, YELLOW)
            screen.blit(desc1, (card.centerx - desc1.get_width()//2, card.y + 110))
            screen.blit(desc2, (card.centerx - desc2.get_width()//2, card.y + 150))
        
        confirm_ready = selected_upgrade_position is not None
        confirm_color = GREEN if confirm_ready and confirm_upgrade_button.collidepoint(pygame.mouse.get_pos()) else (50, 150, 50) if confirm_ready else GRAY
        pygame.draw.rect(screen, confirm_color, confirm_upgrade_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, confirm_upgrade_button, 3, border_radius=10)
        confirm_text = font.render("確認選擇", True, WHITE)
        screen.blit(confirm_text, (
            confirm_upgrade_button.centerx - confirm_text.get_width()//2,
            confirm_upgrade_button.centery - confirm_text.get_height()//2
        ))

    elif game_state == "MENU":
        # 星空背景
        screen.fill(BLACK)
        
        # 繪製星星
        for i in range(100):
            x = (i * 37) % WIDTH
            y = (i * 23) % HEIGHT
            brightness = 100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)
        
        # 繪製一些漂浮的粒子
        for i in range(20):
            x = (WIDTH//2 + math.cos(pygame.time.get_ticks() * 0.002 + i) * 300) % WIDTH
            y = (HEIGHT//2 + math.sin(pygame.time.get_ticks() * 0.001 + i) * 200) % HEIGHT
            alpha = 50 + 30 * math.sin(pygame.time.get_ticks() * 0.003 + i)
            particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (100, 150, 255, alpha), (2, 2), 2)
            screen.blit(particle_surface, (x, y))
        
        # 標題發光效果
        glow_color = (0, 100, 255, 50)
        glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        title = large_font.render("Space War", True, BLUE)
        glow_surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
        
        # 應用發光效果
        for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -3), (0, 3), (-3, 0), (3, 0)]:
            glow_copy = glow_surface.copy()
            glow_copy.fill(glow_color, special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(glow_copy, offset)
        
        # 主標題
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 100))
        
        # 副標題
        subtitle = font.render("太空戰爭", True, WHITE)
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2 - 60))
        
        # 開始遊戲按鈕 (增強樣式)
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = start_button.collidepoint(mouse_pos)
        
        if is_hovered:
            # 懸停時的動畫效果
            scale = 1.05
            scaled_button = pygame.Rect(
                start_button.centerx - start_button.width * scale // 2,
                start_button.centery - start_button.height * scale // 2,
                start_button.width * scale,
                start_button.height * scale
            )
            button_color = (100, 200, 100)
            pygame.draw.rect(screen, button_color, scaled_button, border_radius=12)
            pygame.draw.rect(screen, YELLOW, scaled_button, 4, border_radius=12)
        else:
            button_color = (50, 150, 50)
            pygame.draw.rect(screen, button_color, start_button, border_radius=10)
            pygame.draw.rect(screen, WHITE, start_button, 3, border_radius=10)
        
        # 按鈕文字
        start_btn_txt = font.render("開始遊戲", True, WHITE)
        btn_x = start_button.centerx - start_btn_txt.get_width()//2
        btn_y = start_button.centery - start_btn_txt.get_height()//2
        screen.blit(start_btn_txt, (btn_x, btn_y))

        changelog_color = BLUE if changelog_button.collidepoint(mouse_pos) else (50, 100, 150)
        pygame.draw.rect(screen, changelog_color, changelog_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, changelog_button, 3, border_radius=10)
        changelog_txt = font.render("更新日誌", True, WHITE)
        screen.blit(changelog_txt, (
            changelog_button.centerx - changelog_txt.get_width()//2,
            changelog_button.centery - changelog_txt.get_height()//2
        ))
        
        # 操作說明 (更好的佈局)
        controls_title = font.render("操作說明:", True, YELLOW)
        screen.blit(controls_title, (WIDTH//2 - controls_title.get_width()//2, HEIGHT//2 + 220))
        
        controls = [
            "移動: WASD",
            "手槍模式: 滑鼠左鍵",
            "狙擊模式: 滑鼠右鍵", 
            "衝刺: space鍵",
            "暫停: ESC鍵",
            "升級選單: 升級後點擊選項",
            "操作需要切換至英文輸入法才能使用，請確保切換後再進行遊戲！"
        ]
        
        for i, control in enumerate(controls):
            control_txt = font.render(control, True, GRAY)
            y_pos = HEIGHT//2 + 260 + i * 35
            screen.blit(control_txt, (WIDTH//2 - control_txt.get_width()//2, y_pos))
        
        # 添加一些裝飾性的幾何圖形
        # 左上角裝飾
        pygame.draw.polygon(screen, BLUE, [
            (50, 50), (100, 50), (75, 25)
        ], 2)
        
        # 右下角裝飾
        pygame.draw.polygon(screen, PURPLE, [
            (WIDTH-50, HEIGHT-50), (WIDTH-100, HEIGHT-50), (WIDTH-75, HEIGHT-25)
        ], 2)
        
        # 版本資訊
        version_txt = font.render("v1.152", True, GRAY)
        screen.blit(version_txt, (WIDTH - version_txt.get_width() - 20, HEIGHT - version_txt.get_height() - 20))

        if show_changelog:
            draw_changelog_popup(screen)

    elif game_state == "PAUSED":
        screen.blit(dim_surface, (0, 0))
        pause_txt = large_font.render("暫停中", True, YELLOW)
        resume_txt = font.render("按下 'ESC' 鍵繼續遊戲", True, WHITE)
        
        # 自動置中
        screen.blit(pause_txt, (WIDTH//2 - pause_txt.get_width()//2, HEIGHT//2 - 50))
        screen.blit(resume_txt, (WIDTH//2 - resume_txt.get_width()//2, HEIGHT//2 + 20))
        
        # 繼續遊戲按鈕
        pause_resume_btn = pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 70, 220, 60)
        pause_resume_color = BLUE if pause_resume_btn.collidepoint(pygame.mouse.get_pos()) else (50, 100, 150)
        pygame.draw.rect(screen, pause_resume_color, pause_resume_btn, border_radius=10)
        pygame.draw.rect(screen, WHITE, pause_resume_btn, 3, border_radius=10)
        pause_resume_txt = font.render("繼續遊戲", True, WHITE)
        screen.blit(pause_resume_txt, (pause_resume_btn.centerx - pause_resume_txt.get_width()//2, pause_resume_btn.centery - pause_resume_txt.get_height()//2))

        # 回到主選單按鈕
        pause_menu_btn = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 70, 220, 60)
        pause_menu_color = BLUE if pause_menu_btn.collidepoint(pygame.mouse.get_pos()) else (50, 100, 150)
        pygame.draw.rect(screen, pause_menu_color, pause_menu_btn, border_radius=10)
        pygame.draw.rect(screen, WHITE, pause_menu_btn, 3, border_radius=10)
        pause_menu_txt = font.render("回到選單", True, WHITE)
        screen.blit(pause_menu_txt, (pause_menu_btn.centerx - pause_menu_txt.get_width()//2, pause_menu_btn.centery - pause_menu_txt.get_height()//2))
        
        # 重新開始按鈕
        pause_restart_btn = pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 150, 220, 60)
        pause_restart_color = GREEN if pause_restart_btn.collidepoint(pygame.mouse.get_pos()) else (50, 150, 50)
        pygame.draw.rect(screen, pause_restart_color, pause_restart_btn, border_radius=10)
        pygame.draw.rect(screen, WHITE, pause_restart_btn, 3, border_radius=10)
        pause_restart_txt = font.render("重新開始", True, WHITE)
        screen.blit(pause_restart_txt, (pause_restart_btn.centerx - pause_restart_txt.get_width()//2, pause_restart_btn.centery - pause_restart_txt.get_height()//2))
        
        # 退出遊戲按鈕
        pause_exit_btn = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 150, 220, 60)
        pause_exit_color = RED if pause_exit_btn.collidepoint(pygame.mouse.get_pos()) else (150, 50, 50)
        pygame.draw.rect(screen, pause_exit_color, pause_exit_btn, border_radius=10)
        pygame.draw.rect(screen, WHITE, pause_exit_btn, 3, border_radius=10)
        pause_exit_txt = font.render("退出遊戲", True, WHITE)
        screen.blit(pause_exit_txt, (pause_exit_btn.centerx - pause_exit_txt.get_width()//2, pause_exit_btn.centery - pause_exit_txt.get_height()//2))

        draw_upgrade_summary(screen, WIDTH//2 - 130, HEIGHT//2 + 240, max_items=10, title="本局強化紀錄")
    
    elif game_state == "GAME_OVER":
        screen.blit(dim_surface, (0, 0))
        game_over_txt = large_font.render("Game Over", True, RED)
        
        # 自動置中
        screen.blit(game_over_txt, (WIDTH//2 - game_over_txt.get_width()//2, HEIGHT//2 - 100))
        
        # 重新開始按鈕
        restart_btn_color = GREEN if restart_button.collidepoint(pygame.mouse.get_pos()) else (50, 150, 50)
        pygame.draw.rect(screen, restart_btn_color, restart_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, restart_button, 3, border_radius=10)
        restart_btn_txt = font.render("重新開始", True, WHITE)
        screen.blit(restart_btn_txt, (restart_button.centerx - restart_btn_txt.get_width()//2, restart_button.centery - restart_btn_txt.get_height()//2))
        
        # 回到選單按鈕
        menu_btn_color = BLUE if menu_button.collidepoint(pygame.mouse.get_pos()) else (50, 100, 150)
        pygame.draw.rect(screen, menu_btn_color, menu_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, menu_button, 3, border_radius=10)
        menu_btn_txt = font.render("回到選單", True, WHITE)
        screen.blit(menu_btn_txt, (menu_button.centerx - menu_btn_txt.get_width()//2, menu_button.centery - menu_btn_txt.get_height()//2))




    pygame.display.flip()
    clock.tick(FPS)

<<<<<<< HEAD
pygame.quit()
=======
pygame.quit()
>>>>>>> 5fe3c3b9a6cb6e15508d0cc26521ee2ec490b8fd
