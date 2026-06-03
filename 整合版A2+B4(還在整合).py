import pygame
import random
import math
import os

# 初始化遊戲跟音效
pygame.init()
pygame.mixer.init()

# 設定視窗
WIDTH, HEIGHT = 1024, 768
fullscreen_mode = False
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("霓虹驅魔人 - 開放世界大作版")
clock = pygame.time.Clock()
FPS = 60

# 顏色設定RGB
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
SHIELD_COLOR = (0, 102, 204)    
EXP_COLOR = (124, 252, 0)   
HP_COLOR = (255, 0, 0)    

# 字體設定
CHINESE_FONTS = "microsoftjhenghei,pingfangtc,stheiti,simhei"
font = pygame.font.SysFont(CHINESE_FONTS, 28)
large_font = pygame.font.SysFont(CHINESE_FONTS, 48)
small_font = pygame.font.SysFont(CHINESE_FONTS, 22)

# 動畫以及貼圖系統
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

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

# 音效和音樂系統
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
    if name in sounds and sounds[name] != None: sounds[name].play(loops=loop)
def stop_sound(name):
    if name in sounds and sounds[name] != None: sounds[name].stop()

# 秘技與全域變數
CHEAT_CODE =[pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_b, pygame.K_a, pygame.K_b, pygame.K_a]
key_buffer =[] 
global_offset_x = 0
global_offset_y = 0

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

class Player:
    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        
        self.size = 30
        self.base_speed = 5
        
        # 建立 Rect
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        
        # 同時建立 pos，確保 A2 複製過來的向量功能不會出問題(待確認)
        self.pos = pygame.math.Vector2(self.x, self.y)
        
        # 將 rect 中心對準座標
        self.rect.center = (self.x, self.y)
        
        # 武器系統
        self.weapons = list(WEAPON_TYPES.values())
        self.current_weapon_idx = 0
        
        # 強化系統數值
        self.bullet_count = 1      
        self.bullet_spread = 15
        self.bullet_damage_bonus = 0
        self.damage_reduction = 0
        
        self.exp, self.level, self.max_exp = 0, 1, 100
        self.magnet_radius = 60
        self.max_hp, self.hp, self.max_shield, self.shield = 100, 100, 100, 0       
        self.invincible_timer, self.invincible_duration = 0, 60
        self.max_stamina, self.stamina, self.dash_cost, self.stamina_regen = 100, 100, 35, 0.5   
        self.is_dashing, self.dash_speed, self.dash_duration, self.dash_timer = False, 22, 8, 0
        self.dash_dir_x, self.dash_dir_y = 0, 0
        self.max_energy, self.energy, self.energy_regen = 100, 100, 0.2     
        self.skill_cd, self.skill_max_cd, self.skill_cost = 0, 600, 50        
        self.god_mode = False 

    def update(self):
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
        if not self.is_dashing and self.stamina < self.max_stamina: self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen)
        if self.energy < self.max_energy: self.energy = min(self.max_energy, self.energy + self.energy_regen)

        if (keys[pygame.K_q] or keys[pygame.K_SPACE]) and not self.is_dashing and self.stamina >= self.dash_cost:
            self.stamina -= self.dash_cost
            self.is_dashing, self.dash_timer = True, self.dash_duration
            play_sound("dash")
            if dist > 0: self.dash_dir_x, self.dash_dir_y = move_x, move_y
            else:
                mx, my = pygame.mouse.get_pos()
                dx, dy = mx - (WIDTH/2), my - (HEIGHT/2)
                ddist = math.sqrt(dx**2 + dy**2)
                if ddist > 0: self.dash_dir_x, self.dash_dir_y = dx/ddist, dy/ddist

        intended_x, intended_y = self.x, self.y
        if self.is_dashing:
            intended_x += self.dash_dir_x * self.dash_speed
            intended_y += self.dash_dir_y * self.dash_speed
            # 產生 A2 的殘影
            trails.append(DashTrail(self.pos, self.size))
            self.dash_timer -= 1
            if self.dash_timer <= 0: self.is_dashing = False
        else:
            intended_x += move_x * self.base_speed
            intended_y += move_y * self.base_speed
            
        # 攝影機邏輯，計算偏移量，並把玩家鎖在中心
        offset_x = intended_x - (WIDTH / 2)
        offset_y = intended_y - (HEIGHT / 2)
        self.x, self.y = WIDTH / 2, HEIGHT / 2
        self.rect.center = (int(self.x), int(self.y))
        # 執行攝影機移動
        apply_camera_follow(offset_x, offset_y)

        #  A2 複製過來的功能（如子彈發射方向、向量計算）才會拿到正確的座標###############################
        self.pos.x = self.x
        self.pos.y = self.y

    def draw(self, surface, current_wep=None):
        draw_player = True
        if self.invincible_timer > 0 and not self.god_mode and (self.invincible_timer // 4) % 2 == 0:
            draw_player = False
                
        if draw_player:
            anim_frames = animations.get("player")
            if anim_frames:
                img = anim_frames[int(pygame.time.get_ticks() / 100) % len(anim_frames)]
                if pygame.mouse.get_pos()[0] < self.x: img = pygame.transform.flip(img, True, False)
                surface.blit(img, img.get_rect(center=self.rect.center))
            else:
                pygame.draw.rect(surface, YELLOW if self.god_mode else BLUE, self.rect)
                
            if self.stamina < self.dash_cost: pygame.draw.rect(surface, GRAY, self.rect, 3)

            if current_wep:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx, dy = mouse_x - self.x, mouse_y - self.y
                dist = math.sqrt(dx**2 + dy**2)
                dir_x, dir_y = (dx/dist, dy/dist) if dist > 0 else (1, 0)
                angle = math.degrees(math.atan2(-dy, dx))
                gun_img = images.get("gun_" + current_wep.name)
                
                if gun_img:
                    if dx < 0: gun_img = pygame.transform.flip(gun_img, False, True)
                    rotated_gun = pygame.transform.rotate(gun_img, angle)
                    gun_rect = rotated_gun.get_rect(center=(int(self.x + dir_x * 15), int(self.y + dir_y * 15)))
                    surface.blit(rotated_gun, gun_rect)
                else:
                    end_x, end_y = self.x + dir_x * 25, self.y + dir_y * 25
                    wep_color = PURPLE if current_wep.bullet_type == "piercing" else ORANGE if current_wep.bullet_type == "flamethrower" else CYAN if current_wep.bullet_type == "laser" else WHITE if current_wep.bullet_type == "cannon" else (100, 200, 255) if current_wep.bullet_type == "frost" else RED if current_wep.bullet_type == "flame_grenade" else GREEN if current_wep.bullet_type == "plasma" else YELLOW
                    pygame.draw.line(surface, GRAY, (self.x, self.y), (end_x, end_y), 6)
                    pygame.draw.circle(surface, wep_color, (int(end_x), int(end_y)), 4)

def apply_camera_follow(offset_x, offset_y):
    if offset_x == 0 and offset_y == 0: return
    global global_offset_x, global_offset_y
    global_offset_x += offset_x
    global_offset_y += offset_y
    
    for group in [bullets, enemy_bullets, enemies, particles, items, trails, damage_texts]:
        for obj in group:
            obj.x -= offset_x
            obj.y -= offset_y
            if hasattr(obj, "rect"): obj.rect.center = (int(obj.x), int(obj.y))
            if hasattr(obj, "target_x"): obj.target_x -= offset_x; obj.target_y -= offset_y
            
    if boss_active and boss:
        boss.x -= offset_x; boss.y -= offset_y
        boss.rect.center = (int(boss.x), int(boss.y))
        if hasattr(boss, "aim_x"): boss.aim_x -= offset_x; boss.aim_y -= offset_y

class DashTrail:
    def __init__(self, x, y, size): self.x, self.y, self.size, self.life = x, y, size, 12
    def update(self): self.life -= 1; self.size -= 1.5
    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            rect = pygame.Rect(0, 0, self.size, self.size)
            rect.center = (int(self.x), int(self.y))
            pygame.draw.rect(surface, BLUE, rect, max(1, int(self.life / 3)))

class Bullet:
    def __init__(self, x, y, target_x, target_y, weapon):
        self.x, self.y, self.target_x, self.target_y = x, y, target_x, target_y
        self.b_type, self.damage = weapon.bullet_type, weapon.damage + player.bullet_damage_bonus
        self.is_piercing = self.b_type in["piercing", "laser", "cannon", "flamethrower"]
            
        dx, dy = self.target_x - self.x, self.target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        self.dir_x, self.dir_y = (dx/dist, dy/dist) if dist > 0 else (0,0)
        
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
        if self.b_type == "flame_grenade" and math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2) < self.speed:
            self.explode, self.lifespan = True, 0; return 
        if self.b_type == "plasma":
            # 在開放世界中，電漿子彈碰到畫面邊緣反彈，需要考慮 global_offset
            screen_x, screen_y = self.x + global_offset_x, self.y + global_offset_y
            if screen_x <= 0 or screen_x >= WIDTH: self.dir_x *= -1
            if screen_y <= 0 or screen_y >= HEIGHT: self.dir_y *= -1
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        img = images.get("bullet_" + self.b_type)
        if img:
            angle = math.degrees(math.atan2(-self.dir_y, self.dir_x))
            rotated_img = pygame.transform.rotate(img, angle)
            surface.blit(rotated_img, rotated_img.get_rect(center=self.rect.center))
        else:
            if self.b_type == "laser":
                pygame.draw.line(surface, self.color, (self.x, self.y), (self.x - self.dir_x * 30, self.y - self.dir_y * 30), self.radius*2)
            else: pygame.draw.circle(surface, self.color, self.rect.center, self.radius)

class EnemyBullet:
    def __init__(self, x, y, dir_x, dir_y):
        self.x, self.y, self.dir_x, self.dir_y = x, y, dir_x, dir_y
        dist = math.sqrt(self.dir_x**2 + self.dir_y**2)
        if dist > 0: self.dir_x /= dist; self.dir_y /= dist
        self.radius, self.speed, self.color = 8, 7, ORANGE
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        
    def update(self):
        self.x += self.dir_x * self.speed; self.y += self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface): 
        img = images.get("enemy_bullet")
        if img: surface.blit(img, img.get_rect(center=self.rect.center))
        else: pygame.draw.circle(surface, self.color, self.rect.center, self.radius)

class Enemy:
    def __init__(self, level, is_elite=False):
        self.is_elite = is_elite
        self.size = 42 if is_elite else 25
        speed_bonus = min(level * 0.03, 1.2)
        self.speed = (random.uniform(2.0, 4.0) if is_elite else random.uniform(1.5, 3.5)) + speed_bonus
        self.max_hp = (30 + level * 15) if is_elite else (10 + level * 5)
        self.hp, self.damage = self.max_hp, (35 if is_elite else 15)
        self.shield = level // 4 + (2 if is_elite else 0)
        self.max_shield = self.shield
        self.frost_timer, self.dir_x = 0, 0  
        
        # 開放世界中，在玩家畫面外一圈生成
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        px, py = player.x, player.y
        if edge == 'top': self.x, self.y = px + random.randint(-WIDTH//2, WIDTH//2), py - HEIGHT//2 - self.size
        elif edge == 'bottom': self.x, self.y = px + random.randint(-WIDTH//2, WIDTH//2), py + HEIGHT//2 + self.size
        elif edge == 'left': self.x, self.y = px - WIDTH//2 - self.size, py + random.randint(-HEIGHT//2, HEIGHT//2)
        elif edge == 'right': self.x, self.y = px + WIDTH//2 + self.size, py + random.randint(-HEIGHT//2, HEIGHT//2)
            
        self.rect = pygame.Rect(0, 0, self.size, self.size)

    def update(self, target_x, target_y, all_enemies):
        current_speed = self.speed * 0.4 if self.frost_timer > 0 else self.speed
        if self.frost_timer > 0: self.frost_timer -= 1

        dx, dy = target_x - self.x, target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            self.dir_x, dir_y = dx / dist, dy / dist
            self.x += self.dir_x * current_speed; self.y += dir_y * current_speed

        for other in all_enemies:
            if other is not self:
                dist_sq = (self.x - other.x)**2 + (self.y - other.y)**2
                if 0 < dist_sq < self.size**2:
                    dist_val = math.sqrt(dist_sq)
                    self.x += ((self.x - other.x) / dist_val) * 1.2
                    self.y += ((self.y - other.y) / dist_val) * 1.2
            
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        anim_key = "enemy_elite" if self.is_elite else "enemy_normal"
        anim_frames = animations.get(anim_key)
        
        if anim_frames:
            img = anim_frames[int(pygame.time.get_ticks() / 100) % len(anim_frames)]
            if self.dir_x < 0: img = pygame.transform.flip(img, True, False)
            if self.frost_timer > 0:
                img = img.copy(); img.fill((100, 200, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(img, img.get_rect(center=self.rect.center))
            if self.is_elite:
                glow = math.sin(pygame.time.get_ticks() * 0.01) * 6 + 6
                pygame.draw.rect(surface, DARK_PURPLE, self.rect.copy().inflate(glow, glow), 3) 
        else:
            color = (150, 0, 150) if self.is_elite else RED
            if self.frost_timer > 0: color = (100, 200, 255)
            pygame.draw.rect(surface, color, self.rect)
            if self.is_elite:
                glow = math.sin(pygame.time.get_ticks() * 0.01) * 6 + 6
                pygame.draw.rect(surface, DARK_PURPLE, self.rect.copy().inflate(glow, glow), 3)
                
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
        self.x, self.y = player.x, player.y - HEIGHT//2 - 100
        self.size = 65
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.spawn_level = level
        self.max_hp = 500 + level * 250
        self.hp = self.max_hp
        self.speed = 4.0
        
        self.state = "ENTRANCE"
        self.state_timer, self.frost_timer, self.defeat_timer = 0, 0, 0
        self.entrance_duration = 120  
        self.play_shoot_sound = False 
        
        if self.b_type == "YELLOW": self.color = YELLOW
        elif self.b_type == "RED": self.color, self.aim_x, self.aim_y = RED, 0, 0
        elif self.b_type == "PURPLE": self.color = PURPLE

    def update(self, player_x, player_y, bullets, enemies, enemy_bullets):
        self.state_timer += 1
        current_speed = self.speed * 0.5 if self.frost_timer > 0 else self.speed
        if self.frost_timer > 0: self.frost_timer -= 1
        self.play_shoot_sound = False

        if self.state == "ENTRANCE":
            progress = self.state_timer / self.entrance_duration
            self.y += 1.5 
            if self.b_type == "YELLOW": self.color = (100 + 155*progress, 100 + 155*progress, 0)
            elif self.b_type == "RED": self.color = (100 + 155*progress, 0, 0)
            elif self.b_type == "PURPLE": self.color = (100 + 100*progress, 0, 100 + 155*progress)
            if self.state_timer >= self.entrance_duration:
                self.state = "EVADE" if self.b_type == "YELLOW" else ("CHASE" if self.b_type == "RED" else "FLEE")
                self.state_timer = 0
                
        elif self.state == "DEFEAT":
            self.defeat_timer += 1
            self.y -= 1
            self.x += math.sin(self.defeat_timer * 0.2) * 1.5

        elif self.b_type == "YELLOW":
            if self.state == "EVADE":
                dx, dy = player_x - self.x, player_y - self.y
                dist = math.sqrt(dx**2 + dy**2)
                dir_x, dir_y = (dx/dist, dy/dist) if dist > 0 else (0,0)
                tangent_x, tangent_y = -dir_y, dir_x 
                
                dodged = False
                for b in bullets:
                    if math.sqrt((self.x - b.x)**2 + (self.y - b.y)**2) < 150:
                        f_dx, f_dy = self.x - b.x, self.y - b.y
                        f_dist = math.sqrt(f_dx**2 + f_dy**2)
                        if f_dist > 0:
                            self.x += (f_dx/f_dist) * (current_speed * 1.8)
                            self.y += (f_dy/f_dist) * (current_speed * 1.8)
                        dodged = True; break 
                        
                if not dodged:
                    self.x += tangent_x * current_speed; self.y += tangent_y * current_speed
                    p_dist = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)
                    if p_dist > 250: self.x += dir_x * current_speed; self.y += dir_y * current_speed
                    elif p_dist < 150: self.x -= dir_x * current_speed; self.y -= dir_y * current_speed

                if self.state_timer > 120: self.state = "CHARGE"; self.state_timer = 0
                    
            elif self.state == "CHARGE":
                if self.state_timer > 60: 
                    for i in range(12):
                        angle = math.radians(i * 30)
                        enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, math.cos(angle), math.sin(angle)))
                    if self.spawn_level >= 10:
                        for i in range(12):
                            angle = math.radians(i * 30 + 15)
                            enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, math.cos(angle), math.sin(angle)))
                    self.state = "EVADE"; self.state_timer = 0; self.play_shoot_sound = True

        elif self.b_type == "RED":
            if self.state == "CHASE":
                dx, dy = player_x - self.x, player_y - self.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist > 0: self.x += (dx/dist) * current_speed; self.y += (dy/dist) * current_speed
                if self.state_timer > 150: self.state = "WARN"; self.state_timer = 0
            elif self.state == "WARN":
                self.aim_x, self.aim_y = player_x, player_y
                if self.state_timer > 45:
                    self.state, self.state_timer = "DASH", 0
                    dash_dx, dash_dy = self.aim_x - self.x, self.aim_y - self.y
                    dash_dist = math.sqrt(dash_dx**2 + dash_dy**2)
                    self.dash_dir_x, self.dash_dir_y = (dash_dx/dash_dist, dash_dy/dash_dist) if dash_dist > 0 else (0,0)
                    self.play_shoot_sound = True 
            elif self.state == "DASH":
                self.x += self.dash_dir_x * (current_speed * 6); self.y += self.dash_dir_y * (current_speed * 6)
                if self.state_timer > 20: self.state = "CHASE"; self.state_timer = 0

        elif self.b_type == "PURPLE":
            if self.state == "FLEE":
                dist = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)
                dx, dy = player_x - self.x, player_y - self.y
                dir_x, dir_y = (dx/dist, dy/dist) if dist > 0 else (0,0)
                    
                if dist < 300: self.x -= dir_x * current_speed; self.y -= dir_y * current_speed
                else: self.x += -dir_y * current_speed; self.y += dir_x * current_speed
                
                if self.state_timer > 180: self.state = "SUMMON"; self.state_timer = 0
            elif self.state == "SUMMON":
                if self.state_timer == 45:
                    for _ in range(3):
                        e = Enemy(level=self.spawn_level, is_elite=True)
                        e.x, e.y = self.x + random.randint(-70,70), self.y + random.randint(-70,70)
                        enemies.append(e)
                    self.play_shoot_sound = True
                if self.state_timer > 90: self.state = "FLEE"; self.state_timer = 0
            
        self.rect.center = (int(self.x), int(self.y))

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
            return
            
        elif self.state == "DEFEAT":
            progress = min(1, self.defeat_timer / 60)
            for i in range(5): pygame.draw.circle(surface, (255, 180, 0), self.rect.center, int(self.size + progress * 120 + i * 12), 3)
            core_size = int(self.size * (1 - progress * 0.7))
            pygame.draw.rect(surface, (255, 100, 0), pygame.Rect(0, 0, max(1, core_size), max(1, core_size)).move(self.rect.centerx - core_size//2, self.rect.centery - core_size//2))
            burst = int(progress * 10)
            for i in range(burst):
                angle = i * (math.pi * 2 / max(1, burst)) + self.defeat_timer * 0.3
                px, py = self.rect.centerx + math.cos(angle) * (self.size + 30 + progress * 80), self.rect.centery + math.sin(angle) * (self.size + 30 + progress * 80)
                pygame.draw.circle(surface, RED, (int(px), int(py)), 4)
            return

        anim_key = "boss_" + self.b_type
        anim_frames = animations.get(anim_key)
        
        if anim_frames:
            img = anim_frames[int(pygame.time.get_ticks() / 150) % len(anim_frames)]
            surface.blit(img, img.get_rect(center=self.rect.center))
        else:
            pygame.draw.rect(surface, (100, 200, 255) if self.frost_timer > 0 else self.color, self.rect)
        
        if self.b_type == "YELLOW" and self.state == "EVADE": pygame.draw.circle(surface, WHITE, self.rect.center, int(self.size/2) + 15, 3)
        elif self.b_type == "YELLOW" and self.state == "CHARGE": pygame.draw.circle(surface, RED, self.rect.center, int(self.size/2) + max(0, 30 - int(self.state_timer / 2)), 2)
        elif self.b_type == "RED" and self.state == "WARN": pygame.draw.line(surface, RED, self.rect.center, (int(self.aim_x), int(self.aim_y)), max(1, int(self.state_timer / 8)))
        elif self.b_type == "PURPLE" and self.state == "SUMMON": pygame.draw.circle(surface, DARK_PURPLE, self.rect.center, int(self.size/2) + min(60, self.state_timer), 3)

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vel_x, self.vel_y = random.uniform(-6, 6), random.uniform(-6, 6)
        self.timer, self.size, self.color = random.randint(15, 30), random.randint(4, 8), color
    def update(self):
        self.x += self.vel_x; self.y += self.vel_y; self.timer -= 1; self.size -= 0.25
        if self.size < 0: self.size = 0
    def draw(self, surface):
        if self.size > 0: pygame.draw.rect(surface, self.color, (int(self.x), int(self.y), int(self.size), int(self.size)))

class DamageText:
    def __init__(self, x, y, damage, color=WHITE):
        self.x, self.y, self.damage, self.color = x, y, int(damage), color
        self.timer, self.vel_y, self.offset_x = 40, -1.5, random.randint(-15, 15)
    def update(self):
        self.y += self.vel_y; self.timer -= 1
        self.alpha = max(0, int((self.timer / 40) * 255))
    def draw(self, surface):
        if self.timer > 0:
            txt_surf = font.render(f"-{self.damage}", True, self.color)
            txt_surf.set_alpha(self.alpha)
            surface.blit(txt_surf, (int(self.x + self.offset_x), int(self.y)))

class DropItem:
    def __init__(self, x, y, item_type="EXP", amount=None):
        self.x, self.y, self.item_type = x, y, item_type
        self.rect = pygame.Rect(0, 0, 14, 14)
        self.anim_offset = random.random() * 10
        self.amount = amount if amount else (35 if item_type == "EXP" else 25)
        
    def update(self, p_x, p_y, mag_rad):
        dist = math.sqrt((self.x - p_x)**2 + (self.y - p_y)**2)
        if dist < mag_rad and dist > 0:
            self.x += ((p_x - self.x) / dist) * 8; self.y += ((p_y - self.y) / dist) * 8 
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface):
        img_key = f"drop_{self.item_type}"
        img = images.get(img_key)
        float_y = self.y + math.sin(pygame.time.get_ticks()*0.005 + self.anim_offset) * 3
        
        if img: surface.blit(img, img.get_rect(center=(int(self.x), int(float_y))))
        else:
            if self.item_type == "EXP": pygame.draw.polygon(surface, EXP_COLOR,[(self.x, float_y-6), (self.x+6, float_y), (self.x, float_y+6), (self.x-6, float_y)])
            elif self.item_type == "HP": pygame.draw.rect(surface, HP_COLOR, (self.x-6, float_y-2, 12, 4)); pygame.draw.rect(surface, HP_COLOR, (self.x-2, float_y-6, 4, 12))
            elif self.item_type == "SHIELD": pygame.draw.circle(surface, SHIELD_COLOR, (int(self.x), int(float_y)), 6)

# ==========================================
# 🛑 中文化升級系統 (結合多種增益)
# ==========================================
upgrade_options =[
    {"title": "生命躍升", "desc": ["最大血量 +50", "並恢復當前血量"]},
    {"title": "超頻運轉", "desc": ["武器冷卻減少", "射速大幅提升"]},
    {"title": "能量飲料", "desc": ["體力恢復加快", "衝刺更加頻繁"]},
    {"title": "彈幕擴張", "desc": ["子彈發射數 +1", "形成扇形擴散"]},
    {"title": "高能彈芯", "desc": ["子彈傷害增加", "打王更有效率"]},
    {"title": "備用電池", "desc": ["最大體力增加", "衝刺次數提升"]},
    {"title": "輕量推進", "desc": ["衝刺消耗降低", "更容易連續閃避"]},
    {"title": "離子靴", "desc": ["移動速度提升", "走位更加靈活"]},
    {"title": "磁吸核心", "desc": ["經驗吸取範圍", "大幅度增加"]},
    {"title": "穩定槍管", "desc": ["散射角度縮小", "多重彈幕更集中"]},
    {"title": "延長燃燒", "desc": ["衝刺時間增加", "位移距離更遠"]},
    {"title": "急救模組", "desc": ["立即恢復血量", "最多恢復 60"]},
    {"title": "相位護盾", "desc": ["受傷免傷延長", "更能脫離包圍"]},
    {"title": "裝甲鍍層", "desc": ["受到傷害降低", "硬扛能力提升"]},
    {"title": "爆燃推進", "desc": ["衝刺速度增加", "瞬間拉開距離"]},
    {"title": "戰術背包", "desc": ["血量與體力上限", "小幅同步提升"]},
    {"title": "回收矩陣", "desc": ["吸取範圍增加", "體力恢復小幅提升"]},
    {"title": "能量擴容", "desc": ["最大能量 +50", "施放更多大絕招"]}
]

cards =[pygame.Rect(0, 0, 220, 280), pygame.Rect(0, 0, 220, 280), pygame.Rect(0, 0, 220, 280)]
confirm_upgrade_button = pygame.Rect(0, 0, 220, 60)
current_upgrade_choices =[]
selected_upgrade_position = None
chosen_upgrades =[]

# 選單 UI 按鈕
start_button = pygame.Rect(0, 0, 200, 60)
changelog_button = pygame.Rect(0, 0, 200, 60)
changelog_close_button = pygame.Rect(0, 0, 200, 55)
restart_button = pygame.Rect(0, 0, 200, 60)
menu_button = pygame.Rect(0, 0, 200, 60)
show_changelog, changelog_scroll = False, 0

CHANGELOG =[
    "v1.152",
    "- 融合智慧動態圖片引擎，支援動態換圖",
    "- 開放世界無限跟隨攝影機機制上線！",
    "- 新增18種強大多重技能卡牌庫",
    "v1.151",
    "- 移除追蹤彈，新增更多強化卡牌",
    "- 小兵會隨玩家等級獲得血量、速度與護盾成長",
    "v1.05",
    "- Boss 強化：新增進場與死亡華麗動畫",
    "- 精英小怪邪惡脈衝效果更新",
]

def choose_upgrade_cards():
    global current_upgrade_choices, selected_upgrade_position
    card_count = min(3, len(upgrade_options))
    current_upgrade_choices = random.sample(range(len(upgrade_options)), card_count)
    selected_upgrade_position = None

def add_chosen_upgrade(choice):
    title = upgrade_options[choice]["title"]
    for upgrade in chosen_upgrades:
        if upgrade["title"] == title:
            upgrade["count"] += 1; return
    chosen_upgrades.append({"title": title, "count": 1})

def apply_upgrade(choice):
    global game_state, selected_upgrade_position
    if choice == 0: player.max_hp += 50; player.hp += 50 
    elif choice == 1: player.shoot_delay = max(2, player.shoot_delay - 2) 
    elif choice == 2: player.stamina_regen += 0.3
    elif choice == 3: player.bullet_count += 1
    elif choice == 4: player.bullet_damage_bonus += 5
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
    elif choice == 17: player.max_energy += 50
    add_chosen_upgrade(choice)
    current_upgrade_choices.clear(); selected_upgrade_position = None
    game_state = "PLAYING"             

def draw_upgrade_summary(surface, x, y, max_items=6, title="已選強化"):
    panel_width, row_height = 260, 28
    hidden_count = max(0, len(chosen_upgrades) - max_items)
    row_count = max(1, min(len(chosen_upgrades), max_items))
    panel_height = 44 + row_count * row_height + (row_height if hidden_count else 0)
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((18, 20, 30, 185))
    surface.blit(panel, (x, y))
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

def draw_changelog_popup(surface):
    popup = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 250, 700, 500)
    panel = pygame.Surface((popup.width, popup.height), pygame.SRCALPHA)
    panel.fill((18, 20, 32, 235)); surface.blit(panel, popup.topleft)
    pygame.draw.rect(surface, WHITE, popup, 3, border_radius=12)

    title = large_font.render("更新日誌", True, YELLOW)
    surface.blit(title, (popup.centerx - title.get_width()//2, popup.y + 25))

    content_rect = pygame.Rect(popup.x + 40, popup.y + 90, popup.width - 80, popup.height - 180)
    content_lines =[]
    for line in CHANGELOG:
        color = YELLOW if line.startswith("v") else WHITE
        wrapped = wrap_text(line, font, content_rect.width - 20)
        for wrapped_line in wrapped: content_lines.append((wrapped_line, color))
        content_lines.append(("", WHITE))

    content_height = max(content_rect.height, len(content_lines) * 34 + 10)
    max_scroll = max(0, content_height - content_rect.height)
    global changelog_scroll; scroll_y = min(changelog_scroll, max_scroll)
    content_surface = pygame.Surface((content_rect.width, content_height), pygame.SRCALPHA)

    for i, (line, color) in enumerate(content_lines):
        if line: content_surface.blit(font.render(line, True, color), (0, 6 + i * 34))

    surface.blit(content_surface, content_rect.topleft, pygame.Rect(0, scroll_y, content_rect.width, content_rect.height))
    pygame.draw.rect(surface, GRAY, content_rect, 1)

    changelog_close_button.center = (popup.centerx, popup.bottom - 40)
    close_color = RED if changelog_close_button.collidepoint(pygame.mouse.get_pos()) else (150, 50, 50)
    pygame.draw.rect(surface, close_color, changelog_close_button, border_radius=10); pygame.draw.rect(surface, WHITE, changelog_close_button, 3, border_radius=10)
    close_txt = font.render("關閉", True, WHITE)
    surface.blit(close_txt, (changelog_close_button.centerx - close_txt.get_width()//2, changelog_close_button.centery - close_txt.get_height()//2))

def reset_game(initial_state="PLAYING"):
    global player, bullets, enemy_bullets, enemies, particles, items, trails, damage_texts
    global boss, boss_active, boss_defeated, next_boss_level, game_state, shoot_cooldown, key_buffer
    global current_upgrade_choices, selected_upgrade_position, chosen_upgrades, show_changelog, changelog_scroll
    global global_offset_x, global_offset_y
    
    player = Player()
    bullets, enemy_bullets, enemies, particles, items, trails, damage_texts = [], [], [], [], [], [],[]
    boss = None
    boss_active = False
    boss_defeated = False
    next_boss_level = 5
    shoot_cooldown = 0
    key_buffer =[]
    global_offset_x, global_offset_y = 0, 0
    
    current_upgrade_choices =[]
    selected_upgrade_position = None
    chosen_upgrades =[]
    show_changelog = False
    changelog_scroll = 0
    
    stop_sound("boss_bgm")
    try: pygame.mixer.music.play(-1)
    except: pass
    game_state = initial_state

reset_game("MENU")
SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY_EVENT, 600)
dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
dim_surface.fill((0, 0, 0, 180))

boss_warning_timer = 0
running = True
while running:
    # --- UI 元素自動對齊置中 ---
    start_button.center = (WIDTH//2, HEIGHT//2 + 50)
    changelog_button.center = (WIDTH//2, HEIGHT//2 + 130)
    restart_button.center = (WIDTH//2 - 120, HEIGHT//2 + 100)
    menu_button.center = (WIDTH//2 + 120, HEIGHT//2 + 100)
    cards[0].center = (WIDTH//2 - 240, HEIGHT//2)
    cards[1].center = (WIDTH//2, HEIGHT//2)
    cards[2].center = (WIDTH//2 + 240, HEIGHT//2)
    confirm_upgrade_button.center = (WIDTH//2, HEIGHT//2 + 180)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if event.type == pygame.VIDEORESIZE:
            if not fullscreen_mode:
                WIDTH, HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                dim_surface.fill((0, 0, 0, 180))
                
        if game_state == "MENU" and show_changelog and event.type == pygame.MOUSEWHEEL:
            changelog_scroll = max(0, changelog_scroll - event.y * 45)
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if game_state == "PLAYING": game_state = "PAUSED"
            elif game_state == "PAUSED": game_state = "PLAYING"
            
        if game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: reset_game()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_button.collidepoint(event.pos): reset_game()
                elif menu_button.collidepoint(event.pos): reset_game("MENU")
        elif game_state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_changelog:
                    if changelog_close_button.collidepoint(event.pos): show_changelog = False
                elif start_button.collidepoint(event.pos): reset_game("PLAYING")
                elif changelog_button.collidepoint(event.pos): show_changelog, changelog_scroll = True, 0
        elif game_state == "PAUSED":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 70, 220, 60).collidepoint(event.pos): game_state = "PLAYING"
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 70, 220, 60).collidepoint(event.pos): reset_game("MENU")
                elif pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 150, 220, 60).collidepoint(event.pos): reset_game()
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 150, 220, 60).collidepoint(event.pos): running = False
        elif game_state == "LEVEL_UP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected_upgrade_position is not None and confirm_upgrade_button.collidepoint(event.pos):
                    apply_upgrade(current_upgrade_choices[selected_upgrade_position])
                else:
                    for i, card in enumerate(cards):
                        if i < len(current_upgrade_choices) and card.collidepoint(event.pos):
                            selected_upgrade_position = i
                            break
        elif game_state == "PLAYING":
            if event.type == SPAWN_ENEMY_EVENT: 
                elite_chance = min(0.03 + player.level * 0.006, 0.15)
                enemies.append(Enemy(player.level, is_elite=random.random() < elite_chance))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen_mode = not fullscreen_mode
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if fullscreen_mode else pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                    WIDTH, HEIGHT = screen.get_size()
                    dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    dim_surface.fill((0, 0, 0, 180))
                
                key_buffer.append(event.key)
                if len(key_buffer) > len(CHEAT_CODE): key_buffer.pop(0) 
                if key_buffer == CHEAT_CODE:
                    player.god_mode = not player.god_mode
                    play_sound("levelup"); key_buffer =[] 
                
                if event.key == pygame.K_e:
                    player.current_weapon_idx = (player.current_weapon_idx + 1) % len(player.weapons)
                    play_sound("exp")

    if game_state == "PLAYING":
        if player.level >= next_boss_level and not boss_active:
            boss = Boss(random.choice(["YELLOW", "RED", "PURPLE"]), next_boss_level)
            boss_active, boss_warning_timer = True, 120
            try: pygame.mixer.music.stop()
            except: pass
            play_sound("boss_bgm", loop=-1) 

        mouse_btns, (mouse_x, mouse_y) = pygame.mouse.get_pressed(), pygame.mouse.get_pos()
        current_wep = player.weapons[player.current_weapon_idx]

        if mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing:
            base_dir = pygame.math.Vector2(mouse_x - player.rect.centerx, mouse_y - player.rect.centery)
            if base_dir.length() > 0: base_dir.normalize_ip()
            start_angle = -(player.bullet_count - 1) * player.bullet_spread / 2
            
            for c in range(player.bullet_count):
                angle_offset = start_angle + c * player.bullet_spread
                shot_dir = base_dir.rotate(angle_offset)
                
                if current_wep.bullet_type == "shotgun":
                    for i in range(-2, 3):
                        final_dir = shot_dir.rotate(i * 12)
                        target_pos = player.pos + final_dir * 100
                        bullets.append(Bullet(player.rect.centerx, player.rect.centery, target_pos.x, target_pos.y, current_wep))
                elif current_wep.bullet_type == "flamethrower":
                    target_pos = player.pos + shot_dir * 100
                    bullets.append(Bullet(player.rect.centerx, player.rect.centery, target_pos.x + random.randint(-40, 40), target_pos.y + random.randint(-40, 40), current_wep))
                else:
                    target_pos = player.pos + shot_dir * 100
                    bullets.append(Bullet(player.rect.centerx, player.rect.centery, target_pos.x, target_pos.y, current_wep))
            
            shoot_cooldown = current_wep.shoot_delay
            play_sound(current_wep.sound_name)
            
        if mouse_btns[2] and player.skill_cd <= 0 and player.energy >= player.skill_cost and not player.is_dashing:
            player.energy -= player.skill_cost; player.skill_cd = player.skill_max_cd; play_sound("shoot_cannon") 
            temp_wep = Weapon("大絕", 0, "piercing", 50) 
            for i in range(16):
                angle = math.radians(i * (360 / 16))
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, player.rect.centerx + math.cos(angle)*100, player.rect.centery + math.sin(angle)*100, temp_wep))

        if shoot_cooldown > 0: shoot_cooldown -= 1
        player.update()
        
        if player.is_dashing: trails.append(DashTrail(player.rect.centerx, player.rect.centery, player.size))
        for t in trails[::-1]:
            t.update()
            if t.life <= 0: trails.remove(t)
            
        for b in bullets[::-1]:
            b.update()
            if getattr(b, 'explode', False):
                play_sound("shoot_cannon") 
                for _ in range(30): particles.append(Particle(b.x, b.y, ORANGE))
                for e in enemies[::-1]:
                    if math.sqrt((e.x - b.x)**2 + (e.y - b.y)**2) < 120: 
                        e.hp -= b.damage
                        damage_texts.append(DamageText(e.x, e.y - 15, b.damage, YELLOW if b.damage >= 30 else WHITE))
                        if e.hp <= 0: 
                            if random.random() < e.exp_drop_chance: items.append(DropItem(e.x, e.y, "EXP"))
                            enemies.remove(e)
                if boss_active and math.sqrt((boss.x - b.x)**2 + (boss.y - b.y)**2) < 150: 
                    boss.hp -= b.damage
                    damage_texts.append(DamageText(boss.x, boss.y - 30, b.damage, YELLOW if b.damage >= 30 else WHITE))
                bullets.remove(b)
                continue
            if b.lifespan <= 0 or not screen.get_rect().inflate(500, 500).colliderect(b.rect): bullets.remove(b)
            
        for eb in enemy_bullets[::-1]:
            eb.update()
            if not screen.get_rect().inflate(500, 500).colliderect(eb.rect): enemy_bullets.remove(eb)
            
        for dt in damage_texts[::-1]:
            dt.update()
            if dt.timer <= 0: damage_texts.remove(dt)    
            
        for e in enemies: e.update(player.x, player.y, enemies)
            
        for p in particles[::-1]:
            p.update(); 
            if p.timer <= 0: particles.remove(p)

        if boss_warning_timer > 0: boss_warning_timer -= 1
        
        if boss_active:
            boss.update(player.x, player.y, bullets, enemies, enemy_bullets)
            if boss.play_shoot_sound: play_sound("shoot_normal")
            
        if boss_active and boss.state == "DEFEAT" and boss.defeat_timer > 60:
            boss_active, boss_defeated = False, True
            next_boss_level += 5
            stop_sound("boss_bgm")
            try: pygame.mixer.music.play(-1)
            except: pass

        for b in bullets[::-1]:
            hit_something = False
            for e in enemies[::-1]:
                if b.rect.colliderect(e.rect):
                    if b.b_type == "frost": e.frost_timer = 120 
                    if b.b_type == "cannon": 
                        push_dist = math.sqrt((e.x - player.x)**2 + (e.y - player.y)**2)
                        if push_dist > 0: e.x += ((e.x - player.x)/push_dist)*30; e.y += ((e.y - player.y)/push_dist)*30 
                    elif b.b_type == "flame_grenade": b.explode = True; break
                        
                    shield_damage = min(e.shield, b.damage)
                    e.shield -= shield_damage
                    actual_damage = b.damage - shield_damage
                    e.hp -= actual_damage
                    
                    damage_texts.append(DamageText(e.x, e.y - 15, b.damage, YELLOW if b.damage >= 30 else WHITE))
                    hit_something = True
                    for _ in range(5): particles.append(Particle(e.x, e.y, b.color))
                    play_sound("hit")
                    
                    if e.hp <= 0:
                        for _ in range(12 if e.is_elite else 6): particles.append(Particle(e.x, e.y, RED))
                        if random.random() < e.exp_drop_chance: 
                            gem_count = 3 if e.is_elite else 1
                            for _ in range(gem_count): items.append(DropItem(e.x + random.randint(-12,12), e.y + random.randint(-12,12), "EXP", 35))
                        if random.random() < e.health_drop_chance: 
                            items.append(DropItem(e.x, e.y, "HP", 40 if e.is_elite else 25))
                        enemies.remove(e)
            
            if getattr(b, 'explode', False): continue 

            if boss_active and b.rect.colliderect(boss.rect):
                hit_something = True
                if boss.state == "EVADE":
                    for _ in range(5): particles.append(Particle(boss.x, boss.y, GRAY))
                elif boss.state != "DEFEAT":
                    if b.b_type == "frost": boss.frost_timer = 60 
                    boss.hp -= b.damage
                    damage_texts.append(DamageText(boss.x, boss.y - 30, b.damage, YELLOW if b.damage >= 30 else WHITE))
                    for _ in range(8): particles.append(Particle(boss.x, boss.y, YELLOW))
                    play_sound("hit")
                    if boss.hp <= 0:
                        boss.state, boss.defeat_timer = "DEFEAT", 0
                        for _ in range(40): items.append(DropItem(boss.x + random.randint(-60,60), boss.y + random.randint(-60,60), "EXP", 35))
                        for _ in range(5): items.append(DropItem(boss.x + random.randint(-40,40), boss.y + random.randint(-40,40), random.choice(["HP", "SHIELD"]), 25))
                        for _ in range(50): particles.append(Particle(boss.x, boss.y, YELLOW))
            if hit_something and not b.is_piercing and b in bullets: bullets.remove(b)

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
            if player.rect.colliderect(e.rect): player_take_damage(e.damage)
        for eb in enemy_bullets[::-1]:
            if player.rect.colliderect(eb.rect): player_take_damage(25); enemy_bullets.remove(eb) if eb in enemy_bullets else None
        if boss_active and boss.state != "DEFEAT" and player.rect.colliderect(boss.rect): player_take_damage(40) 

        for item in items[::-1]:
            item.update(player.x, player.y, player.magnet_radius)
            if player.rect.colliderect(item.rect):
                items.remove(item)
                if item.item_type == "EXP": player.exp += item.amount; play_sound("exp") 
                elif item.item_type == "HP": player.hp = min(player.max_hp, player.hp + item.amount); play_sound("exp")
                elif item.item_type == "SHIELD": player.shield = min(player.max_shield, player.shield + item.amount); play_sound("exp")

                if player.exp >= player.max_exp:
                    player.level += 1; player.exp = 0; player.max_exp = int(player.max_exp * 1.5) 
                    choose_upgrade_cards()
                    game_state = "LEVEL_UP"; play_sound("levelup") 

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
        
        controls_title = font.render("操作說明:", True, YELLOW)
        screen.blit(controls_title, (WIDTH//2 - controls_title.get_width()//2, HEIGHT//2 + 180))
        controls = ["移動: WASD", "射擊: 滑鼠左鍵", "大絕招: 滑鼠右鍵", "衝刺: Q鍵 或 SPACE", "切換武器: E鍵", "暫停: ESC", "全螢幕: F11"]
        for i, c in enumerate(controls): screen.blit(small_font.render(c, True, GRAY), (WIDTH//2 - small_font.size(c)[0]//2, HEIGHT//2 + 215 + i*25))

        if show_changelog: draw_changelog_popup(screen)
        
    else:
        if images.get("bg"):
            bg_img = pygame.transform.scale(images["bg"], (WIDTH, HEIGHT))
            bg_x, bg_y = -global_offset_x % WIDTH, -global_offset_y % HEIGHT
            screen.blit(bg_img, (bg_x, bg_y)); screen.blit(bg_img, (bg_x - WIDTH, bg_y))
            screen.blit(bg_img, (bg_x, bg_y - HEIGHT)); screen.blit(bg_img, (bg_x - WIDTH, bg_y - HEIGHT))
        else: screen.fill(BLACK)
        
        for i in items: i.draw(screen)
        for p in particles: p.draw(screen)
        for b in bullets: b.draw(screen)
        for eb in enemy_bullets: eb.draw(screen) 
        for e in enemies: e.draw(screen)
        for t in trails: t.draw(screen)
        for dt in damage_texts: dt.draw(screen)
        if boss_active: boss.draw(screen) 
        
        player.draw(screen, player.weapons[player.current_weapon_idx] if game_state in ["PLAYING", "PAUSED"] else None)
        
        # UI
        pygame.draw.rect(screen, GRAY, (20, 20, 250, 15)); pygame.draw.rect(screen, BLUE, (20, 20, 250 * (player.exp / player.max_exp), 15))
        screen.blit(font.render(f"等級: {player.level}", True, WHITE), (280, 15))
        pygame.draw.rect(screen, GRAY, (20, 45, 200, 15)); pygame.draw.rect(screen, GREEN if player.hp > 30 else RED, (20, 45, 200 * (max(0, player.hp) / player.max_hp), 15))
        screen.blit(font.render(f"血量", True, WHITE), (230, 40))
        pygame.draw.rect(screen, GRAY, (20, 70, 200, 10)); pygame.draw.rect(screen, SHIELD_COLOR, (20, 70, 200 * (max(0, player.shield) / player.max_shield), 10))
        screen.blit(font.render("護盾", True, WHITE), (230, 65))
        pygame.draw.rect(screen, GRAY, (20, 95, 150, 10)); pygame.draw.rect(screen, ORANGE, (20, 95, 150 * (player.stamina / player.max_stamina), 10))
        screen.blit(font.render("體力 (Q/空白)", True, WHITE), (180, 87)) 
        pygame.draw.rect(screen, GRAY, (20, 120, 150, 10)); pygame.draw.rect(screen, CYAN, (20, 120, 150 * (player.energy / player.max_energy), 10))
        screen.blit(font.render("能量", True, WHITE), (180, 112))

        wep_name = player.weapons[player.current_weapon_idx].name
        screen.blit(font.render(f"武器: {wep_name} (E 鍵切換)", True, WHITE), (20, 145))
        wep_icon = images.get("icon_" + wep_name)
        if wep_icon: screen.blit(wep_icon, (20, 175))

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
            boss_name = {"YELLOW": "幾何守衛", "RED": "鮮血狂戰士", "PURPLE": "虛空召喚師"}[boss.b_type]
            
            if boss.state == "ENTRANCE":
                screen.blit(font.render("✦ BOSS 降臨 ✦", True, YELLOW), (WIDTH//2 - 80, HEIGHT//2 - 200))
            elif boss_warning_timer > 0:
                screen.blit(font.render(f"⚠️ 警告：偵測到極度危險異常實體 - 【{boss_name}】", True, RED), (WIDTH//2 - 250, HEIGHT - 110))
            else:
                boss_txt = font.render(f"BOSS Lv.{boss.spawn_level} - 【{boss_name}】", True, WHITE)
                screen.blit(boss_txt, (WIDTH//2 - boss_txt.get_width()//2, HEIGHT - 110))

        if game_state == "LEVEL_UP":
            screen.blit(dim_surface, (0, 0)) 
            title = large_font.render("升級！選擇強化後按確認", True, YELLOW)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
            
            for i, card in enumerate(cards):
                if i >= len(current_upgrade_choices): continue
                upgrade = upgrade_options[current_upgrade_choices[i]]
                is_selected = (selected_upgrade_position == i)
                color = GREEN if is_selected else BLUE if card.collidepoint(pygame.mouse.get_pos()) else CARD_COLOR
                pygame.draw.rect(screen, color, card, border_radius=10)
                pygame.draw.rect(screen, YELLOW if is_selected else WHITE, card, 6 if is_selected else 3, border_radius=10) 
                
                opt_title = font.render(upgrade["title"], True, WHITE)
                screen.blit(opt_title, (card.centerx - opt_title.get_width()//2, card.y + 30))
                screen.blit(font.render(upgrade["desc"][0], True, YELLOW), (card.centerx - font.size(upgrade["desc"][0])[0]//2, card.y + 110))
                screen.blit(font.render(upgrade["desc"][1], True, YELLOW), (card.centerx - font.size(upgrade["desc"][1])[0]//2, card.y + 150))
            
            confirm_ready = selected_upgrade_position is not None
            confirm_color = GREEN if confirm_ready and confirm_upgrade_button.collidepoint(pygame.mouse.get_pos()) else (50, 150, 50) if confirm_ready else GRAY
            pygame.draw.rect(screen, confirm_color, confirm_upgrade_button, border_radius=10)
            pygame.draw.rect(screen, WHITE, confirm_upgrade_button, 3, border_radius=10)
            c_txt = font.render("確認選擇", True, WHITE)
            screen.blit(c_txt, (confirm_upgrade_button.centerx - c_txt.get_width()//2, confirm_upgrade_button.centery - c_txt.get_height()//2))

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
                txt_surf = font.render(txt, True, WHITE)
                screen.blit(txt_surf, (btn.centerx - txt_surf.get_width()//2, btn.centery - txt_surf.get_height()//2))
            
            draw_upgrade_summary(screen, WIDTH//2 - 130, HEIGHT//2 - 120, max_items=5, title="本局強化紀錄")

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
