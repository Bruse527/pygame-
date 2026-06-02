<<<<<<< HEAD
"""
程式基礎與 Pygame 模組 
Import - 匯入 (模組或套件)
Init (Initialize) - 初始化
Display - 顯示器 / 畫面
Screen - 螢幕 / 遊戲主視窗
Surface - 表面 / 畫布圖層
Clock - 時鐘 (控制遊戲幀數)
Tick - 滴答 (推進遊戲幀數)
FPS (Frames Per Second) - 每秒影格數 (幀數)
Event - 事件 (按鍵、滑鼠點擊、視窗縮放)
Quit - 退出 / 離開
Get Pressed - 獲取按鍵/滑鼠當下狀態
Keydown / Mousebuttondown - 按下鍵盤 / 按下滑鼠
Rect (Rectangle) - 矩形 / 碰撞邊界框
Vector (Vector2) - 向量 (處理二維座標)
Fullscreen - 全螢幕模式
Resizable - 可調整視窗大小模式
SRCALPHA - 支援透明度的影像格式
數學與運算 
Math - 數學模組
Random - 隨機模組
Distance To - 計算兩點之間的距離
Normalize - 正規化 (將向量長度縮放為 1)
Cos (Cosine) - 餘弦函數
Sin (Sine) - 正弦函數
Atan2 (Arctangent 2) - 反正切函數 (常用來計算兩點間的角度)
Radians - 弧度 (角度單位)
Tangent - 切線 (遊戲中用來讓 Boss 繞圈移動)
遊戲狀態與介面 
Game State - 遊戲狀態
Playing - 遊戲進行中
Level Up - 升級選單狀態
Game Over - 遊戲結束狀態
UI (User Interface) - 使用者介面
Font / SysFont - 字體 / 系統字體
Title - 標題
Desc (Description) - 敘述 / 說明文字
Card - 卡牌 (升級選項面板)
Upgrade - 升級 / 強化
Blit - 繪製疊加 (將文字或圖片貼到畫布上)
Flip - 翻轉 / 更新整個顯示畫面
玩家屬性與數值 
Player - 玩家
Pos (Position) - 座標位置
Base Speed - 基礎移動速度
HP (Health Point) - 生命值 / 血量
Max HP - 最大生命值
Shield - 護盾
Stamina - 體力
Stamina Regen (Regeneration) - 體力恢復速度
Energy - 能量
Exp (Experience) - 經驗值
Level - 等級
Invincible Timer - 無敵計時器 (受傷後的閃爍時間)
God Mode - 無敵模式
Cheat Code - 秘技 / 作弊碼
Key Buffer - 按鍵緩衝區 (用來記錄秘技輸入)
Magnet Radius - 磁鐵吸收半徑
動作與機制 (Actions & Mechanics)
Update - 更新 (處理遊戲邏輯、移動、碰撞)
Draw - 繪製 (將物件畫到畫面上)
Dash - 衝刺 / 突進
Dash Cost - 衝刺消耗 (體力)
Aim - 瞄準
Shoot / Fire - 射擊 / 開火
Skill CD (Cooldown) - 技能冷卻時間
Collide / Colliderect - 碰撞 / 矩形碰撞偵測
Collidepoint - 點碰撞偵測 (偵測滑鼠是否點擊卡牌)
Explode - 爆炸
武器與攻擊類型 
Weapon - 武器
Shoot Delay - 射擊延遲 (控制射速)
Damage - 傷害值
Lifespan - 子彈存活時間
Pistol / Normal - 手槍 / 普通子彈
Sniper Rifle / Piercing - 狙擊槍 / 貫穿、穿透屬性
Shotgun - 散彈槍
Machine Gun - 機槍
Flamethrower - 火焰噴射器
Laser - 雷射槍
Cannon - 電磁炮 / 加農砲
Frost - 冰霜發射器 / 緩速屬性
Flame Grenade - 火焰榴彈發射器
Plasma - 電漿發射器
Knockback - 擊退效果 (在 cannon 機制中)
敵人與掉落物 (Enemies & Drops)
Enemy - 敵人 / 普通怪物
Elite - 菁英怪
Boss - 首領 / 魔王
Defeated - 被擊敗的
Spawn - 生成 / 產生怪物
Drop Item - 掉落物
Gem - 寶石 (經驗值)
Evade - 閃躲 / 迴避狀態
Charge - 蓄力 / 破綻狀態
Chase - 追擊狀態
Warn - 警告狀態 (紅線瞄準)
Flee - 逃離狀態
Summon - 召喚狀態
視覺與特效 
Particle - 粒子特效 (打擊火花、爆炸血塊)
Dash Trail - 衝刺殘影
Radius - 半徑
Thickness - 粗細 / 厚度 (繪製線條用)
Shrink - 縮小 / 收縮 (Boss 蓄力紅圈)
Expand - 擴張 (Boss 召喚紫圈)
Glow - 發光 (菁英怪的脈衝特效)
Alpha - 透明度
Polygon - 多邊形 (用來畫經驗寶石)
音效與音樂 (Audio & Music)
Mixer - 混音器模組
Sound - 短促音效 (槍聲、受傷聲)
Music / BGM - 長篇背景音樂
Load - 載入 (檔案)
Volume - 音量
Play / Stop - 播放 / 停止
Loop - 循環播放
"""


import pygame
import random
import math
import os

# 初始化遊戲跟音效
pygame.init()
pygame.mixer.init()

# 設定視窗
WIDTH = 800
HEIGHT = 600
fullscreen_mode = False
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("射擊遊戲")
clock = pygame.time.Clock()
FPS = 60

# 宣告一堆顏色變數
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
SHIELD_COLOR = (150, 200, 255) 
CARD_COLOR = (30, 30, 40)

# 字體設定
CHINESE_FONTS = "microsoftjhenghei,pingfangtc,stheiti,simhei"
font = pygame.font.SysFont(CHINESE_FONTS, 28)
large_font = pygame.font.SysFont(CHINESE_FONTS, 48)

# --- 音效與音樂系統 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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

# 槍枝的音效
load_sound("shoot_normal", "shoot_normal.wav")     # 普通槍聲
load_sound("shoot_laser", "shoot_laser.wav")       # 雷射/電漿聲
load_sound("shoot_shotgun", "shoot_shotgun.wav")   # 散彈槍聲
load_sound("shoot_cannon", "shoot_cannon.wav")     # 電磁炮/榴彈重低音
load_sound("shoot_flame", "shoot_flame.wav")       # 火焰噴射/冰霜聲

# 背景音樂 (BGM) 載入設定
bgm_path = os.path.join(BASE_DIR, "bgm.mp3") # 背景音樂支援 mp3 或 wav
try:
    pygame.mixer.music.load(bgm_path)
    pygame.mixer.music.set_volume(0.2) # BGM 音量小一點不要蓋過槍聲
except:
    print("找不到 bgm.mp3，遊戲將在無常規背景音樂下進行")

def play_sound(name, loop=0):
    if name in sounds:
        if sounds[name] != None:
            sounds[name].play(loops=loop)

def stop_sound(name):
    if name in sounds:
        if sounds[name] != None:
            sounds[name].stop()

# 秘技：上上下下左右左右BABA (無敵模式)
CHEAT_CODE =[
    pygame.K_UP, pygame.K_UP, 
    pygame.K_DOWN, pygame.K_DOWN, 
    pygame.K_LEFT, pygame.K_RIGHT, 
    pygame.K_LEFT, pygame.K_RIGHT, 
    pygame.K_b, pygame.K_a,
    pygame.K_b, pygame.K_a
]
key_buffer =[] 

# 【更新】武器的類別 (加入 sound_name 屬性)
class Weapon:
    def __init__(self, name, shoot_delay, bullet_type, damage, sound_name="shoot_normal"):
        self.name = name
        self.shoot_delay = shoot_delay
        self.bullet_type = bullet_type
        self.damage = damage
        self.sound_name = sound_name #紀錄這把槍專屬的聲音

# 所有的武器射速和傷害資料 (有人要改的話記得綁定不同音效)
WEAPON_TYPES = {}
WEAPON_TYPES["手槍"] = Weapon("手槍", 20, "normal", 20, "shoot_normal")
WEAPON_TYPES["狙擊槍"] = Weapon("狙擊槍", 50, "piercing", 45, "shoot_cannon") # 狙擊跟電磁炮以及步槍等槍枝暫時共用音效
WEAPON_TYPES["散彈槍"] = Weapon("散彈槍", 30, "shotgun", 20, "shoot_shotgun")
WEAPON_TYPES["機槍"] = Weapon("機槍", 15, "piercing", 20, "shoot_normal")
WEAPON_TYPES["火焰噴射器"] = Weapon("火焰噴射器", 3, "flamethrower", 4, "shoot_flame")
WEAPON_TYPES["雷射槍"] = Weapon("雷射槍", 25, "laser", 25, "shoot_laser")
WEAPON_TYPES["電磁炮"] = Weapon("電磁炮", 60, "cannon", 50, "shoot_cannon")
WEAPON_TYPES["冰霜發射器"] = Weapon("冰霜發射器", 5, "frost", 6, "shoot_flame")
WEAPON_TYPES["重型機槍"] = Weapon("重型機槍", 17, "piercing", 25, "shoot_shotgun")
WEAPON_TYPES["步槍"] = Weapon("步槍", 40, "piercing", 30, "shoot_cannon")
WEAPON_TYPES["火焰榴彈發射器"] = Weapon("火焰榴彈發射器", 65, "flame_grenade", 70, "shoot_cannon")
WEAPON_TYPES["電漿發射器"] = Weapon("電漿發射器", 30, "plasma", 30, "shoot_laser")

# 玩家類別
class Player:
    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        self.size = 40
        self.base_speed = 5
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        
        self.weapons =[]
        for key in WEAPON_TYPES:
            self.weapons.append(WEAPON_TYPES[key])
        self.current_weapon_idx = 0
        
        self.exp = 0
        self.level = 1
        self.max_exp = 100
        self.magnet_radius = 60
        
        self.max_hp = 100
        self.hp = 100
        self.max_shield = 100 
        self.shield = 0       
        self.invincible_timer = 0  
        
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

    def update(self):
        keys = pygame.key.get_pressed()
        move_x = 0
        move_y = 0
        if keys[pygame.K_w]: move_y = move_y - 1
        if keys[pygame.K_s]: move_y = move_y + 1
        if keys[pygame.K_a]: move_x = move_x - 1
        if keys[pygame.K_d]: move_x = move_x + 1
            
        dist = math.sqrt(move_x * move_x + move_y * move_y)
        if dist > 0:
            move_x = move_x / dist
            move_y = move_y / dist

        if self.invincible_timer > 0: 
            self.invincible_timer = self.invincible_timer - 1
        if self.skill_cd > 0: 
            self.skill_cd = self.skill_cd - 1
            
        if self.is_dashing == False:
            if self.stamina < self.max_stamina:
                self.stamina = self.stamina + self.stamina_regen
                if self.stamina > self.max_stamina:
                    self.stamina = self.max_stamina
                    
        if self.energy < self.max_energy:
            self.energy = self.energy + self.energy_regen
            if self.energy > self.max_energy:
                self.energy = self.max_energy

        if keys[pygame.K_q]:
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

        if self.is_dashing == True:
            self.x = self.x + self.dash_dir_x * self.dash_speed
            self.y = self.y + self.dash_dir_y * self.dash_speed
            self.dash_timer = self.dash_timer - 1
            if self.dash_timer <= 0: 
                self.is_dashing = False
        else:
            self.x = self.x + move_x * self.base_speed
            self.y = self.y + move_y * self.base_speed
            
        if self.x < 0: self.x = 0
        if self.x > WIDTH: self.x = WIDTH
        if self.y < 0: self.y = 0
        if self.y > HEIGHT: self.y = HEIGHT
            
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        draw_player = True
        if self.invincible_timer > 0 and self.god_mode == False:
            if int(self.invincible_timer / 4) % 2 == 0:
                draw_player = False
                
        if draw_player == True:
            if self.god_mode == True: player_color = YELLOW
            else: player_color = BLUE
                
            pygame.draw.rect(surface, player_color, self.rect)
            if self.stamina < self.dash_cost: 
                pygame.draw.rect(surface, GRAY, self.rect, 3)

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
        if self.life > 0:
            if self.size > 0:
                rect = pygame.Rect(0, 0, self.size, self.size)
                rect.center = (int(self.x), int(self.y))
                alpha = int(self.life / 3)
                if alpha < 1: alpha = 1
                pygame.draw.rect(surface, BLUE, rect, alpha)

class Bullet:
    def __init__(self, x, y, target_x, target_y, weapon):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.b_type = weapon.bullet_type
        self.damage = weapon.damage
        
        self.is_piercing = False
        if self.b_type == "piercing" or self.b_type == "laser" or self.b_type == "cannon" or self.b_type == "flamethrower":
            self.is_piercing = True
            
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
        self.lifespan = self.lifespan - 1
        if self.b_type == "flame_grenade":
            dist = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
            if dist < self.speed:
                self.explode = True
                self.lifespan = 0
                return 

        if self.b_type == "plasma":
            if self.x <= 0 or self.x >= WIDTH: self.dir_x = self.dir_x * -1
            if self.y <= 0 or self.y >= HEIGHT: self.dir_y = self.dir_y * -1

        self.x = self.x + self.dir_x * self.speed
        self.y = self.y + self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        if self.b_type == "laser":
            end_x = self.x - (self.dir_x * 30)
            end_y = self.y - (self.dir_y * 30)
            pygame.draw.line(surface, self.color, (self.x, self.y), (end_x, end_y), self.radius*2)
        else:
            pygame.draw.circle(surface, self.color, self.rect.center, self.radius)

class EnemyBullet:
    def __init__(self, x, y, dir_x, dir_y):
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        dist = math.sqrt(self.dir_x * self.dir_x + self.dir_y * self.dir_y)
        if dist > 0:
            self.dir_x = self.dir_x / dist
            self.dir_y = self.dir_y / dist
            
        self.radius = 8
        self.speed = 7
        self.color = ORANGE
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        
    def update(self):
        self.x = self.x + self.dir_x * self.speed
        self.y = self.y + self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface): 
        pygame.draw.circle(surface, self.color, self.rect.center, self.radius)

class Enemy:
    def __init__(self, level, is_elite=False):
        self.is_elite = is_elite
        if is_elite == True: self.size = 35
        else: self.size = 25
            
        if is_elite == True: self.speed = random.uniform(2.0, 4.0)
        else: self.speed = random.uniform(1.5, 3.5)
            
        if is_elite == True: self.max_hp = 30 + level * 15
        else: self.max_hp = 10 + level * 5
            
        self.hp = self.max_hp
        if is_elite == True: self.damage = 35
        else: self.damage = 15
            
        self.frost_timer = 0 
        
        edge_list =['top', 'bottom', 'left', 'right']
        edge = random.choice(edge_list)
        if edge == 'top': 
            self.x = random.randint(0, WIDTH)
            self.y = -self.size
        elif edge == 'bottom': 
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + self.size
        elif edge == 'left': 
            self.x = -self.size
            self.y = random.randint(0, HEIGHT)
        elif edge == 'right': 
            self.x = WIDTH + self.size
            self.y = random.randint(0, HEIGHT)
            
        self.rect = pygame.Rect(0, 0, self.size, self.size)

    def update(self, target_x, target_y):
        current_speed = self.speed
        if self.frost_timer > 0:
            self.frost_timer = self.frost_timer - 1
            current_speed = self.speed * 0.4 

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            dir_x = dx / dist
            dir_y = dy / dist
            self.x = self.x + dir_x * current_speed
            self.y = self.y + dir_y * current_speed
            
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        color = RED
        if self.is_elite == True:
            glow = math.sin(pygame.time.get_ticks() * 0.01) * 6 + 6
            glow_rect = self.rect.copy()
            glow_rect.inflate_ip(glow, glow)
            pygame.draw.rect(surface, DARK_PURPLE, glow_rect, 3) 
            color = (150, 0, 150) 
            
        if self.frost_timer > 0: color = (100, 200, 255)
        pygame.draw.rect(surface, color, self.rect)
        
        if self.hp < self.max_hp:
            pygame.draw.rect(surface, GRAY, (self.rect.x, self.rect.y - 8, self.size, 4))
            pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 8, self.size * (self.hp/self.max_hp), 4))

class Boss:
    def __init__(self, boss_type):
        self.b_type = boss_type
        self.x = WIDTH / 2
        self.y = -60
        self.size = 65
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.state_timer = 0
        self.frost_timer = 0
        self.play_shoot_sound = False 
        
        if self.b_type == "YELLOW":
            self.max_hp = 1000
            self.color = YELLOW
            self.speed = 1.5
            self.state = "EVADE" 
        elif self.b_type == "RED":
            self.max_hp = 900
            self.color = RED
            self.speed = 3.0
            self.state = "CHASE"
            self.aim_x = 0
            self.aim_y = 0
        elif self.b_type == "PURPLE":
            self.max_hp = 800
            self.color = PURPLE
            self.speed = 2.0
            self.state = "FLEE"
            
        self.hp = self.max_hp

    def update(self, player_x, player_y, bullets, enemies, enemy_bullets):
        self.state_timer = self.state_timer + 1
        if self.frost_timer > 0: current_speed = self.speed * 0.5
        else: current_speed = self.speed
            
        if self.frost_timer > 0: self.frost_timer = self.frost_timer - 1
        self.play_shoot_sound = False

        if self.b_type == "YELLOW":
            if self.state == "EVADE":
                dx = player_x - self.x
                dy = player_y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                dir_x, dir_y = 0, 0
                if dist > 0: dir_x, dir_y = dx / dist, dy / dist
                tangent_x, tangent_y = -dir_y, dir_x 
                
                dodged = False
                for i in range(len(bullets)):
                    b = bullets[i]
                    b_dist = math.sqrt((self.x - b.x)**2 + (self.y - b.y)**2)
                    if b_dist < 150:
                        flee_dx = self.x - b.x
                        flee_dy = self.y - b.y
                        flee_dist = math.sqrt(flee_dx*flee_dx + flee_dy*flee_dy)
                        if flee_dist > 0:
                            flee_dir_x, flee_dir_y = flee_dx / flee_dist, flee_dy / flee_dist
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
                    for i in range(12):
                        angle = math.radians(i * 30)
                        eb = EnemyBullet(self.rect.centerx, self.rect.centery, math.cos(angle), math.sin(angle))
                        enemy_bullets.append(eb)
                    self.state = "EVADE"
                    self.state_timer = 0
                    self.play_shoot_sound = True

        elif self.b_type == "RED":
            if self.state == "CHASE":
                dx = player_x - self.x
                dy = player_y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    dir_x, dir_y = dx / dist, dy / dist
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
                    self.dash_dir_x, self.dash_dir_y = 0, 0
                    if dash_dist > 0: 
                        self.dash_dir_x, self.dash_dir_y = dash_dx / dash_dist, dash_dy / dash_dist
                    self.play_shoot_sound = True 
            elif self.state == "DASH":
                self.x = self.x + self.dash_dir_x * (current_speed * 6) 
                self.y = self.y + self.dash_dir_y * (current_speed * 6)
                if self.state_timer > 20:
                    self.state = "CHASE"
                    self.state_timer = 0

        elif self.b_type == "PURPLE":
            if self.state == "FLEE":
                dist = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)
                dx = player_x - self.x
                dy = player_y - self.y
                dir_x, dir_y = 0, 0
                if dist > 0: dir_x, dir_y = dx / dist, dy / dist
                    
                if dist < 300: 
                    self.x = self.x - dir_x * current_speed 
                    self.y = self.y - dir_y * current_speed
                else:
                    tangent_x, tangent_y = -dir_y, dir_x
                    self.x = self.x + tangent_x * current_speed 
                    self.y = self.y + tangent_y * current_speed
                
                if self.state_timer > 180:
                    self.state = "SUMMON"
                    self.state_timer = 0
            elif self.state == "SUMMON":
                if self.state_timer == 45:
                    for _ in range(3):
                        e = Enemy(level=5, is_elite=True)
                        e.x = self.x + random.randint(-70,70)
                        e.y = self.y + random.randint(-70,70)
                        enemies.append(e)
                    self.play_shoot_sound = True
                if self.state_timer > 90:
                    self.state = "FLEE"
                    self.state_timer = 0

        if self.x < self.size: self.x = self.size
        if self.x > WIDTH - self.size: self.x = WIDTH - self.size
        if self.y < self.size: self.y = self.size
        if self.y > HEIGHT - self.size: self.y = HEIGHT - self.size
            
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        if self.frost_timer > 0: color = (100, 200, 255)
        else: color = self.color
            
        pygame.draw.rect(surface, color, self.rect)
        
        if self.b_type == "YELLOW":
            if self.state == "EVADE":
                pygame.draw.circle(surface, WHITE, self.rect.center, int(self.size/2) + 15, 3)
            elif self.state == "CHARGE":
                shrink = 30 - int(self.state_timer / 2)
                if shrink < 0: shrink = 0
                pygame.draw.circle(surface, RED, self.rect.center, int(self.size/2) + shrink, 2)
        elif self.b_type == "RED":
            if self.state == "WARN":
                thickness = int(self.state_timer / 8)
                if thickness < 1: thickness = 1
                pygame.draw.line(surface, RED, self.rect.center, (int(self.aim_x), int(self.aim_y)), thickness)
        elif self.b_type == "PURPLE":
            if self.state == "SUMMON":
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

class DropItem:
    def __init__(self, x, y, item_type="EXP"):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.rect = pygame.Rect(0, 0, 14, 14)
        
    def update(self, p_x, p_y, mag_rad):
        dist = math.sqrt((self.x - p_x)**2 + (self.y - p_y)**2)
        if dist < mag_rad:
            dx = p_x - self.x
            dy = p_y - self.y
            if dist > 0: 
                dir_x = dx / dist
                dir_y = dy / dist
                self.x = self.x + dir_x * 8 
                self.y = self.y + dir_y * 8 
                
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface):
        if self.item_type == "EXP":
            pts =[(self.x, self.y-6), (self.x+6, self.y), (self.x, self.y+6), (self.x-6, self.y)]
            pygame.draw.polygon(surface, BLUE, pts)
        elif self.item_type == "HP":
            pygame.draw.rect(surface, GREEN, (self.x-6, self.y-2, 12, 4))
            pygame.draw.rect(surface, GREEN, (self.x-2, self.y-6, 4, 12))
        elif self.item_type == "SHIELD":
            pygame.draw.circle(surface, SHIELD_COLOR, (int(self.x), int(self.y)), 6)

def apply_upgrade(choice):
    global game_state
    if choice == 0: 
        player.max_hp = player.max_hp + 50
        player.hp = player.hp + 50 
    elif choice == 1: 
        player.max_stamina = player.max_stamina + 50 
    elif choice == 2: 
        player.max_energy = player.max_energy + 50        
    game_state = "PLAYING"             

upgrade_options =[
    {"title": "生命躍升", "desc":["最大血量 +50", "並恢復當前血量"]},
    {"title": "體能強化", "desc":["最大體力 +50", "衝刺次數增加"]},
    {"title": "能量擴容", "desc":["最大能量 +50", "施放更多大絕招"]}
]
cards =[pygame.Rect(100, 200, 160, 240), pygame.Rect(320, 200, 160, 240), pygame.Rect(540, 200, 160, 240)]

# 重置遊戲的狀態 (有音樂處理)
def reset_game():
    global player, bullets, enemy_bullets, enemies, particles, items, trails
    global boss, boss_active, defeated_boss_levels, game_state, shoot_cooldown
    global key_buffer
    
    player = Player()
    bullets = []
    enemy_bullets = []
    enemies = []
    particles =[]
    items = [] 
    trails =[]
    boss = None
    boss_active = False
    defeated_boss_levels =[] 
    shoot_cooldown = 0
    key_buffer =[] 
    
    stop_sound("boss_bgm")
    try:
        pygame.mixer.music.play(-1) # 重新開始一般背景音樂 (-1代表無限循環)
    except:
        pass

    game_state = "PLAYING"

# 開局觸發第一次重置並播放背景音樂
reset_game()
SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY_EVENT, 600)

dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
dim_surface.fill((0, 0, 0, 180))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
        
        if event.type == pygame.VIDEORESIZE:
            if not fullscreen_mode:
                WIDTH = event.w
                HEIGHT = event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                dim_surface.fill((0, 0, 0, 180))
            
        if game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: 
                    reset_game()
        elif game_state == "LEVEL_UP":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in range(len(cards)):
                        card = cards[i]
                        mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()
                        if card.collidepoint(mouse_pos_x, mouse_pos_y) == True: 
                            apply_upgrade(i)
                            break
        elif game_state == "PLAYING":
            if event.type == SPAWN_ENEMY_EVENT: 
                rand_num = random.random()
                is_elite = False
                if rand_num < 0.15:
                    is_elite = True
                new_enemy = Enemy(player.level, is_elite)
                enemies.append(new_enemy)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen_mode = not fullscreen_mode
                    if fullscreen_mode:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                    
                    WIDTH, HEIGHT = screen.get_size()
                    dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    dim_surface.fill((0, 0, 0, 180))
                
                key_buffer.append(event.key)
                if len(key_buffer) > 12:
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

    if game_state == "PLAYING":
        check_boss_level = player.level % 4
        if check_boss_level == 0:
            if player.level > 0:
                is_defeated = False
                for lvl in defeated_boss_levels:
                    if lvl == player.level: is_defeated = True
                if is_defeated == False:
                    if boss_active == False:
                        boss_list =["YELLOW", "RED", "PURPLE"]
                        boss_type = random.choice(boss_list)
                        boss = Boss(boss_type)
                        boss_active = True
                        # 將停止普通背景音樂，改放 Boss 音樂
                        try:
                            pygame.mixer.music.stop()
                        except:
                            pass
                        play_sound("boss_bgm", loop=-1) 

        mouse_btns = pygame.mouse.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        current_wep = player.weapons[player.current_weapon_idx]

        if mouse_btns[0] == True:
            if shoot_cooldown <= 0:
                if player.is_dashing == False:
                    if current_wep.bullet_type == "shotgun":
                        for i in range(-2, 3):
                            dx = mouse_x - player.x
                            dy = mouse_y - player.y
                            angle = math.atan2(dy, dx)
                            new_angle = angle + math.radians(i * 12)
                            final_x = player.x + math.cos(new_angle) * 10
                            final_y = player.y + math.sin(new_angle) * 10
                            new_bullet = Bullet(player.rect.centerx, player.rect.centery, final_x, final_y, current_wep)
                            bullets.append(new_bullet)
                    elif current_wep.bullet_type == "flamethrower":
                        offset_x = random.randint(-40, 40)
                        offset_y = random.randint(-40, 40)
                        new_bullet = Bullet(player.rect.centerx, player.rect.centery, mouse_x + offset_x, mouse_y + offset_y, current_wep)
                        bullets.append(new_bullet)
                    else:
                        new_bullet = Bullet(player.rect.centerx, player.rect.centery, mouse_x, mouse_y, current_wep)
                        bullets.append(new_bullet)
                    
                    shoot_cooldown = current_wep.shoot_delay
                    # 【修改】根據不同武器，播放專屬音效
                    play_sound(current_wep.sound_name)
            
        if mouse_btns[2] == True:
            if player.skill_cd <= 0:
                if player.energy >= player.skill_cost:
                    if player.is_dashing == False:
                        player.energy = player.energy - player.skill_cost
                        player.skill_cd = player.skill_max_cd 
                        play_sound("shoot_cannon")  # 放絕招用重一點的音效
                        temp_wep = Weapon("大絕", 0, "piercing", 50) 
                        for i in range(16):
                            angle = math.radians(i * (360 / 16))
                            target_x = player.rect.centerx + math.cos(angle) * 100
                            target_y = player.rect.centery + math.sin(angle) * 100
                            new_bullet = Bullet(player.rect.centerx, player.rect.centery, target_x, target_y, temp_wep)
                            bullets.append(new_bullet)

        if shoot_cooldown > 0: 
            shoot_cooldown = shoot_cooldown - 1
            
        player.update()
        
        if player.is_dashing == True: 
            trails.append(DashTrail(player.rect.centerx, player.rect.centery, player.size))
            
        for i in range(len(trails) - 1, -1, -1):
            t = trails[i]
            t.update()
            if t.life <= 0: 
                trails.remove(t)
            
        for i in range(len(bullets) - 1, -1, -1):
            b = bullets[i]
            b.update()
            if b.explode == True:
                play_sound("shoot_cannon") # 爆炸也是用較重的聲音
                for _ in range(30): 
                    particles.append(Particle(b.x, b.y, ORANGE))
                for j in range(len(enemies) - 1, -1, -1):
                    e = enemies[j]
                    e_dist = math.sqrt((e.x - b.x)**2 + (e.y - b.y)**2)
                    if e_dist < 120: 
                        e.hp = e.hp - b.damage
                        if e.hp <= 0: 
                            if random.random() < 0.4: 
                                items.append(DropItem(e.x, e.y, "EXP"))
                            enemies.remove(e)
                if boss_active == True:
                    boss_dist = math.sqrt((boss.x - b.x)**2 + (boss.y - b.y)**2)
                    if boss_dist < 150: 
                        boss.hp = boss.hp - b.damage
                bullets.remove(b)
                continue
                
            if b.lifespan <= 0 or screen.get_rect().colliderect(b.rect) == False: 
                bullets.remove(b)
            
        for i in range(len(enemy_bullets) - 1, -1, -1):
            eb = enemy_bullets[i]
            eb.update()
            if screen.get_rect().colliderect(eb.rect) == False: 
                enemy_bullets.remove(eb)
            
        for i in range(len(enemies)):
            e = enemies[i]
            e.update(player.x, player.y)
            
        for i in range(len(particles) - 1, -1, -1):
            p = particles[i]
            p.update()
            if p.timer <= 0: 
                particles.remove(p)

        if boss_active == True:
            boss.update(player.x, player.y, bullets, enemies, enemy_bullets)
            if boss.play_shoot_sound == True: 
                play_sound("shoot_normal")

        # 玩家子彈撞到敵人
        for i in range(len(bullets) - 1, -1, -1):
            b = bullets[i]
            hit_something = False
            for j in range(len(enemies) - 1, -1, -1):
                e = enemies[j]
                if b.rect.colliderect(e.rect) == True:
                    if b.b_type == "frost": 
                        e.frost_timer = 120 
                    if b.b_type == "cannon": 
                        push_dx = e.x - player.x
                        push_dy = e.y - player.y
                        push_dist = math.sqrt(push_dx*push_dx + push_dy*push_dy)
                        if push_dist > 0: 
                            push_dir_x = push_dx / push_dist
                            push_dir_y = push_dy / push_dist
                            e.x = e.x + push_dir_x * 30 
                            e.y = e.y + push_dir_y * 30 
                    elif b.b_type == "flame_grenade":
                        b.explode = True 
                        break
                        
                    e.hp = e.hp - b.damage
                    hit_something = True
                    for _ in range(5): 
                        particles.append(Particle(e.x, e.y, b.color))
                    play_sound("hit")
                    
                    # 敵人死亡與掉落
                    if e.hp <= 0:
                        for _ in range(10): 
                            particles.append(Particle(e.x, e.y, RED))
                        if e.is_elite == True: 
                            items.append(DropItem(e.x-10, e.y, "EXP"))
                            items.append(DropItem(e.x+10, e.y, "EXP"))
                            if random.random() < 0.5:
                                drop_type = random.choice(["HP", "SHIELD"])
                                items.append(DropItem(e.x, e.y-15, drop_type))
                        else:
                            drop_roll = random.random()
                            if drop_roll < 0.40: 
                                items.append(DropItem(e.x, e.y, "EXP"))
                            elif drop_roll < 0.45:
                                items.append(DropItem(e.x, e.y, "HP"))
                            elif drop_roll < 0.50: 
                                items.append(DropItem(e.x, e.y, "SHIELD"))
                        enemies.remove(e)
            
            if getattr(b, 'explode', False): 
                continue 

            if boss_active == True:
                if b.rect.colliderect(boss.rect) == True:
                    hit_something = True
                    if boss.b_type == "YELLOW" and boss.state == "EVADE":
                        for _ in range(5): 
                            particles.append(Particle(boss.x, boss.y, GRAY))
                    else:
                        if b.b_type == "frost": 
                            boss.frost_timer = 60 
                        boss.hp = boss.hp - b.damage
                        for _ in range(8): 
                            particles.append(Particle(boss.x, boss.y, YELLOW))
                        play_sound("hit")
                        
                        if boss.hp <= 0:
                            boss_active = False
                            defeated_boss_levels.append(player.level) 
                            stop_sound("boss_bgm") 
                            # 【修改】打贏Boss重新播放背景音樂
                            try:
                                pygame.mixer.music.play(-1)
                            except:
                                pass
                            
                            for _ in range(40): 
                                items.append(DropItem(boss.x + random.randint(-60,60), boss.y + random.randint(-60,60), "EXP"))
                            for _ in range(5): 
                                drop_type = random.choice(["HP", "SHIELD"])
                                items.append(DropItem(boss.x + random.randint(-40,40), boss.y + random.randint(-40,40), drop_type))
                            for _ in range(50): 
                                particles.append(Particle(boss.x, boss.y, YELLOW))
                            
            if hit_something == True:
                if b.is_piercing == False:
                    is_in_list = False
                    for check_b in bullets:
                        if check_b == b:
                            is_in_list = True
                    if is_in_list == True: 
                        bullets.remove(b)

        # 玩家受傷
        def player_take_damage(dmg):
            global game_state
            if player.god_mode == True:
                return 
                
            if player.invincible_timer <= 0:
                if player.is_dashing == False:
                    if player.shield > 0:
                        if player.shield >= dmg:
                            player.shield = player.shield - dmg
                            dmg = 0
                        else:
                            dmg = dmg - player.shield
                            player.shield = 0
                            
                    if dmg > 0:
                        player.hp = player.hp - dmg
                        
                    player.invincible_timer = 60 
                    play_sound("hurt")
                    if player.hp <= 0:
                        game_state = "GAME_OVER"
                        play_sound("gameover")
                        stop_sound("boss_bgm")  
                        # 【修改】主角死亡停止音樂
                        try:
                            pygame.mixer.music.stop()
                        except:
                            pass

        for i in range(len(enemies)):
            e = enemies[i]
            if player.rect.colliderect(e.rect) == True: 
                player_take_damage(e.damage)
                
        for i in range(len(enemy_bullets) - 1, -1, -1):
            eb = enemy_bullets[i]
            if player.rect.colliderect(eb.rect) == True:
                player_take_damage(25)
                is_in_list2 = False
                for check_eb in enemy_bullets:
                    if check_eb == eb:
                        is_in_list2 = True
                if is_in_list2 == True: 
                    enemy_bullets.remove(eb)
                    
        if boss_active == True:
            if player.rect.colliderect(boss.rect) == True: 
                player_take_damage(40) 

        # 吃掉落物
        for i in range(len(items) - 1, -1, -1):
            item = items[i]
            item.update(player.x, player.y, player.magnet_radius)
            if player.rect.colliderect(item.rect) == True:
                items.remove(item)
                
                if item.item_type == "EXP":
                    player.exp = player.exp + 35 
                    play_sound("exp") 
                elif item.item_type == "HP":
                    player.hp = player.hp + 25
                    if player.hp > player.max_hp: player.hp = player.max_hp
                    play_sound("exp")
                elif item.item_type == "SHIELD":
                    player.shield = player.shield + 25
                    if player.shield > player.max_shield: player.shield = player.max_shield
                    play_sound("exp")

                if player.exp >= player.max_exp:
                    player.level = player.level + 1
                    player.exp = 0
                    player.max_exp = int(player.max_exp * 1.3) 
                    game_state = "LEVEL_UP" 
                    play_sound("levelup") 

    # 畫面繪製
    screen.fill(BLACK)
    for i in range(len(items)):
        items[i].draw(screen)
    for i in range(len(particles)):
        particles[i].draw(screen)
    for i in range(len(bullets)):
        bullets[i].draw(screen)
    for i in range(len(enemy_bullets)):
        enemy_bullets[i].draw(screen) 
    for i in range(len(enemies)):
        enemies[i].draw(screen)
    for i in range(len(trails)):
        trails[i].draw(screen)
        
    if boss_active == True: 
        boss.draw(screen) 
        
    player.draw(screen)
    
    # 畫 UI
    pygame.draw.rect(screen, GRAY, (20, 20, 250, 15))
    exp_width = 250 * (player.exp / player.max_exp)
    pygame.draw.rect(screen, BLUE, (20, 20, exp_width, 15))
    level_text = font.render("等級: " + str(player.level), True, WHITE)
    screen.blit(level_text, (280, 15))

    pygame.draw.rect(screen, GRAY, (20, 45, 200, 15))
    if player.hp > 30: hp_color = GREEN
    else: hp_color = RED
    if player.hp < 0: draw_hp = 0
    else: draw_hp = player.hp
    hp_width = 200 * (draw_hp / player.max_hp)
    pygame.draw.rect(screen, hp_color, (20, 45, hp_width, 15))
    hp_text = font.render("血量", True, WHITE)
    screen.blit(hp_text, (230, 40))

    pygame.draw.rect(screen, GRAY, (20, 70, 200, 10))
    if player.shield < 0: draw_shield = 0
    else: draw_shield = player.shield
    shield_width = 200 * (draw_shield / player.max_shield)
    pygame.draw.rect(screen, SHIELD_COLOR, (20, 70, shield_width, 10))
    shield_text = font.render("護盾", True, WHITE)
    screen.blit(shield_text, (230, 65))

    pygame.draw.rect(screen, GRAY, (20, 95, 150, 10))
    stamina_width = 150 * (player.stamina / player.max_stamina)
    pygame.draw.rect(screen, ORANGE, (20, 95, stamina_width, 10))
    stamina_text = font.render("體力 (Q鍵衝刺)", True, WHITE)
    screen.blit(stamina_text, (180, 87)) 
    
    pygame.draw.rect(screen, GRAY, (20, 120, 150, 10))
    energy_width = 150 * (player.energy / player.max_energy)
    pygame.draw.rect(screen, CYAN, (20, 120, energy_width, 10))
    energy_text = font.render("能量", True, WHITE)
    screen.blit(energy_text, (180, 112))

    wep_name = player.weapons[player.current_weapon_idx].name
    weapon_str = "武器: " + wep_name + " (E 鍵切換)"
    weapon_text = font.render(weapon_str, True, WHITE)
    screen.blit(weapon_text, (20, 145))
    
    guide_text = font.render("F11 切換全螢幕", True, GRAY)
    screen.blit(guide_text, (20, 175))

    if player.skill_cd > 0:
        cd_time = round(player.skill_cd / 60, 1)
        skill_str = "大絕冷卻: " + str(cd_time) + " 秒"
        skill_txt = font.render(skill_str, True, GRAY)
    elif player.energy < player.skill_cost:
        skill_txt = font.render("大絕: 能量不足", True, RED)
    else:
        skill_txt = font.render("大絕準備就緒 (右鍵)", True, GREEN)
        
    screen.blit(skill_txt, (WIDTH - 280, HEIGHT - 40))

    if player.god_mode == True:
        god_text = font.render("【無敵模式啟用】", True, YELLOW)
        screen.blit(god_text, (int(WIDTH/2) - int(god_text.get_width()/2), 20))

    if boss_active == True:
        bar_w = WIDTH - 100
        pygame.draw.rect(screen, GRAY, (50, HEIGHT - 80, bar_w, 20))
        if boss.b_type == "RED": boss_bar_color = RED
        elif boss.b_type == "PURPLE": boss_bar_color = PURPLE
        else: boss_bar_color = YELLOW
            
        if boss.hp < 0: boss_draw_hp = 0
        else: boss_draw_hp = boss.hp
            
        boss_hp_width = bar_w * (boss_draw_hp / boss.max_hp)
        pygame.draw.rect(screen, boss_bar_color, (50, HEIGHT - 80, boss_hp_width, 20))
        
        if boss.b_type == "YELLOW": boss_name = "守衛"
        elif boss.b_type == "RED": boss_name = "狂戰士"
        elif boss.b_type == "PURPLE": boss_name = "召喚師"
            
        boss_str = "BOSS - 【" + boss_name + "】"
        boss_txt = font.render(boss_str, True, WHITE)
        screen.blit(boss_txt, (int(WIDTH/2) - int(boss_txt.get_width()/2), HEIGHT - 110))

    if game_state == "LEVEL_UP":
        screen.blit(dim_surface, (0, 0)) 
        title = large_font.render("升級！請選擇一項強化", True, YELLOW)
        screen.blit(title, (int(WIDTH/2) - int(title.get_width()/2), 100))
        
        cards[0].x = int(WIDTH/2) - 260
        cards[1].x = int(WIDTH/2) - 80
        cards[2].x = int(WIDTH/2) + 100
        
        for i in range(len(cards)):
            card = cards[i]
            mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()
            if card.collidepoint(mouse_pos_x, mouse_pos_y) == True: color = BLUE
            else: color = CARD_COLOR
                
            pygame.draw.rect(screen, color, card, border_radius=10)
            pygame.draw.rect(screen, WHITE, card, 3, border_radius=10) 
            
            opt_title = font.render(upgrade_options[i]["title"], True, WHITE)
            screen.blit(opt_title, (card.centerx - int(opt_title.get_width()/2), card.y + 30))
            
            desc1 = font.render(upgrade_options[i]["desc"][0], True, YELLOW)
            desc2 = font.render(upgrade_options[i]["desc"][1], True, YELLOW)
            screen.blit(desc1, (card.centerx - int(desc1.get_width()/2), card.y + 110))
            screen.blit(desc2, (card.centerx - int(desc2.get_width()/2), card.y + 150))
            
    elif game_state == "GAME_OVER":
        screen.blit(dim_surface, (0, 0))
        game_over_txt = large_font.render("Game Over", True, RED)
        restart_txt = font.render("按下 'R' 鍵重新開始", True, WHITE)
        screen.blit(game_over_txt, (int(WIDTH/2) - int(game_over_txt.get_width()/2), int(HEIGHT/2) - 50))
        screen.blit(restart_txt, (int(WIDTH/2) - int(restart_txt.get_width()/2), int(HEIGHT/2) + 20))

    pygame.display.flip()
    clock.tick(FPS)

=======
"""
程式基礎與 Pygame 模組 
Import - 匯入 (模組或套件)
Init (Initialize) - 初始化
Display - 顯示器 / 畫面
Screen - 螢幕 / 遊戲主視窗
Surface - 表面 / 畫布圖層
Clock - 時鐘 (控制遊戲幀數)
Tick - 滴答 (推進遊戲幀數)
FPS (Frames Per Second) - 每秒影格數 (幀數)
Event - 事件 (按鍵、滑鼠點擊、視窗縮放)
Quit - 退出 / 離開
Get Pressed - 獲取按鍵/滑鼠當下狀態
Keydown / Mousebuttondown - 按下鍵盤 / 按下滑鼠
Rect (Rectangle) - 矩形 / 碰撞邊界框
Vector (Vector2) - 向量 (處理二維座標)
Fullscreen - 全螢幕模式
Resizable - 可調整視窗大小模式
SRCALPHA - 支援透明度的影像格式
數學與運算 
Math - 數學模組
Random - 隨機模組
Distance To - 計算兩點之間的距離
Normalize - 正規化 (將向量長度縮放為 1)
Cos (Cosine) - 餘弦函數
Sin (Sine) - 正弦函數
Atan2 (Arctangent 2) - 反正切函數 (常用來計算兩點間的角度)
Radians - 弧度 (角度單位)
Tangent - 切線 (遊戲中用來讓 Boss 繞圈移動)
遊戲狀態與介面 
Game State - 遊戲狀態
Playing - 遊戲進行中
Level Up - 升級選單狀態
Game Over - 遊戲結束狀態
UI (User Interface) - 使用者介面
Font / SysFont - 字體 / 系統字體
Title - 標題
Desc (Description) - 敘述 / 說明文字
Card - 卡牌 (升級選項面板)
Upgrade - 升級 / 強化
Blit - 繪製疊加 (將文字或圖片貼到畫布上)
Flip - 翻轉 / 更新整個顯示畫面
玩家屬性與數值 
Player - 玩家
Pos (Position) - 座標位置
Base Speed - 基礎移動速度
HP (Health Point) - 生命值 / 血量
Max HP - 最大生命值
Shield - 護盾
Stamina - 體力
Stamina Regen (Regeneration) - 體力恢復速度
Energy - 能量
Exp (Experience) - 經驗值
Level - 等級
Invincible Timer - 無敵計時器 (受傷後的閃爍時間)
God Mode - 無敵模式
Cheat Code - 秘技 / 作弊碼
Key Buffer - 按鍵緩衝區 (用來記錄秘技輸入)
Magnet Radius - 磁鐵吸收半徑
動作與機制 (Actions & Mechanics)
Update - 更新 (處理遊戲邏輯、移動、碰撞)
Draw - 繪製 (將物件畫到畫面上)
Dash - 衝刺 / 突進
Dash Cost - 衝刺消耗 (體力)
Aim - 瞄準
Shoot / Fire - 射擊 / 開火
Skill CD (Cooldown) - 技能冷卻時間
Collide / Colliderect - 碰撞 / 矩形碰撞偵測
Collidepoint - 點碰撞偵測 (偵測滑鼠是否點擊卡牌)
Explode - 爆炸
武器與攻擊類型 
Weapon - 武器
Shoot Delay - 射擊延遲 (控制射速)
Damage - 傷害值
Lifespan - 子彈存活時間
Pistol / Normal - 手槍 / 普通子彈
Sniper Rifle / Piercing - 狙擊槍 / 貫穿、穿透屬性
Shotgun - 散彈槍
Machine Gun - 機槍
Flamethrower - 火焰噴射器
Laser - 雷射槍
Cannon - 電磁炮 / 加農砲
Frost - 冰霜發射器 / 緩速屬性
Flame Grenade - 火焰榴彈發射器
Plasma - 電漿發射器
Knockback - 擊退效果 (在 cannon 機制中)
敵人與掉落物 (Enemies & Drops)
Enemy - 敵人 / 普通怪物
Elite - 菁英怪
Boss - 首領 / 魔王
Defeated - 被擊敗的
Spawn - 生成 / 產生怪物
Drop Item - 掉落物
Gem - 寶石 (經驗值)
Evade - 閃躲 / 迴避狀態
Charge - 蓄力 / 破綻狀態
Chase - 追擊狀態
Warn - 警告狀態 (紅線瞄準)
Flee - 逃離狀態
Summon - 召喚狀態
視覺與特效 
Particle - 粒子特效 (打擊火花、爆炸血塊)
Dash Trail - 衝刺殘影
Radius - 半徑
Thickness - 粗細 / 厚度 (繪製線條用)
Shrink - 縮小 / 收縮 (Boss 蓄力紅圈)
Expand - 擴張 (Boss 召喚紫圈)
Glow - 發光 (菁英怪的脈衝特效)
Alpha - 透明度
Polygon - 多邊形 (用來畫經驗寶石)
音效與音樂 (Audio & Music)
Mixer - 混音器模組
Sound - 短促音效 (槍聲、受傷聲)
Music / BGM - 長篇背景音樂
Load - 載入 (檔案)
Volume - 音量
Play / Stop - 播放 / 停止
Loop - 循環播放
"""


import pygame
import random
import math
import os

# 初始化遊戲跟音效
pygame.init()
pygame.mixer.init()

# 設定視窗
WIDTH = 800
HEIGHT = 600
fullscreen_mode = False
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("射擊遊戲")
clock = pygame.time.Clock()
FPS = 60

# 宣告一堆顏色變數
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
SHIELD_COLOR = (150, 200, 255) 
CARD_COLOR = (30, 30, 40)

# 字體設定
CHINESE_FONTS = "microsoftjhenghei,pingfangtc,stheiti,simhei"
font = pygame.font.SysFont(CHINESE_FONTS, 28)
large_font = pygame.font.SysFont(CHINESE_FONTS, 48)

# --- 音效與音樂系統 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
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

# 槍枝的音效
load_sound("shoot_normal", "shoot_normal.wav")     # 普通槍聲
load_sound("shoot_laser", "shoot_laser.wav")       # 雷射/電漿聲
load_sound("shoot_shotgun", "shoot_shotgun.wav")   # 散彈槍聲
load_sound("shoot_cannon", "shoot_cannon.wav")     # 電磁炮/榴彈重低音
load_sound("shoot_flame", "shoot_flame.wav")       # 火焰噴射/冰霜聲

# 背景音樂 (BGM) 載入設定
bgm_path = os.path.join(BASE_DIR, "bgm.mp3") # 背景音樂支援 mp3 或 wav
try:
    pygame.mixer.music.load(bgm_path)
    pygame.mixer.music.set_volume(0.2) # BGM 音量小一點不要蓋過槍聲
except:
    print("找不到 bgm.mp3，遊戲將在無常規背景音樂下進行")

def play_sound(name, loop=0):
    if name in sounds:
        if sounds[name] != None:
            sounds[name].play(loops=loop)

def stop_sound(name):
    if name in sounds:
        if sounds[name] != None:
            sounds[name].stop()

# 秘技：上上下下左右左右BABA (無敵模式)
CHEAT_CODE =[
    pygame.K_UP, pygame.K_UP, 
    pygame.K_DOWN, pygame.K_DOWN, 
    pygame.K_LEFT, pygame.K_RIGHT, 
    pygame.K_LEFT, pygame.K_RIGHT, 
    pygame.K_b, pygame.K_a,
    pygame.K_b, pygame.K_a
]
key_buffer =[] 

# 【更新】武器的類別 (加入 sound_name 屬性)
class Weapon:
    def __init__(self, name, shoot_delay, bullet_type, damage, sound_name="shoot_normal"):
        self.name = name
        self.shoot_delay = shoot_delay
        self.bullet_type = bullet_type
        self.damage = damage
        self.sound_name = sound_name #紀錄這把槍專屬的聲音

# 所有的武器射速和傷害資料 (有人要改的話記得綁定不同音效)
WEAPON_TYPES = {}
WEAPON_TYPES["手槍"] = Weapon("手槍", 20, "normal", 20, "shoot_normal")
WEAPON_TYPES["狙擊槍"] = Weapon("狙擊槍", 50, "piercing", 45, "shoot_cannon") # 狙擊跟電磁炮以及步槍等槍枝暫時共用音效
WEAPON_TYPES["散彈槍"] = Weapon("散彈槍", 30, "shotgun", 20, "shoot_shotgun")
WEAPON_TYPES["機槍"] = Weapon("機槍", 15, "piercing", 20, "shoot_normal")
WEAPON_TYPES["火焰噴射器"] = Weapon("火焰噴射器", 3, "flamethrower", 4, "shoot_flame")
WEAPON_TYPES["雷射槍"] = Weapon("雷射槍", 25, "laser", 25, "shoot_laser")
WEAPON_TYPES["電磁炮"] = Weapon("電磁炮", 60, "cannon", 50, "shoot_cannon")
WEAPON_TYPES["冰霜發射器"] = Weapon("冰霜發射器", 5, "frost", 6, "shoot_flame")
WEAPON_TYPES["重型機槍"] = Weapon("重型機槍", 17, "piercing", 25, "shoot_shotgun")
WEAPON_TYPES["步槍"] = Weapon("步槍", 40, "piercing", 30, "shoot_cannon")
WEAPON_TYPES["火焰榴彈發射器"] = Weapon("火焰榴彈發射器", 65, "flame_grenade", 70, "shoot_cannon")
WEAPON_TYPES["電漿發射器"] = Weapon("電漿發射器", 30, "plasma", 30, "shoot_laser")

# 玩家類別
class Player:
    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        self.size = 40
        self.base_speed = 5
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        
        self.weapons =[]
        for key in WEAPON_TYPES:
            self.weapons.append(WEAPON_TYPES[key])
        self.current_weapon_idx = 0
        
        self.exp = 0
        self.level = 1
        self.max_exp = 100
        self.magnet_radius = 60
        
        self.max_hp = 100
        self.hp = 100
        self.max_shield = 100 
        self.shield = 0       
        self.invincible_timer = 0  
        
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

    def update(self):
        keys = pygame.key.get_pressed()
        move_x = 0
        move_y = 0
        if keys[pygame.K_w]: move_y = move_y - 1
        if keys[pygame.K_s]: move_y = move_y + 1
        if keys[pygame.K_a]: move_x = move_x - 1
        if keys[pygame.K_d]: move_x = move_x + 1
            
        dist = math.sqrt(move_x * move_x + move_y * move_y)
        if dist > 0:
            move_x = move_x / dist
            move_y = move_y / dist

        if self.invincible_timer > 0: 
            self.invincible_timer = self.invincible_timer - 1
        if self.skill_cd > 0: 
            self.skill_cd = self.skill_cd - 1
            
        if self.is_dashing == False:
            if self.stamina < self.max_stamina:
                self.stamina = self.stamina + self.stamina_regen
                if self.stamina > self.max_stamina:
                    self.stamina = self.max_stamina
                    
        if self.energy < self.max_energy:
            self.energy = self.energy + self.energy_regen
            if self.energy > self.max_energy:
                self.energy = self.max_energy

        if keys[pygame.K_q]:
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

        if self.is_dashing == True:
            self.x = self.x + self.dash_dir_x * self.dash_speed
            self.y = self.y + self.dash_dir_y * self.dash_speed
            self.dash_timer = self.dash_timer - 1
            if self.dash_timer <= 0: 
                self.is_dashing = False
        else:
            self.x = self.x + move_x * self.base_speed
            self.y = self.y + move_y * self.base_speed
            
        if self.x < 0: self.x = 0
        if self.x > WIDTH: self.x = WIDTH
        if self.y < 0: self.y = 0
        if self.y > HEIGHT: self.y = HEIGHT
            
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        draw_player = True
        if self.invincible_timer > 0 and self.god_mode == False:
            if int(self.invincible_timer / 4) % 2 == 0:
                draw_player = False
                
        if draw_player == True:
            if self.god_mode == True: player_color = YELLOW
            else: player_color = BLUE
                
            pygame.draw.rect(surface, player_color, self.rect)
            if self.stamina < self.dash_cost: 
                pygame.draw.rect(surface, GRAY, self.rect, 3)

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
        if self.life > 0:
            if self.size > 0:
                rect = pygame.Rect(0, 0, self.size, self.size)
                rect.center = (int(self.x), int(self.y))
                alpha = int(self.life / 3)
                if alpha < 1: alpha = 1
                pygame.draw.rect(surface, BLUE, rect, alpha)

class Bullet:
    def __init__(self, x, y, target_x, target_y, weapon):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.b_type = weapon.bullet_type
        self.damage = weapon.damage
        
        self.is_piercing = False
        if self.b_type == "piercing" or self.b_type == "laser" or self.b_type == "cannon" or self.b_type == "flamethrower":
            self.is_piercing = True
            
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
        self.lifespan = self.lifespan - 1
        if self.b_type == "flame_grenade":
            dist = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
            if dist < self.speed:
                self.explode = True
                self.lifespan = 0
                return 

        if self.b_type == "plasma":
            if self.x <= 0 or self.x >= WIDTH: self.dir_x = self.dir_x * -1
            if self.y <= 0 or self.y >= HEIGHT: self.dir_y = self.dir_y * -1

        self.x = self.x + self.dir_x * self.speed
        self.y = self.y + self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        if self.b_type == "laser":
            end_x = self.x - (self.dir_x * 30)
            end_y = self.y - (self.dir_y * 30)
            pygame.draw.line(surface, self.color, (self.x, self.y), (end_x, end_y), self.radius*2)
        else:
            pygame.draw.circle(surface, self.color, self.rect.center, self.radius)

class EnemyBullet:
    def __init__(self, x, y, dir_x, dir_y):
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        dist = math.sqrt(self.dir_x * self.dir_x + self.dir_y * self.dir_y)
        if dist > 0:
            self.dir_x = self.dir_x / dist
            self.dir_y = self.dir_y / dist
            
        self.radius = 8
        self.speed = 7
        self.color = ORANGE
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        
    def update(self):
        self.x = self.x + self.dir_x * self.speed
        self.y = self.y + self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface): 
        pygame.draw.circle(surface, self.color, self.rect.center, self.radius)

class Enemy:
    def __init__(self, level, is_elite=False):
        self.is_elite = is_elite
        if is_elite == True: self.size = 35
        else: self.size = 25
            
        if is_elite == True: self.speed = random.uniform(2.0, 4.0)
        else: self.speed = random.uniform(1.5, 3.5)
            
        if is_elite == True: self.max_hp = 30 + level * 15
        else: self.max_hp = 10 + level * 5
            
        self.hp = self.max_hp
        if is_elite == True: self.damage = 35
        else: self.damage = 15
            
        self.frost_timer = 0 
        
        edge_list =['top', 'bottom', 'left', 'right']
        edge = random.choice(edge_list)
        if edge == 'top': 
            self.x = random.randint(0, WIDTH)
            self.y = -self.size
        elif edge == 'bottom': 
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + self.size
        elif edge == 'left': 
            self.x = -self.size
            self.y = random.randint(0, HEIGHT)
        elif edge == 'right': 
            self.x = WIDTH + self.size
            self.y = random.randint(0, HEIGHT)
            
        self.rect = pygame.Rect(0, 0, self.size, self.size)

    def update(self, target_x, target_y):
        current_speed = self.speed
        if self.frost_timer > 0:
            self.frost_timer = self.frost_timer - 1
            current_speed = self.speed * 0.4 

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            dir_x = dx / dist
            dir_y = dy / dist
            self.x = self.x + dir_x * current_speed
            self.y = self.y + dir_y * current_speed
            
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        color = RED
        if self.is_elite == True:
            glow = math.sin(pygame.time.get_ticks() * 0.01) * 6 + 6
            glow_rect = self.rect.copy()
            glow_rect.inflate_ip(glow, glow)
            pygame.draw.rect(surface, DARK_PURPLE, glow_rect, 3) 
            color = (150, 0, 150) 
            
        if self.frost_timer > 0: color = (100, 200, 255)
        pygame.draw.rect(surface, color, self.rect)
        
        if self.hp < self.max_hp:
            pygame.draw.rect(surface, GRAY, (self.rect.x, self.rect.y - 8, self.size, 4))
            pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 8, self.size * (self.hp/self.max_hp), 4))

class Boss:
    def __init__(self, boss_type):
        self.b_type = boss_type
        self.x = WIDTH / 2
        self.y = -60
        self.size = 65
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.state_timer = 0
        self.frost_timer = 0
        self.play_shoot_sound = False 
        
        if self.b_type == "YELLOW":
            self.max_hp = 1000
            self.color = YELLOW
            self.speed = 1.5
            self.state = "EVADE" 
        elif self.b_type == "RED":
            self.max_hp = 900
            self.color = RED
            self.speed = 3.0
            self.state = "CHASE"
            self.aim_x = 0
            self.aim_y = 0
        elif self.b_type == "PURPLE":
            self.max_hp = 800
            self.color = PURPLE
            self.speed = 2.0
            self.state = "FLEE"
            
        self.hp = self.max_hp

    def update(self, player_x, player_y, bullets, enemies, enemy_bullets):
        self.state_timer = self.state_timer + 1
        if self.frost_timer > 0: current_speed = self.speed * 0.5
        else: current_speed = self.speed
            
        if self.frost_timer > 0: self.frost_timer = self.frost_timer - 1
        self.play_shoot_sound = False

        if self.b_type == "YELLOW":
            if self.state == "EVADE":
                dx = player_x - self.x
                dy = player_y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                dir_x, dir_y = 0, 0
                if dist > 0: dir_x, dir_y = dx / dist, dy / dist
                tangent_x, tangent_y = -dir_y, dir_x 
                
                dodged = False
                for i in range(len(bullets)):
                    b = bullets[i]
                    b_dist = math.sqrt((self.x - b.x)**2 + (self.y - b.y)**2)
                    if b_dist < 150:
                        flee_dx = self.x - b.x
                        flee_dy = self.y - b.y
                        flee_dist = math.sqrt(flee_dx*flee_dx + flee_dy*flee_dy)
                        if flee_dist > 0:
                            flee_dir_x, flee_dir_y = flee_dx / flee_dist, flee_dy / flee_dist
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
                    for i in range(12):
                        angle = math.radians(i * 30)
                        eb = EnemyBullet(self.rect.centerx, self.rect.centery, math.cos(angle), math.sin(angle))
                        enemy_bullets.append(eb)
                    self.state = "EVADE"
                    self.state_timer = 0
                    self.play_shoot_sound = True

        elif self.b_type == "RED":
            if self.state == "CHASE":
                dx = player_x - self.x
                dy = player_y - self.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0:
                    dir_x, dir_y = dx / dist, dy / dist
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
                    self.dash_dir_x, self.dash_dir_y = 0, 0
                    if dash_dist > 0: 
                        self.dash_dir_x, self.dash_dir_y = dash_dx / dash_dist, dash_dy / dash_dist
                    self.play_shoot_sound = True 
            elif self.state == "DASH":
                self.x = self.x + self.dash_dir_x * (current_speed * 6) 
                self.y = self.y + self.dash_dir_y * (current_speed * 6)
                if self.state_timer > 20:
                    self.state = "CHASE"
                    self.state_timer = 0

        elif self.b_type == "PURPLE":
            if self.state == "FLEE":
                dist = math.sqrt((self.x - player_x)**2 + (self.y - player_y)**2)
                dx = player_x - self.x
                dy = player_y - self.y
                dir_x, dir_y = 0, 0
                if dist > 0: dir_x, dir_y = dx / dist, dy / dist
                    
                if dist < 300: 
                    self.x = self.x - dir_x * current_speed 
                    self.y = self.y - dir_y * current_speed
                else:
                    tangent_x, tangent_y = -dir_y, dir_x
                    self.x = self.x + tangent_x * current_speed 
                    self.y = self.y + tangent_y * current_speed
                
                if self.state_timer > 180:
                    self.state = "SUMMON"
                    self.state_timer = 0
            elif self.state == "SUMMON":
                if self.state_timer == 45:
                    for _ in range(3):
                        e = Enemy(level=5, is_elite=True)
                        e.x = self.x + random.randint(-70,70)
                        e.y = self.y + random.randint(-70,70)
                        enemies.append(e)
                    self.play_shoot_sound = True
                if self.state_timer > 90:
                    self.state = "FLEE"
                    self.state_timer = 0

        if self.x < self.size: self.x = self.size
        if self.x > WIDTH - self.size: self.x = WIDTH - self.size
        if self.y < self.size: self.y = self.size
        if self.y > HEIGHT - self.size: self.y = HEIGHT - self.size
            
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        if self.frost_timer > 0: color = (100, 200, 255)
        else: color = self.color
            
        pygame.draw.rect(surface, color, self.rect)
        
        if self.b_type == "YELLOW":
            if self.state == "EVADE":
                pygame.draw.circle(surface, WHITE, self.rect.center, int(self.size/2) + 15, 3)
            elif self.state == "CHARGE":
                shrink = 30 - int(self.state_timer / 2)
                if shrink < 0: shrink = 0
                pygame.draw.circle(surface, RED, self.rect.center, int(self.size/2) + shrink, 2)
        elif self.b_type == "RED":
            if self.state == "WARN":
                thickness = int(self.state_timer / 8)
                if thickness < 1: thickness = 1
                pygame.draw.line(surface, RED, self.rect.center, (int(self.aim_x), int(self.aim_y)), thickness)
        elif self.b_type == "PURPLE":
            if self.state == "SUMMON":
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

class DropItem:
    def __init__(self, x, y, item_type="EXP"):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.rect = pygame.Rect(0, 0, 14, 14)
        
    def update(self, p_x, p_y, mag_rad):
        dist = math.sqrt((self.x - p_x)**2 + (self.y - p_y)**2)
        if dist < mag_rad:
            dx = p_x - self.x
            dy = p_y - self.y
            if dist > 0: 
                dir_x = dx / dist
                dir_y = dy / dist
                self.x = self.x + dir_x * 8 
                self.y = self.y + dir_y * 8 
                
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface):
        if self.item_type == "EXP":
            pts =[(self.x, self.y-6), (self.x+6, self.y), (self.x, self.y+6), (self.x-6, self.y)]
            pygame.draw.polygon(surface, BLUE, pts)
        elif self.item_type == "HP":
            pygame.draw.rect(surface, GREEN, (self.x-6, self.y-2, 12, 4))
            pygame.draw.rect(surface, GREEN, (self.x-2, self.y-6, 4, 12))
        elif self.item_type == "SHIELD":
            pygame.draw.circle(surface, SHIELD_COLOR, (int(self.x), int(self.y)), 6)

def apply_upgrade(choice):
    global game_state
    if choice == 0: 
        player.max_hp = player.max_hp + 50
        player.hp = player.hp + 50 
    elif choice == 1: 
        player.max_stamina = player.max_stamina + 50 
    elif choice == 2: 
        player.max_energy = player.max_energy + 50        
    game_state = "PLAYING"             

upgrade_options =[
    {"title": "生命躍升", "desc":["最大血量 +50", "並恢復當前血量"]},
    {"title": "體能強化", "desc":["最大體力 +50", "衝刺次數增加"]},
    {"title": "能量擴容", "desc":["最大能量 +50", "施放更多大絕招"]}
]
cards =[pygame.Rect(100, 200, 160, 240), pygame.Rect(320, 200, 160, 240), pygame.Rect(540, 200, 160, 240)]

# 重置遊戲的狀態 (有音樂處理)
def reset_game():
    global player, bullets, enemy_bullets, enemies, particles, items, trails
    global boss, boss_active, defeated_boss_levels, game_state, shoot_cooldown
    global key_buffer
    
    player = Player()
    bullets = []
    enemy_bullets = []
    enemies = []
    particles =[]
    items = [] 
    trails =[]
    boss = None
    boss_active = False
    defeated_boss_levels =[] 
    shoot_cooldown = 0
    key_buffer =[] 
    
    stop_sound("boss_bgm")
    try:
        pygame.mixer.music.play(-1) # 重新開始一般背景音樂 (-1代表無限循環)
    except:
        pass

    game_state = "PLAYING"

# 開局觸發第一次重置並播放背景音樂
reset_game()
SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY_EVENT, 600)

dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
dim_surface.fill((0, 0, 0, 180))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
        
        if event.type == pygame.VIDEORESIZE:
            if not fullscreen_mode:
                WIDTH = event.w
                HEIGHT = event.h
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                dim_surface.fill((0, 0, 0, 180))
            
        if game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: 
                    reset_game()
        elif game_state == "LEVEL_UP":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in range(len(cards)):
                        card = cards[i]
                        mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()
                        if card.collidepoint(mouse_pos_x, mouse_pos_y) == True: 
                            apply_upgrade(i)
                            break
        elif game_state == "PLAYING":
            if event.type == SPAWN_ENEMY_EVENT: 
                rand_num = random.random()
                is_elite = False
                if rand_num < 0.15:
                    is_elite = True
                new_enemy = Enemy(player.level, is_elite)
                enemies.append(new_enemy)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen_mode = not fullscreen_mode
                    if fullscreen_mode:
                        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
                    
                    WIDTH, HEIGHT = screen.get_size()
                    dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    dim_surface.fill((0, 0, 0, 180))
                
                key_buffer.append(event.key)
                if len(key_buffer) > 12:
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

    if game_state == "PLAYING":
        check_boss_level = player.level % 4
        if check_boss_level == 0:
            if player.level > 0:
                is_defeated = False
                for lvl in defeated_boss_levels:
                    if lvl == player.level: is_defeated = True
                if is_defeated == False:
                    if boss_active == False:
                        boss_list =["YELLOW", "RED", "PURPLE"]
                        boss_type = random.choice(boss_list)
                        boss = Boss(boss_type)
                        boss_active = True
                        # 將停止普通背景音樂，改放 Boss 音樂
                        try:
                            pygame.mixer.music.stop()
                        except:
                            pass
                        play_sound("boss_bgm", loop=-1) 

        mouse_btns = pygame.mouse.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        current_wep = player.weapons[player.current_weapon_idx]

        if mouse_btns[0] == True:
            if shoot_cooldown <= 0:
                if player.is_dashing == False:
                    if current_wep.bullet_type == "shotgun":
                        for i in range(-2, 3):
                            dx = mouse_x - player.x
                            dy = mouse_y - player.y
                            angle = math.atan2(dy, dx)
                            new_angle = angle + math.radians(i * 12)
                            final_x = player.x + math.cos(new_angle) * 10
                            final_y = player.y + math.sin(new_angle) * 10
                            new_bullet = Bullet(player.rect.centerx, player.rect.centery, final_x, final_y, current_wep)
                            bullets.append(new_bullet)
                    elif current_wep.bullet_type == "flamethrower":
                        offset_x = random.randint(-40, 40)
                        offset_y = random.randint(-40, 40)
                        new_bullet = Bullet(player.rect.centerx, player.rect.centery, mouse_x + offset_x, mouse_y + offset_y, current_wep)
                        bullets.append(new_bullet)
                    else:
                        new_bullet = Bullet(player.rect.centerx, player.rect.centery, mouse_x, mouse_y, current_wep)
                        bullets.append(new_bullet)
                    
                    shoot_cooldown = current_wep.shoot_delay
                    # 【修改】根據不同武器，播放專屬音效
                    play_sound(current_wep.sound_name)
            
        if mouse_btns[2] == True:
            if player.skill_cd <= 0:
                if player.energy >= player.skill_cost:
                    if player.is_dashing == False:
                        player.energy = player.energy - player.skill_cost
                        player.skill_cd = player.skill_max_cd 
                        play_sound("shoot_cannon")  # 放絕招用重一點的音效
                        temp_wep = Weapon("大絕", 0, "piercing", 50) 
                        for i in range(16):
                            angle = math.radians(i * (360 / 16))
                            target_x = player.rect.centerx + math.cos(angle) * 100
                            target_y = player.rect.centery + math.sin(angle) * 100
                            new_bullet = Bullet(player.rect.centerx, player.rect.centery, target_x, target_y, temp_wep)
                            bullets.append(new_bullet)

        if shoot_cooldown > 0: 
            shoot_cooldown = shoot_cooldown - 1
            
        player.update()
        
        if player.is_dashing == True: 
            trails.append(DashTrail(player.rect.centerx, player.rect.centery, player.size))
            
        for i in range(len(trails) - 1, -1, -1):
            t = trails[i]
            t.update()
            if t.life <= 0: 
                trails.remove(t)
            
        for i in range(len(bullets) - 1, -1, -1):
            b = bullets[i]
            b.update()
            if b.explode == True:
                play_sound("shoot_cannon") # 爆炸也是用較重的聲音
                for _ in range(30): 
                    particles.append(Particle(b.x, b.y, ORANGE))
                for j in range(len(enemies) - 1, -1, -1):
                    e = enemies[j]
                    e_dist = math.sqrt((e.x - b.x)**2 + (e.y - b.y)**2)
                    if e_dist < 120: 
                        e.hp = e.hp - b.damage
                        if e.hp <= 0: 
                            if random.random() < 0.4: 
                                items.append(DropItem(e.x, e.y, "EXP"))
                            enemies.remove(e)
                if boss_active == True:
                    boss_dist = math.sqrt((boss.x - b.x)**2 + (boss.y - b.y)**2)
                    if boss_dist < 150: 
                        boss.hp = boss.hp - b.damage
                bullets.remove(b)
                continue
                
            if b.lifespan <= 0 or screen.get_rect().colliderect(b.rect) == False: 
                bullets.remove(b)
            
        for i in range(len(enemy_bullets) - 1, -1, -1):
            eb = enemy_bullets[i]
            eb.update()
            if screen.get_rect().colliderect(eb.rect) == False: 
                enemy_bullets.remove(eb)
            
        for i in range(len(enemies)):
            e = enemies[i]
            e.update(player.x, player.y)
            
        for i in range(len(particles) - 1, -1, -1):
            p = particles[i]
            p.update()
            if p.timer <= 0: 
                particles.remove(p)

        if boss_active == True:
            boss.update(player.x, player.y, bullets, enemies, enemy_bullets)
            if boss.play_shoot_sound == True: 
                play_sound("shoot_normal")

        # 玩家子彈撞到敵人
        for i in range(len(bullets) - 1, -1, -1):
            b = bullets[i]
            hit_something = False
            for j in range(len(enemies) - 1, -1, -1):
                e = enemies[j]
                if b.rect.colliderect(e.rect) == True:
                    if b.b_type == "frost": 
                        e.frost_timer = 120 
                    if b.b_type == "cannon": 
                        push_dx = e.x - player.x
                        push_dy = e.y - player.y
                        push_dist = math.sqrt(push_dx*push_dx + push_dy*push_dy)
                        if push_dist > 0: 
                            push_dir_x = push_dx / push_dist
                            push_dir_y = push_dy / push_dist
                            e.x = e.x + push_dir_x * 30 
                            e.y = e.y + push_dir_y * 30 
                    elif b.b_type == "flame_grenade":
                        b.explode = True 
                        break
                        
                    e.hp = e.hp - b.damage
                    hit_something = True
                    for _ in range(5): 
                        particles.append(Particle(e.x, e.y, b.color))
                    play_sound("hit")
                    
                    # 敵人死亡與掉落
                    if e.hp <= 0:
                        for _ in range(10): 
                            particles.append(Particle(e.x, e.y, RED))
                        if e.is_elite == True: 
                            items.append(DropItem(e.x-10, e.y, "EXP"))
                            items.append(DropItem(e.x+10, e.y, "EXP"))
                            if random.random() < 0.5:
                                drop_type = random.choice(["HP", "SHIELD"])
                                items.append(DropItem(e.x, e.y-15, drop_type))
                        else:
                            drop_roll = random.random()
                            if drop_roll < 0.40: 
                                items.append(DropItem(e.x, e.y, "EXP"))
                            elif drop_roll < 0.45:
                                items.append(DropItem(e.x, e.y, "HP"))
                            elif drop_roll < 0.50: 
                                items.append(DropItem(e.x, e.y, "SHIELD"))
                        enemies.remove(e)
            
            if getattr(b, 'explode', False): 
                continue 

            if boss_active == True:
                if b.rect.colliderect(boss.rect) == True:
                    hit_something = True
                    if boss.b_type == "YELLOW" and boss.state == "EVADE":
                        for _ in range(5): 
                            particles.append(Particle(boss.x, boss.y, GRAY))
                    else:
                        if b.b_type == "frost": 
                            boss.frost_timer = 60 
                        boss.hp = boss.hp - b.damage
                        for _ in range(8): 
                            particles.append(Particle(boss.x, boss.y, YELLOW))
                        play_sound("hit")
                        
                        if boss.hp <= 0:
                            boss_active = False
                            defeated_boss_levels.append(player.level) 
                            stop_sound("boss_bgm") 
                            # 【修改】打贏Boss重新播放背景音樂
                            try:
                                pygame.mixer.music.play(-1)
                            except:
                                pass
                            
                            for _ in range(40): 
                                items.append(DropItem(boss.x + random.randint(-60,60), boss.y + random.randint(-60,60), "EXP"))
                            for _ in range(5): 
                                drop_type = random.choice(["HP", "SHIELD"])
                                items.append(DropItem(boss.x + random.randint(-40,40), boss.y + random.randint(-40,40), drop_type))
                            for _ in range(50): 
                                particles.append(Particle(boss.x, boss.y, YELLOW))
                            
            if hit_something == True:
                if b.is_piercing == False:
                    is_in_list = False
                    for check_b in bullets:
                        if check_b == b:
                            is_in_list = True
                    if is_in_list == True: 
                        bullets.remove(b)

        # 玩家受傷
        def player_take_damage(dmg):
            global game_state
            if player.god_mode == True:
                return 
                
            if player.invincible_timer <= 0:
                if player.is_dashing == False:
                    if player.shield > 0:
                        if player.shield >= dmg:
                            player.shield = player.shield - dmg
                            dmg = 0
                        else:
                            dmg = dmg - player.shield
                            player.shield = 0
                            
                    if dmg > 0:
                        player.hp = player.hp - dmg
                        
                    player.invincible_timer = 60 
                    play_sound("hurt")
                    if player.hp <= 0:
                        game_state = "GAME_OVER"
                        play_sound("gameover")
                        stop_sound("boss_bgm")  
                        # 【修改】主角死亡停止音樂
                        try:
                            pygame.mixer.music.stop()
                        except:
                            pass

        for i in range(len(enemies)):
            e = enemies[i]
            if player.rect.colliderect(e.rect) == True: 
                player_take_damage(e.damage)
                
        for i in range(len(enemy_bullets) - 1, -1, -1):
            eb = enemy_bullets[i]
            if player.rect.colliderect(eb.rect) == True:
                player_take_damage(25)
                is_in_list2 = False
                for check_eb in enemy_bullets:
                    if check_eb == eb:
                        is_in_list2 = True
                if is_in_list2 == True: 
                    enemy_bullets.remove(eb)
                    
        if boss_active == True:
            if player.rect.colliderect(boss.rect) == True: 
                player_take_damage(40) 

        # 吃掉落物
        for i in range(len(items) - 1, -1, -1):
            item = items[i]
            item.update(player.x, player.y, player.magnet_radius)
            if player.rect.colliderect(item.rect) == True:
                items.remove(item)
                
                if item.item_type == "EXP":
                    player.exp = player.exp + 35 
                    play_sound("exp") 
                elif item.item_type == "HP":
                    player.hp = player.hp + 25
                    if player.hp > player.max_hp: player.hp = player.max_hp
                    play_sound("exp")
                elif item.item_type == "SHIELD":
                    player.shield = player.shield + 25
                    if player.shield > player.max_shield: player.shield = player.max_shield
                    play_sound("exp")

                if player.exp >= player.max_exp:
                    player.level = player.level + 1
                    player.exp = 0
                    player.max_exp = int(player.max_exp * 1.3) 
                    game_state = "LEVEL_UP" 
                    play_sound("levelup") 

    # 畫面繪製
    screen.fill(BLACK)
    for i in range(len(items)):
        items[i].draw(screen)
    for i in range(len(particles)):
        particles[i].draw(screen)
    for i in range(len(bullets)):
        bullets[i].draw(screen)
    for i in range(len(enemy_bullets)):
        enemy_bullets[i].draw(screen) 
    for i in range(len(enemies)):
        enemies[i].draw(screen)
    for i in range(len(trails)):
        trails[i].draw(screen)
        
    if boss_active == True: 
        boss.draw(screen) 
        
    player.draw(screen)
    
    # 畫 UI
    pygame.draw.rect(screen, GRAY, (20, 20, 250, 15))
    exp_width = 250 * (player.exp / player.max_exp)
    pygame.draw.rect(screen, BLUE, (20, 20, exp_width, 15))
    level_text = font.render("等級: " + str(player.level), True, WHITE)
    screen.blit(level_text, (280, 15))

    pygame.draw.rect(screen, GRAY, (20, 45, 200, 15))
    if player.hp > 30: hp_color = GREEN
    else: hp_color = RED
    if player.hp < 0: draw_hp = 0
    else: draw_hp = player.hp
    hp_width = 200 * (draw_hp / player.max_hp)
    pygame.draw.rect(screen, hp_color, (20, 45, hp_width, 15))
    hp_text = font.render("血量", True, WHITE)
    screen.blit(hp_text, (230, 40))

    pygame.draw.rect(screen, GRAY, (20, 70, 200, 10))
    if player.shield < 0: draw_shield = 0
    else: draw_shield = player.shield
    shield_width = 200 * (draw_shield / player.max_shield)
    pygame.draw.rect(screen, SHIELD_COLOR, (20, 70, shield_width, 10))
    shield_text = font.render("護盾", True, WHITE)
    screen.blit(shield_text, (230, 65))

    pygame.draw.rect(screen, GRAY, (20, 95, 150, 10))
    stamina_width = 150 * (player.stamina / player.max_stamina)
    pygame.draw.rect(screen, ORANGE, (20, 95, stamina_width, 10))
    stamina_text = font.render("體力 (Q鍵衝刺)", True, WHITE)
    screen.blit(stamina_text, (180, 87)) 
    
    pygame.draw.rect(screen, GRAY, (20, 120, 150, 10))
    energy_width = 150 * (player.energy / player.max_energy)
    pygame.draw.rect(screen, CYAN, (20, 120, energy_width, 10))
    energy_text = font.render("能量", True, WHITE)
    screen.blit(energy_text, (180, 112))

    wep_name = player.weapons[player.current_weapon_idx].name
    weapon_str = "武器: " + wep_name + " (E 鍵切換)"
    weapon_text = font.render(weapon_str, True, WHITE)
    screen.blit(weapon_text, (20, 145))
    
    guide_text = font.render("F11 切換全螢幕", True, GRAY)
    screen.blit(guide_text, (20, 175))

    if player.skill_cd > 0:
        cd_time = round(player.skill_cd / 60, 1)
        skill_str = "大絕冷卻: " + str(cd_time) + " 秒"
        skill_txt = font.render(skill_str, True, GRAY)
    elif player.energy < player.skill_cost:
        skill_txt = font.render("大絕: 能量不足", True, RED)
    else:
        skill_txt = font.render("大絕準備就緒 (右鍵)", True, GREEN)
        
    screen.blit(skill_txt, (WIDTH - 280, HEIGHT - 40))

    if player.god_mode == True:
        god_text = font.render("【無敵模式啟用】", True, YELLOW)
        screen.blit(god_text, (int(WIDTH/2) - int(god_text.get_width()/2), 20))

    if boss_active == True:
        bar_w = WIDTH - 100
        pygame.draw.rect(screen, GRAY, (50, HEIGHT - 80, bar_w, 20))
        if boss.b_type == "RED": boss_bar_color = RED
        elif boss.b_type == "PURPLE": boss_bar_color = PURPLE
        else: boss_bar_color = YELLOW
            
        if boss.hp < 0: boss_draw_hp = 0
        else: boss_draw_hp = boss.hp
            
        boss_hp_width = bar_w * (boss_draw_hp / boss.max_hp)
        pygame.draw.rect(screen, boss_bar_color, (50, HEIGHT - 80, boss_hp_width, 20))
        
        if boss.b_type == "YELLOW": boss_name = "守衛"
        elif boss.b_type == "RED": boss_name = "狂戰士"
        elif boss.b_type == "PURPLE": boss_name = "召喚師"
            
        boss_str = "BOSS - 【" + boss_name + "】"
        boss_txt = font.render(boss_str, True, WHITE)
        screen.blit(boss_txt, (int(WIDTH/2) - int(boss_txt.get_width()/2), HEIGHT - 110))

    if game_state == "LEVEL_UP":
        screen.blit(dim_surface, (0, 0)) 
        title = large_font.render("升級！請選擇一項強化", True, YELLOW)
        screen.blit(title, (int(WIDTH/2) - int(title.get_width()/2), 100))
        
        cards[0].x = int(WIDTH/2) - 260
        cards[1].x = int(WIDTH/2) - 80
        cards[2].x = int(WIDTH/2) + 100
        
        for i in range(len(cards)):
            card = cards[i]
            mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()
            if card.collidepoint(mouse_pos_x, mouse_pos_y) == True: color = BLUE
            else: color = CARD_COLOR
                
            pygame.draw.rect(screen, color, card, border_radius=10)
            pygame.draw.rect(screen, WHITE, card, 3, border_radius=10) 
            
            opt_title = font.render(upgrade_options[i]["title"], True, WHITE)
            screen.blit(opt_title, (card.centerx - int(opt_title.get_width()/2), card.y + 30))
            
            desc1 = font.render(upgrade_options[i]["desc"][0], True, YELLOW)
            desc2 = font.render(upgrade_options[i]["desc"][1], True, YELLOW)
            screen.blit(desc1, (card.centerx - int(desc1.get_width()/2), card.y + 110))
            screen.blit(desc2, (card.centerx - int(desc2.get_width()/2), card.y + 150))
            
    elif game_state == "GAME_OVER":
        screen.blit(dim_surface, (0, 0))
        game_over_txt = large_font.render("Game Over", True, RED)
        restart_txt = font.render("按下 'R' 鍵重新開始", True, WHITE)
        screen.blit(game_over_txt, (int(WIDTH/2) - int(game_over_txt.get_width()/2), int(HEIGHT/2) - 50))
        screen.blit(restart_txt, (int(WIDTH/2) - int(restart_txt.get_width()/2), int(HEIGHT/2) + 20))

    pygame.display.flip()
    clock.tick(FPS)

>>>>>>> 5fe3c3b9a6cb6e15508d0cc26521ee2ec490b8fd
pygame.quit()