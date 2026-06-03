"""
驅魔人: 撤離行動 v2.7 (塔科夫究極地堡版)
- 保留：完整 25 張卡牌、UI、四大 BOSS 完整 AI。
- 新增：武器改造台，花費廢料升級武器品質(白>藍>紫>金)與重置詞綴。
- 新增：專屬「格子收藏箱」(禁放武器) 與「自動排序武器箱」(專放武器)。
- 修正：UI 重疊問題、密技解鎖衝突、強化裝備替換與背包拖曳邏輯。
"""

import pygame
import random
import math
import os

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1024, 768
MAP_WIDTH, MAP_HEIGHT = 4200, 2600
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("驅魔人: 撤離行動 v2.7")
clock = pygame.time.Clock()
FPS = 60

camera_x, camera_y = 0, 0
screen_shake = 0  

BLACK, BLUE, RED, YELLOW = (10, 10, 15), (0, 200, 255), (255, 20, 80), (255, 255, 0)
PURPLE, DARK_PURPLE, WHITE = (200, 50, 255), (138, 43, 226), (255, 255, 255)
GRAY, GREEN, ORANGE, CYAN = (100, 100, 110), (0, 255, 100), (255, 150, 0), (0, 255, 255)
SCRAP_COLOR = (200, 200, 200)

CARD_COLOR = (30, 30, 40)
CARD_TYPE_COLORS = {"attack": (120, 35, 45), "support": (35, 75, 130), "life": (35, 110, 65)}
CARD_TYPE_LABELS = {"attack": "攻擊", "support": "支援", "life": "生命"}
SHIELD_COLOR, EXP_COLOR, HP_COLOR = (0, 150, 255), (124, 252, 0), (255, 50, 50)

CHINESE_FONTS = "microsoftjhenghei,pingfangtc,stheiti,simhei"
font = pygame.font.SysFont(CHINESE_FONTS, 24)
large_font = pygame.font.SysFont(CHINESE_FONTS, 42)
small_font = pygame.font.SysFont(CHINESE_FONTS, 18)
tiny_font = pygame.font.SysFont(CHINESE_FONTS, 14)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
if not os.path.exists(IMAGE_DIR): os.makedirs(IMAGE_DIR)

images, animations, sounds = {}, {}, {}

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
    if not os.path.exists(folder_path): os.makedirs(folder_path); animations[name] = None; return
    frames =[]
    for file in sorted(os.listdir(folder_path)):
        if file.endswith((".png", ".jpg")):
            img = pygame.image.load(os.path.join(folder_path, file)).convert_alpha()
            img = pygame.transform.scale(img, size)
            frames.append(img)
    animations[name] = frames if frames else None

def load_sound(name, filename):
    try:
        sound_path = os.path.join(BASE_DIR, filename)
        if os.path.exists(sound_path):
            sounds[name] = pygame.mixer.Sound(sound_path)
            sounds[name].set_volume(0.3)
        else: sounds[name] = None
    except: sounds[name] = None 

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
load_animation("boss_CYAN", "boss_cyan", (100, 100))

load_sound("dash", "dash.wav"); load_sound("hit", "hit.wav"); load_sound("levelup", "levelup.wav")
load_sound("hurt", "hurt.wav"); load_sound("boss_bgm", "boss.wav"); load_sound("gameover", "gameover.wav")
load_sound("exp", "exp.wav"); load_sound("shoot_normal", "shoot_normal.wav")     
load_sound("shoot_laser", "shoot_laser.wav"); load_sound("shoot_shotgun", "shoot_shotgun.wav")   
load_sound("shoot_cannon", "shoot_cannon.wav"); load_sound("shoot_flame", "shoot_flame.wav")       

def play_sound(name, loop=0):
    if sounds.get(name): sounds[name].play(loops=loop)
def stop_sound(name):
    if sounds.get(name): sounds[name].stop()

# ----------------- 塔科夫系統數據 -----------------
persistent_stats = {
    "max_hp": 0, "dmg_bonus": 0, "speed_bonus": 0.0,
    "scrap": 0, "weapon_stash": [], "general_stash": [None]*36
}

CHEAT_CODE =[pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_b, pygame.K_a, pygame.K_b, pygame.K_a]
key_buffer =[] 

# ----------------- 武器與詞綴 -----------------
class Weapon:
    def __init__(self, name, shoot_delay, bullet_type, damage, sound_name="shoot_normal"):
        self.base_name, self.shoot_delay, self.bullet_type, self.damage, self.sound_name = name, shoot_delay, bullet_type, damage, sound_name
        self.rarity = "白"
        self.affixes = []
        load_image("gun_" + name, f"gun_{name}.png", (45, 18))
        
    @property
    def full_name(self): return f"【{self.rarity}】{self.base_name}"

WEAPON_TYPES = {
    "手槍": Weapon("手槍", 20, "normal", 20, "snd_pistol"), "狙擊槍": Weapon("狙擊槍", 50, "piercing", 45, "snd_sniper"),
    "散彈槍": Weapon("散彈槍", 30, "shotgun", 20, "snd_shotgun"), "機槍": Weapon("機槍", 15, "piercing", 20, "snd_mg"),
    "火焰噴射器": Weapon("火焰噴射器", 3, "flamethrower", 4, "snd_flamethrower"), "雷射槍": Weapon("雷射槍", 25, "laser", 25, "snd_laser"),
    "電磁炮": Weapon("電磁炮", 60, "cannon", 50, "snd_cannon"), "冰霜發射器": Weapon("冰霜發射器", 5, "frost", 6, "snd_frost"),
    "重型機槍": Weapon("重型機槍", 17, "piercing", 25, "snd_heavy_mg"), "步槍": Weapon("步槍", 40, "piercing", 30, "snd_rifle"),
    "火焰榴彈": Weapon("火焰榴彈", 65, "flame_grenade", 70, "snd_grenade"), "電漿發射器": Weapon("電漿發射器", 30, "plasma", 30, "snd_plasma")
}

def get_rarity_color(r):
    if r == "金": return (255, 215, 0)
    if r == "紫": return (200, 50, 255)
    if r == "藍": return (50, 150, 255)
    return (200, 200, 200)

def apply_weapon_stats(w):
    base = WEAPON_TYPES[w.base_name]
    dmg_mult = {"白":1.0, "藍":1.3, "紫":1.6, "金":2.2}.get(w.rarity, 1.0)
    w.damage = int(base.damage * dmg_mult)
    w.shoot_delay = max(2, int(base.shoot_delay * 0.60)) if "速射" in w.affixes else base.shoot_delay

def generate_weapon(base_name, rarity="白"):
    base = WEAPON_TYPES[base_name]
    w = Weapon(base.base_name, base.shoot_delay, base.bullet_type, base.damage, base.sound_name)
    w.rarity = rarity
    affixes_pool = ["穿透", "燃燒", "速射", "散射", "吸血", "爆擊"]
    count = {"白":0, "藍":1, "紫":2, "金":3}.get(rarity, 0)
    w.affixes = random.sample(affixes_pool, count) if count > 0 else []
    apply_weapon_stats(w)
    return w

def sort_weapon_stash():
    rarity_val = {"白":0, "藍":1, "紫":2, "金":3}
    weapon_order = list(WEAPON_TYPES.keys())
    persistent_stats["weapon_stash"].sort(
        key=lambda w: (
            weapon_order.index(w.base_name) if w.base_name in weapon_order else 99,
            -rarity_val.get(w.rarity, 0),
            -len(w.affixes),
            "".join(sorted(w.affixes))
        )
    )

# ----------------- 背包實體物品系統 -----------------
class InvItem:
    def __init__(self, i_type, name, count, max_stack, weapon_obj=None):
        self.type, self.name, self.count, self.max_stack, self.weapon_obj = i_type, name, count, max_stack, weapon_obj

def create_item(i_type, amount=1, weapon_obj=None):
    if i_type == "SCRAP": return InvItem("SCRAP", "廢料", amount, 30)
    elif i_type == "MED": return InvItem("MED", "急救包", amount, 5)
    elif i_type == "KEY": return InvItem("KEY", "金鑰匙", amount, 10)
    elif i_type == "WEAPON": return InvItem("WEAPON", weapon_obj.full_name, 1, 1, weapon_obj)

def fast_transfer(item, to_list):
    for t_item in to_list:
        if t_item and t_item.type == item.type and t_item.type != "WEAPON":
            space = t_item.max_stack - t_item.count
            if space > 0:
                add = min(space, item.count)
                t_item.count += add; item.count -= add
                if item.count <= 0: return True
    if item.count > 0:
        for i in range(len(to_list)):
            if to_list[i] is None:
                to_list[i] = item; return True
    return False

# ----------------- 遊戲實體類別 -----------------
class DropItem:
    def __init__(self, x, y, item_type="EXP", weapon_obj=None):
        self.x, self.y, self.item_type, self.weapon_obj = x, y, item_type, weapon_obj
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.anim_offset = random.random() * 10
    def update(self, p_x, p_y, mag_rad):
        if self.item_type not in ["EXP", "MAGNET", "BOMB", "SHIELD"]: return 
        dist = math.sqrt((self.x - p_x)**2 + (self.y - p_y)**2)
        if dist < mag_rad and dist > 0:
            speed = 25 if mag_rad > 1000 else 8
            self.x += ((p_x - self.x) / dist) * speed; self.y += ((p_y - self.y) / dist) * speed 
        self.rect.center = (int(self.x), int(self.y))
    def draw(self, surface):
        draw_x, draw_y = int(self.x - camera_x), int(self.y - camera_y)
        float_y = draw_y + math.sin(pygame.time.get_ticks()*0.005 + self.anim_offset) * 3
        if self.item_type == "WEAPON":
            c = get_rarity_color(self.weapon_obj.rarity)
            pygame.draw.circle(surface, c, (draw_x, int(float_y)), 15, 2)
            txt = tiny_font.render(self.weapon_obj.full_name, True, c)
            surface.blit(txt, (draw_x - txt.get_width()//2, int(float_y) - 25))
            return
        img = images.get(f"drop_{self.item_type}")
        if img: surface.blit(img, img.get_rect(center=(draw_x, int(float_y))))
        else:
            if self.item_type == "EXP": pygame.draw.polygon(surface, EXP_COLOR, [(draw_x, float_y-6), (draw_x+6, float_y), (draw_x, float_y+6), (draw_x-6, float_y)])
            elif self.item_type == "MED": pygame.draw.rect(surface, HP_COLOR, (draw_x-6, float_y-4, 12, 8)); pygame.draw.rect(surface, WHITE, (draw_x-2, float_y-6, 4, 12))
            elif self.item_type == "SHIELD": pygame.draw.circle(surface, SHIELD_COLOR, (draw_x, int(float_y)), 6)
            elif self.item_type == "MAGNET": pygame.draw.circle(surface, YELLOW, (draw_x, int(float_y)), 7); pygame.draw.circle(surface, RED, (draw_x, int(float_y)), 7, 2)
            elif self.item_type == "BOMB": pygame.draw.circle(surface, (50, 50, 50), (draw_x, int(float_y)), 8)
            elif self.item_type == "SCRAP": pygame.draw.polygon(surface, SCRAP_COLOR, [(draw_x, float_y-4), (draw_x+4, float_y), (draw_x, float_y+4), (draw_x-4, float_y)])
            elif self.item_type == "KEY": pygame.draw.rect(surface, YELLOW, (draw_x-8, float_y-2, 16, 4)); pygame.draw.circle(surface, YELLOW, (draw_x-6, int(float_y)), 4, 2)

class Chest:
    def __init__(self, x, y, c_type="NORMAL"):
        self.x, self.y, self.type, self.state = x, y, c_type, "CLOSED"
        self.rect = pygame.Rect(0, 0, 50, 40)
        self.color = (139, 69, 19) if self.type == "NORMAL" else (218, 165, 32)
        self.open_progress = 0
    def draw(self, surface):
        draw_x, draw_y = int(self.x - camera_x), int(self.y - camera_y)
        self.rect.center = (draw_x, draw_y)
        if self.state == "CLOSED":
            pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
            pygame.draw.rect(surface, WHITE if self.type=="NORMAL" else YELLOW, self.rect, 2, border_radius=5)
            if self.type == "LOCKED": pygame.draw.circle(surface, BLACK, (draw_x, draw_y), 6) 
            if self.open_progress > 0:
                pygame.draw.rect(surface, GRAY, (draw_x-25, draw_y-30, 50, 6))
                pygame.draw.rect(surface, GREEN, (draw_x-25, draw_y-30, 50*(self.open_progress/40), 6))
        else:
            open_rect = pygame.Rect(0,0,50,15); open_rect.center = (draw_x, draw_y+10)
            pygame.draw.rect(surface, (80,40,10), open_rect, border_radius=3)

class PlayerLostItem:
    def __init__(self, x, y, level, exp, upgrades):
        self.x, self.y, self.level, self.exp, self.upgrades = x, y, level, exp, upgrades
        self.rect = pygame.Rect(0, 0, 40, 40)
    def draw(self, surface):
        draw_x, draw_y = int(self.x - camera_x), int(self.y - camera_y)
        pygame.draw.circle(surface, GREEN, (draw_x, draw_y), 20)
        pygame.draw.circle(surface, WHITE, (draw_x, draw_y), 22, 2)
        txt = small_font.render(f"遺失物(經驗/卡牌)", True, GREEN)
        surface.blit(txt, (draw_x - txt.get_width()//2, draw_y - 35))

class ExtractionPoint:
    def __init__(self):
        self.x, self.y, self.radius = random.randint(800, MAP_WIDTH - 800), random.randint(800, MAP_HEIGHT - 800), 150
    def draw(self, surface):
        draw_x, draw_y = int(self.x - camera_x), int(self.y - camera_y)
        pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.003)) * 20)
        pygame.draw.circle(surface, GREEN, (draw_x, draw_y), self.radius + pulse, 3)
        txt = font.render("撤離點", True, GREEN)
        surface.blit(txt, (draw_x - txt.get_width()//2, draw_y - 20))

class Player:
    def __init__(self):
        self.x, self.y, self.size = MAP_WIDTH / 2, MAP_HEIGHT / 2, 30
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        
        self.primary_weapon, self.secondary_weapon = generate_weapon("手槍", "白"), generate_weapon("散彈槍", "白")
        self.weapons = [self.primary_weapon, self.secondary_weapon]
        self.current_weapon_idx, self.cheat_all_weapons = 0, False 
        
        self.base_speed = 7.0 + persistent_stats["speed_bonus"]
        self.max_hp = 100 + persistent_stats["max_hp"]
        self.hp, self.max_shield, self.shield = self.max_hp, 100, 100       
        self.max_stamina, self.stamina, self.stamina_regen = 100, 100, 0.5   
        self.max_energy, self.energy, self.energy_regen = 100, 100, 0.2     
        self.exp, self.level, self.max_exp = 0, 1, 80
        self.inventory = [None] * 24
        
        self.bullet_count, self.bullet_spread, self.extra_same_path_bullets = 1, 15, 0
        self.bullet_damage_bonus = persistent_stats["dmg_bonus"]
        self.shoot_delay_reduction, self.damage_reduction = 0, 0
        self.invincible_duration = 60
        self.guidance_level, self.aura_level, self.regen_level, self.regen_progress = 0, 0, 0, 0
        self.exp_multiplier, self.magnet_radius = 1.0, 80
        self.drone_level, self.drone_angle, self.drone_shoot_cd = 0, 0, 0
        
        self.dash_cost, self.is_dashing, self.dash_speed, self.dash_duration = 30, False, 28, 8
        self.dash_timer, self.dash_dir_x, self.dash_dir_y = 0, 0, 0
        self.skill_cd, self.skill_max_cd, self.skill_cost = 0, 600, 50        
        self.invincible_timer, self.god_mode = 0, False 
        self.base_max_ammo, self.mag_size_bonus = 40, 0
        self.ammo, self.reload_duration, self.reload_timer = self.base_max_ammo, 90, 0

    def add_item(self, new_item):
        return fast_transfer(new_item, self.inventory)

    def use_med(self):
        for i in range(24):
            item = self.inventory[i]
            if item and item.type == "MED" and self.hp < self.max_hp:
                self.hp = min(self.max_hp, self.hp + 40); item.count -= 1
                if item.count <= 0: self.inventory[i] = None
                play_sound("exp"); return True
        return False

    def update(self, clamp_rect=None):
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
            if self.regen_progress >= 1: heal = int(self.regen_progress); self.hp = min(self.max_hp, self.hp + heal); self.regen_progress -= heal
            
        if not self.is_dashing:
            if self.stamina < self.max_stamina: self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen)
        if self.energy < self.max_energy: self.energy = min(self.max_energy, self.energy + self.energy_regen)

        if keys[pygame.K_SPACE] or keys[pygame.K_q]:
            if not self.is_dashing and self.stamina >= self.dash_cost:
                self.stamina -= self.dash_cost; self.is_dashing = True; self.dash_timer = self.dash_duration
                play_sound("dash")
                if dist > 0: self.dash_dir_x, self.dash_dir_y = move_x, move_y
                else:
                    mx, my = pygame.mouse.get_pos()
                    wx, wy = mx + camera_x, my + camera_y
                    dx, dy = wx - self.x, wy - self.y
                    ddist = math.sqrt(dx**2 + dy**2)
                    if ddist > 0: self.dash_dir_x, self.dash_dir_y = dx / ddist, dy / ddist

        if self.is_dashing:
            self.x += self.dash_dir_x * self.dash_speed; self.y += self.dash_dir_y * self.dash_speed
            self.dash_timer -= 1
            if self.dash_timer <= 0: self.is_dashing = False
        else:
            self.x += move_x * self.base_speed; self.y += move_y * self.base_speed
            
        if clamp_rect:
            self.x = max(clamp_rect.left + self.size/2, min(clamp_rect.right - self.size/2, self.x))
            self.y = max(clamp_rect.top + self.size/2, min(clamp_rect.bottom - self.size/2, self.y))
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
                mx, _ = pygame.mouse.get_pos()
                if mx + camera_x < self.x: img = pygame.transform.flip(img, True, False)
                surface.blit(img, img.get_rect(center=draw_center))
            else: pygame.draw.rect(surface, YELLOW if self.god_mode else BLUE, draw_rect)
                
            if self.stamina < self.dash_cost: pygame.draw.rect(surface, GRAY, draw_rect, 3)

            if current_wep:
                mx, my = pygame.mouse.get_pos()
                dx, dy = (mx + camera_x) - self.x, (my + camera_y) - self.y
                dist = math.sqrt(dx**2 + dy**2)
                dir_x, dir_y = (dx / dist, dy / dist) if dist > 0 else (1, 0)
                angle = math.degrees(math.atan2(-dy, dx))
                gun_img = images.get("gun_" + current_wep.base_name)
                if gun_img:
                    if dx < 0: gun_img = pygame.transform.flip(gun_img, False, True)
                    rotated_gun = pygame.transform.rotate(gun_img, angle)
                    offset_x, offset_y = dir_x * 15, dir_y * 15
                    surface.blit(rotated_gun, rotated_gun.get_rect(center=(int(self.x + offset_x - camera_x), int(self.y + offset_y - camera_y))))

        if self.aura_level > 0:
            pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10)
            pygame.draw.circle(surface, (0, 180, 255), draw_rect.center, 95 + self.aura_level * 25 + pulse, 2)
            
        if self.drone_level > 0:
            drone_x, drone_y = draw_center[0] + math.cos(self.drone_angle) * 55, draw_center[1] + math.sin(self.drone_angle) * 55
            pygame.draw.circle(surface, (150, 200, 255), (int(drone_x), int(drone_y)), 10)
            pygame.draw.circle(surface, BLUE, (int(drone_x), int(drone_y)), 10, 2); pygame.draw.circle(surface, RED, (int(drone_x), int(drone_y)), 4)

class DashTrail:
    def __init__(self, x, y, size): self.x, self.y, self.size, self.life = x, y, size, 12
    def update(self): self.life -= 1; self.size -= 1.5
    def draw(self, surface):
        if self.life > 0 and self.size > 0:
            rect = pygame.Rect(0, 0, self.size, self.size); rect.center = (int(self.x - camera_x), int(self.y - camera_y))
            pygame.draw.rect(surface, BLUE, rect, max(1, int(self.life / 3)))

class Bullet:
    def __init__(self, x, y, target_x, target_y, weapon, guidance_level=0, dmg_bonus=0):
        self.x, self.y = x, y
        crit_chance = 0.35 if "爆擊" in weapon.affixes else 0.10
        crit_mult = 3.0 if "爆擊" in weapon.affixes else 2.0
        self.is_crit = random.random() < crit_chance
        base_dmg = weapon.damage + dmg_bonus
        self.damage = int(base_dmg * crit_mult) if self.is_crit else base_dmg
        
        self.b_type = weapon.bullet_type
        self.is_burning = "燃燒" in weapon.affixes
        self.is_vampiric = "吸血" in weapon.affixes
        self.is_piercing = self.b_type in ["piercing", "laser", "cannon", "flamethrower"] or "穿透" in weapon.affixes
        self.guidance_level = guidance_level
            
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
        if self.is_burning: self.color = ORANGE

        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        self.explode = False 
        self.target_x, self.target_y = target_x, target_y

    def update(self):
        self.lifespan -= 1
        if self.b_type == "flame_grenade" and math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2) < self.speed:
            self.explode = True; self.lifespan = 0; return 

        if self.guidance_level > 0 and len(enemies) > 0:
            closest_enemy = min(enemies, key=lambda e: math.sqrt((self.x - e.x)**2 + (self.y - e.y)**2), default=None)
            if closest_enemy:
                tx, ty = closest_enemy.x - self.x, closest_enemy.y - self.y
                tdist = math.sqrt(tx**2 + ty**2)
                if tdist > 0:
                    tx, ty = tx / tdist, ty / tdist; turn_speed = min(0.1, 0.02 + self.guidance_level * 0.015)
                    self.dir_x = self.dir_x * (1 - turn_speed) + tx * turn_speed; self.dir_y = self.dir_y * (1 - turn_speed) + ty * turn_speed
                    ndist = math.sqrt(self.dir_x**2 + self.dir_y**2)
                    if ndist > 0: self.dir_x /= ndist; self.dir_y /= ndist

        self.x += self.dir_x * self.speed; self.y += self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        img = images.get("bullet_" + self.b_type)
        if img: surface.blit(pygame.transform.rotate(img, math.degrees(math.atan2(-self.dir_y, self.dir_x))), img.get_rect(center=draw_center))
        else: pygame.draw.circle(surface, self.color, draw_center, self.radius)
        if self.is_crit: pygame.draw.circle(surface, RED, draw_center, self.radius+2, 1)

class EnemyBullet:
    def __init__(self, x, y, dir_x, dir_y, color=ORANGE, is_homing=False, weapon=None):
        self.x, self.y, self.dir_x, self.dir_y = x, y, dir_x, dir_y
        dist = math.sqrt(dir_x**2 + dir_y**2)
        if dist > 0: self.dir_x /= dist; self.dir_y /= dist
        self.is_homing, self.weapon, self.radius, self.speed, self.color = is_homing, weapon, 8, 7, color
        self.damage, self.b_type = 15, "normal"
        if weapon:
            self.b_type, self.damage = weapon.bullet_type, int(weapon.damage * 0.8)
            if self.b_type == "piercing": self.color, self.speed, self.radius = PURPLE, 15, 7
            elif self.b_type == "flamethrower": self.color, self.speed, self.radius = ORANGE, 8, 12
            elif self.b_type == "laser": self.color, self.speed, self.radius = CYAN, 25, 4
            elif self.b_type == "cannon": self.color, self.speed, self.radius = WHITE, 8, 15
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        
    def update(self, target_x=None, target_y=None):
        if self.is_homing and target_x is not None and target_y is not None:
            tx, ty = target_x - self.x, target_y - self.y
            dist = math.sqrt(tx**2 + ty**2)
            if dist > 0:
                turn_speed = 0.035
                self.dir_x = self.dir_x * (1 - turn_speed) + (tx / dist) * turn_speed
                self.dir_y = self.dir_y * (1 - turn_speed) + (ty / dist) * turn_speed
                ndist = math.sqrt(self.dir_x**2 + self.dir_y**2)
                if ndist > 0: self.dir_x /= ndist; self.dir_y /= ndist
        self.x += self.dir_x * self.speed; self.y += self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface): 
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        pygame.draw.circle(surface, self.color, draw_center, self.radius)

class Enemy:
    def __init__(self, level, is_elite=False, spawn_x=MAP_WIDTH/2, spawn_y=MAP_HEIGHT/2):
        self.is_elite, self.size = is_elite, 35 if is_elite else 25
        difficulty_mult = 1.75 if game_mode == "CHALLENGE" else 1.0
        self.speed = ((random.uniform(3.0, 5.5) if is_elite else random.uniform(2.5, 4.5)) + level * 0.05) * (1.2 if game_mode == "CHALLENGE" else 1.0)
        self.max_hp = int(((60 + level * 25) if is_elite else (20 + level * 8)) * difficulty_mult)
        self.hp, self.max_shield = self.max_hp, int(((20 + level * 8) if is_elite else (10 + level * 4)) * difficulty_mult)
        self.shield, self.damage = self.max_shield, int(((35 + level * 3) if is_elite else (15 + level * 1.5)) * difficulty_mult)
        self.frost_timer, self.burn_timer, self.dir_x, self.dir_y = 0, 0, 1, 0  
        self.shoot_cd, self.weapon = random.randint(60, 120), None
        
        self.combat_type = random.choice(["melee", "ranged"]) if is_elite else random.choices(["melee", "ranged", "kamikaze"], weights=[0.45, 0.45, 0.1])[0]
        if self.combat_type == "kamikaze": self.color, self.speed, self.max_hp, self.damage = ORANGE, self.speed*1.4, int(self.max_hp*0.6), int(self.damage*1.5)
        elif self.combat_type == "ranged":
            self.weapon = random.choice(list(WEAPON_TYPES.values()))
            self.shoot_cd = self.weapon.shoot_delay * 3 + random.randint(20, 60)
        
        spawn_dist_x, spawn_dist_y = WIDTH / 2 + 50, HEIGHT / 2 + 50
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top': self.x, self.y = spawn_x + random.randint(-int(spawn_dist_x), int(spawn_dist_x)), spawn_y - spawn_dist_y
        elif edge == 'bottom': self.x, self.y = spawn_x + random.randint(-int(spawn_dist_x), int(spawn_dist_x)), spawn_y + spawn_dist_y
        elif edge == 'left': self.x, self.y = spawn_x - spawn_dist_x, spawn_y + random.randint(-int(spawn_dist_y), int(spawn_dist_y))
        elif edge == 'right': self.x, self.y = spawn_x + spawn_dist_x, spawn_y + random.randint(-int(spawn_dist_y), int(spawn_dist_y))
            
        self.x, self.y = max(0, min(self.x, MAP_WIDTH)), max(0, min(self.y, MAP_HEIGHT))
        self.rect = pygame.Rect(0, 0, self.size, self.size)

    def update(self, target_x, target_y, all_enemies, enemy_bullets):
        current_speed = self.speed * 0.4 if self.frost_timer > 0 else self.speed
        if self.frost_timer > 0: self.frost_timer -= 1 
        if self.burn_timer > 0:
            self.burn_timer -= 1
            if self.burn_timer % 15 == 0: self.hp -= 8; particles.append(Particle(self.x, self.y, ORANGE))

        dx, dy = target_x - self.x, target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0: self.dir_x, self.dir_y = dx / dist, dy / dist

        if self.combat_type == "ranged":
            if dist > 350: self.x += self.dir_x * current_speed; self.y += self.dir_y * current_speed
            elif dist < 200: self.x -= self.dir_x * current_speed; self.y -= self.dir_y * current_speed
            if self.shoot_cd <= 0 and dist <= 500:
                enemy_bullets.append(EnemyBullet(self.x, self.y, self.dir_x, self.dir_y, weapon=self.weapon))
                self.shoot_cd = self.weapon.shoot_delay * 4 + random.randint(20, 60)
            if self.shoot_cd > 0: self.shoot_cd -= 1
        elif self.combat_type == "kamikaze":
            self.x += self.dir_x * current_speed; self.y += self.dir_y * current_speed
        else:
            if dist > (self.size + 30) / 2:
                if dist > 0: self.x += self.dir_x * current_speed; self.y += self.dir_y * current_speed

        for other in all_enemies:
            if other is not self and 0 < (self.x - other.x)**2 + (self.y - other.y)**2 < self.size**2:
                dist_val = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
                self.x += ((self.x - other.x) / dist_val) * 1.3; self.y += ((self.y - other.y) / dist_val) * 1.3
            
        self.x, self.y = max(0, min(self.x, MAP_WIDTH)), max(0, min(self.y, MAP_HEIGHT))
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        draw_rect = self.rect.copy(); draw_rect.center = draw_center
        
        if self.combat_type == "kamikaze":
            pygame.draw.circle(surface, ORANGE, draw_center, self.size // 2)
        else:
            color = (150, 0, 150) if self.is_elite else RED
            if self.frost_timer > 0: color = (100, 200, 255)
            if self.is_elite: pygame.draw.rect(surface, DARK_PURPLE, draw_rect.copy().inflate(6, 6), 3) 
            pygame.draw.rect(surface, color, draw_rect)

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
        self.state_timer, self.frost_timer, self.burn_timer = 0, 0, 0
        self.play_shoot_sound = False 
        
        base_hp = {"YELLOW": 3000, "RED": 4000, "PURPLE": 2500, "CYAN": 3200}[self.b_type]
        self.max_hp = int((base_hp + level * 100) * (1.75 if game_mode == "CHALLENGE" else 1.0))
        self.hp = self.max_hp
        
        if self.b_type == "YELLOW": self.color, self.speed, self.state = YELLOW, 4.0, "EVADE"
        elif self.b_type == "RED": self.color, self.speed, self.state, self.aim_x, self.aim_y = RED, 3.5, "CHASE", 0, 0
        elif self.b_type == "PURPLE": self.color, self.speed, self.state = PURPLE, 3.0, "FLEE"
        elif self.b_type == "CYAN": self.color, self.speed, self.state = CYAN, 3.5, "IDLE" 

    def update(self, player_x, player_y, bullets, enemies, enemy_bullets):
        self.state_timer += 1
        current_speed = self.speed * 0.5 if self.frost_timer > 0 else self.speed
        if self.frost_timer > 0: self.frost_timer -= 1
        if self.burn_timer > 0:
            self.burn_timer -= 1
            if self.burn_timer % 15 == 0: self.hp -= 10; particles.append(Particle(self.x, self.y, ORANGE))
                
        dx, dy = player_x - self.x, player_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        dir_x, dir_y = (dx / dist, dy / dist) if dist > 0 else (0, 0)

        if self.b_type == "RED":
            if self.state == "CHASE":
                if dist > 0: self.x += dir_x * current_speed; self.y += dir_y * current_speed
                if self.state_timer > 150: self.state = "WARN"; self.state_timer = 0
            elif self.state == "WARN":
                self.aim_x, self.aim_y = player_x, player_y
                if self.state_timer > 45:
                    self.state = "DASH"; self.state_timer = 0
                    dash_dist = math.sqrt((self.aim_x - self.x)**2 + (self.aim_y - self.y)**2)
                    self.dash_dir_x, self.dash_dir_y = (self.aim_x - self.x) / dash_dist, (self.aim_y - self.y) / dash_dist if dash_dist > 0 else (0,0)
            elif self.state == "DASH":
                self.x += self.dash_dir_x * (current_speed * 6); self.y += self.dash_dir_y * (current_speed * 6)
                if self.state_timer > 20: self.state = "CHASE"; self.state_timer = 0
        else:
            if dist > 0: self.x += dir_x * current_speed * 0.5; self.y += dir_y * current_speed * 0.5

        self.x = max(self.size, min(MAP_WIDTH - self.size, self.x))
        self.y = max(self.size, min(MAP_HEIGHT - self.size, self.y))
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        pygame.draw.rect(surface, self.color, self.rect.copy().move(-camera_x, -camera_y))

class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vel_x, self.vel_y = random.uniform(-6, 6), random.uniform(-6, 6)
        self.timer, self.size, self.color = random.randint(15, 30), random.randint(4, 8), color
    def update(self): self.x += self.vel_x; self.y += self.vel_y; self.timer -= 1; self.size = max(0, self.size - 0.25)
    def draw(self, surface):
        if self.size > 0: pygame.draw.rect(surface, self.color, (int(self.x - camera_x), int(self.y - camera_y), int(self.size), int(self.size)))

class DamageText:
    def __init__(self, x, y, damage, color=WHITE, is_crit=False):
        self.x, self.y, self.damage, self.color, self.is_crit = x, y, damage, color, is_crit
        self.timer, self.vel_y, self.alpha = 40, -1.5, 255
    def update(self): self.y += self.vel_y; self.timer -= 1; self.alpha = max(0, int((self.timer / 40) * 255))
    def draw(self, surface):
        if self.timer > 0:
            txt_surf = (large_font if self.is_crit else font).render(f"-{int(self.damage)}{'!' if self.is_crit else ''}", True, self.color)
            txt_surf.set_alpha(self.alpha); surface.blit(txt_surf, (int(self.x - camera_x), int(self.y - camera_y)))

# ----------------- UI 繪製與升級卡牌 -----------------
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
        "v2.7 - 塔科夫究極地堡版",
        "- 新增：武器改造台，花費廢料可升級武器品質或重置隨機詞綴！",
        "- 新增：格子收藏箱，專門存放在戰局中打到的所有補給物資。",
        "- 新增：全自動武器箱，只收納武器，並自動依照種類、品質與詞綴排列。",
        "- 修復：密技衝突問題與 UI 疊加顯示問題。",
        "- 保留：ZERO SIEVERT 真實負重系統、完整 25 張卡牌與無盡難度。",
        "- 操作：地堡內按 [E] 進入設施。戰鬥中按 [TAB] 開啟背包，右鍵可快速裝備武器。",
    ]
    content_lines = []
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
    popup = pygame.Rect(WIDTH//2 - 360, HEIGHT//2 - 280, 720, 560)
    panel = pygame.Surface((popup.width, popup.height), pygame.SRCALPHA); panel.fill((18, 20, 32, 235))
    surface.blit(panel, popup.topleft); pygame.draw.rect(surface, WHITE, popup, 3, border_radius=12)
    surface.blit(large_font.render("更新日誌", True, YELLOW), (popup.centerx - large_font.size("更新日誌")[0]//2, popup.y + 20))
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
    surface.blit(font.render("關閉", True, WHITE), (changelog_close_button.centerx - font.size("關閉")[0]//2, changelog_close_button.centery - font.size("關閉")[1]//2))

def draw_upgrade_summary(surface, x, y, max_items=6, title="已選強化"):
    panel_width, row_height = 240, 26
    hidden_count = max(0, len(chosen_upgrades) - max_items)
    row_count = max(1, min(len(chosen_upgrades), max_items))
    panel_height = 40 + row_count * row_height + (row_height if hidden_count else 0)
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA); panel.fill((18, 20, 30, 185))
    surface.blit(panel, (x, y)); pygame.draw.rect(surface, WHITE, (x, y, panel_width, panel_height), 2, border_radius=8)
    total_count = sum(u["count"] for u in chosen_upgrades)
    surface.blit(small_font.render(f"{title} ({total_count})" if chosen_upgrades else title, True, YELLOW), (x + 14, y + 10))
    if not chosen_upgrades:
        surface.blit(small_font.render("尚未選擇", True, GRAY), (x + 14, y + 40)); return
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
    if not rows: surface.blit(small_font.render("尚未選擇任何強化", True, GRAY), (content_rect.x, content_rect.y + 8)); return
    row_h, content_height = 50, max(content_rect.height, len(rows) * 50)
    max_scroll = max(0, content_height - content_rect.height)
    scroll_y = min(pause_upgrade_scroll, max_scroll)
    content_surface = pygame.Surface((content_rect.width, content_height), pygame.SRCALPHA)
    for i, (name, desc) in enumerate(rows):
        content_surface.blit(small_font.render(name, True, WHITE), (0, i * row_h))
        for j, line in enumerate(wrap_text(desc, tiny_font, content_rect.width - 20)):
            content_surface.blit(tiny_font.render(line, True, YELLOW), (18, i * row_h + 20 + j * 16))
    surface.blit(content_surface, content_rect.topleft, pygame.Rect(0, scroll_y, content_rect.width, content_rect.height))

def draw_minimap(surface):
    mm_w, mm_h = 160, 120
    mm_x, mm_y = WIDTH - mm_w - 20, 20
    mm_surface = pygame.Surface((mm_w, mm_h), pygame.SRCALPHA)
    mm_surface.fill((10, 10, 20, 180))
    pygame.draw.rect(mm_surface, WHITE, (0, 0, mm_w, mm_h), 2)
    scale_x, scale_y = mm_w / MAP_WIDTH, mm_h / MAP_HEIGHT
    if extraction_pt: pygame.draw.circle(mm_surface, GREEN, (int(extraction_pt.x * scale_x), int(extraction_pt.y * scale_y)), 4)
    if lost_item: pygame.draw.circle(mm_surface, YELLOW, (int(lost_item.x * scale_x), int(lost_item.y * scale_y)), 3)
    if boss_active and boss: pygame.draw.circle(mm_surface, RED, (int(boss.x * scale_x), int(boss.y * scale_y)), 5)
    pygame.draw.circle(mm_surface, BLUE, (int(player.x * scale_x), int(player.y * scale_y)), 4)
    surface.blit(mm_surface, (mm_x, mm_y))

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

def apply_upgrade(choice, silent=False):
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

    current_upgrade_choices.clear(); selected_upgrade_position = None
    if not silent: game_state = "PLAYING"             

# ----------------- 遊戲管理初始化 -----------------
game_state = "MENU"
game_mode = "NORMAL"
show_inventory = False
drag_data = None 
selected_mod_weapon = None 
selected_arsenal_idx, arsenal_scroll_y = 0, 0

bullets, enemy_bullets, enemies, particles, items, trails, damage_texts, chests = [], [], [], [], [], [], [], []
boss_active, boss, defeated_boss_levels = False, None, []
extraction_pt, extraction_timer, extract_progress, boss_army_active = None, 0, 0, False
lost_item = None
current_upgrade_choices, selected_upgrade_position, chosen_upgrades = [], None, []

exit_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 170, 200, 50)
start_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 30, 200, 50)
changelog_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50)
changelog_close_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 200, 200, 45)
normal_button = pygame.Rect(WIDTH//2 - 340, HEIGHT//2 - 35, 320, 230)
challenge_button = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 - 35, 320, 230)
difficulty_back_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 245, 220, 50)
cards =[pygame.Rect(WIDTH//2 - 370, 240, 220, 280), pygame.Rect(WIDTH//2 - 110, 240, 220, 280), pygame.Rect(WIDTH//2 + 150, 240, 220, 280)]
confirm_upgrade_button = pygame.Rect(WIDTH//2 - 110, 560, 220, 50)
pause_upgrade_scroll, changelog_scroll, changelog_max_scroll = 0, 0, 0
show_changelog, changelog_content_surface = False, None

def put_item_in_slot(source, idx, item):
    t_list = persistent_stats["general_stash"] if source == "STASH" else player.inventory
    t_item = t_list[idx]
    if t_item is None: t_list[idx] = item; return None
    elif t_item.type == item.type and t_item.type != "WEAPON":
        space = t_item.max_stack - t_item.count
        add = min(space, item.count)
        t_item.count += add; item.count -= add
        if item.count > 0: return item
        return None
    else:
        t_list[idx] = item; return t_item

def draw_player_inv_grid(surface, start_x, start_y, m_x, m_y, allow_weapons=True):
    slot_size, margin = 50, 8
    for i in range(24):
        col, row = i % 6, i // 6
        rect = pygame.Rect(start_x + col*(slot_size+margin), start_y + row*(slot_size+margin), slot_size, slot_size)
        pygame.draw.rect(surface, (40, 40, 50), rect, border_radius=5)
        pygame.draw.rect(surface, GRAY, rect, 1, border_radius=5)
        
        item = player.inventory[i]
        if item and not (drag_data and drag_data["source"] == "PLAYER" and drag_data["idx"] == i):
            if not allow_weapons and item.type == "WEAPON":
                pygame.draw.circle(surface, (50,50,50), rect.center, 12)
            else:
                c = WHITE
                if item.type == "WEAPON": c = get_rarity_color(item.weapon_obj.rarity)
                elif item.type == "MED": c = HP_COLOR
                elif item.type == "SCRAP": c = SCRAP_COLOR
                elif item.type == "KEY": c = YELLOW
                pygame.draw.circle(surface, c, rect.center, 12)
                if item.type != "WEAPON": surface.blit(tiny_font.render(str(item.count), True, WHITE), (rect.right - 18, rect.bottom - 18))
            
            if rect.collidepoint(m_x, m_y) and drag_data is None:
                info_txt = item.name if item.type != "WEAPON" else item.weapon_obj.full_name
                pygame.draw.rect(surface, BLACK, (m_x + 10, m_y - 20, font.size(info_txt)[0]+10, 25))
                surface.blit(small_font.render(info_txt, True, WHITE), (m_x + 15, m_y - 18))

player = Player()

def reset_game(initial_state="MENU", mode="NORMAL", keep_stash=False):
    global player, bullets, enemy_bullets, enemies, particles, items, trails, chests
    global boss, boss_active, defeated_boss_levels, game_state, shoot_cooldown
    global key_buffer, damage_texts, camera_x, camera_y, game_mode
    global current_upgrade_choices, selected_upgrade_position, chosen_upgrades
    global show_changelog, changelog_scroll, changelog_content_surface, changelog_max_scroll, pause_upgrade_scroll
    global magnet_timer, screen_flash_timer, lost_item, show_inventory, drag_data, selected_mod_weapon

    game_mode = mode
    old_lost = lost_item if keep_stash else None
    player = Player()
    lost_item = old_lost
    bullets, enemy_bullets, enemies, particles, items, trails, damage_texts, chests = [], [], [], [], [], [], [], []
    boss, boss_active, defeated_boss_levels = None, False, []
    shoot_cooldown, key_buffer = 0, []
    camera_x, camera_y = MAP_WIDTH//2 - WIDTH/2, MAP_HEIGHT//2 - HEIGHT/2
    
    current_upgrade_choices, selected_upgrade_position, chosen_upgrades = [], None, []
    show_changelog, changelog_scroll, changelog_content_surface, changelog_max_scroll, pause_upgrade_scroll = False, 0, None, 0, 0
    magnet_timer, screen_flash_timer = 0, 0
    show_inventory, drag_data, selected_mod_weapon = False, None, None
    
    stop_sound("boss_bgm")
    game_state = initial_state

reset_game()
SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY_EVENT, 500) 

dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); dim_surface.fill((0, 0, 0, 180))

running = True
while running:
    m_x, m_y = pygame.mouse.get_pos()
    m_pos = (m_x, m_y)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if game_state == "MENU" and show_changelog and event.type == pygame.MOUSEWHEEL: changelog_scroll = max(0, min(changelog_max_scroll, changelog_scroll - event.y * 55))
        if game_state == "PAUSED" and event.type == pygame.MOUSEWHEEL: pause_upgrade_scroll = max(0, pause_upgrade_scroll - event.y * 45)
        if game_state == "WEAPON_STASH" and event.type == pygame.MOUSEWHEEL: arsenal_scroll_y = max(0, arsenal_scroll_y - event.y * 30)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == "PLAYING" and not show_inventory: game_state = "PAUSED"
                elif game_state == "PLAYING" and show_inventory: show_inventory = False; drag_data = None
                elif game_state == "PAUSED": game_state = "PLAYING"
                elif game_state in ["SHOP", "WEAPON_STASH", "GENERAL_STASH", "MOD_STATION"]: game_state = "BUNKER"; drag_data = None
                elif game_state == "DIFFICULTY": game_state = "MENU"
            if event.key == pygame.K_TAB and game_state == "PLAYING": show_inventory = not show_inventory; drag_data = None
            if event.key == pygame.K_h and game_state == "PLAYING" and not show_inventory: player.use_med()

        # 背包拖放邏輯 (戰鬥中)
        if show_inventory and game_state == "PLAYING":
            slot_size, margin, start_x, start_y = 50, 8, WIDTH//2 - 170, HEIGHT//2 - 50
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in range(24):
                        rect = pygame.Rect(start_x + (i%6)*(slot_size+margin), start_y + (i//6)*(slot_size+margin), slot_size, slot_size)
                        if rect.collidepoint(event.pos) and player.inventory[i]:
                            drag_data = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}
                            player.inventory[i] = None; break
                elif event.button == 3:
                    for i in range(24):
                        rect = pygame.Rect(start_x + (i%6)*(slot_size+margin), start_y + (i//6)*(slot_size+margin), slot_size, slot_size)
                        if rect.collidepoint(event.pos) and player.inventory[i]:
                            item = player.inventory[i]
                            if item.type == "MED": player.use_med()
                            elif item.type == "WEAPON":
                                old_wep = player.weapons[player.current_weapon_idx]
                                player.weapons[player.current_weapon_idx] = item.weapon_obj
                                if player.current_weapon_idx == 0: player.primary_weapon = item.weapon_obj
                                else: player.secondary_weapon = item.weapon_obj
                                player.inventory[i] = create_item("WEAPON", 1, old_wep); play_sound("exp")
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drag_data:
                dropped_in_slot = False
                for i in range(24):
                    rect = pygame.Rect(start_x + (i%6)*(slot_size+margin), start_y + (i//6)*(slot_size+margin), slot_size, slot_size)
                    if rect.collidepoint(event.pos):
                        rem = put_item_in_slot("PLAYER", i, drag_data["item"])
                        if rem: put_item_in_slot(drag_data["source"], drag_data["idx"], rem)
                        dropped_in_slot = True; break
                
                if not dropped_in_slot and not pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 200, 400, 400).collidepoint(event.pos):
                    item = drag_data["item"]
                    if item.type == "WEAPON": items.append(DropItem(player.x, player.y, "WEAPON", item.weapon_obj))
                    else: items.append(DropItem(player.x, player.y, item.type))
                elif not dropped_in_slot:
                    put_item_in_slot(drag_data["source"], drag_data["idx"], drag_data["item"])
                drag_data = None

        # 格子收藏箱 (GENERAL_STASH) 邏輯
        elif game_state == "GENERAL_STASH":
            p_start_x, p_start_y = WIDTH//2 - 170, HEIGHT//2 + 20
            s_start_x, s_start_y = WIDTH//2 - 170, HEIGHT//2 - 220
            slot_size, margin = 50, 8
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Check Stash
                    for i in range(36):
                        rect = pygame.Rect(s_start_x + (i%6)*(slot_size+margin), s_start_y + (i//6)*(slot_size+margin), slot_size, slot_size)
                        if rect.collidepoint(event.pos) and persistent_stats["general_stash"][i]:
                            drag_data = {"source": "STASH", "idx": i, "item": persistent_stats["general_stash"][i]}
                            persistent_stats["general_stash"][i] = None; break
                    # Check Player
                    if not drag_data:
                        for i in range(24):
                            rect = pygame.Rect(p_start_x + (i%6)*(slot_size+margin), p_start_y + (i//6)*(slot_size+margin), slot_size, slot_size)
                            if rect.collidepoint(event.pos) and player.inventory[i]:
                                drag_data = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}
                                player.inventory[i] = None; break
                elif event.button == 3: # Fast transfer
                    for i in range(36):
                        rect = pygame.Rect(s_start_x + (i%6)*(slot_size+margin), s_start_y + (i//6)*(slot_size+margin), slot_size, slot_size)
                        if rect.collidepoint(event.pos) and persistent_stats["general_stash"][i]:
                            if fast_transfer(persistent_stats["general_stash"][i], player.inventory): persistent_stats["general_stash"][i] = None; play_sound("exp")
                    for i in range(24):
                        rect = pygame.Rect(p_start_x + (i%6)*(slot_size+margin), p_start_y + (i//6)*(slot_size+margin), slot_size, slot_size)
                        item = player.inventory[i]
                        if rect.collidepoint(event.pos) and item and item.type != "WEAPON":
                            if fast_transfer(item, persistent_stats["general_stash"]): player.inventory[i] = None; play_sound("exp")
                
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drag_data:
                dropped = False
                # Drop to Stash (Block Weapons)
                for i in range(36):
                    rect = pygame.Rect(s_start_x + (i%6)*(slot_size+margin), s_start_y + (i//6)*(slot_size+margin), slot_size, slot_size)
                    if rect.collidepoint(event.pos):
                        if drag_data["item"].type == "WEAPON": break # 拒絕武器放入
                        rem = put_item_in_slot("STASH", i, drag_data["item"])
                        if rem: put_item_in_slot(drag_data["source"], drag_data["idx"], rem)
                        dropped = True; break
                # Drop to Player
                if not dropped:
                    for i in range(24):
                        rect = pygame.Rect(p_start_x + (i%6)*(slot_size+margin), p_start_y + (i//6)*(slot_size+margin), slot_size, slot_size)
                        if rect.collidepoint(event.pos):
                            rem = put_item_in_slot("PLAYER", i, drag_data["item"])
                            if rem: put_item_in_slot(drag_data["source"], drag_data["idx"], rem)
                            dropped = True; break
                if not dropped: put_item_in_slot(drag_data["source"], drag_data["idx"], drag_data["item"])
                drag_data = None
                
        elif game_state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_changelog:
                    if changelog_close_button.collidepoint(event.pos): show_changelog, changelog_scroll = False, 0
                else:
                    if start_button.collidepoint(event.pos): game_state = "DIFFICULTY"
                    elif changelog_button.collidepoint(event.pos): show_changelog, changelog_scroll = True, 0; rebuild_changelog_cache(640, 380)
                    elif exit_button.collidepoint(event.pos): running = False

        elif game_state == "DIFFICULTY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if normal_button.collidepoint(event.pos): reset_game("BUNKER", "NORMAL")
                elif challenge_button.collidepoint(event.pos): reset_game("BUNKER", "CHALLENGE")
                elif difficulty_back_button.collidepoint(event.pos): game_state = "MENU"

        elif game_state == "BUNKER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                p_rect_world = player.rect.copy()
                door = pygame.Rect(MAP_WIDTH//2 - 60, MAP_HEIGHT//2 + 200, 120, 60)
                shop = pygame.Rect(MAP_WIDTH//2 - 350, MAP_HEIGHT//2 - 50, 100, 100)
                mod_st = pygame.Rect(MAP_WIDTH//2 - 150, MAP_HEIGHT//2 - 150, 100, 100)
                gen_st = pygame.Rect(MAP_WIDTH//2 + 50, MAP_HEIGHT//2 - 150, 100, 100)
                wep_st = pygame.Rect(MAP_WIDTH//2 + 250, MAP_HEIGHT//2 - 50, 100, 100)
                
                if p_rect_world.colliderect(door): start_raid()
                elif p_rect_world.colliderect(shop): game_state = "SHOP"; play_sound("exp")
                elif p_rect_world.colliderect(gen_st): game_state = "GENERAL_STASH"; play_sound("exp")
                elif p_rect_world.colliderect(mod_st): game_state = "MOD_STATION"; selected_mod_weapon = None; play_sound("exp")
                elif p_rect_world.colliderect(wep_st): 
                    game_state = "WEAPON_STASH"; play_sound("exp")
                    if player.cheat_all_weapons:
                        player.god_mode = False; player.cheat_all_weapons = False
                        player.weapons = [player.primary_weapon, player.secondary_weapon]
                        player.current_weapon_idx = 0
                    sort_weapon_stash()

        elif game_state == "SHOP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                btn_hp = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 60, 200, 40)
                btn_dmg = pygame.Rect(WIDTH//2 - 100, HEIGHT//2, 200, 40)
                btn_spd = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 60, 200, 40)
                btn_close = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 150, 100, 40)
                cost = 50
                if btn_hp.collidepoint(event.pos) and persistent_stats["scrap"] >= cost:
                    persistent_stats["scrap"] -= cost; persistent_stats["max_hp"] += 10
                    player.max_hp += 10; player.hp += 10; play_sound("levelup")
                elif btn_dmg.collidepoint(event.pos) and persistent_stats["scrap"] >= cost:
                    persistent_stats["scrap"] -= cost; persistent_stats["dmg_bonus"] += 2
                    player.bullet_damage_bonus += 2; play_sound("levelup")
                elif btn_spd.collidepoint(event.pos) and persistent_stats["scrap"] >= cost:
                    persistent_stats["scrap"] -= cost; persistent_stats["speed_bonus"] += 0.2
                    player.base_speed += 0.2; play_sound("levelup")
                elif btn_close.collidepoint(event.pos): game_state = "BUNKER"
                
        elif game_state == "MOD_STATION":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 選擇武器
                p_start_x, p_start_y = WIDTH//2 - 320, HEIGHT//2 + 20
                if pygame.Rect(WIDTH//2 - 320, HEIGHT//2 - 100, 140, 100).collidepoint(event.pos): selected_mod_weapon = player.primary_weapon
                elif pygame.Rect(WIDTH//2 - 160, HEIGHT//2 - 100, 140, 100).collidepoint(event.pos): selected_mod_weapon = player.secondary_weapon
                else:
                    for i in range(24):
                        rect = pygame.Rect(p_start_x + (i%6)*58, p_start_y + (i//6)*58, 50, 50)
                        if rect.collidepoint(event.pos) and player.inventory[i] and player.inventory[i].type == "WEAPON":
                            selected_mod_weapon = player.inventory[i].weapon_obj; break
                            
                btn_close = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 270, 100, 40)
                if btn_close.collidepoint(event.pos): game_state = "BUNKER"
                
                # 改造邏輯
                if selected_mod_weapon:
                    upg_btn = pygame.Rect(WIDTH//2 + 50, HEIGHT//2 + 100, 260, 40)
                    reroll_btn = pygame.Rect(WIDTH//2 + 50, HEIGHT//2 + 160, 260, 40)
                    
                    if upg_btn.collidepoint(event.pos) and selected_mod_weapon.rarity != "金":
                        cost = {"白":50, "藍":150, "紫":300}[selected_mod_weapon.rarity]
                        if persistent_stats["scrap"] >= cost:
                            persistent_stats["scrap"] -= cost
                            selected_mod_weapon.rarity = {"白":"藍", "藍":"紫", "紫":"金"}[selected_mod_weapon.rarity]
                            count = {"白":0, "藍":1, "紫":2, "金":3}[selected_mod_weapon.rarity]
                            selected_mod_weapon.affixes = random.sample(["穿透", "燃燒", "速射", "散射", "吸血", "爆擊"], count)
                            apply_weapon_stats(selected_mod_weapon); play_sound("levelup")
                            
                    if reroll_btn.collidepoint(event.pos) and selected_mod_weapon.rarity != "白":
                        cost = {"藍":30, "紫":80, "金":150}[selected_mod_weapon.rarity]
                        if persistent_stats["scrap"] >= cost:
                            persistent_stats["scrap"] -= cost
                            count = {"白":0, "藍":1, "紫":2, "金":3}[selected_mod_weapon.rarity]
                            selected_mod_weapon.affixes = random.sample(["穿透", "燃燒", "速射", "散射", "吸血", "爆擊"], count)
                            apply_weapon_stats(selected_mod_weapon); play_sound("exp")

        elif game_state == "WEAPON_STASH":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                btn_close = pygame.Rect(WIDTH//2 + 140, HEIGHT//2 + 250, 160, 40)
                if btn_close.collidepoint(event.pos): game_state = "BUNKER"
                
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                list_rect = pygame.Rect(WIDTH//2 - 320, HEIGHT//2 - 200, 640, 250)
                p_start_x, p_start_y = WIDTH//2 - 320, HEIGHT//2 + 70
                # Right click on Stash list -> to Player Inv
                if list_rect.collidepoint(event.pos):
                    rel_y = event.pos[1] - list_rect.y + arsenal_scroll_y
                    idx = int(rel_y // 50) * 2 + (0 if event.pos[0] < WIDTH//2 else 1)
                    if 0 <= idx < len(persistent_stats["weapon_stash"]):
                        wep = persistent_stats["weapon_stash"][idx]
                        if player.add_item(create_item("WEAPON", 1, wep)):
                            persistent_stats["weapon_stash"].pop(idx); sort_weapon_stash(); play_sound("exp")
                # Right click on Player Inv -> to Stash
                for i in range(24):
                    rect = pygame.Rect(p_start_x + (i%11)*58, p_start_y + (i//11)*58, 50, 50)
                    item = player.inventory[i]
                    if rect.collidepoint(event.pos) and item and item.type == "WEAPON":
                        persistent_stats["weapon_stash"].append(item.weapon_obj)
                        player.inventory[i] = None; sort_weapon_stash(); play_sound("exp")

        elif game_state == "PLAYING" and not show_inventory:
            if event.type == SPAWN_ENEMY_EVENT and not boss_army_active: 
                enemies.append(Enemy(player.level, random.random() < 0.15, player.x, player.y))
            if event.type == pygame.KEYDOWN:
                key_buffer.append(event.key)
                if len(key_buffer) > len(CHEAT_CODE): key_buffer.pop(0) 
                if key_buffer == CHEAT_CODE: 
                    player.god_mode = not player.god_mode
                    player.cheat_all_weapons = player.god_mode 
                    if player.cheat_all_weapons: player.weapons = [generate_weapon(n, "金") for n in WEAPON_TYPES]
                    else: player.weapons = [player.primary_weapon, player.secondary_weapon]
                    player.current_weapon_idx = 0
                    play_sound("levelup"); key_buffer = [] 
                    
                if event.key == pygame.K_e: player.current_weapon_idx = (player.current_weapon_idx + 1) % len(player.weapons); play_sound("exp")
                if event.key == pygame.K_r and game_mode == "CHALLENGE" and player.reload_timer <= 0 and player.ammo < (player.base_max_ammo + player.mag_size_bonus):
                    player.reload_timer = player.reload_duration
                if event.key == pygame.K_f:
                    for c in chests:
                        if c.state == "CLOSED" and math.hypot(player.x - c.x, player.y - c.y) < 70:
                            has_key = any(item.type == "KEY" for item in player.inventory if item)
                            if c.type == "LOCKED" and not has_key: pass 
                            else:
                                c.open_progress += 1
                                if c.open_progress >= 40:
                                    c.state = "OPEN"
                                    if c.type == "LOCKED":
                                        for i in range(24):
                                            if player.inventory[i] and player.inventory[i].type == "KEY":
                                                player.inventory[i].count -= 1
                                                if player.inventory[i].count <= 0: player.inventory[i] = None
                                                break
                                    open_chest(c)
                    for g in items[:]:
                        if g.item_type not in ["EXP", "MAGNET", "BOMB", "SHIELD"] and math.hypot(player.x - g.x, player.y - g.y) < 70:
                            if player.add_item(create_item(g.item_type, 1, g.weapon_obj)): items.remove(g); play_sound("exp")

        elif game_state == "PAUSED":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 10, 220, 50).collidepoint(event.pos): game_state = "PLAYING"
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 10, 220, 50).collidepoint(event.pos): reset_game("MENU", "NORMAL", keep_stash=True)
                elif pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 80, 220, 50).collidepoint(event.pos): reset_to_bunker(success=False)
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 80, 220, 50).collidepoint(event.pos): running = False

        elif game_state == "LEVEL_UP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected_upgrade_position is not None and confirm_upgrade_button.collidepoint(event.pos): apply_upgrade(current_upgrade_choices[selected_upgrade_position])
                else:
                    for i, card in enumerate(cards):
                        if i < len(current_upgrade_choices) and card.collidepoint(event.pos): selected_upgrade_position = i; break

        elif game_state == "DIED":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: reset_to_bunker(success=False)

    # ---------------- 遊戲邏輯更新 ----------------
    if game_state == "BUNKER":
        bunker_clamp = pygame.Rect(MAP_WIDTH//2 - 400, MAP_HEIGHT//2 - 300, 800, 600)
        player.update(clamp_rect=bunker_clamp)
        camera_x, camera_y = MAP_WIDTH//2 - WIDTH/2, MAP_HEIGHT//2 - HEIGHT/2

    elif game_state == "PLAYING" and not show_inventory:
        shake_x = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
        shake_y = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
        if screen_shake > 0: screen_shake -= 1

        # 負重減速
        weight = player.get_current_weight()
        speed_mult = 1.0
        if weight >= 40.0: speed_mult = 0.4
        elif weight >= 30.0: speed_mult = 0.65
        elif weight >= 20.0: speed_mult = 0.85
        player.base_speed = (7.0 + persistent_stats["speed_bonus"]) * speed_mult

        camera_x = max(0, min(MAP_WIDTH - WIDTH, player.x - WIDTH / 2)) + shake_x
        camera_y = max(0, min(MAP_HEIGHT - HEIGHT, player.y - HEIGHT / 2)) + shake_y
        
        if magnet_timer > 0: magnet_timer -= 1
        if screen_flash_timer > 0: screen_flash_timer -= 1
        
        if extraction_timer > 0: extraction_timer -= 1
        if extraction_timer <= 0:
            boss_army_active = True
            if pygame.time.get_ticks() % 15 == 0:
                e = Enemy(player.level + 15, is_elite=True, spawn_x=player.x, spawn_y=player.y)
                e.max_hp *= 4; e.hp = e.max_hp; e.speed *= 1.3; e.color = DARK_PURPLE
                e.weapon = generate_weapon("機槍", "紫")
                enemies.append(e)

        if extraction_pt:
            dist_to_ext = math.sqrt((player.x - extraction_pt.x)**2 + (player.y - extraction_pt.y)**2)
            if dist_to_ext < extraction_pt.radius:
                extract_progress += 1
                if extract_progress >= 120: play_sound("levelup"); reset_to_bunker(success=True)
            else: extract_progress = 0

        keys_pressed = pygame.key.get_pressed()
        if not keys_pressed[pygame.K_f]:
            for c in chests:
                if c.state == "CLOSED": c.open_progress = max(0, c.open_progress - 2)

        if player.level % 4 == 0 and player.level > 0 and player.level not in defeated_boss_levels and not boss_active and not boss_army_active:
            boss = Boss(random.choice(["YELLOW", "RED", "PURPLE", "CYAN"]), player.level, player.x, player.y)
            boss_active = True
            play_sound("boss_bgm", loop=-1) 

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
                if "散射" in current_wep.affixes: total_bullets += 2 
                start_angle = -(total_bullets - 1) * player.bullet_spread / 2
                
                if current_wep.bullet_type in ["cannon", "flame_grenade"]: screen_shake = 5
                elif current_wep.bullet_type == "shotgun": screen_shake = 2

                for i in range(total_bullets):
                    shot_dir = base_dir.rotate(start_angle + i * player.bullet_spread)
                    for j in range(1 + player.extra_same_path_bullets):
                        spawn_offset = shot_dir * (j * 15)
                        tx, ty = player.x + shot_dir.x * 100 + spawn_offset.x, player.y + shot_dir.y * 100 + spawn_offset.y
                        if current_wep.bullet_type == "flamethrower": tx += random.randint(-40, 40); ty += random.randint(-40, 40)
                        bullets.append(Bullet(player.rect.centerx + spawn_offset.x, player.rect.centery + spawn_offset.y, tx, ty, current_wep, player.guidance_level, player.bullet_damage_bonus))
                shoot_cooldown = max(2, current_wep.shoot_delay - player.shoot_delay_reduction)
                play_sound("shoot_normal" if current_wep.sound_name == "shoot_normal" else current_wep.sound_name)
            
        if mouse_btns[2] and player.skill_cd <= 0 and player.energy >= player.skill_cost and not player.is_dashing:
            player.energy -= player.skill_cost; player.skill_cd = player.skill_max_cd; play_sound("shoot_laser") 
            temp_wep = generate_weapon("手槍", "白"); temp_wep.bullet_type = "piercing"; temp_wep.damage = 50
            for i in range(16):
                angle = math.radians(i * (360 / 16))
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, player.rect.centerx + math.cos(angle)*100, player.rect.centery + math.sin(angle)*100, temp_wep, dmg_bonus=player.bullet_damage_bonus))

        if shoot_cooldown > 0: shoot_cooldown -= 1
        player.update()
        
        if player.drone_level > 0:
            player.drone_angle += 0.05
            if player.drone_shoot_cd > 0: player.drone_shoot_cd -= 1
            if player.drone_shoot_cd <= 0 and enemies:
                closest = min(enemies, key=lambda e: math.sqrt((e.x - player.x)**2 + (e.y - player.y)**2))
                if math.sqrt((closest.x - player.x)**2 + (closest.y - player.y)**2) < 400:
                    drone_x, drone_y = player.x + math.cos(player.drone_angle) * 55, player.y + math.sin(player.drone_angle) * 55
                    temp_wep = generate_weapon("手槍", "白"); temp_wep.bullet_type = "normal"; temp_wep.damage = 10 + player.drone_level * 8
                    bullets.append(Bullet(drone_x, drone_y, closest.x, closest.y, temp_wep))
                    player.drone_shoot_cd = max(10, 60 - player.drone_level * 10)
        
        if player.aura_level > 0:
            aura_radius, aura_damage = 95 + player.aura_level * 25, 0.02 * player.aura_level
            for e in enemies[:]:
                if math.sqrt((e.x - player.x)**2 + (e.y - player.y)**2) <= aura_radius:
                    if e.shield > 0:
                        if aura_damage > e.shield: leftover = aura_damage - e.shield; e.shield = 0; e.hp -= leftover
                        else: e.shield -= aura_damage
                    else: e.hp -= aura_damage
                    if random.random() < 0.05: particles.append(Particle(e.x, e.y, BLUE))
                    if e.hp <= 0:
                        for _ in range(8): particles.append(Particle(e.x, e.y, RED))
                        if random.random() < 0.4: items.append(DropItem(e.x, e.y, "EXP"))
                        enemies.remove(e)
            if boss_active and boss.state != "DEFEAT":
                if math.sqrt((boss.x - player.x)**2 + (boss.y - player.y)**2) <= aura_radius: boss.hp -= aura_damage
        
        if player.is_dashing: trails.append(DashTrail(player.rect.centerx, player.rect.centery, player.size))
        for t in trails[:]:
            t.update(); 
            if t.life <= 0: trails.remove(t)
            
        for b in bullets[:]:
            b.update()
            if b.explode:
                screen_shake = 8; play_sound("shoot_cannon") 
                for _ in range(30): particles.append(Particle(b.x, b.y, ORANGE))
                for e in enemies[:]:
                    if math.sqrt((e.x - b.x)**2 + (e.y - b.y)**2) < 120: 
                        if e.shield > 0:
                            if b.damage > e.shield: leftover = b.damage - e.shield; e.shield = 0; e.hp -= leftover
                            else: e.shield -= b.damage
                        else: e.hp -= b.damage
                        if e.hp <= 0: 
                            if random.random() < 0.4: items.append(DropItem(e.x, e.y, "EXP"))
                            enemies.remove(e)
                if boss_active and math.sqrt((boss.x - b.x)**2 + (boss.y - b.y)**2) < 150: boss.hp -= b.damage
                bullets.remove(b); continue
            if b.lifespan <= 0 or not pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT).colliderect(b.rect): bullets.remove(b)
            
        for eb in enemy_bullets[:]:
            eb.update(player.x, player.y) 
            if not pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT).colliderect(eb.rect): enemy_bullets.remove(eb)
                
        for dt in damage_texts[:]:
            dt.update(); 
            if dt.timer <= 0: damage_texts.remove(dt)    
                
        for e in enemies: e.update(player.x, player.y, enemies, enemy_bullets)
        for p in particles[:]:
            p.update(); 
            if p.timer <= 0: particles.remove(p)

        if boss_active: boss.update(player.x, player.y, bullets, enemies, enemy_bullets)

        for b in bullets[:]:
            hit_something = False
            for e in enemies[:]:
                if b.rect.colliderect(e.rect):
                    if b.b_type == "frost": e.frost_timer = 120 
                    if b.b_type == "cannon": 
                        push_dist = math.sqrt((e.x - player.x)**2 + (e.y - player.y)**2)
                        if push_dist > 0: e.x += ((e.x - player.x) / push_dist) * 30; e.y += ((e.y - player.y) / push_dist) * 30 
                    elif b.b_type == "flame_grenade": b.explode = True; break
                        
                    if b.is_burning: e.burn_timer = 180
                    if b.is_vampiric and random.random() < 0.05: player.hp = min(player.max_hp, player.hp + 2)
                        
                    if e.shield > 0:
                        if b.damage > e.shield: leftover = b.damage - e.shield; e.shield = 0; e.hp -= leftover
                        else: e.shield -= b.damage
                    else: e.hp -= b.damage
                        
                    damage_texts.append(DamageText(e.x, e.y - 20, b.damage, RED if b.is_crit else (YELLOW if b.damage >= 40 else WHITE), b.is_crit))
                    hit_something = True
                    for _ in range(5): particles.append(Particle(e.x, e.y, b.color))
                    play_sound("hit")
                    
                    if e.hp <= 0:
                        for _ in range(10): particles.append(Particle(e.x, e.y, RED))
                        if e.is_elite: 
                            items.append(DropItem(e.x-15, e.y, "EXP")); items.append(DropItem(e.x+15, e.y, "MED")); items.append(DropItem(e.x, e.y+15, "SHIELD"))
                            items.append(DropItem(e.x, e.y-15, "SCRAP"))
                            if random.random() < 0.3: items.append(DropItem(e.x+20, e.y, "KEY")) 
                        else:
                            rand_drop = random.random()
                            if rand_drop < 0.01: items.append(DropItem(e.x, e.y, "MAGNET"))
                            elif rand_drop < 0.02: items.append(DropItem(e.x, e.y, "BOMB"))
                            elif rand_drop < 0.15: items.append(DropItem(e.x, e.y, "SCRAP"))
                            elif rand_drop < 0.35: items.append(DropItem(e.x, e.y, "EXP"))
                            elif rand_drop < 0.40: items.append(DropItem(e.x, e.y, "MED"))
                        enemies.remove(e)
            
            if b.explode: continue 

            if boss_active and b.rect.colliderect(boss.rect):
                hit_something = True
                if boss.b_type == "YELLOW" and boss.state == "EVADE":
                    for _ in range(5): particles.append(Particle(boss.x, boss.y, GRAY))
                else:
                    if b.b_type == "frost": boss.frost_timer = 60 
                    if b.is_burning: boss.burn_timer = 180
                    if b.is_vampiric and random.random() < 0.05: player.hp = min(player.max_hp, player.hp + 2)
                    boss.hp -= b.damage
                    damage_texts.append(DamageText(boss.x, boss.y - 20, b.damage, RED if b.is_crit else WHITE, b.is_crit))
                    for _ in range(8): particles.append(Particle(boss.x, boss.y, YELLOW))
                    play_sound("hit")
                    if boss.hp <= 0:
                        boss_active = False; defeated_boss_levels.append(player.level); stop_sound("boss_bgm") 
                        for _ in range(40): items.append(DropItem(boss.x + random.randint(-60,60), boss.y + random.randint(-60,60), "EXP"))
                        for _ in range(10): items.append(DropItem(boss.x + random.randint(-40,40), boss.y + random.randint(-40,40), "SCRAP"))
                        items.append(DropItem(boss.x, boss.y, "KEY"))
                        for _ in range(50): particles.append(Particle(boss.x, boss.y, YELLOW))
                            
            if hit_something and not b.is_piercing and b in bullets: bullets.remove(b)

        def player_take_damage(dmg):
            global game_state, lost_item, player, chosen_upgrades, screen_shake
            if player.god_mode: return
            if player.invincible_timer <= 0 and not player.is_dashing:
                actual_dmg = max(1, dmg - player.damage_reduction)
                if player.shield > 0:
                    if actual_dmg > player.shield: leftover = actual_dmg - player.shield; player.shield = 0; player.hp -= leftover
                    else: player.shield -= actual_dmg
                else: player.hp -= actual_dmg
                
                player.invincible_timer = player.invincible_duration 
                screen_shake = 10 
                play_sound("hurt")
                
                if player.hp <= 0:
                    lost_item = PlayerLostItem(player.x, player.y, player.level, player.exp, list(chosen_upgrades))
                    for w in [player.primary_weapon, player.secondary_weapon]:
                        if w.rarity != "白": items.append(DropItem(player.x+random.randint(-20,20), player.y, "WEAPON", w))
                    for inv_item in player.inventory:
                        if inv_item:
                            if inv_item.type == "WEAPON": items.append(DropItem(player.x+random.randint(-20,20), player.y, "WEAPON", inv_item.weapon_obj))
                            else: items.append(DropItem(player.x+random.randint(-20,20), player.y, inv_item.type))
                    
                    player = Player() 
                    chosen_upgrades.clear()
                    game_state = "DIED"
                    play_sound("gameover"); stop_sound("boss_bgm")  

        for e in enemies[:]:
            if player.rect.colliderect(e.rect):
                if e.combat_type == "kamikaze":
                    player_take_damage(e.damage)
                    for _ in range(15): particles.append(Particle(e.x, e.y, ORANGE))
                    enemies.remove(e)
                else: player_take_damage(e.damage)
                    
        for eb in enemy_bullets[:]:
            if player.rect.colliderect(eb.rect):
                player_take_damage(25)
                if eb in enemy_bullets: enemy_bullets.remove(eb)
        if boss_active and player.rect.colliderect(boss.rect): player_take_damage(40) 

        eff_radius = 9999 if magnet_timer > 0 else player.magnet_radius
        for g in items[:]:
            g.update(player.x, player.y, eff_radius)
            if g.item_type in ["EXP", "MAGNET", "BOMB", "SHIELD"] and player.rect.colliderect(g.rect):
                items.remove(g)
                if g.item_type == "EXP":
                    player.exp += 25 * player.exp_multiplier 
                    play_sound("exp") 
                    if player.exp >= player.max_exp:
                        player.level += 1; player.exp = 0; player.max_exp = int(player.max_exp * 1.25)
                        choose_upgrade_cards(); game_state = "LEVEL_UP"; play_sound("levelup") 
                elif g.item_type == "SHIELD": player.shield = min(player.max_shield, player.shield + 20); play_sound("exp")
                elif g.item_type == "MAGNET": magnet_timer = 300; play_sound("levelup")
                elif g.item_type == "BOMB":
                    screen_flash_timer = 15
                    for e in enemies[:]:
                        for _ in range(8): particles.append(Particle(e.x, e.y, RED))
                        items.append(DropItem(e.x, e.y, "EXP"))
                    enemies.clear()
                    if boss_active and boss.state != "DEFEAT": boss.hp -= 800; particles.extend([Particle(boss.x, boss.y, ORANGE) for _ in range(15)])
                    play_sound("hit")
                    
        if lost_item and player.rect.colliderect(lost_item.rect):
            player.level = max(player.level, lost_item.level)
            player.exp += lost_item.exp
            for u in lost_item.upgrades:
                idx = next((i for i, opt in enumerate(upgrade_options) if opt["title"] == u["title"]), -1)
                if idx != -1:
                    for _ in range(u["count"]): apply_upgrade(idx, silent=True)
            lost_item = None; play_sound("levelup")

    # ---------------- 畫面渲染 ----------------
    if game_state in ["BUNKER", "SHOP", "GENERAL_STASH", "MOD_STATION", "WEAPON_STASH"]:
        screen.fill(BLACK)
        bunker_rect = pygame.Rect(MAP_WIDTH//2 - 400 - camera_x, MAP_HEIGHT//2 - 300 - camera_y, 800, 600)
        pygame.draw.rect(screen, (30, 30, 40), bunker_rect); pygame.draw.rect(screen, WHITE, bunker_rect, 5)
        
        door_rect = pygame.Rect(MAP_WIDTH//2 - 60 - camera_x, MAP_HEIGHT//2 + 200 - camera_y, 120, 60)
        pygame.draw.rect(screen, GREEN, door_rect)
        screen.blit(small_font.render("部署閘門(按E)", True, WHITE), (door_rect.x, door_rect.y - 25))
        
        shop_rect = pygame.Rect(MAP_WIDTH//2 - 350 - camera_x, MAP_HEIGHT//2 - 50 - camera_y, 100, 100)
        pygame.draw.rect(screen, BLUE, shop_rect)
        screen.blit(small_font.render("黑市(按E)", True, WHITE), (shop_rect.x, shop_rect.y - 25))

        mod_rect = pygame.Rect(MAP_WIDTH//2 - 150 - camera_x, MAP_HEIGHT//2 - 150 - camera_y, 100, 100)
        pygame.draw.rect(screen, ORANGE, mod_rect)
        screen.blit(small_font.render("改造台(按E)", True, WHITE), (mod_rect.x, mod_rect.y - 25))

        gen_rect = pygame.Rect(MAP_WIDTH//2 + 50 - camera_x, MAP_HEIGHT//2 - 150 - camera_y, 100, 100)
        pygame.draw.rect(screen, (50, 150, 200), gen_rect)
        screen.blit(small_font.render("收藏箱(按E)", True, WHITE), (gen_rect.x, gen_rect.y - 25))
        
        wep_rect = pygame.Rect(MAP_WIDTH//2 + 250 - camera_x, MAP_HEIGHT//2 - 50 - camera_y, 100, 100)
        pygame.draw.rect(screen, RED, wep_rect)
        screen.blit(small_font.render("武器箱(按E)", True, WHITE), (wep_rect.x, wep_rect.y - 25))
        
        screen.blit(large_font.render("地堡安全屋", True, YELLOW), (WIDTH//2 - 80, 50))
        screen.blit(font.render(f"擁有廢料: {persistent_stats['scrap']}", True, SCRAP_COLOR), (WIDTH//2 - 70, 100))
        
        player.draw(screen, player.weapons[player.current_weapon_idx])
        draw_upgrade_summary(screen, WIDTH - 260, 20, max_items=5)
        
        if game_state == "SHOP":
            screen.blit(dim_surface, (0, 0))
            shop_bg = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 380)
            pygame.draw.rect(screen, (20, 20, 30), shop_bg, border_radius=15); pygame.draw.rect(screen, WHITE, shop_bg, 3, border_radius=15)
            screen.blit(large_font.render("黑市升級", True, YELLOW), (WIDTH//2 - 80, HEIGHT//2 - 130))
            def draw_shop_btn(rect, text, cost):
                c = GREEN if persistent_stats["scrap"] >= cost else GRAY
                pygame.draw.rect(screen, c, rect, border_radius=8)
                screen.blit(font.render(f"{text} (消耗 {cost} 廢料)", True, BLACK), (rect.x + 10, rect.y + 8))
            draw_shop_btn(pygame.Rect(WIDTH//2 - 160, HEIGHT//2 - 60, 320, 40), f"永久最大血量+10", 50)
            draw_shop_btn(pygame.Rect(WIDTH//2 - 160, HEIGHT//2, 320, 40), f"永久武器傷害+2", 50)
            draw_shop_btn(pygame.Rect(WIDTH//2 - 160, HEIGHT//2 + 60, 320, 40), f"永久移動速度+0.2", 50)
            pygame.draw.rect(screen, RED, pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 150, 100, 40), border_radius=8)
            screen.blit(font.render("離開", True, WHITE), (WIDTH//2 - 20, HEIGHT//2 + 158))

        elif game_state == "GENERAL_STASH":
            screen.blit(dim_surface, (0, 0))
            stash_bg = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 - 280, 440, 580)
            pygame.draw.rect(screen, (20, 20, 30), stash_bg, border_radius=15); pygame.draw.rect(screen, WHITE, stash_bg, 3, border_radius=15)
            screen.blit(large_font.render("格子收藏箱", True, YELLOW), (WIDTH//2 - 90, HEIGHT//2 - 260))
            
            p_start_x, p_start_y = WIDTH//2 - 170, HEIGHT//2 + 20
            s_start_x, s_start_y = WIDTH//2 - 170, HEIGHT//2 - 220
            slot_size, margin = 50, 8
            
            # Draw Stash
            for i in range(36):
                col, row = i % 6, i // 6
                rect = pygame.Rect(s_start_x + col*(slot_size+margin), s_start_y + row*(slot_size+margin), slot_size, slot_size)
                pygame.draw.rect(screen, (30, 30, 40), rect, border_radius=5); pygame.draw.rect(screen, GRAY, rect, 1, border_radius=5)
                item = persistent_stats["general_stash"][i]
                if item and not (drag_data and drag_data["source"] == "STASH" and drag_data["idx"] == i):
                    c = HP_COLOR if item.type == "MED" else (SCRAP_COLOR if item.type == "SCRAP" else YELLOW)
                    pygame.draw.circle(screen, c, rect.center, 12)
                    screen.blit(tiny_font.render(str(item.count), True, WHITE), (rect.right - 18, rect.bottom - 18))
                    if rect.collidepoint(m_x, m_y) and drag_data is None:
                        pygame.draw.rect(screen, BLACK, (m_x + 10, m_y - 20, font.size(item.name)[0]+10, 25))
                        screen.blit(small_font.render(item.name, True, WHITE), (m_x + 15, m_y - 18))
            
            # Draw Player Inv
            draw_player_inv_grid(screen, p_start_x, p_start_y, m_x, m_y, allow_weapons=False)
            screen.blit(small_font.render("背包與收藏箱不可放置武器", True, GRAY), (WIDTH//2 - 110, HEIGHT//2 + 260))

        elif game_state == "MOD_STATION":
            screen.blit(dim_surface, (0, 0))
            mod_bg = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 250, 700, 560)
            pygame.draw.rect(screen, (20, 20, 30), mod_bg, border_radius=15); pygame.draw.rect(screen, WHITE, mod_bg, 3, border_radius=15)
            screen.blit(large_font.render("武器改造台", True, ORANGE), (WIDTH//2 - 100, HEIGHT//2 - 230))
            
            # Left: Weapons
            p_start_x, p_start_y = WIDTH//2 - 320, HEIGHT//2 + 20
            pygame.draw.rect(screen, (40,40,50), (WIDTH//2 - 320, HEIGHT//2 - 100, 140, 100), border_radius=8)
            screen.blit(small_font.render("主武器", True, WHITE), (WIDTH//2 - 275, HEIGHT//2 - 95))
            screen.blit(small_font.render(player.primary_weapon.base_name, True, get_rarity_color(player.primary_weapon.rarity)), (WIDTH//2 - 290, HEIGHT//2 - 70))
            if selected_mod_weapon == player.primary_weapon: pygame.draw.rect(screen, YELLOW, (WIDTH//2 - 320, HEIGHT//2 - 100, 140, 100), 2, border_radius=8)

            pygame.draw.rect(screen, (40,40,50), (WIDTH//2 - 160, HEIGHT//2 - 100, 140, 100), border_radius=8)
            screen.blit(small_font.render("副武器", True, WHITE), (WIDTH//2 - 115, HEIGHT//2 - 95))
            screen.blit(small_font.render(player.secondary_weapon.base_name, True, get_rarity_color(player.secondary_weapon.rarity)), (WIDTH//2 - 130, HEIGHT//2 - 70))
            if selected_mod_weapon == player.secondary_weapon: pygame.draw.rect(screen, YELLOW, (WIDTH//2 - 160, HEIGHT//2 - 100, 140, 100), 2, border_radius=8)

            draw_player_inv_grid(screen, p_start_x, p_start_y, m_x, m_y, allow_weapons=True)
            for i in range(24):
                item = player.inventory[i]
                if item and item.type == "WEAPON" and selected_mod_weapon == item.weapon_obj:
                    pygame.draw.rect(screen, YELLOW, (p_start_x + (i%6)*58, p_start_y + (i//6)*58, 50, 50), 2, border_radius=5)

            # Right: Mod Options
            pygame.draw.rect(screen, (30,30,40), (WIDTH//2 + 30, HEIGHT//2 - 150, 300, 420), border_radius=10)
            if selected_mod_weapon:
                c = get_rarity_color(selected_mod_weapon.rarity)
                screen.blit(large_font.render(selected_mod_weapon.full_name, True, c), (WIDTH//2 + 50, HEIGHT//2 - 130))
                screen.blit(font.render(f"傷害: {selected_mod_weapon.damage}", True, WHITE), (WIDTH//2 + 50, HEIGHT//2 - 80))
                aff_str = ",".join(selected_mod_weapon.affixes) if selected_mod_weapon.affixes else "無"
                screen.blit(font.render(f"詞綴: {aff_str}", True, YELLOW), (WIDTH//2 + 50, HEIGHT//2 - 40))
                
                upg_btn = pygame.Rect(WIDTH//2 + 50, HEIGHT//2 + 100, 260, 40)
                reroll_btn = pygame.Rect(WIDTH//2 + 50, HEIGHT//2 + 160, 260, 40)
                
                if selected_mod_weapon.rarity != "金":
                    cost = {"白":50, "藍":150, "紫":300}[selected_mod_weapon.rarity]
                    pygame.draw.rect(screen, GREEN if persistent_stats["scrap"]>=cost else GRAY, upg_btn, border_radius=5)
                    screen.blit(font.render(f"升級品質 ({cost} 廢料)", True, BLACK), (upg_btn.x + 20, upg_btn.y + 8))
                
                if selected_mod_weapon.rarity != "白":
                    cost = {"藍":30, "紫":80, "金":150}[selected_mod_weapon.rarity]
                    pygame.draw.rect(screen, BLUE if persistent_stats["scrap"]>=cost else GRAY, reroll_btn, border_radius=5)
                    screen.blit(font.render(f"重置詞綴 ({cost} 廢料)", True, WHITE), (reroll_btn.x + 20, reroll_btn.y + 8))
            
            btn_close = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 270, 100, 40)
            pygame.draw.rect(screen, RED, btn_close, border_radius=8); screen.blit(font.render("離開", True, WHITE), (btn_close.x + 25, btn_close.y + 8))

        elif game_state == "WEAPON_STASH":
            screen.blit(dim_surface, (0, 0))
            arsenal_bg = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 250, 700, 560)
            pygame.draw.rect(screen, (20, 20, 30), arsenal_bg, border_radius=15); pygame.draw.rect(screen, WHITE, arsenal_bg, 3, border_radius=15)
            screen.blit(large_font.render("全自動武器箱", True, RED), (WIDTH//2 - 100, HEIGHT//2 - 230))
            
            list_rect = pygame.Rect(WIDTH//2 - 320, HEIGHT//2 - 180, 640, 240)
            pygame.draw.rect(screen, BLACK, list_rect, border_radius=5)
            list_surf = pygame.Surface((list_rect.width, max(list_rect.height, (len(persistent_stats["weapon_stash"])+1)//2 * 50)))
            list_surf.fill(BLACK)
            for i, wep in enumerate(persistent_stats["weapon_stash"]):
                col, row = i % 2, i // 2
                box = pygame.Rect(col*320 + 10, row*50 + 5, 300, 42)
                pygame.draw.rect(list_surf, (40, 40, 50), box, border_radius=6); pygame.draw.rect(list_surf, GRAY, box, 1, border_radius=6)
                c = get_rarity_color(wep.rarity)
                list_surf.blit(font.render(wep.full_name, True, c), (box.x + 5, box.y + 8))
                aff_txt = ",".join(wep.affixes) if wep.affixes else "無"
                list_surf.blit(tiny_font.render(f"傷:{wep.damage} [{aff_txt}]", True, WHITE), (box.x + 160, box.y + 14))
                if box.collidepoint(m_x - list_rect.x, m_y - list_rect.y + arsenal_scroll_y) and list_rect.collidepoint(m_pos):
                    pygame.draw.rect(list_surf, YELLOW, box, 2, border_radius=6)

            screen.blit(list_surf, list_rect.topleft, pygame.Rect(0, arsenal_scroll_y, list_rect.width, list_rect.height))
            pygame.draw.rect(screen, WHITE, list_rect, 2, border_radius=5)

            # Player Inv Weapons
            p_start_x, p_start_y = WIDTH//2 - 320, HEIGHT//2 + 70
            screen.blit(small_font.render("右鍵點擊列表中的武器移入背包，右鍵點擊背包中的武器存入武器箱", True, GRAY), (WIDTH//2 - 250, HEIGHT//2 + 250))
            for i in range(24):
                rect = pygame.Rect(p_start_x + (i%11)*58, p_start_y + (i//11)*58, 50, 50)
                pygame.draw.rect(screen, (40, 40, 50), rect, border_radius=5); pygame.draw.rect(screen, GRAY, rect, 1, border_radius=5)
                item = player.inventory[i]
                if item:
                    if item.type == "WEAPON":
                        pygame.draw.circle(screen, get_rarity_color(item.weapon_obj.rarity), rect.center, 12)
                        if rect.collidepoint(m_x, m_y):
                            pygame.draw.rect(screen, BLACK, (m_x + 10, m_y - 20, font.size(item.weapon_obj.full_name)[0]+10, 25))
                            screen.blit(small_font.render(item.weapon_obj.full_name, True, WHITE), (m_x + 15, m_y - 18))
                    else: pygame.draw.circle(screen, (50,50,50), rect.center, 12)

            btn_close = pygame.Rect(WIDTH//2 - 80, HEIGHT//2 + 280, 160, 40)
            pygame.draw.rect(screen, RED, btn_close, border_radius=8); screen.blit(font.render("離開", True, WHITE), (btn_close.x + 55, btn_close.y + 8))

        if drag_data:
            c = WHITE
            if drag_data["item"].type == "WEAPON": c = get_rarity_color(drag_data["item"].weapon_obj.rarity)
            elif drag_data["item"].type == "MED": c = HP_COLOR
            elif drag_data["item"].type == "SCRAP": c = SCRAP_COLOR
            elif drag_data["item"].type == "KEY": c = YELLOW
            pygame.draw.circle(screen, c, (m_x, m_y), 15)

    elif game_state in ["PLAYING", "PAUSED", "LEVEL_UP", "DIED"]:
        if images.get("bg"):
            bg_w, bg_h = WIDTH, HEIGHT
            for x in range(0, MAP_WIDTH, bg_w):
                for y in range(0, MAP_HEIGHT, bg_h):
                    draw_x = x - int(camera_x); draw_y = y - int(camera_y)
                    if draw_x + bg_w > 0 and draw_x < WIDTH and draw_y + bg_h > 0 and draw_y < HEIGHT: screen.blit(images["bg"], (draw_x, draw_y))
        else: screen.fill(BLACK)
        
        pygame.draw.rect(screen, RED, (-int(camera_x), -int(camera_y), MAP_WIDTH, MAP_HEIGHT), 5)
        
        if extraction_pt: extraction_pt.draw(screen)
        if lost_item: lost_item.draw(screen)
        for c in chests: c.draw(screen)
        for it in items: it.draw(screen)
        for p in particles: p.draw(screen)
        for b in bullets: b.draw(screen)
        for eb in enemy_bullets: eb.draw(screen) 
        for e in enemies: e.draw(screen)
        for t in trails: t.draw(screen)
        for dt in damage_texts: dt.draw(screen)
        if boss_active: boss.draw(screen); draw_boss_direction_arrow(screen, boss, camera_x, camera_y)
            
        if game_state != "DIED": player.draw(screen, player.weapons[player.current_weapon_idx] if game_state == "PLAYING" else None)

        if screen_flash_timer > 0:
            flash_surface = pygame.Surface((WIDTH, HEIGHT)); flash_surface.fill(WHITE)
            flash_surface.set_alpha(int((screen_flash_timer / 15) * 255)); screen.blit(flash_surface, (0, 0))
            
        if boss_army_active and (pygame.time.get_ticks() // 300) % 2 == 0:
            alarm = pygame.Surface((WIDTH, HEIGHT)); alarm.fill(RED); alarm.set_alpha(80); screen.blit(alarm, (0, 0))
        
        if game_state == "PLAYING" and not show_inventory:
            for c in chests:
                if c.state == "CLOSED" and math.hypot(player.x - c.x, player.y - c.y) < 70:
                    has_key = any(item.type == "KEY" for item in player.inventory if item)
                    t = "[F] 開啟寶箱" if c.type == "NORMAL" else ("[F] 消耗鑰匙" if has_key else "需要金鑰匙")
                    t_c = WHITE if c.type == "NORMAL" or has_key else RED
                    screen.blit(small_font.render(t, True, t_c), (c.x - camera_x - 30, c.y - camera_y - 45))
            for g in items:
                if g.item_type not in ["EXP", "MAGNET", "BOMB", "SHIELD"] and math.hypot(player.x - g.x, player.y - g.y) < 70:
                    screen.blit(small_font.render("[F] 撿取", True, WHITE), (g.x - camera_x - 30, g.y - camera_y - 30))
        
        draw_minimap(screen)
        
        # HUD 資訊
        pygame.draw.rect(screen, GRAY, (20, 20, 250, 15)); pygame.draw.rect(screen, BLUE, (20, 20, 250 * (player.exp / player.max_exp), 15))
        screen.blit(font.render("等級: " + str(player.level), True, WHITE), (280, 15))

        pygame.draw.rect(screen, GRAY, (20, 45, 200, 15)); pygame.draw.rect(screen, GREEN if player.hp > 30 else RED, (20, 45, 200 * (max(0, player.hp) / player.max_hp), 15))
        screen.blit(font.render("血量", True, WHITE), (230, 40))

        pygame.draw.rect(screen, GRAY, (20, 70, 200, 15)); pygame.draw.rect(screen, (0, 150, 255), (20, 70, 200 * (max(0, player.shield) / player.max_shield), 15))
        screen.blit(font.render("護盾", True, WHITE), (230, 65))

        pygame.draw.rect(screen, GRAY, (20, 95, 150, 10)); pygame.draw.rect(screen, ORANGE, (20, 95, 150 * (player.stamina / player.max_stamina), 10))
        screen.blit(font.render("體力 (Q鍵)", True, WHITE), (180, 87)) 
        
        pygame.draw.rect(screen, GRAY, (20, 115, 150, 10)); pygame.draw.rect(screen, CYAN, (20, 115, 150 * (player.energy / player.max_energy), 10))
        screen.blit(font.render("能量", True, WHITE), (180, 107))

        weight = player.get_current_weight()
        w_color = GREEN if weight < 20.0 else (YELLOW if weight < 30.0 else RED)
        speed_mult = 1.0
        if weight >= 40.0: speed_mult = 0.4
        elif weight >= 30.0: speed_mult = 0.65
        elif weight >= 20.0: speed_mult = 0.85
        speed_str = f"負重: {weight:.1f}/40.0kg (速度 x{speed_mult})"
        screen.blit(small_font.render(speed_str, True, w_color), (20, 130))

        if player.cheat_all_weapons:
            active_wep = player.weapons[player.current_weapon_idx]
            weapon_str = f"【密技】全解鎖: {active_wep.full_name} (按E切換)"
            w_c = YELLOW
        else:
            w1 = player.weapons[0]; w2 = player.weapons[1]; active_w = player.current_weapon_idx
            w1_t = f"主: {w1.full_name}" + (" <" if active_w==0 else "")
            w2_t = f"副: {w2.full_name}" + (" <" if active_w==1 else "")
            weapon_str = f"{w1_t}  |  {w2_t}"
            w_c = WHITE
            
        screen.blit(small_font.render(weapon_str, True, w_c), (20, 155))
        has_key = sum(i.count for i in player.inventory if i and i.type == "KEY")
        screen.blit(font.render(f"本局廢料: {player.scrap} | 金鑰匙: {has_key}", True, YELLOW), (20, 180))

        if player.skill_cd > 0: skill_txt = font.render(f"技能冷卻: {round(player.skill_cd / 60, 1)} 秒", True, GRAY)
        elif player.energy < player.skill_cost: skill_txt = font.render("能量不足", True, RED)
        else: skill_txt = font.render("技能就緒(右鍵)", True, GREEN)
        screen.blit(skill_txt, (20, HEIGHT - 40))

        if game_mode == "CHALLENGE":
            ammo_txt = font.render(f"彈藥: {player.ammo} / {player.base_max_ammo + player.mag_size_bonus}", True, WHITE if player.ammo > 0 else RED)
            screen.blit(ammo_txt, (20, 210))
            if player.reload_timer > 0:
                pygame.draw.rect(screen, GRAY, (20, 240, 150, 10)); pygame.draw.rect(screen, YELLOW, (20, 240, 150 * (1 - player.reload_timer / player.reload_duration), 10))
                screen.blit(small_font.render("換彈中...", True, YELLOW), (180, 235))

        if extraction_pt:
            time_sec = extraction_timer // FPS
            mins, secs = time_sec // 60, time_sec % 60
            color = WHITE if time_sec > 30 else RED
            screen.blit(large_font.render(f"撤離倒數: {mins:02d}:{secs:02d}", True, color), (WIDTH//2 - 120, 20))
            if extract_progress > 0:
                pygame.draw.rect(screen, GRAY, (WIDTH//2 - 100, 110, 200, 15))
                pygame.draw.rect(screen, GREEN, (WIDTH//2 - 100, 110, 200 * (extract_progress / 120), 15))
            if boss_army_active: screen.blit(large_font.render("警告：超時！狂暴大軍來襲！", True, RED), (WIDTH//2 - 220, 140))

        if boss_active:
            bar_w = WIDTH - 100
            pygame.draw.rect(screen, GRAY, (50, HEIGHT - 80, bar_w, 20))
            boss_bar_color = RED if boss.b_type == "RED" else PURPLE if boss.b_type == "PURPLE" else CYAN if boss.b_type == "CYAN" else YELLOW
            pygame.draw.rect(screen, boss_bar_color, (50, HEIGHT - 80, bar_w * (max(0, boss.hp) / boss.max_hp), 20))
            boss_name = "幾何守衛" if boss.b_type == "YELLOW" else "鮮血狂戰士" if boss.b_type == "RED" else "虛空召喚師" if boss.b_type == "PURPLE" else "天網追蹤者"
            screen.blit(font.render(f"警告：極度危險實體 - 【{boss_name}】", True, WHITE), (WIDTH//2 - 180, HEIGHT - 110))

        if player.god_mode: screen.blit(font.render("【無敵模式啟用】", True, YELLOW), (WIDTH//2 - 80, 20))
        draw_upgrade_summary(screen, WIDTH - 260, HEIGHT - 300, max_items=5)
        
        if show_inventory:
            screen.blit(dim_surface, (0, 0))
            inv_rect = pygame.Rect(WIDTH//2 - 190, HEIGHT//2 - 100, 380, 300)
            pygame.draw.rect(screen, (20, 20, 30), inv_rect, border_radius=10); pygame.draw.rect(screen, WHITE, inv_rect, 2, border_radius=10)
            screen.blit(large_font.render("背包 (TAB關閉)", True, YELLOW), (WIDTH//2 - 120, HEIGHT//2 - 80))
            draw_player_inv_grid(screen, WIDTH//2 - 170, HEIGHT//2 - 50, m_x, m_y, allow_weapons=True)
            if drag_data:
                c = WHITE
                if drag_data["item"].type == "WEAPON": c = get_rarity_color(drag_data["item"].weapon_obj.rarity)
                elif drag_data["item"].type == "MED": c = HP_COLOR
                elif drag_data["item"].type == "SCRAP": c = SCRAP_COLOR
                elif drag_data["item"].type == "KEY": c = YELLOW
                pygame.draw.circle(screen, c, (m_x, m_y), 15)
            screen.blit(small_font.render("左鍵拖曳 / 右鍵裝備或使用 / 拖出框外丟棄", True, GRAY), (WIDTH//2 - 170, HEIGHT//2 + 210))

    if game_state == "MENU":
        screen.fill(BLACK)
        for i in range(100):
            x, y = (i * 37) % WIDTH, (i * 23) % HEIGHT
            brightness = 100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)
        
        glow_color = (0, 100, 255, 50)
        glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        title = large_font.render("驅 魔 人 : 撤 離 行 動 v2.7", True, BLUE)
        glow_surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -3), (0, 3), (-3, 0), (3, 0)]:
            glow_copy = glow_surface.copy(); glow_copy.fill(glow_color, special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(glow_copy, offset)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        screen.blit(font.render("塔科夫究極地堡版 (改造台 + 收藏箱)", True, WHITE), (WIDTH//2 - 200, HEIGHT//2 - 50))

        start_hover = start_button.collidepoint(m_pos)
        if start_hover:
            scale = 1.05
            scaled_btn = pygame.Rect(start_button.centerx - start_button.width * scale // 2, start_button.centery - start_button.height * scale // 2, start_button.width * scale, start_button.height * scale)
            pygame.draw.rect(screen, (100, 200, 100), scaled_btn, border_radius=12); pygame.draw.rect(screen, YELLOW, scaled_btn, 4, border_radius=12)
        else:
            pygame.draw.rect(screen, (50, 150, 50), start_button, border_radius=10); pygame.draw.rect(screen, WHITE, start_button, 3, border_radius=10)
        screen.blit(font.render("部署行動", True, WHITE), (start_button.centerx - 40, start_button.centery - 12))

        changelog_color = BLUE if changelog_button.collidepoint(m_pos) else (50, 100, 150)
        pygame.draw.rect(screen, changelog_color, changelog_button, border_radius=10); pygame.draw.rect(screen, WHITE, changelog_button, 3, border_radius=10)
        screen.blit(font.render("更新日誌", True, WHITE), (changelog_button.centerx - 40, changelog_button.centery - 12))

        exit_color = RED if exit_button.collidepoint(m_pos) else (150, 50, 50)
        pygame.draw.rect(screen, exit_color, exit_button, border_radius=10); pygame.draw.rect(screen, WHITE, exit_button, 3, border_radius=10)
        screen.blit(font.render("退出遊戲", True, WHITE), (exit_button.centerx - 40, exit_button.centery - 12))

        controls = ["移動: WASD", "射擊: 左鍵  |  技能: 右鍵  |  衝刺: Q", "互動: E  |  替換武器/開箱: F", "切換武器: E  |  背包: TAB  |  補血: H"]
        for i, c in enumerate(controls): screen.blit(small_font.render(c, True, GRAY), (WIDTH//2 - font.size(c)[0]//2, HEIGHT//2 + 235 + i * 20))
        
        if show_changelog: draw_changelog_popup(screen)

    elif game_state == "DIFFICULTY":
        screen.fill(BLACK)
        screen.blit(large_font.render("選擇難易度", True, YELLOW), (WIDTH//2 - 100, HEIGHT//2 - 200))
        n_hover, c_hover = normal_button.collidepoint(m_pos), challenge_button.collidepoint(m_pos)
        pygame.draw.rect(screen, (55, 125, 185) if n_hover else (30, 70, 115), normal_button, border_radius=10)
        pygame.draw.rect(screen, YELLOW if n_hover else WHITE, normal_button, 4 if n_hover else 3, border_radius=10)
        pygame.draw.rect(screen, (190, 55, 70) if c_hover else (115, 35, 50), challenge_button, border_radius=10)
        pygame.draw.rect(screen, YELLOW if c_hover else WHITE, challenge_button, 4 if c_hover else 3, border_radius=10)

        screen.blit(large_font.render("普通", True, WHITE), (normal_button.centerx - 40, normal_button.y + 28))
        screen.blit(small_font.render("標準敵人強度與數量", True, WHITE), (normal_button.centerx - 80, normal_button.y + 88))
        for i, line in enumerate(["基礎倍率：1.0x", "無需換彈", "輕鬆農怪"]): screen.blit(small_font.render(line, True, (210, 225, 240)), (normal_button.x + 35, normal_button.y + 132 + i * 28))

        screen.blit(large_font.render("挑戰", True, WHITE), (challenge_button.centerx - 40, challenge_button.y + 28))
        screen.blit(small_font.render("敵人 1.75 倍，速度加成", True, WHITE), (challenge_button.centerx - 90, challenge_button.y + 88))
        for i, line in enumerate(["難度倍率：1.75x", "啟動換彈懲罰機制", "解鎖專屬彈匣卡牌"]): screen.blit(small_font.render(line, True, (255, 220, 220)), (challenge_button.x + 35, challenge_button.y + 132 + i * 28))

        b_hover = difficulty_back_button.collidepoint(m_pos)
        pygame.draw.rect(screen, BLUE if b_hover else (50, 100, 150), difficulty_back_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, difficulty_back_button, 3, border_radius=10)
        screen.blit(font.render("返回", True, WHITE), (difficulty_back_button.centerx - 20, difficulty_back_button.centery - 12))

    elif game_state == "PAUSED":
        screen.blit(dim_surface, (0, 0))
        screen.blit(large_font.render("暫停中", True, YELLOW), (WIDTH//2 - 60, HEIGHT//2 - 100))
        def draw_pause_btn(btn, text, color, hover_color):
            c = hover_color if btn.collidepoint(m_pos) else color
            pygame.draw.rect(screen, c, btn, border_radius=10); pygame.draw.rect(screen, WHITE, btn, 3, border_radius=10)
            screen.blit(font.render(text, True, WHITE), (btn.centerx - font.size(text)[0]//2, btn.centery - 12))

        draw_pause_btn(pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 10, 220, 50), "繼續遊戲", (50, 100, 150), BLUE)
        draw_pause_btn(pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 10, 220, 50), "回到選單", (50, 100, 150), BLUE)
        draw_pause_btn(pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 80, 220, 50), "放棄重製(回地堡)", (50, 150, 50), GREEN)
        draw_pause_btn(pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 80, 220, 50), "退出遊戲", (150, 50, 50), RED)
        draw_pause_upgrade_log(screen)

    elif game_state == "LEVEL_UP":
        screen.blit(dim_surface, (0, 0)) 
        screen.blit(large_font.render("升級！選擇一項強化", True, YELLOW), (WIDTH//2 - 180, 100))
        for i, card in enumerate(cards):
            if i >= len(current_upgrade_choices): continue
            upgrade = upgrade_options[current_upgrade_choices[i]]
            is_selected = (selected_upgrade_position == i)
            base_color = CARD_TYPE_COLORS.get(upgrade.get("type"), CARD_COLOR)
            hover_color = tuple(min(255, c + 35) for c in base_color)
            sel_color = tuple(min(255, c + 65) for c in base_color)
            color = sel_color if is_selected else hover_color if card.collidepoint(m_pos) else base_color
            
            pygame.draw.rect(screen, color, card, border_radius=10); pygame.draw.rect(screen, YELLOW if is_selected else WHITE, card, 6 if is_selected else 3, border_radius=10) 
            
            type_label = CARD_TYPE_LABELS.get(upgrade.get("type"), "")
            if type_label:
                lbl_bg = pygame.Rect(card.centerx - 42, card.y + 18, 84, 28)
                pygame.draw.rect(screen, (20, 20, 28), lbl_bg, border_radius=8); pygame.draw.rect(screen, WHITE, lbl_bg, 1, border_radius=8)
                screen.blit(small_font.render(type_label, True, WHITE), (lbl_bg.centerx - 18, lbl_bg.centery - 10))
            
            screen.blit(font.render(upgrade["title"], True, WHITE), (card.centerx - font.size(upgrade["title"])[0]//2, card.y + 65))
            screen.blit(font.render(upgrade["desc"][0], True, YELLOW), (card.centerx - font.size(upgrade["desc"][0])[0]//2, card.y + 125))
            screen.blit(font.render(upgrade["desc"][1], True, YELLOW), (card.centerx - font.size(upgrade["desc"][1])[0]//2, card.y + 165))
            
        ready = (selected_upgrade_position is not None)
        c_color = GREEN if ready and confirm_upgrade_button.collidepoint(m_pos) else (50, 150, 50) if ready else GRAY
        pygame.draw.rect(screen, c_color, confirm_upgrade_button, border_radius=10); pygame.draw.rect(screen, WHITE, confirm_upgrade_button, 3, border_radius=10)
        screen.blit(font.render("確認選擇", True, WHITE), (confirm_upgrade_button.centerx - 40, confirm_upgrade_button.centery - 12))

    elif game_state == "DIED":
        screen.blit(dim_surface, (0, 0))
        screen.blit(large_font.render("你 已 陣 亡", True, RED), (WIDTH//2 - 100, HEIGHT//2 - 100))
        screen.blit(font.render("背包物資與手上的神裝已掉落。", True, WHITE), (WIDTH//2 - 160, HEIGHT//2 - 20))
        screen.blit(font.render("按 [R] 鍵於地堡重生，去把裝備撿回來！", True, YELLOW), (WIDTH//2 - 200, HEIGHT//2 + 20))

    pygame.display.flip()
    clock.tick(FPS)

>>>>>>> 5fe3c3b9a6cb6e15508d0cc26521ee2ec490b8fd
pygame.quit()
