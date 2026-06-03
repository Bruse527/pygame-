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
    def __init__(self, size):
        self.size = size
        self.pos = pygame.math.Vector2(0, 0)
        self.rect = pygame.Rect(0, 0, self.size, self.size)
    def update(self, target_pos):
        direction = target_pos - self.pos
        if direction.length() > 0: direction.normalize_ip()
        self.pos += direction * self.speed
        self.rect.center = (round(self.pos.x), round(self.pos.y))
    def draw(self, surface): pygame.draw.rect(surface, RED, self.rect)

class Boss:
    def __init__(self):
        self.size = 60  # 必須先定義 size
        self.pos = pygame.math.Vector2(WIDTH/2, -60) 
        # 修正座標限制邏輯
        self.pos.y = max(self.size, min(HEIGHT-self.size, self.pos.y))[cite: 1]
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.max_hp = 500
        self.hp = 500
          # 初始血量建議設為滿血
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
    # 1. 事件處理 (Event Handling)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
        
        if game_state == "GAME_OVER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r: 
                reset_game()
        
        elif game_state == "LEVEL_UP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, card in enumerate(cards):
                    if card.collidepoint(event.pos): 
                        apply_upgrade(i)
                        break
        
        elif game_state == "PLAYING":
            if event.type == SPAWN_ENEMY_EVENT: 
                enemies.append(Enemy())
            # 武器切換 (按 E 鍵)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                player.current_weapon_idx = (player.current_weapon_idx + 1) % len(player.weapons)
                play_sound("exp")

    # 2. 遊戲邏輯更新 (僅在 PLAYING 狀態)
    if game_state == "PLAYING":
        # 更新玩家與物件
        player.update()
        
        # --- 射擊邏輯修正 ---
        mouse_btns = pygame.mouse.get_pressed()
        current_wep = player.weapons[player.current_weapon_idx]
        
        if mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            # 根據武器類型產生子彈[cite: 1]
            if current_wep.bullet_type == "shotgun":
                for i in range(-2, 3):
                    target_vec = pygame.math.Vector2(mouse_x - player.pos.x, mouse_y - player.pos.y)
                    if target_vec.length() > 0:
                        rotated_vec = target_vec.rotate(i * 15)
                        bullets.append(Bullet(player.rect.centerx, player.rect.centery, 
                                             player.pos.x + rotated_vec.x, player.pos.y + rotated_vec.y, False))
            elif current_wep.bullet_type == "flamethrower":
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, 
                                     mouse_x + random.randint(-40, 40), mouse_y + random.randint(-40, 40), False))
            else:
                is_p = (current_wep.bullet_type in ["laser", "piercing"])
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, mouse_x, mouse_y, is_p))

            shoot_cooldown = current_wep.shoot_delay
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
        for event in pygame.event.get():
    if event.type == pygame.QUIT: 
        running = False
    
    if game_state == "PLAYING":
        # 偵測按下 E 鍵切換武器
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            player.current_weapon_idx = (player.current_weapon_idx + 1) % len(player.weapons)
            # 切換武器的音效
            play_sound("exp")
# --- 遊戲主迴圈射擊判斷 ---
while game_state == "PLAYING":
    mouse_btns = pygame.mouse.get_pressed()
current_wep = player.weapons[player.current_weapon_idx]

iif mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing:
    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    # 根據不同的子彈類型發動攻擊
    if current_wep.bullet_type == "shotgun":
        # 散彈槍：一次發射 5 顆扇形子彈
        for i in range(-2, 3):
            # 計算偏移後的目標位置
            angle_offset = i * 0.2  # 弧度偏移
            target_vec = pygame.math.Vector2(mouse_x - player.pos.x, mouse_y - player.pos.y)
            if target_vec.length() > 0:
                # 旋轉向量來達成扇形效果
                rotated_vec = target_vec.rotate(i * 15) 
                final_target = player.pos + rotated_vec
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, 
                                     final_target.x, final_target.y, False))
                                     
    elif current_wep.bullet_type == "flamethrower":
        # 火焰噴射器：極快射速，帶隨機偏移且壽命短 (可自訂子彈速度)
        offset_x = random.randint(-40, 40)
        offset_y = random.randint(-40, 40)
        bullets.append(Bullet(player.rect.centerx, player.rect.centery, 
                             mouse_x + offset_x, mouse_y + offset_y, False))
                             
    elif current_wep.bullet_type == "laser" or current_wep.bullet_type == "piercing":
        # 雷射/穿透類：直接賦予子彈穿透屬性
        bullets.append(Bullet(player.rect.centerx, player.rect.centery, 
                             mouse_x, mouse_y, True))
                             
    else:
        # 一般子彈 (如手槍、機槍、電漿發射器等)
        bullets.append(Bullet(player.rect.centerx, player.rect.centery, 
                             mouse_x, mouse_y, False))

    # 使用武器自定義的冷卻時間
    shoot_cooldown = current_wep.shoot_delay
    play_sound("shoot")[cite: 1]

    # --- 畫面繪製 ---
    screen.fill(BLACK) # 清除畫面[cite: 1]
    
    # 按照順序繪製物件 (背景物件先畫，玩家與 UI 後畫)
    for g in gems: g.draw(screen)[cite: 1]
    for p in particles: p.draw(screen)[cite: 1]
    for t in trails: t.draw(screen)[cite: 1]
    for b in bullets: b.draw(screen)[cite: 1]
    for eb in enemy_bullets: eb.draw(screen)[cite: 1]
    for e in enemies: e.draw(screen)[cite: 1]
    
    if boss_active and boss: # 確保 boss 存在再繪製
        boss.draw(screen)[cite: 1]

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
    #顯示武器種類
    # 顯示武器名稱 (假設武器物件有 bullet_type 屬性)
    current_wep = player.weapons[player.current_weapon_idx]
    weapon_text = font.render(f"武器: {current_wep.bullet_type} (E 切換)", True, WHITE)
    screen.blit(weapon_text, (20, 100))[cite: 1]

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

    pygame.display.flip() # 更新顯示[cite: 1]
    clock.tick(FPS)       # 控制幀率[cite: 1]
>>>>>>> 5fe3c3b9a6cb6e15508d0cc26521ee2ec490b8fd
