import pygame
import random
import math
import os

# --- 1. 遊戲初始化與音效設定 ---
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("驅魔人")
clock = pygame.time.Clock()
FPS = 60

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
        self.pos = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
        self.size = 30
        self.base_speed = 5
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        
        self.exp, self.level, self.max_exp = 0, 1, 100
        self.magnet_radius, self.shoot_delay = 60, 8
        self.is_aiming = False
        
        self.max_hp, self.hp = 100, 100
        self.invincible_timer = 0  
        
        self.max_stamina, self.stamina = 100, 100
        self.dash_cost, self.stamina_regen = 35, 0.5   
        
        self.is_dashing = False
        self.dash_speed, self.dash_duration = 22, 8
        self.dash_timer = 0
        self.dash_direction = pygame.math.Vector2(0, 0)

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

        if keys[pygame.K_LSHIFT] and not self.is_dashing and self.stamina >= self.dash_cost:
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
            
        self.pos.x, self.pos.y = max(0, min(WIDTH, self.pos.x)), max(0, min(HEIGHT, self.pos.y))
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
    def __init__(self):
        self.size, self.speed = 25, random.uniform(1.5, 3.5)
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
    def draw(self, surface): pygame.draw.rect(surface, RED, self.rect)

class Boss:
    def __init__(self):
        self.pos = pygame.math.Vector2(WIDTH/2, -60) 
        self.size = 60
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.max_hp = 1500
        self.hp = 1500
        self.speed = 3.5
        
        self.state = "EVADE" 
        self.state_timer = 0
        self.color = YELLOW

    def update(self, player_pos, bullets):
        self.state_timer += 1
        
        if self.state == "EVADE":
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
                
        self.pos.x = max(self.size, min(WIDTH-self.size, self.pos.x))
        self.pos.y = max(self.size, min(HEIGHT-self.size, self.pos.y))
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def draw(self, surface):
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

def apply_upgrade(choice):
    global game_state
    if choice == 0: player.max_hp += 50; player.hp += 50 
    elif choice == 1: player.shoot_delay = max(2, player.shoot_delay - 2) 
    elif choice == 2: player.stamina_regen += 0.3        
    game_state = "PLAYING"             

# ==========================================
# 🛑 中文化升級選項系統 (用陣列方便換行)
# ==========================================
upgrade_options =[
    {"title": "生命躍升", "desc": ["最大血量 +50", "並恢復當前血量"]},
    {"title": "超頻運轉", "desc": ["機槍射速提升", "子彈連發加快"]},
    {"title": "能量飲料", "desc": ["體力恢復加快", "衝刺更加頻繁"]}
]
cards =[pygame.Rect(100, 200, 160, 240), pygame.Rect(320, 200, 160, 240), pygame.Rect(540, 200, 160, 240)]

# --- 遊戲狀態重置系統 ---
def reset_game():
    global player, bullets, enemy_bullets, enemies, particles, gems, trails
    global boss, boss_active, boss_defeated, game_state
    player = Player()
    bullets, enemy_bullets, enemies, particles, gems, trails = [], [], [], [], [],[]
    boss = None
    boss_active = False
    boss_defeated = False
    stop_sound("boss_bgm")
    game_state = "PLAYING"

reset_game()
shoot_cooldown = 0 
SPAWN_ENEMY_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY_EVENT, 600)
dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
dim_surface.fill((0, 0, 0, 180))

# --- 4. 遊戲主迴圈 ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: reset_game()
        elif game_state == "LEVEL_UP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, card in enumerate(cards):
                    if card.collidepoint(event.pos): apply_upgrade(i); break
        elif game_state == "PLAYING":
            if event.type == SPAWN_ENEMY_EVENT: enemies.append(Enemy())

    if game_state == "PLAYING":
        if player.level >= 3 and not boss_active and not boss_defeated:
            boss = Boss()
            boss_active = True
            play_sound("boss_bgm", loop=-1) 

        mouse_btns = pygame.mouse.get_pressed()
        if mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            is_piercing = player.is_aiming 
            bullets.append(Bullet(player.rect.centerx, player.rect.centery, mouse_x, mouse_y, is_piercing))
            shoot_cooldown = 30 if is_piercing else player.shoot_delay
            play_sound("shoot")

        if shoot_cooldown > 0: shoot_cooldown -= 1
        player.update()
        
        if player.is_dashing: trails.append(DashTrail(player.rect.centerx, player.rect.centery, player.size))
        for t in trails[:]:
            t.update()
            if t.life <= 0: trails.remove(t)
            
        for b in bullets[:]:
            b.update()
            if not screen.get_rect().colliderect(b.rect): bullets.remove(b)
            
        for eb in enemy_bullets[:]:
            eb.update()
            if not screen.get_rect().colliderect(eb.rect): enemy_bullets.remove(eb)
            
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
                boss.state = "EVADE"
                play_sound("shoot")

        for b in bullets[:]:
            hit_something = False
            for e in enemies[:]:
                if b.rect.colliderect(e.rect):
                    for _ in range(10): particles.append(Particle(e.pos.x, e.pos.y, RED))
                    if random.random() < 0.4: gems.append(Gem(e.pos.x, e.pos.y))
                    enemies.remove(e)
                    hit_something = True
                    play_sound("hit")
            
            if boss_active and b.rect.colliderect(boss.rect):
                hit_something = True
                if boss.state == "EVADE":
                    for _ in range(5): particles.append(Particle(boss.pos.x, boss.pos.y, GRAY))
                else:
                    damage = 30 if b.is_piercing else 8
                    boss.hp -= damage
                    for _ in range(8): particles.append(Particle(boss.pos.x, boss.pos.y, YELLOW))
                    play_sound("hit")
                    
                    if boss.hp <= 0:
                        boss_active = False
                        boss_defeated = True
                        stop_sound("boss_bgm") 
                        for _ in range(40): gems.append(Gem(boss.pos.x + random.randint(-60,60), boss.pos.y + random.randint(-60,60)))
                        for _ in range(50): particles.append(Particle(boss.pos.x, boss.pos.y, YELLOW))
                        
            if hit_something and not b.is_piercing and b in bullets: bullets.remove(b)

        def player_take_damage(dmg):
            if player.invincible_timer <= 0 and not player.is_dashing:
                player.hp -= dmg
                player.invincible_timer = 60 
                play_sound("hurt")
                
                if player.hp <= 0:
                    global game_state
                    game_state = "GAME_OVER"
                    play_sound("gameover")  
                    stop_sound("boss_bgm")  

        for e in enemies:
            if player.rect.colliderect(e.rect): player_take_damage(20)
        for eb in enemy_bullets[:]:
            if player.rect.colliderect(eb.rect):
                player_take_damage(25)
                if eb in enemy_bullets: enemy_bullets.remove(eb)
        if boss_active and player.rect.colliderect(boss.rect):
            player_take_damage(40) 

        for g in gems[:]:
            g.update(player.pos, player.magnet_radius)
            if player.rect.colliderect(g.rect):
                gems.remove(g)
                player.exp += 15
                play_sound("exp") 
                
                if player.exp >= player.max_exp:
                    player.level += 1; player.exp = 0; player.max_exp = int(player.max_exp * 1.5)
                    game_state = "LEVEL_UP" 
                    play_sound("levelup") 

    # --- 畫面繪製 ---
    screen.fill(BLACK)
    
    for g in gems: g.draw(screen)
    for p in particles: p.draw(screen)
    for b in bullets: b.draw(screen)
    for eb in enemy_bullets: eb.draw(screen) 
    for e in enemies: e.draw(screen)
    for t in trails: t.draw(screen)
    
    if boss_active: boss.draw(screen) 
    player.draw(screen)
    
    # === UI 面板 (中文化) ===
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
    if boss_active:
        bar_w = WIDTH - 100
        pygame.draw.rect(screen, GRAY, (50, HEIGHT - 40, bar_w, 20))
        pygame.draw.rect(screen, YELLOW, (50, HEIGHT - 40, bar_w * (max(0, boss.hp) / boss.max_hp), 20))
        # Boss 警告
        boss_txt = font.render("警告：偵測到極度危險異常實體", True, WHITE)
        screen.blit(boss_txt, (WIDTH//2 - boss_txt.get_width()//2, HEIGHT - 70))

    if game_state == "LEVEL_UP":
        screen.blit(dim_surface, (0, 0)) 
        title = large_font.render("升級！請選擇一項強化", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        for i, card in enumerate(cards):
            color = BLUE if card.collidepoint(pygame.mouse.get_pos()) else CARD_COLOR
            pygame.draw.rect(screen, color, card, border_radius=10)
            pygame.draw.rect(screen, WHITE, card, 3, border_radius=10) 
            
            # 卡牌標題
            opt_title = font.render(upgrade_options[i]["title"], True, WHITE)
            screen.blit(opt_title, (card.centerx - opt_title.get_width()//2, card.y + 30))
            
            # 卡牌敘述 (現在分為兩行自動置中)
            desc1 = font.render(upgrade_options[i]["desc"][0], True, YELLOW)
            desc2 = font.render(upgrade_options[i]["desc"][1], True, YELLOW)
            screen.blit(desc1, (card.centerx - desc1.get_width()//2, card.y + 110))
            screen.blit(desc2, (card.centerx - desc2.get_width()//2, card.y + 150))

    elif game_state == "GAME_OVER":
        screen.blit(dim_surface, (0, 0))
        game_over_txt = large_font.render("Game Over", True, RED)
        restart_txt = font.render("按下 'R' 鍵重新開始", True, WHITE)
        
        # 自動置中
        screen.blit(game_over_txt, (WIDTH//2 - game_over_txt.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_txt, (WIDTH//2 - restart_txt.get_width()//2, HEIGHT//2 + 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()