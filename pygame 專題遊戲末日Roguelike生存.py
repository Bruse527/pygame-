import pygame
import random
import math
import os

# 初始化遊戲跟音效
pygame.init()
pygame.mixer.init()

# 64個音效通道
pygame.mixer.set_num_channels(64) 

# 自適應全螢幕與畫布系統 
window_width = 1024
window_height = 768
WIDTH = window_width
HEIGHT = window_height
mapWidth = 4200
mapHeight = 2600
scaleFactor = 1.0

isFullScreen = False
offsetX = 0
offsetY = 0

#隱藏滑鼠游標，因為有繪製準新
pygame.mouse.set_visible(False) 

# real_screen 是實際顯示的視窗，screen 變成我們內部固定 1024x768 的畫布
screenReal = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
screen = pygame.Surface((window_width, window_height)) 
pygame.display.set_caption("末日肉鴿生存")

# 切換全螢幕模式，內部畫布仍保持固定大小
def toggleFullScreen():
    global isFullScreen, screenReal
    if isFullScreen == False:
        isFullScreen = True
        info = pygame.display.Info()
        screenReal = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    else:
        isFullScreen = False
        screenReal = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)

clock = pygame.time.Clock()
FPS = 60

camX = 0
camY = 0
screenShake = 0

# 顏色定義
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
SCRAP_COLOR = (200, 200, 200)
CARD_COLOR = (30, 30, 40)

cardTypeColors = {"attack": (120, 35, 45), "support": (35, 75, 130), "life": (35, 110, 65)}
cardTypeLabels = {"attack": "攻擊", "support": "支援", "life": "生命"}
shieldColor = (0, 150, 255)
expColor = (124, 252, 0)
hpColor = (255, 50, 50)

# 根據屏幕大小動態調整字體大小
chineseFonts = "microsoftjhenghei,pingfangtc,stheiti,simhei"
font = pygame.font.SysFont(chineseFonts, 24)
large_font = pygame.font.SysFont(chineseFonts, 42)
small_font = pygame.font.SysFont(chineseFonts, 18)
tiny_font = pygame.font.SysFont(chineseFonts, 14)

# 資源目錄與資料夾初始化
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
imageDir = os.path.join(BASE_DIR, "images")
audioDir = os.path.join(BASE_DIR, "audio")

if not os.path.exists(imageDir):
    os.makedirs(imageDir)
if not os.path.exists(audioDir):
    os.makedirs(audioDir)

images = {}
animations = {}
sounds = {}

# 圖片載入函式，支援縮放與不存在檢查
def load_image(name, filename, size=None):
    try:
        path = os.path.join(imageDir, filename)
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            if size != None:
                images[name] = pygame.transform.scale(img, size)
            else:
                images[name] = img
        else:
            images[name] = None
    except:
        images[name] = None

# 從資料夾讀取多幀圖檔並轉成動畫列表
def loadAnimation(name, folder_name, size):
    folder_path = os.path.join(imageDir, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        animations[name] = None
        return
    
    frames = []
    files = os.listdir(folder_path)
    files.sort() 
    for f in files:
        if f.endswith(".png") or f.endswith(".jpg"):
            path = os.path.join(folder_path, f)
            image = pygame.image.load(path).convert_alpha()
            image = pygame.transform.scale(image, size)
            frames.append(image)
            
    if len(frames) > 0:
        animations[name] = frames
    else:
        animations[name] = None

# 檢查檔案是否存在並設定音量的音效載入函式
def loadSound(name, filename):
    try:
        path = os.path.join(audioDir, filename)
        if os.path.exists(path):
            sounds[name] = pygame.mixer.Sound(path)
            sounds[name].set_volume(0.5)
        else:
            sounds[name] = None
    except:
        sounds[name] = None
# 圖片
load_image("crosshair", "crosshair.png", (32, 32))  # 準心圖片(沒有找到適合的圖片，所以有另外繪製十字替代)
load_image("bg", "bg.png", (WIDTH, HEIGHT))  # 遊戲背景圖片
#load_image("drop_EXP", "drop_exp.png", (20, 20))  # 經驗值掉落圖示
load_image("chest_NORMAL_CLOSED", "chest_normal_closed.png", (50, 40))  # 普通寶箱關閉狀態圖片
load_image("chest_NORMAL_OPEN", "chest_normal_open.png", (50, 40))  # 普通寶箱開啟狀態圖片
load_image("chest_LOCKED_CLOSED", "chest_locked_closed.png", (50, 40))  # 鎖定寶箱關閉狀態圖片
load_image("chest_LOCKED_OPEN", "chest_locked_open.png", (50, 40))  # 鎖定寶箱開啟狀態圖片

load_image("bullet_normal", "bullet_normal.png", (30, 30))  # 普通子彈圖示
load_image("bullet_piercing", "bullet_piercing.png", (25, 25))  # 穿甲子彈圖示
load_image("bullet_shotgun", "bullet_shotgun.png", (30, 30))  # 散彈槍子彈圖示
load_image("bullet_flamethrower", "bullet_flame.png", (90, 65))  # 火焰噴射器子彈圖示
load_image("bullet_laser", "bullet_laser.png", (37, 30))  # 雷射子彈圖示
load_image("bullet_cannon", "bullet_cannon.png", (90, 90))  # 大炮砲彈圖示
load_image("bullet_frost", "bullet_frost.png", (30, 30))  # 冰霜子彈圖示
load_image("bullet_flame_grenade", "bullet_grenade.png", (60, 30))  # 火焰榴彈圖示
load_image("bullet_plasma", "bullet_plasma.png", (40, 40))  # 等離子子彈圖示
load_image("enemy_bullet", "bullet_enemy.png", (30, 30))  # 敵人子彈圖示

#圖片逐格動畫
loadAnimation("player", "player", (65, 65))  # 玩家角色動畫
loadAnimation("enemy_normal", "enemy_normal", (120, 100))  # 普通敵人動畫
loadAnimation("enemy_elite", "enemy_elite", (90, 90))  # 菁英敵人動畫
loadAnimation("enemy_kamikaze", "enemy_kamikaze", (30, 50)) # 自爆怪動畫
loadAnimation("dummy", "dummy", (55, 80))  # 訓練假人動畫
loadAnimation("boss_yellow", "boss_yellow", (200, 155))    # 第一隻 Boss
loadAnimation("boss_charger", "boss_charger", (185, 185))  # 第二隻 Boss
loadAnimation("boss_red", "boss_red", (200, 200))          # 第三隻 Boss

#基礎音效
loadSound("dash", "dash.wav")  # 衝刺音效
loadSound("hit", "hit.wav")  # 攻擊命中音效
loadSound("levelup", "levelup.wav")  # 升級音效
loadSound("hurt", "hurt.wav")  # 受傷音效
loadSound("boss_bgm", "boss.wav")  # Boss 戰背景音樂
loadSound("gameover", "gameover.wav")  # 遊戲結束音效
loadSound("exp", "exp.wav")  # 獲得經驗值音效

#備用槍枝音效
#loadSound("shoot_normal", "shoot_normal.wav")  # 普通射擊音效
#loadSound("shoot_laser", "shoot_laser.wav")  # 雷射射擊音效
#loadSound("shoot_shotgun", "shoot_shotgun.wav")  # 散彈槍射擊音效
#loadSound("shoot_cannon", "shoot_cannon.wav")  # 大炮發射音效
#loadSound("shoot_flame", "shoot_flame.wav")  # 火焰噴射器發射音效

#子彈打空時會觸發
loadSound("empty_click", "empty.wav") # 卡彈聲
loadSound("reload", "reload.wav")     # 換彈聲

# 專屬武器音效載入，若檔案缺失則使用備援音效
def load_weapon_sound(wk, fn, fb):
    p = os.path.join(audioDir, fn)
    if os.path.exists(p):
        sounds[wk] = pygame.mixer.Sound(p)
    else:
        if fb in sounds:
            sounds[wk] = sounds[fb]
        else:
            sounds[wk] = None
            
    if wk in sounds and sounds[wk] != None:
        sounds[wk].set_volume(0.08)

#槍枝音效
load_weapon_sound("snd_pistol", "pistol.wav", "shoot_normal")  # 手槍射擊音效
load_weapon_sound("snd_sniper", "sniper.wav", "shoot_cannon")  # 狙擊槍射擊音效
load_weapon_sound("snd_shotgun", "shotgun.wav", "shoot_shotgun")  # 散彈槍射擊音效
load_weapon_sound("snd_mg", "submachine_gun.wav", "shoot_normal")  # 衝鋒槍射擊音效
load_weapon_sound("snd_flamethrower", "flamethrower.wav", "shoot_flame")  # 火焰噴射器發射音效
load_weapon_sound("snd_laser", "laser.wav", "shoot_laser")  # 雷射武器發射音效
load_weapon_sound("snd_cannon", "cannon.wav", "shoot_cannon")  # 大炮發射音效
load_weapon_sound("snd_frost", "frost.wav", "shoot_flame")  # 冰霜武器發射音效
load_weapon_sound("snd_heavy_mg", "heavy_mg.wav", "shoot_shotgun")  # 重機槍射擊音效
load_weapon_sound("snd_rifle", "rifle.wav", "shoot_cannon")  # 步槍射擊音效
load_weapon_sound("snd_grenade", "grenade.wav", "shoot_cannon")  # 手榴彈爆炸音效
load_weapon_sound("snd_plasma", "plasma.wav", "shoot_laser")  # 等離子武器發射音效

# 背景音樂載入與循環播放
bgm_path = os.path.join(audioDir, "bgm.mp3")
if os.path.exists(bgm_path):
    pygame.mixer.music.load(bgm_path)
    pygame.mixer.music.set_volume(0.5) #音量大小50%
    pygame.mixer.music.play(-1) 

# 音效播放、停止函式
# 紀錄音效最後播放時間
sound_last_played = {}

def playSound(name, loop=0, custom_cooldown=None):
    if name not in sounds or sounds[name] == None:
        return
    
    now = pygame.time.get_ticks()
    cooldown = 0
    # 自動為容易重疊的音效設定冷卻毫秒防止聲音瞬間爆音
    if custom_cooldown != None:
        cooldown = custom_cooldown
    else:
        if name == "hit": cooldown = 40
        elif name == "shoot_cannon": cooldown = 60
        elif name == "exp": cooldown = 20
        elif name == "empty_click": cooldown = 250
        else: cooldown = 0
    
    if cooldown > 0:
        if name in sound_last_played:
            if now - sound_last_played[name] < cooldown:
                # 如果在冷卻時間內直接攔截不播放
                return 
        sound_last_played[name] = now
        
    # 槍聲動態音量變化讓連續開火聽起來有高低起伏，比較不會那麼死板
    if name.startswith("snd_") or name.startswith("shoot_"):
        sounds[name].set_volume(random.uniform(0.06, 0.11))
        
    sounds[name].play(loops=loop)

def stopSound(name):
    if name in sounds and sounds[name] != None:
        sounds[name].stop()

# UI 繪製函數，統一風格的面板與標題顯示
def draw_ui_panel(surface, rect, title, accentColor):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (18, 20, 26, 245), panel.get_rect(), border_radius=12)
    pygame.draw.rect(panel, (50, 55, 65), panel.get_rect(), 2, border_radius=12)
    pygame.draw.rect(panel, (30, 34, 42, 255), pygame.Rect(0, 0, rect.width, 45), border_top_left_radius=12, border_top_right_radius=12)
    pygame.draw.line(panel, accentColor, (0, 45), (rect.width, 45), 2)
    surface.blit(panel, (rect.x, rect.y))
    t_surf = large_font.render(title, True, accentColor)
    surface.blit(t_surf, (rect.centerx - t_surf.get_width()//2, rect.y -8)) #視窗標題

# 繪製懸浮按鈕，根據滑鼠位置改變外觀並回傳懸浮狀態
def draw_hover_button(surface, rect, text, baseColor, hoverColor=None, textColor=WHITE):
    if hoverColor == None:
        r = baseColor[0] + 40
        if r > 255: r = 255
        g = baseColor[1] + 40
        if g > 255: g = 255
        b = baseColor[2] + 40
        if b > 255: b = 255
        hoverColor = (r, g, b)
        
    mouse_pos = pygame.mouse.get_pos()
    isHover = False
    if rect.collidepoint(mouse_pos):
        isHover = True
        
    if isHover:
        pygame.draw.rect(surface, hoverColor, rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, rect, 2, border_radius=8)
    else:
        pygame.draw.rect(surface, baseColor, rect, border_radius=8)
        pygame.draw.rect(surface, GRAY, rect, 2, border_radius=8)
        
    t_surf = font.render(text, True, textColor)
    surface.blit(t_surf, (rect.centerx - t_surf.get_width() // 2, rect.centery - t_surf.get_height() // 2))
    return isHover

# 繪製物品提示框，根據物品類型顯示詳細屬性或簡單名稱
def draw_item_tooltip(surface, item, mx, my):
    if item == None:
        return
    if item.type == "WEAPON":
        wep = item.weapon_obj
        ttRect = pygame.Rect(mx+15, my, 240, 95)
        if ttRect.right > WIDTH:
            ttRect.x -= 270
        if ttRect.bottom > HEIGHT:
            ttRect.y -= 105
        pygame.draw.rect(surface, (15, 18, 22), ttRect, border_radius=8)
        c = getRarityColor(wep.rarity)
        pygame.draw.rect(surface, c, ttRect, 2, border_radius=8)
        surface.blit(font.render(wep.full_name, True, c), (ttRect.x+10, ttRect.y+10))
        surface.blit(small_font.render("傷害: " + str(wep.damage) + "   冷卻: " + str(wep.shoot_delay), True, WHITE), (ttRect.x+10, ttRect.y+40))
        
        affStr = ""
        if len(wep.affixes) > 0:
            for a in wep.affixes:
                affStr += a + ","
            affStr = affStr[:-1] 
        else:
            affStr = "無"
            
        surface.blit(small_font.render("屬性: " + affStr, True, YELLOW), (ttRect.x+10, ttRect.y+65))
    else:
        w = font.size(item.name)[0] + 30
        if w < 150: w = 150
        ttRect = pygame.Rect(mx+15, my, w, 45)
        if ttRect.right > WIDTH:
            ttRect.x -= (ttRect.width + 30)
        pygame.draw.rect(surface, (20, 22, 28), ttRect, border_radius=6)
        pygame.draw.rect(surface, GRAY, ttRect, 1, border_radius=6)
        surface.blit(font.render(item.name, True, WHITE), (ttRect.x+15, ttRect.y+10))

# 繪製終端機面板，顯示任務提示、重要資訊或劇情對話，並根據時間添加閃爍效果
def draw_terminal(surface, rect, baseColor, text, icon_text):
    pygame.draw.rect(surface, BLACK, rect.move(5,5), border_radius=8)
    pygame.draw.rect(surface, (45, 50, 60), rect, border_radius=8)
    sRect = pygame.Rect(rect.x+10, rect.y+10, rect.width-20, rect.height-30)
    pygame.draw.rect(surface, (20, 22, 28), sRect, border_radius=4)
    pulse = int(abs(math.sin(pygame.time.get_ticks()*0.003))*50)
    
    r = baseColor[0] + pulse
    if r > 255: r = 255
    g = baseColor[1] + pulse
    if g > 255: g = 255
    b = baseColor[2] + pulse
    if b > 255: b = 255
    gc = (r, g, b)
    
    pygame.draw.rect(surface, gc, sRect, 2, border_radius=4)
    surf = font.render(icon_text, True, gc)
    surface.blit(surf, (sRect.centerx - surf.get_width()//2, sRect.centery - surf.get_height()//2))
    pygame.draw.line(surface, baseColor, (rect.x+15, rect.bottom-10), (rect.right-15, rect.bottom-10), 3)
    lbl = small_font.render(text, True, WHITE)
    surface.blit(lbl, (rect.centerx - lbl.get_width()//2, rect.y - 25))

# 繪製迷你地圖，顯示玩家、目標點、Boss 和重要物品的位置，並根據距離調整圖示大小與顏色
def drawMinimap(surface):
    map_w = 160
    map_h = 120
    m_rect = pygame.Rect(WIDTH - map_w - 20, 20, map_w, map_h)
    mmSurf = pygame.Surface((map_w, map_h), pygame.SRCALPHA)
    pygame.draw.rect(mmSurf, (10, 10, 20, 180), mmSurf.get_rect(), border_radius=5)
    pygame.draw.rect(mmSurf, (50, 200, 50), mmSurf.get_rect(), 2, border_radius=5)
    surface.blit(mmSurf, m_rect.topleft)
    # 根據玩家在地圖上的位置繪製玩家圖示，並根據距離調整顏色與大小
    if extractionPt != None:
        ex = m_rect.x + (extractionPt.x / mapWidth) * map_w
        ey = m_rect.y + (extractionPt.y / mapHeight) * map_h
        pygame.draw.circle(surface, GREEN, (int(ex), int(ey)), 4)
    # 根據 Boss 在地圖上的位置繪製 Boss 圖示，並根據距離調整顏色與大小   
    if isBossActive == True and boss != None:
        bx = m_rect.x + (boss.x / mapWidth) * map_w
        by = m_rect.y + (boss.y / mapHeight) * map_h
        pygame.draw.circle(surface, RED, (int(bx), int(by)), 5)
    # 根據掉落物在地圖上的位置繪製掉落物圖示，並根據距離添加閃爍效果以增加可見度   
    if lostItem != None:
        lx = m_rect.x + (lostItem.x / mapWidth) * map_w
        ly = m_rect.y + (lostItem.y / mapHeight) * map_h
        p = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 4)
        pygame.draw.circle(surface, YELLOW, (int(lx), int(ly)), 4)
        pygame.draw.circle(surface, RED, (int(lx), int(ly)), 5 + p, 1)
        
    px = m_rect.x + (player.x / mapWidth) * map_w
    py = m_rect.y + (player.y / mapHeight) * map_h
    pygame.draw.circle(surface, BLUE, (int(px), int(py)), 4)

# Boss方向提示箭頭(會根據距離調整大小與顏色)
def drawBossDirection(surface, bossObj, cam_x, cam_y):
    if bossObj == None:
        return
    if hasattr(bossObj, "state") and bossObj.state == "DEFEAT":
        return
        
    bx = bossObj.x - cam_x
    by = bossObj.y - cam_y
    if bx >= 0 and bx <= WIDTH and by >= 0 and by <= HEIGHT:
        return 
        
    cx = WIDTH / 2
    cy = HEIGHT / 2
    direction = pygame.math.Vector2(bx - cx, by - cy)
    if direction.length_squared() == 0:
        return
    direction.normalize_ip()
    
    margin = 56
    scaleX = 9999
    scaleY = 9999
    if abs(direction.x) > 0.001:
        scaleX = (WIDTH / 2 - margin) / abs(direction.x)
    if abs(direction.y) > 0.001:
        scaleY = (HEIGHT / 2 - margin) / abs(direction.y)
        
    minScale = scaleX
    if scaleY < scaleX:
        minScale = scaleY
        
    arrow_pos = pygame.math.Vector2(cx, cy) + direction * minScale
    side = direction.rotate(90)
    tip = arrow_pos + direction * 25
    left = arrow_pos - direction * 18 + side * 15
    right = arrow_pos - direction * 18 - side * 15
    
    pts = [(int(tip.x), int(tip.y)), (int(left.x), int(left.y)), (int(right.x), int(right.y))]
    pygame.draw.polygon(surface, BLACK, pts)
    pygame.draw.polygon(surface, YELLOW, pts, 0)
    pygame.draw.polygon(surface, RED, pts, 3)

#  Boss 血條
def drawBossHealth(surface, bossObj):
    bar_rect = pygame.Rect(110, HEIGHT - 52, WIDTH - 220, 28)
    ratio = bossObj.hp / bossObj.max_hp
    if ratio < 0: ratio = 0
    if ratio > 1: ratio = 1
    
    pulse = abs(math.sin(pygame.time.get_ticks() * 0.006))
    
    phase = 1
    if hasattr(bossObj, "phase"):
        phase = bossObj.phase
        
    if phase >= 2: fillColor = (255, 35, 55)
    else: fillColor = (255, 185, 35)
        
    edgeColor = WHITE
    if bossObj.state == "TRANSFORM" or bossObj.state == "CHARGE" or bossObj.state == "AIM" or bossObj.state == "RAGE_WINDUP":
        edgeColor = (255, 230, 120)

    shadow = pygame.Surface((bar_rect.width + 28, bar_rect.height + 34), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 160), (14, 17, bar_rect.width, bar_rect.height), border_radius=7)
    surface.blit(shadow, (bar_rect.x - 14, bar_rect.y - 17))
    pygame.draw.rect(surface, (28, 18, 24), bar_rect.inflate(18, 16), border_radius=8)
    pygame.draw.rect(surface, edgeColor, bar_rect.inflate(18, 16), 3, border_radius=8)
    pygame.draw.rect(surface, (75, 60, 65), bar_rect, border_radius=5)

    fillW = int(bar_rect.width * ratio)
    if fillW > 0:
        fillRect = pygame.Rect(bar_rect.x, bar_rect.y, fillW, bar_rect.height)
        pygame.draw.rect(surface, fillColor, fillRect, border_radius=5)
        hlW = fillRect.width - 8
        if hlW < 0: hlW = 0
        highlight = pygame.Rect(fillRect.x + 4, fillRect.y + 4, hlW, 7)
        if highlight.width > 0:
            pygame.draw.rect(surface, (255, 245, 170), highlight, border_radius=3)
        if ratio < 0.35 or bossObj.state == "TRANSFORM" or bossObj.state == "RAGE_DASH":
            pygame.draw.circle(surface, (255, 255, 210), (fillRect.right - 4, fillRect.centery), int(10 + pulse * 7), 2)

    for i in range(1, 12):
        x = bar_rect.x + int(bar_rect.width * i / 12)
        pygame.draw.line(surface, (45, 28, 34), (x, bar_rect.y + 3), (x, bar_rect.bottom - 3), 2)

    name = "BOSS"
    if hasattr(bossObj, "name"): name = bossObj.name
        
    phaseLabel = ""
    if hasattr(bossObj, "phase"):
        phaseLabel = "  PHASE " + str(phase)
        
    titleTxt = font.render(name + "  Lv." + str(bossObj.spawn_level) + phaseLabel, True, edgeColor)
    showHp = int(bossObj.hp)
    if showHp < 0: showHp = 0
    hpTxt = small_font.render(str(showHp) + " / " + str(bossObj.max_hp), True, WHITE)
    surface.blit(titleTxt, (bar_rect.x, bar_rect.y - titleTxt.get_height() - 14))
    surface.blit(hpTxt, (bar_rect.right - hpTxt.get_width(), bar_rect.y - hpTxt.get_height() - 12))
    
    if bossObj.state == "TRANSFORM":
        rageTxt = small_font.render("RAGE CORE REBOOTING - HP REFILL", True, RED)
        surface.blit(rageTxt, (bar_rect.centerx - rageTxt.get_width() // 2, bar_rect.y - 58))

# 當遺失物品距離玩家過遠時會有箭頭顯示方向提示(跟BOSS的差不多)
def drawLostArrow(surface, cx, cy):
    if lostItem == None: return
        
    dx = lostItem.x - player.x
    dy = lostItem.y - player.y
    dist = math.sqrt(dx**2 + dy**2)
    
    minDim = WIDTH
    if HEIGHT < WIDTH: minDim = HEIGHT
    
    if dist > minDim * 0.4:
        angle = math.atan2(dy, dx)
        r = minDim / 2 - 60
        ax = WIDTH/2 + math.cos(angle)*r
        ay = HEIGHT/2 + math.sin(angle)*r
        side = pygame.math.Vector2(math.cos(angle), math.sin(angle)).rotate(90)
        p = pygame.math.Vector2(ax, ay)
        d = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        pts = [p + d*20, p - d*10 + side*15, p - d*10 - side*15]
        pygame.draw.polygon(surface, YELLOW, pts)
        pygame.draw.polygon(surface, RED, pts, 2)
        txt = small_font.render("遺失物", True, YELLOW)
        surface.blit(txt, (ax - txt.get_width()//2, ay - 35))

# 顯示最近選擇的強化項目與總數量，超過上限則顯示隱藏提示
def drawUpgradeSummary(surface, x, y, max_items=6, title="已選強化"):
    panel_width = 240
    row_height = 26
    hidden_count = len(chosenUpgrades) - max_items
    if hidden_count < 0: hidden_count = 0
    
    row_count = len(chosenUpgrades)
    if row_count > max_items: row_count = max_items
    if row_count == 0: row_count = 1
    
    panel_height = 40 + row_count * row_height
    if hidden_count > 0: panel_height += row_height
        
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    panel.fill((18, 20, 30, 185))
    surface.blit(panel, (x, y))
    pygame.draw.rect(surface, WHITE, (x, y, panel_width, panel_height), 2, border_radius=8)

    total_count = 0
    for u in chosenUpgrades:
        total_count += u["count"]
        
    if len(chosenUpgrades) > 0: title_label = title + " (" + str(total_count) + ")"
    else: title_label = title
        
    surface.blit(small_font.render(title_label, True, YELLOW), (x + 14, y + 10))

    if len(chosenUpgrades) == 0:
        surface.blit(small_font.render("尚未選擇", True, GRAY), (x + 14, y + 40))
        return
        
    showList = chosenUpgrades[-max_items:]
    i = 0
    for upgrade in showList:
        if upgrade["count"] > 1: suffix = " x" + str(upgrade['count'])
        else: suffix = ""
        surface.blit(small_font.render(upgrade['title'] + suffix, True, WHITE), (x + 14, y + 40 + i * row_height))
        i += 1

    if hidden_count > 0:
        surface.blit(small_font.render("還有 " + str(hidden_count) + " 種...", True, GRAY), (x + 14, y + 40 + len(showList) * row_height))

# 任務面板 會依照是否在戰鬥中顯示不同的資訊量與樣式(因為太多資訊所以改成戰鬥中會有迷你顯示)
def drawTaskPanel(surface, taskSystem, x, y, compact=False):
    # 戰鬥中的迷你模式
    if compact == True:
        if taskSystem.current_task == None:
            return
        task = taskSystem.current_task
        
        if task.objective_value > 0:
            progress_percent = task.current_progress / task.objective_value
            if progress_percent > 1.0: progress_percent = 1.0
        else:
            progress_percent = 0
            
        # 繪製半透明極簡小面板，背景 + 邊框，不擋畫面
        miniSurf = pygame.Surface((180, 45), pygame.SRCALPHA)
        pygame.draw.rect(miniSurf, (20, 24, 32, 150), miniSurf.get_rect(), border_radius=6)
        pygame.draw.rect(miniSurf, (100, 200, 100, 150), miniSurf.get_rect(), 1, border_radius=6)
        surface.blit(miniSurf, (x - 10, y - 5))
        
        # 任務標題
        surface.blit(tiny_font.render("目標: " + task.name, True, YELLOW), (x, y - 2))
        
        # 縮小的迷你進度條
        bar_w = 160
        pygame.draw.rect(surface, (60, 65, 75), (x, y + 20, bar_w, 10), border_radius=5)
        pygame.draw.rect(surface, (0, 200, 100), (x, y + 20, bar_w * progress_percent, 10), border_radius=5)
        
        # 進度數字
        prog_txt = tiny_font.render(str(int(task.current_progress)) + "/" + str(task.objective_value), True, WHITE)
        surface.blit(prog_txt, (x + bar_w//2 - prog_txt.get_width()//2, y + 19))
        return

    # 常規任務面板會顯示更多資訊
    panel_width = 320
    panel_height = 180
    panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (18, 20, 26, 245), panel.get_rect(), border_radius=12)
    pygame.draw.rect(panel, (100, 200, 100), panel.get_rect(), 2, border_radius=12)
    header = pygame.Rect(0, 0, panel_width, 40)
    pygame.draw.rect(panel, (30, 34, 42, 255), header, border_top_left_radius=12, border_top_right_radius=12)
    pygame.draw.line(panel, (100, 200, 100), (0, 40), (panel_width, 40), 2)
    title_surf = font.render("任務", True, (100, 200, 100))
    panel.blit(title_surf, (panel_width//2 - title_surf.get_width()//2, 8))
    surface.blit(panel, (x, y))
    
    if taskSystem.current_task != None:
        task = taskSystem.current_task
        surface.blit(font.render(task.name, True, YELLOW), (x + 15, y + 50))
        surface.blit(small_font.render(task.description, True, WHITE), (x + 15, y + 85))
        
        if task.objective_value > 0:
            progress_percent = task.current_progress / task.objective_value
            if progress_percent > 1.0: progress_percent = 1.0
        else:
            progress_percent = 0
            
        pygame.draw.rect(surface, GRAY, (x + 15, y + 120, 280, 12), border_radius=3)
        pygame.draw.rect(surface, (0, 200, 100), (x + 15, y + 120, 280 * progress_percent, 12), border_radius=3)
        surface.blit(tiny_font.render(str(int(task.current_progress)) + "/" + str(task.objective_value), True, WHITE), (x + 20, y + 121))
        
        reward_text = ""
        if task.reward_type == "scrap": reward_text = "獎勵: " + str(task.reward_amount) + " 廢料"
        elif task.reward_type == "exp": reward_text = "獎勵: " + str(task.reward_amount) + " 經驗"
        elif task.reward_type == "dmg_bonus": reward_text = "獎勵: +" + str(task.reward_amount) + " 傷害"
        elif task.reward_type == "max_hp": reward_text = "獎勵: +" + str(task.reward_amount) + " 血量"
        elif task.reward_type == "max_stamina": reward_text = "獎勵: +" + str(task.reward_amount) + " 體力"
        surface.blit(small_font.render(reward_text, True, YELLOW), (x + 15, y + 150))
    else:
        no_task = small_font.render("暫無可用任務", True, GRAY)
        surface.blit(no_task, (x + panel_width//2 - no_task.get_width()//2, y + 100))

# 繪製指南與介紹的彈出面板
def drawGuidePopup(surface):
    global changelogMaxScroll, gd_surf 
    
    # 把面板放大容納更多說明文字
    rect = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 250, 700, 500)
    draw_ui_panel(surface, rect, "操作指南與遊戲介紹", BLUE)
    
    close_rect = pygame.Rect(rect.right - 45, rect.y + 10, 35, 35)
    draw_hover_button(surface, close_rect, "X", (180, 60, 60), RED, WHITE)

    # 定義文字可視區域
    view_rect = pygame.Rect(rect.x + 25, rect.y + 60, rect.width - 50, rect.height - 80)
    line_height = 28
    total_height = len(guide_text_lines) * line_height

    # 動態計算最大滾動值
    changelogMaxScroll = total_height - view_rect.height
    if changelogMaxScroll < 0: 
        changelogMaxScroll = 0

    if gd_surf == None:
        gd_surf = pygame.Surface((view_rect.width, total_height), pygame.SRCALPHA)

        for i, line in enumerate(guide_text_lines):
            
            # 大標題 以 [ 括號 或 ( 括號開頭  整行變黃色
            if line.startswith("[") or line.startswith("("):
                txt_surf = small_font.render(line, True, YELLOW)
                gd_surf.blit(txt_surf, (0, i * line_height))
            
            # 重點說明 包含半形冒號:   雙色顯示
            elif ":" in line:
                # 直接使用半形冒號作為分隔符
                parts = line.split(":", 1)  # 從第一個半形冒號切開
                
                # 畫冒號與前面的字 亮青色CYAN
                key_text = parts[0] + ":"  
                key_surf = small_font.render(key_text, True, CYAN)
                gd_surf.blit(key_surf, (0, i * line_height))
                
                # 畫冒號後面的字 白色WHITE，接在前面文字的右邊
                if len(parts) > 1:
                    val_surf = small_font.render(parts[1], True, WHITE)
                    gd_surf.blit(val_surf, (key_surf.get_width() + 5, i * line_height))
            
            # 一般內文 白色
            else:
                txt_surf = small_font.render(line, True, WHITE)
                gd_surf.blit(txt_surf, (0, i * line_height))

    # 會直接把畫好的圖放上
    surface.blit(gd_surf, view_rect.topleft, pygame.Rect(0, changelogScroll, view_rect.width, view_rect.height))

    # 旁邊的捲動條 
    if changelogMaxScroll > 0:
        scrollbar_x = view_rect.right + 10
        scrollbar_y = view_rect.y
        scrollbar_h = view_rect.height
        pygame.draw.rect(surface, (40, 45, 55), (scrollbar_x, scrollbar_y, 6, scrollbar_h), border_radius=3)
        
        handle_h = max(40, scrollbar_h * (view_rect.height / total_height))
        handle_y = scrollbar_y + (scrollbar_h - handle_h) * (changelogScroll / changelogMaxScroll)
        pygame.draw.rect(surface, GRAY, (scrollbar_x, handle_y, 6, handle_h), border_radius=3)

# 暫停選單中已獲得強化的總結面板，顯示玩家目前的強化列表與數量
def drawPauseUpgradeLog(surface):
    drawUpgradeSummary(surface, WIDTH//2 - 120, HEIGHT//2 + 150, max_items=8, title="已獲得的強化")

# 玩家背包格子繪製函式，顯示物品圖示、數量與稀有度，並回傳懸浮物品資訊
def drawPlayerInvGrid(surface, start_x, start_y, mx, my, allow_weapons=True):
    hoverInfo = None
    for i in range(24):
        col = i % 6
        row = i // 6
        rect = pygame.Rect(start_x + col*58, start_y + row*58, 50, 50)
        pygame.draw.rect(surface, (25, 28, 35), rect, border_radius=6)
        pygame.draw.rect(surface, (55, 60, 70), rect, 1, border_radius=6)
        item = player.inventory[i]
        
        is_dragging_this = False
        if dragData != None and dragData["source"] == "PLAYER" and dragData["idx"] == i:
            is_dragging_this = True
            
        if item != None and is_dragging_this == False:
            if item.type == "WEAPON":
                if allow_weapons == True:
                    gunName = "gun_" + item.weapon_obj.base_name
                    # 在 UI 背包中畫出槍枝圖片
                    if gunName in images and images[gunName] != None:
                        scaledGun = pygame.transform.scale(images[gunName], (40, 16))
                        surface.blit(scaledGun, scaledGun.get_rect(center=rect.center))
                    else:
                        pygame.draw.circle(surface, getRarityColor(item.weapon_obj.rarity), rect.center, 14)
                else:
                    pygame.draw.circle(surface, (60, 60, 60), rect.center, 14)
            else:
                c = YELLOW
                if item.type == "MED": c = hpColor
                elif item.type == "SCRAP": c = SCRAP_COLOR
                pygame.draw.circle(surface, c, rect.center, 14)
                surface.blit(tiny_font.render(str(item.count), True, WHITE), (rect.right - 18, rect.bottom - 18))
            
            if rect.collidepoint(mx, my) and dragData == None:
                hoverInfo = {"source": "PLAYER", "idx": i, "item": item}
                pygame.draw.rect(surface, WHITE, rect, 2, border_radius=6)
                
    return hoverInfo

# 開啟寶箱的函式
def openChest(c):
    if c.type == "NORMAL": numItems = random.randint(2, 4)
    else: numItems = random.randint(4, 7)
        
    for i in range(numItems):
        randVal = random.random()
        rx = c.x + random.randint(-30, 30)
        ry = c.y + random.randint(-30, 30)
        
        if randVal < 0.2:
            items.append(DropItem(rx, ry, "MED"))
        elif randVal < 0.5:
            items.append(DropItem(rx, ry, "SCRAP", random.randint(2, 5)))
        elif randVal < 0.7:
            rarityRoll = random.random()
            if rarityRoll < 0.6: rarity = "白"
            elif rarityRoll < 0.9: rarity = "藍"
            elif rarityRoll < 0.98: rarity = "紫"
            else: rarity = "金"
            
            wType = random.choice(list(weaponTypes.keys()))
            wep = generateWeapon(wType, rarity)
            items.append(DropItem(rx, ry, "WEAPON", weapon_obj=wep))
        else:
            items.append(DropItem(rx, ry, "EXP", random.randint(1, 3)))
            
    if c.type == "LOCKED":
        items.append(DropItem(c.x, c.y + 20, "MAGNET"))
        items.append(DropItem(c.x, c.y - 20, "BOMB"))
    playSound("exp")


# 類似 RPG 的劇情對話系統 
class DialogueManager:
    def __init__(self):
        self.active = False
        self.current_script = []
        self.index = 0
        self.previous_state = "MENU"
        
    def start(self, script_key, prev_state):
        if script_key not in storyScripts: return
        self.current_script = storyScripts[script_key]
        self.index = 0
        self.active = True
        self.previous_state = prev_state
        global gameState
        # 切換到對話狀態，凍結遊戲
        gameState = "DIALOGUE" 
        # 對話彈出時的提示音效
        playSound("exp")

    def next_line(self):
        # 玩家點擊下一句時的按鍵音效
        playSound("exp")
        self.index += 1
        if self.index >= len(self.current_script):
            self.active = False
            global gameState
            # 對話結束，切回原本的狀態
            gameState = self.previous_state

# 劇情、劇本庫 (本來想寫更完整的劇情+動畫，但後來發現沒時間做動畫，就只用純文字了QQ)
storyScripts = {
    "opening_narrative": [
        ("旁白", "西元 2084 年，智械天災 無預警降臨..."),
        ("旁白", "全球的機械同時失控，人類文明在短短幾天內化為焦土。"),
        ("旁白", "身為少數的倖存者，你找到了這處廢棄的地下防線 地堡 。"),
        ("旁白", "外面的地表已被失控的機械大軍佔領，資源極度匱乏。"),
        ("系統 AI", "系統重啟完成。倖存者，掃描到地表有零星的武器與廢料。"),
        ("系統 AI", "請利用周圍設備強化武裝。準備好後，從下方的閘門前往地表探索吧。")
    ],
    "timeout_warning": [
        ("系統 AI", "警告:撤離時間已逾時！"),
        ("系統 AI", "偵測到極大數量的狂暴機械軍團正在包圍該區域！"),
        ("系統 AI", "無法提供支援，祝你好運...")
    ],
    "boss1_intro": [
        ("系統 AI", "警告:第一隻 BOSS 出現！"),
        ("系統 AI", "它會繞著你旋轉，並持續發射彈幕。"),
        ("系統 AI", "保持移動，抓住空隙反擊！")
    ],
    "boss2_intro": [
        ("系統 AI", "警告:第二隻 BOSS 出現！"),
        ("系統 AI", "黃色軌道代表即將衝刺，變成紅色時會高速突進。"),
        ("系統 AI", "看到箭頭後請立刻閃開，趁牠衝刺後的硬直再反擊。")
    ],
    "boss3_intro": [
        ("系統 AI", "警告:第三隻 BOSS 出現！"),
        ("系統 AI", "一階會緊追著你重砍；半血後會變身進入狂暴二階。"),
        ("系統 AI", "變身時處於無敵狀態，請拉開距離，等紅色震波結束再攻擊！")
    ]
}

dialogueSys = DialogueManager()

# 繪製對話框，根據當前劇本的說話者和內容顯示在畫面下方
def draw_dialogue_box(surface):
    if dialogueSys.active == False or len(dialogueSys.current_script) == 0:
        return
        
    speaker = dialogueSys.current_script[dialogueSys.index][0]
    text = dialogueSys.current_script[dialogueSys.index][1]
    
    bw = int(WIDTH * 0.8)
    bh = 160
    bx = int(WIDTH * 0.1)
    by = int(HEIGHT - 220)
    
    panel = pygame.Surface((bw, bh), pygame.SRCALPHA)
    pygame.draw.rect(panel, (20, 20, 28, 230), panel.get_rect(), border_radius=10)
    pygame.draw.rect(panel, (100, 150, 200), panel.get_rect(), 2, border_radius=10)
    surface.blit(panel, (bx, by))
    
    nameSurf = large_font.render(speaker, True, (255, 200, 50))
    surface.blit(nameSurf, (bx + 20, by + 15))
    
    maxW = bw - 40
    lineY = by + 65
    currentLine = ""
    
    for char in text:
        if font.size(currentLine + char)[0] < maxW:
            currentLine += char
        else:
            surface.blit(font.render(currentLine, True, WHITE), (bx + 20, lineY))
            currentLine = char
            lineY += 30
            
    if currentLine != "":
        surface.blit(font.render(currentLine, True, WHITE), (bx + 20, lineY))
        
    prompt = small_font.render("點擊左鍵 或 空白鍵繼續...", True, GRAY)
    surface.blit(prompt, (bx + bw - prompt.get_width() - 15, by + bh - 25))

# 任務系統與升級機制
class Task:
    def __init__(self, task_id, name, description, objective_type, objective_value, reward_type, reward_amount):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.objective_type = objective_type
        self.objective_value = objective_value
        self.current_progress = 0
        self.is_completed = False
        self.reward_type = reward_type
        self.reward_amount = reward_amount
        
    # 根據當前進度和目標值判斷任務是否完成，完成後標記並回傳 True
    def check_completion(self):
        if self.is_completed == False:
            if self.current_progress >= self.objective_value:
                self.is_completed = True
                return True
        return False
        
    # 根據任務的獎勵類型，將獎勵應用到玩家對象或持久化統計數據中
    def apply_reward(self, player_obj):
        if self.reward_type == "scrap":
            persistentStats["scrap"] += self.reward_amount
        elif self.reward_type == "exp":
            player_obj.exp += self.reward_amount * player_obj.exp_multiplier
        elif self.reward_type == "max_hp":
            persistentStats["max_hp"] += self.reward_amount
            player_obj.max_hp += self.reward_amount
            player_obj.hp += self.reward_amount
            if player_obj.hp > player_obj.max_hp: player_obj.hp = player_obj.max_hp
        elif self.reward_type == "dmg_bonus":
            persistentStats["dmg_bonus"] += self.reward_amount
            player_obj.bullet_damage_bonus += self.reward_amount
        elif self.reward_type == "max_stamina":
            persistentStats["max_stamina"] += self.reward_amount
            player_obj.max_stamina += self.reward_amount
            player_obj.stamina += self.reward_amount

# 任務系統管理當前任務、已完成任務和任務池，提供生成新任務、更新進度和完成任務的功能
class TaskSystem:
    def __init__(self):
        self.current_task = None
        self.completed_tasks = []
        self.task_pool = [
            {"name": "廢料獵人", "desc": "收集 30 個廢料", "type": "collect", "value": 30, "reward_type": "scrap", "reward": 100},
            {"name": "廢料販子", "desc": "收集 50 個廢料", "type": "collect", "value": 50, "reward_type": "scrap", "reward": 150},
            {"name": "初級獵人", "desc": "消滅 20 個敵人", "type": "kill", "value": 20, "reward_type": "exp", "reward": 50},
            {"name": "精英獵人", "desc": "消滅 5 個精英敵人", "type": "kill_elite", "value": 5, "reward_type": "dmg_bonus", "reward": 3},
            {"name": "武裝分子", "desc": "造成 5000 點傷害", "type": "damage", "value": 5000, "reward_type": "scrap", "reward": 100},
            {"name": "長期作戰", "desc": "在突襲中存活 5 分鐘", "type": "survive", "value": 300, "reward_type": "scrap", "reward": 90},
        ]
        self.generate_new_task()
        
    # 從任務池中隨機選擇一個尚未完成的任務作為當前任務，如果所有任務都已完成則設為 None
    def generate_new_task(self):
        available = []
        i = 0
        for t in self.task_pool:
            if i not in self.completed_tasks:
                available.append(t)
            i += 1
        #
        if len(available) > 0:
            td = random.choice(available)
            idx = 0
            for x in self.task_pool:
                if x == td: break
                idx += 1
                
            self.current_task = Task(idx, td["name"], td["desc"], td["type"], td["value"], td["reward_type"], td["reward"])
        else:
            self.current_task = None
            
    # 完成當前任務，將其 ID 加入已完成列表，並生成新任務
    def complete_task(self):
        if self.current_task != None:
            self.completed_tasks.append(self.current_task.task_id)
            self.generate_new_task()
            return True
        return False
        
    # 根據任務類型和事件更新當前任務的進度，如果任務完成則返回 True
    def update_progress(self, objective_type, amount):
        if self.current_task != None:
            if self.current_task.objective_type == objective_type:
                self.current_task.current_progress += amount
                if self.current_task.check_completion():
                    return True
        return False

# 卡牌升級選項定義，每個選項有標題、描述、類型和權重，有些選項可能只在特定模式下出現
upgradeOptions =[
    {"title": "生命躍升", "desc": ["最大血量 +50", "並恢復當前血量"], "type": "life", "weight": 1},
    {"title": "超頻運轉", "desc": ["射速提升", "子彈連發加快"], "type": "attack", "weight": 5},
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
    {"title": "擴容彈匣", "desc": ["挑戰限定", "增加彈藥庫上限"], "type": "attack", "weight": 4, "challenge_only": True}
]

# 權重隨機選擇升級選項以確保挑戰模式限定的選項只在挑戰模式下出現還有更新當前可選擇的升級列表和選擇狀態
def chooseUpgradeCards():
    global currentUpgradeChoices, selectedUpgradePosition
    avail = []
    weights = []
    i = 0
    for opt in upgradeOptions:
        challengeOnly = False
        if "challenge_only" in opt: challengeOnly = opt["challenge_only"]
            
        if challengeOnly == True and gameMode != "CHALLENGE":
            i += 1
            continue
            
        avail.append(i)
        w = 1
        if "weight" in opt: w = opt["weight"]
        weights.append(w)
        i += 1
        
    currentUpgradeChoices = []
    while len(currentUpgradeChoices) < 3 and len(avail) > 0:
        total_weight = 0
        for w in weights: total_weight += w
            
        pick = random.random() * total_weight
        idx = None
        remove_index = -1
        
        c = 0
        for w in weights:
            pick -= w
            if pick <= 0:
                idx = avail[c]
                remove_index = c
                break
            c += 1
            
        if idx == None:
            idx = avail[-1]
            remove_index = len(avail) - 1
            
        currentUpgradeChoices.append(idx)
        avail.pop(remove_index)
        weights.pop(remove_index)
        
    selectedUpgradePosition = None

# 會根據選擇的升級選項對硬玩家狀態的具體增益效果並更新已選擇的升級列表
def apply_upgrade(idx, silent=False):
    global gameState, chosenUpgrades
    opt = upgradeOptions[idx]
    found = False
    for u in chosenUpgrades:
        if u["title"] == opt["title"]:
            u["count"] += 1
            found = True
            break
            
    if found == False:
        chosenUpgrades.append({"title": opt["title"], "count": 1})

    t = opt["title"]
    if t == "生命躍升":
        player.max_hp += 50
        player.hp = player.max_hp
    elif t == "超頻運轉": player.shoot_delay_reduction += 2
    elif t == "能量飲料": player.stamina_regen += 0.2
    elif t == "彈幕擴張": player.bullet_count += 1
    elif t == "高能彈芯": player.bullet_damage_bonus += 5
    elif t == "備用電池":
        player.max_stamina += 25
        player.stamina += 25
    elif t == "輕量推進":
        player.dash_cost -= 5
        if player.dash_cost < 10: player.dash_cost = 10
    elif t == "離子靴": player.base_speed += 0.5
    elif t == "磁吸核心": player.magnet_radius += 50
    elif t == "穩定槍管":
        player.bullet_spread -= 3.0
        if player.bullet_spread < 3.0: player.bullet_spread = 3.0
    elif t == "急救模組":
        player.hp += 60
        if player.hp > player.max_hp: player.hp = player.max_hp
    elif t == "相位護盾": player.invincible_duration += 15
    elif t == "爆燃推進": player.dash_speed += 3
    elif t == "寬幅槍口": player.extra_same_path_bullets += 1
    elif t == "導引模組": player.guidance_level += 1
    elif t == "電弧光環": player.aura_level += 1
    elif t == "再生奈米": player.regen_level += 1
    elif t == "擴容彈匣":
        player.mag_size_bonus += 10
        player.ammo += 10
    
    if silent == False:
        gameState = "PLAYING"
        playSound("levelup")

# 裝備與物品系統
persistentStats = {
    "max_hp": 0, "dmg_bonus": 0, "speed_bonus": 0.0, "max_stamina": 0, 
    "max_shield": 0, "max_energy": 0, "scrap": 0, 
    "weapon_stash": [], "general_stash": [None]*36
}

class Weapon:
    def __init__(self, name, shoot_delay, bullet_type, damage, sound_name="shoot_normal", recoil=2.0):
        self.base_name = name
        self.shoot_delay = shoot_delay
        self.bullet_type = bullet_type
        self.damage = damage
        self.sound_name = sound_name
        self.base_recoil = recoil
        self.rarity = "白"
        self.affixes = []
        load_image("gun_" + name, "gun_" + name + ".png", None)
        
    @property
    # 武器的完整名稱會根據稀有度和附加屬性動態，例如金手槍 (速射、穿透)
    def full_name(self):
        return "【" + self.rarity + "】" + self.base_name
    
# (名稱, 射擊冷卻(越小越快), 子彈類型, 單發傷害, 音效, 後座力散佈)                                                                        
weaponTypes = {
    "手槍": Weapon("手槍", 20, "normal", 20, "snd_pistol", 1.5),
    "狙擊槍": Weapon("狙擊槍", 50, "piercing", 45, "snd_sniper", 8.0),
    "散彈槍": Weapon("散彈槍", 30, "shotgun", 20, "snd_shotgun", 5.0),
    "衝鋒槍": Weapon("衝鋒槍", 5, "piercing", 6, "snd_mg", 2.0),
    "火焰噴射器": Weapon("火焰噴射器", 3, "flamethrower", 4, "snd_flamethrower", 0.2),
    "雷射槍": Weapon("雷射槍", 25, "laser", 25, "snd_laser", 0.5),
    "電磁炮": Weapon("電磁炮", 60, "cannon", 50, "snd_cannon", 10.0),
    "冰霜發射器": Weapon("冰霜發射器", 10, "frost", 10, "snd_frost", 0.2),
    "重型機槍": Weapon("重型機槍", 17, "piercing", 25, "snd_heavy_mg", 1.5),
    "步槍": Weapon("步槍", 40, "piercing", 30, "snd_rifle", 3.0),
    "火焰榴彈發射器": Weapon("火焰榴彈發射器", 65, "flame_grenade", 70, "snd_grenade", 6.0),
    "電漿發射器": Weapon("電漿發射器", 30, "plasma", 30, "snd_plasma", 2.0)
}

def getRarityColor(r):
    if r == "金": return (255, 215, 0)
    elif r == "紫": return (200, 50, 255)
    elif r == "藍": return (50, 150, 255)
    else: return (200, 200, 200)

def applyWeaponStats(w):
    base = weaponTypes[w.base_name]
    if w.rarity == "白": w.damage = int(base.damage * 1.0)
    elif w.rarity == "藍": w.damage = int(base.damage * 1.3)
    elif w.rarity == "紫": w.damage = int(base.damage * 1.6)
    elif w.rarity == "金": w.damage = int(base.damage * 2.2)
    else: w.damage = base.damage
        
    if "速射" in w.affixes:
        w.shoot_delay = int(base.shoot_delay * 0.60)
        if w.shoot_delay < 2: w.shoot_delay = 2
    else: w.shoot_delay = base.shoot_delay
        
    if "散射" in w.affixes: w.bullet_count = 3    
    else: w.bullet_count = 1
#負責產出不同稀有度跟詞綴的武器生成，會根據武器類型、稀有度和隨機附加屬性生成武器的函式，稀有度越高，附加屬性越多，但附加屬性會根據武器類型過濾掉不適用的選項，因為怕某些屬性重複就沒有意義了
def generateWeapon(base_name, rarity="白"):
    base = weaponTypes[base_name]
    w = Weapon(base.base_name, base.shoot_delay, base.bullet_type, base.damage, base.sound_name, base.base_recoil)
    w.rarity = rarity

    # 決定要給幾個詞綴 (白板=0, 藍=1, 紫=2, 金=3)
    if rarity == "白": c = 0
    elif rarity == "藍": c = 1
    elif rarity == "紫": c = 2
    elif rarity == "金": c = 3
    else: c = 0
    # 詞綴區
    pool = ["速射", "散射", "吸血", "爆擊"]

    # 濾掉不適合的屬性 (火焰槍不要給穿透，不然特效會卡死)
    if base.bullet_type != "piercing" and base.bullet_type != "laser" and base.bullet_type != "cannon" and base.bullet_type != "flamethrower":
        pool.append("穿透")
    if base.bullet_type != "flamethrower" and base.bullet_type != "flame_grenade":
        pool.append("燃燒")
        
    if c > 0:
        amount = c
        if amount > len(pool): amount = len(pool)
        w.affixes = random.sample(pool, amount) # 隨機抽詞綴
    else: w.affixes = []
        
    applyWeaponStats(w)
    return w

# 將武器庫中的武器按照類型、稀有度和附加屬性排序已方便玩家瀏覽和管理，稀有度高的武器會排在前面，同類型的武器會根據附加屬性數量和字母順序進行次級排序
def sortWeaponStash():
    order = list(weaponTypes.keys())
    rarity_rank = {"白":0, "藍":1, "紫":2, "金":3}
    
    def weapon_sort_key(w):
        if w.base_name in order: name_index = order.index(w.base_name)
        else: name_index = 99
            
        if w.rarity in rarity_rank: rarity_value = rarity_rank[w.rarity]
        else: rarity_value = 0
            
        affix_text = ""
        sorted_affixes = sorted(w.affixes)
        for a in sorted_affixes: affix_text += a
            
        return (name_index, -rarity_value, -len(w.affixes), affix_text)
        
    persistentStats["weapon_stash"].sort(key=weapon_sort_key)

# 根據物品類型和屬性計算出售價格的函式，武器價格根據稀有度和附加屬性增加，消耗品價格則是根據數量計算
def getSellValue(item):
    if item == None: return 0
    if item.type == "WEAPON":
        if item.weapon_obj.rarity == "白": return 20
        elif item.weapon_obj.rarity == "藍": return 50
        elif item.weapon_obj.rarity == "紫": return 120
        elif item.weapon_obj.rarity == "金": return 300
        else: return 10
    elif item.type == "MED": return 5 * item.count
    elif item.type == "KEY": return 30 * item.count
    else: return 0

# 玩家背包物品類別與操作函式
class InvItem:
    def __init__(self, i_type, name, count, max_stack, weapon_obj=None):
        self.type = i_type
        self.name = name
        self.count = count
        self.max_stack = max_stack
        self.weapon_obj = weapon_obj

# 根據類型創建物品的函式，武器類型需要傳入武器物件以獲取名稱和屬性
def createItem(i_type, amount=1, weapon_obj=None):
    if i_type == "SCRAP": return InvItem("SCRAP", "廢料", amount, 999)
    elif i_type == "MED": return InvItem("MED", "急救包", amount, 5)
    elif i_type == "KEY": return InvItem("KEY", "金鑰匙", amount, 10)
    elif i_type == "WEAPON": return InvItem("WEAPON", weapon_obj.full_name, 1, 1, weapon_obj)

# 快速轉移物品的函式會優先嘗試堆疊同類型的物品，最後才放入空格子，(武器類型不會堆疊)(為了方便區分)
def fastTransfer(item, to_list):
    for t_item in to_list:
        if t_item != None and t_item.type == item.type and t_item.type != "WEAPON":
            space = t_item.max_stack - t_item.count
            if space > 0:
                if space < item.count: add = space
                else: add = item.count
                t_item.count += add
                item.count -= add
                if item.count <= 0: return True
                    
    if item.count > 0:
        for i in range(len(to_list)):
            if to_list[i] == None:
                to_list[i] = item
                return True
    return False

# 將物品放入指定格子的函式，會返回原本格子裡的物品，優先嘗試堆疊同類型的物品，武器類型不會堆疊
def putItemInSlot(source, idx, item):
    if source == "PLAYER": target_list = player.inventory
    else: target_list = persistentStats["general_stash"]
        
    old_item = target_list[idx]
    if old_item != None and old_item.type == item.type and item.type != "WEAPON":
        space = old_item.max_stack - old_item.count
        if space > 0:
            if space < item.count: add = space
            else: add = item.count
            old_item.count += add
            item.count -= add
            if item.count <= 0: return None
                
    target_list[idx] = item
    return old_item


# 實際的粒子效果、傷害數字和衝刺軌跡類別
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
        self.x += self.vel_x
        self.y += self.vel_y
        self.timer -= 1
        if self.size > 0: self.size -= 0.25
        else: self.size = 0
            
    def draw(self, surface):
        if self.size > 0:
            pygame.draw.rect(surface, self.color, (int(self.x - camX), int(self.y - camY), int(self.size), int(self.size)))

# 傷害數字類別，會隨時間上升並淡出，暴擊會使用不同的字體和顏色
class DamageText:
    def __init__(self, x, y, damage, color, is_crit=False):
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.is_crit = is_crit
        # 暴擊傷害數字會停留更久、上升更快，並使用更大的字體和亮眼的顏色
        if is_crit:
            self.timer = 50
            self.vel_y = -3.5
            self.alpha = 255
            self.offset_x = random.randint(-15,15)
            self.font = large_font
            
            self.surf = self.font.render("-" + str(int(self.damage)) + "!", True, self.color)
        # 普通傷害數字則較快淡出和上升，使用標準字體和顏色
        else:
            self.timer = 35
            self.vel_y = -2.0
            self.alpha = 255
            self.offset_x = random.randint(-15,15)
            self.font = small_font
            
            self.surf = self.font.render("-" + str(int(self.damage)), True, self.color)
     # 會更新位置和透明度當計時器結束後會完全透明並停止更新   
    def update(self):
        self.y += self.vel_y
        self.vel_y += 0.2
        self.timer -= 1
        a = int((self.timer / 35) * 255)
        if a < 0: self.alpha = 0
        else: self.alpha = a
        
    def draw(self, surface):
        if self.timer > 0:
            self.surf.set_alpha(self.alpha)
            surface.blit(self.surf, (int(self.x + self.offset_x - camX - self.surf.get_width()//2), int(self.y - camY)))

# 衝刺軌跡類別，會在玩家衝刺時生成還會隨時間淡出並消失
class DashTrail:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.life = 15
        
    def update(self):
        self.life -= 1
        
    def draw(self, surface):
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        a = int((self.life / 15) * 150)
        if a < 0: a = 0
        pygame.draw.rect(surf, (0, 200, 255, a), (0, 0, self.size, self.size), border_radius=5)
        surface.blit(surf, (int(self.x - camX - self.size/2), int(self.y - camY - self.size/2)))

# 掉落物品類別 包含經驗、醫療包、磁鐵、炸彈、武器等，會被玩家吸收移動到玩家位置，會自動放入背包或是自動使用
class DropItem:
    def __init__(self, x, y, item_type="EXP", count=1, weapon_obj=None):
        self.x = x
        self.y = y
        self.item_type = item_type
        self.count = count
        self.weapon_obj = weapon_obj
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.anim_offset = random.random() * 10
        
    def update(self, p_x, p_y, mag_rad):
        # 現在的版本有移除限制讓所有物品(包含武器、廢料)靠近時都會被玩家或磁鐵吸過去
        dist_sq = (self.x - p_x)**2 + (self.y - p_y)**2
        if dist_sq > 0 and dist_sq < mag_rad**2:
            dist = math.sqrt(dist_sq)
            if mag_rad > 1000: speed = 25
            else: speed = 8
            self.x += ((p_x - self.x) / dist) * speed
            self.y += ((p_y - self.y) / dist) * speed 
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface):
        draw_x = int(self.x - camX)
        draw_y = int(self.y - camY)
        float_y = draw_y + math.sin(pygame.time.get_ticks()*0.005 + self.anim_offset) * 3
        
        if self.item_type == "WEAPON":
            c = getRarityColor(self.weapon_obj.rarity)
            pygame.draw.circle(surface, c, (draw_x, int(float_y)), 15, 2)
            txt = tiny_font.render(self.weapon_obj.full_name, True, c)
            surface.blit(txt, (draw_x - txt.get_width()//2, int(float_y) - 25))
            return
            
        imgName = "drop_" + self.item_type
        # 先嘗試畫出圖片，沒有圖片才畫
        if imgName in images and images[imgName] != None:
            img = images[imgName]
            surface.blit(img, img.get_rect(center=(draw_x, int(float_y))))
        else:
            if self.item_type == "EXP": pygame.draw.polygon(surface, expColor, [(draw_x, float_y-6), (draw_x+6, float_y), (draw_x, float_y+6), (draw_x-6, float_y)])
            elif self.item_type == "MED":
                pygame.draw.rect(surface, hpColor, (draw_x-6, float_y-4, 12, 8))
                pygame.draw.rect(surface, WHITE, (draw_x-2, float_y-6, 4, 12))
            elif self.item_type == "SHIELD": pygame.draw.circle(surface, shieldColor, (draw_x, int(float_y)), 6)
            elif self.item_type == "MAGNET":
                pygame.draw.circle(surface, YELLOW, (draw_x, int(float_y)), 7)
                pygame.draw.circle(surface, RED, (draw_x, int(float_y)), 7, 2)
            elif self.item_type == "BOMB": pygame.draw.circle(surface, (50, 50, 50), (draw_x, int(float_y)), 8)
            elif self.item_type == "SCRAP": pygame.draw.polygon(surface, SCRAP_COLOR, [(draw_x, float_y-4), (draw_x+4, float_y), (draw_x, float_y+4), (draw_x-4, float_y)])
            elif self.item_type == "KEY":
                pygame.draw.rect(surface, YELLOW, (draw_x-8, float_y-2, 16, 4))
                pygame.draw.circle(surface, YELLOW, (draw_x-6, int(float_y)), 4, 2)
            
        if self.count > 1 and (self.item_type == "SCRAP" or self.item_type == "MED" or self.item_type == "KEY"):
            surface.blit(tiny_font.render(str(self.count), True, WHITE), (draw_x + 5, int(float_y) + 5))
          
# 地圖物件類別，包含寶箱、玩家遺失物、撤離點和測試用的假人靶子，每個類別都有自己的繪製方式和互動邏輯
class Chest:
    def __init__(self, x, y, c_type="NORMAL"):
        self.x = x
        self.y = y
        self.type = c_type
        self.state = "CLOSED"
        self.open_progress = 0
        self.rect = pygame.Rect(0, 0, 50, 40)
        self.rect.center = (int(self.x), int(self.y))
        if c_type == "NORMAL": self.color = (139, 69, 19)
        else: self.color = (218, 165, 32)
                                          
    def draw(self, surface):
        dx = int(self.x - camX)
        dy = int(self.y - camY)
        img_key = "chest_" + self.type + "_" + self.state
        
        # 優先顯示寶箱圖片
        if img_key in images and images[img_key] != None:
            img = images[img_key]
            surface.blit(img, img.get_rect(center=(dx, dy)))
            if self.state == "CLOSED" and self.open_progress > 0:
                pygame.draw.rect(surface, GRAY, (dx-25, dy-30, 50, 6))
                pygame.draw.rect(surface, GREEN, (dx-25, dy-30, 50*(self.open_progress/40), 6))
        else:
            draw_rect = self.rect.copy()
            draw_rect.center = (dx, dy)
            if self.state == "CLOSED":
                pygame.draw.rect(surface, self.color, draw_rect, border_radius=5)
                if self.type == "NORMAL": bc = WHITE
                else: bc = YELLOW
                pygame.draw.rect(surface, bc, draw_rect, 2, border_radius=5)
                
                if self.type == "LOCKED":
                    pygame.draw.circle(surface, BLACK, (dx, dy), 6) 
                if self.open_progress > 0:
                    pygame.draw.rect(surface, GRAY, (dx-25, dy-30, 50, 6))
                    pygame.draw.rect(surface, GREEN, (dx-25, dy-30, 50*(self.open_progress/40), 6))
            else: 
                pygame.draw.rect(surface, (80,40,10), pygame.Rect(dx-25, dy+2, 50, 15), border_radius=3)

# 玩家遺失物類別(當玩家死亡時會在原地生成一個遺失物，包含玩家的等級、經驗、升級次數、背包物品和武器，讓玩家觸碰時可以撿回等級槍枝等配備:)
class PlayerLostItem:
    def __init__(self, x, y, level, exp, upgrades, inv_items, w1, w2):
        self.x = x
        self.y = y
        self.level = level
        self.exp = exp
        self.upgrades = upgrades
        self.inventory = inv_items
        self.w1 = w1
        self.w2 = w2
        self.rect = pygame.Rect(0, 0, 50, 50)
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface):
        self.rect.center = (int(self.x), int(self.y))
        draw_x = int(self.x - camX)
        draw_y = int(self.y - camY)
        p = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 5)
        pygame.draw.circle(surface, YELLOW, (draw_x, draw_y), 20 + p)
        pygame.draw.circle(surface, WHITE, (draw_x, draw_y), 22 + p, 2)
        txt = small_font.render("遺失物(觸碰拾取)", True, YELLOW)
        surface.blit(txt, (draw_x - txt.get_width()//2, draw_y - 35))

# 撤離點類別(當玩家完成最後一個任務後會在地圖上生成一個撤離點，在這側離區等待幾秒鐘後就可以返回地堡，還有撤離點會有一個動態的光環效果我覺得這樣比較不單調)
class ExtractionPoint:
    def __init__(self):
        self.x = random.randint(800, mapWidth - 800)
        self.y = random.randint(800, mapHeight - 800)
        self.radius = 150
        
    def draw(self, surface):
        draw_x = int(self.x - camX)
        draw_y = int(self.y - camY)
        p = int(abs(math.sin(pygame.time.get_ticks() * 0.003)) * 20)
        pygame.draw.circle(surface, GREEN, (draw_x, draw_y), self.radius + p, 3)
        surface.blit(font.render("撤離點", True, GREEN), (draw_x - 35, draw_y - 20))

# 假人靶子類別，(讓玩家的可以測試武器傷害)
class DummyTarget:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(0, 0, 40, 60)
        self.rect.center = (int(self.x), int(self.y))
        self.hit_log = []
        self.shake_timer = 0
        
    def update(self):
        now = pygame.time.get_ticks()
        newLog = []
        for log in self.hit_log:
            if now - log[0] <= 3000:
                newLog.append(log)
        self.hit_log = newLog
        
        if self.shake_timer > 0: self.shake_timer -= 1
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface):
        dx = int(self.x - camX)
        dy = int(self.y - camY)
        if "dummy" in animations and animations["dummy"] != None:
            anim_frames = animations["dummy"]
            img = anim_frames[int(pygame.time.get_ticks() / 150) % len(anim_frames)]
            surface.blit(img, img.get_rect(center=(dx, dy)))


# 玩家類別(玩家屬性、武器、背包、經驗和等級、移動、攻擊、使用物品和升級等功能，還有處理衝刺、技能冷卻、回血和其他狀態效果等....
class Player:
    def __init__(self):
        self.x = mapWidth / 2
        self.y = mapHeight / 2
        self.size = 30
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        
        self.primary_weapon = generateWeapon("手槍", "白")
        self.secondary_weapon = generateWeapon("散彈槍", "白")
        self.weapons = [self.primary_weapon, self.secondary_weapon]
        self.current_weapon_idx = 0
        self.cheat_all_weapons = False 
        
        self.base_speed = 7.0 + persistentStats["speed_bonus"]
        self.max_hp = 100 + persistentStats["max_hp"]
        self.max_shield = 100 + persistentStats["max_shield"]
        self.max_stamina = 100 + persistentStats["max_stamina"]
        self.max_energy = 100 + persistentStats["max_energy"]
        
        self.hp = self.max_hp
        self.shield = self.max_shield       
        self.stamina = self.max_stamina
        self.stamina_regen = 0.5   
        self.energy = self.max_energy
        self.energy_regen = 0.2 
        
        self.exp = 0
        self.level = 1
        self.max_exp = 80
        self.inventory = [None] * 24
        
        self.current_spread = 15.0
        self.bullet_count = 1
        self.bullet_spread = 15.0
        self.extra_same_path_bullets = 0
        
        self.bullet_damage_bonus = persistentStats["dmg_bonus"]
        self.shoot_delay_reduction = 0
        self.damage_reduction = 0
        
        self.invincible_duration = 60
        self.guidance_level = 0
        self.aura_level = 0
        self.regen_level = 0
        self.regen_progress = 0
        
        self.exp_multiplier = 1.0
        self.magnet_radius = 80
        
        self.dash_cost = 30
        self.is_dashing = False
        self.dash_speed = 28
        self.dash_duration = 8
        self.dash_timer = 0
        self.dash_dir_x = 0
        self.dash_dir_y = 0
        
        self.skill_cd = 0
        self.skill_max_cd = 600
        self.skill_cost = 50        
        self.invincible_timer = 0
        self.god_mode = False 
        
        self.base_max_ammo = 40
        self.mag_size_bonus = 0
        self.reload_duration = 90
        self.reload_timer = 0
        self.ammo = self.base_max_ammo

    @property
    # 計算玩家目前的廢料數量，遍歷背包中的物品並累加所有廢料的數量，返回總和
    def scrap(self):
        s = 0
        for i in self.inventory:
            if i != None and i.type == "SCRAP": s += i.count
        return s
     # 將新物品加入玩家背包的函式，會使用快速轉移函式將物品放入背包中，若背包已滿則返回False   
    def add_item(self, new_item):
        return fastTransfer(new_item, self.inventory)
     # 使用醫療包的函式，會循找背包中的物品，找到第一個醫療包並使用它來回復玩家的生命值，若生命值已滿則不使用醫療包。使用後會減少醫療包的數量，若數量為零則從背包中移除該物品   
    def use_med(self):
        for i in range(24):
            item = self.inventory[i]
            if item != None and item.type == "MED" and self.hp < self.max_hp:
                self.hp += 40
                if self.hp > self.max_hp: self.hp = self.max_hp
                item.count -= 1
                if item.count <= 0: self.inventory[i] = None
                playSound("exp")
                return True
        return False
        
    # 更新玩家狀態處理移動、衝刺、技能冷卻、回血和其他效果，以及玩家不會超出地圖邊界或穿牆    
    def update(self, clamp_rect=None):
        keys = pygame.key.get_pressed()
        move_x = 0
        move_y = 0
        if keys[pygame.K_w]: move_y -= 1
        if keys[pygame.K_s]: move_y += 1
        if keys[pygame.K_a]: move_x -= 1
        if keys[pygame.K_d]: move_x += 1
            
        dist = math.sqrt(move_x**2 + move_y**2)
        if dist > 0:
            move_x /= dist
            move_y /= dist

        if self.invincible_timer > 0: self.invincible_timer -= 1
        if self.skill_cd > 0: self.skill_cd -= 1
        if self.reload_timer > 0:
            self.reload_timer -= 1
            if self.reload_timer <= 0:
                self.ammo = self.base_max_ammo + self.mag_size_bonus

        if self.regen_level > 0 and self.hp < self.max_hp:
            self.regen_progress += 0.01 * self.regen_level
            if self.regen_progress >= 1:
                heal = int(self.regen_progress)
                self.hp += heal
                if self.hp > self.max_hp: self.hp = self.max_hp
                self.regen_progress -= heal
            
        if self.is_dashing == False:
            if self.stamina < self.max_stamina:
                self.stamina += self.stamina_regen
                if self.stamina > self.max_stamina: self.stamina = self.max_stamina
                
        if self.energy < self.max_energy:
            self.energy += self.energy_regen
            if self.energy > self.max_energy: self.energy = self.max_energy

        if keys[pygame.K_SPACE] or keys[pygame.K_q]:
            if self.is_dashing == False and self.stamina >= self.dash_cost:
                self.stamina -= self.dash_cost
                self.is_dashing = True
                self.dash_timer = self.dash_duration
                playSound("dash")
                if dist > 0:
                    self.dash_dir_x = move_x
                    self.dash_dir_y = move_y
                else:
                    mx, my = pygame.mouse.get_pos()
                    wx = mx + camX
                    wy = my + camY
                    dx = wx - self.x
                    dy = wy - self.y
                    ddist = math.sqrt(dx**2 + dy**2)
                    if ddist > 0:
                        self.dash_dir_x = dx / ddist
                        self.dash_dir_y = dy / ddist
                    
        if self.is_dashing == True:
            self.x += self.dash_dir_x * self.dash_speed
            self.y += self.dash_dir_y * self.dash_speed
            self.dash_timer -= 1
            if self.dash_timer <= 0: self.is_dashing = False
        else:
            self.x += move_x * self.base_speed
            self.y += move_y * self.base_speed
            
        if clamp_rect != None:
            if self.x < clamp_rect.left + self.size/2: self.x = clamp_rect.left + self.size/2
            if self.x > clamp_rect.right - self.size/2: self.x = clamp_rect.right - self.size/2
            if self.y < clamp_rect.top + self.size/2: self.y = clamp_rect.top + self.size/2
            if self.y > clamp_rect.bottom - self.size/2: self.y = clamp_rect.bottom - self.size/2
        else:
            if self.x < self.size/2: self.x = self.size/2
            if self.x > mapWidth - self.size/2: self.x = mapWidth - self.size/2
            if self.y < self.size/2: self.y = self.size/2
            if self.y > mapHeight - self.size/2: self.y = mapHeight - self.size/2
            
        self.rect.center = (int(self.x), int(self.y))
        if self.current_spread > self.bullet_spread:
            self.current_spread -= 0.5
            if self.current_spread < self.bullet_spread: self.current_spread = self.bullet_spread
                
    # 繪製玩家角色，包含無敵閃爍效果、武器瞄準線、光環和無人機等裝飾元素，根據玩家狀態和裝備變化顏色和圖案   
    def draw(self, surface, current_wep=None):
        draw_player = True
        draw_center = (int(self.rect.centerx - camX), int(self.rect.centery - camY))
        draw_rect = self.rect.copy()
        draw_rect.center = draw_center
        
        if self.invincible_timer > 0 and self.god_mode == False:
            if (self.invincible_timer // 4) % 2 == 0: draw_player = False
                
        if draw_player == True:
            # 顯示玩家圖片
            if "player" in animations and animations["player"] != None:
                anim_frames = animations["player"]
                img = anim_frames[int(pygame.time.get_ticks() / 100) % len(anim_frames)]
                mx, my = pygame.mouse.get_pos()
                if mx + camX < self.x: img = pygame.transform.flip(img, True, False)
                surface.blit(img, img.get_rect(center=draw_center))
            else:
                if self.god_mode: pc = YELLOW
                else: pc = BLUE
                pygame.draw.rect(surface, pc, draw_rect)
                
            if self.stamina < self.dash_cost: pygame.draw.rect(surface, GRAY, draw_rect, 3)

            if current_wep != None:
                mx, my = pygame.mouse.get_pos()
                dx = (mx + camX) - self.x
                dy = (my + camY) - self.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist > 0:
                    dir_x = dx / dist
                    dir_y = dy / dist
                else:
                    dir_x = 1
                    dir_y = 0
                
                # 顯示手持武器圖片
                angle = math.degrees(math.atan2(-dy, dx))
                gunName = "gun_" + current_wep.base_name
                if gunName in images and images[gunName] != None:
                    gun_img = images[gunName]
                    if dx < 0: gun_img = pygame.transform.flip(gun_img, False, True)
                    rotated_gun = pygame.transform.rotate(gun_img, angle)
                    offset_x = dir_x * 15
                    offset_y = dir_y * 15
                    surface.blit(rotated_gun, rotated_gun.get_rect(center=(int(self.x + offset_x - camX), int(self.y + offset_y - camY))))
                else:
                    end_x = self.x + dir_x * 25 - camX
                    end_y = self.y + dir_y * 25 - camY
                    wep_color = YELLOW
                    if current_wep.bullet_type == "piercing": wep_color = PURPLE
                    elif current_wep.bullet_type == "flamethrower": wep_color = ORANGE
                    elif current_wep.bullet_type == "laser": wep_color = CYAN
                    elif current_wep.bullet_type == "cannon": wep_color = WHITE
                    elif current_wep.bullet_type == "frost": wep_color = (100, 200, 255)
                    elif current_wep.bullet_type == "flame_grenade": wep_color = RED
                    pygame.draw.line(surface, GRAY, (self.x - camX, self.y - camY), (end_x, end_y), 6)
                    pygame.draw.circle(surface, wep_color, (int(end_x), int(end_y)), 4)

        if self.aura_level > 0:
            pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 10)
            pygame.draw.circle(surface, (0, 180, 255), draw_rect.center, 95 + self.aura_level * 25 + pulse, 2)

# 子彈類別 包含玩家和敵人的子彈，會根據武器的屬性計算傷害、速度、顏色和其他效果，並在更新時處理導引、碰撞和爆炸等邏輯
class Bullet:
    def __init__(self, x, y, target_x, target_y, weapon, guidance_level=0, dmg_bonus=0):
        self.x = x
        self.y = y
        
        crit_chance = 0.10
        crit_mult = 2.0
        if "爆擊" in weapon.affixes:
            crit_chance = 0.35
            crit_mult = 3.0
            
        self.is_crit = False
        if random.random() < crit_chance: self.is_crit = True
            
        base_dmg = weapon.damage + dmg_bonus
        if self.is_crit: self.damage = int(base_dmg * crit_mult)
        else: self.damage = base_dmg
            
        self.b_type = weapon.bullet_type
        
        self.is_burning = False
        if "燃燒" in weapon.affixes: self.is_burning = True
            
        self.is_vampiric = False
        if "吸血" in weapon.affixes: self.is_vampiric = True
            
        self.is_piercing = False
        if self.b_type == "piercing" or self.b_type == "laser" or self.b_type == "cannon" or self.b_type == "flamethrower" or "穿透" in weapon.affixes:
            self.is_piercing = True
            
        self.guidance_level = guidance_level
            
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            self.dir_x = dx / dist
            self.dir_y = dy / dist
        else:
            self.dir_x = 1
            self.dir_y = 0
        
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
            
        if self.is_burning: self.color = ORANGE
            
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        self.explode = False
        self.target_x = target_x
        self.target_y = target_y
        
    # 更新子彈的位置和狀態 如果是特定類型的子彈則會有特殊的行為，例如火焰手榴彈會在接近目標時爆炸，導引子彈會追蹤最近的敵人，穿透子彈會繼續前進直到超過壽命或離開畫面
    def update(self, all_enemies=None, boss_obj=None):
        if all_enemies == None: all_enemies = []
            
        self.lifespan -= 1
        
        if self.b_type == "flame_grenade":
            distToTarget = math.sqrt((self.target_x - self.x)**2 + (self.target_y - self.y)**2)
            # 榴彈抵達滑鼠目標點引爆
            if distToTarget < self.speed:
                self.explode = True
                self.lifespan = 0
                return 
            # 飛行途中撞到一般敵人提前引爆
            for e in all_enemies:
                if e.hp > 0 and self.rect.colliderect(e.rect):
                    self.explode = True
                    self.lifespan = 0
                    return
            # 飛行途中撞到 Boss 提前引爆
            if boss_obj != None and boss_obj.state != "DEFEAT" and self.rect.colliderect(boss_obj.rect):
                self.explode = True
                self.lifespan = 0
                return

        if self.guidance_level > 0 and len(all_enemies) > 0:
            closest_enemy = None
            min_dist = 999999
            for e in all_enemies:
                distToEnemy = math.sqrt((self.x - e.x)**2 + (self.y - e.y)**2)
                if distToEnemy < min_dist:
                    min_dist = distToEnemy
                    closest_enemy = e
                    
            if closest_enemy != None:
                tx = closest_enemy.x - self.x
                ty = closest_enemy.y - self.y
                tdist = math.sqrt(tx**2 + ty**2)
                if tdist > 0:
                    tx /= tdist
                    ty /= tdist
                    turn_speed = 0.02 + self.guidance_level * 0.015
                    if turn_speed > 0.1: turn_speed = 0.1
                    self.dir_x = self.dir_x * (1 - turn_speed) + tx * turn_speed
                    self.dir_y = self.dir_y * (1 - turn_speed) + ty * turn_speed
                    ndist = math.sqrt(self.dir_x**2 + self.dir_y**2)
                    if ndist > 0:
                        self.dir_x /= ndist
                        self.dir_y /= ndist
                        
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface):
        draw_center = (int(self.rect.centerx - camX), int(self.rect.centery - camY))
        imgName = "bullet_" + self.b_type
        if imgName in images and images[imgName] != None:
            img = images[imgName]
            angle = math.degrees(math.atan2(-self.dir_y, self.dir_x))
            rotated_img = pygame.transform.rotate(img, angle)
            surface.blit(rotated_img, rotated_img.get_rect(center=draw_center))

# 敵人子彈類別，與玩家子彈類似，但會有一些不同的屬性和行為，例如可能會有導引但不會暴擊，或者有特殊的子彈類型和效果
class EnemyBullet:
    def __init__(self, x, y, dir_x, dir_y, color=ORANGE, core_color=WHITE, style="round", is_homing=False, weapon=None):
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        dist = math.sqrt(dir_x**2 + dir_y**2)
        if dist > 0:
            self.dir_x /= dist
            self.dir_y /= dist
            
        self.is_homing = is_homing
        self.weapon = weapon
        self.radius = 8
        self.speed = 7
        self.damage = 15
        self.b_type = "normal"
        self.color = color
        self.core_color = core_color
        self.style = style
        
        if weapon != None:
            self.b_type = weapon.bullet_type
            self.damage = int(weapon.damage * 0.8)
            if self.b_type == "piercing":
                self.color = PURPLE
                self.speed = 15
                self.radius = 7
            elif self.b_type == "flamethrower":
                self.color = ORANGE
                self.speed = 8
                self.radius = 12
            elif self.b_type == "laser":
                self.color = CYAN
                self.speed = 25
                self.radius = 4
            elif self.b_type == "cannon":
                self.color = WHITE
                self.speed = 8
                self.radius = 15
                
        self.rect = pygame.Rect(0, 0, self.radius*2, self.radius*2)
        if is_homing: self.lifespan = 150
        else: self.lifespan = 9999
        self.explode = False
        
    # 更新子彈的位置和狀態，如果是導引子彈則會嘗試追蹤玩家的位置，並在到達目標或超過壽命時觸發爆炸
    def update(self, target_x=None, target_y=None):
        self.lifespan -= 1
        if self.lifespan <= 0:
            self.explode = True
            return

        if self.is_homing and target_x != None and target_y != None:
            tx = target_x - self.x
            ty = target_y - self.y
            dist = math.sqrt(tx**2 + ty**2)
            if dist > 0:
                turn_speed = 0.045 * (self.lifespan / 150)
                self.dir_x = self.dir_x * (1 - turn_speed) + (tx / dist) * turn_speed
                self.dir_y = self.dir_y * (1 - turn_speed) + (ty / dist) * turn_speed
                ndist = math.sqrt(self.dir_x**2 + self.dir_y**2)
                if ndist > 0:
                    self.dir_x /= ndist
                    self.dir_y /= ndist
                
        self.x += self.dir_x * self.speed
        self.y += self.dir_y * self.speed
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface): 
        draw_center = (int(self.rect.centerx - camX), int(self.rect.centery - camY))
        if "enemy_bullet" in images and images["enemy_bullet"] != None:
            img = images["enemy_bullet"]
            angle = math.degrees(math.atan2(-self.dir_y, self.dir_x))
            rotated_img = pygame.transform.rotate(img, angle)
            surface.blit(rotated_img, rotated_img.get_rect(center=draw_center))

# 敵人類別包含普通敵人和精英敵人，會根據等級和遊戲模式生成不同的屬性和行為，並在更新時處理移動、攻擊、狀態效果和其他邏輯
class Enemy:
    def __init__(self, level, is_elite=False, spawn_x=mapWidth/2, spawn_y=mapHeight/2):
        self.is_elite = is_elite
        if is_elite: self.size = 35
        else: self.size = 25
        
        difficulty_mult = 1.0
        if gameMode == "CHALLENGE": difficulty_mult = 1.75
        
        if is_elite: bspd = random.uniform(3.0, 5.5)
        else: bspd = random.uniform(2.5, 4.5)
        
        cSpdMult = 1.0
        if gameMode == "CHALLENGE": cSpdMult = 1.2
        self.speed = (bspd + level * 0.05) * cSpdMult
        
        if is_elite: hpBase = 60 + level * 25
        else: hpBase = 20 + level * 8
        self.max_hp = int(hpBase * difficulty_mult)
        self.hp = self.max_hp
        
        if is_elite: shieldBase = 20 + level * 8
        else: shieldBase = 10 + level * 4
        self.max_shield = int(shieldBase * difficulty_mult)
        self.shield = self.max_shield
        
        if is_elite: dmgBase = 35 + level * 3
        else: dmgBase = 15 + level * 1.5
        self.damage = int(dmgBase * difficulty_mult)
        
        self.frost_timer = 0
        self.burn_timer = 0
        self.dir_x = 1
        self.dir_y = 0
        self.hit_timer = 0
        
        if is_elite:
            if random.random() < 0.5: self.combat_type = "melee"
            else: self.combat_type = "ranged"
        else:
            rand_val = random.random()
            if rand_val < 0.45: self.combat_type = "melee"
            elif rand_val < 0.9: self.combat_type = "ranged"
            else: self.combat_type = "kamikaze"

        if self.combat_type == "kamikaze":
            self.color = ORANGE
            self.speed = self.speed * 1.4
            self.max_hp = int(self.max_hp * 0.6)
            self.damage = int(self.damage * 1.5)
            self.hp = self.max_hp
            self.weapon = None
            self.shoot_cd = 0
        elif self.combat_type == "ranged":
            weaponsList = list(weaponTypes.values())
            if len(weaponsList) > 0: self.weapon = random.choice(weaponsList)
            else: self.weapon = None

            if self.weapon != None:
                if hasattr(self.weapon, "shoot_delay"): wDelay = self.weapon.shoot_delay
                else: wDelay = 20
                self.shoot_cd = wDelay * 3 + random.randint(20, 60)
            else:
                self.shoot_cd = 120
        else:
            self.weapon = None
            self.shoot_cd = 0
        
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
            
        if self.x < 0: self.x = 0
        if self.x > mapWidth: self.x = mapWidth
        if self.y < 0: self.y = 0
        if self.y > mapHeight: self.y = mapHeight
        
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.rect.center = (int(self.x), int(self.y))
        
    # 更新函數處理敵人的行為邏輯，包括移動、攻擊、狀態效果和碰撞等，根據不同的戰鬥類型有不同的行為模式，並且會避免與其他敵人重疊     
    def update(self, target_x, target_y, all_enemies, enemy_bullets):
        if self.frost_timer > 0: current_speed = self.speed * 0.4
        else: current_speed = self.speed
        
        if self.hit_timer > 0: self.hit_timer -= 1
        if self.frost_timer > 0: self.frost_timer -= 1 
        if self.burn_timer > 0:
            self.burn_timer -= 1
            if self.burn_timer % 15 == 0:
                self.hp -= 8
                particles.append(Particle(self.x, self.y, ORANGE))

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist > 0:
            self.dir_x = dx / dist
            self.dir_y = dy / dist

        if self.combat_type == "ranged":
            if dist > 350:
                self.x += self.dir_x * current_speed
                self.y += self.dir_y * current_speed
            elif dist < 200:
                self.x -= self.dir_x * current_speed
                self.y -= self.dir_y * current_speed
                
            if self.shoot_cd <= 0 and dist <= 500:
                if self.weapon != None and self.weapon.bullet_type == "shotgun":
                    for i in range(-2, 3):
                        ang = math.atan2(self.dir_y, self.dir_x) + math.radians(i*12)
                        enemy_bullets.append(EnemyBullet(self.x, self.y, math.cos(ang), math.sin(ang), weapon=self.weapon))
                elif self.weapon != None:
                    enemy_bullets.append(EnemyBullet(self.x, self.y, self.dir_x, self.dir_y, weapon=self.weapon))
                    
                if self.weapon != None:
                    if hasattr(self.weapon, "shoot_delay"): wDelay = self.weapon.shoot_delay
                    else: wDelay = 20
                    self.shoot_cd = wDelay * 4 + random.randint(20, 60)
                else:
                    self.shoot_cd = 120
                    
            if self.shoot_cd > 0: self.shoot_cd -= 1
        elif self.combat_type == "kamikaze":
            self.x += self.dir_x * current_speed
            self.y += self.dir_y * current_speed
        else:
            if dist > (self.size + 30) / 2:
                self.x += self.dir_x * current_speed
                self.y += self.dir_y * current_speed

        for other in all_enemies:
            if other != self:
                if 0 < (self.x - other.x)**2 + (self.y - other.y)**2 < self.size**2:
                    dist_val = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
                    self.x += ((self.x - other.x) / dist_val) * 1.3
                    self.y += ((self.y - other.y) / dist_val) * 1.3
            
        if self.x < 0: self.x = 0
        if self.x > mapWidth: self.x = mapWidth
        if self.y < 0: self.y = 0
        if self.y > mapHeight: self.y = mapHeight
        self.rect.center = (int(self.x), int(self.y))
        
    def draw(self, surface):
        draw_center = (int(self.rect.centerx - camX), int(self.rect.centery - camY))
        
        anim_key = "enemy_normal"
        if self.combat_type == "kamikaze": anim_key = "enemy_kamikaze"
        elif self.is_elite: anim_key = "enemy_elite"
        
        if anim_key in animations and animations[anim_key] != None:
            anim_frames = animations[anim_key]
            img = anim_frames[int(pygame.time.get_ticks() / 100) % len(anim_frames)]
            if self.dir_x < 0: img = pygame.transform.flip(img, True, False)
            
            # 受傷閃白/冰凍發藍特效 
            if self.hit_timer > 0:
                img = img.copy()
                img.fill((255, 255, 255, 150), special_flags=pygame.BLEND_RGBA_ADD)
            elif self.frost_timer > 0:
                img = img.copy()
                img.fill((0, 80, 255, 180), special_flags=pygame.BLEND_RGBA_MULT)
                
            surface.blit(img, img.get_rect(center=draw_center))

        # 保留血條與護盾條繪製
        draw_rect = self.rect.copy()
        draw_rect.center = draw_center
        if self.max_shield > 0 and self.shield > 0:
            pygame.draw.rect(surface, GRAY, (draw_rect.x, draw_rect.y - 14, self.size, 4))
            pygame.draw.rect(surface, (0, 150, 255), (draw_rect.x, draw_rect.y - 14, self.size * (self.shield/self.max_shield), 4))
        if self.hp < self.max_hp: 
            pygame.draw.rect(surface, GRAY, (draw_rect.x, draw_rect.y - 8, self.size, 4))
            pygame.draw.rect(surface, GREEN, (draw_rect.x, draw_rect.y - 8, self.size * (self.hp/self.max_hp), 4))

##################################################################
# 第一隻 BOSS 防衛核心 (讀取 boss_yellow)
# Boss移動緩慢但會像無人機砲塔一樣，會使用規律的向灑水器依樣旋轉和十字的彈幕
class CoreBoss:
    def __init__(self, spawn_level=5, player_x=0, player_y=0):
        # 基本屬性設定
        self.x = player_x
        # 從玩家上方 600 像素的位置出現
        self.y = player_y - 600
        self.size = 80
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.name = "防衛核心"
        self.spawn_level = spawn_level
        self.color = YELLOW
        
        # 數值設定
        difficulty = 1.0
        if gameMode == "CHALLENGE": difficulty = 1.75
        self.max_hp = int((1000 + spawn_level * 300) * difficulty)
        self.hp = self.max_hp
        self.speed = 1.5 
        self.collision_damage = 40
        
        # 狀態與計時器
        # 狀態就是一直攻擊
        self.state = "ATTACK" 
        # 用來控制攻擊頻率的計時器
        self.timer = 0
        # 死亡倒數計時器
        self.defeat_timer = 0
        # 控制旋轉射擊的角度
        self.gun_angle = 0
        # 控制圖片左右翻轉
        self.flip_x = False

    def update(self, player_x, player_y, bullets, enemies, enemy_bullets):
        # 如果處於死亡狀態就只計算死亡時間並原地爆炸，不執行攻擊和移動邏輯
        if self.state == "DEFEAT":
            self.defeat_timer += 1
            # 死亡時緩慢往上飄
            self.y -= 0.5
            self.rect.center = (int(self.x), int(self.y))
            # 阻斷後面所有的移動與發射子彈邏輯
            return
            
        self.timer += 1
        
        # 面向玩家，如果玩家在 Boss 左邊就會翻轉圖片
        if player_x < self.x: self.flip_x = True
        else: self.flip_x = False

        # 簡單的追蹤移動 (算出距離然後會往玩家方向走)
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.sqrt(dx**2 + dy**2)
        
        # 如果距離大於200才慢慢靠近
        if dist > 200:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

        # 更新碰撞框位置
        self.rect.center = (int(self.x), int(self.y))
        
        # 呼叫攻擊函式
        self.emit_attacks(enemy_bullets)

    def emit_attacks(self, enemy_bullets):
        # 攻擊模式 A 會像灑水器旋轉射擊 (每 6 個 frame 發射一次)
        if self.timer % 6 == 0:
            # 每次轉 15 度
            self.gun_angle += 15
            rad = math.radians(self.gun_angle)
            dir_x = math.cos(rad)
            dir_y = math.sin(rad)
            # 產生一顆黃色子彈
            enemy_bullets.append(EnemyBullet(self.x, self.y, dir_x, dir_y, color=YELLOW))
            playSound("shoot_normal")

        # 攻擊模式 B 十字重砲爆發 (每 90 個 frame 發射一次)
        if self.timer % 90 == 0:
            # 上下左右四個方向
            for angle in [0, 90, 180, 270]:
                rad = math.radians(angle)
                dir_x = math.cos(rad)
                dir_y = math.sin(rad)
                # 產生一顆紅色大子彈
                enemy_bullets.append(EnemyBullet(self.x, self.y, dir_x, dir_y, color=RED, style="diamond"))
            playSound("shoot_cannon")

    def can_take_damage(self): 
        if self.state == "DEFEAT": return False
        # 永遠可以受傷
        return True

    def get_intro_title(self): return self.name + " 啟動！"
    def get_state_message(self): return "防衛核心 - 規律彈幕射擊中", YELLOW

    def draw(self, surface):
        # 抓取畫面相對座標
        cx = int(self.x - camX)
        cy = int(self.y - camY)

        # 讀取對應的動畫資料夾圖片
        if "boss_yellow" in animations and animations["boss_yellow"] != None:
            # 根據時間輪播圖片
            anim_frames = animations["boss_yellow"]
            frame_index = int(pygame.time.get_ticks() / 150) % len(anim_frames)
            img = anim_frames[frame_index]
            
            # 如果面向左邊就翻轉圖片
            if self.flip_x: img = pygame.transform.flip(img, True, False)

            # 死亡時圖片變成紅色半透明
            if self.state == "DEFEAT":
                img = img.copy()
                img.fill((255, 0, 0, 150), special_flags=pygame.BLEND_RGBA_MULT)
                
            # 畫到螢幕上
            surface.blit(img, img.get_rect(center=(cx, cy)))
        
        # 死亡的爆炸粒子特效
        if self.state == "DEFEAT":
            for _ in range(3):
                rx = cx + random.randint(-40, 40)
                ry = cy + random.randint(-40, 40)
                pygame.draw.circle(surface, ORANGE, (rx, ry), random.randint(5, 15))


##################################################################
# 第二隻 BOSS  衝刺突擊者 (讀取 boss_charger)
# 衝刺行敵人會鎖定玩家 -> 停止 -> 高速衝撞 -> 衝撞時背後發射子彈
class ChargerBoss:
    def __init__(self, spawn_level=5, player_x=0, player_y=0):
        self.x = player_x + 600
        self.y = player_y
        self.size = 80
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.name = "衝刺突擊者"
        self.spawn_level = spawn_level
        self.color = ORANGE
        
        difficulty = 1.0
        if gameMode == "CHALLENGE": difficulty = 1.75
        self.max_hp = int((1200 + spawn_level * 300) * difficulty)
        self.hp = self.max_hp
        self.speed = 3.0
        self.collision_damage = 60
        
        # 追逐(CHASE) -> 準備衝刺(AIM) -> 衝刺中(DASH) -> 休息(REST)
        self.state = "CHASE"  
        self.timer = 0
        self.defeat_timer = 0  
        self.dash_dir_x = 0
        self.dash_dir_y = 0
        self.flip_x = False

    def update(self, player_x, player_y, bullets, enemies, enemy_bullets):
        # 如果處於死亡狀態就只計算死亡時間並原地爆炸，不執行攻擊和移動邏輯
        if self.state == "DEFEAT":
            self.defeat_timer += 1
            # 死亡時緩慢往上飄
            self.y -= 0.5
            self.rect.center = (int(self.x), int(self.y))
            # 阻斷後面所有的移動與發射子彈邏輯
            return
            
        self.timer += 1
        
        # 只有在追逐和瞄準時才會改變面向衝刺時固定朝衝刺方向
        if self.state == "CHASE" or self.state == "AIM":
            if player_x < self.x: self.flip_x = True
            else: self.flip_x = False

        # 狀態一:追逐玩家
        if self.state == "CHASE":
            dx = player_x - self.x
            dy = player_y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
                
            # 追了 70 個 frame 2秒後進入瞄準狀態
            if self.timer > 70:
                self.state = "AIM"
                self.timer = 0

        # 狀態二:鎖定瞄準
        elif self.state == "AIM":
            # 停留在原地不動，準備衝刺
            if self.timer > 60:
                # 瞄準 1 秒鐘
                # 記錄衝刺方向
                dx = player_x - self.x
                dy = player_y - self.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist > 0:
                    self.dash_dir_x = dx / dist
                    self.dash_dir_y = dy / dist
                self.state = "DASH"
                self.timer = 0

        # 狀態三:高速衝刺
        elif self.state == "DASH":
            # 速度 30.0， (原本設太高結果閃不過先下修)
            self.x += self.dash_dir_x * 30.0
            self.y += self.dash_dir_y * 30.0
            
            # 衝刺時背後狂發射子彈
            if self.timer % 5 == 0:
                # 子彈往後飛 (加上負號)
                enemy_bullets.append(EnemyBullet(self.x, self.y, -self.dash_dir_x, -self.dash_dir_y, color=GRAY))
                playSound("shoot_shotgun")
                
            # 衝刺時間 40 個 frame 後停下來休息
            if self.timer > 40:
                self.state = "REST"
                self.timer = 0

        # 狀態四:過載休息
        elif self.state == "REST":
            # 原地發呆給玩家一個攻擊輸出的空檔
            if self.timer > 60:
                self.state = "CHASE"
                self.timer = 0

        # 更新碰撞框
        self.rect.center = (int(self.x), int(self.y))

    def emit_attacks(self, enemy_bullets):
        # 衝刺怪的攻擊寫在 update 
        pass

    def can_take_damage(self): 
        if self.state == "DEFEAT": return False
        # 衝刺時有無敵裝甲不能受傷
        if self.state == "DASH": return False
        return True

    def get_intro_title(self): return self.name + " 鎖定目標！"
    def get_state_message(self):
        if self.state == "AIM": return "警告:鎖定衝刺！", RED
        elif self.state == "REST": return "引擎過熱 - 攻擊好時機！", GREEN
        return "衝刺突擊者 - 追擊中", ORANGE

    def draw(self, surface):
        cx = int(self.x - camX)
        cy = int(self.y - camY)

        # 瞄準狀態時會畫一條紅色的警告雷射線
        if self.state == "AIM":
            end_x = cx + (player.x - self.x) * 10 
            end_y = cy + (player.y - self.y) * 10
            pygame.draw.line(surface, RED, (cx, cy), (end_x, end_y), 2) 

        # 讀取圖片
        if "boss_charger" in animations and animations["boss_charger"] != None:
            anim_frames = animations["boss_charger"]
            img = anim_frames[int(pygame.time.get_ticks() / 150) % len(anim_frames)]
            if self.flip_x: img = pygame.transform.flip(img, True, False)
            
            # 死亡時圖片變成紅色半透明
            if self.state == "DEFEAT":
                img = img.copy()
                img.fill((255, 0, 0, 150), special_flags=pygame.BLEND_RGBA_MULT)

            surface.blit(img, img.get_rect(center=(cx, cy)))

        # 死亡的爆炸粒子特效
        if self.state == "DEFEAT":
            for _ in range(3):
                rx = cx + random.randint(-40, 40)
                ry = cy + random.randint(-40, 40)
                pygame.draw.circle(surface, ORANGE, (rx, ry), random.randint(5, 15))


##################################################################
# 第三隻 BOSS 狂亂終結者 (讀取 boss_red)
# 故障的機器人會發射追蹤飛彈並爆炸，還有結合前兩個BOSS的攻擊模式
class BerserkerBoss:
    def __init__(self, spawn_level=5, player_x=0, player_y=0):
        self.x = player_x
        self.y = player_y - 400
        self.size = 80
        self.rect = pygame.Rect(0, 0, self.size, self.size)
        self.name = "狂亂終結者"
        self.spawn_level = spawn_level
        self.color = RED
        
        difficulty = 1.0
        if gameMode == "CHALLENGE": difficulty = 1.75
        self.max_hp = int((1500 + spawn_level * 300) * difficulty)
        self.hp = self.max_hp
        self.speed = 2.5
        self.collision_damage = 50
        
        self.state = "WALK"
        self.timer = 0
        self.defeat_timer = 0  
        self.flip_x = False

    def update(self, player_x, player_y, bullets, enemies, enemy_bullets):
        # 如果處於死亡狀態就只計算死亡時間並原地爆炸，不執行攻擊和移動邏輯
        if self.state == "DEFEAT":
            self.defeat_timer += 1
            # 死亡時緩慢往上飄
            self.y -= 0.5
            self.rect.center = (int(self.x), int(self.y))
            # 阻斷後面所有的移動與發射子彈邏輯
            return
            
        self.timer += 1
        
        if player_x < self.x: self.flip_x = True
        else: self.flip_x = False

        # 狀態1: 發射追蹤飛彈與Boss1旋轉彈幕
        if self.state == "WALK":
            dx, dy = player_x - self.x, player_y - self.y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                self.x += (dx / dist) * (self.speed * 0.5)
                self.y += (dy / dist) * (self.speed * 0.5)
                
            # 追蹤飛彈
            if self.timer % 60 == 0:
                enemy_bullets.append(EnemyBullet(self.x, self.y, 1, -0.5, color=PURPLE, is_homing=True))
                enemy_bullets.append(EnemyBullet(self.x, self.y, -1, -0.5, color=PURPLE, is_homing=True))
                playSound("shoot_laser")
                
            # Boss1的旋轉彈幕
            if self.timer % 8 == 0:
                rad = math.radians(self.timer * 4)
                enemy_bullets.append(EnemyBullet(self.x, self.y, math.cos(rad), math.sin(rad), color=YELLOW))

            if self.timer > 150:
                self.state = "DASH"
                self.timer = 0

        # 狀態2: Boss2鎖定後高速衝刺，沿途留下爆炸地雷
        elif self.state == "DASH":
            if self.timer == 1:
                dx, dy = player_x - self.x, player_y - self.y
                dist = math.sqrt(dx**2 + dy**2)
                if dist > 0:
                    self.dir_x, self.dir_y = dx / dist, dy / dist
                else:
                    self.dir_x, self.dir_y = 1, 0
                    
            if 20 < self.timer < 40:
                self.x += self.dir_x * 25.0
                self.y += self.dir_y * 25.0
                # 沿途會有地雷 (會爆炸的紅色子彈)
                if self.timer % 4 == 0:
                    eb = EnemyBullet(self.x, self.y, 0, 0, color=RED, style="diamond")
                    eb.explode = True # 落地即爆
                    enemy_bullets.append(eb)
                    
            if self.timer > 60:
                self.state = "REST"
                self.timer = 0

        # 狀態3: 過熱 漸低難度製造玩家攻擊空檔
        elif self.state == "REST":
            # 停在原地給玩家打
            if self.timer > 90:
                self.state = "WALK"
                self.timer = 0

        self.rect.center = (int(self.x), int(self.y))

    def get_state_message(self):
        if self.state == "DASH": return "系統暴走 - 追擊與轟炸！", RED
        elif self.state == "REST": return "系統過熱 - 全力反擊！", GREEN
        return "狂亂終結者 - 混合火力模式", ORANGE

    def draw(self, surface):
        cx = int(self.x - camX)
        cy = int(self.y - camY)

        has_anim = False
        # 讀取圖片
        if "boss_red" in animations and animations["boss_red"] != None:
            anim_frames = animations["boss_red"]
            has_anim = True
        
        # 如果正在瞬移，讓圖片半透明閃爍
        if self.state == "TELEPORT" and self.timer < 30:
            if has_anim:
                img = anim_frames[0].copy()
                # 半透明
                img.set_alpha(100)
                surface.blit(img, img.get_rect(center=(cx, cy)))
            else:
                pygame.draw.circle(surface, PURPLE, (cx, cy), self.size // 2, 2)
            return

        # 正常畫圖
        if has_anim:
            img = anim_frames[int(pygame.time.get_ticks() / 150) % len(anim_frames)]
            if self.flip_x: img = pygame.transform.flip(img, True, False)

            # 死亡時圖片變成紅色半透明
            if self.state == "DEFEAT":
                img = img.copy()
                img.fill((255, 0, 0, 150), special_flags=pygame.BLEND_RGBA_MULT)

            surface.blit(img, img.get_rect(center=(cx, cy)))
        else:
            pygame.draw.rect(surface, RED, (cx - 35, cy - 45, 70, 90))
        
        if self.state == "DEFEAT":
            for _ in range(3):
                rx = cx + random.randint(-40, 40)
                ry = cy + random.randint(-40, 40)
                pygame.draw.circle(surface, ORANGE, (rx, ry), random.randint(5, 15))


######################################
# 遊戲全域狀態與核心初始化
chosenUpgrades = []
defeatedBossLevels = []
lostItem = None
gameMode = "NORMAL"

bullets = [] # 玩家子彈列表
bunker_bullets = [] # 地堡內子彈列表，黑市購買和改造台強化武器時的展示
enemy_bullets = [] # 敵人子彈列表
enemies = []
particles = []
items = []
trails = []
damage_texts = []
chests = []

boss = None
isBossActive = False
shootCooldown = 0
magnetTimer = 0
screenFlashTimer = 0
bossArmyActive = False
extractionTimer = 0
extractionPt = None
extractProgress = 0 # 抵達撤離點後的進度條滿了會就回地堡

showChangelog = True
changelogScroll = 0 # y軸捲動量
changelogMaxScroll = 0 # y軸最大捲動量
changelogScrollX = 0   # X軸捲動量
changelogMaxScrollX = 0  # X軸最大捲動量

pauseUpgradeScroll = 0
arsenalScrollY = 0
selectedArsenalIdx = 0
arsenalWeaponsList = [] # 地堡武器庫中目前可用的武器列表會根據玩家狀態動態生成

showInventory = False
dragData = None
selectedModWeapon = None 
currentUpgradeChoices = [] # 升級選單中目前可選的升級選項列表，會根據玩家狀態動態生成
selectedUpgradePosition = None # 升級選單中選擇的格子位置 (0-5)，用來顯示對應的升級說明文字

bunker_dummy = DummyTarget(mapWidth//2 + 200, mapHeight//2 - 50)
taskSystem = TaskSystem()
raidStartTime = None
enemySpawnTimer = 0

guide_text_lines = [
    "[遊戲概念]",
    "我們製作的這一款以遊戲是以末日肉鴿(Roguelite)2D射擊類",
    "生存挑戰元氣騎士為概念的遊戲。背景是玩家在一個被機器人",
    "入侵的世界末日中，躲在地堡裡強化自己對抗外面",
    "源源不絕的敵人。",
    "透過擊敗敵人以及尋找寶箱獲取獎勵來不斷強化自身。",
    "每次挑戰都會遭遇隨機的敵人與3種BOSS，",
    "抵達撤離點回到地堡，抵達測離點回到地堡或是死亡的循環。",
    "",
    "[遊戲基礎操作]",
    "{開始遊戲前請先切換成英文輸入法，否則無法操作}",
    "移動: WASD",
    "射擊: 滑鼠左鍵",
    "技能: 滑鼠右鍵",
    "衝刺: SPACE / Q",
    "互動: E",
    "開箱: F",
    "切換武器: E",
    "背包: TAB",
    "補血: H",
    "換彈: R",
    "出售物品: X (在背包內游標指著)",
    "暫停: ESC",
    "全螢幕: F11",
    "",
    "[地堡基地 (安全屋)]",
    "開始突襲:進入戰鬥地圖",
    "黑市購買:花費廢料進行永久屬性升級",
    "收藏箱:管理與存放物品",
    "改造台:強化或調整武器屬性",
    "武器庫:可以裝備或切換武器",
    "",
    "[戰鬥與機制]",
    "超時事件: 若存活時間超過限制，將觸發BOSS軍隊事件，",
    "大量精英包圍",
    "衝刺: 消耗體力進行高速閃避，帶有藍色殘影",
    "無敵機制: 受擊後會短暫進入無敵狀態(閃爍)，防止連續扣血",
    "護盾系統: 受傷優先扣藍色護盾，脫離戰鬥後會自動恢復",
    "",
    "[武器與裝備]",
    "稀有度: 白 -> 藍 -> 紫 -> 金，對應 0~3 個隨機詞綴",
    "詞綴包含: 速射、散射、吸血、爆擊、穿透、燃燒",
    "共有12種特色武器，手槍、雷射槍等武器",
    "",
    "[敵人與 BOSS]",
    "敵人分近戰、遠程與自爆三種。難度會隨玩家等級動態調整",
    "三大Boss會在玩家每次等級提升5級時出現: ",
    "1. 核心機器人: 基礎彈幕射擊型",
    "2. 衝刺突擊者: 高機動性衝刺模式",
    "3. 狂亂終結者: 會瞬移與多階段爆發的危險目標",
    "",
    "[死亡與保存機制]",
    "類似魂類遊戲的撿屍目前沒有讀檔機制，但地堡內的黑市",
    "購買、收藏箱物品與武器庫裝備均會自動保存，除非退出遊戲",
    "或是當次突襲進度若死亡一次後再死亡則會遺失",
    "",
    "[難度差異]",
    "{{為了方便測試，卡牌升級以及槍枝數值有提高}}",
    "普通模式:基礎倍率 1.0x，有無限彈藥",
    "挑戰模式:敵人強度 1.75x 且有速度加成，會有子彈減少的",
    "換彈機制增加難度，還有專屬卡牌技能",
    "",
    "[簡要開發日誌]",
    "從開學期初開始製作總共花了超過105小時以上製作，",
    "其實原本畫了很大的餅，連3D視角(B9版)都做了，",
    "但太出現太多問題以及遇到了障礙擱置，所以後來刪減了",
    "很多內容才完成",
    "主要歷經A1->A2->A3->A4->A5->B1->B2->B3->B4->",
    "B5->B6->B7->B8->B8.5->B9(以擱置的3D功能版)->",
    "接續B8.5的B8.6->B8.7->B8.8->C1->C2->B8.9多個版本",
    "迭代，為了方便上傳最後我們把完成的B8.9直接整合成",
    "同一個檔。",
    "製作最久的功能是戰鬥系統與BOSS，從最初的簡單射擊",
    "演變為現在包含多種子彈機制、三大特色BOSS的機制。",
    "還有所有的UI介面也花了非常多時間因為找不到滿意的",
    "圖片設計，只好直接寫在遊戲中在逐一微調，",
    "不過寫完一部分之後就只要複製修改就好了。",
    "因為沒有足夠時間繪製圖片，圖片素材使用的是免費素材，",
    "使用 itch.io 網站上的免費素材，",
    "音效則是使用 pixabay 上的免費音效",
    "參考資料大多是pygame遊戲製作相關文章以及，",
    "YT遊戲製作影片與B站還有以前製作過的遊戲",
    "",
    "(架構基礎)",
    "原本只打算使用 800x600 固定場景，後來改成 4200x2600 ",
    "的小型開放世界，還加入了支援自適應全螢幕切換的功能",
    "",
    "(戰鬥系統)",
    "利用 WASD 八個方向移動與滑鼠射擊(利用三角函數計算軌跡)。",
    "子彈追蹤邏輯，可隨升級強化強度)、武器詞綴屬性、",
    "物理擊退效果與彈性傷害數值顯示",
    "感官回饋:加入卡肉感(Hit Stop)、受擊閃白(Hit Flash)、",
    "以及子彈擊中時的粒子特效",
    "",
    "(進階 Roguelite 與 RPG 玩法)",
    "以Roguelite遊戲的成長系統作為參考製作了 25 種強化卡牌",
    "例如子彈分裂等、升級時的點擊選擇介面。",
    "後來擴展成開放世界加入了地圖與探索，動態相機跟隨、",
    "小地圖(實時顯示玩家、撤離點、Boss 與遺失物)以及",
    "Boss 方向警示",
    "採用類魂類遊戲死亡機制，玩家死亡後物品、經驗值",
    "會成為遺失物掉落在地上，需回到原處觸碰撿回，",
    "若是在尋找遺失物觸碰前死亡，遺失物將會消失。",
    "還有撤離系統，撤離成功可保留物資帶回地堡",
    "至於RPG元素則是對話系統與隨機任務系統，玩家可以執行任務",
    "並獲取獎勵",
    "",
    "(資源與 UI 管理) ",
    "可以透過24 格的背包存放物品以及武器，",
    "背包會自動撿取地上的物品、武器，用滑鼠拖曳整理、",
    "物品變賣、以及黑市商店與武器改造台、武器庫",
    "物資系統:新增護盾(具備脫戰自動恢復)、血包、",
    "各式武器(含槍枝與特效)，並將物品拾取調整為自動吸附模式",
    "",
    "(Boss 與音效):",
    "原本設計了四款BOSS，但最終實裝了三個比較有特色的BOSS ，",
    "BOSS與敵人根據玩家等級動態調整難度",
    " 64 音效通道讓獨立短促音效、Boss 專屬背景音樂",
    "以及槍聲表現可以正常",
    "",
    "(維護與優化)",
    "Bug修復了因介面重繪導致的掉幀問題(主選單光暈重繪)、",
    "碰撞運算優化，整合了遺失物回收的安全鎖機制(防止裝備消失)、",
    "修復碰撞穿模、UI 對齊以及動畫顯示異常，",
    "還有防爆音與動態槍聲機制等問題"
]

# 宣告一個全域變數來存畫好的文字圖(忘了加上避免每幀重畫)
gd_surf = None

# 進入 BUNKER 模式，重置遊戲狀態是否成功完成突襲來處理獎勵和懲罰，在進入 BUNKER 後有一個全新的狀態來面對新的挑戰
def enterBunker(success=False):
    global gameState, bullets, bunker_bullets, enemy_bullets, enemies, particles, items, trails, damage_texts, chests
    global boss, isBossActive, shootCooldown, magnetTimer, screenFlashTimer
    global bossArmyActive, extractionTimer, extractionPt, extractProgress, enemySpawnTimer, taskSystem
    
    if success == True:
        scrap_count = 0
        for i in player.inventory:
            if i != None and i.type == "SCRAP":
                scrap_count += i.count
        persistentStats["scrap"] += scrap_count * 10 
        
        for i in range(24):
            if player.inventory[i] != None and player.inventory[i].type == "SCRAP":
                player.inventory[i] = None
                
    player.hp = player.max_hp
    player.shield = player.max_shield
    player.ammo = player.base_max_ammo + player.mag_size_bonus
    
    bullets.clear()
    bunker_bullets.clear()
    enemy_bullets.clear()
    enemies.clear()
    particles.clear()
    items.clear()
    trails.clear()
    damage_texts.clear()
    chests.clear()
    
    boss = None
    isBossActive = False
    shootCooldown = 0
    magnetTimer = 0
    screenFlashTimer = 0
    bossArmyActive = False
    extractionTimer = 15*60*FPS
    extractionPt = None
    extractProgress = 0
    enemySpawnTimer = 0
    
    player.x = mapWidth//2
    player.y = mapHeight//2
    gameState = "BUNKER"
    stopSound("boss_bgm")
    pygame.mixer.music.unpause() 
    taskSystem = TaskSystem()

# 開始突襲模式會重置遊戲狀態並生成新的挑戰，敵人、寶箱、抽取點等，並開始計時
def startRaid():
    global gameState, extractionTimer, extractionPt, bossArmyActive, extractProgress
    global bullets, enemy_bullets, enemies, particles, items, trails, damage_texts, chests
    global isBossActive, boss, player, enemySpawnTimer, raidStartTime
    
    gameState = "PLAYING"
    player.x = mapWidth//2
    player.y = mapHeight//2
    
    bullets.clear()
    enemy_bullets.clear()
    enemies.clear()
    particles.clear()
    items.clear()
    trails.clear()
    damage_texts.clear()
    chests.clear() 
    
    extractionPt = ExtractionPoint()
    extractionTimer = 420 * FPS # 撤離時間7分鐘
    extractProgress = 0
    isBossActive = False
    boss = None
    enemySpawnTimer = 10
    raidStartTime = pygame.time.get_ticks()
    
    # 隨機產生普通寶箱
    for i in range(15):
        cx = random.randint(400, mapWidth-400)
        cy = random.randint(400, mapHeight-400)
        chests.append(Chest(cx, cy, "NORMAL"))
        
    # 隨機產生上鎖寶箱
    for i in range(5):
        cx = random.randint(400, mapWidth-400)
        cy = random.randint(400, mapHeight-400)
        chests.append(Chest(cx, cy, "LOCKED"))
        
    stopSound("boss_bgm")     
    pygame.mixer.music.unpause()   

# 完全重置遊戲狀態，回到初始菜單，清除所有進度和狀態，並根據選擇的模式設定初始條件
def fullWipe(mode="NORMAL"):
    global player, gameMode, chosenUpgrades, lostItem, defeatedBossLevels
    gameMode = mode
    player = Player()
    lostItem = None
    chosenUpgrades.clear()
    defeatedBossLevels.clear()
    enterBunker(False)

# 處理玩家與寶箱的碰撞，確保玩家在接觸到寶箱時能夠正確地停留在寶箱邊緣而不是穿過它，並返回是否碰撞到寶箱的布林值
def resolveChestCollision(entity, chests_list):
    hit_chest = False
    for c in chests_list:
        if entity.rect.colliderect(c.rect):
            hit_chest = True
            overlap_l = entity.rect.right - c.rect.left
            overlap_r = c.rect.right - entity.rect.left
            overlap_t = entity.rect.bottom - c.rect.top
            overlap_b = c.rect.bottom - entity.rect.top
            
            # 找出最小的重疊量，推出去
            min_overlap = overlap_l
            if overlap_r < min_overlap: min_overlap = overlap_r
            if overlap_t < min_overlap: min_overlap = overlap_t
            if overlap_b < min_overlap: min_overlap = overlap_b
            
            if min_overlap == overlap_l:
                entity.x -= overlap_l
            elif min_overlap == overlap_r:
                entity.x += overlap_r
            elif min_overlap == overlap_t:
                entity.y -= overlap_t
            elif min_overlap == overlap_b:
                entity.y += overlap_b
                
            entity.rect.center = (int(entity.x), int(entity.y))
    return hit_chest


# 遊戲剛開始先重製一次
fullWipe("NORMAL")
gameState = "MENU"
dim_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
dim_surface.fill((0, 0, 0, 180))

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
changelog_close_button = pygame.Rect(WIDTH//2 + 305, HEIGHT//2 - 240, 35, 35)
restart_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 100, 220, 50)
menu_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 170, 220, 50)
confirm_upgrade_button = pygame.Rect(WIDTH//2 - 110, HEIGHT//2 + 190, 220, 50)

cards = []
for i in range(3):
    cards.append(pygame.Rect(WIDTH//2 - 350 + i*240, HEIGHT//2 - 150, 220, 320))

shop_bg = pygame.Rect(int(WIDTH//2 - 300*scaleFactor), int(HEIGHT//2 - 250*scaleFactor), int(600*scaleFactor), int(500*scaleFactor))
stash_bg = pygame.Rect(int(WIDTH//2 - 380*scaleFactor), int(HEIGHT//2 - 250*scaleFactor), int(760*scaleFactor), int(500*scaleFactor)) 
mod_bg = pygame.Rect(int(WIDTH//2 - 380*scaleFactor), int(HEIGHT//2 - 260*scaleFactor), int(760*scaleFactor), int(520*scaleFactor)) 
wep_stash_bg = pygame.Rect(int(WIDTH//2 - 380*scaleFactor), int(HEIGHT//2 - 280*scaleFactor), int(760*scaleFactor), int(560*scaleFactor)) 

btn_shop_close = pygame.Rect(int(WIDTH//2 + 250*scaleFactor), int(HEIGHT//2 - 240*scaleFactor), int(40*scaleFactor), int(40*scaleFactor))
btn_stash_close = pygame.Rect(int(WIDTH//2 + 335*scaleFactor), int(HEIGHT//2 - 240*scaleFactor), int(35*scaleFactor), int(35*scaleFactor))
btn_mod_close = pygame.Rect(int(WIDTH//2 + 335*scaleFactor), int(HEIGHT//2 - 250*scaleFactor), int(35*scaleFactor), int(35*scaleFactor))
btn_wep_close = pygame.Rect(int(WIDTH//2 + 335*scaleFactor), int(HEIGHT//2 - 270*scaleFactor), int(35*scaleFactor), int(35*scaleFactor))

btn_hp = pygame.Rect(int(WIDTH//2 - 260*scaleFactor), int(HEIGHT//2 - 140*scaleFactor), int(240*scaleFactor), int(70*scaleFactor))
btn_dmg = pygame.Rect(int(WIDTH//2 + 20*scaleFactor),  int(HEIGHT//2 - 140*scaleFactor), int(240*scaleFactor), int(70*scaleFactor))
btn_spd  = pygame.Rect(int(WIDTH//2 - 260*scaleFactor), int(HEIGHT//2 - 40*scaleFactor),  int(240*scaleFactor), int(70*scaleFactor))
btn_stamina = pygame.Rect(int(WIDTH//2 + 20*scaleFactor),  int(HEIGHT//2 - 40*scaleFactor),  int(240*scaleFactor), int(70*scaleFactor))
btn_shield = pygame.Rect(int(WIDTH//2 - 260*scaleFactor), int(HEIGHT//2 + 60*scaleFactor),  int(240*scaleFactor), int(70*scaleFactor))
btn_energy = pygame.Rect(int(WIDTH//2 + 20*scaleFactor),  int(HEIGHT//2 + 60*scaleFactor),  int(240*scaleFactor), int(70*scaleFactor))

list_rect = pygame.Rect(int(WIDTH//2 - 280*scaleFactor), int(HEIGHT//2 - 200*scaleFactor), int(560*scaleFactor), int(300*scaleFactor))
btn_prim_w = pygame.Rect(int(WIDTH//2 - 160*scaleFactor), int(HEIGHT//2 + 235*scaleFactor), int(140*scaleFactor), int(40*scaleFactor))
btn_sec_w = pygame.Rect(int(WIDTH//2 + 20*scaleFactor), int(HEIGHT//2 + 235*scaleFactor), int(140*scaleFactor), int(40*scaleFactor))

rect_prim = pygame.Rect(int(WIDTH//2 - 350*scaleFactor), int(HEIGHT//2 - 180*scaleFactor), int(160*scaleFactor), int(80*scaleFactor))
rect_sec = pygame.Rect(int(WIDTH//2 - 170*scaleFactor), int(HEIGHT//2 - 180*scaleFactor), int(160*scaleFactor), int(80*scaleFactor))
upg_btn = pygame.Rect(int(WIDTH//2 + 70*scaleFactor), int(HEIGHT//2 + 40*scaleFactor), int(230*scaleFactor), int(45*scaleFactor))
reroll_btn = pygame.Rect(int(WIDTH//2 + 70*scaleFactor), int(HEIGHT//2 + 110*scaleFactor), int(230*scaleFactor), int(45*scaleFactor))

s_start_x = int(WIDTH//2 - 350*scaleFactor)
s_start_y = int(HEIGHT//2 - 150*scaleFactor)

p_start_x_s = int(WIDTH//2 + 30*scaleFactor)
p_start_y_s = int(HEIGHT//2 - 150*scaleFactor)

p_start_x_m = int(WIDTH//2 - 350*scaleFactor)
p_start_y_m = int(HEIGHT//2 - 40*scaleFactor)

p_start_x_w = int(WIDTH//2 - 344*scaleFactor)
p_start_y_w = int(HEIGHT//2 + 115*scaleFactor)

# 遊戲主迴圈開始
while running == True:
    if lostItem != None:
        try:
            lostItem.rect.center = (int(lostItem.x), int(lostItem.y))
        except:
            pass
    
    # 獲取滑鼠位置並轉換成遊戲內座標
    raw_mx, raw_my = pygame.mouse.get_pos()
    mx = int((raw_mx - offsetX) / scaleFactor)
    my = int((raw_my - offsetY) / scaleFactor)
    mPos = (mx, my)
    hoveredSlotInfo = None 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        #   
        if gameState == "DIALOGUE":
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                dialogueSys.next_line()
            continue  # 對話中不能按其他鍵會暫時封鎖其他輸入

         #選單與清單的捲動的滾輪操作   
        if gameState == "MENU" and showChangelog == True and event.type == pygame.MOUSEWHEEL:
            # 滾動速度設 40 比較順手
            changelogScroll -= event.y * 40
            if changelogScroll < 0: 
                changelogScroll = 0
            
            if changelogScroll > changelogMaxScroll: 
                changelogScroll = changelogMaxScroll
        # 暫停選單升級項目捲動   
        if gameState == "PAUSED" and event.type == pygame.MOUSEWHEEL:
            pauseUpgradeScroll -= event.y * 45

            if pauseUpgradeScroll < 0: pauseUpgradeScroll = 0
        # 武器庫清單捲動    
        if gameState == "WEAPON_STASH" and event.type == pygame.MOUSEWHEEL:
            arsenalScrollY -= event.y * 30

            if arsenalScrollY < 0: arsenalScrollY = 0
        # 鍵盤按鍵的切換
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                toggleFullScreen()
        
            if event.key == pygame.K_ESCAPE:
                if gameState == "PLAYING" and showInventory == False:
                    gameState = "PAUSED"
                elif gameState == "PLAYING" and showInventory == True:
                    showInventory = False
                    dragData = None
                elif gameState == "PAUSED":
                    gameState = "PLAYING"
                elif gameState == "SHOP" or gameState == "WEAPON_STASH" or gameState == "GENERAL_STASH" or gameState == "MOD_STATION":
                    gameState = "BUNKER"
                    dragData = None
                elif gameState == "DIFFICULTY":
                    gameState = "MENU" 
            # TAB 鍵 開啟或關閉背包介面
            if event.key == pygame.K_TAB and gameState == "PLAYING":
                if showInventory == True: showInventory = False
                else: showInventory = True
                dragData = None
            # H 鍵 使用醫療包
            if event.key == pygame.K_h and gameState == "PLAYING" and showInventory == False:
                player.use_med()
            # X 鍵 快速出售物品會配合滑鼠懸停觸發機制
            if event.key == pygame.K_x:
                currentHovered = None
                # 各介面尋找被選中的物品
                if gameState == "PLAYING" and showInventory == True:
                    for i in range(24):
                        rect = pygame.Rect(WIDTH//2 - 170 + (i%6)*58, HEIGHT//2 - 40 + (i//6)*58, 50, 50)
                        if rect.collidepoint(mx, my) and player.inventory[i] != None:
                            currentHovered = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}
                            break
                
                elif gameState == "GENERAL_STASH":
                    for i in range(36):
                        rect = pygame.Rect(s_start_x + (i%6)*58, s_start_y + (i//6)*58, 50, 50)
                        if rect.collidepoint(mx, my) and persistentStats["general_stash"][i] != None:
                            currentHovered = {"source": "STASH", "idx": i, "item": persistentStats["general_stash"][i]}
                            break
                    if currentHovered == None:
                        for i in range(24):
                            rect = pygame.Rect(p_start_x_s + (i%6)*58, p_start_y_s + (i//6)*58, 50, 50)
                            if rect.collidepoint(mx, my) and player.inventory[i] != None:
                                currentHovered = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}
                                break
                
                elif gameState == "MOD_STATION":
                    for i in range(24):
                        rect = pygame.Rect(p_start_x_m + (i%6)*58, p_start_y_m + (i//6)*58, 50, 50)
                        if rect.collidepoint(mx, my) and player.inventory[i] != None:
                            currentHovered = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}
                            break
                
                elif gameState == "WEAPON_STASH":
                    if list_rect.collidepoint(mx, my):
                        rel_y = my - list_rect.y + arsenalScrollY
                        idx = int(rel_y // 50) * 2
                        if mx >= WIDTH//2: idx += 1
                        if idx >= 0 and idx < len(arsenalWeaponsList):
                            currentHovered = {"source": "ARSENAL", "idx": idx, "item": createItem("WEAPON", 1, arsenalWeaponsList[idx])}
                    if currentHovered == None:
                        for i in range(24):
                            rect = pygame.Rect(p_start_x_w + (i%12)*58, p_start_y_w + (i//12)*58, 50, 50)
                            if rect.collidepoint(mx, my) and player.inventory[i] != None and player.inventory[i].type == "WEAPON":
                                currentHovered = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}
                                break
                
                # 賣東西換廢料
                if currentHovered != None:
                    val = getSellValue(currentHovered["item"])
                    if val > 0:
                        persistentStats["scrap"] += val
                        if currentHovered["source"] == "PLAYER":
                            player.inventory[currentHovered["idx"]] = None
                        elif currentHovered["source"] == "STASH":
                            persistentStats["general_stash"][currentHovered["idx"]] = None
                        elif currentHovered["source"] == "ARSENAL":
                            persistentStats["weapon_stash"].pop(currentHovered["idx"])
                            sortWeaponStash()
                            arsenalWeaponsList = []
                            for n in weaponTypes: arsenalWeaponsList.append(generateWeapon(n, "白"))
                            for w in persistentStats["weapon_stash"]: arsenalWeaponsList.append(w)
                        playSound("exp")
                        selectedModWeapon = None 
            # R 鍵（死亡重來）重生玩家並清空進度紀錄
            if event.key == pygame.K_r and gameState == "DIED":
                player = Player()
                chosenUpgrades.clear()
                enterBunker(False)
            # E 鍵 戰鬥中切換武器
            if event.key == pygame.K_e and gameState == "PLAYING":
                player.current_weapon_idx += 1
                if player.current_weapon_idx >= len(player.weapons):
                    player.current_weapon_idx = 0
                playSound("exp")
            # R 鍵（填裝彈藥） 只有在挑戰模式下才有換彈機制觸發填彈
            if event.key == pygame.K_r and gameState == "PLAYING" and gameMode == "CHALLENGE":
                if player.reload_timer <= 0 and player.ammo < (player.base_max_ammo + player.mag_size_bonus):
                    player.reload_timer = player.reload_duration
            #無敵模式密技
            if gameState == "PLAYING":
                key_buffer.append(event.key)
                if len(key_buffer) > len(CHEAT_CODE):
                    key_buffer.pop(0) 
                if key_buffer == CHEAT_CODE: 
                    if player.god_mode == False:
                        player.god_mode = True
                        player.cheat_all_weapons = True 
                    else:
                        player.god_mode = False
                        player.cheat_all_weapons = False
                        
                    if player.cheat_all_weapons == True:
                        player.weapons = []
                        for n in weaponTypes: player.weapons.append(generateWeapon(n, "金"))
                    else:
                        player.weapons = [player.primary_weapon, player.secondary_weapon]
                    player.current_weapon_idx = 0
                    playSound("levelup")
                    key_buffer = [] 
            #背包的拖拽系統處理物品的移動、裝備與丟棄
        if showInventory == True and gameState == "PLAYING":
            slot_size = 50
            margin = 8
            start_x = WIDTH//2 - 170
            start_y = HEIGHT//2 - 50
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in range(24):
                        rect = pygame.Rect(start_x + (i%6)*(slot_size+margin), start_y + (i//6)*(slot_size+margin), slot_size, slot_size)
                        if rect.collidepoint(mPos) and player.inventory[i] != None:
                            dragData = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}
                            player.inventory[i] = None
                            break
                elif event.button == 3:
                    for i in range(24):
                        rect = pygame.Rect(start_x + (i%6)*(slot_size+margin), start_y + (i//6)*(slot_size+margin), slot_size, slot_size)
                        if rect.collidepoint(mPos) and player.inventory[i] != None:
                            item = player.inventory[i]
                            if item.type == "MED":
                                player.use_med()
                            elif item.type == "WEAPON":
                                old_wep = player.weapons[player.current_weapon_idx]
                                player.weapons[player.current_weapon_idx] = item.weapon_obj
                                if player.current_weapon_idx == 0: player.primary_weapon = item.weapon_obj
                                else: player.secondary_weapon = item.weapon_obj
                                player.inventory[i] = createItem("WEAPON", 1, old_wep)
                                playSound("exp")
                                
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragData != None:
                droppedInSlot = False
                for i in range(24):
                    rect = pygame.Rect(start_x + (i%6)*(slot_size+margin), start_y + (i//6)*(slot_size+margin), slot_size, slot_size)
                    if rect.collidepoint(mPos):
                        rem = putItemInSlot("PLAYER", i, dragData["item"])
                        if rem != None:
                            putItemInSlot(dragData["source"], dragData["idx"], rem)
                        droppedInSlot = True
                        break
                        
                if droppedInSlot == False and not pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 200, 400, 400).collidepoint(mPos):
                    item = dragData["item"]
                    if item.type == "WEAPON":
                        items.append(DropItem(player.x, player.y, "WEAPON", weapon_obj=item.weapon_obj))
                    else:
                        items.append(DropItem(player.x, player.y, item.type, count=item.count))
                elif droppedInSlot == False:
                    putItemInSlot(dragData["source"], dragData["idx"], dragData["item"])
                dragData = None
        # 在基地中整理你的物資，存取與快速轉移        
        elif gameState == "GENERAL_STASH":
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in range(36):
                        rect = pygame.Rect(s_start_x + (i%6)*58, s_start_y + (i//6)*58, 50, 50)
                        if rect.collidepoint(mPos) and persistentStats["general_stash"][i] != None:
                            dragData = {"source": "STASH", "idx": i, "item": persistentStats["general_stash"][i]}
                            persistentStats["general_stash"][i] = None
                            break
                    if dragData == None:
                        for i in range(24):
                            rect = pygame.Rect(p_start_x_s + (i%6)*58, p_start_y_s + (i//6)*58, 50, 50)
                            if rect.collidepoint(mPos) and player.inventory[i] != None:
                                dragData = {"source": "PLAYER", "idx": i, "item": player.inventory[i]}
                                player.inventory[i] = None
                                break
                    if btn_stash_close.collidepoint(mPos):
                        gameState = "BUNKER"
                elif event.button == 3: 
                    for i in range(36):
                        rect = pygame.Rect(s_start_x + (i%6)*58, s_start_y + (i//6)*58, 50, 50)
                        if rect.collidepoint(mPos) and persistentStats["general_stash"][i] != None:
                            if fastTransfer(persistentStats["general_stash"][i], player.inventory):
                                persistentStats["general_stash"][i] = None
                                playSound("exp")
                    for i in range(24):
                        item = player.inventory[i]
                        rect = pygame.Rect(p_start_x_s + (i%6)*58, p_start_y_s + (i//6)*58, 50, 50)
                        if rect.collidepoint(mPos) and item != None and item.type != "WEAPON":
                            if fastTransfer(item, persistentStats["general_stash"]):
                                player.inventory[i] = None
                                playSound("exp")
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragData != None:
                dropped = False
                for i in range(36):
                    rect = pygame.Rect(s_start_x + (i%6)*58, s_start_y + (i//6)*58, 50, 50)
                    if rect.collidepoint(mPos):
                        if dragData["item"].type == "WEAPON": break 
                        rem = putItemInSlot("STASH", i, dragData["item"])
                        if rem != None: putItemInSlot(dragData["source"], dragData["idx"], rem)
                        dropped = True
                        break
                if dropped == False:
                    for i in range(24):
                        rect = pygame.Rect(p_start_x_s + (i%6)*58, p_start_y_s + (i//6)*58, 50, 50)
                        if rect.collidepoint(mPos):
                            rem = putItemInSlot("PLAYER", i, dragData["item"])
                            if rem != None: putItemInSlot(dragData["source"], dragData["idx"], rem)
                            dropped = True
                            break
                if dropped == False:
                    putItemInSlot(dragData["source"], dragData["idx"], dragData["item"])
                dragData = None
        #主選單互動區控制遊戲開始、遊戲操作手冊或離開        
        elif gameState == "MENU":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if showChangelog == True:
                    if changelog_close_button.collidepoint(mPos) or changelog_button.collidepoint(mPos):
                        showChangelog = False
                        changelogScroll = 0
                else:
                    if start_button.collidepoint(mPos):
                        gameState = "DIFFICULTY"
                    elif changelog_button.collidepoint(mPos):
                        showChangelog = True
                        changelogScroll = 0
                    elif exit_button.collidepoint(mPos):
                        running = False
        #難度選擇               
        elif gameState == "DIFFICULTY":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if normal_button.collidepoint(mPos): 
                    fullWipe("NORMAL")
                    dialogueSys.start("opening_narrative", "BUNKER")
                elif challenge_button.collidepoint(mPos): 
                    fullWipe("CHALLENGE")
                    dialogueSys.start("opening_narrative", "BUNKER")
                elif difficulty_back_button.collidepoint(mPos): 
                    gameState = "MENU"

        #在基地按下 E 鍵與互動物件進行交互的功能             
        elif gameState == "BUNKER":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                p_rect = player.rect.copy()
                #是否站在出擊傳送門上準備前往戰場
                if p_rect.colliderect(pygame.Rect(mapWidth//2 - 60, mapHeight//2 + 200, 120, 60)):
                    startRaid()
                #是否靠近商店準備升級裝備與屬性
                elif p_rect.colliderect(pygame.Rect(mapWidth//2 - 350, mapHeight//2 - 50, 100, 100)):
                    gameState = "SHOP"
                    playSound("exp")
                #是否靠近通用物資庫管理雜物
                elif p_rect.colliderect(pygame.Rect(mapWidth//2 + 50, mapHeight//2 - 150, 100, 100)):
                    gameState = "GENERAL_STASH"
                    playSound("exp")
                #是否靠近改裝台
                elif p_rect.colliderect(pygame.Rect(mapWidth//2 - 150, mapHeight//2 - 150, 100, 100)):
                    gameState = "MOD_STATION"
                    selectedModWeapon = None
                    playSound("exp")
                # 是否靠近武器庫整理與配置你的軍火庫
                elif p_rect.colliderect(pygame.Rect(mapWidth//2 + 250, mapHeight//2 - 50, 100, 100)): 
                    gameState = "WEAPON_STASH"
                    selectedArsenalIdx = 0
                    arsenalScrollY = 0
                    playSound("exp")
                    if player.cheat_all_weapons:
                        player.god_mode = False
                        player.cheat_all_weapons = False
                        player.weapons = [player.primary_weapon, player.secondary_weapon]
                        player.current_weapon_idx = 0
                    sortWeaponStash()
                    arsenalWeaponsList = []
                    for n in weaponTypes: arsenalWeaponsList.append(generateWeapon(n, "白"))
                    for w in persistentStats["weapon_stash"]: arsenalWeaponsList.append(w)
        # 商店系統使用廢料 (Scrap)作為貨幣來強化玩家          
        elif gameState == "SHOP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                #  購買生命值上限升級
                if btn_hp.collidepoint(mPos) and persistentStats["scrap"] >= 50:
                    persistentStats["scrap"] -= 50
                    persistentStats["max_hp"] += 10
                    player.max_hp += 10
                    player.hp += 10
                    playSound("levelup")
                # 購買傷害加成升級
                elif btn_dmg.collidepoint(mPos) and persistentStats["scrap"] >= 50:
                    persistentStats["scrap"] -= 50
                    persistentStats["dmg_bonus"] += 2
                    player.bullet_damage_bonus += 2
                    playSound("levelup")
                #  購買移動速度加成升級
                elif btn_spd.collidepoint(mPos) and persistentStats["scrap"] >= 50:
                    persistentStats["scrap"] -= 50
                    persistentStats["speed_bonus"] += 0.2
                    player.base_speed += 0.2
                    playSound("levelup")
                # 購買體力上限升級 
                elif btn_stamina.collidepoint(mPos) and persistentStats["scrap"] >= 50:
                    persistentStats["scrap"] -= 50
                    persistentStats["max_stamina"] += 20
                    player.max_stamina += 20
                    player.stamina += 20
                    playSound("levelup")
                # 購買護盾上限升級
                elif btn_shield.collidepoint(mPos) and persistentStats["scrap"] >= 50:
                    persistentStats["scrap"] -= 50
                    persistentStats["max_shield"] += 20
                    player.max_shield += 20
                    player.shield += 20
                    playSound("levelup")
                # 購買能量上限升級
                elif btn_energy.collidepoint(mPos) and persistentStats["scrap"] >= 50:
                    persistentStats["scrap"] -= 50
                    persistentStats["max_energy"] += 20
                    player.max_energy += 20
                    player.energy += 20
                    playSound("levelup")
                # 關閉商店頁面回到基地
                elif btn_shop_close.collidepoint(mPos):
                    gameState = "BUNKER"

        # 武器庫管理裝備與存取軍火          
        elif gameState == "WEAPON_STASH":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_wep_close.collidepoint(mPos):
                    gameState = "BUNKER"
                elif list_rect.collidepoint(mPos):
                    rel_y = mPos[1] - list_rect.y + arsenalScrollY
                    idx = int(rel_y // 50) * 2 # 計算玩家點選的是倉庫列表中的哪一項 
                    if mPos[0] >= WIDTH//2: idx += 1
                    if idx >= 0 and idx < len(arsenalWeaponsList):
                        selectedArsenalIdx = idx
                        playSound("exp")
                # 處理武器的裝備切換(放入主武器或副武器欄位)      
                if selectedArsenalIdx >= 0 and selectedArsenalIdx < len(arsenalWeaponsList):
                    sel_wep = arsenalWeaponsList[selectedArsenalIdx]
                    if btn_prim_w.collidepoint(mPos):
                        if player.primary_weapon.rarity != "白":
                            persistentStats["weapon_stash"].append(player.primary_weapon)
                        player.primary_weapon = sel_wep
                        player.weapons[0] = sel_wep
                        player.current_weapon_idx = 0
                        if selectedArsenalIdx >= 12:
                            persistentStats["weapon_stash"].pop(selectedArsenalIdx - 12)
                        sortWeaponStash()
                        arsenalWeaponsList = []
                        for n in weaponTypes: arsenalWeaponsList.append(generateWeapon(n, "白"))
                        for w in persistentStats["weapon_stash"]: arsenalWeaponsList.append(w)
                        playSound("levelup")
                    
                    elif btn_sec_w.collidepoint(mPos):
                        if player.secondary_weapon.rarity != "白":
                            persistentStats["weapon_stash"].append(player.secondary_weapon)
                        player.secondary_weapon = sel_wep
                        player.weapons[1] = sel_wep
                        player.current_weapon_idx = 1
                        if selectedArsenalIdx >= 12:
                            persistentStats["weapon_stash"].pop(selectedArsenalIdx - 12)
                        sortWeaponStash()
                        arsenalWeaponsList = []
                        for n in weaponTypes: arsenalWeaponsList.append(generateWeapon(n, "白"))
                        for w in persistentStats["weapon_stash"]: arsenalWeaponsList.append(w)
                        playSound("levelup")
            # 右鍵將武器從軍火庫取出至背包或將背包物品移入倉庫
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if list_rect.collidepoint(mPos):
                    rel_y = mPos[1] - list_rect.y + arsenalScrollY
                    idx = int(rel_y // 50) * 2
                    if mPos[0] >= WIDTH//2: idx += 1
                    if idx >= 12 and idx < len(arsenalWeaponsList):
                        wep = arsenalWeaponsList[idx]
                        if player.add_item(createItem("WEAPON", 1, wep)):
                            persistentStats["weapon_stash"].pop(idx - 12)
                            sortWeaponStash()
                            arsenalWeaponsList = []
                            for n in weaponTypes: arsenalWeaponsList.append(generateWeapon(n, "白"))
                            for w in persistentStats["weapon_stash"]: arsenalWeaponsList.append(w)
                            playSound("exp")
                # 掃描背包中的武器準備將其存入武器庫
                for i in range(24):
                    item = player.inventory[i]
                    rect = pygame.Rect(p_start_x_w + (i%12)*58, p_start_y_w + (i//12)*58, 50, 50) # 定義背包格子範圍
                    if rect.collidepoint(mPos) and item != None and item.type == "WEAPON":
                        persistentStats["weapon_stash"].append(item.weapon_obj)
                        player.inventory[i] = None
                        sortWeaponStash()
                        arsenalWeaponsList = []
                        for n in weaponTypes: arsenalWeaponsList.append(generateWeapon(n, "白"))
                        for w in persistentStats["weapon_stash"]: arsenalWeaponsList.append(w)
                        playSound("exp")
        #  改裝台可以選擇要進行強化的槍械              
        elif gameState == "MOD_STATION":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                p_x = WIDTH//2 - 320
                p_y = HEIGHT//2 + 20
                if rect_prim.collidepoint(mPos):
                    selectedModWeapon = player.primary_weapon
                elif rect_sec.collidepoint(mPos):
                    selectedModWeapon = player.secondary_weapon
                else:
                    # 在背包中尋找玩家點選的武器進行改裝
                    for i in range(24):
                        rect = pygame.Rect(p_x + (i%6)*58, p_y + (i//6)*58, 50, 50)
                        if rect.collidepoint(mPos) and player.inventory[i] != None and player.inventory[i].type == "WEAPON":
                            selectedModWeapon = player.inventory[i].weapon_obj
                            break
                            
                if btn_mod_close.collidepoint(mPos):
                    gameState = "BUNKER"
                # 會根據武器的稀有度來決定升級的成本和可獲得的附加屬性，當玩家點擊升級按鈕且選中的武器不是金色時會觸發這個邏輯   
                if selectedModWeapon != None:
                    if upg_btn.collidepoint(mPos) and selectedModWeapon.rarity != "金":
                        cost = 0
                        if selectedModWeapon.rarity == "白": cost = 50
                        elif selectedModWeapon.rarity == "藍": cost = 150
                        elif selectedModWeapon.rarity == "紫": cost = 300
                        # 升級武器會消耗廢料，武器的稀有度會提升，接著會據新的稀有度從可用的附加屬性池裡隨機獲得新的附加屬性，有限制金色武器為最高稀有度不可再生及
                        if persistentStats["scrap"] >= cost:
                            persistentStats["scrap"] -= cost
                            if selectedModWeapon.rarity == "白": selectedModWeapon.rarity = "藍"
                            elif selectedModWeapon.rarity == "藍": selectedModWeapon.rarity = "紫"
                            elif selectedModWeapon.rarity == "紫": selectedModWeapon.rarity = "金"
                            
                            pool = ["速射", "散射", "吸血", "爆擊"]
                            if selectedModWeapon.bullet_type != "piercing" and selectedModWeapon.bullet_type != "laser" and selectedModWeapon.bullet_type != "cannon" and selectedModWeapon.bullet_type != "flamethrower":
                                pool.append("穿透")
                            if selectedModWeapon.bullet_type != "flamethrower" and selectedModWeapon.bullet_type != "flame_grenade":
                                pool.append("燃燒")
                                
                            c = 0
                            if selectedModWeapon.rarity == "白": c = 0
                            elif selectedModWeapon.rarity == "藍": c = 1
                            elif selectedModWeapon.rarity == "紫": c = 2
                            elif selectedModWeapon.rarity == "金": c = 3
                            # 根據武器稀有度從裡面隨機選擇附加屬性
                            if c > len(pool): c = len(pool)
                            selectedModWeapon.affixes = random.sample(pool, c)
                            applyWeaponStats(selectedModWeapon)
                            playSound("levelup")
                     # 重置武器的附加屬性，會根據武器稀有度而定的廢料，當玩家點擊重置按鈕且選中的武器不是白色時會觸發這個邏輯，會限制白色是為了讓玩家多開寶相尋找       
                    if reroll_btn.collidepoint(mPos) and selectedModWeapon.rarity != "白":
                        cost = 0
                        if selectedModWeapon.rarity == "藍": cost = 30
                        elif selectedModWeapon.rarity == "紫": cost = 80
                        elif selectedModWeapon.rarity == "金": cost = 150
                        
                        if persistentStats["scrap"] >= cost:
                            persistentStats["scrap"] -= cost
                            pool = ["速射", "散射", "吸血", "爆擊"]
                            if selectedModWeapon.bullet_type != "piercing" and selectedModWeapon.bullet_type != "laser" and selectedModWeapon.bullet_type != "cannon" and selectedModWeapon.bullet_type != "flamethrower":
                                pool.append("穿透")
                            if selectedModWeapon.bullet_type != "flamethrower" and selectedModWeapon.bullet_type != "flame_grenade":
                                pool.append("燃燒")
                                
                            c = 0
                            if selectedModWeapon.rarity == "白": c = 0
                            elif selectedModWeapon.rarity == "藍": c = 1
                            elif selectedModWeapon.rarity == "紫": c = 2
                            elif selectedModWeapon.rarity == "金": c = 3
                            
                            if c > len(pool): c = len(pool)
                            selectedModWeapon.affixes = random.sample(pool, c)
                            applyWeaponStats(selectedModWeapon)
                            playSound("exp")
        # 在暫停狀態下玩家可以選擇繼續遊戲、進入避難所、重置遊戲或退出遊戲                    
        elif gameState == "PAUSED":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 10, 220, 50).collidepoint(mPos):
                    gameState = "PLAYING"
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 10, 220, 50).collidepoint(mPos):
                    enterBunker(False)
                elif pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 80, 220, 50).collidepoint(mPos):
                    fullWipe("NORMAL")
                elif pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 80, 220, 50).collidepoint(mPos):
                    running = False
        # 玩家可以點擊卡牌升級選項來選擇升級，然後點擊確認按鈕來應用升級。也可以點擊其他升級選項來切換選擇           
        elif gameState == "LEVEL_UP":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if selectedUpgradePosition != None and confirm_upgrade_button.collidepoint(mPos):
                    apply_upgrade(currentUpgradeChoices[selectedUpgradePosition])
                else:
                    i = 0
                    for card in cards:
                        if i < len(currentUpgradeChoices) and card.collidepoint(mPos):
                            selectedUpgradePosition = i
                            break
                        i += 1

    # 處理遊戲世界的邏輯更新
    if gameState == "BUNKER":
        player.update(clamp_rect=pygame.Rect(mapWidth//2 - 400, mapHeight//2 - 300, 800, 600))
        camX = mapWidth//2 - WIDTH/2
        camY = mapHeight//2 - HEIGHT/2

        if bunker_dummy != None: bunker_dummy.update()
        
        mouse_btns = pygame.mouse.get_pressed()
        # 當玩家按下左鍵且射擊冷卻時間小於等於0且不在衝刺狀態時，會根據當前武器的類型和屬性生成子彈
        if mouse_btns[0] and shootCooldown <= 0 and player.is_dashing == False:
            wep = player.weapons[player.current_weapon_idx]
            base_dir = pygame.math.Vector2((mx + camX) - player.x, (my + camY) - player.y)
            if base_dir.length() > 0:
                base_dir.normalize_ip()
            else:
                base_dir = pygame.math.Vector2(1, 0)
            
            player.current_spread += wep.base_recoil
            if player.current_spread > player.bullet_spread + 25.0:
                player.current_spread = player.bullet_spread + 25.0
                
            t_bullets = player.bullet_count
            if wep.bullet_type == "shotgun": t_bullets += 4
            if "散射" in wep.affixes: t_bullets += 2
                
            s_angle = -(t_bullets - 1) * player.current_spread / 2
            
            if wep.bullet_type == "cannon" or wep.bullet_type == "flame_grenade": screenShake = 5
            elif wep.bullet_type == "shotgun": screenShake = 2
            #火焰噴射器的彈道會隨機偏移模擬火焰的散亂感，就像越南大戰的風格
            for i in range(t_bullets):
                s_dir = base_dir.rotate(s_angle + i * player.current_spread)
                for j in range(1 + player.extra_same_path_bullets):
                    off = s_dir * (j * 15)
                #榴彈發射距離如果(flame_grenade)就飛350再爆炸
                    dist = 350 if wep.bullet_type == "flame_grenade" else 100
                    tx = player.x + s_dir.x * dist + off.x
                    ty = player.y + s_dir.y * dist + off.y

                    if wep.bullet_type == "flamethrower":
                        tx += random.randint(-40, 40)
                        ty += random.randint(-40, 40)
                    bunker_bullets.append(Bullet(player.rect.centerx + off.x, player.rect.centery + off.y, tx, ty, wep, player.guidance_level, player.bullet_damage_bonus))
                    
            shootCooldown = wep.shoot_delay
            playSound(wep.sound_name)
            
        alive_bunker_bullets = []
        # 更新子彈位置並偵測碰撞，只有在子彈還有生命且在地圖範圍內或是穿透子彈沒有擊中假人時才會繼續存在
        for b in bunker_bullets:
            b.update()
            if bunker_dummy != None and b.rect.colliderect(bunker_dummy.rect):
                damage_texts.append(DamageText(b.x, b.y - 20, b.damage, RED if b.is_crit else WHITE, b.is_crit))
                bunker_dummy.hit_log.append((pygame.time.get_ticks(), b.damage))
                bunker_dummy.shake_timer = 5
                for i in range(3): particles.append(Particle(b.x, b.y, b.color))
                playSound("hit")
                if b.is_piercing: alive_bunker_bullets.append(b)
            elif b.lifespan > 0 and pygame.Rect(0, 0, mapWidth, mapHeight).colliderect(b.rect):
                alive_bunker_bullets.append(b)
        bunker_bullets = alive_bunker_bullets

        alive_particles = []
        for p in particles:
            p.update()
            if p.timer > 0: alive_particles.append(p)
        particles = alive_particles
        
        alive_dt = []
        for dt in damage_texts:
            dt.update()
            if dt.timer > 0: alive_dt.append(dt)
        damage_texts = alive_dt
        
        if shootCooldown > 0: shootCooldown -= 1

    elif gameState == "PLAYING" and showInventory == False:
        if enemySpawnTimer > 0: enemySpawnTimer -= 1
        if enemySpawnTimer <= 0 and bossArmyActive == False:
            if len(enemies) < 150:
                is_e = False
                if random.random() < 0.15: is_e = True
                enemies.append(Enemy(player.level, is_e, player.x, player.y))
            enemySpawnTimer = 30 - player.level
            if enemySpawnTimer < 5: enemySpawnTimer = 5
        
        if raidStartTime != None and bossArmyActive == False:
            taskSystem.update_progress("survive", 1.0 / FPS)
            
        shake_x = 0
        shake_y = 0
        if screenShake > 0:
            shake_x = random.randint(-screenShake, screenShake)
            shake_y = random.randint(-screenShake, screenShake)
            screenShake -= 1

        camX = player.x - WIDTH / 2
        if camX < 0: camX = 0
        if camX > mapWidth - WIDTH: camX = mapWidth - WIDTH
        camX += shake_x
        
        camY = player.y - HEIGHT / 2
        if camY < 0: camY = 0
        if camY > mapHeight - HEIGHT: camY = mapHeight - HEIGHT
        camY += shake_y
        
        if magnetTimer > 0: magnetTimer -= 1
        if screenFlashTimer > 0: screenFlashTimer -= 1
        
        if extractionTimer > 0: 
            extractionTimer -= 1
        
        if extractionTimer <= 0 and bossArmyActive == False:
            bossArmyActive = True
            dialogueSys.start("timeout_warning", "PLAYING")
        
        if bossArmyActive == True:
            if pygame.time.get_ticks() % 15 == 0:
                e = Enemy(player.level + 15, True)
                e.max_hp *= 4
                e.hp = e.max_hp
                e.speed *= 1.3
                e.color = DARK_PURPLE
                e.weapon = generateWeapon("衝鋒槍", "紫")
                enemies.append(e)
        # 如果有提取點會辨識玩家是否在提取點範圍內以進行提取
        if extractionPt != None:
            distToExtract = math.sqrt((player.x - extractionPt.x)**2 + (player.y - extractionPt.y)**2)
            if distToExtract < extractionPt.radius:
                extractProgress += 1
                if extractProgress >= 120:
                    playSound("levelup")
                    enterBunker(True)
            else:
                extractProgress = 0

        keys_pressed = pygame.key.get_pressed()
        # 按住F鍵靠近箱子可以開箱
        if keys_pressed[pygame.K_f]:
            for c in chests:
                if c.state == "CLOSED":
                    distToChest = math.hypot(player.x - c.x, player.y - c.y)
                    if distToChest < 70:
                        has_key = False
                        for item in player.inventory:
                            if item != None and item.type == "KEY":
                                has_key = True
                                break
                        # 如果箱子是鎖著的但玩家沒有鑰匙就不能開箱      
                        if c.type == "LOCKED" and has_key == False:
                            pass 
                        else:
                            c.open_progress += 1
                            if c.open_progress >= 40:
                                c.state = "OPEN"
                                if c.type == "LOCKED":
                                    for i in range(24):
                                        if player.inventory[i] != None and player.inventory[i].type == "KEY":
                                            player.inventory[i].count -= 1
                                            if player.inventory[i].count <= 0: player.inventory[i] = None
                                            break
                                openChest(c)
        else:
            for c in chests:
                if c.state == "CLOSED":
                    c.open_progress -= 2
                    if c.open_progress < 0: c.open_progress = 0
        # 升級判定
        if player.exp >= player.max_exp:
            player.exp -= player.max_exp
            player.level += 1
            player.max_exp = int(player.max_exp * 1.25)
            chooseUpgradeCards()
            gameState = "LEVEL_UP"
            playSound("levelup")
        
        if taskSystem.current_task != None and taskSystem.current_task.is_completed == True:
            taskSystem.current_task.apply_reward(player)
            playSound("levelup")
            taskSystem.complete_task() 

        # Boss判定
        if player.level % 5 == 0 and player.level > 0 and player.level not in defeatedBossLevels and isBossActive == False and bossArmyActive == False:
            boss_spawn_count = len(defeatedBossLevels)
            boss_cycle = boss_spawn_count % 3
            if boss_cycle == 0: 
                boss = CoreBoss(player.level, player.x, player.y)
                dialogueSys.start("boss1_intro", "PLAYING")
            elif boss_cycle == 1: 
                boss = ChargerBoss(player.level, player.x, player.y)
                dialogueSys.start("boss2_intro", "PLAYING")
            else: 
                boss = BerserkerBoss(player.level, player.x, player.y)
                dialogueSys.start("boss3_intro", "PLAYING") 
            
            isBossActive = True
            pygame.mixer.music.pause()
            playSound("boss_bgm", -1)

        mouse_btns = pygame.mouse.get_pressed()
        world_mouse_x = mx + camX
        world_mouse_y = my + camY
        current_wep = player.weapons[player.current_weapon_idx]
        
        # 滑鼠開火
        if mouse_btns[0] and shootCooldown <= 0 and player.is_dashing == False:
            can_fire = True
            if gameMode == "CHALLENGE":
                if player.ammo <= 0: 
                    can_fire = False
                    if player.reload_timer <= 0:
                        player.reload_timer = player.reload_duration
                        playSound("reload")
                    else:
                        playSound("empty_click")
                else: 
                    player.ammo -= 1
                    if player.ammo <= 0:
                        player.reload_timer = player.reload_duration
                        playSound("reload")
            # 按下開火鍵時如果正在重裝則取消重裝            
            if can_fire == True:
                base_dir = pygame.math.Vector2(world_mouse_x - player.x, world_mouse_y - player.y)
                if base_dir.length() > 0: base_dir.normalize_ip()
                else: base_dir = pygame.math.Vector2(1, 0)
                
                player.current_spread += current_wep.base_recoil
                # 控制散布上限，避免散布過大導致子彈亂飛
                if player.current_spread > player.bullet_spread + 25.0:
                    player.current_spread = player.bullet_spread + 25.0
                    
                t_bullets = player.bullet_count
                # 根據武器特性增加子彈數量
                if current_wep.bullet_type == "shotgun": t_bullets += 4
                if "散射" in current_wep.affixes: t_bullets += 2
                    
                s_angle = -(t_bullets - 1) * player.current_spread / 2
                # 根據子彈類型決定畫面震動強度
                if current_wep.bullet_type == "cannon" or current_wep.bullet_type == "flame_grenade": screenShake = 5
                elif current_wep.bullet_type == "shotgun": screenShake = 2
                # 穿透子彈不會被箱子擋住
                for i in range(t_bullets):
                    s_dir = base_dir.rotate(s_angle + i * player.current_spread)
                    # 同一路徑多發幾發子彈
                    for j in range(1 + player.extra_same_path_bullets):
                        spawn_offset = s_dir * (j * 15) 

                        dist = 350 if current_wep.bullet_type == "flame_grenade" else 100
                        tx = player.x + s_dir.x * dist + spawn_offset.x
                        ty = player.y + s_dir.y * dist + spawn_offset.y

                        if current_wep.bullet_type == "flamethrower":
                            tx += random.randint(-40, 40)
                            ty += random.randint(-40, 40)
                        bullets.append(Bullet(player.rect.centerx + spawn_offset.x, player.rect.centery + spawn_offset.y, tx, ty, current_wep, player.guidance_level, player.bullet_damage_bonus))
                        
                shootCooldown = current_wep.shoot_delay - player.shoot_delay_reduction
                if shootCooldown < 2: shootCooldown = 2
                playSound(current_wep.sound_name)
                
        # 右鍵放技能
        if mouse_btns[2] and player.skill_cd <= 0 and player.energy >= player.skill_cost and player.is_dashing == False:
            player.energy -= player.skill_cost
            player.skill_cd = player.skill_max_cd
            playSound("shoot_laser") 
            temp_wep = generateWeapon("手槍", "白")
            temp_wep.bullet_type = "piercing"
            temp_wep.damage = 50
            for i in range(16):
                angle = math.radians(i * (360 / 16))
                bullets.append(Bullet(player.rect.centerx, player.rect.centery, player.rect.centerx + math.cos(angle)*100, player.rect.centery + math.sin(angle)*100, temp_wep, dmg_bonus=player.bullet_damage_bonus))
        # 技能冷卻
        if shootCooldown > 0: shootCooldown -= 1
        player.update()
        
        # 光環傷害判定            
        if player.aura_level > 0:
            aura_radius = 95 + player.aura_level * 25
            aura_damage = 0.02 * player.aura_level
            alive_enemies = []
            # 更新敵人狀態並判定是否受到光環傷害
            for e in enemies:
                if math.sqrt((e.x - player.x)**2 + (e.y - player.y)**2) <= aura_radius:
                    if e.shield > 0:
                        if aura_damage > e.shield:
                            leftover = aura_damage - e.shield
                            e.shield = 0
                            e.hp -= leftover
                        else: e.shield -= aura_damage
                    else: e.hp -= aura_damage
                    # 受傷粒子
                    if random.random() < 0.05: particles.append(Particle(e.x, e.y, BLUE))
                    # 經驗值掉落判定
                    if e.hp <= 0:
                        for i in range(8): particles.append(Particle(e.x, e.y, RED))
                        if random.random() < 0.4: items.append(DropItem(e.x, e.y, "EXP"))
                    else:
                        alive_enemies.append(e)
                else:
                    alive_enemies.append(e)
            enemies = alive_enemies
            
            if isBossActive and boss.state != "DEFEAT":
                if math.sqrt((boss.x - player.x)**2 + (boss.y - player.y)**2) <= aura_radius:
                    boss.hp -= aura_damage
        # 玩家衝刺軌跡       
        if player.is_dashing: trails.append(DashTrail(player.rect.centerx, player.rect.centery, player.size))
        alive_trails = []
        # 更新軌跡並移除已消失的軌跡
        for t in trails:
            t.update()
            if t.life > 0: alive_trails.append(t)
        trails = alive_trails
            
        map_rect = pygame.Rect(0, 0, mapWidth, mapHeight)
        alive_bullets = []

        # 子彈撞擊判定
        for b in bullets:
            b.update(enemies, boss if isBossActive else None)
            hit_chest = False
            for c in chests:
                if b.rect.colliderect(c.rect):
                    hit_chest = True
                    if b.is_piercing == False:
                        for i in range(3): particles.append(Particle(b.x, b.y, GRAY))
                        playSound("hit")
                    break
            # 穿透子彈不會被箱子擋住
            if hit_chest and b.is_piercing == False: continue 
            # 子彈與牆壁碰撞
            if b.explode:
                screenShake = 8
                playSound("shoot_cannon") 
                for i in range(30): particles.append(Particle(b.x, b.y, ORANGE))
                alive_enemies2 = []
                # 爆炸傷害判定
                for e in enemies:
                    if math.hypot(e.x - b.x, e.y - b.y) < 120: 
                        actual_dmg = b.damage
                        if e.shield > 0:
                            leftover = actual_dmg - e.shield
                            e.shield -= actual_dmg
                            if e.shield < 0: e.shield = 0
                            if leftover > 0: e.hp -= leftover
                        else:
                            e.hp -= actual_dmg
                         # 受傷粒子   
                        if e.hp <= 0: 
                            if random.random() < 0.4: items.append(DropItem(e.x, e.y, "EXP"))
                        else:
                            alive_enemies2.append(e)
                    else:
                        alive_enemies2.append(e)
                enemies = alive_enemies2
                # Boss爆炸傷害
                if isBossActive and boss.state != "DEFEAT" and math.hypot(boss.x - b.x, boss.y - b.y) < 150:
                    boss.hp -= b.damage
                continue 
                
            hit_something = False
            
            alive_enemies3 = []
            # 子彈與敵人碰撞
            for e in enemies:
                if b.rect.colliderect(e.rect) and hit_something == False:
                    if b.b_type == "frost": e.frost_timer = 120 
                    if b.b_type == "cannon": 
                        push_dist = math.hypot(e.x - player.x, e.y - player.y)
                        if push_dist > 0:
                            e.x += ((e.x - player.x) / push_dist) * 30
                            e.y += ((e.y - player.y) / push_dist) * 30 
                        
                    if b.is_burning: e.burn_timer = 180

                    if b.is_vampiric and random.random() < 0.05:
                        player.hp += 2
                        if player.hp > player.max_hp: player.hp = player.max_hp
                        
                    if e.shield > 0:
                        leftover = b.damage - e.shield
                        e.shield -= b.damage
                        if e.shield < 0: e.shield = 0
                        if leftover > 0: e.hp -= leftover
                    else:
                        e.hp -= b.damage
                        
                    e.hit_timer = 4 
                    if e.combat_type != "kamikaze": 
                        kb_force = b.damage * 0.1
                        if kb_force > 6.0: kb_force = 6.0
                        if b.is_crit: kb_force *= 1.5
                        e.x += b.dir_x * kb_force
                        e.y += b.dir_y * kb_force
                    
                    if b.is_crit or b.damage >= 50:
                        if screenShake < 6: screenShake = 6 

                    cColor = WHITE
                    if b.is_crit: cColor = RED
                    elif b.damage >= 40: cColor = YELLOW
                    damage_texts.append(DamageText(e.x, e.y - 20, b.damage, cColor, b.is_crit))
                    hit_something = True
                    # 受傷粒子
                    for i in range(2): particles.append(Particle(e.x, e.y, b.color))
                    playSound("hit")
                    taskSystem.update_progress("damage", b.damage)

                    # 穿透判定
                    if b.is_piercing == False: break 
            
            # Boss碰撞判定 (只扣血，不處理死亡掉落)
            if isBossActive and boss != None and b.rect.colliderect(boss.rect) and boss.state != "DEFEAT":
                hit_something = True
                if boss.can_take_damage() == False:
                    # Boss受傷無敵中
                    for i in range(5): particles.append(Particle(boss.x, boss.y, GRAY))
                else:
                    if b.b_type == "frost": boss.frost_timer = 60 
                    if b.is_burning: boss.burn_timer = 180
                    if b.is_vampiric and random.random() < 0.05:
                        player.hp += 2
                        if player.hp > player.max_hp: player.hp = player.max_hp
                    boss.hp -= b.damage
                    boss.hit_timer = 4
                    if b.is_crit or b.damage >= 50:
                        if screenShake < 8: screenShake = 8
                        pygame.time.delay(15)
                    damage_texts.append(DamageText(boss.x, boss.y - 20, b.damage, RED if b.is_crit else WHITE, b.is_crit))
                    for i in range(8): particles.append(Particle(boss.x, boss.y, YELLOW))
                    playSound("hit")
                    taskSystem.update_progress("damage", b.damage)

            if b.lifespan > 0 and map_rect.colliderect(b.rect) and (hit_something == False or b.is_piercing) and b.explode == False:
                alive_bullets.append(b)
        bullets = alive_bullets

        alive_dt = []
        # 傷害文字更新
        for dt in damage_texts:
            dt.update()
            if dt.timer > 0: alive_dt.append(dt)
        damage_texts = alive_dt
        
        alive_particles = []
        # 粒子更新
        for p in particles:
            p.update()
            if p.timer > 0: alive_particles.append(p)
        particles = alive_particles

        alive_eb = []
        # 敵方子彈更新與判定
        for eb in enemy_bullets:
            eb.update(player.x, player.y)
            hit_chest = False
            for c in chests:
                if eb.rect.colliderect(c.rect):
                    hit_chest = True
                    if eb.b_type != "piercing" and eb.b_type != "laser":
                        for i in range(3): particles.append(Particle(eb.x, eb.y, GRAY))
                        playSound("hit")
                    break
                    
            if hit_chest and eb.b_type != "piercing" and eb.b_type != "laser":
                continue
            # 敵方子彈爆炸判定
            if hasattr(eb, 'explode') and eb.explode:
                playSound("shoot_cannon") 
                for i in range(12): 
                    p = Particle(eb.x, eb.y, eb.color)
                    p.vel_x = math.cos(i*30)*3
                    p.vel_y = math.sin(i*30)*3
                    particles.append(p)
                if math.hypot(player.x - eb.x, player.y - eb.y) < 70:
                    if player.god_mode == False and player.invincible_timer <= 0 and player.is_dashing == False:
                        actual_dmg = int(eb.damage * 1.5) - player.damage_reduction
                        if actual_dmg < 1: actual_dmg = 1
                        if player.shield > 0:
                            if actual_dmg > player.shield:
                                leftover = actual_dmg - player.shield
                                player.shield = 0
                                player.hp -= leftover
                            else: player.shield -= actual_dmg
                        else: player.hp -= actual_dmg
                        player.invincible_timer = player.invincible_duration
                        screenShake = 12
                        playSound("hurt")
                continue
            
            if map_rect.colliderect(eb.rect):
                alive_eb.append(eb)
        enemy_bullets = alive_eb

        resolveChestCollision(player, chests)
        for e in enemies:
            e.update(player.x, player.y, enemies, enemy_bullets)
            resolveChestCollision(e, chests)
        # Boss行動
        if isBossActive and boss != None:
            boss.update(player.x, player.y, bullets, enemies, enemy_bullets)
            if resolveChestCollision(boss, chests):
                if boss.state == "CHARGE" or boss.state == "DASH" or boss.state == "SLAM" or boss.state == "RAGE_DASH":
                    b_name = ""
                    if hasattr(boss, "name"): b_name = boss.name

                    if b_name == "防衛核心": boss.state = "ATTACK"
                    elif b_name == "衝刺突擊者": boss.state = "REST"
                    else: boss.state = "WALK"
                    boss.timer = 0
                    screenShake = 15

                    playSound("shoot_cannon") 
                    for i in range(15): particles.append(Particle(boss.x, boss.y, GRAY)) 
                    
            if boss.state == "DEFEAT" and boss.defeat_timer > 60:
                isBossActive = False
                defeatedBossLevels.append(boss.spawn_level)
                stopSound("boss_bgm")
                pygame.mixer.music.unpause()
                
        # 怪物撞玩家
        for e in enemies:
            if gameState == "DIED": break
            if player.rect.colliderect(e.rect):

                if player.god_mode: continue
                if player.invincible_timer <= 0 and player.is_dashing == False:
                    actual_dmg = e.damage - player.damage_reduction

                    if actual_dmg < 1: actual_dmg = 1
                    if player.shield > 0:

                        if actual_dmg > player.shield:
                            leftover = actual_dmg - player.shield
                            player.shield = 0
                            player.hp -= leftover

                        else: player.shield -= actual_dmg

                    else: player.hp -= actual_dmg
                    player.invincible_timer = player.invincible_duration
                    screenShake = 10
                    playSound("hurt")

                if e.combat_type == "kamikaze":
                    for i in range(15): particles.append(Particle(e.x, e.y, ORANGE))
                    e.hp = 0 # 讓他在前面的清血量被清掉
                    
        # 敵方子彈撞玩家
        alive_eb2 = []
        for eb in enemy_bullets:
            if gameState == "DIED": break
            if player.rect.colliderect(eb.rect):
                if player.god_mode == False and player.invincible_timer <= 0 and player.is_dashing == False:
                    actual_dmg = 25 - player.damage_reduction
                    if actual_dmg < 1: actual_dmg = 1
                    if player.shield > 0:
                        if actual_dmg > player.shield:
                            leftover = actual_dmg - player.shield
                            player.shield = 0
                            player.hp -= leftover
                        else: player.shield -= actual_dmg
                    else: player.hp -= actual_dmg
                    player.invincible_timer = player.invincible_duration
                    screenShake = 10
                    playSound("hurt")
            else:
                alive_eb2.append(eb)
        enemy_bullets = alive_eb2
                
        if isBossActive and player.rect.colliderect(boss.rect) and gameState == "PLAYING": 
            if player.god_mode == False and player.invincible_timer <= 0 and player.is_dashing == False:
                actual_dmg = boss.collision_damage - player.damage_reduction
                if actual_dmg < 1: actual_dmg = 1
                if player.shield > 0:
                    if actual_dmg > player.shield:
                        leftover = actual_dmg - player.shield
                        player.shield = 0
                        player.hp -= leftover
                    else: player.shield -= actual_dmg
                else: player.hp -= actual_dmg
                player.invincible_timer = player.invincible_duration
                screenShake = 10
                playSound("hurt")

        # 在所有動作後處理敵人與BOSS的死亡與掉落物
        alive_enemies_final = []
        for e in enemies:
            if e.hp <= 0:
                for i in range(10): particles.append(Particle(e.x, e.y, RED))
                taskSystem.update_progress("kill", 1)
                if e.is_elite:
                    taskSystem.update_progress("kill_elite", 1)
                    items.append(DropItem(e.x-15, e.y, "EXP"))
                    items.append(DropItem(e.x+15, e.y, "MED"))
                    items.append(DropItem(e.x, e.y+15, "SHIELD"))
                    items.append(DropItem(e.x, e.y-15, "SCRAP", random.randint(1,3)))
                    if random.random() < 0.3: items.append(DropItem(e.x+20, e.y, "KEY")) 
                else:
                    if e.combat_type != "kamikaze": # 自爆怪不掉裝備物資
                        rand_drop = random.random()
                        if rand_drop < 0.01: items.append(DropItem(e.x, e.y, "MAGNET"))
                        elif rand_drop < 0.02: items.append(DropItem(e.x, e.y, "BOMB"))
                        elif rand_drop < 0.15: items.append(DropItem(e.x, e.y, "SCRAP", random.randint(1,2)))
                        elif rand_drop < 0.35: items.append(DropItem(e.x, e.y, "EXP"))
                        elif rand_drop < 0.40: items.append(DropItem(e.x, e.y, "MED"))
            else:
                alive_enemies_final.append(e)
        enemies = alive_enemies_final

        if isBossActive and boss != None and boss.hp <= 0 and boss.state != "DEFEAT":
            boss.state = "DEFEAT"
            boss.defeat_timer = 0
            for i in range(40): items.append(DropItem(boss.x + random.randint(-60,60), boss.y + random.randint(-60,60), "EXP"))
            for i in range(10): items.append(DropItem(boss.x + random.randint(-40,40), boss.y + random.randint(-40,40), "SCRAP", random.randint(2,5)))
            items.append(DropItem(boss.x, boss.y, "KEY"))
            for i in range(50): particles.append(Particle(boss.x, boss.y, YELLOW))
                
        # 處理玩家死掉
        if player.hp <= 0 and gameState == "PLAYING":
            inv_copy = []
            for item in player.inventory:
                if item != None: inv_copy.append(item)
                
            w1 = None
            if player.primary_weapon.rarity != "白": w1 = player.primary_weapon
            w2 = None
            if player.secondary_weapon.rarity != "白": w2 = player.secondary_weapon
            
            uCopy = []
            for cu in chosenUpgrades: uCopy.append(cu)
            
            lostItem = PlayerLostItem(player.x, player.y, player.level, player.exp, uCopy, inv_copy, w1, w2)
            gameState = "DIED"
            playSound("gameover")
            stopSound("boss_bgm")
            pygame.mixer.music.unpause()
        # 撿道具，磁鐵效果，還有撿回自己掉的東西
        if gameState == "PLAYING":
            if magnetTimer > 0: eff_radius = 9999
            else: eff_radius = player.magnet_radius
            
            alive_items = []
            # 更新道具狀態
            for g in items:
                g.update(player.x, player.y, eff_radius)
                # 撿到東西
                if player.rect.colliderect(g.rect):
                    if g.item_type == "EXP" or g.item_type == "MAGNET" or g.item_type == "BOMB" or g.item_type == "SHIELD":
                        if g.item_type == "EXP":
                            player.exp += 25 * player.exp_multiplier
                            playSound("exp") 
                        elif g.item_type == "SHIELD":
                            player.shield += 20
                            if player.shield > player.max_shield: player.shield = player.max_shield
                            playSound("exp")
                        elif g.item_type == "MAGNET":
                            magnetTimer = 300
                            playSound("levelup")
                        elif g.item_type == "BOMB":
                            screenFlashTimer = 15
                            for e in enemies:
                                for i in range(8): particles.append(Particle(e.x, e.y, RED))
                                items.append(DropItem(e.x, e.y, "EXP"))
                            enemies.clear()
                            if isBossActive and boss.state != "DEFEAT":
                                boss.hp -= 800
                                for i in range(15): particles.append(Particle(boss.x, boss.y, ORANGE))
                            playSound("hit")
                    else:
                        if g.item_type == "WEAPON": new_item = createItem("WEAPON", 1, g.weapon_obj)
                        else: new_item = createItem(g.item_type, g.count)
                        
                        if player.add_item(new_item):
                            playSound("exp")
                            if g.item_type == "SCRAP" or g.item_type == "KEY":
                                taskSystem.update_progress("collect", g.count)
                        else:
                            alive_items.append(g) # 撿不起來留著
                else:
                    alive_items.append(g)
            items = alive_items
            # 處理玩家撿到自己掉的東西          
            if lostItem != None and player.rect.colliderect(lostItem.rect):
                if lostItem.level > player.level: player.level = lostItem.level
                player.exp += lostItem.exp
                
                for u in lostItem.upgrades:
                    idx = -1
                    c = 0
                    for opt in upgradeOptions:
                        if opt["title"] == u["title"]:
                            idx = c
                            break
                        c += 1
                        
                    if idx != -1:
                        for i in range(u["count"]):
                            apply_upgrade(idx, True)
                            
                if lostItem.w1 != None: items.append(DropItem(lostItem.x + random.randint(-40,40), lostItem.y + random.randint(-40,40), "WEAPON", weapon_obj=lostItem.w1))
                if lostItem.w2 != None: items.append(DropItem(lostItem.x + random.randint(-40,40), lostItem.y + random.randint(-40,40), "WEAPON", weapon_obj=lostItem.w2))
                for item in lostItem.inventory:
                    if item.type == "WEAPON": items.append(DropItem(lostItem.x + random.randint(-40,40), lostItem.y + random.randint(-40,40), "WEAPON", weapon_obj=item.weapon_obj))
                    else: items.append(DropItem(lostItem.x + random.randint(-40,40), lostItem.y + random.randint(-40,40), item.type, count=item.count))
                lostItem = None
                playSound("levelup")

    # 畫面繪製
    if gameState == "BUNKER" or gameState == "SHOP" or gameState == "GENERAL_STASH" or gameState == "MOD_STATION" or gameState == "WEAPON_STASH" or (gameState == "DIALOGUE" and dialogueSys.previous_state == "BUNKER"):
        screen.fill(BLACK)
        # 畫地網格
        for i in range(0, WIDTH, 40): pygame.draw.line(screen, (15, 18, 22), (i,0), (i,HEIGHT))
        for i in range(0, HEIGHT, 40): pygame.draw.line(screen, (15, 18, 22), (0,i), (WIDTH,i))
        
        bunker_rect = pygame.Rect(mapWidth//2 - 400 - camX, mapHeight//2 - 300 - camY, 800, 600)
        pygame.draw.rect(screen, (25, 28, 35), bunker_rect)
        pygame.draw.rect(screen, (60, 65, 80), bunker_rect, 4)
        
        draw_terminal(screen, pygame.Rect(mapWidth//2 - 60 - camX, mapHeight//2 + 200 - camY, 120, 60), GREEN, "部署閘門 [E]", "DEPLOY")
        draw_terminal(screen, pygame.Rect(mapWidth//2 - 350 - camX, mapHeight//2 - 50 - camY, 100, 100), BLUE, "黑市商店 [E]", "SHOP")
        draw_terminal(screen, pygame.Rect(mapWidth//2 - 150 - camX, mapHeight//2 - 150 - camY, 100, 100), ORANGE, "改造台 [E]", "MOD")
        draw_terminal(screen, pygame.Rect(mapWidth//2 + 50 - camX, mapHeight//2 - 150 - camY, 100, 100), (50, 150, 200), "收藏箱 [E]", "STASH")
        draw_terminal(screen, pygame.Rect(mapWidth//2 + 250 - camX, mapHeight//2 - 50 - camY, 100, 100), RED, "武器箱 [E]", "WEAPON")
        
        if bunker_dummy != None: bunker_dummy.draw(screen)

        for b in bunker_bullets: b.draw(screen)
        for p in particles: p.draw(screen)
        for dt in damage_texts: dt.draw(screen)

        screen.blit(large_font.render("地堡安全屋", True, YELLOW), (WIDTH//2 - 120, 50))
        screen.blit(font.render("擁有廢料: " + str(persistentStats['scrap']), True, SCRAP_COLOR), (WIDTH//2 - 70, 100))
        
        player.draw(screen, player.weapons[player.current_weapon_idx])
        drawUpgradeSummary(screen, WIDTH - 260, 20, max_items=5)
        drawTaskPanel(screen, taskSystem, 20, HEIGHT - 220)
        # 升級商店
        if gameState == "SHOP":
            screen.blit(dim_surface, (0, 0))
            draw_ui_panel(screen, shop_bg, "黑市升級 (BLACK MARKET)", BLUE)
            draw_hover_button(screen, btn_shop_close, "X", (180, 60, 60), RED, WHITE)
            
            cHp = GRAY
            if persistentStats["scrap"]>=50: cHp = GREEN
            draw_hover_button(screen, btn_hp, "最大血量+10 (目前:" + str(player.max_hp) + ") - 50廢料", cHp, (50, 180, 50), BLACK)
            
            cDmg = GRAY
            if persistentStats["scrap"]>=50: cDmg = ORANGE
            draw_hover_button(screen, btn_dmg, "武器傷害+2 (目前:+" + str(persistentStats['dmg_bonus']) + ") - 50廢料", cDmg, (200, 120, 0), BLACK)
            
            cSpd = GRAY
            if persistentStats["scrap"]>=50: cSpd = CYAN
            draw_hover_button(screen, btn_spd, "移動速度+0.2 (目前:+" + str(round(persistentStats['speed_bonus'], 1)) + ") - 50廢料", cSpd, (0, 180, 180), BLACK)
            
            cStm = GRAY
            if persistentStats["scrap"]>=50: cStm = (220, 220, 80)
            draw_hover_button(screen, btn_stamina, "最大體力+20 (目前:" + str(player.max_stamina) + ") - 50廢料", cStm, (255, 255, 100), BLACK)
            
            cShd = GRAY
            if persistentStats["scrap"]>=50: cShd = (100, 150, 255)
            draw_hover_button(screen, btn_shield, "最大護盾+20 (目前:" + str(player.max_shield) + ") - 50廢料", cShd, (130, 180, 255), BLACK)
            
            cEn = GRAY
            if persistentStats["scrap"]>=50: cEn = (200, 100, 255)
            draw_hover_button(screen, btn_energy, "最大能量+20 (目前:" + str(player.max_energy) + ") - 50廢料", cEn, (230, 130, 255), BLACK)
            
            scrap_txt = font.render("擁有廢料: " + str(persistentStats['scrap']), True, SCRAP_COLOR)
            screen.blit(scrap_txt, (shop_bg.centerx - scrap_txt.get_width()//2, shop_bg.bottom - 40))
        # 收藏箱    
        elif gameState == "GENERAL_STASH":
            screen.blit(dim_surface, (0, 0))
            draw_ui_panel(screen, stash_bg, "格子收藏箱 (GENERAL STASH)", (50, 150, 200))
            for i in range(36):
                col = i % 6
                row = i // 6
                rect = pygame.Rect(s_start_x + col*58, s_start_y + row*58, 50, 50)
                pygame.draw.rect(screen, (25, 28, 35), rect, border_radius=6)
                pygame.draw.rect(screen, (55, 60, 70), rect, 1, border_radius=6)
                item = persistentStats["general_stash"][i]
                
                is_dragging_this = False
                if dragData != None and dragData["source"] == "STASH" and dragData["idx"] == i:
                    is_dragging_this = True
                    
                if item != None and is_dragging_this == False:
                    c = YELLOW
                    if item.type == "MED": c = hpColor
                    elif item.type == "SCRAP": c = SCRAP_COLOR
                    pygame.draw.circle(screen, c, rect.center, 14)
                    screen.blit(tiny_font.render(str(item.count), True, WHITE), (rect.right - 18, rect.bottom - 18))
                    
                    if rect.collidepoint(mPos) and dragData == None:
                        hoveredSlotInfo = {"source": "STASH", "idx": i, "item": item}
                        pygame.draw.rect(screen, WHITE, rect, 2, border_radius=6)
                        
            hi = drawPlayerInvGrid(screen, p_start_x_s, p_start_y_s, mx, my, False)
            if hi != None: hoveredSlotInfo = hi
            
            screen.blit(small_font.render("背包與收藏箱不可放武器 | 游標指著按 [X] 出售", True, GRAY), (WIDTH//2 - 180, HEIGHT//2 + 250))
            draw_hover_button(screen, btn_stash_close, "X", (150, 50, 50), RED)
        # 武器改造台    
        elif gameState == "MOD_STATION":
            screen.blit(dim_surface, (0, 0))
            draw_ui_panel(screen, mod_bg, "武器改造台 (WORKBENCH)", ORANGE)
            draw_hover_button(screen, btn_mod_close, "X", (180, 60, 60), RED, WHITE)
            
            pygame.draw.rect(screen, (30,34,42), rect_prim, border_radius=8)
            screen.blit(small_font.render("主武器", True, WHITE), (rect_prim.centerx - 25, rect_prim.y + 12))
            w_name_1 = font.render(player.primary_weapon.base_name, True, getRarityColor(player.primary_weapon.rarity))
            screen.blit(w_name_1, (rect_prim.centerx - w_name_1.get_width()//2, rect_prim.centery + 5))
            if selectedModWeapon == player.primary_weapon: pygame.draw.rect(screen, YELLOW, rect_prim, 2, border_radius=8)
            elif rect_prim.collidepoint(mPos): pygame.draw.rect(screen, WHITE, rect_prim, 1, border_radius=8)

            pygame.draw.rect(screen, (30,34,42), rect_sec, border_radius=8)
            screen.blit(small_font.render("副武器", True, WHITE), (rect_sec.centerx - 25, rect_sec.y + 12))
            w_name_2 = font.render(player.secondary_weapon.base_name, True, getRarityColor(player.secondary_weapon.rarity))
            screen.blit(w_name_2, (rect_sec.centerx - w_name_2.get_width()//2, rect_sec.centery + 5))
            if selectedModWeapon == player.secondary_weapon: pygame.draw.rect(screen, YELLOW, rect_sec, 2, border_radius=8)
            elif rect_sec.collidepoint(mPos): pygame.draw.rect(screen, WHITE, rect_sec, 1, border_radius=8)

            hi = drawPlayerInvGrid(screen, p_start_x_m, p_start_y_m, mx, my, True)
            if hi != None: hoveredSlotInfo = hi
            
            for i in range(24):
                item = player.inventory[i]
                if item != None and item.type == "WEAPON" and selectedModWeapon == item.weapon_obj:
                    pygame.draw.rect(screen, YELLOW, (p_start_x_m + (i%6)*58, p_start_y_m + (i//6)*58, 50, 50), 2, border_radius=6)

            detail_rect = pygame.Rect(WIDTH//2 + 20, HEIGHT//2 - 180, 330, 410)
            pygame.draw.rect(screen, (25,28,35), detail_rect, border_radius=10)
            # 顯示選中武器的資訊
            if selectedModWeapon != None:
                c = getRarityColor(selectedModWeapon.rarity)
                screen.blit(large_font.render(selectedModWeapon.full_name, True, c), (detail_rect.x + 20, detail_rect.y + 20))
                screen.blit(font.render("傷害: " + str(selectedModWeapon.damage), True, WHITE), (detail_rect.x + 20, detail_rect.y + 80))
                
                affStr = ""
                if len(selectedModWeapon.affixes) > 0:
                    for a in selectedModWeapon.affixes: affStr += a + ","
                    affStr = affStr[:-1]
                else: affStr = "無"
                screen.blit(font.render("詞綴: " + affStr, True, YELLOW), (detail_rect.x + 20, detail_rect.y + 120))
                
                if selectedModWeapon.rarity != "金":
                    cost = 0
                    if selectedModWeapon.rarity == "白": cost = 50
                    elif selectedModWeapon.rarity == "藍": cost = 150
                    elif selectedModWeapon.rarity == "紫": cost = 300
                    cUpg = GRAY
                    if persistentStats["scrap"] >= cost: cUpg = GREEN
                    draw_hover_button(screen, upg_btn, "升級品質 (" + str(cost) + " 廢料)", cUpg, (50, 180, 50), BLACK)
                    
                if selectedModWeapon.rarity != "白":
                    cost = 0
                    if selectedModWeapon.rarity == "藍": cost = 30
                    elif selectedModWeapon.rarity == "紫": cost = 80
                    elif selectedModWeapon.rarity == "金": cost = 150
                    cRe = GRAY
                    if persistentStats["scrap"] >= cost: cRe = BLUE
                    draw_hover_button(screen, reroll_btn, "重置詞綴 (" + str(cost) + " 廢料)", cRe, (50, 100, 180))
            
            draw_hover_button(screen, btn_mod_close, "X", (150, 50, 50), RED)
        # 武器收藏箱
        elif gameState == "WEAPON_STASH":
            screen.blit(dim_surface, (0, 0))
            draw_ui_panel(screen, wep_stash_bg, "全自動武器箱 (ARSENAL)", RED)
            draw_hover_button(screen, btn_wep_close, "X", (180, 60, 60), RED, WHITE)
            
            p_c = getRarityColor(player.primary_weapon.rarity)
            s_c = getRarityColor(player.secondary_weapon.rarity)
            screen.blit(small_font.render("當前裝備 =>", True, WHITE), (WIDTH//2 - 340, HEIGHT//2 - 220))
            screen.blit(small_font.render("主: " + player.primary_weapon.full_name, True, p_c), (WIDTH//2 - 220, HEIGHT//2 - 220))
            screen.blit(small_font.render("副: " + player.secondary_weapon.full_name, True, s_c), (WIDTH//2 + 50, HEIGHT//2 - 220))

            list_rect = pygame.Rect(WIDTH//2 - 340, HEIGHT//2 - 180, 680, 260)
            pygame.draw.rect(screen, (15, 18, 22), list_rect, border_radius=6)
            pygame.draw.rect(screen, (50, 55, 65), list_rect, 1, border_radius=6)
            
            listH = (len(arsenalWeaponsList)+1)//2 * 50
            if listH < list_rect.height: listH = list_rect.height
            list_surf = pygame.Surface((list_rect.width, listH))
            list_surf.fill((15, 18, 22))
            
            i = 0
            for wep in arsenalWeaponsList:
                col = i % 2
                row = i // 2
                box = pygame.Rect(col*335 + 10, row*50 + 5, 315, 42)
                
                is_sel = False
                if i == selectedArsenalIdx: is_sel = True
                    
                pygame.draw.rect(list_surf, (40, 45, 55), box, border_radius=6)
                if is_sel:
                    pygame.draw.rect(list_surf, YELLOW, box, 2, border_radius=6)
                else:
                    pygame.draw.rect(list_surf, GRAY, box, 1, border_radius=6)
                
                c = getRarityColor(wep.rarity)
                gunName = "gun_" + wep.base_name
                if gunName in images and images[gunName] != None:
                    gun_img = images[gunName]
                    list_surf.blit(gun_img, (box.x + 10, box.centery - 9))
                    name_surf = small_font.render(wep.full_name, True, c)
                    list_surf.blit(name_surf, (box.x + 60, box.y + 10))
                else:
                    name_surf = small_font.render(wep.full_name, True, c)
                    list_surf.blit(name_surf, (box.x + 10, box.y + 10))
                    
                affStr = ""
                if len(wep.affixes) > 0:
                    for a in wep.affixes: affStr += a + ","
                    affStr = affStr[:-1]
                else: affStr = "無"
                
                stat_surf = tiny_font.render("傷:" + str(wep.damage) + " [" + affStr + "]", True, WHITE)
                list_surf.blit(stat_surf, (box.right - stat_surf.get_width() - 10, box.y + 14))
                
                mx_rel = mx - list_rect.x
                my_rel = my - list_rect.y + arsenalScrollY
                if box.collidepoint(mx_rel, my_rel) and list_rect.collidepoint(mPos):
                    pygame.draw.rect(list_surf, WHITE, box, 1, border_radius=6)
                    hoveredSlotInfo = {"source": "ARSENAL", "idx": i, "item": createItem("WEAPON", 1, wep)}
                i += 1

            screen.blit(list_surf, list_rect.topleft, pygame.Rect(0, arsenalScrollY, list_rect.width, list_rect.height))
            screen.blit(small_font.render("右鍵:切換武器箱與背包 | 游標指著按 [X] 出售", True, GRAY), (WIDTH//2 - 344, HEIGHT//2 + 90))
            # 背包格子
            for i in range(24):
                rect = pygame.Rect(p_start_x_w + (i%12)*58, p_start_y_w + (i//12)*58, 50, 50)
                pygame.draw.rect(screen, (25, 28, 35), rect, border_radius=6)
                pygame.draw.rect(screen, (55, 60, 70), rect, 1, border_radius=6)
                item = player.inventory[i]
                if item != None:
                    if item.type == "WEAPON":
                        gunName = "gun_" + item.weapon_obj.base_name
                        if gunName in images and images[gunName] != None:
                            scaled_gun = pygame.transform.scale(images[gunName], (40, 16))
                            screen.blit(scaled_gun, scaled_gun.get_rect(center=rect.center))
                        else:
                            pygame.draw.circle(screen, getRarityColor(item.weapon_obj.rarity), rect.center, 14)
                            
                        if rect.collidepoint(mPos): 
                            hoveredSlotInfo = {"source": "PLAYER", "idx": i, "item": item}
                            pygame.draw.rect(screen, WHITE, rect, 2, border_radius=6)
                    else: 
                        pygame.draw.circle(screen, (60,60,60), rect.center, 14)

            draw_hover_button(screen, btn_prim_w, "裝備為主武器", GREEN, (50, 180, 50), BLACK)
            draw_hover_button(screen, btn_sec_w, "裝備為副武器", BLUE, (50, 100, 180), WHITE)
            draw_hover_button(screen, btn_wep_close, "X", (150, 50, 50), RED)
        # 游標跟隨拖動的物品
        if dragData != None:
            c = WHITE
            if dragData["item"].type == "WEAPON": c = getRarityColor(dragData["item"].weapon_obj.rarity)
            elif dragData["item"].type == "MED": c = hpColor
            elif dragData["item"].type == "SCRAP": c = SCRAP_COLOR
            elif dragData["item"].type == "KEY": c = YELLOW
            pygame.draw.circle(screen, c, (mx, my), 15)

        # 游標指著物品的提示   
        if hoveredSlotInfo != None and dragData == None:
            draw_item_tooltip(screen, hoveredSlotInfo["item"], mx, my)
            val = getSellValue(hoveredSlotInfo["item"])
            if val > 0:
                screen.blit(small_font.render("[X] 出售可得 " + str(val) + " 廢料", True, SCRAP_COLOR), (mx+25, my-25))
    # 遊戲主畫面
    elif gameState == "PLAYING" or gameState == "PAUSED" or gameState == "LEVEL_UP" or gameState == "DIED" or (gameState == "DIALOGUE" and dialogueSys.previous_state == "PLAYING"):
        if "bg" in images and images["bg"] != None:
            bg_img = images["bg"]
            bg_w = bg_img.get_width()
            bg_h = bg_img.get_height()
            
            start_x = - (int(camX) % bg_w)
            start_y = - (int(camY) % bg_h)
            
            x = start_x
            while x < WIDTH:
                y = start_y
                while y < HEIGHT:
                    screen.blit(bg_img, (x, y))
                    y += bg_h
                x += bg_w
        else: 
            screen.fill(BLACK)
            
        pygame.draw.rect(screen, RED, (-int(camX), -int(camY), mapWidth, mapHeight), 5)
        
        if extractionPt != None: extractionPt.draw(screen)
        if lostItem != None:
            lostItem.draw(screen)
            drawLostArrow(screen, camX, camY)
        # 畫箱子、道具、粒子、子彈、敵人、軌跡和傷害數字，圖層順序解釋:   
        for c in chests: c.draw(screen) # 箱子要先於敵人
        for it in items: it.draw(screen) # 道具要先於敵人
        for p in particles: p.draw(screen) # 爆炸粒子要先於敵人
        for b in bullets: b.draw(screen) # 玩家子彈要先於敵人
        for eb in enemy_bullets: eb.draw(screen) # 敵人子彈要先於敵人
        for e in enemies: e.draw(screen) # 怪物要先於玩家
        for t in trails: t.draw(screen) # 軌跡要先於玩家
        for dt in damage_texts: dt.draw(screen) # 傷害數字要先於玩家
        # BOSS 
        if isBossActive:
            boss.draw(screen)
            drawBossDirection(screen, boss, camX, camY)
        # 玩家    
        if gameState != "DIED":
            pw = None
            if gameState == "PLAYING": pw = player.weapons[player.current_weapon_idx]
            player.draw(screen, pw)
        #炸彈爆炸或受到重擊時會閃紅的畫面閃爍
        if screenFlashTimer > 0:
            flash_surface = pygame.Surface((WIDTH, HEIGHT))
            flash_surface.fill(WHITE)
            flash_surface.set_alpha(int((screenFlashTimer / 15) * 255))
            screen.blit(flash_surface, (0, 0))
        # BOSS警告    
        if bossArmyActive and (pygame.time.get_ticks() // 300) % 2 == 0:
            alarm = pygame.Surface((WIDTH, HEIGHT))
            alarm.fill(RED)
            alarm.set_alpha(80)
            screen.blit(alarm, (0, 0))
        # 打開箱子提示    
        if gameState == "PLAYING" and showInventory == False:
            for c in chests:
                if c.state == "CLOSED":
                    if math.hypot(player.x - c.x, player.y - c.y) < 70:
                        has_key = False
                        for item in player.inventory:
                            if item != None and item.type == "KEY": has_key = True
                                
                        if c.type == "NORMAL": t = "[F] 開啟木箱"
                        else:
                            if has_key: t = "[F] 消耗金鑰匙"
                            else: t = "需要金鑰匙"
                            
                        t_c = RED
                        if c.type == "NORMAL" or has_key: t_c = WHITE
                            
                        bg_r = pygame.Rect(c.x - camX - 40, c.y - camY - 80, font.size(t)[0]+20, 25) # 開啟木箱、需要鑰匙文字
                        popup = pygame.Surface((bg_r.width, bg_r.height), pygame.SRCALPHA)
                        pygame.draw.rect(popup, (20, 20, 25, 200), popup.get_rect(), border_radius=4)
                        screen.blit(popup, (bg_r.x, bg_r.y))
                        screen.blit(small_font.render(t, True, t_c), (bg_r.x+10, bg_r.y+3))
           
        drawMinimap(screen)
        
        # 經驗值、等級、血量、護盾、體力、能量、武器資訊、廢料和金鑰匙數量、技能狀態UI繪製
        pygame.draw.rect(screen, GRAY, (20, 20, 250, 15))
        expW = 250 * (player.exp / player.max_exp)
        pygame.draw.rect(screen, BLUE, (20, 20, expW, 15))
        screen.blit(font.render("等級: " + str(player.level), True, WHITE), (280, 15))

        pygame.draw.rect(screen, GRAY, (20, 45, 200, 15))
        hpW = 200 * (player.hp / player.max_hp)
        if hpW < 0: hpW = 0
        hc = RED
        if player.hp > 30: hc = GREEN
        pygame.draw.rect(screen, hc, (20, 45, hpW, 15))
        screen.blit(font.render("血量", True, WHITE), (230, 40))

        pygame.draw.rect(screen, GRAY, (20, 70, 200, 15))
        shW = 200 * (player.shield / player.max_shield)
        if shW < 0: shW = 0
        pygame.draw.rect(screen, (0, 150, 255), (20, 70, shW, 15))
        screen.blit(font.render("護盾", True, WHITE), (230, 65))

        pygame.draw.rect(screen, GRAY, (20, 95, 150, 10))
        stW = 150 * (player.stamina / player.max_stamina)
        pygame.draw.rect(screen, ORANGE, (20, 95, stW, 10))
        screen.blit(font.render("體力 (Q)", True, WHITE), (180, 87)) 
        
        pygame.draw.rect(screen, GRAY, (20, 115, 150, 10))
        enW = 150 * (player.energy / player.max_energy)
        pygame.draw.rect(screen, CYAN, (20, 115, enW, 10))
        screen.blit(font.render("能量", True, WHITE), (180, 107))

        if player.cheat_all_weapons == True:
            active_wep = player.weapons[player.current_weapon_idx]
            weapon_str = "【密技】全解鎖: " + active_wep.full_name + " (按E切換)"
            w_c = YELLOW
        else:
            w1 = player.weapons[0]
            w2 = player.weapons[1]
            active_w = player.current_weapon_idx
            
            w1_t = "主: " + w1.full_name
            if active_w == 0: w1_t += " <"
                
            w2_t = "副: " + w2.full_name
            if active_w == 1: w2_t += " <"
                
            weapon_str = w1_t + "  |  " + w2_t
            w_c = WHITE
            
        screen.blit(small_font.render(weapon_str, True, w_c), (20, 140))
        
        has_key_num = 0
        for i in player.inventory:
            if i != None and i.type == "KEY": has_key_num += i.count
        screen.blit(font.render("本局廢料: " + str(player.scrap) + " | 金鑰匙: " + str(has_key_num), True, YELLOW), (20, 165))

        if player.skill_cd > 0:
            skill_txt = font.render("技能: " + str(round(player.skill_cd / 60, 1)) + " 秒", True, GRAY)
        elif player.energy < player.skill_cost:
            skill_txt = font.render("技能: 能量不足", True, RED)
        else:
            skill_txt = font.render("技能就緒 (右鍵)", True, GREEN)
        screen.blit(skill_txt, (20, HEIGHT - 40))
        # 挑戰模式的彈藥和撤離點UI
        if gameMode == "CHALLENGE":
            ac = RED
            if player.ammo > 0: ac = WHITE
            screen.blit(font.render("彈藥: " + str(player.ammo) + "/" + str(player.base_max_ammo + player.mag_size_bonus), True, ac), (20, 195))
            if player.reload_timer > 0:
                pygame.draw.rect(screen, GRAY, (20, 225, 150, 10))
                rw = 150 * (1 - player.reload_timer / player.reload_duration)
                pygame.draw.rect(screen, YELLOW, (20, 225, rw, 10))
                screen.blit(small_font.render("換彈中...", True, YELLOW), (180, 220))
         # 撤離點和Boss的UI       
        if extractionPt != None:
            time_sec = extractionTimer // FPS
            mins = time_sec // 60
            secs = time_sec % 60
            
            tc = RED
            if time_sec > 30: tc = WHITE
                
            ms = str(mins)
            if len(ms) < 2: ms = "0" + ms
            ss = str(secs)
            if len(ss) < 2: ss = "0" + ss
            
            screen.blit(large_font.render("撤離倒數: " + ms + ":" + ss, True, tc), (WIDTH//2 - 120, 70))
            if extractProgress > 0:
                pygame.draw.rect(screen, GRAY, (WIDTH//2 - 100, 110, 200, 15))
                pygame.draw.rect(screen, GREEN, (WIDTH//2 - 100, 110, 200 * (extractProgress / 120), 15))
        # Boss相關UI    
        if isBossActive:
            drawBossHealth(screen, boss)
            if boss.state == "ENTRANCE":
                entrance_text = font.render(boss.get_intro_title(), True, YELLOW)
                screen.blit(entrance_text, (WIDTH//2 - entrance_text.get_width()//2, HEIGHT//2 - 200))
            else:
                state_message, state_color = boss.get_state_message()
                state_txt = font.render(state_message, True, state_color)
                screen.blit(state_txt, (WIDTH//2 - state_txt.get_width()//2, HEIGHT - 90))
        # 無敵模式提示
        if player.god_mode:
            screen.blit(font.render("{{{無敵模式啟用}}}", True, YELLOW), (WIDTH//2 - 80, 20))
        # 根據遊戲狀態顯示不同的界面元素
        if gameState == "PLAYING":
            drawTaskPanel(screen, taskSystem, WIDTH - 190, 160, True)
        else:
            drawUpgradeSummary(screen, WIDTH - 260, HEIGHT - 300, 5)
            drawTaskPanel(screen, taskSystem, 20, HEIGHT - 220, False)
        # 背包界面
        if showInventory == True:
            screen.blit(dim_surface, (0, 0))
            inv_rect = pygame.Rect(WIDTH//2 - 190, HEIGHT//2 - 100, 380, 300)
            draw_ui_panel(screen, inv_rect, "背包 (INVENTORY)", YELLOW)
            hi = drawPlayerInvGrid(screen, WIDTH//2 - 170, HEIGHT//2 - 40, mx, my, True)
            
            if dragData != None:
                c = WHITE
                if dragData["item"].type == "WEAPON": c = getRarityColor(dragData["item"].weapon_obj.rarity)
                elif dragData["item"].type == "MED": c = hpColor
                elif dragData["item"].type == "SCRAP": c = SCRAP_COLOR
                elif dragData["item"].type == "KEY": c = YELLOW
                pygame.draw.circle(screen, c, (mx, my), 15)
            elif hi != None:
                draw_item_tooltip(screen, hi["item"], mx, my)
                hoveredSlotInfo = hi
            
            val = 0
            if hoveredSlotInfo != None: val = getSellValue(hoveredSlotInfo["item"])
            
            hint = "左鍵拖曳 / 右鍵裝備使用 / 拖出丟棄"
            if val > 0: hint += " | [X] 出售得 " + str(val) + " 廢料"
            screen.blit(small_font.render(hint, True, GRAY), (WIDTH//2 - 210, HEIGHT//2 + 215))
    # 升級選單、死亡畫面、對話框等
    if gameState == "MENU":
        screen.fill(BLACK)
        for i in range(100):
            rx = (i * 37) % WIDTH
            ry = (i * 23) % HEIGHT
            brightness = int(100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i))
            pygame.draw.circle(screen, (brightness, brightness, brightness), (rx, ry), 1)
        
        # 升級選單、死亡畫面、對話框等
    if gameState == "MENU":
        screen.fill(BLACK)
        for i in range(100):
            rx = (i * 37) % WIDTH
            ry = (i * 23) % HEIGHT
            brightness = int(100 + 50 * math.sin(pygame.time.get_ticks() * 0.001 + i))
            pygame.draw.circle(screen, (brightness, brightness, brightness), (rx, ry), 1)
        
        #遊戲名稱標題
        title = large_font.render("末日肉鴿生存", True, BLUE)
        title_x = WIDTH//2 - title.get_width()//2
        title_y = HEIGHT//2 - 120
        screen.blit(title, (title_x, title_y))

        # 大標題置中
        title = large_font.render("末日肉鴿生存", True, BLUE)
        title_x = WIDTH//2 - title.get_width()//2
        title_y = HEIGHT//2 - 120
        screen.blit(title, (title_x, title_y))
        
        # 副標題動態置中
        subtitle = font.render("末日Roguelike生存", True, WHITE)
        subtitle_x = WIDTH//2 - subtitle.get_width()//2
        subtitle_y = HEIGHT//2 - 50
        screen.blit(subtitle, (subtitle_x, subtitle_y))

        draw_hover_button(screen, start_button, "開始遊戲", (50, 150, 50), (100, 200, 100))
        # 按鈕名稱
        draw_hover_button(screen, changelog_button, "遊戲指南", (50, 100, 150), BLUE)
        draw_hover_button(screen, exit_button, "退出遊戲", (150, 50, 50), RED)
            
        # 呼叫指南函式
        if showChangelog:
            drawGuidePopup(screen)

    # 難易度選單
    elif gameState == "DIFFICULTY":
        screen.fill(BLACK)
        screen.blit(large_font.render("選擇難易度", True, YELLOW), (WIDTH//2 - 100, HEIGHT//2 - 200))
        
        n_hover = normal_button.collidepoint(mPos)
        c_hover = challenge_button.collidepoint(mPos)
        
        if n_hover: pygame.draw.rect(screen, (55, 125, 185), normal_button, border_radius=10)
        else: pygame.draw.rect(screen, (30, 70, 115), normal_button, border_radius=10)
            
        if n_hover: pygame.draw.rect(screen, YELLOW, normal_button, 4, border_radius=10)
        else: pygame.draw.rect(screen, WHITE, normal_button, 3, border_radius=10)
            
        if c_hover: pygame.draw.rect(screen, (190, 55, 70), challenge_button, border_radius=10)
        else: pygame.draw.rect(screen, (115, 35, 50), challenge_button, border_radius=10)
            
        if c_hover: pygame.draw.rect(screen, YELLOW, challenge_button, 4, border_radius=10)
        else: pygame.draw.rect(screen, WHITE, challenge_button, 3, border_radius=10)

        # 普通難度排版
        screen.blit(large_font.render("普通", True, WHITE), (normal_button.centerx - 40, normal_button.y + 28)) 
        screen.blit(small_font.render("標準敵人強度與數量", True, WHITE), (normal_button.centerx - 80, normal_button.y + 88))
        
        nl = ["基礎倍率:1.0x", "無需換彈", "輕鬆農怪"]
        i = 0
        for line in nl:
            screen.blit(small_font.render(line, True, (210, 225, 240)), (normal_button.x + 35, normal_button.y + 132 + i * 28))
            i += 1
            
        # 挑戰難度排版
        screen.blit(large_font.render("挑戰", True, WHITE), (challenge_button.centerx - 40, challenge_button.y + 28))
        screen.blit(small_font.render("敵人 1.75 倍，速度加成", True, WHITE), (challenge_button.centerx - 90, challenge_button.y + 88))
        
        cl = ["難度倍率:1.75x", "啟動換彈懲罰機制", "解鎖專屬彈匣卡牌"]
        i = 0
        for line in cl:
            screen.blit(small_font.render(line, True, (255, 220, 220)), (challenge_button.x + 35, challenge_button.y + 132 + i * 28))
            i += 1

        draw_hover_button(screen, difficulty_back_button, "返回", (50, 100, 150), BLUE)
    # 升級選單、死亡畫面、暫停選單、對話框等
    elif gameState == "PAUSED":
        screen.blit(dim_surface, (0, 0))
        screen.blit(large_font.render("暫停中", True, YELLOW), (WIDTH//2 - 60, HEIGHT//2 - 100))
        draw_hover_button(screen, pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 10, 220, 50), "繼續遊戲", (50, 100, 150), BLUE)
        draw_hover_button(screen, pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 10, 220, 50), "回到選單", (50, 100, 150), BLUE)
        draw_hover_button(screen, pygame.Rect(WIDTH//2 - 240, HEIGHT//2 + 80, 220, 50), "放棄重製(回地堡)", (50, 150, 50), GREEN)
        draw_hover_button(screen, pygame.Rect(WIDTH//2 + 20, HEIGHT//2 + 80, 220, 50), "退出遊戲", (150, 50, 50), RED)
        drawPauseUpgradeLog(screen)
    # 升級選單的畫面
    elif gameState == "LEVEL_UP":
        screen.blit(dim_surface, (0, 0)) 
        screen.blit(large_font.render("升級！選擇一項強化", True, YELLOW), (WIDTH//2 - 180, 100))
        
        i = 0
        for card in cards:
            if i >= len(currentUpgradeChoices):
                i += 1
                continue
                
            upgrade = upgradeOptions[currentUpgradeChoices[i]]
            
            is_selected = False
            if selectedUpgradePosition == i: is_selected = True
                
            base_color = CARD_COLOR
            if "type" in upgrade and upgrade["type"] in cardTypeColors:
                base_color = cardTypeColors[upgrade["type"]]
                
            # 顏色計算 為了了讓升級選項的顏色在被選取或滑鼠懸停時能夠變亮一些
            r = base_color[0] + 35
            if r > 255: r = 255
            g = base_color[1] + 35
            if g > 255: g = 255
            b = base_color[2] + 35
            if b > 255: b = 255
            hover_color = (r, g, b)
            
            r2 = base_color[0] + 65
            if r2 > 255: r2 = 255
            g2 = base_color[1] + 65
            if g2 > 255: g2 = 255
            b2 = base_color[2] + 65
            if b2 > 255: b2 = 255
            sel_color = (r2, g2, b2)
            
            color = base_color
            if is_selected: color = sel_color
            elif card.collidepoint(mPos): color = hover_color
            
            pygame.draw.rect(screen, color, card, border_radius=10)
            if is_selected: pygame.draw.rect(screen, YELLOW, card, 6, border_radius=10) 
            else: pygame.draw.rect(screen, WHITE, card, 3, border_radius=10)
            
            type_label = ""
            if "type" in upgrade and upgrade["type"] in cardTypeLabels:
                type_label = cardTypeLabels[upgrade["type"]]
                
            if type_label != "":
                lbl_bg = pygame.Rect(card.centerx - 42, card.y + 18, 84, 28)
                pygame.draw.rect(screen, (20, 20, 28), lbl_bg, border_radius=8)
                pygame.draw.rect(screen, WHITE, lbl_bg, 1, border_radius=8)
                screen.blit(small_font.render(type_label, True, WHITE), (lbl_bg.centerx - 18, lbl_bg.centery - 10))
            
            screen.blit(font.render(upgrade["title"], True, WHITE), (card.centerx - font.size(upgrade["title"])[0]//2, card.y + 65))
            screen.blit(font.render(upgrade["desc"][0], True, YELLOW), (card.centerx - font.size(upgrade["desc"][0])[0]//2, card.y + 125))
            screen.blit(font.render(upgrade["desc"][1], True, YELLOW), (card.centerx - font.size(upgrade["desc"][1])[0]//2, card.y + 165))
            i += 1
            
        ready = False
        if selectedUpgradePosition != None: ready = True
            
        btn_col = GRAY
        if ready: btn_col = GREEN
            
        hb_col = GRAY
        if ready: hb_col = (50, 180, 50)
        draw_hover_button(screen, confirm_upgrade_button, "確認選擇", btn_col, hb_col)

    elif gameState == "DIED":
        screen.blit(dim_surface, (0, 0))
        screen.blit(large_font.render("你 已 陣 亡", True, RED), (WIDTH//2 - 100, HEIGHT//2 - 100))
        screen.blit(font.render("所有卡牌、物資與裝備已遺落在戰場。", True, WHITE), (WIDTH//2 - 200, HEIGHT//2 - 20))
        screen.blit(font.render("按 [R] 在地堡重生，重返戰場奪回一切！", True, YELLOW), (WIDTH//2 - 220, HEIGHT//2 + 20))

    if gameState == "DIALOGUE":
        darken = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        darken.fill((0, 0, 0, 100)) 
        screen.blit(darken, (0, 0))
        draw_dialogue_box(screen)
    
    # 畫準心 (滑鼠游標)
    if "crosshair" in images and images["crosshair"] != None:
        crosshair_img = images["crosshair"]
        cursor_rect = crosshair_img.get_rect(center=mPos)
        screen.blit(crosshair_img, cursor_rect)
    else:
        pygame.draw.line(screen, WHITE, (mx - 12, my), (mx - 4, my), 2)
        pygame.draw.line(screen, WHITE, (mx + 4, my), (mx + 12, my), 2)
        pygame.draw.line(screen, WHITE, (mx, my - 12), (mx, my - 4), 2)
        pygame.draw.line(screen, WHITE, (mx, my + 4), (mx, my + 12), 2)
        pygame.draw.circle(screen, RED, (mx +1 , my +1), 3)

    # 最終縮放跟 Letterboxing (黑邊置中)
    win_w = screenReal.get_width()
    win_h = screenReal.get_height()
    
    s_x = win_w / window_width
    s_y = win_h / window_height
    if s_x < s_y: scaleFactor = s_x
    else: scaleFactor = s_y
        
    new_w = int(window_width * scaleFactor)
    new_h = int(window_height * scaleFactor)
       
    offsetX = (win_w - new_w) // 2
    offsetY = (win_h - new_h) // 2

    scaled_surf = pygame.transform.scale(screen, (new_w, new_h))
    screenReal.fill((8, 10, 15)) 
    screenReal.blit(scaled_surf, (offsetX, offsetY))
    
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()