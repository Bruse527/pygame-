<<<<<<< HEAD
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
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("末日肉鴿生存?")
clock = pygame.time.Clock()
FPS = 60

# World狀態
camera_x, camera_y = 0, 0
screen_shake = 0  

# 顏色定義
BLACK, BLUE, RED, YELLOW = (10, 10, 15), (0, 200, 255), (255, 20, 80), (255, 255, 0)
PURPLE, DARK_PURPLE, WHITE = (200, 50, 255), (138, 43, 226), (255, 255, 255)
GRAY, GREEN, ORANGE, CYAN = (100, 100, 110), (0, 255, 100), (255, 150, 0), (0, 255, 255)
SCRAP_COLOR = (200, 200, 200)

# 卡牌顏色與類型定義
CARD_COLOR = (30, 30, 40)
CARD_TYPE_COLORS = {"attack": (120, 35, 45), "support": (35, 75, 130), "life": (35, 110, 65)}
CARD_TYPE_LABELS = {"attack": "攻擊", "support": "支援", "life": "生命"}
SHIELD_COLOR, EXP_COLOR, HP_COLOR = (0, 150, 255), (124, 252, 0), (255, 50, 50)

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

# 圖片載入函式，從指定路徑載入圖片並且根據提供的大小進行縮放，如果檔案不存在或載入失敗則將該圖片設為 None，以便後續使用時進行檢查
def load_image(name, filename, size=None):
    try:
        path = os.path.join(IMAGE_DIR, filename)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            if size: img = pygame.transform.scale(img, size)
            images[name] = img
        else: images[name] = None
    except: images[name] = None

# 動畫載入函式，從指定資料夾載入一系列圖片作為動畫幀，並且根據提供的大小進行縮放，如果資料夾不存在或沒有有效圖片則將該動畫設為 None
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

# 載入子彈 (自訂的長寬比例)
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

# 音效和音樂系統，從 audio 資料夾讀取
def load_sound(name, filename):
    try:
        sound_path = os.path.join(AUDIO_DIR, filename) # 修改為 AUDIO_DIR
        if os.path.exists(sound_path):
            sounds[name] = pygame.mixer.Sound(sound_path)
            sounds[name].set_volume(0.3)
        else:
            sounds[name] = None
    except:
        sounds[name] = None 

# 載入基礎音效
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

# 載入專屬武器音效 (有專屬檔就讀，沒有就用基礎音效代替)
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

# 載入並播放背景音樂
bgm_path = os.path.join(AUDIO_DIR, "bgm.mp3")
if os.path.exists(bgm_path):
    pygame.mixer.music.load(bgm_path)
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(loops=-1)

# 音效控制函式
def play_sound(name, loop=0):
    if sounds.get(name): sounds[name].play(loops=loop)

def stop_sound(name):
    if sounds.get(name): sounds[name].stop()

################################################################################


# 繪製UI面板，包含標題、背景、邊框和分隔線，並且使用半透明效果讓底下的遊戲畫面隱約可見
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
# 繪製懸浮按鈕，根據滑鼠位置改變顏色和邊框，並且回傳是否正在懸浮
def draw_hover_button(surface, rect, text, base_color, hover_color, text_color=WHITE):
    m_pos = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(m_pos)
    color = hover_color if is_hover else base_color
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, WHITE if is_hover else GRAY, rect, 2, border_radius=8)
    t_surf = font.render(text, True, text_color)
    surface.blit(t_surf, (rect.centerx - t_surf.get_width()//2, rect.centery - t_surf.get_height()//2))
    return is_hover
# 繪製物品提示框，根據物品類型顯示不同的資訊和樣式，並且自動調整位置避免超出螢幕邊界
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
# 繪製終端機面板，包含閃爍的邊框和動態變化的顏色，並且在面板上顯示圖示和文字
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
# 繪製迷你地圖，顯示玩家、Boss、撤離點和遺失物的位置，並且根據距離和狀態改變顏色和大小
def draw_minimap(surface):
    map_w, map_h = 160, 120
    m_rect = pygame.Rect(WIDTH - map_w - 20, 20, map_w, map_h)
    
    mm_surf = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
    pygame.draw.rect(mm_surf, (10, 10, 20, 180), mm_surf.get_rect(), border_radius=5)
    pygame.draw.rect(mm_surf, (50, 200, 50), mm_surf.get_rect(), 2, border_radius=5)
    surface.blit(mm_surf, (m_rect.x, m_rect.y))
    # 將遊戲內座標轉換為迷你地圖座標的函式
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
# 畫出Boss方向箭頭（當Boss在視野外時）
def draw_boss_direction_arrow(surface, boss_obj, cam_x, cam_y):
    if not boss_obj or (hasattr(boss_obj, "state") and boss_obj.state == "DEFEAT"): return
    boss_screen_x, boss_screen_y = boss_obj.x - cam_x, boss_obj.y - cam_y
    if 0 <= boss_screen_x <= WIDTH and 0 <= boss_screen_y <= HEIGHT: return

    center = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
    direction = pygame.math.Vector2(boss_screen_x - center.x, boss_screen_y - center.y)
    if direction.length_squared() == 0: return
    direction.normalize_ip()
    margin = 56
    scale_x = (WIDTH / 2 - margin) / abs(direction.x) if abs(direction.x) > 0.001 else float("inf")
    scale_y = (HEIGHT / 2 - margin) / abs(direction.y) if abs(direction.y) > 0.001 else float("inf")
    arrow_pos = center + direction * min(scale_x, scale_y)
    side = direction.rotate(90)
    tip = arrow_pos + direction * 25
    left = arrow_pos - direction * 18 + side * 15
    right = arrow_pos - direction * 18 - side * 15
    arrow_points = [(int(tip.x), int(tip.y)), (int(left.x), int(left.y)), (int(right.x), int(right.y))]
    pygame.draw.polygon(surface, BLACK, arrow_points); pygame.draw.polygon(surface, YELLOW, arrow_points, 0); pygame.draw.polygon(surface, RED, arrow_points, 3)
# 畫出遺失物方向箭頭（當遺失物在視野外且存在時）
def draw_lost_item_arrow(surface, cx, cy):
    if not ('lost_item' in globals() and lost_item): return
    dx, dy = lost_item.x - player.x, lost_item.y - player.y
    if math.sqrt(dx**2 + dy**2) > min(WIDTH, HEIGHT) * 0.4:
        angle = math.atan2(dy, dx)
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

# UI 介面全域變數與按鈕大小優化 (置中對齊與自適應)
shop_bg = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 300)
stash_bg = pygame.Rect(WIDTH//2 - 380, HEIGHT//2 - 250, 760, 500)
mod_bg = pygame.Rect(WIDTH//2 - 380, HEIGHT//2 - 250, 760, 500)
wep_stash_bg = pygame.Rect(WIDTH//2 - 380, HEIGHT//2 - 280, 760, 560)

s_start_x, s_start_y = WIDTH//2 - 350, HEIGHT//2 - 150
p_start_x_s, p_start_y_s = WIDTH//2 + 30, HEIGHT//2 - 150
p_start_x_m, p_start_y_m = WIDTH//2 - 320, HEIGHT//2 + 20
p_start_x_w, p_start_y_w = WIDTH//2 - 320, HEIGHT//2 + 100

rect_prim = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 150, 180, 60)
rect_sec = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 - 150, 180, 60)
upg_btn = pygame.Rect(WIDTH//2 + 100, HEIGHT//2 - 130, 200, 40)
reroll_btn = pygame.Rect(WIDTH//2 + 100, HEIGHT//2 - 70, 200, 40)

btn_prim_w = pygame.Rect(WIDTH//2 - 160, HEIGHT//2 + 220, 140, 40)
btn_sec_w = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 220, 140, 40)

cards = [pygame.Rect(WIDTH//2 - 350 + i*240, HEIGHT//2 - 150, 220, 320) for i in range(3)]
# 玩家背包格子位置
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
# 儲存格放置物品的函式，根據來源和目標更新玩家背包或一般儲藏室的物品，並且處理堆疊邏輯以確保相同類型的物品可以合併
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
# 開啟寶箱的函式，根據寶箱類型生成不同數量和種類的物品，並且在特定條件下添加特殊物品，最後播放獲得物品的音效
def open_chest(c):
    num_items = random.randint(2, 4) if c.type == "NORMAL" else random.randint(4, 7)
    for _ in range(num_items):
        rand_val = random.random()
        if rand_val < 0.2:
            items.append(DropItem(c.x + random.randint(-30, 30), c.y + random.randint(-30, 30), "MED"))
        elif rand_val < 0.5:
            items.append(DropItem(c.x + random.randint(-30, 30), c.y + random.randint(-30, 30), "SCRAP", random.randint(2, 5)))
        elif rand_val < 0.7:
            wep = generate_weapon(random.choice(list(WEAPON_TYPES.keys())), random.choices(["白", "藍", "紫", "金"], weights=[0.6, 0.3, 0.08, 0.02])[0])
            items.append(DropItem(c.x + random.randint(-30, 30), c.y + random.randint(-30, 30), "WEAPON", weapon_obj=wep))
        else:
            items.append(DropItem(c.x + random.randint(-30, 30), c.y + random.randint(-30, 30), "EXP", random.randint(1, 3)))
    if c.type == "LOCKED":
        items.append(DropItem(c.x, c.y + 20, "MAGNET"))
        items.append(DropItem(c.x, c.y - 20, "BOMB"))
    play_sound("exp")
# 更新日誌快取重建函式，當遊戲更新或修復後需要重新生成更新日誌的內容以供顯示
def rebuild_changelog_cache(w, h): pass 
# 繪製更新日誌彈窗，顯示修復和優化的內容，並且使用半透明面板和分行文字來呈現資訊
def draw_changelog_popup(surface):
    rect = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 200, 500, 400)
    draw_ui_panel(surface, rect, "更新與修復日誌", BLUE)
    logs = [
        "修復項目與優化內容:",
        "- 徹底修復：傷害數字與特效凍結在畫面的問題。",
        "- 徹底修復：敵人生成後不移動、不追蹤的問題。",
        "- 徹底修復：Boss 行為凍結的問題。",
        "- 修復缺圖片時槍枝消失，新增幾何備用繪製。",
        "- 小地圖改為戰術雷達風格，畫面更乾淨。",
        "- 成功撤離會完美保留所有狀態。",
    ]
    for i, line in enumerate(logs):
        surface.blit(small_font.render(line, True, WHITE), (rect.x + 20, rect.y + 60 + i * 30))
# 繪製暫停時的升級日誌，顯示玩家已獲得的強化內容，並且使用半透明面板和分行文字來呈現資訊
def draw_pause_upgrade_log(surface):
    draw_upgrade_summary(surface, WIDTH//2 - 120, HEIGHT//2 + 150, max_items=8, title="已獲得的強化")


# 升級選項定義，標題、描述、類型和權重等資訊，其中部分選項僅在特定遊戲模式下可用
# UI 升級卡牌完整資料 (共 25 種)
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
# 選擇升級卡牌的函式，根據權重隨機選擇三張可用的升級選項，並且將它們的索引存儲在全域變數中以供後續使用
def choose_upgrade_cards():
    global current_upgrade_choices, selected_upgrade_position
    available_indices = []
    weights = []
    for i, opt in enumerate(upgrade_options):
        if opt.get("challenge_only", False) and game_mode != "CHALLENGE":
            continue
        available_indices.append(i)
        weights.append(opt.get("weight", 1))
        
    chosen_indices = []
    while len(chosen_indices) < 3 and available_indices:
        idx = random.choices(available_indices, weights=weights, k=1)[0]
        chosen_indices.append(idx)
        remove_idx = available_indices.index(idx)
        available_indices.pop(remove_idx)
        weights.pop(remove_idx)
        
    current_upgrade_choices = chosen_indices
    selected_upgrade_position = None
# 應用升級效果的函式，根據選擇的升級選項更新玩家的屬性，並且將已選擇的升級記錄在全域變數中以供顯示
def apply_upgrade(idx, silent=False):
    global game_state, chosen_upgrades
    opt = upgrade_options[idx]
    found = False
    for u in chosen_upgrades:
        if u["title"] == opt["title"]:
            u["count"] += 1
            found = True
            break
    if not found:
        chosen_upgrades.append({"title": opt["title"], "count": 1})
    # 根據升級標題應用對應的效果，這裡使用一系列的條件判斷來更新玩家的屬性值
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
    
    if not silent:
        game_state = "PLAYING"
        play_sound("levelup")

# 全域變數定義，包含玩家的持久化屬性、作弊碼序列和按鍵緩衝區等資訊，以便在遊戲中使用和更新
persistent_stats = {"max_hp": 0, "dmg_bonus": 0, "speed_bonus": 0.0, "scrap": 0, "weapon_stash": [], "general_stash": [None]*36}
CHEAT_CODE = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_b, pygame.K_a, pygame.K_b, pygame.K_a]
key_buffer = []
# 武器類別定義，包含名稱、射擊延遲、子彈類型、傷害、音效名稱和後坐力等屬性，並且根據名稱載入對應的圖片資源
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
# 根據稀有度返回對應的顏色，金色、紫色、藍色和白色分別對應不同的RGB值，默認為灰色
def get_rarity_color(r):
    return {"金": (255, 215, 0), "紫": (200, 50, 255), "藍": (50, 150, 255)}.get(r, (200, 200, 200))
# 根據武器的基礎屬性、稀有度和詞綴來計算最終的傷害和射擊延遲，速射詞綴會大幅降低射擊延遲，而稀有度會增加傷害
def apply_weapon_stats(w):
    base = WEAPON_TYPES[w.base_name]
    w.damage = int(base.damage * {"白":1.0, "藍":1.3, "紫":1.6, "金":2.2}.get(w.rarity, 1.0))
    w.shoot_delay = max(2, int(base.shoot_delay * 0.60)) if "速射" in w.affixes else base.shoot_delay
# 根據武器的基礎類型和稀有度來生成一把新的武器，並且從動態詞綴池中隨機選擇一些詞綴來增加武器的特性，最後應用這些屬性來計算最終的傷害和射擊延遲
def generate_weapon(base_name, rarity="白"):
    base = WEAPON_TYPES[base_name]
    w = Weapon(base.base_name, base.shoot_delay, base.bullet_type, base.damage, base.sound_name, base.base_recoil)
    w.rarity = rarity
    c = {"白":0, "藍":1, "紫":2, "金":3}.get(rarity, 0)
    
    # 動態詞綴池：避開武器本身已有的特性，確保詞綴能「疊加」而不是浪費
    pool = ["速射", "散射", "吸血", "爆擊"]
    if base.bullet_type not in ["piercing", "laser", "cannon", "flamethrower"]:
        pool.append("穿透") # 本身不會穿透的武器才給穿透
    if base.bullet_type not in ["flamethrower", "flame_grenade"]:
        pool.append("燃燒") # 本身沒有火焰效果的才給燃燒
        
    w.affixes = random.sample(pool, min(c, len(pool))) if c > 0 else []
    apply_weapon_stats(w)
    return w
# 將武器儲藏室中的武器按照基礎類型、稀有度、詞綴數量和詞綴內容進行排序，確保同類型的武器會被歸類在一起，並且更稀有和更強力的武器會排在前面
def sort_weapon_stash():
    rv = {"白":0, "藍":1, "紫":2, "金":3}; order = list(WEAPON_TYPES.keys())
    persistent_stats["weapon_stash"].sort(key=lambda w: (order.index(w.base_name) if w.base_name in order else 99, -rv.get(w.rarity, 0), -len(w.affixes), "".join(sorted(w.affixes))))
# 根據物品的類型和屬性來計算它的出售價值，武器的價值取決於稀有度，醫療包和金鑰匙的價值取決於數量，其他物品則沒有價值
def get_sell_value(item):
    if not item: return 0
    if item.type == "WEAPON": return {"白":20, "藍":50, "紫":120, "金":300}.get(item.weapon_obj.rarity, 10)
    elif item.type == "MED": return 5 * item.count
    elif item.type == "KEY": return 30 * item.count
    return 0
# 物品類別定義，包含類型、名稱、數量、最大堆疊數量和武器對象等屬性，武器物品會包含一個對應的武器對象以供使用
class InvItem:
    def __init__(self, i_type, name, count, max_stack, weapon_obj=None):
        self.type, self.name, self.count, self.max_stack, self.weapon_obj = i_type, name, count, max_stack, weapon_obj
# 根據物品的類型和屬性來創建一個新的物品實例，廢料、急救包和金鑰匙有固定的名稱和最大堆疊數量，而武器則根據武器對象來設定名稱和屬性
def create_item(i_type, amount=1, weapon_obj=None):
    if i_type == "SCRAP": return InvItem("SCRAP", "廢料", amount, 999)
    elif i_type == "MED": return InvItem("MED", "急救包", amount, 5)
    elif i_type == "KEY": return InvItem("KEY", "金鑰匙", amount, 10)
    elif i_type == "WEAPON": return InvItem("WEAPON", weapon_obj.full_name, 1, 1, weapon_obj)
# 快速轉移物品的函式，嘗試將一個物品堆疊到目標列表中相同類型的物品上，如果無法完全堆疊則放到第一個空格中，返回是否成功轉移
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

# 粒子特效類別，包含位置、速度、計時器、大小和顏色等屬性，更新時會根據速度移動位置並減小大小，繪製時會根據剩餘時間和大小來呈現不同的效果
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vel_x, self.vel_y = random.uniform(-6, 6), random.uniform(-6, 6)
        self.timer, self.size, self.color = random.randint(15, 30), random.randint(4, 8), color

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.timer -= 1
        self.size = max(0, self.size - 0.25)

    def draw(self, surface):
        if self.size > 0: 
            pygame.draw.rect(surface, self.color, (int(self.x - camera_x), int(self.y - camera_y), int(self.size), int(self.size)))

# 傷害數字類別，包含位置、傷害值、顏色、是否暴擊等屬性，更新時會向上移動並逐漸變淡，繪製時會根據傷害值和暴擊狀態來呈現不同的文字效果
class DamageText:
    def __init__(self, x, y, damage, color, is_crit=False):
        self.x, self.y = x, y
        self.damage = damage
        self.color = color
        self.is_crit = is_crit
        self.timer, self.vel_y, self.alpha = 40, -1.5, 255
        self.offset_x = random.randint(-15, 15)
        self.font = large_font if is_crit else small_font

    def update(self):
        self.y += self.vel_y
        self.timer -= 1
        self.alpha = max(0, int((self.timer / 40) * 255))

    def draw(self, surface):
        if self.timer > 0:
            text = f"-{int(self.damage)}" + ("!" if self.is_crit else "")
            txt_surf = self.font.render(text, True, self.color)
            txt_surf.set_alpha(self.alpha)
            surface.blit(txt_surf, (int(self.x + self.offset_x - camera_x - txt_surf.get_width()//2), int(self.y - camera_y)))

# 衝刺殘影類別，包含位置、大小和生命值等屬性，更新時會減少生命值，繪製時會根據剩餘生命值來呈現不同的透明度效果
class DashTrail:
    def __init__(self, x, y, size):
        self.x, self.y = x, y
        self.size = size
        self.life = 15
        
    def update(self):
        self.life -= 1
        
    def draw(self, surface):
        alpha = max(0, int((self.life / 15) * 150))
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 200, 255, alpha), (0, 0, self.size, self.size), border_radius=5)
        surface.blit(surf, (int(self.x - camera_x - self.size/2), int(self.y - camera_y - self.size/2)))

# 掉落物品類別，包含位置、類型、數量和武器對象等屬性，更新時會根據玩家位置和磁吸範圍來移動位置，繪製時會根據類型來呈現不同的圖像或幾何圖形
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
        if self.count > 1 and self.item_type in ["SCRAP", "MED", "KEY"]:
            surface.blit(tiny_font.render(str(self.count), True, WHITE), (draw_x + 5, int(float_y) + 5))

# 寶箱類別，包含位置、類型、狀態和開啟進度等屬性，更新時會根據玩家位置和開啟狀態來增加開啟進度，繪製時會根據狀態來呈現不同的圖像或幾何圖形
class Chest:
    def __init__(self, x, y, c_type="NORMAL"):
        self.x, self.y, self.type, self.state, self.open_progress = x, y, c_type, "CLOSED", 0
        self.rect, self.color = pygame.Rect(0, 0, 50, 40), (139, 69, 19) if c_type == "NORMAL" else (218, 165, 32)
    def draw(self, surface):
        draw_x, draw_y = int(self.x - camera_x), int(self.y - camera_y)
        self.rect.center = (draw_x, draw_y)
        
        # 優先讀取圖片，找不到才畫幾何圖形
        img_key = f"chest_{self.type}_{self.state}"
        img = images.get(img_key)
        
        if img:
            surface.blit(img, img.get_rect(center=(draw_x, draw_y)))
            # 開啟進度條仍保留繪製在圖片上方
            if self.state == "CLOSED" and self.open_progress > 0:
                pygame.draw.rect(surface, GRAY, (draw_x-25, draw_y-30, 50, 6))
                pygame.draw.rect(surface, GREEN, (draw_x-25, draw_y-30, 50*(self.open_progress/40), 6))
        else:
            # 幾何圖形備用方案
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

# 玩家遺失物品類別，包含位置、玩家等級、經驗值、升級選項、背包物品和武器等屬性，更新時會根據玩家位置來移動位置，繪製時會呈現一個閃爍的圓形和提示文字，讓玩家知道可以觸碰拾取
class PlayerLostItem:
    def __init__(self, x, y, level, exp, upgrades, inv_items, w1, w2):
        self.x, self.y, self.level, self.exp, self.upgrades = x, y, level, exp, upgrades
        self.inventory, self.w1, self.w2 = inv_items, w1, w2
        self.rect = pygame.Rect(0, 0, 50, 50)
        self.rect.center = (int(self.x), int(self.y))
    def draw(self, surface):
        self.rect.center = (int(self.x), int(self.y))
        draw_x, draw_y = int(self.x - camera_x), int(self.y - camera_y)
        p = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 5)
        pygame.draw.circle(surface, YELLOW, (draw_x, draw_y), 20 + p)
        pygame.draw.circle(surface, WHITE, (draw_x, draw_y), 22 + p, 2)
        txt = small_font.render(f"遺失物(觸碰拾取)", True, YELLOW)
        surface.blit(txt, (draw_x - txt.get_width()//2, draw_y - 35))

# 撤離點類別，包含位置和半徑等屬性，更新時不需要做任何事情，繪製時會呈現一個閃爍的圓形和提示文字，讓玩家知道這是撤離點
class ExtractionPoint:
    def __init__(self): self.x, self.y, self.radius = random.randint(800, MAP_WIDTH - 800), random.randint(800, MAP_HEIGHT - 800), 150
    def draw(self, surface):
        draw_x, draw_y = int(self.x - camera_x), int(self.y - camera_y)
        p = int(abs(math.sin(pygame.time.get_ticks() * 0.003)) * 20)
        pygame.draw.circle(surface, GREEN, (draw_x, draw_y), self.radius + p, 3)
        txt = font.render("撤離點", True, GREEN); surface.blit(txt, (draw_x - txt.get_width()//2, draw_y - 20))

# 模擬目標類別，包含位置、矩形、傷害記錄和震動計時器等屬性，更新時會清理過期的傷害記錄並減少震動計時器，繪製時會根據位置和傷害狀態來呈現一個矩形和傷害數字，並且在受到攻擊時產生震動效果
class DummyTarget:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.rect = pygame.Rect(0, 0, 40, 60)
        self.rect.center = (int(self.x), int(self.y)) # [修復] 初始化為世界座標
        self.hit_log = []
        self.shake_timer = 0
        
    def update(self):
        now = pygame.time.get_ticks()
        self.hit_log = [(t, dmg) for t, dmg in self.hit_log if now - t <= 3000]
        if self.shake_timer > 0: self.shake_timer -= 1
        # 確保碰撞框永遠鎖定在正確的世界座標上
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface):
        # 繪圖專用的螢幕座標 (加上受傷震動偏移)
        dx = int(self.x - camera_x) + (random.randint(-2,2) if self.shake_timer>0 else 0)
        dy = int(self.y - camera_y) + (random.randint(-2,2) if self.shake_timer>0 else 0)
        # 優先使用動畫或圖片，找不到才畫幾何圖形
        anim_frames = animations.get("dummy")
        if anim_frames:
            img = anim_frames[int(pygame.time.get_ticks() / 150) % len(anim_frames)]
            if self.shake_timer > 0:
                img = img.copy()
                img.fill((255, 100, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(img, img.get_rect(center=(dx, dy)))
        else:
            # 備用的幾何圖形畫法
            draw_rect = self.rect.copy()
            draw_rect.center = (dx, dy)
            pygame.draw.rect(surface, (150, 100, 80), draw_rect, border_radius=10)
            pygame.draw.circle(surface, RED, (dx, dy - 10), 8)
            pygame.draw.circle(surface, WHITE, (dx, dy - 10), 4)
        # 顯示DPS，計算最近3秒內的總傷害並除以3來獲得每秒傷害，根據DPS值來決定顏色，並且將文字繪製在模擬目標上方        
        total_dmg = sum(dmg for t, dmg in self.hit_log)
        dps = int(total_dmg / 3.0) if self.hit_log else 0
        dps_txt = small_font.render(f"DPS: {dps}", True, CYAN if dps > 0 else GRAY)
        surface.blit(dps_txt, (dx - dps_txt.get_width()//2, dy - 50))
# 玩家類別，包含位置、大小、矩形、武器、屬性、經驗值、等級、背包和升級等屬性，更新時會根據鍵盤輸入來移動位置和使用技能，並且處理衝刺、回血、能量恢復和升級等邏輯，繪製時會根據狀態來呈現玩家的圖像和相關資訊
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
        self.current_spread, self.bullet_count, self.bullet_spread, self.extra_same_path_bullets = 15.0, 1, 15.0, 0
        self.bullet_damage_bonus, self.shoot_delay_reduction, self.damage_reduction = persistent_stats["dmg_bonus"], 0, 0
        self.invincible_duration, self.guidance_level, self.aura_level, self.regen_level, self.regen_progress = 60, 0, 0, 0, 0
        self.exp_multiplier, self.magnet_radius, self.drone_level, self.drone_angle, self.drone_shoot_cd = 1.0, 80, 0, 0, 0
        self.dash_cost, self.is_dashing, self.dash_speed, self.dash_duration, self.dash_timer, self.dash_dir_x, self.dash_dir_y = 30, False, 28, 8, 0, 0, 0
        self.skill_cd, self.skill_max_cd, self.skill_cost = 0, 600, 50        
        self.invincible_timer, self.god_mode = 0, False 
        self.base_max_ammo, self.mag_size_bonus, self.reload_duration, self.reload_timer = 40, 0, 90, 0
        self.ammo = self.base_max_ammo

    @property 
    #這個方法用來計算玩家背包中所有廢料的總數量，通過遍歷背包中的物品並累加類型為"SCRAP"的物品數量來實現，方便在遊戲中顯示和使用廢料資源
    def scrap(self):
        return sum(i.count for i in self.inventory if i and i.type == "SCRAP")

    def add_item(self, new_item): return fast_transfer(new_item, self.inventory)
    def use_med(self):
        for i in range(24):
            item = self.inventory[i]
            if item and item.type == "MED" and self.hp < self.max_hp:
                self.hp = min(self.max_hp, self.hp + 40); item.count -= 1
                if item.count <= 0: self.inventory[i] = None
                play_sound("exp"); return True
        return False
    #這個方法用來處理玩家的移動和技能使用邏輯，首先根據鍵盤輸入來計算移動方向，然後處理衝刺、回血、能量恢復和升級等邏輯，最後根據位置和狀態來更新玩家的矩形和子彈散布等屬性，確保玩家在遊戲中能夠流暢地移動和使用技能
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
        #衝刺邏輯：當玩家按下空格或Q鍵並且有足夠的耐力時，啟動衝刺狀態，消耗耐力並設定衝刺方向和持續時間，在衝刺期間玩家會以更高的速度移動，並且在結束後恢復正常狀態
        if not self.is_dashing:
            if self.stamina < self.max_stamina: self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen)
        if self.energy < self.max_energy: self.energy = min(self.max_energy, self.energy + self.energy_regen)

        if keys[pygame.K_SPACE] or keys[pygame.K_q]:
            if not self.is_dashing and self.stamina >= self.dash_cost:
                self.stamina -= self.dash_cost; self.is_dashing = True; self.dash_timer = self.dash_duration
                play_sound("dash")
                if dist > 0: self.dash_dir_x, self.dash_dir_y = move_x, move_y
                else:
                    mx, my = pygame.mouse.get_pos(); wx, wy = mx + camera_x, my + camera_y
                    dx, dy = wx - self.x, wy - self.y; ddist = math.sqrt(dx**2 + dy**2)
                    if ddist > 0: self.dash_dir_x, self.dash_dir_y = dx / ddist, dy / ddist
        #根據衝刺狀態來更新玩家的位置，如果正在衝刺則以更高的速度移動，並且減少衝刺計時器，當計時器結束後恢復正常狀態，如果沒有衝刺則根據移動方向和基礎速度來移動，最後根據位置和狀態來更新玩家的矩形和子彈散布等屬性，確保玩家在遊戲中能夠流暢地移動和使用技能
        if self.is_dashing:
            self.x += self.dash_dir_x * self.dash_speed; self.y += self.dash_dir_y * self.dash_speed
            self.dash_timer -= 1; 
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
        if self.current_spread > self.bullet_spread: self.current_spread = max(self.bullet_spread, self.current_spread - 0.5)
    #這個方法用來繪製玩家的圖像和相關資訊，首先根據無敵狀態來決定是否繪製玩家，然後根據武器動畫和鼠標位置來繪製玩家和武器的圖像，最後根據狀態來繪製衝刺殘影、護盾光環和無人機等特效，確保玩家在遊戲中能夠清晰地看到自己的角色和狀態
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
                mx, my = pygame.mouse.get_pos(); dx, dy = (mx + camera_x) - self.x, (my + camera_y) - self.y
                dist = math.sqrt(dx**2 + dy**2); dir_x, dir_y = (dx / dist, dy / dist) if dist > 0 else (1, 0)
                angle = math.degrees(math.atan2(-dy, dx))
                gun_img = images.get("gun_" + current_wep.base_name)
                
                if gun_img:
                    if dx < 0: gun_img = pygame.transform.flip(gun_img, False, True)
                    rotated_gun = pygame.transform.rotate(gun_img, angle)
                    offset_x, offset_y = dir_x * 15, dir_y * 15
                    surface.blit(rotated_gun, rotated_gun.get_rect(center=(int(self.x + offset_x - camera_x), int(self.y + offset_y - camera_y))))
                else:
                    end_x = self.x + dir_x * 25 - camera_x
                    end_y = self.y + dir_y * 25 - camera_y
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
            pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10)
            pygame.draw.circle(surface, (0, 180, 255), draw_rect.center, 95 + self.aura_level * 25 + pulse, 2)
            
        if self.drone_level > 0:
            drone_x, drone_y = draw_center[0] + math.cos(self.drone_angle) * 55, draw_center[1] + math.sin(self.drone_angle) * 55
            pygame.draw.circle(surface, (150, 200, 255), (int(drone_x), int(drone_y)), 10)
            pygame.draw.circle(surface, BLUE, (int(drone_x), int(drone_y)), 10, 2); pygame.draw.circle(surface, RED, (int(drone_x), int(drone_y)), 4)

#玩家發射的子彈，包含位置、方向、傷害、類型和特殊效果等屬性，更新時會根據導引等級來調整方向，並且根據類型來移動位置和處理爆炸等邏輯，繪製時會根據類型和暴擊狀態來呈現不同的圖像或幾何圖形，確保玩家在遊戲中能夠清晰地看到子彈的軌跡和效果
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

    #更新子彈的位置和狀態，首先根據導引等級來調整方向，然後根據類型來移動位置和處理爆炸等邏輯，最後更新矩形位置以便碰撞檢測，確保子彈在遊戲中能夠正確地移動和產生效果
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
    #繪製子彈的圖像，首先根據類型和暴擊狀態來決定使用哪個圖像或幾何圖形來繪製子彈，然後根據位置和攝像機偏移來計算繪製位置，最後將圖像或幾何圖形繪製到屏幕上，確保玩家在遊戲中能夠清晰地看到子彈的軌跡和效果
    def draw(self, surface):
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        img = images.get("bullet_" + self.b_type)
        if img: surface.blit(pygame.transform.rotate(img, math.degrees(math.atan2(-self.dir_y, self.dir_x))), img.get_rect(center=draw_center))
        else: pygame.draw.circle(surface, self.color, draw_center, self.radius)
        if self.is_crit: pygame.draw.circle(surface, RED, draw_center, self.radius+2, 1)
#敵人類別，包含位置、大小、生命值、攻擊方式和特殊效果等屬性，更新時會根據玩家位置來移動和攻擊，並且處理冰凍、燃燒和其他狀態效果的邏輯，繪製時會根據狀態來呈現不同的圖像或幾何圖形，確保玩家在遊戲中能夠清晰地看到敵人的位置和狀態
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
        
        # 飛彈壽命與爆炸標記 (追蹤彈壽命約 2.5 秒，一般子彈無限)
        self.lifespan = 150 if is_homing else 9999 
        self.explode = False

    def update(self, target_x=None, target_y=None):
        # [新增] 壽命衰減判定
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.explode = True
            return

        if self.is_homing and target_x is not None and target_y is not None:
            tx, ty = target_x - self.x, target_y - self.y
            dist = math.sqrt(tx**2 + ty**2)
            if dist > 0:
                # 飛彈越快沒燃料，追蹤轉向能力就越差，讓玩家更好閃避
                turn_speed = 0.045 * (self.lifespan / 150)
                self.dir_x = self.dir_x * (1 - turn_speed) + (tx / dist) * turn_speed
                self.dir_y = self.dir_y * (1 - turn_speed) + (ty / dist) * turn_speed
                ndist = math.sqrt(self.dir_x**2 + self.dir_y**2)
                if ndist > 0: self.dir_x /= ndist; self.dir_y /= ndist
                
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))
    #繪製敵人子彈的圖像，首先根據類型和追蹤狀態來決定使用哪個圖像或幾何圖形來繪製子彈，然後根據位置和攝像機偏移來計算繪製位置，最後將圖像或幾何圖形繪製到屏幕上，確保玩家在遊戲中能夠清晰地看到敵人子彈的軌跡和效果
    def draw(self, surface): 
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        pygame.draw.circle(surface, self.color, draw_center, self.radius)
#敵人類別，包含位置、大小、生命值、攻擊方式和特殊效果等屬性，更新時會根據玩家位置來移動和攻擊，並且處理冰凍、燃燒和其他狀態效果的邏輯，繪製時會根據狀態來呈現不同的圖像或幾何圖形，確保玩家在遊戲中能夠清晰地看到敵人的位置和狀態
class Enemy:
    def __init__(self, level, is_elite=False, spawn_x=MAP_WIDTH/2, spawn_y=MAP_HEIGHT/2):
        self.is_elite, self.size = is_elite, 35 if is_elite else 25
        difficulty_mult = 1.75 if game_mode == "CHALLENGE" else 1.0
        self.speed = ((random.uniform(3.0, 5.5) if is_elite else random.uniform(2.5, 4.5)) + level * 0.05) * (1.2 if game_mode == "CHALLENGE" else 1.0)
        self.max_hp = int(((60 + level * 25) if is_elite else (20 + level * 8)) * difficulty_mult)
        self.hp, self.max_shield = self.max_hp, int(((20 + level * 8) if is_elite else (10 + level * 4)) * difficulty_mult)
        self.shield, self.damage = self.max_shield, int(((35 + level * 3) if is_elite else (15 + level * 1.5)) * difficulty_mult)
        self.frost_timer, self.burn_timer, self.dir_x, self.dir_y = 0, 0, 1, 0  
        
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
        
        # 畫面邊緣包圍生成邏輯
        spawn_dist_x = WIDTH / 2 + 50
        spawn_dist_y = HEIGHT / 2 + 50
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top': 
            self.x = spawn_x + random.randint(-int(spawn_dist_x), int(spawn_dist_x))
            self.y = spawn_y - spawn_dist_y
        elif edge == 'bottom': 
            self.x = spawn_x + random.randint(-int(spawn_dist_x), int(spawn_dist_x))
            self.y = spawn_y + spawn_dist_y
        elif edge == 'left': 
            self.x = spawn_x - spawn_dist_x
            self.y = spawn_y + random.randint(-int(spawn_dist_y), int(spawn_dist_y))
        elif edge == 'right': 
            self.x = spawn_x + spawn_dist_x
            self.y = spawn_y + random.randint(-int(spawn_dist_y), int(spawn_dist_y))
            
        self.x = max(0, min(self.x, MAP_WIDTH))
        self.y = max(0, min(self.y, MAP_HEIGHT))
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = (int(self.x), int(self.y))
    #更新敵人的位置和狀態，首先根據玩家位置來計算移動方向，然後根據攻擊方式來決定移動和攻擊的行為，最後處理冰凍、燃燒和其他狀態效果的邏輯，確保敵人在遊戲中能夠正確地追蹤玩家並產生攻擊行為
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
    #繪製敵人的圖像，首先根據狀態來決定使用哪個圖像或幾何圖形來繪製敵人，然後根據位置和攝像機偏移來計算繪製位置，最後將圖像或幾何圖形繪製到屏幕上，確保玩家在遊戲中能夠清晰地看到敵人的位置和狀態
    def draw(self, surface):
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        draw_rect = self.rect.copy(); draw_rect.center = draw_center
        
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
                if self.dir_x < 0: img = pygame.transform.flip(img, True, False)
                if self.frost_timer > 0:
                    img = img.copy(); img.fill((100, 200, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)
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
            
            if self.dir_x != 0 or self.dir_y != 0:
                angle = math.atan2(self.dir_y, self.dir_x)
                if self.combat_type == "melee":
                    swing = math.sin(pygame.time.get_ticks() * 0.015) * 0.8; draw_angle = angle + swing
                    end_x, end_y = draw_center[0] + math.cos(draw_angle) * (self.size * 1.0), draw_center[1] + math.sin(draw_angle) * (self.size * 1.0)
                    pygame.draw.line(surface, (220, 220, 220), draw_center, (end_x, end_y), 4)
                    h_x, h_y = draw_center[0] + math.cos(draw_angle) * (self.size * 0.3), draw_center[1] + math.sin(draw_angle) * (self.size * 0.3)
                    p_angle = draw_angle + math.pi / 2
                    pygame.draw.line(surface, (150, 100, 50), (h_x + math.cos(p_angle)*6, h_y + math.sin(p_angle)*6), (h_x - math.cos(p_angle)*6, h_y - math.sin(p_angle)*6), 3)
                elif self.combat_type == "ranged":
                    end_x, end_y = draw_center[0] + math.cos(angle) * (self.size * 0.8), draw_center[1] + math.sin(angle) * (self.size * 0.8)
                    pygame.draw.line(surface, (80, 80, 80), draw_center, (end_x, end_y), 6); pygame.draw.circle(surface, ORANGE, (int(end_x), int(end_y)), 3)

        if self.max_shield > 0 and self.shield > 0:
            pygame.draw.rect(surface, GRAY, (draw_rect.x, draw_rect.y - 14, self.size, 4))
            pygame.draw.rect(surface, (0, 150, 255), (draw_rect.x, draw_rect.y - 14, self.size * (max(0, self.shield)/self.max_shield), 4))
        if self.hp < self.max_hp:
            pygame.draw.rect(surface, GRAY, (draw_rect.x, draw_rect.y - 8, self.size, 4))
            pygame.draw.rect(surface, GREEN, (draw_rect.x, draw_rect.y - 8, self.size * (max(0, self.hp)/self.max_hp), 4))
#Boss類別，包含位置、大小、生命值、攻擊方式和特殊效果等屬性，更新時會根據玩家位置來移動和攻擊，並且處理冰凍、燃燒和其他狀態效果的邏輯，繪製時會根據狀態來呈現不同的圖像或幾何圖形，確保玩家在遊戲中能夠清晰地看到Boss的存在和威脅
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
        
        if self.b_type == "YELLOW": self.color, self.speed, self.state = YELLOW, 3.0, "EVADE"
        elif self.b_type == "RED": self.color, self.speed, self.state, self.aim_x, self.aim_y = RED, 2.5, "CHASE", 0, 0
        elif self.b_type == "PURPLE": self.color, self.speed, self.state = PURPLE, 2.0, "FLEE"
        elif self.b_type == "CYAN": self.color, self.speed, self.state = CYAN, 3.0, "IDLE"
    #更新Boss的位置和狀態，首先根據玩家位置來計算移動方向，然後根據攻擊模式來決定移動和攻擊的行為，最後處理冰凍、燃燒和其他狀態效果的邏輯，確保Boss在遊戲中能夠正確地追蹤玩家並產生攻擊行為
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
        tang_x, tang_y = -dir_y, dir_x
        #根據不同的Boss類型和狀態來決定行為模式，黃色Boss會在閃避和攻擊之間切換，紅色Boss會追蹤玩家並進行衝刺攻擊，紫色Boss會在逃跑和召喚小怪之間切換，青色Boss會在移動和射擊之間切換，確保每個Boss都有獨特的行為模式和挑戰性
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
    #繪製Boss的圖像，首先根據狀態來決定使用哪個圖像或幾何圖形來繪製Boss，然後根據位置和攝像機偏移來計算繪製位置，最後將圖像或幾何圖形繪製到屏幕上，確保玩家在遊戲中能夠清晰地看到Boss的存在和威脅
    def draw(self, surface):
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        anim_key = "boss_" + self.b_type
        anim_frames = animations.get(anim_key)
        if anim_frames:
            img = anim_frames[int(pygame.time.get_ticks() / 150) % len(anim_frames)]
            surface.blit(img, img.get_rect(center=draw_center))
        else:
            c = (100, 200, 255) if self.frost_timer > 0 else self.color
            if self.b_type == "CYAN":
                pts = [(draw_center[0], draw_center[1] - self.size), (draw_center[0] + self.size, draw_center[1]), (draw_center[0], draw_center[1] + self.size), (draw_center[0] - self.size, draw_center[1])]
                pygame.draw.polygon(surface, c, pts); pygame.draw.polygon(surface, WHITE, pts, 3)
            else: pygame.draw.rect(surface, c, self.rect.copy().move(-camera_x, -camera_y))
        
        if self.b_type == "YELLOW":
            if self.state == "EVADE": pygame.draw.circle(surface, WHITE, draw_center, int(self.size/2) + 15, 3)
            elif self.state == "CHARGE": pygame.draw.circle(surface, RED, draw_center, int(self.size/2) + max(0, 30 - int(self.state_timer / 2)), 2)
        elif self.b_type == "RED" and self.state == "WARN": pygame.draw.line(surface, RED, draw_center, (int(self.aim_x - camera_x), int(self.aim_y - camera_y)), max(1, int(self.state_timer / 8)))
        elif self.b_type == "PURPLE" and self.state == "SUMMON": pygame.draw.circle(surface, DARK_PURPLE, draw_center, int(self.size/2) + min(60, self.state_timer), 3)
        elif self.b_type == "CYAN" and self.state == "FIRE": pygame.draw.circle(surface, CYAN, draw_center, int(self.size/2) + 20, 4)

# 遊戲全域狀態與事件系統
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
#進入掩體，重置遊戲狀態並根據是否成功完成突襲來處理獎勵和懲罰，確保玩家在每次進入掩體時都能夠有一個清晰的起點和適當的獎勵機制
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

    player.hp = player.max_hp
    player.shield = player.max_shield
    player.ammo = player.base_max_ammo + player.mag_size_bonus
    
    bullets.clear(); bunker_bullets.clear(); enemy_bullets.clear(); enemies.clear()
    particles.clear(); items.clear(); trails.clear(); damage_texts.clear(); chests.clear()
    boss = None; boss_active = False
    shoot_cooldown, magnet_timer, screen_flash_timer = 0, 0, 0
    boss_army_active, extraction_timer, extraction_pt, extract_progress = False, 15*60*FPS, None, 0
    enemy_spawn_timer = 0
    
    player.x, player.y = MAP_WIDTH//2, MAP_HEIGHT//2
    game_state = "BUNKER"
    stop_sound("boss_bgm")
#開始突襲，重置遊戲狀態並生成敵人和寶箱，確保玩家在每次開始突襲時都能夠有一個清晰的起點和適當的挑戰機制
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
    extract_progress = 0
    boss_army_active = False
    boss_active, boss = False, None
    enemy_spawn_timer = 10 
    for _ in range(15): chests.append(Chest(random.randint(400, MAP_WIDTH-400), random.randint(400, MAP_HEIGHT-400), "NORMAL"))
    for _ in range(5): chests.append(Chest(random.randint(400, MAP_WIDTH-400), random.randint(400, MAP_HEIGHT-400), "LOCKED"))
    play_sound("boss_bgm", loop=-1)
#完全重置遊戲狀態，清除所有進度和獎勵，並返回主菜單，確保玩家在選擇重新開始遊戲時能夠有一個全新的體驗
def full_wipe(mode="NORMAL"):
    global player, game_mode, chosen_upgrades, lost_item, defeated_boss_levels
    game_mode = mode
    player = Player()
    chosen_upgrades.clear()
    lost_item = None
    defeated_boss_levels.clear()
    enter_bunker(success=False)


# 遊戲啟動與主迴圈，處理遊戲的主要邏輯和事件，包括玩家輸入、遊戲狀態更新、敵人行為、碰撞檢測和繪製等

full_wipe("NORMAL")
game_state = "MENU"
dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); dim_surface.fill((0, 0, 0, 180))
#這一行代碼設置了一個布爾變量running為True，這個變量用於控制遊戲主循環的運行狀態。
#當running為True時，遊戲主循環會繼續執行，處理玩家輸入、更新遊戲狀態、繪製圖像等；當running被設置為False時，主循環將停止，遊戲將結束並退出
running = True 
#定義遊戲中各種按鈕的矩形區域，主菜單、難度選擇、商店、庫存和其他界面
#分別是開始遊戲、查看更新日誌、退出遊戲、選擇普通模式、選擇挑戰模式、難度選擇界面的返回按鈕、更新日誌界面的關閉按鈕、商店界面中升級生命值、傷害和速度的按鈕，以及商店、庫存、武器和模組界面的關閉按鈕、顯示升級選項的列表區域和確認升級的按鈕
#按鈕的x坐標、y坐標、寬度和高度
start_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 20, 220, 50)
changelog_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 100, 220, 50)
exit_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 180, 220, 50)
normal_button = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 - 60, 210, 230)
challenge_button = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 - 60, 210, 230)
difficulty_back_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 200, 220, 50)
changelog_close_button = pygame.Rect(WIDTH//2 + 300, HEIGHT//2 - 200, 40, 40)
shop_buttons = {"hp": pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 80, 140, 40), "dmg": pygame.Rect(WIDTH//2 + 10, HEIGHT//2 - 80, 140, 40), "spd": pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 25, 140, 40)}
btn_hp, btn_dmg, btn_spd = shop_buttons["hp"], shop_buttons["dmg"], shop_buttons["spd"]
btn_shop_close = pygame.Rect(WIDTH//2 + 260, HEIGHT//2 - 230, 60, 60)
btn_stash_close = pygame.Rect(WIDTH//2 + 260, HEIGHT//2 - 230, 60, 60)
btn_wep_close = pygame.Rect(WIDTH//2 + 260, HEIGHT//2 - 230, 60, 60)
btn_mod_close = pygame.Rect(WIDTH//2 + 260, HEIGHT//2 - 230, 60, 60)
list_rect = pygame.Rect(WIDTH//2 - 280, HEIGHT//2 - 200, 560, 300)
confirm_upgrade_button = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 230, 100, 50)

while running:
    if 'lost_item' in globals() and lost_item:
        try: lost_item.rect.center = (int(lost_item.x), int(lost_item.y))
        except Exception: pass
    m_x, m_y = pygame.mouse.get_pos()
    m_pos = (m_x, m_y)
    hovered_slot_info = None 

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
                player = Player()
                chosen_upgrades.clear()
                enter_bunker(success=False)
            
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
        #庫存界面，處理玩家與庫存物品的交互，包括拖放物品、快速轉移物品和關閉庫存界面等，確保玩家在管理庫存時能夠有一個流暢和直觀的體驗
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
            #拖放物品到庫存或玩家背包，首先檢查鼠標位置是否在庫存格子或玩家背包格子上，如果是，則嘗試將物品放入對應的格子中，如果放入成功，則從原位置移除物品；如果放入失敗，則將物品放回原位置；如果鼠標位置不在任何格子上，則將物品丟棄在玩家當前位置，並從原位置移除物品；最後重置拖動狀態
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
        #主菜單界面，處理玩家在主菜單上的點擊事件，包括開始遊戲、查看更新日誌和退出遊戲等選項，確保玩家在進入遊戲前能夠有一個清晰的選擇界面
        elif game_state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_changelog:
                    if changelog_close_button.collidepoint(event.pos): show_changelog, changelog_scroll = False, 0
                else:
                    if start_button.collidepoint(event.pos): game_state = "DIFFICULTY"
                    elif changelog_button.collidepoint(event.pos): show_changelog, changelog_scroll = True, 0; rebuild_changelog_cache(640, 380)
                    elif exit_button.collidepoint(event.pos): running = False
        #難度選擇界面，處理玩家在難度選擇界面上的點擊事件，包括選擇普通模式、挑戰模式和返回主菜單等選項，確保玩家在開始遊戲前能夠有一個清晰的難度選擇界面
        elif game_state == "DIFFICULTY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if normal_button.collidepoint(event.pos): full_wipe("NORMAL")
                elif challenge_button.collidepoint(event.pos): full_wipe("CHALLENGE")
                elif difficulty_back_button.collidepoint(event.pos): game_state = "MENU"
        #掩體界面，處理玩家在掩體內的交互事件，包括進入突襲、進入商店、進入庫存、進入模組工作台和進入武器庫等選項，確保玩家在掩體內能夠有一個清晰的交互界面和適當的獎勵機制
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
        #商店界面，處理玩家在商店內的交互事件，包括購買升級、關閉商店等選項，確保玩家在商店內能夠有一個清晰的交互界面和適當的獎勵機制
        elif game_state == "SHOP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_hp.collidepoint(event.pos) and persistent_stats["scrap"] >= 50:
                    persistent_stats["scrap"] -= 50; persistent_stats["max_hp"] += 10; player.max_hp += 10; player.hp += 10; play_sound("levelup")
                elif btn_dmg.collidepoint(event.pos) and persistent_stats["scrap"] >= 50:
                    persistent_stats["scrap"] -= 50; persistent_stats["dmg_bonus"] += 2; player.bullet_damage_bonus += 2; play_sound("levelup")
                elif btn_spd.collidepoint(event.pos) and persistent_stats["scrap"] >= 50:
                    persistent_stats["scrap"] -= 50; persistent_stats["speed_bonus"] += 0.2; player.base_speed += 0.2; play_sound("levelup")
                elif btn_shop_close.collidepoint(event.pos): game_state = "BUNKER"
        #武器庫界面，處理玩家在武器庫內的交互事件，包括選擇武器、裝備武器、出售武器和關閉武器庫等選項，確保玩家在武器庫內能夠有一個清晰的交互界面和適當的獎勵機制
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
            #右鍵點擊武器庫中的武器或玩家背包中的武器，首先檢查鼠標位置是否在武器庫列表區域內，如果是，則計算出被點擊的武器索引，並嘗試將該武器添加到玩家背包中，如果添加成功，則從武器庫中移除該武器；如果鼠標位置不在武器庫列表區域內，則檢查是否點擊了玩家背包中的武器，如果是，則嘗試將該武器添加到武器庫中，如果添加成功，則從玩家背包中移除該武器；最後更新武器庫列表和播放相應的聲音效果    
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
                    rect = pygame.Rect(p_start_x_w + (i%11)*58, p_start_y_w + (i//11)*58, 50, 50)
                    item = player.inventory[i]
                    if rect.collidepoint(event.pos) and item and item.type == "WEAPON":
                        persistent_stats["weapon_stash"].append(item.weapon_obj)
                        player.inventory[i] = None; sort_weapon_stash()
                        arsenal_weapons_list = [generate_weapon(n, "白") for n in WEAPON_TYPES] + persistent_stats["weapon_stash"]; play_sound("exp")
        #改造台界面，處理玩家在改造台內的交互事件，包括選擇武器、升級武器、重置詞綴和關閉改造台等選項，確保玩家在改造台內能夠有一個清晰的交互界面和適當的獎勵機制
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
                            
                            # 改造台套用動態詞綴池
                            pool = ["速射", "散射", "吸血", "爆擊"]
                            if selected_mod_weapon.bullet_type not in ["piercing", "laser", "cannon", "flamethrower"]: pool.append("穿透")
                            if selected_mod_weapon.bullet_type not in ["flamethrower", "flame_grenade"]: pool.append("燃燒")
                            selected_mod_weapon.affixes = random.sample(pool, min({"白":0, "藍":1, "紫":2, "金":3}[selected_mod_weapon.rarity], len(pool)))
                            
                            apply_weapon_stats(selected_mod_weapon); play_sound("levelup")
                      #重置詞綴按鈕被點擊，且選中的武器稀有度不為白色，首先根據武器的稀有度計算重置詞綴的成本，如果玩家的碎片數量足夠支付成本，則從玩家的碎片中扣除相應的數量，然後根據武器的類型動態生成一個新的詞綴池，從中隨機選擇適合該武器稀有度的詞綴數量，最後將選中的詞綴應用到武器上並播放相應的聲音效果      
                    if reroll_btn.collidepoint(event.pos) and selected_mod_weapon.rarity != "白":
                        cost = {"藍":30, "紫":80, "金":150}[selected_mod_weapon.rarity]
                        if persistent_stats["scrap"] >= cost:
                            persistent_stats["scrap"] -= cost
                            
                            # 動態詞綴池
                            pool = ["速射", "散射", "吸血", "爆擊"]
                            if selected_mod_weapon.bullet_type not in ["piercing", "laser", "cannon", "flamethrower"]: pool.append("穿透")
                            if selected_mod_weapon.bullet_type not in ["flamethrower", "flame_grenade"]: pool.append("燃燒")
                            selected_mod_weapon.affixes = random.sample(pool, min({"白":0, "藍":1, "紫":2, "金":3}[selected_mod_weapon.rarity], len(pool)))
                            
                            apply_weapon_stats(selected_mod_weapon); play_sound("exp")
        #暫停界面，處理玩家在暫停界面上的交互事件，包括繼續遊戲、進入掩體、重新開始和退出遊戲等選項，確保玩家在暫停遊戲時能夠有一個清晰的選擇界面和適當的獎勵機制
        elif game_state == "PAUSED":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 10, 220, 50).collidepoint(event.pos): game_state = "PLAYING"
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 10, 220, 50).collidepoint(event.pos): enter_bunker(success=False)
                elif pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 80, 220, 50).collidepoint(event.pos): full_wipe("NORMAL")
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 80, 220, 50).collidepoint(event.pos): running = False
        #升級界面，處理玩家在升級界面上的交互事件，包括選擇升級和確認升級等選項，確保玩家在升級時能夠有一個清晰的選擇界面和適當的獎勵機制
        elif game_state == "LEVEL_UP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected_upgrade_position is not None and confirm_upgrade_button.collidepoint(event.pos): apply_upgrade(current_upgrade_choices[selected_upgrade_position])
                else:
                    for i, card in enumerate(cards):
                        if i < len(current_upgrade_choices) and card.collidepoint(event.pos): selected_upgrade_position = i; break

    # 遊戲邏輯更新
    if game_state == "BUNKER":
        bunker_clamp = pygame.Rect(MAP_WIDTH//2 - 400, MAP_HEIGHT//2 - 300, 800, 600)
        player.update(clamp_rect=bunker_clamp)
        camera_x, camera_y = MAP_WIDTH//2 - WIDTH/2, MAP_HEIGHT//2 - HEIGHT/2

        if bunker_dummy: bunker_dummy.update()
        mouse_btns = pygame.mouse.get_pressed()
        if mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing:
            wep = player.weapons[player.current_weapon_idx]
            base_dir = pygame.math.Vector2((m_x + camera_x) - player.x, (m_y + camera_y) - player.y)
            if base_dir.length() > 0: base_dir.normalize_ip()
            else: base_dir = pygame.math.Vector2(1, 0)
            
            player.current_spread = min(player.bullet_spread + 25.0, player.current_spread + wep.base_recoil)
            t_bullets = player.bullet_count + (4 if wep.bullet_type == "shotgun" else 0) + (2 if "散射" in wep.affixes else 0)
            s_angle = -(t_bullets - 1) * player.current_spread / 2
            
            if wep.bullet_type in ["cannon", "flame_grenade"]: screen_shake = 5
            elif wep.bullet_type == "shotgun": screen_shake = 2

            for i in range(t_bullets):
                s_dir = base_dir.rotate(s_angle + i * player.current_spread)
                for j in range(1 + player.extra_same_path_bullets):
                    off = s_dir * (j * 15)
                    tx, ty = player.x + s_dir.x * 100 + off.x, player.y + s_dir.y * 100 + off.y
                    if wep.bullet_type == "flamethrower": tx += random.randint(-40, 40); ty += random.randint(-40, 40)
                    bunker_bullets.append(Bullet(player.rect.centerx + off.x, player.rect.centery + off.y, tx, ty, wep, player.guidance_level, player.bullet_damage_bonus))
            shoot_cooldown = wep.shoot_delay
            play_sound(wep.sound_name)
        # 更新子彈位置，檢查與掩體Dummy的碰撞，處理傷害、擊打反饋和子彈壽命，確保子彈在遊戲中有適當的行為和反應
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
    #遊戲主循環，根據當前的遊戲狀態更新遊戲邏輯，包括玩家移動、敵人生成和行為、子彈更新、物品交互和界面交互等，確保遊戲在不同狀態下有適當的行為和反應
    elif game_state == "PLAYING" and not show_inventory:
        
        if enemy_spawn_timer > 0: enemy_spawn_timer -= 1
        if enemy_spawn_timer <= 0 and not boss_army_active:
            if len(enemies) < 150: 
                enemies.append(Enemy(player.level, random.random() < 0.15, player.x, player.y))
            enemy_spawn_timer = max(5, 30 - player.level) 
            
        shake_x = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
        shake_y = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
        if screen_shake > 0: screen_shake -= 1

        camera_x = max(0, min(MAP_WIDTH - WIDTH, player.x - WIDTH / 2)) + shake_x
        camera_y = max(0, min(MAP_HEIGHT - HEIGHT, player.y - HEIGHT / 2)) + shake_y
        
        if magnet_timer > 0: magnet_timer -= 1
        if screen_flash_timer > 0: screen_flash_timer -= 1
        # 更新敵人行為，處理與玩家的互動，生成子彈和掉落物，並管理敵人的生命週期，確保遊戲中的敵人有適當的挑戰性和反應
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
            # 處理開寶箱邏輯
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
                            
            # 撿起地上物資 (廢料、鑰匙、補血包、槍枝)
            for g in items[:]:
                if g.item_type not in ["EXP", "MAGNET", "BOMB", "SHIELD"] and math.hypot(player.x - g.x, player.y - g.y) < 70:
                    if g.item_type == "WEAPON":
                        new_item = create_item("WEAPON", 1, g.weapon_obj)
                    else:
                        new_item = create_item(g.item_type, g.count)
                    
                    # 判斷背包是否已滿，如果有空間則放入並刪除地上掉落物
                    if player.add_item(new_item):
                        items.remove(g)
                        play_sound("exp")
        else:
            for c in chests:
                if c.state == "CLOSED": c.open_progress = max(0, c.open_progress - 2)

        if player.exp >= player.max_exp:
            player.exp -= player.max_exp
            player.level += 1; player.max_exp = int(player.max_exp * 1.25)
            choose_upgrade_cards(); game_state = "LEVEL_UP"; play_sound("levelup") 
        # 每5級出現一個BOSS，且不會在同一關重複出現同一個BOSS
        if player.level % 5 == 0 and player.level > 0 and player.level not in defeated_boss_levels and not boss_active and not boss_army_active:
            boss = Boss(random.choice(["YELLOW", "RED", "PURPLE", "CYAN"]), player.level, player.x, player.y)
            boss_active = True; play_sound("boss_bgm", loop=-1) 

        mouse_btns = pygame.mouse.get_pressed()
        world_mouse_x, world_mouse_y = m_x + camera_x, m_y + camera_y
        current_wep = player.weapons[player.current_weapon_idx]
        # 處理玩家射擊邏輯，根據玩家當前武器、彈藥、冷卻時間和其他狀態決定是否可以射擊，生成子彈並應用相應的效果和反饋
        if mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing:
            can_fire = True
            if game_mode == "CHALLENGE":
                if player.ammo <= 0: can_fire = False; player.reload_timer = player.reload_duration if player.reload_timer <= 0 else player.reload_timer
                else: player.ammo -= 1; player.reload_timer = player.reload_duration if player.ammo <= 0 else player.reload_timer
            # 霰彈槍和火焰噴射器在彈藥耗盡後可以繼續射擊，但射擊效果會受到影響，霰彈槍會減少散射彈數，火焰噴射器會減少射程和傷害
            if can_fire:
                base_dir = pygame.math.Vector2(world_mouse_x - player.x, world_mouse_y - player.y)
                if base_dir.length() > 0: base_dir.normalize_ip()
                else: base_dir = pygame.math.Vector2(1, 0)
                
                player.current_spread = min(player.bullet_spread + 25.0, player.current_spread + current_wep.base_recoil)
                t_bullets = player.bullet_count + (4 if current_wep.bullet_type == "shotgun" else 0) + (2 if "散射" in current_wep.affixes else 0)
                s_angle = -(t_bullets - 1) * player.current_spread / 2
            # 根據武器類型應用不同的屏幕震動效果，火炮和榴彈會有較強的震動，而霰彈槍會有較弱的震動，確保射擊時有適當的視覺反饋
                if current_wep.bullet_type in ["cannon", "flame_grenade"]: screen_shake = 5
                elif current_wep.bullet_type == "shotgun": screen_shake = 2

                for i in range(t_bullets):
                    s_dir = base_dir.rotate(s_angle + i * player.current_spread)
                    for j in range(1 + player.extra_same_path_bullets):
                        spawn_offset = s_dir * (j * 15) 
                        tx, ty = player.x + s_dir.x * 100 + spawn_offset.x, player.y + s_dir.y * 100 + spawn_offset.y
                        if current_wep.bullet_type == "flamethrower": tx += random.randint(-40, 40); ty += random.randint(-40, 40)
                        bullets.append(Bullet(player.rect.centerx + spawn_offset.x, player.rect.centery + spawn_offset.y, tx, ty, current_wep, player.guidance_level, player.bullet_damage_bonus))
                shoot_cooldown = max(2, current_wep.shoot_delay - player.shoot_delay_reduction)
                play_sound(current_wep.sound_name)
        # 右鍵技能環狀穿透彈幕    
        if mouse_btns[2] and player.skill_cd <= 0 and player.energy >= player.skill_cost and not player.is_dashing:
            player.energy -= player.skill_cost; player.skill_cd = player.skill_max_cd; play_sound("shoot_laser") 
            temp_wep = generate_weapon("手槍", "白"); temp_wep.bullet_type = "piercing"; temp_wep.damage = 50
            for i in range(16):
                angle = math.radians(i * (360 / 16))
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, player.rect.centerx + math.cos(angle)*100, player.rect.centery + math.sin(angle)*100, temp_wep, dmg_bonus=player.bullet_damage_bonus))

        if shoot_cooldown > 0: shoot_cooldown -= 1
        player.update()
        # 無敵模式下不受任何傷害，直接跳過碰撞和死亡檢測
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
        # 處理玩家的光環傷害，對範圍內的敵人造成持續傷害，並根據玩家的光環等級增加傷害和範圍，同時生成相應的粒子效果和掉落物
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
        # 處理玩家的衝刺軌跡，當玩家在衝刺時生成軌跡效果，並隨著時間減少軌跡的生命週期，確保衝刺軌跡在遊戲中有適當的視覺效果和持續時間
        if player.is_dashing: trails.append(DashTrail(player.rect.centerx, player.rect.centery, player.size))
        for t in trails[:]: t.update(); trails.remove(t) if t.life <= 0 else None
            
        map_rect = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
        alive_bullets = []

        for b in bullets:
            b.update(enemies)
            
            if b.explode:
                screen_shake = 8; play_sound("shoot_cannon") 
                for _ in range(30): particles.append(Particle(b.x, b.y, ORANGE))
                for e in enemies[:]:
                    if math.hypot(e.x - b.x, e.y - b.y) < 120: 
                        actual_dmg = b.damage
                        if e.shield > 0:
                            leftover = actual_dmg - e.shield
                            e.shield = max(0, e.shield - actual_dmg)
                            if leftover > 0: e.hp -= leftover
                        else: e.hp -= actual_dmg
                        
                        if e.hp <= 0: 
                            if random.random() < 0.4: items.append(DropItem(e.x, e.y, "EXP"))
                            if e in enemies: enemies.remove(e)
                            
                if boss_active and boss.state != "DEFEAT" and math.hypot(boss.x - b.x, boss.y - b.y) < 150: 
                    boss.hp -= b.damage
                continue 
            # 子彈與敵人碰撞檢測        
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
                        leftover = b.damage - e.shield
                        e.shield = max(0, e.shield - b.damage)
                        if leftover > 0: e.hp -= leftover
                    else: e.hp -= b.damage
                        
                    damage_texts.append(DamageText(e.x, e.y - 20, b.damage, RED if b.is_crit else (YELLOW if b.damage >= 40 else WHITE), b.is_crit))
                    hit_something = True
                    for _ in range(5): particles.append(Particle(e.x, e.y, b.color))
                    play_sound("hit")
                    # 根據敵人類型和是否為精英，決定掉落物種類和數量
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
                    
                    if not b.is_piercing:
                        break 
            # Boss 碰撞檢測放在最後，確保子彈優先與普通敵人互動
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
                        for _ in range(10): items.append(DropItem(boss.x + random.randint(-40,40), boss.y + random.randint(-40,40), "SCRAP", random.randint(2,5)))
                        items.append(DropItem(boss.x, boss.y, "KEY"))
                        for _ in range(50): particles.append(Particle(boss.x, boss.y, YELLOW))

            if b.lifespan > 0 and map_rect.colliderect(b.rect) and (not hit_something or b.is_piercing) and not b.explode:
                alive_bullets.append(b)

        bullets = alive_bullets

        # 敵人、子彈、傷害數字、粒子更新與碰撞檢測
        
        for dt in damage_texts[:]:
            dt.update()
            if dt.timer <= 0: damage_texts.remove(dt)

        for p in particles[:]:
            p.update()
            if p.timer <= 0: particles.remove(p)

        for eb in enemy_bullets[:]:
            eb.update(player.x, player.y)
            
            # 如果飛彈壽命耗盡，產生範圍爆炸
            if getattr(eb, 'explode', False):
                play_sound("shoot_cannon") # 播放爆炸音效
                # 產生環狀爆炸特效
                for i in range(12): 
                    p = Particle(eb.x, eb.y, eb.color)
                    p.vel_x, p.vel_y = math.cos(i*30)*3, math.sin(i*30)*3
                    particles.append(p)
                
                # 檢查玩家是否在爆炸範圍內 (半徑 70)
                if math.hypot(player.x - eb.x, player.y - eb.y) < 70:
                    if not player.god_mode and player.invincible_timer <= 0 and not player.is_dashing:
                        actual_dmg = max(1, int(eb.damage * 1.5) - player.damage_reduction) # 爆炸傷害為 1.5 倍
                        if player.shield > 0:
                            if actual_dmg > player.shield: leftover = actual_dmg - player.shield; player.shield = 0; player.hp -= leftover
                            else: player.shield -= actual_dmg
                        else: player.hp -= actual_dmg
                        player.invincible_timer = player.invincible_duration; screen_shake = 12; play_sound("hurt")
                
                if eb in enemy_bullets: enemy_bullets.remove(eb)
                continue

            if not map_rect.colliderect(eb.rect): 
                enemy_bullets.remove(eb)

        for e in enemies:
            e.update(player.x, player.y, enemies, enemy_bullets)

        if boss_active and boss:
            boss.update(player.x, player.y, bullets, enemies, enemy_bullets)
        ##################################################################################
        #玩家受到攻擊的判定，無論是敵人本體還是子彈，只要碰撞就會觸發傷害計算和無敵時間，並且在玩家死亡時生成((遺失物))
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
                    player.invincible_timer = player.invincible_duration 
                    screen_shake = 10; play_sound("hurt")
                    
                if e.combat_type == "kamikaze":
                    for _ in range(15): particles.append(Particle(e.x, e.y, ORANGE))
                    if e in enemies: enemies.remove(e)
       # Boss 的碰撞檢測放在最後，確保玩家優先與普通敵人互動，只有在沒有其他碰撞的情況下才會檢測與 Boss 的碰撞，這樣可以增加遊戲的公平性和挑戰性             
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
        # Boss 的碰撞檢測放在最後，確保玩家優先與普通敵人和子彈互動，只有在沒有其他碰撞的情況下才會檢測與 Boss 的碰撞，這樣可以增加遊戲的公平性和挑戰性
        if boss_active and player.rect.colliderect(boss.rect) and game_state == "PLAYING": 
            if not player.god_mode and player.invincible_timer <= 0 and not player.is_dashing:
                actual_dmg = max(1, 40 - player.damage_reduction)
                if player.shield > 0:
                    if actual_dmg > player.shield: leftover = actual_dmg - player.shield; player.shield = 0; player.hp -= leftover
                    else: player.shield -= actual_dmg
                else: player.hp -= actual_dmg
                player.invincible_timer = player.invincible_duration; screen_shake = 10; play_sound("hurt")

        # 統一的玩家死亡判定：無論是否為白板，都會蓋過上一次的遺失物
        if player.hp <= 0 and game_state == "PLAYING":
            inv_copy = [item for item in player.inventory if item is not None]
            w1 = player.primary_weapon if player.primary_weapon.rarity != "白" else None
            w2 = player.secondary_weapon if player.secondary_weapon.rarity != "白" else None
            lost_item = PlayerLostItem(player.x, player.y, player.level, player.exp, list(chosen_upgrades), inv_copy, w1, w2)
            
            game_state = "DIED"
            play_sound("gameover")
            stop_sound("boss_bgm")

        # 狀態保護：只有活著的狀態下，才能拾取物資或遺失物 (防止死亡瞬間立刻把剛掉落的遺失物撿起銷毀)
        if game_state == "PLAYING":
            eff_radius = 9999 if magnet_timer > 0 else player.magnet_radius
            for g in items[:]:
                g.update(player.x, player.y, eff_radius)
                if g.item_type in ["EXP", "MAGNET", "BOMB", "SHIELD"] and player.rect.colliderect(g.rect):
                    items.remove(g)
                    if g.item_type == "EXP":
                        player.exp += 25 * player.exp_multiplier; play_sound("exp") 
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

    #畫面繪製
    if game_state in ["BUNKER", "SHOP", "GENERAL_STASH", "MOD_STATION", "WEAPON_STASH"]:
        screen.fill(BLACK)
        for i in range(0, WIDTH, 40): pygame.draw.line(screen, (15, 18, 22), (i,0), (i,HEIGHT))
        for i in range(0, HEIGHT, 40): pygame.draw.line(screen, (15, 18, 22), (0,i), (WIDTH,i))
        
        bunker_rect = pygame.Rect(MAP_WIDTH//2 - 400 - camera_x, MAP_HEIGHT//2 - 300 - camera_y, 800, 600)
        pygame.draw.rect(screen, (25, 28, 35), bunker_rect); pygame.draw.rect(screen, (60, 65, 80), bunker_rect, 4)
        #畫出地堡的終端機，部署閘門、黑市商店、改造台、收藏箱和武器箱，並根據當前遊戲狀態決定是否顯示地堡Dummy(我知道實際看起來不太像終端機OWO)
        draw_terminal(screen, pygame.Rect(MAP_WIDTH//2 - 60 - camera_x, MAP_HEIGHT//2 + 200 - camera_y, 120, 60), GREEN, "部署閘門 [E]", "DEPLOY")
        draw_terminal(screen, pygame.Rect(MAP_WIDTH//2 - 350 - camera_x, MAP_HEIGHT//2 - 50 - camera_y, 100, 100), BLUE, "黑市商店 [E]", "SHOP")
        draw_terminal(screen, pygame.Rect(MAP_WIDTH//2 - 150 - camera_x, MAP_HEIGHT//2 - 150 - camera_y, 100, 100), ORANGE, "改造台 [E]", "MOD")
        draw_terminal(screen, pygame.Rect(MAP_WIDTH//2 + 50 - camera_x, MAP_HEIGHT//2 - 150 - camera_y, 100, 100), (50, 150, 200), "收藏箱 [E]", "STASH")
        draw_terminal(screen, pygame.Rect(MAP_WIDTH//2 + 250 - camera_x, MAP_HEIGHT//2 - 50 - camera_y, 100, 100), RED, "武器箱 [E]", "WEAPON")
        if bunker_dummy: bunker_dummy.draw(screen)

        for b in bunker_bullets: b.draw(screen)
        for p in particles: p.draw(screen)
        for dt in damage_texts: dt.draw(screen)

        screen.blit(large_font.render("地堡安全屋", True, YELLOW), (WIDTH//2 - 120, 50))
        screen.blit(font.render(f"擁有廢料: {persistent_stats['scrap']}", True, SCRAP_COLOR), (WIDTH//2 - 70, 100))
        
        player.draw(screen, player.weapons[player.current_weapon_idx])
        draw_upgrade_summary(screen, WIDTH - 260, 20, max_items=5)
        #根據當前遊戲狀態繪製相應的UI界面，包含黑市商店、格子收藏箱和武器改造台，並在玩家與這些界面互動時顯示相關資訊和選項
        if game_state == "SHOP":
            screen.blit(dim_surface, (0, 0))
            draw_ui_panel(screen, shop_bg, "黑市升級 (BLACK MARKET)", BLUE)
            draw_hover_button(screen, btn_hp, f"最大血量+10 (目前:{player.max_hp}) - 50廢料", GREEN if persistent_stats["scrap"]>=50 else GRAY, (50, 180, 50))
            draw_hover_button(screen, btn_dmg, f"武器傷害+2 (目前:+{persistent_stats['dmg_bonus']}) - 50廢料", ORANGE if persistent_stats["scrap"]>=50 else GRAY, (200, 120, 0))
            draw_hover_button(screen, btn_spd, f"移動速度+0.2 (目前:+{persistent_stats['speed_bonus']:.1f}) - 50廢料", CYAN if persistent_stats["scrap"]>=50 else GRAY, (0, 180, 180))
            draw_hover_button(screen, btn_shop_close, "關閉離開", (150, 50, 50), RED)

        elif game_state == "GENERAL_STASH":
            screen.blit(dim_surface, (0, 0))
            draw_ui_panel(screen, stash_bg, "格子收藏箱 (GENERAL STASH)", (50, 150, 200))
            #繪製6x6的格子收藏箱界面，顯示玩家存放的物品，並根據物品類型使用不同顏色的圓點表示，同時在游標懸停時顯示物品資訊和高亮邊框
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
            draw_hover_button(screen, btn_stash_close, "關閉離開", (150, 50, 50), RED)
        #根據當前遊戲狀態繪製相應的UI界面，包含黑市商店、格子收藏箱和武器改造台，並在玩家與這些界面互動時顯示相關資訊和選項
        elif game_state == "MOD_STATION":
            screen.blit(dim_surface, (0, 0))
            draw_ui_panel(screen, mod_bg, "武器改造台 (WORKBENCH)", ORANGE)
            #繪製主武器和副武器的改造選項，顯示當前裝備的武器名稱和品質顏色，並在玩家選擇或懸停時高亮邊框，同時在右側顯示選中武器的詳細資訊和可用改造選項
            pygame.draw.rect(screen, (30,34,42), rect_prim, border_radius=8)
            screen.blit(small_font.render("主武器", True, WHITE), (rect_prim.centerx - 25, rect_prim.y + 10))
            screen.blit(small_font.render(player.primary_weapon.base_name, True, get_rarity_color(player.primary_weapon.rarity)), (rect_prim.centerx - 35, rect_prim.centery + 10))
            if selected_mod_weapon == player.primary_weapon: pygame.draw.rect(screen, YELLOW, rect_prim, 2, border_radius=8)
            elif rect_prim.collidepoint(m_pos): pygame.draw.rect(screen, WHITE, rect_prim, 1, border_radius=8)
            #副武器的繪製邏輯與主武器類似，但會根據玩家當前裝備的副武器顯示相應的名稱和品質顏色，並在玩家選擇或懸停時高亮邊框，同時在右側顯示選中武器的詳細資訊和可用改造選項
            pygame.draw.rect(screen, (30,34,42), rect_sec, border_radius=8)
            screen.blit(small_font.render("副武器", True, WHITE), (rect_sec.centerx - 25, rect_sec.y + 10))
            screen.blit(small_font.render(player.secondary_weapon.base_name, True, get_rarity_color(player.secondary_weapon.rarity)), (rect_sec.centerx - 35, rect_sec.centery + 10))
            if selected_mod_weapon == player.secondary_weapon: pygame.draw.rect(screen, YELLOW, rect_sec, 2, border_radius=8)
            elif rect_sec.collidepoint(m_pos): pygame.draw.rect(screen, WHITE, rect_sec, 1, border_radius=8)
            #繪製6x4的武器改造台界面，顯示玩家背包中的武器，並根據武器品質使用不同顏色的圓點表示，同時在游標懸停時顯示武器資訊和高亮邊框，並在右側顯示選中武器的詳細資訊和可用改造選項
            hi = draw_player_inv_grid(screen, p_start_x_m, p_start_y_m, m_x, m_y, allow_weapons=True)
            if hi: hovered_slot_info = hi
            for i in range(24):
                item = player.inventory[i]
                if item and item.type == "WEAPON" and selected_mod_weapon == item.weapon_obj:
                    pygame.draw.rect(screen, YELLOW, (p_start_x_m + (i%6)*58, p_start_y_m + (i//6)*58, 50, 50), 2, border_radius=6)
            #在武器改造台界面右側繪製選中武器的詳細資訊，包括武器名稱、傷害值、詞綴列表，以及根據武器品質顯示相應的改造選項，並根據玩家的廢料數量決定改造選項的可用性，同時在游標懸停時高亮按鈕邊框
            pygame.draw.rect(screen, (25,28,35), (WIDTH//2 + 30, HEIGHT//2 - 150, 300, 400), border_radius=10)
            if selected_mod_weapon:
                c = get_rarity_color(selected_mod_weapon.rarity)
                screen.blit(large_font.render(selected_mod_weapon.full_name, True, c), (WIDTH//2 + 50, HEIGHT//2 - 130))
                screen.blit(font.render(f"傷害: {selected_mod_weapon.damage}", True, WHITE), (WIDTH//2 + 50, HEIGHT//2 - 80))
                aff_str = ",".join(selected_mod_weapon.affixes) if selected_mod_weapon.affixes else "無"
                screen.blit(font.render(f"詞綴: {aff_str}", True, YELLOW), (WIDTH//2 + 50, HEIGHT//2 - 40))
                
                if selected_mod_weapon.rarity != "金":
                    cost = {"白":50, "藍":150, "紫":300}[selected_mod_weapon.rarity]
                    draw_hover_button(screen, upg_btn, f"升級品質 ({cost} 廢料)", GREEN if persistent_stats["scrap"]>=cost else GRAY, (50, 180, 50), BLACK)
                if selected_mod_weapon.rarity != "白":
                    cost = {"藍":30, "紫":80, "金":150}[selected_mod_weapon.rarity]
                    draw_hover_button(screen, reroll_btn, f"重置詞綴 ({cost} 廢料)", BLUE if persistent_stats["scrap"]>=cost else GRAY, (50, 100, 180))
            
            draw_hover_button(screen, btn_mod_close, "關閉離開", (150, 50, 50), RED)

        elif game_state == "WEAPON_STASH":
            screen.blit(dim_surface, (0, 0))
            draw_ui_panel(screen, wep_stash_bg, "全自動武器箱 (ARSENAL)", RED)
            
            p_c, s_c = get_rarity_color(player.primary_weapon.rarity), get_rarity_color(player.secondary_weapon.rarity)
            screen.blit(small_font.render("當前裝備 =>", True, WHITE), (WIDTH//2 - 320, HEIGHT//2 - 260))
            screen.blit(small_font.render(f"主: {player.primary_weapon.full_name}", True, p_c), (WIDTH//2 - 200, HEIGHT//2 - 260))
            screen.blit(small_font.render(f"副: {player.secondary_weapon.full_name}", True, s_c), (WIDTH//2 + 50, HEIGHT//2 - 260))
            # 武器列表區域
            pygame.draw.rect(screen, (15, 18, 22), list_rect, border_radius=6); pygame.draw.rect(screen, (50, 55, 65), list_rect, 1, border_radius=6)
            list_surf = pygame.Surface((list_rect.width, max(list_rect.height, (len(arsenal_weapons_list)+1)//2 * 50)))
            list_surf.fill((15, 18, 22))
            for i, wep in enumerate(arsenal_weapons_list):
                col, row = i % 2, i // 2
                box = pygame.Rect(col*320 + 10, row*50 + 5, 300, 42)
                is_sel = (i == selected_arsenal_idx)
                pygame.draw.rect(list_surf, (40, 45, 55), box, border_radius=6)
                pygame.draw.rect(list_surf, YELLOW if is_sel else GRAY, box, 2 if is_sel else 1, border_radius=6)
                c = get_rarity_color(wep.rarity)
                list_surf.blit(font.render(wep.full_name, True, c), (box.x + 10, box.y + 8))
                aff_txt = ",".join(wep.affixes) if wep.affixes else "無"
                list_surf.blit(tiny_font.render(f"傷:{wep.damage} [{aff_txt}]", True, WHITE), (box.x + 160, box.y + 14))
                if box.collidepoint(m_x - list_rect.x, m_y - list_rect.y + arsenal_scroll_y) and list_rect.collidepoint(m_pos):
                    pygame.draw.rect(list_surf, WHITE, box, 1, border_radius=6)
                    hovered_slot_info = {"source": "ARSENAL", "idx": i, "item": create_item("WEAPON", 1, wep)}

            screen.blit(list_surf, list_rect.topleft, pygame.Rect(0, arsenal_scroll_y, list_rect.width, list_rect.height))
            
            screen.blit(small_font.render("右鍵:切換武器箱與背包 | 游標指著按 [X] 出售", True, GRAY), (WIDTH//2 - 320, HEIGHT//2 + 45))
            for i in range(24):
                rect = pygame.Rect(p_start_x_w + (i%11)*58, p_start_y_w + (i//11)*58, 50, 50)
                pygame.draw.rect(screen, (25, 28, 35), rect, border_radius=6); pygame.draw.rect(screen, (55, 60, 70), rect, 1, border_radius=6)
                item = player.inventory[i]
                if item:
                    if item.type == "WEAPON":
                        pygame.draw.circle(screen, get_rarity_color(item.weapon_obj.rarity), rect.center, 14)
                        if rect.collidepoint(m_x, m_y):
                            hovered_slot_info = {"source": "PLAYER", "idx": i, "item": item}
                            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=6)
                    else: pygame.draw.circle(screen, (60,60,60), rect.center, 14)

            draw_hover_button(screen, btn_prim_w, "裝備為主武器", GREEN, (50, 180, 50), BLACK)
            draw_hover_button(screen, btn_sec_w, "裝備為副武器", BLUE, (50, 100, 180), WHITE)
            draw_hover_button(screen, btn_wep_close, "關閉離開", (150, 50, 50), RED)

        # 游標拖著物品的視覺反饋，根據物品類型顯示不同顏色的圓圈，並且如果游標在某個物品上且沒有拖著東西，則顯示該物品的說明和出售價值
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
    # 根據遊戲狀態繪製遊戲主畫面，包含背景、地圖邊界、玩家、敵人、子彈、物品、粒子效果、傷害數字，以及根據不同狀態顯示相應的提示和UI元素，例如開箱提示、撿取提示、Boss方向箭頭等，同時在玩家死亡時顯示遺失物並提供撿取選項
    elif game_state in ["PLAYING", "PAUSED", "LEVEL_UP", "DIED"]:
        if images.get("bg"):
            bg_w, bg_h = WIDTH, HEIGHT
            for x in range(0, MAP_WIDTH, bg_w):
                for y in range(0, MAP_HEIGHT, bg_h):
                    draw_x = x - int(camera_x); draw_y = y - int(camera_y)
                    if draw_x + bg_w > 0 and draw_x < WIDTH and draw_y + bg_h > 0 and draw_y < HEIGHT: screen.blit(images["bg"], (draw_x, draw_y))
        else: screen.fill(BLACK)
        #地圖邊界框線暫時先用紅色表示，之後可以換成更有科技感的邊界特效會發光閃逤，或是更淺的顏色加上半透明的遮罩，或著配合背景顏色
        pygame.draw.rect(screen, RED, (-int(camera_x), -int(camera_y), MAP_WIDTH, MAP_HEIGHT), 5)
        
        if extraction_pt: extraction_pt.draw(screen)
        if lost_item: lost_item.draw(screen); draw_lost_item_arrow(screen, camera_x, camera_y)
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
        #根據玩家與環境的互動狀態，顯示相應的提示信息，例如當玩家靠近木箱時顯示開箱提示，當玩家靠近可撿取的物品時顯示撿取提示，並且根據木箱類型和玩家是否擁有金鑰匙來調整提示文本和顏色，以提供清晰的反饋和指引
        if game_state == "PLAYING" and not show_inventory:
            for c in chests:
                if c.state == "CLOSED" and math.hypot(player.x - c.x, player.y - c.y) < 70:
                    has_key = any(item.type == "KEY" for item in player.inventory if item)
                    t = "[F] 開啟木箱" if c.type == "NORMAL" else ("[F] 消耗金鑰匙" if has_key else "需要金鑰匙")
                    t_c = WHITE if c.type == "NORMAL" or has_key else RED
                    bg_r = pygame.Rect(c.x - camera_x - 40, c.y - camera_y - 50, font.size(t)[0]+20, 25)
                    popup = pygame.Surface((bg_r.width, bg_r.height), pygame.SRCALPHA)
                    pygame.draw.rect(popup, (20, 20, 25, 200), popup.get_rect(), border_radius=4)
                    screen.blit(popup, (bg_r.x, bg_r.y))
                    screen.blit(small_font.render(t, True, t_c), (bg_r.x+10, bg_r.y+3))
                    
            for g in items:
                if g.item_type not in ["EXP", "MAGNET", "BOMB", "SHIELD"] and math.hypot(player.x - g.x, player.y - g.y) < 70:
                    bg_r = pygame.Rect(g.x - camera_x - 30, g.y - camera_y - 40, 60, 25)
                    popup = pygame.Surface((bg_r.width, bg_r.height), pygame.SRCALPHA)
                    pygame.draw.rect(popup, (20, 20, 25, 200), popup.get_rect(), border_radius=4)
                    screen.blit(popup, (bg_r.x, bg_r.y))
                    screen.blit(small_font.render("[F] 撿取", True, WHITE), (bg_r.x+5, bg_r.y+3))
        
        draw_minimap(screen)
        
        # HUD 資訊，根據玩家的經驗值、等級、血量、護盾、體力、能量、武器裝備狀態以及當前遊戲模式，繪製相應的進度條和文本信息，並使用不同的顏色來表示不同的狀態，例如當血量較低時顯示紅色，當能量不足時顯示灰色，以及根據玩家是否啟用全解鎖密技來調整武器名稱的顏色，以提供清晰的反饋和指引
        pygame.draw.rect(screen, GRAY, (20, 20, 250, 15)); pygame.draw.rect(screen, BLUE, (20, 20, 250 * (player.exp / player.max_exp), 15))
        screen.blit(font.render("等級: " + str(player.level), True, WHITE), (280, 15))

        pygame.draw.rect(screen, GRAY, (20, 45, 200, 15)); pygame.draw.rect(screen, GREEN if player.hp > 30 else RED, (20, 45, 200 * (max(0, player.hp) / player.max_hp), 15))
        screen.blit(font.render("血量", True, WHITE), (230, 40))

        pygame.draw.rect(screen, GRAY, (20, 70, 200, 15)); pygame.draw.rect(screen, (0, 150, 255), (20, 70, 200 * (max(0, player.shield) / player.max_shield), 15))
        screen.blit(font.render("護盾", True, WHITE), (230, 65))

        pygame.draw.rect(screen, GRAY, (20, 95, 150, 10)); pygame.draw.rect(screen, ORANGE, (20, 95, 150 * (player.stamina / player.max_stamina), 10))
        screen.blit(font.render("體力 (Q)", True, WHITE), (180, 87)) 
        
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
        #根據玩家的武器狀態繪製當前裝備的主武器和副武器名稱，並使用不同顏色表示是否啟用全解鎖密技，同時在玩家按下切換武器的按鍵時更新顯示的武器名稱和高亮指示，以提供清晰的裝備資訊    
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
        #根據當前遊戲狀態繪製相應的提示信息，例如當玩家靠近木箱時顯示開箱提示，當玩家靠近可撿取的物品時顯示撿取提示，並且根據木箱類型和玩家是否擁有金鑰匙來調整提示文本和顏色，以提供清晰的反饋和指引
        if extraction_pt:
            time_sec = extraction_timer // FPS
            mins, secs = time_sec // 60, time_sec % 60
            color = WHITE if time_sec > 30 else RED
            screen.blit(large_font.render(f"撤離倒數: {mins:02d}:{secs:02d}", True, color), (WIDTH//2 - 120, 20))
            if extract_progress > 0:
                pygame.draw.rect(screen, GRAY, (WIDTH//2 - 100, 110, 200, 15)); pygame.draw.rect(screen, GREEN, (WIDTH//2 - 100, 110, 200 * (extract_progress / 120), 15))
            if boss_army_active: screen.blit(large_font.render("警告：超時！狂暴大軍來襲！", True, RED), (WIDTH//2 - 220, 140))
        #根據Boss的狀態繪製Boss血量條，顯示Boss的名稱和當前血量百分比，並根據Boss的類型使用不同顏色的血量條，同時在Boss出現時顯示警告信息，提醒玩家注意即將到來的危險
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
    # 根據遊戲狀態繪製主選單界面，包含背景特效、遊戲標題、按鈕選項，以及根據玩家的互動狀態顯示相應的提示信息和更新日誌彈窗，提供一個吸引人且功能齊全的入口界面
    if game_state == "MENU":
        screen.fill(BLACK)
        for i in range(100):
            x, y = (i * 37) % WIDTH, (i * 23) % HEIGHT
            brightness = 100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)
        
        glow_color = (0, 100, 255, 50)
        glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        title = large_font.render("末日肉鴿生存?", True, BLUE)
        glow_surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -3), (0, 3), (-3, 0), (3, 0)]:
            glow_copy = glow_surface.copy(); glow_copy.fill(glow_color, special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(glow_copy, offset)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        screen.blit(font.render("末日肉鴿RPG?", True, WHITE), (WIDTH//2 - 120, HEIGHT//2 - 50))

        draw_hover_button(screen, start_button, "部署行動", (50, 150, 50), (100, 200, 100))
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

=======
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
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("末日肉鴿生存?")
clock = pygame.time.Clock()
FPS = 60

# World狀態
camera_x, camera_y = 0, 0
screen_shake = 0  

# 顏色定義
BLACK, BLUE, RED, YELLOW = (10, 10, 15), (0, 200, 255), (255, 20, 80), (255, 255, 0)
PURPLE, DARK_PURPLE, WHITE = (200, 50, 255), (138, 43, 226), (255, 255, 255)
GRAY, GREEN, ORANGE, CYAN = (100, 100, 110), (0, 255, 100), (255, 150, 0), (0, 255, 255)
SCRAP_COLOR = (200, 200, 200)

# 卡牌顏色與類型定義
CARD_COLOR = (30, 30, 40)
CARD_TYPE_COLORS = {"attack": (120, 35, 45), "support": (35, 75, 130), "life": (35, 110, 65)}
CARD_TYPE_LABELS = {"attack": "攻擊", "support": "支援", "life": "生命"}
SHIELD_COLOR, EXP_COLOR, HP_COLOR = (0, 150, 255), (124, 252, 0), (255, 50, 50)

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

# 圖片載入函式，從指定路徑載入圖片並且根據提供的大小進行縮放，如果檔案不存在或載入失敗則將該圖片設為 None，以便後續使用時進行檢查
def load_image(name, filename, size=None):
    try:
        path = os.path.join(IMAGE_DIR, filename)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            if size: img = pygame.transform.scale(img, size)
            images[name] = img
        else: images[name] = None
    except: images[name] = None

# 動畫載入函式，從指定資料夾載入一系列圖片作為動畫幀，並且根據提供的大小進行縮放，如果資料夾不存在或沒有有效圖片則將該動畫設為 None
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

# 載入子彈 (自訂的長寬比例)
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

# 音效和音樂系統，從 audio 資料夾讀取
def load_sound(name, filename):
    try:
        sound_path = os.path.join(AUDIO_DIR, filename) # 修改為 AUDIO_DIR
        if os.path.exists(sound_path):
            sounds[name] = pygame.mixer.Sound(sound_path)
            sounds[name].set_volume(0.3)
        else:
            sounds[name] = None
    except:
        sounds[name] = None 

# 載入基礎音效
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

# 載入專屬武器音效 (有專屬檔就讀，沒有就用基礎音效代替)
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

# 載入並播放背景音樂
bgm_path = os.path.join(AUDIO_DIR, "bgm.mp3")
if os.path.exists(bgm_path):
    pygame.mixer.music.load(bgm_path)
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(loops=-1)

# 音效控制函式
def play_sound(name, loop=0):
    if sounds.get(name): sounds[name].play(loops=loop)

def stop_sound(name):
    if sounds.get(name): sounds[name].stop()

################################################################################


# 繪製UI面板，包含標題、背景、邊框和分隔線，並且使用半透明效果讓底下的遊戲畫面隱約可見
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
# 繪製懸浮按鈕，根據滑鼠位置改變顏色和邊框，並且回傳是否正在懸浮
def draw_hover_button(surface, rect, text, base_color, hover_color, text_color=WHITE):
    m_pos = pygame.mouse.get_pos()
    is_hover = rect.collidepoint(m_pos)
    color = hover_color if is_hover else base_color
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, WHITE if is_hover else GRAY, rect, 2, border_radius=8)
    t_surf = font.render(text, True, text_color)
    surface.blit(t_surf, (rect.centerx - t_surf.get_width()//2, rect.centery - t_surf.get_height()//2))
    return is_hover
# 繪製物品提示框，根據物品類型顯示不同的資訊和樣式，並且自動調整位置避免超出螢幕邊界
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
# 繪製終端機面板，包含閃爍的邊框和動態變化的顏色，並且在面板上顯示圖示和文字
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
# 繪製迷你地圖，顯示玩家、Boss、撤離點和遺失物的位置，並且根據距離和狀態改變顏色和大小
def draw_minimap(surface):
    map_w, map_h = 160, 120
    m_rect = pygame.Rect(WIDTH - map_w - 20, 20, map_w, map_h)
    
    mm_surf = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
    pygame.draw.rect(mm_surf, (10, 10, 20, 180), mm_surf.get_rect(), border_radius=5)
    pygame.draw.rect(mm_surf, (50, 200, 50), mm_surf.get_rect(), 2, border_radius=5)
    surface.blit(mm_surf, (m_rect.x, m_rect.y))
    # 將遊戲內座標轉換為迷你地圖座標的函式
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
# 畫出Boss方向箭頭（當Boss在視野外時）
def draw_boss_direction_arrow(surface, boss_obj, cam_x, cam_y):
    if not boss_obj or (hasattr(boss_obj, "state") and boss_obj.state == "DEFEAT"): return
    boss_screen_x, boss_screen_y = boss_obj.x - cam_x, boss_obj.y - cam_y
    if 0 <= boss_screen_x <= WIDTH and 0 <= boss_screen_y <= HEIGHT: return

    center = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
    direction = pygame.math.Vector2(boss_screen_x - center.x, boss_screen_y - center.y)
    if direction.length_squared() == 0: return
    direction.normalize_ip()
    margin = 56
    scale_x = (WIDTH / 2 - margin) / abs(direction.x) if abs(direction.x) > 0.001 else float("inf")
    scale_y = (HEIGHT / 2 - margin) / abs(direction.y) if abs(direction.y) > 0.001 else float("inf")
    arrow_pos = center + direction * min(scale_x, scale_y)
    side = direction.rotate(90)
    tip = arrow_pos + direction * 25
    left = arrow_pos - direction * 18 + side * 15
    right = arrow_pos - direction * 18 - side * 15
    arrow_points = [(int(tip.x), int(tip.y)), (int(left.x), int(left.y)), (int(right.x), int(right.y))]
    pygame.draw.polygon(surface, BLACK, arrow_points); pygame.draw.polygon(surface, YELLOW, arrow_points, 0); pygame.draw.polygon(surface, RED, arrow_points, 3)
# 畫出遺失物方向箭頭（當遺失物在視野外且存在時）
def draw_lost_item_arrow(surface, cx, cy):
    if not ('lost_item' in globals() and lost_item): return
    dx, dy = lost_item.x - player.x, lost_item.y - player.y
    if math.sqrt(dx**2 + dy**2) > min(WIDTH, HEIGHT) * 0.4:
        angle = math.atan2(dy, dx)
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

# UI 介面全域變數與按鈕大小優化 (置中對齊與自適應)
shop_bg = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 300)
stash_bg = pygame.Rect(WIDTH//2 - 380, HEIGHT//2 - 250, 760, 500)
mod_bg = pygame.Rect(WIDTH//2 - 380, HEIGHT//2 - 250, 760, 500)
wep_stash_bg = pygame.Rect(WIDTH//2 - 380, HEIGHT//2 - 280, 760, 560)

s_start_x, s_start_y = WIDTH//2 - 350, HEIGHT//2 - 150
p_start_x_s, p_start_y_s = WIDTH//2 + 30, HEIGHT//2 - 150
p_start_x_m, p_start_y_m = WIDTH//2 - 320, HEIGHT//2 + 20
p_start_x_w, p_start_y_w = WIDTH//2 - 320, HEIGHT//2 + 100

rect_prim = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 150, 180, 60)
rect_sec = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 - 150, 180, 60)
upg_btn = pygame.Rect(WIDTH//2 + 100, HEIGHT//2 - 130, 200, 40)
reroll_btn = pygame.Rect(WIDTH//2 + 100, HEIGHT//2 - 70, 200, 40)

btn_prim_w = pygame.Rect(WIDTH//2 - 160, HEIGHT//2 + 220, 140, 40)
btn_sec_w = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 220, 140, 40)

cards = [pygame.Rect(WIDTH//2 - 350 + i*240, HEIGHT//2 - 150, 220, 320) for i in range(3)]
# 玩家背包格子位置
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
# 儲存格放置物品的函式，根據來源和目標更新玩家背包或一般儲藏室的物品，並且處理堆疊邏輯以確保相同類型的物品可以合併
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
# 開啟寶箱的函式，根據寶箱類型生成不同數量和種類的物品，並且在特定條件下添加特殊物品，最後播放獲得物品的音效
def open_chest(c):
    num_items = random.randint(2, 4) if c.type == "NORMAL" else random.randint(4, 7)
    for _ in range(num_items):
        rand_val = random.random()
        if rand_val < 0.2:
            items.append(DropItem(c.x + random.randint(-30, 30), c.y + random.randint(-30, 30), "MED"))
        elif rand_val < 0.5:
            items.append(DropItem(c.x + random.randint(-30, 30), c.y + random.randint(-30, 30), "SCRAP", random.randint(2, 5)))
        elif rand_val < 0.7:
            wep = generate_weapon(random.choice(list(WEAPON_TYPES.keys())), random.choices(["白", "藍", "紫", "金"], weights=[0.6, 0.3, 0.08, 0.02])[0])
            items.append(DropItem(c.x + random.randint(-30, 30), c.y + random.randint(-30, 30), "WEAPON", weapon_obj=wep))
        else:
            items.append(DropItem(c.x + random.randint(-30, 30), c.y + random.randint(-30, 30), "EXP", random.randint(1, 3)))
    if c.type == "LOCKED":
        items.append(DropItem(c.x, c.y + 20, "MAGNET"))
        items.append(DropItem(c.x, c.y - 20, "BOMB"))
    play_sound("exp")
# 更新日誌快取重建函式，當遊戲更新或修復後需要重新生成更新日誌的內容以供顯示
def rebuild_changelog_cache(w, h): pass 
# 繪製更新日誌彈窗，顯示修復和優化的內容，並且使用半透明面板和分行文字來呈現資訊
def draw_changelog_popup(surface):
    rect = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 200, 500, 400)
    draw_ui_panel(surface, rect, "更新與修復日誌", BLUE)
    logs = [
        "修復項目與優化內容:",
        "- 徹底修復：傷害數字與特效凍結在畫面的問題。",
        "- 徹底修復：敵人生成後不移動、不追蹤的問題。",
        "- 徹底修復：Boss 行為凍結的問題。",
        "- 修復缺圖片時槍枝消失，新增幾何備用繪製。",
        "- 小地圖改為戰術雷達風格，畫面更乾淨。",
        "- 成功撤離會完美保留所有狀態。",
    ]
    for i, line in enumerate(logs):
        surface.blit(small_font.render(line, True, WHITE), (rect.x + 20, rect.y + 60 + i * 30))
# 繪製暫停時的升級日誌，顯示玩家已獲得的強化內容，並且使用半透明面板和分行文字來呈現資訊
def draw_pause_upgrade_log(surface):
    draw_upgrade_summary(surface, WIDTH//2 - 120, HEIGHT//2 + 150, max_items=8, title="已獲得的強化")


# 升級選項定義，標題、描述、類型和權重等資訊，其中部分選項僅在特定遊戲模式下可用
# UI 升級卡牌完整資料 (共 25 種)
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
# 選擇升級卡牌的函式，根據權重隨機選擇三張可用的升級選項，並且將它們的索引存儲在全域變數中以供後續使用
def choose_upgrade_cards():
    global current_upgrade_choices, selected_upgrade_position
    available_indices = []
    weights = []
    for i, opt in enumerate(upgrade_options):
        if opt.get("challenge_only", False) and game_mode != "CHALLENGE":
            continue
        available_indices.append(i)
        weights.append(opt.get("weight", 1))
        
    chosen_indices = []
    while len(chosen_indices) < 3 and available_indices:
        idx = random.choices(available_indices, weights=weights, k=1)[0]
        chosen_indices.append(idx)
        remove_idx = available_indices.index(idx)
        available_indices.pop(remove_idx)
        weights.pop(remove_idx)
        
    current_upgrade_choices = chosen_indices
    selected_upgrade_position = None
# 應用升級效果的函式，根據選擇的升級選項更新玩家的屬性，並且將已選擇的升級記錄在全域變數中以供顯示
def apply_upgrade(idx, silent=False):
    global game_state, chosen_upgrades
    opt = upgrade_options[idx]
    found = False
    for u in chosen_upgrades:
        if u["title"] == opt["title"]:
            u["count"] += 1
            found = True
            break
    if not found:
        chosen_upgrades.append({"title": opt["title"], "count": 1})
    # 根據升級標題應用對應的效果，這裡使用一系列的條件判斷來更新玩家的屬性值
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
    
    if not silent:
        game_state = "PLAYING"
        play_sound("levelup")

# 全域變數定義，包含玩家的持久化屬性、作弊碼序列和按鍵緩衝區等資訊，以便在遊戲中使用和更新
persistent_stats = {"max_hp": 0, "dmg_bonus": 0, "speed_bonus": 0.0, "scrap": 0, "weapon_stash": [], "general_stash": [None]*36}
CHEAT_CODE = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_b, pygame.K_a, pygame.K_b, pygame.K_a]
key_buffer = []
# 武器類別定義，包含名稱、射擊延遲、子彈類型、傷害、音效名稱和後坐力等屬性，並且根據名稱載入對應的圖片資源
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
# 根據稀有度返回對應的顏色，金色、紫色、藍色和白色分別對應不同的RGB值，默認為灰色
def get_rarity_color(r):
    return {"金": (255, 215, 0), "紫": (200, 50, 255), "藍": (50, 150, 255)}.get(r, (200, 200, 200))
# 根據武器的基礎屬性、稀有度和詞綴來計算最終的傷害和射擊延遲，速射詞綴會大幅降低射擊延遲，而稀有度會增加傷害
def apply_weapon_stats(w):
    base = WEAPON_TYPES[w.base_name]
    w.damage = int(base.damage * {"白":1.0, "藍":1.3, "紫":1.6, "金":2.2}.get(w.rarity, 1.0))
    w.shoot_delay = max(2, int(base.shoot_delay * 0.60)) if "速射" in w.affixes else base.shoot_delay
# 根據武器的基礎類型和稀有度來生成一把新的武器，並且從動態詞綴池中隨機選擇一些詞綴來增加武器的特性，最後應用這些屬性來計算最終的傷害和射擊延遲
def generate_weapon(base_name, rarity="白"):
    base = WEAPON_TYPES[base_name]
    w = Weapon(base.base_name, base.shoot_delay, base.bullet_type, base.damage, base.sound_name, base.base_recoil)
    w.rarity = rarity
    c = {"白":0, "藍":1, "紫":2, "金":3}.get(rarity, 0)
    
    # 動態詞綴池：避開武器本身已有的特性，確保詞綴能「疊加」而不是浪費
    pool = ["速射", "散射", "吸血", "爆擊"]
    if base.bullet_type not in ["piercing", "laser", "cannon", "flamethrower"]:
        pool.append("穿透") # 本身不會穿透的武器才給穿透
    if base.bullet_type not in ["flamethrower", "flame_grenade"]:
        pool.append("燃燒") # 本身沒有火焰效果的才給燃燒
        
    w.affixes = random.sample(pool, min(c, len(pool))) if c > 0 else []
    apply_weapon_stats(w)
    return w
# 將武器儲藏室中的武器按照基礎類型、稀有度、詞綴數量和詞綴內容進行排序，確保同類型的武器會被歸類在一起，並且更稀有和更強力的武器會排在前面
def sort_weapon_stash():
    rv = {"白":0, "藍":1, "紫":2, "金":3}; order = list(WEAPON_TYPES.keys())
    persistent_stats["weapon_stash"].sort(key=lambda w: (order.index(w.base_name) if w.base_name in order else 99, -rv.get(w.rarity, 0), -len(w.affixes), "".join(sorted(w.affixes))))
# 根據物品的類型和屬性來計算它的出售價值，武器的價值取決於稀有度，醫療包和金鑰匙的價值取決於數量，其他物品則沒有價值
def get_sell_value(item):
    if not item: return 0
    if item.type == "WEAPON": return {"白":20, "藍":50, "紫":120, "金":300}.get(item.weapon_obj.rarity, 10)
    elif item.type == "MED": return 5 * item.count
    elif item.type == "KEY": return 30 * item.count
    return 0
# 物品類別定義，包含類型、名稱、數量、最大堆疊數量和武器對象等屬性，武器物品會包含一個對應的武器對象以供使用
class InvItem:
    def __init__(self, i_type, name, count, max_stack, weapon_obj=None):
        self.type, self.name, self.count, self.max_stack, self.weapon_obj = i_type, name, count, max_stack, weapon_obj
# 根據物品的類型和屬性來創建一個新的物品實例，廢料、急救包和金鑰匙有固定的名稱和最大堆疊數量，而武器則根據武器對象來設定名稱和屬性
def create_item(i_type, amount=1, weapon_obj=None):
    if i_type == "SCRAP": return InvItem("SCRAP", "廢料", amount, 999)
    elif i_type == "MED": return InvItem("MED", "急救包", amount, 5)
    elif i_type == "KEY": return InvItem("KEY", "金鑰匙", amount, 10)
    elif i_type == "WEAPON": return InvItem("WEAPON", weapon_obj.full_name, 1, 1, weapon_obj)
# 快速轉移物品的函式，嘗試將一個物品堆疊到目標列表中相同類型的物品上，如果無法完全堆疊則放到第一個空格中，返回是否成功轉移
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

# 粒子特效類別，包含位置、速度、計時器、大小和顏色等屬性，更新時會根據速度移動位置並減小大小，繪製時會根據剩餘時間和大小來呈現不同的效果
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vel_x, self.vel_y = random.uniform(-6, 6), random.uniform(-6, 6)
        self.timer, self.size, self.color = random.randint(15, 30), random.randint(4, 8), color

    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y
        self.timer -= 1
        self.size = max(0, self.size - 0.25)

    def draw(self, surface):
        if self.size > 0: 
            pygame.draw.rect(surface, self.color, (int(self.x - camera_x), int(self.y - camera_y), int(self.size), int(self.size)))

# 傷害數字類別，包含位置、傷害值、顏色、是否暴擊等屬性，更新時會向上移動並逐漸變淡，繪製時會根據傷害值和暴擊狀態來呈現不同的文字效果
class DamageText:
    def __init__(self, x, y, damage, color, is_crit=False):
        self.x, self.y = x, y
        self.damage = damage
        self.color = color
        self.is_crit = is_crit
        self.timer, self.vel_y, self.alpha = 40, -1.5, 255
        self.offset_x = random.randint(-15, 15)
        self.font = large_font if is_crit else small_font

    def update(self):
        self.y += self.vel_y
        self.timer -= 1
        self.alpha = max(0, int((self.timer / 40) * 255))

    def draw(self, surface):
        if self.timer > 0:
            text = f"-{int(self.damage)}" + ("!" if self.is_crit else "")
            txt_surf = self.font.render(text, True, self.color)
            txt_surf.set_alpha(self.alpha)
            surface.blit(txt_surf, (int(self.x + self.offset_x - camera_x - txt_surf.get_width()//2), int(self.y - camera_y)))

# 衝刺殘影類別，包含位置、大小和生命值等屬性，更新時會減少生命值，繪製時會根據剩餘生命值來呈現不同的透明度效果
class DashTrail:
    def __init__(self, x, y, size):
        self.x, self.y = x, y
        self.size = size
        self.life = 15
        
    def update(self):
        self.life -= 1
        
    def draw(self, surface):
        alpha = max(0, int((self.life / 15) * 150))
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 200, 255, alpha), (0, 0, self.size, self.size), border_radius=5)
        surface.blit(surf, (int(self.x - camera_x - self.size/2), int(self.y - camera_y - self.size/2)))

# 掉落物品類別，包含位置、類型、數量和武器對象等屬性，更新時會根據玩家位置和磁吸範圍來移動位置，繪製時會根據類型來呈現不同的圖像或幾何圖形
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
        if self.count > 1 and self.item_type in ["SCRAP", "MED", "KEY"]:
            surface.blit(tiny_font.render(str(self.count), True, WHITE), (draw_x + 5, int(float_y) + 5))

# 寶箱類別，包含位置、類型、狀態和開啟進度等屬性，更新時會根據玩家位置和開啟狀態來增加開啟進度，繪製時會根據狀態來呈現不同的圖像或幾何圖形
class Chest:
    def __init__(self, x, y, c_type="NORMAL"):
        self.x, self.y, self.type, self.state, self.open_progress = x, y, c_type, "CLOSED", 0
        self.rect, self.color = pygame.Rect(0, 0, 50, 40), (139, 69, 19) if c_type == "NORMAL" else (218, 165, 32)
    def draw(self, surface):
        draw_x, draw_y = int(self.x - camera_x), int(self.y - camera_y)
        self.rect.center = (draw_x, draw_y)
        
        # 優先讀取圖片，找不到才畫幾何圖形
        img_key = f"chest_{self.type}_{self.state}"
        img = images.get(img_key)
        
        if img:
            surface.blit(img, img.get_rect(center=(draw_x, draw_y)))
            # 開啟進度條仍保留繪製在圖片上方
            if self.state == "CLOSED" and self.open_progress > 0:
                pygame.draw.rect(surface, GRAY, (draw_x-25, draw_y-30, 50, 6))
                pygame.draw.rect(surface, GREEN, (draw_x-25, draw_y-30, 50*(self.open_progress/40), 6))
        else:
            # 幾何圖形備用方案
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

# 玩家遺失物品類別，包含位置、玩家等級、經驗值、升級選項、背包物品和武器等屬性，更新時會根據玩家位置來移動位置，繪製時會呈現一個閃爍的圓形和提示文字，讓玩家知道可以觸碰拾取
class PlayerLostItem:
    def __init__(self, x, y, level, exp, upgrades, inv_items, w1, w2):
        self.x, self.y, self.level, self.exp, self.upgrades = x, y, level, exp, upgrades
        self.inventory, self.w1, self.w2 = inv_items, w1, w2
        self.rect = pygame.Rect(0, 0, 50, 50)
        self.rect.center = (int(self.x), int(self.y))
    def draw(self, surface):
        self.rect.center = (int(self.x), int(self.y))
        draw_x, draw_y = int(self.x - camera_x), int(self.y - camera_y)
        p = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 5)
        pygame.draw.circle(surface, YELLOW, (draw_x, draw_y), 20 + p)
        pygame.draw.circle(surface, WHITE, (draw_x, draw_y), 22 + p, 2)
        txt = small_font.render(f"遺失物(觸碰拾取)", True, YELLOW)
        surface.blit(txt, (draw_x - txt.get_width()//2, draw_y - 35))

# 撤離點類別，包含位置和半徑等屬性，更新時不需要做任何事情，繪製時會呈現一個閃爍的圓形和提示文字，讓玩家知道這是撤離點
class ExtractionPoint:
    def __init__(self): self.x, self.y, self.radius = random.randint(800, MAP_WIDTH - 800), random.randint(800, MAP_HEIGHT - 800), 150
    def draw(self, surface):
        draw_x, draw_y = int(self.x - camera_x), int(self.y - camera_y)
        p = int(abs(math.sin(pygame.time.get_ticks() * 0.003)) * 20)
        pygame.draw.circle(surface, GREEN, (draw_x, draw_y), self.radius + p, 3)
        txt = font.render("撤離點", True, GREEN); surface.blit(txt, (draw_x - txt.get_width()//2, draw_y - 20))

# 模擬目標類別，包含位置、矩形、傷害記錄和震動計時器等屬性，更新時會清理過期的傷害記錄並減少震動計時器，繪製時會根據位置和傷害狀態來呈現一個矩形和傷害數字，並且在受到攻擊時產生震動效果
class DummyTarget:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.rect = pygame.Rect(0, 0, 40, 60)
        self.rect.center = (int(self.x), int(self.y)) # [修復] 初始化為世界座標
        self.hit_log = []
        self.shake_timer = 0
        
    def update(self):
        now = pygame.time.get_ticks()
        self.hit_log = [(t, dmg) for t, dmg in self.hit_log if now - t <= 3000]
        if self.shake_timer > 0: self.shake_timer -= 1
        # 確保碰撞框永遠鎖定在正確的世界座標上
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface):
        # 繪圖專用的螢幕座標 (加上受傷震動偏移)
        dx = int(self.x - camera_x) + (random.randint(-2,2) if self.shake_timer>0 else 0)
        dy = int(self.y - camera_y) + (random.randint(-2,2) if self.shake_timer>0 else 0)
        # 優先使用動畫或圖片，找不到才畫幾何圖形
        anim_frames = animations.get("dummy")
        if anim_frames:
            img = anim_frames[int(pygame.time.get_ticks() / 150) % len(anim_frames)]
            if self.shake_timer > 0:
                img = img.copy()
                img.fill((255, 100, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(img, img.get_rect(center=(dx, dy)))
        else:
            # 備用的幾何圖形畫法
            draw_rect = self.rect.copy()
            draw_rect.center = (dx, dy)
            pygame.draw.rect(surface, (150, 100, 80), draw_rect, border_radius=10)
            pygame.draw.circle(surface, RED, (dx, dy - 10), 8)
            pygame.draw.circle(surface, WHITE, (dx, dy - 10), 4)
        # 顯示DPS，計算最近3秒內的總傷害並除以3來獲得每秒傷害，根據DPS值來決定顏色，並且將文字繪製在模擬目標上方        
        total_dmg = sum(dmg for t, dmg in self.hit_log)
        dps = int(total_dmg / 3.0) if self.hit_log else 0
        dps_txt = small_font.render(f"DPS: {dps}", True, CYAN if dps > 0 else GRAY)
        surface.blit(dps_txt, (dx - dps_txt.get_width()//2, dy - 50))
# 玩家類別，包含位置、大小、矩形、武器、屬性、經驗值、等級、背包和升級等屬性，更新時會根據鍵盤輸入來移動位置和使用技能，並且處理衝刺、回血、能量恢復和升級等邏輯，繪製時會根據狀態來呈現玩家的圖像和相關資訊
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
        self.current_spread, self.bullet_count, self.bullet_spread, self.extra_same_path_bullets = 15.0, 1, 15.0, 0
        self.bullet_damage_bonus, self.shoot_delay_reduction, self.damage_reduction = persistent_stats["dmg_bonus"], 0, 0
        self.invincible_duration, self.guidance_level, self.aura_level, self.regen_level, self.regen_progress = 60, 0, 0, 0, 0
        self.exp_multiplier, self.magnet_radius, self.drone_level, self.drone_angle, self.drone_shoot_cd = 1.0, 80, 0, 0, 0
        self.dash_cost, self.is_dashing, self.dash_speed, self.dash_duration, self.dash_timer, self.dash_dir_x, self.dash_dir_y = 30, False, 28, 8, 0, 0, 0
        self.skill_cd, self.skill_max_cd, self.skill_cost = 0, 600, 50        
        self.invincible_timer, self.god_mode = 0, False 
        self.base_max_ammo, self.mag_size_bonus, self.reload_duration, self.reload_timer = 40, 0, 90, 0
        self.ammo = self.base_max_ammo

    @property 
    #這個方法用來計算玩家背包中所有廢料的總數量，通過遍歷背包中的物品並累加類型為"SCRAP"的物品數量來實現，方便在遊戲中顯示和使用廢料資源
    def scrap(self):
        return sum(i.count for i in self.inventory if i and i.type == "SCRAP")

    def add_item(self, new_item): return fast_transfer(new_item, self.inventory)
    def use_med(self):
        for i in range(24):
            item = self.inventory[i]
            if item and item.type == "MED" and self.hp < self.max_hp:
                self.hp = min(self.max_hp, self.hp + 40); item.count -= 1
                if item.count <= 0: self.inventory[i] = None
                play_sound("exp"); return True
        return False
    #這個方法用來處理玩家的移動和技能使用邏輯，首先根據鍵盤輸入來計算移動方向，然後處理衝刺、回血、能量恢復和升級等邏輯，最後根據位置和狀態來更新玩家的矩形和子彈散布等屬性，確保玩家在遊戲中能夠流暢地移動和使用技能
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
        #衝刺邏輯：當玩家按下空格或Q鍵並且有足夠的耐力時，啟動衝刺狀態，消耗耐力並設定衝刺方向和持續時間，在衝刺期間玩家會以更高的速度移動，並且在結束後恢復正常狀態
        if not self.is_dashing:
            if self.stamina < self.max_stamina: self.stamina = min(self.max_stamina, self.stamina + self.stamina_regen)
        if self.energy < self.max_energy: self.energy = min(self.max_energy, self.energy + self.energy_regen)

        if keys[pygame.K_SPACE] or keys[pygame.K_q]:
            if not self.is_dashing and self.stamina >= self.dash_cost:
                self.stamina -= self.dash_cost; self.is_dashing = True; self.dash_timer = self.dash_duration
                play_sound("dash")
                if dist > 0: self.dash_dir_x, self.dash_dir_y = move_x, move_y
                else:
                    mx, my = pygame.mouse.get_pos(); wx, wy = mx + camera_x, my + camera_y
                    dx, dy = wx - self.x, wy - self.y; ddist = math.sqrt(dx**2 + dy**2)
                    if ddist > 0: self.dash_dir_x, self.dash_dir_y = dx / ddist, dy / ddist
        #根據衝刺狀態來更新玩家的位置，如果正在衝刺則以更高的速度移動，並且減少衝刺計時器，當計時器結束後恢復正常狀態，如果沒有衝刺則根據移動方向和基礎速度來移動，最後根據位置和狀態來更新玩家的矩形和子彈散布等屬性，確保玩家在遊戲中能夠流暢地移動和使用技能
        if self.is_dashing:
            self.x += self.dash_dir_x * self.dash_speed; self.y += self.dash_dir_y * self.dash_speed
            self.dash_timer -= 1; 
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
        if self.current_spread > self.bullet_spread: self.current_spread = max(self.bullet_spread, self.current_spread - 0.5)
    #這個方法用來繪製玩家的圖像和相關資訊，首先根據無敵狀態來決定是否繪製玩家，然後根據武器動畫和鼠標位置來繪製玩家和武器的圖像，最後根據狀態來繪製衝刺殘影、護盾光環和無人機等特效，確保玩家在遊戲中能夠清晰地看到自己的角色和狀態
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
                mx, my = pygame.mouse.get_pos(); dx, dy = (mx + camera_x) - self.x, (my + camera_y) - self.y
                dist = math.sqrt(dx**2 + dy**2); dir_x, dir_y = (dx / dist, dy / dist) if dist > 0 else (1, 0)
                angle = math.degrees(math.atan2(-dy, dx))
                gun_img = images.get("gun_" + current_wep.base_name)
                
                if gun_img:
                    if dx < 0: gun_img = pygame.transform.flip(gun_img, False, True)
                    rotated_gun = pygame.transform.rotate(gun_img, angle)
                    offset_x, offset_y = dir_x * 15, dir_y * 15
                    surface.blit(rotated_gun, rotated_gun.get_rect(center=(int(self.x + offset_x - camera_x), int(self.y + offset_y - camera_y))))
                else:
                    end_x = self.x + dir_x * 25 - camera_x
                    end_y = self.y + dir_y * 25 - camera_y
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
            pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10)
            pygame.draw.circle(surface, (0, 180, 255), draw_rect.center, 95 + self.aura_level * 25 + pulse, 2)
            
        if self.drone_level > 0:
            drone_x, drone_y = draw_center[0] + math.cos(self.drone_angle) * 55, draw_center[1] + math.sin(self.drone_angle) * 55
            pygame.draw.circle(surface, (150, 200, 255), (int(drone_x), int(drone_y)), 10)
            pygame.draw.circle(surface, BLUE, (int(drone_x), int(drone_y)), 10, 2); pygame.draw.circle(surface, RED, (int(drone_x), int(drone_y)), 4)

#玩家發射的子彈，包含位置、方向、傷害、類型和特殊效果等屬性，更新時會根據導引等級來調整方向，並且根據類型來移動位置和處理爆炸等邏輯，繪製時會根據類型和暴擊狀態來呈現不同的圖像或幾何圖形，確保玩家在遊戲中能夠清晰地看到子彈的軌跡和效果
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

    #更新子彈的位置和狀態，首先根據導引等級來調整方向，然後根據類型來移動位置和處理爆炸等邏輯，最後更新矩形位置以便碰撞檢測，確保子彈在遊戲中能夠正確地移動和產生效果
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
    #繪製子彈的圖像，首先根據類型和暴擊狀態來決定使用哪個圖像或幾何圖形來繪製子彈，然後根據位置和攝像機偏移來計算繪製位置，最後將圖像或幾何圖形繪製到屏幕上，確保玩家在遊戲中能夠清晰地看到子彈的軌跡和效果
    def draw(self, surface):
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        img = images.get("bullet_" + self.b_type)
        if img: surface.blit(pygame.transform.rotate(img, math.degrees(math.atan2(-self.dir_y, self.dir_x))), img.get_rect(center=draw_center))
        else: pygame.draw.circle(surface, self.color, draw_center, self.radius)
        if self.is_crit: pygame.draw.circle(surface, RED, draw_center, self.radius+2, 1)
#敵人類別，包含位置、大小、生命值、攻擊方式和特殊效果等屬性，更新時會根據玩家位置來移動和攻擊，並且處理冰凍、燃燒和其他狀態效果的邏輯，繪製時會根據狀態來呈現不同的圖像或幾何圖形，確保玩家在遊戲中能夠清晰地看到敵人的位置和狀態
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
        
        # 飛彈壽命與爆炸標記 (追蹤彈壽命約 2.5 秒，一般子彈無限)
        self.lifespan = 150 if is_homing else 9999 
        self.explode = False

    def update(self, target_x=None, target_y=None):
        # [新增] 壽命衰減判定
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.explode = True
            return

        if self.is_homing and target_x is not None and target_y is not None:
            tx, ty = target_x - self.x, target_y - self.y
            dist = math.sqrt(tx**2 + ty**2)
            if dist > 0:
                # 飛彈越快沒燃料，追蹤轉向能力就越差，讓玩家更好閃避
                turn_speed = 0.045 * (self.lifespan / 150)
                self.dir_x = self.dir_x * (1 - turn_speed) + (tx / dist) * turn_speed
                self.dir_y = self.dir_y * (1 - turn_speed) + (ty / dist) * turn_speed
                ndist = math.sqrt(self.dir_x**2 + self.dir_y**2)
                if ndist > 0: self.dir_x /= ndist; self.dir_y /= ndist
                
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))
    #繪製敵人子彈的圖像，首先根據類型和追蹤狀態來決定使用哪個圖像或幾何圖形來繪製子彈，然後根據位置和攝像機偏移來計算繪製位置，最後將圖像或幾何圖形繪製到屏幕上，確保玩家在遊戲中能夠清晰地看到敵人子彈的軌跡和效果
    def draw(self, surface): 
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        pygame.draw.circle(surface, self.color, draw_center, self.radius)
#敵人類別，包含位置、大小、生命值、攻擊方式和特殊效果等屬性，更新時會根據玩家位置來移動和攻擊，並且處理冰凍、燃燒和其他狀態效果的邏輯，繪製時會根據狀態來呈現不同的圖像或幾何圖形，確保玩家在遊戲中能夠清晰地看到敵人的位置和狀態
class Enemy:
    def __init__(self, level, is_elite=False, spawn_x=MAP_WIDTH/2, spawn_y=MAP_HEIGHT/2):
        self.is_elite, self.size = is_elite, 35 if is_elite else 25
        difficulty_mult = 1.75 if game_mode == "CHALLENGE" else 1.0
        self.speed = ((random.uniform(3.0, 5.5) if is_elite else random.uniform(2.5, 4.5)) + level * 0.05) * (1.2 if game_mode == "CHALLENGE" else 1.0)
        self.max_hp = int(((60 + level * 25) if is_elite else (20 + level * 8)) * difficulty_mult)
        self.hp, self.max_shield = self.max_hp, int(((20 + level * 8) if is_elite else (10 + level * 4)) * difficulty_mult)
        self.shield, self.damage = self.max_shield, int(((35 + level * 3) if is_elite else (15 + level * 1.5)) * difficulty_mult)
        self.frost_timer, self.burn_timer, self.dir_x, self.dir_y = 0, 0, 1, 0  
        
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
        
        # 畫面邊緣包圍生成邏輯
        spawn_dist_x = WIDTH / 2 + 50
        spawn_dist_y = HEIGHT / 2 + 50
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top': 
            self.x = spawn_x + random.randint(-int(spawn_dist_x), int(spawn_dist_x))
            self.y = spawn_y - spawn_dist_y
        elif edge == 'bottom': 
            self.x = spawn_x + random.randint(-int(spawn_dist_x), int(spawn_dist_x))
            self.y = spawn_y + spawn_dist_y
        elif edge == 'left': 
            self.x = spawn_x - spawn_dist_x
            self.y = spawn_y + random.randint(-int(spawn_dist_y), int(spawn_dist_y))
        elif edge == 'right': 
            self.x = spawn_x + spawn_dist_x
            self.y = spawn_y + random.randint(-int(spawn_dist_y), int(spawn_dist_y))
            
        self.x = max(0, min(self.x, MAP_WIDTH))
        self.y = max(0, min(self.y, MAP_HEIGHT))
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = (int(self.x), int(self.y))
    #更新敵人的位置和狀態，首先根據玩家位置來計算移動方向，然後根據攻擊方式來決定移動和攻擊的行為，最後處理冰凍、燃燒和其他狀態效果的邏輯，確保敵人在遊戲中能夠正確地追蹤玩家並產生攻擊行為
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
    #繪製敵人的圖像，首先根據狀態來決定使用哪個圖像或幾何圖形來繪製敵人，然後根據位置和攝像機偏移來計算繪製位置，最後將圖像或幾何圖形繪製到屏幕上，確保玩家在遊戲中能夠清晰地看到敵人的位置和狀態
    def draw(self, surface):
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        draw_rect = self.rect.copy(); draw_rect.center = draw_center
        
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
                if self.dir_x < 0: img = pygame.transform.flip(img, True, False)
                if self.frost_timer > 0:
                    img = img.copy(); img.fill((100, 200, 255, 100), special_flags=pygame.BLEND_RGBA_MULT)
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
            
            if self.dir_x != 0 or self.dir_y != 0:
                angle = math.atan2(self.dir_y, self.dir_x)
                if self.combat_type == "melee":
                    swing = math.sin(pygame.time.get_ticks() * 0.015) * 0.8; draw_angle = angle + swing
                    end_x, end_y = draw_center[0] + math.cos(draw_angle) * (self.size * 1.0), draw_center[1] + math.sin(draw_angle) * (self.size * 1.0)
                    pygame.draw.line(surface, (220, 220, 220), draw_center, (end_x, end_y), 4)
                    h_x, h_y = draw_center[0] + math.cos(draw_angle) * (self.size * 0.3), draw_center[1] + math.sin(draw_angle) * (self.size * 0.3)
                    p_angle = draw_angle + math.pi / 2
                    pygame.draw.line(surface, (150, 100, 50), (h_x + math.cos(p_angle)*6, h_y + math.sin(p_angle)*6), (h_x - math.cos(p_angle)*6, h_y - math.sin(p_angle)*6), 3)
                elif self.combat_type == "ranged":
                    end_x, end_y = draw_center[0] + math.cos(angle) * (self.size * 0.8), draw_center[1] + math.sin(angle) * (self.size * 0.8)
                    pygame.draw.line(surface, (80, 80, 80), draw_center, (end_x, end_y), 6); pygame.draw.circle(surface, ORANGE, (int(end_x), int(end_y)), 3)

        if self.max_shield > 0 and self.shield > 0:
            pygame.draw.rect(surface, GRAY, (draw_rect.x, draw_rect.y - 14, self.size, 4))
            pygame.draw.rect(surface, (0, 150, 255), (draw_rect.x, draw_rect.y - 14, self.size * (max(0, self.shield)/self.max_shield), 4))
        if self.hp < self.max_hp:
            pygame.draw.rect(surface, GRAY, (draw_rect.x, draw_rect.y - 8, self.size, 4))
            pygame.draw.rect(surface, GREEN, (draw_rect.x, draw_rect.y - 8, self.size * (max(0, self.hp)/self.max_hp), 4))
#Boss類別，包含位置、大小、生命值、攻擊方式和特殊效果等屬性，更新時會根據玩家位置來移動和攻擊，並且處理冰凍、燃燒和其他狀態效果的邏輯，繪製時會根據狀態來呈現不同的圖像或幾何圖形，確保玩家在遊戲中能夠清晰地看到Boss的存在和威脅
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
        
        if self.b_type == "YELLOW": self.color, self.speed, self.state = YELLOW, 3.0, "EVADE"
        elif self.b_type == "RED": self.color, self.speed, self.state, self.aim_x, self.aim_y = RED, 2.5, "CHASE", 0, 0
        elif self.b_type == "PURPLE": self.color, self.speed, self.state = PURPLE, 2.0, "FLEE"
        elif self.b_type == "CYAN": self.color, self.speed, self.state = CYAN, 3.0, "IDLE"
    #更新Boss的位置和狀態，首先根據玩家位置來計算移動方向，然後根據攻擊模式來決定移動和攻擊的行為，最後處理冰凍、燃燒和其他狀態效果的邏輯，確保Boss在遊戲中能夠正確地追蹤玩家並產生攻擊行為
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
        tang_x, tang_y = -dir_y, dir_x
        #根據不同的Boss類型和狀態來決定行為模式，黃色Boss會在閃避和攻擊之間切換，紅色Boss會追蹤玩家並進行衝刺攻擊，紫色Boss會在逃跑和召喚小怪之間切換，青色Boss會在移動和射擊之間切換，確保每個Boss都有獨特的行為模式和挑戰性
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
    #繪製Boss的圖像，首先根據狀態來決定使用哪個圖像或幾何圖形來繪製Boss，然後根據位置和攝像機偏移來計算繪製位置，最後將圖像或幾何圖形繪製到屏幕上，確保玩家在遊戲中能夠清晰地看到Boss的存在和威脅
    def draw(self, surface):
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        anim_key = "boss_" + self.b_type
        anim_frames = animations.get(anim_key)
        if anim_frames:
            img = anim_frames[int(pygame.time.get_ticks() / 150) % len(anim_frames)]
            surface.blit(img, img.get_rect(center=draw_center))
        else:
            c = (100, 200, 255) if self.frost_timer > 0 else self.color
            if self.b_type == "CYAN":
                pts = [(draw_center[0], draw_center[1] - self.size), (draw_center[0] + self.size, draw_center[1]), (draw_center[0], draw_center[1] + self.size), (draw_center[0] - self.size, draw_center[1])]
                pygame.draw.polygon(surface, c, pts); pygame.draw.polygon(surface, WHITE, pts, 3)
            else: pygame.draw.rect(surface, c, self.rect.copy().move(-camera_x, -camera_y))
        
        if self.b_type == "YELLOW":
            if self.state == "EVADE": pygame.draw.circle(surface, WHITE, draw_center, int(self.size/2) + 15, 3)
            elif self.state == "CHARGE": pygame.draw.circle(surface, RED, draw_center, int(self.size/2) + max(0, 30 - int(self.state_timer / 2)), 2)
        elif self.b_type == "RED" and self.state == "WARN": pygame.draw.line(surface, RED, draw_center, (int(self.aim_x - camera_x), int(self.aim_y - camera_y)), max(1, int(self.state_timer / 8)))
        elif self.b_type == "PURPLE" and self.state == "SUMMON": pygame.draw.circle(surface, DARK_PURPLE, draw_center, int(self.size/2) + min(60, self.state_timer), 3)
        elif self.b_type == "CYAN" and self.state == "FIRE": pygame.draw.circle(surface, CYAN, draw_center, int(self.size/2) + 20, 4)

# 遊戲全域狀態與事件系統
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
#進入掩體，重置遊戲狀態並根據是否成功完成突襲來處理獎勵和懲罰，確保玩家在每次進入掩體時都能夠有一個清晰的起點和適當的獎勵機制
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

    player.hp = player.max_hp
    player.shield = player.max_shield
    player.ammo = player.base_max_ammo + player.mag_size_bonus
    
    bullets.clear(); bunker_bullets.clear(); enemy_bullets.clear(); enemies.clear()
    particles.clear(); items.clear(); trails.clear(); damage_texts.clear(); chests.clear()
    boss = None; boss_active = False
    shoot_cooldown, magnet_timer, screen_flash_timer = 0, 0, 0
    boss_army_active, extraction_timer, extraction_pt, extract_progress = False, 15*60*FPS, None, 0
    enemy_spawn_timer = 0
    
    player.x, player.y = MAP_WIDTH//2, MAP_HEIGHT//2
    game_state = "BUNKER"
    stop_sound("boss_bgm")
#開始突襲，重置遊戲狀態並生成敵人和寶箱，確保玩家在每次開始突襲時都能夠有一個清晰的起點和適當的挑戰機制
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
    extract_progress = 0
    boss_army_active = False
    boss_active, boss = False, None
    enemy_spawn_timer = 10 
    for _ in range(15): chests.append(Chest(random.randint(400, MAP_WIDTH-400), random.randint(400, MAP_HEIGHT-400), "NORMAL"))
    for _ in range(5): chests.append(Chest(random.randint(400, MAP_WIDTH-400), random.randint(400, MAP_HEIGHT-400), "LOCKED"))
    play_sound("boss_bgm", loop=-1)
#完全重置遊戲狀態，清除所有進度和獎勵，並返回主菜單，確保玩家在選擇重新開始遊戲時能夠有一個全新的體驗
def full_wipe(mode="NORMAL"):
    global player, game_mode, chosen_upgrades, lost_item, defeated_boss_levels
    game_mode = mode
    player = Player()
    chosen_upgrades.clear()
    lost_item = None
    defeated_boss_levels.clear()
    enter_bunker(success=False)


# 遊戲啟動與主迴圈，處理遊戲的主要邏輯和事件，包括玩家輸入、遊戲狀態更新、敵人行為、碰撞檢測和繪製等

full_wipe("NORMAL")
game_state = "MENU"
dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); dim_surface.fill((0, 0, 0, 180))
#這一行代碼設置了一個布爾變量running為True，這個變量用於控制遊戲主循環的運行狀態。
#當running為True時，遊戲主循環會繼續執行，處理玩家輸入、更新遊戲狀態、繪製圖像等；當running被設置為False時，主循環將停止，遊戲將結束並退出
running = True 
#定義遊戲中各種按鈕的矩形區域，主菜單、難度選擇、商店、庫存和其他界面
#分別是開始遊戲、查看更新日誌、退出遊戲、選擇普通模式、選擇挑戰模式、難度選擇界面的返回按鈕、更新日誌界面的關閉按鈕、商店界面中升級生命值、傷害和速度的按鈕，以及商店、庫存、武器和模組界面的關閉按鈕、顯示升級選項的列表區域和確認升級的按鈕
#按鈕的x坐標、y坐標、寬度和高度
start_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 20, 220, 50)
changelog_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 100, 220, 50)
exit_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 180, 220, 50)
normal_button = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 - 60, 210, 230)
challenge_button = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 - 60, 210, 230)
difficulty_back_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 200, 220, 50)
changelog_close_button = pygame.Rect(WIDTH//2 + 300, HEIGHT//2 - 200, 40, 40)
shop_buttons = {"hp": pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 80, 140, 40), "dmg": pygame.Rect(WIDTH//2 + 10, HEIGHT//2 - 80, 140, 40), "spd": pygame.Rect(WIDTH//2 - 150, HEIGHT//2 - 25, 140, 40)}
btn_hp, btn_dmg, btn_spd = shop_buttons["hp"], shop_buttons["dmg"], shop_buttons["spd"]
btn_shop_close = pygame.Rect(WIDTH//2 + 260, HEIGHT//2 - 230, 60, 60)
btn_stash_close = pygame.Rect(WIDTH//2 + 260, HEIGHT//2 - 230, 60, 60)
btn_wep_close = pygame.Rect(WIDTH//2 + 260, HEIGHT//2 - 230, 60, 60)
btn_mod_close = pygame.Rect(WIDTH//2 + 260, HEIGHT//2 - 230, 60, 60)
list_rect = pygame.Rect(WIDTH//2 - 280, HEIGHT//2 - 200, 560, 300)
confirm_upgrade_button = pygame.Rect(WIDTH//2 - 50, HEIGHT//2 + 230, 100, 50)

while running:
    if 'lost_item' in globals() and lost_item:
        try: lost_item.rect.center = (int(lost_item.x), int(lost_item.y))
        except Exception: pass
    m_x, m_y = pygame.mouse.get_pos()
    m_pos = (m_x, m_y)
    hovered_slot_info = None 

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
                player = Player()
                chosen_upgrades.clear()
                enter_bunker(success=False)
            
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
        #庫存界面，處理玩家與庫存物品的交互，包括拖放物品、快速轉移物品和關閉庫存界面等，確保玩家在管理庫存時能夠有一個流暢和直觀的體驗
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
            #拖放物品到庫存或玩家背包，首先檢查鼠標位置是否在庫存格子或玩家背包格子上，如果是，則嘗試將物品放入對應的格子中，如果放入成功，則從原位置移除物品；如果放入失敗，則將物品放回原位置；如果鼠標位置不在任何格子上，則將物品丟棄在玩家當前位置，並從原位置移除物品；最後重置拖動狀態
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
        #主菜單界面，處理玩家在主菜單上的點擊事件，包括開始遊戲、查看更新日誌和退出遊戲等選項，確保玩家在進入遊戲前能夠有一個清晰的選擇界面
        elif game_state == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if show_changelog:
                    if changelog_close_button.collidepoint(event.pos): show_changelog, changelog_scroll = False, 0
                else:
                    if start_button.collidepoint(event.pos): game_state = "DIFFICULTY"
                    elif changelog_button.collidepoint(event.pos): show_changelog, changelog_scroll = True, 0; rebuild_changelog_cache(640, 380)
                    elif exit_button.collidepoint(event.pos): running = False
        #難度選擇界面，處理玩家在難度選擇界面上的點擊事件，包括選擇普通模式、挑戰模式和返回主菜單等選項，確保玩家在開始遊戲前能夠有一個清晰的難度選擇界面
        elif game_state == "DIFFICULTY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if normal_button.collidepoint(event.pos): full_wipe("NORMAL")
                elif challenge_button.collidepoint(event.pos): full_wipe("CHALLENGE")
                elif difficulty_back_button.collidepoint(event.pos): game_state = "MENU"
        #掩體界面，處理玩家在掩體內的交互事件，包括進入突襲、進入商店、進入庫存、進入模組工作台和進入武器庫等選項，確保玩家在掩體內能夠有一個清晰的交互界面和適當的獎勵機制
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
        #商店界面，處理玩家在商店內的交互事件，包括購買升級、關閉商店等選項，確保玩家在商店內能夠有一個清晰的交互界面和適當的獎勵機制
        elif game_state == "SHOP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_hp.collidepoint(event.pos) and persistent_stats["scrap"] >= 50:
                    persistent_stats["scrap"] -= 50; persistent_stats["max_hp"] += 10; player.max_hp += 10; player.hp += 10; play_sound("levelup")
                elif btn_dmg.collidepoint(event.pos) and persistent_stats["scrap"] >= 50:
                    persistent_stats["scrap"] -= 50; persistent_stats["dmg_bonus"] += 2; player.bullet_damage_bonus += 2; play_sound("levelup")
                elif btn_spd.collidepoint(event.pos) and persistent_stats["scrap"] >= 50:
                    persistent_stats["scrap"] -= 50; persistent_stats["speed_bonus"] += 0.2; player.base_speed += 0.2; play_sound("levelup")
                elif btn_shop_close.collidepoint(event.pos): game_state = "BUNKER"
        #武器庫界面，處理玩家在武器庫內的交互事件，包括選擇武器、裝備武器、出售武器和關閉武器庫等選項，確保玩家在武器庫內能夠有一個清晰的交互界面和適當的獎勵機制
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
            #右鍵點擊武器庫中的武器或玩家背包中的武器，首先檢查鼠標位置是否在武器庫列表區域內，如果是，則計算出被點擊的武器索引，並嘗試將該武器添加到玩家背包中，如果添加成功，則從武器庫中移除該武器；如果鼠標位置不在武器庫列表區域內，則檢查是否點擊了玩家背包中的武器，如果是，則嘗試將該武器添加到武器庫中，如果添加成功，則從玩家背包中移除該武器；最後更新武器庫列表和播放相應的聲音效果    
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
                    rect = pygame.Rect(p_start_x_w + (i%11)*58, p_start_y_w + (i//11)*58, 50, 50)
                    item = player.inventory[i]
                    if rect.collidepoint(event.pos) and item and item.type == "WEAPON":
                        persistent_stats["weapon_stash"].append(item.weapon_obj)
                        player.inventory[i] = None; sort_weapon_stash()
                        arsenal_weapons_list = [generate_weapon(n, "白") for n in WEAPON_TYPES] + persistent_stats["weapon_stash"]; play_sound("exp")
        #改造台界面，處理玩家在改造台內的交互事件，包括選擇武器、升級武器、重置詞綴和關閉改造台等選項，確保玩家在改造台內能夠有一個清晰的交互界面和適當的獎勵機制
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
                            
                            # 改造台套用動態詞綴池
                            pool = ["速射", "散射", "吸血", "爆擊"]
                            if selected_mod_weapon.bullet_type not in ["piercing", "laser", "cannon", "flamethrower"]: pool.append("穿透")
                            if selected_mod_weapon.bullet_type not in ["flamethrower", "flame_grenade"]: pool.append("燃燒")
                            selected_mod_weapon.affixes = random.sample(pool, min({"白":0, "藍":1, "紫":2, "金":3}[selected_mod_weapon.rarity], len(pool)))
                            
                            apply_weapon_stats(selected_mod_weapon); play_sound("levelup")
                      #重置詞綴按鈕被點擊，且選中的武器稀有度不為白色，首先根據武器的稀有度計算重置詞綴的成本，如果玩家的碎片數量足夠支付成本，則從玩家的碎片中扣除相應的數量，然後根據武器的類型動態生成一個新的詞綴池，從中隨機選擇適合該武器稀有度的詞綴數量，最後將選中的詞綴應用到武器上並播放相應的聲音效果      
                    if reroll_btn.collidepoint(event.pos) and selected_mod_weapon.rarity != "白":
                        cost = {"藍":30, "紫":80, "金":150}[selected_mod_weapon.rarity]
                        if persistent_stats["scrap"] >= cost:
                            persistent_stats["scrap"] -= cost
                            
                            # 動態詞綴池
                            pool = ["速射", "散射", "吸血", "爆擊"]
                            if selected_mod_weapon.bullet_type not in ["piercing", "laser", "cannon", "flamethrower"]: pool.append("穿透")
                            if selected_mod_weapon.bullet_type not in ["flamethrower", "flame_grenade"]: pool.append("燃燒")
                            selected_mod_weapon.affixes = random.sample(pool, min({"白":0, "藍":1, "紫":2, "金":3}[selected_mod_weapon.rarity], len(pool)))
                            
                            apply_weapon_stats(selected_mod_weapon); play_sound("exp")
        #暫停界面，處理玩家在暫停界面上的交互事件，包括繼續遊戲、進入掩體、重新開始和退出遊戲等選項，確保玩家在暫停遊戲時能夠有一個清晰的選擇界面和適當的獎勵機制
        elif game_state == "PAUSED":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 10, 220, 50).collidepoint(event.pos): game_state = "PLAYING"
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 10, 220, 50).collidepoint(event.pos): enter_bunker(success=False)
                elif pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 80, 220, 50).collidepoint(event.pos): full_wipe("NORMAL")
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 80, 220, 50).collidepoint(event.pos): running = False
        #升級界面，處理玩家在升級界面上的交互事件，包括選擇升級和確認升級等選項，確保玩家在升級時能夠有一個清晰的選擇界面和適當的獎勵機制
        elif game_state == "LEVEL_UP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selected_upgrade_position is not None and confirm_upgrade_button.collidepoint(event.pos): apply_upgrade(current_upgrade_choices[selected_upgrade_position])
                else:
                    for i, card in enumerate(cards):
                        if i < len(current_upgrade_choices) and card.collidepoint(event.pos): selected_upgrade_position = i; break

    # 遊戲邏輯更新
    if game_state == "BUNKER":
        bunker_clamp = pygame.Rect(MAP_WIDTH//2 - 400, MAP_HEIGHT//2 - 300, 800, 600)
        player.update(clamp_rect=bunker_clamp)
        camera_x, camera_y = MAP_WIDTH//2 - WIDTH/2, MAP_HEIGHT//2 - HEIGHT/2

        if bunker_dummy: bunker_dummy.update()
        mouse_btns = pygame.mouse.get_pressed()
        if mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing:
            wep = player.weapons[player.current_weapon_idx]
            base_dir = pygame.math.Vector2((m_x + camera_x) - player.x, (m_y + camera_y) - player.y)
            if base_dir.length() > 0: base_dir.normalize_ip()
            else: base_dir = pygame.math.Vector2(1, 0)
            
            player.current_spread = min(player.bullet_spread + 25.0, player.current_spread + wep.base_recoil)
            t_bullets = player.bullet_count + (4 if wep.bullet_type == "shotgun" else 0) + (2 if "散射" in wep.affixes else 0)
            s_angle = -(t_bullets - 1) * player.current_spread / 2
            
            if wep.bullet_type in ["cannon", "flame_grenade"]: screen_shake = 5
            elif wep.bullet_type == "shotgun": screen_shake = 2

            for i in range(t_bullets):
                s_dir = base_dir.rotate(s_angle + i * player.current_spread)
                for j in range(1 + player.extra_same_path_bullets):
                    off = s_dir * (j * 15)
                    tx, ty = player.x + s_dir.x * 100 + off.x, player.y + s_dir.y * 100 + off.y
                    if wep.bullet_type == "flamethrower": tx += random.randint(-40, 40); ty += random.randint(-40, 40)
                    bunker_bullets.append(Bullet(player.rect.centerx + off.x, player.rect.centery + off.y, tx, ty, wep, player.guidance_level, player.bullet_damage_bonus))
            shoot_cooldown = wep.shoot_delay
            play_sound(wep.sound_name)
        # 更新子彈位置，檢查與掩體Dummy的碰撞，處理傷害、擊打反饋和子彈壽命，確保子彈在遊戲中有適當的行為和反應
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
    #遊戲主循環，根據當前的遊戲狀態更新遊戲邏輯，包括玩家移動、敵人生成和行為、子彈更新、物品交互和界面交互等，確保遊戲在不同狀態下有適當的行為和反應
    elif game_state == "PLAYING" and not show_inventory:
        
        if enemy_spawn_timer > 0: enemy_spawn_timer -= 1
        if enemy_spawn_timer <= 0 and not boss_army_active:
            if len(enemies) < 150: 
                enemies.append(Enemy(player.level, random.random() < 0.15, player.x, player.y))
            enemy_spawn_timer = max(5, 30 - player.level) 
            
        shake_x = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
        shake_y = random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0
        if screen_shake > 0: screen_shake -= 1

        camera_x = max(0, min(MAP_WIDTH - WIDTH, player.x - WIDTH / 2)) + shake_x
        camera_y = max(0, min(MAP_HEIGHT - HEIGHT, player.y - HEIGHT / 2)) + shake_y
        
        if magnet_timer > 0: magnet_timer -= 1
        if screen_flash_timer > 0: screen_flash_timer -= 1
        # 更新敵人行為，處理與玩家的互動，生成子彈和掉落物，並管理敵人的生命週期，確保遊戲中的敵人有適當的挑戰性和反應
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
            # 處理開寶箱邏輯
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
                            
            # 撿起地上物資 (廢料、鑰匙、補血包、槍枝)
            for g in items[:]:
                if g.item_type not in ["EXP", "MAGNET", "BOMB", "SHIELD"] and math.hypot(player.x - g.x, player.y - g.y) < 70:
                    if g.item_type == "WEAPON":
                        new_item = create_item("WEAPON", 1, g.weapon_obj)
                    else:
                        new_item = create_item(g.item_type, g.count)
                    
                    # 判斷背包是否已滿，如果有空間則放入並刪除地上掉落物
                    if player.add_item(new_item):
                        items.remove(g)
                        play_sound("exp")
        else:
            for c in chests:
                if c.state == "CLOSED": c.open_progress = max(0, c.open_progress - 2)

        if player.exp >= player.max_exp:
            player.exp -= player.max_exp
            player.level += 1; player.max_exp = int(player.max_exp * 1.25)
            choose_upgrade_cards(); game_state = "LEVEL_UP"; play_sound("levelup") 
        # 每5級出現一個BOSS，且不會在同一關重複出現同一個BOSS
        if player.level % 5 == 0 and player.level > 0 and player.level not in defeated_boss_levels and not boss_active and not boss_army_active:
            boss = Boss(random.choice(["YELLOW", "RED", "PURPLE", "CYAN"]), player.level, player.x, player.y)
            boss_active = True; play_sound("boss_bgm", loop=-1) 

        mouse_btns = pygame.mouse.get_pressed()
        world_mouse_x, world_mouse_y = m_x + camera_x, m_y + camera_y
        current_wep = player.weapons[player.current_weapon_idx]
        # 處理玩家射擊邏輯，根據玩家當前武器、彈藥、冷卻時間和其他狀態決定是否可以射擊，生成子彈並應用相應的效果和反饋
        if mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing:
            can_fire = True
            if game_mode == "CHALLENGE":
                if player.ammo <= 0: can_fire = False; player.reload_timer = player.reload_duration if player.reload_timer <= 0 else player.reload_timer
                else: player.ammo -= 1; player.reload_timer = player.reload_duration if player.ammo <= 0 else player.reload_timer
            # 霰彈槍和火焰噴射器在彈藥耗盡後可以繼續射擊，但射擊效果會受到影響，霰彈槍會減少散射彈數，火焰噴射器會減少射程和傷害
            if can_fire:
                base_dir = pygame.math.Vector2(world_mouse_x - player.x, world_mouse_y - player.y)
                if base_dir.length() > 0: base_dir.normalize_ip()
                else: base_dir = pygame.math.Vector2(1, 0)
                
                player.current_spread = min(player.bullet_spread + 25.0, player.current_spread + current_wep.base_recoil)
                t_bullets = player.bullet_count + (4 if current_wep.bullet_type == "shotgun" else 0) + (2 if "散射" in current_wep.affixes else 0)
                s_angle = -(t_bullets - 1) * player.current_spread / 2
            # 根據武器類型應用不同的屏幕震動效果，火炮和榴彈會有較強的震動，而霰彈槍會有較弱的震動，確保射擊時有適當的視覺反饋
                if current_wep.bullet_type in ["cannon", "flame_grenade"]: screen_shake = 5
                elif current_wep.bullet_type == "shotgun": screen_shake = 2

                for i in range(t_bullets):
                    s_dir = base_dir.rotate(s_angle + i * player.current_spread)
                    for j in range(1 + player.extra_same_path_bullets):
                        spawn_offset = s_dir * (j * 15) 
                        tx, ty = player.x + s_dir.x * 100 + spawn_offset.x, player.y + s_dir.y * 100 + spawn_offset.y
                        if current_wep.bullet_type == "flamethrower": tx += random.randint(-40, 40); ty += random.randint(-40, 40)
                        bullets.append(Bullet(player.rect.centerx + spawn_offset.x, player.rect.centery + spawn_offset.y, tx, ty, current_wep, player.guidance_level, player.bullet_damage_bonus))
                shoot_cooldown = max(2, current_wep.shoot_delay - player.shoot_delay_reduction)
                play_sound(current_wep.sound_name)
        # 右鍵技能環狀穿透彈幕    
        if mouse_btns[2] and player.skill_cd <= 0 and player.energy >= player.skill_cost and not player.is_dashing:
            player.energy -= player.skill_cost; player.skill_cd = player.skill_max_cd; play_sound("shoot_laser") 
            temp_wep = generate_weapon("手槍", "白"); temp_wep.bullet_type = "piercing"; temp_wep.damage = 50
            for i in range(16):
                angle = math.radians(i * (360 / 16))
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, player.rect.centerx + math.cos(angle)*100, player.rect.centery + math.sin(angle)*100, temp_wep, dmg_bonus=player.bullet_damage_bonus))

        if shoot_cooldown > 0: shoot_cooldown -= 1
        player.update()
        # 無敵模式下不受任何傷害，直接跳過碰撞和死亡檢測
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
        # 處理玩家的光環傷害，對範圍內的敵人造成持續傷害，並根據玩家的光環等級增加傷害和範圍，同時生成相應的粒子效果和掉落物
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
        # 處理玩家的衝刺軌跡，當玩家在衝刺時生成軌跡效果，並隨著時間減少軌跡的生命週期，確保衝刺軌跡在遊戲中有適當的視覺效果和持續時間
        if player.is_dashing: trails.append(DashTrail(player.rect.centerx, player.rect.centery, player.size))
        for t in trails[:]: t.update(); trails.remove(t) if t.life <= 0 else None
            
        map_rect = pygame.Rect(0, 0, MAP_WIDTH, MAP_HEIGHT)
        alive_bullets = []

        for b in bullets:
            b.update(enemies)
            
            if b.explode:
                screen_shake = 8; play_sound("shoot_cannon") 
                for _ in range(30): particles.append(Particle(b.x, b.y, ORANGE))
                for e in enemies[:]:
                    if math.hypot(e.x - b.x, e.y - b.y) < 120: 
                        actual_dmg = b.damage
                        if e.shield > 0:
                            leftover = actual_dmg - e.shield
                            e.shield = max(0, e.shield - actual_dmg)
                            if leftover > 0: e.hp -= leftover
                        else: e.hp -= actual_dmg
                        
                        if e.hp <= 0: 
                            if random.random() < 0.4: items.append(DropItem(e.x, e.y, "EXP"))
                            if e in enemies: enemies.remove(e)
                            
                if boss_active and boss.state != "DEFEAT" and math.hypot(boss.x - b.x, boss.y - b.y) < 150: 
                    boss.hp -= b.damage
                continue 
            # 子彈與敵人碰撞檢測        
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
                        leftover = b.damage - e.shield
                        e.shield = max(0, e.shield - b.damage)
                        if leftover > 0: e.hp -= leftover
                    else: e.hp -= b.damage
                        
                    damage_texts.append(DamageText(e.x, e.y - 20, b.damage, RED if b.is_crit else (YELLOW if b.damage >= 40 else WHITE), b.is_crit))
                    hit_something = True
                    for _ in range(5): particles.append(Particle(e.x, e.y, b.color))
                    play_sound("hit")
                    # 根據敵人類型和是否為精英，決定掉落物種類和數量
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
                    
                    if not b.is_piercing:
                        break 
            # Boss 碰撞檢測放在最後，確保子彈優先與普通敵人互動
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
                        for _ in range(10): items.append(DropItem(boss.x + random.randint(-40,40), boss.y + random.randint(-40,40), "SCRAP", random.randint(2,5)))
                        items.append(DropItem(boss.x, boss.y, "KEY"))
                        for _ in range(50): particles.append(Particle(boss.x, boss.y, YELLOW))

            if b.lifespan > 0 and map_rect.colliderect(b.rect) and (not hit_something or b.is_piercing) and not b.explode:
                alive_bullets.append(b)

        bullets = alive_bullets

        # 敵人、子彈、傷害數字、粒子更新與碰撞檢測
        
        for dt in damage_texts[:]:
            dt.update()
            if dt.timer <= 0: damage_texts.remove(dt)

        for p in particles[:]:
            p.update()
            if p.timer <= 0: particles.remove(p)

        for eb in enemy_bullets[:]:
            eb.update(player.x, player.y)
            
            # 如果飛彈壽命耗盡，產生範圍爆炸
            if getattr(eb, 'explode', False):
                play_sound("shoot_cannon") # 播放爆炸音效
                # 產生環狀爆炸特效
                for i in range(12): 
                    p = Particle(eb.x, eb.y, eb.color)
                    p.vel_x, p.vel_y = math.cos(i*30)*3, math.sin(i*30)*3
                    particles.append(p)
                
                # 檢查玩家是否在爆炸範圍內 (半徑 70)
                if math.hypot(player.x - eb.x, player.y - eb.y) < 70:
                    if not player.god_mode and player.invincible_timer <= 0 and not player.is_dashing:
                        actual_dmg = max(1, int(eb.damage * 1.5) - player.damage_reduction) # 爆炸傷害為 1.5 倍
                        if player.shield > 0:
                            if actual_dmg > player.shield: leftover = actual_dmg - player.shield; player.shield = 0; player.hp -= leftover
                            else: player.shield -= actual_dmg
                        else: player.hp -= actual_dmg
                        player.invincible_timer = player.invincible_duration; screen_shake = 12; play_sound("hurt")
                
                if eb in enemy_bullets: enemy_bullets.remove(eb)
                continue

            if not map_rect.colliderect(eb.rect): 
                enemy_bullets.remove(eb)

        for e in enemies:
            e.update(player.x, player.y, enemies, enemy_bullets)

        if boss_active and boss:
            boss.update(player.x, player.y, bullets, enemies, enemy_bullets)
        ##################################################################################
        #玩家受到攻擊的判定，無論是敵人本體還是子彈，只要碰撞就會觸發傷害計算和無敵時間，並且在玩家死亡時生成((遺失物))
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
                    player.invincible_timer = player.invincible_duration 
                    screen_shake = 10; play_sound("hurt")
                    
                if e.combat_type == "kamikaze":
                    for _ in range(15): particles.append(Particle(e.x, e.y, ORANGE))
                    if e in enemies: enemies.remove(e)
       # Boss 的碰撞檢測放在最後，確保玩家優先與普通敵人互動，只有在沒有其他碰撞的情況下才會檢測與 Boss 的碰撞，這樣可以增加遊戲的公平性和挑戰性             
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
        # Boss 的碰撞檢測放在最後，確保玩家優先與普通敵人和子彈互動，只有在沒有其他碰撞的情況下才會檢測與 Boss 的碰撞，這樣可以增加遊戲的公平性和挑戰性
        if boss_active and player.rect.colliderect(boss.rect) and game_state == "PLAYING": 
            if not player.god_mode and player.invincible_timer <= 0 and not player.is_dashing:
                actual_dmg = max(1, 40 - player.damage_reduction)
                if player.shield > 0:
                    if actual_dmg > player.shield: leftover = actual_dmg - player.shield; player.shield = 0; player.hp -= leftover
                    else: player.shield -= actual_dmg
                else: player.hp -= actual_dmg
                player.invincible_timer = player.invincible_duration; screen_shake = 10; play_sound("hurt")

        # 統一的玩家死亡判定：無論是否為白板，都會蓋過上一次的遺失物
        if player.hp <= 0 and game_state == "PLAYING":
            inv_copy = [item for item in player.inventory if item is not None]
            w1 = player.primary_weapon if player.primary_weapon.rarity != "白" else None
            w2 = player.secondary_weapon if player.secondary_weapon.rarity != "白" else None
            lost_item = PlayerLostItem(player.x, player.y, player.level, player.exp, list(chosen_upgrades), inv_copy, w1, w2)
            
            game_state = "DIED"
            play_sound("gameover")
            stop_sound("boss_bgm")

        # 狀態保護：只有活著的狀態下，才能拾取物資或遺失物 (防止死亡瞬間立刻把剛掉落的遺失物撿起銷毀)
        if game_state == "PLAYING":
            eff_radius = 9999 if magnet_timer > 0 else player.magnet_radius
            for g in items[:]:
                g.update(player.x, player.y, eff_radius)
                if g.item_type in ["EXP", "MAGNET", "BOMB", "SHIELD"] and player.rect.colliderect(g.rect):
                    items.remove(g)
                    if g.item_type == "EXP":
                        player.exp += 25 * player.exp_multiplier; play_sound("exp") 
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

    #畫面繪製
    if game_state in ["BUNKER", "SHOP", "GENERAL_STASH", "MOD_STATION", "WEAPON_STASH"]:
        screen.fill(BLACK)
        for i in range(0, WIDTH, 40): pygame.draw.line(screen, (15, 18, 22), (i,0), (i,HEIGHT))
        for i in range(0, HEIGHT, 40): pygame.draw.line(screen, (15, 18, 22), (0,i), (WIDTH,i))
        
        bunker_rect = pygame.Rect(MAP_WIDTH//2 - 400 - camera_x, MAP_HEIGHT//2 - 300 - camera_y, 800, 600)
        pygame.draw.rect(screen, (25, 28, 35), bunker_rect); pygame.draw.rect(screen, (60, 65, 80), bunker_rect, 4)
        #畫出地堡的終端機，部署閘門、黑市商店、改造台、收藏箱和武器箱，並根據當前遊戲狀態決定是否顯示地堡Dummy(我知道實際看起來不太像終端機OWO)
        draw_terminal(screen, pygame.Rect(MAP_WIDTH//2 - 60 - camera_x, MAP_HEIGHT//2 + 200 - camera_y, 120, 60), GREEN, "部署閘門 [E]", "DEPLOY")
        draw_terminal(screen, pygame.Rect(MAP_WIDTH//2 - 350 - camera_x, MAP_HEIGHT//2 - 50 - camera_y, 100, 100), BLUE, "黑市商店 [E]", "SHOP")
        draw_terminal(screen, pygame.Rect(MAP_WIDTH//2 - 150 - camera_x, MAP_HEIGHT//2 - 150 - camera_y, 100, 100), ORANGE, "改造台 [E]", "MOD")
        draw_terminal(screen, pygame.Rect(MAP_WIDTH//2 + 50 - camera_x, MAP_HEIGHT//2 - 150 - camera_y, 100, 100), (50, 150, 200), "收藏箱 [E]", "STASH")
        draw_terminal(screen, pygame.Rect(MAP_WIDTH//2 + 250 - camera_x, MAP_HEIGHT//2 - 50 - camera_y, 100, 100), RED, "武器箱 [E]", "WEAPON")
        if bunker_dummy: bunker_dummy.draw(screen)

        for b in bunker_bullets: b.draw(screen)
        for p in particles: p.draw(screen)
        for dt in damage_texts: dt.draw(screen)

        screen.blit(large_font.render("地堡安全屋", True, YELLOW), (WIDTH//2 - 120, 50))
        screen.blit(font.render(f"擁有廢料: {persistent_stats['scrap']}", True, SCRAP_COLOR), (WIDTH//2 - 70, 100))
        
        player.draw(screen, player.weapons[player.current_weapon_idx])
        draw_upgrade_summary(screen, WIDTH - 260, 20, max_items=5)
        #根據當前遊戲狀態繪製相應的UI界面，包含黑市商店、格子收藏箱和武器改造台，並在玩家與這些界面互動時顯示相關資訊和選項
        if game_state == "SHOP":
            screen.blit(dim_surface, (0, 0))
            draw_ui_panel(screen, shop_bg, "黑市升級 (BLACK MARKET)", BLUE)
            draw_hover_button(screen, btn_hp, f"最大血量+10 (目前:{player.max_hp}) - 50廢料", GREEN if persistent_stats["scrap"]>=50 else GRAY, (50, 180, 50))
            draw_hover_button(screen, btn_dmg, f"武器傷害+2 (目前:+{persistent_stats['dmg_bonus']}) - 50廢料", ORANGE if persistent_stats["scrap"]>=50 else GRAY, (200, 120, 0))
            draw_hover_button(screen, btn_spd, f"移動速度+0.2 (目前:+{persistent_stats['speed_bonus']:.1f}) - 50廢料", CYAN if persistent_stats["scrap"]>=50 else GRAY, (0, 180, 180))
            draw_hover_button(screen, btn_shop_close, "關閉離開", (150, 50, 50), RED)

        elif game_state == "GENERAL_STASH":
            screen.blit(dim_surface, (0, 0))
            draw_ui_panel(screen, stash_bg, "格子收藏箱 (GENERAL STASH)", (50, 150, 200))
            #繪製6x6的格子收藏箱界面，顯示玩家存放的物品，並根據物品類型使用不同顏色的圓點表示，同時在游標懸停時顯示物品資訊和高亮邊框
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
            draw_hover_button(screen, btn_stash_close, "關閉離開", (150, 50, 50), RED)
        #根據當前遊戲狀態繪製相應的UI界面，包含黑市商店、格子收藏箱和武器改造台，並在玩家與這些界面互動時顯示相關資訊和選項
        elif game_state == "MOD_STATION":
            screen.blit(dim_surface, (0, 0))
            draw_ui_panel(screen, mod_bg, "武器改造台 (WORKBENCH)", ORANGE)
            #繪製主武器和副武器的改造選項，顯示當前裝備的武器名稱和品質顏色，並在玩家選擇或懸停時高亮邊框，同時在右側顯示選中武器的詳細資訊和可用改造選項
            pygame.draw.rect(screen, (30,34,42), rect_prim, border_radius=8)
            screen.blit(small_font.render("主武器", True, WHITE), (rect_prim.centerx - 25, rect_prim.y + 10))
            screen.blit(small_font.render(player.primary_weapon.base_name, True, get_rarity_color(player.primary_weapon.rarity)), (rect_prim.centerx - 35, rect_prim.centery + 10))
            if selected_mod_weapon == player.primary_weapon: pygame.draw.rect(screen, YELLOW, rect_prim, 2, border_radius=8)
            elif rect_prim.collidepoint(m_pos): pygame.draw.rect(screen, WHITE, rect_prim, 1, border_radius=8)
            #副武器的繪製邏輯與主武器類似，但會根據玩家當前裝備的副武器顯示相應的名稱和品質顏色，並在玩家選擇或懸停時高亮邊框，同時在右側顯示選中武器的詳細資訊和可用改造選項
            pygame.draw.rect(screen, (30,34,42), rect_sec, border_radius=8)
            screen.blit(small_font.render("副武器", True, WHITE), (rect_sec.centerx - 25, rect_sec.y + 10))
            screen.blit(small_font.render(player.secondary_weapon.base_name, True, get_rarity_color(player.secondary_weapon.rarity)), (rect_sec.centerx - 35, rect_sec.centery + 10))
            if selected_mod_weapon == player.secondary_weapon: pygame.draw.rect(screen, YELLOW, rect_sec, 2, border_radius=8)
            elif rect_sec.collidepoint(m_pos): pygame.draw.rect(screen, WHITE, rect_sec, 1, border_radius=8)
            #繪製6x4的武器改造台界面，顯示玩家背包中的武器，並根據武器品質使用不同顏色的圓點表示，同時在游標懸停時顯示武器資訊和高亮邊框，並在右側顯示選中武器的詳細資訊和可用改造選項
            hi = draw_player_inv_grid(screen, p_start_x_m, p_start_y_m, m_x, m_y, allow_weapons=True)
            if hi: hovered_slot_info = hi
            for i in range(24):
                item = player.inventory[i]
                if item and item.type == "WEAPON" and selected_mod_weapon == item.weapon_obj:
                    pygame.draw.rect(screen, YELLOW, (p_start_x_m + (i%6)*58, p_start_y_m + (i//6)*58, 50, 50), 2, border_radius=6)
            #在武器改造台界面右側繪製選中武器的詳細資訊，包括武器名稱、傷害值、詞綴列表，以及根據武器品質顯示相應的改造選項，並根據玩家的廢料數量決定改造選項的可用性，同時在游標懸停時高亮按鈕邊框
            pygame.draw.rect(screen, (25,28,35), (WIDTH//2 + 30, HEIGHT//2 - 150, 300, 400), border_radius=10)
            if selected_mod_weapon:
                c = get_rarity_color(selected_mod_weapon.rarity)
                screen.blit(large_font.render(selected_mod_weapon.full_name, True, c), (WIDTH//2 + 50, HEIGHT//2 - 130))
                screen.blit(font.render(f"傷害: {selected_mod_weapon.damage}", True, WHITE), (WIDTH//2 + 50, HEIGHT//2 - 80))
                aff_str = ",".join(selected_mod_weapon.affixes) if selected_mod_weapon.affixes else "無"
                screen.blit(font.render(f"詞綴: {aff_str}", True, YELLOW), (WIDTH//2 + 50, HEIGHT//2 - 40))
                
                if selected_mod_weapon.rarity != "金":
                    cost = {"白":50, "藍":150, "紫":300}[selected_mod_weapon.rarity]
                    draw_hover_button(screen, upg_btn, f"升級品質 ({cost} 廢料)", GREEN if persistent_stats["scrap"]>=cost else GRAY, (50, 180, 50), BLACK)
                if selected_mod_weapon.rarity != "白":
                    cost = {"藍":30, "紫":80, "金":150}[selected_mod_weapon.rarity]
                    draw_hover_button(screen, reroll_btn, f"重置詞綴 ({cost} 廢料)", BLUE if persistent_stats["scrap"]>=cost else GRAY, (50, 100, 180))
            
            draw_hover_button(screen, btn_mod_close, "關閉離開", (150, 50, 50), RED)

        elif game_state == "WEAPON_STASH":
            screen.blit(dim_surface, (0, 0))
            draw_ui_panel(screen, wep_stash_bg, "全自動武器箱 (ARSENAL)", RED)
            
            p_c, s_c = get_rarity_color(player.primary_weapon.rarity), get_rarity_color(player.secondary_weapon.rarity)
            screen.blit(small_font.render("當前裝備 =>", True, WHITE), (WIDTH//2 - 320, HEIGHT//2 - 260))
            screen.blit(small_font.render(f"主: {player.primary_weapon.full_name}", True, p_c), (WIDTH//2 - 200, HEIGHT//2 - 260))
            screen.blit(small_font.render(f"副: {player.secondary_weapon.full_name}", True, s_c), (WIDTH//2 + 50, HEIGHT//2 - 260))
            # 武器列表區域
            pygame.draw.rect(screen, (15, 18, 22), list_rect, border_radius=6); pygame.draw.rect(screen, (50, 55, 65), list_rect, 1, border_radius=6)
            list_surf = pygame.Surface((list_rect.width, max(list_rect.height, (len(arsenal_weapons_list)+1)//2 * 50)))
            list_surf.fill((15, 18, 22))
            for i, wep in enumerate(arsenal_weapons_list):
                col, row = i % 2, i // 2
                box = pygame.Rect(col*320 + 10, row*50 + 5, 300, 42)
                is_sel = (i == selected_arsenal_idx)
                pygame.draw.rect(list_surf, (40, 45, 55), box, border_radius=6)
                pygame.draw.rect(list_surf, YELLOW if is_sel else GRAY, box, 2 if is_sel else 1, border_radius=6)
                c = get_rarity_color(wep.rarity)
                list_surf.blit(font.render(wep.full_name, True, c), (box.x + 10, box.y + 8))
                aff_txt = ",".join(wep.affixes) if wep.affixes else "無"
                list_surf.blit(tiny_font.render(f"傷:{wep.damage} [{aff_txt}]", True, WHITE), (box.x + 160, box.y + 14))
                if box.collidepoint(m_x - list_rect.x, m_y - list_rect.y + arsenal_scroll_y) and list_rect.collidepoint(m_pos):
                    pygame.draw.rect(list_surf, WHITE, box, 1, border_radius=6)
                    hovered_slot_info = {"source": "ARSENAL", "idx": i, "item": create_item("WEAPON", 1, wep)}

            screen.blit(list_surf, list_rect.topleft, pygame.Rect(0, arsenal_scroll_y, list_rect.width, list_rect.height))
            
            screen.blit(small_font.render("右鍵:切換武器箱與背包 | 游標指著按 [X] 出售", True, GRAY), (WIDTH//2 - 320, HEIGHT//2 + 45))
            for i in range(24):
                rect = pygame.Rect(p_start_x_w + (i%11)*58, p_start_y_w + (i//11)*58, 50, 50)
                pygame.draw.rect(screen, (25, 28, 35), rect, border_radius=6); pygame.draw.rect(screen, (55, 60, 70), rect, 1, border_radius=6)
                item = player.inventory[i]
                if item:
                    if item.type == "WEAPON":
                        pygame.draw.circle(screen, get_rarity_color(item.weapon_obj.rarity), rect.center, 14)
                        if rect.collidepoint(m_x, m_y):
                            hovered_slot_info = {"source": "PLAYER", "idx": i, "item": item}
                            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=6)
                    else: pygame.draw.circle(screen, (60,60,60), rect.center, 14)

            draw_hover_button(screen, btn_prim_w, "裝備為主武器", GREEN, (50, 180, 50), BLACK)
            draw_hover_button(screen, btn_sec_w, "裝備為副武器", BLUE, (50, 100, 180), WHITE)
            draw_hover_button(screen, btn_wep_close, "關閉離開", (150, 50, 50), RED)

        # 游標拖著物品的視覺反饋，根據物品類型顯示不同顏色的圓圈，並且如果游標在某個物品上且沒有拖著東西，則顯示該物品的說明和出售價值
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
    # 根據遊戲狀態繪製遊戲主畫面，包含背景、地圖邊界、玩家、敵人、子彈、物品、粒子效果、傷害數字，以及根據不同狀態顯示相應的提示和UI元素，例如開箱提示、撿取提示、Boss方向箭頭等，同時在玩家死亡時顯示遺失物並提供撿取選項
    elif game_state in ["PLAYING", "PAUSED", "LEVEL_UP", "DIED"]:
        if images.get("bg"):
            bg_w, bg_h = WIDTH, HEIGHT
            for x in range(0, MAP_WIDTH, bg_w):
                for y in range(0, MAP_HEIGHT, bg_h):
                    draw_x = x - int(camera_x); draw_y = y - int(camera_y)
                    if draw_x + bg_w > 0 and draw_x < WIDTH and draw_y + bg_h > 0 and draw_y < HEIGHT: screen.blit(images["bg"], (draw_x, draw_y))
        else: screen.fill(BLACK)
        #地圖邊界框線暫時先用紅色表示，之後可以換成更有科技感的邊界特效會發光閃逤，或是更淺的顏色加上半透明的遮罩，或著配合背景顏色
        pygame.draw.rect(screen, RED, (-int(camera_x), -int(camera_y), MAP_WIDTH, MAP_HEIGHT), 5)
        
        if extraction_pt: extraction_pt.draw(screen)
        if lost_item: lost_item.draw(screen); draw_lost_item_arrow(screen, camera_x, camera_y)
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
        #根據玩家與環境的互動狀態，顯示相應的提示信息，例如當玩家靠近木箱時顯示開箱提示，當玩家靠近可撿取的物品時顯示撿取提示，並且根據木箱類型和玩家是否擁有金鑰匙來調整提示文本和顏色，以提供清晰的反饋和指引
        if game_state == "PLAYING" and not show_inventory:
            for c in chests:
                if c.state == "CLOSED" and math.hypot(player.x - c.x, player.y - c.y) < 70:
                    has_key = any(item.type == "KEY" for item in player.inventory if item)
                    t = "[F] 開啟木箱" if c.type == "NORMAL" else ("[F] 消耗金鑰匙" if has_key else "需要金鑰匙")
                    t_c = WHITE if c.type == "NORMAL" or has_key else RED
                    bg_r = pygame.Rect(c.x - camera_x - 40, c.y - camera_y - 50, font.size(t)[0]+20, 25)
                    popup = pygame.Surface((bg_r.width, bg_r.height), pygame.SRCALPHA)
                    pygame.draw.rect(popup, (20, 20, 25, 200), popup.get_rect(), border_radius=4)
                    screen.blit(popup, (bg_r.x, bg_r.y))
                    screen.blit(small_font.render(t, True, t_c), (bg_r.x+10, bg_r.y+3))
                    
            for g in items:
                if g.item_type not in ["EXP", "MAGNET", "BOMB", "SHIELD"] and math.hypot(player.x - g.x, player.y - g.y) < 70:
                    bg_r = pygame.Rect(g.x - camera_x - 30, g.y - camera_y - 40, 60, 25)
                    popup = pygame.Surface((bg_r.width, bg_r.height), pygame.SRCALPHA)
                    pygame.draw.rect(popup, (20, 20, 25, 200), popup.get_rect(), border_radius=4)
                    screen.blit(popup, (bg_r.x, bg_r.y))
                    screen.blit(small_font.render("[F] 撿取", True, WHITE), (bg_r.x+5, bg_r.y+3))
        
        draw_minimap(screen)
        
        # HUD 資訊，根據玩家的經驗值、等級、血量、護盾、體力、能量、武器裝備狀態以及當前遊戲模式，繪製相應的進度條和文本信息，並使用不同的顏色來表示不同的狀態，例如當血量較低時顯示紅色，當能量不足時顯示灰色，以及根據玩家是否啟用全解鎖密技來調整武器名稱的顏色，以提供清晰的反饋和指引
        pygame.draw.rect(screen, GRAY, (20, 20, 250, 15)); pygame.draw.rect(screen, BLUE, (20, 20, 250 * (player.exp / player.max_exp), 15))
        screen.blit(font.render("等級: " + str(player.level), True, WHITE), (280, 15))

        pygame.draw.rect(screen, GRAY, (20, 45, 200, 15)); pygame.draw.rect(screen, GREEN if player.hp > 30 else RED, (20, 45, 200 * (max(0, player.hp) / player.max_hp), 15))
        screen.blit(font.render("血量", True, WHITE), (230, 40))

        pygame.draw.rect(screen, GRAY, (20, 70, 200, 15)); pygame.draw.rect(screen, (0, 150, 255), (20, 70, 200 * (max(0, player.shield) / player.max_shield), 15))
        screen.blit(font.render("護盾", True, WHITE), (230, 65))

        pygame.draw.rect(screen, GRAY, (20, 95, 150, 10)); pygame.draw.rect(screen, ORANGE, (20, 95, 150 * (player.stamina / player.max_stamina), 10))
        screen.blit(font.render("體力 (Q)", True, WHITE), (180, 87)) 
        
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
        #根據玩家的武器狀態繪製當前裝備的主武器和副武器名稱，並使用不同顏色表示是否啟用全解鎖密技，同時在玩家按下切換武器的按鍵時更新顯示的武器名稱和高亮指示，以提供清晰的裝備資訊    
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
        #根據當前遊戲狀態繪製相應的提示信息，例如當玩家靠近木箱時顯示開箱提示，當玩家靠近可撿取的物品時顯示撿取提示，並且根據木箱類型和玩家是否擁有金鑰匙來調整提示文本和顏色，以提供清晰的反饋和指引
        if extraction_pt:
            time_sec = extraction_timer // FPS
            mins, secs = time_sec // 60, time_sec % 60
            color = WHITE if time_sec > 30 else RED
            screen.blit(large_font.render(f"撤離倒數: {mins:02d}:{secs:02d}", True, color), (WIDTH//2 - 120, 20))
            if extract_progress > 0:
                pygame.draw.rect(screen, GRAY, (WIDTH//2 - 100, 110, 200, 15)); pygame.draw.rect(screen, GREEN, (WIDTH//2 - 100, 110, 200 * (extract_progress / 120), 15))
            if boss_army_active: screen.blit(large_font.render("警告：超時！狂暴大軍來襲！", True, RED), (WIDTH//2 - 220, 140))
        #根據Boss的狀態繪製Boss血量條，顯示Boss的名稱和當前血量百分比，並根據Boss的類型使用不同顏色的血量條，同時在Boss出現時顯示警告信息，提醒玩家注意即將到來的危險
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
    # 根據遊戲狀態繪製主選單界面，包含背景特效、遊戲標題、按鈕選項，以及根據玩家的互動狀態顯示相應的提示信息和更新日誌彈窗，提供一個吸引人且功能齊全的入口界面
    if game_state == "MENU":
        screen.fill(BLACK)
        for i in range(100):
            x, y = (i * 37) % WIDTH, (i * 23) % HEIGHT
            brightness = 100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i)
            pygame.draw.circle(screen, (brightness, brightness, brightness), (x, y), 1)
        
        glow_color = (0, 100, 255, 50)
        glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        title = large_font.render("末日肉鴿生存?", True, BLUE)
        glow_surface.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2), (0, -3), (0, 3), (-3, 0), (3, 0)]:
            glow_copy = glow_surface.copy(); glow_copy.fill(glow_color, special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(glow_copy, offset)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//2 - 120))
        screen.blit(font.render("末日肉鴿RPG?", True, WHITE), (WIDTH//2 - 120, HEIGHT//2 - 50))

        draw_hover_button(screen, start_button, "部署行動", (50, 150, 50), (100, 200, 100))
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

>>>>>>> 5fe3c3b9a6cb6e15508d0cc26521ee2ec490b8fd
pygame.quit()