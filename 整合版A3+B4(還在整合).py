<<<<<<< HEAD
import pygame
import random
import math
import os
import ctypes

# 初始化遊戲跟音效
pygame.init()
pygame.mixer.init()
# 設定常數
WIDTH, HEIGHT = 1024, 768
#設定視窗
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("AI末日生存者")
#定義半透明遮罩UI 遮罩的表面
dim_surface = pygame.Surface((4200, 2600), pygame.SRCALPHA) # 等於地圖大小
dim_surface.fill((0, 0, 0, 150))  # (紅, 綠, 藍, 透明度)，150 是半透明
MAP_WIDTH, MAP_HEIGHT = 4200, 2600 # 開放世界地圖大小
fullscreen_mode = False

clock = pygame.time.Clock()
FPS = 60
WINDOW_FOCUS_GAINED = getattr(pygame, "WINDOWFOCUSGAINED", None)

def switch_to_english_input():
    if os.name != "nt": return
    try:
        # 獲取當前視窗句柄並切換輸入法為英文，避免遊戲中誤觸中文輸入法無法操控
        hwnd = pygame.display.get_wm_info().get("window")
        if hwnd:
            english_layout = ctypes.windll.user32.LoadKeyboardLayoutW("00000409", 1)
            ctypes.windll.user32.ActivateKeyboardLayout(english_layout, 0)
            ctypes.windll.user32.PostMessageW(hwnd, 0x0050, 0, english_layout)
    except Exception: pass

switch_to_english_input()

# --- 顏色定義 ---
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
CARD_TYPE_COLORS = { "attack": (120, 35, 45), "support": (35, 75, 130), "life": (35, 110, 65) }
CARD_TYPE_LABELS = { "attack": "攻擊", "support": "支援", "life": "生命" }
SHIELD_COLOR = (0, 102, 204)    
EXP_COLOR = (124, 252, 0)   
HP_COLOR = (255, 0, 0)    

NORMAL_MODE = "NORMAL"
CHALLENGE_MODE = "CHALLENGE"
CHALLENGE_ENEMY_MULTIPLIER = 1.75
CHALLENGE_ENEMY_SPEED_MULTIPLIER = 1.25
NORMAL_SPAWN_INTERVAL = 420
CHALLENGE_SPAWN_INTERVAL = 600
SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
game_mode = NORMAL_MODE

# --- 字體設定 ---
CHINESE_FONTS = "microsoftjhenghei,pingfangtc,stheiti,simhei"
font = pygame.font.SysFont(CHINESE_FONTS, 28)
large_font = pygame.font.SysFont(CHINESE_FONTS, 48)
small_font = pygame.font.SysFont(CHINESE_FONTS, 22)
tiny_font = pygame.font.SysFont(CHINESE_FONTS, 18)

# ==========================================
# 2. 智慧動畫、貼圖與音效系統
# ==========================================
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
        os.makedirs(folder_path) 
        animations[name] = None
        return
    frames =[]
    for file in sorted(os.listdir(folder_path)):
        if file.endswith((".png", ".jpg")):
            img = pygame.image.load(os.path.join(folder_path, file)).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
    animations[name] = frames if frames else None

# 載入所有圖片資源
load_image("bg", "bg.png", (WIDTH, HEIGHT))
load_image("drop_EXP", "drop_exp.png", (20, 20))
load_image("drop_HP", "drop_hp.png", (20, 20))
load_image("drop_SHIELD", "drop_shield.png", (20, 20))
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

# --- 音效系統 ---
sounds = {}
def load_sound(name, filename):
    try:
        sounds[name] = pygame.mixer.Sound(os.path.join(BASE_DIR, filename))
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

try:
    pygame.mixer.music.load(os.path.join(BASE_DIR, "bgm.mp3"))
    pygame.mixer.music.set_volume(0.2) 
except: pass

def play_sound(name, loop=0):
    if name in sounds and sounds[name] != None: sounds[name].play(loops=loop)
def stop_sound(name):
    if name in sounds and sounds[name] != None: sounds[name].stop()

# ==========================================
# 3. 遊戲機制與實體類別
# ==========================================
CHEAT_CODE =[pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_b, pygame.K_a, pygame.K_b, pygame.K_a]
key_buffer =[] 
global_offset_x = 0
global_offset_y = 0

class Weapon:
    def __init__(self, name, shoot_delay, bullet_type, damage, sound_name="shoot_normal"):
        self.name, self.shoot_delay, self.bullet_type, self.damage, self.sound_name = name, shoot_delay, bullet_type, damage, sound_name
        load_image("gun_" + name, f"gun_{name}.png", (45, 18))
        load_image("icon_" + name, f"icon_{name}.png", (60, 30))

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

class Player:
    def __init__(self):
        self.pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
        self.size, self.base_speed = 30, 5
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.weapons = list(WEAPON_TYPES.values())
        self.current_weapon_idx = 0
        self.anim_idx = 0
        
        self.bullet_count = 1      
        self.extra_same_path_bullets = 0
        self.bullet_spread = 15
        self.bullet_damage_bonus = 0
        self.guidance_level = 0
        self.aura_level = 0
        self.regen_level = 0
        self.regen_progress = 0
        self.exp_multiplier = 1.0
        self.damage_reduction = 0
        
        self.exp, self.level, self.max_exp = 0, 1, 100
        self.magnet_radius = 60
        self.max_hp, self.hp = 100, 100
        self.max_shield = int(self.max_hp * 0.2)
        self.shield = self.max_shield
        self.shield_regen_rate = 0.18
        self.shield_regen_delay = 150
        self.shield_regen_timer = 0
        self.invincible_timer, self.invincible_duration = 0, 60

        self.max_stamina, self.stamina, self.dash_cost, self.stamina_regen = 100, 100, 35, 0.5   
        self.is_dashing, self.dash_speed, self.dash_duration, self.dash_timer = False, 22, 8, 0
        self.dash_direction = pygame.math.Vector2(0, 0)
        self.max_energy, self.energy, self.energy_regen = 100, 100, 0.2     
        self.skill_cd, self.skill_max_cd, self.skill_cost = 0, 600, 50        
        self.god_mode = False 
        
        self.pistol_mag_size = 45
        self.sniper_mag_size = 7
        self.pistol_ammo = self.pistol_mag_size
        self.sniper_ammo = self.sniper_mag_size
        self.reload_timer = 0
        self.reload_duration = 90
        self.reloading_weapon = None

    def update(self):
        self.anim_idx += 0.15
        keys = pygame.key.get_pressed()
        move_vector = pygame.math.Vector2(0, 0)

        if self.reload_timer > 0:
            self.reload_timer -= 1
            if self.reload_timer <= 0:
                if self.reloading_weapon == "sniper": self.sniper_ammo = self.sniper_mag_size
                else: self.pistol_ammo = self.pistol_mag_size
                self.reloading_weapon = None
        
        if keys[pygame.K_w]: move_vector.y -= 1
        if keys[pygame.K_s]: move_vector.y += 1
        if keys[pygame.K_a]: move_vector.x -= 1
        if keys[pygame.K_d]: move_vector.x += 1
        if move_vector.length() > 0: move_vector.normalize_ip()

        if self.invincible_timer > 0: self.invincible_timer -= 1
        if self.skill_cd > 0: self.skill_cd -= 1
        
        if self.shield_regen_timer > 0: self.shield_regen_timer -= 1
        elif self.shield < self.max_shield: self.shield = min(self.max_shield, self.shield + self.shield_regen_rate)
            
        if not self.is_dashing and self.stamina < self.max_stamina: self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen)
        if self.energy < self.max_energy: self.energy = min(self.max_energy, self.energy + self.energy_regen)

        if (keys[pygame.K_q] or keys[pygame.K_SPACE]) and not self.is_dashing and self.stamina >= self.dash_cost:
            self.stamina -= self.dash_cost
            self.is_dashing, self.dash_timer = True, self.dash_duration
            play_sound("dash")
            if move_vector.length() > 0: self.dash_direction = move_vector.copy()
            else:
                mx, my = pygame.mouse.get_pos()
                self.dash_direction = pygame.math.Vector2(mx - WIDTH/2, my - HEIGHT/2)
                if self.dash_direction.length() > 0: self.dash_direction.normalize_ip()

        # 計算玩家的「絕對世界座標」位移
        world_pos = pygame.math.Vector2(WIDTH/2 + global_offset_x, HEIGHT/2 + global_offset_y)
        if self.is_dashing:
            world_pos += self.dash_direction * self.dash_speed
            self.dash_timer -= 1
            if self.dash_timer <= 0: self.is_dashing = False
        else:
            world_pos += move_vector * self.base_speed
            
        half = self.size / 2
        world_pos.x = max(half, min(MAP_WIDTH - half, world_pos.x))
        world_pos.y = max(half, min(MAP_HEIGHT - half, world_pos.y))
            
        # 計算偏移量推進攝影機
        shift_x = world_pos.x - WIDTH/2 - global_offset_x
        shift_y = world_pos.y - HEIGHT/2 - global_offset_y
        apply_camera_follow(pygame.math.Vector2(shift_x, shift_y))
        
        self.pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2) # 永遠保持在畫布中央
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def current_weapon_type(self):
        w_type = self.weapons[self.current_weapon_idx].bullet_type
        return "sniper" if w_type == "piercing" else "pistol"

    def can_fire_current_weapon(self):
        global game_mode
        if game_mode != CHALLENGE_MODE: return True
        if self.reload_timer > 0: return False
        if self.current_weapon_type() == "sniper": return self.sniper_ammo > 0
        return self.pistol_ammo > 0

    def consume_current_ammo(self):
        global game_mode
        if game_mode != CHALLENGE_MODE: return
        if self.current_weapon_type() == "sniper":
            self.sniper_ammo = max(0, self.sniper_ammo - 1)
            if self.sniper_ammo <= 0: self.start_reload("sniper")
        else:
            self.pistol_ammo = max(0, self.pistol_ammo - 1)
            if self.pistol_ammo <= 0: self.start_reload("pistol")

    def start_reload(self, weapon=None):
        global game_mode
        if game_mode != CHALLENGE_MODE or self.reload_timer > 0: return
        self.reloading_weapon = weapon or self.current_weapon_type()
        self.reload_timer = self.reload_duration
    
    def get_muzzle_pos(self, world_mouse):
        # 計算從玩家指向滑鼠的方向向量
        direction = world_mouse - pygame.math.Vector2(self.pos)
        if direction.length_squared() > 0:
            direction.normalize_ip()
        else:
            direction = pygame.math.Vector2(1, 0) # 預設朝右
        # 設定槍口距離中心點的像素距離
        # 這裡的 25 必須和 draw 方法裡的畫槍的偏移量 (offset) 一致，可以根據槍枝貼圖長度調整
        # 設為比槍枝貼圖長度稍微多一點點點，這樣才不會從槍管中間飛出來
        muzzle_dist = 25
    
        # 玩家位置 + (方向 * 距離)
        return pygame.math.Vector2(self.pos) + direction * muzzle_dist

    def draw(self, surface, current_wep=None):
        draw_player = True
        if self.invincible_timer > 0 and not self.god_mode and (self.invincible_timer // 4) % 2 == 0:
            draw_player = False
                
        if draw_player:
            # 電弧光環
            if self.aura_level > 0:
                aura_radius = 95 + self.aura_level * 25
                pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10)
                pygame.draw.circle(surface, (0, 180, 255), self.rect.center, aura_radius + pulse, 2)
                pygame.draw.circle(surface, (0, 90, 180), self.rect.center, max(12, aura_radius - 18), 1)
                
            anim_frames = animations.get("player")
            if anim_frames:
                img = anim_frames[int(self.anim_idx) % len(anim_frames)]
                if pygame.mouse.get_pos()[0] < self.pos.x: img = pygame.transform.flip(img, True, False)
                surface.blit(img, img.get_rect(center=self.rect.center))
            else:
                pygame.draw.rect(surface, YELLOW if self.god_mode else BLUE, self.rect)
                
            if self.stamina < self.dash_cost: pygame.draw.rect(surface, GRAY, self.rect, 3)
            if self.shield > 0:
                s_color = (70, 180, 255) if (self.shield / self.max_shield) > 0.35 else (255, 210, 70)
                pygame.draw.circle(surface, s_color, self.rect.center, self.size // 2 + 8, 2)

            # 動態持槍
            if current_wep:
                mx, my = pygame.mouse.get_pos()
                direction = pygame.math.Vector2(mx - self.pos.x, my - self.pos.y)
                if direction.length() > 0: direction.normalize_ip()
                else: direction = pygame.math.Vector2(1, 0)
                
                angle = math.degrees(math.atan2(-direction.y, direction.x))
                gun_img = images.get("gun_" + current_wep.name)
                
                if gun_img:
                    if direction.x < 0: gun_img = pygame.transform.flip(gun_img, False, True)
                    rotated_gun = pygame.transform.rotate(gun_img, angle)
                    gun_rect = rotated_gun.get_rect(center=(int(self.pos.x + direction.x * 15), int(self.pos.y + direction.y * 15)))
                    surface.blit(rotated_gun, gun_rect)
                else:
                    end_pos = self.pos + direction * 25
                    wep_color = PURPLE if current_wep.bullet_type == "piercing" else ORANGE if current_wep.bullet_type == "flamethrower" else CYAN if current_wep.bullet_type == "laser" else WHITE if current_wep.bullet_type == "cannon" else (100, 200, 255) if current_wep.bullet_type == "frost" else RED if current_wep.bullet_type == "flame_grenade" else GREEN if current_wep.bullet_type == "plasma" else YELLOW
                    pygame.draw.line(surface, GRAY, self.rect.center, end_pos, 6)
                    pygame.draw.circle(surface, wep_color, (int(end_pos.x), int(end_pos.y)), 4)

def apply_camera_follow(offset_vector):
    if offset_vector.length_squared() == 0: return
    global global_offset_x, global_offset_y
    global_offset_x += offset_vector.x
    global_offset_y += offset_vector.y
    
    for group in [bullets, enemy_bullets, enemies, particles, items, trails, damage_texts]:
        for obj in group:
            obj.pos -= offset_vector
            if hasattr(obj, "rect"): obj.rect.center = (round(obj.pos.x), round(obj.pos.y))
            if hasattr(obj, "target"): obj.target -= offset_vector
            
    if boss_active and boss:
        boss.pos -= offset_vector
        boss.rect.center = (round(boss.pos.x), round(boss.pos.y))
        if hasattr(boss, "aim_target"): boss.aim_target -= offset_vector
        if hasattr(boss, "entrance_start"): boss.entrance_start -= offset_vector; boss.entrance_end -= offset_vector

def draw_map_bounds(surface):
    map_rect = pygame.Rect(-global_offset_x, -global_offset_y, MAP_WIDTH, MAP_HEIGHT)
    pygame.draw.rect(surface, (25, 30, 45), map_rect, 4)
    for x in range(0, MAP_WIDTH + 1, 400):
        sx = x - global_offset_x
        if -10 <= sx <= WIDTH + 10: pygame.draw.line(surface, (18, 22, 32), (sx, max(0, -global_offset_y)), (sx, min(HEIGHT, MAP_HEIGHT - global_offset_y)), 1)
    for y in range(0, MAP_HEIGHT + 1, 400):
        sy = y - global_offset_y
        if -10 <= sy <= HEIGHT + 10: pygame.draw.line(surface, (18, 22, 32), (max(0, -global_offset_x), sy), (min(WIDTH, MAP_WIDTH - global_offset_x), sy), 1)

def draw_boss_direction_arrow(surface, boss_obj):
    if not boss_obj or boss_obj.state == "DEFEAT": return
    visible_rect = pygame.Rect(-40, -40, WIDTH + 80, HEIGHT + 80)
    if visible_rect.collidepoint(boss_obj.pos.x, boss_obj.pos.y): return

    center = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
    direction = boss_obj.pos - center
    if direction.length_squared() == 0: return
    direction.normalize_ip()
    margin = 56
    scale_x = (WIDTH / 2 - margin) / abs(direction.x) if abs(direction.x) > 0.001 else float("inf")
    scale_y = (HEIGHT / 2 - margin) / abs(direction.y) if abs(direction.y) > 0.001 else float("inf")
    arrow_pos = center + direction * min(scale_x, scale_y)
    side = direction.rotate(90)
    tip = arrow_pos + direction * 30
    left = arrow_pos - direction * 22 + side * 18
    right = arrow_pos - direction * 22 - side * 18
    arrow_points = [(int(tip.x), int(tip.y)), (int(left.x), int(left.y)), (int(right.x), int(right.y))]
    pygame.draw.polygon(surface, BLACK, arrow_points)
    pygame.draw.polygon(surface, YELLOW, arrow_points, 0)
    pygame.draw.polygon(surface, RED, arrow_points, 3)
    distance = max(0, int(player.pos.distance_to(boss_obj.pos)))
    distance_txt = small_font.render(f"Boss 距離 {distance:03d}", True, YELLOW)
    surface.blit(distance_txt, (int(arrow_pos.x - distance_txt.get_width()/2), int(arrow_pos.y - 48)))

class DashTrail:
    def __init__(self, pos, size): self.pos, self.size, self.life = pos.copy(), size, 12
    def update(self): self.life -= 1; self.size -= 1.5
    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            rect = pygame.Rect(0, 0, self.size, self.size)
            rect.center = (round(self.pos.x), round(self.pos.y))
            pygame.draw.rect(surface, BLUE, rect, max(1, int(self.life / 3)))

class Bullet:
    def __init__(self, start_pos, target_pos, weapon, guidance_level=0):
        self.pos = start_pos.copy()
        self.target = target_pos.copy()
        self.b_type, self.damage = weapon.bullet_type, weapon.damage + player.bullet_damage_bonus
        self.is_piercing = self.b_type in["piercing", "laser", "cannon", "flamethrower"]
        self.guidance_level = guidance_level
            
        self.direction = self.target - self.pos
        if self.direction.length() > 0: self.direction.normalize_ip()
        
        self.lifespan, self.speed, self.radius, self.color = 120, 18, 6, YELLOW
        if self.b_type == "piercing": self.color = PURPLE; self.speed = 28; self.radius = 7
        elif self.b_type == "flamethrower": self.color = ORANGE; self.speed = 12; self.radius = 12; self.lifespan = 25
        elif self.b_type == "laser": self.color = CYAN; self.speed = 45; self.radius = 4
        elif self.b_type == "cannon": self.color = WHITE; self.speed = 12; self.radius = 20
        elif self.b_type == "frost": self.color = (100, 200, 255); self.speed = 16; self.radius = 8
        elif self.b_type == "flame_grenade": self.color = RED; self.speed = 10; self.radius = 10
        elif self.b_type == "plasma": self.color = GREEN; self.speed = 15; self.radius = 10

        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        self.explode = False 

    def update(self):
        self.lifespan -= 1
        
        if self.guidance_level > 0 and self.lifespan % 2 == 0:
            targets = enemies[:]
            if boss_active and boss and boss.state != "DEFEAT": targets.append(boss)
            if targets:
                guide_range = 220 + self.guidance_level * 45
                nearby = [t for t in targets if self.pos.distance_to(t.pos) <= guide_range]
                if nearby:
                    target = min(nearby, key=lambda t: self.pos.distance_to(t.pos))
                    t_dir = target.pos - self.pos
                    if t_dir.length() > 0:
                        t_dir.normalize_ip()
                        turn_speed = min(0.08, 0.025 + self.guidance_level * 0.012)
                        self.direction += t_dir * turn_speed
                        self.direction.normalize_ip()
                        
        if self.b_type == "flame_grenade" and self.pos.distance_to(self.target) < self.speed:
            self.explode, self.lifespan = True, 0; return 
        if self.b_type == "plasma":
            # 轉換為真實的世界座標再檢查邊界
            screen_x, screen_y = self.pos.x + global_offset_x, self.pos.y + global_offset_y
            if screen_x <= 0 or screen_x >= MAP_WIDTH: self.direction.x *= -1
            if screen_y <= 0 or screen_y >= MAP_HEIGHT: self.direction.y *= -1
            
        self.pos += self.direction * self.speed
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def draw(self, surface):
        img = images.get("bullet_" + self.b_type)
        if img:
            angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))
            rotated_img = pygame.transform.rotate(img, angle)
            surface.blit(rotated_img, rotated_img.get_rect(center=self.rect.center))
        else:
            if self.b_type == "laser":
                end_pos = self.pos - (self.direction * 30)
                pygame.draw.line(surface, self.color, self.pos, end_pos, self.radius*2)
            else: pygame.draw.circle(surface, self.color, self.rect.center, self.radius)

class EnemyBullet:
    def __init__(self, pos, direction, color=ORANGE, core_color=WHITE, style="round"):
        self.pos = pos.copy()
        self.direction = direction.copy()
        if self.direction.length() > 0: self.direction.normalize_ip()
        self.radius, self.speed, self.color = 8, 7, color
        self.core_color, self.style = core_color, style
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        
    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
    def draw(self, surface): 
        img = images.get("enemy_bullet")
        if img and self.style == "round": surface.blit(img, img.get_rect(center=self.rect.center))
        else:
            pygame.draw.circle(surface, BLACK, self.rect.center, self.radius + 4)
            pygame.draw.circle(surface, self.color, self.rect.center, self.radius + 2)
            if self.style == "diamond":
                pts = [ (self.pos.x, self.pos.y - self.radius - 1), (self.pos.x + self.radius + 1, self.pos.y), (self.pos.x, self.pos.y + self.radius + 1), (self.pos.x - self.radius - 1, self.pos.y) ]
                pygame.draw.polygon(surface, self.core_color, pts)
            elif self.style == "slash":
                side = self.direction.rotate(90)
                front = self.pos + self.direction * (self.radius + 4)
                back = self.pos - self.direction * (self.radius + 4)
                left = self.pos + side * 4
                right = self.pos - side * 4
                pygame.draw.polygon(surface, self.core_color, [(int(p.x), int(p.y)) for p in [front, left, back, right]])
            else: pygame.draw.circle(surface, self.core_color, self.rect.center, max(3, self.radius // 2))

class Enemy:
    def __init__(self, level, is_elite=False):
        self.is_elite = is_elite
        self.size = 42 if is_elite else 25
        global game_mode
        diff_mult = CHALLENGE_ENEMY_MULTIPLIER if game_mode == CHALLENGE_MODE else 1
        speed_mult = CHALLENGE_ENEMY_SPEED_MULTIPLIER if game_mode == CHALLENGE_MODE else 1
        speed_bonus = min(level * 0.03, 1.2)
        self.speed = ((random.uniform(1.1, 2.2) if is_elite else random.uniform(1.5, 3.5)) + speed_bonus) * speed_mult
        
        base_hp = 5 if is_elite else 1
        self.max_hp = max(1, int((base_hp + level // 6) * diff_mult))
        self.hp, self.damage = self.max_hp, int((35 if is_elite else 20) * diff_mult)
        self.shield = int((level // 4 + (2 if is_elite else 0)) * diff_mult)
        self.max_shield = self.shield
        
        self.exp_drop_chance = 0.85 if is_elite else 0.4
        self.health_drop_chance = 0.12 if is_elite else 0.035
        self.combat_type = "ranged" if random.random() < (0.38 if is_elite else 0.32) else "melee"
        self.attack_range = 420 if is_elite else 320
        self.keep_distance = 260 if is_elite else 205
        self.shoot_cooldown = random.randint(35, 90)
        self.shoot_delay = 85 if is_elite else 115
        
        self.frost_timer, self.anim_idx = 0, 0
        self.facing = pygame.math.Vector2(1, 0)
        
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        world_px, world_py = player.pos.x + global_offset_x, player.pos.y + global_offset_y 
        if edge == 'top': world_x, world_y = world_px + random.randint(-WIDTH, WIDTH), world_py - HEIGHT//2 - self.size
        elif edge == 'bottom': world_x, world_y = world_px + random.randint(-WIDTH, WIDTH), world_py + HEIGHT//2 + self.size
        elif edge == 'left': world_x, world_y = world_px - WIDTH//2 - self.size, world_py + random.randint(-HEIGHT, HEIGHT)
        else: world_x, world_y = world_px + WIDTH//2 + self.size, world_py + random.randint(-HEIGHT, HEIGHT)
        
        world_x = max(self.size, min(MAP_WIDTH - self.size, world_x))
        world_y = max(self.size, min(MAP_HEIGHT - self.size, world_y))
        self.pos = pygame.math.Vector2(world_x - global_offset_x, world_y - global_offset_y)
        self.rect = pygame.Rect(0, 0, self.size, self.size)

    def update(self, target_pos, all_enemies):
        self.anim_idx += 0.15
        current_speed = self.speed * 0.4 if self.frost_timer > 0 else self.speed
        if self.frost_timer > 0: self.frost_timer -= 1

        direction = target_pos - self.pos
        distance = direction.length()
        if distance > 0:
            direction.normalize_ip()
            self.facing = direction.copy()
            
        move_dir = direction
        if self.combat_type == "ranged":
            if distance < self.keep_distance: move_dir = -direction
            elif distance <= self.attack_range: move_dir = pygame.math.Vector2(0, 0)
            if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
            
        self.pos += move_dir * current_speed

        # Boids 群體互斥
        for other in all_enemies:
            if other is not self:
                dist_sq = self.pos.distance_squared_to(other.pos)
                if 0 < dist_sq < self.size**2:
                    dist_val = math.sqrt(dist_sq)
                    push_dir = (self.pos - other.pos) / dist_val
                    self.pos += push_dir * 1.2
            
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def emit_attacks(self, enemy_bullets, target_pos):
        if self.combat_type != "ranged" or self.shoot_cooldown > 0: return
        direction = target_pos - self.pos
        if direction.length_squared() == 0 or direction.length() > self.attack_range + 80: return
        direction.normalize_ip()
        self.facing = direction.copy()
        bullet_color = (255, 120, 45) if self.is_elite else ORANGE
        enemy_bullets.append(EnemyBullet(self.pos, direction, color=bullet_color, core_color=WHITE, style="round"))
        self.shoot_cooldown = self.shoot_delay

    def draw(self, surface):
        anim_key = "enemy_elite" if self.is_elite else "enemy_normal"
        anim_frames = animations.get(anim_key)
        
        if anim_frames:
            img = anim_frames[int(self.anim_idx) % len(anim_frames)]
            if self.facing.x < 0: img = pygame.transform.flip(img, True, False)
            if self.frost_timer > 0:
                img = img.copy(); img.fill((100, 200, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(img, img.get_rect(center=self.rect.center))
            if self.is_elite:
                glow = math.sin(pygame.time.get_ticks() * 0.01) * 6 + 6
                pygame.draw.rect(surface, DARK_PURPLE, self.rect.copy().inflate(glow, glow), 3) 
        else:
            side = self.facing.rotate(90)
            weapon_reach = 34 if self.is_elite else 24
            weapon_offset = self.size * 0.28
            hand = self.pos + self.facing * weapon_offset + side * (self.size * 0.2)
            
            if self.combat_type == "melee":
                hilt = hand + self.facing * (8 if self.is_elite else 5)
                blade_tip = hand + self.facing * (weapon_reach + 16)
                blade_mid = hilt + self.facing * ((weapon_reach + 12) * 0.55)
                b_half = 7 if self.is_elite else 5
                b_color = (80, 240, 255) if self.is_elite else (100, 255, 145)
                pygame.draw.polygon(surface, BLACK, [(p.x, p.y) for p in [blade_tip, blade_mid + side * b_half, hilt + side * max(3, b_half-2), hilt - side * max(3, b_half-2), blade_mid - side * b_half]])
                pygame.draw.polygon(surface, b_color, [(p.x, p.y) for p in [blade_tip - self.facing*2, blade_mid + side * max(3, b_half-2), hilt + side*2, hilt - side*2, blade_mid - side * max(3, b_half-2)]])
            else:
                muzzle = self.pos + self.facing * weapon_reach + side * (self.size * 0.2)
                rear = self.pos + self.facing * (self.size * 0.02) + side * (self.size * 0.2)
                b_half = 5 if self.is_elite else 4
                pygame.draw.polygon(surface, BLACK, [(p.x, p.y) for p in [rear + side * b_half, muzzle + side * max(2, b_half-2), muzzle - side * max(2, b_half-2), rear - side * b_half]])
                pygame.draw.polygon(surface, (205, 210, 215), [(p.x, p.y) for p in [rear + side*(b_half-1), muzzle + side * max(1, b_half-3), muzzle - side * max(1, b_half-3), rear - side*(b_half-1)]])
                barrel_tip = muzzle + self.facing * (7 if self.is_elite else 5)
                pygame.draw.line(surface, BLACK, muzzle, barrel_tip, 5 if self.is_elite else 4)
                pygame.draw.circle(surface, ORANGE if self.is_elite else YELLOW, (int(barrel_tip.x), int(barrel_tip.y)), 3)

            color = (170, 40, 255) if self.is_elite else RED
            if self.frost_timer > 0: color = (100, 200, 255)
            pygame.draw.rect(surface, color, self.rect)
            if self.is_elite:
                pygame.draw.circle(surface, (230, 170, 255), self.rect.center, self.size//2 + 8, 2)
                pygame.draw.rect(surface, WHITE, self.rect, 3)
                
        if self.shield > 0: pygame.draw.rect(surface, BLUE, self.rect.inflate(8, 8), 2)
        if self.hp < self.max_hp or self.shield > 0:
            pygame.draw.rect(surface, GRAY, (self.rect.x, self.rect.y - 8, self.size, 4))
            pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 8, self.size * (self.hp/self.max_hp), 4))
            if self.max_shield > 0:
                pygame.draw.rect(surface, GRAY, (self.rect.x, self.rect.y - 14, self.size, 4))
                pygame.draw.rect(surface, BLUE, (self.rect.x, self.rect.y - 14, self.size * (self.shield/self.max_shield), 4))

class Boss:
    def __init__(self, boss_type, level=5):
        self.b_type = boss_type
        world_x, world_y = player.pos.x + global_offset_x, player.pos.y + global_offset_y - HEIGHT//2 - 100
        
        self.entrance_start = pygame.math.Vector2(world_x - global_offset_x, world_y - global_offset_y)
        self.entrance_end = pygame.math.Vector2(world_x - global_offset_x, world_y - global_offset_y + 200)
        self.pos = self.entrance_start.copy()
        
        self.size = 65
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.spawn_level = level
        global game_mode
        diff_mult = CHALLENGE_ENEMY_MULTIPLIER if game_mode == CHALLENGE_MODE else 1
        
        self.state = "ENTRANCE"
        self.state_timer, self.frost_timer, self.defeat_timer, self.anim_idx = 0, 0, 0, 0
        self.entrance_duration = 120  
        self.play_shoot_sound = False 
        self.collision_damage = int(40 * diff_mult)
        
        if self.b_type == "YELLOW":
            self.max_hp = int((1000 + level*300) * diff_mult)
            self.color, self.speed, self.name = YELLOW, 3.0 * diff_mult, "幾何守衛"
        elif self.b_type == "RED":
            self.max_hp = int((1500 + level*300) * diff_mult)
            self.color, self.speed, self.name = RED, 2.5 * diff_mult, "鮮血狂戰士"
            self.aim_target, self.dash_dir, self.spin_angle = pygame.math.Vector2(0,0), pygame.math.Vector2(1,0), 0
        elif self.b_type == "PURPLE":
            self.max_hp = int((800 + level*300) * diff_mult)
            self.color, self.speed, self.name = PURPLE, 2.0 * diff_mult, "虛空召喚師"
            
        self.hp = self.max_hp

    def update(self, player_pos, bullets):
        self.state_timer += 1; self.anim_idx += 0.1
        current_speed = self.speed * 0.5 if self.frost_timer > 0 else self.speed
        if self.frost_timer > 0: self.frost_timer -= 1
        self.play_shoot_sound = False

        if self.state == "ENTRANCE":
            progress = min(1, self.state_timer / self.entrance_duration)
            eased = 1 - (1 - progress) ** 3
            self.pos = self.entrance_start.lerp(self.entrance_end, eased)
            glow = int(100 + 155 * progress)
            if self.b_type == "YELLOW": self.color = (glow, glow, 0)
            elif self.b_type == "RED": self.color = (glow, 0, 0)
            elif self.b_type == "PURPLE": self.color = (int(100+100*progress), 0, int(100+155*progress))
            if self.state_timer >= self.entrance_duration:
                self.state = "EVADE" if self.b_type == "YELLOW" else ("CHASE" if self.b_type == "RED" else "FLEE")
                self.state_timer = 0
                
        elif self.state == "DEFEAT":
            self.defeat_timer += 1
            self.pos.y -= 1
            self.pos.x += math.sin(self.defeat_timer * 0.2) * 1.5

        elif self.b_type == "YELLOW":
            if self.state == "EVADE":
                direction = player_pos - self.pos
                if direction.length() > 0: direction.normalize_ip()
                else: direction = pygame.math.Vector2(1,0)
                tangent = pygame.math.Vector2(-direction.y, direction.x) 
                
                dodged = False
                for b in bullets:
                    if self.pos.distance_to(b.pos) < 150:
                        flee_dir = self.pos - b.pos
                        if flee_dir.length() > 0: flee_dir.normalize_ip()
                        self.pos += flee_dir * (current_speed * 1.8)
                        dodged = True; break 
                        
                if not dodged:
                    self.pos += tangent * current_speed
                    p_dist = self.pos.distance_to(player_pos)
                    if p_dist > 250: self.pos += direction * current_speed
                    elif p_dist < 150: self.pos -= direction * current_speed

                if self.state_timer > 120: self.state = "CHARGE"; self.state_timer = 0
                    
            elif self.state == "CHARGE":
                if self.state_timer > 60: self.state = "SHOOT"; self.state_timer = 0

        elif self.b_type == "RED":
            if self.state == "CHASE":
                direction = player_pos - self.pos
                if direction.length() > 0:
                    direction.normalize_ip()
                    self.pos += direction * current_speed
                if self.state_timer > 150: self.state = "WARN"; self.state_timer = 0
            elif self.state == "WARN":
                self.aim_target = player_pos.copy()
                if self.state_timer > 45:
                    self.state, self.state_timer = "DASH", 0
                    self.dash_dir = self.aim_target - self.pos
                    if self.dash_dir.length() > 0: self.dash_dir.normalize_ip()
                    else: self.dash_dir = pygame.math.Vector2(1,0)
                    self.play_shoot_sound = True 
            elif self.state == "DASH":
                self.pos += self.dash_dir * (current_speed * 6)
                if self.state_timer % 6 == 0:
                    side1 = self.dash_dir.rotate(90)
                    side2 = self.dash_dir.rotate(-90)
                    global enemy_bullets
                    enemy_bullets.append(EnemyBullet(self.pos, side1, color=(0, 210, 255), core_color=WHITE, style="slash"))
                    enemy_bullets.append(EnemyBullet(self.pos, side2, color=(0, 210, 255), core_color=WHITE, style="slash"))
                if self.state_timer > 25 or self.pos.distance_to(self.aim_target) < 30:
                    self.state = "RECOVER"; self.state_timer = 0
            elif self.state == "RECOVER":
                self.spin_angle += 0.15
                if self.state_timer > 120: self.state = "CHASE"; self.state_timer = 0

        elif self.b_type == "PURPLE":
            if self.state == "FLEE":
                dist = self.pos.distance_to(player_pos)
                direction = player_pos - self.pos
                if direction.length() > 0: direction.normalize_ip()
                else: direction = pygame.math.Vector2(1,0)
                    
                if dist < 300: self.pos -= direction * current_speed 
                else:
                    tangent = pygame.math.Vector2(-direction.y, direction.x)
                    self.pos += tangent * current_speed 
                
                if self.state_timer > 180: self.state = "SUMMON"; self.state_timer = 0
            elif self.state == "SUMMON":
                if self.state_timer == 45:
                    for _ in range(3):
                        e = Enemy(level=self.spawn_level, is_elite=True)
                        e.pos = self.pos + pygame.math.Vector2(random.randint(-70,70), random.randint(-70,70))
                        global enemies; enemies.append(e)
                    self.play_shoot_sound = True
                if self.state_timer > 90: self.state = "FLEE"; self.state_timer = 0

        world_x, world_y = self.pos.x + global_offset_x, self.pos.y + global_offset_y
        world_x = max(self.size, min(MAP_WIDTH - self.size, world_x))
        world_y = max(self.size, min(MAP_HEIGHT - self.size, world_y))
        self.pos.x, self.pos.y = world_x - global_offset_x, world_y - global_offset_y
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def can_take_damage(self):
        if self.state in ["ENTRANCE", "DEFEAT"]: return False
        if self.b_type == "YELLOW" and self.state == "EVADE": return False
        if self.b_type == "RED" and self.state == "DASH": return False
        return True

    def emit_attacks(self, enemy_bullets):
        if self.b_type == "YELLOW" and self.state == "SHOOT":
            for i in range(12):
                angle = math.radians(i * 30)
                enemy_bullets.append(EnemyBullet(self.pos, pygame.math.Vector2(math.cos(angle), math.sin(angle))))
            if self.spawn_level >= 10:
                for i in range(12):
                    angle = math.radians(i * 30 + 15)
                    enemy_bullets.append(EnemyBullet(self.pos, pygame.math.Vector2(math.cos(angle), math.sin(angle))))
            self.state = "EVADE"
            play_sound("shoot")
        elif self.b_type == "RED" and self.state == "RECOVER":
            if self.state_timer % 10 == 0:
                for i in range(6):
                    angle = self.spin_angle + i * (math.pi*2/6)
                    enemy_bullets.append(EnemyBullet(self.pos, pygame.math.Vector2(math.cos(angle), math.sin(angle)), color=PURPLE, style="round"))

    def get_intro_title(self): return f"✦ {self.name} 降臨 ✦"

    def get_intro_lines(self):
        return [ "⚠️ BOSS 出現！時間暫停中", "準備迎接史詩級的挑戰！", "觀察型態轉換，把握攻擊時機！" ]

    def get_state_message(self):
        if self.b_type == "YELLOW":
            if self.state == "EVADE": return "閃避階段 - 無敵護盾 (黃色)", YELLOW
            elif self.state == "CHARGE": return "蓄力階段 - 可攻擊 (橙紅色)", ORANGE
            return "發射階段 - 可攻擊", RED
        elif self.b_type == "RED":
            if self.state == "WARN": return "鎖定階段 - 即將衝刺 (金色)", YELLOW
            elif self.state == "DASH": return "突擊階段 - 高速衝刺", RED
            elif self.state == "RECOVER": return "冷卻階段 - 原地旋轉彈幕", PURPLE
            return "追擊階段", WHITE
        elif self.b_type == "PURPLE":
            if self.state == "SUMMON": return "召喚階段 - 召喚菁英怪", PURPLE
            return "逃跑階段", WHITE
        return "BOSS 交戰中", WHITE

    def draw(self, surface):
        if self.state == "ENTRANCE":
            pulse = abs(math.sin(self.state_timer * 0.1))
            current_size = int(self.size * (0.8 + pulse * 0.4))
            for i in range(3):
                ring_size = current_size // 2 + 20 + i * 15
                alpha_val = int(200 * (1 - i/3) * (1 - pulse))
                if alpha_val > 0: pygame.draw.circle(surface, WHITE, self.rect.center, ring_size, 2)
            pygame.draw.rect(surface, self.color, pygame.Rect(0, 0, current_size, current_size).move(self.rect.centerx - current_size//2, self.rect.centery - current_size//2))
            pygame.draw.circle(surface, WHITE, self.rect.center, current_size//2 + 15, 3)
            for i in range(8):
                angle = (self.state_timer * 0.05 + i * math.pi / 4)
                px = self.rect.centerx + math.cos(angle) * (self.size + 30)
                py = self.rect.centery + math.sin(angle) * (self.size + 30)
                pygame.draw.circle(surface, YELLOW, (int(px), int(py)), 3)
            return
            
        elif self.state == "DEFEAT":
            progress = min(1, self.defeat_timer / 60)
            for i in range(5): pygame.draw.circle(surface, (255, 180, 0), self.rect.center, int(self.size + progress * 120 + i * 12), 3)
            core_size = max(1, int(self.size * (1 - progress * 0.7)))
            pygame.draw.rect(surface, (255, 100, 0), pygame.Rect(0, 0, core_size, core_size).move(self.rect.centerx - core_size//2, self.rect.centery - core_size//2))
            burst = int(progress * 10)
            for i in range(burst):
                angle = i * (math.pi * 2 / max(1, burst)) + self.defeat_timer * 0.3
                px = self.rect.centerx + math.cos(angle) * (self.size + 30 + progress * 80)
                py = self.rect.centery + math.sin(angle) * (self.size + 30 + progress * 80)
                pygame.draw.circle(surface, RED, (int(px), int(py)), 4)
            return

        anim_key = "boss_" + self.b_type
        anim_frames = animations.get(anim_key)
        
        if anim_frames:
            img = anim_frames[int(self.anim_idx) % len(anim_frames)]
            surface.blit(img, img.get_rect(center=self.rect.center))
        else:
            pygame.draw.rect(surface, (100, 200, 255) if self.frost_timer > 0 else self.color, self.rect)
        
        if self.b_type == "YELLOW" and self.state == "EVADE": pygame.draw.circle(surface, WHITE, self.rect.center, int(self.size/2) + 15, 3)
        elif self.b_type == "YELLOW" and self.state == "CHARGE": pygame.draw.circle(surface, RED, self.rect.center, int(self.size/2) + max(0, 30 - int(self.state_timer / 2)), 2)
        elif self.b_type == "RED" and self.state == "WARN": pygame.draw.line(surface, RED, self.rect.center, (int(self.aim_target.x), int(self.aim_target.y)), max(1, int(self.state_timer / 8)))
        elif self.b_type == "PURPLE" and self.state == "SUMMON": pygame.draw.circle(surface, DARK_PURPLE, self.rect.center, int(self.size/2) + min(60, self.state_timer), 3)

class Particle:
    def __init__(self, x, y, color):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(random.uniform(-6, 6), random.uniform(-6, 6))
        self.timer, self.size, self.color = random.randint(15, 30), random.randint(4, 8), color
    def update(self):
        self.pos += self.vel; self.timer -= 1; self.size = max(0, self.size - 0.25)
    def draw(self, surface):
        if self.size > 0: pygame.draw.rect(surface, self.color, (int(self.pos.x), int(self.pos.y), int(self.size), int(self.size)))

class DamageText:
    def __init__(self, x, y, damage, color=WHITE):
        self.pos = pygame.math.Vector2(x, y)
        self.damage, self.color = int(damage), color
        self.timer, self.vel_y, self.offset_x = 40, -1.5, random.randint(-15, 15)
        self.alpha = 255
    def update(self):
        self.pos.y += self.vel_y; self.timer -= 1
        self.alpha = max(0, int((self.timer / 40) * 255))
    def draw(self, surface):
        if self.timer > 0:
            txt_surf = font.render(f"-{self.damage}", True, self.color)
            alpha_surf = pygame.Surface(txt_surf.get_size(), pygame.SRCALPHA)
            alpha_surf.fill((255, 255, 255, self.alpha))
            txt_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(txt_surf, (int(self.pos.x + self.offset_x), int(self.pos.y)))

class DropItem:
    def __init__(self, x, y, item_type="EXP", amount=None):
        self.pos = pygame.math.Vector2(x, y)
        self.item_type = item_type
        self.rect = pygame.Rect(0, 0, 14, 14)
        self.anim_offset = random.random() * 10
        self.amount = amount if amount else (35 if item_type == "EXP" else 25)
        
    def update(self, p_pos, mag_rad):
        dist = self.pos.distance_to(p_pos)
        if dist < mag_rad and dist > 0:
            self.pos += ((p_pos - self.pos) / dist) * 8
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
    def draw(self, surface):
        img_key = f"drop_{self.item_type}"
        img = images.get(img_key)
        float_y = self.pos.y + math.sin(pygame.time.get_ticks()*0.005 + self.anim_offset) * 3
        
        if img: surface.blit(img, img.get_rect(center=(int(self.pos.x), int(float_y))))
        else:
            if self.item_type == "EXP": pygame.draw.polygon(surface, EXP_COLOR,[(self.pos.x, float_y-6), (self.pos.x+6, float_y), (self.pos.x, float_y+6), (self.pos.x-6, float_y)])
            elif self.item_type == "HP": pygame.draw.rect(surface, HP_COLOR, (self.pos.x-6, float_y-2, 12, 4)); pygame.draw.rect(surface, HP_COLOR, (self.pos.x-2, float_y-6, 4, 12))
            elif self.item_type == "SHIELD": pygame.draw.circle(surface, SHIELD_COLOR, (int(self.pos.x), int(float_y)), 6)

# ==========================================
# 4. 遊戲狀態與系統選單 (結合 A3 18種卡牌與權重)
# ==========================================
def refresh_player_shield_max(fill_gain=False):
    old_max = max(1, player.max_shield)
    old_ratio = player.shield / old_max
    player.max_shield = max(1, int(player.max_hp * 0.2))
    if fill_gain: player.shield = min(player.max_shield, player.shield + max(0, player.max_shield - old_max))
    else: player.shield = min(player.max_shield, player.max_shield * old_ratio)

def apply_upgrade(choice):
    global game_state, selected_upgrade_position
    if choice == 0: player.max_hp += 50; player.hp += 50; refresh_player_shield_max(fill_gain=True)
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
    elif choice == 15: player.max_hp += 25; player.max_stamina += 15; player.hp += 25; player.stamina += 15; refresh_player_shield_max(fill_gain=True)
    elif choice == 16: player.magnet_radius += 25; player.stamina_regen += 0.15
    elif choice == 17: player.extra_same_path_bullets += 1
    elif choice == 18: player.guidance_level += 1
    elif choice == 19: player.aura_level += 1
    elif choice == 20: player.regen_level += 1
    elif choice == 21: player.exp_multiplier += 0.2
    elif choice == 22: player.pistol_mag_size += 10; player.sniper_mag_size += 2; player.pistol_ammo += 10; player.sniper_ammo += 2
    elif choice == 23: player.reload_duration = max(35, player.reload_duration - 18)
    add_chosen_upgrade(choice)
    current_upgrade_choices.clear(); selected_upgrade_position = None
    switch_to_english_input()
    game_state = "PLAYING"             

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
    {"title": "擴容彈匣", "desc": ["挑戰限定卡牌", "步槍+10 狙擊+2"], "type": "attack", "weight": 4, "challenge_only": True},
    {"title": "快拆彈匣", "desc": ["挑戰限定卡牌", "換彈時間縮短"], "type": "support", "weight": 3, "challenge_only": True}
]

cards =[pygame.Rect(0, 0, 220, 280), pygame.Rect(0, 0, 220, 280), pygame.Rect(0, 0, 220, 280)]
confirm_upgrade_button = pygame.Rect(0, 0, 220, 60)
current_upgrade_choices =[]
selected_upgrade_position = None
chosen_upgrades =[]
pause_upgrade_scroll = 0

start_button = pygame.Rect(0, 0, 200, 60)
normal_button = pygame.Rect(0, 0, 380, 230)
challenge_button = pygame.Rect(0, 0, 380, 230)
difficulty_back_button = pygame.Rect(0, 0, 220, 55)
changelog_button = pygame.Rect(0, 0, 200, 60)
changelog_close_button = pygame.Rect(0, 0, 200, 55)
restart_button = pygame.Rect(0, 0, 200, 60)
menu_button = pygame.Rect(0, 0, 200, 60)
exit_button = pygame.Rect(0, 0, 200, 60)

CHANGELOG =[
    "v1.5 終極完全體",
    "- 將 24 種強化與開放世界整合",
    "- 融合 12 種不同特性的武器與右技能系統",
    "- 所有特效、UI 與傷害跳字系統全面結合且不會閃退",
    "v1.4",
    "- 統一所有底層座標為 Vector2",
    "v1.367",
    "- 小兵與精英小兵分為近戰和遠程兩類",
    "v1.315",
    "- 挑戰模式敵人強度提升為 1.75 倍，並啟用彈匣與換彈系統",
    "v1.185",
    "- Boss 出場動畫期間會暫停遊戲並顯示提示語",
    "- 新增裂空突擊者 Boss：衝向玩家並向兩側發射子彈",
]

show_changelog, changelog_scroll, changelog_content_surface, changelog_max_scroll = False, 0, None, 0

def choose_upgrade_cards():
    global current_upgrade_choices, selected_upgrade_position
    card_count = min(3, len(upgrade_options))
    available = [i for i, option in enumerate(upgrade_options) if game_mode == CHALLENGE_MODE or not option.get("challenge_only")]
    card_count = min(card_count, len(available))
    current_upgrade_choices =[]
    for _ in range(card_count):
        total_weight = sum(upgrade_options[i].get("weight", 1) for i in available)
        pick = random.uniform(0, total_weight)
        running_weight = 0
        for i in available:
            running_weight += upgrade_options[i].get("weight", 1)
            if pick <= running_weight:
                current_upgrade_choices.append(i); available.remove(i); break
    selected_upgrade_position = None

def add_chosen_upgrade(choice):
    title = upgrade_options[choice]["title"]
    for upgrade in chosen_upgrades:
        if upgrade["title"] == title:
            upgrade["count"] += 1; return
    chosen_upgrades.append({"title": title, "count": 1})

def wrap_text(text, text_font, max_width):
    lines =[]; current = ""
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
    content_lines =[]
    for line in CHANGELOG:
        color = YELLOW if line.startswith("v") else WHITE
        for wrapped_line in wrap_text(line, font, content_width - 20): content_lines.append((wrapped_line, color))
        content_lines.append(("", WHITE))
    surface_height = max(content_height, len(content_lines) * 34 + 10)
    changelog_content_surface = pygame.Surface((content_width, surface_height), pygame.SRCALPHA)
    for i, (line, color) in enumerate(content_lines):
        if line: changelog_content_surface.blit(font.render(line, True, color), (0, 6 + i * 34))
    changelog_max_scroll = max(0, surface_height - content_height)

def draw_changelog_popup(surface):
    popup = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 250, 700, 500)
    panel = pygame.Surface((popup.width, popup.height), pygame.SRCALPHA)
    panel.fill((18, 20, 32, 235)); surface.blit(panel, popup.topleft)
    pygame.draw.rect(surface, WHITE, popup, 3, border_radius=12)

    title = large_font.render("更新日誌", True, YELLOW)
    surface.blit(title, (popup.centerx - title.get_width()//2, popup.y + 25))

    content_rect = pygame.Rect(popup.x + 40, popup.y + 90, popup.width - 80, popup.height - 180)
    if changelog_content_surface is None: rebuild_changelog_cache(content_rect.width, content_rect.height)

    scroll_y = min(changelog_scroll, changelog_max_scroll)
    surface.blit(changelog_content_surface, content_rect.topleft, pygame.Rect(0, scroll_y, content_rect.width, content_rect.height))
    pygame.draw.rect(surface, GRAY, content_rect, 1)

    if changelog_max_scroll > 0:
        bar_h = max(40, int(content_rect.height * content_rect.height / changelog_content_surface.get_height()))
        bar_y = content_rect.y + int((content_rect.height - bar_h) * (scroll_y / changelog_max_scroll))
        pygame.draw.rect(surface, GRAY, (content_rect.right + 8, content_rect.y, 8, content_rect.height), border_radius=4)
        pygame.draw.rect(surface, YELLOW, (content_rect.right + 8, bar_y, 8, bar_h), border_radius=4)

    changelog_close_button.center = (popup.centerx, popup.bottom - 40)
    close_color = RED if changelog_close_button.collidepoint(pygame.mouse.get_pos()) else (150, 50, 50)
    pygame.draw.rect(surface, close_color, changelog_close_button, border_radius=10); pygame.draw.rect(surface, WHITE, changelog_close_button, 3, border_radius=10)
    close_txt = font.render("關閉", True, WHITE)
    surface.blit(close_txt, (changelog_close_button.centerx - close_txt.get_width()//2, changelog_close_button.centery - close_txt.get_height()//2))

def draw_pause_upgrade_log(surface):
    panel_rect = pygame.Rect(WIDTH//2 - 330, HEIGHT//2 + 235, 660, 260)
    panel = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    panel.fill((18, 20, 30, 205)); surface.blit(panel, panel_rect.topleft)
    pygame.draw.rect(surface, WHITE, panel_rect, 2, border_radius=8)

    title = small_font.render("本局強化紀錄（滑鼠滾輪上下瀏覽）", True, YELLOW)
    surface.blit(title, (panel_rect.x + 16, panel_rect.y + 12))
    content_rect = pygame.Rect(panel_rect.x + 16, panel_rect.y + 44, panel_rect.width - 42, panel_rect.height - 58)

    rows =[]
    for upgrade in chosen_upgrades:
        option = next((opt for opt in upgrade_options if opt["title"] == upgrade["title"]), None)
        desc = " / ".join(option["desc"]) if option else ""
        count = f" x{upgrade['count']}" if upgrade["count"] > 1 else ""
        rows.append((f"{upgrade['title']}{count}", desc))

    if not rows:
        surface.blit(small_font.render("尚未選擇任何強化", True, GRAY), (content_rect.x, content_rect.y + 8))
        return

    row_h = 54
    content_height = max(content_rect.height, len(rows) * row_h)
    max_scroll = max(0, content_height - content_rect.height)
    scroll_y = min(pause_upgrade_scroll, max_scroll)
    content_surface = pygame.Surface((content_rect.width, content_height), pygame.SRCALPHA)

    for i, (name, desc) in enumerate(rows):
        y = i * row_h
        content_surface.blit(small_font.render(name, True, WHITE), (0, y))
        for j, line in enumerate(wrap_text(desc, tiny_font, content_rect.width - 20)):
            content_surface.blit(tiny_font.render(line, True, YELLOW), (18, y + 25 + j * 20))

    surface.blit(content_surface, content_rect.topleft, pygame.Rect(0, scroll_y, content_rect.width, content_rect.height))
    if max_scroll > 0:
        bar_h = max(36, int(content_rect.height * content_rect.height / content_height))
        bar_y = content_rect.y + int((content_rect.height - bar_h) * (scroll_y / max_scroll))
        pygame.draw.rect(surface, GRAY, (content_rect.right + 8, content_rect.y, 7, content_rect.height), border_radius=4)
        pygame.draw.rect(surface, YELLOW, (content_rect.right + 8, bar_y, 7, bar_h), border_radius=4)

def draw_upgrade_summary(surface, x, y, max_items=6, title="已選強化"):
    panel_width, row_height = 260, 28
    hidden_count = max(0, len(chosen_upgrades) - max_items)
    row_count = max(1, min(len(chosen_upgrades), max_items))
    panel_height = 44 + row_count * row_height + (row_height if hidden_count else 0)
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((18, 20, 30, 185)); surface.blit(panel, (x, y))
    pygame.draw.rect(surface, WHITE, (x, y, panel_width, panel_height), 2, border_radius=8)

    title_label = f"{title} ({sum(u['count'] for u in chosen_upgrades)})" if chosen_upgrades else title
    surface.blit(small_font.render(title_label, True, YELLOW), (x + 14, y + 10))

    if not chosen_upgrades:
        surface.blit(small_font.render("尚未選擇", True, GRAY), (x + 14, y + 42))
        return

    visible_upgrades = chosen_upgrades[-max_items:]
    for i, upgrade in enumerate(visible_upgrades):
        suffix = f" x{upgrade['count']}" if upgrade["count"] > 1 else ""
        surface.blit(small_font.render(f"{upgrade['title']}{suffix}", True, WHITE), (x + 14, y + 42 + i * row_height))

    if hidden_count:
        surface.blit(small_font.render(f"還有 {hidden_count} 種...", True, GRAY), (x + 14, y + 42 + len(visible_upgrades) * row_height))

def draw_boss_entrance_frame():
    screen.fill(BLACK)
    draw_map_bounds(screen)
    
    for item in items: item.draw(screen)
    for p in particles: p.draw(screen)
    for b in bullets: b.draw(screen)
    for eb in enemy_bullets: eb.draw(screen) 
    for e in enemies: e.draw(screen)
    for t in trails: t.draw(screen)
    
    if boss_active: boss.draw(screen)
    player.draw(screen, player.weapons[player.current_weapon_idx])

    if 'dim_surface' not in globals():
        # 如果真的找不到，現場補做一個，並確保它等於目前視窗大小
        dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim_surface.fill((0, 0, 0, 150))

    screen.blit(dim_surface, (0, 0))
    title = large_font.render(boss.get_intro_title(), True, YELLOW)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 190))

    progress = min(1, boss.state_timer / boss.entrance_duration)
    bar_rect = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 - 120, 440, 18)
    pygame.draw.rect(screen, GRAY, bar_rect, border_radius=8)
    pygame.draw.rect(screen, RED, (bar_rect.x, bar_rect.y, int(bar_rect.width * progress), bar_rect.height), border_radius=8)
    pygame.draw.rect(screen, WHITE, bar_rect, 2, border_radius=8)

    for i, line in enumerate(boss.get_intro_lines()):
        color = RED if i == 0 else WHITE
        text = font.render(line, True, color)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 75 + i * 42))

    pause_text = small_font.render("出場動畫期間遊戲暫停，請觀察提示", True, GRAY)
    screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 + 70))

def reset_game(initial_state="PLAYING", mode=None):
    global player, bullets, enemy_bullets, enemies, particles, items, trails, damage_texts
    global boss, boss_active, boss_defeated, next_boss_level, boss_spawn_count, game_state, game_mode
    global current_upgrade_choices, selected_upgrade_position, chosen_upgrades, show_changelog, changelog_scroll
    global changelog_content_surface, changelog_max_scroll, pause_upgrade_scroll, global_offset_x, global_offset_y
    global shoot_cooldown, key_buffer, boss_warning_timer
    
    if mode is not None: game_mode = mode
    player = Player()
    bullets, enemy_bullets, enemies, particles, items, trails, damage_texts = [], [], [], [], [], [],[]
    boss, boss_active, boss_defeated, next_boss_level, boss_spawn_count = None, False, False, 5, 0
    current_upgrade_choices, selected_upgrade_position, chosen_upgrades = [], None,[]
    show_changelog, changelog_scroll, changelog_content_surface, changelog_max_scroll, pause_upgrade_scroll = False, 0, None, 0, 0
    global_offset_x, global_offset_y, shoot_cooldown, key_buffer, boss_warning_timer = 0, 0, 0,[], 0
    
    stop_sound("boss_bgm")
    if initial_state == "PLAYING":
        try: pygame.mixer.music.play(-1)
        except: pass
    game_state = initial_state
    pygame.time.set_timer(SPAWN_ENEMY_EVENT, NORMAL_SPAWN_INTERVAL if game_mode == NORMAL_MODE else CHALLENGE_SPAWN_INTERVAL)

reset_game("MENU")

# ==========================================
# 5. 遊戲主迴圈
# ==========================================
running = True
while running:
    # --- 動態調整 UI 位置 ---
    start_button.center = (WIDTH//2, HEIGHT//2 + 20)
    changelog_button.center = (WIDTH//2, HEIGHT//2 + 95)
    exit_button.center = (WIDTH//2, HEIGHT//2 + 170)
    
    normal_button.center = (WIDTH//2 - 220, HEIGHT//2)
    challenge_button.center = (WIDTH//2 + 220, HEIGHT//2)
    difficulty_back_button.center = (WIDTH//2, HEIGHT//2 + 245)

    cards[0].center = (WIDTH//2 - 250, HEIGHT//2)
    cards[1].center = (WIDTH//2, HEIGHT//2)
    cards[2].center = (WIDTH//2 + 250, HEIGHT//2)
    confirm_upgrade_button.center = (WIDTH//2, HEIGHT//2 + 200)

    restart_button.center = (WIDTH//2 - 120, HEIGHT//2 + 100)
    menu_button.center = (WIDTH//2 + 120, HEIGHT//2 + 100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if WINDOW_FOCUS_GAINED is not None and event.type == WINDOW_FOCUS_GAINED:
            switch_to_english_input()
        if game_state == "MENU" and show_changelog and event.type == pygame.MOUSEWHEEL:
            changelog_scroll = max(0, min(changelog_max_scroll, changelog_scroll - event.y * 55))
        if game_state == "PAUSED" and event.type == pygame.MOUSEWHEEL:
            pause_upgrade_scroll = max(0, pause_upgrade_scroll - event.y * 45)
        
        if event.type == pygame.VIDEORESIZE:
            if not fullscreen_mode:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if game_state == "PLAYING": game_state = "PAUSED"
            elif game_state == "PAUSED":
                switch_to_english_input()
                game_state = "PLAYING"
            elif game_state == "DIFFICULTY": game_state = "MENU"
            
        if game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: reset_game("PLAYING", game_mode); switch_to_english_input()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_button.collidepoint(event.pos): reset_game("PLAYING", game_mode); switch_to_english_input()
                elif menu_button.collidepoint(event.pos): reset_game("MENU", NORMAL_MODE)
                
        elif game_state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_changelog:
                    if changelog_close_button.collidepoint(event.pos): show_changelog = False
                elif start_button.collidepoint(event.pos): game_state = "DIFFICULTY"
                elif changelog_button.collidepoint(event.pos):
                    show_changelog, changelog_scroll = True, 0
                    if changelog_content_surface is None: rebuild_changelog_cache(720, 455)
                elif exit_button.collidepoint(event.pos): running = False
                
        elif game_state == "DIFFICULTY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if normal_button.collidepoint(event.pos): reset_game("PLAYING", NORMAL_MODE); switch_to_english_input()
                elif challenge_button.collidepoint(event.pos): reset_game("PLAYING", CHALLENGE_MODE); switch_to_english_input()
                elif difficulty_back_button.collidepoint(event.pos): game_state = "MENU"
                
        elif game_state == "PAUSED":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 70, 220, 60).collidepoint(event.pos): switch_to_english_input(); game_state = "PLAYING"
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 70, 220, 60).collidepoint(event.pos): reset_game("MENU", NORMAL_MODE)
                elif pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 150, 220, 60).collidepoint(event.pos): reset_game("PLAYING", game_mode); switch_to_english_input()
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 150, 220, 60).collidepoint(event.pos): running = False
                
        elif game_state == "LEVEL_UP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected_upgrade_position is not None and confirm_upgrade_button.collidepoint(event.pos):
                    apply_upgrade(current_upgrade_choices[selected_upgrade_position])
                else:
                    for i, card in enumerate(cards):
                        if i < len(current_upgrade_choices) and card.collidepoint(event.pos):
                            selected_upgrade_position = i; break
                            
        elif game_state == "PLAYING":
            if event.type == SPAWN_ENEMY_EVENT: 
                if not boss_active:
                    elite_chance = min(0.03 + player.level * 0.006, 0.15)
                    enemies.append(Enemy(level=player.level, is_elite=random.random() < elite_chance))
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen_mode = not fullscreen_mode
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if fullscreen_mode else pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                    WIDTH, HEIGHT = screen.get_size()
                # 秘技長度自動判斷，避免卡 Bug
                key_buffer.append(event.key)
                if len(key_buffer) > len(CHEAT_CODE): key_buffer.pop(0) 
                if key_buffer == CHEAT_CODE:
                    player.god_mode = not player.god_mode
                    play_sound("levelup"); key_buffer =[] 
                
                if event.key == pygame.K_e:
                    player.current_weapon_idx = (player.current_weapon_idx + 1) % len(player.weapons)
                    play_sound("exp")
                if event.key == pygame.K_r:
                    player.start_reload()

    if game_state == "PLAYING":
        if player.level >= next_boss_level and not boss_active:
            boss_spawn_count += 1
            if boss_spawn_count % 2 == 1:
                boss = Boss(random.choice(["YELLOW", "PURPLE"]), next_boss_level)
            else:
                boss = ChargerBoss(next_boss_level)
            boss_active, boss_warning_timer, boss_defeated = True, 120, False
            enemies.clear()
            try: pygame.mixer.music.stop()
            except: pass
            play_sound("boss_bgm", loop=-1) 

        boss_entrance_pause = boss_active and boss and boss.state == "ENTRANCE"
        if boss_entrance_pause:
            boss.update(player.pos, bullets)
            if boss_warning_timer > 0: boss_warning_timer -= 1
            draw_boss_entrance_frame()
            pygame.display.flip()
            clock.tick(FPS)
            continue

        mouse_btns, (mouse_x, mouse_y) = pygame.mouse.get_pressed(), pygame.mouse.get_pos()
        current_wep = player.weapons[player.current_weapon_idx]

    # 玩家左鍵普通射擊發射機制，結合 A3 的升級系統與 B4 的12種武器特性
    if mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing and player.can_fire_current_weapon():
        # 1. 取得世界座標與基礎方向
        world_mouse = pygame.math.Vector2(mouse_x + global_offset_x, mouse_y + global_offset_y)
        actual_muzzle_start = player.get_muzzle_pos(world_mouse)
    
        base_dir = world_mouse - player.pos
        if base_dir.length_squared() > 0:
            base_dir.normalize_ip()
        else:
            base_dir = pygame.math.Vector2(1, 0)

        # 判斷武器類型
        wep_type = current_wep.bullet_type
        # B4 的穿透型武器清單
        is_piercing = wep_type in ["piercing", "laser", "cannon", "flamethrower", "plasma", "railgun"]
    
        # 計算扇形擴散 (A3 升級系統)
        # 穿透型武器的散度通常較小
        current_spread = player.bullet_spread * (0.35 if is_piercing else 1)
        start_angle = -(player.bullet_count - 1) * current_spread / 2
    
        # 發射迴圈
        for c in range(player.bullet_count):
            angle_offset = start_angle + c * current_spread
            shot_dir = base_dir.rotate(angle_offset)
        
            # 處理「同路徑多重子彈」升級
            for j in range(1 + player.extra_same_path_bullets):
                # 每一顆子彈的起點 (考慮槍口位置與路徑偏移)
                spawn_pos = actual_muzzle_start + shot_dir * (j * 18)
            
                # 武器機制產生子彈
                if wep_type == "shotgun":
                    # 散彈槍：每一發再額外噴出 5 顆扇形子彈
                    for i in range(-2, 3):
                        final_dir = shot_dir.rotate(i * 12)
                        target_pos = spawn_pos + final_dir * 100
                        bullets.append(Bullet(spawn_pos, target_pos, current_wep, player.guidance_level))

                elif wep_type == "spread":
                    # 大範圍擴散彈：角度更寬
                    final_dir = shot_dir.rotate(random.uniform(-15, 15))
                    target_pos = spawn_pos + final_dir * 100
                    bullets.append(Bullet(spawn_pos, target_pos, current_wep, player.guidance_level))
            
                elif wep_type == "flamethrower":
                    # 火焰噴射器：目標點隨機抖動，模擬火焰的散亂效果
                    target_pos = spawn_pos + shot_dir * 100
                    target_pos += (random.randint(-40, 40), random.randint(-40, 40))
                    bullets.append(Bullet(spawn_pos, target_pos, current_wep, player.guidance_level))
                
                else:
                    # 其他所有武器 (Pistol, SMG, Sniper, Laser, Railgun 等)
                    # 這些武器的差異主要在 Bullet 類別內的 speed, damage, piercing 屬性
                    target_pos = spawn_pos + shot_dir * 100
                    bullets.append(Bullet(spawn_pos, target_pos, current_wep, player.guidance_level))
    
        # 5. 更新冷卻與音效 B4 的高頻率與低頻率差異
        shoot_cooldown = current_wep.shoot_delay
        if is_piercing and shoot_cooldown < 10: # 強力武器若冷卻過短則修正
            shoot_cooldown = 15 
        
        player.consume_current_ammo()
        play_sound(current_wep.sound_name)
            
        # 玩家右鍵技能發動機制，結合 B4 的12種武器特性
        if mouse_btns[2] and player.skill_cd <= 0 and player.energy >= player.skill_cost and not player.is_dashing:
            player.energy -= player.skill_cost; player.skill_cd = player.skill_max_cd; play_sound("shoot_cannon") 
            temp_wep = Weapon("大絕", 0, "piercing", 50) 
            for i in range(16):
                angle = math.radians(i * (360 / 16))
                target_pos = player.pos + pygame.math.Vector2(math.cos(angle)*100, math.sin(angle)*100)
                bullets.append(Bullet(player.pos, target_pos, temp_wep))

        if shoot_cooldown > 0: shoot_cooldown -= 1
        player.update()
        
        #恢復
        if player.regen_level > 0 and player.hp < player.max_hp:
            player.regen_progress += 0.01 * player.regen_level
            if player.regen_progress >= 1:
                heal = int(player.regen_progress)
                player.hp = min(player.max_hp, player.hp + heal)
                player.regen_progress -= heal
        else: player.regen_progress = 0

        if player.is_dashing: trails.append(DashTrail(player.pos, player.size))
        for t in trails[::-1]:
            t.update(); 
            if t.life <= 0: trails.remove(t)
            
        world_rect = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
        for b in bullets[::-1]:
            b.update()
            if getattr(b, 'explode', False):
                play_sound("shoot_cannon") 
                for _ in range(30): particles.append(Particle(b.pos.x, b.pos.y, ORANGE))
                for e in enemies[::-1]:
                    if b.pos.distance_to(e.pos) < 120: 
                        shield_damage = min(e.shield, b.damage)
                        e.shield -= shield_damage
                        e.hp -= (b.damage - shield_damage)
                        damage_texts.append(DamageText(e.pos.x, e.pos.y - 15, b.damage, YELLOW if b.damage >= 30 else WHITE))
                        if e.hp <= 0: 
                            if random.random() < e.exp_drop_chance: items.append(DropItem(e.pos.x, e.pos.y, "EXP"))
                            enemies.remove(e)
                if boss_active and b.pos.distance_to(boss.pos) < 150: 
                    boss.hp -= b.damage
                    damage_texts.append(DamageText(boss.pos.x, boss.pos.y - 30, b.damage, YELLOW if b.damage >= 30 else WHITE))
                bullets.remove(b)
                continue
            if b.lifespan <= 0 or not world_rect.inflate(500, 500).colliderect(b.rect): bullets.remove(b)
            
        for eb in enemy_bullets[::-1]:
            eb.update()
            if not world_rect.inflate(500, 500).colliderect(eb.rect): enemy_bullets.remove(eb)
            
        for dt in damage_texts[::-1]:
            dt.update()
            if dt.timer <= 0: damage_texts.remove(dt)    
            
        for e in enemies:
            e.update(player.pos, enemies)
            e.emit_attacks(enemy_bullets, player.pos)
            
        for p in particles[::-1]:
            p.update(); 
            if p.timer <= 0: particles.remove(p)

        if boss_warning_timer > 0: boss_warning_timer -= 1

        if boss_active:
            boss.update(player.pos, bullets) 
            boss.emit_attacks(enemy_bullets)
            
        if boss_active and boss.state == "DEFEAT" and boss.defeat_timer > 60:
            boss_active, boss_defeated = False, True
            next_boss_level += 5
            stop_sound("boss_bgm")
            try: pygame.mixer.music.play(-1)
            except: pass

        # 玩家子彈撞到敵人
        for b in bullets[::-1]:
            hit_something = False
            for e in enemies[::-1]:
                if b.rect.colliderect(e.rect):
                    if b.b_type == "frost": e.frost_timer = 120 
                    if b.b_type == "cannon": 
                        push_dir = e.pos - player.pos
                        if push_dir.length() > 0: push_dir.normalize_ip(); e.pos += push_dir * 30 
                    elif b.b_type == "flame_grenade": b.explode = True; break
                        
                    shield_damage = min(e.shield, b.damage)
                    e.shield -= shield_damage
                    actual_damage = b.damage - shield_damage
                    e.hp -= actual_damage
                    
                    damage_texts.append(DamageText(e.pos.x, e.pos.y - 15, b.damage, YELLOW if b.damage >= 30 else WHITE))
                    hit_something = True
                    for _ in range(5): particles.append(Particle(e.pos.x, e.pos.y, b.color))
                    play_sound("hit")
                    
                    if e.hp <= 0:
                        for _ in range(12 if e.is_elite else 6): particles.append(Particle(e.pos.x, e.pos.y, RED))
                        if random.random() < e.exp_drop_chance: 
                            gem_count = 3 if e.is_elite else 1
                            for _ in range(gem_count): items.append(DropItem(e.pos.x + random.randint(-12,12), e.pos.y + random.randint(-12,12), "EXP", 35))
                        if random.random() < e.health_drop_chance: 
                            items.append(DropItem(e.pos.x, e.pos.y, "HP", 40 if e.is_elite else 25))
                        enemies.remove(e)
            
            if getattr(b, 'explode', False): continue 

            if boss_active and b.rect.colliderect(boss.rect):
                hit_something = True
                if not boss.can_take_damage():
                    for _ in range(5): particles.append(Particle(boss.pos.x, boss.pos.y, GRAY))
                elif boss.state != "DEFEAT":
                    if b.b_type == "frost": boss.frost_timer = 60 
                    boss.hp -= b.damage
                    damage_texts.append(DamageText(boss.pos.x, boss.pos.y - 30, b.damage, YELLOW if b.damage >= 30 else WHITE))
                    for _ in range(8): particles.append(Particle(boss.pos.x, boss.pos.y, YELLOW))
                    play_sound("hit")
                    
                    if boss.hp <= 0:
                        boss.state, boss.defeat_timer = "DEFEAT", 0
                        for _ in range(40): items.append(DropItem(boss.pos.x + random.randint(-60,60), boss.pos.y + random.randint(-60,60), "EXP", 35))
                        for _ in range(5): items.append(DropItem(boss.pos.x + random.randint(-40,40), boss.pos.y + random.randint(-40,40), random.choice(["HP", "SHIELD"]), 25))
                        for _ in range(50): particles.append(Particle(boss.pos.x, boss.pos.y, YELLOW))
            if hit_something and not b.is_piercing and b in bullets: bullets.remove(b)

        # 電弧光環傷害
        if player.aura_level > 0:
            aura_radius = 95 + player.aura_level * 25
            aura_damage = 0.015 * player.aura_level
            for e in enemies[::-1]:
                if player.pos.distance_to(e.pos) <= aura_radius:
                    shield_damage = min(e.shield, aura_damage)
                    e.shield -= shield_damage
                    e.hp -= (aura_damage - shield_damage)
                    if random.random() < 0.08: particles.append(Particle(e.pos.x, e.pos.y, BLUE))
                    if e.hp <= 0:
                        for _ in range(8 if e.is_elite else 4): particles.append(Particle(e.pos.x, e.pos.y, e.color))
                        if random.random() < e.exp_drop_chance: items.append(DropItem(e.pos.x, e.pos.y, "EXP"))
                        if random.random() < e.health_drop_chance: items.append(DropItem(e.pos.x, e.pos.y, "HP", 40 if e.is_elite else 25))
                        enemies.remove(e)

        # 玩家受傷
        def player_take_damage(dmg):
            global game_state
            if player.god_mode: return 
            if player.invincible_timer <= 0 and not player.is_dashing:
                actual_dmg = max(1, dmg - player.damage_reduction)
                if player.shield > 0:
                    if player.shield >= actual_dmg: player.shield -= actual_dmg; actual_dmg = 0
                    else: actual_dmg -= player.shield; player.shield = 0
                if actual_dmg > 0: player.hp -= actual_dmg
                player.invincible_timer = player.invincible_duration; play_sound("hurt")
                if player.hp <= 0:
                    game_state = "GAME_OVER"; play_sound("gameover"); stop_sound("boss_bgm")  
                    try: pygame.mixer.music.stop()
                    except: pass

        for e in enemies:
            if e.combat_type == "melee" and player.rect.colliderect(e.rect): player_take_damage(e.damage)
        for eb in enemy_bullets[::-1]:
            if player.rect.colliderect(eb.rect): player_take_damage(25); enemy_bullets.remove(eb) if eb in enemy_bullets else None
        if boss_active and boss.state != "DEFEAT" and player.rect.colliderect(boss.rect): player_take_damage(boss.collision_damage) 

        # 吃掉掉落物
        for item in items[::-1]:
            item.update(player.pos, player.magnet_radius)
            if player.rect.colliderect(item.rect):
                items.remove(item)
                if item.item_type == "EXP": player.exp += int(item.amount * player.exp_multiplier); play_sound("exp") 
                elif item.item_type == "HP": player.hp = min(player.max_hp, player.hp + item.amount); play_sound("exp")
                elif item.item_type == "SHIELD": player.shield = min(player.max_shield, player.shield + item.amount); play_sound("exp")

                if player.exp >= player.max_exp:
                    player.level += 1; player.exp = 0; player.max_exp = int(player.max_exp * 1.25) 
                    choose_upgrade_cards(); game_state = "LEVEL_UP"; play_sound("levelup") 

    # 畫面繪製
    if game_state == "MENU":
        screen.fill(BLACK)
        for i in range(100):
            x = (i * 37) % WIDTH; y = (i * 23) % HEIGHT
            brightness = 100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i)
            pygame.draw.circle(screen, (int(brightness), int(brightness), int(brightness)), (x, y), 1)
            
        glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        title = large_font.render("Space War", True, BLUE)
        glow_surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -3), (0, 3), (-3, 0), (3, 0)]:
            glow_copy = glow_surface.copy()
            glow_copy.fill((0, 100, 255, 50), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(glow_copy, offset)
            
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        subtitle = font.render("霓虹驅魔人", True, WHITE)
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2 - 60))
        
        mouse_pos = pygame.mouse.get_pos()
        if start_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (100, 200, 100), start_button.inflate(10, 10), border_radius=12)
            pygame.draw.rect(screen, YELLOW, start_button.inflate(10, 10), 4, border_radius=12)
        else:
            pygame.draw.rect(screen, (50, 150, 50), start_button, border_radius=10)
            pygame.draw.rect(screen, WHITE, start_button, 3, border_radius=10)
        start_txt = font.render("開始遊戲", True, WHITE)
        screen.blit(start_txt, (start_button.centerx - start_txt.get_width()//2, start_button.centery - start_txt.get_height()//2))

        pygame.draw.rect(screen, BLUE if changelog_button.collidepoint(mouse_pos) else (50, 100, 150), changelog_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, changelog_button, 3, border_radius=10)
        cl_txt = font.render("更新日誌", True, WHITE)
        screen.blit(cl_txt, (changelog_button.centerx - cl_txt.get_width()//2, changelog_button.centery - cl_txt.get_height()//2))

        pygame.draw.rect(screen, RED if exit_button.collidepoint(mouse_pos) else (150, 50, 50), exit_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, exit_button, 3, border_radius=10)
        ex_txt = font.render("退出遊戲", True, WHITE)
        screen.blit(ex_txt, (exit_button.centerx - ex_txt.get_width()//2, exit_button.centery - ex_txt.get_height()//2))
        
        controls_title = font.render("操作說明:", True, YELLOW)
        screen.blit(controls_title, (WIDTH//2 - controls_title.get_width()//2, HEIGHT//2 + 250))
        controls = ["移動: WASD", "射擊: 滑鼠左鍵", "大絕招: 滑鼠右鍵", "衝刺: Q鍵 或 SPACE", "切換武器: E鍵", "暫停: ESC", "全螢幕: F11"]
        for i, c in enumerate(controls): screen.blit(small_font.render(c, True, GRAY), (WIDTH//2 - small_font.size(c)[0]//2, HEIGHT//2 + 285 + i*25))

        screen.blit(font.render("v1.5 (A3+B4 終極完全體)", True, GRAY), (20, HEIGHT - 40))

        if show_changelog: draw_changelog_popup(screen)
        
    elif game_state == "DIFFICULTY":
        screen.fill(BLACK)
        for i in range(100):
            x = (i * 37) % WIDTH; y = (i * 23) % HEIGHT
            brightness = 100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i)
            pygame.draw.circle(screen, (int(brightness), int(brightness), int(brightness)), (x, y), 1)

        title = large_font.render("選擇難易度", True, YELLOW)
        subtitle = font.render("Boss 戰會清空小怪，專心迎戰核心威脅", True, GRAY)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 235))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2 - 180))

        mouse_pos = pygame.mouse.get_pos()
        normal_hovered, challenge_hovered = normal_button.collidepoint(mouse_pos), challenge_button.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (55, 125, 185) if normal_hovered else (30, 70, 115), normal_button, border_radius=10)
        pygame.draw.rect(screen, YELLOW if normal_hovered else WHITE, normal_button, 4 if normal_hovered else 3, border_radius=10)
        pygame.draw.rect(screen, (190, 55, 70) if challenge_hovered else (115, 35, 50), challenge_button, border_radius=10)
        pygame.draw.rect(screen, YELLOW if challenge_hovered else WHITE, challenge_button, 4 if challenge_hovered else 3, border_radius=10)

        n_txt = large_font.render("普通", True, WHITE)
        screen.blit(n_txt, (normal_button.centerx - n_txt.get_width()//2, normal_button.y + 28))
        screen.blit(small_font.render("標準節奏，無限彈藥", True, WHITE), (normal_button.centerx - 85, normal_button.y + 88))
        for i, line in enumerate(["敵人強度：標準", "彈藥：無需換彈", "適合享受割草快感"]):
            screen.blit(small_font.render(line, True, (210, 225, 240)), (normal_button.x + 42, normal_button.y + 132 + i * 28))

        c_txt = large_font.render("挑戰", True, WHITE)
        screen.blit(c_txt, (challenge_button.centerx - c_txt.get_width()//2, challenge_button.y + 28))
        screen.blit(small_font.render("敵人 1.75 倍，啟用彈匣", True, WHITE), (challenge_button.centerx - 100, challenge_button.y + 88))
        for i, line in enumerate(["彈匣打完自動換彈 (也可按 R)", "追加挑戰專屬卡牌", "適合追求極限走位"]):
            screen.blit(small_font.render(line, True, (255, 220, 220)), (challenge_button.x + 42, challenge_button.y + 132 + i * 28))

        pygame.draw.rect(screen, BLUE if difficulty_back_button.collidepoint(mouse_pos) else (50, 100, 150), difficulty_back_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, difficulty_back_button, 3, border_radius=10)
        screen.blit(font.render("返回", True, WHITE), (difficulty_back_button.centerx - 28, difficulty_back_button.centery - 16))

    else:
        # 遊戲進行中畫面繪製
        if images.get("bg"):
            bg_img = pygame.transform.scale(images["bg"], (WIDTH, HEIGHT))
            bg_x, bg_y = -global_offset_x % WIDTH, -global_offset_y % HEIGHT
            screen.blit(bg_img, (bg_x, bg_y)); screen.blit(bg_img, (bg_x - WIDTH, bg_y))
            screen.blit(bg_img, (bg_x, bg_y - HEIGHT)); screen.blit(bg_img, (bg_x - WIDTH, bg_y - HEIGHT))
        else: screen.fill(BLACK)
        draw_map_bounds(screen)
        
        for i in items: i.draw(screen)
        for p in particles: p.draw(screen)
        for b in bullets: b.draw(screen)
        for eb in enemy_bullets: eb.draw(screen) 
        for e in enemies: e.draw(screen)
        for t in trails: t.draw(screen)
        if boss_active: boss.draw(screen) 
        
        player.draw(screen, player.weapons[player.current_weapon_idx] if game_state in ["PLAYING", "PAUSED"] else None)
        
        # 將浮動傷害畫在最上面一層，才不會被怪物擋住
        for dt in damage_texts: dt.draw(screen)
        if boss_active: draw_boss_direction_arrow(screen, boss)

        # UI
        pygame.draw.rect(screen, GRAY, (20, 20, 250, 15)); pygame.draw.rect(screen, BLUE, (20, 20, 250 * (player.exp / player.max_exp), 15))
        screen.blit(font.render(f"等級: {player.level}", True, WHITE), (280, 15))
        pygame.draw.rect(screen, GRAY, (20, 45, 200, 15)); pygame.draw.rect(screen, GREEN if player.hp > 30 else RED, (20, 45, 200 * (max(0, player.hp) / player.max_hp), 15))
        screen.blit(font.render(f"血量", True, WHITE), (230, 40))
        pygame.draw.rect(screen, GRAY, (20, 70, 200, 12)); pygame.draw.rect(screen, BLUE, (20, 70, 200 * (max(0, player.shield) / player.max_shield), 12))
        screen.blit(font.render("護盾", True, WHITE), (230, 62))
        pygame.draw.rect(screen, GRAY, (20, 95, 150, 10)); pygame.draw.rect(screen, ORANGE, (20, 95, 150 * (player.stamina / player.max_stamina), 10))
        screen.blit(font.render("體力 (Q鍵)", True, WHITE), (180, 87)) 
        pygame.draw.rect(screen, GRAY, (20, 120, 150, 10)); pygame.draw.rect(screen, CYAN, (20, 120, 150 * (player.energy / player.max_energy), 10))
        screen.blit(font.render("能量", True, WHITE), (180, 112))

        if game_mode == CHALLENGE_MODE:
            screen.blit(small_font.render("挑戰模式", True, RED), (20, 142))
            r_c = YELLOW if player.current_weapon_type() == "pistol" else WHITE
            s_c = YELLOW if player.current_weapon_type() == "sniper" else WHITE
            screen.blit(small_font.render(f"一般彈藥: {player.pistol_ammo}/{player.pistol_mag_size}", True, r_c), (20, 170))
            screen.blit(small_font.render(f"高階彈藥: {player.sniper_ammo}/{player.sniper_mag_size}", True, s_c), (20, 196))
            if player.reload_timer > 0:
                pygame.draw.rect(screen, GRAY, (20, 224, 170, 10))
                pygame.draw.rect(screen, YELLOW, (20, 224, int(170 * (1 - player.reload_timer / player.reload_duration)), 10))
                reload_name = "高階" if player.reloading_weapon == "sniper" else "一般"
                screen.blit(small_font.render(f"{reload_name}換彈中", True, YELLOW), (200, 212))

        wep_name = player.weapons[player.current_weapon_idx].name
        screen.blit(font.render(f"武器: {wep_name} (E 鍵切換)", True, WHITE), (20, 250 if game_mode == CHALLENGE_MODE else 145))
        wep_icon = images.get("icon_" + wep_name)
        if wep_icon: screen.blit(wep_icon, (20, 280 if game_mode == CHALLENGE_MODE else 175))

        if player.skill_cd > 0: skill_txt = font.render(f"大絕冷卻: {round(player.skill_cd / 60, 1)} 秒", True, GRAY)
        elif player.energy < player.skill_cost: skill_txt = font.render("大絕: 能量不足", True, RED)
        else: skill_txt = font.render("大絕準備就緒 (右鍵)", True, GREEN)
        screen.blit(skill_txt, (WIDTH - 280, HEIGHT - 40))
        if player.god_mode: screen.blit(font.render("【無敵模式啟用】", True, YELLOW), (WIDTH//2 - 100, 20))

        if boss_active:
            bar_w = min(WIDTH - 100, 800)
            bar_x = WIDTH//2 - bar_w//2
            pygame.draw.rect(screen, GRAY, (bar_x, HEIGHT - 80, bar_w, 20))
            boss_bar_color = RED if boss.b_type == "RED" else (PURPLE if boss.b_type == "PURPLE" else YELLOW)
            pygame.draw.rect(screen, boss_bar_color, (bar_x, HEIGHT - 80, bar_w * (max(0, boss.hp) / boss.max_hp), 20))
            
            if boss_warning_timer > 0 and boss.state != "ENTRANCE": screen.blit(font.render(f"⚠️ 警告：偵測到極度危險異常實體 - 【{boss.name}】", True, RED), (WIDTH//2 - 250, HEIGHT - 110))
            elif boss.state != "ENTRANCE":
                msg, clr = boss.get_state_message()
                screen.blit(font.render(f"Lv.{boss.spawn_level} 【{boss.name}】: {msg}", True, clr), (WIDTH//2 - 250, HEIGHT - 110))

        if game_state == "LEVEL_UP":
            screen.blit(dim_surface, (0, 0)) 
            title = large_font.render("升級！選擇強化後按確認", True, YELLOW)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
            
            for i, card in enumerate(cards):
                if i >= len(current_upgrade_choices): continue
                upgrade = upgrade_options[current_upgrade_choices[i]]
                is_selected = (selected_upgrade_position == i)
                base_color = CARD_TYPE_COLORS.get(upgrade.get("type"), CARD_COLOR)
                hover_color = tuple(min(255, c + 35) for c in base_color)
                color = tuple(min(255, c + 65) for c in base_color) if is_selected else hover_color if card.collidepoint(pygame.mouse.get_pos()) else base_color
                
                pygame.draw.rect(screen, color, card, border_radius=10)
                pygame.draw.rect(screen, YELLOW if is_selected else WHITE, card, 6 if is_selected else 3, border_radius=10) 
                
                type_label = CARD_TYPE_LABELS.get(upgrade.get("type"), "")
                if type_label:
                    label_bg = pygame.Rect(card.centerx - 42, card.y + 18, 84, 28)
                    pygame.draw.rect(screen, (20, 20, 28), label_bg, border_radius=8)
                    pygame.draw.rect(screen, WHITE, label_bg, 1, border_radius=8)
                    screen.blit(small_font.render(type_label, True, WHITE), (label_bg.centerx - 20, label_bg.centery - 12))
                
                opt_title = font.render(upgrade["title"], True, WHITE)
                screen.blit(opt_title, (card.centerx - opt_title.get_width()//2, card.y + 65))
                screen.blit(font.render(upgrade["desc"][0], True, YELLOW), (card.centerx - font.size(upgrade["desc"][0])[0]//2, card.y + 125))
                screen.blit(font.render(upgrade["desc"][1], True, YELLOW), (card.centerx - font.size(upgrade["desc"][1])[0]//2, card.y + 165))
            
            confirm_ready = selected_upgrade_position is not None
            pygame.draw.rect(screen, GREEN if confirm_ready and confirm_upgrade_button.collidepoint(pygame.mouse.get_pos()) else (50, 150, 50) if confirm_ready else GRAY, confirm_upgrade_button, border_radius=10)
            pygame.draw.rect(screen, WHITE, confirm_upgrade_button, 3, border_radius=10)
            screen.blit(font.render("確認選擇", True, WHITE), (confirm_upgrade_button.centerx - 55, confirm_upgrade_button.centery - 15))

        elif game_state == "PAUSED":
            screen.blit(dim_surface, (0, 0))
            screen.blit(large_font.render("暫停中", True, YELLOW), (WIDTH//2 - 75, HEIGHT//2 - 200))
            
            btns =[
                (pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 70, 220, 60), "繼續遊戲", BLUE),
                (pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 70, 220, 60), "回到選單", BLUE),
                (pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 150, 220, 60), "重新開始", GREEN),
                (pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 150, 220, 60), "退出遊戲", RED)
            ]
            for btn, txt, clr in btns:
                pygame.draw.rect(screen, clr if btn.collidepoint(pygame.mouse.get_pos()) else (clr[0]//2, clr[1]//2, clr[2]//2), btn, border_radius=10)
                pygame.draw.rect(screen, WHITE, btn, 3, border_radius=10)
                t_surf = font.render(txt, True, WHITE)
                screen.blit(t_surf, (btn.centerx - t_surf.get_width()//2, btn.centery - t_surf.get_height()//2))
            
            draw_pause_upgrade_log(screen)

        elif game_state == "GAME_OVER":
            screen.blit(dim_surface, (0, 0))
            game_over_txt = large_font.render("Game Over", True, RED)
            screen.blit(game_over_txt, (WIDTH//2 - game_over_txt.get_width()//2, HEIGHT//2 - 150))
            
            for btn, txt, clr in [(restart_button, "重新開始", GREEN), (menu_button, "回到選單", BLUE)]:
                pygame.draw.rect(screen, clr if btn.collidepoint(pygame.mouse.get_pos()) else (clr[0]//2, clr[1]//2, clr[2]//2), btn, border_radius=10)
                pygame.draw.rect(screen, WHITE, btn, 3, border_radius=10)
                t_surf = font.render(txt, True, WHITE)
                screen.blit(t_surf, (btn.centerx - t_surf.get_width()//2, btn.centery - t_surf.get_height()//2))

    pygame.display.flip()
    clock.tick(FPS)

=======
import pygame
import random
import math
import os
import ctypes

# ==========================================
# 1. 遊戲初始化與視窗設定
# ==========================================
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1024, 768
MAP_WIDTH, MAP_HEIGHT = 4200, 2600 # 開放世界地圖大小
fullscreen_mode = False
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("霓虹驅魔人 - 終極完全體 (A3+B4 完美整合)")
clock = pygame.time.Clock()
FPS = 60
WINDOW_FOCUS_GAINED = getattr(pygame, "WINDOWFOCUSGAINED", None)

def switch_to_english_input():
    if os.name != "nt": return
    try:
        hwnd = pygame.display.get_wm_info().get("window")
        if hwnd:
            english_layout = ctypes.windll.user32.LoadKeyboardLayoutW("00000409", 1)
            ctypes.windll.user32.ActivateKeyboardLayout(english_layout, 0)
            ctypes.windll.user32.PostMessageW(hwnd, 0x0050, 0, english_layout)
    except Exception: pass

switch_to_english_input()

# --- 顏色定義 ---
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
CARD_TYPE_COLORS = { "attack": (120, 35, 45), "support": (35, 75, 130), "life": (35, 110, 65) }
CARD_TYPE_LABELS = { "attack": "攻擊", "support": "支援", "life": "生命" }
SHIELD_COLOR = (0, 102, 204)    
EXP_COLOR = (124, 252, 0)   
HP_COLOR = (255, 0, 0)    

NORMAL_MODE = "NORMAL"
CHALLENGE_MODE = "CHALLENGE"
CHALLENGE_ENEMY_MULTIPLIER = 1.75
CHALLENGE_ENEMY_SPEED_MULTIPLIER = 1.25
NORMAL_SPAWN_INTERVAL = 420
CHALLENGE_SPAWN_INTERVAL = 600

# --- 字體設定 ---
CHINESE_FONTS = "microsoftjhenghei,pingfangtc,stheiti,simhei"
font = pygame.font.SysFont(CHINESE_FONTS, 28)
large_font = pygame.font.SysFont(CHINESE_FONTS, 48)
small_font = pygame.font.SysFont(CHINESE_FONTS, 22)
tiny_font = pygame.font.SysFont(CHINESE_FONTS, 18)

# ==========================================
# 2. 智慧動畫、貼圖與音效系統
# ==========================================
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
        os.makedirs(folder_path) 
        animations[name] = None
        return
    frames =[]
    for file in sorted(os.listdir(folder_path)):
        if file.endswith((".png", ".jpg")):
            img = pygame.image.load(os.path.join(folder_path, file)).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
    animations[name] = frames if frames else None

# 載入所有圖片資源
load_image("bg", "bg.png", (WIDTH, HEIGHT))
load_image("drop_EXP", "drop_exp.png", (20, 20))
load_image("drop_HP", "drop_hp.png", (20, 20))
load_image("drop_SHIELD", "drop_shield.png", (20, 20))
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

# --- 音效系統 ---
sounds = {}
def load_sound(name, filename):
    try:
        sounds[name] = pygame.mixer.Sound(os.path.join(BASE_DIR, filename))
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

try:
    pygame.mixer.music.load(os.path.join(BASE_DIR, "bgm.mp3"))
    pygame.mixer.music.set_volume(0.2) 
except: pass

def play_sound(name, loop=0):
    if name in sounds and sounds[name] != None: sounds[name].play(loops=loop)
def stop_sound(name):
    if name in sounds and sounds[name] != None: sounds[name].stop()

# ==========================================
# 3. 遊戲機制與實體類別
# ==========================================
CHEAT_CODE =[pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_b, pygame.K_a, pygame.K_b, pygame.K_a]
key_buffer =[] 
global_offset_x = 0
global_offset_y = 0

class Weapon:
    def __init__(self, name, shoot_delay, bullet_type, damage, sound_name="shoot_normal"):
        self.name, self.shoot_delay, self.bullet_type, self.damage, self.sound_name = name, shoot_delay, bullet_type, damage, sound_name
        load_image("gun_" + name, f"gun_{name}.png", (45, 18))
        load_image("icon_" + name, f"icon_{name}.png", (60, 30))

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

class Player:
    def __init__(self):
        self.pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
        self.size, self.base_speed = 30, 5
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.weapons = list(WEAPON_TYPES.values())
        self.current_weapon_idx = 0
        self.anim_idx = 0
        
        # 強化系統數值
        self.bullet_count = 1      
        self.extra_same_path_bullets = 0
        self.bullet_spread = 15
        self.bullet_damage_bonus = 0
        self.guidance_level = 0
        self.aura_level = 0
        self.regen_level = 0
        self.regen_progress = 0
        self.exp_multiplier = 1.0
        self.damage_reduction = 0
        
        self.exp, self.level, self.max_exp = 0, 1, 100
        self.magnet_radius = 60
        self.max_hp, self.hp = 100, 100
        self.max_shield = int(self.max_hp * 0.2)
        self.shield = self.max_shield
        self.shield_regen_rate = 0.18
        self.shield_regen_delay = 150
        self.shield_regen_timer = 0
        self.invincible_timer, self.invincible_duration = 0, 60

        self.max_stamina, self.stamina, self.dash_cost, self.stamina_regen = 100, 100, 35, 0.5   
        self.is_dashing, self.dash_speed, self.dash_duration, self.dash_timer = False, 22, 8, 0
        self.dash_direction = pygame.math.Vector2(0, 0)
        self.max_energy, self.energy, self.energy_regen = 100, 100, 0.2     
        self.skill_cd, self.skill_max_cd, self.skill_cost = 0, 600, 50        
        self.god_mode = False 
        
        self.pistol_mag_size = 45
        self.sniper_mag_size = 7
        self.pistol_ammo = self.pistol_mag_size
        self.sniper_ammo = self.sniper_mag_size
        self.reload_timer = 0
        self.reload_duration = 90
        self.reloading_weapon = None

    def update(self):
        self.anim_idx += 0.15
        keys = pygame.key.get_pressed()
        move_vector = pygame.math.Vector2(0, 0)

        if self.reload_timer > 0:
            self.reload_timer -= 1
            if self.reload_timer <= 0:
                if self.reloading_weapon == "sniper": self.sniper_ammo = self.sniper_mag_size
                else: self.pistol_ammo = self.pistol_mag_size
                self.reloading_weapon = None
        
        if keys[pygame.K_w]: move_vector.y -= 1
        if keys[pygame.K_s]: move_vector.y += 1
        if keys[pygame.K_a]: move_vector.x -= 1
        if keys[pygame.K_d]: move_vector.x += 1
        if move_vector.length() > 0: move_vector.normalize_ip()

        if self.invincible_timer > 0: self.invincible_timer -= 1
        if self.skill_cd > 0: self.skill_cd -= 1
        
        if self.shield_regen_timer > 0: self.shield_regen_timer -= 1
        elif self.shield < self.max_shield: self.shield = min(self.max_shield, self.shield + self.shield_regen_rate)
            
        if not self.is_dashing and self.stamina < self.max_stamina: self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen)
        if self.energy < self.max_energy: self.energy = min(self.max_energy, self.energy + self.energy_regen)

        if (keys[pygame.K_q] or keys[pygame.K_SPACE]) and not self.is_dashing and self.stamina >= self.dash_cost:
            self.stamina -= self.dash_cost
            self.is_dashing, self.dash_timer = True, self.dash_duration
            play_sound("dash")
            if move_vector.length() > 0: self.dash_direction = move_vector.copy()
            else:
                mx, my = pygame.mouse.get_pos()
                self.dash_direction = pygame.math.Vector2(mx - WIDTH/2, my - HEIGHT/2)
                if self.dash_direction.length() > 0: self.dash_direction.normalize_ip()

        # 計算世界地圖的絕對座標
        world_pos = pygame.math.Vector2(WIDTH/2 + global_offset_x, HEIGHT/2 + global_offset_y)
        if self.is_dashing:
            world_pos += self.dash_direction * self.dash_speed
            self.dash_timer -= 1
            if self.dash_timer <= 0: self.is_dashing = False
        else:
            world_pos += move_vector * self.base_speed
            
        half = self.size / 2
        world_pos.x = max(half, min(MAP_WIDTH - half, world_pos.x))
        world_pos.y = max(half, min(MAP_HEIGHT - half, world_pos.y))
            
        # 計算位移，推進攝影機
        shift_x = world_pos.x - WIDTH/2 - global_offset_x
        shift_y = world_pos.y - HEIGHT/2 - global_offset_y
        apply_camera_follow(pygame.math.Vector2(shift_x, shift_y))
        
        self.pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2) # 玩家永遠在螢幕正中央
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def current_weapon_type(self):
        w_type = self.weapons[self.current_weapon_idx].bullet_type
        return "sniper" if w_type == "piercing" else "pistol"

    def can_fire_current_weapon(self):
        global game_mode
        if game_mode != CHALLENGE_MODE: return True
        if self.reload_timer > 0: return False
        if self.current_weapon_type() == "sniper": return self.sniper_ammo > 0
        return self.pistol_ammo > 0

    def consume_current_ammo(self):
        global game_mode
        if game_mode != CHALLENGE_MODE: return
        if self.current_weapon_type() == "sniper":
            self.sniper_ammo = max(0, self.sniper_ammo - 1)
            if self.sniper_ammo <= 0: self.start_reload("sniper")
        else:
            self.pistol_ammo = max(0, self.pistol_ammo - 1)
            if self.pistol_ammo <= 0: self.start_reload("pistol")

    def start_reload(self, weapon=None):
        global game_mode
        if game_mode != CHALLENGE_MODE or self.reload_timer > 0: return
        self.reloading_weapon = weapon or self.current_weapon_type()
        self.reload_timer = self.reload_duration

    def draw(self, surface, current_wep=None):
        draw_player = True
        if self.invincible_timer > 0 and not self.god_mode and (self.invincible_timer // 4) % 2 == 0:
            draw_player = False
                
        if draw_player:
            # 電弧光環
            if self.aura_level > 0:
                aura_radius = 95 + self.aura_level * 25
                pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10)
                pygame.draw.circle(surface, (0, 180, 255), self.rect.center, aura_radius + pulse, 2)
                pygame.draw.circle(surface, (0, 90, 180), self.rect.center, max(12, aura_radius - 18), 1)
                
            anim_frames = animations.get("player")
            if anim_frames:
                img = anim_frames[int(self.anim_idx) % len(anim_frames)]
                if pygame.mouse.get_pos()[0] < self.pos.x: img = pygame.transform.flip(img, True, False)
                surface.blit(img, img.get_rect(center=self.rect.center))
            else:
                pygame.draw.rect(surface, YELLOW if self.god_mode else BLUE, self.rect)
                
            if self.stamina < self.dash_cost: pygame.draw.rect(surface, GRAY, self.rect, 3)
            if self.shield > 0:
                s_color = (70, 180, 255) if (self.shield / self.max_shield) > 0.35 else (255, 210, 70)
                pygame.draw.circle(surface, s_color, self.rect.center, self.size // 2 + 8, 2)

            if current_wep:
                mx, my = pygame.mouse.get_pos()
                direction = pygame.math.Vector2(mx - self.pos.x, my - self.pos.y)
                if direction.length() > 0: direction.normalize_ip()
                else: direction = pygame.math.Vector2(1, 0)
                
                angle = math.degrees(math.atan2(-direction.y, direction.x))
                gun_img = images.get("gun_" + current_wep.name)
                
                if gun_img:
                    if direction.x < 0: gun_img = pygame.transform.flip(gun_img, False, True)
                    rotated_gun = pygame.transform.rotate(gun_img, angle)
                    gun_rect = rotated_gun.get_rect(center=(int(self.pos.x + direction.x * 15), int(self.pos.y + direction.y * 15)))
                    surface.blit(rotated_gun, gun_rect)
                else:
                    end_pos = self.pos + direction * 25
                    wep_color = PURPLE if current_wep.bullet_type == "piercing" else ORANGE if current_wep.bullet_type == "flamethrower" else CYAN if current_wep.bullet_type == "laser" else WHITE if current_wep.bullet_type == "cannon" else (100, 200, 255) if current_wep.bullet_type == "frost" else RED if current_wep.bullet_type == "flame_grenade" else GREEN if current_wep.bullet_type == "plasma" else YELLOW
                    pygame.draw.line(surface, GRAY, self.rect.center, end_pos, 6)
                    pygame.draw.circle(surface, wep_color, (int(end_pos.x), int(end_pos.y)), 4)

def apply_camera_follow(offset_vector):
    if offset_vector.length_squared() == 0: return
    global global_offset_x, global_offset_y
    global_offset_x += offset_vector.x
    global_offset_y += offset_vector.y
    
    for group in [bullets, enemy_bullets, enemies, particles, items, trails, damage_texts]:
        for obj in group:
            obj.pos -= offset_vector
            if hasattr(obj, "rect"): obj.rect.center = (round(obj.pos.x), round(obj.pos.y))
            if hasattr(obj, "target"): obj.target -= offset_vector
            
    if boss_active and boss:
        boss.pos -= offset_vector
        boss.rect.center = (round(boss.pos.x), round(boss.pos.y))
        if hasattr(boss, "aim_target"): boss.aim_target -= offset_vector

def draw_map_bounds(surface):
    map_rect = pygame.Rect(-global_offset_x, -global_offset_y, MAP_WIDTH, MAP_HEIGHT)
    pygame.draw.rect(surface, (25, 30, 45), map_rect, 4)
    for x in range(0, MAP_WIDTH + 1, 400):
        sx = x - global_offset_x
        if -10 <= sx <= WIDTH + 10: pygame.draw.line(surface, (18, 22, 32), (sx, max(0, -global_offset_y)), (sx, min(HEIGHT, MAP_HEIGHT - global_offset_y)), 1)
    for y in range(0, MAP_HEIGHT + 1, 400):
        sy = y - global_offset_y
        if -10 <= sy <= HEIGHT + 10: pygame.draw.line(surface, (18, 22, 32), (max(0, -global_offset_x), sy), (min(WIDTH, MAP_WIDTH - global_offset_x), sy), 1)

def draw_boss_direction_arrow(surface, boss_obj):
    if not boss_obj or boss_obj.state == "DEFEAT": return
    visible_rect = pygame.Rect(-40, -40, WIDTH + 80, HEIGHT + 80)
    if visible_rect.collidepoint(boss_obj.pos.x, boss_obj.pos.y): return

    center = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
    direction = boss_obj.pos - center
    if direction.length_squared() == 0: return
    direction.normalize_ip()
    margin = 56
    scale_x = (WIDTH / 2 - margin) / abs(direction.x) if abs(direction.x) > 0.001 else float("inf")
    scale_y = (HEIGHT / 2 - margin) / abs(direction.y) if abs(direction.y) > 0.001 else float("inf")
    arrow_pos = center + direction * min(scale_x, scale_y)
    side = direction.rotate(90)
    tip = arrow_pos + direction * 30
    left = arrow_pos - direction * 22 + side * 18
    right = arrow_pos - direction * 22 - side * 18
    arrow_points = [(int(tip.x), int(tip.y)), (int(left.x), int(left.y)), (int(right.x), int(right.y))]
    pygame.draw.polygon(surface, BLACK, arrow_points)
    pygame.draw.polygon(surface, YELLOW, arrow_points, 0)
    pygame.draw.polygon(surface, RED, arrow_points, 3)
    distance = max(0, int(player.pos.distance_to(boss_obj.pos)))
    distance_txt = small_font.render(f"Boss 距離 {distance:03d}", True, YELLOW)
    surface.blit(distance_txt, (int(arrow_pos.x - distance_txt.get_width()/2), int(arrow_pos.y - 48)))

class DashTrail:
    def __init__(self, pos, size): self.pos, self.size, self.life = pos.copy(), size, 12
    def update(self): self.life -= 1; self.size -= 1.5
    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            rect = pygame.Rect(0, 0, self.size, self.size)
            rect.center = (round(self.pos.x), round(self.pos.y))
            pygame.draw.rect(surface, BLUE, rect, max(1, int(self.life / 3)))

class Bullet:
    def __init__(self, start_pos, target_pos, weapon, guidance_level=0):
        self.pos = start_pos.copy()
        self.target = target_pos.copy()
        self.b_type, self.damage = weapon.bullet_type, weapon.damage + player.bullet_damage_bonus
        self.is_piercing = self.b_type in["piercing", "laser", "cannon", "flamethrower"]
        self.guidance_level = guidance_level
            
        self.direction = self.target - self.pos
        if self.direction.length() > 0: self.direction.normalize_ip()
        
        self.lifespan, self.speed, self.radius, self.color = 120, 18, 6, YELLOW
        if self.b_type == "piercing": self.color = PURPLE; self.speed = 28; self.radius = 7
        elif self.b_type == "flamethrower": self.color = ORANGE; self.speed = 12; self.radius = 12; self.lifespan = 25
        elif self.b_type == "laser": self.color = CYAN; self.speed = 45; self.radius = 4
        elif self.b_type == "cannon": self.color = WHITE; self.speed = 12; self.radius = 20
        elif self.b_type == "frost": self.color = (100, 200, 255); self.speed = 16; self.radius = 8
        elif self.b_type == "flame_grenade": self.color = RED; self.speed = 10; self.radius = 10
        elif self.b_type == "plasma": self.color = GREEN; self.speed = 15; self.radius = 10

        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        self.explode = False 

    def update(self):
        self.lifespan -= 1
        if self.guidance_level > 0 and self.lifespan % 2 == 0:
            targets = enemies[:]
            if boss_active and boss and boss.state != "DEFEAT": targets.append(boss)
            if targets:
                guide_range = 220 + self.guidance_level * 45
                nearby = [t for t in targets if self.pos.distance_to(t.pos) <= guide_range]
                if nearby:
                    target = min(nearby, key=lambda t: self.pos.distance_to(t.pos))
                    t_dir = target.pos - self.pos
                    if t_dir.length() > 0:
                        t_dir.normalize_ip()
                        turn_speed = min(0.08, 0.025 + self.guidance_level * 0.012)
                        self.direction += t_dir * turn_speed
                        self.direction.normalize_ip()
                        
        if self.b_type == "flame_grenade" and self.pos.distance_to(self.target) < self.speed:
            self.explode, self.lifespan = True, 0; return 
        if self.b_type == "plasma":
            screen_x, screen_y = self.pos.x + global_offset_x, self.pos.y + global_offset_y
            if screen_x <= 0 or screen_x >= MAP_WIDTH: self.direction.x *= -1
            if screen_y <= 0 or screen_y >= MAP_HEIGHT: self.direction.y *= -1
            
        self.pos += self.direction * self.speed
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def draw(self, surface):
        img = images.get("bullet_" + self.b_type)
        if img:
            angle = math.degrees(math.atan2(-self.direction.y, self.direction.x))
            rotated_img = pygame.transform.rotate(img, angle)
            surface.blit(rotated_img, rotated_img.get_rect(center=self.rect.center))
        else:
            if self.b_type == "laser":
                end_pos = self.pos - (self.direction * 30)
                pygame.draw.line(surface, self.color, self.pos, end_pos, self.radius*2)
            else: pygame.draw.circle(surface, self.color, self.rect.center, self.radius)

class EnemyBullet:
    def __init__(self, pos, direction, color=ORANGE, core_color=WHITE, style="round"):
        self.pos = pos.copy()
        self.direction = direction.copy()
        if self.direction.length() > 0: self.direction.normalize_ip()
        self.radius, self.speed, self.color = 8, 7, color
        self.core_color, self.style = core_color, style
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        
    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
    def draw(self, surface): 
        img = images.get("enemy_bullet")
        if img and self.style == "round": surface.blit(img, img.get_rect(center=self.rect.center))
        else:
            pygame.draw.circle(surface, BLACK, self.rect.center, self.radius + 4)
            pygame.draw.circle(surface, self.color, self.rect.center, self.radius + 2)
            if self.style == "diamond":
                pts = [ (self.pos.x, self.pos.y - self.radius - 1), (self.pos.x + self.radius + 1, self.pos.y), (self.pos.x, self.pos.y + self.radius + 1), (self.pos.x - self.radius - 1, self.pos.y) ]
                pygame.draw.polygon(surface, self.core_color, pts)
            elif self.style == "slash":
                side = self.direction.rotate(90)
                front = self.pos + self.direction * (self.radius + 4)
                back = self.pos - self.direction * (self.radius + 4)
                left = self.pos + side * 4
                right = self.pos - side * 4
                pygame.draw.polygon(surface, self.core_color, [(int(p.x), int(p.y)) for p in [front, left, back, right]])
            else: pygame.draw.circle(surface, self.core_color, self.rect.center, max(3, self.radius // 2))

class Enemy:
    def __init__(self, level, is_elite=False):
        self.is_elite = is_elite
        self.size = 42 if is_elite else 25
        global game_mode
        diff_mult = CHALLENGE_ENEMY_MULTIPLIER if game_mode == CHALLENGE_MODE else 1
        speed_mult = CHALLENGE_ENEMY_SPEED_MULTIPLIER if game_mode == CHALLENGE_MODE else 1
        speed_bonus = min(level * 0.03, 1.2)
        self.speed = ((random.uniform(1.1, 2.2) if is_elite else random.uniform(1.5, 3.5)) + speed_bonus) * speed_mult
        
        base_hp = 5 if is_elite else 1
        self.max_hp = max(1, int((base_hp + level // 6) * diff_mult))
        self.hp, self.damage = self.max_hp, int((35 if is_elite else 20) * diff_mult)
        self.shield = int((level // 4 + (2 if is_elite else 0)) * diff_mult)
        self.max_shield = self.shield
        
        self.exp_drop_chance = 0.85 if is_elite else 0.4
        self.health_drop_chance = 0.12 if is_elite else 0.035
        self.combat_type = "ranged" if random.random() < (0.38 if is_elite else 0.32) else "melee"
        self.attack_range = 420 if is_elite else 320
        self.keep_distance = 260 if is_elite else 205
        self.shoot_cooldown = random.randint(35, 90)
        self.shoot_delay = 85 if is_elite else 115
        
        self.frost_timer, self.anim_idx = 0, 0
        self.facing = pygame.math.Vector2(1, 0)
        
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        world_px, world_py = player.pos.x + global_offset_x, player.pos.y + global_offset_y 
        if edge == 'top': world_x, world_y = world_px + random.randint(-WIDTH, WIDTH), world_py - HEIGHT//2 - self.size
        elif edge == 'bottom': world_x, world_y = world_px + random.randint(-WIDTH, WIDTH), world_py + HEIGHT//2 + self.size
        elif edge == 'left': world_x, world_y = world_px - WIDTH//2 - self.size, world_py + random.randint(-HEIGHT, HEIGHT)
        else: world_x, world_y = world_px + WIDTH//2 + self.size, world_py + random.randint(-HEIGHT, HEIGHT)
        
        world_x = max(self.size, min(MAP_WIDTH - self.size, world_x))
        world_y = max(self.size, min(MAP_HEIGHT - self.size, world_y))
        self.pos = pygame.math.Vector2(world_x - global_offset_x, world_y - global_offset_y)
        self.rect = pygame.Rect(0, 0, self.size, self.size)

    def update(self, target_pos, all_enemies):
        self.anim_idx += 0.15
        current_speed = self.speed * 0.4 if self.frost_timer > 0 else self.speed
        if self.frost_timer > 0: self.frost_timer -= 1

        direction = target_pos - self.pos
        distance = direction.length()
        if distance > 0:
            direction.normalize_ip()
            self.facing = direction.copy()
            
        move_dir = direction
        if self.combat_type == "ranged":
            if distance < self.keep_distance: move_dir = -direction
            elif distance <= self.attack_range: move_dir = pygame.math.Vector2(0, 0)
            if self.shoot_cooldown > 0: self.shoot_cooldown -= 1
            
        self.pos += move_dir * current_speed

        # Boids 群體互斥
        for other in all_enemies:
            if other is not self:
                dist_sq = self.pos.distance_squared_to(other.pos)
                if 0 < dist_sq < self.size**2:
                    dist_val = math.sqrt(dist_sq)
                    push_dir = (self.pos - other.pos) / dist_val
                    self.pos += push_dir * 1.2
            
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def emit_attacks(self, enemy_bullets, target_pos):
        if self.combat_type != "ranged" or self.shoot_cooldown > 0: return
        direction = target_pos - self.pos
        if direction.length_squared() == 0 or direction.length() > self.attack_range + 80: return
        direction.normalize_ip()
        self.facing = direction.copy()
        bullet_color = (255, 120, 45) if self.is_elite else ORANGE
        enemy_bullets.append(EnemyBullet(self.pos, direction, color=bullet_color, core_color=WHITE, style="round"))
        self.shoot_cooldown = self.shoot_delay

    def draw(self, surface):
        anim_key = "enemy_elite" if self.is_elite else "enemy_normal"
        anim_frames = animations.get(anim_key)
        
        if anim_frames:
            img = anim_frames[int(self.anim_idx) % len(anim_frames)]
            if self.facing.x < 0: img = pygame.transform.flip(img, True, False)
            if self.frost_timer > 0:
                img = img.copy(); img.fill((100, 200, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(img, img.get_rect(center=self.rect.center))
            if self.is_elite:
                glow = math.sin(pygame.time.get_ticks() * 0.01) * 6 + 6
                pygame.draw.rect(surface, DARK_PURPLE, self.rect.copy().inflate(glow, glow), 3) 
        else:
            side = self.facing.rotate(90)
            weapon_reach = 34 if self.is_elite else 24
            weapon_offset = self.size * 0.28
            hand = self.pos + self.facing * weapon_offset + side * (self.size * 0.2)
            
            if self.combat_type == "melee":
                hilt = hand + self.facing * (8 if self.is_elite else 5)
                blade_tip = hand + self.facing * (weapon_reach + 16)
                blade_mid = hilt + self.facing * ((weapon_reach + 12) * 0.55)
                b_half = 7 if self.is_elite else 5
                b_color = (80, 240, 255) if self.is_elite else (100, 255, 145)
                pygame.draw.polygon(surface, BLACK, [(p.x, p.y) for p in [blade_tip, blade_mid + side * b_half, hilt + side * max(3, b_half-2), hilt - side * max(3, b_half-2), blade_mid - side * b_half]])
                pygame.draw.polygon(surface, b_color, [(p.x, p.y) for p in [blade_tip - self.facing*2, blade_mid + side * max(3, b_half-2), hilt + side*2, hilt - side*2, blade_mid - side * max(3, b_half-2)]])
            else:
                muzzle = self.pos + self.facing * weapon_reach + side * (self.size * 0.2)
                rear = self.pos + self.facing * (self.size * 0.02) + side * (self.size * 0.2)
                b_half = 5 if self.is_elite else 4
                pygame.draw.polygon(surface, BLACK, [(p.x, p.y) for p in [rear + side * b_half, muzzle + side * max(2, b_half-2), muzzle - side * max(2, b_half-2), rear - side * b_half]])
                pygame.draw.polygon(surface, (205, 210, 215), [(p.x, p.y) for p in [rear + side*(b_half-1), muzzle + side * max(1, b_half-3), muzzle - side * max(1, b_half-3), rear - side*(b_half-1)]])
                barrel_tip = muzzle + self.facing * (7 if self.is_elite else 5)
                pygame.draw.line(surface, BLACK, muzzle, barrel_tip, 5 if self.is_elite else 4)
                pygame.draw.circle(surface, ORANGE if self.is_elite else YELLOW, (int(barrel_tip.x), int(barrel_tip.y)), 3)

            color = (170, 40, 255) if self.is_elite else RED
            if self.frost_timer > 0: color = (100, 200, 255)
            pygame.draw.rect(surface, color, self.rect)
            if self.is_elite:
                pygame.draw.circle(surface, (230, 170, 255), self.rect.center, self.size//2 + 8, 2)
                pygame.draw.rect(surface, WHITE, self.rect, 3)
                
        if self.shield > 0: pygame.draw.rect(surface, BLUE, self.rect.inflate(8, 8), 2)
        if self.hp < self.max_hp or self.shield > 0:
            pygame.draw.rect(surface, GRAY, (self.rect.x, self.rect.y - 8, self.size, 4))
            pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 8, self.size * (self.hp/self.max_hp), 4))
            if self.max_shield > 0:
                pygame.draw.rect(surface, GRAY, (self.rect.x, self.rect.y - 14, self.size, 4))
                pygame.draw.rect(surface, BLUE, (self.rect.x, self.rect.y - 14, self.size * (self.shield/self.max_shield), 4))

class Boss:
    def __init__(self, boss_type, level=5):
        self.b_type = boss_type
        
        world_x, world_y = player.pos.x + global_offset_x, player.pos.y + global_offset_y - HEIGHT//2 - 100
        self.pos = pygame.math.Vector2(world_x - global_offset_x, world_y - global_offset_y)
        
        self.size = 65
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.spawn_level = level
        global game_mode
        diff_mult = CHALLENGE_ENEMY_MULTIPLIER if game_mode == CHALLENGE_MODE else 1
        
        self.state = "ENTRANCE"
        self.state_timer, self.frost_timer, self.defeat_timer, self.anim_idx = 0, 0, 0, 0
        self.entrance_duration = 120  
        self.play_shoot_sound = False 
        
        if self.b_type == "YELLOW":
            self.max_hp = int((1000 + level*300) * diff_mult)
            self.color, self.speed, self.name = YELLOW, 3.0 * diff_mult, "幾何守衛"
        elif self.b_type == "RED":
            self.max_hp = int((1500 + level*300) * diff_mult)
            self.color, self.speed, self.name = RED, 2.5 * diff_mult, "鮮血狂戰士"
            self.aim_target, self.dash_dir, self.spin_angle = pygame.math.Vector2(0,0), pygame.math.Vector2(1,0), 0
        elif self.b_type == "PURPLE":
            self.max_hp = int((800 + level*300) * diff_mult)
            self.color, self.speed, self.name = PURPLE, 2.0 * diff_mult, "虛空召喚師"
            
        self.hp = self.max_hp
        self.collision_damage = int(40 * diff_mult)

    def update(self, player_pos, bullets):
        self.state_timer += 1; self.anim_idx += 0.1
        current_speed = self.speed * 0.5 if self.frost_timer > 0 else self.speed
        if self.frost_timer > 0: self.frost_timer -= 1
        self.play_shoot_sound = False

        if self.state == "ENTRANCE":
            progress = min(1, self.state_timer / self.entrance_duration)
            self.pos.y += 1.5 
            if self.b_type == "YELLOW": self.color = (100 + 155*progress, 100 + 155*progress, 0)
            elif self.b_type == "RED": self.color = (100 + 155*progress, 0, 0)
            elif self.b_type == "PURPLE": self.color = (int(100+100*progress), 0, int(100+155*progress))
            if self.state_timer >= self.entrance_duration:
                self.state = "EVADE" if self.b_type == "YELLOW" else ("CHASE" if self.b_type == "RED" else "FLEE")
                self.state_timer = 0
                
        elif self.state == "DEFEAT":
            self.defeat_timer += 1
            self.pos.y -= 1
            self.pos.x += math.sin(self.defeat_timer * 0.2) * 1.5

        elif self.b_type == "YELLOW":
            if self.state == "EVADE":
                direction = player_pos - self.pos
                if direction.length() > 0: direction.normalize_ip()
                else: direction = pygame.math.Vector2(1,0)
                tangent = pygame.math.Vector2(-direction.y, direction.x) 
                
                dodged = False
                for b in bullets:
                    if self.pos.distance_to(b.pos) < 150:
                        flee_dir = self.pos - b.pos
                        if flee_dir.length() > 0: flee_dir.normalize_ip()
                        self.pos += flee_dir * (current_speed * 1.8)
                        dodged = True; break 
                        
                if not dodged:
                    self.pos += tangent * current_speed
                    p_dist = self.pos.distance_to(player_pos)
                    if p_dist > 250: self.pos += direction * current_speed
                    elif p_dist < 150: self.pos -= direction * current_speed

                if self.state_timer > 120: self.state = "CHARGE"; self.state_timer = 0
                    
            elif self.state == "CHARGE":
                if self.state_timer > 60: self.state = "SHOOT"; self.state_timer = 0

        elif self.b_type == "RED":
            if self.state == "CHASE":
                direction = player_pos - self.pos
                if direction.length() > 0:
                    direction.normalize_ip()
                    self.pos += direction * current_speed
                if self.state_timer > 150: self.state = "WARN"; self.state_timer = 0
            elif self.state == "WARN":
                self.aim_target = player_pos.copy()
                if self.state_timer > 45:
                    self.state, self.state_timer = "DASH", 0
                    self.dash_dir = self.aim_target - self.pos
                    if self.dash_dir.length() > 0: self.dash_dir.normalize_ip()
                    else: self.dash_dir = pygame.math.Vector2(1,0)
                    self.play_shoot_sound = True 
            elif self.state == "DASH":
                self.pos += self.dash_dir * (current_speed * 6)
                if self.state_timer % 6 == 0:
                    side1 = self.dash_dir.rotate(90)
                    side2 = self.dash_dir.rotate(-90)
                    global enemy_bullets
                    enemy_bullets.append(EnemyBullet(self.pos, side1, color=(0, 210, 255), core_color=WHITE, style="slash"))
                    enemy_bullets.append(EnemyBullet(self.pos, side2, color=(0, 210, 255), core_color=WHITE, style="slash"))
                if self.state_timer > 25 or self.pos.distance_to(self.aim_target) < 30:
                    self.state = "RECOVER"; self.state_timer = 0
            elif self.state == "RECOVER":
                self.spin_angle += 0.15
                if self.state_timer > 120: self.state = "CHASE"; self.state_timer = 0

        elif self.b_type == "PURPLE":
            if self.state == "FLEE":
                dist = self.pos.distance_to(player_pos)
                direction = player_pos - self.pos
                if direction.length() > 0: direction.normalize_ip()
                else: direction = pygame.math.Vector2(1,0)
                    
                if dist < 300: self.pos -= direction * current_speed 
                else:
                    tangent = pygame.math.Vector2(-direction.y, direction.x)
                    self.pos += tangent * current_speed 
                
                if self.state_timer > 180: self.state = "SUMMON"; self.state_timer = 0
            elif self.state == "SUMMON":
                if self.state_timer == 45:
                    for _ in range(3):
                        e = Enemy(level=self.spawn_level, is_elite=True)
                        e.pos = self.pos + pygame.math.Vector2(random.randint(-70,70), random.randint(-70,70))
                        global enemies; enemies.append(e)
                    self.play_shoot_sound = True
                if self.state_timer > 90: self.state = "FLEE"; self.state_timer = 0

        world_x = self.pos.x + global_offset_x
        world_y = self.pos.y + global_offset_y
        world_x = max(self.size, min(MAP_WIDTH - self.size, world_x))
        world_y = max(self.size, min(MAP_HEIGHT - self.size, world_y))
        self.pos.x = world_x - global_offset_x
        self.pos.y = world_y - global_offset_y
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def can_take_damage(self):
        if self.state in ["ENTRANCE", "DEFEAT"]: return False
        if self.b_type == "YELLOW" and self.state == "EVADE": return False
        if self.b_type == "RED" and self.state == "DASH": return False
        return True

    def emit_attacks(self, enemy_bullets):
        if self.b_type == "YELLOW" and self.state == "SHOOT":
            for i in range(12):
                angle = math.radians(i * 30)
                dir_vec = pygame.math.Vector2(math.cos(angle), math.sin(angle))
                enemy_bullets.append(EnemyBullet(self.pos, dir_vec))
            if self.spawn_level >= 10:
                for i in range(12):
                    angle = math.radians(i * 30 + 15)
                    dir_vec = pygame.math.Vector2(math.cos(angle), math.sin(angle))
                    enemy_bullets.append(EnemyBullet(self.pos, dir_vec))
            self.state = "EVADE"
            play_sound("shoot")
        elif self.b_type == "RED" and self.state == "RECOVER":
            if self.state_timer % 10 == 0:
                for i in range(6):
                    angle = self.spin_angle + i * (math.pi*2/6)
                    enemy_bullets.append(EnemyBullet(self.pos, pygame.math.Vector2(math.cos(angle), math.sin(angle)), color=PURPLE, style="round"))

    def get_intro_title(self): return f"✦ {self.name} 降臨 ✦"

    def get_state_message(self):
        if self.b_type == "YELLOW":
            if self.state == "EVADE": return "閃避階段 - 無敵護盾 (黃色)", YELLOW
            elif self.state == "CHARGE": return "蓄力階段 - 可攻擊 (橙紅色)", ORANGE
            return "發射階段 - 可攻擊", RED
        elif self.b_type == "RED":
            if self.state == "WARN": return "鎖定階段 - 即將衝刺 (金色)", YELLOW
            elif self.state == "DASH": return "突擊階段 - 高速衝刺", RED
            elif self.state == "RECOVER": return "冷卻階段 - 原地旋轉彈幕", PURPLE
            return "追擊階段", WHITE
        elif self.b_type == "PURPLE":
            if self.state == "SUMMON": return "召喚階段 - 召喚菁英怪", PURPLE
            return "逃跑階段", WHITE
        return "BOSS 交戰中", WHITE

    def draw(self, surface):
        if self.state == "ENTRANCE":
            pulse = abs(math.sin(self.state_timer * 0.1))
            current_size = int(self.size * (0.8 + pulse * 0.4))
            for i in range(3):
                ring_size = current_size // 2 + 20 + i * 15
                alpha_val = int(200 * (1 - i/3) * (1 - pulse))
                if alpha_val > 0: pygame.draw.circle(surface, WHITE, self.rect.center, ring_size, 2)
            pygame.draw.rect(surface, self.color, pygame.Rect(0, 0, current_size, current_size).move(self.rect.centerx - current_size//2, self.rect.centery - current_size//2))
            pygame.draw.circle(surface, WHITE, self.rect.center, current_size//2 + 15, 3)
            for i in range(8):
                angle = (self.state_timer * 0.05 + i * math.pi / 4)
                px = self.rect.centerx + math.cos(angle) * (self.size + 30)
                py = self.rect.centery + math.sin(angle) * (self.size + 30)
                pygame.draw.circle(surface, YELLOW, (int(px), int(py)), 3)
            return
            
        elif self.state == "DEFEAT":
            progress = min(1, self.defeat_timer / 60)
            for i in range(5): pygame.draw.circle(surface, (255, 180, 0), self.rect.center, int(self.size + progress * 120 + i * 12), 3)
            core_size = max(1, int(self.size * (1 - progress * 0.7)))
            pygame.draw.rect(surface, (255, 100, 0), pygame.Rect(0, 0, core_size, core_size).move(self.rect.centerx - core_size//2, self.rect.centery - core_size//2))
            burst = int(progress * 10)
            for i in range(burst):
                angle = i * (math.pi * 2 / max(1, burst)) + self.defeat_timer * 0.3
                px = self.rect.centerx + math.cos(angle) * (self.size + 30 + progress * 80)
                py = self.rect.centery + math.sin(angle) * (self.size + 30 + progress * 80)
                pygame.draw.circle(surface, RED, (int(px), int(py)), 4)
            return

        anim_key = "boss_" + self.b_type
        anim_frames = animations.get(anim_key)
        
        if anim_frames:
            img = anim_frames[int(self.anim_idx) % len(anim_frames)]
            surface.blit(img, img.get_rect(center=self.rect.center))
        else:
            pygame.draw.rect(surface, (100, 200, 255) if self.frost_timer > 0 else self.color, self.rect)
        
        if self.b_type == "YELLOW" and self.state == "EVADE": pygame.draw.circle(surface, WHITE, self.rect.center, int(self.size/2) + 15, 3)
        elif self.b_type == "YELLOW" and self.state == "CHARGE": pygame.draw.circle(surface, RED, self.rect.center, int(self.size/2) + max(0, 30 - int(self.state_timer / 2)), 2)
        elif self.b_type == "RED" and self.state == "WARN": pygame.draw.line(surface, RED, self.rect.center, (int(self.aim_target.x), int(self.aim_target.y)), max(1, int(self.state_timer / 8)))
        elif self.b_type == "PURPLE" and self.state == "SUMMON": pygame.draw.circle(surface, DARK_PURPLE, self.rect.center, int(self.size/2) + min(60, self.state_timer), 3)

class Particle:
    def __init__(self, x, y, color):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(random.uniform(-6, 6), random.uniform(-6, 6))
        self.timer, self.size, self.color = random.randint(15, 30), random.randint(4, 8), color
    def update(self):
        self.pos += self.vel; self.timer -= 1; self.size = max(0, self.size - 0.25)
    def draw(self, surface):
        if self.size > 0: pygame.draw.rect(surface, self.color, (int(self.pos.x), int(self.pos.y), int(self.size), int(self.size)))

class DamageText:
    def __init__(self, x, y, damage, color=WHITE):
        self.pos = pygame.math.Vector2(x, y)
        self.damage, self.color = int(damage), color
        self.timer, self.vel_y, self.offset_x = 40, -1.5, random.randint(-15, 15)
    def update(self):
        self.pos.y += self.vel_y; self.timer -= 1
        self.alpha = max(0, int((self.timer / 40) * 255))
    def draw(self, surface):
        if self.timer > 0:
            txt_surf = font.render(f"-{self.damage}", True, self.color)
            alpha_surf = pygame.Surface(txt_surf.get_size(), pygame.SRCALPHA)
            alpha_surf.fill((255, 255, 255, self.alpha))
            txt_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(txt_surf, (int(self.pos.x + self.offset_x), int(self.pos.y)))

class DropItem:
    def __init__(self, x, y, item_type="EXP", amount=None):
        self.pos = pygame.math.Vector2(x, y)
        self.item_type = item_type
        self.rect = pygame.Rect(0, 0, 14, 14)
        self.anim_offset = random.random() * 10
        self.amount = amount if amount else (35 if item_type == "EXP" else 25)
        
    def update(self, p_pos, mag_rad):
        dist = self.pos.distance_to(p_pos)
        if dist < mag_rad and dist > 0:
            self.pos += ((p_pos - self.pos) / dist) * 8
        self.rect.center = (round(self.pos.x), round(self.pos.y))
        
    def draw(self, surface):
        img_key = f"drop_{self.item_type}"
        img = images.get(img_key)
        float_y = self.pos.y + math.sin(pygame.time.get_ticks()*0.005 + self.anim_offset) * 3
        
        if img: surface.blit(img, img.get_rect(center=(int(self.pos.x), int(float_y))))
        else:
            if self.item_type == "EXP": pygame.draw.polygon(surface, EXP_COLOR,[(self.pos.x, float_y-6), (self.pos.x+6, float_y), (self.pos.x, float_y+6), (self.pos.x-6, float_y)])
            elif self.item_type == "HP": pygame.draw.rect(surface, HP_COLOR, (self.pos.x-6, float_y-2, 12, 4)); pygame.draw.rect(surface, HP_COLOR, (self.pos.x-2, float_y-6, 4, 12))
            elif self.item_type == "SHIELD": pygame.draw.circle(surface, SHIELD_COLOR, (int(self.pos.x), int(float_y)), 6)

# ==========================================
# 4. 遊戲狀態與系統選單
# ==========================================
def refresh_player_shield_max(fill_gain=False):
    old_max = max(1, player.max_shield)
    old_ratio = player.shield / old_max
    player.max_shield = max(1, int(player.max_hp * 0.2))
    if fill_gain: player.shield = min(player.max_shield, player.shield + max(0, player.max_shield - old_max))
    else: player.shield = min(player.max_shield, player.max_shield * old_ratio)

def apply_upgrade(choice):
    global game_state, selected_upgrade_position
    if choice == 0: player.max_hp += 50; player.hp += 50; refresh_player_shield_max(fill_gain=True)
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
    elif choice == 15: player.max_hp += 25; player.max_stamina += 15; player.hp += 25; player.stamina += 15; refresh_player_shield_max(fill_gain=True)
    elif choice == 16: player.magnet_radius += 25; player.stamina_regen += 0.15
    elif choice == 17: player.extra_same_path_bullets += 1
    elif choice == 18: player.guidance_level += 1
    elif choice == 19: player.aura_level += 1
    elif choice == 20: player.regen_level += 1
    elif choice == 21: player.exp_multiplier += 0.2
    elif choice == 22: player.pistol_mag_size += 10; player.sniper_mag_size += 2; player.pistol_ammo += 10; player.sniper_ammo += 2
    elif choice == 23: player.reload_duration = max(35, player.reload_duration - 18)
    add_chosen_upgrade(choice)
    current_upgrade_choices.clear(); selected_upgrade_position = None
    switch_to_english_input()
    game_state = "PLAYING"             

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
    {"title": "擴容彈匣", "desc": ["挑戰限定卡牌", "步槍+10 狙擊+2"], "type": "attack", "weight": 4, "challenge_only": True},
    {"title": "快拆彈匣", "desc": ["挑戰限定卡牌", "換彈時間縮短"], "type": "support", "weight": 3, "challenge_only": True}
]

cards =[pygame.Rect(0, 0, 220, 280), pygame.Rect(0, 0, 220, 280), pygame.Rect(0, 0, 220, 280)]
confirm_upgrade_button = pygame.Rect(0, 0, 220, 60)
current_upgrade_choices =[]
selected_upgrade_position = None
chosen_upgrades =[]
pause_upgrade_scroll = 0

start_button = pygame.Rect(0, 0, 200, 60)
normal_button = pygame.Rect(0, 0, 380, 230)
challenge_button = pygame.Rect(0, 0, 380, 230)
difficulty_back_button = pygame.Rect(0, 0, 220, 55)
changelog_button = pygame.Rect(0, 0, 200, 60)
changelog_close_button = pygame.Rect(0, 0, 200, 55)
restart_button = pygame.Rect(0, 0, 200, 60)
menu_button = pygame.Rect(0, 0, 200, 60)
exit_button = pygame.Rect(0, 0, 200, 60)

CHANGELOG =[
    "v1.4 終極完全體",
    "- 將 18 種強化與開放世界整合進 B4 動態貼圖引擎",
    "- 融合 12 種不同特性的武器與右鍵大絕招系統",
    "- 統一所有底層座標為 Vector2",
    "v1.367",
    "- 小兵與精英小兵分為近戰和遠程兩類",
    "v1.315",
    "- 挑戰模式敵人強度提升為 1.75 倍，並啟用彈匣與換彈系統",
    "v1.185",
    "- Boss 出場動畫期間會暫停遊戲並顯示提示語",
    "- 新增裂空突擊者 Boss：衝向玩家並向兩側發射子彈",
]

show_changelog, changelog_scroll, changelog_content_surface, changelog_max_scroll = False, 0, None, 0

def choose_upgrade_cards():
    global current_upgrade_choices, selected_upgrade_position
    card_count = min(3, len(upgrade_options))
    available = [i for i, option in enumerate(upgrade_options) if game_mode == CHALLENGE_MODE or not option.get("challenge_only")]
    card_count = min(card_count, len(available))
    current_upgrade_choices =[]
    for _ in range(card_count):
        total_weight = sum(upgrade_options[i].get("weight", 1) for i in available)
        pick = random.uniform(0, total_weight)
        running_weight = 0
        for i in available:
            running_weight += upgrade_options[i].get("weight", 1)
            if pick <= running_weight:
                current_upgrade_choices.append(i); available.remove(i); break
    selected_upgrade_position = None

def add_chosen_upgrade(choice):
    title = upgrade_options[choice]["title"]
    for upgrade in chosen_upgrades:
        if upgrade["title"] == title:
            upgrade["count"] += 1; return
    chosen_upgrades.append({"title": title, "count": 1})

def wrap_text(text, text_font, max_width):
    lines =[]; current = ""
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
    content_lines =[]
    for line in CHANGELOG:
        color = YELLOW if line.startswith("v") else WHITE
        for wrapped_line in wrap_text(line, font, content_width - 20): content_lines.append((wrapped_line, color))
        content_lines.append(("", WHITE))
    surface_height = max(content_height, len(content_lines) * 34 + 10)
    changelog_content_surface = pygame.Surface((content_width, surface_height), pygame.SRCALPHA)
    for i, (line, color) in enumerate(content_lines):
        if line: changelog_content_surface.blit(font.render(line, True, color), (0, 6 + i * 34))
    changelog_max_scroll = max(0, surface_height - content_height)

def draw_changelog_popup(surface):
    popup = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 250, 700, 500)
    panel = pygame.Surface((popup.width, popup.height), pygame.SRCALPHA)
    panel.fill((18, 20, 32, 235)); surface.blit(panel, popup.topleft)
    pygame.draw.rect(surface, WHITE, popup, 3, border_radius=12)

    title = large_font.render("更新日誌", True, YELLOW)
    surface.blit(title, (popup.centerx - title.get_width()//2, popup.y + 25))

    content_rect = pygame.Rect(popup.x + 40, popup.y + 90, popup.width - 80, popup.height - 180)
    if changelog_content_surface is None: rebuild_changelog_cache(content_rect.width, content_rect.height)

    scroll_y = min(changelog_scroll, changelog_max_scroll)
    surface.blit(changelog_content_surface, content_rect.topleft, pygame.Rect(0, scroll_y, content_rect.width, content_rect.height))
    pygame.draw.rect(surface, GRAY, content_rect, 1)

    if changelog_max_scroll > 0:
        bar_h = max(40, int(content_rect.height * content_rect.height / changelog_content_surface.get_height()))
        bar_y = content_rect.y + int((content_rect.height - bar_h) * (scroll_y / changelog_max_scroll))
        pygame.draw.rect(surface, GRAY, (content_rect.right + 8, content_rect.y, 8, content_rect.height), border_radius=4)
        pygame.draw.rect(surface, YELLOW, (content_rect.right + 8, bar_y, 8, bar_h), border_radius=4)

    changelog_close_button.center = (popup.centerx, popup.bottom - 40)
    close_color = RED if changelog_close_button.collidepoint(pygame.mouse.get_pos()) else (150, 50, 50)
    pygame.draw.rect(surface, close_color, changelog_close_button, border_radius=10); pygame.draw.rect(surface, WHITE, changelog_close_button, 3, border_radius=10)
    close_txt = font.render("關閉", True, WHITE)
    surface.blit(close_txt, (changelog_close_button.centerx - close_txt.get_width()//2, changelog_close_button.centery - close_txt.get_height()//2))

def draw_pause_upgrade_log(surface):
    panel_rect = pygame.Rect(WIDTH//2 - 330, HEIGHT//2 + 235, 660, 260)
    panel = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    panel.fill((18, 20, 30, 205)); surface.blit(panel, panel_rect.topleft)
    pygame.draw.rect(surface, WHITE, panel_rect, 2, border_radius=8)

    title = small_font.render("本局強化紀錄（滑鼠滾輪上下瀏覽）", True, YELLOW)
    surface.blit(title, (panel_rect.x + 16, panel_rect.y + 12))
    content_rect = pygame.Rect(panel_rect.x + 16, panel_rect.y + 44, panel_rect.width - 42, panel_rect.height - 58)

    rows =[]
    for upgrade in chosen_upgrades:
        option = next((opt for opt in upgrade_options if opt["title"] == upgrade["title"]), None)
        desc = " / ".join(option["desc"]) if option else ""
        count = f" x{upgrade['count']}" if upgrade["count"] > 1 else ""
        rows.append((f"{upgrade['title']}{count}", desc))

    if not rows:
        surface.blit(small_font.render("尚未選擇任何強化", True, GRAY), (content_rect.x, content_rect.y + 8))
        return

    row_h = 54
    content_height = max(content_rect.height, len(rows) * row_h)
    max_scroll = max(0, content_height - content_rect.height)
    scroll_y = min(pause_upgrade_scroll, max_scroll)
    content_surface = pygame.Surface((content_rect.width, content_height), pygame.SRCALPHA)

    for i, (name, desc) in enumerate(rows):
        y = i * row_h
        content_surface.blit(small_font.render(name, True, WHITE), (0, y))
        for j, line in enumerate(wrap_text(desc, tiny_font, content_rect.width - 20)):
            content_surface.blit(tiny_font.render(line, True, YELLOW), (18, y + 25 + j * 20))

    surface.blit(content_surface, content_rect.topleft, pygame.Rect(0, scroll_y, content_rect.width, content_rect.height))
    if max_scroll > 0:
        bar_h = max(36, int(content_rect.height * content_rect.height / content_height))
        bar_y = content_rect.y + int((content_rect.height - bar_h) * (scroll_y / max_scroll))
        pygame.draw.rect(surface, GRAY, (content_rect.right + 8, content_rect.y, 7, content_rect.height), border_radius=4)
        pygame.draw.rect(surface, YELLOW, (content_rect.right + 8, bar_y, 7, bar_h), border_radius=4)

def draw_upgrade_summary(surface, x, y, max_items=6, title="已選強化"):
    panel_width, row_height = 260, 28
    hidden_count = max(0, len(chosen_upgrades) - max_items)
    row_count = max(1, min(len(chosen_upgrades), max_items))
    panel_height = 44 + row_count * row_height + (row_height if hidden_count else 0)
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((18, 20, 30, 185)); surface.blit(panel, (x, y))
    pygame.draw.rect(surface, WHITE, (x, y, panel_width, panel_height), 2, border_radius=8)

    title_label = f"{title} ({sum(u['count'] for u in chosen_upgrades)})" if chosen_upgrades else title
    surface.blit(small_font.render(title_label, True, YELLOW), (x + 14, y + 10))

    if not chosen_upgrades:
        surface.blit(small_font.render("尚未選擇", True, GRAY), (x + 14, y + 42))
        return

    visible_upgrades = chosen_upgrades[-max_items:]
    for i, upgrade in enumerate(visible_upgrades):
        suffix = f" x{upgrade['count']}" if upgrade["count"] > 1 else ""
        surface.blit(small_font.render(f"{upgrade['title']}{suffix}", True, WHITE), (x + 14, y + 42 + i * row_height))

    if hidden_count:
        surface.blit(small_font.render(f"還有 {hidden_count} 種...", True, GRAY), (x + 14, y + 42 + len(visible_upgrades) * row_height))

def reset_game(initial_state="PLAYING", mode=None):
    global player, bullets, enemy_bullets, enemies, particles, items, trails, damage_texts
    global boss, boss_active, boss_defeated, next_boss_level, boss_spawn_count, game_state, game_mode
    global current_upgrade_choices, selected_upgrade_position, chosen_upgrades, show_changelog, changelog_scroll
    global changelog_content_surface, changelog_max_scroll, pause_upgrade_scroll, global_offset_x, global_offset_y
    global shoot_cooldown, key_buffer, boss_warning_timer
    
    if mode is not None: game_mode = mode
    player = Player()
    bullets, enemy_bullets, enemies, particles, items, trails, damage_texts = [], [], [], [], [], [],[]
    boss, boss_active, boss_defeated, next_boss_level, boss_spawn_count = None, False, False, 5, 0
    current_upgrade_choices, selected_upgrade_position, chosen_upgrades = [], None,[]
    show_changelog, changelog_scroll, changelog_content_surface, changelog_max_scroll, pause_upgrade_scroll = False, 0, None, 0, 0
    global_offset_x, global_offset_y, shoot_cooldown, key_buffer, boss_warning_timer = 0, 0, 0,[], 0
    
    stop_sound("boss_bgm")
    if initial_state == "PLAYING":
        try: pygame.mixer.music.play(-1)
        except: pass
    game_state = initial_state
    pygame.time.set_timer(SPAWN_ENEMY_EVENT, NORMAL_SPAWN_INTERVAL if game_mode == NORMAL_MODE else CHALLENGE_SPAWN_INTERVAL)

reset_game("MENU")
SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY_EVENT, 600)
dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
dim_surface.fill((0, 0, 0, 180))

# ==========================================
# 5. 遊戲主迴圈
# ==========================================
running = True
while running:
    # --- 動態調整 UI 位置 ---
    start_button.center = (WIDTH//2, HEIGHT//2 + 20)
    changelog_button.center = (WIDTH//2, HEIGHT//2 + 95)
    exit_button.center = (WIDTH//2, HEIGHT//2 + 170)
    
    normal_button.center = (WIDTH//2 - 220, HEIGHT//2)
    challenge_button.center = (WIDTH//2 + 220, HEIGHT//2)
    difficulty_back_button.center = (WIDTH//2, HEIGHT//2 + 245)

    cards[0].center = (WIDTH//2 - 250, HEIGHT//2)
    cards[1].center = (WIDTH//2, HEIGHT//2)
    cards[2].center = (WIDTH//2 + 250, HEIGHT//2)
    confirm_upgrade_button.center = (WIDTH//2, HEIGHT//2 + 200)

    restart_button.center = (WIDTH//2 - 120, HEIGHT//2 + 100)
    menu_button.center = (WIDTH//2 + 120, HEIGHT//2 + 100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if WINDOW_FOCUS_GAINED is not None and event.type == WINDOW_FOCUS_GAINED:
            switch_to_english_input()
        if game_state == "MENU" and show_changelog and event.type == pygame.MOUSEWHEEL:
            changelog_scroll = max(0, min(changelog_max_scroll, changelog_scroll - event.y * 55))
        if game_state == "PAUSED" and event.type == pygame.MOUSEWHEEL:
            pause_upgrade_scroll = max(0, pause_upgrade_scroll - event.y * 45)
        
        if event.type == pygame.VIDEORESIZE:
            if not fullscreen_mode:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if game_state == "PLAYING": game_state = "PAUSED"
            elif game_state == "PAUSED":
                switch_to_english_input()
                game_state = "PLAYING"
            elif game_state == "DIFFICULTY": game_state = "MENU"
            
        if game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: reset_game("PLAYING", game_mode); switch_to_english_input()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_button.collidepoint(event.pos): reset_game("PLAYING", game_mode); switch_to_english_input()
                elif menu_button.collidepoint(event.pos): reset_game("MENU", NORMAL_MODE)
                
        elif game_state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_changelog:
                    if changelog_close_button.collidepoint(event.pos): show_changelog = False
                elif start_button.collidepoint(event.pos): game_state = "DIFFICULTY"
                elif changelog_button.collidepoint(event.pos):
                    show_changelog, changelog_scroll = True, 0
                    if changelog_content_surface is None: rebuild_changelog_cache(720, 455)
                elif exit_button.collidepoint(event.pos): running = False
                
        elif game_state == "DIFFICULTY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if normal_button.collidepoint(event.pos): reset_game("PLAYING", NORMAL_MODE); switch_to_english_input()
                elif challenge_button.collidepoint(event.pos): reset_game("PLAYING", CHALLENGE_MODE); switch_to_english_input()
                elif difficulty_back_button.collidepoint(event.pos): game_state = "MENU"
                
        elif game_state == "PAUSED":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 70, 220, 60).collidepoint(event.pos): switch_to_english_input(); game_state = "PLAYING"
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 70, 220, 60).collidepoint(event.pos): reset_game("MENU", NORMAL_MODE)
                elif pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 150, 220, 60).collidepoint(event.pos): reset_game("PLAYING", game_mode); switch_to_english_input()
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 150, 220, 60).collidepoint(event.pos): running = False
                
        elif game_state == "LEVEL_UP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected_upgrade_position is not None and confirm_upgrade_button.collidepoint(event.pos):
                    apply_upgrade(current_upgrade_choices[selected_upgrade_position])
                else:
                    for i, card in enumerate(cards):
                        if i < len(current_upgrade_choices) and card.collidepoint(event.pos):
                            selected_upgrade_position = i; break
                            
        elif game_state == "PLAYING":
            if event.type == SPAWN_ENEMY_EVENT: 
                if not boss_active:
                    elite_chance = min(0.03 + player.level * 0.006, 0.15)
                    enemies.append(Enemy(level=player.level, is_elite=random.random() < elite_chance))
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen_mode = not fullscreen_mode
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if fullscreen_mode else pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                    WIDTH, HEIGHT = screen.get_size()
                
                key_buffer.append(event.key)
                if len(key_buffer) > len(CHEAT_CODE): key_buffer.pop(0) 
                if key_buffer == CHEAT_CODE:
                    player.god_mode = not player.god_mode
                    play_sound("levelup"); key_buffer =[] 
                
                if event.key == pygame.K_e:
                    player.current_weapon_idx = (player.current_weapon_idx + 1) % len(player.weapons)
                    play_sound("exp")
                if event.key == pygame.K_r:
                    player.start_reload()

    if game_state == "PLAYING":
        if player.level >= next_boss_level and not boss_active:
            boss_spawn_count += 1
            boss = Boss(random.choice(["YELLOW", "RED", "PURPLE"]), next_boss_level)
            boss_active, boss_warning_timer, boss_defeated = True, 120, False
            enemies.clear()
            try: pygame.mixer.music.stop()
            except: pass
            play_sound("boss_bgm", loop=-1) 

        boss_entrance_pause = boss_active and boss and boss.state == "ENTRANCE"

        if boss_entrance_pause:
            boss.update(player.pos, bullets)
            if boss_warning_timer > 0: boss_warning_timer -= 1
            
            # --- 繪製出場動畫凍結畫面 ---
            screen.fill(BLACK)
            draw_map_bounds(screen)
            for i in items: i.draw(screen)
            for p in particles: p.draw(screen)
            for b in bullets: b.draw(screen)
            for eb in enemy_bullets: eb.draw(screen) 
            for e in enemies: e.draw(screen)
            for t in trails: t.draw(screen)
            if boss_active: boss.draw(screen)
            player.draw(screen, player.weapons[player.current_weapon_idx])
            
            screen.blit(dim_surface, (0, 0))
            title = large_font.render(boss.get_intro_title(), True, YELLOW)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 190))
        
            progress = min(1, boss.state_timer / boss.entrance_duration)
            bar_rect = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 - 120, 440, 18)
            pygame.draw.rect(screen, GRAY, bar_rect, border_radius=8)
            pygame.draw.rect(screen, RED, (bar_rect.x, bar_rect.y, int(bar_rect.width * progress), bar_rect.height), border_radius=8)
            pygame.draw.rect(screen, WHITE, bar_rect, 2, border_radius=8)
        
            warning_lines = [
                "⚠️ BOSS 出現！時間暫停中",
                "準備迎接史詩級的挑戰！",
                "觀察型態轉換，把握攻擊時機！"
            ]
            for i, line in enumerate(warning_lines):
                color = RED if i == 0 else WHITE
                text = font.render(line, True, color)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 75 + i * 42))
        
            pygame.display.flip()
            clock.tick(FPS)
            continue

        mouse_btns, (mouse_x, mouse_y) = pygame.mouse.get_pressed(), pygame.mouse.get_pos()
        current_wep = player.weapons[player.current_weapon_idx]

        # 玩家左鍵普通射擊
        if mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing and player.can_fire_current_weapon():
            world_mouse = pygame.math.Vector2(mouse_x + global_offset_x, mouse_y + global_offset_y)
            is_piercing = current_wep.bullet_type in ["piercing", "laser", "cannon", "flamethrower"]
            base_dir = world_mouse - player.pos
            if base_dir.length() > 0: base_dir.normalize_ip()
            
            current_spread = player.bullet_spread * (0.35 if is_piercing else 1)
            start_angle = -(player.bullet_count - 1) * current_spread / 2
            
            for c in range(player.bullet_count):
                angle_offset = start_angle + c * current_spread
                shot_dir = base_dir.rotate(angle_offset)
                
                same_path_count = 1 + player.extra_same_path_bullets
                for j in range(same_path_count):
                    spawn_offset = shot_dir * (j * 18)
                    if current_wep.bullet_type == "shotgun":
                        for i in range(-2, 3):
                            final_dir = shot_dir.rotate(i * 12)
                            target_pos = player.pos + final_dir * 100 + spawn_offset
                            bullets.append(Bullet(player.pos + spawn_offset, target_pos, current_wep, player.guidance_level))
                    elif current_wep.bullet_type == "flamethrower":
                        target_pos = player.pos + shot_dir * 100 + spawn_offset
                        target_pos.x += random.randint(-40, 40); target_pos.y += random.randint(-40, 40)
                        bullets.append(Bullet(player.pos + spawn_offset, target_pos, current_wep, player.guidance_level))
                    else:
                        target_pos = player.pos + shot_dir * 100 + spawn_offset
                        bullets.append(Bullet(player.pos + spawn_offset, target_pos, current_wep, player.guidance_level))
            
            shoot_cooldown = current_wep.shoot_delay
            player.consume_current_ammo()
            play_sound(current_wep.sound_name)
            
        # 玩家右鍵大絕招
        if mouse_btns[2] and player.skill_cd <= 0 and player.energy >= player.skill_cost and not player.is_dashing:
            player.energy -= player.skill_cost; player.skill_cd = player.skill_max_cd; play_sound("shoot_cannon") 
            temp_wep = Weapon("大絕", 0, "piercing", 50) 
            for i in range(16):
                angle = math.radians(i * (360 / 16))
                target_pos = player.pos + pygame.math.Vector2(math.cos(angle)*100, math.sin(angle)*100)
                bullets.append(Bullet(player.pos, target_pos, temp_wep))

        if shoot_cooldown > 0: shoot_cooldown -= 1
        player.update()
        
        # 奈米恢復
        if player.regen_level > 0 and player.hp < player.max_hp:
            player.regen_progress += 0.01 * player.regen_level
            if player.regen_progress >= 1:
                heal = int(player.regen_progress)
                player.hp = min(player.max_hp, player.hp + heal)
                player.regen_progress -= heal
        else: player.regen_progress = 0

        if player.is_dashing: trails.append(DashTrail(player.pos, player.size))
        for t in trails[::-1]:
            t.update(); 
            if t.life <= 0: trails.remove(t)
            
        for b in bullets[::-1]:
            b.update()
            if getattr(b, 'explode', False):
                play_sound("shoot_cannon") 
                for _ in range(30): particles.append(Particle(b.pos.x, b.pos.y, ORANGE))
                for e in enemies[::-1]:
                    if b.pos.distance_to(e.pos) < 120: 
                        shield_damage = min(e.shield, b.damage)
                        e.shield -= shield_damage
                        e.hp -= (b.damage - shield_damage)
                        damage_texts.append(DamageText(e.pos.x, e.pos.y - 15, b.damage, YELLOW if b.damage >= 30 else WHITE))
                        if e.hp <= 0: 
                            if random.random() < e.exp_drop_chance: items.append(DropItem(e.pos.x, e.pos.y, "EXP"))
                            enemies.remove(e)
                if boss_active and b.pos.distance_to(boss.pos) < 150: 
                    boss.hp -= b.damage
                    damage_texts.append(DamageText(boss.pos.x, boss.pos.y - 30, b.damage, YELLOW if b.damage >= 30 else WHITE))
                bullets.remove(b)
                continue
            # 開放世界中判斷飛出大邊界
            if b.lifespan <= 0 or not pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT).inflate(500, 500).colliderect(b.rect): bullets.remove(b)
            
        for eb in enemy_bullets[::-1]:
            eb.update()
            if not pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT).inflate(500, 500).colliderect(eb.rect): enemy_bullets.remove(eb)
            
        for e in enemies:
            e.update(player.pos, enemies)
            e.emit_attacks(enemy_bullets, player.pos)
            
        for p in particles[::-1]:
            p.update(); 
            if p.timer <= 0: particles.remove(p)
            
        for dt in damage_texts[::-1]:
            dt.update()
            if dt.timer <= 0: damage_texts.remove(dt)

        if boss_warning_timer > 0: boss_warning_timer -= 1

        if boss_active:
            boss.update(player.pos, bullets) 
            boss.emit_attacks(enemy_bullets)
            
        if boss_active and boss.state == "DEFEAT" and boss.defeat_timer > 60:
            boss_active, boss_defeated = False, True
            next_boss_level += 5
            stop_sound("boss_bgm")
            try: pygame.mixer.music.play(-1)
            except: pass

        # 玩家子彈撞到敵人
        for b in bullets[::-1]:
            hit_something = False
            for e in enemies[::-1]:
                if b.rect.colliderect(e.rect):
                    if b.b_type == "frost": e.frost_timer = 120 
                    if b.b_type == "cannon": 
                        push_dir = e.pos - player.pos
                        if push_dir.length() > 0: push_dir.normalize_ip(); e.pos += push_dir * 30 
                    elif b.b_type == "flame_grenade": b.explode = True; break
                        
                    shield_damage = min(e.shield, b.damage)
                    e.shield -= shield_damage
                    actual_damage = b.damage - shield_damage
                    e.hp -= actual_damage
                    
                    damage_texts.append(DamageText(e.pos.x, e.pos.y - 15, b.damage, YELLOW if b.damage >= 30 else WHITE))
                    hit_something = True
                    for _ in range(5): particles.append(Particle(e.pos.x, e.pos.y, b.color))
                    play_sound("hit")
                    
                    if e.hp <= 0:
                        for _ in range(12 if e.is_elite else 6): particles.append(Particle(e.pos.x, e.pos.y, RED))
                        if random.random() < e.exp_drop_chance: 
                            gem_count = 3 if e.is_elite else 1
                            for _ in range(gem_count): items.append(DropItem(e.pos.x + random.randint(-12,12), e.pos.y + random.randint(-12,12), "EXP", 35))
                        if random.random() < e.health_drop_chance: 
                            items.append(DropItem(e.pos.x, e.pos.y, "HP", 40 if e.is_elite else 25))
                        enemies.remove(e)
            
            if getattr(b, 'explode', False): continue 

            if boss_active and b.rect.colliderect(boss.rect):
                hit_something = True
                if not boss.can_take_damage():
                    for _ in range(5): particles.append(Particle(boss.pos.x, boss.pos.y, GRAY))
                elif boss.state != "DEFEAT":
                    if b.b_type == "frost": boss.frost_timer = 60 
                    boss.hp -= b.damage
                    damage_texts.append(DamageText(boss.pos.x, boss.pos.y - 30, b.damage, YELLOW if b.damage >= 30 else WHITE))
                    for _ in range(8): particles.append(Particle(boss.pos.x, boss.pos.y, YELLOW))
                    play_sound("hit")
                    
                    if boss.hp <= 0:
                        boss.state, boss.defeat_timer = "DEFEAT", 0
                        for _ in range(40): items.append(DropItem(boss.pos.x + random.randint(-60,60), boss.pos.y + random.randint(-60,60), "EXP", 35))
                        for _ in range(5): items.append(DropItem(boss.pos.x + random.randint(-40,40), boss.pos.y + random.randint(-40,40), random.choice(["HP", "SHIELD"]), 25))
                        for _ in range(50): particles.append(Particle(boss.pos.x, boss.pos.y, YELLOW))
            if hit_something and not b.is_piercing and b in bullets: bullets.remove(b)

        # 電弧光環傷害
        if player.aura_level > 0:
            aura_radius = 95 + player.aura_level * 25
            aura_damage = 0.015 * player.aura_level
            for e in enemies[::-1]:
                if player.pos.distance_to(e.pos) <= aura_radius:
                    shield_damage = min(e.shield, aura_damage)
                    e.shield -= shield_damage
                    e.hp -= (aura_damage - shield_damage)
                    if random.random() < 0.08: particles.append(Particle(e.pos.x, e.pos.y, BLUE))
                    if e.hp <= 0:
                        for _ in range(8 if e.is_elite else 4): particles.append(Particle(e.pos.x, e.pos.y, e.color))
                        if random.random() < e.exp_drop_chance: items.append(DropItem(e.pos.x, e.pos.y, "EXP"))
                        if random.random() < e.health_drop_chance: items.append(DropItem(e.pos.x, e.pos.y, "HP", 40 if e.is_elite else 25))
                        enemies.remove(e)

        # 玩家受傷
        def player_take_damage(dmg):
            global game_state
            if player.god_mode: return 
            if player.invincible_timer <= 0 and not player.is_dashing:
                actual_dmg = max(1, dmg - player.damage_reduction)
                if player.shield > 0:
                    if player.shield >= actual_dmg: player.shield -= actual_dmg; actual_dmg = 0
                    else: actual_dmg -= player.shield; player.shield = 0
                if actual_dmg > 0: player.hp -= actual_dmg
                player.invincible_timer = player.invincible_duration; play_sound("hurt")
                if player.hp <= 0:
                    game_state = "GAME_OVER"; play_sound("gameover"); stop_sound("boss_bgm")  
                    try: pygame.mixer.music.stop()
                    except: pass

        for e in enemies:
            if e.combat_type == "melee" and player.rect.colliderect(e.rect): player_take_damage(e.damage)
        for eb in enemy_bullets[::-1]:
            if player.rect.colliderect(eb.rect): player_take_damage(25); enemy_bullets.remove(eb) if eb in enemy_bullets else None
        if boss_active and boss.state != "DEFEAT" and player.rect.colliderect(boss.rect): player_take_damage(boss.collision_damage) 

        # 吃掉落物
        for item in items[::-1]:
            item.update(player.pos, player.magnet_radius)
            if player.rect.colliderect(item.rect):
                items.remove(item)
                if item.item_type == "EXP": player.exp += int(item.amount * player.exp_multiplier); play_sound("exp") 
                elif item.item_type == "HP": player.hp = min(player.max_hp, player.hp + item.amount); play_sound("exp")
                elif item.item_type == "SHIELD": player.shield = min(player.max_shield, player.shield + item.amount); play_sound("exp")

                if player.exp >= player.max_exp:
                    player.level += 1; player.exp = 0; player.max_exp = int(player.max_exp * 1.25) 
                    choose_upgrade_cards(); game_state = "LEVEL_UP"; play_sound("levelup") 

    # --- 畫面繪製 ---
    if game_state == "MENU":
        screen.fill(BLACK)
        for i in range(100):
            x = (i * 37) % WIDTH; y = (i * 23) % HEIGHT
            brightness = 100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i)
            pygame.draw.circle(screen, (int(brightness), int(brightness), int(brightness)), (x, y), 1)
            
        glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        title = large_font.render("Space War", True, BLUE)
        glow_surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -3), (0, 3), (-3, 0), (3, 0)]:
            glow_copy = glow_surface.copy()
            glow_copy.fill((0, 100, 255, 50), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(glow_copy, offset)
            
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        subtitle = font.render("霓虹驅魔人", True, WHITE)
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2 - 60))
        
        mouse_pos = pygame.mouse.get_pos()
        if start_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (100, 200, 100), start_button.inflate(10, 10), border_radius=12)
            pygame.draw.rect(screen, YELLOW, start_button.inflate(10, 10), 4, border_radius=12)
        else:
            pygame.draw.rect(screen, (50, 150, 50), start_button, border_radius=10)
            pygame.draw.rect(screen, WHITE, start_button, 3, border_radius=10)
        start_txt = font.render("開始遊戲", True, WHITE)
        screen.blit(start_txt, (start_button.centerx - start_txt.get_width()//2, start_button.centery - start_txt.get_height()//2))

        pygame.draw.rect(screen, BLUE if changelog_button.collidepoint(mouse_pos) else (50, 100, 150), changelog_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, changelog_button, 3, border_radius=10)
        cl_txt = font.render("更新日誌", True, WHITE)
        screen.blit(cl_txt, (changelog_button.centerx - cl_txt.get_width()//2, changelog_button.centery - cl_txt.get_height()//2))

        pygame.draw.rect(screen, RED if exit_button.collidepoint(mouse_pos) else (150, 50, 50), exit_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, exit_button, 3, border_radius=10)
        ex_txt = font.render("退出遊戲", True, WHITE)
        screen.blit(ex_txt, (exit_button.centerx - ex_txt.get_width()//2, exit_button.centery - ex_txt.get_height()//2))
        
        controls_title = font.render("操作說明:", True, YELLOW)
        screen.blit(controls_title, (WIDTH//2 - controls_title.get_width()//2, HEIGHT//2 + 250))
        controls = ["移動: WASD", "射擊: 滑鼠左鍵", "大絕招: 滑鼠右鍵", "衝刺: Q鍵 或 SPACE", "切換武器: E鍵", "暫停: ESC", "全螢幕: F11"]
        for i, c in enumerate(controls): screen.blit(small_font.render(c, True, GRAY), (WIDTH//2 - small_font.size(c)[0]//2, HEIGHT//2 + 285 + i*25))

        screen.blit(font.render("v1.4 (A3+B4 融合版)", True, GRAY), (20, HEIGHT - 40))

        if show_changelog: draw_changelog_popup(screen)
        
    elif game_state == "DIFFICULTY":
        screen.fill(BLACK)
        for i in range(100):
            x = (i * 37) % WIDTH; y = (i * 23) % HEIGHT
            brightness = 100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i)
            pygame.draw.circle(screen, (int(brightness), int(brightness), int(brightness)), (x, y), 1)

        title = large_font.render("選擇難易度", True, YELLOW)
        subtitle = font.render("Boss 戰會清空小怪，專心迎戰核心威脅", True, GRAY)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 235))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2 - 180))

        mouse_pos = pygame.mouse.get_pos()
        normal_hovered, challenge_hovered = normal_button.collidepoint(mouse_pos), challenge_button.collidepoint(mouse_pos)
        pygame.draw.rect(screen, (55, 125, 185) if normal_hovered else (30, 70, 115), normal_button, border_radius=10)
        pygame.draw.rect(screen, YELLOW if normal_hovered else WHITE, normal_button, 4 if normal_hovered else 3, border_radius=10)
        pygame.draw.rect(screen, (190, 55, 70) if challenge_hovered else (115, 35, 50), challenge_button, border_radius=10)
        pygame.draw.rect(screen, YELLOW if challenge_hovered else WHITE, challenge_button, 4 if challenge_hovered else 3, border_radius=10)

        n_txt = large_font.render("普通", True, WHITE)
        screen.blit(n_txt, (normal_button.centerx - n_txt.get_width()//2, normal_button.y + 28))
        screen.blit(small_font.render("標準節奏，無限彈藥", True, WHITE), (normal_button.centerx - 85, normal_button.y + 88))
        for i, line in enumerate(["敵人強度：標準", "彈藥：無需換彈", "適合享受割草快感"]):
            screen.blit(small_font.render(line, True, (210, 225, 240)), (normal_button.x + 42, normal_button.y + 132 + i * 28))

        c_txt = large_font.render("挑戰", True, WHITE)
        screen.blit(c_txt, (challenge_button.centerx - c_txt.get_width()//2, challenge_button.y + 28))
        screen.blit(small_font.render("敵人 1.75 倍，啟用彈匣", True, WHITE), (challenge_button.centerx - 100, challenge_button.y + 88))
        for i, line in enumerate(["彈匣打完自動換彈 (也可按 R)", "追加挑戰專屬卡牌", "適合追求極限走位"]):
            screen.blit(small_font.render(line, True, (255, 220, 220)), (challenge_button.x + 42, challenge_button.y + 132 + i * 28))

        pygame.draw.rect(screen, BLUE if difficulty_back_button.collidepoint(mouse_pos) else (50, 100, 150), difficulty_back_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, difficulty_back_button, 3, border_radius=10)
        screen.blit(font.render("返回", True, WHITE), (difficulty_back_button.centerx - 28, difficulty_back_button.centery - 16))

    else:
        # 遊戲進行中畫面繪製
        if images.get("bg"):
            bg_img = pygame.transform.scale(images["bg"], (WIDTH, HEIGHT))
            bg_x, bg_y = -global_offset_x % WIDTH, -global_offset_y % HEIGHT
            screen.blit(bg_img, (bg_x, bg_y)); screen.blit(bg_img, (bg_x - WIDTH, bg_y))
            screen.blit(bg_img, (bg_x, bg_y - HEIGHT)); screen.blit(bg_img, (bg_x - WIDTH, bg_y - HEIGHT))
        else: screen.fill(BLACK)
        draw_map_bounds(screen)
        
        for i in items: i.draw(screen)
        for p in particles: p.draw(screen)
        for b in bullets: b.draw(screen)
        for eb in enemy_bullets: eb.draw(screen) 
        for e in enemies: e.draw(screen)
        for t in trails: t.draw(screen)
        for dt in damage_texts: dt.draw(screen)
        if boss_active: boss.draw(screen) 
        
        player.draw(screen, player.weapons[player.current_weapon_idx] if game_state in ["PLAYING", "PAUSED"] else None)
        if boss_active: draw_boss_direction_arrow(screen, boss)

        # UI
        pygame.draw.rect(screen, GRAY, (20, 20, 250, 15)); pygame.draw.rect(screen, BLUE, (20, 20, 250 * (player.exp / player.max_exp), 15))
        screen.blit(font.render(f"等級: {player.level}", True, WHITE), (280, 15))
        pygame.draw.rect(screen, GRAY, (20, 45, 200, 15)); pygame.draw.rect(screen, GREEN if player.hp > 30 else RED, (20, 45, 200 * (max(0, player.hp) / player.max_hp), 15))
        screen.blit(font.render(f"血量", True, WHITE), (230, 40))
        pygame.draw.rect(screen, GRAY, (20, 70, 200, 12)); pygame.draw.rect(screen, BLUE, (20, 70, 200 * (max(0, player.shield) / player.max_shield), 12))
        screen.blit(font.render("護盾", True, WHITE), (230, 62))
        pygame.draw.rect(screen, GRAY, (20, 95, 150, 10)); pygame.draw.rect(screen, ORANGE, (20, 95, 150 * (player.stamina / player.max_stamina), 10))
        screen.blit(font.render("體力 (Q鍵)", True, WHITE), (180, 87)) 
        pygame.draw.rect(screen, GRAY, (20, 120, 150, 10)); pygame.draw.rect(screen, CYAN, (20, 120, 150 * (player.energy / player.max_energy), 10))
        screen.blit(font.render("能量", True, WHITE), (180, 112))

        if game_mode == CHALLENGE_MODE:
            screen.blit(small_font.render("挑戰模式", True, RED), (20, 142))
            r_c = YELLOW if player.current_weapon_type() == "pistol" else WHITE
            s_c = YELLOW if player.current_weapon_type() == "sniper" else WHITE
            screen.blit(small_font.render(f"一般彈藥: {player.pistol_ammo}/{player.pistol_mag_size}", True, r_c), (20, 170))
            screen.blit(small_font.render(f"高階彈藥: {player.sniper_ammo}/{player.sniper_mag_size}", True, s_c), (20, 196))
            if player.reload_timer > 0:
                pygame.draw.rect(screen, GRAY, (20, 224, 170, 10))
                pygame.draw.rect(screen, YELLOW, (20, 224, int(170 * (1 - player.reload_timer / player.reload_duration)), 10))
                reload_name = "高階" if player.reloading_weapon == "sniper" else "一般"
                screen.blit(small_font.render(f"{reload_name}換彈中", True, YELLOW), (200, 212))

        wep_name = player.weapons[player.current_weapon_idx].name
        screen.blit(font.render(f"武器: {wep_name} (E 鍵切換)", True, WHITE), (20, 250 if game_mode == CHALLENGE_MODE else 145))
        wep_icon = images.get("icon_" + wep_name)
        if wep_icon: screen.blit(wep_icon, (20, 280 if game_mode == CHALLENGE_MODE else 175))

        if player.skill_cd > 0: skill_txt = font.render(f"大絕冷卻: {round(player.skill_cd / 60, 1)} 秒", True, GRAY)
        elif player.energy < player.skill_cost: skill_txt = font.render("大絕: 能量不足", True, RED)
        else: skill_txt = font.render("大絕準備就緒 (右鍵)", True, GREEN)
        screen.blit(skill_txt, (WIDTH - 280, HEIGHT - 40))
        if player.god_mode: screen.blit(font.render("【無敵模式啟用】", True, YELLOW), (WIDTH//2 - 100, 20))

        if boss_active:
            bar_w = min(WIDTH - 100, 800)
            bar_x = WIDTH//2 - bar_w//2
            pygame.draw.rect(screen, GRAY, (bar_x, HEIGHT - 80, bar_w, 20))
            boss_bar_color = RED if boss.b_type == "RED" else (PURPLE if boss.b_type == "PURPLE" else YELLOW)
            pygame.draw.rect(screen, boss_bar_color, (bar_x, HEIGHT - 80, bar_w * (max(0, boss.hp) / boss.max_hp), 20))
            
            if boss_warning_timer > 0 and boss.state != "ENTRANCE": screen.blit(font.render(f"⚠️ 警告：偵測到極度危險異常實體 - 【{boss.name}】", True, RED), (WIDTH//2 - 250, HEIGHT - 110))
            elif boss.state != "ENTRANCE":
                msg, clr = boss.get_state_message()
                screen.blit(font.render(f"Lv.{boss.spawn_level} 【{boss.name}】: {msg}", True, clr), (WIDTH//2 - 250, HEIGHT - 110))

        if game_state == "LEVEL_UP":
            screen.blit(dim_surface, (0, 0)) 
            title = large_font.render("升級！選擇強化後按確認", True, YELLOW)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
            
            for i, card in enumerate(cards):
                if i >= len(current_upgrade_choices): continue
                upgrade = upgrade_options[current_upgrade_choices[i]]
                is_selected = (selected_upgrade_position == i)
                base_color = CARD_TYPE_COLORS.get(upgrade.get("type"), CARD_COLOR)
                hover_color = tuple(min(255, c + 35) for c in base_color)
                color = tuple(min(255, c + 65) for c in base_color) if is_selected else hover_color if card.collidepoint(pygame.mouse.get_pos()) else base_color
                
                pygame.draw.rect(screen, color, card, border_radius=10)
                pygame.draw.rect(screen, YELLOW if is_selected else WHITE, card, 6 if is_selected else 3, border_radius=10) 
                
                type_label = CARD_TYPE_LABELS.get(upgrade.get("type"), "")
                if type_label:
                    label_bg = pygame.Rect(card.centerx - 42, card.y + 18, 84, 28)
                    pygame.draw.rect(screen, (20, 20, 28), label_bg, border_radius=8)
                    pygame.draw.rect(screen, WHITE, label_bg, 1, border_radius=8)
                    screen.blit(small_font.render(type_label, True, WHITE), (label_bg.centerx - 20, label_bg.centery - 12))
                
                opt_title = font.render(upgrade["title"], True, WHITE)
                screen.blit(opt_title, (card.centerx - opt_title.get_width()//2, card.y + 65))
                screen.blit(font.render(upgrade["desc"][0], True, YELLOW), (card.centerx - font.size(upgrade["desc"][0])[0]//2, card.y + 125))
                screen.blit(font.render(upgrade["desc"][1], True, YELLOW), (card.centerx - font.size(upgrade["desc"][1])[0]//2, card.y + 165))
            
            confirm_ready = selected_upgrade_position is not None
            pygame.draw.rect(screen, GREEN if confirm_ready and confirm_upgrade_button.collidepoint(pygame.mouse.get_pos()) else (50, 150, 50) if confirm_ready else GRAY, confirm_upgrade_button, border_radius=10)
            pygame.draw.rect(screen, WHITE, confirm_upgrade_button, 3, border_radius=10)
            screen.blit(font.render("確認選擇", True, WHITE), (confirm_upgrade_button.centerx - 55, confirm_upgrade_button.centery - 15))

        elif game_state == "PAUSED":
            screen.blit(dim_surface, (0, 0))
            screen.blit(large_font.render("暫停中", True, YELLOW), (WIDTH//2 - 75, HEIGHT//2 - 200))
            
            btns =[
                (pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 70, 220, 60), "繼續遊戲", BLUE),
                (pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 70, 220, 60), "回到選單", BLUE),
                (pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 150, 220, 60), "重新開始", GREEN),
                (pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 150, 220, 60), "退出遊戲", RED)
            ]
            for btn, txt, clr in btns:
                pygame.draw.rect(screen, clr if btn.collidepoint(pygame.mouse.get_pos()) else (clr[0]//2, clr[1]//2, clr[2]//2), btn, border_radius=10)
                pygame.draw.rect(screen, WHITE, btn, 3, border_radius=10)
                t_surf = font.render(txt, True, WHITE)
                screen.blit(t_surf, (btn.centerx - t_surf.get_width()//2, btn.centery - t_surf.get_height()//2))
            
            draw_pause_upgrade_log(screen)

        elif game_state == "GAME_OVER":
            screen.blit(dim_surface, (0, 0))
            game_over_txt = large_font.render("Game Over", True, RED)
            screen.blit(game_over_txt, (WIDTH//2 - game_over_txt.get_width()//2, HEIGHT//2 - 150))
            
            for btn, txt, clr in [(restart_button, "重新開始", GREEN), (menu_button, "回到選單", BLUE)]:
                pygame.draw.rect(screen, clr if btn.collidepoint(pygame.mouse.get_pos()) else (clr[0]//2, clr[1]//2, clr[2]//2), btn, border_radius=10)
                pygame.draw.rect(screen, WHITE, btn, 3, border_radius=10)
                t_surf = font.render(txt, True, WHITE)
                screen.blit(t_surf, (btn.centerx - t_surf.get_width()//2, btn.centery - t_surf.get_height()//2))

    pygame.display.flip()
    clock.tick(FPS)

>>>>>>> 5fe3c3b9a6cb6e15508d0cc26521ee2ec490b8fd
pygame.quit()