"""
整合 B4 開放世界/防穿透核心 + A3 完整 UI 系統 + 25 種卡牌
- v1.9 新增：敵人隨機使用 12 種武器
- v1.9 新增：死亡遺失物機制、地堡安全區復活
- v1.9 新增：動態隨機撤離點、倒數計時大軍淹沒(Boss Swarm)機制
- 介面自適應 1024x768 視窗
"""

import pygame
import random
import math
import os

# 初始化遊戲跟音效
pygame.init()
pygame.mixer.init()

# 設定視窗與開放世界大小
WIDTH, HEIGHT = 1024, 768
MAP_WIDTH, MAP_HEIGHT = 4200, 2600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("驅魔人: 撤離點")
clock = pygame.time.Clock()
FPS = 60

# 全域相機與特效座標
camera_x = 0
camera_y = 0

# 顏色定義
BLACK = (10, 10, 15)
BLUE = (0, 200, 255)
RED = (255, 20, 80)
YELLOW = (255, 255, 0)
PURPLE = (200, 50, 255)
DARK_PURPLE = (138, 43, 226) 
WHITE = (255, 255, 255)
GRAY = (100, 100, 110)
GREEN = (0, 255, 100)
ORANGE = (255, 150, 0)
CYAN = (0, 255, 255)

CARD_COLOR = (30, 30, 40)
CARD_TYPE_COLORS = {"attack": (120, 35, 45), "support": (35, 75, 130), "life": (35, 110, 65)}
CARD_TYPE_LABELS = {"attack": "攻擊", "support": "支援", "life": "生命"}
SHIELD_COLOR = (0, 150, 255)
EXP_COLOR = (124, 252, 0)
HP_COLOR = (255, 50, 50)

# 字體設定
CHINESE_FONTS = "microsoftjhenghei,pingfangtc,stheiti,simhei"
font = pygame.font.SysFont(CHINESE_FONTS, 24)
large_font = pygame.font.SysFont(CHINESE_FONTS, 42)
small_font = pygame.font.SysFont(CHINESE_FONTS, 18)
tiny_font = pygame.font.SysFont(CHINESE_FONTS, 14)

# 動畫以及貼圖系統
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
if not os.path.exists(IMAGE_DIR): os.makedirs(IMAGE_DIR)

images = {}
animations = {}

def load_image(name, filename, size=None):
    try:
        path = os.path.join(IMAGE_DIR, filename)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            if size: img = pygame.transform.scale(img, size)
            images[name] = img
        else: images[name] = None
    except: images[name] = None

def load_animation(name, folder_name, size):
    folder_path = os.path.join(IMAGE_DIR, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path); animations[name] = None; return
    frames =[]
    for file in sorted(os.listdir(folder_path)):
        if file.endswith((".png", ".jpg")):
            img = pygame.image.load(os.path.join(folder_path, file)).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
    animations[name] = frames if frames else None

load_image("bg", "bg.png", (WIDTH, HEIGHT))
load_image("drop_EXP", "drop_exp.png", (20, 20))
load_image("bullet_normal", "bullet_normal.png", (16, 16))
load_image("bullet_piercing", "bullet_piercing.png", (20, 20))
load_image("bullet_shotgun", "bullet_shotgun.png", (16, 16))
load_image("bullet_flamethrower", "bullet_flame.png", (30, 30))
load_image("bullet_laser", "bullet_laser.png", (10, 40)) 
load_image("bullet_cannon", "bullet_cannon.png", (40, 40))
load_image("bullet_frost", "bullet_frost.png", (20, 20))
load_image("bullet_flame_grenade", "bullet_grenade.png", (24, 24))
load_image("bullet_plasma", "bullet_plasma.png", (24, 24))
load_image("enemy_bullet", "bullet_enemy.png", (18, 18))

load_animation("player", "player", (40, 40))
load_animation("enemy_normal", "enemy_normal", (35, 35))
load_animation("enemy_elite", "enemy_elite", (50, 50))
load_animation("boss_YELLOW", "boss_yellow", (100, 100))
load_animation("boss_RED", "boss_red", (100, 100))
load_animation("boss_PURPLE", "boss_purple", (100, 100))

sounds = {}
def load_sound(name, filename):
    try:
        sound_path = os.path.join(BASE_DIR, filename)
        sounds[name] = pygame.mixer.Sound(sound_path)
        sounds[name].set_volume(0.3)
    except: sounds[name] = None 

load_sound("dash", "dash.wav")
load_sound("hit", "hit.wav")
load_sound("levelup", "levelup.wav")
load_sound("hurt", "hurt.wav")
load_sound("boss_bgm", "boss.wav") 
load_sound("gameover", "gameover.wav")
load_sound("exp", "exp.wav") 
load_sound("shoot_normal", "shoot_normal.wav")     
load_sound("shoot_laser", "shoot_laser.wav")       
load_sound("shoot_shotgun", "shoot_shotgun.wav")   
load_sound("shoot_cannon", "shoot_cannon.wav")     
load_sound("shoot_flame", "shoot_flame.wav")       

def load_weapon_sound(weapon_key, filename, fallback_key):
    try:
        sound_path = os.path.join(BASE_DIR, filename)
        if os.path.exists(sound_path):
            sounds[weapon_key] = pygame.mixer.Sound(sound_path)
            sounds[weapon_key].set_volume(0.3)
        else: sounds[weapon_key] = sounds.get(fallback_key)
    except: sounds[weapon_key] = sounds.get(fallback_key)

load_weapon_sound("snd_pistol", "pistol.wav", "shoot_normal")
load_weapon_sound("snd_sniper", "sniper.wav", "shoot_cannon")
load_weapon_sound("snd_shotgun", "shotgun.wav", "shoot_shotgun")
load_weapon_sound("snd_mg", "machinegun.wav", "shoot_normal")
load_weapon_sound("snd_flamethrower", "flamethrower.wav", "shoot_flame")
load_weapon_sound("snd_laser", "laser.wav", "shoot_laser")
load_weapon_sound("snd_cannon", "cannon.wav", "shoot_cannon")
load_weapon_sound("snd_frost", "frost.wav", "shoot_flame")
load_weapon_sound("snd_heavy_mg", "heavy_mg.wav", "shoot_shotgun")
load_weapon_sound("snd_rifle", "rifle.wav", "shoot_cannon")
load_weapon_sound("snd_grenade", "grenade.wav", "shoot_cannon")
load_weapon_sound("snd_plasma", "plasma.wav", "shoot_laser")

bgm_path = os.path.join(BASE_DIR, "bgm.mp3")
try:
    pygame.mixer.music.load(bgm_path)
    pygame.mixer.music.set_volume(0.2)
except: pass

def play_sound(name, loop=0):
    if sounds.get(name): sounds[name].play(loops=loop)

def stop_sound(name):
    if sounds.get(name): sounds[name].stop()

CHEAT_CODE =[
    pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, 
    pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, 
    pygame.K_b, pygame.K_a, pygame.K_b, pygame.K_a
]
key_buffer =[] 

class Weapon:
    def __init__(self, name, shoot_delay, bullet_type, damage, sound_name="shoot_normal"):
        self.name, self.shoot_delay, self.bullet_type, self.damage, self.sound_name = name, shoot_delay, bullet_type, damage, sound_name
        load_image("gun_" + name, f"gun_{name}.png", (45, 18))

WEAPON_TYPES = {
    "手槍": Weapon("手槍", 20, "normal", 20, "snd_pistol"),
    "狙擊槍": Weapon("狙擊槍", 50, "piercing", 45, "snd_sniper"),
    "散彈槍": Weapon("散彈槍", 30, "shotgun", 20, "snd_shotgun"),
    "機槍": Weapon("機槍", 15, "piercing", 20, "snd_mg"),
    "火焰噴射器": Weapon("火焰噴射器", 3, "flamethrower", 4, "snd_flamethrower"),
    "雷射槍": Weapon("雷射槍", 25, "laser", 25, "snd_laser"),
    "電磁炮": Weapon("電磁炮", 60, "cannon", 50, "snd_cannon"),
    "冰霜發射器": Weapon("冰霜發射器", 5, "frost", 6, "snd_frost"),
    "重型機槍": Weapon("重型機槍", 17, "piercing", 25, "snd_heavy_mg"),
    "步槍": Weapon("步槍", 40, "piercing", 30, "snd_rifle"),
    "火焰榴彈發射器": Weapon("火焰榴彈發射器", 65, "flame_grenade", 70, "snd_grenade"),
    "電漿發射器": Weapon("電漿發射器", 30, "plasma", 30, "snd_plasma")
}

# 撤離點系統
class ExtractionPoint:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.radius = 150
        self.rect = pygame.Rect(x-150, y-150, 300, 300)
        self.progress = 0 # 0 ~ 100
        
    def update(self, px, py):
        if math.hypot(px - self.x, py - self.y) < self.radius:
            self.progress += 0.35 # 約 5 秒可撤離
        else:
            self.progress = max(0, self.progress - 0.5)
        return self.progress >= 100
            
    def draw(self, surface):
        cx, cy = int(self.x - camera_x), int(self.y - camera_y)
        pulse = math.sin(pygame.time.get_ticks()*0.005)*15
        pygame.draw.circle(surface, (0, 255, 100, 100), (cx, cy), int(self.radius + pulse), 2)
        pygame.draw.circle(surface, (0, 200, 50, 40), (cx, cy), self.radius)
        if self.progress > 0:
            bar_w = 120
            pygame.draw.rect(surface, GRAY, (cx - bar_w//2, cy - self.radius - 25, bar_w, 12), border_radius=4)
            pygame.draw.rect(surface, GREEN, (cx - bar_w//2, cy - self.radius - 25, bar_w * (self.progress/100), 12), border_radius=4)
            pygame.draw.rect(surface, WHITE, (cx - bar_w//2, cy - self.radius - 25, bar_w, 12), 2, border_radius=4)
            txt = small_font.render("撤離進度", True, WHITE)
            surface.blit(txt, (cx - txt.get_width()//2, cy - self.radius - 50))

class Player:
    def __init__(self):
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.size = 30
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.weapons = list(WEAPON_TYPES.values())
        self.current_weapon_idx = 0
        
        self.base_speed = 7.0
        self.max_hp, self.hp = 100, 100
        self.max_shield, self.shield = 100, 100       
        self.max_stamina, self.stamina = 100, 100
        self.stamina_regen = 0.5   
        self.max_energy, self.energy = 100, 100
        self.energy_regen = 0.2     
        self.exp, self.level, self.max_exp = 0, 1, 80
        self.pending_level_ups = 0
        
        # 強化數值
        self.bullet_count, self.bullet_spread, self.extra_same_path_bullets = 1, 15, 0
        self.bullet_damage_bonus, self.shoot_delay_reduction, self.damage_reduction = 0, 0, 0
        self.invincible_duration, self.guidance_level, self.aura_level, self.regen_level = 60, 0, 0, 0
        self.regen_progress, self.exp_multiplier, self.magnet_radius = 0, 1.0, 80
        self.drone_level, self.drone_angle, self.drone_shoot_cd = 0, 0, 0
        
        # 衝刺相關
        self.dash_cost, self.is_dashing, self.dash_speed, self.dash_duration = 30, False, 28, 8
        self.dash_timer, self.dash_dir_x, self.dash_dir_y = 0, 0, 0
        
        self.skill_cd, self.skill_max_cd, self.skill_cost = 0, 600, 50        
        self.invincible_timer, self.god_mode = 0, False 

        # 挑戰模式彈匣
        self.base_max_ammo, self.mag_size_bonus, self.reload_duration, self.reload_timer = 40, 0, 90, 0
        self.ammo = self.base_max_ammo

    def update(self):
        global game_state
        keys = pygame.key.get_pressed()
        move_x, move_y = 0, 0
        if keys[pygame.K_w]: move_y -= 1
        if keys[pygame.K_s]: move_y += 1
        if keys[pygame.K_a]: move_x -= 1
        if keys[pygame.K_d]: move_x += 1
            
        dist = math.sqrt(move_x**2 + move_y**2)
        if dist > 0: move_x /= dist; move_y /= dist

        if self.invincible_timer > 0: self.invincible_timer -= 1
        if self.skill_cd > 0: self.skill_cd -= 1
        
        if self.reload_timer > 0:
            self.reload_timer -= 1
            if self.reload_timer <= 0: self.ammo = self.base_max_ammo + self.mag_size_bonus

        if self.regen_level > 0 and self.hp < self.max_hp:
            self.regen_progress += 0.01 * self.regen_level
            if self.regen_progress >= 1:
                heal = int(self.regen_progress)
                self.hp = min(self.max_hp, self.hp + heal); self.regen_progress -= heal
            
        if not self.is_dashing:
            if self.stamina < self.max_stamina: self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen)
        if self.energy < self.max_energy: self.energy = min(self.max_energy, self.energy + self.energy_regen)

        if keys[pygame.K_SPACE] or keys[pygame.K_q]:
            if not self.is_dashing and self.stamina >= self.dash_cost:
                self.stamina -= self.dash_cost; self.is_dashing = True; self.dash_timer = self.dash_duration
                play_sound("dash")
                if dist > 0: self.dash_dir_x, self.dash_dir_y = move_x, move_y
                else:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    dash_dx, dash_dy = (mouse_x + camera_x) - self.x, (mouse_y + camera_y) - self.y
                    dash_dist = math.sqrt(dash_dx**2 + dash_dy**2)
                    if dash_dist > 0: self.dash_dir_x, self.dash_dir_y = dash_dx / dash_dist, dash_dy / dash_dist

        if self.is_dashing:
            self.x += self.dash_dir_x * self.dash_speed; self.y += self.dash_dir_y * self.dash_speed
            self.dash_timer -= 1
            if self.dash_timer <= 0: self.is_dashing = False
        else:
            self.x += move_x * self.base_speed; self.y += move_y * self.base_speed
            
        if game_state == "BUNKER":
            self.x = max(WIDTH//2 - 380, min(WIDTH//2 + 380, self.x))
            self.y = max(HEIGHT//2 - 280, min(HEIGHT//2 + 280, self.y))
        else:
            self.x = max(self.size/2, min(MAP_WIDTH - self.size/2, self.x))
            self.y = max(self.size/2, min(MAP_HEIGHT - self.size/2, self.y))
            
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface, current_wep=None):
        draw_player = True
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        draw_rect = self.rect.copy(); draw_rect.center = draw_center
        
        if self.invincible_timer > 0 and not self.god_mode:
            if (self.invincible_timer // 4) % 2 == 0: draw_player = False
                
        if draw_player:
            anim_frames = animations.get("player")
            if anim_frames:
                img = anim_frames[int(pygame.time.get_ticks() / 100) % len(anim_frames)]
                mouse_x, _ = pygame.mouse.get_pos()
                if mouse_x + camera_x < self.x: img = pygame.transform.flip(img, True, False)
                surface.blit(img, img.get_rect(center=draw_center))
            else:
                pygame.draw.rect(surface, YELLOW if self.god_mode else BLUE, draw_rect)
                
            if self.stamina < self.dash_cost: pygame.draw.rect(surface, GRAY, draw_rect, 3)

            if current_wep:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx, dy = (mouse_x + camera_x) - self.x, (mouse_y + camera_y) - self.y
                dist = math.sqrt(dx**2 + dy**2)
                dir_x = dx / dist if dist > 0 else 1
                dir_y = dy / dist if dist > 0 else 0
                angle = math.degrees(math.atan2(-dy, dx))
                gun_img = images.get("gun_" + current_wep.name)
                
                if gun_img:
                    if dx < 0: gun_img = pygame.transform.flip(gun_img, False, True)
                    rotated_gun = pygame.transform.rotate(gun_img, angle)
                    offset_x, offset_y = dir_x * 15, dir_y * 15
                    gun_rect = rotated_gun.get_rect(center=(int(self.x + offset_x - camera_x), int(self.y + offset_y - camera_y)))
                    surface.blit(rotated_gun, gun_rect)
                else:
                    end_x, end_y = self.x + dir_x * 25 - camera_x, self.y + dir_y * 25 - camera_y
                    wep_color = YELLOW
                    if current_wep.bullet_type == "piercing": wep_color = PURPLE
                    elif current_wep.bullet_type == "flamethrower": wep_color = ORANGE
                    elif current_wep.bullet_type == "laser": wep_color = CYAN
                    elif current_wep.bullet_type == "cannon": wep_color = WHITE
                    elif current_wep.bullet_type == "frost": wep_color = (100, 200, 255)
                    elif current_wep.bullet_type == "flame_grenade": wep_color = RED
                    elif current_wep.bullet_type == "plasma": wep_color = GREEN
                    pygame.draw.line(surface, GRAY, (self.x - camera_x, self.y - camera_y), (end_x, end_y), 6)
                    pygame.draw.circle(surface, wep_color, (int(end_x), int(end_y)), 4)

        if self.aura_level > 0:
            aura_radius = 95 + self.aura_level * 25
            pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10)
            pygame.draw.circle(surface, (0, 180, 255), draw_rect.center, aura_radius + pulse, 2)
            
        if self.drone_level > 0:
            drone_x = draw_center[0] + math.cos(self.drone_angle) * 55
            drone_y = draw_center[1] + math.sin(self.drone_angle) * 55
            pygame.draw.circle(surface, (150, 200, 255), (int(drone_x), int(drone_y)), 10)
            pygame.draw.circle(surface, BLUE, (int(drone_x), int(drone_y)), 10, 2)
            pygame.draw.circle(surface, RED, (int(drone_x), int(drone_y)), 4)

class DashTrail:
    def __init__(self, x, y, size): self.x, self.y, self.size, self.life = x, y, size, 12
    def update(self): self.life -= 1; self.size -= 1.5
    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            rect = pygame.Rect(0, 0, self.size, self.size)
            rect.center = (int(self.x - camera_x), int(self.y - camera_y))
            pygame.draw.rect(surface, BLUE, rect, max(1, int(self.life / 3)))

class Bullet:
    def __init__(self, x, y, target_x, target_y, weapon, guidance_level=0, dmg_bonus=0):
        self.x, self.y = x, y
        self.b_type, self.damage = weapon.bullet_type, weapon.damage + dmg_bonus
        self.guidance_level = guidance_level
        self.is_piercing = self.b_type in ["piercing", "laser", "cannon", "flamethrower"]
            
        dx, dy = target_x - self.x, target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        self.dir_x, self.dir_y = (dx / dist, dy / dist) if dist > 0 else (1, 0)
        
        self.lifespan, self.speed, self.radius, self.color = 120, 18, 6, YELLOW
        if self.b_type == "piercing": self.color, self.speed, self.radius = PURPLE, 28, 7
        elif self.b_type == "flamethrower": self.color, self.speed, self.radius, self.lifespan = ORANGE, 12, 12, 25
        elif self.b_type == "laser": self.color, self.speed, self.radius = CYAN, 45, 4
        elif self.b_type == "cannon": self.color, self.speed, self.radius = WHITE, 12, 20
        elif self.b_type == "frost": self.color, self.speed, self.radius = (100, 200, 255), 16, 8
        elif self.b_type == "flame_grenade": self.color, self.speed, self.radius = RED, 10, 10
        elif self.b_type == "plasma": self.color, self.speed, self.radius = GREEN, 15, 10

        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        self.explode = False 
        self.target_x, self.target_y = target_x, target_y

    def update(self):
        self.lifespan -= 1
        if self.b_type == "flame_grenade" and math.hypot(self.target_x - self.x, self.target_y - self.y) < self.speed:
            self.explode = True; self.lifespan = 0; return 
        if self.b_type == "plasma":
            if self.x <= 0 or self.x >= MAP_WIDTH: self.dir_x *= -1
            if self.y <= 0 or self.y >= MAP_HEIGHT: self.dir_y *= -1

        if self.guidance_level > 0 and enemies:
            min_dist, closest_enemy = 220 + self.guidance_level * 50, None
            for e in enemies:
                dist = math.hypot(self.x - e.x, self.y - e.y)
                if dist < min_dist: min_dist, closest_enemy = dist, e
            if bosses:
                for boss in bosses:
                    if boss.state != "DEFEAT":
                        dist = math.hypot(self.x - boss.x, self.y - boss.y)
                        if dist < min_dist: closest_enemy = boss
            if closest_enemy:
                tx, ty = closest_enemy.x - self.x, closest_enemy.y - self.y
                tdist = math.hypot(tx, ty)
                if tdist > 0:
                    tx, ty = tx / tdist, ty / tdist
                    turn_speed = min(0.1, 0.02 + self.guidance_level * 0.015)
                    self.dir_x = self.dir_x * (1 - turn_speed) + tx * turn_speed
                    self.dir_y = self.dir_y * (1 - turn_speed) + ty * turn_speed
                    ndist = math.hypot(self.dir_x, self.dir_y)
                    if ndist > 0: self.dir_x /= ndist; self.dir_y /= ndist

        self.x += self.dir_x * self.speed; self.y += self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        img = images.get("bullet_" + self.b_type)
        if img:
            rotated_img = pygame.transform.rotate(img, math.degrees(math.atan2(-self.dir_y, self.dir_x)))
            surface.blit(rotated_img, rotated_img.get_rect(center=draw_center))
        else:
            if self.b_type == "laser":
                end_x, end_y = self.x - (self.dir_x * 30) - camera_x, self.y - (self.dir_y * 30) - camera_y
                pygame.draw.line(surface, self.color, (self.x - camera_x, self.y - camera_y), (end_x, end_y), self.radius*2)
            else: pygame.draw.circle(surface, self.color, draw_center, self.radius)

class EnemyBullet:
    def __init__(self, x, y, dir_x, dir_y, weapon=None, dmg_mult=1.0, color=ORANGE, is_homing=False):
        self.x, self.y = x, y
        dist = math.hypot(dir_x, dir_y)
        self.dir_x, self.dir_y = (dir_x / dist, dir_y / dist) if dist > 0 else (1, 0)
        
        self.weapon = weapon
        self.is_homing = is_homing
        self.damage = 15 * dmg_mult
        self.b_type = weapon.bullet_type if weapon else "normal"
        self.speed, self.radius, self.color = 7, 8, color
        
        if weapon:
            self.damage = weapon.damage * dmg_mult
            if self.b_type == "piercing": self.color, self.speed, self.radius = PURPLE, 15, 7
            elif self.b_type == "flamethrower": self.color, self.speed, self.radius = ORANGE, 8, 12
            elif self.b_type == "laser": self.color, self.speed, self.radius = CYAN, 25, 4
            elif self.b_type == "cannon": self.color, self.speed, self.radius = WHITE, 8, 20
            elif self.b_type == "frost": self.color, self.speed, self.radius = (100, 200, 255), 10, 8
            elif self.b_type == "flame_grenade": self.color, self.speed, self.radius = RED, 7, 10
            elif self.b_type == "plasma": self.color, self.speed, self.radius = GREEN, 10, 10
            elif self.b_type == "shotgun": self.color, self.speed, self.radius = YELLOW, 12, 5
            
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        
    def update(self, target_x=None, target_y=None):
        if self.is_homing and target_x is not None and target_y is not None:
            tx, ty = target_x - self.x, target_y - self.y
            dist = math.hypot(tx, ty)
            if dist > 0:
                tx, ty = tx / dist, ty / dist
                turn_speed = 0.035
                self.dir_x = self.dir_x * (1 - turn_speed) + tx * turn_speed
                self.dir_y = self.dir_y * (1 - turn_speed) + ty * turn_speed
                ndist = math.hypot(self.dir_x, self.dir_y)
                if ndist > 0: self.dir_x /= ndist; self.dir_y /= ndist
                
        self.x += self.dir_x * self.speed; self.y += self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface): 
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        img = images.get("bullet_" + self.b_type)
        if img and not self.is_homing: 
            rotated_img = pygame.transform.rotate(img, math.degrees(math.atan2(-self.dir_y, self.dir_x)))
            surface.blit(rotated_img, rotated_img.get_rect(center=draw_center))
        else: 
            if self.b_type == "laser":
                end_x, end_y = self.x - (self.dir_x * 20) - camera_x, self.y - (self.dir_y * 20) - camera_y
                pygame.draw.line(surface, self.color, (self.x - camera_x, self.y - camera_y), (end_x, end_y), self.radius*2)
            else:
                pygame.draw.circle(surface, self.color, draw_center, self.radius)
                if self.is_homing: pygame.draw.circle(surface, WHITE, draw_center, self.radius-2)

class Enemy:
    def __init__(self, level, is_elite=False, spawn_x=MAP_WIDTH/2, spawn_y=MAP_HEIGHT/2):
        self.is_elite = is_elite
        self.size = 35 if is_elite else 25
        difficulty_mult = 1.75 if game_mode == "CHALLENGE" else 1.0
        
        level_speed_bonus = level * 0.05
        base_speed = (random.uniform(3.0, 5.5) if is_elite else random.uniform(2.5, 4.5)) + level_speed_bonus
        self.speed = base_speed * (1.2 if game_mode == "CHALLENGE" else 1.0)
        
        self.max_hp = int(((60 + level * 25) if is_elite else (20 + level * 8)) * difficulty_mult)
        self.hp = self.max_hp
        self.max_shield = int(((20 + level * 8) if is_elite else (10 + level * 4)) * difficulty_mult)
        self.shield = self.max_shield
        self.base_damage = (35 + level * 3) if is_elite else (15 + level * 1.5)
        self.damage = int(self.base_damage * difficulty_mult)
        
        self.frost_timer = 0 
        self.dir_x, self.dir_y = 1, 0  
        self.weapon = None
        
        if not is_elite: self.combat_type = random.choices(["melee", "ranged", "kamikaze"], weights=[0.4, 0.5, 0.1])[0]
        else: self.combat_type = random.choice(["melee", "ranged"])
            
        if self.combat_type == "kamikaze":
            self.color = ORANGE; self.speed *= 1.4; self.max_hp = int(self.max_hp * 0.6); self.damage = int(self.damage * 1.5)
        elif self.combat_type == "ranged":
            # 隨機分配 12 種武器
            self.weapon = random.choice(list(WEAPON_TYPES.values()))
            self.shoot_cd = self.weapon.shoot_delay * 3 + random.randint(30, 90) # 敵人射速比玩家慢
        
        spawn_dist_x, spawn_dist_y = WIDTH / 2 + 50, HEIGHT / 2 + 50
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top': self.x, self.y = spawn_x + random.randint(-int(spawn_dist_x), int(spawn_dist_x)), spawn_y - spawn_dist_y
        elif edge == 'bottom': self.x, self.y = spawn_x + random.randint(-int(spawn_dist_x), int(spawn_dist_x)), spawn_y + spawn_dist_y
        elif edge == 'left': self.x, self.y = spawn_x - spawn_dist_x, spawn_y + random.randint(-int(spawn_dist_y), int(spawn_dist_y))
        elif edge == 'right': self.x, self.y = spawn_x + spawn_dist_x, spawn_y + random.randint(-int(spawn_dist_y), int(spawn_dist_y))
            
        self.x = max(0, min(self.x, MAP_WIDTH)); self.y = max(0, min(self.y, MAP_HEIGHT))
        self.rect = pygame.Rect(0, 0, self.size, self.size)

    def update(self, target_x, target_y, all_enemies, enemy_bullets):
        current_speed = self.speed
        if self.frost_timer > 0: self.frost_timer -= 1; current_speed *= 0.4 

        dx, dy = target_x - self.x, target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0: self.dir_x, self.dir_y = dx / dist, dy / dist

        if self.combat_type == "ranged":
            if dist > 300: self.x += self.dir_x * current_speed; self.y += self.dir_y * current_speed
            elif dist < 200: self.x -= self.dir_x * current_speed; self.y -= self.dir_y * current_speed
            
            if self.shoot_cd <= 0 and dist <= 500 and self.weapon:
                dmg_mult = self.damage / 15.0
                if self.weapon.bullet_type == "shotgun":
                    for i in range(-1, 2):
                        angle = math.atan2(self.dir_y, self.dir_x) + math.radians(i * 15)
                        enemy_bullets.append(EnemyBullet(self.x, self.y, math.cos(angle), math.sin(angle), self.weapon, dmg_mult))
                else:
                    enemy_bullets.append(EnemyBullet(self.x, self.y, self.dir_x, self.dir_y, self.weapon, dmg_mult))
                self.shoot_cd = self.weapon.shoot_delay * 4 + random.randint(30, 60)
            if self.shoot_cd > 0: self.shoot_cd -= 1
            
        elif self.combat_type == "kamikaze":
            self.x += self.dir_x * current_speed; self.y += self.dir_y * current_speed
        else:
            if dist > (self.size + 30) / 2:
                if dist > 0: self.x += self.dir_x * current_speed; self.y += self.dir_y * current_speed
            else:
                if dist > 0: self.x -= self.dir_x * (current_speed * 0.8); self.y -= self.dir_y * (current_speed * 0.8)

        for other in all_enemies:
            if other is not self:
                dist_sq = (self.x - other.x)**2 + (self.y - other.y)**2
                if 0 < dist_sq < self.size**2:
                    dist_val = math.sqrt(dist_sq)
                    self.x += ((self.x - other.x) / dist_val) * 1.3; self.y += ((self.y - other.y) / dist_val) * 1.3
            
        self.x = max(0, min(self.x, MAP_WIDTH)); self.y = max(0, min(self.y, MAP_HEIGHT))
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        draw_rect = self.rect.copy(); draw_rect.center = draw_center
        
        if self.combat_type == "kamikaze":
            pygame.draw.circle(surface, ORANGE, draw_center, self.size // 2)
            for i in range(8):
                angle = pygame.time.get_ticks() * 0.01 + i * math.pi / 4
                end_x, end_y = draw_center[0] + math.cos(angle) * (self.size * 0.8), draw_center[1] + math.sin(angle) * (self.size * 0.8)
                pygame.draw.line(surface, YELLOW, draw_center, (end_x, end_y), 3)
        else:
            anim_key = "enemy_elite" if self.is_elite else "enemy_normal"
            anim_frames = animations.get(anim_key)
            if anim_frames:
                img = anim_frames[int(pygame.time.get_ticks() / 100) % len(anim_frames)]
                if self.dir_x < 0: img = pygame.transform.flip(img, True, False)
                if self.frost_timer > 0: img = img.copy(); img.fill((100, 200, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)
                surface.blit(img, img.get_rect(center=draw_center))
                if self.is_elite:
                    glow = math.sin(pygame.time.get_ticks() * 0.01) * 6 + 6
                    pygame.draw.rect(surface, DARK_PURPLE, draw_rect.copy().inflate(glow, glow), 3) 
            else:
                color = (150, 0, 150) if self.is_elite else RED
                if self.frost_timer > 0: color = (100, 200, 255)
                if self.is_elite:
                    glow = math.sin(pygame.time.get_ticks() * 0.01) * 6 + 6
                    pygame.draw.rect(surface, DARK_PURPLE, draw_rect.copy().inflate(glow, glow), 3) 
                pygame.draw.rect(surface, color, draw_rect)
            
            # 武器繪製
            if self.dir_x != 0 or self.dir_y != 0:
                angle = math.atan2(self.dir_y, self.dir_x)
                if self.combat_type == "melee":
                    draw_angle = angle + math.sin(pygame.time.get_ticks() * 0.015) * 0.8
                    end_x, end_y = draw_center[0] + math.cos(draw_angle) * (self.size * 1.0), draw_center[1] + math.sin(draw_angle) * (self.size * 1.0)
                    pygame.draw.line(surface, (220, 220, 220), draw_center, (end_x, end_y), 4)
                    h_x, h_y = draw_center[0] + math.cos(draw_angle) * (self.size * 0.3), draw_center[1] + math.sin(draw_angle) * (self.size * 0.3)
                    p_angle = draw_angle + math.pi / 2
                    pygame.draw.line(surface, (150, 100, 50), (h_x + math.cos(p_angle)*6, h_y + math.sin(p_angle)*6), (h_x - math.cos(p_angle)*6, h_y - math.sin(p_angle)*6), 3)
                elif self.combat_type == "ranged" and self.weapon:
                    gun_img = images.get("gun_" + self.weapon.name)
                    if gun_img:
                        if self.dir_x < 0: gun_img = pygame.transform.flip(gun_img, False, True)
                        rotated_gun = pygame.transform.rotate(gun_img, math.degrees(-angle))
                        offset_x, offset_y = self.dir_x * 15, self.dir_y * 15
                        gun_rect = rotated_gun.get_rect(center=(int(draw_center[0] + offset_x), int(draw_center[1] + offset_y)))
                        surface.blit(rotated_gun, gun_rect)
                    else:
                        end_x, end_y = draw_center[0] + math.cos(angle) * (self.size * 0.8), draw_center[1] + math.sin(angle) * (self.size * 0.8)
                        pygame.draw.line(surface, (80, 80, 80), draw_center, (end_x, end_y), 6); pygame.draw.circle(surface, ORANGE, (int(end_x), int(end_y)), 3)

        if self.max_shield > 0 and self.shield > 0:
            pygame.draw.rect(surface, GRAY, (draw_rect.x, draw_rect.y - 14, self.size, 4))
            pygame.draw.rect(surface, (0, 150, 255), (draw_rect.x, draw_rect.y - 14, self.size * (max(0, self.shield)/self.max_shield), 4))
            
        if self.hp < self.max_hp:
            pygame.draw.rect(surface, GRAY, (draw_rect.x, draw_rect.y - 8, self.size, 4))
            pygame.draw.rect(surface, GREEN, (draw_rect.x, draw_rect.y - 8, self.size * (max(0, self.hp)/self.max_hp), 4))

class Boss:
    def __init__(self, boss_type, level, spawn_x=MAP_WIDTH/2, spawn_y=MAP_HEIGHT/2):
        self.b_type = boss_type
        self.x, self.y = spawn_x, max(0, spawn_y - 400)
        self.size = 65
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.state_timer, self.frost_timer = 0, 0
        self.play_shoot_sound = False 
        self.x = max(0, min(self.x, MAP_WIDTH)); self.y = max(0, min(self.y, MAP_HEIGHT))
        
        difficulty_mult = 1.75 if game_mode == "CHALLENGE" else 1.0
        base_hp = {"YELLOW": 3000, "RED": 4000, "PURPLE": 2500, "CYAN": 3200}[self.b_type]
        self.max_hp = int((base_hp + level * 100) * difficulty_mult)
        
        if self.b_type == "YELLOW": self.color, self.speed, self.state = YELLOW, 4.0, "EVADE"
        elif self.b_type == "RED": self.color, self.speed, self.state, self.aim_x, self.aim_y = RED, 3.5, "CHASE", 0, 0
        elif self.b_type == "PURPLE": self.color, self.speed, self.state = PURPLE, 3.0, "FLEE"
        elif self.b_type == "CYAN": self.color, self.speed, self.state = CYAN, 3.5, "IDLE"
        
        self.hp = self.max_hp

    def update(self, player_x, player_y, bullets, enemies, enemy_bullets):
        self.state_timer += 1
        current_speed = self.speed * 0.5 if self.frost_timer > 0 else self.speed
        if self.frost_timer > 0: self.frost_timer -= 1
        self.play_shoot_sound = False
        
        dx, dy = player_x - self.x, player_y - self.y
        dist = math.hypot(dx, dy)
        dir_x, dir_y = (dx / dist, dy / dist) if dist > 0 else (0, 0)
        tangent_x, tangent_y = -dir_y, dir_x 

        if self.b_type == "YELLOW":
            if self.state == "EVADE":
                dodged = False
                for b in bullets:
                    if math.hypot(self.x - b.x, self.y - b.y) < 150:
                        flee_dist = math.hypot(self.x - b.x, self.y - b.y)
                        if flee_dist > 0: self.x += ((self.x - b.x) / flee_dist) * (current_speed * 1.8); self.y += ((self.y - b.y) / flee_dist) * (current_speed * 1.8)
                        dodged = True; break 
                if not dodged:
                    self.x += tangent_x * current_speed; self.y += tangent_y * current_speed
                    if dist > 250: self.x += dir_x * current_speed; self.y += dir_y * current_speed
                    elif dist < 150: self.x -= dir_x * current_speed; self.y -= dir_y * current_speed
                if self.state_timer > 120: self.state = "CHARGE"; self.state_timer = 0
            elif self.state == "CHARGE" and self.state_timer > 60:
                for i in range(12):
                    angle = math.radians(i * 30)
                    enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, math.cos(angle), math.sin(angle)))
                self.state = "EVADE"; self.state_timer = 0; self.play_shoot_sound = True

        elif self.b_type == "RED":
            if self.state == "CHASE":
                if dist > 0: self.x += dir_x * current_speed; self.y += dir_y * current_speed
                if self.state_timer > 150: self.state = "WARN"; self.state_timer = 0
            elif self.state == "WARN":
                self.aim_x, self.aim_y = player_x, player_y
                if self.state_timer > 45:
                    self.state = "DASH"; self.state_timer = 0
                    dash_dist = math.hypot(self.aim_x - self.x, self.aim_y - self.y)
                    self.dash_dir_x, self.dash_dir_y = (self.aim_x - self.x) / dash_dist, (self.aim_y - self.y) / dash_dist if dash_dist > 0 else (0,0)
                    self.play_shoot_sound = True 
            elif self.state == "DASH":
                self.x += self.dash_dir_x * (current_speed * 6); self.y += self.dash_dir_y * (current_speed * 6)
                if self.state_timer > 20: self.state = "CHASE"; self.state_timer = 0

        elif self.b_type == "PURPLE":
            if self.state == "FLEE":
                if dist > 0:
                    if dist < 300: self.x -= dir_x * current_speed; self.y -= dir_y * current_speed
                    else: self.x += -dir_y * current_speed; self.y += dir_x * current_speed
                if self.state_timer > 180: self.state = "SUMMON"; self.state_timer = 0
            elif self.state == "SUMMON":
                if self.state_timer == 45:
                    for _ in range(3): enemies.append(Enemy(level=5, is_elite=True, spawn_x=self.x, spawn_y=self.y))
                    self.play_shoot_sound = True
                if self.state_timer > 90: self.state = "FLEE"; self.state_timer = 0

        elif self.b_type == "CYAN":
            if self.state == "IDLE":
                if dist > 350: self.x += dir_x * current_speed; self.y += dir_y * current_speed
                elif dist < 250: self.x -= dir_x * current_speed; self.y -= dir_y * current_speed
                else: self.x += tangent_x * current_speed; self.y += tangent_y * current_speed
                
                if self.state_timer > 100: self.state = "FIRE"; self.state_timer = 0
            elif self.state == "FIRE":
                if self.state_timer == 10 or self.state_timer == 20 or self.state_timer == 30:
                    for i in range(-1, 2):
                        angle = math.atan2(dir_y, dir_x) + math.radians(i * 20)
                        enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, math.cos(angle), math.sin(angle), color=CYAN, is_homing=True))
                    self.play_shoot_sound = True
                if self.state_timer > 40: self.state = "IDLE"; self.state_timer = 0

        self.x = max(self.size, min(MAP_WIDTH - self.size, self.x))
        self.y = max(self.size, min(MAP_HEIGHT - self.size, self.y))
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        draw_rect = self.rect.copy(); draw_rect.center = draw_center
        
        anim_key = "boss_" + self.b_type
        anim_frames = animations.get(anim_key)
        
        if anim_frames:
            img = anim_frames[int(pygame.time.get_ticks() / 150) % len(anim_frames)]
            surface.blit(img, img.get_rect(center=draw_center))
        else:
            color = (100, 200, 255) if self.frost_timer > 0 else self.color
            if self.b_type == "CYAN":
                pts = [
                    (draw_center[0], draw_center[1] - self.size), (draw_center[0] + self.size, draw_center[1]),
                    (draw_center[0], draw_center[1] + self.size), (draw_center[0] - self.size, draw_center[1])
                ]
                pygame.draw.polygon(surface, color, pts); pygame.draw.polygon(surface, WHITE, pts, 3)
            else: pygame.draw.rect(surface, color, draw_rect)
        
        if self.b_type == "YELLOW":
            if self.state == "EVADE": pygame.draw.circle(surface, WHITE, draw_center, int(self.size/2) + 15, 3)
            elif self.state == "CHARGE": pygame.draw.circle(surface, RED, draw_center, int(self.size/2) + max(0, 30 - int(self.state_timer / 2)), 2)
        elif self.b_type == "RED":
            if self.state == "WARN": pygame.draw.line(surface, RED, draw_center, (int(self.aim_x - camera_x), int(self.aim_y - camera_y)), max(1, int(self.state_timer / 8)))
        elif self.b_type == "PURPLE":
            if self.state == "SUMMON": pygame.draw.circle(surface, DARK_PURPLE, draw_center, int(self.size/2) + min(60, self.state_timer), 3)
        elif self.b_type == "CYAN":
            if self.state == "FIRE": pygame.draw.circle(surface, CYAN, draw_center, int(self.size/2) + 20, 4)

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vel_x, self.vel_y = random.uniform(-6, 6), random.uniform(-6, 6)
        self.timer, self.size, self.color = random.randint(15, 30), random.randint(4, 8), color
    def update(self):
        self.x += self.vel_x; self.y += self.vel_y; self.timer -= 1; self.size = max(0, self.size - 0.25)
    def draw(self, surface):
        if self.size > 0: pygame.draw.rect(surface, self.color, (int(self.x - camera_x), int(self.y - camera_y), int(self.size), int(self.size)))

class DamageText:
    def __init__(self, x, y, damage, color=WHITE):
        self.x, self.y, self.damage, self.color = x, y, damage, color
        self.timer, self.vel_y, self.alpha = 40, -1.5, 255
        self.offset_x = random.randint(-15, 15)

    def update(self):
        self.y += self.vel_y; self.timer -= 1; self.alpha = max(0, int((self.timer / 40) * 255))

    def draw(self, surface):
        if self.timer > 0:
            txt_surf = font.render(f"-{int(self.damage)}", True, self.color)
            txt_surf.set_alpha(self.alpha) 
            surface.blit(txt_surf, (int(self.x + self.offset_x - camera_x), int(self.y - camera_y)))
            
class DropItem:
    def __init__(self, x, y, item_type="EXP"):
        self.x, self.y, self.item_type = x, y, item_type
        self.rect = pygame.Rect(0, 0, 14, 14)
        self.anim_offset = random.random() * 10
        self.saved_exp = 0 
        self.saved_level = 1
        
    def update(self, p_x, p_y, mag_rad):
        if self.item_type == "LOST_ITEM":
            self.rect.center = (int(self.x), int(self.y))
            return # 遺失物不會被磁鐵吸走
            
        dist = math.hypot(self.x - p_x, self.y - p_y)
        if dist < mag_rad and dist > 0:
            speed = 25 if mag_rad > 1000 else 8
            self.x += ((p_x - self.x) / dist) * speed 
            self.y += ((p_y - self.y) / dist) * speed 
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface):
        draw_x, draw_y = int(self.x - camera_x), int(self.y - camera_y)
        float_y = draw_y + math.sin(pygame.time.get_ticks()*0.005 + self.anim_offset) * 3
        
        if self.item_type == "LOST_ITEM":
            pygame.draw.rect(surface, (120, 120, 120), (draw_x - 12, float_y - 20, 24, 35), border_radius=4)
            pygame.draw.line(surface, GREEN, (draw_x, float_y - 12), (draw_x, float_y + 5), 4)
            pygame.draw.line(surface, GREEN, (draw_x - 8, float_y - 3), (draw_x + 8, float_y - 3), 4)
            return

        img = images.get(f"drop_{self.item_type}")
        if img: surface.blit(img, img.get_rect(center=(draw_x, int(float_y))))
        else:
            if self.item_type == "EXP": pygame.draw.polygon(surface, EXP_COLOR, [(draw_x, float_y-6), (draw_x+6, float_y), (draw_x, float_y+6), (draw_x-6, float_y)])
            elif self.item_type == "HP":
                pygame.draw.rect(surface, HP_COLOR, (draw_x-6, float_y-2, 12, 4)); pygame.draw.rect(surface, HP_COLOR, (draw_x-2, float_y-6, 4, 12))
            elif self.item_type == "SHIELD": pygame.draw.circle(surface, SHIELD_COLOR, (draw_x, int(float_y)), 6)
            elif self.item_type == "MAGNET":
                pygame.draw.circle(surface, YELLOW, (draw_x, int(float_y)), 7); pygame.draw.circle(surface, RED, (draw_x, int(float_y)), 7, 2)
            elif self.item_type == "BOMB":
                pygame.draw.circle(surface, (50, 50, 50), (draw_x, int(float_y)), 8)
                pygame.draw.circle(surface, RED, (draw_x, int(float_y)), 4); pygame.draw.circle(surface, ORANGE, (draw_x, int(float_y)), 9, 2)

upgrade_options =[
    {"title": "生命躍升", "desc": ["最大血量 +50", "並恢復當前血量"], "type": "life", "weight": 1},
    {"title": "超頻運轉", "desc": ["機槍射速提升", "子彈連發加快"], "type": "attack", "weight": 5},
    {"title": "能量飲料", "desc": ["體力恢復加快", "衝刺更加頻繁"], "type": "support", "weight": 3},
    {"title": "彈幕擴張", "desc": ["子彈發射數 +1", "形成扇形擴散"], "type": "attack", "weight": 5},
    {"title": "高能彈芯", "desc": ["子彈傷害增加", "打精英更有效"], "type": "attack", "weight": 5},
    {"title": "備用電池", "desc": ["最大體力 +25", "衝刺資源增加"], "type": "support", "weight": 3},
    {"title": "輕量推進", "desc": ["衝刺消耗降低", "更容易連續閃避"], "type": "support", "weight": 3},
    {"title": "離子靴", "desc": ["移動速度提升", "走位更加靈活"], "type": "support", "weight": 3},
    {"title": "磁吸核心", "desc": ["經驗吸取範圍", "大幅增加"], "type": "support", "weight": 3},
    {"title": "穩定槍管", "desc": ["散射角度縮小", "彈幕更集中"], "type": "attack", "weight": 5},
    {"title": "運動健將", "desc": ["衝刺時間增加", "位移距離更遠"], "type": "support", "weight": 3},
    {"title": "急救模組", "desc": ["立即恢復血量", "最多恢復 60"], "type": "life", "weight": 1},
    {"title": "相位護盾", "desc": ["受傷免傷延長", "更能脫離包圍"], "type": "life", "weight": 1},
    {"title": "裝甲鍍層", "desc": ["受到傷害降低", "硬扛能力提升"], "type": "life", "weight": 1},
    {"title": "爆燃推進", "desc": ["衝刺速度增加", "瞬間拉開距離"], "type": "support", "weight": 3},
    {"title": "生命本源", "desc": ["血量與體力上限", "小幅同步提升"], "type": "life", "weight": 1},
    {"title": "清道夫", "desc": ["吸取範圍增加", "體力恢復小幅提升"], "type": "support", "weight": 3},
    {"title": "寬幅槍口", "desc": ["同彈道追加子彈", "不再增加散射"], "type": "attack", "weight": 5},
    {"title": "導引模組", "desc": ["近距離小幅追蹤", "不會自動鎖全場"], "type": "attack", "weight": 5},
    {"title": "電弧光環", "desc": ["持續傷害附近敵人", "等級越高範圍越大"], "type": "attack", "weight": 5},
    {"title": "再生奈米", "desc": ["緩慢持續回血", "脫戰續航提升"], "type": "life", "weight": 1},
    {"title": "學習核心", "desc": ["經驗獲得 +20%", "升級速度提升"], "type": "support", "weight": 3},
    {"title": "擴容彈匣", "desc": ["挑戰限定卡牌", "增加彈藥庫上限"], "type": "attack", "weight": 4, "challenge_only": True},
    {"title": "快拆彈匣", "desc": ["挑戰限定卡牌", "換彈時間縮短"], "type": "support", "weight": 3, "challenge_only": True},
    {"title": "戰術無人機", "desc": ["召喚跟隨無人機", "自動鎖定攻擊敵人"], "type": "attack", "weight": 4}
]

exit_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 170, 200, 50)
start_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 30, 200, 50)
changelog_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50)
changelog_close_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 200, 200, 45)
normal_button = pygame.Rect(WIDTH//2 - 340, HEIGHT//2 - 35, 320, 230)
challenge_button = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 - 35, 320, 230)
difficulty_back_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 245, 220, 50)
restart_button = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 + 100, 200, 50)
menu_button = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 100, 200, 50)

cards =[
    pygame.Rect(WIDTH//2 - 370, 240, 220, 280),
    pygame.Rect(WIDTH//2 - 110, 240, 220, 280),
    pygame.Rect(WIDTH//2 + 150, 240, 220, 280)
]
confirm_upgrade_button = pygame.Rect(WIDTH//2 - 110, 560, 220, 50)

current_upgrade_choices = []
selected_upgrade_position = None
chosen_upgrades = []
pause_upgrade_scroll, changelog_scroll, changelog_max_scroll = 0, 0, 0
show_changelog = False
changelog_content_surface = None
game_mode = "NORMAL"

def wrap_text(text, text_font, max_width):
    lines = []; current = ""
    for char in text:
        test = current + char
        if text_font.size(test)[0] <= max_width: current = test
        else:
            if current: lines.append(current)
            current = char
    if current: lines.append(current)
    return lines

def rebuild_changelog_cache(content_width, content_height):
    global changelog_content_surface, changelog_max_scroll
    CHANGELOG = [
        "v1.9 - 撤離點與武裝進化",
        "- 新增：敵人全面升級，將隨機使用12把武器",
        "- 新增：撤離點機制！3分鐘內必須抵達綠色區域",
        "- 新增：死亡不會結束遊戲，會在地堡重生",
        "- 新增：地圖上保留「遺失物」，撿回可恢復全部經驗",
        "- 調整：若未能在時間內撤離，王級大軍將淹沒地圖",
        "v1.8 - 極速與動態挑戰",
        "- 新增：全新 BOSS 天網追蹤者 (CYAN)，會發射導航飛彈",
        "- 更新：玩家與敵人基礎速度全面加快，節奏更刺激",
    ]
    content_lines = []
    for line in CHANGELOG:
        color = YELLOW if line.startswith("v") else WHITE
        for wrapped_line in wrap_text(line, font, content_width - 20): content_lines.append((wrapped_line, color))
        content_lines.append(("", WHITE))

    surface_height = max(content_height, len(content_lines) * 34 + 10)
    changelog_content_surface = pygame.Surface((content_width, surface_height), pygame.SRCALPHA)
    for i, (line, color) in enumerate(content_lines):
        if line:
            text = font.render(line, True, color)
            changelog_content_surface.blit(text, (0, 6 + i * 34))
    changelog_max_scroll = max(0, surface_height - content_height)

def draw_changelog_popup(surface):
    popup = pygame.Rect(WIDTH//2 - 360, HEIGHT//2 - 280, 720, 560)
    panel = pygame.Surface((popup.width, popup.height), pygame.SRCALPHA); panel.fill((18, 20, 32, 235))
    surface.blit(panel, popup.topleft); pygame.draw.rect(surface, WHITE, popup, 3, border_radius=12)

    title = large_font.render("更新日誌", True, YELLOW)
    surface.blit(title, (popup.centerx - title.get_width()//2, popup.y + 20))

    content_rect = pygame.Rect(popup.x + 40, popup.y + 80, popup.width - 80, popup.height - 180)
    if changelog_content_surface is None: rebuild_changelog_cache(content_rect.width, content_rect.height)

    scroll_y = min(changelog_scroll, changelog_max_scroll)
    surface.blit(changelog_content_surface, content_rect.topleft, pygame.Rect(0, scroll_y, content_rect.width, content_rect.height))
    pygame.draw.rect(surface, GRAY, content_rect, 1)

    if changelog_max_scroll > 0:
        bar_h = max(40, int(content_rect.height * content_rect.height / changelog_content_surface.get_height()))
        bar_y = content_rect.y + int((content_rect.height - bar_h) * (scroll_y / changelog_max_scroll))
        pygame.draw.rect(surface, GRAY, (content_rect.right + 8, content_rect.y, 8, content_rect.height), border_radius=4)
        pygame.draw.rect(surface, YELLOW, (content_rect.right + 8, bar_y, 8, bar_h), border_radius=4)

    close_color = RED if changelog_close_button.collidepoint(pygame.mouse.get_pos()) else (150, 50, 50)
    pygame.draw.rect(surface, close_color, changelog_close_button, border_radius=10); pygame.draw.rect(surface, WHITE, changelog_close_button, 3, border_radius=10)
    close_txt = font.render("關閉", True, WHITE)
    surface.blit(close_txt, (changelog_close_button.centerx - close_txt.get_width()//2, changelog_close_button.centery - close_txt.get_height()//2))

def draw_upgrade_summary(surface, x, y, max_items=6, title="已選強化"):
    panel_width, row_height = 240, 26
    hidden_count = max(0, len(chosen_upgrades) - max_items)
    row_count = max(1, min(len(chosen_upgrades), max_items))
    panel_height = 40 + row_count * row_height + (row_height if hidden_count else 0)
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA); panel.fill((18, 20, 30, 185))
    surface.blit(panel, (x, y)); pygame.draw.rect(surface, WHITE, (x, y, panel_width, panel_height), 2, border_radius=8)

    total_count = sum(u["count"] for u in chosen_upgrades)
    title_txt = small_font.render(f"{title} ({total_count})" if chosen_upgrades else title, True, YELLOW)
    surface.blit(title_txt, (x + 14, y + 10))

    if not chosen_upgrades:
        surface.blit(small_font.render("尚未選擇", True, GRAY), (x + 14, y + 40))
        return

    for i, upgrade in enumerate(chosen_upgrades[-max_items:]):
        suffix = f" x{upgrade['count']}" if upgrade["count"] > 1 else ""
        surface.blit(small_font.render(f"{upgrade['title']}{suffix}", True, WHITE), (x + 14, y + 40 + i * row_height))

    if hidden_count: surface.blit(small_font.render(f"還有 {hidden_count} 種...", True, GRAY), (x + 14, y + 40 + min(len(chosen_upgrades), max_items) * row_height))

def draw_pause_upgrade_log(surface):
    panel_rect = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 + 155, 600, 180)
    panel = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA); panel.fill((18, 20, 30, 205))
    surface.blit(panel, panel_rect.topleft); pygame.draw.rect(surface, WHITE, panel_rect, 2, border_radius=8)

    surface.blit(small_font.render("本局強化紀錄（滑鼠滾輪瀏覽）", True, YELLOW), (panel_rect.x + 16, panel_rect.y + 12))
    content_rect = pygame.Rect(panel_rect.x + 16, panel_rect.y + 40, panel_rect.width - 32, panel_rect.height - 50)

    rows = []
    for u in chosen_upgrades:
        opt = next((o for o in upgrade_options if o["title"] == u["title"]), None)
        rows.append((f"{u['title']}{' x'+str(u['count']) if u['count']>1 else ''}", " / ".join(opt["desc"]) if opt else ""))

    if not rows:
        surface.blit(small_font.render("尚未選擇任何強化", True, GRAY), (content_rect.x, content_rect.y + 8))
        return

    row_h = 50
    content_height = max(content_rect.height, len(rows) * row_h)
    max_scroll = max(0, content_height - content_rect.height)
    scroll_y = min(pause_upgrade_scroll, max_scroll)
    content_surface = pygame.Surface((content_rect.width, content_height), pygame.SRCALPHA)

    for i, (name, desc) in enumerate(rows):
        content_surface.blit(small_font.render(name, True, WHITE), (0, i * row_h))
        for j, line in enumerate(wrap_text(desc, tiny_font, content_rect.width - 20)):
            content_surface.blit(tiny_font.render(line, True, YELLOW), (18, i * row_h + 20 + j * 16))

    surface.blit(content_surface, content_rect.topleft, pygame.Rect(0, scroll_y, content_rect.width, content_rect.height))

def draw_arrow_to_target(surface, tx, ty, color=YELLOW, label=""):
    screen_x, screen_y = tx - camera_x, ty - camera_y
    if 0 <= screen_x <= WIDTH and 0 <= screen_y <= HEIGHT: return

    center = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
    direction = pygame.math.Vector2(screen_x - center.x, screen_y - center.y)
    if direction.length_squared() == 0: return
    direction.normalize_ip()
    scale_x = (WIDTH / 2 - 56) / abs(direction.x) if abs(direction.x) > 0.001 else float("inf")
    scale_y = (HEIGHT / 2 - 56) / abs(direction.y) if abs(direction.y) > 0.001 else float("inf")
    arrow_pos = center + direction * min(scale_x, scale_y)
    side = direction.rotate(90)
    tip, left, right = arrow_pos + direction * 25, arrow_pos - direction * 18 + side * 15, arrow_pos - direction * 18 - side * 15
    pts = [(int(tip.x), int(tip.y)), (int(left.x), int(left.y)), (int(right.x), int(right.y))]
    pygame.draw.polygon(surface, BLACK, pts); pygame.draw.polygon(surface, color, pts, 0); pygame.draw.polygon(surface, WHITE, pts, 2)
    if label:
        txt = small_font.render(label, True, color)
        surface.blit(txt, (arrow_pos.x - txt.get_width()//2, arrow_pos.y - 40))

def choose_upgrade_cards():
    global current_upgrade_choices, selected_upgrade_position
    available = [i for i, option in enumerate(upgrade_options) if game_mode == "CHALLENGE" or not option.get("challenge_only")]
    current_upgrade_choices = []
    for _ in range(min(3, len(available))):
        total_weight = sum(upgrade_options[i].get("weight", 1) for i in available)
        if total_weight <= 0: break
        pick = random.uniform(0, total_weight)
        running_weight = 0
        for i in available:
            running_weight += upgrade_options[i].get("weight", 1)
            if pick <= running_weight:
                current_upgrade_choices.append(i); available.remove(i); break
    selected_upgrade_position = None

def apply_upgrade(choice):
    global game_state, selected_upgrade_position
    if choice == 0: player.max_hp += 50; player.hp += 50
    elif choice == 1: player.shoot_delay_reduction += 2 
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
    elif choice == 15: player.max_hp += 25; player.max_stamina += 15; player.hp += 25; player.stamina += 15
    elif choice == 16: player.magnet_radius += 25; player.stamina_regen += 0.15
    elif choice == 17: player.extra_same_path_bullets += 1
    elif choice == 18: player.guidance_level += 1
    elif choice == 19: player.aura_level += 1
    elif choice == 20: player.regen_level += 1
    elif choice == 21: player.exp_multiplier += 0.2
    elif choice == 22: player.mag_size_bonus += 10; player.ammo += 10
    elif choice == 23: player.reload_duration = max(30, player.reload_duration - 15)
    elif choice == 24: player.drone_level += 1

    title = upgrade_options[choice]["title"]
    found = False
    for u in chosen_upgrades:
        if u["title"] == title: u["count"] += 1; found = True; break
    if not found: chosen_upgrades.append({"title": title, "count": 1})

    current_upgrade_choices.clear(); selected_upgrade_position = None; game_state = "PLAYING"             

def deploy_to_map():
    global game_state, camera_x, camera_y, extraction_timer, swarm_mode, extraction_point
    global enemies, bullets, enemy_bullets, particles, items, trails, bosses
    game_state = "PLAYING"
    items = [i for i in items if i.item_type == "LOST_ITEM"] # 只保留遺失物
    enemies.clear(); bullets.clear(); enemy_bullets.clear(); particles.clear(); trails.clear(); bosses.clear()
    
    player.x, player.y = MAP_WIDTH//2, MAP_HEIGHT//2
    camera_x = max(0, min(MAP_WIDTH - WIDTH, player.x - WIDTH / 2))
    camera_y = max(0, min(MAP_HEIGHT - HEIGHT, player.y - HEIGHT / 2))
    
    extraction_timer = 180 * 60 # 3分鐘
    swarm_mode = False
    ext_x, ext_y = random.randint(500, MAP_WIDTH-500), random.randint(500, MAP_HEIGHT-500)
    extraction_point = ExtractionPoint(ext_x, ext_y)
    stop_sound("boss_bgm")

def reset_game(initial_state="MENU", mode="NORMAL"):
    global player, bullets, enemy_bullets, enemies, particles, items, trails
    global bosses, defeated_boss_levels, game_state, shoot_cooldown
    global key_buffer, damage_texts, camera_x, camera_y, game_mode
    global current_upgrade_choices, selected_upgrade_position, chosen_upgrades
    global show_changelog, changelog_scroll, changelog_content_surface, changelog_max_scroll, pause_upgrade_scroll
    global magnet_timer, screen_flash_timer, extraction_timer, swarm_mode, extraction_point

    game_mode = mode
    player = Player()
    bullets, enemy_bullets, enemies, particles, items, trails, damage_texts, bosses = [], [], [], [], [], [], [], []
    defeated_boss_levels = [] 
    shoot_cooldown, key_buffer = 0, []
    camera_x, camera_y = 0, 0
    
    current_upgrade_choices, selected_upgrade_position, chosen_upgrades = [], None, []
    show_changelog, changelog_scroll, changelog_content_surface, changelog_max_scroll, pause_upgrade_scroll = False, 0, None, 0, 0
    magnet_timer, screen_flash_timer = 0, 0
    extraction_timer, swarm_mode, extraction_point = 0, False, None
    
    stop_sound("boss_bgm")
    game_state = initial_state
    if initial_state == "BUNKER": player.x, player.y = WIDTH//2, HEIGHT//2

reset_game()
SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY_EVENT, 500) 

dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); dim_surface.fill((0, 0, 0, 180))

running = True
while running:
    player_dead = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
            
        if game_state == "MENU" and show_changelog and event.type == pygame.MOUSEWHEEL:
            changelog_scroll = max(0, min(changelog_max_scroll, changelog_scroll - event.y * 55))
        if game_state == "PAUSED" and event.type == pygame.MOUSEWHEEL:
            pause_upgrade_scroll = max(0, pause_upgrade_scroll - event.y * 45)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if game_state == "PLAYING": game_state = "PAUSED"
            elif game_state == "PAUSED": game_state = "PLAYING"
            elif game_state == "DIFFICULTY": game_state = "MENU"
        
        if game_state == "PLAYING" and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            if game_mode == "CHALLENGE" and player.reload_timer <= 0 and player.ammo < (player.base_max_ammo + player.mag_size_bonus):
                player.reload_timer = player.reload_duration

        if game_state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_changelog:
                    if changelog_close_button.collidepoint(event.pos): show_changelog, changelog_scroll = False, 0
                else:
                    if start_button.collidepoint(event.pos): game_state = "DIFFICULTY"
                    elif changelog_button.collidepoint(event.pos):
                        show_changelog, changelog_scroll = True, 0
                        if changelog_content_surface is None: rebuild_changelog_cache(640, 380)
                    elif exit_button.collidepoint(event.pos): running = False

        elif game_state == "DIFFICULTY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if normal_button.collidepoint(event.pos): reset_game("BUNKER", "NORMAL")
                elif challenge_button.collidepoint(event.pos): reset_game("BUNKER", "CHALLENGE")
                elif difficulty_back_button.collidepoint(event.pos): game_state = "MENU"

        elif game_state == "PAUSED":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 10, 220, 50).collidepoint(event.pos): game_state = "PLAYING"
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 10, 220, 50).collidepoint(event.pos): reset_game("MENU", "NORMAL")
                elif pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 80, 220, 50).collidepoint(event.pos): reset_game("BUNKER", game_mode)
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 80, 220, 50).collidepoint(event.pos): running = False

        elif game_state == "LEVEL_UP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected_upgrade_position is not None and confirm_upgrade_button.collidepoint(event.pos):
                    apply_upgrade(current_upgrade_choices[selected_upgrade_position])
                else:
                    for i, card in enumerate(cards):
                        if i < len(current_upgrade_choices) and card.collidepoint(event.pos):
                            selected_upgrade_position = i; break

        elif game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: reset_game("BUNKER", game_mode)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_button.collidepoint(event.pos): reset_game("BUNKER", game_mode)
                elif menu_button.collidepoint(event.pos): reset_game("MENU", "NORMAL")

        elif game_state == "PLAYING":
            if event.type == SPAWN_ENEMY_EVENT: 
                enemies.append(Enemy(player.level, random.random() < 0.15, player.x, player.y))
                
            if event.type == pygame.KEYDOWN:
                key_buffer.append(event.key)
                if len(key_buffer) > len(CHEAT_CODE): key_buffer.pop(0) 
                if key_buffer == CHEAT_CODE:
                    player.god_mode = not player.god_mode
                    play_sound("levelup"); key_buffer = [] 
                if event.key == pygame.K_e:
                    player.current_weapon_idx = (player.current_weapon_idx + 1) % len(player.weapons)
                    play_sound("exp")

    # === BUNKER (地堡邏輯) ===
    if game_state == "BUNKER":
        player.update()
        portal_pos = (WIDTH//2, HEIGHT//2 - 180)
        if math.hypot(player.x - portal_pos[0], player.y - portal_pos[1]) < 60:
            deploy_to_map()

    # === PLAYING (地圖邏輯) ===
    if game_state == "PLAYING":
        camera_x = max(0, min(MAP_WIDTH - WIDTH, player.x - WIDTH / 2))
        camera_y = max(0, min(MAP_HEIGHT - HEIGHT, player.y - HEIGHT / 2))
        
        if magnet_timer > 0: magnet_timer -= 1
        if screen_flash_timer > 0: screen_flash_timer -= 1
        
        if extraction_timer > 0:
            extraction_timer -= 1
            if extraction_timer <= 0:
                swarm_mode = True
                play_sound("boss_bgm", loop=-1)
        
        if swarm_mode:
            if random.random() < 0.15: enemies.append(Enemy(player.level, True, player.x, player.y)) 
            if random.random() < 0.005: bosses.append(Boss(random.choice(["YELLOW", "RED", "PURPLE", "CYAN"]), player.level, player.x, player.y))

        if extraction_point:
            if extraction_point.update(player.x, player.y):
                # 成功撤離
                game_state = "BUNKER"
                player.x, player.y = WIDTH//2, HEIGHT//2
                player.hp = player.max_hp; player.shield = player.max_shield
                extraction_point = None

        # Level UP Queuing
        if player.pending_level_ups > 0:
            player.pending_level_ups -= 1
            choose_upgrade_cards(); game_state = "LEVEL_UP"
            play_sound("levelup") 

        mouse_btns = pygame.mouse.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_mouse_x, world_mouse_y = mouse_x + camera_x, mouse_y + camera_y
        current_wep = player.weapons[player.current_weapon_idx]

        if mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing:
            can_fire = True
            if game_mode == "CHALLENGE":
                if player.ammo <= 0:
                    can_fire = False
                    if player.reload_timer <= 0: player.reload_timer = player.reload_duration
                else:
                    player.ammo -= 1
                    if player.ammo <= 0: player.reload_timer = player.reload_duration
            
            if can_fire:
                base_dir = pygame.math.Vector2(world_mouse_x - player.x, world_mouse_y - player.y)
                if base_dir.length() > 0: base_dir.normalize_ip()
                else: base_dir = pygame.math.Vector2(1, 0)
                
                total_bullets = player.bullet_count + (4 if current_wep.bullet_type == "shotgun" else 0)
                current_spread = player.bullet_spread
                start_angle = -(total_bullets - 1) * current_spread / 2
                
                for i in range(total_bullets):
                    angle = start_angle + (i * current_spread)
                    shot_dir = base_dir.rotate(angle)
                    
                    same_path_count = 1 + player.extra_same_path_bullets
                    for j in range(same_path_count):
                        spawn_offset = shot_dir * (j * 15)
                        tx = player.x + shot_dir.x * 100 + spawn_offset.x
                        ty = player.y + shot_dir.y * 100 + spawn_offset.y
                        
                        if current_wep.bullet_type == "flamethrower":
                            tx += random.randint(-40, 40); ty += random.randint(-40, 40)
                            
                        bullets.append(Bullet(
                            player.rect.centerx + spawn_offset.x, player.rect.centery + spawn_offset.y, 
                            tx, ty, current_wep, guidance_level=player.guidance_level, dmg_bonus=player.bullet_damage_bonus
                        ))
                
                shoot_cooldown = max(2, current_wep.shoot_delay - player.shoot_delay_reduction)
                play_sound("shoot")
            
        if mouse_btns[2] and player.skill_cd <= 0 and player.energy >= player.skill_cost and not player.is_dashing:
            player.energy -= player.skill_cost
            player.skill_cd = player.skill_max_cd 
            play_sound("shoot") 
            temp_wep = Weapon("技能", 0, "piercing", 50) 
            for i in range(16):
                angle = math.radians(i * (360 / 16))
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, player.rect.centerx + math.cos(angle)*100, player.rect.centery + math.sin(angle)*100, temp_wep, dmg_bonus=player.bullet_damage_bonus))

        if shoot_cooldown > 0: shoot_cooldown -= 1
        player.update()
        
        if player.drone_level > 0:
            player.drone_angle += 0.05
            if player.drone_shoot_cd > 0: player.drone_shoot_cd -= 1
            if player.drone_shoot_cd <= 0 and enemies:
                closest = min(enemies, key=lambda e: math.hypot(e.x - player.x, e.y - player.y))
                if math.hypot(closest.x - player.x, closest.y - player.y) < 400:
                    temp_wep = Weapon("無人機", 0, "normal", 10 + player.drone_level * 8)
                    drone_world_x = player.x + math.cos(player.drone_angle) * 55
                    drone_world_y = player.y + math.sin(player.drone_angle) * 55
                    bullets.append(Bullet(drone_world_x, drone_world_y, closest.x, closest.y, temp_wep))
                    player.drone_shoot_cd = max(10, 60 - player.drone_level * 10)
        
        if player.aura_level > 0:
            aura_radius = 95 + player.aura_level * 25
            aura_damage = 0.02 * player.aura_level
            for e in enemies[:]:
                if math.hypot(e.x - player.x, e.y - player.y) <= aura_radius:
                    if e.shield > 0:
                        if aura_damage > e.shield:
                            leftover = aura_damage - e.shield; e.shield = 0; e.hp -= leftover
                        else: e.shield -= aura_damage
                    else: e.hp -= aura_damage
                        
                    if random.random() < 0.05: particles.append(Particle(e.x, e.y, BLUE))
                    if e.hp <= 0:
                        for _ in range(8): particles.append(Particle(e.x, e.y, RED))
                        if random.random() < 0.4: items.append(DropItem(e.x, e.y, "EXP"))
                        enemies.remove(e)
            for boss in bosses:
                if boss.state != "DEFEAT":
                    if math.hypot(boss.x - player.x, boss.y - player.y) <= aura_radius: boss.hp -= aura_damage
        
        if player.is_dashing: trails.append(DashTrail(player.rect.centerx, player.rect.centery, player.size))
        for t in trails[:]:
            t.update(); 
            if t.life <= 0: trails.remove(t)
            
        for b in bullets[:]:
            b.update()
            if b.explode:
                play_sound("shoot") 
                for _ in range(30): particles.append(Particle(b.x, b.y, ORANGE))
                for e in enemies[:]:
                    if math.hypot(e.x - b.x, e.y - b.y) < 120: 
                        if e.shield > 0:
                            if b.damage > e.shield: leftover = b.damage - e.shield; e.shield = 0; e.hp -= leftover
                            else: e.shield -= b.damage
                        else: e.hp -= b.damage
                            
                        if e.hp <= 0: 
                            if random.random() < 0.4: items.append(DropItem(e.x, e.y, "EXP"))
                            enemies.remove(e)
                for boss in bosses:
                    if math.hypot(boss.x - b.x, boss.y - b.y) < 150: boss.hp -= b.damage
                bullets.remove(b); continue
                
            if b.lifespan <= 0 or not pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT).colliderect(b.rect): bullets.remove(b)
            
        for eb in enemy_bullets[:]:
            eb.update(player.x, player.y) 
            if not pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT).colliderect(eb.rect): enemy_bullets.remove(eb)
                
        for dt in damage_texts[:]:
            dt.update()
            if dt.timer <= 0: damage_texts.remove(dt)    
                
        for e in enemies: e.update(player.x, player.y, enemies, enemy_bullets)
        for p in particles[:]:
            p.update()
            if p.timer <= 0: particles.remove(p)

        for boss in bosses:
            boss.update(player.x, player.y, bullets, enemies, enemy_bullets)
            if boss.play_shoot_sound: play_sound("shoot")

        # 子彈判定
        for b in bullets[:]:
            hit_something = False
            for e in enemies[:]:
                if b.rect.colliderect(e.rect):
                    if b.b_type == "frost": e.frost_timer = 120 
                    if b.b_type == "cannon": 
                        push_dist = math.hypot(e.x - player.x, e.y - player.y)
                        if push_dist > 0: e.x += ((e.x - player.x) / push_dist) * 30; e.y += ((e.y - player.y) / push_dist) * 30 
                    elif b.b_type == "flame_grenade": b.explode = True; break
                        
                    if e.shield > 0:
                        if b.damage > e.shield:
                            leftover = b.damage - e.shield; e.shield = 0; e.hp -= leftover
                        else: e.shield -= b.damage
                    else: e.hp -= b.damage
                        
                    damage_texts.append(DamageText(e.x, e.y - 20, b.damage, YELLOW if b.damage >= 40 else WHITE))
                    hit_something = True
                    for _ in range(5): particles.append(Particle(e.x, e.y, b.color))
                    play_sound("hit")
                    
                    if e.hp <= 0:
                        for _ in range(10): particles.append(Particle(e.x, e.y, RED))
                        if e.is_elite: 
                            items.append(DropItem(e.x-15, e.y, "EXP")); items.append(DropItem(e.x+15, e.y, "HP")); items.append(DropItem(e.x, e.y+15, "SHIELD"))
                        else:
                            rand_drop = random.random()
                            if rand_drop < 0.01: items.append(DropItem(e.x, e.y, "MAGNET"))
                            elif rand_drop < 0.02: items.append(DropItem(e.x, e.y, "BOMB"))
                            elif rand_drop < 0.3: items.append(DropItem(e.x, e.y, "EXP"))
                            elif rand_drop < 0.34: items.append(DropItem(e.x, e.y, "HP"))
                            elif rand_drop < 0.38: items.append(DropItem(e.x, e.y, "SHIELD"))
                        enemies.remove(e)
            
            if b.explode: continue 

            for boss in bosses:
                if b.rect.colliderect(boss.rect):
                    hit_something = True
                    if boss.b_type == "YELLOW" and boss.state == "EVADE":
                        for _ in range(5): particles.append(Particle(boss.x, boss.y, GRAY))
                    else:
                        if b.b_type == "frost": boss.frost_timer = 60 
                        boss.hp -= b.damage
                        for _ in range(8): particles.append(Particle(boss.x, boss.y, YELLOW))
                        play_sound("hit")
                        
                        if boss.hp <= 0:
                            boss.state = "DEFEAT"
                            defeated_boss_levels.append(player.level) 
                            for _ in range(40): items.append(DropItem(boss.x + random.randint(-60,60), boss.y + random.randint(-60,60), "EXP"))
                            for _ in range(50): particles.append(Particle(boss.x, boss.y, YELLOW))
                            
            if hit_something and not b.is_piercing and b in bullets: bullets.remove(b)
            
        bosses = [b for b in bosses if b.state != "DEFEAT"]

        def player_take_damage(dmg):
            global player_dead
            if player.god_mode: return
            if player.invincible_timer <= 0 and not player.is_dashing:
                actual_dmg = max(1, dmg - player.damage_reduction)
                if player.shield > 0:
                    if actual_dmg > player.shield:
                        leftover = actual_dmg - player.shield; player.shield = 0; player.hp -= leftover
                    else: player.shield -= actual_dmg
                else: player.hp -= actual_dmg
                
                player.invincible_timer = player.invincible_duration 
                play_sound("hurt")
                if player.hp <= 0: player_dead = True

        for e in enemies[:]:
            if player.rect.colliderect(e.rect):
                if e.combat_type == "kamikaze":
                    player_take_damage(e.damage)
                    for _ in range(15): particles.append(Particle(e.x, e.y, ORANGE))
                    enemies.remove(e)
                else: player_take_damage(e.damage)
                    
        for eb in enemy_bullets[:]:
            if player.rect.colliderect(eb.rect):
                player_take_damage(eb.damage)
                if eb in enemy_bullets: enemy_bullets.remove(eb)
                
        for boss in bosses:
            if player.rect.colliderect(boss.rect): player_take_damage(40) 

        eff_radius = 9999 if magnet_timer > 0 else player.magnet_radius
        for g in items[:]:
            g.update(player.x, player.y, eff_radius)
            if player.rect.colliderect(g.rect):
                items.remove(g)
                if g.item_type == "LOST_ITEM":
                    player.exp += getattr(g, "saved_exp", 0)
                    play_sound("levelup")
                    while player.exp >= player.max_exp:
                        player.level += 1; player.exp -= player.max_exp; player.max_exp = int(player.max_exp * 1.25)
                        player.pending_level_ups += 1
                elif g.item_type == "EXP":
                    player.exp += 25 * player.exp_multiplier
                    play_sound("exp") 
                    if player.exp >= player.max_exp:
                        player.level += 1; player.exp -= player.max_exp; player.max_exp = int(player.max_exp * 1.25)
                        player.pending_level_ups += 1
                elif g.item_type == "HP": player.hp = min(player.max_hp, player.hp + 20); play_sound("exp")
                elif g.item_type == "SHIELD": player.shield = min(player.max_shield, player.shield + 20); play_sound("exp")
                elif g.item_type == "MAGNET": magnet_timer = 300; play_sound("levelup")
                elif g.item_type == "BOMB":
                    screen_flash_timer = 15
                    for e in enemies[:]:
                        for _ in range(8): particles.append(Particle(e.x, e.y, RED))
                        items.append(DropItem(e.x, e.y, "EXP"))
                    enemies.clear()
                    for boss in bosses: boss.hp -= 800; [particles.append(Particle(boss.x, boss.y, ORANGE)) for _ in range(15)]
                    play_sound("hit")

        # 玩家死亡結算邏輯：掉落遺失物並返回地堡
        if player_dead:
            li = DropItem(player.x, player.y, "LOST_ITEM")
            li.saved_exp = player.exp + (player.level * 100) # 給予巨量經驗以還原等級
            items = [i for i in items if i.item_type != "LOST_ITEM"] # 移除舊的
            items.append(li)
            
            player = Player()
            chosen_upgrades.clear(); current_upgrade_choices.clear()
            game_state = "BUNKER"
            player.x, player.y = WIDTH//2, HEIGHT//2
            stop_sound("boss_bgm")

    # --- 畫面渲染 ---
    if game_state == "BUNKER":
        screen.fill(BLACK)
        # 地堡背景
        pygame.draw.rect(screen, (30, 30, 40), (WIDTH//2 - 400, HEIGHT//2 - 300, 800, 600))
        pygame.draw.rect(screen, WHITE, (WIDTH//2 - 400, HEIGHT//2 - 300, 800, 600), 5)
        # 撤離傳送門
        portal_pos = (WIDTH//2, HEIGHT//2 - 180)
        pulse = math.sin(pygame.time.get_ticks() * 0.005) * 10
        pygame.draw.circle(screen, (0, 255, 100, 100), portal_pos, int(50 + pulse), 3)
        pygame.draw.circle(screen, (0, 200, 50), portal_pos, 45)
        
        txt1 = large_font.render("安全區 (地堡)", True, YELLOW)
        txt2 = font.render("踏入上方傳送門部署至地圖", True, WHITE)
        screen.blit(txt1, (WIDTH//2 - txt1.get_width()//2, HEIGHT//2 + 50))
        screen.blit(txt2, (WIDTH//2 - txt2.get_width()//2, HEIGHT//2 + 120))
        
        player.draw(screen, player.weapons[player.current_weapon_idx])

    elif game_state in ["PLAYING", "PAUSED", "LEVEL_UP", "GAME_OVER"]:
        if images.get("bg"):
            bg_w, bg_h = WIDTH, HEIGHT
            for x in range(0, MAP_WIDTH, bg_w):
                for y in range(0, MAP_HEIGHT, bg_h):
                    draw_x, draw_y = x - int(camera_x), y - int(camera_y)
                    if draw_x + bg_w > 0 and draw_x < WIDTH and draw_y + bg_h > 0 and draw_y < HEIGHT:
                        screen.blit(images["bg"], (draw_x, draw_y))
        else: screen.fill(BLACK)
        
        pygame.draw.rect(screen, RED, (-int(camera_x), -int(camera_y), MAP_WIDTH, MAP_HEIGHT), 5)
            
        if extraction_point: extraction_point.draw(screen)
        for it in items: it.draw(screen)
        for p in particles: p.draw(screen)
        for b in bullets: b.draw(screen)
        for eb in enemy_bullets: eb.draw(screen) 
        for e in enemies: e.draw(screen)
        for t in trails: t.draw(screen)
        for dt in damage_texts: dt.draw(screen)
        for boss in bosses: boss.draw(screen); draw_boss_direction_arrow(screen, boss, camera_x, camera_y)
        
        if extraction_point: draw_arrow_to_target(screen, extraction_point.x, extraction_point.y, GREEN, "撤離點")
            
        player.draw(screen, player.weapons[player.current_weapon_idx] if game_state == "PLAYING" else None)

        if screen_flash_timer > 0:
            flash_surface = pygame.Surface((WIDTH, HEIGHT)); flash_surface.fill(WHITE)
            flash_surface.set_alpha(int((screen_flash_timer / 15) * 255)); screen.blit(flash_surface, (0, 0))
        
        # 繪製 HUD 資訊
        pygame.draw.rect(screen, GRAY, (20, 20, 250, 15))
        pygame.draw.rect(screen, BLUE, (20, 20, 250 * (player.exp / player.max_exp), 15))
        screen.blit(font.render("等級: " + str(player.level), True, WHITE), (280, 15))

        pygame.draw.rect(screen, GRAY, (20, 45, 200, 15))
        pygame.draw.rect(screen, GREEN if player.hp > 30 else RED, (20, 45, 200 * (max(0, player.hp) / player.max_hp), 15))
        screen.blit(font.render("血量", True, WHITE), (230, 40))

        pygame.draw.rect(screen, GRAY, (20, 70, 200, 15))
        pygame.draw.rect(screen, (0, 150, 255), (20, 70, 200 * (max(0, player.shield) / player.max_shield), 15))
        screen.blit(font.render("護盾", True, WHITE), (230, 65))

        pygame.draw.rect(screen, GRAY, (20, 95, 150, 10))
        pygame.draw.rect(screen, ORANGE, (20, 95, 150 * (player.stamina / player.max_stamina), 10))
        screen.blit(font.render("體力 (Q鍵衝刺)", True, WHITE), (180, 87)) 
        
        pygame.draw.rect(screen, GRAY, (20, 115, 150, 10))
        pygame.draw.rect(screen, CYAN, (20, 115, 150 * (player.energy / player.max_energy), 10))
        screen.blit(font.render("能量", True, WHITE), (180, 107))

        weapon_str = "武器: " + player.weapons[player.current_weapon_idx].name + " (E 鍵切換)"
        if game_mode == "CHALLENGE": weapon_str = "[挑戰] " + weapon_str
        screen.blit(font.render(weapon_str, True, WHITE if game_mode == "NORMAL" else RED), (20, 140))

        if player.skill_cd > 0: skill_txt = font.render(f"技能冷卻: {round(player.skill_cd / 60, 1)} 秒", True, GRAY)
        elif player.energy < player.skill_cost: skill_txt = font.render("技能: 能量不足", True, RED)
        else: skill_txt = font.render("技能準備就緒 (右鍵)", True, GREEN)
        screen.blit(skill_txt, (WIDTH - 280, HEIGHT - 40))

        if game_mode == "CHALLENGE":
            ammo_txt = font.render(f"彈藥: {player.ammo} / {player.base_max_ammo + player.mag_size_bonus}", True, WHITE if player.ammo > 0 else RED)
            screen.blit(ammo_txt, (20, 165))
            if player.reload_timer > 0:
                reload_ratio = 1 - (player.reload_timer / player.reload_duration)
                pygame.draw.rect(screen, GRAY, (20, 195, 150, 10)); pygame.draw.rect(screen, YELLOW, (20, 195, 150 * reload_ratio, 10))
                screen.blit(small_font.render("換彈中...", True, YELLOW), (180, 190))

        # 撤離倒數計時與狀態顯示
        if extraction_timer > 0:
            secs = extraction_timer // 60; mins = secs // 60; secs = secs % 60
            time_txt = large_font.render(f"撤離倒數: {mins:02d}:{secs:02d}", True, WHITE)
            screen.blit(time_txt, (WIDTH//2 - time_txt.get_width()//2, 20))
        else:
            warn_txt = large_font.render("⚠️ 信號崩潰，大軍來襲！強行突圍撤離！ ⚠️", True, RED)
            screen.blit(warn_txt, (WIDTH//2 - warn_txt.get_width()//2, 20))

        for i, boss in enumerate(bosses):
            bar_w = WIDTH - 100
            pygame.draw.rect(screen, GRAY, (50, HEIGHT - 60 - i*30, bar_w, 20))
            boss_bar_color = RED if boss.b_type == "RED" else PURPLE if boss.b_type == "PURPLE" else CYAN if boss.b_type == "CYAN" else YELLOW
            pygame.draw.rect(screen, boss_bar_color, (50, HEIGHT - 60 - i*30, bar_w * (max(0, boss.hp) / boss.max_hp), 20))
            if i == 0:
                boss_txt = font.render("極度危險異常實體", True, WHITE)
                screen.blit(boss_txt, (WIDTH//2 - boss_txt.get_width()//2, HEIGHT - 90))

        if player.god_mode: screen.blit(font.render("【無敵模式啟用】", True, YELLOW), (WIDTH//2 - 100, 70))
        draw_upgrade_summary(screen, WIDTH - 260, 20, max_items=5)

    if game_state == "MENU":
        screen.fill(BLACK)
        for i in range(100):
            x, y = (i * 37) % WIDTH, (i * 23) % HEIGHT
            brightness = 100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)
        for i in range(20):
            x, y = (WIDTH//2 + math.cos(pygame.time.get_ticks() * 0.002 + i) * 300) % WIDTH, (HEIGHT//2 + math.sin(pygame.time.get_ticks() * 0.001 + i) * 200) % HEIGHT
            alpha = 50 + 30 * math.sin(pygame.time.get_ticks() * 0.003 + i)
            psurf = pygame.Surface((4, 4), pygame.SRCALPHA); pygame.draw.circle(psurf, (100, 150, 255, alpha), (2, 2), 2); screen.blit(psurf, (x, y))
        
        glow_color = (0, 100, 255, 50)
        glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        title = large_font.render("驅 魔 人", True, BLUE)
        glow_surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -3), (0, 3), (-3, 0), (3, 0)]:
            glow_copy = glow_surface.copy(); glow_copy.fill(glow_color, special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(glow_copy, offset)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        subtitle = font.render("A3 視覺重製版 + 塔科夫撤離模式", True, WHITE)
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2 - 60))

        mouse_pos = pygame.mouse.get_pos()
        start_hover = start_button.collidepoint(mouse_pos)
        if start_hover:
            scale = 1.05
            scaled_btn = pygame.Rect(start_button.centerx - start_button.width * scale // 2, start_button.centery - start_button.height * scale // 2, start_button.width * scale, start_button.height * scale)
            pygame.draw.rect(screen, (100, 200, 100), scaled_btn, border_radius=12); pygame.draw.rect(screen, YELLOW, scaled_btn, 4, border_radius=12)
        else: pygame.draw.rect(screen, (50, 150, 50), start_button, border_radius=10); pygame.draw.rect(screen, WHITE, start_button, 3, border_radius=10)
        start_txt = font.render("開始遊戲", True, WHITE)
        screen.blit(start_txt, (start_button.centerx - start_txt.get_width()//2, start_button.centery - start_txt.get_height()//2))

        changelog_color = BLUE if changelog_button.collidepoint(mouse_pos) else (50, 100, 150)
        pygame.draw.rect(screen, changelog_color, changelog_button, border_radius=10); pygame.draw.rect(screen, WHITE, changelog_button, 3, border_radius=10)
        c_txt = font.render("更新日誌", True, WHITE)
        screen.blit(c_txt, (changelog_button.centerx - c_txt.get_width()//2, changelog_button.centery - c_txt.get_height()//2))

        exit_color = RED if exit_button.collidepoint(mouse_pos) else (150, 50, 50)
        pygame.draw.rect(screen, exit_color, exit_button, border_radius=10); pygame.draw.rect(screen, WHITE, exit_button, 3, border_radius=10)
        e_txt = font.render("退出遊戲", True, WHITE)
        screen.blit(e_txt, (exit_button.centerx - e_txt.get_width()//2, exit_button.centery - e_txt.get_height()//2))

        ctrl_title = font.render("操作說明:", True, YELLOW)
        screen.blit(ctrl_title, (WIDTH//2 - ctrl_title.get_width()//2, HEIGHT//2 + 235))
        controls = ["移動: WASD", "射擊: 滑鼠左鍵  |  技能: 滑鼠右鍵", "衝刺: SPACE 鍵 / Q 鍵", "切換武器: E 鍵", "挑戰換彈: R 鍵  |  暫停: ESC 鍵"]
        for i, c in enumerate(controls): screen.blit(font.render(c, True, GRAY), (WIDTH//2 - font.size(c)[0]//2, HEIGHT//2 + 265 + i * 25))

        pygame.draw.polygon(screen, BLUE, [(30, 30), (80, 30), (55, 10)], 2)
        pygame.draw.polygon(screen, PURPLE, [(WIDTH-30, HEIGHT-30), (WIDTH-80, HEIGHT-30), (WIDTH-55, HEIGHT-10)], 2)
        screen.blit(small_font.render("v1.9", True, GRAY), (WIDTH - 40, HEIGHT - 25))

        if show_changelog: draw_changelog_popup(screen)

    elif game_state == "DIFFICULTY":
        screen.fill(BLACK)
        for i in range(100):
            x, y = (i * 37) % WIDTH, (i * 23) % HEIGHT
            brightness = 100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)

        title = large_font.render("選擇難易度", True, YELLOW)
        subtitle = font.render("挑戰模式下敵人強度大幅提升，並啟用彈藥機制", True, GRAY)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 200))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2 - 150))

        mouse_pos = pygame.mouse.get_pos()
        n_hover, c_hover = normal_button.collidepoint(mouse_pos), challenge_button.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (55, 125, 185) if n_hover else (30, 70, 115), normal_button, border_radius=10); pygame.draw.rect(screen, YELLOW if n_hover else WHITE, normal_button, 4 if n_hover else 3, border_radius=10)
        pygame.draw.rect(screen, (190, 55, 70) if c_hover else (115, 35, 50), challenge_button, border_radius=10); pygame.draw.rect(screen, YELLOW if c_hover else WHITE, challenge_button, 4 if c_hover else 3, border_radius=10)

        n_txt, n_desc = large_font.render("普通", True, WHITE), small_font.render("標準敵人強度與數量", True, WHITE)
        screen.blit(n_txt, (normal_button.centerx - n_txt.get_width()//2, normal_button.y + 28)); screen.blit(n_desc, (normal_button.centerx - n_desc.get_width()//2, normal_button.y + 88))
        for i, line in enumerate(["基礎倍率：1.0x", "無需換彈", "穩定探索地圖邊界與搭配流派"]): screen.blit(small_font.render(line, True, (210, 225, 240)), (normal_button.x + 35, normal_button.y + 132 + i * 28))

        c_txt, c_desc = large_font.render("挑戰", True, WHITE), small_font.render("敵人 1.75 倍，速度加成", True, WHITE)
        screen.blit(c_txt, (challenge_button.centerx - c_txt.get_width()//2, challenge_button.y + 28)); screen.blit(c_desc, (challenge_button.centerx - c_desc.get_width()//2, challenge_button.y + 88))
        for i, line in enumerate(["難度倍率：1.75x", "包含射擊換彈懲罰機制", "解鎖挑戰專屬強化：擴容/快拆彈匣"]): screen.blit(small_font.render(line, True, (255, 220, 220)), (challenge_button.x + 35, challenge_button.y + 132 + i * 28))

        b_hover = difficulty_back_button.collidepoint(mouse_pos)
        pygame.draw.rect(screen, BLUE if b_hover else (50, 100, 150), difficulty_back_button, border_radius=10); pygame.draw.rect(screen, WHITE, difficulty_back_button, 3, border_radius=10)
        b_txt = font.render("返回", True, WHITE)
        screen.blit(b_txt, (difficulty_back_button.centerx - b_txt.get_width()//2, difficulty_back_button.centery - b_txt.get_height()//2))

    elif game_state == "PAUSED":
        screen.blit(dim_surface, (0, 0))
        pause_txt = large_font.render("暫停中", True, YELLOW)
        screen.blit(pause_txt, (WIDTH//2 - pause_txt.get_width()//2, HEIGHT//2 - 100))
        screen.blit(font.render("按下 'ESC' 鍵繼續遊戲", True, WHITE), (WIDTH//2 - 120, HEIGHT//2 - 40))
        
        m_pos = pygame.mouse.get_pos()
        pause_resume_btn = pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 10, 220, 50)
        pause_menu_btn = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 10, 220, 50)
        pause_restart_btn = pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 80, 220, 50)
        pause_exit_btn = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 80, 220, 50)
        
        def draw_pause_btn(btn, text, color, hover_color):
            c = hover_color if btn.collidepoint(m_pos) else color
            pygame.draw.rect(screen, c, btn, border_radius=10); pygame.draw.rect(screen, WHITE, btn, 3, border_radius=10)
            txt = font.render(text, True, WHITE)
            screen.blit(txt, (btn.centerx - txt.get_width()//2, btn.centery - txt.get_height()//2))

        draw_pause_btn(pause_resume_btn, "繼續遊戲", (50, 100, 150), BLUE)
        draw_pause_btn(pause_menu_btn, "回到選單", (50, 100, 150), BLUE)
        draw_pause_btn(pause_restart_btn, "重新開始", (50, 150, 50), GREEN)
        draw_pause_btn(pause_exit_btn, "退出遊戲", (150, 50, 50), RED)
        draw_pause_upgrade_log(screen)

    elif game_state == "LEVEL_UP":
        screen.blit(dim_surface, (0, 0)) 
        title = large_font.render("升級！選擇一項強化", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        for i, card in enumerate(cards):
            if i >= len(current_upgrade_choices): continue
            upgrade = upgrade_options[current_upgrade_choices[i]]
            is_selected = (selected_upgrade_position == i)
            base_color = CARD_TYPE_COLORS.get(upgrade.get("type"), CARD_COLOR)
            hover_color = tuple(min(255, c + 35) for c in base_color)
            sel_color = tuple(min(255, c + 65) for c in base_color)
            color = sel_color if is_selected else hover_color if card.collidepoint(pygame.mouse.get_pos()) else base_color
            
            pygame.draw.rect(screen, color, card, border_radius=10)
            pygame.draw.rect(screen, YELLOW if is_selected else WHITE, card, 6 if is_selected else 3, border_radius=10) 
            
            type_label = CARD_TYPE_LABELS.get(upgrade.get("type"), "")
            if type_label:
                lbl = small_font.render(type_label, True, WHITE)
                lbl_bg = pygame.Rect(card.centerx - 42, card.y + 18, 84, 28)
                pygame.draw.rect(screen, (20, 20, 28), lbl_bg, border_radius=8); pygame.draw.rect(screen, WHITE, lbl_bg, 1, border_radius=8)
                screen.blit(lbl, (lbl_bg.centerx - lbl.get_width()//2, lbl_bg.centery - lbl.get_height()//2))
            
            opt_title = font.render(upgrade["title"], True, WHITE)
            screen.blit(opt_title, (card.centerx - opt_title.get_width()//2, card.y + 65))
            desc1 = font.render(upgrade["desc"][0], True, YELLOW); desc2 = font.render(upgrade["desc"][1], True, YELLOW)
            screen.blit(desc1, (card.centerx - desc1.get_width()//2, card.y + 125)); screen.blit(desc2, (card.centerx - desc2.get_width()//2, card.y + 165))
            
        ready = (selected_upgrade_position is not None)
        c_color = GREEN if ready and confirm_upgrade_button.collidepoint(pygame.mouse.get_pos()) else (50, 150, 50) if ready else GRAY
        pygame.draw.rect(screen, c_color, confirm_upgrade_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, confirm_upgrade_button, 3, border_radius=10)
        txt = font.render("確認選擇", True, WHITE)
        screen.blit(txt, (confirm_upgrade_button.centerx - txt.get_width()//2, confirm_upgrade_button.centery - txt.get_height()//2))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()