import pygame
import random
import math
import os
import ctypes

#--- 遊戲初始化與音效設定 ---
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1920, 1080
MAP_WIDTH, MAP_HEIGHT = 4200, 2600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space War")
clock = pygame.time.Clock()
FPS = 80
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
CARD_TYPE_COLORS = {
    "attack": (120, 35, 45),
    "support": (35, 75, 130),
    "life": (35, 110, 65),
}
CARD_TYPE_LABELS = {
    "attack": "攻擊",
    "support": "支援",
    "life": "生命",
}
NORMAL_MODE = "NORMAL"
CHALLENGE_MODE = "CHALLENGE"
CHALLENGE_ENEMY_MULTIPLIER = 1.75
CHALLENGE_ENEMY_SPEED_MULTIPLIER = 1.25
NORMAL_SPAWN_INTERVAL = 420
CHALLENGE_SPAWN_INTERVAL = 600


# 優先尋找微軟正黑體，若無則找蘋方體(Mac)或黑體
CHINESE_FONTS = "microsoftjhenghei,pingfangtc,stheiti,simhei"
font = pygame.font.SysFont(CHINESE_FONTS, 28)       # 一般大小字體
large_font = pygame.font.SysFont(CHINESE_FONTS, 48) # 大字體標題
small_font = pygame.font.SysFont(CHINESE_FONTS, 22) # 小字體 UI
tiny_font = pygame.font.SysFont(CHINESE_FONTS, 18) # 暫停紀錄說明

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
        self.extra_same_path_bullets = 0
        self.bullet_spread = 15
        self.bullet_damage_bonus = 0
        self.guidance_level = 0
        self.aura_level = 0
        self.regen_level = 0
        self.regen_progress = 0
        self.exp_multiplier = 1.0
        self.pos = pygame.math.Vector2(MAP_WIDTH / 2, MAP_HEIGHT / 2)
        self.size = 30
        self.base_speed = 5
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        
        self.exp, self.level, self.max_exp = 0, 1, 100
        self.magnet_radius, self.shoot_delay = 60, 8
        self.is_aiming = False
        
        self.max_hp, self.hp = 100, 100
        self.max_shield = int(self.max_hp * 0.2)
        self.shield = self.max_shield
        self.shield_regen_rate = 0.18
        self.shield_regen_delay = 150
        self.shield_regen_timer = 0
        self.invincible_timer = 0
        self.invincible_duration = 120
        self.damage_reduction = 0
        
        self.max_stamina, self.stamina = 100, 100
        self.dash_cost, self.stamina_regen = 35, 0.5   

        self.pistol_mag_size = 45
        self.sniper_mag_size = 7
        self.pistol_ammo = self.pistol_mag_size
        self.sniper_ammo = self.sniper_mag_size
        self.reload_timer = 0
        self.reload_duration = 90
        self.reloading_weapon = None
        
        self.is_dashing = False
        self.dash_speed, self.dash_duration = 22, 8
        self.dash_timer = 0
        self.dash_direction = pygame.math.Vector2(0, 0)

    def update(self):
        mouse_btns = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()
        self.is_aiming = mouse_btns[2] 
        move_vector = pygame.math.Vector2(0, 0)

        if self.reload_timer > 0:
            self.reload_timer -= 1
            if self.reload_timer <= 0:
                if self.reloading_weapon == "sniper":
                    self.sniper_ammo = self.sniper_mag_size
                else:
                    self.pistol_ammo = self.pistol_mag_size
                self.reloading_weapon = None
        
        if keys[pygame.K_w]: move_vector.y -= 1
        if keys[pygame.K_s]: move_vector.y += 1
        if keys[pygame.K_a]: move_vector.x -= 1
        if keys[pygame.K_d]: move_vector.x += 1
        if move_vector.length() > 0: move_vector.normalize_ip()

        if self.invincible_timer > 0: self.invincible_timer -= 1
        if self.shield_regen_timer > 0:
            self.shield_regen_timer -= 1
        elif self.shield < self.max_shield:
            self.shield = min(self.max_shield, self.shield + self.shield_regen_rate)
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
                self.dash_direction = mouse_pos - pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
                if self.dash_direction.length() > 0: self.dash_direction.normalize_ip()

        if self.is_dashing:
            self.pos += self.dash_direction * self.dash_speed
            self.dash_timer -= 1
            if self.dash_timer <= 0: self.is_dashing = False
        else:
            current_speed = self.base_speed / 2 if self.is_aiming else self.base_speed
            self.pos += move_vector * current_speed
            
        half = self.size / 2
        self.pos.x = max(half, min(MAP_WIDTH - half, self.pos.x))
        self.pos.y = max(half, min(MAP_HEIGHT - half, self.pos.y))
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def current_weapon(self):
        return "sniper" if self.is_aiming else "pistol"

    def can_fire_current_weapon(self):
        if game_mode != CHALLENGE_MODE:
            return True
        if self.reload_timer > 0:
            return False
        if self.current_weapon() == "sniper":
            return self.sniper_ammo > 0
        return self.pistol_ammo > 0

    def consume_current_ammo(self):
        if game_mode != CHALLENGE_MODE:
            return
        if self.current_weapon() == "sniper":
            self.sniper_ammo = max(0, self.sniper_ammo - 1)
            if self.sniper_ammo <= 0:
                self.start_reload("sniper")
        else:
            self.pistol_ammo = max(0, self.pistol_ammo - 1)
            if self.pistol_ammo <= 0:
                self.start_reload("pistol")

    def start_reload(self, weapon=None):
        if game_mode != CHALLENGE_MODE or self.reload_timer > 0:
            return
        self.reloading_weapon = weapon or self.current_weapon()
        self.reload_timer = self.reload_duration

    def draw(self, surface, camera):
        draw_rect = self.rect.move(-camera.x, -camera.y)
        mouse_world = pygame.math.Vector2(pygame.mouse.get_pos()) + camera
        aim_dir = mouse_world - self.pos
        if aim_dir.length_squared() == 0:
            aim_dir = pygame.math.Vector2(1, 0)
        else:
            aim_dir.normalize_ip()
        gun_side = aim_dir.rotate(90)

        def to_screen(point):
            return (round(point.x - camera.x), round(point.y - camera.y))

        def draw_weapon_poly(points, color, border=BLACK):
            screen_points = [to_screen(point) for point in points]
            pygame.draw.polygon(surface, border, screen_points)
            inner_points = [to_screen(self.pos + (point - self.pos) * 0.94) for point in points]
            pygame.draw.polygon(surface, color, inner_points)

        accent = RED if self.is_aiming else YELLOW
        metal = (185, 195, 205)
        dark_metal = (55, 62, 72)
        body_start = self.pos + aim_dir * 4
        body_end = self.pos + aim_dir * (42 if self.is_aiming else 34)
        body_half = 8 if self.is_aiming else 9
        draw_weapon_poly([
            body_start + gun_side * body_half,
            body_end + gun_side * (body_half - 2),
            body_end - gun_side * (body_half - 2),
            body_start - gun_side * body_half,
        ], dark_metal)

        barrel_start = body_end
        barrel_end = self.pos + aim_dir * (78 if self.is_aiming else 58)
        pygame.draw.line(surface, BLACK, to_screen(barrel_start), to_screen(barrel_end), 9 if self.is_aiming else 8)
        pygame.draw.line(surface, metal, to_screen(barrel_start), to_screen(barrel_end), 5 if self.is_aiming else 4)
        muzzle = barrel_end + aim_dir * 6
        pygame.draw.line(surface, accent, to_screen(barrel_end - gun_side * 5), to_screen(muzzle - gun_side * 5), 3)
        pygame.draw.line(surface, accent, to_screen(barrel_end + gun_side * 5), to_screen(muzzle + gun_side * 5), 3)

        stock_base = self.pos - aim_dir * 8
        draw_weapon_poly([
            stock_base + gun_side * 5,
            stock_base - gun_side * 5,
            stock_base - aim_dir * 24 - gun_side * 7,
            stock_base - aim_dir * 24 + gun_side * 7,
        ], (95, 105, 118))

        grip_top = self.pos + aim_dir * 12 - gun_side * 6
        draw_weapon_poly([
            grip_top + gun_side * 3,
            grip_top - gun_side * 8,
            grip_top - aim_dir * 4 - gun_side * 24,
            grip_top - aim_dir * 11 - gun_side * 21,
        ], (210, 215, 220))

        if self.is_aiming:
            scope_start = self.pos + aim_dir * 20 + gun_side * 12
            scope_end = self.pos + aim_dir * 46 + gun_side * 12
            pygame.draw.line(surface, BLACK, to_screen(scope_start), to_screen(scope_end), 9)
            pygame.draw.line(surface, WHITE, to_screen(scope_start), to_screen(scope_end), 5)
            pygame.draw.circle(surface, accent, to_screen(scope_end), 6, 2)
            pygame.draw.circle(surface, WHITE, to_screen(scope_start), 5, 2)
        else:
            foregrip = self.pos + aim_dir * 36
            pygame.draw.line(surface, BLACK, to_screen(foregrip), to_screen(foregrip - gun_side * 19), 7)
            pygame.draw.line(surface, (210, 215, 220), to_screen(foregrip), to_screen(foregrip - gun_side * 16), 4)
            sight_front = self.pos + aim_dir * 52
            sight_rear = self.pos + aim_dir * 18
            pygame.draw.line(surface, accent, to_screen(sight_front - gun_side * 5), to_screen(sight_front + gun_side * 5), 2)
            pygame.draw.line(surface, accent, to_screen(sight_rear - gun_side * 4), to_screen(sight_rear + gun_side * 4), 2)

        if self.shield > 0:
            shield_ratio = self.shield / self.max_shield
            shield_radius = self.size // 2 + 8
            shield_color = (70, 180, 255) if shield_ratio > 0.35 else (255, 210, 70)
            pygame.draw.circle(surface, shield_color, draw_rect.center, shield_radius, 2)
        if self.aura_level > 0:
            aura_radius = 95 + self.aura_level * 25
            pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10)
            pygame.draw.circle(surface, (0, 180, 255), draw_rect.center, aura_radius + pulse, 2)
            pygame.draw.circle(surface, (0, 90, 180), draw_rect.center, max(12, aura_radius - 18), 1)
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0: pass
        else:
            pygame.draw.rect(surface, BLUE, draw_rect)
            if self.stamina < self.dash_cost: pygame.draw.rect(surface, GRAY, draw_rect, 3)
            if self.is_aiming and not self.is_dashing:
                pygame.draw.line(surface, RED, draw_rect.center, pygame.mouse.get_pos(), 2)

class DashTrail:
    def __init__(self, x, y, size):
        self.pos = pygame.math.Vector2(x, y); self.size, self.life = size, 12
    def update(self): self.life -= 1; self.size -= 1.5
    def draw(self, surface, camera):
        if self.life > 0 and self.size > 0:
            rect = pygame.Rect(0, 0, self.size, self.size)
            rect.center = (round(self.pos.x - camera.x), round(self.pos.y - camera.y))
            pygame.draw.rect(surface, BLUE, rect, max(1, int(self.life / 3)))

class Bullet:
    def __init__(self, x, y, target_x, target_y, is_piercing=False, guidance_level=0):
        self.pos = pygame.math.Vector2(x, y)
        self.is_piercing = is_piercing
        self.guidance_level = guidance_level
        if self.is_piercing: self.radius, self.speed, self.color = 15, 25, PURPLE
        else: self.radius, self.speed, self.color = 6, 18, YELLOW
        target = pygame.math.Vector2(target_x, target_y)
        self.direction = target - self.pos
        if self.direction.length() > 0: self.direction.normalize_ip()
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
    def update(self):
        if self.guidance_level > 0:
            targets = enemies[:]
            if boss_active and boss and boss.state != "DEFEAT":
                targets.append(boss)
            if targets:
                guide_range = 220 + self.guidance_level * 45
                nearby_targets = [t for t in targets if self.pos.distance_to(t.pos) <= guide_range]
                if nearby_targets:
                    target = min(nearby_targets, key=lambda t: self.pos.distance_to(t.pos))
                    target_dir = target.pos - self.pos
                    if target_dir.length() > 0:
                        target_dir.normalize_ip()
                        turn_speed = min(0.08, 0.025 + self.guidance_level * 0.012)
                        self.direction += target_dir * turn_speed
                        self.direction.normalize_ip()
        self.pos += self.direction * self.speed
        self.rect.center = (round(self.pos.x), round(self.pos.y))
    def draw(self, surface, camera): pygame.draw.circle(surface, self.color, (round(self.pos.x - camera.x), round(self.pos.y - camera.y)), self.radius)

class EnemyBullet:
    def __init__(self, x, y, dir_x, dir_y, color=ORANGE, core_color=WHITE, style="round"):
        self.pos = pygame.math.Vector2(x, y)
        self.direction = pygame.math.Vector2(dir_x, dir_y)
        if self.direction.length() > 0: self.direction.normalize_ip()
        self.radius, self.speed, self.color = 8, 7, ORANGE
        self.color = color
        self.core_color = core_color
        self.style = style
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
    def update(self):
        self.pos += self.direction * self.speed
        self.rect.center = (round(self.pos.x), round(self.pos.y))
    def draw(self, surface, camera):
        center = (round(self.pos.x - camera.x), round(self.pos.y - camera.y))
        pygame.draw.circle(surface, BLACK, center, self.radius + 4)
        pygame.draw.circle(surface, self.color, center, self.radius + 2)
        if self.style == "diamond":
            pts = [
                (center[0], center[1] - self.radius - 1),
                (center[0] + self.radius + 1, center[1]),
                (center[0], center[1] + self.radius + 1),
                (center[0] - self.radius - 1, center[1])
            ]
            pygame.draw.polygon(surface, self.core_color, pts)
        elif self.style == "slash":
            side = self.direction.rotate(90)
            front = pygame.math.Vector2(center) + self.direction * (self.radius + 4)
            back = pygame.math.Vector2(center) - self.direction * (self.radius + 4)
            left = pygame.math.Vector2(center) + side * 4
            right = pygame.math.Vector2(center) - side * 4
            pts = [(int(front.x), int(front.y)), (int(left.x), int(left.y)), (int(back.x), int(back.y)), (int(right.x), int(right.y))]
            pygame.draw.polygon(surface, self.core_color, pts)
        else:
            pygame.draw.circle(surface, self.core_color, center, max(3, self.radius // 2))

class Enemy:
    def __init__(self, is_elite=False, level=1):
        self.is_elite = is_elite
        self.level = level
        self.size = 42 if self.is_elite else 25
        difficulty_multiplier = CHALLENGE_ENEMY_MULTIPLIER if game_mode == CHALLENGE_MODE else 1
        speed_multiplier = CHALLENGE_ENEMY_SPEED_MULTIPLIER if game_mode == CHALLENGE_MODE else 1
        speed_bonus = min(level * 0.03, 1.2)
        self.speed = ((random.uniform(1.1, 2.2) if self.is_elite else random.uniform(1.5, 3.5)) + speed_bonus) * speed_multiplier
        base_hp = 5 if self.is_elite else 1
        self.max_hp = max(1, int((base_hp + level // 6) * difficulty_multiplier))
        self.hp = self.max_hp
        self.shield = int((level // 4 + (2 if self.is_elite else 0)) * difficulty_multiplier)
        self.max_shield = self.shield
        self.damage = int((35 if self.is_elite else 20) * difficulty_multiplier)
        self.exp_drop_chance = 0.85 if self.is_elite else 0.4
        self.health_drop_chance = 0.12 if self.is_elite else 0.035
        self.color = (170, 40, 255) if self.is_elite else RED
        self.combat_type = "ranged" if random.random() < (0.38 if self.is_elite else 0.32) else "melee"
        self.attack_range = 420 if self.is_elite else 320
        self.keep_distance = 260 if self.is_elite else 205
        self.shoot_cooldown = random.randint(35, 90)
        self.shoot_delay = 85 if self.is_elite else 115
        self.facing = pygame.math.Vector2(1, 0)
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top': x, y = random.randint(0, MAP_WIDTH), -self.size
        elif edge == 'bottom': x, y = random.randint(0, MAP_WIDTH), MAP_HEIGHT + self.size
        elif edge == 'left': x, y = -self.size, random.randint(0, MAP_HEIGHT)
        else: x, y = MAP_WIDTH + self.size, random.randint(0, MAP_HEIGHT)
        self.pos = pygame.math.Vector2(x, y)
        self.rect = pygame.Rect(0, 0, self.size, self.size)
    def update(self, target_pos):
        direction = target_pos - self.pos
        distance = direction.length()
        if distance > 0:
            direction.normalize_ip()
            self.facing = direction.copy()
        move_dir = direction
        if self.combat_type == "ranged":
            if distance < self.keep_distance:
                move_dir = -direction
            elif distance <= self.attack_range:
                move_dir = pygame.math.Vector2(0, 0)
            if self.shoot_cooldown > 0:
                self.shoot_cooldown -= 1
        self.pos += move_dir * self.speed
        self.rect.center = (round(self.pos.x), round(self.pos.y))
    def emit_attacks(self, enemy_bullets, target_pos):
        if self.combat_type != "ranged" or self.shoot_cooldown > 0:
            return
        direction = target_pos - self.pos
        if direction.length_squared() == 0 or direction.length() > self.attack_range + 80:
            return
        direction.normalize_ip()
        self.facing = direction.copy()
        bullet_color = (255, 120, 45) if self.is_elite else ORANGE
        enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, direction.x, direction.y, color=bullet_color, core_color=WHITE, style="round"))
        self.shoot_cooldown = self.shoot_delay
    def draw(self, surface, camera):
        draw_rect = self.rect.move(-camera.x, -camera.y)
        facing = getattr(self, "facing", pygame.math.Vector2(1, 0))
        if facing.length_squared() == 0:
            facing = pygame.math.Vector2(1, 0)
        side = facing.rotate(90)
        center = pygame.math.Vector2(self.pos.x - camera.x, self.pos.y - camera.y)
        weapon_reach = 34 if self.is_elite else 24
        weapon_offset = self.size * 0.28
        hand = center + facing * weapon_offset + side * (self.size * 0.2)
        if self.combat_type == "melee":
            hilt = hand + facing * (8 if self.is_elite else 5)
            blade_tip = hand + facing * (weapon_reach + 16)
            blade_mid = hilt + facing * ((weapon_reach + 12) * 0.55)
            blade_half = 7 if self.is_elite else 5
            blade_color = (80, 240, 255) if self.is_elite else (100, 255, 145)
            blade_poly = [
                blade_tip,
                blade_mid + side * blade_half,
                hilt + side * max(3, blade_half - 2),
                hilt - side * max(3, blade_half - 2),
                blade_mid - side * blade_half,
            ]
            pygame.draw.polygon(surface, BLACK, [(round(p.x), round(p.y)) for p in blade_poly])
            inner_poly = [
                blade_tip - facing * 2,
                blade_mid + side * max(3, blade_half - 2),
                hilt + side * 2,
                hilt - side * 2,
                blade_mid - side * max(3, blade_half - 2),
            ]
            pygame.draw.polygon(surface, blade_color, [(round(p.x), round(p.y)) for p in inner_poly])
            pygame.draw.line(surface, WHITE, (round(hilt.x), round(hilt.y)), (round((blade_tip - facing * 5).x), round((blade_tip - facing * 5).y)), 2)
            pygame.draw.line(surface, WHITE, (round((hilt - side * 8).x), round((hilt - side * 8).y)), (round((hilt + side * 8).x), round((hilt + side * 8).y)), 3)
        else:
            muzzle = center + facing * weapon_reach + side * (self.size * 0.2)
            rear = center + facing * (self.size * 0.02) + side * (self.size * 0.2)
            body_half = 5 if self.is_elite else 4
            pistol_body = [
                rear + side * body_half,
                muzzle + side * max(2, body_half - 2),
                muzzle - side * max(2, body_half - 2),
                rear - side * body_half,
            ]
            pygame.draw.polygon(surface, BLACK, [(round(p.x), round(p.y)) for p in pistol_body])
            inner_body = [
                rear + side * (body_half - 1),
                muzzle + side * max(1, body_half - 3),
                muzzle - side * max(1, body_half - 3),
                rear - side * (body_half - 1),
            ]
            pygame.draw.polygon(surface, (205, 210, 215), [(round(p.x), round(p.y)) for p in inner_body])
            barrel_tip = muzzle + facing * (7 if self.is_elite else 5)
            pygame.draw.line(surface, BLACK, (round(muzzle.x), round(muzzle.y)), (round(barrel_tip.x), round(barrel_tip.y)), 5 if self.is_elite else 4)
            pygame.draw.line(surface, (235, 238, 240), (round(muzzle.x), round(muzzle.y)), (round(barrel_tip.x), round(barrel_tip.y)), 2)
            grip_top = rear - facing * 1 - side * body_half
            grip_bottom = grip_top - side * (13 if self.is_elite else 10) - facing * 3
            pygame.draw.line(surface, BLACK, (round(grip_top.x), round(grip_top.y)), (round(grip_bottom.x), round(grip_bottom.y)), 6 if self.is_elite else 5)
            pygame.draw.line(surface, (80, 85, 95), (round(grip_top.x), round(grip_top.y)), (round(grip_bottom.x), round(grip_bottom.y)), 3)
            pygame.draw.circle(surface, ORANGE if self.is_elite else YELLOW, (round(barrel_tip.x), round(barrel_tip.y)), 3)
        pygame.draw.rect(surface, self.color, draw_rect)
        if self.shield > 0:
            pygame.draw.rect(surface, BLUE, draw_rect.inflate(8, 8), 2)
        if self.is_elite:
            pygame.draw.circle(surface, (230, 170, 255), draw_rect.center, self.size//2 + 8, 2)
            pygame.draw.rect(surface, WHITE, draw_rect, 3)
            hp_bar = pygame.Rect(draw_rect.x, draw_rect.y - 10, self.size, 5)
            pygame.draw.rect(surface, GRAY, hp_bar)
            pygame.draw.rect(surface, GREEN, (hp_bar.x, hp_bar.y, hp_bar.width * (self.hp / self.max_hp), hp_bar.height))
            if self.max_shield > 0:
                shield_bar = pygame.Rect(draw_rect.x, draw_rect.y - 16, self.size, 4)
                pygame.draw.rect(surface, GRAY, shield_bar)
                pygame.draw.rect(surface, BLUE, (shield_bar.x, shield_bar.y, shield_bar.width * (self.shield / self.max_shield), shield_bar.height))

class Boss:
    def __init__(self, spawn_level=5, player_pos=None):
        spawn_center = pygame.math.Vector2(player_pos) if player_pos else pygame.math.Vector2(MAP_WIDTH / 2, MAP_HEIGHT / 2)
        end_x = max(120, min(MAP_WIDTH - 120, spawn_center.x))
        end_y = max(140, min(MAP_HEIGHT - 140, spawn_center.y - 220))
        start_y = max(80, end_y - 420)
        self.entrance_start = pygame.math.Vector2(end_x, start_y)
        self.entrance_end = pygame.math.Vector2(end_x, end_y)
        self.pos = self.entrance_start.copy()
        self.size = 60
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.spawn_level = spawn_level
        difficulty_multiplier = CHALLENGE_ENEMY_MULTIPLIER if game_mode == CHALLENGE_MODE else 1
        self.max_hp = int((1000 + spawn_level * 300) * difficulty_multiplier)
        self.hp = self.max_hp
        self.speed = 4.0 * difficulty_multiplier
        
        self.state = "ENTRANCE"  # 改為出場狀態
        self.state_timer = 0
        self.defeat_timer = 0
        self.color = YELLOW
        self.entrance_duration = 240  # 出場動畫持續時間(秒數)
        self.name = "星核守衛"
        self.collision_damage = int(40 * difficulty_multiplier)

    def update(self, player_pos, bullets):
        self.state_timer += 1
        
        if self.state == "ENTRANCE":
            progress = min(1, self.state_timer / self.entrance_duration)
            eased = 1 - (1 - progress) ** 3
            self.pos = self.entrance_start.lerp(self.entrance_end, eased)
            glow = int(100 + 155 * progress)
            self.color = (glow, glow, 0)
            
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
            
        self.pos.x = max(self.size, min(MAP_WIDTH-self.size, self.pos.x))
        self.pos.y = max(self.size, min(MAP_HEIGHT-self.size, self.pos.y))
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def can_take_damage(self):
        return self.state not in ("ENTRANCE", "EVADE", "DEFEAT")

    def emit_attacks(self, enemy_bullets):
        if self.state == "SHOOT":
            for i in range(12):
                angle = math.radians(i * 30)
                dir_x, dir_y = math.cos(angle), math.sin(angle)
                enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, dir_x, dir_y, color=(255, 30, 95), core_color=(255, 245, 120), style="diamond"))
            if self.spawn_level >= 10:
                for i in range(12):
                    angle = math.radians(i * 30 + 15)
                    dir_x, dir_y = math.cos(angle), math.sin(angle)
                    enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, dir_x, dir_y, color=(255, 115, 30), core_color=(255, 255, 210), style="diamond"))
            self.state = "EVADE"
            play_sound("shoot")

    def get_intro_title(self):
        return f"✦ {self.name} 入場 ✦"

    def get_intro_lines(self):
        return [
            "⚠️ BOSS 出現！時間暫停中",
            "黃色 = 閃避護盾模式  |  橙紅色 = 可攻擊",
            "觀察型態轉換，把握攻擊時機！"
        ]

    def get_state_message(self):
        if self.state == "EVADE":
            return "閃避階段 - 無敵狀態 (黃色)", YELLOW
        if self.state == "CHARGE":
            return "蓄力階段 - 可攻擊 (橙紅色)", ORANGE
        if self.state == "SHOOT":
            return "發射階段 - 可攻擊", RED
        return "BOSS 交戰中", WHITE

    def draw(self, surface, camera):
        def draw_threat_core(size, color):
            cx, cy = (round(self.pos.x - camera.x), round(self.pos.y - camera.y))
            half = size // 2
            horn = size // 3
            points = [
                (cx, cy - half - horn),
                (cx + half, cy - half // 2),
                (cx + half + horn, cy),
                (cx + half, cy + half // 2),
                (cx, cy + half + horn),
                (cx - half, cy + half // 2),
                (cx - half - horn, cy),
                (cx - half, cy - half // 2)
            ]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, WHITE, points, 3)
            pygame.draw.circle(surface, RED, (cx, cy), max(8, size // 5))
            pygame.draw.circle(surface, BLACK, (cx, cy), max(3, size // 10))
            for i in range(4):
                angle = pygame.time.get_ticks() * 0.002 + i * math.pi / 2
                sx = cx + math.cos(angle) * (half + 22)
                sy = cy + math.sin(angle) * (half + 22)
                pygame.draw.circle(surface, ORANGE, (int(sx), int(sy)), 5)

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
                    pygame.draw.circle(surface, WHITE, (round(self.pos.x - camera.x), round(self.pos.y - camera.y)), ring_size, 2)
            
            draw_threat_core(current_size, self.color)
            
            # 繪製能量粒子
            for i in range(8):
                angle = (self.state_timer * 0.05 + i * math.pi / 4)
                px = self.pos.x - camera.x + math.cos(angle) * (self.size + 30)
                py = self.pos.y - camera.y + math.sin(angle) * (self.size + 30)
                pygame.draw.circle(surface, YELLOW, (int(px), int(py)), 3)
        elif self.state == "DEFEAT":
            # 爆炸特效
            progress = min(1, self.defeat_timer / 60)
            center = (round(self.pos.x - camera.x), round(self.pos.y - camera.y))
            for i in range(7):
                radius = int(self.size * 0.6 + progress * 150 + i * 14)
                ring_color = (255, max(60, 210 - i * 22), 30 + i * 18)
                pygame.draw.circle(surface, ring_color, center, radius, 3)
            core_size = max(1, int(self.size * (1 - progress * 0.85)))
            core_points = []
            for i in range(8):
                angle = self.defeat_timer * 0.08 + i * math.pi / 4
                length = core_size + (14 if i % 2 == 0 else 2)
                core_points.append((int(center[0] + math.cos(angle) * length), int(center[1] + math.sin(angle) * length)))
            if len(core_points) >= 3:
                pygame.draw.polygon(surface, (255, 210, 60), core_points)
            
            burst = int(8 + progress * 18)
            for i in range(burst):
                angle = i * (math.pi * 2 / max(1, burst)) + self.defeat_timer * 0.3
                distance = self.size + 20 + progress * 130
                px = center[0] + math.cos(angle) * distance
                py = center[1] + math.sin(angle) * distance
                pygame.draw.circle(surface, RED if i % 2 else YELLOW, (int(px), int(py)), 5)
        else:
            # 正常繪制
            aura_radius = self.size + 28 + int(abs(math.sin(self.state_timer * 0.08)) * 12)
            boss_center = (round(self.pos.x - camera.x), round(self.pos.y - camera.y))
            pygame.draw.circle(surface, RED if self.state == "CHARGE" else PURPLE, boss_center, aura_radius, 2)
            draw_threat_core(self.size, self.color)
            if self.state == "EVADE":
                pygame.draw.circle(surface, WHITE, boss_center, self.size//2 + 24, 3)
            elif self.state == "CHARGE":
                shrink = max(0, 30 - (self.state_timer // 2))
                pygame.draw.circle(surface, RED, boss_center, self.size//2 + shrink + 18, 3)

class ChargerBoss:
    def __init__(self, spawn_level=5, player_pos=None):
        spawn_center = pygame.math.Vector2(player_pos) if player_pos else pygame.math.Vector2(MAP_WIDTH / 2, MAP_HEIGHT / 2)
        side = -1 if random.random() < 0.5 else 1
        end_x = max(160, min(MAP_WIDTH - 160, spawn_center.x + side * 320))
        end_y = max(160, min(MAP_HEIGHT - 160, spawn_center.y - 120))
        start_x = max(100, min(MAP_WIDTH - 100, end_x + side * 520))
        self.entrance_start = pygame.math.Vector2(start_x, end_y)
        self.entrance_end = pygame.math.Vector2(end_x, end_y)
        self.pos = self.entrance_start.copy()
        self.size = 76
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.spawn_level = spawn_level
        difficulty_multiplier = CHALLENGE_ENEMY_MULTIPLIER if game_mode == CHALLENGE_MODE else 1
        self.max_hp = int((650 + spawn_level * 135) * difficulty_multiplier)
        self.hp = self.max_hp
        self.speed = (5.2 + min(spawn_level * 0.08, 1.6)) * difficulty_multiplier
        self.state = "ENTRANCE"
        self.state_timer = 0
        self.defeat_timer = 0
        self.color = (255, 70, 60)
        self.entrance_duration = 130
        self.name = "裂空突擊者"
        self.collision_damage = int(50 * difficulty_multiplier)
        self.charge_direction = pygame.math.Vector2(1, 0)
        self.charge_target = self.pos.copy()
        self.side_fire_timer = 0
        self.spin_fire_timer = 0
        self.spin_angle = 0

    def update(self, player_pos, bullets):
        self.state_timer += 1

        if self.state == "ENTRANCE":
            progress = min(1, self.state_timer / self.entrance_duration)
            eased = 1 - (1 - progress) ** 3
            self.pos = self.entrance_start.lerp(self.entrance_end, eased)
            pulse = int(80 * abs(math.sin(self.state_timer * 0.12)))
            self.color = (175 + pulse, 45, 55)
            if self.state_timer >= self.entrance_duration:
                self.state = "AIM"
                self.state_timer = 0

        elif self.state == "AIM":
            self.color = (255, 210, 60)
            direction = player_pos - self.pos
            if direction.length() > 0:
                direction.normalize_ip()
                self.charge_direction = direction
                self.charge_target = self.pos + direction * 760
            if self.state_timer > 70:
                self.state = "DASH"
                self.state_timer = 0
                self.side_fire_timer = 0

        elif self.state == "DASH":
            self.color = (255, 45, 45)
            self.pos += self.charge_direction * (self.speed * 3.2)
            self.side_fire_timer += 1
            if self.state_timer > 44 or self.pos.distance_to(self.charge_target) < 45:
                self.state = "RECOVER"
                self.state_timer = 0

        elif self.state == "RECOVER":
            self.color = (170, 80, 255)
            self.spin_angle += 0.13
            self.spin_fire_timer += 1
            if self.state_timer > 240:
                self.state = "AIM"
                self.state_timer = 0
                self.spin_fire_timer = 0

        elif self.state == "DEFEAT":
            self.defeat_timer += 1
            self.color = (255, max(0, 120 - self.defeat_timer * 3), 60)
            self.pos.y -= 0.8
            self.pos.x += math.sin(self.defeat_timer * 0.25) * 2

        self.pos.x = max(self.size, min(MAP_WIDTH - self.size, self.pos.x))
        self.pos.y = max(self.size, min(MAP_HEIGHT - self.size, self.pos.y))
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def can_take_damage(self):
        return self.state not in ("ENTRANCE", "DASH", "DEFEAT")

    def emit_attacks(self, enemy_bullets):
        if self.state == "DASH" and self.side_fire_timer % 7 == 0:
            side_a = self.charge_direction.rotate(90)
            side_b = self.charge_direction.rotate(-90)
            for side in (side_a, side_b):
                enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, side.x, side.y, color=(0, 210, 255), core_color=(210, 255, 255), style="slash"))
                if self.spawn_level >= 10:
                    enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, (side + self.charge_direction * 0.35).x, (side + self.charge_direction * 0.35).y, color=(50, 255, 170), core_color=(225, 255, 240), style="slash"))
            play_sound("shoot")
        elif self.state == "RECOVER" and self.spin_fire_timer % 14 == 0:
            shots = 6 if self.spawn_level < 10 else 8
            for i in range(shots):
                angle = self.spin_angle + i * (math.pi * 2 / shots)
                enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, math.cos(angle), math.sin(angle), color=(185, 60, 255), core_color=(255, 220, 255), style="round"))
            play_sound("shoot")

    def get_intro_title(self):
        return f"✦ {self.name} 入場 ✦"

    def get_intro_lines(self):
        return [
            "⚠️ 特殊 BOSS 出現！時間暫停中",
            "金色 = 鎖定玩家  |  紅色 = 無敵長距離衝刺",
            "紫色冷卻時會原地旋轉射擊，別貼太近！"
        ]

    def get_state_message(self):
        if self.state == "AIM":
            return "鎖定階段 - 即將衝刺 (金色)", YELLOW
        if self.state == "DASH":
            return "突擊階段 - 無敵高速衝刺", RED
        if self.state == "RECOVER":
            return "冷卻階段 - 原地旋轉彈幕", PURPLE
        return "BOSS 交戰中", WHITE

    def draw(self, surface, camera):
        cx, cy = (round(self.pos.x - camera.x), round(self.pos.y - camera.y))
        pulse = abs(math.sin(self.state_timer * 0.13))
        direction = self.charge_direction if self.charge_direction.length_squared() > 0 else pygame.math.Vector2(1, 0)
        nose = (cx + int(direction.x * (self.size // 2 + 26)), cy + int(direction.y * (self.size // 2 + 26)))
        back = pygame.math.Vector2(cx, cy) - direction * (self.size // 2)
        left = back + direction.rotate(90) * (self.size // 2)
        right = back + direction.rotate(-90) * (self.size // 2)
        wing_left = pygame.math.Vector2(cx, cy) + direction.rotate(90) * (self.size // 2 + 24)
        wing_right = pygame.math.Vector2(cx, cy) + direction.rotate(-90) * (self.size // 2 + 24)

        if self.state == "ENTRANCE":
            for i in range(4):
                radius = self.size // 2 + 18 + i * 16 + int(pulse * 8)
                pygame.draw.circle(surface, (255, 90, 90), (cx, cy), radius, 2)
        elif self.state == "DEFEAT":
            progress = min(1, self.defeat_timer / 60)
            for i in range(4):
                radius = int(self.size * 0.7 + progress * 170 + i * 18)
                pygame.draw.circle(surface, (255, 70 + i * 25, 45), (cx, cy), radius, 3)
            for i in range(8):
                angle = self.defeat_timer * 0.09 + i * math.pi / 4
                distance = 35 + progress * (110 + i * 8)
                shard_center = pygame.math.Vector2(cx, cy) + pygame.math.Vector2(math.cos(angle), math.sin(angle)) * distance
                shard_dir = pygame.math.Vector2(math.cos(angle), math.sin(angle))
                shard_side = shard_dir.rotate(90)
                shard_len = max(8, int(26 * (1 - progress * 0.45)))
                shard_points = [
                    shard_center + shard_dir * shard_len,
                    shard_center - shard_dir * shard_len * 0.6 + shard_side * 8,
                    shard_center - shard_dir * shard_len * 0.6 - shard_side * 8,
                ]
                pygame.draw.polygon(surface, ORANGE if i % 2 else RED, [(int(p.x), int(p.y)) for p in shard_points])

        body_points = [
            nose,
            (int(wing_left.x), int(wing_left.y)),
            (int(left.x), int(left.y)),
            (cx - int(direction.x * 12), cy - int(direction.y * 12)),
            (int(right.x), int(right.y)),
            (int(wing_right.x), int(wing_right.y)),
        ]
        aura_color = RED if self.state == "DASH" else ORANGE if self.state == "AIM" else PURPLE
        pygame.draw.circle(surface, aura_color, (cx, cy), self.size // 2 + 30 + int(pulse * 10), 2)
        if self.state == "DEFEAT":
            shake = math.sin(self.defeat_timer * 0.7) * 5
            broken_points = [(x + int(shake if i % 2 == 0 else -shake), y) for i, (x, y) in enumerate(body_points)]
            pygame.draw.polygon(surface, (120, 30, 35), broken_points)
            pygame.draw.polygon(surface, RED, broken_points, 2)
            pygame.draw.circle(surface, (255, 120, 40), (cx, cy), max(2, int(16 * (1 - progress))), 2)
        else:
            pygame.draw.polygon(surface, self.color, body_points)
            pygame.draw.polygon(surface, WHITE, body_points, 3)
            pygame.draw.circle(surface, BLACK, (cx, cy), 14)
            pygame.draw.circle(surface, RED if self.state == "DASH" else YELLOW, (cx, cy), 8)

        if self.state == "AIM":
            target = pygame.math.Vector2(cx, cy) + direction * 260
            pygame.draw.line(surface, YELLOW, (cx, cy), (int(target.x), int(target.y)), 3)
        elif self.state == "DASH":
            pygame.draw.circle(surface, WHITE, (cx, cy), self.size // 2 + 36, 3)
            for side_angle in (90, -90):
                side = direction.rotate(side_angle)
                tip = pygame.math.Vector2(cx, cy) + side * 120
                pygame.draw.line(surface, ORANGE, (cx, cy), (int(tip.x), int(tip.y)), 2)
        elif self.state == "RECOVER":
            for i in range(6):
                angle = self.spin_angle + i * math.pi / 3
                tip = pygame.math.Vector2(cx, cy) + pygame.math.Vector2(math.cos(angle), math.sin(angle)) * 95
                pygame.draw.line(surface, PURPLE, (cx, cy), (int(tip.x), int(tip.y)), 2)

class Particle:
    def __init__(self, x, y, color=RED):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(random.uniform(-6, 6), random.uniform(-6, 6))
        self.timer, self.size, self.color = random.randint(15, 30), random.randint(4, 8), color
    def update(self):
        self.pos += self.vel; self.timer -= 1; self.size = max(0, self.size - 0.25)
    def draw(self, surface, camera):
        if self.size > 0: pygame.draw.rect(surface, self.color, (self.pos.x - camera.x, self.pos.y - camera.y, self.size, self.size))

class Gem:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y); self.rect = pygame.Rect(0, 0, 10, 10)
    def update(self, p_pos, mag_rad):
        if self.pos.distance_to(p_pos) < mag_rad:
            dir = p_pos - self.pos
            if dir.length() > 0: dir.normalize_ip()
            self.pos += dir * 8 
        self.rect.center = (round(self.pos.x), round(self.pos.y))
    def draw(self, surface, camera):
        x, y = self.pos.x - camera.x, self.pos.y - camera.y
        pts =[(x, y-6), (x+6, y), (x, y+6), (x-6, y)]
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

    def draw(self, surface, camera):
        draw_rect = self.rect.move(-camera.x, -camera.y)
        pygame.draw.rect(surface, GREEN, draw_rect, border_radius=4)
        pygame.draw.rect(surface, WHITE, draw_rect, 2, border_radius=4)
        pygame.draw.rect(surface, WHITE, (draw_rect.centerx - 2, draw_rect.y + 4, 4, self.size - 8))
        pygame.draw.rect(surface, WHITE, (draw_rect.x + 4, draw_rect.centery - 2, self.size - 8, 4))

def choose_upgrade_cards():
    global current_upgrade_choices, selected_upgrade_position
    card_count = min(3, len(upgrade_options))
    available = [
        i for i, option in enumerate(upgrade_options)
        if game_mode == CHALLENGE_MODE or not option.get("challenge_only")
    ]
    card_count = min(card_count, len(available))
    current_upgrade_choices = []
    for _ in range(card_count):
        total_weight = sum(upgrade_options[i].get("weight", 1) for i in available)
        pick = random.uniform(0, total_weight)
        running_weight = 0
        for i in available:
            running_weight += upgrade_options[i].get("weight", 1)
            if pick <= running_weight:
                current_upgrade_choices.append(i)
                available.remove(i)
                break
    selected_upgrade_position = None

def add_chosen_upgrade(choice):
    title = upgrade_options[choice]["title"]
    for upgrade in chosen_upgrades:
        if upgrade["title"] == title:
            upgrade["count"] += 1
            return
    chosen_upgrades.append({"title": title, "count": 1})

def refresh_player_shield_max(fill_gain=False):
    old_max = max(1, player.max_shield)
    old_ratio = player.shield / old_max
    player.max_shield = max(1, int(player.max_hp * 0.2))
    if fill_gain:
        player.shield = min(player.max_shield, player.shield + max(0, player.max_shield - old_max))
    else:
        player.shield = min(player.max_shield, player.max_shield * old_ratio)

def apply_upgrade(choice):
    global game_state, selected_upgrade_position
    if choice == 0:
        player.max_hp += 50
        player.hp += 50
        refresh_player_shield_max(fill_gain=True)
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
        refresh_player_shield_max(fill_gain=True)
    elif choice == 16: player.magnet_radius += 25; player.stamina_regen += 0.15
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
    elif choice == 23: player.reload_duration = max(35, player.reload_duration - 18)
    add_chosen_upgrade(choice)
    current_upgrade_choices.clear()
    selected_upgrade_position = None
    switch_to_english_input()
    game_state = "PLAYING"             

# ==========================================
# 🛑 中文化升級選項系統 (用陣列方便換行)
# ==========================================
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
cards =[
    pygame.Rect(WIDTH//2 - 360, 260, 220, 280),
    pygame.Rect(WIDTH//2 - 110, 260, 220, 280),
    pygame.Rect(WIDTH//2 + 140, 260, 220, 280)
]
confirm_upgrade_button = pygame.Rect(WIDTH//2 - 110, 590, 220, 60)
current_upgrade_choices = []
selected_upgrade_position = None
chosen_upgrades = []
pause_upgrade_scroll = 0

# 退出遊戲按鈕
exit_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 170, 200, 60)

# 開始遊戲按鈕
start_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 60)
normal_button = pygame.Rect(WIDTH//2 - 430, HEIGHT//2 - 35, 380, 230)
challenge_button = pygame.Rect(WIDTH//2 + 50, HEIGHT//2 - 35, 380, 230)
difficulty_back_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 245, 220, 55)

# 更新日誌按鈕
changelog_button = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 95, 200, 60)
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

def draw_pause_upgrade_log(surface):
    panel_rect = pygame.Rect(WIDTH//2 - 330, HEIGHT//2 + 235, 660, 260)
    panel = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
    panel.fill((18, 20, 30, 205))
    surface.blit(panel, panel_rect.topleft)
    pygame.draw.rect(surface, WHITE, panel_rect, 2, border_radius=8)

    title = small_font.render("本局強化紀錄（滑鼠滾輪上下瀏覽）", True, YELLOW)
    surface.blit(title, (panel_rect.x + 16, panel_rect.y + 12))
    content_rect = pygame.Rect(panel_rect.x + 16, panel_rect.y + 44, panel_rect.width - 42, panel_rect.height - 58)

    rows = []
    for upgrade in chosen_upgrades:
        option = next((opt for opt in upgrade_options if opt["title"] == upgrade["title"]), None)
        desc = " / ".join(option["desc"]) if option else ""
        count = f" x{upgrade['count']}" if upgrade["count"] > 1 else ""
        rows.append((f"{upgrade['title']}{count}", desc))

    if not rows:
        empty = small_font.render("尚未選擇任何強化", True, GRAY)
        surface.blit(empty, (content_rect.x, content_rect.y + 8))
        return

    row_h = 54
    content_height = max(content_rect.height, len(rows) * row_h)
    max_scroll = max(0, content_height - content_rect.height)
    scroll_y = min(pause_upgrade_scroll, max_scroll)
    content_surface = pygame.Surface((content_rect.width, content_height), pygame.SRCALPHA)

    for i, (name, desc) in enumerate(rows):
        y = i * row_h
        name_txt = small_font.render(name, True, WHITE)
        content_surface.blit(name_txt, (0, y))
        for j, line in enumerate(wrap_text(desc, tiny_font, content_rect.width - 20)):
            desc_txt = tiny_font.render(line, True, YELLOW)
            content_surface.blit(desc_txt, (18, y + 25 + j * 20))

    surface.blit(content_surface, content_rect.topleft, pygame.Rect(0, scroll_y, content_rect.width, content_rect.height))
    if max_scroll > 0:
        bar_h = max(36, int(content_rect.height * content_rect.height / content_height))
        bar_y = content_rect.y + int((content_rect.height - bar_h) * (scroll_y / max_scroll))
        pygame.draw.rect(surface, GRAY, (content_rect.right + 8, content_rect.y, 7, content_rect.height), border_radius=4)
        pygame.draw.rect(surface, YELLOW, (content_rect.right + 8, bar_y, 7, bar_h), border_radius=4)

def get_camera_offset():
    camera_x = max(0, min(MAP_WIDTH - WIDTH, player.pos.x - WIDTH / 2))
    camera_y = max(0, min(MAP_HEIGHT - HEIGHT, player.pos.y - HEIGHT / 2))
    return pygame.math.Vector2(camera_x, camera_y)

def draw_map_bounds(surface, camera):
    map_rect = pygame.Rect(-camera.x, -camera.y, MAP_WIDTH, MAP_HEIGHT)
    pygame.draw.rect(surface, (25, 30, 45), map_rect, 4)
    for x in range(0, MAP_WIDTH + 1, 400):
        sx = x - camera.x
        if -10 <= sx <= WIDTH + 10:
            pygame.draw.line(surface, (18, 22, 32), (sx, -camera.y), (sx, MAP_HEIGHT - camera.y), 1)
    for y in range(0, MAP_HEIGHT + 1, 400):
        sy = y - camera.y
        if -10 <= sy <= HEIGHT + 10:
            pygame.draw.line(surface, (18, 22, 32), (-camera.x, sy), (MAP_WIDTH - camera.x, sy), 1)

def draw_boss_direction_arrow(surface, boss_obj, camera):
    if not boss_obj or boss_obj.state == "DEFEAT":
        return
    boss_screen = pygame.math.Vector2(boss_obj.pos.x - camera.x, boss_obj.pos.y - camera.y)
    visible_rect = pygame.Rect(-40, -40, WIDTH + 80, HEIGHT + 80)
    if visible_rect.collidepoint(boss_screen.x, boss_screen.y):
        return

    center = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
    direction = boss_screen - center
    if direction.length_squared() == 0:
        return
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
    distance_txt = small_font.render(f"Boss 距離 {distance:03d} stud", True, YELLOW)
    label_pos = arrow_pos - pygame.math.Vector2(distance_txt.get_width() / 2, 48)
    surface.blit(distance_txt, (int(label_pos.x), int(label_pos.y)))

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

def rebuild_changelog_cache(content_width, content_height):
    global changelog_content_surface, changelog_max_scroll
    content_lines = []
    for line in CHANGELOG:
        color = YELLOW if line.startswith("v") else WHITE
        for wrapped_line in wrap_text(line, font, content_width - 20):
            content_lines.append((wrapped_line, color))
        content_lines.append(("", WHITE))

    surface_height = max(content_height, len(content_lines) * 34 + 10)
    changelog_content_surface = pygame.Surface((content_width, surface_height), pygame.SRCALPHA)
    for i, (line, color) in enumerate(content_lines):
        if line:
            text = font.render(line, True, color)
            changelog_content_surface.blit(text, (0, 6 + i * 34))
    changelog_max_scroll = max(0, surface_height - content_height)

def draw_changelog_popup(surface):
    popup = pygame.Rect(WIDTH//2 - 420, HEIGHT//2 - 300, 840, 660)
    panel = pygame.Surface((popup.width, popup.height), pygame.SRCALPHA)
    panel.fill((18, 20, 32, 235))
    surface.blit(panel, popup.topleft)
    pygame.draw.rect(surface, WHITE, popup, 3, border_radius=12)

    title = large_font.render("更新日誌", True, YELLOW)
    surface.blit(title, (popup.centerx - title.get_width()//2, popup.y + 35))

    content_rect = pygame.Rect(popup.x + 60, popup.y + 110, popup.width - 120, popup.height - 205)
    if changelog_content_surface is None:
        rebuild_changelog_cache(content_rect.width, content_rect.height)

    scroll_y = min(changelog_scroll, changelog_max_scroll)
    surface.blit(changelog_content_surface, content_rect.topleft, pygame.Rect(0, scroll_y, content_rect.width, content_rect.height))
    pygame.draw.rect(surface, GRAY, content_rect, 1)

    if changelog_max_scroll > 0:
        bar_h = max(40, int(content_rect.height * content_rect.height / changelog_content_surface.get_height()))
        bar_y = content_rect.y + int((content_rect.height - bar_h) * (scroll_y / changelog_max_scroll))
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
    
    "v1.367",
    "- 移除玩家步槍側邊彈匣，保留俯視角槍身、前握把與準星",
    "- 小兵與精英小兵分為近戰和遠程兩類",
    "- 近戰小兵拿光劍，遠程小兵拿小手槍並會保持距離射擊",
    "v1.357",
    "- 步槍改為更明確的俯視角模型，加入側邊彈匣、前握把與準星細節",
    "- 回血包掉落與拾取功能恢復，護盾仍維持獨立自動恢復",
    "- 小兵新增手持武器外觀，會朝玩家方向持槍",
    "v1.347",
    "- 優化玩家步槍與狙擊槍模型，補上槍身、槍托、握把與配件輪廓",
    "- 新增玩家護盾，初始值為最大血量 20%，受傷後會自動恢復",
    "- 護盾不使用回血包機制，改為受傷後延遲自動恢復",
    "v1.337",
    "- 普通模式小兵生成速度提高",
    "- 玩家旁新增步槍與狙擊槍外型，右鍵瞄準時會顯示狙擊鏡",
    "- Boss 離開可見範圍時會在畫面邊緣顯示方位箭頭",
    "- 初始頁面新增退出遊戲按鈕",
    "v1.327",
    "- 修復挑戰模式下某些敵人移動異常的問題",
    "- 調整挑戰模式步槍與狙擊槍的傷害平衡",
    "v1.326",
    "- 將手槍名稱統一改為步槍",
    "- 挑戰模式步槍彈匣提升為 45 發",
    "- 擴容彈匣改為步槍 +10、狙擊 +2",
    "v1.325",
    "- 難易度選擇畫面重新排版，強化普通與挑戰模式差異提示",
    "- 所有模式 Boss 出現時會清空小怪",
    "- Boss 存活期間暫停召喚小怪，直到 Boss 被擊敗才恢復",
    "v1.315",
    "- 開始遊戲後新增普通與挑戰模式選擇",
    "- 挑戰模式敵人強度提升為 1.75 倍，並啟用步槍/狙擊彈匣與換彈系統",
    "- 挑戰模式新增擴容彈匣與快拆彈匣強化卡牌",
    "- 寬幅槍口改為同一條彈道追加子彈，不再和彈幕擴張重複",
    "v1.305",
    "- 優化兩種 Boss 的專屬死亡動畫",
    "- 導引模組恢復為持續小幅追蹤附近目標",
    "- 進入與回到遊戲時會嘗試自動切換英文輸入法",
    "v1.295",
    "- 版本號承接上版調整並追加本次更新",
    "- 裂空突擊者衝刺冷卻延長，冷卻時會原地旋轉發射子彈",
    "- 裂空突擊者衝刺距離加長，衝刺期間改為無敵",
    "- 導引模組改為每顆子彈固定鎖定單一敵人，不會中途被其他敵人吸走",
    "v1.185",
    "- Boss 出場動畫期間會暫停遊戲並顯示提示語",
    "- 新增裂空突擊者 Boss：衝向玩家並向兩側發射子彈",
    "- 兩種 Boss 會依出現次數輪流登場",
    "v1.175",
    "- 強化卡牌加入攻擊、支援、生命分類與背景色",
    "- 抽卡權重調整：攻擊最高、支援其次、生命最低",
    "- 新增學習核心，可提升經驗獲得倍率",
    "v1.165",
    "- 降低回血包掉落率",
    "- 狙擊模式多彈幕散射懲罰降低",
    "- 新增電弧光環與再生奈米強化",
    "v1.155",
    "- 更新日誌文字改用快取繪製，減少滑動卡頓",
    "v1.154",
    "- 地圖改為固定大小，Boss 不會被鏡頭推到場外",
    "- 暫停畫面強化紀錄可滾動瀏覽並顯示效果說明",
    "v1.153",
    "- 導引模組改為近距離小幅追蹤",
    "- 精英怪紫色識別更明顯",
    "- Boss 外觀改為更具壓迫感的尖刺核心",
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
changelog_content_surface = None
changelog_max_scroll = 0
game_mode = NORMAL_MODE
SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1

# --- 遊戲狀態重置系統 ---
def reset_game(initial_state="PLAYING", mode=None):
    global player, bullets, enemy_bullets, enemies, particles, gems, health_packs, trails
    global boss, boss_active, boss_defeated, next_boss_level, boss_spawn_count, game_state, game_mode, current_upgrade_choices, selected_upgrade_position, chosen_upgrades, show_changelog, changelog_scroll, changelog_content_surface, changelog_max_scroll, pause_upgrade_scroll
    if mode is not None:
        game_mode = mode
    player = Player()
    bullets, enemy_bullets, enemies, particles, gems, health_packs, trails = [], [], [], [], [], [], []
    boss = None
    boss_active = False
    boss_defeated = False
    next_boss_level = 5
    boss_spawn_count = 0
    current_upgrade_choices = []
    selected_upgrade_position = None
    chosen_upgrades = []
    show_changelog = False
    changelog_scroll = 0
    changelog_content_surface = None
    changelog_max_scroll = 0
    pause_upgrade_scroll = 0
    stop_sound("boss_bgm")
    game_state = initial_state
    pygame.time.set_timer(SPAWN_ENEMY_EVENT, NORMAL_SPAWN_INTERVAL if game_mode == NORMAL_MODE else CHALLENGE_SPAWN_INTERVAL)
    
    

reset_game("MENU")
shoot_cooldown = 0 
dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
dim_surface.fill((0, 0, 0, 180))

# Boss 警告計時器
boss_warning_timer = 0
boss_spawn_count = 0

def draw_boss_entrance_frame():
    camera = get_camera_offset()
    screen.fill(BLACK)
    draw_map_bounds(screen, camera)
    
    for g in gems: g.draw(screen, camera)
    for p in particles: p.draw(screen, camera)
    for b in bullets: b.draw(screen, camera)
    for eb in enemy_bullets: eb.draw(screen, camera) 
    for e in enemies: e.draw(screen, camera)
    for t in trails: t.draw(screen, camera)
    
    if boss_active: boss.draw(screen, camera)
    player.draw(screen, camera)
    if boss_active: draw_boss_direction_arrow(screen, boss, camera)

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

# --- 4. 遊戲主迴圈 ---
running = True
while running:
    for event in pygame.event.get():
        if WINDOW_FOCUS_GAINED is not None and event.type == WINDOW_FOCUS_GAINED:
            switch_to_english_input()
        if game_state == "MENU" and show_changelog and event.type == pygame.MOUSEWHEEL:
            changelog_scroll = max(0, min(changelog_max_scroll, changelog_scroll - event.y * 55))
        if game_state == "PAUSED" and event.type == pygame.MOUSEWHEEL:
            pause_upgrade_scroll = max(0, pause_upgrade_scroll - event.y * 45)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if game_state == "PLAYING":
                game_state = "PAUSED"
            elif game_state == "PAUSED":
                switch_to_english_input()
                game_state = "PLAYING"
            elif game_state == "DIFFICULTY":
                game_state = "MENU"

        if game_state == "PLAYING" and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            player.start_reload()
        
        if game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game("PLAYING", game_mode)
                switch_to_english_input()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if restart_button.collidepoint(event.pos):
                    reset_game("PLAYING", game_mode)
                    switch_to_english_input()
                elif menu_button.collidepoint(event.pos):
                    reset_game("MENU", NORMAL_MODE)
        elif game_state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_changelog:
                    if changelog_close_button.collidepoint(event.pos):
                        show_changelog = False
                        changelog_scroll = 0
                elif start_button.collidepoint(event.pos):
                    game_state = "DIFFICULTY"
                elif changelog_button.collidepoint(event.pos):
                    show_changelog = True
                    changelog_scroll = 0
                    if changelog_content_surface is None:
                        rebuild_changelog_cache(720, 455)
                elif exit_button.collidepoint(event.pos):
                    running = False
        elif game_state == "DIFFICULTY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if normal_button.collidepoint(event.pos):
                    reset_game("PLAYING", NORMAL_MODE)
                    switch_to_english_input()
                elif challenge_button.collidepoint(event.pos):
                    reset_game("PLAYING", CHALLENGE_MODE)
                    switch_to_english_input()
                elif difficulty_back_button.collidepoint(event.pos):
                    game_state = "MENU"
        elif game_state == "PAUSED":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pause_resume_btn = pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 70, 220, 60)
                pause_menu_btn = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 70, 220, 60)
                pause_restart_btn = pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 150, 220, 60)
                pause_exit_btn = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 150, 220, 60)
                if pause_resume_btn.collidepoint(event.pos):
                    switch_to_english_input()
                    game_state = "PLAYING"
                elif pause_menu_btn.collidepoint(event.pos):
                    reset_game("MENU", NORMAL_MODE)
                elif pause_restart_btn.collidepoint(event.pos):
                    reset_game("PLAYING", game_mode)
                    switch_to_english_input()
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
                if not boss_active:
                    elite_chance = min(0.03 + player.level * 0.006, 0.15)
                    enemies.append(Enemy(is_elite=random.random() < elite_chance, level=player.level))

    if game_state == "PLAYING":
        if player.level >= next_boss_level and not boss_active:
            boss_spawn_count += 1
            boss = Boss(next_boss_level, player.pos) if boss_spawn_count % 2 == 1 else ChargerBoss(next_boss_level, player.pos)
            boss_active = True
            boss_defeated = False
            enemies.clear()
            boss_warning_timer = 120  # boss警告時常(秒數)
            play_sound("boss_bgm", loop=-1) 

        boss_entrance_pause = boss_active and boss and boss.state == "ENTRANCE"

        if boss_entrance_pause:
            boss.update(player.pos, bullets)
            if boss_warning_timer > 0:
                boss_warning_timer -= 1
            draw_boss_entrance_frame()
            pygame.display.flip()
            clock.tick(FPS)
            continue

        mouse_btns = pygame.mouse.get_pressed()
        if mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing and player.can_fire_current_weapon():
            camera = get_camera_offset()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            world_mouse = pygame.math.Vector2(mouse_x + camera.x, mouse_y + camera.y)
            is_piercing = player.is_aiming
            # 計算基礎向量
            base_dir = world_mouse - player.pos
            if base_dir.length() > 0: base_dir.normalize_ip()
            # 根據 bullet_count 產生子彈
            current_spread = player.bullet_spread * (0.35 if is_piercing else 1)
            start_angle = -(player.bullet_count - 1) * current_spread / 2
            for i in range(player.bullet_count):
                angle = start_angle + (i * current_spread)
                # 旋轉基礎向量來產生散彈效果
                shot_dir = base_dir.rotate(angle)
                same_path_count = 1 + player.extra_same_path_bullets
                for j in range(same_path_count):
                    spawn_offset = shot_dir * (j * 18)
                    target_pos = player.pos + shot_dir * 100 + spawn_offset
                    bullets.append(Bullet(
                        player.rect.centerx + spawn_offset.x,
                        player.rect.centery + spawn_offset.y,
                        target_pos.x,
                        target_pos.y,
                        is_piercing,
                        guidance_level=player.guidance_level
                    ))
            shoot_cooldown = 30 if is_piercing else player.shoot_delay
            player.consume_current_ammo()
            play_sound("shoot")

        if shoot_cooldown > 0: shoot_cooldown -= 1
        player.update()

        if player.regen_level > 0 and player.hp < player.max_hp:
            player.regen_progress += 0.01 * player.regen_level
            if player.regen_progress >= 1:
                heal = int(player.regen_progress)
                player.hp = min(player.max_hp, player.hp + heal)
                player.regen_progress -= heal
        else:
            player.regen_progress = 0
        
        if player.is_dashing: trails.append(DashTrail(player.rect.centerx, player.rect.centery, player.size))
        for t in trails[:]:
            t.update()
            if t.life <= 0: trails.remove(t)
            
        for b in bullets[:]:
            b.update()
            if not pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT).inflate(500, 500).colliderect(b.rect): bullets.remove(b)
            
        for eb in enemy_bullets[:]:
            eb.update()
            if not pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT).inflate(500, 500).colliderect(eb.rect): enemy_bullets.remove(eb)
            
        for e in enemies:
            e.update(player.pos)
            e.emit_attacks(enemy_bullets, player.pos)
        for p in particles[:]:
            p.update()
            if p.timer <= 0: particles.remove(p)

        if boss_active:
            boss.update(player.pos, bullets) 
            boss.emit_attacks(enemy_bullets)

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
                if not boss.can_take_damage():
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

        if player.aura_level > 0:
            aura_radius = 95 + player.aura_level * 25
            aura_damage = 0.015 * player.aura_level
            for e in enemies[:]:
                if player.pos.distance_to(e.pos) <= aura_radius:
                    if e.shield > 0:
                        shield_damage = min(e.shield, aura_damage)
                        e.shield -= shield_damage
                        aura_damage_left = aura_damage - shield_damage
                    else:
                        aura_damage_left = aura_damage
                    e.hp -= aura_damage_left
                    if random.random() < 0.08:
                        particles.append(Particle(e.pos.x, e.pos.y, BLUE))
                    if e.hp <= 0:
                        for _ in range(8 if e.is_elite else 4): particles.append(Particle(e.pos.x, e.pos.y, e.color))
                        if random.random() < e.exp_drop_chance:
                            gems.append(Gem(e.pos.x, e.pos.y))
                        if random.random() < e.health_drop_chance:
                            health_packs.append(HealthPack(e.pos.x, e.pos.y, heal_amount=40 if e.is_elite else 25))
                        enemies.remove(e)

        def player_take_damage(dmg):
            if player.invincible_timer <= 0 and not player.is_dashing:
                damage = max(1, dmg - player.damage_reduction)
                shield_damage = min(player.shield, damage)
                player.shield -= shield_damage
                player.shield_regen_timer = player.shield_regen_delay
                player.hp -= damage - shield_damage
                player.invincible_timer = player.invincible_duration 
                play_sound("hurt")
                
                if player.hp <= 0:
                    global game_state
                    game_state = "GAME_OVER"
                    play_sound("gameover")  
                    stop_sound("boss_bgm")  

        for e in enemies:
            if e.combat_type == "melee" and player.rect.colliderect(e.rect):
                player_take_damage(e.damage)
        for eb in enemy_bullets[:]:
            if player.rect.colliderect(eb.rect):
                player_take_damage(25)
                if eb in enemy_bullets: enemy_bullets.remove(eb)
        if boss_active and boss.state != "DEFEAT" and player.rect.colliderect(boss.rect):
            player_take_damage(boss.collision_damage) 

        for g in gems[:]:
            g.update(player.pos, player.magnet_radius)
            if player.rect.colliderect(g.rect):
                gems.remove(g)
                player.exp += int(15 * player.exp_multiplier)
                play_sound("exp") 
                
                if player.exp >= player.max_exp:
                    player.level += 1; player.exp = 0; player.max_exp = int(player.max_exp * 1.25)
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
    camera = get_camera_offset()
    screen.fill(BLACK)
    draw_map_bounds(screen, camera)
    
    for g in gems: g.draw(screen, camera)
    for hp in health_packs: hp.draw(screen, camera)
    for p in particles: p.draw(screen, camera)
    for b in bullets: b.draw(screen, camera)
    for eb in enemy_bullets: eb.draw(screen, camera) 
    for e in enemies: e.draw(screen, camera)
    for t in trails: t.draw(screen, camera)
    
    if boss_active: boss.draw(screen, camera) 
    player.draw(screen, camera)
    
<<<<<<< HEAD
    # UI 面板
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

    pygame.draw.rect(screen, GRAY, (20, 70, 200, 12))
    shield_ratio = max(0, player.shield) / player.max_shield
    pygame.draw.rect(screen, BLUE, (20, 70, 200 * shield_ratio, 12))
    screen.blit(font.render("護盾", True, WHITE), (230, 62))

    pygame.draw.rect(screen, GRAY, (20, 95, 150, 10))
    pygame.draw.rect(screen, ORANGE, (20, 95, 150 * (player.stamina / player.max_stamina), 10))
    # 顯示體力
    screen.blit(font.render("體力", True, WHITE), (180, 87))

    if game_mode == CHALLENGE_MODE:
        mode_txt = small_font.render("挑戰模式", True, RED)
        rifle_color = YELLOW if player.current_weapon() == "pistol" else WHITE
        sniper_color = YELLOW if player.current_weapon() == "sniper" else WHITE
        rifle_txt = small_font.render(f"步槍: {player.pistol_ammo}/{player.pistol_mag_size}", True, rifle_color)
        sniper_txt = small_font.render(f"狙擊: {player.sniper_ammo}/{player.sniper_mag_size}", True, sniper_color)
        screen.blit(mode_txt, (20, 112))
        screen.blit(rifle_txt, (20, 140))
        screen.blit(sniper_txt, (20, 166))
        if player.reload_timer > 0:
            reload_ratio = 1 - player.reload_timer / player.reload_duration
            reload_bar = pygame.Rect(20, 194, 170, 10)
            pygame.draw.rect(screen, GRAY, reload_bar)
            pygame.draw.rect(screen, YELLOW, (reload_bar.x, reload_bar.y, int(reload_bar.width * reload_ratio), reload_bar.height))
            reload_name = "狙擊" if player.reloading_weapon == "sniper" else "步槍"
            reload_txt = small_font.render(f"{reload_name}換彈中", True, YELLOW)
            screen.blit(reload_txt, (200, 182))

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
            entrance_text = font.render(boss.get_intro_title(), True, YELLOW)
            screen.blit(entrance_text, (WIDTH//2 - entrance_text.get_width()//2, HEIGHT//2 - 200))
            
            # 顯示警告文本
            warning_lines = boss.get_intro_lines()
            for i, line in enumerate(warning_lines):
                warning = font.render(line, True, RED)
                screen.blit(warning, (WIDTH//2 - warning.get_width()//2, HEIGHT//2 - 150 + i * 40))
        elif boss_warning_timer > 0:
            warning_txt = font.render(f"⚠️ {boss.name} 出現！觀察型態變化", True, RED)
            screen.blit(warning_txt, (WIDTH//2 - warning_txt.get_width()//2, HEIGHT - 90))
        else:
            state_message, state_color = boss.get_state_message()
            state_txt = font.render(state_message, True, state_color)
            screen.blit(state_txt, (WIDTH//2 - state_txt.get_width()//2, HEIGHT - 90))
        draw_boss_direction_arrow(screen, boss, camera)

    if game_state == "LEVEL_UP":
        screen.blit(dim_surface, (0, 0)) 
        title = large_font.render("升級！選擇強化後按確認", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        for i, card in enumerate(cards):
            if i >= len(current_upgrade_choices):
                continue
            upgrade = upgrade_options[current_upgrade_choices[i]]
            is_selected = selected_upgrade_position == i
            base_color = CARD_TYPE_COLORS.get(upgrade.get("type"), CARD_COLOR)
            hover_color = tuple(min(255, c + 35) for c in base_color)
            selected_color = tuple(min(255, c + 65) for c in base_color)
            color = selected_color if is_selected else hover_color if card.collidepoint(pygame.mouse.get_pos()) else base_color
            pygame.draw.rect(screen, color, card, border_radius=10)
            border_color = YELLOW if is_selected else WHITE
            border_width = 6 if is_selected else 3
            pygame.draw.rect(screen, border_color, card, border_width, border_radius=10) 

            type_label = CARD_TYPE_LABELS.get(upgrade.get("type"), "")
            if type_label:
                label_txt = small_font.render(type_label, True, WHITE)
                label_bg = pygame.Rect(card.centerx - 42, card.y + 18, 84, 28)
                pygame.draw.rect(screen, (20, 20, 28), label_bg, border_radius=8)
                pygame.draw.rect(screen, WHITE, label_bg, 1, border_radius=8)
                screen.blit(label_txt, (label_bg.centerx - label_txt.get_width()//2, label_bg.centery - label_txt.get_height()//2))
            
            # 卡牌標題
            opt_title = font.render(upgrade["title"], True, WHITE)
            screen.blit(opt_title, (card.centerx - opt_title.get_width()//2, card.y + 65))
            
            # 卡牌敘述 (現在分為兩行自動置中)
            desc1 = font.render(upgrade["desc"][0], True, YELLOW)
            desc2 = font.render(upgrade["desc"][1], True, YELLOW)
            screen.blit(desc1, (card.centerx - desc1.get_width()//2, card.y + 125))
            screen.blit(desc2, (card.centerx - desc2.get_width()//2, card.y + 165))
        
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

        exit_color = RED if exit_button.collidepoint(mouse_pos) else (150, 50, 50)
        pygame.draw.rect(screen, exit_color, exit_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, exit_button, 3, border_radius=10)
        exit_txt = font.render("退出遊戲", True, WHITE)
        screen.blit(exit_txt, (
            exit_button.centerx - exit_txt.get_width()//2,
            exit_button.centery - exit_txt.get_height()//2
        ))
        
        # 操作說明 (更好的佈局)
        controls_title = font.render("操作說明:", True, YELLOW)
        screen.blit(controls_title, (WIDTH//2 - controls_title.get_width()//2, HEIGHT//2 + 255))
        
        controls = [
            "移動: WASD",
            "步槍模式: 滑鼠左鍵",
            "狙擊模式: 滑鼠右鍵", 
            "衝刺: space鍵",
            "暫停: ESC鍵",
            "挑戰模式換彈: R鍵",
            "升級選單: 升級後點擊選項",
        ]
        
        for i, control in enumerate(controls):
            control_txt = font.render(control, True, GRAY)
            y_pos = HEIGHT//2 + 295 + i * 32
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
        version_txt = font.render("v1.367", True, GRAY)
        screen.blit(version_txt, (WIDTH - version_txt.get_width() - 20, HEIGHT - version_txt.get_height() - 20))

        if show_changelog:
            draw_changelog_popup(screen)

    elif game_state == "DIFFICULTY":
        screen.fill(BLACK)
        for i in range(100):
            x = (i * 37) % WIDTH
            y = (i * 23) % HEIGHT
            brightness = 100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)

        title = large_font.render("選擇難易度", True, YELLOW)
        subtitle = font.render("Boss 戰會清空小怪，專心迎戰核心威脅", True, GRAY)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 235))
        screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//2 - 180))

        mouse_pos = pygame.mouse.get_pos()
        normal_hovered = normal_button.collidepoint(mouse_pos)
        challenge_hovered = challenge_button.collidepoint(mouse_pos)
        normal_color = (55, 125, 185) if normal_hovered else (30, 70, 115)
        challenge_color = (190, 55, 70) if challenge_hovered else (115, 35, 50)
        pygame.draw.rect(screen, normal_color, normal_button, border_radius=10)
        pygame.draw.rect(screen, YELLOW if normal_hovered else WHITE, normal_button, 4 if normal_hovered else 3, border_radius=10)
        pygame.draw.rect(screen, challenge_color, challenge_button, border_radius=10)
        pygame.draw.rect(screen, YELLOW if challenge_hovered else WHITE, challenge_button, 4 if challenge_hovered else 3, border_radius=10)

        normal_txt = large_font.render("普通", True, WHITE)
        normal_desc = small_font.render("標準節奏，完整強化池", True, WHITE)
        screen.blit(normal_txt, (normal_button.centerx - normal_txt.get_width()//2, normal_button.y + 28))
        screen.blit(normal_desc, (normal_button.centerx - normal_desc.get_width()//2, normal_button.y + 88))
        normal_lines = [
            "敵人強度：標準",
            "彈藥：無需換彈",
            "適合熟悉卡牌與 Boss 節奏"
        ]
        for i, line in enumerate(normal_lines):
            line_txt = small_font.render(line, True, (210, 225, 240))
            screen.blit(line_txt, (normal_button.x + 42, normal_button.y + 132 + i * 28))

        challenge_txt = large_font.render("挑戰", True, WHITE)
        challenge_desc = small_font.render("敵人 1.75 倍，啟用彈匣", True, WHITE)
        screen.blit(challenge_txt, (challenge_button.centerx - challenge_txt.get_width()//2, challenge_button.y + 28))
        screen.blit(challenge_desc, (challenge_button.centerx - challenge_desc.get_width()//2, challenge_button.y + 88))
        challenge_lines = [
            "步槍 45 發 / 狙擊 7 發",
            "打完自動換彈，也可按 R",
            "追加挑戰限定卡牌"
        ]
        for i, line in enumerate(challenge_lines):
            line_txt = small_font.render(line, True, (255, 220, 220))
            screen.blit(line_txt, (challenge_button.x + 42, challenge_button.y + 132 + i * 28))

        detail_lines = [
            "選定難度後本局固定，重新開始會沿用目前難度。",
            "回到主選單後可重新選擇。"
        ]
        for i, line in enumerate(detail_lines):
            detail_txt = small_font.render(line, True, GRAY)
            screen.blit(detail_txt, (WIDTH//2 - detail_txt.get_width()//2, HEIGHT//2 + 205 + i * 26))

        back_color = BLUE if difficulty_back_button.collidepoint(mouse_pos) else (50, 100, 150)
        pygame.draw.rect(screen, back_color, difficulty_back_button, border_radius=10)
        pygame.draw.rect(screen, WHITE, difficulty_back_button, 3, border_radius=10)
        back_txt = font.render("返回", True, WHITE)
        screen.blit(back_txt, (
            difficulty_back_button.centerx - back_txt.get_width()//2,
            difficulty_back_button.centery - back_txt.get_height()//2
        ))

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

        draw_pause_upgrade_log(screen)
    
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

pygame.quit()
