import pygame
import random
import math
import os
import ctypes

# 初始化遊戲
pygame.init()
pygame.mixer.init()

# 設定視窗
WIDTH, HEIGHT = 1024,768
fullscreen_mode = False
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("霓虹驅魔人 - 終極完全體 (純淨新手版)")
clock = pygame.time.Clock()
FPS = 60
WINDOW_FOCUS_GAINED = getattr(pygame, "WINDOWFOCUSGAINED", None)

def switch_to_english_input():
    if os.name != "nt": 
        return
    try:
        hwnd = pygame.display.get_wm_info().get("window")
        if hwnd:
            english_layout = ctypes.windll.user32.LoadKeyboardLayoutW("00000409", 1)
            ctypes.windll.user32.ActivateKeyboardLayout(english_layout, 0)
            ctypes.windll.user32.PostMessageW(hwnd, 0x0050, 0, english_layout)
    except Exception: 
        pass

switch_to_english_input()

# 顏色定義RGB
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
CYAN = (0, 255, 255) # 青色

CARD_COLOR = (30, 30, 40)   # 卡片
SHIELD_COLOR = (0, 102, 204)    # 護盾
EXP_COLOR = (124, 252, 0)   # 經驗值
HP_COLOR = (255, 0, 0)    # 血量

# 遊戲模式與生成頻率定義
NORMAL_MODE = 0
HARD_MODE = 1


# 不同模式下的敵人基礎生成間隔 (單位: 幀數)
NORMAL_SPAWN_INTERVAL = 60    # 1秒生一隻
HARD_SPAWN_INTERVAL = 40      # 約0.66秒生一隻


# 字體設定，優先尋找微軟正黑體，若無則找蘋方體(Mac)或黑體
CHINESE_FONTS = "microsoftjhenghei,pingfangtc,stheiti,simhei"
font = pygame.font.SysFont(CHINESE_FONTS, 28)
large_font = pygame.font.SysFont(CHINESE_FONTS, 48)
small_font = pygame.font.SysFont(CHINESE_FONTS, 22)
tiny_font = pygame.font.SysFont(CHINESE_FONTS, 18)

# 遊戲模式與常數
NORMAL_MODE = "NORMAL"
CHALLENGE_MODE = "CHALLENGE"
game_mode = NORMAL_MODE
SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
bg_offset_x = 0
bg_offset_y = 0

# 動畫以及貼圖系統 ###############################################################################
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
            if size != None: 
                img = pygame.transform.scale(img, size)
            images[name] = img
        else: 
            images[name] = None
    except: 
        images[name] = None

def load_animation(name, folder_name, size):
    folder_path = os.path.join(IMAGE_DIR, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path) 
        animations[name] = None
        return
    frames =[]
    file_list = sorted(os.listdir(folder_path))
    for i in range(len(file_list)):
        file = file_list[i]
        if file.endswith(".png") or file.endswith(".jpg"):
            img = pygame.image.load(os.path.join(folder_path, file)).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
    if len(frames) > 0:
        animations[name] = frames
    else:
        animations[name] = None

# 載入背景與掉落物
load_image("bg", "bg.png", (WIDTH, HEIGHT))
load_image("drop_EXP", "drop_exp.png", (20, 20))
load_image("drop_HP", "drop_hp.png", (20, 20))
load_image("drop_SHIELD", "drop_shield.png", (20, 20))

# 載入子彈
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

# 載入動畫
load_animation("player", "player", (40, 40))
load_animation("enemy_normal", "enemy_normal", (35, 35))
load_animation("enemy_elite", "enemy_elite", (50, 50))
load_animation("boss_YELLOW", "boss_yellow", (100, 100))
load_animation("boss_RED", "boss_red", (100, 100))
load_animation("boss_PURPLE", "boss_purple", (100, 100))

# 音效和音樂(BGM)系統 ################################################################################
sounds = {}
def load_sound(name, filename):
    try:
        sound_path = os.path.join(BASE_DIR, filename)
        sounds[name] = pygame.mixer.Sound(sound_path)
        sounds[name].set_volume(0.3)
    except: 
        sounds[name] = None 

# 載入系統音效
load_sound("dash", "dash.wav")
load_sound("hit", "hit.wav")
load_sound("levelup", "levelup.wav")
load_sound("hurt", "hurt.wav")
load_sound("boss_bgm", "boss.wav") 
load_sound("gameover", "gameover.wav")
load_sound("exp", "exp.wav") 

# 通用槍枝音效
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
        else: 
            sounds[weapon_key] = sounds.get(fallback_key)
    except: 
        sounds[weapon_key] = sounds.get(fallback_key)
# 12 把武器設定專屬音效，也就是將特定的音效檔案載入遊戲，並將它與某個武器的射擊動作綁定(音效標籤/ID、檔案路徑、動作分類/回退機制)
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
    bgm_path = os.path.join(BASE_DIR, "bgm.mp3")# 背景音樂 (BGM) 載入設定
    pygame.mixer.music.load(bgm_path)
    pygame.mixer.music.set_volume(0.2) 
except: 
    pass

def play_sound(name, loop=0):
    if name in sounds:
        if sounds[name] != None:
            sounds[name].play(loops=loop)

def stop_sound(name):
    if name in sounds:
        if sounds[name] != None:
            sounds[name].stop()


# 遊戲類別定義


# 秘技密碼 ：上上下下左右左右BABA (無敵模式)
CHEAT_CODE = [
    pygame.K_UP, pygame.K_UP, 
    pygame.K_DOWN, pygame.K_DOWN, 
    pygame.K_LEFT, pygame.K_RIGHT, 
    pygame.K_LEFT, pygame.K_RIGHT, 
    pygame.K_b, pygame.K_a,
    pygame.K_b, pygame.K_a
]
key_buffer =[] 

class Weapon:
    def __init__(self, name, shoot_delay, bullet_type, damage, sound_name="shoot_normal"):
        self.name = name
        self.shoot_delay = shoot_delay
        self.bullet_type = bullet_type
        self.damage = damage
        self.sound_name = sound_name
        load_image("gun_" + name, "gun_" + name + ".png", (45, 18))
        load_image("icon_" + name, "icon_" + name + ".png", (60, 30))

WEAPON_TYPES = {}
WEAPON_TYPES["手槍"] = Weapon("手槍", 20, "normal", 20, "snd_pistol")
WEAPON_TYPES["狙擊槍"] = Weapon("狙擊槍", 50, "piercing", 45, "snd_sniper")
WEAPON_TYPES["散彈槍"] = Weapon("散彈槍", 30, "shotgun", 20, "snd_shotgun")
WEAPON_TYPES["機槍"] = Weapon("機槍", 15, "piercing", 20, "snd_mg")
WEAPON_TYPES["火焰噴射器"] = Weapon("火焰噴射器", 3, "flamethrower", 4, "snd_flamethrower")
WEAPON_TYPES["雷射槍"] = Weapon("雷射槍", 25, "laser", 25, "snd_laser")
WEAPON_TYPES["電磁炮"] = Weapon("電磁炮", 60, "cannon", 50, "snd_cannon")
WEAPON_TYPES["冰霜發射器"] = Weapon("冰霜發射器", 5, "frost", 6, "snd_frost")
WEAPON_TYPES["重型機槍"] = Weapon("重型機槍", 17, "piercing", 25, "snd_heavy_mg")
WEAPON_TYPES["步槍"] = Weapon("步槍", 40, "piercing", 30, "snd_rifle")
WEAPON_TYPES["火焰榴彈發射器"] = Weapon("火焰榴彈發射器", 65, "flame_grenade", 70, "snd_grenade")
WEAPON_TYPES["電漿發射器"] = Weapon("電漿發射器", 30, "plasma", 30, "snd_plasma")

class Player:
    def __init__(self):
        # 玩家永遠在畫面正中央
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        self.size = 30
        self.base_speed = 5
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        
        self.weapons =[]
        for key in WEAPON_TYPES:
            self.weapons.append(WEAPON_TYPES[key])
        self.current_weapon_idx = 0
        self.anim_timer = 0
        
        # A3 升級強化數值
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
        
        self.exp = 0
        self.level = 1
        self.max_exp = 100
        self.magnet_radius = 60
        
        self.max_hp = 100
        self.hp = 100
        self.max_shield = int(self.max_hp * 0.2)
        self.shield = self.max_shield
        self.shield_regen_rate = 0.18
        self.shield_regen_delay = 150
        self.shield_regen_timer = 0
        self.invincible_timer = 0
        self.invincible_duration = 60
        
        self.max_stamina = 100
        self.stamina = 100
        self.dash_cost = 35
        self.stamina_regen = 0.5   
        
        self.is_dashing = False
        self.dash_speed = 22
        self.dash_duration = 8
        self.dash_timer = 0
        self.dash_dir_x = 0
        self.dash_dir_y = 0
        
        self.max_energy = 100
        self.energy = 100
        self.energy_regen = 0.2     
        self.skill_cd = 0
        self.skill_max_cd = 600     
        self.skill_cost = 50        
        
        self.god_mode = False 
        
        # 困難模式彈藥系統
        self.pistol_mag_size = 45
        self.sniper_mag_size = 7
        self.pistol_ammo = self.pistol_mag_size
        self.sniper_ammo = self.sniper_mag_size
        self.reload_timer = 0
        self.reload_duration = 90
        self.reloading_weapon = "None"

    @property
    def pos(self):
        return pygame.math.Vector2(self.x, self.y)

    def get_muzzle_pos(self, world_mouse):
        dx = world_mouse.x - self.x
        dy = world_mouse.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            dir_x = dx / dist
            dir_y = dy / dist
        else:
            dir_x = 1
            dir_y = 0

        side_x = -dir_y
        side_y = dir_x
        weapon_reach = 25
        muzzle_x = self.x + dir_x * weapon_reach + side_x * (self.size * 0.2)
        muzzle_y = self.y + dir_y * weapon_reach + side_y * (self.size * 0.2)
        return pygame.math.Vector2(muzzle_x, muzzle_y)

    def current_weapon_type(self):
        w_type = self.weapons[self.current_weapon_idx].bullet_type
        if w_type == "piercing" or w_type == "laser" or w_type == "cannon" or w_type == "plasma":
            return "sniper"
        else:
            return "pistol"

    def can_fire_current_weapon(self):
        if game_mode != CHALLENGE_MODE: 
            return True
        if self.reload_timer > 0: 
            return False
            
        if self.current_weapon_type() == "sniper": 
            if self.sniper_ammo > 0:
                return True
            else:
                return False
        else:
            if self.pistol_ammo > 0:
                return True
            else:
                return False

    def consume_current_ammo(self):
        if game_mode != CHALLENGE_MODE: 
            return
            
        if self.current_weapon_type() == "sniper":
            self.sniper_ammo = self.sniper_ammo - 1
            if self.sniper_ammo <= 0: 
                self.sniper_ammo = 0
                self.start_reload("sniper")
        else:
            self.pistol_ammo = self.pistol_ammo - 1
            if self.pistol_ammo <= 0: 
                self.pistol_ammo = 0
                self.start_reload("pistol")

    def start_reload(self, weapon_type="None"):
        if game_mode != CHALLENGE_MODE:
            return
        if self.reload_timer > 0: 
            return
            
        if weapon_type == "None":
            self.reloading_weapon = self.current_weapon_type()
        else:
            self.reloading_weapon = weapon_type
            
        self.reload_timer = self.reload_duration

    def update(self):
        self.anim_timer = self.anim_timer + 1
        keys = pygame.key.get_pressed()
        move_x = 0
        move_y = 0

        # 彈藥填充倒數
        if self.reload_timer > 0:
            self.reload_timer = self.reload_timer - 1
            if self.reload_timer <= 0:
                if self.reloading_weapon == "sniper": 
                    self.sniper_ammo = self.sniper_mag_size
                else: 
                    self.pistol_ammo = self.pistol_mag_size
                self.reloading_weapon = "None"
        
        if keys[pygame.K_w]: move_y = move_y - 1
        if keys[pygame.K_s]: move_y = move_y + 1
        if keys[pygame.K_a]: move_x = move_x - 1
        if keys[pygame.K_d]: move_x = move_x + 1
            
        dist = math.sqrt(move_x * move_x + move_y * move_y)
        if dist > 0:
            move_x = move_x / dist
            move_y = move_y / dist

        if self.invincible_timer > 0: 
            self.invincible_timer -= 1
        if self.skill_cd > 0: 
            self.skill_cd -= 1
            
        # 護盾恢復
        if self.shield_regen_timer > 0: 
            self.shield_regen_timer -= 1
        else:
            if self.shield < self.max_shield: 
                self.shield = self.shield + self.shield_regen_rate
                if self.shield > self.max_shield:
                    self.shield = self.max_shield
            
        # 體力與能量恢復
        if self.is_dashing == False:
            if self.stamina < self.max_stamina:
                self.stamina = self.stamina + self.stamina_regen
                if self.stamina > self.max_stamina:
                    self.stamina = self.max_stamina
                    
        if self.energy < self.max_energy:
            self.energy = self.energy + self.energy_regen
            if self.energy > self.max_energy:
                self.energy = self.max_energy

        # 衝刺判定
        if keys[pygame.K_q] or keys[pygame.K_SPACE]:
            if self.is_dashing == False:
                if self.stamina >= self.dash_cost:
                    self.stamina = self.stamina - self.dash_cost
                    self.is_dashing = True
                    self.dash_timer = self.dash_duration
                    play_sound("dash")
                    
                    if dist > 0: 
                        self.dash_dir_x = move_x
                        self.dash_dir_y = move_y
                    else:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        dash_dx = mouse_x - self.x
                        dash_dy = mouse_y - self.y
                        dash_dist = math.sqrt(dash_dx * dash_dx + dash_dy * dash_dy)
                        if dash_dist > 0: 
                            self.dash_dir_x = dash_dx / dash_dist
                            self.dash_dir_y = dash_dy / dash_dist
                        else:
                            self.dash_dir_x = 1
                            self.dash_dir_y = 0

        # 計算玩家的位移，然後交給攝影機處理 (相對座標法)
        offset_x = 0
        offset_y = 0
        
        if self.is_dashing == True:
            offset_x = self.dash_dir_x * self.dash_speed
            offset_y = self.dash_dir_y * self.dash_speed
            self.dash_timer = self.dash_timer - 1
            if self.dash_timer <= 0: 
                self.is_dashing = False
        else:
            offset_x = move_x * self.base_speed
            offset_y = move_y * self.base_speed
            
        # 套用攝影機移動
        apply_camera_follow(offset_x, offset_y)
        
        # 玩家永遠在畫面正中央
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface, current_wep):
        draw_player = True
        if self.invincible_timer > 0 and self.god_mode == False:
            if int(self.invincible_timer / 4) % 2 == 0:
                draw_player = False
                
        if draw_player == True:
            # 畫電弧光環 (A3 功能)
            if self.aura_level > 0:
                aura_radius = 95 + self.aura_level * 25
                pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10)
                pygame.draw.circle(surface, (0, 180, 255), self.rect.center, aura_radius + pulse, 2)
                pygame.draw.circle(surface, (0, 90, 180), self.rect.center, aura_radius - 18, 1)
                
            # 畫玩家貼圖
            anim_frames = animations.get("player")
            if anim_frames != None:
                img_idx = int(self.anim_timer / 6) % len(anim_frames)
                img = anim_frames[img_idx]
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if mouse_x < self.x: 
                    img = pygame.transform.flip(img, True, False)
                surface.blit(img, img.get_rect(center=self.rect.center))
            else:
                if self.god_mode == True: 
                    player_color = YELLOW
                else: 
                    player_color = BLUE
                pygame.draw.rect(surface, player_color, self.rect)
                
            # 畫體力不夠的灰色框
            if self.stamina < self.dash_cost: 
                pygame.draw.rect(surface, GRAY, self.rect, 3)
                
            # 畫護盾圈圈
            if self.shield > 0:
                shield_ratio = self.shield / self.max_shield
                shield_radius = int(self.size / 2) + 8
                if shield_ratio > 0.35:
                    s_color = (70, 180, 255)
                else:
                    s_color = (255, 210, 70)
                pygame.draw.circle(surface, s_color, self.rect.center, shield_radius, 2)

            # 動態畫出手上的槍
            if current_wep != None:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx = mouse_x - self.x
                dy = mouse_y - self.y
                dist = math.sqrt(dx * dx + dy * dy)
                if dist > 0:
                    dir_x = dx / dist
                    dir_y = dy / dist
                else:
                    dir_x = 1
                    dir_y = 0
                
                angle = math.degrees(math.atan2(-dir_y, dir_x))
                gun_img = images.get("gun_" + current_wep.name)
                
                if gun_img != None:
                    if dir_x < 0: 
                        gun_img = pygame.transform.flip(gun_img, False, True)
                    rotated_gun = pygame.transform.rotate(gun_img, angle)
                    offset_x = dir_x * 15
                    offset_y = dir_y * 15
                    gun_rect = rotated_gun.get_rect(center=(int(self.x + offset_x), int(self.y + offset_y)))
                    surface.blit(rotated_gun, gun_rect)
                else:
                    end_x = self.x + dir_x * 25
                    end_y = self.y + dir_y * 25
                    
                    if current_wep.bullet_type == "piercing": wep_color = PURPLE
                    elif current_wep.bullet_type == "flamethrower": wep_color = ORANGE
                    elif current_wep.bullet_type == "laser": wep_color = CYAN
                    elif current_wep.bullet_type == "cannon": wep_color = WHITE
                    elif current_wep.bullet_type == "frost": wep_color = (100, 200, 255)
                    elif current_wep.bullet_type == "flame_grenade": wep_color = RED
                    elif current_wep.bullet_type == "plasma": wep_color = GREEN
                    else: wep_color = YELLOW
                        
                    pygame.draw.line(surface, GRAY, self.rect.center, (int(end_x), int(end_y)), 6)
                    pygame.draw.circle(surface, wep_color, (int(end_x), int(end_y)), 4)

# 攝影機跟隨系統 (移動所有其他物件來達成相對運動)
def apply_camera_follow(offset_x, offset_y):
    if offset_x == 0 and offset_y == 0: 
        return
        
    global bg_offset_x, bg_offset_y
    bg_offset_x = bg_offset_x + offset_x
    bg_offset_y = bg_offset_y + offset_y
    
    # 移動所有子彈
    for i in range(len(bullets)):
        bullets[i].x = bullets[i].x - offset_x
        bullets[i].y = bullets[i].y - offset_y
        bullets[i].target_x = bullets[i].target_x - offset_x
        bullets[i].target_y = bullets[i].target_y - offset_y
        bullets[i].rect.center = (int(bullets[i].x), int(bullets[i].y))
        
    # 移動敵人子彈
    for i in range(len(enemy_bullets)):
        enemy_bullets[i].x = enemy_bullets[i].x - offset_x
        enemy_bullets[i].y = enemy_bullets[i].y - offset_y
        enemy_bullets[i].rect.center = (int(enemy_bullets[i].x), int(enemy_bullets[i].y))
        
    # 移動敵人
    for i in range(len(enemies)):
        enemies[i].x = enemies[i].x - offset_x
        enemies[i].y = enemies[i].y - offset_y
        enemies[i].rect.center = (int(enemies[i].x), int(enemies[i].y))
        
    # 移動粒子
    for i in range(len(particles)):
        particles[i].x = particles[i].x - offset_x
        particles[i].y = particles[i].y - offset_y
        
    # 移動掉落物
    for i in range(len(items)):
        items[i].x = items[i].x - offset_x
        items[i].y = items[i].y - offset_y
        items[i].rect.center = (int(items[i].x), int(items[i].y))
        
    # 移動殘影
    for i in range(len(trails)):
        trails[i].x = trails[i].x - offset_x
        trails[i].y = trails[i].y - offset_y
        
    # 移動傷害文字
    for i in range(len(damage_texts)):
        damage_texts[i].x = damage_texts[i].x - offset_x
        damage_texts[i].y = damage_texts[i].y - offset_y
        
    # 移動 Boss
    if boss_active == True and boss != None:
        boss.x = boss.x - offset_x
        boss.y = boss.y - offset_y
        boss.rect.center = (int(boss.x), int(boss.y))
        if hasattr(boss, "aim_x"):
            boss.aim_x = boss.aim_x - offset_x
            boss.aim_y = boss.aim_y - offset_y
        if hasattr(boss, "entrance_start_x"):
            boss.entrance_start_x = boss.entrance_start_x - offset_x
            boss.entrance_start_y = boss.entrance_start_y - offset_y
            boss.entrance_end_x = boss.entrance_end_x - offset_x
            boss.entrance_end_y = boss.entrance_end_y - offset_y

class DashTrail:
    def __init__(self, x, y, size): 
        self.x = x
        self.y = y
        self.size = size
        self.life = 12
        
    def update(self): 
        self.life = self.life - 1
        self.size = self.size - 1.5
        
    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            rect = pygame.Rect(0, 0, int(self.size), int(self.size))
            rect.center = (int(self.x), int(self.y))
            pygame.draw.rect(surface, BLUE, rect, max(1, int(self.life / 3)))

class Bullet:
    def __init__(self, start_x, start_y, target_x, target_y, weapon, guidance_level=0):
        self.x = start_x
        self.y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.b_type = weapon.bullet_type
        self.damage = weapon.damage + player.bullet_damage_bonus
        
        self.is_piercing = False
        if self.b_type == "piercing" or self.b_type == "laser" or self.b_type == "cannon" or self.b_type == "flamethrower":
            self.is_piercing = True
            
        self.guidance_level = guidance_level
            
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        self.dir_x = 0
        self.dir_y = 0
        if dist > 0: 
            self.dir_x = dx / dist
            self.dir_y = dy / dist
        
        self.lifespan = 120 
        self.speed = 18
        self.radius = 6
        self.color = YELLOW
        
        if self.b_type == "piercing": 
            self.color = PURPLE
            self.speed = 28
            self.radius = 7
        elif self.b_type == "flamethrower": 
            self.color = ORANGE
            self.speed = 12
            self.radius = 12
            self.lifespan = 25
        elif self.b_type == "laser": 
            self.color = CYAN
            self.speed = 45
            self.radius = 4
        elif self.b_type == "cannon": 
            self.color = WHITE
            self.speed = 12
            self.radius = 20
        elif self.b_type == "frost": 
            self.color = (100, 200, 255)
            self.speed = 16
            self.radius = 8
        elif self.b_type == "flame_grenade": 
            self.color = RED
            self.speed = 10
            self.radius = 10
        elif self.b_type == "plasma": 
            self.color = GREEN
            self.speed = 15
            self.radius = 10

        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        self.explode = False 

    def update(self):
        self.lifespan = self.lifespan - 1
        
        # 導向子彈追蹤機制
        if self.guidance_level > 0 and self.lifespan % 2 == 0:
            closest_enemy = None
            closest_dist = 99999
            guide_range = 220 + self.guidance_level * 45
            
            # 尋找最近的敵人
            for i in range(len(enemies)):
                e = enemies[i]
                d = math.sqrt((self.x - e.x)**2 + (self.y - e.y)**2)
                if d <= guide_range and d < closest_dist:
                    closest_dist = d
                    closest_enemy = e
                    
            if boss_active == True and boss != None and boss.state != "DEFEAT":
                d = math.sqrt((self.x - boss.x)**2 + (self.y - boss.y)**2)
                if d <= guide_range and d < closest_dist:
                    closest_dist = d
                    closest_enemy = boss
                    
            if closest_enemy != None:
                t_dx = closest_enemy.x - self.x
                t_dy = closest_enemy.y - self.y
                t_dist = math.sqrt(t_dx * t_dx + t_dy * t_dy)
                if t_dist > 0:
                    t_dir_x = t_dx / t_dist
                    t_dir_y = t_dy / t_dist
                    turn_speed = 0.025 + self.guidance_level * 0.012
                    if turn_speed > 0.08: turn_speed = 0.08
                    self.dir_x = self.dir_x + t_dir_x * turn_speed
                    self.dir_y = self.dir_y + t_dir_y * turn_speed
                    
                    new_dist = math.sqrt(self.dir_x**2 + self.dir_y**2)
                    if new_dist > 0:
                        self.dir_x = self.dir_x / new_dist
                        self.dir_y = self.dir_y / new_dist
                        
        if self.b_type == "flame_grenade":
            dist_to_target = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
            if dist_to_target < self.speed:
                self.explode = True
                self.lifespan = 0
                return 
                
        if self.b_type == "plasma":
            # 電漿碰到邊界反彈，這裡將螢幕座標轉換回絕對世界座標做判定
            world_x = self.x + bg_offset_x
            world_y = self.y + bg_offset_y
            if world_x <= 0 or world_x >= MAP_WIDTH: 
                self.dir_x = self.dir_x * -1
            if world_y <= 0 or world_y >= MAP_HEIGHT: 
                self.dir_y = self.dir_y * -1
            
        self.x = self.x + self.dir_x * self.speed
        self.y = self.y + self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        img_key = "bullet_" + self.b_type
        img = images.get(img_key)
        if img != None:
            angle = math.degrees(math.atan2(-self.dir_y, self.dir_x))
            rotated_img = pygame.transform.rotate(img, angle)
            surface.blit(rotated_img, rotated_img.get_rect(center=self.rect.center))
        else:
            if self.b_type == "laser":
                end_x = self.x - (self.dir_x * 30)
                end_y = self.y - (self.dir_y * 30)
                pygame.draw.line(surface, self.color, (self.x, self.y), (end_x, end_y), self.radius*2)
            else: 
                pygame.draw.circle(surface, self.color, self.rect.center, self.radius)

class EnemyBullet:
    def __init__(self, x, y, dir_x, dir_y, color=ORANGE, core_color=WHITE, style="round"):
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        
        dist = math.sqrt(self.dir_x**2 + self.dir_y**2)
        if dist > 0: 
            self.dir_x = self.dir_x / dist
            self.dir_y = self.dir_y / dist
            
        self.radius = 8
        self.speed = 7
        self.color = color
        self.core_color = core_color
        self.style = style
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        
    def update(self):
        self.x = self.x + self.dir_x * self.speed
        self.y = self.y + self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface): 
        img = images.get("enemy_bullet")
        if img != None and self.style == "round": 
            surface.blit(img, img.get_rect(center=self.rect.center))
        else:
            pygame.draw.circle(surface, BLACK, self.rect.center, self.radius + 4)
            pygame.draw.circle(surface, self.color, self.rect.center, self.radius + 2)
            if self.style == "diamond":
                pts = [ 
                    (self.x, self.y - self.radius - 1), 
                    (self.x + self.radius + 1, self.y), 
                    (self.x, self.y + self.radius + 1), 
                    (self.x - self.radius - 1, self.y) 
                ]
                pygame.draw.polygon(surface, self.core_color, pts)
            elif self.style == "slash":
                # 計算旋轉 90 度的側邊向量
                side_x = -self.dir_y
                side_y = self.dir_x
                
                front_x = self.x + self.dir_x * (self.radius + 4)
                front_y = self.y + self.dir_y * (self.radius + 4)
                back_x = self.x - self.dir_x * (self.radius + 4)
                back_y = self.y - self.dir_y * (self.radius + 4)
                left_x = self.x + side_x * 4
                left_y = self.y + side_y * 4
                right_x = self.x - side_x * 4
                right_y = self.y - side_y * 4
                
                pts = [(int(front_x), int(front_y)), (int(left_x), int(left_y)), (int(back_x), int(back_y)), (int(right_x), int(right_y))]
                pygame.draw.polygon(surface, self.core_color, pts)
            else: 
                pygame.draw.circle(surface, self.core_color, self.rect.center, max(3, int(self.radius / 2)))

class Enemy:
    def __init__(self, level, is_elite=False):
        self.is_elite = is_elite
        if self.is_elite == True:
            self.size = 42
        else:
            self.size = 25
            
        global game_mode
        if game_mode == CHALLENGE_MODE:
            diff_mult = CHALLENGE_ENEMY_MULTIPLIER
            speed_mult = CHALLENGE_ENEMY_SPEED_MULTIPLIER
        else:
            diff_mult = 1
            speed_mult = 1
            
        speed_bonus = level * 0.03
        if speed_bonus > 1.2:
            speed_bonus = 1.2
            
        if self.is_elite == True:
            self.speed = (random.uniform(2.0, 4.0) + speed_bonus) * speed_mult
            base_hp = 5
            self.damage = int(35 * diff_mult)
            self.exp_drop_chance = 0.85
            self.health_drop_chance = 0.12
        else:
            self.speed = (random.uniform(1.5, 3.5) + speed_bonus) * speed_mult
            base_hp = 1
            self.damage = int(20 * diff_mult)
            self.exp_drop_chance = 0.4
            self.health_drop_chance = 0.035
            
        self.max_hp = base_hp + int(level / 6)
        self.max_hp = int(self.max_hp * diff_mult)
        if self.max_hp < 1: self.max_hp = 1
        self.hp = self.max_hp
        
        shield_base = int(level / 4)
        if self.is_elite == True: shield_base = shield_base + 2
        self.shield = int(shield_base * diff_mult)
        self.max_shield = self.shield
        
        rand_val = random.random()
        if self.is_elite == True:
            is_ranged = rand_val < 0.38
        else:
            is_ranged = rand_val < 0.32
            
        if is_ranged == True: self.combat_type = "ranged"
        else: self.combat_type = "melee"
        
        if self.is_elite == True:
            self.attack_range = 420
            self.keep_distance = 260
            self.shoot_delay = 85
        else:
            self.attack_range = 320
            self.keep_distance = 205
            self.shoot_delay = 115
            
        self.shoot_cooldown = random.randint(35, 90)
        self.frost_timer = 0
        self.anim_timer = 0
        self.dir_x = 1
        self.dir_y = 0
        
        # 決定重生點 (絕對世界座標)
        edge_list =['top', 'bottom', 'left', 'right']
        edge = random.choice(edge_list)
        world_px = player.x + bg_offset_x
        world_py = player.y + bg_offset_y
        
        if edge == 'top': 
            world_x = world_px + random.randint(-WIDTH, WIDTH)
            world_y = world_py - int(HEIGHT/2) - self.size
        elif edge == 'bottom': 
            world_x = world_px + random.randint(-WIDTH, WIDTH)
            world_y = world_py + int(HEIGHT/2) + self.size
        elif edge == 'left': 
            world_x = world_px - int(WIDTH/2) - self.size
            world_y = world_py + random.randint(-HEIGHT, HEIGHT)
        elif edge == 'right': 
            world_x = world_px + int(WIDTH/2) + self.size
            world_y = world_py + random.randint(-HEIGHT, HEIGHT)
            
        # 轉換為螢幕相對座標
        self.x = world_x - bg_offset_x
        self.y = world_y - bg_offset_y
        self.rect = pygame.Rect(0, 0, self.size, self.size)

    def update(self, target_x, target_y, all_enemies):
        self.anim_timer = self.anim_timer + 1
        current_speed = self.speed
        if self.frost_timer > 0:
            self.frost_timer = self.frost_timer - 1
            current_speed = self.speed * 0.4 

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        move_dir_x = 0
        move_dir_y = 0
        
        if dist > 0:
            self.dir_x = dx / dist
            self.dir_y = dy / dist
            
            if self.combat_type == "ranged":
                if dist < self.keep_distance:
                    move_dir_x = -self.dir_x
                    move_dir_y = -self.dir_y
                elif dist <= self.attack_range:
                    move_dir_x = 0
                    move_dir_y = 0
                else:
                    move_dir_x = self.dir_x
                    move_dir_y = self.dir_y
                    
                if self.shoot_cooldown > 0: 
                    self.shoot_cooldown = self.shoot_cooldown - 1
            else:
                move_dir_x = self.dir_x
                move_dir_y = self.dir_y
                
        self.x = self.x + move_dir_x * current_speed
        self.y = self.y + move_dir_y * current_speed

        # Boids 群體互斥避免疊羅漢
        for i in range(len(all_enemies)):
            other = all_enemies[i]
            if other != self:
                dist_sq = (self.x - other.x)**2 + (self.y - other.y)**2
                if dist_sq > 0 and dist_sq < self.size**2:
                    dist_val = math.sqrt(dist_sq)
                    push_x = (self.x - other.x) / dist_val
                    push_y = (self.y - other.y) / dist_val
                    self.x = self.x + push_x * 1.2
                    self.y = self.y + push_y * 1.2
            
        self.rect.center = (int(self.x), int(self.y))

    def emit_attacks(self, enemy_bullets_list, target_x, target_y):
        if self.combat_type != "ranged": return
        if self.shoot_cooldown > 0: return
        
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist == 0 or dist > self.attack_range + 80: 
            return
            
        dir_x = dx / dist
        dir_y = dy / dist
        self.dir_x = dir_x
        self.dir_y = dir_y
        
        if self.is_elite == True: bullet_color = (255, 120, 45)
        else: bullet_color = ORANGE
            
        enemy_bullets_list.append(EnemyBullet(self.x, self.y, dir_x, dir_y, color=bullet_color, core_color=WHITE, style="round"))
        self.shoot_cooldown = self.shoot_delay

    def draw(self, surface):
        if self.is_elite == True: anim_key = "enemy_elite"
        else: anim_key = "enemy_normal"
        anim_frames = animations.get(anim_key)
        
        if anim_frames != None:
            img_idx = int(self.anim_timer / 6) % len(anim_frames)
            img = anim_frames[img_idx]
            if self.dir_x < 0: 
                img = pygame.transform.flip(img, True, False)
            if self.frost_timer > 0:
                img = img.copy()
                img.fill((100, 200, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(img, img.get_rect(center=self.rect.center))
            
            if self.is_elite == True:
                glow = math.sin(pygame.time.get_ticks() * 0.01) * 6 + 6
                glow_rect = self.rect.copy()
                glow_rect.inflate_ip(glow, glow)
                pygame.draw.rect(surface, DARK_PURPLE, glow_rect, 3) 
        else:
            # 原版 A3 幾何圖形繪製
            side_x = -self.dir_y
            side_y = self.dir_x
            
            if self.is_elite == True: weapon_reach = 34
            else: weapon_reach = 24
                
            weapon_offset = self.size * 0.28
            hand_x = self.x + self.dir_x * weapon_offset + side_x * (self.size * 0.2)
            hand_y = self.y + self.dir_y * weapon_offset + side_y * (self.size * 0.2)
            
            if self.combat_type == "melee":
                if self.is_elite == True: h_dist = 8
                else: h_dist = 5
                hilt_x = hand_x + self.dir_x * h_dist
                hilt_y = hand_y + self.dir_y * h_dist
                
                blade_tip_x = hand_x + self.dir_x * (weapon_reach + 16)
                blade_tip_y = hand_y + self.dir_y * (weapon_reach + 16)
                
                blade_mid_x = hilt_x + self.dir_x * ((weapon_reach + 12) * 0.55)
                blade_mid_y = hilt_y + self.dir_y * ((weapon_reach + 12) * 0.55)
                
                if self.is_elite == True: b_half = 7
                else: b_half = 5
                
                b_half_2 = max(3, b_half - 2)
                
                if self.is_elite == True: b_color = (80, 240, 255)
                else: b_color = (100, 255, 145)
                    
                pts_black =[
                    (blade_tip_x, blade_tip_y),
                    (blade_mid_x + side_x * b_half, blade_mid_y + side_y * b_half),
                    (hilt_x + side_x * b_half_2, hilt_y + side_y * b_half_2),
                    (hilt_x - side_x * b_half_2, hilt_y - side_y * b_half_2),
                    (blade_mid_x - side_x * b_half, blade_mid_y - side_y * b_half)
                ]
                pygame.draw.polygon(surface, BLACK, [(int(p[0]), int(p[1])) for p in pts_black])
                
                pts_color =[
                    (blade_tip_x - self.dir_x * 2, blade_tip_y - self.dir_y * 2),
                    (blade_mid_x + side_x * b_half_2, blade_mid_y + side_y * b_half_2),
                    (hilt_x + side_x * 2, hilt_y + side_y * 2),
                    (hilt_x - side_x * 2, hilt_y - side_y * 2),
                    (blade_mid_x - side_x * b_half_2, blade_mid_y - side_y * b_half_2)
                ]
                pygame.draw.polygon(surface, b_color, [(int(p[0]), int(p[1])) for p in pts_color])
            else:
                muzzle_x = self.x + self.dir_x * weapon_reach + side_x * (self.size * 0.2)
                muzzle_y = self.y + self.dir_y * weapon_reach + side_y * (self.size * 0.2)
                
                rear_x = self.x + self.dir_x * (self.size * 0.02) + side_x * (self.size * 0.2)
                rear_y = self.y + self.dir_y * (self.size * 0.02) + side_y * (self.size * 0.2)
                
                if self.is_elite == True: b_half = 5
                else: b_half = 4
                    
                b_half_2 = max(2, b_half - 2)
                b_half_3 = max(1, b_half - 3)
                
                pts_black =[
                    (rear_x + side_x * b_half, rear_y + side_y * b_half),
                    (muzzle_x + side_x * b_half_2, muzzle_y + side_y * b_half_2),
                    (muzzle_x - side_x * b_half_2, muzzle_y - side_y * b_half_2),
                    (rear_x - side_x * b_half, rear_y - side_y * b_half)
                ]
                pygame.draw.polygon(surface, BLACK, [(int(p[0]), int(p[1])) for p in pts_black])
                
                pts_color =[
                    (rear_x + side_x * (b_half - 1), rear_y + side_y * (b_half - 1)),
                    (muzzle_x + side_x * b_half_3, muzzle_y + side_y * b_half_3),
                    (muzzle_x - side_x * b_half_3, muzzle_y - side_y * b_half_3),
                    (rear_x - side_x * (b_half - 1), rear_y - side_y * (b_half - 1))
                ]
                pygame.draw.polygon(surface, (205, 210, 215), [(int(p[0]), int(p[1])) for p in pts_color])
                
                if self.is_elite == True: tip_dist = 7
                else: tip_dist = 5
                    
                barrel_tip_x = muzzle_x + self.dir_x * tip_dist
                barrel_tip_y = muzzle_y + self.dir_y * tip_dist
                
                if self.is_elite == True: l_thick = 5
                else: l_thick = 4
                    
                pygame.draw.line(surface, BLACK, (int(muzzle_x), int(muzzle_y)), (int(barrel_tip_x), int(barrel_tip_y)), l_thick)
                
                if self.is_elite == True: c_color = ORANGE
                else: c_color = YELLOW
                pygame.draw.circle(surface, c_color, (int(barrel_tip_x), int(barrel_tip_y)), 3)

            if self.is_elite == True: color = (170, 40, 255)
            else: color = RED
                
            if self.frost_timer > 0: color = (100, 200, 255)
            pygame.draw.rect(surface, color, self.rect)
            
            if self.is_elite == True:
                pygame.draw.circle(surface, (230, 170, 255), self.rect.center, int(self.size/2) + 8, 2)
                pygame.draw.rect(surface, WHITE, self.rect, 3)
                
        if self.shield > 0: 
            pygame.draw.rect(surface, BLUE, self.rect.inflate(8, 8), 2)
            
        if self.hp < self.max_hp or self.shield > 0:
            pygame.draw.rect(surface, GRAY, (self.rect.x, self.rect.y - 8, self.size, 4))
            pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 8, int(self.size * (self.hp/self.max_hp)), 4))
            if self.max_shield > 0:
                pygame.draw.rect(surface, GRAY, (self.rect.x, self.rect.y - 14, self.size, 4))
                pygame.draw.rect(surface, BLUE, (self.rect.x, self.rect.y - 14, int(self.size * (self.shield/self.max_shield)), 4))

class Boss:
    def __init__(self, boss_type, level=5):
        self.b_type = boss_type
        
        # 決定世界重生座標
        world_x = player.x + bg_offset_x
        world_y = player.y + bg_offset_y - int(HEIGHT/2) - 100
        
        # 存成絕對世界座標，用來做入場動畫的平滑插值
        self.entrance_start_x = world_x 
        self.entrance_start_y = world_y
        self.entrance_end_x = world_x
        self.entrance_end_y = world_y + 200
        
        # 目前顯示的座標
        self.x = self.entrance_start_x - bg_offset_x
        self.y = self.entrance_start_y - bg_offset_y
        
        self.size = 65
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.spawn_level = level
        
        global game_mode
        if game_mode == CHALLENGE_MODE: diff_mult = CHALLENGE_ENEMY_MULTIPLIER
        else: diff_mult = 1
        
        self.state = "ENTRANCE"
        self.state_timer = 0
        self.frost_timer = 0
        self.defeat_timer = 0
        self.anim_timer = 0
        self.entrance_duration = 120  
        self.play_shoot_sound = False 
        self.collision_damage = int(40 * diff_mult)
        
        if self.b_type == "YELLOW":
            self.max_hp = int((1000 + level*300) * diff_mult)
            self.color = YELLOW
            self.speed = 3.0 * diff_mult
            self.name = "幾何守衛"
        elif self.b_type == "RED":
            self.max_hp = int((1500 + level*300) * diff_mult)
            self.color = RED
            self.speed = 2.5 * diff_mult
            self.name = "鮮血狂戰士"
            self.aim_x = 0
            self.aim_y = 0
            self.dash_dir_x = 1
            self.dash_dir_y = 0
            self.spin_angle = 0
        elif self.b_type == "PURPLE":
            self.max_hp = int((800 + level*300) * diff_mult)
            self.color = PURPLE
            self.speed = 2.0 * diff_mult
            self.name = "虛空召喚師"
        elif self.b_type == "CHARGER":
            # 將 A3 的 ChargerBoss 完美整合成一種 Type
            self.max_hp = int((650 + level*135) * diff_mult)
            self.color = (255, 70, 60)
            self.speed = (5.2 + min(level * 0.08, 1.6)) * diff_mult
            self.name = "裂空突擊者"
            self.aim_x = 0
            self.aim_y = 0
            self.dash_dir_x = 1
            self.dash_dir_y = 0
            self.spin_angle = 0
            self.side_fire_timer = 0
            self.spin_fire_timer = 0
            self.entrance_duration = 130
            self.collision_damage = int(50 * diff_mult)
            
            # ChargerBoss 獨特的出場方式
            side = -1
            if random.random() < 0.5: side = 1
            self.entrance_end_x = player.x + bg_offset_x + side * 320
            self.entrance_start_x = self.entrance_end_x + side * 520
            self.x = self.entrance_start_x - bg_offset_x
            
        self.hp = self.max_hp

    def update(self, player_x, player_y, bullets_list, enemies_list, enemy_bullets_list):
        self.state_timer = self.state_timer + 1
        self.anim_timer = self.anim_timer + 1
        
        current_speed = self.speed
        if self.frost_timer > 0: 
            current_speed = self.speed * 0.5
            self.frost_timer = self.frost_timer - 1
            
        self.play_shoot_sound = False

        if self.state == "ENTRANCE":
            progress = self.state_timer / self.entrance_duration
            if progress > 1: progress = 1
            eased = 1 - (1 - progress) ** 3
            
            # 使用絕對座標做過場動畫插值
            current_world_x = self.entrance_start_x + (self.entrance_end_x - self.entrance_start_x) * eased
            current_world_y = self.entrance_start_y + (self.entrance_end_y - self.entrance_start_y) * eased
            
            self.x = current_world_x - bg_offset_x
            self.y = current_world_y - bg_offset_y
            
            glow = int(100 + 155 * progress)
            if self.b_type == "YELLOW": self.color = (glow, glow, 0)
            elif self.b_type == "RED": self.color = (glow, 0, 0)
            elif self.b_type == "PURPLE": self.color = (int(100+100*progress), 0, int(100+155*progress))
            elif self.b_type == "CHARGER": 
                pulse = int(80 * abs(math.sin(self.state_timer * 0.12)))
                self.color = (175 + pulse, 45, 55)
                
            if self.state_timer >= self.entrance_duration:
                if self.b_type == "YELLOW": self.state = "EVADE"
                elif self.b_type == "RED": self.state = "CHASE"
                elif self.b_type == "PURPLE": self.state = "FLEE"
                elif self.b_type == "CHARGER": self.state = "AIM"
                self.state_timer = 0
                
        elif self.state == "DEFEAT":
            self.defeat_timer = self.defeat_timer + 1
            self.y = self.y - 1
            self.x = self.x + math.sin(self.defeat_timer * 0.2) * 1.5

        elif self.b_type == "YELLOW":
            if self.state == "EVADE":
                dx = player_x - self.x
                dy = player_y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                dir_x = 0
                dir_y = 0
                if dist > 0: 
                    dir_x = dx / dist
                    dir_y = dy / dist
                    
                tangent_x = -dir_y
                tangent_y = dir_x 
                
                dodged = False
                for i in range(len(bullets_list)):
                    b = bullets_list[i]
                    b_dist = math.sqrt((self.x - b.x)**2 + (self.y - b.y)**2)
                    if b_dist < 150:
                        flee_dx = self.x - b.x
                        flee_dy = self.y - b.y
                        flee_dist = math.sqrt(flee_dx*flee_dx + flee_dy*flee_dy)
                        if flee_dist > 0:
                            flee_dir_x = flee_dx / flee_dist
                            flee_dir_y = flee_dy / flee_dist
                            self.x = self.x + flee_dir_x * (current_speed * 1.8)
                            self.y = self.y + flee_dir_y * (current_speed * 1.8)
                        dodged = True
                        break 
                        
                if dodged == False:
                    self.x = self.x + tangent_x * current_speed
                    self.y = self.y + tangent_y * current_speed
                    p_dist = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)
                    if p_dist > 250: 
                        self.x = self.x + dir_x * current_speed
                        self.y = self.y + dir_y * current_speed
                    elif p_dist < 150: 
                        self.x = self.x - dir_x * current_speed
                        self.y = self.y - dir_y * current_speed

                if self.state_timer > 120:
                    self.state = "CHARGE"
                    self.state_timer = 0
                    
            elif self.state == "CHARGE":
                if self.state_timer > 60: 
                    self.state = "SHOOT"
                    self.state_timer = 0

        elif self.b_type == "RED":
            if self.state == "CHASE":
                dx = player_x - self.x
                dy = player_y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    dir_x = dx / dist
                    dir_y = dy / dist
                    self.x = self.x + dir_x * current_speed
                    self.y = self.y + dir_y * current_speed
                    
                if self.state_timer > 150:
                    self.state = "WARN"
                    self.state_timer = 0
            elif self.state == "WARN":
                self.aim_x = player_x 
                self.aim_y = player_y
                if self.state_timer > 45:
                    self.state = "DASH"
                    self.state_timer = 0
                    dash_dx = self.aim_x - self.x
                    dash_dy = self.aim_y - self.y
                    dash_dist = math.sqrt(dash_dx*dash_dx + dash_dy*dash_dy)
                    self.dash_dir_x = 0
                    self.dash_dir_y = 0
                    if dash_dist > 0: 
                        self.dash_dir_x = dash_dx / dash_dist
                        self.dash_dir_y = dash_dy / dash_dist
                    else:
                        self.dash_dir_x = 1
                        self.dash_dir_y = 0
                    self.play_shoot_sound = True 
            elif self.state == "DASH":
                self.x = self.x + self.dash_dir_x * (current_speed * 6) 
                self.y = self.y + self.dash_dir_y * (current_speed * 6)
                if self.state_timer % 6 == 0:
                    # 發射十字子彈
                    side1_x = -self.dash_dir_y
                    side1_y = self.dash_dir_x
                    side2_x = self.dash_dir_y
                    side2_y = -self.dash_dir_x
                    enemy_bullets_list.append(EnemyBullet(self.x, self.y, side1_x, side1_y, color=(0, 210, 255), core_color=WHITE, style="slash"))
                    enemy_bullets_list.append(EnemyBullet(self.x, self.y, side2_x, side2_y, color=(0, 210, 255), core_color=WHITE, style="slash"))
                if self.state_timer > 25:
                    aim_dist = math.sqrt((self.aim_x - self.x)**2 + (self.aim_y - self.y)**2)
                    if aim_dist < 30:
                        self.state = "RECOVER"
                        self.state_timer = 0
            elif self.state == "RECOVER":
                self.spin_angle = self.spin_angle + 0.15
                if self.state_timer > 120: 
                    self.state = "CHASE"
                    self.state_timer = 0

        elif self.b_type == "PURPLE":
            if self.state == "FLEE":
                dist = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)
                dx = player_x - self.x
                dy = player_y - self.y
                dir_x = 0
                dir_y = 0
                if dist > 0:
                    dir_x = dx / dist
                    dir_y = dy / dist
                else:
                    dir_x = 1
                    dir_y = 0
                    
                if dist < 300: 
                    self.x = self.x - dir_x * current_speed 
                    self.y = self.y - dir_y * current_speed
                else:
                    tangent_x = -dir_y
                    tangent_y = dir_x
                    self.x = self.x + tangent_x * current_speed 
                    self.y = self.y + tangent_y * current_speed
                
                if self.state_timer > 180:
                    self.state = "SUMMON"
                    self.state_timer = 0
            elif self.state == "SUMMON":
                if self.state_timer == 45:
                    for _ in range(3):
                        e = Enemy(self.spawn_level, is_elite=True)
                        e.x = self.x + random.randint(-70,70)
                        e.y = self.y + random.randint(-70,70)
                        enemies_list.append(e)
                    self.play_shoot_sound = True
                if self.state_timer > 90: 
                    self.state = "FLEE"
                    self.state_timer = 0
                    
        elif self.b_type == "CHARGER":
            if self.state == "AIM":
                self.color = (255, 210, 60)
                dx = player_x - self.x
                dy = player_y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    self.dash_dir_x = dx / dist
                    self.dash_dir_y = dy / dist
                else:
                    self.dash_dir_x = 1
                    self.dash_dir_y = 0
                    
                self.aim_x = self.x + self.dash_dir_x * 760
                self.aim_y = self.y + self.dash_dir_y * 760
                
                if self.state_timer > 70:
                    self.state = "DASH"
                    self.state_timer = 0
                    self.side_fire_timer = 0

            elif self.state == "DASH":
                self.color = (255, 45, 45)
                self.x = self.x + self.dash_dir_x * (current_speed * 3.2)
                self.y = self.y + self.dash_dir_y * (current_speed * 3.2)
                self.side_fire_timer = self.side_fire_timer + 1
                
                aim_dist = math.sqrt((self.aim_x - self.x)**2 + (self.aim_y - self.y)**2)
                if self.state_timer > 44 or aim_dist < 45:
                    self.state = "RECOVER"
                    self.state_timer = 0

            elif self.state == "RECOVER":
                self.color = (170, 80, 255)
                self.spin_angle = self.spin_angle + 0.13
                self.spin_fire_timer = self.spin_fire_timer + 1
                if self.state_timer > 240:
                    self.state = "AIM"
                    self.state_timer = 0
                    self.spin_fire_timer = 0

        # 將座標鎖在地圖邊界內 (考慮 global_offset)
        world_x = self.x + bg_offset_x
        world_y = self.y + bg_offset_y
        if world_x < self.size: world_x = self.size
        if world_x > MAP_WIDTH - self.size: world_x = MAP_WIDTH - self.size
        if world_y < self.size: world_y = self.size
        if world_y > MAP_HEIGHT - self.size: world_y = MAP_HEIGHT - self.size
        
        self.x = world_x - bg_offset_x
        self.y = world_y - bg_offset_y
        self.rect.center = (int(self.x), int(self.y))

    def can_take_damage(self):
        if self.state == "ENTRANCE": return False
        if self.state == "DEFEAT": return False
        if self.b_type == "YELLOW" and self.state == "EVADE": return False
        if self.b_type == "RED" and self.state == "DASH": return False
        if self.b_type == "CHARGER" and self.state == "DASH": return False
        return True

    def emit_attacks(self, enemy_bullets_list):
        if self.b_type == "YELLOW" and self.state == "SHOOT":
            for i in range(12):
                angle = math.radians(i * 30)
                dir_x = math.cos(angle)
                dir_y = math.sin(angle)
                enemy_bullets_list.append(EnemyBullet(self.x, self.y, dir_x, dir_y))
                
            if self.spawn_level >= 10:
                for i in range(12):
                    angle = math.radians(i * 30 + 15)
                    dir_x = math.cos(angle)
                    dir_y = math.sin(angle)
                    enemy_bullets_list.append(EnemyBullet(self.x, self.y, dir_x, dir_y))
                    
            self.state = "EVADE"
            play_sound("shoot")
            
        elif self.b_type == "RED" and self.state == "RECOVER":
            if self.state_timer % 10 == 0:
                for i in range(6):
                    angle = self.spin_angle + i * (math.pi*2/6)
                    dir_x = math.cos(angle)
                    dir_y = math.sin(angle)
                    enemy_bullets_list.append(EnemyBullet(self.x, self.y, dir_x, dir_y, color=PURPLE, style="round"))
                    
        elif self.b_type == "CHARGER":
            if self.state == "DASH" and self.side_fire_timer % 7 == 0:
                side_a_x = -self.dash_dir_y
                side_a_y = self.dash_dir_x
                side_b_x = self.dash_dir_y
                side_b_y = -self.dash_dir_x
                
                enemy_bullets_list.append(EnemyBullet(self.x, self.y, side_a_x, side_a_y, color=(0, 210, 255), core_color=(210, 255, 255), style="slash"))
                enemy_bullets_list.append(EnemyBullet(self.x, self.y, side_b_x, side_b_y, color=(0, 210, 255), core_color=(210, 255, 255), style="slash"))
                play_sound("shoot")
                
            elif self.state == "RECOVER" and self.spin_fire_timer % 14 == 0:
                if self.spawn_level < 10: shots = 6
                else: shots = 8
                    
                for i in range(shots):
                    angle = self.spin_angle + i * (math.pi * 2 / shots)
                    dir_x = math.cos(angle)
                    dir_y = math.sin(angle)
                    enemy_bullets_list.append(EnemyBullet(self.x, self.y, dir_x, dir_y, color=(185, 60, 255), core_color=(255, 220, 255), style="round"))
                play_sound("shoot")

    def get_intro_title(self): 
        return "✦ " + self.name + " 降臨 ✦"

    def get_intro_lines(self):
        if self.b_type == "CHARGER":
            return[
                "⚠️ 特殊 BOSS 出現！時間暫停中",
                "金色 = 鎖定玩家  |  紅色 = 無敵長距離衝刺",
                "紫色冷卻時會原地旋轉射擊，別貼太近！"
            ]
        else:
            return [ 
                "⚠️ BOSS 出現！時間暫停中", 
                "準備迎接史詩級的挑戰！", 
                "觀察型態轉換，把握攻擊時機！" 
            ]

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
        elif self.b_type == "CHARGER":
            if self.state == "AIM": return "鎖定階段 - 即將衝刺 (金色)", YELLOW
            if self.state == "DASH": return "突擊階段 - 無敵高速衝刺", RED
            if self.state == "RECOVER": return "冷卻階段 - 原地旋轉彈幕", PURPLE
            return "BOSS 交戰中", WHITE
            
        return "BOSS 交戰中", WHITE

    def draw(self, surface):
        if self.state == "ENTRANCE":
            pulse = abs(math.sin(self.state_timer * 0.1))
            current_size = int(self.size * (0.8 + pulse * 0.4))
            for i in range(3):
                ring_size = int(current_size / 2) + 20 + i * 15
                alpha_val = int(200 * (1 - i/3) * (1 - pulse))
                if alpha_val > 0: 
                    pygame.draw.circle(surface, WHITE, self.rect.center, ring_size, 2)
                    
            draw_rect = pygame.Rect(0, 0, current_size, current_size)
            draw_rect.center = self.rect.center
            pygame.draw.rect(surface, self.color, draw_rect)
            pygame.draw.circle(surface, WHITE, self.rect.center, int(current_size/2) + 15, 3)
            
            for i in range(8):
                angle = (self.state_timer * 0.05 + i * math.pi / 4)
                px = self.rect.centerx + math.cos(angle) * (self.size + 30)
                py = self.rect.centery + math.sin(angle) * (self.size + 30)
                pygame.draw.circle(surface, YELLOW, (int(px), int(py)), 3)
            return
            
        elif self.state == "DEFEAT":
            progress = self.defeat_timer / 60
            if progress > 1: progress = 1
                
            for i in range(5): 
                radius = int(self.size + progress * 120 + i * 12)
                pygame.draw.circle(surface, (255, 180, 0), self.rect.center, radius, 3)
                
            core_size = int(self.size * (1 - progress * 0.7))
            if core_size < 1: core_size = 1
            core_rect = pygame.Rect(0, 0, core_size, core_size)
            core_rect.center = self.rect.center
            pygame.draw.rect(surface, (255, 100, 0), core_rect)
            
            burst = int(progress * 10)
            for i in range(burst):
                angle = i * (math.pi * 2 / max(1, burst)) + self.defeat_timer * 0.3
                px = self.rect.centerx + math.cos(angle) * (self.size + 30 + progress * 80)
                py = self.rect.centery + math.sin(angle) * (self.size + 30 + progress * 80)
                pygame.draw.circle(surface, RED, (int(px), int(py)), 4)
            return

        # 針對 ChargerBoss 的特殊幾何繪製
        if self.b_type == "CHARGER":
            pulse = abs(math.sin(self.state_timer * 0.13))
            dir_x = self.dash_dir_x
            dir_y = self.dash_dir_y
            if dir_x == 0 and dir_y == 0:
                dir_x = 1
                
            nose_x = self.x + dir_x * (self.size / 2 + 26)
            nose_y = self.y + dir_y * (self.size / 2 + 26)
            
            back_x = self.x - dir_x * (self.size / 2)
            back_y = self.y - dir_y * (self.size / 2)
            
            side_x = -dir_y
            side_y = dir_x
            
            left_x = back_x + side_x * (self.size / 2)
            left_y = back_y + side_y * (self.size / 2)
            right_x = back_x - side_x * (self.size / 2)
            right_y = back_y - side_y * (self.size / 2)
            
            wing_l_x = self.x + side_x * (self.size / 2 + 24)
            wing_l_y = self.y + side_y * (self.size / 2 + 24)
            wing_r_x = self.x - side_x * (self.size / 2 + 24)
            wing_r_y = self.y - side_y * (self.size / 2 + 24)

            body_points =[
                (int(nose_x), int(nose_y)), 
                (int(wing_l_x), int(wing_l_y)), 
                (int(left_x), int(left_y)),
                (int(self.x - dir_x * 12), int(self.y - dir_y * 12)),
                (int(right_x), int(right_y)), 
                (int(wing_r_x), int(wing_r_y)),
            ]
            
            if self.state == "DASH": aura_color = RED 
            elif self.state == "AIM": aura_color = ORANGE 
            else: aura_color = PURPLE
                
            pygame.draw.circle(surface, aura_color, (int(self.x), int(self.y)), int(self.size / 2 + 30 + pulse * 10), 2)
            pygame.draw.polygon(surface, self.color, body_points)
            pygame.draw.polygon(surface, WHITE, body_points, 3)
            pygame.draw.circle(surface, BLACK, (int(self.x), int(self.y)), 14)
            
            if self.state == "DASH": center_color = RED 
            else: center_color = YELLOW
            pygame.draw.circle(surface, center_color, (int(self.x), int(self.y)), 8)

            if self.state == "AIM":
                pygame.draw.line(surface, YELLOW, (int(self.x), int(self.y)), (int(self.aim_x), int(self.aim_y)), 3)
            elif self.state == "DASH":
                pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), int(self.size / 2) + 36, 3)
                tip_l_x = self.x + side_x * 120
                tip_l_y = self.y + side_y * 120
                tip_r_x = self.x - side_x * 120
                tip_r_y = self.y - side_y * 120
                pygame.draw.line(surface, ORANGE, (int(self.x), int(self.y)), (int(tip_l_x), int(tip_l_y)), 2)
                pygame.draw.line(surface, ORANGE, (int(self.x), int(self.y)), (int(tip_r_x), int(tip_r_y)), 2)
            elif self.state == "RECOVER":
                for i in range(6):
                    angle = self.spin_angle + i * math.pi / 3
                    tip_x = self.x + math.cos(angle) * 95
                    tip_y = self.y + math.sin(angle) * 95
                    pygame.draw.line(surface, PURPLE, (int(self.x), int(self.y)), (int(tip_x), int(tip_y)), 2)
            
            return

        # 其他常規 Boss 的動畫繪製
        anim_key = "boss_" + self.b_type
        anim_frames = animations.get(anim_key)
        
        if anim_frames != None:
            img_idx = int(self.anim_timer / 8) % len(anim_frames)
            img = anim_frames[img_idx]
            surface.blit(img, img.get_rect(center=self.rect.center))
        else:
            if self.frost_timer > 0: color = (100, 200, 255)
            else: color = self.color
            pygame.draw.rect(surface, color, self.rect)
        
        if self.b_type == "YELLOW" and self.state == "EVADE": 
            pygame.draw.circle(surface, WHITE, self.rect.center, int(self.size/2) + 15, 3)
        elif self.b_type == "YELLOW" and self.state == "CHARGE": 
            shrink = 30 - int(self.state_timer / 2)
            if shrink < 0: shrink = 0
            pygame.draw.circle(surface, RED, self.rect.center, int(self.size/2) + shrink, 2)
        elif self.b_type == "RED" and self.state == "WARN": 
            thickness = int(self.state_timer / 8)
            if thickness < 1: thickness = 1
            pygame.draw.line(surface, RED, self.rect.center, (int(self.aim_x), int(self.aim_y)), thickness)
        elif self.b_type == "PURPLE" and self.state == "SUMMON": 
            expand = self.state_timer
            if expand > 60: expand = 60
            pygame.draw.circle(surface, DARK_PURPLE, self.rect.center, int(self.size/2) + expand, 3)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vel_x = random.uniform(-6, 6)
        self.vel_y = random.uniform(-6, 6)
        self.timer = random.randint(15, 30)
        self.size = random.randint(4, 8)
        self.color = color
        
    def update(self):
        self.x = self.x + self.vel_x
        self.y = self.y + self.vel_y
        self.timer = self.timer - 1
        self.size = self.size - 0.25
        if self.size < 0: self.size = 0
        
    def draw(self, surface):
        if self.size > 0: 
            pygame.draw.rect(surface, self.color, (int(self.x), int(self.y), int(self.size), int(self.size)))

class DamageText:
    def __init__(self, x, y, damage, color=WHITE):
        self.x = x
        self.y = y
        self.damage = int(damage)
        self.color = color
        self.timer = 40  
        self.vel_y = -1.5  
        self.alpha = 255
        self.offset_x = random.randint(-15, 15)
        
    def update(self):
        self.y = self.y + self.vel_y
        self.timer = self.timer - 1
        self.alpha = int((self.timer / 40) * 255)
        if self.alpha < 0: self.alpha = 0
            
    def draw(self, surface):
        if self.timer > 0:
            txt_surf = font.render("-" + str(self.damage), True, self.color)
            alpha_surf = pygame.Surface(txt_surf.get_size(), pygame.SRCALPHA)
            alpha_surf.fill((255, 255, 255, self.alpha))
            txt_surf.blit(alpha_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(txt_surf, (int(self.x + self.offset_x), int(self.y)))

class DropItem:
    def __init__(self, x, y, item_type="EXP", amount=None):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.rect = pygame.Rect(0, 0, 14, 14)
        self.anim_offset = random.random() * 10
        if amount != None: self.amount = amount
        else:
            if item_type == "EXP": self.amount = 35
            else: self.amount = 25
        
    def update(self, p_x, p_y, mag_rad):
        dx = p_x - self.x
        dy = p_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist < mag_rad and dist > 0:
            dir_x = dx / dist
            dir_y = dy / dist
            self.x = self.x + dir_x * 8 
            self.y = self.y + dir_y * 8 
                
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface):
        img_key = "drop_" + self.item_type
        img = images.get(img_key)
        float_y = self.y + math.sin(pygame.time.get_ticks() * 0.005 + self.anim_offset) * 3
        
        if img != None: 
            surface.blit(img, img.get_rect(center=(int(self.x), int(float_y))))
        else:
            if self.item_type == "EXP": 
                pts =[
                    (self.x, float_y - 6), 
                    (self.x + 6, float_y), 
                    (self.x, float_y + 6), 
                    (self.x - 6, float_y)
                ]
                pygame.draw.polygon(surface, EXP_COLOR, pts) 
            elif self.item_type == "HP": 
                pygame.draw.rect(surface, HP_COLOR, (self.x - 6, float_y - 2, 12, 4))
                pygame.draw.rect(surface, HP_COLOR, (self.x - 2, float_y - 6, 4, 12))
            elif self.item_type == "SHIELD": 
                pygame.draw.circle(surface, SHIELD_COLOR, (int(self.x), int(float_y)), 6)

# ==========================================
# 4. 遊戲狀態與系統選單 
# ==========================================
def refresh_player_shield_max(fill_gain=False):
    old_max = player.max_shield
    if old_max < 1: old_max = 1
        
    old_ratio = player.shield / old_max
    
    player.max_shield = int(player.max_hp * 0.2)
    if player.max_shield < 1: player.max_shield = 1
        
    if fill_gain == True: 
        diff = player.max_shield - old_max
        if diff < 0: diff = 0
        player.shield = player.shield + diff
        if player.shield > player.max_shield: player.shield = player.max_shield
    else: 
        player.shield = player.max_shield * old_ratio
        if player.shield > player.max_shield: player.shield = player.max_shield

def apply_upgrade(choice):
    global game_state, selected_upgrade_position
    if choice == 0: 
        player.max_hp += 50
        player.hp += 50
        refresh_player_shield_max(fill_gain=True)
    elif choice == 1: 
        player.shoot_delay -= 2
        if player.shoot_delay < 2: player.shoot_delay = 2
    elif choice == 2: player.stamina_regen += 0.3
    elif choice == 3: player.bullet_count += 1
    elif choice == 4: player.bullet_damage_bonus += 2
    elif choice == 5: 
        player.max_stamina += 25
        player.stamina += 25
    elif choice == 6: 
        player.dash_cost -= 8
        if player.dash_cost < 15: player.dash_cost = 15
    elif choice == 7: player.base_speed += 0.7
    elif choice == 8: player.magnet_radius += 45
    elif choice == 9: 
        player.bullet_spread -= 3
        if player.bullet_spread < 6: player.bullet_spread = 6
    elif choice == 10: player.dash_duration += 2
    elif choice == 11: 
        player.hp += 60
        if player.hp > player.max_hp: player.hp = player.max_hp
    elif choice == 12: player.invincible_duration += 30
    elif choice == 13: player.damage_reduction += 3
    elif choice == 14: player.dash_speed += 3
    elif choice == 15: 
        player.max_hp += 25
        player.max_stamina += 15
        player.hp += 25
        player.stamina += 15
        refresh_player_shield_max(fill_gain=True)
    elif choice == 16: 
        player.magnet_radius += 25
        player.stamina_regen += 0.15
    elif choice == 17: player.extra_same_path_bullets += 1
    elif choice == 18: player.guidance_level += 1
    elif choice == 19: player.aura_level += 1
    elif choice == 20: player.regen_level += 1
    elif choice == 21: player.exp_multiplier += 0.2
    elif choice == 22: 
        player.pistol_mag_size += 10
        player.sniper_mag_size += 2
        player.pistol_ammo += 10
        player.sniper_ammo += 2
    elif choice == 23: 
        player.reload_duration -= 18
        if player.reload_duration < 35: player.reload_duration = 35
        
    add_chosen_upgrade(choice)
    current_upgrade_choices.clear()
    selected_upgrade_position = None
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
    {"title": "擴容彈匣", "desc": ["困難限定卡牌", "步槍+10 狙擊+2"], "type": "attack", "weight": 4, "challenge_only": True},
    {"title": "快拆彈匣", "desc": ["困難限定卡牌", "換彈時間縮短"], "type": "support", "weight": 3, "challenge_only": True}
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
    "v1.6",
    "- 世界座標統整為螢幕相對座標，解決發射偏移與子彈卡邊界問題",
    "- 修正所有物件更新方式與刪除機制",
    "v1.5 終極完全體",
    "- 將 24 種強化與開放世界整合進動態貼圖引擎",
    "- 融合 12 種不同特性的武器與右鍵大絕招系統",
    "- 修正傷害跳字層級，保證顯示於最上層",
    "v1.4",
    "- 統一所有底層座標為 Vector2",
    "v1.367",
    "- 小兵與精英小兵分為近戰和遠程兩類",
    "v1.315",
    "- 困難模式敵人強度提升為 1.75 倍，並啟用彈匣與換彈系統",
    "v1.185",
    "- Boss 出場動畫期間會暫停遊戲並顯示提示語",
    "- 新增裂空突擊者 Boss：衝向玩家並向兩側發射子彈",
]

show_changelog = False
changelog_scroll = 0
changelog_content_surface = None
changelog_max_scroll = 0

def choose_upgrade_cards():
    global current_upgrade_choices, selected_upgrade_position
    
    available =[]
    for i in range(len(upgrade_options)):
        option = upgrade_options[i]
        if game_mode == CHALLENGE_MODE or option.get("challenge_only") != True:
            available.append(i)
            
    card_count = 3
    if len(available) < 3: card_count = len(available)
        
    current_upgrade_choices =[]
    for _ in range(card_count):
        total_weight = 0
        for i in range(len(available)):
            idx = available[i]
            total_weight = total_weight + upgrade_options[idx].get("weight", 1)
            
        pick = random.uniform(0, total_weight)
        running_weight = 0
        
        for i in range(len(available)):
            idx = available[i]
            running_weight = running_weight + upgrade_options[idx].get("weight", 1)
            if pick <= running_weight:
                current_upgrade_choices.append(idx)
                available.remove(idx)
                break
                
    selected_upgrade_position = None

def add_chosen_upgrade(choice):
    title = upgrade_options[choice]["title"]
    for i in range(len(chosen_upgrades)):
        upgrade = chosen_upgrades[i]
        if upgrade["title"] == title:
            upgrade["count"] += 1
            return
            
    chosen_upgrades.append({"title": title, "count": 1})

def wrap_text(text, text_font, max_width):
    lines =[]
    current = ""
    for char in text:
        test = current + char
        if text_font.size(test)[0] <= max_width: 
            current = test
        else:
            if current != "": lines.append(current)
            current = char
    if current != "": lines.append(current)
    return lines

def rebuild_changelog_cache(content_width, content_height):
    global changelog_content_surface, changelog_max_scroll
    content_lines =[]
    for i in range(len(CHANGELOG)):
        line = CHANGELOG[i]
        if line.startswith("v"): color = YELLOW 
        else: color = WHITE
            
        wrapped_lines = wrap_text(line, font, content_width - 20)
        for j in range(len(wrapped_lines)):
            content_lines.append((wrapped_lines[j], color))
        content_lines.append(("", WHITE))
        
    surface_height = len(content_lines) * 34 + 10
    if content_height > surface_height: surface_height = content_height
        
    changelog_content_surface = pygame.Surface((content_width, surface_height), pygame.SRCALPHA)
    for i in range(len(content_lines)):
        line_data = content_lines[i]
        if line_data[0] != "": 
            text_surf = font.render(line_data[0], True, line_data[1])
            changelog_content_surface.blit(text_surf, (0, 6 + i * 34))
            
    changelog_max_scroll = surface_height - content_height
    if changelog_max_scroll < 0: changelog_max_scroll = 0

def draw_changelog_popup(surface):
    popup = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 250, 700, 500)
    panel = pygame.Surface((popup.width, popup.height), pygame.SRCALPHA)
    panel.fill((18, 20, 32, 235))
    surface.blit(panel, popup.topleft)
    pygame.draw.rect(surface, WHITE, popup, 3, border_radius=12)

    title = large_font.render("更新日誌", True, YELLOW)
    surface.blit(title, (popup.centerx - int(title.get_width()/2), popup.y + 25))

    content_rect = pygame.Rect(popup.x + 40, popup.y + 90, popup.width - 80, popup.height - 180)
    if changelog_content_surface == None: 
        rebuild_changelog_cache(content_rect.width, content_rect.height)

    scroll_y = changelog_scroll
    if scroll_y > changelog_max_scroll: scroll_y = changelog_max_scroll
        
    surface.blit(changelog_content_surface, content_rect.topleft, pygame.Rect(0, scroll_y, content_rect.width, content_rect.height))
    pygame.draw.rect(surface, GRAY, content_rect, 1)

    if changelog_max_scroll > 0:
        bar_h = int(content_rect.height * content_rect.height / changelog_content_surface.get_height())
        if bar_h < 40: bar_h = 40
        bar_y = content_rect.y + int((content_rect.height - bar_h) * (scroll_y / changelog_max_scroll))
        pygame.draw.rect(surface, GRAY, (content_rect.right + 8, content_rect.y, 8, content_rect.height), border_radius=4)
        pygame.draw.rect(surface, YELLOW, (content_rect.right + 8, bar_y, 8, bar_h), border_radius=4)

    changelog_close_button.center = (popup.centerx, popup.bottom - 40)
    mouse_pos = pygame.mouse.get_pos()
    if changelog_close_button.collidepoint(mouse_pos) == True: close_color = RED 
    else: close_color = (150, 50, 50)
        
    pygame.draw.rect(surface, close_color, changelog_close_button, border_radius=10)
    pygame.draw.rect(surface, WHITE, changelog_close_button, 3, border_radius=10)
    close_txt = font.render("關閉", True, WHITE)
    surface.blit(close_txt, (changelog_close_button.centerx - int(close_txt.get_width()/2), changelog_close_button.centery - int(close_txt.get_height()/2)))

def draw_pause_upgrade_log(surface):
    panel_rect = pygame.Rect(WIDTH//2 - 330, HEIGHT//2 + 235, 660, 260)
    panel = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    panel.fill((18, 20, 30, 205))
    surface.blit(panel, panel_rect.topleft)
    pygame.draw.rect(surface, WHITE, panel_rect, 2, border_radius=8)

    title = small_font.render("本局強化紀錄（滑鼠滾輪上下瀏覽）", True, YELLOW)
    surface.blit(title, (panel_rect.x + 16, panel_rect.y + 12))
    content_rect = pygame.Rect(panel_rect.x + 16, panel_rect.y + 44, panel_rect.width - 42, panel_rect.height - 58)

    rows =[]
    for i in range(len(chosen_upgrades)):
        upgrade = chosen_upgrades[i]
        
        # 尋找說明
        option = None
        for j in range(len(upgrade_options)):
            if upgrade_options[j]["title"] == upgrade["title"]:
                option = upgrade_options[j]
                break
                
        if option != None: desc = option["desc"][0] + " / " + option["desc"][1]
        else: desc = ""
            
        if upgrade["count"] > 1: count_str = " x" + str(upgrade["count"])
        else: count_str = ""
            
        rows.append((upgrade["title"] + count_str, desc))

    if len(rows) == 0:
        surface.blit(small_font.render("尚未選擇任何強化", True, GRAY), (content_rect.x, content_rect.y + 8))
        return

    row_h = 54
    content_height = len(rows) * row_h
    if content_height < content_rect.height: content_height = content_rect.height
        
    max_scroll = content_height - content_rect.height
    if max_scroll < 0: max_scroll = 0
        
    scroll_y = pause_upgrade_scroll
    if scroll_y > max_scroll: scroll_y = max_scroll
        
    content_surface = pygame.Surface((content_rect.width, content_height), pygame.SRCALPHA)

    for i in range(len(rows)):
        name = rows[i][0]
        desc = rows[i][1]
        y = i * row_h
        content_surface.blit(small_font.render(name, True, WHITE), (0, y))
        wrapped_desc = wrap_text(desc, tiny_font, content_rect.width - 20)
        for j in range(len(wrapped_desc)):
            line = wrapped_desc[j]
            content_surface.blit(tiny_font.render(line, True, YELLOW), (18, y + 25 + j * 20))

    surface.blit(content_surface, content_rect.topleft, pygame.Rect(0, scroll_y, content_rect.width, content_rect.height))
    if max_scroll > 0:
        bar_h = int(content_rect.height * content_rect.height / content_height)
        if bar_h < 36: bar_h = 36
        bar_y = content_rect.y + int((content_rect.height - bar_h) * (scroll_y / max_scroll))
        pygame.draw.rect(surface, GRAY, (content_rect.right + 8, content_rect.y, 7, content_rect.height), border_radius=4)
        pygame.draw.rect(surface, YELLOW, (content_rect.right + 8, bar_y, 7, bar_h), border_radius=4)

def draw_upgrade_summary(surface, x, y, max_items=6, title="已選強化"):
    panel_width = 260
    row_height = 28
    
    hidden_count = len(chosen_upgrades) - max_items
    if hidden_count < 0: hidden_count = 0
        
    row_count = len(chosen_upgrades)
    if row_count > max_items: row_count = max_items
    if row_count < 1: row_count = 1
        
    panel_height = 44 + row_count * row_height
    if hidden_count > 0: panel_height += row_height
        
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((18, 20, 30, 185))
    surface.blit(panel, (x, y))
    pygame.draw.rect(surface, WHITE, (x, y, panel_width, panel_height), 2, border_radius=8)

    total_count = 0
    for i in range(len(chosen_upgrades)):
        total_count += chosen_upgrades[i]["count"]
        
    if len(chosen_upgrades) > 0: title_label = title + " (" + str(total_count) + ")"
    else: title_label = title
        
    surface.blit(small_font.render(title_label, True, YELLOW), (x + 14, y + 10))

    if len(chosen_upgrades) == 0:
        surface.blit(small_font.render("尚未選擇", True, GRAY), (x + 14, y + 42))
        return

    # 只取最後 max_items 個
    start_idx = len(chosen_upgrades) - max_items
    if start_idx < 0: start_idx = 0
        
    visible_upgrades = chosen_upgrades[start_idx:]
    for i in range(len(visible_upgrades)):
        upgrade = visible_upgrades[i]
        if upgrade["count"] > 1: suffix = " x" + str(upgrade["count"])
        else: suffix = ""
        surface.blit(small_font.render(upgrade["title"] + suffix, True, WHITE), (x + 14, y + 42 + i * row_height))

    if hidden_count > 0:
        surface.blit(small_font.render("還有 " + str(hidden_count) + " 種...", True, GRAY), (x + 14, y + 42 + len(visible_upgrades) * row_height))

def reset_game(initial_state="PLAYING", mode=None):
    global player, bullets, enemy_bullets, enemies, particles, items, trails, damage_texts
    global boss, boss_active, boss_defeated, next_boss_level, boss_spawn_count, game_state, game_mode
    global current_upgrade_choices, selected_upgrade_position, chosen_upgrades, show_changelog, changelog_scroll
    global changelog_content_surface, changelog_max_scroll, pause_upgrade_scroll, global_offset_x, global_offset_y
    global shoot_cooldown, key_buffer, boss_warning_timer
    
    if mode != None: game_mode = mode
    
    player = Player()
    bullets = []
    enemy_bullets = []
    enemies = []
    particles = []
    items =[]
    trails = []
    damage_texts =[]
    
    boss = None
    boss_active = False
    boss_defeated = False
    next_boss_level = 5
    boss_spawn_count = 0
    current_upgrade_choices =[]
    selected_upgrade_position = None
    chosen_upgrades =[]
    
    show_changelog = False
    changelog_scroll = 0
    changelog_content_surface = None
    changelog_max_scroll = 0
    pause_upgrade_scroll = 0
    
    global_offset_x = 0
    global_offset_y = 0
    shoot_cooldown = 0
    key_buffer =[]
    boss_warning_timer = 0
    
    stop_sound("boss_bgm")
    if initial_state == "PLAYING":
        try: pygame.mixer.music.play(-1)
        except: pass
        
    game_state = initial_state
    if game_mode == NORMAL_MODE: interval = NORMAL_SPAWN_INTERVAL
    else: interval = CHALLENGE_SPAWN_INTERVAL
    pygame.time.set_timer(SPAWN_ENEMY_EVENT, interval)

reset_game("MENU")

# ==========================================
# 5. 遊戲主迴圈
# ==========================================
running = True
while running:
    # --- 動態調整 UI 位置 ---
    start_button.center = (int(WIDTH/2), int(HEIGHT/2) + 20)
    changelog_button.center = (int(WIDTH/2), int(HEIGHT/2) + 95)
    exit_button.center = (int(WIDTH/2), int(HEIGHT/2) + 170)
    
    normal_button.center = (int(WIDTH/2) - 220, int(HEIGHT/2))
    challenge_button.center = (int(WIDTH/2) + 220, int(HEIGHT/2))
    difficulty_back_button.center = (int(WIDTH/2), int(HEIGHT/2) + 245)

    cards[0].center = (int(WIDTH/2) - 250, int(HEIGHT/2))
    cards[1].center = (int(WIDTH/2), int(HEIGHT/2))
    cards[2].center = (int(WIDTH/2) + 250, int(HEIGHT/2))
    confirm_upgrade_button.center = (int(WIDTH/2), int(HEIGHT/2) + 200)

    restart_button.center = (int(WIDTH/2) - 120, int(HEIGHT/2) + 100)
    menu_button.center = (int(WIDTH/2) + 120, int(HEIGHT/2) + 100)

    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
            
        if WINDOW_FOCUS_GAINED != None and event.type == WINDOW_FOCUS_GAINED:
            switch_to_english_input()
            
        if event.type == pygame.MOUSEWHEEL:
            if game_state == "MENU" and show_changelog == True:
                changelog_scroll = changelog_scroll - event.y * 55
                if changelog_scroll < 0: changelog_scroll = 0
                if changelog_scroll > changelog_max_scroll: changelog_scroll = changelog_max_scroll
            elif game_state == "PAUSED":
                pause_upgrade_scroll = pause_upgrade_scroll - event.y * 45
                if pause_upgrade_scroll < 0: pause_upgrade_scroll = 0
        
        if event.type == pygame.VIDEORESIZE:
            if fullscreen_mode == False:
                WIDTH = event.w
                HEIGHT = event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == "PLAYING": 
                    game_state = "PAUSED"
                elif game_state == "PAUSED":
                    switch_to_english_input()
                    game_state = "PLAYING"
                elif game_state == "DIFFICULTY": 
                    game_state = "MENU"
                    
            if event.key == pygame.K_r and game_state == "PLAYING":
                player.start_reload()
                
            if game_state == "GAME_OVER":
                if event.key == pygame.K_r: 
                    reset_game("PLAYING", game_mode)
                    switch_to_english_input()
                    
            if game_state == "PLAYING":
                if event.key == pygame.K_F11:
                    if fullscreen_mode == True: fullscreen_mode = False
                    else: fullscreen_mode = True
                        
                    if fullscreen_mode == True:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                    WIDTH, HEIGHT = screen.get_size()
                
                key_buffer.append(event.key)
                if len(key_buffer) > len(CHEAT_CODE): 
                    key_buffer.pop(0) 
                    
                if key_buffer == CHEAT_CODE:
                    if player.god_mode == True: player.god_mode = False
                    else: player.god_mode = True
                    play_sound("levelup")
                    key_buffer =[] 
                
                if event.key == pygame.K_e:
                    player.current_weapon_idx = player.current_weapon_idx + 1
                    if player.current_weapon_idx >= len(player.weapons):
                        player.current_weapon_idx = 0
                    play_sound("exp")
                    
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if game_state == "GAME_OVER":
                if restart_button.collidepoint(mouse_pos): 
                    reset_game("PLAYING", game_mode)
                    switch_to_english_input()
                elif menu_button.collidepoint(mouse_pos): 
                    reset_game("MENU", NORMAL_MODE)
                    
            elif game_state == "MENU":
                if show_changelog == True:
                    if changelog_close_button.collidepoint(mouse_pos): 
                        show_changelog = False
                elif start_button.collidepoint(mouse_pos): 
                    game_state = "DIFFICULTY"
                elif changelog_button.collidepoint(mouse_pos):
                    show_changelog = True
                    changelog_scroll = 0
                    if changelog_content_surface == None: 
                        rebuild_changelog_cache(720, 455)
                elif exit_button.collidepoint(mouse_pos): 
                    running = False
                    
            elif game_state == "DIFFICULTY":
                if normal_button.collidepoint(mouse_pos): 
                    reset_game("PLAYING", NORMAL_MODE)
                    switch_to_english_input()
                elif challenge_button.collidepoint(mouse_pos): 
                    reset_game("PLAYING", CHALLENGE_MODE)
                    switch_to_english_input()
                elif difficulty_back_button.collidepoint(mouse_pos): 
                    game_state = "MENU"
                    
            elif game_state == "PAUSED":
                btn1 = pygame.Rect(int(WIDTH/2) - 240, int(HEIGHT/2) + 70, 220, 60)
                btn2 = pygame.Rect(int(WIDTH/2) + 20, int(HEIGHT/2) + 70, 220, 60)
                btn3 = pygame.Rect(int(WIDTH/2) - 240, int(HEIGHT/2) + 150, 220, 60)
                btn4 = pygame.Rect(int(WIDTH/2) + 20, int(HEIGHT/2) + 150, 220, 60)
                
                if btn1.collidepoint(mouse_pos): 
                    switch_to_english_input()
                    game_state = "PLAYING"
                elif btn2.collidepoint(mouse_pos): 
                    reset_game("MENU", NORMAL_MODE)
                elif btn3.collidepoint(mouse_pos): 
                    reset_game("PLAYING", game_mode)
                    switch_to_english_input()
                elif btn4.collidepoint(mouse_pos): 
                    running = False
                    
            elif game_state == "LEVEL_UP":
                if selected_upgrade_position != None and confirm_upgrade_button.collidepoint(mouse_pos):
                    apply_upgrade(current_upgrade_choices[selected_upgrade_position])
                else:
                    for i in range(len(cards)):
                        card = cards[i]
                        if i < len(current_upgrade_choices) and card.collidepoint(mouse_pos):
                            selected_upgrade_position = i
                            break
                            
        if event.type == SPAWN_ENEMY_EVENT and game_state == "PLAYING":
            if boss_active == False:
                elite_chance = 0.03 + player.level * 0.006
                if elite_chance > 0.15: elite_chance = 0.15
                is_elite = False
                if random.random() < elite_chance: is_elite = True
                enemies.append(Enemy(player.level, is_elite))

    # --- PLAYING 邏輯更新 ---
    if game_state == "PLAYING":
        check_boss_level = player.level % 4
        if check_boss_level == 0 and player.level > 0 and boss_active == False:
            is_defeated = False
            for i in range(len(defeated_boss_levels)):
                if defeated_boss_levels[i] == player.level:
                    is_defeated = True
            
            if is_defeated == False:
                boss_spawn_count += 1
                boss_types = ["YELLOW", "RED", "PURPLE", "CHARGER"]
                chosen_boss = random.choice(boss_types)
                boss = Boss(chosen_boss, next_boss_level)
                
                boss_active = True
                boss_defeated = False
                boss_warning_timer = 120 
                enemies.clear() # 清空小兵迎戰
                try: pygame.mixer.music.stop()
                except: pass
                play_sound("boss_bgm", loop=-1) 

        # Boss 入場動畫暫停所有邏輯
        if boss_active == True and boss != None and boss.state == "ENTRANCE":
            boss.update(player.pos, bullets)
            if boss_warning_timer > 0: boss_warning_timer -= 1
            
            # --- 繪製入場畫面 ---
            screen.fill(BLACK)
            draw_map_bounds(screen)
            for i in range(len(items)): items[i].draw(screen)
            for i in range(len(particles)): particles[i].draw(screen)
            for i in range(len(bullets)): bullets[i].draw(screen)
            for i in range(len(enemy_bullets)): enemy_bullets[i].draw(screen) 
            for i in range(len(enemies)): enemies[i].draw(screen)
            for i in range(len(trails)): trails[i].draw(screen)
            
            boss.draw(screen)
            player.draw(screen, player.weapons[player.current_weapon_idx])
            
            dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            dim_surface.fill((0, 0, 0, 180))
            screen.blit(dim_surface, (0, 0))
            
            title = large_font.render(boss.get_intro_title(), True, YELLOW)
            screen.blit(title, (int(WIDTH/2) - int(title.get_width()/2), int(HEIGHT/2) - 190))
        
            progress = boss.state_timer / boss.entrance_duration
            if progress > 1: progress = 1
            bar_rect = pygame.Rect(int(WIDTH/2) - 220, int(HEIGHT/2) - 120, 440, 18)
            pygame.draw.rect(screen, GRAY, bar_rect, border_radius=8)
            pygame.draw.rect(screen, RED, (bar_rect.x, bar_rect.y, int(bar_rect.width * progress), bar_rect.height), border_radius=8)
            pygame.draw.rect(screen, WHITE, bar_rect, 2, border_radius=8)
        
            warning_lines = boss.get_intro_lines()
            for i in range(len(warning_lines)):
                if i == 0: color = RED 
                else: color = WHITE
                text = font.render(warning_lines[i], True, color)
                screen.blit(text, (int(WIDTH/2) - int(text.get_width()/2), int(HEIGHT/2) - 75 + i * 42))
        
            pygame.display.flip()
            clock.tick(FPS)
            continue

        mouse_btns = pygame.mouse.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        current_wep = player.weapons[player.current_weapon_idx]

        # 玩家左鍵普通射擊 (支援螢幕/世界座標統一 & 扇形擴散)
        if mouse_btns[0] == True and shoot_cooldown <= 0 and player.is_dashing == False and player.can_fire_current_weapon() == True:
            # 轉換為真實的世界座標
            world_mouse = pygame.math.Vector2(mouse_x + global_offset_x, mouse_y + global_offset_y)
            actual_muzzle_start = player.get_muzzle_pos(world_mouse)
            
            wep_type = current_wep.bullet_type
            is_piercing = False
            if wep_type == "piercing" or wep_type == "laser" or wep_type == "cannon" or wep_type == "flamethrower":
                is_piercing = True
                
            dx = world_mouse.x - player.pos.x
            dy = world_mouse.y - player.pos.y
            dist = math.sqrt(dx * dx + dy * dy)
            base_dir = pygame.math.Vector2(0, 0)
            if dist > 0: 
                base_dir.x = dx / dist
                base_dir.y = dy / dist
            else: 
                base_dir.x = 1
            
            if is_piercing == True: current_spread = player.bullet_spread * 0.35
            else: current_spread = player.bullet_spread
                
            start_angle = -(player.bullet_count - 1) * current_spread / 2
            
            for c in range(player.bullet_count):
                angle_offset = start_angle + c * current_spread
                shot_dir = base_dir.rotate(angle_offset)
                
                same_path_count = 1 + player.extra_same_path_bullets
                for j in range(same_path_count):
                    spawn_offset = shot_dir * (j * 18)
                    spawn_pos = actual_muzzle_start + spawn_offset
                    
                    if wep_type == "shotgun":
                        for i in range(-2, 3):
                            final_dir = shot_dir.rotate(i * 12)
                            target_pos = spawn_pos + final_dir * 100
                            bullets.append(Bullet(spawn_pos, target_pos, current_wep, player.guidance_level))
                    elif wep_type == "flamethrower":
                        target_pos = spawn_pos + shot_dir * 100
                        target_pos.x += random.randint(-40, 40)
                        target_pos.y += random.randint(-40, 40)
                        bullets.append(Bullet(spawn_pos, target_pos, current_wep, player.guidance_level))
                    else:
                        target_pos = spawn_pos + shot_dir * 100
                        bullets.append(Bullet(spawn_pos, target_pos, current_wep, player.guidance_level))
            
            if is_piercing == True: shoot_cooldown = 30
            else: shoot_cooldown = current_wep.shoot_delay
                
            if is_piercing == True and shoot_cooldown < 15: 
                shoot_cooldown = 15 # 強力穿透武器防卡冷卻
                
            player.consume_current_ammo()
            play_sound(current_wep.sound_name)
            
        # 玩家右鍵大絕招
        if mouse_btns[2] == True and player.skill_cd <= 0 and player.energy >= player.skill_cost and player.is_dashing == False:
            player.energy -= player.skill_cost
            player.skill_cd = player.skill_max_cd
            play_sound("shoot_cannon") 
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
                player.hp = player.hp + heal
                if player.hp > player.max_hp: player.hp = player.max_hp
                player.regen_progress -= heal
        else: 
            player.regen_progress = 0

        if player.is_dashing == True: 
            trails.append(DashTrail(player.pos, player.size))
            
        for i in range(len(trails) - 1, -1, -1):
            t = trails[i]
            t.update()
            if t.life <= 0: trails.remove(t)
            
        # 子彈更新區塊
        world_rect = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
        for i in range(len(bullets) - 1, -1, -1):
            b = bullets[i]
            b.update()
            
            if b.explode == True:
                play_sound("shoot_cannon") 
                for _ in range(30): particles.append(Particle(b.x, b.y, ORANGE))
                for j in range(len(enemies) - 1, -1, -1):
                    e = enemies[j]
                    dx = e.x - b.x
                    dy = e.y - b.y
                    if math.sqrt(dx*dx + dy*dy) < 120: 
                        shield_damage = b.damage
                        if e.shield < shield_damage: shield_damage = e.shield
                        e.shield -= shield_damage
                        e.hp -= (b.damage - shield_damage)
                        
                        if b.damage >= 30: txt_color = YELLOW 
                        else: txt_color = WHITE
                        damage_texts.append(DamageText(e.x, e.y - 15, b.damage, txt_color))
                        
                        if e.hp <= 0: 
                            if random.random() < e.exp_drop_chance: 
                                items.append(DropItem(e.x, e.y, "EXP"))
                            enemies.remove(e)
                            
                if boss_active == True:
                    b_dx = boss.x - b.x
                    b_dy = boss.y - b.y
                    if math.sqrt(b_dx*b_dx + b_dy*b_dy) < 150: 
                        boss.hp -= b.damage
                        if b.damage >= 30: txt_color = YELLOW 
                        else: txt_color = WHITE
                        damage_texts.append(DamageText(boss.x, boss.y - 30, b.damage, txt_color))
                bullets.remove(b)
                continue
                
            # 開放世界中判斷飛出大邊界
            if b.lifespan <= 0 or world_rect.inflate(500, 500).colliderect(b.rect) == False: 
                bullets.remove(b)
            
        for i in range(len(enemy_bullets) - 1, -1, -1):
            eb = enemy_bullets[i]
            eb.update()
            if world_rect.inflate(500, 500).colliderect(eb.rect) == False: 
                enemy_bullets.remove(eb)
            
        for i in range(len(damage_texts) - 1, -1, -1):
            dt = damage_texts[i]
            dt.update()
            if dt.timer <= 0: damage_texts.remove(dt)    
            
        for i in range(len(enemies)):
            e = enemies[i]
            e.update(player.pos, enemies)
            e.emit_attacks(enemy_bullets, player.pos)
            
        for i in range(len(particles) - 1, -1, -1):
            p = particles[i]
            p.update()
            if p.timer <= 0: particles.remove(p)

        if boss_warning_timer > 0: boss_warning_timer -= 1

        if boss_active == True:
            boss.update(player.pos, bullets) 
            boss.emit_attacks(enemy_bullets)
            
        if boss_active == True and boss.state == "DEFEAT" and boss.defeat_timer > 60:
            boss_active = False
            boss_defeated = True
            next_boss_level += 5
            stop_sound("boss_bgm")
            try: pygame.mixer.music.play(-1)
            except: pass

        # 玩家子彈撞到敵人
        for i in range(len(bullets) - 1, -1, -1):
            b = bullets[i]
            hit_something = False
            for j in range(len(enemies) - 1, -1, -1):
                e = enemies[j]
                if b.rect.colliderect(e.rect) == True:
                    if b.b_type == "frost": e.frost_timer = 120 
                    if b.b_type == "cannon": 
                        push_dx = e.x - player.pos.x
                        push_dy = e.y - player.pos.y
                        push_dist = math.sqrt(push_dx*push_dx + push_dy*push_dy)
                        if push_dist > 0: 
                            e.x += (push_dx / push_dist) * 30 
                            e.y += (push_dy / push_dist) * 30 
                    elif b.b_type == "flame_grenade": 
                        b.explode = True 
                        break
                        
                    shield_damage = b.damage
                    if e.shield < shield_damage: shield_damage = e.shield
                    e.shield -= shield_damage
                    actual_damage = b.damage - shield_damage
                    e.hp -= actual_damage
                    
                    if b.damage >= 30: txt_color = YELLOW 
                    else: txt_color = WHITE
                    damage_texts.append(DamageText(e.x, e.y - 15, b.damage, txt_color))
                    hit_something = True
                    for _ in range(5): particles.append(Particle(e.x, e.y, b.color))
                    play_sound("hit")
                    
                    if e.hp <= 0:
                        if e.is_elite == True: p_count = 12
                        else: p_count = 6
                        for _ in range(p_count): particles.append(Particle(e.x, e.y, RED))
                        
                        if random.random() < e.exp_drop_chance: 
                            if e.is_elite == True: gem_count = 3 
                            else: gem_count = 1
                            for _ in range(gem_count): 
                                items.append(DropItem(e.x + random.randint(-12,12), e.y + random.randint(-12,12), "EXP", 35))
                        if random.random() < e.health_drop_chance: 
                            if e.is_elite == True: hp_amt = 40
                            else: hp_amt = 25
                            items.append(DropItem(e.x, e.y, "HP", hp_amt))
                        enemies.remove(e)
            
            if b.explode == True: 
                continue 

            if boss_active == True and b.rect.colliderect(boss.rect) == True:
                hit_something = True
                if boss.can_take_damage() == False:
                    for _ in range(5): particles.append(Particle(boss.x, boss.y, GRAY))
                elif boss.state != "DEFEAT":
                    if b.b_type == "frost": boss.frost_timer = 60 
                    boss.hp -= b.damage
                    
                    if b.damage >= 30: txt_color = YELLOW 
                    else: txt_color = WHITE
                    damage_texts.append(DamageText(boss.x, boss.y - 30, b.damage, txt_color))
                    
                    for _ in range(8): particles.append(Particle(boss.x, boss.y, YELLOW))
                    play_sound("hit")
                    
                    if boss.hp <= 0:
                        boss.state = "DEFEAT"
                        boss.defeat_timer = 0
                        for _ in range(40): 
                            items.append(DropItem(boss.x + random.randint(-60,60), boss.y + random.randint(-60,60), "EXP", 35))
                        for _ in range(5): 
                            drop_type = "HP"
                            if random.random() < 0.5: drop_type = "SHIELD"
                            items.append(DropItem(boss.x + random.randint(-40,40), boss.y + random.randint(-40,40), drop_type, 25))
                        for _ in range(50): particles.append(Particle(boss.x, boss.y, YELLOW))
                        
            if hit_something == True and b.is_piercing == False:
                is_in_list = False
                for check_b in bullets:
                    if check_b == b: is_in_list = True
                if is_in_list == True: bullets.remove(b)

        # 電弧光環傷害
        if player.aura_level > 0:
            aura_radius = 95 + player.aura_level * 25
            aura_damage = 0.015 * player.aura_level
            for i in range(len(enemies) - 1, -1, -1):
                e = enemies[i]
                dx = player.pos.x - e.x
                dy = player.pos.y - e.y
                if math.sqrt(dx*dx + dy*dy) <= aura_radius:
                    shield_damage = aura_damage
                    if e.shield < shield_damage: shield_damage = e.shield
                    e.shield -= shield_damage
                    e.hp -= (aura_damage - shield_damage)
                    
                    if random.random() < 0.08: particles.append(Particle(e.x, e.y, BLUE))
                    if e.hp <= 0:
                        if e.is_elite == True: p_count = 8
                        else: p_count = 4
                        for _ in range(p_count): particles.append(Particle(e.x, e.y, e.color))
                        
                        if random.random() < e.exp_drop_chance: 
                            items.append(DropItem(e.x, e.y, "EXP"))
                        if random.random() < e.health_drop_chance: 
                            if e.is_elite == True: hp_amt = 40
                            else: hp_amt = 25
                            items.append(DropItem(e.x, e.y, "HP", hp_amt))
                        enemies.remove(e)

        # 玩家受傷
        def player_take_damage(dmg):
            global game_state
            if player.god_mode == True: return 
            if player.invincible_timer <= 0 and player.is_dashing == False:
                actual_dmg = dmg - player.damage_reduction
                if actual_dmg < 1: actual_dmg = 1
                    
                if player.shield > 0:
                    if player.shield >= actual_dmg: 
                        player.shield -= actual_dmg
                        actual_dmg = 0
                    else: 
                        actual_dmg -= player.shield
                        player.shield = 0
                        
                if actual_dmg > 0: player.hp -= actual_dmg
                player.invincible_timer = player.invincible_duration
                play_sound("hurt")
                
                if player.hp <= 0:
                    game_state = "GAME_OVER"
                    play_sound("gameover")
                    stop_sound("boss_bgm")  
                    try: pygame.mixer.music.stop()
                    except: pass

        for i in range(len(enemies)):
            e = enemies[i]
            if e.combat_type == "melee" and player.rect.colliderect(e.rect): 
                player_take_damage(e.damage)
                
        for i in range(len(enemy_bullets) - 1, -1, -1):
            eb = enemy_bullets[i]
            if player.rect.colliderect(eb.rect): 
                player_take_damage(25)
                is_in_list2 = False
                for check_eb in enemy_bullets:
                    if check_eb == eb: is_in_list2 = True
                if is_in_list2 == True: enemy_bullets.remove(eb)
                
        if boss_active == True and boss.state != "DEFEAT" and player.rect.colliderect(boss.rect): 
            player_take_damage(boss.collision_damage) 

        # 吃掉落物
        for i in range(len(items) - 1, -1, -1):
            item = items[i]
            item.update(player.pos, player.magnet_radius)
            if player.rect.colliderect(item.rect):
                items.remove(item)
                if item.item_type == "EXP": 
                    player.exp += int(item.amount * player.exp_multiplier)
                    play_sound("exp") 
                elif item.item_type == "HP": 
                    player.hp += item.amount
                    if player.hp > player.max_hp: player.hp = player.max_hp
                    play_sound("exp")
                elif item.item_type == "SHIELD": 
                    player.shield += item.amount
                    if player.shield > player.max_shield: player.shield = player.max_shield
                    play_sound("exp")

                if player.exp >= player.max_exp:
                    player.level += 1
                    player.exp = 0
                    player.max_exp = int(player.max_exp * 1.25) 
                    choose_upgrade_cards()
                    game_state = "LEVEL_UP"
                    play_sound("levelup") 

    # ==========================================
    # 畫面繪製區塊
    # ==========================================
    if game_state == "MENU":
        screen.fill(BLACK)
        for i in range(100):
            x = (i * 37) % WIDTH
            y = (i * 23) % HEIGHT
            brightness = int(100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i))
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)
            
        glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        title = large_font.render("Space War", True, BLUE)
        glow_surface.blit(title, (int(WIDTH/2) - int(title.get_width()/2), int(HEIGHT/2) - 120))
        for offset_pos in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -3), (0, 3), (-3, 0), (3, 0)]:
            glow_copy = glow_surface.copy()
            glow_copy.fill((0, 100, 255, 50), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(glow_copy, offset_pos)
            
        screen.blit(title, (int(WIDTH/2) - int(title.get_width()/2), int(HEIGHT/2) - 120))
        subtitle = font.render("霓虹驅魔人", True, WHITE)
        screen.blit(subtitle, (int(WIDTH/2) - int(subtitle.get_width()/2), int(HEIGHT/2) - 60))
        
        mouse_pos = pygame.mouse.get_pos()
        if start_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (100, 200, 100), start_button.inflate(10, 10), border_radius=12)
            pygame.draw.rect(screen, YELLOW, start_button.inflate(10, 10), 4, border_radius=12)
        else:
            pygame.draw.rect(screen, (50, 150, 50), start_button, border_radius=10)
            pygame.draw.rect(screen, WHITE, start_button, 3, border_radius=10)
        start_txt = font.render("開始遊戲", True, WHITE)
        screen.blit(start_txt, (start_button.centerx - int(start_txt.get_width()/2), start_button.centery - int(start_txt.get_height()/2)))

        if changelog_button.collidepoint(mouse_pos): cl_color = BLUE
        else: cl_color = (50, 100, 150)
        pygame.draw.rect(screen, cl_color, changelog_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, changelog_button, 3, border_radius=10)
        cl_txt = font.render("更新日誌", True, WHITE)
        screen.blit(cl_txt, (changelog_button.centerx - int(cl_txt.get_width()/2), changelog_button.centery - int(cl_txt.get_height()/2)))

        if exit_button.collidepoint(mouse_pos): ex_color = RED
        else: ex_color = (150, 50, 50)
        pygame.draw.rect(screen, ex_color, exit_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, exit_button, 3, border_radius=10)
        ex_txt = font.render("退出遊戲", True, WHITE)
        screen.blit(ex_txt, (exit_button.centerx - int(ex_txt.get_width()/2), exit_button.centery - int(ex_txt.get_height()/2)))
        
        controls_title = font.render("操作說明:", True, YELLOW)
        screen.blit(controls_title, (int(WIDTH/2) - int(controls_title.get_width()/2), int(HEIGHT/2) + 250))
        controls = ["移動: WASD", "射擊: 滑鼠左鍵", "大絕招: 滑鼠右鍵", "衝刺: Q鍵 或 SPACE", "切換武器: E鍵", "暫停: ESC", "全螢幕: F11"]
        for i in range(len(controls)): 
            c = controls[i]
            c_txt_obj = small_font.render(c, True, GRAY)
            screen.blit(c_txt_obj, (int(WIDTH/2) - int(c_txt_obj.get_width()/2), int(HEIGHT/2) + 285 + i*25))

        v_txt = font.render("v1.6 (終極完美版)", True, GRAY)
        screen.blit(v_txt, (20, HEIGHT - 40))

        if show_changelog == True: draw_changelog_popup(screen)
        
    elif game_state == "DIFFICULTY":
        screen.fill(BLACK)
        for i in range(100):
            x = (i * 37) % WIDTH; y = (i * 23) % HEIGHT
            brightness = int(100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i))
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)

        title = large_font.render("選擇難易度", True, YELLOW)
        subtitle = font.render("Boss 戰會清空小怪，專心迎戰核心威脅", True, GRAY)
        screen.blit(title, (int(WIDTH/2) - int(title.get_width()/2), int(HEIGHT/2) - 235))
        screen.blit(subtitle, (int(WIDTH/2) - int(subtitle.get_width()/2), int(HEIGHT/2) - 180))

        mouse_pos = pygame.mouse.get_pos()
        normal_hovered = normal_button.collidepoint(mouse_pos)
        challenge_hovered = challenge_button.collidepoint(mouse_pos)
        
        if normal_hovered: normal_color = (55, 125, 185)
        else: normal_color = (30, 70, 115)
        pygame.draw.rect(screen, normal_color, normal_button, border_radius=10)
        pygame.draw.rect(screen, YELLOW if normal_hovered else WHITE, normal_button, 4 if normal_hovered else 3, border_radius=10)
        
        if challenge_hovered: challenge_color = (190, 55, 70)
        else: challenge_color = (115, 35, 50)
        pygame.draw.rect(screen, challenge_color, challenge_button, border_radius=10)
        pygame.draw.rect(screen, YELLOW if challenge_hovered else WHITE, challenge_button, 4 if challenge_hovered else 3, border_radius=10)

        n_txt = large_font.render("普通", True, WHITE)
        screen.blit(n_txt, (normal_button.centerx - int(n_txt.get_width()/2), normal_button.y + 28))
        n_desc = small_font.render("標準節奏，無限彈藥", True, WHITE)
        screen.blit(n_desc, (normal_button.centerx - int(n_desc.get_width()/2), normal_button.y + 88))
        normal_lines = ["敵人強度：標準", "彈藥：無需換彈", "適合享受割草快感"]
        for i in range(len(normal_lines)):
            line = normal_lines[i]
            screen.blit(small_font.render(line, True, (210, 225, 240)), (normal_button.x + 42, normal_button.y + 132 + i * 28))

        c_txt = large_font.render("困難", True, WHITE)
        screen.blit(c_txt, (challenge_button.centerx - int(c_txt.get_width()/2), challenge_button.y + 28))
        c_desc = small_font.render("敵人 1.75 倍，啟用彈匣", True, WHITE)
        screen.blit(c_desc, (challenge_button.centerx - int(c_desc.get_width()/2), challenge_button.y + 88))
        challenge_lines = ["彈匣打完自動換彈 (也可按 R)", "追加困難專屬卡牌", "適合追求極限走位"]
        for i in range(len(challenge_lines)):
            line = challenge_lines[i]
            screen.blit(small_font.render(line, True, (255, 220, 220)), (challenge_button.x + 42, challenge_button.y + 132 + i * 28))

        if difficulty_back_button.collidepoint(mouse_pos): back_color = BLUE
        else: back_color = (50, 100, 150)
        pygame.draw.rect(screen, back_color, difficulty_back_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, difficulty_back_button, 3, border_radius=10)
        back_txt = font.render("返回", True, WHITE)
        screen.blit(back_txt, (difficulty_back_button.centerx - int(back_txt.get_width()/2), difficulty_back_button.centery - int(back_txt.get_height()/2)))

    else:
        # 遊戲內渲染 (PLAYING, PAUSED, LEVEL_UP, GAME_OVER 共用背景)
        if images.get("bg"):
            bg_img = pygame.transform.scale(images["bg"], (WIDTH, HEIGHT))
            bg_x = -global_offset_x % WIDTH
            bg_y = -global_offset_y % HEIGHT
            screen.blit(bg_img, (bg_x, bg_y))
            screen.blit(bg_img, (bg_x - WIDTH, bg_y))
            screen.blit(bg_img, (bg_x, bg_y - HEIGHT))
            screen.blit(bg_img, (bg_x - WIDTH, bg_y - HEIGHT))
        else: screen.fill(BLACK)
        
        draw_map_bounds(screen)
        
        # 將世界座標轉換為畫布螢幕座標 (繪製所有物件)
        for i in range(len(items)): items[i].draw(screen)
        for i in range(len(particles)): particles[i].draw(screen)
        for i in range(len(bullets)): bullets[i].draw(screen)
        for i in range(len(enemy_bullets)): enemy_bullets[i].draw(screen) 
        for i in range(len(enemies)): enemies[i].draw(screen)
        for i in range(len(trails)): trails[i].draw(screen)
        
        # 浮動傷害數字要在實體之上
        for i in range(len(damage_texts)): damage_texts[i].draw(screen)
            
        if boss_active == True: boss.draw(screen) 
        
        if game_state == "PLAYING" or game_state == "PAUSED":
            player.draw(screen, player.weapons[player.current_weapon_idx])
        else:
            player.draw(screen, None)
            
        if boss_active == True: draw_boss_direction_arrow(screen, boss)

        # 左上角 UI 面板
        pygame.draw.rect(screen, GRAY, (20, 20, 250, 15))
        exp_width = int(250 * (player.exp / player.max_exp))
        pygame.draw.rect(screen, BLUE, (20, 20, exp_width, 15))
        screen.blit(font.render("等級: " + str(player.level), True, WHITE), (280, 15))
        
        pygame.draw.rect(screen, GRAY, (20, 45, 200, 15))
        if player.hp > 30: hp_color = GREEN
        else: hp_color = RED
        draw_hp = player.hp
        if draw_hp < 0: draw_hp = 0
        hp_width = int(200 * (draw_hp / player.max_hp))
        pygame.draw.rect(screen, hp_color, (20, 45, hp_width, 15))
        screen.blit(font.render("血量", True, WHITE), (230, 40))
        
        pygame.draw.rect(screen, GRAY, (20, 70, 200, 12))
        draw_shield = player.shield
        if draw_shield < 0: draw_shield = 0
        shield_width = int(200 * (draw_shield / player.max_shield))
        pygame.draw.rect(screen, BLUE, (20, 70, shield_width, 12))
        screen.blit(font.render("護盾", True, WHITE), (230, 62))
        
        pygame.draw.rect(screen, GRAY, (20, 95, 150, 10))
        stamina_width = int(150 * (player.stamina / player.max_stamina))
        pygame.draw.rect(screen, ORANGE, (20, 95, stamina_width, 10))
        screen.blit(font.render("體力 (Q鍵)", True, WHITE), (180, 87)) 
        
        pygame.draw.rect(screen, GRAY, (20, 120, 150, 10))
        energy_width = int(150 * (player.energy / player.max_energy))
        pygame.draw.rect(screen, CYAN, (20, 120, energy_width, 10))
        screen.blit(font.render("能量", True, WHITE), (180, 112))

        # 困難模式彈藥 UI
        if game_mode == CHALLENGE_MODE:
            screen.blit(small_font.render("困難模式", True, RED), (20, 142))
            if player.current_weapon_type() == "pistol": r_c = YELLOW 
            else: r_c = WHITE
                
            if player.current_weapon_type() == "sniper": s_c = YELLOW 
            else: s_c = WHITE
                
            screen.blit(small_font.render("一般彈藥: " + str(player.pistol_ammo) + "/" + str(player.pistol_mag_size), True, r_c), (20, 170))
            screen.blit(small_font.render("高階彈藥: " + str(player.sniper_ammo) + "/" + str(player.sniper_mag_size), True, s_c), (20, 196))
            
            if player.reload_timer > 0:
                pygame.draw.rect(screen, GRAY, (20, 224, 170, 10))
                reload_width = int(170 * (1 - player.reload_timer / player.reload_duration))
                pygame.draw.rect(screen, YELLOW, (20, 224, reload_width, 10))
                if player.reloading_weapon == "sniper": reload_name = "高階" 
                else: reload_name = "一般"
                screen.blit(small_font.render(reload_name + "換彈中", True, YELLOW), (200, 212))

        wep_name = player.weapons[player.current_weapon_idx].name
        if game_mode == CHALLENGE_MODE: wep_y = 250
        else: wep_y = 145
        screen.blit(font.render("武器: " + wep_name + " (E 鍵切換)", True, WHITE), (20, wep_y))
        wep_icon = images.get("icon_" + wep_name)
        if wep_icon != None: 
            screen.blit(wep_icon, (20, wep_y + 30))

        if player.skill_cd > 0: 
            cd_time = round(player.skill_cd / 60, 1)
            skill_txt = font.render("大絕冷卻: " + str(cd_time) + " 秒", True, GRAY)
        elif player.energy < player.skill_cost: 
            skill_txt = font.render("大絕: 能量不足", True, RED)
        else: 
            skill_txt = font.render("大絕準備就緒 (右鍵)", True, GREEN)
        screen.blit(skill_txt, (WIDTH - 280, HEIGHT - 40))
        
        if player.god_mode == True: 
            god_text = font.render("【無敵模式啟用】", True, YELLOW)
            screen.blit(god_text, (int(WIDTH/2) - int(god_text.get_width()/2), 20))

        # Boss 血條 UI
        if boss_active == True:
            bar_w = WIDTH - 100
            if bar_w > 800: bar_w = 800
            bar_x = int(WIDTH/2) - int(bar_w/2)
            pygame.draw.rect(screen, GRAY, (bar_x, HEIGHT - 80, bar_w, 20))
            
            if boss.b_type == "RED" or boss.b_type == "CHARGER": boss_bar_color = RED
            elif boss.b_type == "PURPLE": boss_bar_color = PURPLE
            else: boss_bar_color = YELLOW
                
            boss_draw_hp = boss.hp
            if boss_draw_hp < 0: boss_draw_hp = 0
            boss_hp_width = int(bar_w * (boss_draw_hp / boss.max_hp))
            pygame.draw.rect(screen, boss_bar_color, (bar_x, HEIGHT - 80, boss_hp_width, 20))
            
            if boss_warning_timer > 0 and boss.state != "ENTRANCE": 
                w_txt = font.render("⚠️ 警告：偵測到極度危險異常實體 - 【" + boss.name + "】", True, RED)
                screen.blit(w_txt, (int(WIDTH/2) - int(w_txt.get_width()/2), HEIGHT - 110))
            elif boss.state != "ENTRANCE":
                msg, clr = boss.get_state_message()
                boss_txt = font.render("Lv." + str(boss.spawn_level) + " 【" + boss.name + "】: " + msg, True, clr)
                screen.blit(boss_txt, (int(WIDTH/2) - int(boss_txt.get_width()/2), HEIGHT - 110))

        # === 狀態選單繪製區塊 ===
        if game_state == "LEVEL_UP":
            screen.blit(dim_surface, (0, 0)) 
            title = large_font.render("升級！選擇強化後按確認", True, YELLOW)
            screen.blit(title, (int(WIDTH/2) - int(title.get_width()/2), 100))
            
            for i in range(len(cards)):
                if i >= len(current_upgrade_choices): continue
                card = cards[i]
                upgrade = upgrade_options[current_upgrade_choices[i]]
                is_selected = False
                if selected_upgrade_position == i: is_selected = True
                    
                type_key = upgrade.get("type", "none")
                if type_key in CARD_TYPE_COLORS: base_color = CARD_TYPE_COLORS[type_key]
                else: base_color = CARD_COLOR
                    
                hover_color = (min(255, base_color[0] + 35), min(255, base_color[1] + 35), min(255, base_color[2] + 35))
                color = base_color
                if is_selected == True:
                    color = (min(255, base_color[0] + 65), min(255, base_color[1] + 65), min(255, base_color[2] + 65))
                elif card.collidepoint(pygame.mouse.get_pos()) == True:
                    color = hover_color
                
                pygame.draw.rect(screen, color, card, border_radius=10)
                if is_selected == True: border_color = YELLOW; border_width = 6
                else: border_color = WHITE; border_width = 3
                pygame.draw.rect(screen, border_color, card, border_width, border_radius=10) 
                
                if type_key in CARD_TYPE_LABELS:
                    type_label = CARD_TYPE_LABELS[type_key]
                    label_bg = pygame.Rect(card.centerx - 42, card.y + 18, 84, 28)
                    pygame.draw.rect(screen, (20, 20, 28), label_bg, border_radius=8)
                    pygame.draw.rect(screen, WHITE, label_bg, 1, border_radius=8)
                    label_txt = small_font.render(type_label, True, WHITE)
                    screen.blit(label_txt, (label_bg.centerx - int(label_txt.get_width()/2), label_bg.centery - int(label_txt.get_height()/2)))
                
                opt_title = font.render(upgrade["title"], True, WHITE)
                screen.blit(opt_title, (card.centerx - int(opt_title.get_width()/2), card.y + 65))
                
                desc1 = font.render(upgrade["desc"][0], True, YELLOW)
                desc2 = font.render(upgrade["desc"][1], True, YELLOW)
                screen.blit(desc1, (card.centerx - int(desc1.get_width()/2), card.y + 125))
                screen.blit(desc2, (card.centerx - int(desc2.get_width()/2), card.y + 165))
            
            confirm_ready = False
            if selected_upgrade_position != None: confirm_ready = True
                
            if confirm_ready == True and confirm_upgrade_button.collidepoint(pygame.mouse.get_pos()): confirm_color = GREEN 
            elif confirm_ready == True: confirm_color = (50, 150, 50)
            else: confirm_color = GRAY
                
            pygame.draw.rect(screen, confirm_color, confirm_upgrade_button, border_radius=10)
            pygame.draw.rect(screen, WHITE, confirm_upgrade_button, 3, border_radius=10)
            c_txt = font.render("確認選擇", True, WHITE)
            screen.blit(c_txt, (confirm_upgrade_button.centerx - int(c_txt.get_width()/2), confirm_upgrade_button.centery - int(c_txt.get_height()/2)))

        elif game_state == "PAUSED":
            screen.blit(dim_surface, (0, 0))
            p_title = large_font.render("暫停中", True, YELLOW)
            screen.blit(p_title, (int(WIDTH/2) - int(p_title.get_width()/2), int(HEIGHT/2) - 200))
            
            btn_data =[
                (pygame.Rect(int(WIDTH/2) - 240, int(HEIGHT/2) + 70, 220, 60), "繼續遊戲", BLUE),
                (pygame.Rect(int(WIDTH/2) + 20, int(HEIGHT/2) + 70, 220, 60), "回到選單", BLUE),
                (pygame.Rect(int(WIDTH/2) - 240, int(HEIGHT/2) + 150, 220, 60), "重新開始", GREEN),
                (pygame.Rect(int(WIDTH/2) + 20, int(HEIGHT/2) + 150, 220, 60), "退出遊戲", RED)
            ]
            for i in range(len(btn_data)):
                btn_rect = btn_data[i][0]
                txt_str = btn_data[i][1]
                clr = btn_data[i][2]
                
                if btn_rect.collidepoint(pygame.mouse.get_pos()) == True: draw_clr = clr
                else: draw_clr = (int(clr[0]/2), int(clr[1]/2), int(clr[2]/2))
                    
                pygame.draw.rect(screen, draw_clr, btn_rect, border_radius=10)
                pygame.draw.rect(screen, WHITE, btn_rect, 3, border_radius=10)
                t_surf = font.render(txt_str, True, WHITE)
                screen.blit(t_surf, (btn_rect.centerx - int(t_surf.get_width()/2), btn_rect.centery - int(t_surf.get_height()/2)))
            
            draw_pause_upgrade_log(screen)

        elif game_state == "GAME_OVER":
            screen.blit(dim_surface, (0, 0))
            game_over_txt = large_font.render("Game Over", True, RED)
            screen.blit(game_over_txt, (int(WIDTH/2) - int(game_over_txt.get_width()/2), int(HEIGHT/2) - 150))
            
            btn_data = [(restart_button, "重新開始", GREEN), (menu_button, "回到選單", BLUE)]
            for i in range(len(btn_data)):
                btn_rect = btn_data[i][0]
                txt_str = btn_data[i][1]
                clr = btn_data[i][2]
                
                if btn_rect.collidepoint(pygame.mouse.get_pos()) == True: draw_clr = clr
                else: draw_clr = (int(clr[0]/2), int(clr[1]/2), int(clr[2]/2))
                    
                pygame.draw.rect(screen, draw_clr, btn_rect, border_radius=10)
                pygame.draw.rect(screen, WHITE, btn_rect, 3, border_radius=10)
                t_surf = font.render(txt_str, True, WHITE)
                screen.blit(t_surf, (btn_rect.centerx - int(t_surf.get_width()/2), btn_rect.centery - int(t_surf.get_height()/2)))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()