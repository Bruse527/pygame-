import pygame
import random
import math
import os
import ctypes
import sys

# 初始化遊戲跟音效
pygame.init()
pygame.mixer.init()

# 自動切換到英文鍵盤輸入（僅適用於 Windows）
def switch_to_english_input():
    try:
        user32 = ctypes.windll.user32
        hkl = user32.LoadKeyboardLayoutW("00000409", 1)
        if hkl:
            user32.ActivateKeyboardLayout(hkl, 0)
    except Exception:
        pass

switch_to_english_input()

# 設定視窗與開放世界大小
WIDTH, HEIGHT = 1024, 768
MAP_WIDTH, MAP_HEIGHT = 4200, 2600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("末日肉鴿生存 - 3D視角升級版")
clock = pygame.time.Clock()
FPS = 60

# 全域相機與畫面震動變數
camera_x, camera_y = 0, 0
shake_x, shake_y = 0, 0
screen_shake = 0  
camera_angle = 0.0  # 相機旋轉角度
view_mode = "ISOMETRIC"  # 紀錄當前視角模式 ISOMETRIC 45度、FPS 平視、CLASSIC 2D防暈。

def project_3d(world_x, world_y, world_z=0):
    dx = world_x - player.x
    dy = world_y - player.y
    
    if view_mode == "CLASSIC":
        # 防暈模式：完全不旋轉、不壓縮 Y 軸
        screen_x = WIDTH / 2 + dx + shake_x
        screen_y = HEIGHT / 2 + dy - world_z + shake_y
        return int(screen_x), int(screen_y), dy
    # FPS 和 ISOMETRIC 模式需要先旋轉座標，再根據模式壓縮 Y 軸
    cos_a = math.cos(-camera_angle)
    sin_a = math.sin(-camera_angle)
    rot_x = dx * cos_a - dy * sin_a
    rot_y = dx * sin_a + dy * cos_a
    
    if view_mode == "FPS":
        screen_x = WIDTH / 2 + rot_x + shake_x
        screen_y = HEIGHT * 0.65 + (rot_y * 0.3) - world_z + shake_y
    else: # ISOMETRIC
        screen_x = WIDTH / 2 + rot_x + shake_x
        screen_y = HEIGHT / 2 + (rot_y * 0.5) - world_z + shake_y
    return int(screen_x), int(screen_y), rot_y

def unproject_3d(screen_x, screen_y):
    rx = screen_x - WIDTH / 2 - shake_x
    # 根據視角模式逆推 Y 軸距離
    if view_mode == "CLASSIC":
        # 防暈模式直接逆推，無旋轉無壓縮
        ry = screen_y - HEIGHT / 2 - shake_y
        return player.x + rx, player.y + ry
    # FPS 模式 Y 軸壓增加縮比，ISOMETRIC 模式則是 0.5 的壓縮
    if view_mode == "FPS":
        ry = (screen_y - HEIGHT * 0.65 - shake_y) / 0.3
    else:
        ry = (screen_y - HEIGHT / 2 - shake_y) / 0.5
    # 逆旋轉回世界座標
    cos_a = math.cos(camera_angle)
    sin_a = math.sin(camera_angle)
    dx = rx * cos_a - ry * sin_a
    dy = rx * sin_a + ry * cos_a
    return player.x + dx, player.y + dy

# 顏色定義 (賽博龐克風格色盤)
BLACK = (5, 6, 8)                # 極深陰影黑
BLUE = (0, 230, 255)             # 霓虹青
RED = (255, 40, 80)              # 霓虹血紅
YELLOW = (255, 210, 0)           # 刺眼高壓黃
PURPLE = (200, 40, 255)          # 迷幻紫
DARK_PURPLE = (70, 20, 100)
WHITE = (240, 245, 255)          # 泛白高光
GRAY = (50, 55, 65)              # 黯淡金屬灰
GREEN = (0, 255, 150)            # 放射綠
ORANGE = (255, 100, 20)          # 餘燼橘
CYAN = (0, 255, 255)

SCRAP_COLOR = (180, 190, 200)
CARD_COLOR = (20, 22, 28)
CARD_TYPE_COLORS = {"attack": (120, 35, 45), "support": (35, 75, 130), "life": (35, 110, 65)}
CARD_TYPE_LABELS = {"attack": "攻擊", "support": "支援", "life": "生命"}
SHIELD_COLOR, EXP_COLOR, HP_COLOR = (0, 200, 255), (150, 255, 0), (255, 50, 80)

# 字體設定
CHINESE_FONTS = "microsoftjhenghei,pingfangtc,stheiti,simhei"
font = pygame.font.SysFont(CHINESE_FONTS, 24)
large_font = pygame.font.SysFont(CHINESE_FONTS, 42)
small_font = pygame.font.SysFont(CHINESE_FONTS, 18)
tiny_font = pygame.font.SysFont(CHINESE_FONTS, 14)

# 資源管理
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, "images")
AUDIO_DIR = os.path.join(BASE_DIR, "audio")

if not os.path.exists(IMAGE_DIR): os.makedirs(IMAGE_DIR)
if not os.path.exists(AUDIO_DIR): os.makedirs(AUDIO_DIR)

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
    frames = []
    for file in sorted(os.listdir(folder_path)):
        if file.endswith((".png", ".jpg")):
            img = pygame.image.load(os.path.join(folder_path, file)).convert_alpha()
            frames.append(pygame.transform.scale(img, size))
    animations[name] = frames if frames else None

# 載入單張靜態圖片
load_image("bg", "bg.png", (WIDTH, HEIGHT))
load_image("drop_EXP", "drop_exp.png", (20, 20))
load_image("chest_NORMAL_CLOSED", "chest_normal_closed.png", (50, 40))
load_image("chest_NORMAL_OPEN", "chest_normal_open.png", (50, 40))
load_image("chest_LOCKED_CLOSED", "chest_locked_closed.png", (50, 40))
load_image("chest_LOCKED_OPEN", "chest_locked_open.png", (50, 40))

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
load_animation("boss_CYAN", "boss_cyan", (100, 100))
load_animation("dummy", "dummy", (40, 60)) 

# 載入地板、地堡牆壁與撤離點 (圖片或動畫)
load_image("floor", "floor.png", (MAP_WIDTH, MAP_HEIGHT))
load_image("bunker_wall", "bunker_wall.png")
load_animation("extraction_point", "extraction_point", (150, 150))
load_image("extraction_point", "extraction_point.png", (150, 150))


def load_sound(name, filename):
    try:
        sound_path = os.path.join(AUDIO_DIR, filename) 
        if os.path.exists(sound_path):
            sounds[name] = pygame.mixer.Sound(sound_path)
            sounds[name].set_volume(0.3)
        else:
            sounds[name] = None
    except:
        sounds[name] = None 

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
        sound_path = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(sound_path):
            sounds[weapon_key] = pygame.mixer.Sound(sound_path)
            sounds[weapon_key].set_volume(0.3)
        else:
            sounds[weapon_key] = sounds.get(fallback_key)
    except:
        sounds[weapon_key] = sounds.get(fallback_key)

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

bgm_path = os.path.join(AUDIO_DIR, "bgm.mp3")
if os.path.exists(bgm_path):
    pygame.mixer.music.load(bgm_path)
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(loops=-1)

def play_sound(name, loop=0):
    if sounds.get(name): sounds[name].play(loops=loop)

def stop_sound(name):
    if sounds.get(name): sounds[name].stop()


# ========================== UI 函式 ==========================
def draw_ui_panel(surface, rect, title, accent_color):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (18, 20, 26, 245), panel.get_rect(), border_radius=12)
    pygame.draw.rect(panel, (50, 55, 65), panel.get_rect(), 2, border_radius=12)
    header = pygame.Rect(0, 0, rect.width, 45)
    pygame.draw.rect(panel, (30, 34, 42, 255), header, border_top_left_radius=12, border_top_right_radius=12)
    pygame.draw.line(panel, accent_color, (0, 45), (rect.width, 45), 2)
    surface.blit(panel, (rect.x, rect.y))
    
    t_surf = large_font.render(title, True, accent_color)
    surface.blit(t_surf, (rect.centerx - t_surf.get_width()//2, rect.y + 5))

def draw_hover_button(surface, rect, text, base_color, hover_color, text_color=WHITE):
    m_pos = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(m_pos)
    color = hover_color if is_hover else base_color
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, WHITE if is_hover else GRAY, rect, 2, border_radius=8)

    t_surf = small_font.render(text, True, text_color)
    surface.blit(t_surf, (rect.centerx - t_surf.get_width() // 2, rect.centery - t_surf.get_height() // 2))
    return is_hover

def draw_item_tooltip(surface, item, m_x, m_y):
    if not item: return
    if item.type == "WEAPON":
        wep = item.weapon_obj
        tt_rect = pygame.Rect(m_x+15, m_y, 240, 95)
        if tt_rect.right > WIDTH: tt_rect.x -= 270
        if tt_rect.bottom > HEIGHT: tt_rect.y -= 105
        pygame.draw.rect(surface, (15, 18, 22), tt_rect, border_radius=8)
        c = get_rarity_color(wep.rarity)
        pygame.draw.rect(surface, c, tt_rect, 2, border_radius=8)
        surface.blit(font.render(wep.full_name, True, c), (tt_rect.x+10, tt_rect.y+10))
        surface.blit(small_font.render(f"傷害: {wep.damage}   冷卻: {wep.shoot_delay}", True, WHITE), (tt_rect.x+10, tt_rect.y+40))
        aff = ",".join(wep.affixes) if wep.affixes else "無附加詞綴"
        surface.blit(small_font.render(f"屬性: {aff}", True, YELLOW), (tt_rect.x+10, tt_rect.y+65))
    else:
        tt_rect = pygame.Rect(m_x+15, m_y, max(150, font.size(item.name)[0] + 30), 45)
        if tt_rect.right > WIDTH: tt_rect.x -= (tt_rect.width + 30)
        pygame.draw.rect(surface, (20, 22, 28), tt_rect, border_radius=6)
        pygame.draw.rect(surface, GRAY, tt_rect, 1, border_radius=6)
        surface.blit(font.render(item.name, True, WHITE), (tt_rect.x+15, tt_rect.y+10))

def draw_terminal(surface, rect, base_color, text, icon_text):
    pygame.draw.rect(surface, BLACK, rect.move(5,5), border_radius=8)
    pygame.draw.rect(surface, (45, 50, 60), rect, border_radius=8)
    s_rect = pygame.Rect(rect.x+10, rect.y+10, rect.width-20, rect.height-30)
    pygame.draw.rect(surface, (20, 22, 28), s_rect, border_radius=4)
    pulse = int(abs(math.sin(pygame.time.get_ticks()*0.003))*50)
    g_c = (min(255, base_color[0]+pulse), min(255, base_color[1]+pulse), min(255, base_color[2]+pulse))
    pygame.draw.rect(surface, g_c, s_rect, 2, border_radius=4)
    surf = font.render(icon_text, True, g_c)
    surface.blit(surf, (s_rect.centerx - surf.get_width()//2, s_rect.centery - surf.get_height()//2))
    pygame.draw.line(surface, base_color, (rect.x+15, rect.bottom-10), (rect.right-15, rect.bottom-10), 3)
    lbl = small_font.render(text, True, WHITE)
    surface.blit(lbl, (rect.centerx - lbl.get_width()//2, rect.y - 25))

def draw_terminal_billboard(surface, world_x, world_y, width, height, base_color, text, icon_text):
    sx, sy, depth = project_3d(world_x, world_y)
    if depth < -500: return 
    rect = pygame.Rect(0, 0, width, height)
    rect.center = (sx, sy)
    draw_terminal(surface, rect, base_color, text, icon_text)

def draw_minimap(surface):
    map_w, map_h = 160, 120
    m_rect = pygame.Rect(WIDTH - map_w - 20, 20, map_w, map_h)
    
    mm_surf = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
    pygame.draw.rect(mm_surf, (10, 10, 20, 180), mm_surf.get_rect(), border_radius=5)
    pygame.draw.rect(mm_surf, (50, 200, 50), mm_surf.get_rect(), 2, border_radius=5)
    surface.blit(mm_surf, (m_rect.x, m_rect.y))
    def to_mm(px, py): return m_rect.x + (px / MAP_WIDTH) * map_w, m_rect.y + (py / MAP_HEIGHT) * map_h
    if extraction_pt:
        ex, ey = to_mm(extraction_pt.x, extraction_pt.y)
        pygame.draw.circle(surface, GREEN, (int(ex), int(ey)), 4)
    if 'boss_active' in globals() and boss_active and boss:
        bx, by = to_mm(boss.x, boss.y)
        pygame.draw.circle(surface, RED, (int(bx), int(by)), 5)
    if 'lost_item' in globals() and lost_item:
        lx, ly = to_mm(lost_item.x, lost_item.y)
        p = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 4)
        pygame.draw.circle(surface, YELLOW, (int(lx), int(ly)), 4)
        pygame.draw.circle(surface, RED, (int(lx), int(ly)), 5 + p, 1)
        
    px, py = to_mm(player.x, player.y)
    pygame.draw.circle(surface, BLUE, (int(px), int(py)), 4)

def draw_boss_direction_arrow(surface, boss_obj, cam_x, cam_y):
    if not boss_obj or (hasattr(boss_obj, "state") and boss_obj.state == "DEFEAT"): return
    dx = boss_obj.x - player.x
    dy = boss_obj.y - player.y
    dist = math.hypot(dx, dy)
    
    if dist > 450:
        cos_a = math.cos(-camera_angle)
        sin_a = math.sin(-camera_angle)
        rx = dx * cos_a - dy * sin_a
        ry = dx * sin_a + dy * cos_a
        angle = math.atan2(ry * 0.5, rx)
        
        r = min(WIDTH, HEIGHT) / 2 - 60
        ax, ay = WIDTH/2 + math.cos(angle)*r, HEIGHT/2 + math.sin(angle)*r
        side = pygame.math.Vector2(math.cos(angle), math.sin(angle)).rotate(90)
        p = pygame.math.Vector2(ax, ay)
        d = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        pts = [p + d*25, p - d*10 + side*15, p - d*10 - side*15]
        pygame.draw.polygon(surface, BLACK, pts); pygame.draw.polygon(surface, RED, pts, 0); pygame.draw.polygon(surface, YELLOW, pts, 3)

def draw_lost_item_arrow(surface):
    if not ('lost_item' in globals() and lost_item): return
    dx = lost_item.x - player.x
    dy = lost_item.y - player.y
    dist = math.hypot(dx, dy)
    if dist > 400:
        cos_a = math.cos(-camera_angle)
        sin_a = math.sin(-camera_angle)
        rx = dx * cos_a - dy * sin_a
        ry = dx * sin_a + dy * cos_a
        angle = math.atan2(ry * 0.5, rx)
        
        r = min(WIDTH, HEIGHT) / 2 - 60
        ax, ay = WIDTH/2 + math.cos(angle)*r, HEIGHT/2 + math.sin(angle)*r
        side = pygame.math.Vector2(math.cos(angle), math.sin(angle)).rotate(90)
        p = pygame.math.Vector2(ax, ay)
        d = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        pts = [p + d*20, p - d*10 + side*15, p - d*10 - side*15]
        pygame.draw.polygon(surface, YELLOW, pts); pygame.draw.polygon(surface, RED, pts, 2)
        txt = small_font.render("遺失物", True, YELLOW)
        surface.blit(txt, (ax - txt.get_width()//2, ay - 35))

def draw_upgrade_summary(surface, x, y, max_items=6, title="已選強化"):
    panel_width = 240
    row_height = 26
    hidden_count = max(0, len(chosen_upgrades) - max_items)
    row_count = max(1, min(len(chosen_upgrades), max_items))
    panel_height = 40 + row_count * row_height + (row_height if hidden_count else 0)
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((18, 20, 30, 185))
    surface.blit(panel, (x, y))
    pygame.draw.rect(surface, WHITE, (x, y, panel_width, panel_height), 2, border_radius=8)

    total_count = sum(u["count"] for u in chosen_upgrades)
    title_label = f"{title} ({total_count})" if chosen_upgrades else title
    title_txt = small_font.render(title_label, True, YELLOW)
    surface.blit(title_txt, (x + 14, y + 10))

    if not chosen_upgrades:
        empty_txt = small_font.render("尚未選擇", True, GRAY)
        surface.blit(empty_txt, (x + 14, y + 40))
        return

    visible_upgrades = chosen_upgrades[-max_items:]
    for i, upgrade in enumerate(visible_upgrades):
        suffix = f" x{upgrade['count']}" if upgrade["count"] > 1 else ""
        line = small_font.render(f"{upgrade['title']}{suffix}", True, WHITE)
        surface.blit(line, (x + 14, y + 40 + i * row_height))

    if hidden_count:
        hidden_txt = small_font.render(f"還有 {hidden_count} 種...", True, GRAY)
        surface.blit(hidden_txt, (x + 14, y + 40 + len(visible_upgrades) * row_height))

def draw_player_inv_grid(surface, start_x, start_y, m_x, m_y, allow_weapons=True):
    hover_info = None
    for i in range(24):
        rect = pygame.Rect(start_x + (i%6)*58, start_y + (i//6)*58, 50, 50)
        pygame.draw.rect(surface, (25, 28, 35), rect, border_radius=6)
        pygame.draw.rect(surface, (55, 60, 70), rect, 1, border_radius=6)
        item = player.inventory[i]
        if item and not (drag_data and drag_data["source"] == "PLAYER" and drag_data["idx"] == i):
            if item.type == "WEAPON":
                if allow_weapons:
                    c = get_rarity_color(item.weapon_obj.rarity)
                    pygame.draw.circle(surface, c, rect.center, 14)
                else:
                    pygame.draw.circle(surface, (60, 60, 60), rect.center, 14)
            else:
                c = HP_COLOR if item.type == "MED" else (SCRAP_COLOR if item.type == "SCRAP" else YELLOW)
                pygame.draw.circle(surface, c, rect.center, 14)
                surface.blit(tiny_font.render(str(item.count), True, WHITE), (rect.right - 18, rect.bottom - 18))
            
            if rect.collidepoint(m_x, m_y) and not drag_data:
                hover_info = {"source": "PLAYER", "idx": i, "item": item}
                pygame.draw.rect(surface, WHITE, rect, 2, border_radius=6)
    return hover_info

def put_item_in_slot(source, idx, item):
    target_list = player.inventory if source == "PLAYER" else persistent_stats["general_stash"]
    old_item = target_list[idx]
    if old_item and old_item.type == item.type and item.type != "WEAPON":
        space = old_item.max_stack - old_item.count
        if space > 0:
            add = min(space, item.count)
            old_item.count += add
            item.count -= add
            if item.count <= 0: return None
    target_list[idx] = item
    return old_item

def open_chest(c):
    num_items = random.randint(2, 4) if c.type == "NORMAL" else random.randint(4, 7)
    for _ in range(num_items):
        rand_val = random.random()
        if rand_val < 0.2: items.append(DropItem(c.x + random.randint(-30, 30), c.y + random.randint(-30, 30), "MED"))
        elif rand_val < 0.5: items.append(DropItem(c.x + random.randint(-30, 30), c.y + random.randint(-30, 30), "SCRAP", random.randint(2, 5)))
        elif rand_val < 0.7:
            wep = generate_weapon(random.choice(list(WEAPON_TYPES.keys())), random.choices(["白", "藍", "紫", "金"], weights=[0.6, 0.3, 0.08, 0.02])[0])
            items.append(DropItem(c.x + random.randint(-30, 30), c.y + random.randint(-30, 30), "WEAPON", weapon_obj=wep))
        else: items.append(DropItem(c.x + random.randint(-30, 30), c.y + random.randint(-30, 30), "EXP", random.randint(1, 3)))
    if c.type == "LOCKED":
        items.append(DropItem(c.x, c.y + 20, "MAGNET"))
        items.append(DropItem(c.x, c.y - 20, "BOMB"))
    play_sound("exp")

def draw_changelog_popup(surface):
    rect = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 - 200, 600, 400)
    draw_ui_panel(surface, rect, "更新與修復日誌", BLUE)
    close_rect = pygame.Rect(rect.right - 45, rect.y + 10, 35, 35)
    draw_hover_button(surface, close_rect, "X", (180, 60, 60), RED, WHITE)
    logs = [
        "修復項目與優化內容:",
        "- 徹底升級：3D 地平線視角與透視網格",
        "- 徹底升級：視角與游標同步，真正的第三人稱動作射擊",
        "- 徹底升級：廣告板渲染技術 (物件永遠正立)",
        "- 徹底升級：8向人物行走動畫與DOOM式怪物翻轉",
        "- 徹底升級：3D 世界邊界，看見地圖外的星空夕陽",
        "- 優化：地堡中新增雷射全息圍牆",
        "- 優化：精準的 3D 逆投影滑鼠瞄準，射擊不跑偏",
    ]
    for i, line in enumerate(logs):
        surface.blit(small_font.render(line, True, WHITE), (rect.x + 20, rect.y + 60 + i * 30))

def draw_pause_upgrade_log(surface):
    draw_upgrade_summary(surface, WIDTH//2 - 120, HEIGHT//2 + 150, max_items=8, title="已獲得的強化")

# 升級卡牌完整資料
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

def choose_upgrade_cards():
    global current_upgrade_choices, selected_upgrade_position
    available_indices = []
    weights = []
    for i, opt in enumerate(upgrade_options):
        if opt.get("challenge_only", False) and game_mode != "CHALLENGE": continue
        available_indices.append(i); weights.append(opt.get("weight", 1))
        
    chosen_indices = []
    while len(chosen_indices) < 3 and available_indices:
        idx = random.choices(available_indices, weights=weights, k=1)[0]
        chosen_indices.append(idx)
        remove_idx = available_indices.index(idx)
        available_indices.pop(remove_idx); weights.pop(remove_idx)
        
    current_upgrade_choices = chosen_indices
    selected_upgrade_position = None

def apply_upgrade(idx, silent=False):
    global game_state, chosen_upgrades
    opt = upgrade_options[idx]
    found = False
    for u in chosen_upgrades:
        if u["title"] == opt["title"]: u["count"] += 1; found = True; break
    if not found: chosen_upgrades.append({"title": opt["title"], "count": 1})
    
    title = opt["title"]
    if title == "生命躍升": player.max_hp += 50; player.hp = player.max_hp
    elif title == "超頻運轉": player.shoot_delay_reduction += 2
    elif title == "能量飲料": player.stamina_regen += 0.2
    elif title == "彈幕擴張": player.bullet_count += 1
    elif title == "高能彈芯": player.bullet_damage_bonus += 5
    elif title == "備用電池": player.max_stamina += 25; player.stamina += 25
    elif title == "輕量推進": player.dash_cost = max(10, player.dash_cost - 5)
    elif title == "離子靴": player.base_speed += 0.5
    elif title == "磁吸核心": player.magnet_radius += 50
    elif title == "穩定槍管": player.bullet_spread = max(3.0, player.bullet_spread - 3.0)
    elif title == "運動健將": player.dash_duration += 2
    elif title == "急救模組": player.hp = min(player.max_hp, player.hp + 60)
    elif title == "相位護盾": player.invincible_duration += 15
    elif title == "裝甲鍍層": player.damage_reduction += 2
    elif title == "爆燃推進": player.dash_speed += 3
    elif title == "生命本源": player.max_hp += 20; player.hp += 20; player.max_stamina += 10
    elif title == "清道夫": player.magnet_radius += 20; player.stamina_regen += 0.1
    elif title == "寬幅槍口": player.extra_same_path_bullets += 1
    elif title == "導引模組": player.guidance_level += 1
    elif title == "電弧光環": player.aura_level += 1
    elif title == "再生奈米": player.regen_level += 1
    elif title == "學習核心": player.exp_multiplier += 0.2
    elif title == "擴容彈匣": player.mag_size_bonus += 10; player.ammo += 10
    elif title == "快拆彈匣": player.reload_duration = max(10, player.reload_duration - 15)
    elif title == "戰術無人機": player.drone_level += 1
    
    if not silent: game_state = "PLAYING"; play_sound("levelup")

persistent_stats = {"max_hp": 0, "dmg_bonus": 0, "speed_bonus": 0.0, "max_stamina": 0, "max_shield": 0, "max_energy": 0, "scrap": 0, "weapon_stash": [], "general_stash": [None]*36}
CHEAT_CODE = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_b, pygame.K_a, pygame.K_b, pygame.K_a]
key_buffer = []

class Weapon:
    def __init__(self, name, shoot_delay, bullet_type, damage, sound_name="shoot_normal", recoil=2.0):
        self.base_name, self.shoot_delay, self.bullet_type, self.damage, self.sound_name, self.base_recoil = name, shoot_delay, bullet_type, damage, sound_name, recoil
        self.rarity, self.affixes = "白", []
        load_image("gun_" + name, f"gun_{name}.png", (45, 18))
    @property 
    def full_name(self): return f"【{self.rarity}】{self.base_name}"

WEAPON_TYPES = {}
WEAPON_TYPES["手槍"] = Weapon("手槍", 20, "normal", 20, "snd_pistol", 1.5)
WEAPON_TYPES["狙擊槍"] = Weapon("狙擊槍", 50, "piercing", 45, "snd_sniper", 8.0)
WEAPON_TYPES["散彈槍"] = Weapon("散彈槍", 30, "shotgun", 20, "snd_shotgun", 5.0)
WEAPON_TYPES["機槍"] = Weapon("機槍", 15, "piercing", 20, "snd_mg", 1.0)
WEAPON_TYPES["火焰噴射器"] = Weapon("火焰噴射器", 3, "flamethrower", 4, "snd_flamethrower", 0.2)
WEAPON_TYPES["雷射槍"] = Weapon("雷射槍", 25, "laser", 25, "snd_laser", 0.5)
WEAPON_TYPES["電磁炮"] = Weapon("電磁炮", 60, "cannon", 50, "snd_cannon", 10.0)
WEAPON_TYPES["冰霜發射器"] = Weapon("冰霜發射器", 5, "frost", 6, "snd_frost", 0.2)
WEAPON_TYPES["重型機槍"] = Weapon("重型機槍", 17, "piercing", 25, "snd_heavy_mg", 1.5)
WEAPON_TYPES["步槍"] = Weapon("步槍", 40, "piercing", 30, "snd_rifle", 3.0)
WEAPON_TYPES["火焰榴彈發射器"] = Weapon("火焰榴彈發射器", 65, "flame_grenade", 70, "snd_grenade", 6.0)
WEAPON_TYPES["電漿發射器"] = Weapon("電漿發射器", 30, "plasma", 30, "snd_plasma", 2.0)

def get_rarity_color(r): return {"金": (255, 215, 0), "紫": (200, 50, 255), "藍": (50, 150, 255)}.get(r, (200, 200, 200))

def apply_weapon_stats(w):
    base = WEAPON_TYPES[w.base_name]
    w.damage = int(base.damage * {"白":1.0, "藍":1.3, "紫":1.6, "金":2.2}.get(w.rarity, 1.0))
    w.shoot_delay = max(2, int(base.shoot_delay * 0.60)) if "速射" in w.affixes else base.shoot_delay

def generate_weapon(base_name, rarity="白"):
    base = WEAPON_TYPES[base_name]
    w = Weapon(base.base_name, base.shoot_delay, base.bullet_type, base.damage, base.sound_name, base.base_recoil)
    w.rarity = rarity
    c = {"白":0, "藍":1, "紫":2, "金":3}.get(rarity, 0)
    pool = ["速射", "散射", "吸血", "爆擊"]
    if base.bullet_type not in ["piercing", "laser", "cannon", "flamethrower"]: pool.append("穿透") 
    if base.bullet_type not in ["flamethrower", "flame_grenade"]: pool.append("燃燒") 
    w.affixes = random.sample(pool, min(c, len(pool))) if c > 0 else []
    apply_weapon_stats(w)
    return w

def sort_weapon_stash():
    rv = {"白":0, "藍":1, "紫":2, "金":3}; order = list(WEAPON_TYPES.keys())
    persistent_stats["weapon_stash"].sort(key=lambda w: (order.index(w.base_name) if w.base_name in order else 99, -rv.get(w.rarity, 0), -len(w.affixes), "".join(sorted(w.affixes))))

def get_sell_value(item):
    if not item: return 0
    if item.type == "WEAPON": return {"白":20, "藍":50, "紫":120, "金":300}.get(item.weapon_obj.rarity, 10)
    elif item.type == "MED": return 5 * item.count
    elif item.type == "KEY": return 30 * item.count
    return 0

class InvItem:
    def __init__(self, i_type, name, count, max_stack, weapon_obj=None):
        self.type, self.name, self.count, self.max_stack, self.weapon_obj = i_type, name, count, max_stack, weapon_obj

def create_item(i_type, amount=1, weapon_obj=None):
    if i_type == "SCRAP": return InvItem("SCRAP", "廢料", amount, 999)
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
            if to_list[i] is None: to_list[i] = item; return True
    return False

# ========================== 實體物件 ==========================
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vel_x, self.vel_y = random.uniform(-6, 6), random.uniform(-6, 6)
        self.timer, self.size, self.color = random.randint(15, 30), random.randint(4, 8), color
    def update(self):
        self.x += self.vel_x; self.y += self.vel_y; self.timer -= 1; self.size = max(0, self.size - 0.25)
    # (被統一由主迴圈接管座標進行 Billboarding 繪圖)

class DamageText:
    def __init__(self, x, y, damage, color, is_crit=False):
        self.x, self.y, self.damage, self.color, self.is_crit = x, y, damage, color, is_crit
        self.timer = 50 if is_crit else 35; self.vel_y = -3.5 if is_crit else -2.0
        self.alpha, self.offset_x, self.font = 255, random.randint(-15, 15), large_font if is_crit else small_font
    def update(self):
        self.y += self.vel_y; self.vel_y += 0.2; self.timer -= 1; self.alpha = max(0, int((self.timer / 35) * 255))
    def draw(self, surface):
        if self.timer > 0:
            txt = self.font.render(f"-{int(self.damage)}" + ("!" if self.is_crit else ""), True, self.color)
            txt.set_alpha(self.alpha)
            surface.blit(txt, (int(self.x + self.offset_x - txt.get_width()//2), int(self.y)))

class DashTrail:
    def __init__(self, x, y, size): self.x, self.y, self.size, self.life = x, y, size, 15
    def update(self): self.life -= 1
    def draw(self, surface):
        alpha = max(0, int((self.life / 15) * 150))
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 200, 255, alpha), (0, 0, self.size, self.size), border_radius=5)
        surface.blit(surf, (int(self.x - self.size/2), int(self.y - self.size/2)))

class DropItem:
    def __init__(self, x, y, item_type="EXP", count=1, weapon_obj=None):
        self.x, self.y, self.item_type, self.count, self.weapon_obj = x, y, item_type, count, weapon_obj
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.anim_offset = random.random() * 10
    def update(self, p_x, p_y, mag_rad):
        if self.item_type not in ["EXP", "MAGNET", "BOMB", "SHIELD"]: return 
        dist_sq = (self.x - p_x)**2 + (self.y - p_y)**2
        if 0 < dist_sq < mag_rad**2:
            dist = math.sqrt(dist_sq)
            speed = 25 if mag_rad > 1000 else 8
            self.x += ((p_x - self.x) / dist) * speed; self.y += ((p_y - self.y) / dist) * speed 
        self.rect.center = (int(self.x), int(self.y))
    def draw(self, surface):
        draw_x, draw_y = int(self.x), int(self.y)
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
        if self.count > 1 and self.item_type in ["SCRAP", "MED", "KEY"]:
            surface.blit(tiny_font.render(str(self.count), True, WHITE), (draw_x + 5, int(float_y) + 5))

class Chest:
    def __init__(self, x, y, c_type="NORMAL"):
        self.x, self.y, self.type, self.state, self.open_progress = x, y, c_type, "CLOSED", 0
        self.rect = pygame.Rect(0, 0, 50, 40)
        self.rect.center = (int(self.x), int(self.y))
        self.color = (139, 69, 19) if c_type == "NORMAL" else (218, 165, 32)
    def draw(self, surface):
        draw_x, draw_y = int(self.x), int(self.y)
        draw_rect = self.rect.copy(); draw_rect.center = (draw_x, draw_y)
        img = images.get(f"chest_{self.type}_{self.state}")
        if img:
            surface.blit(img, img.get_rect(center=(draw_x, draw_y)))
            if self.state == "CLOSED" and self.open_progress > 0:
                pygame.draw.rect(surface, GRAY, (draw_x-25, draw_y-30, 50, 6))
                pygame.draw.rect(surface, GREEN, (draw_x-25, draw_y-30, 50*(self.open_progress/40), 6))
        else:
            if self.state == "CLOSED":
                pygame.draw.rect(surface, self.color, draw_rect, border_radius=5)
                pygame.draw.rect(surface, WHITE if self.type=="NORMAL" else YELLOW, draw_rect, 2, border_radius=5)
                if self.type == "LOCKED": pygame.draw.circle(surface, BLACK, (draw_x, draw_y), 6) 
                if self.open_progress > 0:
                    pygame.draw.rect(surface, GRAY, (draw_x-25, draw_y-30, 50, 6)); pygame.draw.rect(surface, GREEN, (draw_x-25, draw_y-30, 50*(self.open_progress/40), 6))
            else:
                open_rect = pygame.Rect(0,0,50,15); open_rect.center = (draw_x, draw_y+10)
                pygame.draw.rect(surface, (80,40,10), open_rect, border_radius=3)

class PlayerLostItem:
    def __init__(self, x, y, level, exp, upgrades, inv_items, w1, w2):
        self.x, self.y, self.level, self.exp, self.upgrades = x, y, level, exp, upgrades
        self.inventory, self.w1, self.w2 = inv_items, w1, w2
        self.rect = pygame.Rect(0, 0, 50, 50); self.rect.center = (int(self.x), int(self.y))
    def draw(self, surface):
        draw_x, draw_y = int(self.x), int(self.y)
        p = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 5)
        pygame.draw.circle(surface, YELLOW, (draw_x, draw_y), 20 + p)
        pygame.draw.circle(surface, WHITE, (draw_x, draw_y), 22 + p, 2)
        txt = small_font.render(f"遺失物(觸碰拾取)", True, YELLOW)
        surface.blit(txt, (draw_x - txt.get_width()//2, draw_y - 35))

class ExtractionPoint:
    def __init__(self): self.x, self.y, self.radius = random.randint(800, MAP_WIDTH - 800), random.randint(800, MAP_HEIGHT - 800), 150
    
    def draw(self, surface):
        # 取得 3D 投影座標
        sx, sy, depth = project_3d(self.x, self.y, 0)
        if depth < -5000: return
        
        # 依據視角決定法陣/貼圖的 Y 軸壓扁比例
        y_compress = 0.3 if view_mode == "FPS" else (1.0 if view_mode == "CLASSIC" else 0.5)
        
        anim_frames = animations.get("extraction_point")
        img = images.get("extraction_point")
        
        # 優先使用動畫
        if anim_frames:
            frame = anim_frames[int(pygame.time.get_ticks() / 150) % len(anim_frames)]
            w, h = frame.get_size()
            frame = pygame.transform.scale(frame, (w, int(h * y_compress)))
            surface.blit(frame, frame.get_rect(center=(sx, sy)))
        # 其次使用靜態圖片
        elif img:
            w, h = img.get_size()
            scaled_img = pygame.transform.scale(img, (w, int(h * y_compress)))
            surface.blit(scaled_img, scaled_img.get_rect(center=(sx, sy)))
        # 備像素投影
        else:
            p = int(abs(math.sin(pygame.time.get_ticks() * 0.003)) * 20)
            rect_w = (self.radius + p) * 2
            rect_h = (self.radius + p) * 2 * y_compress
            pygame.draw.ellipse(surface, GREEN, (sx - rect_w/2, sy - rect_h/2, rect_w, rect_h), 3)
            txt = font.render("撤離點", True, GREEN)
            surface.blit(txt, (sx - txt.get_width()//2, sy - 20))

class DummyTarget:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.rect = pygame.Rect(0, 0, 40, 60); self.rect.center = (int(self.x), int(self.y)) 
        self.hit_log = []
        self.shake_timer = 0
    def update(self):
        now = pygame.time.get_ticks()
        self.hit_log = [(t, dmg) for t, dmg in self.hit_log if now - t <= 3000]
        if self.shake_timer > 0: self.shake_timer -= 1
        self.rect.center = (int(self.x), int(self.y))
    def draw(self, surface):
        dx = int(self.x) + (random.randint(-2,2) if self.shake_timer>0 else 0)
        dy = int(self.y) + (random.randint(-2,2) if self.shake_timer>0 else 0)
        anim_frames = animations.get("dummy")
        if anim_frames:
            img = anim_frames[int(pygame.time.get_ticks() / 150) % len(anim_frames)]
            if self.shake_timer > 0:
                img = img.copy(); img.fill((255, 100, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(img, img.get_rect(center=(dx, dy)))
        else:
            draw_rect = self.rect.copy(); draw_rect.center = (dx, dy)
            pygame.draw.rect(surface, (150, 100, 80), draw_rect, border_radius=10)
            pygame.draw.circle(surface, RED, (dx, dy - 10), 8); pygame.draw.circle(surface, WHITE, (dx, dy - 10), 4)
        total_dmg = sum(dmg for t, dmg in self.hit_log)
        dps = int(total_dmg / 3.0) if self.hit_log else 0
        dps_txt = small_font.render(f"DPS: {dps}", True, CYAN if dps > 0 else GRAY)
        surface.blit(dps_txt, (dx - dps_txt.get_width()//2, dy - 50))

class Player:
    def __init__(self):
        self.x, self.y, self.size = MAP_WIDTH / 2, MAP_HEIGHT / 2, 30
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.primary_weapon, self.secondary_weapon = generate_weapon("手槍", "白"), generate_weapon("散彈槍", "白")
        self.weapons = [self.primary_weapon, self.secondary_weapon]
        self.current_weapon_idx, self.cheat_all_weapons = 0, False 
        
        self.base_speed = 7.0 + persistent_stats["speed_bonus"]
        self.max_hp = 100 + persistent_stats["max_hp"]
        self.max_shield = 100 + persistent_stats["max_shield"]
        self.max_stamina = 100 + persistent_stats["max_stamina"]
        self.max_energy = 100 + persistent_stats["max_energy"]
        
        self.hp, self.shield = self.max_hp, self.max_shield       
        self.stamina, self.stamina_regen = self.max_stamina, 0.5   
        self.energy, self.energy_regen = self.max_energy, 0.2 
        self.exp, self.level, self.max_exp = 0, 1, 80
        self.inventory = [None] * 24
        
        self.current_spread, self.bullet_count, self.bullet_spread, self.extra_same_path_bullets = 15.0, 1, 15.0, 0
        self.bullet_damage_bonus, self.shoot_delay_reduction, self.damage_reduction = persistent_stats["dmg_bonus"], 0, 0
        self.invincible_duration, self.guidance_level, self.aura_level, self.regen_level, self.regen_progress = 60, 0, 0, 0, 0
        self.exp_multiplier, self.magnet_radius, self.drone_level, self.drone_angle, self.drone_shoot_cd = 1.0, 80, 0, 0, 0
        self.dash_cost, self.is_dashing, self.dash_speed, self.dash_duration, self.dash_timer, self.dash_dir_x, self.dash_dir_y = 30, False, 28, 8, 0, 0, 0
        self.skill_cd, self.skill_max_cd, self.skill_cost = 0, 600, 50        
        self.invincible_timer, self.god_mode = 0, False 
        self.base_max_ammo, self.mag_size_bonus, self.reload_duration, self.reload_timer = 40, 0, 90, 0
        self.ammo = self.base_max_ammo
        self.z, self.vel_x, self.vel_y = 0, 0, 0
        self.aim_dir_x, self.aim_dir_y, self.facing_angle = 1, 0, 0

    @property 
    def scrap(self): return sum(i.count for i in self.inventory if i and i.type == "SCRAP")
    def add_item(self, new_item): return fast_transfer(new_item, self.inventory)
    def use_med(self):
        for i in range(24):
            item = self.inventory[i]
            if item and item.type == "MED" and self.hp < self.max_hp:
                self.hp = min(self.max_hp, self.hp + 40); item.count -= 1
                if item.count <= 0: self.inventory[i] = None
                play_sound("exp"); return True
        return False
    def switch_weapon(self, idx):
        if idx != self.current_weapon_idx and 0 <= idx < len(self.weapons):
            self.current_weapon_idx = idx; self.skill_cd = 0; self.reload_timer = 0
            self.ammo = self.base_max_ammo + self.mag_size_bonus

    def update(self, clamp_rect=None):
        global camera_angle
        keys = pygame.key.get_pressed()
        
        # 相對鏡頭的第三人稱視角移動 (W永遠朝畫面上方)
        cam_forward_x, cam_forward_y = math.sin(camera_angle), -math.cos(camera_angle)
        cam_right_x, cam_right_y = math.cos(camera_angle), math.sin(camera_angle)

        move_x, move_y = 0, 0
        if keys[pygame.K_w]: move_x += cam_forward_x; move_y += cam_forward_y
        if keys[pygame.K_s]: move_x -= cam_forward_x; move_y -= cam_forward_y
        if keys[pygame.K_a]: move_x -= cam_right_x; move_y -= cam_right_y
        if keys[pygame.K_d]: move_x += cam_right_x; move_y += cam_right_y
            
        dist = math.sqrt(move_x**2 + move_y**2)
        if dist > 0: move_x /= dist; move_y /= dist
        
        if dist > 0: self.facing_angle = math.atan2(move_y, move_x)
        self.vel_x, self.vel_y = move_x * self.base_speed, move_y * self.base_speed

        if self.invincible_timer > 0: self.invincible_timer -= 1
        if self.skill_cd > 0: self.skill_cd -= 1
        if self.reload_timer > 0:
            self.reload_timer -= 1
            if self.reload_timer <= 0: self.ammo = self.base_max_ammo + self.mag_size_bonus

        if self.regen_level > 0 and self.hp < self.max_hp:
            self.regen_progress += 0.01 * self.regen_level
            if self.regen_progress >= 1: 
                heal = int(self.regen_progress); self.hp = min(self.max_hp, self.hp + heal); self.regen_progress -= heal
            
        if not self.is_dashing and self.stamina < self.max_stamina: self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen)
        if self.energy < self.max_energy: self.energy = min(self.max_energy, self.energy + self.energy_regen)

        if keys[pygame.K_SPACE]:
            if not self.is_dashing and self.stamina >= self.dash_cost:
                self.stamina -= self.dash_cost; self.is_dashing = True; self.dash_timer = self.dash_duration
                play_sound("dash")
                if dist > 0: self.dash_dir_x, self.dash_dir_y = move_x, move_y
                else:
                    if 'world_mouse_x' in globals(): dx, dy = world_mouse_x - self.x, world_mouse_y - self.y
                    else: dx, dy = 1, 0
                    ddist = math.sqrt(dx**2 + dy**2)
                    self.dash_dir_x, self.dash_dir_y = (dx / ddist, dy / ddist) if ddist > 0 else (1, 0)

        if self.is_dashing:
            self.x += self.dash_dir_x * self.dash_speed; self.y += self.dash_dir_y * self.dash_speed
            self.dash_timer -= 1
            progress = 1.0 - (self.dash_timer / self.dash_duration)
            self.z = math.sin(progress * math.pi) * 22
            if self.dash_timer <= 0: self.is_dashing = False; self.z = 0
        else:
            self.x += move_x * self.base_speed; self.y += move_y * self.base_speed; self.z = 0
            
        if clamp_rect:
            self.x = max(clamp_rect.left + self.size/2, min(clamp_rect.right - self.size/2, self.x))
            self.y = max(clamp_rect.top + self.size/2, min(clamp_rect.bottom - self.size/2, self.y))
        else:
            self.x = max(self.size/2, min(MAP_WIDTH - self.size/2, self.x))
            self.y = max(self.size/2, min(MAP_HEIGHT - self.size/2, self.y))
            
        self.rect.center = (int(self.x), int(self.y))
        if self.current_spread > self.bullet_spread: self.current_spread = max(self.bullet_spread, self.current_spread - 0.5)

    def draw(self, surface, current_wep=None):
        draw_center = (int(self.x), int(self.y))
        draw_player = True
        if self.invincible_timer > 0 and not self.god_mode:
            if (self.invincible_timer // 4) % 2 == 0: draw_player = False
                
        if draw_player:
            # 8向視角
            relative_angle = math.degrees(self.facing_angle - camera_angle) % 360
            dir_idx = int((relative_angle + 22.5) // 45) % 8
            anim_list = ["right", "down_right", "down", "down_left", "left", "up_left", "up", "up_right"]
            
            img = images.get(f"player_{anim_list[dir_idx]}") or images.get("player")
            
            if img:
                if dir_idx in [3, 4, 5]: img = pygame.transform.flip(img, True, False)
                
                breath = 1.0 + math.sin(pygame.time.get_ticks() * 0.006) * 0.06
                tilt_angle = -self.vel_x * 1.5 
                
                # 視角微放大角色 (2 倍)，增加跟隨感但不會擋住前方
                base_scale = 2.0 if view_mode == "FPS" else 1.0
                
                if self.is_dashing:
                    tilt_angle = -self.dash_dir_x * 20
                    scaled_img = pygame.transform.scale(img, (int(self.size * 1.2 * base_scale), int(self.size * 0.8 * base_scale)))
                else:
                    scaled_img = pygame.transform.scale(img, (int(self.size * base_scale), int(self.size * breath * base_scale)))
                
                final_img = pygame.transform.rotate(scaled_img, tilt_angle)
                surface.blit(final_img, final_img.get_rect(center=draw_center))
            else: 
                
                draw_rect = pygame.Rect(0, 0, self.size, self.size)
                draw_rect.center = draw_center
                
                # REPLACED 風格：黑色剪影本體 + 霓虹邊框 + 發光護目鏡
                outline_color = YELLOW if self.god_mode else CYAN
                
                # 深淵黑實體
                pygame.draw.rect(surface, (10, 12, 15), draw_rect)
                # 霓虹高光邊框
                pygame.draw.rect(surface, outline_color, draw_rect, 2)
                
                # 科幻發光面罩 (Visor)
                visor_y = draw_rect.top + 8
                # 模擬 Bloom 發光效果
                pygame.draw.line(surface, outline_color, (draw_rect.left - 2, visor_y), (draw_rect.right + 2, visor_y), 4)
                pygame.draw.line(surface, WHITE, (draw_rect.left + 2, visor_y), (draw_rect.right - 2, visor_y), 2)
            
            if self.stamina < self.dash_cost: pygame.draw.circle(surface, GRAY, draw_center, self.size, 2)

            if current_wep:
                rel_aim_x = self.aim_dir_x * math.cos(-camera_angle) - self.aim_dir_y * math.sin(-camera_angle)
                rel_aim_y = self.aim_dir_x * math.sin(-camera_angle) + self.aim_dir_y * math.cos(-camera_angle)
                
               
                # 同步槍枝的視角傾斜角
                if view_mode == "FPS": y_compress = 0.3
                elif view_mode == "CLASSIC": y_compress = 1.0
                else: y_compress = 0.5
                screen_dir_y = rel_aim_y * y_compress
                
                
                angle = math.degrees(math.atan2(-screen_dir_y, rel_aim_x))
                
                gun_img = images.get("gun_" + current_wep.base_name)
                if gun_img:
                    if rel_aim_x < 0: gun_img = pygame.transform.flip(gun_img, False, True)
                    
                    if view_mode == "FPS":
                        gun_w, gun_h = gun_img.get_size()
                        gun_img = pygame.transform.scale(gun_img, (int(gun_w * 1.25), int(gun_h * 1.25)))
                        
                    rotated_gun = pygame.transform.rotate(gun_img, angle)
                    
                    gun_offset_scale = 1.25 if view_mode == "FPS" else 1.0
                    offset_x = rel_aim_x * 18 * gun_offset_scale
                    offset_y = screen_dir_y * 36 * gun_offset_scale 
                    surface.blit(rotated_gun, rotated_gun.get_rect(center=(draw_center[0] + offset_x, draw_center[1] + offset_y)))

        if self.aura_level > 0:
            pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10)
            pygame.draw.ellipse(surface, (0, 180, 255), (draw_center[0]-95-pulse, draw_center[1]-30, 190+pulse*2, 60), 2)
            
        if self.drone_level > 0:
            drone_x, drone_y = draw_center[0] + math.cos(self.drone_angle) * 55, draw_center[1] + math.sin(self.drone_angle) * 27 + math.sin(pygame.time.get_ticks()*0.01)*10
            pygame.draw.circle(surface, (150, 200, 255), (int(drone_x), int(drone_y)), 10)
            pygame.draw.circle(surface, BLUE, (int(drone_x), int(drone_y)), 10, 2); pygame.draw.circle(surface, RED, (int(drone_x), int(drone_y)), 4)
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
        self.explode, self.target_x, self.target_y = False, target_x, target_y

    def update(self, all_enemies=None):
        if all_enemies is None: all_enemies = []
        self.lifespan -= 1
        if self.b_type == "flame_grenade" and math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2) < self.speed:
            self.explode = True; self.lifespan = 0; return 

        if self.guidance_level > 0 and len(all_enemies) > 0:
            closest_enemy = min(all_enemies, key=lambda e: math.sqrt((self.x - e.x)**2 + (self.y - e.y)**2), default=None)
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
        draw_center = (int(self.x), int(self.y))
        img = images.get("bullet_" + self.b_type)
        if img: 
            rel_dir_x = self.dir_x * math.cos(-camera_angle) - self.dir_y * math.sin(-camera_angle)
            rel_dir_y = self.dir_x * math.sin(-camera_angle) + self.dir_y * math.cos(-camera_angle)
            
            # 同步子彈影像的旋轉壓扁率
            if view_mode == "FPS": y_compress = 0.3
            elif view_mode == "CLASSIC": y_compress = 1.0
            else: y_compress = 0.5
            screen_dir_y = rel_dir_y * y_compress
            
            angle = math.degrees(math.atan2(-screen_dir_y, rel_dir_x))
            rotated_img = pygame.transform.rotate(img, angle)
            surface.blit(rotated_img, rotated_img.get_rect(center=draw_center))
        else: 
            pygame.draw.circle(surface, self.color, draw_center, self.radius)
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
        self.lifespan = 150 if is_homing else 9999 
        self.explode = False
    def update(self, target_x=None, target_y=None):
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.explode = True
            return
        if self.is_homing and target_x is not None and target_y is not None:
            tx, ty = target_x - self.x, target_y - self.y
            dist = math.sqrt(tx**2 + ty**2)
            if dist > 0:
                turn_speed = 0.045 * (self.lifespan / 150)
                self.dir_x = self.dir_x * (1 - turn_speed) + (tx / dist) * turn_speed
                self.dir_y = self.dir_y * (1 - turn_speed) + (ty / dist) * turn_speed
                ndist = math.sqrt(self.dir_x**2 + self.dir_y**2)
                if ndist > 0: self.dir_x /= ndist; self.dir_y /= ndist
        self.x += self.dir_x * self.speed; self.y += self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))
    def draw(self, surface): 
        draw_center = (int(self.x), int(self.y))
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
        self.hit_timer = 0
        self.combat_type = random.choice(["melee", "ranged"]) if is_elite else random.choices(["melee", "ranged", "kamikaze"], weights=[0.45, 0.45, 0.1])[0]
        
        if self.combat_type == "kamikaze": 
            self.color, self.speed, self.max_hp, self.damage = ORANGE, self.speed*1.4, int(self.max_hp*0.6), int(self.damage*1.5)
            self.hp = self.max_hp; self.weapon = None; self.shoot_cd = 0
        elif self.combat_type == "ranged":
            weapons = list(WEAPON_TYPES.values())
            self.weapon = random.choice(weapons) if weapons else None
            self.shoot_cd = getattr(self.weapon, "shoot_delay", 20) * 3 + random.randint(20, 60) if self.weapon else 120
        else:
            self.weapon = None; self.shoot_cd = 0
        
        spawn_dist_x = WIDTH / 2 + 50
        spawn_dist_y = HEIGHT / 2 + 50
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top': self.x, self.y = spawn_x + random.randint(-int(spawn_dist_x), int(spawn_dist_x)), spawn_y - spawn_dist_y
        elif edge == 'bottom': self.x, self.y = spawn_x + random.randint(-int(spawn_dist_x), int(spawn_dist_x)), spawn_y + spawn_dist_y
        elif edge == 'left': self.x, self.y = spawn_x - spawn_dist_x, spawn_y + random.randint(-int(spawn_dist_y), int(spawn_dist_y))
        elif edge == 'right': self.x, self.y = spawn_x + spawn_dist_x, spawn_y + random.randint(-int(spawn_dist_y), int(spawn_dist_y))
            
        self.x = max(0, min(self.x, MAP_WIDTH))
        self.y = max(0, min(self.y, MAP_HEIGHT))
        self.rect = pygame.Rect(0, 0, self.size, self.size); self.rect.center = (int(self.x), int(self.y))

    def update(self, target_x, target_y, all_enemies, enemy_bullets):
        current_speed = self.speed * 0.4 if self.frost_timer > 0 else self.speed
        if self.hit_timer > 0: self.hit_timer -= 1
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
                if self.weapon and self.weapon.bullet_type == "shotgun":
                    for i in range(-2, 3):
                        ang = math.atan2(self.dir_y, self.dir_x) + math.radians(i*12)
                        enemy_bullets.append(EnemyBullet(self.x, self.y, math.cos(ang), math.sin(ang), weapon=self.weapon))
                elif self.weapon:
                    enemy_bullets.append(EnemyBullet(self.x, self.y, self.dir_x, self.dir_y, weapon=self.weapon))
                self.shoot_cd = getattr(self.weapon, "shoot_delay", 20) * 4 + random.randint(20, 60) if self.weapon else 120
            if self.shoot_cd > 0: self.shoot_cd -= 1
        elif self.combat_type == "kamikaze": self.x += self.dir_x * current_speed; self.y += self.dir_y * current_speed
        else:
            if dist > (self.size + 30) / 2: self.x += self.dir_x * current_speed; self.y += self.dir_y * current_speed

        for other in all_enemies:
            if other is not self and 0 < (self.x - other.x)**2 + (self.y - other.y)**2 < self.size**2:
                dist_val = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
                self.x += ((self.x - other.x) / dist_val) * 1.3; self.y += ((self.y - other.y) / dist_val) * 1.3
            
        self.x, self.y = max(0, min(self.x, MAP_WIDTH)), max(0, min(self.y, MAP_HEIGHT))
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        draw_center = (int(self.x), int(self.y))
        
        # 廣告板相對向量：判斷敵人在 3D 畫面上是往左跑還是往右跑
        cos_a = math.cos(-camera_angle)
        sin_a = math.sin(-camera_angle)
        rel_dir_x = self.dir_x * cos_a - self.dir_y * sin_a  

        if self.combat_type == "kamikaze":
            pygame.draw.circle(surface, ORANGE, draw_center, self.size // 2)
            for i in range(8):
                angle = pygame.time.get_ticks() * 0.01 + i * math.pi / 4
                end_x = draw_center[0] + math.cos(angle) * (self.size * 0.8)
                end_y = draw_center[1] + math.sin(angle) * (self.size * 0.8)
                pygame.draw.line(surface, YELLOW, draw_center, (end_x, end_y), 3)
        else:
            anim_key = "enemy_elite" if self.is_elite else "enemy_normal"
            anim_frames = animations.get(anim_key)
            if anim_frames:
                img = anim_frames[int(pygame.time.get_ticks() / 100) % len(anim_frames)]
                # 若相對鏡頭向左跑，翻轉圖片 (DOOM-style)
                if rel_dir_x < 0: img = pygame.transform.flip(img, True, False)
                
                if self.hit_timer > 0:
                    img = img.copy()
                    img.fill((255, 255, 255, 150), special_flags=pygame.BLEND_RGBA_ADD)
                elif self.frost_timer > 0:
                    img = img.copy(); img.fill((100, 200, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)
                
                surface.blit(img, img.get_rect(center=draw_center))
            ###############################
            else:
                #  draw_rect 要對齊中心
                draw_rect = pygame.Rect(0, 0, self.size, self.size)
                draw_rect.center = draw_center
                
                # REPLACED 風格：幽暗機械實體 + 狂暴霓虹勾邊
                pygame.draw.rect(surface, (12, 10, 14), draw_rect) # 實體黑影
                
                # 決定霓虹顏色
                neon_color = PURPLE if getattr(self, 'is_elite', False) else RED
                if getattr(self, 'hit_timer', 0) > 0: neon_color = WHITE 
                elif getattr(self, 'frost_timer', 0) > 0: neon_color = BLUE
                
                # 精英怪的光暈放大感
                if getattr(self, 'is_elite', False):
                    glow = math.sin(pygame.time.get_ticks() * 0.01) * 6 + 4
                    pygame.draw.rect(surface, DARK_PURPLE, draw_rect.copy().inflate(glow, glow), 2)
                
                # 繪製高壓霓虹邊框
                pygame.draw.rect(surface, neon_color, draw_rect, 2)
                
                # 狂暴紅色/紫色單眼 (發光掃描器)
                eye_rect = pygame.Rect(draw_center[0] - 6 + (self.dir_x * 4), draw_rect.top + 6, 12, 4)
                pygame.draw.rect(surface, neon_color, eye_rect)
                pygame.draw.rect(surface, WHITE, eye_rect.inflate(-2, -2)) # 核心白點

        bar_y = draw_center[1] - self.size//2 - 10
        if self.max_shield > 0 and self.shield > 0:
            pygame.draw.rect(surface, GRAY, (draw_center[0]-self.size//2, bar_y-6, self.size, 4))
            pygame.draw.rect(surface, (0, 150, 255), (draw_center[0]-self.size//2, bar_y-6, self.size * (max(0, self.shield)/self.max_shield), 4))
        if self.hp < self.max_hp:
            pygame.draw.rect(surface, GRAY, (draw_center[0]-self.size//2, bar_y, self.size, 4))
            pygame.draw.rect(surface, GREEN, (draw_center[0]-self.size//2, bar_y, self.size * (max(0, self.hp)/self.max_hp), 4))

class Boss:
    def __init__(self, boss_type, level, spawn_x=MAP_WIDTH/2, spawn_y=MAP_HEIGHT/2):
        self.b_type = boss_type
        self.x, self.y = spawn_x, max(0, spawn_y - 400)
        self.size = 65
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.state_timer, self.frost_timer, self.burn_timer = 0, 0, 0
        self.play_shoot_sound = False 
        self.hit_timer = 0
        
        base_hp = {"YELLOW": 3000, "RED": 4000, "PURPLE": 2500, "CYAN": 3200}[self.b_type]
        self.max_hp = int((base_hp + level * 100) * (1.75 if game_mode == "CHALLENGE" else 1.0))
        self.hp = self.max_hp
        
        if self.b_type == "YELLOW": self.color, self.speed, self.state = YELLOW, 3.0, "EVADE"
        elif self.b_type == "RED": self.color, self.speed, self.state, self.aim_x, self.aim_y = RED, 2.5, "CHASE", 0, 0
        elif self.b_type == "PURPLE": self.color, self.speed, self.state = PURPLE, 2.0, "FLEE"
        elif self.b_type == "CYAN": self.color, self.speed, self.state = CYAN, 3.0, "IDLE"

    def update(self, player_x, player_y, bullets, enemies, enemy_bullets):
        self.state_timer += 1
        current_speed = self.speed * 0.5 if self.frost_timer > 0 else self.speed
        if self.hit_timer > 0: self.hit_timer -= 1
        if self.frost_timer > 0: self.frost_timer -= 1
        if self.burn_timer > 0:
            self.burn_timer -= 1
            if self.burn_timer % 15 == 0: self.hp -= 10; particles.append(Particle(self.x, self.y, ORANGE))
                
        dx, dy = player_x - self.x, player_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        dir_x, dir_y = (dx / dist, dy / dist) if dist > 0 else (0, 0)
        tang_x, tang_y = -dir_y, dir_x
        
        if self.b_type == "YELLOW":
            if self.state == "EVADE":
                dodged = False
                for b in bullets:
                    if math.hypot(self.x - b.x, self.y - b.y) < 150:
                        fd = math.hypot(self.x - b.x, self.y - b.y)
                        if fd > 0: self.x += ((self.x - b.x) / fd) * (current_speed * 1.8); self.y += ((self.y - b.y) / fd) * (current_speed * 1.8)
                        dodged = True; break 
                if not dodged:
                    self.x += tang_x * current_speed; self.y += tang_y * current_speed
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
                    d_dist = math.hypot(self.aim_x - self.x, self.aim_y - self.y)
                    self.dash_dir_x, self.dash_dir_y = (self.aim_x - self.x)/d_dist, (self.aim_y - self.y)/d_dist if d_dist > 0 else (0,0)
                    self.play_shoot_sound = True
            elif self.state == "DASH":
                self.x += self.dash_dir_x * (current_speed * 6); self.y += self.dash_dir_y * (current_speed * 6)
                if self.state_timer > 20: self.state = "CHASE"; self.state_timer = 0
        elif self.b_type == "PURPLE":
            if self.state == "FLEE":
                if dist > 0:
                    if dist < 300: self.x -= dir_x * current_speed; self.y -= dir_y * current_speed
                    else: self.x += tang_x * current_speed; self.y += tang_y * current_speed
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
                else: self.x += tang_x * current_speed; self.y += tang_y * current_speed
                if self.state_timer > 100: self.state = "FIRE"; self.state_timer = 0
            elif self.state == "FIRE":
                if self.state_timer in [10, 20, 30]:
                    for i in range(-1, 2):
                        ang = math.atan2(dir_y, dir_x) + math.radians(i * 20)
                        enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, math.cos(ang), math.sin(ang), color=CYAN, is_homing=True))
                    self.play_shoot_sound = True
                if self.state_timer > 40: self.state = "IDLE"; self.state_timer = 0

        self.x = max(self.size, min(MAP_WIDTH - self.size, self.x))
        self.y = max(self.size, min(MAP_HEIGHT - self.size, self.y))
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        draw_center = (int(self.x), int(self.y))
        anim_key = "boss_" + self.b_type
        anim_frames = animations.get(anim_key)
        
        # 決定 Boss 面向左還右
        rel_x = player.x - self.x
        screen_rel_x = rel_x * math.cos(-camera_angle)

        if anim_frames:
            img = anim_frames[int(pygame.time.get_ticks() / 150) % len(anim_frames)]
            if screen_rel_x < 0: img = pygame.transform.flip(img, True, False)
            
            if getattr(self, 'hit_timer', 0) > 0:
                img = img.copy(); img.fill((255, 255, 255, 150), special_flags=pygame.BLEND_RGBA_ADD)
            elif self.frost_timer > 0:
                img = img.copy(); img.fill((100, 200, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)
                
            surface.blit(img, img.get_rect(center=draw_center))
        else:
            if getattr(self, 'hit_timer', 0) > 0: c = WHITE
            elif self.frost_timer > 0: c = (100, 200, 255)
            else: c = self.color
                
            if self.b_type == "CYAN":
                pts = [(draw_center[0], draw_center[1] - self.size), (draw_center[0] + self.size, draw_center[1]), (draw_center[0], draw_center[1] + self.size), (draw_center[0] - self.size, draw_center[1])]
                pygame.draw.polygon(surface, c, pts); pygame.draw.polygon(surface, WHITE, pts, 3)
            else: 
                draw_rect = self.rect.copy(); draw_rect.center = draw_center
                pygame.draw.rect(surface, c, draw_rect)
        
        if self.b_type == "YELLOW":
            if self.state == "EVADE": pygame.draw.circle(surface, WHITE, draw_center, int(self.size/2) + 15, 3)
            elif self.state == "CHARGE": pygame.draw.circle(surface, RED, draw_center, int(self.size/2) + max(0, 30 - int(self.state_timer / 2)), 2)
        elif self.b_type == "RED" and self.state == "WARN":
            sx, sy, depth = project_3d(self.aim_x, self.aim_y)
            pygame.draw.line(surface, RED, draw_center, (sx, sy), max(1, int(self.state_timer / 8)))
        elif self.b_type == "PURPLE" and self.state == "SUMMON": pygame.draw.circle(surface, DARK_PURPLE, draw_center, int(self.size/2) + min(60, self.state_timer), 3)
        elif self.b_type == "CYAN" and self.state == "FIRE": pygame.draw.circle(surface, CYAN, draw_center, int(self.size/2) + 20, 4)

# ========================== 全域狀態 ==========================
chosen_upgrades = []
defeated_boss_levels = []
lost_item = None
game_mode = "NORMAL"
bullets, bunker_bullets, enemy_bullets, enemies, particles, items, trails, damage_texts, chests = [], [], [], [], [], [], [], [], []
boss, boss_active = None, False
shoot_cooldown, magnet_timer, screen_flash_timer = 0, 0, 0
boss_army_active, extraction_timer, extraction_pt, extract_progress = False, 0, None, 0
show_changelog, changelog_scroll, changelog_max_scroll = False, 0, 0
pause_upgrade_scroll, arsenal_scroll_y, selected_arsenal_idx, arsenal_weapons_list = 0, 0, 0, []
show_inventory, drag_data, selected_mod_weapon = False, None, None
current_upgrade_choices, selected_upgrade_position = [], None
bunker_dummy = DummyTarget(MAP_WIDTH//2 + 200, MAP_HEIGHT//2 - 50)

def enter_bunker(success=False):
    global game_state, bullets, bunker_bullets, enemy_bullets, enemies, particles, items, trails, damage_texts, chests
    global boss, boss_active, shoot_cooldown, magnet_timer, screen_flash_timer
    global boss_army_active, extraction_timer, extraction_pt, extract_progress, enemy_spawn_timer

    if success:
        scrap_count = sum(i.count for i in player.inventory if i and i.type == "SCRAP")
        persistent_stats["scrap"] += scrap_count * 10 
        for i in range(24):
            if player.inventory[i] and player.inventory[i].type == "SCRAP":
                player.inventory[i] = None

    player.hp, player.shield = player.max_hp, player.max_shield
    player.ammo = player.base_max_ammo + player.mag_size_bonus
    
    bullets.clear(); bunker_bullets.clear(); enemy_bullets.clear(); enemies.clear()
    particles.clear(); items.clear(); trails.clear(); damage_texts.clear(); chests.clear()
    boss = None; boss_active = False
    shoot_cooldown, magnet_timer, screen_flash_timer = 0, 0, 0
    boss_army_active, extraction_timer, extraction_pt, extract_progress = False, 15*60*FPS, None, 0
    enemy_spawn_timer = 0
    
    player.x, player.y = MAP_WIDTH//2, MAP_HEIGHT//2
    game_state = "BUNKER"; stop_sound("boss_bgm")

def start_raid():
    global game_state, extraction_timer, extraction_pt, boss_army_active, extract_progress
    global bullets, enemy_bullets, enemies, particles, items, trails, damage_texts, chests
    global boss_active, boss, player, enemy_spawn_timer
    game_state = "PLAYING"
    player.x, player.y = MAP_WIDTH//2, MAP_HEIGHT//2
    bullets.clear(); enemy_bullets.clear(); enemies.clear(); particles.clear()
    items.clear(); trails.clear(); damage_texts.clear(); chests.clear()
    extraction_pt = ExtractionPoint()
    extraction_timer = 180 * FPS
    extract_progress, boss_army_active, boss_active, boss, enemy_spawn_timer = 0, False, False, None, 10
    for _ in range(15): chests.append(Chest(random.randint(400, MAP_WIDTH-400), random.randint(400, MAP_HEIGHT-400), "NORMAL"))
    for _ in range(5): chests.append(Chest(random.randint(400, MAP_WIDTH-400), random.randint(400, MAP_HEIGHT-400), "LOCKED"))
    play_sound("boss_bgm", loop=-1)

def full_wipe(mode="NORMAL"):
    global player, game_mode, chosen_upgrades, lost_item, defeated_boss_levels
    game_mode = mode; player = Player(); chosen_upgrades.clear(); lost_item = None; defeated_boss_levels.clear()
    enter_bunker(success=False)

def resolve_chest_collision(entity, chests_list):
    hit_chest = False
    for c in chests_list:
        if entity.rect.colliderect(c.rect):
            hit_chest = True
            overlap_l = entity.rect.right - c.rect.left
            overlap_r = c.rect.right - entity.rect.left
            overlap_t = entity.rect.bottom - c.rect.top
            overlap_b = c.rect.bottom - entity.rect.top
            
            min_overlap = min(overlap_l, overlap_r, overlap_t, overlap_b)
            if min_overlap == overlap_l: entity.x -= overlap_l
            elif min_overlap == overlap_r: entity.x += overlap_r
            elif min_overlap == overlap_t: entity.y -= overlap_t
            elif min_overlap == overlap_b: entity.y += overlap_b
            entity.rect.center = (int(entity.x), int(entity.y))
    return hit_chest

full_wipe("NORMAL")
game_state = "MENU"
dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); dim_surface.fill((0, 0, 0, 180))

# 按鈕定義
start_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 20, 220, 50)
changelog_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 100, 220, 50)
exit_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 180, 220, 50)

normal_button = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 - 60, 210, 230)
challenge_button = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 - 60, 210, 230)
difficulty_back_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 200, 220, 50)

changelog_close_button = pygame.Rect(WIDTH//2 + 205, HEIGHT//2 - 195, 35, 35)
restart_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 100, 220, 50)
menu_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 170, 220, 50)

cards = [pygame.Rect(WIDTH//2 - 350 + i*240, HEIGHT//2 - 150, 220, 320) for i in range(3)]
confirm_upgrade_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 190, 220, 50)

shop_bg = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 - 250, 600, 500) 
stash_bg = pygame.Rect(WIDTH//2 - 380, HEIGHT//2 - 250, 760, 500) 
mod_bg = pygame.Rect(WIDTH//2 - 380, HEIGHT//2 - 260, 760, 520) 
wep_stash_bg = pygame.Rect(WIDTH//2 - 380, HEIGHT//2 - 280, 760, 560) 

btn_shop_close = pygame.Rect(WIDTH//2 + 250, HEIGHT//2 - 240, 40, 40)
btn_stash_close = pygame.Rect(WIDTH//2 + 335, HEIGHT//2 - 240, 35, 35)
btn_mod_close = pygame.Rect(WIDTH//2 + 335, HEIGHT//2 - 250, 35, 35) 
btn_wep_close = pygame.Rect(WIDTH//2 + 335, HEIGHT//2 - 270, 35, 35)

btn_hp = pygame.Rect(WIDTH//2 - 260, HEIGHT//2 - 140, 240, 70)
btn_dmg = pygame.Rect(WIDTH//2 + 20,  HEIGHT//2 - 140, 240, 70)
btn_spd  = pygame.Rect(WIDTH//2 - 260, HEIGHT//2 - 40,  240, 70)
btn_stamina = pygame.Rect(WIDTH//2 + 20,  HEIGHT//2 - 40,  240, 70)
btn_shield = pygame.Rect(WIDTH//2 - 260, HEIGHT//2 + 60,  240, 70)
btn_energy = pygame.Rect(WIDTH//2 + 20,  HEIGHT//2 + 60,  240, 70)

list_rect = pygame.Rect(WIDTH//2 - 280, HEIGHT//2 - 200, 560, 300)
btn_prim_w = pygame.Rect(WIDTH//2 - 160, HEIGHT//2 + 235, 140, 40) 
btn_sec_w = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 235, 140, 40)   
rect_prim = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 180, 160, 80) 
rect_sec = pygame.Rect(WIDTH//2 - 170, HEIGHT//2 - 180, 160, 80)  
upg_btn = pygame.Rect(WIDTH//2 + 70, HEIGHT//2 + 40, 230, 45)     
reroll_btn = pygame.Rect(WIDTH//2 + 70, HEIGHT//2 + 110, 230, 45) 

s_start_x, s_start_y = WIDTH//2 - 350, HEIGHT//2 - 150       
p_start_x_s, p_start_y_s = WIDTH//2 + 30, HEIGHT//2 - 150    
p_start_x_m, p_start_y_m = WIDTH//2 - 350, HEIGHT//2 - 40    
p_start_x_w, p_start_y_w = WIDTH//2 - 344, HEIGHT//2 + 115   

running = True 

while running:
    if 'lost_item' in globals() and lost_item:
        try: lost_item.rect.center = (int(lost_item.x), int(lost_item.y))
        except Exception: pass
        
    m_x, m_y = pygame.mouse.get_pos()
    m_pos = (m_x, m_y)
    hovered_slot_info = None

    # 處理畫面震動
    shake_x = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
    shake_y = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
    if screen_shake > 0: screen_shake -= 1

    #視角旋轉與游標同步
    # 取得滑鼠相對於畫面正中心 玩家的向量
    screen_dx = m_x - WIDTH // 2
    # 根據不同的視角模式，給予正確的 Y 軸還原倍率，讓轉視角保持正圓平滑手感
    if view_mode == "FPS":
        screen_dy = (m_y - HEIGHT * 0.8) / 0.3
    else:
        screen_dy = (m_y - HEIGHT // 2) / 0.5

    # 當游標不在畫面正中心時，才進行視角轉動 (避免手抖造成畫面亂晃)
    if game_state in ["PLAYING", "BUNKER"] and not show_inventory and view_mode != "CLASSIC":
        aim_dx = world_mouse_x - player.x
        aim_dy = world_mouse_y - player.y

        if math.hypot(screen_dx, screen_dy) > 30:
            # 絕對視角映射，直接把游標在螢幕的方位，當作相機要轉向的「固定角度」
            target_cam_angle = math.atan2(screen_dy, screen_dx) + math.pi / 2
            
            # 平滑緩動 (數值 0.08 讓轉向滑順，游標停下鏡頭就會停下，不會瘋狂轉圈)
            angle_diff = (target_cam_angle - camera_angle + math.pi) % (2 * math.pi) - math.pi
            camera_angle += angle_diff * 0.08  

    #  視角更新後重新精準計算世界座標的瞄準點槍口與滑鼠同步
    world_mouse_x, world_mouse_y = unproject_3d(m_x, m_y)
    mouse_btns = pygame.mouse.get_pressed()
    
    aim_dx = world_mouse_x - player.x
    aim_dy = world_mouse_y - player.y
    aim_dist = math.hypot(aim_dx, aim_dy)
    if aim_dist > 0:
        player.aim_dir_x = aim_dx / aim_dist
        player.aim_dir_y = aim_dy / aim_dist

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

            if event.key == pygame.K_v:
                # 三種視角切換
                modes = ["ISOMETRIC", "FPS", "CLASSIC"]
                view_mode = modes[(modes.index(view_mode) + 1) % len(modes)]
                if view_mode == "CLASSIC":
                    camera_angle = 0.0 # 切換回2D時將角度歸零，避免視角歪斜
                play_sound("exp")

            if event.key == pygame.K_h and game_state == "PLAYING" and not show_inventory: player.use_med()
            
            if event.key == pygame.K_x and hovered_slot_info:
                val = get_sell_value(hovered_slot_info["item"])
                if val > 0:
                    persistent_stats["scrap"] += val
                    if hovered_slot_info["source"] == "PLAYER": player.inventory[hovered_slot_info["idx"]] = None
                    elif hovered_slot_info["source"] == "STASH": persistent_stats["general_stash"][hovered_slot_info["idx"]] = None
                    elif hovered_slot_info["source"] == "ARSENAL":
                        persistent_stats["weapon_stash"].pop(hovered_slot_info["idx"])
                        sort_weapon_stash(); arsenal_weapons_list = [generate_weapon(n, "白") for n in WEAPON_TYPES] + persistent_stats["weapon_stash"]
                    play_sound("exp"); hovered_slot_info, selected_mod_weapon = None, None 

            if event.key == pygame.K_r and game_state == "DIED": 
                player = Player(); chosen_upgrades.clear(); enter_bunker(success=False)
            
            if event.key == pygame.K_e and game_state == "PLAYING":
                player.current_weapon_idx = (player.current_weapon_idx + 1) % len(player.weapons); play_sound("exp")

            if event.key == pygame.K_r and game_state == "PLAYING" and game_mode == "CHALLENGE" and player.reload_timer <= 0 and player.ammo < (player.base_max_ammo + player.mag_size_bonus):
                player.reload_timer = player.reload_duration
                
            if game_state == "PLAYING":
                key_buffer.append(event.key)
                if len(key_buffer) > len(CHEAT_CODE): key_buffer.pop(0) 
                if key_buffer == CHEAT_CODE: 
                    player.god_mode = not player.god_mode; player.cheat_all_weapons = player.god_mode 
                    if player.cheat_all_weapons: player.weapons = [generate_weapon(n, "金") for n in WEAPON_TYPES]
                    else: player.weapons = [player.primary_weapon, player.secondary_weapon]
                    player.current_weapon_idx = 0; play_sound("levelup"); key_buffer = [] 

        if show_inventory and game_state == "PLAYING":
            slot_size, margin, start_x, start_y = 50, 8, WIDTH//2 - 170, HEIGHT//2 - 50
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in range(24):
                        rect = pygame.Rect(start_x + (i%6)*(slot_size+margin), start_y + (i//6)*(slot_size+margin), slot_size, slot_size)
                        if rect.collidepoint(event.pos) and player.inventory[i]:
                            drag_data = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}; player.inventory[i] = None; break
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
                    if item.type == "WEAPON": items.append(DropItem(player.x, player.y, "WEAPON", weapon_obj=item.weapon_obj))
                    else: items.append(DropItem(player.x, player.y, item.type, count=item.count))
                elif not dropped_in_slot: put_item_in_slot(drag_data["source"], drag_data["idx"], drag_data["item"])
                drag_data = None
                
        elif game_state == "GENERAL_STASH":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in range(36):
                        rect = pygame.Rect(s_start_x + (i%6)*58, s_start_y + (i//6)*58, 50, 50)
                        if rect.collidepoint(event.pos) and persistent_stats["general_stash"][i]:
                            drag_data = {"source": "STASH", "idx": i, "item": persistent_stats["general_stash"][i]}
                            persistent_stats["general_stash"][i] = None; break
                    if not drag_data:
                        for i in range(24):
                            rect = pygame.Rect(p_start_x_s + (i%6)*58, p_start_y_s + (i//6)*58, 50, 50)
                            if rect.collidepoint(event.pos) and player.inventory[i]:
                                drag_data = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}
                                player.inventory[i] = None; break
                    if btn_stash_close.collidepoint(event.pos): game_state = "BUNKER"
                elif event.button == 3: 
                    for i in range(36):
                        rect = pygame.Rect(s_start_x + (i%6)*58, s_start_y + (i//6)*58, 50, 50)
                        if rect.collidepoint(event.pos) and persistent_stats["general_stash"][i]:
                            if fast_transfer(persistent_stats["general_stash"][i], player.inventory): persistent_stats["general_stash"][i] = None; play_sound("exp")
                    for i in range(24):
                        rect = pygame.Rect(p_start_x_s + (i%6)*58, p_start_y_s + (i//6)*58, 50, 50)
                        item = player.inventory[i]
                        if rect.collidepoint(event.pos) and item and item.type != "WEAPON":
                            if fast_transfer(item, persistent_stats["general_stash"]): player.inventory[i] = None; play_sound("exp")
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drag_data:
                dropped = False
                for i in range(36):
                    rect = pygame.Rect(s_start_x + (i%6)*58, s_start_y + (i//6)*58, 50, 50)
                    if rect.collidepoint(event.pos):
                        if drag_data["item"].type == "WEAPON": break 
                        rem = put_item_in_slot("STASH", i, drag_data["item"])
                        if rem: put_item_in_slot(drag_data["source"], drag_data["idx"], rem)
                        dropped = True; break
                if not dropped:
                    for i in range(24):
                        rect = pygame.Rect(p_start_x_s + (i%6)*58, p_start_y_s + (i//6)*58, 50, 50)
                        if rect.collidepoint(event.pos):
                            rem = put_item_in_slot("PLAYER", i, drag_data["item"])
                            if rem: put_item_in_slot(drag_data["source"], drag_data["idx"], rem)
                            dropped = True; break
                if not dropped: put_item_in_slot(drag_data["source"], drag_data["idx"], drag_data["item"])
                drag_data = None
                
        elif game_state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_changelog:
                    if changelog_close_button.collidepoint(event.pos) or changelog_button.collidepoint(event.pos): show_changelog, changelog_scroll = False, 0
                else:
                    if start_button.collidepoint(event.pos): game_state = "DIFFICULTY"
                    elif changelog_button.collidepoint(event.pos): show_changelog, changelog_scroll = True, 0
                    elif exit_button.collidepoint(event.pos): running = False
                    
        elif game_state == "DIFFICULTY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if normal_button.collidepoint(event.pos): full_wipe("NORMAL")
                elif challenge_button.collidepoint(event.pos): full_wipe("CHALLENGE")
                elif difficulty_back_button.collidepoint(event.pos): game_state = "MENU"
                
        elif game_state == "BUNKER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                p_rect = player.rect.copy()
                door = pygame.Rect(MAP_WIDTH//2 - 60, MAP_HEIGHT//2 + 200, 120, 60)
                shop = pygame.Rect(MAP_WIDTH//2 - 350, MAP_HEIGHT//2 - 50, 100, 100)
                mod_st = pygame.Rect(MAP_WIDTH//2 - 150, MAP_HEIGHT//2 - 150, 100, 100)
                gen_st = pygame.Rect(MAP_WIDTH//2 + 50, MAP_HEIGHT//2 - 150, 100, 100)
                wep_st = pygame.Rect(MAP_WIDTH//2 + 250, MAP_HEIGHT//2 - 50, 100, 100)
                
                if p_rect.colliderect(door): start_raid()
                elif p_rect.colliderect(shop): game_state = "SHOP"; play_sound("exp")
                elif p_rect.colliderect(gen_st): game_state = "GENERAL_STASH"; play_sound("exp")
                elif p_rect.colliderect(mod_st): game_state = "MOD_STATION"; selected_mod_weapon = None; play_sound("exp")
                elif p_rect.colliderect(wep_st): 
                    game_state = "WEAPON_STASH"; play_sound("exp"); selected_arsenal_idx = 0; arsenal_scroll_y = 0
                    if player.cheat_all_weapons:
                        player.god_mode, player.cheat_all_weapons = False, False
                        player.weapons = [player.primary_weapon, player.secondary_weapon]; player.current_weapon_idx = 0
                    sort_weapon_stash()
                    arsenal_weapons_list = [generate_weapon(n, "白") for n in WEAPON_TYPES] + persistent_stats["weapon_stash"]
                    
        elif game_state == "SHOP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_hp.collidepoint(event.pos) and persistent_stats["scrap"] >= 50:
                    persistent_stats["scrap"] -= 50; persistent_stats["max_hp"] += 10; player.max_hp += 10; player.hp += 10; play_sound("levelup")
                elif btn_dmg.collidepoint(event.pos) and persistent_stats["scrap"] >= 50:
                    persistent_stats["scrap"] -= 50; persistent_stats["dmg_bonus"] += 2; player.bullet_damage_bonus += 2; play_sound("levelup")
                elif btn_spd.collidepoint(event.pos) and persistent_stats["scrap"] >= 50:
                    persistent_stats["scrap"] -= 50; persistent_stats["speed_bonus"] += 0.2; player.base_speed += 0.2; play_sound("levelup")
                elif btn_stamina.collidepoint(event.pos) and persistent_stats["scrap"] >= 50:
                    persistent_stats["scrap"] -= 50; persistent_stats["max_stamina"] += 20; player.max_stamina += 20; player.stamina += 20; play_sound("levelup")
                elif btn_shield.collidepoint(event.pos) and persistent_stats["scrap"] >= 50:
                    persistent_stats["scrap"] -= 50; persistent_stats["max_shield"] += 20; player.max_shield += 20; player.shield += 20; play_sound("levelup")
                elif btn_energy.collidepoint(event.pos) and persistent_stats["scrap"] >= 50:
                    persistent_stats["scrap"] -= 50; persistent_stats["max_energy"] += 20; player.max_energy += 20; player.energy += 20; play_sound("levelup")
                elif btn_shop_close.collidepoint(event.pos): game_state = "BUNKER"
                
        elif game_state == "WEAPON_STASH":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_wep_close.collidepoint(event.pos): game_state = "BUNKER"
                elif list_rect.collidepoint(m_pos):
                    rel_y = m_pos[1] - list_rect.y + arsenal_scroll_y
                    idx = int(rel_y // 50) * 2 + (0 if m_pos[0] < WIDTH//2 else 1)
                    if 0 <= idx < len(arsenal_weapons_list): selected_arsenal_idx = idx; play_sound("exp")
                
                if 0 <= selected_arsenal_idx < len(arsenal_weapons_list):
                    sel_wep = arsenal_weapons_list[selected_arsenal_idx]
                    if btn_prim_w.collidepoint(m_pos):
                        if player.primary_weapon.rarity != "白": persistent_stats["weapon_stash"].append(player.primary_weapon)
                        player.primary_weapon = sel_wep; player.weapons[0] = sel_wep; player.current_weapon_idx = 0
                        if selected_arsenal_idx >= 12: persistent_stats["weapon_stash"].pop(selected_arsenal_idx - 12)
                        sort_weapon_stash(); arsenal_weapons_list = [generate_weapon(n, "白") for n in WEAPON_TYPES] + persistent_stats["weapon_stash"]; play_sound("levelup")
                    elif btn_sec_w.collidepoint(m_pos):
                        if player.secondary_weapon.rarity != "白": persistent_stats["weapon_stash"].append(player.secondary_weapon)
                        player.secondary_weapon = sel_wep; player.weapons[1] = sel_wep; player.current_weapon_idx = 1
                        if selected_arsenal_idx >= 12: persistent_stats["weapon_stash"].pop(selected_arsenal_idx - 12)
                        sort_weapon_stash(); arsenal_weapons_list = [generate_weapon(n, "白") for n in WEAPON_TYPES] + persistent_stats["weapon_stash"]; play_sound("levelup")
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if list_rect.collidepoint(event.pos):
                    rel_y = event.pos[1] - list_rect.y + arsenal_scroll_y
                    idx = int(rel_y // 50) * 2 + (0 if event.pos[0] < WIDTH//2 else 1)
                    if 12 <= idx < len(arsenal_weapons_list):
                        wep = arsenal_weapons_list[idx]
                        if player.add_item(create_item("WEAPON", 1, wep)):
                            persistent_stats["weapon_stash"].pop(idx - 12); sort_weapon_stash()
                            arsenal_weapons_list = [generate_weapon(n, "白") for n in WEAPON_TYPES] + persistent_stats["weapon_stash"]; play_sound("exp")
                for i in range(24):
                    rect = pygame.Rect(p_start_x_w + (i%12)*58, p_start_y_w + (i//12)*58, 50, 50)
                    item = player.inventory[i]
                    if rect.collidepoint(event.pos) and item and item.type == "WEAPON":
                        persistent_stats["weapon_stash"].append(item.weapon_obj)
                        player.inventory[i] = None; sort_weapon_stash()
                        arsenal_weapons_list = [generate_weapon(n, "白") for n in WEAPON_TYPES] + persistent_stats["weapon_stash"]; play_sound("exp")
                        
        elif game_state == "MOD_STATION":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                p_x, p_y = WIDTH//2 - 320, HEIGHT//2 + 20
                if rect_prim.collidepoint(event.pos): selected_mod_weapon = player.primary_weapon
                elif rect_sec.collidepoint(event.pos): selected_mod_weapon = player.secondary_weapon
                else:
                    for i in range(24):
                        if pygame.Rect(p_x + (i%6)*58, p_y + (i//6)*58, 50, 50).collidepoint(event.pos) and player.inventory[i] and player.inventory[i].type == "WEAPON":
                            selected_mod_weapon = player.inventory[i].weapon_obj; break
                            
                if btn_mod_close.collidepoint(event.pos): game_state = "BUNKER"
                
                if selected_mod_weapon:
                    if upg_btn.collidepoint(event.pos) and selected_mod_weapon.rarity != "金":
                        cost = {"白":50, "藍":150, "紫":300}[selected_mod_weapon.rarity]
                        if persistent_stats["scrap"] >= cost:
                            persistent_stats["scrap"] -= cost
                            selected_mod_weapon.rarity = {"白":"藍", "藍":"紫", "紫":"金"}[selected_mod_weapon.rarity]
                            pool = ["速射", "散射", "吸血", "爆擊"]
                            if selected_mod_weapon.bullet_type not in ["piercing", "laser", "cannon", "flamethrower"]: pool.append("穿透")
                            if selected_mod_weapon.bullet_type not in ["flamethrower", "flame_grenade"]: pool.append("燃燒")
                            selected_mod_weapon.affixes = random.sample(pool, min({"白":0, "藍":1, "紫":2, "金":3}[selected_mod_weapon.rarity], len(pool)))
                            apply_weapon_stats(selected_mod_weapon); play_sound("levelup")
                    if reroll_btn.collidepoint(event.pos) and selected_mod_weapon.rarity != "白":
                        cost = {"藍":30, "紫":80, "金":150}[selected_mod_weapon.rarity]
                        if persistent_stats["scrap"] >= cost:
                            persistent_stats["scrap"] -= cost
                            pool = ["速射", "散射", "吸血", "爆擊"]
                            if selected_mod_weapon.bullet_type not in ["piercing", "laser", "cannon", "flamethrower"]: pool.append("穿透")
                            if selected_mod_weapon.bullet_type not in ["flamethrower", "flame_grenade"]: pool.append("燃燒")
                            selected_mod_weapon.affixes = random.sample(pool, min({"白":0, "藍":1, "紫":2, "金":3}[selected_mod_weapon.rarity], len(pool)))
                            apply_weapon_stats(selected_mod_weapon); play_sound("exp")
                            
        elif game_state == "PAUSED":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 10, 220, 50).collidepoint(event.pos): game_state = "PLAYING"
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 10, 220, 50).collidepoint(event.pos): enter_bunker(success=False)
                elif pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 80, 220, 50).collidepoint(event.pos): full_wipe("NORMAL")
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 80, 220, 50).collidepoint(event.pos): running = False
                
        elif game_state == "LEVEL_UP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected_upgrade_position is not None and confirm_upgrade_button.collidepoint(event.pos): apply_upgrade(current_upgrade_choices[selected_upgrade_position])
                else:
                    for i, card in enumerate(cards):
                        if i < len(current_upgrade_choices) and card.collidepoint(event.pos): selected_upgrade_position = i; break

    # 遊戲邏輯更新 =================================================================
    if game_state == "BUNKER":
        bunker_clamp = pygame.Rect(MAP_WIDTH//2 - 400, MAP_HEIGHT//2 - 300, 800, 600)
        player.update(clamp_rect=bunker_clamp)

        if bunker_dummy: bunker_dummy.update()
        if mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing:
            wep = player.weapons[player.current_weapon_idx]
            
            # 使用精準的 3D 同步游標座標
            base_dir = pygame.math.Vector2(player.aim_dir_x, player.aim_dir_y)
            
            player.current_spread = min(player.bullet_spread + 25.0, player.current_spread + wep.base_recoil)
            t_bullets = player.bullet_count + (4 if wep.bullet_type == "shotgun" else 0) + (2 if "散射" in wep.affixes else 0)
            s_angle = -(t_bullets - 1) * player.current_spread / 2
            
            if wep.bullet_type in ["cannon", "flame_grenade"]: screen_shake = 5
            elif wep.bullet_type == "shotgun": screen_shake = 2

            for i in range(t_bullets):
                s_dir = base_dir.rotate(s_angle + i * player.current_spread)
                for j in range(1 + player.extra_same_path_bullets):
                    off = s_dir * (j * 15)
                    muzzle_x, muzzle_y = player.x + player.aim_dir_x * 18, player.y + player.aim_dir_y * 18 * 2
                    tx, ty = muzzle_x + s_dir.x * 100 + off.x, muzzle_y + s_dir.y * 100 + off.y
                    if wep.bullet_type == "flamethrower": tx += random.randint(-40, 40); ty += random.randint(-40, 40)
                    bunker_bullets.append(Bullet(muzzle_x + off.x, muzzle_y + off.y, tx, ty, wep, player.guidance_level, player.bullet_damage_bonus))
            shoot_cooldown = wep.shoot_delay
            play_sound(wep.sound_name)
            
        for b in bunker_bullets[:]:
            b.update()
            if bunker_dummy and b.rect.colliderect(bunker_dummy.rect):
                damage_texts.append(DamageText(b.x, b.y - 20, b.damage, RED if b.is_crit else WHITE, b.is_crit))
                bunker_dummy.hit_log.append((pygame.time.get_ticks(), b.damage))
                bunker_dummy.shake_timer = 5
                for _ in range(3): particles.append(Particle(b.x, b.y, b.color))
                play_sound("hit")
                if not b.is_piercing: bunker_bullets.remove(b)
            elif b.lifespan <= 0 or not pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT).colliderect(b.rect): bunker_bullets.remove(b)

        for p in particles[:]: p.update(); particles.remove(p) if p.timer <= 0 else None
        for dt in damage_texts[:]: dt.update(); damage_texts.remove(dt) if dt.timer <= 0 else None
        if shoot_cooldown > 0: shoot_cooldown -= 1
        
    elif game_state == "PLAYING" and not show_inventory:
        if enemy_spawn_timer > 0: enemy_spawn_timer -= 1
        if enemy_spawn_timer <= 0 and not boss_army_active:
            if len(enemies) < 150: enemies.append(Enemy(player.level, random.random() < 0.15, player.x, player.y))
            enemy_spawn_timer = max(5, 30 - player.level) 
            
        if magnet_timer > 0: magnet_timer -= 1
        if screen_flash_timer > 0: screen_flash_timer -= 1
        
        if extraction_timer > 0: extraction_timer -= 1
        if extraction_timer <= 0:
            boss_army_active = True
            if pygame.time.get_ticks() % 15 == 0:
                e = Enemy(player.level + 15, is_elite=True)
                e.max_hp *= 4; e.hp = e.max_hp; e.speed *= 1.3; e.color = DARK_PURPLE
                e.weapon = generate_weapon("機槍", "紫"); enemies.append(e)

        if extraction_pt:
            dist_to_ext = math.sqrt((player.x - extraction_pt.x)**2 + (player.y - extraction_pt.y)**2)
            if dist_to_ext < extraction_pt.radius:
                extract_progress += 1
                if extract_progress >= 120: play_sound("levelup"); enter_bunker(success=True)
            else: extract_progress = 0

        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_f]:
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
                                        if player.inventory[i].count <= 0: player.inventory[i] = None; break
                            open_chest(c)
                            
            for g in items[:]:
                if g.item_type not in ["EXP", "MAGNET", "BOMB", "SHIELD"] and math.hypot(player.x - g.x, player.y - g.y) < 70:
                    new_item = create_item("WEAPON", 1, g.weapon_obj) if g.item_type == "WEAPON" else create_item(g.item_type, g.count)
                    if player.add_item(new_item): items.remove(g); play_sound("exp")
        else:
            for c in chests:
                if c.state == "CLOSED": c.open_progress = max(0, c.open_progress - 2)

        if player.exp >= player.max_exp:
            player.exp -= player.max_exp; player.level += 1; player.max_exp = int(player.max_exp * 1.25)
            choose_upgrade_cards(); game_state = "LEVEL_UP"; play_sound("levelup") 
            
        if player.level % 5 == 0 and player.level > 0 and player.level not in defeated_boss_levels and not boss_active and not boss_army_active:
            boss = Boss(random.choice(["YELLOW", "RED", "PURPLE", "CYAN"]), player.level, player.x, player.y)
            boss_active = True; play_sound("boss_bgm", loop=-1) 

        current_wep = player.weapons[player.current_weapon_idx]

        if mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing:
            can_fire = True
            if game_mode == "CHALLENGE":
                if player.ammo <= 0: can_fire = False; player.reload_timer = player.reload_duration if player.reload_timer <= 0 else player.reload_timer
                else: player.ammo -= 1; player.reload_timer = player.reload_duration if player.ammo <= 0 else player.reload_timer
            
            if can_fire:
                base_dir = pygame.math.Vector2(player.aim_dir_x, player.aim_dir_y)
                player.current_spread = min(player.bullet_spread + 25.0, player.current_spread + current_wep.base_recoil)
                t_bullets = player.bullet_count + (4 if current_wep.bullet_type == "shotgun" else 0) + (2 if "散射" in current_wep.affixes else 0)
                s_angle = -(t_bullets - 1) * player.current_spread / 2
                
                if current_wep.bullet_type in ["cannon", "flame_grenade"]: screen_shake = 5
                elif current_wep.bullet_type == "shotgun": screen_shake = 2

                for i in range(t_bullets):
                    s_dir = base_dir.rotate(s_angle + i * player.current_spread)
                    for j in range(1 + player.extra_same_path_bullets):
                        spawn_offset = s_dir * (j * 15) 
                        muzzle_x, muzzle_y = player.x + player.aim_dir_x * 18, player.y + player.aim_dir_y * 18 * 2
                        tx, ty = muzzle_x + s_dir.x * 100 + spawn_offset.x, muzzle_y + s_dir.y * 100 + spawn_offset.y
                        if current_wep.bullet_type == "flamethrower": tx += random.randint(-40, 40); ty += random.randint(-40, 40)
                        bullets.append(Bullet(muzzle_x + spawn_offset.x, muzzle_y + spawn_offset.y, tx, ty, current_wep, player.guidance_level, player.bullet_damage_bonus))
                        
                shoot_cooldown = max(2, current_wep.shoot_delay - player.shoot_delay_reduction)
                play_sound(current_wep.sound_name)

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
                closest = min(enemies, key=lambda e: math.sqrt((e.x - player.x)**2 + (e.y - player.y)**2), default=None)
                if closest and math.sqrt((closest.x - player.x)**2 + (closest.y - player.y)**2) < 400:
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
                        if e in enemies: enemies.remove(e)
            if boss_active and boss.state != "DEFEAT":
                if math.sqrt((boss.x - player.x)**2 + (boss.y - player.y)**2) <= aura_radius: boss.hp -= aura_damage
                
        if player.is_dashing: trails.append(DashTrail(player.rect.centerx, player.rect.centery, player.size))
        for t in trails[:]: t.update(); trails.remove(t) if t.life <= 0 else None
            
        map_rect = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
        alive_bullets = []

        for b in bullets:
            b.update(enemies)
            hit_chest = False
            for c in chests:
                if b.rect.colliderect(c.rect):
                    hit_chest = True
                    if not b.is_piercing:
                        for _ in range(3): particles.append(Particle(b.x, b.y, GRAY))
                        play_sound("hit")
                    break
            
            if hit_chest and not b.is_piercing: continue
            
            if b.explode:
                screen_shake = 8; play_sound("shoot_cannon") 
                for _ in range(30): particles.append(Particle(b.x, b.y, ORANGE))
                for e in enemies[:]:
                    if math.hypot(e.x - b.x, e.y - b.y) < 120: 
                        actual_dmg = b.damage
                        if e.shield > 0:
                            leftover = actual_dmg - e.shield; e.shield = max(0, e.shield - actual_dmg)
                            if leftover > 0: e.hp -= leftover
                        else: e.hp -= actual_dmg
                        
                        if e.hp <= 0: 
                            if random.random() < 0.4: items.append(DropItem(e.x, e.y, "EXP"))
                            if e in enemies: enemies.remove(e)
                            
                if boss_active and boss.state != "DEFEAT" and math.hypot(boss.x - b.x, boss.y - b.y) < 150: boss.hp -= b.damage
                continue 
                
            hit_something = False
            for e in enemies[:]:
                if b.rect.colliderect(e.rect):
                    if b.b_type == "frost": e.frost_timer = 120 
                    if b.b_type == "cannon": 
                        push_dist = math.hypot(e.x - player.x, e.y - player.y)
                        if push_dist > 0: e.x += ((e.x - player.x) / push_dist) * 30; e.y += ((e.y - player.y) / push_dist) * 30 
                    elif b.b_type == "flame_grenade": b.explode = True; break
                        
                    if b.is_burning: e.burn_timer = 180
                    if b.is_vampiric and random.random() < 0.05: player.hp = min(player.max_hp, player.hp + 2)
                        
                    if e.shield > 0:
                        leftover = b.damage - e.shield; e.shield = max(0, e.shield - b.damage)
                        if leftover > 0: e.hp -= leftover
                    else: e.hp -= b.damage
                        
                    e.hit_timer = 4  
                    if e.combat_type != "kamikaze":
                        kb_force = min(6.0, b.damage * 0.1) 
                        if b.is_crit: kb_force *= 1.5
                        e.x += b.dir_x * kb_force; e.y += b.dir_y * kb_force
                    
                    if b.is_crit or b.damage >= 50:
                        screen_shake = max(screen_shake, 6)
                        pygame.time.delay(12)               

                    damage_texts.append(DamageText(e.x, e.y - 20, b.damage, RED if b.is_crit else (YELLOW if b.damage >= 40 else WHITE), b.is_crit))
                    hit_something = True
                    for _ in range(5): particles.append(Particle(e.x, e.y, b.color))
                    play_sound("hit")
                    if e.hp <= 0 and e in enemies:
                        for _ in range(10): particles.append(Particle(e.x, e.y, RED))
                        if e.is_elite: 
                            items.append(DropItem(e.x-15, e.y, "EXP")); items.append(DropItem(e.x+15, e.y, "MED")); items.append(DropItem(e.x, e.y+15, "SHIELD"))
                            items.append(DropItem(e.x, e.y-15, "SCRAP", random.randint(1,3)))
                            if random.random() < 0.3: items.append(DropItem(e.x+20, e.y, "KEY")) 
                        else:
                            rand_drop = random.random()
                            if rand_drop < 0.01: items.append(DropItem(e.x, e.y, "MAGNET"))
                            elif rand_drop < 0.02: items.append(DropItem(e.x, e.y, "BOMB"))
                            elif rand_drop < 0.15: items.append(DropItem(e.x, e.y, "SCRAP", random.randint(1,2)))
                            elif rand_drop < 0.35: items.append(DropItem(e.x, e.y, "EXP"))
                            elif rand_drop < 0.40: items.append(DropItem(e.x, e.y, "MED"))
                        enemies.remove(e)
                    
                    if not b.is_piercing: break 
            
            if boss_active and b.rect.colliderect(boss.rect):
                hit_something = True
                if boss.b_type == "YELLOW" and boss.state == "EVADE":
                    for _ in range(5): particles.append(Particle(boss.x, boss.y, GRAY))
                else:
                    if b.b_type == "frost": boss.frost_timer = 60 
                    if b.is_burning: boss.burn_timer = 180
                    if b.is_vampiric and random.random() < 0.05: player.hp = min(player.max_hp, player.hp + 2)
                    boss.hp -= b.damage
                    boss.hit_timer = 4
                    if b.is_crit or b.damage >= 50:
                        screen_shake = max(screen_shake, 8) 
                        pygame.time.delay(15)              
                    damage_texts.append(DamageText(boss.x, boss.y - 20, b.damage, RED if b.is_crit else WHITE, b.is_crit))
                    for _ in range(8): particles.append(Particle(boss.x, boss.y, YELLOW))
                    play_sound("hit")
                    if boss.hp <= 0:
                        boss_active = False; defeated_boss_levels.append(player.level); stop_sound("boss_bgm") 
                        for _ in range(40): items.append(DropItem(boss.x + random.randint(-60,60), boss.y + random.randint(-60,60), "EXP"))
                        for _ in range(10): items.append(DropItem(boss.x + random.randint(-40,40), boss.y + random.randint(-40,40), "SCRAP", random.randint(2,5)))
                        items.append(DropItem(boss.x, boss.y, "KEY"))
                        for _ in range(50): particles.append(Particle(boss.x, boss.y, YELLOW))

            if b.lifespan > 0 and map_rect.colliderect(b.rect) and (not hit_something or b.is_piercing) and not b.explode: alive_bullets.append(b)
        bullets = alive_bullets

        for dt in damage_texts[:]:
            dt.update()
            if dt.timer <= 0: damage_texts.remove(dt)
        for p in particles[:]:
            p.update()
            if p.timer <= 0: particles.remove(p)

        for eb in enemy_bullets[:]:
            eb.update(player.x, player.y)
            hit_chest = False
            for c in chests:
                if eb.rect.colliderect(c.rect):
                    hit_chest = True
                    if eb.b_type not in ["piercing", "laser"]:
                        for _ in range(3): particles.append(Particle(eb.x, eb.y, GRAY))
                        play_sound("hit")
                    break
            if hit_chest and eb.b_type not in ["piercing", "laser"]:
                enemy_bullets.remove(eb); continue
            
            if getattr(eb, 'explode', False):
                play_sound("shoot_cannon") 
                for i in range(12): 
                    p = Particle(eb.x, eb.y, eb.color); p.vel_x, p.vel_y = math.cos(i*30)*3, math.sin(i*30)*3; particles.append(p)
                if math.hypot(player.x - eb.x, player.y - eb.y) < 70:
                    if not player.god_mode and player.invincible_timer <= 0 and not player.is_dashing:
                        actual_dmg = max(1, int(eb.damage * 1.5) - player.damage_reduction)
                        if player.shield > 0:
                            if actual_dmg > player.shield: leftover = actual_dmg - player.shield; player.shield = 0; player.hp -= leftover
                            else: player.shield -= actual_dmg
                        else: player.hp -= actual_dmg
                        player.invincible_timer = player.invincible_duration; screen_shake = 12; play_sound("hurt")
                if eb in enemy_bullets: enemy_bullets.remove(eb)
                continue
            if not map_rect.colliderect(eb.rect): enemy_bullets.remove(eb)

        resolve_chest_collision(player, chests)

        for e in enemies:
            e.update(player.x, player.y, enemies, enemy_bullets)
            resolve_chest_collision(e, chests)

        if boss_active and boss:
            boss.update(player.x, player.y, bullets, enemies, enemy_bullets)
            if resolve_chest_collision(boss, chests):
                if boss.state in ["CHARGE", "DASH"]:
                    boss.state = "EVADE" if boss.b_type == "YELLOW" else "CHASE"
                    boss.state_timer = 0; screen_shake = 15; play_sound("shoot_cannon") 
                    for _ in range(15): particles.append(Particle(boss.x, boss.y, GRAY)) 

        for e in enemies[:]:
            if game_state == "DIED": break
            if player.rect.colliderect(e.rect):
                if player.god_mode: continue
                if player.invincible_timer <= 0 and not player.is_dashing:
                    actual_dmg = max(1, e.damage - player.damage_reduction)
                    if player.shield > 0:
                        if actual_dmg > player.shield: leftover = actual_dmg - player.shield; player.shield = 0; player.hp -= leftover
                        else: player.shield -= actual_dmg
                    else: player.hp -= actual_dmg
                    player.invincible_timer = player.invincible_duration; screen_shake = 10; play_sound("hurt")
                    
                if e.combat_type == "kamikaze":
                    for _ in range(15): particles.append(Particle(e.x, e.y, ORANGE))
                    if e in enemies: enemies.remove(e)
                    
        for eb in enemy_bullets[:]:
            if game_state == "DIED": break
            if player.rect.colliderect(eb.rect):
                if not player.god_mode and player.invincible_timer <= 0 and not player.is_dashing:
                    actual_dmg = max(1, 25 - player.damage_reduction)
                    if player.shield > 0:
                        if actual_dmg > player.shield: leftover = actual_dmg - player.shield; player.shield = 0; player.hp -= leftover
                        else: player.shield -= actual_dmg
                    else: player.hp -= actual_dmg
                    player.invincible_timer = player.invincible_duration; screen_shake = 10; play_sound("hurt")
                if eb in enemy_bullets: enemy_bullets.remove(eb)
                
        if boss_active and player.rect.colliderect(boss.rect) and game_state == "PLAYING": 
            if not player.god_mode and player.invincible_timer <= 0 and not player.is_dashing:
                actual_dmg = max(1, 40 - player.damage_reduction)
                if player.shield > 0:
                    if actual_dmg > player.shield: leftover = actual_dmg - player.shield; player.shield = 0; player.hp -= leftover
                    else: player.shield -= actual_dmg
                else: player.hp -= actual_dmg
                player.invincible_timer = player.invincible_duration; screen_shake = 10; play_sound("hurt")

        if player.hp <= 0 and game_state == "PLAYING":
            inv_copy = [item for item in player.inventory if item is not None]
            w1 = player.primary_weapon if player.primary_weapon.rarity != "白" else None
            w2 = player.secondary_weapon if player.secondary_weapon.rarity != "白" else None
            lost_item = PlayerLostItem(player.x, player.y, player.level, player.exp, list(chosen_upgrades), inv_copy, w1, w2)
            game_state = "DIED"; play_sound("gameover"); stop_sound("boss_bgm")

        if game_state == "PLAYING":
            eff_radius = 9999 if magnet_timer > 0 else player.magnet_radius
            for g in items[:]:
                g.update(player.x, player.y, eff_radius)
                if g.item_type in ["EXP", "MAGNET", "BOMB", "SHIELD"] and player.rect.colliderect(g.rect):
                    items.remove(g)
                    if g.item_type == "EXP": player.exp += 25 * player.exp_multiplier; play_sound("exp") 
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
                if lost_item.w1: items.append(DropItem(lost_item.x + random.randint(-40,40), lost_item.y + random.randint(-40,40), "WEAPON", weapon_obj=lost_item.w1))
                if lost_item.w2: items.append(DropItem(lost_item.x + random.randint(-40,40), lost_item.y + random.randint(-40,40), "WEAPON", weapon_obj=lost_item.w2))
                for item in lost_item.inventory:
                    if item.type == "WEAPON": items.append(DropItem(lost_item.x + random.randint(-40,40), lost_item.y + random.randint(-40,40), "WEAPON", weapon_obj=item.weapon_obj))
                    else: items.append(DropItem(lost_item.x + random.randint(-40,40), lost_item.y + random.randint(-40,40), item.type, count=item.count))
                lost_item = None; play_sound("levelup")

    # 畫面繪製
    if game_state in ["BUNKER", "SHOP", "GENERAL_STASH", "MOD_STATION", "WEAPON_STASH", "PLAYING", "PAUSED", "LEVEL_UP", "DIED"]:
        # REPLACED 風格：極致深邃的暗藍色虛空
        screen.fill((8, 10, 14)) 
        
        if view_mode != "CLASSIC":
            HORIZON = int(HEIGHT * 0.25) if view_mode == "FPS" else HEIGHT // 3
            
            sun_world_x = MAP_WIDTH + 1500  
            sun_world_y = MAP_HEIGHT // 2   
            sun_world_z = 350               
            
            sun_sx, sun_sy, sun_depth = project_3d(sun_world_x, sun_world_y, sun_world_z)
            if sun_depth > -5000:
                dist_to_sun = math.hypot(sun_world_x - player.x, sun_world_y - player.y)
                sun_radius = max(60, int(150000 / max(100, dist_to_sun))) 
                
                # Synthwave 漸層發光夕陽 (疊加多層 Alpha 製造濃厚電影 Bloom 效果)
                for i, alpha in enumerate([30, 60, 100, 255]):
                    r = int(sun_radius * (1.6 - i*0.2))
                    color = (255, 40, 80, alpha) if i < 3 else (255, 150, 50)
                    surface_sun = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
                    pygame.draw.circle(surface_sun, color, (r, r), r)
                    screen.blit(surface_sun, (int(sun_sx - r), int(sun_sy - r)))
        
        map_corners = [(0, 0), (MAP_WIDTH, 0), (MAP_WIDTH, MAP_HEIGHT), (0, MAP_HEIGHT)]
        proj_corners = [project_3d(cx, cy, 0)[:2] for cx, cy in map_corners]
        
        floor_img = images.get("floor")
        if floor_img:
            rot_floor = pygame.transform.rotate(floor_img, math.degrees(camera_angle))
            y_compress = 0.3 if view_mode == "FPS" else (1.0 if view_mode == "CLASSIC" else 0.5)
            w, h = rot_floor.get_size()
            scaled_floor = pygame.transform.scale(rot_floor, (w, int(h * y_compress)))
            center_sx, center_sy, _ = project_3d(MAP_WIDTH/2, MAP_HEIGHT/2, 0)
            screen.blit(scaled_floor, scaled_floor.get_rect(center=(center_sx, center_sy)))
        else:
            # 深淵暗藍基地地板
            pygame.draw.polygon(screen, (12, 14, 18), proj_corners) 
            
        # 電子邊界高光
        pygame.draw.polygon(screen, (0, 150, 255), proj_corners, 2) 
        
        # 幽暗科技網格 (不再是明亮的白線，而是沉穩的暗青色)
        grid_size = 150
        for x in range(0, MAP_WIDTH + 1, grid_size):
            p1 = project_3d(x, 0); p2 = project_3d(x, MAP_HEIGHT)
            if p1[2] > -5000 or p2[2] > -5000:
                pygame.draw.line(screen, (20, 35, 45), p1[:2], p2[:2], 2)
                
        for y in range(0, MAP_HEIGHT + 1, grid_size):
            p1 = project_3d(0, y); p2 = project_3d(MAP_WIDTH, y)
            if p1[2] > -5000 or p2[2] > -5000:
                pygame.draw.line(screen, (20, 35, 45), p1[:2], p2[:2], 2)

        # BUNKER 地堡面板立體廣告板與雷射圍牆
        if game_state in ["BUNKER", "SHOP", "GENERAL_STASH", "MOD_STATION", "WEAPON_STASH"]:
            # 畫出安全區的高科技雷射圍牆
            bx, by, bw, bh = MAP_WIDTH//2 - 400, MAP_HEIGHT//2 - 300, 800, 600
            wall_corners = [(bx, by), (bx+bw, by), (bx+bw, by+bh), (bx, by+bh)]
            
            for i in range(4):
                p1 = wall_corners[i]
                p2 = wall_corners[(i+1)%4]
                s1_bot = project_3d(p1[0], p1[1], 0)
                s2_bot = project_3d(p2[0], p2[1], 0)
                s1_top = project_3d(p1[0], p1[1], 150) # 牆高 150
                s2_top = project_3d(p2[0], p2[1], 150)
                
                # 確保牆面在鏡頭前方才渲染
                if s1_bot[2] > -5000 or s2_bot[2] > -5000:
                    
                    # 地堡牆壁貼圖
                    wall_img = images.get("bunker_wall")
                    if wall_img:
                        # 將 2D 圖片拉伸貼合在牆壁的 3D 邊界框內
                        min_x = min(s1_bot[0], s2_bot[0], s1_top[0], s2_top[0])
                        max_x = max(s1_bot[0], s2_bot[0], s1_top[0], s2_top[0])
                        min_y = min(s1_bot[1], s2_bot[1], s1_top[1], s2_top[1])
                        max_y = max(s1_bot[1], s2_bot[1], s1_top[1], s2_top[1])
                        w, h = max(1, max_x - min_x), max(1, max_y - min_y)
                        
                        scaled_wall = pygame.transform.scale(wall_img, (int(w), int(h)))
                        screen.blit(scaled_wall, (min_x, min_y))
                    else:
                        # 備用幾何雷射牆
                        pygame.draw.line(screen, (0, 255, 255), s1_bot[:2], s1_top[:2], 3)
                        pygame.draw.line(screen, (0, 255, 255), s2_bot[:2], s2_top[:2], 3)
                        
                        wall_polygon = [s1_bot[:2], s2_bot[:2], s2_top[:2], s1_top[:2]]
                        surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                        pygame.draw.polygon(surf, (0, 150, 255, 40), wall_polygon) 
                        screen.blit(surf, (0, 0))
                        
                        for j in range(0, 5): 
                            h_line = j * (150 / 4)
                            sm1 = project_3d(p1[0], p1[1], h_line)
                            sm2 = project_3d(p2[0], p2[1], h_line)
                            pygame.draw.line(screen, (0, 150, 255), sm1[:2], sm2[:2], 1)

            draw_terminal_billboard(screen, MAP_WIDTH//2 - 60, MAP_HEIGHT//2 + 200, 120, 60, GREEN, "部署閘門 [E]", "DEPLOY")
            draw_terminal_billboard(screen, MAP_WIDTH//2 - 350, MAP_HEIGHT//2 - 50, 100, 100, BLUE, "黑市商店 [E]", "SHOP")
            draw_terminal_billboard(screen, MAP_WIDTH//2 - 150, MAP_HEIGHT//2 - 150, 100, 100, ORANGE, "改造台 [E]", "MOD")
            draw_terminal_billboard(screen, MAP_WIDTH//2 + 50, MAP_HEIGHT//2 - 150, 100, 100, (50, 150, 200), "收藏箱 [E]", "STASH")
            draw_terminal_billboard(screen, MAP_WIDTH//2 + 250, MAP_HEIGHT//2 - 50, 100, 100, RED, "武器箱 [E]", "WEAPON")

        # 深度排序收集所有實體並依照 Z 軸深度 (rot_y) 排序
        render_entities = []
        if game_state in ["PLAYING", "PAUSED", "LEVEL_UP", "DIED"]:
            render_entities.extend(chests)
            render_entities.extend(items)
            render_entities.extend(enemies)
            if 'lost_item' in globals() and lost_item: render_entities.append(lost_item)
            if 'boss_active' in globals() and boss_active and boss: render_entities.append(boss)
        
        if game_state in ["BUNKER", "SHOP", "GENERAL_STASH", "MOD_STATION", "WEAPON_STASH"]:
            if bunker_dummy: render_entities.append(bunker_dummy)
            
        if game_state != "DIED": 
            render_entities.append(player)

        render_entities.sort(key=lambda obj: project_3d(obj.x, obj.y)[2])

        # 暫存真正的相機座標，並歸零，讓各物件的 draw 方法畫在「螢幕」而非「世界」
        temp_cam_x, temp_cam_y = camera_x, camera_y
        camera_x, camera_y = 0, 0

        # ==== 開始廣告板繪製 (Billboarding) ====
        for obj in render_entities:
            sx, sy, depth = project_3d(obj.x, obj.y, getattr(obj, 'z', 0))
            if depth < -5000: continue # 在相機正後方太遠，不畫
            
            # 畫腳底的影子
            obj_size = getattr(obj, 'size', 30)
            pygame.draw.ellipse(screen, (0, 0, 0, 120), (sx - obj_size*0.6, sy - obj_size*0.2, obj_size*1.2, obj_size*0.4))
            
            # 暫時覆寫實體的物理位置，轉交給各自的 draw 去畫出立起來的 2D 圖片
            temp_x, temp_y = obj.x, obj.y
            obj.x, obj.y = sx, sy 
            
            if obj == player:
                player.draw(screen, player.weapons[player.current_weapon_idx] if game_state in ["PLAYING", "BUNKER"] else None)
            else:
                obj.draw(screen)
                
            # 復原物理位置
            obj.x, obj.y = temp_x, temp_y

        # 特效深度轉換與渲染
        current_bullets = bunker_bullets if game_state in ["BUNKER", "SHOP", "GENERAL_STASH", "MOD_STATION", "WEAPON_STASH"] else bullets + enemy_bullets
        for b in current_bullets:
            sx, sy, depth = project_3d(b.x, b.y)
            if depth < -5000: continue
            temp_x, temp_y = b.x, b.y
            b.x, b.y = sx, sy
            b.draw(screen)
            b.x, b.y = temp_x, temp_y
            
        for p in particles:
            sx, sy, depth = project_3d(p.x, p.y)
            if depth < -5000: continue
            if p.size > 0: pygame.draw.rect(screen, p.color, (int(sx), int(sy), int(p.size), int(p.size)))

        for t in trails:
            sx, sy, depth = project_3d(t.x, t.y)
            if depth < -5000: continue
            temp_x, temp_y = t.x, t.y
            t.x, t.y = sx, sy
            t.draw(screen)
            t.x, t.y = temp_x, temp_y

        for dt in damage_texts:
            sx, sy, depth = project_3d(dt.x, dt.y)
            if depth < -5000: continue
            temp_x, temp_y = dt.x, dt.y
            dt.x, dt.y = sx, sy
            dt.draw(screen)
            dt.x, dt.y = temp_x, temp_y

        # 還原相機座標
        camera_x, camera_y = temp_cam_x, temp_cam_y

        # ==== 覆蓋在 3D 場景上的純 2D UI 介面 ====
        if game_state in ["BUNKER", "SHOP", "GENERAL_STASH", "MOD_STATION", "WEAPON_STASH"]:
            screen.blit(large_font.render("地堡安全屋", True, YELLOW), (WIDTH//2 - 120, 50))
            screen.blit(font.render(f"擁有廢料: {persistent_stats['scrap']}", True, SCRAP_COLOR), (WIDTH//2 - 70, 100))
            draw_upgrade_summary(screen, WIDTH - 260, 20, max_items=5)
            
            if game_state == "SHOP":
                screen.blit(dim_surface, (0, 0))
                draw_ui_panel(screen, shop_bg, "黑市升級 (BLACK MARKET)", BLUE)
                draw_hover_button(screen, btn_shop_close, "X", (180, 60, 60), RED, WHITE)
                draw_hover_button(screen, btn_hp, f"最大血量+10 (目前:{player.max_hp}) - 50廢料", GREEN if persistent_stats["scrap"]>=50 else GRAY, (50, 180, 50), BLACK)
                draw_hover_button(screen, btn_dmg, f"武器傷害+2 (目前:+{persistent_stats['dmg_bonus']}) - 50廢料", ORANGE if persistent_stats["scrap"]>=50 else GRAY, (200, 120, 0), BLACK)
                draw_hover_button(screen, btn_spd, f"移動速度+0.2 (目前:+{persistent_stats['speed_bonus']:.1f}) - 50廢料", CYAN if persistent_stats["scrap"]>=50 else GRAY, (0, 180, 180), BLACK)
                draw_hover_button(screen, btn_stamina, f"最大體力+20 (目前:{player.max_stamina}) - 50廢料", (220, 220, 80) if persistent_stats["scrap"]>=50 else GRAY, (255, 255, 100), BLACK)
                draw_hover_button(screen, btn_shield, f"最大護盾+20 (目前:{player.max_shield}) - 50廢料", (100, 150, 255) if persistent_stats["scrap"]>=50 else GRAY, (130, 180, 255), BLACK)
                draw_hover_button(screen, btn_energy, f"最大能量+20 (目前:{player.max_energy}) - 50廢料", (200, 100, 255) if persistent_stats["scrap"]>=50 else GRAY, (230, 130, 255), BLACK)
                scrap_txt = font.render(f"擁有廢料: {persistent_stats['scrap']}", True, SCRAP_COLOR)
                screen.blit(scrap_txt, (shop_bg.centerx - scrap_txt.get_width()//2, shop_bg.bottom - 40))
                
            elif game_state == "GENERAL_STASH":
                screen.blit(dim_surface, (0, 0))
                draw_ui_panel(screen, stash_bg, "格子收藏箱 (GENERAL STASH)", (50, 150, 200))
                for i in range(36):
                    col, row = i % 6, i // 6
                    rect = pygame.Rect(s_start_x + col*58, s_start_y + row*58, 50, 50)
                    pygame.draw.rect(screen, (25, 28, 35), rect, border_radius=6); pygame.draw.rect(screen, (55, 60, 70), rect, 1, border_radius=6)
                    item = persistent_stats["general_stash"][i]
                    if item and not (drag_data and drag_data["source"] == "STASH" and drag_data["idx"] == i):
                        c = HP_COLOR if item.type == "MED" else (SCRAP_COLOR if item.type == "SCRAP" else YELLOW)
                        pygame.draw.circle(screen, c, rect.center, 14)
                        screen.blit(tiny_font.render(str(item.count), True, WHITE), (rect.right - 18, rect.bottom - 18))
                        if rect.collidepoint(m_x, m_y) and not drag_data: hovered_slot_info = {"source": "STASH", "idx": i, "item": item}; pygame.draw.rect(screen, WHITE, rect, 2, border_radius=6)
                hi = draw_player_inv_grid(screen, p_start_x_s, p_start_y_s, m_x, m_y, allow_weapons=False)
                if hi: hovered_slot_info = hi
                screen.blit(small_font.render("背包與收藏箱不可放武器 | 游標指著按 [X] 出售", True, GRAY), (WIDTH//2 - 180, HEIGHT//2 + 250))
                draw_hover_button(screen, btn_stash_close, "X", (150, 50, 50), RED)
                
            elif game_state == "MOD_STATION":
                screen.blit(dim_surface, (0, 0))
                draw_ui_panel(screen, mod_bg, "武器改造台 (WORKBENCH)", ORANGE)
                draw_hover_button(screen, btn_mod_close, "X", (180, 60, 60), RED, WHITE)
                pygame.draw.rect(screen, (30,34,42), rect_prim, border_radius=8)
                screen.blit(small_font.render("主武器", True, WHITE), (rect_prim.centerx - 25, rect_prim.y + 12))
                w_name_1 = font.render(player.primary_weapon.base_name, True, get_rarity_color(player.primary_weapon.rarity))
                screen.blit(w_name_1, (rect_prim.centerx - w_name_1.get_width()//2, rect_prim.centery + 5))
                if selected_mod_weapon == player.primary_weapon: pygame.draw.rect(screen, YELLOW, rect_prim, 2, border_radius=8)
                elif rect_prim.collidepoint(m_pos): pygame.draw.rect(screen, WHITE, rect_prim, 1, border_radius=8)

                pygame.draw.rect(screen, (30,34,42), rect_sec, border_radius=8)
                screen.blit(small_font.render("副武器", True, WHITE), (rect_sec.centerx - 25, rect_sec.y + 12))
                w_name_2 = font.render(player.secondary_weapon.base_name, True, get_rarity_color(player.secondary_weapon.rarity))
                screen.blit(w_name_2, (rect_sec.centerx - w_name_2.get_width()//2, rect_sec.centery + 5))
                if selected_mod_weapon == player.secondary_weapon: pygame.draw.rect(screen, YELLOW, rect_sec, 2, border_radius=8)
                elif rect_sec.collidepoint(m_pos): pygame.draw.rect(screen, WHITE, rect_sec, 1, border_radius=8)

                hi = draw_player_inv_grid(screen, p_start_x_m, p_start_y_m, m_x, m_y, allow_weapons=True)
                if hi: hovered_slot_info = hi
                for i in range(24):
                    item = player.inventory[i]
                    if item and item.type == "WEAPON" and selected_mod_weapon == item.weapon_obj:
                        pygame.draw.rect(screen, YELLOW, (p_start_x_m + (i%6)*58, p_start_y_m + (i//6)*58, 50, 50), 2, border_radius=6)

                detail_rect = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 - 180, 330, 410)
                pygame.draw.rect(screen, (25,28,35), detail_rect, border_radius=10)
                if selected_mod_weapon:
                    c = get_rarity_color(selected_mod_weapon.rarity)
                    screen.blit(large_font.render(selected_mod_weapon.full_name, True, c), (detail_rect.x + 20, detail_rect.y + 20))
                    screen.blit(font.render(f"傷害: {selected_mod_weapon.damage}", True, WHITE), (detail_rect.x + 20, detail_rect.y + 80))
                    aff_str = ",".join(selected_mod_weapon.affixes) if selected_mod_weapon.affixes else "無"
                    screen.blit(font.render(f"詞綴: {aff_str}", True, YELLOW), (detail_rect.x + 20, detail_rect.y + 120))
                    if selected_mod_weapon.rarity != "金":
                        cost = {"白":50, "藍":150, "紫":300}[selected_mod_weapon.rarity]
                        draw_hover_button(screen, upg_btn, f"升級品質 ({cost} 廢料)", GREEN if persistent_stats["scrap"]>=cost else GRAY, (50, 180, 50), BLACK)
                    if selected_mod_weapon.rarity != "白":
                        cost = {"藍":30, "紫":80, "金":150}[selected_mod_weapon.rarity]
                        draw_hover_button(screen, reroll_btn, f"重置詞綴 ({cost} 廢料)", BLUE if persistent_stats["scrap"]>=cost else GRAY, (50, 100, 180))
                draw_hover_button(screen, btn_mod_close, "X", (150, 50, 50), RED)

            elif game_state == "WEAPON_STASH":
                screen.blit(dim_surface, (0, 0))
                draw_ui_panel(screen, wep_stash_bg, "全自動武器箱 (ARSENAL)", RED)
                draw_hover_button(screen, btn_wep_close, "X", (180, 60, 60), RED, WHITE)
                
                p_c, s_c = get_rarity_color(player.primary_weapon.rarity), get_rarity_color(player.secondary_weapon.rarity)
                screen.blit(small_font.render("當前裝備 =>", True, WHITE), (WIDTH//2 - 340, HEIGHT//2 - 220))
                screen.blit(small_font.render(f"主: {player.primary_weapon.full_name}", True, p_c), (WIDTH//2 - 220, HEIGHT//2 - 220))
                screen.blit(small_font.render(f"副: {player.secondary_weapon.full_name}", True, s_c), (WIDTH//2 + 50, HEIGHT//2 - 220))

                list_rect = pygame.Rect(WIDTH//2 - 340, HEIGHT//2 - 180, 680, 260)
                pygame.draw.rect(screen, (15, 18, 22), list_rect, border_radius=6)
                pygame.draw.rect(screen, (50, 55, 65), list_rect, 1, border_radius=6)
                list_surf = pygame.Surface((list_rect.width, max(list_rect.height, (len(arsenal_weapons_list)+1)//2 * 50)))
                list_surf.fill((15, 18, 22))
                for i, wep in enumerate(arsenal_weapons_list):
                    col, row = i % 2, i // 2
                    box = pygame.Rect(col*335 + 10, row*50 + 5, 315, 42)
                    is_sel = (i == selected_arsenal_idx)
                    pygame.draw.rect(list_surf, (40, 45, 55), box, border_radius=6)
                    pygame.draw.rect(list_surf, YELLOW if is_sel else GRAY, box, 2 if is_sel else 1, border_radius=6)
                    c = get_rarity_color(wep.rarity)
                    name_surf = small_font.render(wep.full_name, True, c)
                    list_surf.blit(name_surf, (box.x + 10, box.y + 10))
                    aff_txt = ",".join(wep.affixes) if wep.affixes else "無"
                    stat_surf = tiny_font.render(f"傷:{wep.damage} [{aff_txt}]", True, WHITE)
                    list_surf.blit(stat_surf, (box.right - stat_surf.get_width() - 10, box.y + 14))
                    if box.collidepoint(m_x - list_rect.x, m_y - list_rect.y + arsenal_scroll_y) and list_rect.collidepoint(m_pos):
                        pygame.draw.rect(list_surf, WHITE, box, 1, border_radius=6)
                        hovered_slot_info = {"source": "ARSENAL", "idx": i, "item": create_item("WEAPON", 1, wep)}
                screen.blit(list_surf, list_rect.topleft, pygame.Rect(0, arsenal_scroll_y, list_rect.width, list_rect.height))
                
                screen.blit(small_font.render("右鍵:切換武器箱與背包 | 游標指著按 [X] 出售", True, GRAY), (WIDTH//2 - 344, HEIGHT//2 + 90))
                for i in range(24):
                    rect = pygame.Rect(p_start_x_w + (i%12)*58, p_start_y_w + (i//12)*58, 50, 50)
                    pygame.draw.rect(screen, (25, 28, 35), rect, border_radius=6); pygame.draw.rect(screen, (55, 60, 70), rect, 1, border_radius=6)
                    item = player.inventory[i]
                    if item:
                        if item.type == "WEAPON":
                            pygame.draw.circle(screen, get_rarity_color(item.weapon_obj.rarity), rect.center, 14)
                            if rect.collidepoint(m_x, m_y):
                                hovered_slot_info = {"source": "PLAYER", "idx": i, "item": item}; pygame.draw.rect(screen, WHITE, rect, 2, border_radius=6)
                        else: pygame.draw.circle(screen, (60,60,60), rect.center, 14)

                draw_hover_button(screen, btn_prim_w, "裝備為主武器", GREEN, (50, 180, 50), BLACK)
                draw_hover_button(screen, btn_sec_w, "裝備為副武器", BLUE, (50, 100, 180), WHITE)
                draw_hover_button(screen, btn_wep_close, "X", (150, 50, 50), RED)

            if drag_data:
                c = WHITE
                if drag_data["item"].type == "WEAPON": c = get_rarity_color(drag_data["item"].weapon_obj.rarity)
                elif drag_data["item"].type == "MED": c = HP_COLOR
                elif drag_data["item"].type == "SCRAP": c = SCRAP_COLOR
                elif drag_data["item"].type == "KEY": c = YELLOW
                pygame.draw.circle(screen, c, (m_x, m_y), 15)
                
            if hovered_slot_info and not drag_data:
                draw_item_tooltip(screen, hovered_slot_info["item"], m_x, m_y)
                val = get_sell_value(hovered_slot_info["item"])
                if val > 0: screen.blit(small_font.render(f"[X] 出售可得 {val} 廢料", True, SCRAP_COLOR), (m_x+25, m_y-25))

        elif game_state in ["PLAYING", "PAUSED", "LEVEL_UP", "DIED"]:
            if 'boss_active' in globals() and boss_active: draw_boss_direction_arrow(screen, boss, camera_x, camera_y)
            draw_lost_item_arrow(screen)

            if game_state == "PLAYING" and not show_inventory:
                for c in chests:
                    if c.state == "CLOSED" and math.hypot(player.x - c.x, player.y - c.y) < 70:
                        has_key = any(item.type == "KEY" for item in player.inventory if item)
                        t = "[F] 開啟木箱" if c.type == "NORMAL" else ("[F] 消耗金鑰匙" if has_key else "需要金鑰匙")
                        t_c = WHITE if c.type == "NORMAL" or has_key else RED
                        sx, sy, depth = project_3d(c.x, c.y)
                        bg_r = pygame.Rect(sx - 40, sy - 50, font.size(t)[0]+20, 25)
                        popup = pygame.Surface((bg_r.width, bg_r.height), pygame.SRCALPHA)
                        pygame.draw.rect(popup, (20, 20, 25, 200), popup.get_rect(), border_radius=4)
                        screen.blit(popup, (bg_r.x, bg_r.y))
                        screen.blit(small_font.render(t, True, t_c), (bg_r.x+10, bg_r.y+3))
                        
                for g in items:
                    if g.item_type not in ["EXP", "MAGNET", "BOMB", "SHIELD"] and math.hypot(player.x - g.x, player.y - g.y) < 70:
                        sx, sy, depth = project_3d(g.x, g.y)
                        bg_r = pygame.Rect(sx - 30, sy - 40, 60, 25)
                        popup = pygame.Surface((bg_r.width, bg_r.height), pygame.SRCALPHA)
                        pygame.draw.rect(popup, (20, 20, 25, 200), popup.get_rect(), border_radius=4)
                        screen.blit(popup, (bg_r.x, bg_r.y))
                        screen.blit(small_font.render("[F] 撿取", True, WHITE), (bg_r.x+5, bg_r.y+3))
            
            draw_minimap(screen)
            
            # HUD 資訊
            pygame.draw.rect(screen, GRAY, (20, 20, 250, 15)); pygame.draw.rect(screen, BLUE, (20, 20, 250 * (player.exp / player.max_exp), 15))
            screen.blit(font.render("等級: " + str(player.level), True, WHITE), (280, 15))
            pygame.draw.rect(screen, GRAY, (20, 45, 200, 15)); pygame.draw.rect(screen, GREEN if player.hp > 30 else RED, (20, 45, 200 * (max(0, player.hp) / player.max_hp), 15))
            screen.blit(font.render("血量", True, WHITE), (230, 40))
            pygame.draw.rect(screen, GRAY, (20, 70, 200, 15)); pygame.draw.rect(screen, (0, 150, 255), (20, 70, 200 * (max(0, player.shield) / player.max_shield), 15))
            screen.blit(font.render("護盾", True, WHITE), (230, 65))
            pygame.draw.rect(screen, GRAY, (20, 95, 150, 10)); pygame.draw.rect(screen, ORANGE, (20, 95, 150 * (player.stamina / player.max_stamina), 10))
            screen.blit(font.render("體力 (SPACE)", True, WHITE), (180, 87)) 
            pygame.draw.rect(screen, GRAY, (20, 115, 150, 10)); pygame.draw.rect(screen, CYAN, (20, 115, 150 * (player.energy / player.max_energy), 10))
            screen.blit(font.render("能量", True, WHITE), (180, 107))

            if player.cheat_all_weapons:
                active_wep = player.weapons[player.current_weapon_idx]
                weapon_str = f"【密技】全解鎖: {active_wep.full_name} (按E切換)"
                w_c = YELLOW
            else:
                w1, w2, active_w = player.weapons[0], player.weapons[1], player.current_weapon_idx
                w1_t = f"主: {w1.full_name}" + (" <" if active_w==0 else "")
                w2_t = f"副: {w2.full_name}" + (" <" if active_w==1 else "")
                weapon_str, w_c = f"{w1_t}  |  {w2_t}", WHITE
                
            screen.blit(small_font.render(weapon_str, True, w_c), (20, 140))
            has_key = sum(i.count for i in player.inventory if i and i.type == "KEY")
            screen.blit(font.render(f"本局廢料: {player.scrap} | 金鑰匙: {has_key}", True, YELLOW), (20, 165))

            if player.skill_cd > 0: skill_txt = font.render(f"技能: {round(player.skill_cd / 60, 1)} 秒", True, GRAY)
            elif player.energy < player.skill_cost: skill_txt = font.render("技能: 能量不足", True, RED)
            else: skill_txt = font.render("技能就緒 (右鍵)", True, GREEN)
            screen.blit(skill_txt, (20, HEIGHT - 40))

            if game_mode == "CHALLENGE":
                screen.blit(font.render(f"彈藥: {player.ammo}/{player.base_max_ammo + player.mag_size_bonus}", True, WHITE if player.ammo > 0 else RED), (20, 195))
                if player.reload_timer > 0:
                    pygame.draw.rect(screen, GRAY, (20, 225, 150, 10)); pygame.draw.rect(screen, YELLOW, (20, 225, 150 * (1 - player.reload_timer / player.reload_duration), 10))
                    screen.blit(small_font.render("換彈中...", True, YELLOW), (180, 220))

            if extraction_pt:
                time_sec = extraction_timer // FPS
                mins, secs = time_sec // 60, time_sec % 60
                color = WHITE if time_sec > 30 else RED
                screen.blit(large_font.render(f"撤離倒數: {mins:02d}:{secs:02d}", True, color), (WIDTH//2 - 120, 20))
                if extract_progress > 0:
                    pygame.draw.rect(screen, GRAY, (WIDTH//2 - 100, 110, 200, 15)); pygame.draw.rect(screen, GREEN, (WIDTH//2 - 100, 110, 200 * (extract_progress / 120), 15))
                if boss_army_active: screen.blit(large_font.render("!!!大軍來襲!!!", True, RED), (WIDTH//2 - 220, 140))

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
                draw_ui_panel(screen, inv_rect, "背包 (INVENTORY)", YELLOW)
                hi = draw_player_inv_grid(screen, WIDTH//2 - 170, HEIGHT//2 - 40, m_x, m_y, allow_weapons=True)
                if drag_data:
                    c = WHITE
                    if drag_data["item"].type == "WEAPON": c = get_rarity_color(drag_data["item"].weapon_obj.rarity)
                    elif drag_data["item"].type == "MED": c = HP_COLOR
                    elif drag_data["item"].type == "SCRAP": c = SCRAP_COLOR
                    elif drag_data["item"].type == "KEY": c = YELLOW
                    pygame.draw.circle(screen, c, (m_x, m_y), 15)
                elif hi:
                    draw_item_tooltip(screen, hi["item"], m_x, m_y)
                    hovered_slot_info = hi
                
                val = get_sell_value(hovered_slot_info["item"]) if hovered_slot_info else 0
                screen.blit(small_font.render(f"左鍵拖曳 / 右鍵裝備使用 / 拖出丟棄" + (f" | [X] 出售得 {val} 廢料" if val>0 else ""), True, GRAY), (WIDTH//2 - 210, HEIGHT//2 + 215))

    if game_state == "MENU":
        screen.fill(BLACK)
        for i in range(100):
            x, y = (i * 37) % WIDTH, (i * 23) % HEIGHT
            brightness = 100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)
        

        glow_color = (0, 100, 255, 50)
        glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        title = large_font.render("末日肉鴿生存", True, BLUE)
        glow_surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -3), (0, 3), (-3, 0), (3, 0)]:
            glow_copy = glow_surface.copy(); glow_copy.fill(glow_color, special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(glow_copy, offset)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        screen.blit(font.render("末日肉鴿RPG", True, WHITE), (WIDTH//2 - 60, HEIGHT//2 - 50))

        draw_hover_button(screen, start_button, "開始遊戲", (50, 150, 50), (100, 200, 100))
        draw_hover_button(screen, changelog_button, "更新日誌", (50, 100, 150), BLUE)
        draw_hover_button(screen, exit_button, "退出遊戲", (150, 50, 50), RED)

        controls = ["移動: WASD", "射擊: 左鍵  |  技能: 右鍵  |  衝刺: Q", "互動: E  |  替換武器/開箱/拾取: F", "切換武器: E  |  背包: TAB  |  補血: H"]
        for i, c in enumerate(controls): screen.blit(small_font.render(c, True, GRAY), (WIDTH//2 - font.size(c)[0]//2, HEIGHT//2 + 235 + i * 20))
        if show_changelog: draw_changelog_popup(screen)
    # 選擇難易度的畫面
    elif game_state == "DIFFICULTY":
        screen.fill(BLACK)
        screen.blit(large_font.render("選擇難易度", True, YELLOW), (WIDTH//2 - 100, HEIGHT//2 - 200))
        n_hover, c_hover = normal_button.collidepoint(m_pos), challenge_button.collidepoint(m_pos)
        pygame.draw.rect(screen, (55, 125, 185) if n_hover else (30, 70, 115), normal_button, border_radius=10)
        pygame.draw.rect(screen, YELLOW if n_hover else WHITE, normal_button, 4 if n_hover else 3, border_radius=10)
        pygame.draw.rect(screen, (190, 55, 70) if c_hover else (115, 35, 50), challenge_button, border_radius=10)
        pygame.draw.rect(screen, YELLOW if c_hover else WHITE, challenge_button, 4 if c_hover else 3, border_radius=10)

        #普通難度說明，我覺得這樣的排版還不錯，左邊是簡短的標語，右邊是詳細的說明，然後下面再用三行重點來強調特色，挑戰難度也是同樣的結構
        screen.blit(large_font.render("普通", True, WHITE), (normal_button.centerx - 40, normal_button.y + 28)) #數值代表距離按鈕中心的偏移，這樣無論按鈕大小怎麼調整，標題都能保持在適當的位置
        screen.blit(small_font.render("標準敵人強度與數量", True, WHITE), (normal_button.centerx - 80, normal_button.y + 88))
        for i, line in enumerate(["基礎倍率：1.0x", "無需換彈", "輕鬆農怪"]): screen.blit(small_font.render(line, True, (210, 225, 240)), (normal_button.x + 35, normal_button.y + 132 + i * 28))
        #挑戰難度說明
        screen.blit(large_font.render("挑戰", True, WHITE), (challenge_button.centerx - 40, challenge_button.y + 28))
        screen.blit(small_font.render("敵人 1.75 倍，速度加成", True, WHITE), (challenge_button.centerx - 90, challenge_button.y + 88))
        for i, line in enumerate(["難度倍率：1.75x", "啟動換彈懲罰機制", "解鎖專屬彈匣卡牌"]): screen.blit(small_font.render(line, True, (255, 220, 220)), (challenge_button.x + 35, challenge_button.y + 132 + i * 28))

        draw_hover_button(screen, difficulty_back_button, "返回", (50, 100, 150), BLUE)
    # 暫停畫面的四個選項：繼續遊戲、回到選單、放棄重製（回地堡）和退出遊戲。這些選項提供了玩家在暫停時的不同選擇，讓他們可以根據當前情況做出最適合的決定。
    elif game_state == "PAUSED":
        screen.blit(dim_surface, (0, 0))
        screen.blit(large_font.render("暫停中", True, YELLOW), (WIDTH//2 - 60, HEIGHT//2 - 100))
        draw_hover_button(screen, pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 10, 220, 50), "繼續遊戲", (50, 100, 150), BLUE)
        draw_hover_button(screen, pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 10, 220, 50), "回到選單", (50, 100, 150), BLUE)
        draw_hover_button(screen, pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 80, 220, 50), "放棄重製(回地堡)", (50, 150, 50), GREEN)
        draw_hover_button(screen, pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 80, 220, 50), "退出遊戲", (150, 50, 50), RED)
        draw_pause_upgrade_log(screen)
        # 暫停畫面也會顯示升級紀錄，讓玩家回顧剛剛的選擇和獲得的強化，這樣即使在緊張的戰鬥中途暫停，也能清楚記得自己目前的狀態和優勢，為接下來的挑戰做好心理準備。
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
        draw_hover_button(screen, confirm_upgrade_button, "確認選擇", GREEN if ready else GRAY, (50, 180, 50) if ready else GRAY)
    # 玩家陣亡後的畫面會顯示玩家已經陣亡的訊息，以及所有卡牌、物資與裝備已遺落在戰場的提示。玩家可以按下 [R] 鍵在地堡重生接著重返戰場。
    elif game_state == "DIED":
        screen.blit(dim_surface, (0, 0))
        screen.blit(large_font.render("你 已 陣 亡", True, RED), (WIDTH//2 - 100, HEIGHT//2 - 100))
        screen.blit(font.render("所有卡牌、物資與裝備已遺落在戰場。", True, WHITE), (WIDTH//2 - 200, HEIGHT//2 - 20))
        screen.blit(font.render("按 [R] 在地堡重生，重返戰場奪回一切！", True, YELLOW), (WIDTH//2 - 220, HEIGHT//2 + 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
