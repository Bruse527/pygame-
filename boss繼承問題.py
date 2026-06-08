class Boss:
    def __init__(self, name, max_hp_base, speed, size, spawn_level):
        self.name = name
        self.spawn_level = spawn_level
        difficulty = 1.75 if game_mode == "CHALLENGE" else 1.0
        
        # 基礎屬性
        self.max_hp = int((max_hp_base + spawn_level * 200) * difficulty)
        self.hp = self.max_hp
        self.speed = speed * difficulty
        self.size = size
        self.pos = pygame.math.Vector2(0, 0)
        self.rect = pygame.Rect(0, 0, size, size)
        
        # 狀態計時器
        self.state = "ENTRANCE"
        self.state_timer = 0
        self.hit_timer = 0
        self.frost_timer = 0
        self.burn_timer = 0
        self.defeat_timer = 0
        self.flip_x = False

    def handle_status_effects(self):
        # 統一處理受傷閃爍、冰凍減速、燃燒扣血
        if self.hit_timer > 0: self.hit_timer -= 1
        if self.frost_timer > 0: self.frost_timer -= 1
        if self.burn_timer > 0:
            self.burn_timer -= 1
            if self.burn_timer % 15 == 0: 
                self.hp -= 10
                particles.append(Particle(self.pos.x, self.pos.y, ORANGE))
        return 0.5 if self.frost_timer > 0 else 1.0 # 返回速度倍率

    def update_basic(self):
        #　更新計時器與坐標同步
        self.state_timer += 1
        self.pos.x = max(self.size, min(MAP_WIDTH - self.size, self.pos.x))
        self.pos.y = max(self.size, min(MAP_HEIGHT - self.size, self.pos.y))
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def get_draw_pos(self):
        # 自動計算相機偏移後的繪製坐標
        return round(self.pos.x - camera_x), round(self.pos.y - camera_y)

    def can_take_damage(self):
        return self.state not in ("ENTRANCE", "DEFEAT")
    
    