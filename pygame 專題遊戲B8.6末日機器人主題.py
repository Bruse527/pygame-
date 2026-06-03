import pygame
import random
import math
import os
import ctypes

# 初始化遊戲跟音效
pygame.init()
pygame.mixer.init()

def switch_to_english_input():
    try:
        user32 = ctypes.windll.user32
        hkl = user32.LoadKeyboardLayoutW("00000409", 1)
        if hkl: user32.ActivateKeyboardLayout(hkl, 0)
    except Exception: pass
switch_to_english_input()

# 設定遊戲分辨率（1024x768）
WIDTH, HEIGHT = 1024, 768
MAP_WIDTH, MAP_HEIGHT = 4200, 2600

# 縮放因子（用於動態UI調整，預留擴展空間）
SCALE = 1.0

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("末日肉鴿生存 - 最終融合版")
clock, FPS = pygame.time.Clock(), 60

camera_x, camera_y, screen_shake = 0, 0, 0  

BLACK, BLUE, RED, YELLOW = (10, 10, 15), (0, 200, 255), (255, 20, 80), (255, 255, 0)
PURPLE, DARK_PURPLE, WHITE = (200, 50, 255), (138, 43, 226), (255, 255, 255)
GRAY, GREEN, ORANGE, CYAN = (100, 100, 110), (0, 255, 100), (255, 150, 0), (0, 255, 255)
SCRAP_COLOR, CARD_COLOR = (200, 200, 200), (30, 30, 40)
CARD_TYPE_COLORS = {"attack": (120, 35, 45), "support": (35, 75, 130), "life": (35, 110, 65)}
CARD_TYPE_LABELS = {"attack": "攻擊", "support": "支援", "life": "生命"}
SHIELD_COLOR, EXP_COLOR, HP_COLOR = (0, 150, 255), (124, 252, 0), (255, 50, 50)

CHINESE_FONTS = "microsoftjhenghei,pingfangtc,stheiti,simhei"
# 根據屏幕大小動態調整字體大小
font = pygame.font.SysFont(CHINESE_FONTS, max(18, int(24 * SCALE)))
large_font = pygame.font.SysFont(CHINESE_FONTS, max(32, int(42 * SCALE)))
small_font = pygame.font.SysFont(CHINESE_FONTS, max(14, int(18 * SCALE)))
tiny_font = pygame.font.SysFont(CHINESE_FONTS, max(12, int(14 * SCALE)))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR, AUDIO_DIR = os.path.join(BASE_DIR, "images"), os.path.join(BASE_DIR, "audio")
if not os.path.exists(IMAGE_DIR): os.makedirs(IMAGE_DIR)
if not os.path.exists(AUDIO_DIR): os.makedirs(AUDIO_DIR)
images, animations, sounds = {}, {}, {}

def load_image(name, filename, size=None):
    try:
        path = os.path.join(IMAGE_DIR, filename)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            images[name] = pygame.transform.scale(img, size) if size else img
        else: images[name] = None
    except: images[name] = None

def load_animation(name, folder_name, size):
    folder_path = os.path.join(IMAGE_DIR, folder_name)
    if not os.path.exists(folder_path): os.makedirs(folder_path); animations[name] = None; return
    frames = [pygame.transform.scale(pygame.image.load(os.path.join(folder_path, f)).convert_alpha(), size) for f in sorted(os.listdir(folder_path)) if f.endswith((".png", ".jpg"))]
    animations[name] = frames if frames else None

def load_sound(name, filename):
    try:
        path = os.path.join(AUDIO_DIR, filename)
        if os.path.exists(path): sounds[name] = pygame.mixer.Sound(path); sounds[name].set_volume(0.3)
        else: sounds[name] = None
    except: sounds[name] = None 

load_image("bg", "bg.png", (WIDTH, HEIGHT)); load_image("drop_EXP", "drop_exp.png", (20, 20))
load_image("chest_NORMAL_CLOSED", "chest_normal_closed.png", (50, 40)); load_image("chest_NORMAL_OPEN", "chest_normal_open.png", (50, 40))
load_image("chest_LOCKED_CLOSED", "chest_locked_closed.png", (50, 40)); load_image("chest_LOCKED_OPEN", "chest_locked_open.png", (50, 40))
load_image("bullet_normal", "bullet_normal.png", (16, 16)); load_image("bullet_piercing", "bullet_piercing.png", (20, 20))
load_image("bullet_shotgun", "bullet_shotgun.png", (16, 16)); load_image("bullet_flamethrower", "bullet_flame.png", (30, 30))
load_image("bullet_laser", "bullet_laser.png", (10, 40)); load_image("bullet_cannon", "bullet_cannon.png", (40, 40))
load_image("bullet_frost", "bullet_frost.png", (20, 20)); load_image("bullet_flame_grenade", "bullet_grenade.png", (24, 24))
load_image("bullet_plasma", "bullet_plasma.png", (24, 24)); load_image("enemy_bullet", "bullet_enemy.png", (18, 18))
load_animation("player", "player", (40, 40)); load_animation("enemy_normal", "enemy_normal", (35, 35))
load_animation("enemy_elite", "enemy_elite", (50, 50)); load_animation("dummy", "dummy", (40, 60)) 

load_sound("dash", "dash.wav"); load_sound("hit", "hit.wav"); load_sound("levelup", "levelup.wav")
load_sound("hurt", "hurt.wav"); load_sound("boss_bgm", "boss.wav"); load_sound("gameover", "gameover.wav")
load_sound("exp", "exp.wav"); load_sound("shoot_normal", "shoot_normal.wav"); load_sound("shoot_laser", "shoot_laser.wav")
load_sound("shoot_shotgun", "shoot_shotgun.wav"); load_sound("shoot_cannon", "shoot_cannon.wav"); load_sound("shoot_flame", "shoot_flame.wav") 

def load_weapon_sound(wk, fn, fb):
    p = os.path.join(AUDIO_DIR, fn)
    sounds[wk] = pygame.mixer.Sound(p) if os.path.exists(p) else sounds.get(fb)
    if sounds.get(wk): sounds[wk].set_volume(0.3)

load_weapon_sound("snd_pistol", "pistol.wav", "shoot_normal"); load_weapon_sound("snd_sniper", "sniper.wav", "shoot_cannon")
load_weapon_sound("snd_shotgun", "shotgun.wav", "shoot_shotgun"); load_weapon_sound("snd_mg", "machinegun.wav", "shoot_normal")
load_weapon_sound("snd_flamethrower", "flamethrower.wav", "shoot_flame"); load_weapon_sound("snd_laser", "laser.wav", "shoot_laser")
load_weapon_sound("snd_cannon", "cannon.wav", "shoot_cannon"); load_weapon_sound("snd_frost", "frost.wav", "shoot_flame")
load_weapon_sound("snd_heavy_mg", "heavy_mg.wav", "shoot_shotgun"); load_weapon_sound("snd_rifle", "rifle.wav", "shoot_cannon")
load_weapon_sound("snd_grenade", "grenade.wav", "shoot_cannon"); load_weapon_sound("snd_plasma", "plasma.wav", "shoot_laser")

bgm_path = os.path.join(AUDIO_DIR, "bgm.mp3")
if os.path.exists(bgm_path): pygame.mixer.music.load(bgm_path); pygame.mixer.music.set_volume(0.2); pygame.mixer.music.play(loops=-1)

def play_sound(name, loop=0):
    if sounds.get(name): sounds[name].play(loops=loop)
def stop_sound(name):
    if sounds.get(name): sounds[name].stop()

# ================== UI 與繪圖系統 ==================
def draw_ui_panel(surface, rect, title, accent_color):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (18, 20, 26, 245), panel.get_rect(), border_radius=12)
    pygame.draw.rect(panel, (50, 55, 65), panel.get_rect(), 2, border_radius=12)
    pygame.draw.rect(panel, (30, 34, 42, 255), pygame.Rect(0, 0, rect.width, 45), border_top_left_radius=12, border_top_right_radius=12)
    pygame.draw.line(panel, accent_color, (0, 45), (rect.width, 45), 2)
    surface.blit(panel, (rect.x, rect.y))
    t_surf = large_font.render(title, True, accent_color)
    surface.blit(t_surf, (rect.centerx - t_surf.get_width()//2, rect.y + 5))

def draw_hover_button(surface, rect, text, base_color, hover_color=None, text_color=WHITE):
    if hover_color is None: hover_color = (min(255, base_color[0]+40), min(255, base_color[1]+40), min(255, base_color[2]+40))
    is_hover = rect.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(surface, hover_color if is_hover else base_color, rect, border_radius=8)
    pygame.draw.rect(surface, WHITE if is_hover else GRAY, rect, 2, border_radius=8)
    t_surf = font.render(text, True, text_color)
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
        surface.blit(small_font.render(f"屬性: {','.join(wep.affixes) if wep.affixes else '無'}", True, YELLOW), (tt_rect.x+10, tt_rect.y+65))
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

def draw_minimap(surface):
    map_w, map_h = 160, 120
    m_rect = pygame.Rect(WIDTH - map_w - 20, 20, map_w, map_h)
    mm_surf = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
    pygame.draw.rect(mm_surf, (10, 10, 20, 180), mm_surf.get_rect(), border_radius=5)
    pygame.draw.rect(mm_surf, (50, 200, 50), mm_surf.get_rect(), 2, border_radius=5)
    surface.blit(mm_surf, m_rect.topleft)
    def to_mm(px, py): return m_rect.x + (px / MAP_WIDTH) * map_w, m_rect.y + (py / MAP_HEIGHT) * map_h
    if extraction_pt:
        pygame.draw.circle(surface, GREEN, (int(to_mm(extraction_pt.x, extraction_pt.y)[0]), int(to_mm(extraction_pt.x, extraction_pt.y)[1])), 4)
    if 'boss_active' in globals() and boss_active and boss:
        pygame.draw.circle(surface, RED, (int(to_mm(boss.x, boss.y)[0]), int(to_mm(boss.x, boss.y)[1])), 5)
    if 'lost_item' in globals() and lost_item:
        lx, ly = to_mm(lost_item.x, lost_item.y)
        p = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 4)
        pygame.draw.circle(surface, YELLOW, (int(lx), int(ly)), 4); pygame.draw.circle(surface, RED, (int(lx), int(ly)), 5 + p, 1)
    px, py = to_mm(player.x, player.y)
    pygame.draw.circle(surface, BLUE, (int(px), int(py)), 4)

def draw_boss_direction_arrow(surface, boss_obj, cam_x, cam_y):
    if not boss_obj or (hasattr(boss_obj, "state") and boss_obj.state == "DEFEAT"): return
    bx, by = boss_obj.x - cam_x, boss_obj.y - cam_y
    if 0 <= bx <= WIDTH and 0 <= by <= HEIGHT: return
    center = pygame.math.Vector2(WIDTH / 2, HEIGHT / 2)
    direction = pygame.math.Vector2(bx - center.x, by - center.y)
    if direction.length_squared() == 0: return
    direction.normalize_ip()
    margin = 56
    scale_x = (WIDTH / 2 - margin) / abs(direction.x) if abs(direction.x) > 0.001 else float("inf")
    scale_y = (HEIGHT / 2 - margin) / abs(direction.y) if abs(direction.y) > 0.001 else float("inf")
    arrow_pos = center + direction * min(scale_x, scale_y)
    side = direction.rotate(90)
    tip, left, right = arrow_pos + direction * 25, arrow_pos - direction * 18 + side * 15, arrow_pos - direction * 18 - side * 15
    pts = [(int(tip.x), int(tip.y)), (int(left.x), int(left.y)), (int(right.x), int(right.y))]
    pygame.draw.polygon(surface, BLACK, pts); pygame.draw.polygon(surface, YELLOW, pts, 0); pygame.draw.polygon(surface, RED, pts, 3)

def draw_boss_health_bar(surface, boss_obj):
    bar_rect = pygame.Rect(110, HEIGHT - 52, WIDTH - 220, 28)
    ratio = max(0, min(1, boss_obj.hp / boss_obj.max_hp))
    pulse = abs(math.sin(pygame.time.get_ticks() * 0.006))
    phase = getattr(boss_obj, "phase", 1)
    fill_color = (255, 35, 55) if phase >= 2 else (255, 185, 35)
    edge_color = (255, 230, 120) if boss_obj.state in ("TRANSFORM", "CHARGE", "AIM", "RAGE_WINDUP") else WHITE

    shadow = pygame.Surface((bar_rect.width + 28, bar_rect.height + 34), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 160), (14, 17, bar_rect.width, bar_rect.height), border_radius=7)
    surface.blit(shadow, (bar_rect.x - 14, bar_rect.y - 17))
    pygame.draw.rect(surface, (28, 18, 24), bar_rect.inflate(18, 16), border_radius=8)
    pygame.draw.rect(surface, edge_color, bar_rect.inflate(18, 16), 3, border_radius=8)
    pygame.draw.rect(surface, (75, 60, 65), bar_rect, border_radius=5)

    fill_w = int(bar_rect.width * ratio)
    if fill_w > 0:
        fill_rect = pygame.Rect(bar_rect.x, bar_rect.y, fill_w, bar_rect.height)
        pygame.draw.rect(surface, fill_color, fill_rect, border_radius=5)
        highlight = pygame.Rect(fill_rect.x + 4, fill_rect.y + 4, max(0, fill_rect.width - 8), 7)
        if highlight.width > 0: pygame.draw.rect(surface, (255, 245, 170), highlight, border_radius=3)
        if ratio < 0.35 or boss_obj.state in ("TRANSFORM", "RAGE_DASH"):
            pygame.draw.circle(surface, (255, 255, 210), (fill_rect.right - 4, fill_rect.centery), int(10 + pulse * 7), 2)

    for i in range(1, 12):
        x = bar_rect.x + int(bar_rect.width * i / 12)
        pygame.draw.line(surface, (45, 28, 34), (x, bar_rect.y + 3), (x, bar_rect.bottom - 3), 2)

    name = getattr(boss_obj, "name", "BOSS")
    phase_label = f"  PHASE {phase}" if hasattr(boss_obj, "phase") else ""
    title_txt = font.render(f"{name}  Lv.{boss_obj.spawn_level}{phase_label}", True, edge_color)
    hp_txt = small_font.render(f"{max(0, int(boss_obj.hp))} / {boss_obj.max_hp}", True, WHITE)
    surface.blit(title_txt, (bar_rect.x, bar_rect.y - title_txt.get_height() - 14))
    surface.blit(hp_txt, (bar_rect.right - hp_txt.get_width(), bar_rect.y - hp_txt.get_height() - 12))
    if boss_obj.state == "TRANSFORM":
        rage_txt = small_font.render("RAGE CORE REBOOTING - HP REFILL", True, RED)
        surface.blit(rage_txt, (bar_rect.centerx - rage_txt.get_width() // 2, bar_rect.y - 58))

def draw_lost_item_arrow(surface, cx, cy):
    if not ('lost_item' in globals() and lost_item): return
    dx, dy = lost_item.x - player.x, lost_item.y - player.y
    if math.sqrt(dx**2 + dy**2) > min(WIDTH, HEIGHT) * 0.4:
        angle = math.atan2(dy, dx)
        r = min(WIDTH, HEIGHT) / 2 - 60
        ax, ay = WIDTH/2 + math.cos(angle)*r, HEIGHT/2 + math.sin(angle)*r
        side = pygame.math.Vector2(math.cos(angle), math.sin(angle)).rotate(90)
        p = pygame.math.Vector2(ax, ay); d = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        pts = [p + d*20, p - d*10 + side*15, p - d*10 - side*15]
        pygame.draw.polygon(surface, YELLOW, pts); pygame.draw.polygon(surface, RED, pts, 2)
        txt = small_font.render("遺失物", True, YELLOW)
        surface.blit(txt, (ax - txt.get_width()//2, ay - 35))

def draw_upgrade_summary(surface, x, y, max_items=6, title="已選強化"):
    panel_width, row_height = 240, 26
    hidden_count = max(0, len(chosen_upgrades) - max_items)
    row_count = max(1, min(len(chosen_upgrades), max_items))
    panel_height = 40 + row_count * row_height + (row_height if hidden_count else 0)
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((18, 20, 30, 185)); surface.blit(panel, (x, y))
    pygame.draw.rect(surface, WHITE, (x, y, panel_width, panel_height), 2, border_radius=8)

    total_count = sum(u["count"] for u in chosen_upgrades)
    title_label = f"{title} ({total_count})" if chosen_upgrades else title
    surface.blit(small_font.render(title_label, True, YELLOW), (x + 14, y + 10))

    if not chosen_upgrades:
        surface.blit(small_font.render("尚未選擇", True, GRAY), (x + 14, y + 40)); return

    for i, upgrade in enumerate(chosen_upgrades[-max_items:]):
        suffix = f" x{upgrade['count']}" if upgrade["count"] > 1 else ""
        surface.blit(small_font.render(f"{upgrade['title']}{suffix}", True, WHITE), (x + 14, y + 40 + i * row_height))

    if hidden_count: surface.blit(small_font.render(f"還有 {hidden_count} 種...", True, GRAY), (x + 14, y + 40 + len(chosen_upgrades[-max_items:]) * row_height))

def draw_task_panel(surface, task_system, x, y):
    panel_width, panel_height = 320, 180
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (18, 20, 26, 245), panel.get_rect(), border_radius=12)
    pygame.draw.rect(panel, (100, 200, 100), panel.get_rect(), 2, border_radius=12)
    header = pygame.Rect(0, 0, panel_width, 40)
    pygame.draw.rect(panel, (30, 34, 42, 255), header, border_top_left_radius=12, border_top_right_radius=12)
    pygame.draw.line(panel, (100, 200, 100), (0, 40), (panel_width, 40), 2)
    title_surf = font.render("每日任務", True, (100, 200, 100))
    panel.blit(title_surf, (panel_width//2 - title_surf.get_width()//2, 8)); surface.blit(panel, (x, y))
    
    if task_system.current_task:
        task = task_system.current_task
        surface.blit(font.render(task.name, True, YELLOW), (x + 15, y + 50))
        surface.blit(small_font.render(task.description, True, WHITE), (x + 15, y + 85))
        progress_percent = min(1.0, task.current_progress / task.objective_value) if task.objective_value > 0 else 0
        pygame.draw.rect(surface, GRAY, (x + 15, y + 120, 280, 12), border_radius=3)
        pygame.draw.rect(surface, (0, 200, 100), (x + 15, y + 120, 280 * progress_percent, 12), border_radius=3)
        surface.blit(tiny_font.render(f"{int(task.current_progress)}/{task.objective_value}", True, WHITE), (x + 20, y + 121))
        
        reward_text = ""
        if task.reward_type == "scrap": reward_text = f"獎勵: {task.reward_amount} 廢料"
        elif task.reward_type == "exp": reward_text = f"獎勵: {task.reward_amount} 經驗"
        elif task.reward_type == "dmg_bonus": reward_text = f"獎勵: +{task.reward_amount} 傷害"
        elif task.reward_type == "max_hp": reward_text = f"獎勵: +{task.reward_amount} 血量"
        elif task.reward_type == "max_stamina": reward_text = f"獎勵: +{task.reward_amount} 體力"
        surface.blit(small_font.render(reward_text, True, YELLOW), (x + 15, y + 150))
    else:
        no_task = small_font.render("暫無可用任務", True, GRAY)
        surface.blit(no_task, (x + panel_width//2 - no_task.get_width()//2, y + 100))

def rebuild_changelog_cache(w, h): pass

def draw_changelog_popup(surface):
    rect = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 200, 500, 400)
    draw_ui_panel(surface, rect, "更新與修復日誌", BLUE)
    close_rect = pygame.Rect(rect.right - 45, rect.y + 10, 35, 35)
    draw_hover_button(surface, close_rect, "X", (180, 60, 60), RED, WHITE)
    logs = [
        "修復項目與優化內容:",
        "- 全新三大階段 Boss 系統加入！",
        "- 修復：傷害數字與特效凍結在畫面的問題。",
        "- 修復：Boss 行為凍結的問題。",
        "- 成功撤離會完美保留所有狀態。",
    ]
    for i, line in enumerate(logs):
        surface.blit(small_font.render(line, True, WHITE), (rect.x + 20, rect.y + 60 + i * 30))

def draw_pause_upgrade_log(surface):
    draw_upgrade_summary(surface, WIDTH//2 - 120, HEIGHT//2 + 150, max_items=8, title="已獲得的強化")

def draw_player_inv_grid(surface, start_x, start_y, m_x, m_y, allow_weapons=True):
    hover_info = None
    for i in range(24):
        rect = pygame.Rect(start_x + (i%6)*58, start_y + (i//6)*58, 50, 50)
        pygame.draw.rect(surface, (25, 28, 35), rect, border_radius=6)
        pygame.draw.rect(surface, (55, 60, 70), rect, 1, border_radius=6)
        item = player.inventory[i]
        if item and not (drag_data and drag_data["source"] == "PLAYER" and drag_data["idx"] == i):
            if item.type == "WEAPON":
                if allow_weapons: pygame.draw.circle(surface, get_rarity_color(item.weapon_obj.rarity), rect.center, 14)
                else: pygame.draw.circle(surface, (60, 60, 60), rect.center, 14)
            else:
                c = HP_COLOR if item.type == "MED" else (SCRAP_COLOR if item.type == "SCRAP" else YELLOW)
                pygame.draw.circle(surface, c, rect.center, 14)
                surface.blit(tiny_font.render(str(item.count), True, WHITE), (rect.right - 18, rect.bottom - 18))
            
            if rect.collidepoint(m_x, m_y) and not drag_data:
                hover_info = {"source": "PLAYER", "idx": i, "item": item}
                pygame.draw.rect(surface, WHITE, rect, 2, border_radius=6)
    return hover_info

# 開啟寶箱的函式
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



# 任務系統與升級機制
class Task:
    def __init__(self, task_id, name, description, objective_type, objective_value, reward_type, reward_amount):
        self.task_id, self.name, self.description = task_id, name, description
        self.objective_type, self.objective_value = objective_type, objective_value
        self.current_progress, self.is_completed = 0, False
        self.reward_type, self.reward_amount = reward_type, reward_amount

    def check_completion(self):
        if not self.is_completed and self.current_progress >= self.objective_value:
            self.is_completed = True
            return True
        return False

    def apply_reward(self, player_obj):
        if self.reward_type == "scrap": persistent_stats["scrap"] += self.reward_amount
        elif self.reward_type == "exp": player_obj.exp += self.reward_amount * player_obj.exp_multiplier
        elif self.reward_type == "max_hp":
            persistent_stats["max_hp"] += self.reward_amount; player_obj.max_hp += self.reward_amount
            player_obj.hp = min(player_obj.max_hp, player_obj.hp + self.reward_amount)
        elif self.reward_type == "dmg_bonus":
            persistent_stats["dmg_bonus"] += self.reward_amount; player_obj.bullet_damage_bonus += self.reward_amount
        elif self.reward_type == "max_stamina":
            persistent_stats["max_stamina"] += self.reward_amount; player_obj.max_stamina += self.reward_amount; player_obj.stamina += self.reward_amount

class TaskSystem:
    def __init__(self):
        self.current_task, self.completed_tasks = None, []
        self.task_pool = [
            {"name": "廢料獵人", "desc": "收集 30 個廢料", "type": "collect", "value": 30, "reward_type": "scrap", "reward": 100},
            {"name": "廢料販子", "desc": "收集 50 個廢料", "type": "collect", "value": 50, "reward_type": "scrap", "reward": 150},
            {"name": "初級獵人", "desc": "消滅 20 個敵人", "type": "kill", "value": 20, "reward_type": "exp", "reward": 50},
            {"name": "精英獵人", "desc": "消滅 5 個精英敵人", "type": "kill_elite", "value": 5, "reward_type": "dmg_bonus", "reward": 3},
            {"name": "武裝分子", "desc": "造成 5000 點傷害", "type": "damage", "value": 5000, "reward_type": "scrap", "reward": 100},
            {"name": "長期作戰", "desc": "在突襲中存活 5 分鐘", "type": "survive", "value": 300, "reward_type": "scrap", "reward": 90},
        ]
        self.generate_new_task()

    def generate_new_task(self):
        available = [t for i, t in enumerate(self.task_pool) if i not in self.completed_tasks]
        if available:
            td = random.choice(available)
            self.current_task = Task(self.task_pool.index(td), td["name"], td["desc"], td["type"], td["value"], td["reward_type"], td["reward"])
        else: self.current_task = None

    def complete_task(self):
        if self.current_task:
            self.completed_tasks.append(self.current_task.task_id); self.generate_new_task(); return True
        return False

    def update_progress(self, objective_type, amount):
        if self.current_task and self.current_task.objective_type == objective_type:
            self.current_task.current_progress += amount
            if self.current_task.check_completion(): return True
        return False

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
    {"title": "急救模組", "desc": ["立即恢復血量", "最多恢復 60"], "type": "life", "weight": 1},
    {"title": "相位護盾", "desc": ["受傷免傷延長", "更能脫離包圍"], "type": "life", "weight": 1},
    {"title": "爆燃推進", "desc": ["衝刺速度增加", "瞬間拉開距離"], "type": "support", "weight": 3},
    {"title": "寬幅槍口", "desc": ["同彈道追加子彈", "不再增加散射"], "type": "attack", "weight": 5},
    {"title": "導引模組", "desc": ["近距離小幅追蹤", "不會自動鎖全場"], "type": "attack", "weight": 5},
    {"title": "再生奈米", "desc": ["緩慢持續回血", "脫戰續航提升"], "type": "life", "weight": 1},
    {"title": "擴容彈匣", "desc": ["挑戰限定", "增加彈藥庫上限"], "type": "attack", "weight": 4, "challenge_only": True},
    {"title": "戰術無人機", "desc": ["召喚跟隨無人機", "自動鎖定攻擊敵人"], "type": "attack", "weight": 4}
]

def choose_upgrade_cards():
    global current_upgrade_choices, selected_upgrade_position
    avail, weights = [], []
    for i, opt in enumerate(upgrade_options):
        if opt.get("challenge_only", False) and game_mode != "CHALLENGE": continue
        avail.append(i); weights.append(opt.get("weight", 1))
    current_upgrade_choices = []
    while len(current_upgrade_choices) < 3 and avail:
        idx = random.choices(avail, weights=weights, k=1)[0]
        current_upgrade_choices.append(idx)
        ridx = avail.index(idx); avail.pop(ridx); weights.pop(ridx)
    selected_upgrade_position = None

def apply_upgrade(idx, silent=False):
    global game_state, chosen_upgrades
    opt = upgrade_options[idx]
    found = False
    for u in chosen_upgrades:
        if u["title"] == opt["title"]: u["count"] += 1; found = True; break
    if not found: chosen_upgrades.append({"title": opt["title"], "count": 1})
    
    t = opt["title"]
    if t == "生命躍升": player.max_hp += 50; player.hp = player.max_hp
    elif t == "超頻運轉": player.shoot_delay_reduction += 2
    elif t == "能量飲料": player.stamina_regen += 0.2
    elif t == "彈幕擴張": player.bullet_count += 1
    elif t == "高能彈芯": player.bullet_damage_bonus += 5
    elif t == "備用電池": player.max_stamina += 25; player.stamina += 25
    elif t == "輕量推進": player.dash_cost = max(10, player.dash_cost - 5)
    elif t == "離子靴": player.base_speed += 0.5
    elif t == "磁吸核心": player.magnet_radius += 50
    elif t == "穩定槍管": player.bullet_spread = max(3.0, player.bullet_spread - 3.0)
    elif t == "急救模組": player.hp = min(player.max_hp, player.hp + 60)
    elif t == "相位護盾": player.invincible_duration += 15
    elif t == "爆燃推進": player.dash_speed += 3
    elif t == "寬幅槍口": player.extra_same_path_bullets += 1
    elif t == "導引模組": player.guidance_level += 1
    elif t == "電弧光環": player.aura_level += 1
    elif t == "再生奈米": player.regen_level += 1
    elif t == "擴容彈匣": player.mag_size_bonus += 10; player.ammo += 10
    elif t == "戰術無人機": player.drone_level += 1
    
    if not silent: game_state = "PLAYING"; play_sound("levelup")

# 裝備與背包機制
persistent_stats = {"max_hp": 0, "dmg_bonus": 0, "speed_bonus": 0.0, "max_stamina": 0, "max_shield": 0, "max_energy": 0, "scrap": 0, "weapon_stash": [], "general_stash": [None]*36}
class Weapon:
    def __init__(self, name, shoot_delay, bullet_type, damage, sound_name="shoot_normal", recoil=2.0):
        self.base_name, self.shoot_delay, self.bullet_type, self.damage, self.sound_name, self.base_recoil = name, shoot_delay, bullet_type, damage, sound_name, recoil
        self.rarity, self.affixes = "白", []
    @property 
    def full_name(self): return f"【{self.rarity}】{self.base_name}"

WEAPON_TYPES = {
    "手槍": Weapon("手槍", 20, "normal", 20, "snd_pistol", 1.5),
    "狙擊槍": Weapon("狙擊槍", 50, "piercing", 45, "snd_sniper", 8.0),
    "散彈槍": Weapon("散彈槍", 30, "shotgun", 20, "snd_shotgun", 5.0),
    "機槍": Weapon("機槍", 15, "piercing", 20, "snd_mg", 1.0),
    "火焰噴射器": Weapon("火焰噴射器", 3, "flamethrower", 4, "snd_flamethrower", 0.2),
    "雷射槍": Weapon("雷射槍", 25, "laser", 25, "snd_laser", 0.5),
    "電磁炮": Weapon("電磁炮", 60, "cannon", 50, "snd_cannon", 10.0),
    "冰霜發射器": Weapon("冰霜發射器", 5, "frost", 6, "snd_frost", 0.2),
    "重型機槍": Weapon("重型機槍", 17, "piercing", 25, "snd_heavy_mg", 1.5),
    "步槍": Weapon("步槍", 40, "piercing", 30, "snd_rifle", 3.0),
    "火焰榴彈發射器": Weapon("火焰榴彈發射器", 65, "flame_grenade", 70, "snd_grenade", 6.0),
    "電漿發射器": Weapon("電漿發射器", 30, "plasma", 30, "snd_plasma", 2.0)
}
def get_rarity_color(r): return {"金": (255, 215, 0), "紫": (200, 50, 255), "藍": (50, 150, 255)}.get(r, (200, 200, 200))
def apply_weapon_stats(w):
    base = WEAPON_TYPES[w.base_name]
    w.damage = int(base.damage * {"白":1.0, "藍":1.3, "紫":1.6, "金":2.2}.get(w.rarity, 1.0))
    w.shoot_delay = max(2, int(base.shoot_delay * 0.60)) if "速射" in w.affixes else base.shoot_delay
def generate_weapon(base_name, rarity="白"):
    base = WEAPON_TYPES[base_name]
    w = Weapon(base.base_name, base.shoot_delay, base.bullet_type, base.damage, base.sound_name, base.base_recoil)
    w.rarity = rarity; c = {"白":0, "藍":1, "紫":2, "金":3}.get(rarity, 0)
    pool = ["速射", "散射", "吸血", "爆擊"]
    if base.bullet_type not in ["piercing", "laser", "cannon", "flamethrower"]: pool.append("穿透") 
    if base.bullet_type not in ["flamethrower", "flame_grenade"]: pool.append("燃燒") 
    w.affixes = random.sample(pool, min(c, len(pool))) if c > 0 else []
    apply_weapon_stats(w); return w
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
                add = min(space, item.count); t_item.count += add; item.count -= add
                if item.count <= 0: return True
    if item.count > 0:
        for i in range(len(to_list)):
            if to_list[i] is None: to_list[i] = item; return True
    return False
def put_item_in_slot(source, idx, item):
    target_list = player.inventory if source == "PLAYER" else persistent_stats["general_stash"]
    old_item = target_list[idx]
    if old_item and old_item.type == item.type and item.type != "WEAPON":
        space = old_item.max_stack - old_item.count
        if space > 0:
            add = min(space, item.count); old_item.count += add; item.count -= add
            if item.count <= 0: return None
    target_list[idx] = item; return old_item

# 實體物件
class Particle:
    def __init__(self, x, y, color):
        self.x, self.y = x, y
        self.vel_x, self.vel_y = random.uniform(-6, 6), random.uniform(-6, 6)
        self.timer, self.size, self.color = random.randint(15, 30), random.randint(4, 8), color
    def update(self):
        self.x += self.vel_x; self.y += self.vel_y; self.timer -= 1; self.size = max(0, self.size - 0.25)
    def draw(self, surface):
        if self.size > 0: pygame.draw.rect(surface, self.color, (int(self.x - camera_x), int(self.y - camera_y), int(self.size), int(self.size)))

class DamageText:
    def __init__(self, x, y, damage, color, is_crit=False):
        self.x, self.y, self.damage, self.color, self.is_crit = x, y, damage, color, is_crit
        self.timer, self.vel_y, self.alpha, self.offset_x = (50, -3.5, 255, random.randint(-15,15)) if is_crit else (35, -2.0, 255, random.randint(-15,15))
        self.font = large_font if is_crit else small_font
    def update(self):
        self.y += self.vel_y; self.vel_y += 0.2; self.timer -= 1; self.alpha = max(0, int((self.timer / 35) * 255))
    def draw(self, surface):
        if self.timer > 0:
            ts = self.font.render(f"-{int(self.damage)}" + ("!" if self.is_crit else ""), True, self.color); ts.set_alpha(self.alpha)
            surface.blit(ts, (int(self.x + self.offset_x - camera_x - ts.get_width()//2), int(self.y - camera_y)))

class DashTrail:
    def __init__(self, x, y, size): self.x, self.y, self.size, self.life = x, y, size, 15
    def update(self): self.life -= 1
    def draw(self, surface):
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0, 200, 255, max(0, int((self.life / 15) * 150))), (0, 0, self.size, self.size), border_radius=5)
        surface.blit(surf, (int(self.x - camera_x - self.size/2), int(self.y - camera_y - self.size/2)))

class DropItem:
    def __init__(self, x, y, item_type="EXP", count=1, weapon_obj=None):
        self.x, self.y, self.item_type, self.count, self.weapon_obj = x, y, item_type, count, weapon_obj
        self.rect = pygame.Rect(0, 0, 20, 20); self.anim_offset = random.random() * 10
    def update(self, p_x, p_y, mag_rad):
        if self.item_type not in ["EXP", "MAGNET", "BOMB", "SHIELD"]: return 
        dist_sq = (self.x - p_x)**2 + (self.y - p_y)**2
        if 0 < dist_sq < mag_rad**2:
            dist = math.sqrt(dist_sq); speed = 25 if mag_rad > 1000 else 8
            self.x += ((p_x - self.x) / dist) * speed; self.y += ((p_y - self.y) / dist) * speed 
        self.rect.center = (int(self.x), int(self.y))
    def draw(self, surface):
        draw_x, draw_y = int(self.x - camera_x), int(self.y - camera_y)
        float_y = draw_y + math.sin(pygame.time.get_ticks()*0.005 + self.anim_offset) * 3
        if self.item_type == "WEAPON":
            c = get_rarity_color(self.weapon_obj.rarity)
            pygame.draw.circle(surface, c, (draw_x, int(float_y)), 15, 2)
            txt = tiny_font.render(self.weapon_obj.full_name, True, c); surface.blit(txt, (draw_x - txt.get_width()//2, int(float_y) - 25))
            return
        if self.item_type == "EXP": pygame.draw.polygon(surface, EXP_COLOR, [(draw_x, float_y-6), (draw_x+6, float_y), (draw_x, float_y+6), (draw_x-6, float_y)])
        elif self.item_type == "MED": pygame.draw.rect(surface, HP_COLOR, (draw_x-6, float_y-4, 12, 8)); pygame.draw.rect(surface, WHITE, (draw_x-2, float_y-6, 4, 12))
        elif self.item_type == "SHIELD": pygame.draw.circle(surface, SHIELD_COLOR, (draw_x, int(float_y)), 6)
        elif self.item_type == "MAGNET": pygame.draw.circle(surface, YELLOW, (draw_x, int(float_y)), 7); pygame.draw.circle(surface, RED, (draw_x, int(float_y)), 7, 2)
        elif self.item_type == "BOMB": pygame.draw.circle(surface, (50, 50, 50), (draw_x, int(float_y)), 8)
        elif self.item_type == "SCRAP": pygame.draw.polygon(surface, SCRAP_COLOR, [(draw_x, float_y-4), (draw_x+4, float_y), (draw_x, float_y+4), (draw_x-4, float_y)])
        elif self.item_type == "KEY": pygame.draw.rect(surface, YELLOW, (draw_x-8, float_y-2, 16, 4)); pygame.draw.circle(surface, YELLOW, (draw_x-6, int(float_y)), 4, 2)
        if self.count > 1 and self.item_type in ["SCRAP", "MED", "KEY"]: surface.blit(tiny_font.render(str(self.count), True, WHITE), (draw_x + 5, int(float_y) + 5))

class Chest:
    def __init__(self, x, y, c_type="NORMAL"):
        self.x, self.y, self.type, self.state, self.open_progress = x, y, c_type, "CLOSED", 0
        self.rect = pygame.Rect(0, 0, 50, 40); self.rect.center = (int(self.x), int(self.y))
        self.color = (139, 69, 19) if c_type == "NORMAL" else (218, 165, 32)
    def draw(self, surface):
        dx, dy = int(self.x - camera_x), int(self.y - camera_y)
        draw_rect = self.rect.copy(); draw_rect.center = (dx, dy)
        if self.state == "CLOSED":
            pygame.draw.rect(surface, self.color, draw_rect, border_radius=5)
            pygame.draw.rect(surface, WHITE if self.type=="NORMAL" else YELLOW, draw_rect, 2, border_radius=5)
            if self.type == "LOCKED": pygame.draw.circle(surface, BLACK, (dx, dy), 6) 
            if self.open_progress > 0: pygame.draw.rect(surface, GRAY, (dx-25, dy-30, 50, 6)); pygame.draw.rect(surface, GREEN, (dx-25, dy-30, 50*(self.open_progress/40), 6))
        else: pygame.draw.rect(surface, (80,40,10), pygame.Rect(dx-25, dy+2, 50, 15), border_radius=3)

class PlayerLostItem:
    def __init__(self, x, y, level, exp, upgrades, inv_items, w1, w2):
        self.x, self.y, self.level, self.exp, self.upgrades = x, y, level, exp, upgrades
        self.inventory, self.w1, self.w2 = inv_items, w1, w2
        self.rect = pygame.Rect(0, 0, 50, 50); self.rect.center = (int(self.x), int(self.y))
    def draw(self, surface):
        self.rect.center = (int(self.x), int(self.y))
        draw_x, draw_y = int(self.x - camera_x), int(self.y - camera_y)
        p = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 5)
        pygame.draw.circle(surface, YELLOW, (draw_x, draw_y), 20 + p)
        pygame.draw.circle(surface, WHITE, (draw_x, draw_y), 22 + p, 2)
        txt = small_font.render("遺失物(觸碰拾取)", True, YELLOW)
        surface.blit(txt, (draw_x - txt.get_width()//2, draw_y - 35))

class ExtractionPoint:
    def __init__(self): self.x, self.y, self.radius = random.randint(800, MAP_WIDTH - 800), random.randint(800, MAP_HEIGHT - 800), 150
    def draw(self, surface):
        draw_x, draw_y = int(self.x - camera_x), int(self.y - camera_y)
        p = int(abs(math.sin(pygame.time.get_ticks() * 0.003)) * 20)
        pygame.draw.circle(surface, GREEN, (draw_x, draw_y), self.radius + p, 3)
        surface.blit(font.render("撤離點", True, GREEN), (draw_x - 35, draw_y - 20))

class DummyTarget:
    def __init__(self, x, y):
        self.x, self.y = x, y; self.rect = pygame.Rect(0, 0, 40, 60); self.rect.center = (int(self.x), int(self.y))
        self.hit_log, self.shake_timer = [], 0
    def update(self):
        now = pygame.time.get_ticks()
        self.hit_log = [(t, dmg) for t, dmg in self.hit_log if now - t <= 3000]
        if self.shake_timer > 0: self.shake_timer -= 1
        self.rect.center = (int(self.x), int(self.y))
    def draw(self, surface):
        dx, dy = int(self.x - camera_x) + (random.randint(-2,2) if self.shake_timer>0 else 0), int(self.y - camera_y) + (random.randint(-2,2) if self.shake_timer>0 else 0)
        pygame.draw.rect(surface, (150, 100, 80), pygame.Rect(dx-20, dy-30, 40, 60), border_radius=10)
        pygame.draw.circle(surface, RED, (dx, dy - 10), 8); pygame.draw.circle(surface, WHITE, (dx, dy - 10), 4)
        dps = int(sum(dmg for t, dmg in self.hit_log) / 3.0) if self.hit_log else 0
        dps_txt = small_font.render(f"DPS: {dps}", True, CYAN if dps > 0 else GRAY)
        surface.blit(dps_txt, (dx - dps_txt.get_width()//2, dy - 50))

# 戰鬥單位 (玩家與彈藥)
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
                    mx, my = pygame.mouse.get_pos(); wx, wy = mx + camera_x, my + camera_y
                    dx, dy = wx - self.x, wy - self.y; ddist = math.sqrt(dx**2 + dy**2)
                    if ddist > 0: self.dash_dir_x, self.dash_dir_y = dx / ddist, dy / ddist
                    
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
        
    def draw(self, surface, current_wep=None):
        draw_player = True
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        draw_rect = self.rect.copy(); draw_rect.center = draw_center
        
        if self.invincible_timer > 0 and not self.god_mode:
            if (self.invincible_timer // 4) % 2 == 0: draw_player = False
                
        if draw_player:
            pygame.draw.rect(surface, YELLOW if self.god_mode else BLUE, draw_rect)
            if self.stamina < self.dash_cost: pygame.draw.rect(surface, GRAY, draw_rect, 3)

            if current_wep:
                mx, my = pygame.mouse.get_pos(); dx, dy = (mx + camera_x) - self.x, (my + camera_y) - self.y
                dist = math.sqrt(dx**2 + dy**2); dir_x, dir_y = (dx / dist, dy / dist) if dist > 0 else (1, 0)
                end_x, end_y = self.x + dir_x * 25 - camera_x, self.y + dir_y * 25 - camera_y
                wep_color = YELLOW
                if current_wep.bullet_type == "piercing": wep_color = PURPLE
                elif current_wep.bullet_type == "flamethrower": wep_color = ORANGE
                elif current_wep.bullet_type == "laser": wep_color = CYAN
                elif current_wep.bullet_type == "cannon": wep_color = WHITE
                elif current_wep.bullet_type == "frost": wep_color = (100, 200, 255)
                elif current_wep.bullet_type == "flame_grenade": wep_color = RED
                
                pygame.draw.line(surface, GRAY, (self.x - camera_x, self.y - camera_y), (end_x, end_y), 6)
                pygame.draw.circle(surface, wep_color, (int(end_x), int(end_y)), 4)

        if self.aura_level > 0:
            pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10)
            pygame.draw.circle(surface, (0, 180, 255), draw_rect.center, 95 + self.aura_level * 25 + pulse, 2)
            
        if self.drone_level > 0:
            drone_x, drone_y = draw_center[0] + math.cos(self.drone_angle) * 55, draw_center[1] + math.sin(self.drone_angle) * 55
            pygame.draw.circle(surface, (150, 200, 255), (int(drone_x), int(drone_y)), 10)
            pygame.draw.circle(surface, BLUE, (int(drone_x), int(drone_y)), 10, 2); pygame.draw.circle(surface, RED, (int(drone_x), int(drone_y)), 4)

class Bullet:
    def __init__(self, x, y, target_x, target_y, weapon, guidance_level=0, dmg_bonus=0):
        self.x, self.y = x, y
        crit_chance, crit_mult = (0.35, 3.0) if "爆擊" in weapon.affixes else (0.10, 2.0)
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
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        pygame.draw.circle(surface, self.color, draw_center, self.radius)
        if self.is_crit: pygame.draw.circle(surface, RED, draw_center, self.radius+2, 1)

class EnemyBullet:
    def __init__(self, x, y, dir_x, dir_y, color=ORANGE, core_color=WHITE, style="round", is_homing=False, weapon=None):
        self.x, self.y, self.dir_x, self.dir_y = x, y, dir_x, dir_y
        dist = math.sqrt(dir_x**2 + dir_y**2)
        if dist > 0: self.dir_x /= dist; self.dir_y /= dist
        self.is_homing, self.weapon, self.radius, self.speed = is_homing, weapon, 8, 7
        self.damage, self.b_type = 15, "normal"
        self.color, self.core_color, self.style = color, core_color, style
        if weapon:
            self.b_type, self.damage = weapon.bullet_type, int(weapon.damage * 0.8)
            if self.b_type == "piercing": self.color, self.speed, self.radius = PURPLE, 15, 7
            elif self.b_type == "flamethrower": self.color, self.speed, self.radius = ORANGE, 8, 12
            elif self.b_type == "laser": self.color, self.speed, self.radius = CYAN, 25, 4
            elif self.b_type == "cannon": self.color, self.speed, self.radius = WHITE, 8, 15
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        self.lifespan, self.explode = 150 if is_homing else 9999, False

    def update(self, target_x=None, target_y=None):
        self.lifespan -= 1
        if self.lifespan <= 0: self.explode = True; return

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
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        pygame.draw.circle(surface, BLACK, draw_center, self.radius + 4)
        pygame.draw.circle(surface, self.color, draw_center, self.radius + 2)
        if hasattr(self, 'style'):
            if self.style == "diamond":
                pts = [
                    (draw_center[0], draw_center[1] - self.radius - 1), (draw_center[0] + self.radius + 1, draw_center[1]),
                    (draw_center[0], draw_center[1] + self.radius + 1), (draw_center[0] - self.radius - 1, draw_center[1])
                ]
                pygame.draw.polygon(surface, getattr(self, 'core_color', WHITE), pts)
            elif self.style == "slash":
                side = pygame.math.Vector2(self.dir_x, self.dir_y).rotate(90)
                front = pygame.math.Vector2(draw_center) + pygame.math.Vector2(self.dir_x, self.dir_y) * (self.radius + 4)
                back = pygame.math.Vector2(draw_center) - pygame.math.Vector2(self.dir_x, self.dir_y) * (self.radius + 4)
                left = pygame.math.Vector2(draw_center) + side * 4
                right = pygame.math.Vector2(draw_center) - side * 4
                pts = [(int(front.x), int(front.y)), (int(left.x), int(left.y)), (int(back.x), int(back.y)), (int(right.x), int(right.y))]
                pygame.draw.polygon(surface, getattr(self, 'core_color', WHITE), pts)
            else: pygame.draw.circle(surface, getattr(self, 'core_color', WHITE), draw_center, max(3, self.radius // 2))
        else: pygame.draw.circle(surface, getattr(self, 'core_color', WHITE), draw_center, max(3, self.radius // 2))

class Enemy:
    def __init__(self, level, is_elite=False, spawn_x=MAP_WIDTH/2, spawn_y=MAP_HEIGHT/2):
        self.is_elite, self.size = is_elite, 35 if is_elite else 25
        difficulty_mult = 1.75 if game_mode == "CHALLENGE" else 1.0
        self.speed = ((random.uniform(3.0, 5.5) if is_elite else random.uniform(2.5, 4.5)) + level * 0.05) * (1.2 if game_mode == "CHALLENGE" else 1.0)
        self.max_hp = int(((60 + level * 25) if is_elite else (20 + level * 8)) * difficulty_mult)
        self.hp, self.max_shield = self.max_hp, int(((20 + level * 8) if is_elite else (10 + level * 4)) * difficulty_mult)
        self.shield, self.damage = self.max_shield, int(((35 + level * 3) if is_elite else (15 + level * 1.5)) * difficulty_mult)
        self.frost_timer, self.burn_timer, self.dir_x, self.dir_y, self.hit_timer = 0, 0, 1, 0, 0
        
        self.combat_type = random.choice(["melee", "ranged"]) if is_elite else random.choices(["melee", "ranged", "kamikaze"], weights=[0.45, 0.45, 0.1])[0]
        if self.combat_type == "kamikaze": 
            self.color, self.speed, self.max_hp, self.damage = ORANGE, self.speed*1.4, int(self.max_hp*0.6), int(self.damage*1.5)
            self.hp = self.max_hp; self.weapon = None; self.shoot_cd = 0
        elif self.combat_type == "ranged":
            weapons = list(WEAPON_TYPES.values())
            self.weapon = random.choice(weapons) if weapons else None
            self.shoot_cd = getattr(self.weapon, "shoot_delay", 20) * 3 + random.randint(20, 60) if self.weapon else 120
        else: self.weapon, self.shoot_cd = None, 0
        
        spawn_dist_x, spawn_dist_y = WIDTH / 2 + 50, HEIGHT / 2 + 50
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top': self.x, self.y = spawn_x + random.randint(-int(spawn_dist_x), int(spawn_dist_x)), spawn_y - spawn_dist_y
        elif edge == 'bottom': self.x, self.y = spawn_x + random.randint(-int(spawn_dist_x), int(spawn_dist_x)), spawn_y + spawn_dist_y
        elif edge == 'left': self.x, self.y = spawn_x - spawn_dist_x, spawn_y + random.randint(-int(spawn_dist_y), int(spawn_dist_y))
        elif edge == 'right': self.x, self.y = spawn_x + spawn_dist_x, spawn_y + random.randint(-int(spawn_dist_y), int(spawn_dist_y))
            
        self.x, self.y = max(0, min(self.x, MAP_WIDTH)), max(0, min(self.y, MAP_HEIGHT))
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
                elif self.weapon: enemy_bullets.append(EnemyBullet(self.x, self.y, self.dir_x, self.dir_y, weapon=self.weapon))
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
        draw_center = (int(self.rect.centerx - camera_x), int(self.rect.centery - camera_y))
        draw_rect = self.rect.copy(); draw_rect.center = draw_center
        
        if self.combat_type == "kamikaze":
            pygame.draw.circle(surface, ORANGE, draw_center, self.size // 2)
            for i in range(8):
                angle = pygame.time.get_ticks() * 0.01 + i * math.pi / 4
                end_x, end_y = draw_center[0] + math.cos(angle) * (self.size * 0.8), draw_center[1] + math.sin(angle) * (self.size * 0.8)
                pygame.draw.line(surface, YELLOW, draw_center, (end_x, end_y), 3)
        else:
            color = WHITE if self.hit_timer > 0 else ((100, 200, 255) if self.frost_timer > 0 else ((150, 0, 150) if self.is_elite else RED))
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
            pygame.draw.rect(surface, GRAY, (draw_rect.x, draw_rect.y - 14, self.size, 4)); pygame.draw.rect(surface, (0, 150, 255), (draw_rect.x, draw_rect.y - 14, self.size * (max(0, self.shield)/self.max_shield), 4))
        if self.hp < self.max_hp:
            pygame.draw.rect(surface, GRAY, (draw_rect.x, draw_rect.y - 8, self.size, 4)); pygame.draw.rect(surface, GREEN, (draw_rect.x, draw_rect.y - 8, self.size * (max(0, self.hp)/self.max_hp), 4))

# 核心 Boss 系統
class CoreBoss:
    def __init__(self, spawn_level=5, player_x=0, player_y=0):
        spawn_center = pygame.math.Vector2(player_x, player_y)
        end_x, end_y = max(120, min(MAP_WIDTH - 120, spawn_center.x)), max(140, min(MAP_HEIGHT - 140, spawn_center.y - 220))
        self.entrance_start = pygame.math.Vector2(end_x, max(80, end_y - 420)); self.entrance_end = pygame.math.Vector2(end_x, end_y)
        self.pos = self.entrance_start.copy()
        self.x, self.y = self.pos.x, self.pos.y
        self.size = 60
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.spawn_level = spawn_level
        difficulty_multiplier = 1.75 if game_mode == "CHALLENGE" else 1.0
        self.max_hp = int((1000 + spawn_level * 300) * difficulty_multiplier)
        self.hp = self.max_hp
        self.speed = 4.0 * difficulty_multiplier
        
        self.state, self.state_timer, self.defeat_timer = "ENTRANCE", 0, 0
        self.color, self.entrance_duration, self.name = YELLOW, 240, "旋轉彈幕核心"
        self.collision_damage = int(40 * difficulty_multiplier)
        self.orbit_angle, self.fire_timer, self.fire_angle = random.random() * math.pi * 2, 0, 0
        self.frost_timer, self.burn_timer, self.hit_timer = 0, 0, 0

    def update(self, player_x, player_y, bullets, enemies, enemy_bullets):
        self.state_timer += 1
        player_pos = pygame.math.Vector2(player_x, player_y)
        if getattr(self, 'hit_timer', 0) > 0: self.hit_timer -= 1
        if self.frost_timer > 0: self.frost_timer -= 1
        if self.burn_timer > 0:
            self.burn_timer -= 1
            if self.burn_timer % 15 == 0: self.hp -= 10; particles.append(Particle(self.x, self.y, ORANGE))
        eff_speed = self.speed * 0.5 if self.frost_timer > 0 else self.speed
        
        if self.state == "ENTRANCE":
            progress = min(1, self.state_timer / self.entrance_duration)
            self.pos = self.entrance_start.lerp(self.entrance_end, 1 - (1 - progress) ** 3)
            glow = int(100 + 155 * progress); self.color = (glow, glow, 0)
            if self.state_timer >= self.entrance_duration: self.state, self.state_timer = "SHOOT", 0
        elif self.state == "EVADE":
            self.color = YELLOW
            direction = player_pos - self.pos
            if direction.length() > 0:
                direction.normalize_ip(); tangent = pygame.math.Vector2(-direction.y, direction.x) 
                dodged = False
                for b in bullets:
                    if self.pos.distance_to(pygame.math.Vector2(b.x, b.y)) < 150:
                        flee_dir = self.pos - pygame.math.Vector2(b.x, b.y)
                        if flee_dir.length() > 0: flee_dir.normalize_ip()
                        self.pos += flee_dir * (eff_speed * 1.8); dodged = True; break 
                if not dodged:
                    self.pos += tangent * eff_speed; dist = self.pos.distance_to(player_pos)
                    if dist > 250: self.pos += direction * eff_speed
                    elif dist < 150: self.pos -= direction * eff_speed
            if self.state_timer > 120: self.state, self.state_timer = "CHARGE", 0
        elif self.state == "CHARGE":
            self.color = (255, 100, 0)
            if self.state_timer > 60: self.state, self.state_timer = "SHOOT", 0
        elif self.state == "SHOOT":
            self.color = RED
            self.orbit_angle += 0.035 + min(self.spawn_level * 0.001, 0.018); self.fire_angle += 0.09
            orbit_target = player_pos + pygame.math.Vector2(math.cos(self.orbit_angle), math.sin(self.orbit_angle)) * 230
            move_dir = orbit_target - self.pos
            if move_dir.length() > 4: move_dir.scale_to_length(min(eff_speed * 1.25, move_dir.length())); self.pos += move_dir
        elif self.state == "DEFEAT":
            self.defeat_timer += 1
            self.color = (255, max(0, 150 - self.defeat_timer * 3), 0)
            self.pos.y -= 1; self.pos.x += math.sin(self.defeat_timer * 0.2) * 1.5
            
        self.pos.x = max(self.size, min(MAP_WIDTH-self.size, self.pos.x))
        self.pos.y = max(self.size, min(MAP_HEIGHT-self.size, self.pos.y))
        self.x, self.y = self.pos.x, self.pos.y
        self.rect.center = (round(self.x), round(self.y))
        self.emit_attacks(enemy_bullets)

    def can_take_damage(self): return self.state not in ("ENTRANCE", "EVADE", "DEFEAT")

    def emit_attacks(self, enemy_bullets):
        if self.state == "SHOOT":
            self.fire_timer += 1
            fire_interval = 12 if self.spawn_level < 10 else 9
            if self.fire_timer % fire_interval != 0: return
            shots = 8 if self.spawn_level < 10 else 10
            for i in range(shots):
                angle = self.fire_angle + i * (math.pi * 2 / shots)
                enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, math.cos(angle), math.sin(angle), color=(255, 30, 95), core_color=(255, 245, 120), style="diamond"))
            if self.spawn_level >= 10:
                for i in range(shots):
                    angle = -self.fire_angle * 0.75 + i * (math.pi * 2 / shots) + math.pi / shots
                    enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, math.cos(angle), math.sin(angle), color=(255, 115, 30), core_color=(255, 255, 210), style="diamond"))
            play_sound("shoot_cannon")

    def get_intro_title(self): return f"{self.name} 登場！"
    def get_intro_lines(self): return ["警告：第一階段 BOSS 出現！", "它會繞著你旋轉，並持續發射彈幕。", "保持移動，抓住空隙反擊！"]
    def get_state_message(self):
        if self.state == "EVADE": return "閃避階段 - 暫時不易命中", YELLOW
        if self.state == "CHARGE": return "蓄力階段 - 可以攻擊", ORANGE
        if self.state == "SHOOT": return "旋轉彈幕階段 - 可以攻擊", RED
        return "BOSS 戰鬥中", WHITE

    def draw(self, surface):
        def draw_threat_core(size, color):
            cx, cy = (round(self.x - camera_x), round(self.y - camera_y))
            half, horn = size // 2, size // 3
            pts = [(cx, cy - half - horn), (cx + half, cy - half // 2), (cx + half + horn, cy), (cx + half, cy + half // 2), (cx, cy + half + horn), (cx - half, cy + half // 2), (cx - half - horn, cy), (cx - half, cy - half // 2)]
            pygame.draw.polygon(surface, color, pts); pygame.draw.polygon(surface, WHITE, pts, 3)
            pygame.draw.circle(surface, RED, (cx, cy), max(8, size // 5)); pygame.draw.circle(surface, BLACK, (cx, cy), max(3, size // 10))
            for i in range(4):
                angle = pygame.time.get_ticks() * 0.002 + i * math.pi / 2
                pygame.draw.circle(surface, ORANGE, (int(cx + math.cos(angle) * (half + 22)), int(cy + math.sin(angle) * (half + 22))), 5)

        core_color = WHITE if getattr(self, 'hit_timer', 0) > 0 else ((100, 200, 255) if self.frost_timer > 0 else self.color)
        if self.state == "ENTRANCE":
            pulse = abs(math.sin(self.state_timer * 0.1))
            current_size = int(self.size * (0.8 + pulse * 0.4))
            for i in range(3):
                ring_size = current_size // 2 + 20 + i * 15; alpha_val = int(200 * (1 - i/3) * (1 - pulse))
                if alpha_val > 0: pygame.draw.circle(surface, WHITE, (round(self.x - camera_x), round(self.y - camera_y)), ring_size, 2)
            draw_threat_core(current_size, core_color)
            for i in range(8):
                angle = (self.state_timer * 0.05 + i * math.pi / 4)
                pygame.draw.circle(surface, YELLOW, (int(self.x - camera_x + math.cos(angle) * (self.size + 30)), int(self.y - camera_y + math.sin(angle) * (self.size + 30))), 3)
        elif self.state == "DEFEAT":
            progress = min(1, self.defeat_timer / 60)
            center = (round(self.x - camera_x), round(self.y - camera_y))
            for i in range(7):
                radius = int(self.size * 0.6 + progress * 150 + i * 14)
                pygame.draw.circle(surface, (255, max(60, 210 - i * 22), 30 + i * 18), center, radius, 3)
            core_size = max(1, int(self.size * (1 - progress * 0.85)))
            core_points = [(int(center[0] + math.cos(self.defeat_timer * 0.08 + i * math.pi / 4) * (core_size + (14 if i % 2 == 0 else 2))), int(center[1] + math.sin(self.defeat_timer * 0.08 + i * math.pi / 4) * (core_size + (14 if i % 2 == 0 else 2)))) for i in range(8)]
            if len(core_points) >= 3: pygame.draw.polygon(surface, (255, 210, 60), core_points)
            burst = int(8 + progress * 18)
            for i in range(burst):
                angle = i * (math.pi * 2 / max(1, burst)) + self.defeat_timer * 0.3
                distance = self.size + 20 + progress * 130
                pygame.draw.circle(surface, RED if i % 2 else YELLOW, (int(center[0] + math.cos(angle) * distance), int(center[1] + math.sin(angle) * distance)), 5)
        else:
            aura_radius = self.size + 28 + int(abs(math.sin(self.state_timer * 0.08)) * 12)
            boss_center = (round(self.x - camera_x), round(self.y - camera_y))
            pygame.draw.circle(surface, RED if self.state == "CHARGE" else PURPLE, boss_center, aura_radius, 2)
            draw_threat_core(self.size, core_color)
            if self.state == "EVADE": pygame.draw.circle(surface, WHITE, boss_center, self.size//2 + 24, 3)
            elif self.state == "CHARGE": pygame.draw.circle(surface, RED, boss_center, self.size//2 + max(0, 30 - (self.state_timer // 2)) + 18, 3)

class ChargerBoss:
    def __init__(self, spawn_level=5, player_x=0, player_y=0):
        spawn_center = pygame.math.Vector2(player_x, player_y)
        side = -1 if random.random() < 0.5 else 1
        end_x, end_y = max(160, min(MAP_WIDTH - 160, spawn_center.x + side * 320)), max(160, min(MAP_HEIGHT - 160, spawn_center.y - 120))
        self.entrance_start = pygame.math.Vector2(max(100, min(MAP_WIDTH - 100, end_x + side * 520)), end_y)
        self.entrance_end = pygame.math.Vector2(end_x, end_y)
        self.pos = self.entrance_start.copy()
        self.x, self.y = self.pos.x, self.pos.y
        self.size = 76
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.spawn_level = spawn_level
        difficulty_multiplier = 1.75 if game_mode == "CHALLENGE" else 1.0
        self.max_hp = int((650 + spawn_level * 135) * difficulty_multiplier)
        self.hp = self.max_hp
        self.speed = (5.2 + min(spawn_level * 0.08, 1.6)) * difficulty_multiplier
        self.state, self.state_timer, self.defeat_timer = "ENTRANCE", 0, 0
        self.color, self.entrance_duration, self.name = (255, 70, 60), 130, "衝刺突擊者"
        self.collision_damage = int(50 * difficulty_multiplier)
        self.charge_direction, self.charge_target = pygame.math.Vector2(1, 0), self.pos.copy()
        self.side_fire_timer, self.spin_fire_timer, self.spin_angle = 0, 0, 0
        self.frost_timer, self.burn_timer, self.hit_timer = 0, 0, 0

    def update(self, player_x, player_y, bullets, enemies, enemy_bullets):
        self.state_timer += 1
        player_pos = pygame.math.Vector2(player_x, player_y)
        if getattr(self, 'hit_timer', 0) > 0: self.hit_timer -= 1
        if self.frost_timer > 0: self.frost_timer -= 1
        if self.burn_timer > 0:
            self.burn_timer -= 1
            if self.burn_timer % 15 == 0: self.hp -= 10; particles.append(Particle(self.x, self.y, ORANGE))
        eff_speed = self.speed * 0.5 if self.frost_timer > 0 else self.speed

        if self.state == "ENTRANCE":
            progress = min(1, self.state_timer / self.entrance_duration)
            self.pos = self.entrance_start.lerp(self.entrance_end, 1 - (1 - progress) ** 3)
            self.color = (175 + int(80 * abs(math.sin(self.state_timer * 0.12))), 45, 55)
            if self.state_timer >= self.entrance_duration: self.state, self.state_timer = "AIM", 0
        elif self.state == "AIM":
            self.color = (255, 210, 60)
            direction = player_pos - self.pos
            if direction.length() > 0:
                direction.normalize_ip(); self.charge_direction = direction; self.charge_target = self.pos + direction * 760
            if self.state_timer > 70: self.state, self.state_timer, self.side_fire_timer = "DASH", 0, 0
        elif self.state == "DASH":
            self.color = (255, 45, 45)
            self.pos += self.charge_direction * (eff_speed * 3.2); self.side_fire_timer += 1
            if self.state_timer > 44 or self.pos.distance_to(self.charge_target) < 45: self.state, self.state_timer = "RECOVER", 0
        elif self.state == "RECOVER":
            self.color = (170, 80, 255)
            self.spin_angle += 0.13; self.spin_fire_timer += 1
            if self.state_timer > 240: self.state, self.state_timer, self.spin_fire_timer = "AIM", 0, 0
        elif self.state == "DEFEAT":
            self.defeat_timer += 1
            self.color = (255, max(0, 120 - self.defeat_timer * 3), 60)
            self.pos.y -= 0.8; self.pos.x += math.sin(self.defeat_timer * 0.25) * 2

        self.pos.x = max(self.size, min(MAP_WIDTH - self.size, self.pos.x))
        self.pos.y = max(self.size, min(MAP_HEIGHT - self.size, self.pos.y))
        self.x, self.y = self.pos.x, self.pos.y
        self.rect.center = (round(self.x), round(self.y))
        self.emit_attacks(enemy_bullets)

    def can_take_damage(self): return self.state not in ("ENTRANCE", "DASH", "DEFEAT")

    def emit_attacks(self, enemy_bullets):
        if self.state == "DASH" and self.side_fire_timer % 5 == 0:
            side_a, side_b = self.charge_direction.rotate(90), self.charge_direction.rotate(-90)
            forward_angles = (-18, 0, 18) if self.spawn_level < 10 else (-28, -14, 0, 14, 28)
            for angle in forward_angles:
                forward = self.charge_direction.rotate(angle)
                enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, forward.x, forward.y, color=(255, 95, 70), core_color=(255, 245, 210), style="slash"))
            for side in (side_a, side_b):
                enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, side.x, side.y, color=(0, 210, 255), core_color=(210, 255, 255), style="slash"))
                back_spray = side - self.charge_direction * 0.45
                enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, back_spray.x, back_spray.y, color=(40, 235, 255), core_color=(220, 255, 255), style="slash"))
                if self.spawn_level >= 10:
                    ex, ey = (side + self.charge_direction * 0.35).x, (side + self.charge_direction * 0.35).y
                    enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, ex, ey, color=(50, 255, 170), core_color=(225, 255, 240), style="slash"))
            play_sound("shoot_cannon")
        elif self.state == "RECOVER" and self.spin_fire_timer % 10 == 0:
            shots = 10 if self.spawn_level < 10 else 12
            for i in range(shots):
                angle = self.spin_angle + i * (math.pi * 2 / shots)
                enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, math.cos(angle), math.sin(angle), color=(185, 60, 255), core_color=(255, 220, 255), style="round"))
                if self.spawn_level >= 10:
                    offset_angle = angle + math.pi / shots
                    enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, math.cos(offset_angle), math.sin(offset_angle), color=(245, 95, 255), core_color=(255, 235, 255), style="round"))
            play_sound("shoot_cannon")

    def get_intro_title(self): return f"{self.name} 登場！"
    def get_intro_lines(self): return ["警告：第二階段 BOSS 出現！", "黃色軌道代表即將衝刺，紅色時會高速突進。", "看到箭頭後立刻閃開，衝刺後再反擊。"]
    def get_state_message(self):
        if self.state == "AIM": return "瞄準階段 - 即將衝刺", YELLOW
        if self.state == "DASH": return "衝刺階段 - 暫時無法受傷", RED
        if self.state == "RECOVER": return "回復階段 - 可以攻擊", PURPLE
        return "BOSS 戰鬥中", WHITE

    def draw(self, surface):
        cx, cy = (round(self.x - camera_x), round(self.y - camera_y))
        pulse = abs(math.sin(self.state_timer * 0.13))
        direction = self.charge_direction if self.charge_direction.length_squared() > 0 else pygame.math.Vector2(1, 0)
        nose = (cx + int(direction.x * (self.size // 2 + 26)), cy + int(direction.y * (self.size // 2 + 26)))
        back = pygame.math.Vector2(cx, cy) - direction * (self.size // 2)
        left, right = back + direction.rotate(90) * (self.size // 2), back + direction.rotate(-90) * (self.size // 2)
        wing_left, wing_right = pygame.math.Vector2(cx, cy) + direction.rotate(90) * (self.size // 2 + 24), pygame.math.Vector2(cx, cy) + direction.rotate(-90) * (self.size // 2 + 24)

        core_color = WHITE if getattr(self, 'hit_timer', 0) > 0 else ((100, 200, 255) if self.frost_timer > 0 else self.color)

        if self.state == "ENTRANCE":
            for i in range(4): pygame.draw.circle(surface, (255, 90, 90), (cx, cy), self.size // 2 + 18 + i * 16 + int(pulse * 8), 2)
        elif self.state == "DEFEAT":
            progress = min(1, self.defeat_timer / 60)
            for i in range(4): pygame.draw.circle(surface, (255, 70 + i * 25, 45), (cx, cy), int(self.size * 0.7 + progress * 170 + i * 18), 3)
            for i in range(8):
                angle, distance = self.defeat_timer * 0.09 + i * math.pi / 4, 35 + progress * (110 + i * 8)
                shard_center, shard_dir = pygame.math.Vector2(cx, cy) + pygame.math.Vector2(math.cos(angle), math.sin(angle)) * distance, pygame.math.Vector2(math.cos(angle), math.sin(angle))
                shard_side, shard_len = shard_dir.rotate(90), max(8, int(26 * (1 - progress * 0.45)))
                pygame.draw.polygon(surface, ORANGE if i % 2 else RED, [(int(p.x), int(p.y)) for p in [shard_center + shard_dir * shard_len, shard_center - shard_dir * shard_len * 0.6 + shard_side * 8, shard_center - shard_dir * shard_len * 0.6 - shard_side * 8]])

        body_points = [nose, (int(wing_left.x), int(wing_left.y)), (int(left.x), int(left.y)), (cx - int(direction.x * 12), cy - int(direction.y * 12)), (int(right.x), int(right.y)), (int(wing_right.x), int(wing_right.y))]
        pygame.draw.circle(surface, RED if self.state == "DASH" else ORANGE if self.state == "AIM" else PURPLE, (cx, cy), self.size // 2 + 30 + int(pulse * 10), 2)
        if self.state == "DEFEAT":
            shake = math.sin(self.defeat_timer * 0.7) * 5
            broken_points = [(px + int(shake if i % 2 == 0 else -shake), py) for i, (px, py) in enumerate(body_points)]
            pygame.draw.polygon(surface, (120, 30, 35), broken_points); pygame.draw.polygon(surface, RED, broken_points, 2)
            pygame.draw.circle(surface, (255, 120, 40), (cx, cy), max(2, int(16 * (1 - progress))), 2)
        else:
            pygame.draw.polygon(surface, core_color, body_points); pygame.draw.polygon(surface, WHITE, body_points, 3)
            pygame.draw.circle(surface, BLACK, (cx, cy), 14); pygame.draw.circle(surface, RED if self.state == "DASH" else YELLOW, (cx, cy), 8)

        if self.state == "AIM":
            aim_ratio = min(1, self.state_timer / 70); shrink = 1 - aim_ratio
            start, end = pygame.math.Vector2(cx, cy) + direction * (35 + 70 * aim_ratio), pygame.math.Vector2(cx, cy) + direction * (360 - 120 * aim_ratio)
            side, lane_width, warning_color = direction.rotate(90), 24 * shrink + 7, RED if aim_ratio > 0.68 else YELLOW
            pygame.draw.line(surface, warning_color, (int(start.x), int(start.y)), (int(end.x), int(end.y)), 3)
            pygame.draw.line(surface, ORANGE, (int((start + side * lane_width).x), int((start + side * lane_width).y)), (int((end + side * lane_width).x), int((end + side * lane_width).y)), 2)
            pygame.draw.line(surface, ORANGE, (int((start - side * lane_width).x), int((start - side * lane_width).y)), (int((end - side * lane_width).x), int((end - side * lane_width).y)), 2)
            for i in range(4):
                if int(self.size // 2 + 20 + i * 22 * shrink) > self.size // 2 + 8: pygame.draw.circle(surface, warning_color, (cx, cy), int(self.size // 2 + 20 + i * 22 * shrink), 2)
            for i in range(5):
                mark = start.lerp(end, 0.18 + i * 0.16).lerp(pygame.math.Vector2(cx, cy), aim_ratio * 0.45)
                arrow_back, arrow_width = mark - direction * (16 * shrink + 5), 10 * shrink + 4
                pygame.draw.line(surface, WHITE, (int(mark.x), int(mark.y)), (int((arrow_back + side * arrow_width).x), int((arrow_back + side * arrow_width).y)), 2)
                pygame.draw.line(surface, WHITE, (int(mark.x), int(mark.y)), (int((arrow_back - side * arrow_width).x), int((arrow_back - side * arrow_width).y)), 2)
        elif self.state == "DASH":
            pygame.draw.circle(surface, WHITE, (cx, cy), self.size // 2 + 36, 3); side = direction.rotate(90)
            for i in range(6):
                trail_center, width = pygame.math.Vector2(cx, cy) - direction * (35 + i * 28), max(8, 32 - i * 4)
                pygame.draw.line(surface, ORANGE if i % 2 == 0 else YELLOW, (int((trail_center + side * width).x), int((trail_center + side * width).y)), (int((trail_center - side * width).x), int((trail_center - side * width).y)), 2)
            for i in range(3):
                mark = pygame.math.Vector2(cx, cy) + direction * (65 + i * 55); arrow_back = mark - direction * 22
                pygame.draw.line(surface, WHITE, (int(mark.x), int(mark.y)), (int((arrow_back + side * 14).x), int((arrow_back + side * 14).y)), 3)
                pygame.draw.line(surface, WHITE, (int(mark.x), int(mark.y)), (int((arrow_back - side * 14).x), int((arrow_back - side * 14).y)), 3)
        elif self.state == "RECOVER":
            for i in range(6):
                tip = pygame.math.Vector2(cx, cy) + pygame.math.Vector2(math.cos(self.spin_angle + i * math.pi / 3), math.sin(self.spin_angle + i * math.pi / 3)) * 95
                pygame.draw.line(surface, PURPLE, (cx, cy), (int(tip.x), int(tip.y)), 2)

class BerserkerBoss:
    def __init__(self, spawn_level=5, player_x=0, player_y=0):
        spawn_center = pygame.math.Vector2(player_x, player_y)
        end_x, end_y = max(180, min(MAP_WIDTH - 180, spawn_center.x)), max(180, min(MAP_HEIGHT - 180, spawn_center.y - 260))
        self.entrance_start = pygame.math.Vector2(end_x, max(100, end_y - 520)); self.entrance_end = pygame.math.Vector2(end_x, end_y)
        self.pos = self.entrance_start.copy()
        self.x, self.y = self.pos.x, self.pos.y
        self.size = 82
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.spawn_level = spawn_level
        difficulty_multiplier = 1.75 if game_mode == "CHALLENGE" else 1.0
        self.max_hp = int((980 + spawn_level * 190) * difficulty_multiplier)
        self.hp = self.max_hp
        self.phase, self.phase2_started = 1, False
        self.speed = (4.1 + min(spawn_level * 0.08, 1.7)) * difficulty_multiplier
        self.state, self.state_timer, self.defeat_timer = "ENTRANCE", 0, 0
        self.entrance_duration, self.name, self.color = 165, "腐化機器人", (210, 55, 40)
        self.collision_damage = int(62 * difficulty_multiplier)
        self.facing, self.attack_direction = pygame.math.Vector2(0, 1), pygame.math.Vector2(0, 1)
        self.attack_emitted, self.spin_angle = False, 0
        self.last_player_pos = spawn_center.copy()
        self.aoe_spots, self.rage_cycle, self.swing_direction = [], 0, pygame.math.Vector2(0, 1)
        self.transform_duration = 135
        self.frost_timer, self.burn_timer, self.hit_timer = 0, 0, 0

    def update(self, player_x, player_y, bullets, enemies, enemy_bullets):
        self.state_timer += 1
        player_pos = pygame.math.Vector2(player_x, player_y)
        self.last_player_pos = player_pos.copy()
        
        if getattr(self, 'hit_timer', 0) > 0: self.hit_timer -= 1
        if self.frost_timer > 0: self.frost_timer -= 1
        if self.burn_timer > 0:
            self.burn_timer -= 1
            if self.burn_timer % 15 == 0: self.hp -= 10; particles.append(Particle(self.x, self.y, ORANGE))
        eff_speed = self.speed * 0.5 if self.frost_timer > 0 else self.speed

        if self.state == "ENTRANCE":
            progress = min(1, self.state_timer / self.entrance_duration)
            self.pos = self.entrance_start.lerp(self.entrance_end, 1 - (1 - progress) ** 3)
            self.color = (170 + int(80 * abs(math.sin(self.state_timer * 0.1))), 45, 35)
            if self.state_timer >= self.entrance_duration: self.state, self.state_timer = "HUNT", 0
        elif self.state == "HUNT":
            self.color = (210, 55, 40) if self.phase == 1 else (255, 35, 35)
            direction = player_pos - self.pos
            distance = direction.length()
            if distance > 0:
                direction.normalize_ip(); self.facing = direction.copy()
                self.pos += direction * (eff_speed * (1.08 if self.phase == 1 else 1.25))
            trigger_time, trigger_dist = (64, 330) if self.phase == 1 else (42, 280)
            if self.state_timer > trigger_time or distance < trigger_dist:
                self.state = "WINDUP" if self.phase == 1 else "RAGE_AOE_WINDUP"
                self.state_timer, self.attack_emitted = 0, False
                if self.phase == 2: self.begin_rage_aoe()
        elif self.state == "WINDUP":
            self.color = ORANGE; self.face_player(player_pos)
            if self.state_timer > 34: self.state, self.state_timer, self.attack_emitted = "SLAM", 0, False
        elif self.state == "SLAM":
            self.color = (255, 80, 25)
            if self.state_timer <= 16: self.pos += self.attack_direction * (eff_speed * 3.1)
            if self.state_timer > 36: self.state, self.state_timer = "HUNT", 0
        elif self.state == "TRANSFORM":
            self.phase, self.color = 2, (255, 25, 25)
            self.spin_angle += 0.24
            self.hp = max(1, int(self.max_hp * min(1, self.state_timer / self.transform_duration)))
            if self.state_timer >= self.transform_duration:
                self.hp, self.state, self.state_timer, self.attack_emitted = self.max_hp, "RAGE_AOE_WINDUP", 0, False
                self.begin_rage_aoe()
        elif self.state == "RAGE_AOE_WINDUP":
            self.color = (255, 210, 35); self.face_player(player_pos)
            if self.state_timer > 46: self.state, self.state_timer, self.attack_emitted = "RAGE_AOE_BLAST", 0, False
        elif self.state == "RAGE_AOE_BLAST":
            self.color, self.spin_angle = (255, 65, 70), self.spin_angle + 0.1
            if self.state_timer > 34: self.state, self.state_timer, self.attack_emitted = "RAGE_RECOVER", 0, False
        elif self.state == "RAGE_RECOVER":
            self.color = (255, 90, 115)
            direction = player_pos - self.pos
            if direction.length_squared() > 0: direction.normalize_ip(); self.facing = direction.copy(); self.pos += direction * (eff_speed * 0.7)
            if self.state_timer > 40:
                self.rage_cycle += 1
                if self.rage_cycle % 4 == 0: self.state = "RAGE_DASH"; self.begin_rage_dash(player_pos)
                else: self.state = "HUNT"
                self.state_timer, self.attack_emitted = 0, False
        elif self.state == "RAGE_DASH":
            self.color = (255, 35, 35); self.pos += self.attack_direction * (eff_speed * 2.2)
            if self.state_timer > 16: self.state, self.state_timer, self.attack_emitted = "RAGE_RECOVER", 0, False
        elif self.state == "DEFEAT":
            self.defeat_timer += 1; self.color = (255, max(0, 85 - self.defeat_timer * 2), 45)
            self.pos.y -= 0.7; self.pos.x += math.sin(self.defeat_timer * 0.22) * 2.3

        self.pos.x = max(self.size, min(MAP_WIDTH - self.size, self.pos.x))
        self.pos.y = max(self.size, min(MAP_HEIGHT - self.size, self.pos.y))
        self.x, self.y = self.pos.x, self.pos.y
        self.rect.center = (round(self.x), round(self.y))
        self.emit_attacks(enemy_bullets)

    def face_player(self, player_pos):
        direction = player_pos - self.pos
        if direction.length_squared() > 0: direction.normalize_ip(); self.facing = direction.copy(); self.attack_direction = direction.copy()

    def begin_rage_aoe(self):
        self.aoe_spots = [pygame.math.Vector2(random.randint(180, MAP_WIDTH - 180), random.randint(180, MAP_HEIGHT - 180)) for _ in range(5 if self.spawn_level < 10 else 7)]
        player_anchor = self.last_player_pos + pygame.math.Vector2(random.randint(-90, 90), random.randint(-90, 90))
        player_anchor.x, player_anchor.y = max(180, min(MAP_WIDTH - 180, player_anchor.x)), max(180, min(MAP_HEIGHT - 180, player_anchor.y))
        self.aoe_spots.append(player_anchor)
        self.attack_emitted = False
        self.swing_direction = self.last_player_pos - self.pos
        if self.swing_direction.length_squared() == 0: self.swing_direction = self.facing.copy()
        if self.swing_direction.length_squared() == 0: self.swing_direction = pygame.math.Vector2(0, 1)
        self.swing_direction.normalize_ip()

    def begin_rage_dash(self, player_pos):
        direction = player_pos - self.pos
        if direction.length_squared() == 0: direction = pygame.math.Vector2(1, 0)
        else: direction.normalize_ip()
        self.attack_direction, self.facing, self.attack_emitted = direction.copy(), direction.copy(), False

    def start_phase_two(self):
        self.phase, self.phase2_started, self.hp, self.state, self.state_timer, self.attack_emitted = 2, True, 1, "TRANSFORM", 0, False
        self.collision_damage, self.rage_cycle, self.aoe_spots = int(self.collision_damage * 1.25), 0, []

    def survive_lethal_damage(self):
        if not self.phase2_started: self.start_phase_two(); return True
        return False

    def can_take_damage(self): return self.state not in ("ENTRANCE", "TRANSFORM", "DEFEAT")

    def emit_attacks(self, enemy_bullets):
        if self.state == "SLAM" and not self.attack_emitted and self.state_timer >= 12:
            self.attack_emitted = True
            shots = 14 if self.spawn_level < 10 else 18
            for i in range(shots):
                direction = self.attack_direction.rotate(-80 + i * (160 / max(1, shots - 1)))
                enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, direction.x, direction.y, color=(255, 90, 25), core_color=(255, 235, 170), style="slash"))
            for offset in (-35, 0, 35):
                direction = self.attack_direction.rotate(offset)
                enemy_bullets.append(EnemyBullet(self.rect.centerx, self.rect.centery, direction.x, direction.y, color=(255, 30, 80), core_color=WHITE, style="diamond"))
            play_sound("shoot_cannon")
        elif self.state == "RAGE_AOE_BLAST" and self.state_timer in (2, 10, 18, 26):
            if not self.aoe_spots: self.begin_rage_aoe()
            radial_count = 10 if self.spawn_level < 10 else 12
            for spot in self.aoe_spots:
                for i in range(radial_count):
                    angle = self.spin_angle + i * math.pi * 2 / radial_count
                    enemy_bullets.append(EnemyBullet(spot.x, spot.y, math.cos(angle), math.sin(angle), color=(255, 55, 45), core_color=(255, 235, 170), style="diamond"))
            slash_origin = self.pos + self.swing_direction * 48
            for i in range(7):
                slash_dir = self.swing_direction.rotate(-32 + i * (64 / 6))
                spawn = slash_origin + self.swing_direction.rotate(90) * ((i - 3) * 10)
                enemy_bullets.append(EnemyBullet(spawn.x, spawn.y, slash_dir.x, slash_dir.y, color=(255, 25, 95), core_color=(255, 245, 190), style="slash"))
            play_sound("shoot_cannon")
        elif self.state == "RAGE_DASH" and self.state_timer == 4:
            forward = self.attack_direction if self.attack_direction.length_squared() > 0 else pygame.math.Vector2(0, 1)
            side_axis = forward.rotate(90)
            for i in range(5):
                spawn = self.pos + forward * 52 + side_axis * ((i - 2) * 18)
                slash_dir = forward.rotate((i - 2) * 18 * 0.15)
                enemy_bullets.append(EnemyBullet(spawn.x, spawn.y, slash_dir.x, slash_dir.y, color=(255, 65, 45), core_color=(255, 245, 190), style="slash"))
            play_sound("shoot_cannon")

    def get_intro_title(self): return f"!! {self.name} 登場 !!"
    def get_intro_lines(self): return ["第三支 BOSS 出現：半血後會進入狂暴二階", "一階 = 追擊重砍  |  二階 = 高速衝刺與旋轉斬", "變身時無敵，拉開距離等紅色震波結束"]
    def get_state_message(self):
        if self.state == "HUNT": return f"腐化機器人第 {self.phase} 階段 - 追擊中", RED if self.phase == 2 else ORANGE
        if self.state in ("WINDUP", "RAGE_WINDUP"): return "腐化機器人蓄力 - 準備重擊", YELLOW
        if self.state == "SLAM": return "腐化機器人重砍 - 扇形震波", ORANGE
        if self.state == "TRANSFORM": return "狂暴化 - 第二階段覺醒", RED
        if self.state == "RAGE_DASH": return "狂暴衝刺 - 保持橫向閃避", RED
        if self.state == "RAGE_AOE_WINDUP": return "RAGE AOE - MAP TELEGRAPH", YELLOW
        if self.state == "RAGE_AOE_BLAST": return "RAGE AOE - MULTI POINT BLAST", RED
        if self.state == "RAGE_RECOVER": return "RAGE RECOVER - NEXT WAVE", PURPLE
        if self.state == "RAGE_SPIN": return "旋轉斬 - 彈幕擴散", PURPLE
        return "BOSS 交戰中", WHITE

    def draw(self, surface):
        cx, cy = (round(self.x - camera_x), round(self.y - camera_y))
        center, facing = pygame.math.Vector2(cx, cy), self.facing if self.facing.length_squared() > 0 else pygame.math.Vector2(0, 1)
        side = facing.rotate(90)
        pulse, aura_base, aura_color = abs(math.sin(self.state_timer * 0.14)), self.size // 2 + (34 if self.phase == 2 else 24), RED if self.phase == 2 else ORANGE

        if self.state == "TRANSFORM":
            for i in range(5): pygame.draw.circle(surface, RED if i % 2 else YELLOW, (cx, cy), int(aura_base + i * 18 + pulse * 12), 3)
            trap_center = (round(self.last_player_pos.x - camera_x), round(self.last_player_pos.y - camera_y))
            trap_pulse = int(abs(math.sin(self.state_timer * 0.22)) * 14)
            pygame.draw.circle(surface, (255, 45, 45), trap_center, 86 - trap_pulse, 3)
            pygame.draw.circle(surface, (255, 210, 60), trap_center, 42 + trap_pulse, 2)
            for i in range(8):
                mark = pygame.math.Vector2(trap_center) + pygame.math.Vector2(math.cos(self.spin_angle + i * math.pi / 4), math.sin(self.spin_angle + i * math.pi / 4)) * (58 + trap_pulse)
                pygame.draw.circle(surface, ORANGE, (int(mark.x), int(mark.y)), 4)
        elif self.state in ("RAGE_AOE_WINDUP", "RAGE_AOE_BLAST"):
            for i, spot in enumerate(self.aoe_spots):
                sx, sy = round(spot.x - camera_x), round(spot.y - camera_y)
                ring_pulse = abs(math.sin((self.state_timer + i * 13) * 0.18))
                outer, inner, warn_color = 54 + int(ring_pulse * 12), 20 + int(ring_pulse * 6), YELLOW if self.state == "RAGE_AOE_WINDUP" else RED
                pygame.draw.circle(surface, warn_color, (sx, sy), outer, 3); pygame.draw.circle(surface, ORANGE, (sx, sy), inner, 2)
                for j in range(4): pygame.draw.circle(surface, WHITE if self.state == "RAGE_AOE_WINDUP" else YELLOW, (int(sx + math.cos(self.spin_angle + j * math.pi / 2 + i * 0.5) * (outer - 8)), int(sy + math.sin(self.spin_angle + j * math.pi / 2 + i * 0.5) * (outer - 8))), 3)
        elif self.state == "RAGE_RECOVER":
            for i in range(6):
                tip = center + pygame.math.Vector2(math.cos(self.spin_angle + i * math.pi / 3), math.sin(self.spin_angle + i * math.pi / 3)) * (100 + pulse * 8)
                pygame.draw.line(surface, PURPLE, (cx, cy), (int(tip.x), int(tip.y)), 2)
        elif self.state == "RAGE_DASH":
            pygame.draw.circle(surface, RED, (cx, cy), self.size // 2 + 40 + int(pulse * 10), 2)
            tip = center + self.attack_direction * 170
            for i in range(5):
                mark = center + self.attack_direction * (35 + i * 26)
                pygame.draw.line(surface, ORANGE, (int(mark.x), int(mark.y)), (int((mark + side * 18).x), int((mark + side * 18).y)), 2)
                pygame.draw.line(surface, ORANGE, (int(mark.x), int(mark.y)), (int((mark - side * 18).x), int((mark - side * 18).y)), 2)
            pygame.draw.line(surface, WHITE, (cx, cy), (int(tip.x), int(tip.y)), 2)
        elif self.state == "DEFEAT":
            progress = min(1, self.defeat_timer / 60)
            for i in range(5): pygame.draw.circle(surface, (255, max(30, 120 - i * 12), 35), (cx, cy), int(self.size * 0.7 + progress * 150 + i * 16), 3)
        else: pygame.draw.circle(surface, aura_color, (cx, cy), int(aura_base + pulse * 12), 2)

        body_top, body_bottom = center - facing * 25, center + facing * 30
        shoulder_l, shoulder_r, waist_l, waist_r = body_top + side * 34, body_top - side * 34, body_bottom + side * 22, body_bottom - side * 22
        body_points = [shoulder_l, shoulder_r, waist_r, waist_l]
        pygame.draw.polygon(surface, BLACK, [(int(p.x), int(p.y)) for p in body_points])
        
        core_color = WHITE if getattr(self, 'hit_timer', 0) > 0 else ((100, 200, 255) if self.frost_timer > 0 else self.color)
        inner = [center + (p - center) * 0.88 for p in body_points]
        if self.state == "DEFEAT":
            shake = math.sin(self.defeat_timer * 0.7) * 5
            broken_points = [(px + int(shake if i % 2 == 0 else -shake), py) for i, (px, py) in enumerate(body_points)]
            pygame.draw.polygon(surface, (120, 30, 35), broken_points); pygame.draw.polygon(surface, RED, broken_points, 2)
        else: pygame.draw.polygon(surface, core_color, [(int(p.x), int(p.y)) for p in inner])
            
        chest_core = center - facing * 3
        pygame.draw.circle(surface, BLACK, (int(chest_core.x), int(chest_core.y)), 20)
        pygame.draw.circle(surface, (255, 55, 65) if self.phase == 2 else (255, 185, 70), (int(chest_core.x), int(chest_core.y)), 13)
        pygame.draw.circle(surface, WHITE, (int(chest_core.x - side.x * 5), int(chest_core.y - side.y * 5)), 3)

        head = center - facing * 43
        head_points = [head - facing * 14 + side * 17, head - facing * 14 - side * 17, head + facing * 12 - side * 13, head + facing * 12 + side * 13]
        pygame.draw.polygon(surface, BLACK, [(int(p.x), int(p.y)) for p in head_points]); pygame.draw.polygon(surface, (80, 88, 98), [(int(p.x), int(p.y)) for p in head_points])
        eye_l, eye_r = head - facing * 2 + side * 7, head - facing * 2 - side * 7
        pygame.draw.circle(surface, RED if self.phase == 2 else YELLOW, (int(eye_l.x), int(eye_l.y)), 3); pygame.draw.circle(surface, RED if self.phase == 2 else YELLOW, (int(eye_r.x), int(eye_r.y)), 3)

        for shoulder, hand_side in ((shoulder_l, 1), (shoulder_r, -1)):
            elbow = center + side * (hand_side * 42) + facing * 8
            pygame.draw.line(surface, BLACK, (int(shoulder.x), int(shoulder.y)), (int(elbow.x), int(elbow.y)), 11)
            pygame.draw.line(surface, (95, 105, 116), (int(shoulder.x), int(shoulder.y)), (int(elbow.x), int(elbow.y)), 6)
            pygame.draw.circle(surface, (40, 45, 55), (int(shoulder.x), int(shoulder.y)), 9)

        sword_hand, sword_dir = center + side * 43 + facing * 10, facing
        sword_side, sword_tip = sword_dir.rotate(90), sword_hand + sword_dir * (118 if self.phase == 2 else 98)
        sword_base, blade_half = sword_hand - sword_dir * 12, 13 if self.phase == 2 else 10
        sword_points = [sword_tip, sword_hand + sword_dir * 18 + sword_side * blade_half, sword_base + sword_side * 8, sword_base - sword_side * 8, sword_hand + sword_dir * 18 - sword_side * blade_half]
        pygame.draw.polygon(surface, BLACK, [(int(p.x), int(p.y)) for p in sword_points])
        inner_blade = [sword_hand + (p - sword_hand) * 0.88 for p in sword_points]
        pygame.draw.polygon(surface, (220, 230, 240), [(int(p.x), int(p.y)) for p in inner_blade])
        pygame.draw.line(surface, (255, 50, 75) if self.phase == 2 else (255, 210, 80), (int(sword_base.x), int(sword_base.y)), (int(sword_tip.x), int(sword_tip.y)), 3)
        guard_l, guard_r = sword_hand + sword_side * 24, sword_hand - sword_side * 24
        pygame.draw.line(surface, BLACK, (int(guard_l.x), int(guard_l.y)), (int(guard_r.x), int(guard_r.y)), 8)
        pygame.draw.line(surface, ORANGE if self.phase == 1 else RED, (int(guard_l.x), int(guard_l.y)), (int(guard_r.x), int(guard_r.y)), 4)

        if self.state in ("WINDUP", "RAGE_WINDUP"):
            windup_ratio = min(1, self.state_timer / (32 if self.phase == 2 else 45))
            pygame.draw.circle(surface, YELLOW if windup_ratio < 0.75 else RED, (cx, cy), int(self.size + 70 * (1 - windup_ratio)), 3)
            pygame.draw.line(surface, RED, (cx, cy), (int((center + self.attack_direction * 210).x), int((center + self.attack_direction * 210).y)), 3)
        elif self.state in ("SLAM", "RAGE_DASH"):
            tip, left, right = center + self.attack_direction * 150, center + self.attack_direction.rotate(35) * 110, center + self.attack_direction.rotate(-35) * 110
            pygame.draw.line(surface, ORANGE, (cx, cy), (int(tip.x), int(tip.y)), 3); pygame.draw.line(surface, ORANGE, (cx, cy), (int(left.x), int(left.y)), 2); pygame.draw.line(surface, ORANGE, (cx, cy), (int(right.x), int(right.y)), 2)
        elif self.state == "RAGE_SPIN":
            for i in range(8):
                tip = center + pygame.math.Vector2(math.cos(self.spin_angle + i * math.pi / 4), math.sin(self.spin_angle + i * math.pi / 4)) * 118
                pygame.draw.line(surface, PURPLE, (cx, cy), (int(tip.x), int(tip.y)), 2)


# 遊戲全域狀態與核心初始化
chosen_upgrades, defeated_boss_levels = [], []
lost_item, game_mode = None, "NORMAL"
bullets, bunker_bullets, enemy_bullets, enemies, particles, items, trails, damage_texts, chests = [], [], [], [], [], [], [], [], []
boss, boss_active = None, False
shoot_cooldown, magnet_timer, screen_flash_timer = 0, 0, 0
boss_army_active, extraction_timer, extraction_pt, extract_progress = False, 0, None, 0
show_changelog, changelog_scroll, changelog_max_scroll = False, 0, 0
pause_upgrade_scroll, arsenal_scroll_y, selected_arsenal_idx, arsenal_weapons_list = 0, 0, 0, []
show_inventory, drag_data, selected_mod_weapon = False, None, None
current_upgrade_choices, selected_upgrade_position = [], None
bunker_dummy = DummyTarget(MAP_WIDTH//2 + 200, MAP_HEIGHT//2 - 50)
task_system = TaskSystem()
raid_start_time, enemy_spawn_timer = None, 0

def enter_bunker(success=False):
    global game_state, bullets, bunker_bullets, enemy_bullets, enemies, particles, items, trails, damage_texts, chests
    global boss, boss_active, shoot_cooldown, magnet_timer, screen_flash_timer
    global boss_army_active, extraction_timer, extraction_pt, extract_progress, enemy_spawn_timer, task_system
    if success:
        scrap_count = sum(i.count for i in player.inventory if i and i.type == "SCRAP")
        persistent_stats["scrap"] += scrap_count * 10 
        for i in range(24):
            if player.inventory[i] and player.inventory[i].type == "SCRAP": player.inventory[i] = None
    player.hp, player.shield, player.ammo = player.max_hp, player.max_shield, player.base_max_ammo + player.mag_size_bonus
    bullets.clear(); bunker_bullets.clear(); enemy_bullets.clear(); enemies.clear()
    particles.clear(); items.clear(); trails.clear(); damage_texts.clear(); chests.clear()
    boss, boss_active, shoot_cooldown, magnet_timer, screen_flash_timer = None, False, 0, 0, 0
    boss_army_active, extraction_timer, extraction_pt, extract_progress, enemy_spawn_timer = False, 15*60*FPS, None, 0, 0
    player.x, player.y = MAP_WIDTH//2, MAP_HEIGHT//2
    game_state = "BUNKER"; stop_sound("boss_bgm"); task_system = TaskSystem()

def start_raid():
    global game_state, extraction_timer, extraction_pt, boss_army_active, extract_progress
    global bullets, enemy_bullets, enemies, particles, items, trails, damage_texts, chests
    global boss_active, boss, player, enemy_spawn_timer, raid_start_time
    game_state, player.x, player.y = "PLAYING", MAP_WIDTH//2, MAP_HEIGHT//2
    bullets.clear(); enemy_bullets.clear(); enemies.clear(); particles.clear()
    items.clear(); trails.clear(); damage_texts.clear(); chests.clear()
    extraction_pt, extraction_timer, extract_progress = ExtractionPoint(), 180 * FPS, 0
    boss_army_active, boss_active, boss, enemy_spawn_timer = False, False, None, 10
    raid_start_time = pygame.time.get_ticks()
    for _ in range(15): chests.append(Chest(random.randint(400, MAP_WIDTH-400), random.randint(400, MAP_HEIGHT-400), "NORMAL"))
    for _ in range(5): chests.append(Chest(random.randint(400, MAP_WIDTH-400), random.randint(400, MAP_HEIGHT-400), "LOCKED"))
    play_sound("boss_bgm", loop=-1)

def full_wipe(mode="NORMAL"):
    global player, game_mode, chosen_upgrades, lost_item, defeated_boss_levels
    game_mode, player, lost_item = mode, Player(), None
    chosen_upgrades.clear(); defeated_boss_levels.clear()
    enter_bunker(success=False)

def resolve_chest_collision(entity, chests_list):
    hit_chest = False
    for c in chests_list:
        if entity.rect.colliderect(c.rect):
            hit_chest = True
            overlap_l, overlap_r = entity.rect.right - c.rect.left, c.rect.right - entity.rect.left
            overlap_t, overlap_b = entity.rect.bottom - c.rect.top, c.rect.bottom - entity.rect.top
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

CHEAT_CODE = [pygame.K_UP, pygame.K_UP, pygame.K_DOWN, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_b, pygame.K_a, pygame.K_b, pygame.K_a]
key_buffer = []


running = True 

# UI 定位宣告
start_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 20, 220, 50)
changelog_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 100, 220, 50)
exit_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 180, 220, 50)
normal_button = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 - 60, 210, 230)
challenge_button = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 - 60, 210, 230)
difficulty_back_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 200, 220, 50)
changelog_close_button = pygame.Rect(WIDTH//2 + 205, HEIGHT//2 - 195, 35, 35)
restart_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 100, 220, 50)
menu_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 170, 220, 50)
confirm_upgrade_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 190, 220, 50)
# 地堡面板與按鈕（包含黑市、收藏箱、改造台、武器庫）
cards = [pygame.Rect(WIDTH//2 - 350 + i*240, HEIGHT//2 - 150, 220, 320) for i in range(3)]
# 地堡四大面板背景
shop_bg = pygame.Rect(int(WIDTH//2 - 300*SCALE), int(HEIGHT//2 - 250*SCALE), int(600*SCALE), int(500*SCALE)) # 黑市
stash_bg = pygame.Rect(int(WIDTH//2 - 380*SCALE), int(HEIGHT//2 - 250*SCALE), int(760*SCALE), int(500*SCALE)) # 收藏箱
mod_bg = pygame.Rect(int(WIDTH//2 - 380*SCALE), int(HEIGHT//2 - 260*SCALE), int(760*SCALE), int(520*SCALE)) # 改造台
wep_stash_bg = pygame.Rect(int(WIDTH//2 - 380*SCALE), int(HEIGHT//2 - 280*SCALE), int(760*SCALE), int(560*SCALE)) # 武器庫
# 面板關閉按鈕
btn_shop_close = pygame.Rect(int(WIDTH//2 + 250*SCALE), int(HEIGHT//2 - 240*SCALE), int(40*SCALE), int(40*SCALE))
btn_stash_close = pygame.Rect(int(WIDTH//2 + 335*SCALE), int(HEIGHT//2 - 240*SCALE), int(35*SCALE), int(35*SCALE))
btn_mod_close = pygame.Rect(int(WIDTH//2 + 335*SCALE), int(HEIGHT//2 - 250*SCALE), int(35*SCALE), int(35*SCALE))
btn_wep_close = pygame.Rect(int(WIDTH//2 + 335*SCALE), int(HEIGHT//2 - 270*SCALE), int(35*SCALE), int(35*SCALE))
# 黑市商店按鈕
btn_hp = pygame.Rect(int(WIDTH//2 - 260*SCALE), int(HEIGHT//2 - 140*SCALE), int(240*SCALE), int(70*SCALE))
btn_dmg = pygame.Rect(int(WIDTH//2 + 20*SCALE),  int(HEIGHT//2 - 140*SCALE), int(240*SCALE), int(70*SCALE))
btn_spd  = pygame.Rect(int(WIDTH//2 - 260*SCALE), int(HEIGHT//2 - 40*SCALE),  int(240*SCALE), int(70*SCALE))
btn_stamina = pygame.Rect(int(WIDTH//2 + 20*SCALE),  int(HEIGHT//2 - 40*SCALE),  int(240*SCALE), int(70*SCALE))
btn_shield = pygame.Rect(int(WIDTH//2 - 260*SCALE), int(HEIGHT//2 + 60*SCALE),  int(240*SCALE), int(70*SCALE))
btn_energy = pygame.Rect(int(WIDTH//2 + 20*SCALE),  int(HEIGHT//2 + 60*SCALE),  int(240*SCALE), int(70*SCALE))
# 武器庫列表與按鈕
list_rect = pygame.Rect(int(WIDTH//2 - 280*SCALE), int(HEIGHT//2 - 200*SCALE), int(560*SCALE), int(300*SCALE))
btn_prim_w = pygame.Rect(int(WIDTH//2 - 160*SCALE), int(HEIGHT//2 + 235*SCALE), int(140*SCALE), int(40*SCALE))
btn_sec_w = pygame.Rect(int(WIDTH//2 + 20*SCALE), int(HEIGHT//2 + 235*SCALE), int(140*SCALE), int(40*SCALE))
# 改造台按鈕與框架
rect_prim = pygame.Rect(int(WIDTH//2 - 350*SCALE), int(HEIGHT//2 - 180*SCALE), int(160*SCALE), int(80*SCALE))
rect_sec = pygame.Rect(int(WIDTH//2 - 170*SCALE), int(HEIGHT//2 - 180*SCALE), int(160*SCALE), int(80*SCALE))
upg_btn = pygame.Rect(int(WIDTH//2 + 70*SCALE), int(HEIGHT//2 + 40*SCALE), int(230*SCALE), int(45*SCALE))
reroll_btn = pygame.Rect(int(WIDTH//2 + 70*SCALE), int(HEIGHT//2 + 110*SCALE), int(230*SCALE), int(45*SCALE))
# 各面板的 6*4 格背包繪製起點
s_start_x, s_start_y = int(WIDTH//2 - 350*SCALE), int(HEIGHT//2 - 150*SCALE)
p_start_x_s, p_start_y_s = int(WIDTH//2 + 30*SCALE), int(HEIGHT//2 - 150*SCALE)
p_start_x_m, p_start_y_m = int(WIDTH//2 - 350*SCALE), int(HEIGHT//2 - 40*SCALE)
p_start_x_w, p_start_y_w = int(WIDTH//2 - 344*SCALE), int(HEIGHT//2 + 115*SCALE)

# 主循環
while running:
    if 'lost_item' in globals() and lost_item:
        try: lost_item.rect.center = (int(lost_item.x), int(lost_item.y))
        except Exception: pass
    m_x, m_y = pygame.mouse.get_pos(); m_pos = (m_x, m_y); hovered_slot_info = None 

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if game_state == "MENU" and show_changelog and event.type == pygame.MOUSEWHEEL: changelog_scroll = max(0, min(changelog_max_scroll, changelog_scroll - event.y * 55))
        if game_state == "PAUSED" and event.type == pygame.MOUSEWHEEL: pause_upgrade_scroll = max(0, pause_upgrade_scroll - event.y * 45)
        if game_state == "WEAPON_STASH" and event.type == pygame.MOUSEWHEEL: arsenal_scroll_y = max(0, arsenal_scroll_y - event.y * 30)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == "PLAYING" and not show_inventory: game_state = "PAUSED"
                elif game_state == "PLAYING" and show_inventory: show_inventory, drag_data = False, None
                elif game_state == "PAUSED": game_state = "PLAYING"
                elif game_state in ["SHOP", "WEAPON_STASH", "GENERAL_STASH", "MOD_STATION"]: game_state, drag_data = "BUNKER", None
                elif game_state == "DIFFICULTY": game_state = "MENU"
            
            if event.key == pygame.K_TAB and game_state == "PLAYING": show_inventory, drag_data = not show_inventory, None
            if event.key == pygame.K_h and game_state == "PLAYING" and not show_inventory: player.use_med()
            
            if event.key == pygame.K_x:
                # 動態檢測當前鼠標位置下的物品，支持庫存、收藏箱和武器箱
                current_hovered = None
                
                if game_state == "PLAYING" and show_inventory:
                    for i in range(24):
                        rect = pygame.Rect(WIDTH//2 - 170 + (i%6)*58, HEIGHT//2 - 40 + (i//6)*58, 50, 50)
                        if rect.collidepoint(m_x, m_y) and player.inventory[i]: current_hovered = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}; break
                
                elif game_state == "GENERAL_STASH":
                    for i in range(36):
                        rect = pygame.Rect(s_start_x + (i%6)*58, s_start_y + (i//6)*58, 50, 50)
                        if rect.collidepoint(m_x, m_y) and persistent_stats["general_stash"][i]: current_hovered = {"source": "STASH", "idx": i, "item": persistent_stats["general_stash"][i]}; break
                    if not current_hovered:
                        for i in range(24):
                            rect = pygame.Rect(p_start_x_s + (i%6)*58, p_start_y_s + (i//6)*58, 50, 50)
                            if rect.collidepoint(m_x, m_y) and player.inventory[i]: current_hovered = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}; break
                
                elif game_state == "MOD_STATION":
                    for i in range(24):
                        rect = pygame.Rect(p_start_x_m + (i%6)*58, p_start_y_m + (i//6)*58, 50, 50)
                        if rect.collidepoint(m_x, m_y) and player.inventory[i]: current_hovered = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}; break
                
                elif game_state == "WEAPON_STASH":
                    if list_rect.collidepoint(m_x, m_y):
                        rel_y = m_y - list_rect.y + arsenal_scroll_y; idx = int(rel_y // 50) * 2 + (0 if m_x < WIDTH//2 else 1)
                        if 0 <= idx < len(arsenal_weapons_list): current_hovered = {"source": "ARSENAL", "idx": idx, "item": create_item("WEAPON", 1, arsenal_weapons_list[idx])}
                    if not current_hovered:
                        for i in range(24):
                            rect = pygame.Rect(p_start_x_w + (i%12)*58, p_start_y_w + (i//12)*58, 50, 50)
                            if rect.collidepoint(m_x, m_y) and player.inventory[i] and player.inventory[i].type == "WEAPON":
                                current_hovered = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}; break
                
                # 執行出售
                if current_hovered:
                    val = get_sell_value(current_hovered["item"])
                    if val > 0:
                        persistent_stats["scrap"] += val
                        if current_hovered["source"] == "PLAYER": player.inventory[current_hovered["idx"]] = None
                        elif current_hovered["source"] == "STASH": persistent_stats["general_stash"][current_hovered["idx"]] = None
                        elif current_hovered["source"] == "ARSENAL":
                            persistent_stats["weapon_stash"].pop(current_hovered["idx"]); sort_weapon_stash()
                            arsenal_weapons_list = [generate_weapon(n, "白") for n in WEAPON_TYPES] + persistent_stats["weapon_stash"]
                        play_sound("exp"); selected_mod_weapon = None 

            if event.key == pygame.K_r and game_state == "DIED": player = Player(); chosen_upgrades.clear(); enter_bunker(success=False)
            if event.key == pygame.K_e and game_state == "PLAYING": player.current_weapon_idx = (player.current_weapon_idx + 1) % len(player.weapons); play_sound("exp")
            if event.key == pygame.K_r and game_state == "PLAYING" and game_mode == "CHALLENGE" and player.reload_timer <= 0 and player.ammo < (player.base_max_ammo + player.mag_size_bonus): player.reload_timer = player.reload_duration
                
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
                        if pygame.Rect(start_x + (i%6)*(slot_size+margin), start_y + (i//6)*(slot_size+margin), slot_size, slot_size).collidepoint(event.pos) and player.inventory[i]:
                            drag_data = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}; player.inventory[i] = None; break
                elif event.button == 3:
                    for i in range(24):
                        if pygame.Rect(start_x + (i%6)*(slot_size+margin), start_y + (i//6)*(slot_size+margin), slot_size, slot_size).collidepoint(event.pos) and player.inventory[i]:
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
                    if pygame.Rect(start_x + (i%6)*(slot_size+margin), start_y + (i//6)*(slot_size+margin), slot_size, slot_size).collidepoint(event.pos):
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
                        if pygame.Rect(s_start_x + (i%6)*58, s_start_y + (i//6)*58, 50, 50).collidepoint(event.pos) and persistent_stats["general_stash"][i]:
                            drag_data = {"source": "STASH", "idx": i, "item": persistent_stats["general_stash"][i]}; persistent_stats["general_stash"][i] = None; break
                    if not drag_data:
                        for i in range(24):
                            if pygame.Rect(p_start_x_s + (i%6)*58, p_start_y_s + (i//6)*58, 50, 50).collidepoint(event.pos) and player.inventory[i]:
                                drag_data = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}; player.inventory[i] = None; break
                    if btn_stash_close.collidepoint(event.pos): game_state = "BUNKER"
                elif event.button == 3: 
                    for i in range(36):
                        if pygame.Rect(s_start_x + (i%6)*58, s_start_y + (i//6)*58, 50, 50).collidepoint(event.pos) and persistent_stats["general_stash"][i]:
                            if fast_transfer(persistent_stats["general_stash"][i], player.inventory): persistent_stats["general_stash"][i] = None; play_sound("exp")
                    for i in range(24):
                        item = player.inventory[i]
                        if pygame.Rect(p_start_x_s + (i%6)*58, p_start_y_s + (i//6)*58, 50, 50).collidepoint(event.pos) and item and item.type != "WEAPON":
                            if fast_transfer(item, persistent_stats["general_stash"]): player.inventory[i] = None; play_sound("exp")
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drag_data:
                dropped = False
                for i in range(36):
                    if pygame.Rect(s_start_x + (i%6)*58, s_start_y + (i//6)*58, 50, 50).collidepoint(event.pos):
                        if drag_data["item"].type == "WEAPON": break 
                        rem = put_item_in_slot("STASH", i, drag_data["item"])
                        if rem: put_item_in_slot(drag_data["source"], drag_data["idx"], rem)
                        dropped = True; break
                if not dropped:
                    for i in range(24):
                        if pygame.Rect(p_start_x_s + (i%6)*58, p_start_y_s + (i//6)*58, 50, 50).collidepoint(event.pos):
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
                    elif changelog_button.collidepoint(event.pos): show_changelog, changelog_scroll = True, 0; rebuild_changelog_cache(640, 380)
                    elif exit_button.collidepoint(event.pos): running = False
                    
        elif game_state == "DIFFICULTY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if normal_button.collidepoint(event.pos): full_wipe("NORMAL")
                elif challenge_button.collidepoint(event.pos): full_wipe("CHALLENGE")
                elif difficulty_back_button.collidepoint(event.pos): game_state = "MENU"
                
        elif game_state == "BUNKER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                p_rect = player.rect.copy()
                if p_rect.colliderect(pygame.Rect(MAP_WIDTH//2 - 60, MAP_HEIGHT//2 + 200, 120, 60)): start_raid()
                elif p_rect.colliderect(pygame.Rect(MAP_WIDTH//2 - 350, MAP_HEIGHT//2 - 50, 100, 100)): game_state = "SHOP"; play_sound("exp")
                elif p_rect.colliderect(pygame.Rect(MAP_WIDTH//2 + 50, MAP_HEIGHT//2 - 150, 100, 100)): game_state = "GENERAL_STASH"; play_sound("exp")
                elif p_rect.colliderect(pygame.Rect(MAP_WIDTH//2 - 150, MAP_HEIGHT//2 - 150, 100, 100)): game_state = "MOD_STATION"; selected_mod_weapon = None; play_sound("exp")
                elif p_rect.colliderect(pygame.Rect(MAP_WIDTH//2 + 250, MAP_HEIGHT//2 - 50, 100, 100)): 
                    game_state, selected_arsenal_idx, arsenal_scroll_y = "WEAPON_STASH", 0, 0; play_sound("exp")
                    if player.cheat_all_weapons: player.god_mode, player.cheat_all_weapons = False, False; player.weapons = [player.primary_weapon, player.secondary_weapon]; player.current_weapon_idx = 0
                    sort_weapon_stash(); arsenal_weapons_list = [generate_weapon(n, "白") for n in WEAPON_TYPES] + persistent_stats["weapon_stash"]
                    
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
                    item = player.inventory[i]
                    if pygame.Rect(p_start_x_w + (i%12)*58, p_start_y_w + (i//12)*58, 50, 50).collidepoint(event.pos) and item and item.type == "WEAPON":
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

    # 遊戲邏輯更新
    if game_state == "BUNKER":
        player.update(clamp_rect=pygame.Rect(MAP_WIDTH//2 - 400, MAP_HEIGHT//2 - 300, 800, 600))
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
            
        for b in bunker_bullets[:]:
            b.update()
            if bunker_dummy and b.rect.colliderect(bunker_dummy.rect):
                damage_texts.append(DamageText(b.x, b.y - 20, b.damage, RED if b.is_crit else WHITE, b.is_crit))
                bunker_dummy.hit_log.append((pygame.time.get_ticks(), b.damage)); bunker_dummy.shake_timer = 5
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
        
        # 每過一幀，就平滑增加 1/FPS 秒的存活進度
        if raid_start_time and not boss_army_active:
            task_system.update_progress("survive", 1.0 / FPS)
            
        shake_x, shake_y = (random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0), (random.randint(-screen_shake, screen_shake) if screen_shake > 0 else 0)
        if screen_shake > 0: screen_shake -= 1

        camera_x = max(0, min(MAP_WIDTH - WIDTH, player.x - WIDTH / 2)) + shake_x
        camera_y = max(0, min(MAP_HEIGHT - HEIGHT, player.y - HEIGHT / 2)) + shake_y
        
        if magnet_timer > 0: magnet_timer -= 1
        if screen_flash_timer > 0: screen_flash_timer -= 1
        if extraction_timer > 0: extraction_timer -= 1
        if extraction_timer <= 0:
            boss_army_active = True
            if pygame.time.get_ticks() % 15 == 0:
                e = Enemy(player.level + 15, is_elite=True); e.max_hp *= 4; e.hp = e.max_hp; e.speed *= 1.3; e.color = DARK_PURPLE
                e.weapon = generate_weapon("機槍", "紫"); enemies.append(e)

        if extraction_pt:
            if math.sqrt((player.x - extraction_pt.x)**2 + (player.y - extraction_pt.y)**2) < extraction_pt.radius:
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
                    if player.add_item(new_item):
                        items.remove(g); play_sound("exp")
                        if g.item_type in ["SCRAP", "KEY"]: task_system.update_progress("collect", g.count)
        else:
            for c in chests:
                if c.state == "CLOSED": c.open_progress = max(0, c.open_progress - 2)

        if player.exp >= player.max_exp:
            player.exp -= player.max_exp; player.level += 1; player.max_exp = int(player.max_exp * 1.25)
            choose_upgrade_cards(); game_state = "LEVEL_UP"; play_sound("levelup")
        
        if task_system.current_task and task_system.current_task.is_completed:
            task_system.current_task.apply_reward(player); play_sound("levelup"); task_system.complete_task() 

        #  Boss 每 5 級出現一次，不會在同一關重複出現同一個 Boss
        if player.level % 5 == 0 and player.level > 0 and player.level not in defeated_boss_levels and not boss_active and not boss_army_active:
            boss_spawn_count = len(defeated_boss_levels)
            boss_cycle = boss_spawn_count % 3
            if boss_cycle == 0: boss = CoreBoss(player.level, player.x, player.y)
            elif boss_cycle == 1: boss = ChargerBoss(player.level, player.x, player.y)
            else: boss = BerserkerBoss(player.level, player.x, player.y)
            boss_active = True; play_sound("boss_bgm", loop=-1) 

        mouse_btns = pygame.mouse.get_pressed()
        world_mouse_x, world_mouse_y = m_x + camera_x, m_y + camera_y
        current_wep = player.weapons[player.current_weapon_idx]
        
        if mouse_btns[0] and shoot_cooldown <= 0 and not player.is_dashing:
            can_fire = True
            if game_mode == "CHALLENGE":
                if player.ammo <= 0: can_fire = False; player.reload_timer = player.reload_duration if player.reload_timer <= 0 else player.reload_timer
                else: player.ammo -= 1; player.reload_timer = player.reload_duration if player.ammo <= 0 else player.reload_timer
            
            if can_fire:
                base_dir = pygame.math.Vector2(world_mouse_x - player.x, world_mouse_y - player.y)
                if base_dir.length() > 0: base_dir.normalize_ip()
                else: base_dir = pygame.math.Vector2(1, 0)
                
                player.current_spread = min(player.bullet_spread + 25.0, player.current_spread + current_wep.base_recoil)
                t_bullets = player.bullet_count + (4 if current_wep.bullet_type == "shotgun" else 0) + (2 if "散射" in current_wep.affixes else 0)
                s_angle = -(t_bullets - 1) * player.current_spread / 2
                
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
                    play_sound("hit"); task_system.update_progress("damage", b.damage)
                    
                    if e.hp <= 0 and e in enemies:
                        for _ in range(10): particles.append(Particle(e.x, e.y, RED))
                        task_system.update_progress("kill", 1)
                        if e.is_elite: task_system.update_progress("kill_elite", 1)
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
                if not boss.can_take_damage():
                    for _ in range(5): particles.append(Particle(boss.x, boss.y, GRAY))
                else:
                    if b.b_type == "frost": boss.frost_timer = 60 
                    if b.is_burning: boss.burn_timer = 180
                    if b.is_vampiric and random.random() < 0.05: player.hp = min(player.max_hp, player.hp + 2)
                    boss.hp -= b.damage
                    boss.hit_timer = 4
                    if b.is_crit or b.damage >= 50: screen_shake = max(screen_shake, 8); pygame.time.delay(15)               
                    damage_texts.append(DamageText(boss.x, boss.y - 20, b.damage, RED if b.is_crit else WHITE, b.is_crit))
                    for _ in range(8): particles.append(Particle(boss.x, boss.y, YELLOW))
                    play_sound("hit"); task_system.update_progress("damage", b.damage)
                    
                    if boss.hp <= 0 and hasattr(boss, "survive_lethal_damage") and boss.survive_lethal_damage():
                        for _ in range(28): particles.append(Particle(boss.x, boss.y, RED))
                    elif boss.hp <= 0 and boss.state != "DEFEAT":
                        boss.state, boss.defeat_timer = "DEFEAT", 0
                        for _ in range(40): items.append(DropItem(boss.x + random.randint(-60,60), boss.y + random.randint(-60,60), "EXP"))
                        for _ in range(10): items.append(DropItem(boss.x + random.randint(-40,40), boss.y + random.randint(-40,40), "SCRAP", random.randint(2,5)))
                        items.append(DropItem(boss.x, boss.y, "KEY"))
                        for _ in range(50): particles.append(Particle(boss.x, boss.y, YELLOW))

            if b.lifespan > 0 and map_rect.colliderect(b.rect) and (not hit_something or b.is_piercing) and not b.explode:
                alive_bullets.append(b)
        bullets = alive_bullets

        for dt in damage_texts[:]:
            dt.update(); damage_texts.remove(dt) if dt.timer <= 0 else None
        for p in particles[:]:
            p.update(); particles.remove(p) if p.timer <= 0 else None

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
                    
            if hit_chest and eb.b_type not in ["piercing", "laser"]: enemy_bullets.remove(eb); continue
            
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
        for e in enemies: e.update(player.x, player.y, enemies, enemy_bullets); resolve_chest_collision(e, chests)

        if boss_active and boss:
            boss.update(player.x, player.y, bullets, enemies, enemy_bullets)
            if resolve_chest_collision(boss, chests):
                if boss.state in ["CHARGE", "DASH", "SLAM", "RAGE_DASH"]:
                    # 避免沒有 name 屬性造成錯誤
                    b_name = getattr(boss, "name", "")
                    boss.state = "EVADE" if b_name == "旋轉彈幕核心" else ("RECOVER" if b_name == "衝刺突擊者" else "HUNT")
                    boss.state_timer, screen_shake = 0, 15; play_sound("shoot_cannon") 
                    for _ in range(15): particles.append(Particle(boss.x, boss.y, GRAY)) 
                    
            if boss.state == "DEFEAT" and boss.defeat_timer > 60:
                boss_active = False
                # 紀錄 boss.spawn_level 防止等級計算 Bug 
                defeated_boss_levels.append(boss.spawn_level)
                stop_sound("boss_bgm")
                
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
                    player.invincible_timer, screen_shake = player.invincible_duration, 10; play_sound("hurt")
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
                    player.invincible_timer, screen_shake = player.invincible_duration, 10; play_sound("hurt")
                if eb in enemy_bullets: enemy_bullets.remove(eb)
                
        if boss_active and player.rect.colliderect(boss.rect) and game_state == "PLAYING": 
            if not player.god_mode and player.invincible_timer <= 0 and not player.is_dashing:
                actual_dmg = max(1, boss.collision_damage - player.damage_reduction)
                if player.shield > 0:
                    if actual_dmg > player.shield: leftover = actual_dmg - player.shield; player.shield = 0; player.hp -= leftover
                    else: player.shield -= actual_dmg
                else: player.hp -= actual_dmg
                player.invincible_timer, screen_shake = player.invincible_duration, 10; play_sound("hurt")

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
                player.level = max(player.level, lost_item.level); player.exp += lost_item.exp
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
    if game_state in ["BUNKER", "SHOP", "GENERAL_STASH", "MOD_STATION", "WEAPON_STASH"]:
        screen.fill(BLACK)
        for i in range(0, WIDTH, 40): pygame.draw.line(screen, (15, 18, 22), (i,0), (i,HEIGHT))
        for i in range(0, HEIGHT, 40): pygame.draw.line(screen, (15, 18, 22), (0,i), (WIDTH,i))
        
        bunker_rect = pygame.Rect(MAP_WIDTH//2 - 400 - camera_x, MAP_HEIGHT//2 - 300 - camera_y, 800, 600)
        pygame.draw.rect(screen, (25, 28, 35), bunker_rect); pygame.draw.rect(screen, (60, 65, 80), bunker_rect, 4)
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
        draw_task_panel(screen, task_system, 20, HEIGHT - 220)
        
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
                col, row = i % 6, i // 6; rect = pygame.Rect(s_start_x + col*58, s_start_y + row*58, 50, 50)
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
            
            pygame.draw.rect(screen, (30,34,42), rect_prim, border_radius=8); screen.blit(small_font.render("主武器", True, WHITE), (rect_prim.centerx - 25, rect_prim.y + 12))
            w_name_1 = font.render(player.primary_weapon.base_name, True, get_rarity_color(player.primary_weapon.rarity))
            screen.blit(w_name_1, (rect_prim.centerx - w_name_1.get_width()//2, rect_prim.centery + 5))
            if selected_mod_weapon == player.primary_weapon: pygame.draw.rect(screen, YELLOW, rect_prim, 2, border_radius=8)
            elif rect_prim.collidepoint(m_pos): pygame.draw.rect(screen, WHITE, rect_prim, 1, border_radius=8)

            pygame.draw.rect(screen, (30,34,42), rect_sec, border_radius=8); screen.blit(small_font.render("副武器", True, WHITE), (rect_sec.centerx - 25, rect_sec.y + 12))
            w_name_2 = font.render(player.secondary_weapon.base_name, True, get_rarity_color(player.secondary_weapon.rarity))
            screen.blit(w_name_2, (rect_sec.centerx - w_name_2.get_width()//2, rect_sec.centery + 5))
            if selected_mod_weapon == player.secondary_weapon: pygame.draw.rect(screen, YELLOW, rect_sec, 2, border_radius=8)
            elif rect_sec.collidepoint(m_pos): pygame.draw.rect(screen, WHITE, rect_sec, 1, border_radius=8)

            hi = draw_player_inv_grid(screen, p_start_x_m, p_start_y_m, m_x, m_y, allow_weapons=True)
            if hi: hovered_slot_info = hi
            for i in range(24):
                item = player.inventory[i]
                if item and item.type == "WEAPON" and selected_mod_weapon == item.weapon_obj: pygame.draw.rect(screen, YELLOW, (p_start_x_m + (i%6)*58, p_start_y_m + (i//6)*58, 50, 50), 2, border_radius=6)

            detail_rect = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 - 180, 330, 410); pygame.draw.rect(screen, (25,28,35), detail_rect, border_radius=10)
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
            pygame.draw.rect(screen, (15, 18, 22), list_rect, border_radius=6); pygame.draw.rect(screen, (50, 55, 65), list_rect, 1, border_radius=6)
            list_surf = pygame.Surface((list_rect.width, max(list_rect.height, (len(arsenal_weapons_list)+1)//2 * 50))); list_surf.fill((15, 18, 22))
            
            for i, wep in enumerate(arsenal_weapons_list):
                col, row = i % 2, i // 2; box = pygame.Rect(col*335 + 10, row*50 + 5, 315, 42)
                is_sel = (i == selected_arsenal_idx)
                pygame.draw.rect(list_surf, (40, 45, 55), box, border_radius=6); pygame.draw.rect(list_surf, YELLOW if is_sel else GRAY, box, 2 if is_sel else 1, border_radius=6)
                c = get_rarity_color(wep.rarity); name_surf = small_font.render(wep.full_name, True, c); list_surf.blit(name_surf, (box.x + 10, box.y + 10))
                aff_txt = ",".join(wep.affixes) if wep.affixes else "無"
                stat_surf = tiny_font.render(f"傷:{wep.damage} [{aff_txt}]", True, WHITE); list_surf.blit(stat_surf, (box.right - stat_surf.get_width() - 10, box.y + 14))
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
                        if rect.collidepoint(m_x, m_y): hovered_slot_info = {"source": "PLAYER", "idx": i, "item": item}; pygame.draw.rect(screen, WHITE, rect, 2, border_radius=6)
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
        if images.get("bg"):
            bg_w, bg_h = WIDTH, HEIGHT
            for x in range(0, MAP_WIDTH, bg_w):
                for y in range(0, MAP_HEIGHT, bg_h):
                    draw_x, draw_y = x - int(camera_x), y - int(camera_y)
                    if draw_x + bg_w > 0 and draw_x < WIDTH and draw_y + bg_h > 0 and draw_y < HEIGHT: screen.blit(images["bg"], (draw_x, draw_y))
        else: screen.fill(BLACK)
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
            
        if game_state == "PLAYING" and not show_inventory:
            for c in chests:
                if c.state == "CLOSED" and math.hypot(player.x - c.x, player.y - c.y) < 70:
                    has_key = any(item.type == "KEY" for item in player.inventory if item)
                    t = "[F] 開啟木箱" if c.type == "NORMAL" else ("[F] 消耗金鑰匙" if has_key else "需要金鑰匙")
                    t_c = WHITE if c.type == "NORMAL" or has_key else RED
                    bg_r = pygame.Rect(c.x - camera_x - 40, c.y - camera_y - 50, font.size(t)[0]+20, 25)
                    popup = pygame.Surface((bg_r.width, bg_r.height), pygame.SRCALPHA); pygame.draw.rect(popup, (20, 20, 25, 200), popup.get_rect(), border_radius=4)
                    screen.blit(popup, (bg_r.x, bg_r.y)); screen.blit(small_font.render(t, True, t_c), (bg_r.x+10, bg_r.y+3))
            for g in items:
                if g.item_type not in ["EXP", "MAGNET", "BOMB", "SHIELD"] and math.hypot(player.x - g.x, player.y - g.y) < 70:
                    bg_r = pygame.Rect(g.x - camera_x - 30, g.y - camera_y - 40, 60, 25)
                    popup = pygame.Surface((bg_r.width, bg_r.height), pygame.SRCALPHA); pygame.draw.rect(popup, (20, 20, 25, 200), popup.get_rect(), border_radius=4)
                    screen.blit(popup, (bg_r.x, bg_r.y)); screen.blit(small_font.render("[F] 撿取", True, WHITE), (bg_r.x+5, bg_r.y+3))
        
        draw_minimap(screen)
        
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
            weapon_str, w_c = f"【密技】全解鎖: {active_wep.full_name} (按E切換)", YELLOW
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
            time_sec = extraction_timer // FPS; mins, secs = time_sec // 60, time_sec % 60
            color = WHITE if time_sec > 30 else RED
            screen.blit(large_font.render(f"撤離倒數: {mins:02d}:{secs:02d}", True, color), (WIDTH//2 - 120, 20))
            if extract_progress > 0:
                pygame.draw.rect(screen, GRAY, (WIDTH//2 - 100, 110, 200, 15)); pygame.draw.rect(screen, GREEN, (WIDTH//2 - 100, 110, 200 * (extract_progress / 120), 15))
            if boss_army_active: screen.blit(large_font.render("警告：超時！狂暴大軍來襲！", True, RED), (WIDTH//2 - 220, 140))
            
        if boss_active:
            draw_boss_health_bar(screen, boss)
            if boss.state == "ENTRANCE":
                entrance_text = font.render(boss.get_intro_title(), True, YELLOW)
                screen.blit(entrance_text, (WIDTH//2 - entrance_text.get_width()//2, HEIGHT//2 - 200))
                for i, line in enumerate(boss.get_intro_lines()):
                    warning = font.render(line, True, RED if i == 0 else WHITE)
                    screen.blit(warning, (WIDTH//2 - warning.get_width()//2, HEIGHT//2 - 150 + i * 40))
            else:
                state_message, state_color = boss.get_state_message()
                state_txt = font.render(state_message, True, state_color)
                screen.blit(state_txt, (WIDTH//2 - state_txt.get_width()//2, HEIGHT - 90))

        if player.god_mode: screen.blit(font.render("【無敵模式啟用】", True, YELLOW), (WIDTH//2 - 80, 20))
        draw_upgrade_summary(screen, WIDTH - 260, HEIGHT - 300, max_items=5)
        draw_task_panel(screen, task_system, 20, HEIGHT - 220)
        
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
>>>>>>> 5fe3c3b9a6cb6e15508d0cc26521ee2ec490b8fd
