


import pygame
import random
import sys
import math

pygame.init()

# --- 효과음 설정 ---
try:
    shoot_sound = pygame.mixer.Sound("ScreenRecording_04-21-2026-11.mp3")  # ← 여기에 나중에 경로 넣기
    shoot_sound.set_volume(0.5)
except Exception:
    shoot_sound = None
    print("발사 사운드 로드 실패")

# --- 화면 및 기본 설정 ---
FPS = 60

# 색상
WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
GRAY    = (20,  20,  40)
BLUE    = (50,  150, 255)
RED     = (220, 50,  50)
YELLOW  = (240, 220, 0)
GREEN   = (50,  220, 80)
ORANGE  = (255, 140, 0)
PURPLE  = (180, 50,  255)
CYAN    = (0,   255, 255)

# 전체화면 모드 설정 및 동적 해상도 가져오기
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
WIDTH, HEIGHT = screen.get_size()

pygame.display.set_caption("Space Shooter: Ambient BGM Update")
clock = pygame.time.Clock()

def get_korean_font(size):
    sys_fonts = pygame.font.get_fonts()
    korean_candidates = ['malgungothic', 'gulim', 'batang', 'dotum', 'applegothic', 'applemyungjo', 'nanumgothic', 'notosanscjk', 'notosanskr']
    
    for font_name in korean_candidates:
        if font_name in sys_fonts:
            return pygame.font.SysFont(font_name, size)
            
    return pygame.font.SysFont(None, size)

font = get_korean_font(24)
font_big = get_korean_font(50)

# --- 배경음악 설정 ---
bgm_paths = ['freemusicforvideo-space-ambient-446647.mp3', 'bgm.mp3']
bgm_loaded = False
for path in bgm_paths:
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(0.5) 
        pygame.mixer.music.play(-1)        
        bgm_loaded = True
        print(f"배경음악 로드 성공: {path}")
        break
    except Exception:
        continue

if not bgm_loaded:
    print("배경음악 로드 실패: 게임 폴더에 mp3 파일이 제대로 있는지 확인해 주세요.")


# --- 이미지 로드 및 전처리 ---
IMAGES = {}

def load_and_prep_image(paths, size, rotate_to_right=False):
    if isinstance(paths, str):
        paths = [paths]
        
    for path in paths:
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, size)
            
            for x in range(img.get_width()):
                for y in range(img.get_height()):
                    r, g, b, a = img.get_at((x, y))
                    if r > 230 and g > 230 and b > 230:
                        img.set_at((x, y), (255, 255, 255, 0))
            
            if rotate_to_right:
                img = pygame.transform.rotate(img, -90)
            return img
        except Exception:
            continue
            
    print(f"이미지 로드 실패: {paths}")
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(RED) 
    return surf

IMAGES['player'] = load_and_prep_image(['a645405b-af50-4ea5-85e2-cbff43f9a1dc.jpg', 'player.jpg'], (50, 50), True)
IMAGES['kamikaze'] = load_and_prep_image(['unnamed.png', 'kamikaze.png'], (40, 40), True)
IMAGES['shooter'] = load_and_prep_image(['5f8adaeb-f933-4906-b008-8c79c9a1778b.jpg', 'shooter.jpg'], (45, 45), True)
IMAGES['boss_main'] = load_and_prep_image(['cbaad650-4dd3-48fa-b635-b7249d389353.jpg', 'boss.jpg', 'boss.jpeg'], (140, 140), False)
IMAGES['boss_split'] = load_and_prep_image(['cbaad650-4dd3-48fa-b635-b7249d389353.jpg', 'boss.jpg', 'boss.jpeg'], (80, 80), False)


# --- 클래스 정의 ---

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 100
        self.speed = 5
        self.radius = 20
        self.angle = 0
        self.lives = 5
        self.invincible = 0
        self.weapon_type = 1 
        self.image = IMAGES['player']
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and self.x - self.radius > 0:      self.x -= self.speed
        if keys[pygame.K_d] and self.x + self.radius < WIDTH:  self.x += self.speed
        if keys[pygame.K_w] and self.y - self.radius > 0:      self.y -= self.speed
        if keys[pygame.K_s] and self.y + self.radius < HEIGHT: self.y += self.speed

        mx, my = pygame.mouse.get_pos()
        dx, dy = mx - self.x, my - self.y
        self.angle = math.atan2(dy, dx)
        
        if self.invincible > 0:
            self.invincible -= 1

    def draw(self, surface):
        if self.invincible % 10 > 5: return 
        rotated_image = pygame.transform.rotate(self.image, math.degrees(-self.angle))
        rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_image, rect.topleft)

class Bullet:
    def __init__(self, x, y, angle, b_type, is_enemy=False, speed_mult=1.0):
        self.x = x; self.y = y; self.angle = angle; self.type = b_type
        self.is_enemy = is_enemy; self.active = True; self.fuse = 0 
        
        if is_enemy:
            self.speed = 5 * speed_mult; self.radius = 5; self.color = RED
        elif self.type == 1: 
            self.speed = 12; self.radius = 4; self.color = YELLOW
        elif self.type == 2: 
            self.speed = 8; self.radius = 8; self.color = ORANGE
        elif self.type == 3: 
            self.speed = 10; self.radius = 6; self.color = PURPLE
        elif self.type == 4:
            self.speed = 15; self.radius = 10; self.color = GREEN; self.fuse = 25 

        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed

    def update(self):
        self.x += self.vx; self.y += self.vy
        if self.x < -50 or self.x > WIDTH + 50 or self.y < -50 or self.y > HEIGHT + 50:
            self.active = False

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        if self.type == 4:
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius - 3)

class Enemy:
    def __init__(self, e_type, spawn_x=None, spawn_y=None):
        self.type = e_type
        if spawn_x is not None and spawn_y is not None:
            self.x, self.y = spawn_x, spawn_y
        else:
            side = random.randint(1, 4)
            if side == 1:   self.x, self.y = random.randint(0, WIDTH), -20
            elif side == 2: self.x, self.y = random.randint(0, WIDTH), HEIGHT + 20
            elif side == 3: self.x, self.y = -20, random.randint(0, HEIGHT)
            else:           self.x, self.y = WIDTH + 20, random.randint(0, HEIGHT)
        
        self.radius = 15; self.active = True; self.is_ally = False; self.angle = 0 
        
        if self.type == 'kamikaze':
            self.speed = random.uniform(2.0, 3.5)
            self.image = IMAGES['kamikaze']
        elif self.type == 'shooter':
            self.speed = 1.5
            self.image = IMAGES['shooter']
            self.shoot_timer = random.randint(60, 120)

    def update(self, player, enemies, bullets, bosses, emp_active=False):
        if not self.active or emp_active: return 
        
        target_x, target_y = player.x, player.y
        if self.is_ally:
            if bosses:
                target_boss = min(bosses, key=lambda b: math.hypot(b.x - self.x, b.y - self.y))
                target_x, target_y = target_boss.x, target_boss.y
            else:
                nearest_dist = float('inf')
                target_enemy = None
                for e in enemies:
                    if not e.is_ally and e != self:
                        dist = math.hypot(e.x - self.x, e.y - self.y)
                        if dist < nearest_dist:
                            nearest_dist = dist; target_enemy = e
                if target_enemy: target_x, target_y = target_enemy.x, target_enemy.y
                else: target_y -= 10 
        
        dx, dy = target_x - self.x, target_y - self.y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            self.angle = math.atan2(dy, dx)
            if self.type == 'kamikaze' or self.is_ally:
                self.x += (dx / dist) * self.speed
                self.y += (dy / dist) * self.speed
            elif self.type == 'shooter':
                if dist > 250: 
                    self.x += (dx / dist) * self.speed
                    self.y += (dy / dist) * self.speed
                if not self.is_ally:
                    self.shoot_timer -= 1
                    if self.shoot_timer <= 0:
                        angle = math.atan2(dy, dx)
                        bullets.append(Bullet(self.x, self.y, angle, 0, is_enemy=True))
                        self.shoot_timer = random.randint(80, 150)

    def draw(self, surface, emp_active=False):
        if self.is_ally: pygame.draw.circle(surface, GREEN, (int(self.x), int(self.y)), self.radius + 10, 4)
        rotated_image = pygame.transform.rotate(self.image, math.degrees(-self.angle))
        rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_image, rect.topleft)
        if emp_active: pygame.draw.circle(surface, CYAN, (int(self.x), int(self.y)), self.radius + 12, 2)

class Explosion:
    def __init__(self, x, y, max_rad=80, color=ORANGE, growth_rate=5):
        self.x = x; self.y = y; self.radius = 5
        self.max_radius = max_rad; self.active = True
        self.color = color; self.growth_rate = growth_rate

    def update(self):
        self.radius += self.growth_rate
        if self.radius >= self.max_radius: self.active = False

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.radius), max(1, int(self.max_radius - self.radius)//3))

class AoeWarning:
    def __init__(self, x, y, is_fast=False):
        self.x = x; self.y = y
        self.timer = 60 if is_fast else 90 
        self.max_timer = self.timer
        self.radius = 80; self.active = True

    def update(self):
        self.timer -= 1
        if self.timer <= 0: self.active = False

    def draw(self, surface):
        if self.timer % 10 > 3:
            pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius, 2)
            pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), int(self.radius * (self.timer/self.max_timer)), 1)

class Boss:
    def __init__(self, x=WIDTH//2, y=150, is_split=False):
        self.x = x; self.y = y; self.is_split = is_split 
        self.radius = 40 if is_split else 70
        self.max_hp = 1000
        self.hp = 500 if is_split else 1000
        self.active = True
        self.minion_spawn_timer = 180 
        self.weakpoint_angle = random.uniform(0, math.pi*2)
        self.weakpoint_dist = 50 if is_split else 80
        self.weakpoint_radius = 12 if is_split else 15
        self.wx, self.wy = self.x, self.y
        self.state_timer = 120; self.pattern = 0
        self.laser_angle = 0; self.laser_active = 0
        self.enraged = False; self.enrage_timer = 0
        self.image = IMAGES['boss_split'] if self.is_split else IMAGES['boss_main']
        self.draw_angle = 0 

    def take_damage(self, amount, enemies, explosions):
        self.hp -= amount
        if not self.is_split and self.hp <= 200 and not self.enraged: 
            self.enraged = True; self.enrage_timer = 60      
            explosions.append(Explosion(self.x, self.y, max_rad=800, color=RED, growth_rate=40))
            for _ in range(20):
                e_type = 'kamikaze' if random.random() < 0.7 else 'shooter'
                spawn_x = max(20, min(WIDTH - 20, self.x + random.randint(-400, 400)))
                spawn_y = max(20, min(HEIGHT - 20, self.y + random.randint(-400, 400)))
                enemies.append(Enemy(e_type, spawn_x=spawn_x, spawn_y=spawn_y))

    def update(self, player, bullets, warnings, enemies):
        if not self.active: return
        
        is_fast = self.enraged and not self.is_split
        self.draw_angle = (self.draw_angle + (2 if is_fast else 1)) % 360 
        
        self.minion_spawn_timer -= 1
        if self.minion_spawn_timer <= 0:
            for _ in range(2):
                offset_x = random.randint(-40, 40)
                offset_y = random.randint(-40, 40)
                enemies.append(Enemy('kamikaze', spawn_x=self.x + offset_x, spawn_y=self.y + offset_y))
            self.minion_spawn_timer = 144 if is_fast else 180

        self.state_timer -= 1
        
        if self.pattern == 0: 
            move_speed = 2.0 if is_fast else 1.5
            self.x += math.sin(pygame.time.get_ticks() / 1000.0 + self.y) * move_speed
            if self.state_timer <= 0:
                self.pattern = random.randint(1, 3)
                if self.pattern != 3: self.state_timer = 144 if is_fast else 180
                else: self.state_timer = 264 if is_fast else 330
                
        elif self.pattern == 1: 
            shoot_interval = 12 if is_fast else 15
            if self.state_timer % shoot_interval == 0:
                offset = (self.state_timer % (shoot_interval * 2)) / 10.0
                num_bullets = 8 if self.is_split else 12
                for i in range(num_bullets):
                    angle = (i * math.pi * 2 / num_bullets) + offset
                    speed_mult = 1.0 if is_fast else 0.8
                    bullets.append(Bullet(self.x, self.y, angle, 0, is_enemy=True, speed_mult=speed_mult))
            if self.state_timer <= 0:
                self.pattern = 0; self.state_timer = 80 if is_fast else 100
                
        elif self.pattern == 2: 
            trigger_times = [120, 80, 40] if is_fast else [150, 100, 50]
            if self.state_timer in trigger_times: warnings.append(AoeWarning(player.x, player.y, is_fast)) 
            if self.state_timer <= 0:
                self.pattern = 0; self.state_timer = 80 if is_fast else 100
                
        elif self.pattern == 3: 
            charge_time = 168 if is_fast else 210
            fire_time = 24 if is_fast else 30
            
            if self.state_timer > charge_time:
                dx, dy = player.x - self.x, player.y - self.y
                self.laser_angle = math.atan2(dy, dx)
            elif self.state_timer == fire_time: self.laser_active = 30 
                
            if self.state_timer <= 0:
                self.pattern = 0; self.state_timer = 96 if is_fast else 120

        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(self.radius, min(HEIGHT - self.radius, self.y))

        self.weakpoint_angle += 0.03
        self.wx = self.x + math.cos(self.weakpoint_angle) * self.weakpoint_dist
        self.wy = self.y + math.sin(self.weakpoint_angle) * self.weakpoint_dist

        if self.laser_active > 0:
            self.laser_active -= 1
            if player.invincible <= 0:
                p_dx, p_dy = player.x - self.x, player.y - self.y
                if math.cos(self.laser_angle)*p_dx + math.sin(self.laser_angle)*p_dy > 0:
                    dist = abs(math.sin(self.laser_angle)*p_dx - math.cos(self.laser_angle)*p_dy)
                    laser_width = 15 if self.is_split else 20
                    if dist < laser_width: 
                        player.lives -= 1; player.invincible = 60

    def draw(self, surface, show_weakpoint):
        if self.enraged: pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius + 15, 3)
        if self.enrage_timer > 0:
            self.enrage_timer -= 1
            if self.enrage_timer % 10 < 5: pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.radius + (60 - self.enrage_timer) * 10, 5)

        rotated_image = pygame.transform.rotate(self.image, self.draw_angle)
        rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(rotated_image, rect.topleft)
        
        if show_weakpoint:
            pygame.draw.circle(surface, CYAN, (int(self.wx), int(self.wy)), self.weakpoint_radius)
            pygame.draw.circle(surface, WHITE, (int(self.wx), int(self.wy)), self.weakpoint_radius - 4)
            
        hp_ratio = self.hp / self.max_hp
        if self.is_split:
            pygame.draw.rect(surface, RED, (self.x - 40, self.y - self.radius - 20, 80, 8))
            pygame.draw.rect(surface, GREEN, (self.x - 40, self.y - self.radius - 20, 80 * hp_ratio, 8))
        else:
            bar_width = 260; bar_start_x = WIDTH//2 - (bar_width // 2)
            pygame.draw.rect(surface, RED, (bar_start_x, 30, bar_width, 20))
            bar_color = ORANGE if self.enraged else GREEN
            pygame.draw.rect(surface, bar_color, (bar_start_x, 30, bar_width * hp_ratio, 20))
            boss_hp_text = font.render("BOSS", True, WHITE)
            surface.blit(boss_hp_text, (WIDTH//2 - boss_hp_text.get_width()//2, 5))

        if self.pattern == 3:
            end_x = self.x + math.cos(self.laser_angle) * 1500
            end_y = self.y + math.sin(self.laser_angle) * 1500
            is_fast = self.enraged and not self.is_split
            charge_time = 168 if is_fast else 210
            fire_time = 24 if is_fast else 30
            
            if self.state_timer > charge_time: pygame.draw.line(surface, (255, 100, 100), (self.x, self.y), (end_x, end_y), 1)
            elif self.state_timer > fire_time:
                if self.state_timer % 10 < 5: pygame.draw.line(surface, RED, (self.x, self.y), (end_x, end_y), 3)
                else: pygame.draw.line(surface, YELLOW, (self.x, self.y), (end_x, end_y), 1)

        if self.laser_active > 0:
            end_x = self.x + math.cos(self.laser_angle) * 1500
            end_y = self.y + math.sin(self.laser_angle) * 1500
            w1 = 30 if self.is_split else 40
            w2 = 10 if self.is_split else 15
            pygame.draw.line(surface, PURPLE if self.is_split else RED, (self.x, self.y), (end_x, end_y), w1)
            pygame.draw.line(surface, WHITE, (self.x, self.y), (end_x, end_y), w2)

# --- 메인 루프 ---

def main():
    player = Player()
    bullets, enemies, explosions, warnings, bosses = [], [], [], [], []
    
    score, shoot_cd, spawn_timer = 0, 0, 0
    boss_spawned = False
    emp_timer, emp_cd = 0, 0
    weapon_4_unlocked = False; unlock_message_timer = 0
    
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 2)) for _ in range(100)]

    running = True
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
        lshift_pressed = keys[pygame.K_LSHIFT]
        space_pressed = keys[pygame.K_SPACE]
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                # 전체화면 종료를 위한 안전장치 추가 (ESC키)
                if event.key == pygame.K_ESCAPE: 
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_1: player.weapon_type = 1
                if event.key == pygame.K_2: player.weapon_type = 2
                if event.key == pygame.K_3: player.weapon_type = 3
                if event.key == pygame.K_4 and weapon_4_unlocked: player.weapon_type = 4
                if event.key == pygame.K_k: 
                    for boss in bosses:
                        if boss.active: boss.take_damage(int(boss.max_hp * 0.1), enemies, explosions)
                if event.key == pygame.K_j: player.lives = 5

        if score >= 150 and not boss_spawned:
            bosses.append(Boss()); boss_spawned = True; enemies.clear() 

        shoot_cd -= 1; emp_cd -= 1
        if emp_timer > 0: emp_timer -= 1
        if unlock_message_timer > 0: unlock_message_timer -= 1
        
        if space_pressed and emp_cd <= 0:
            emp_timer = 240; emp_cd = 600
            explosions.append(Explosion(player.x, player.y, max_rad=WIDTH*1.5, color=CYAN, growth_rate=30))

        if pygame.mouse.get_pressed()[0] and shoot_cd <= 0:
            bullets.append(Bullet(player.x, player.y, player.angle, player.weapon_type, is_enemy=False))
    
            if shoot_sound:
                shoot_sound.play()
    
            if player.weapon_type == 1: shoot_cd = 20
            elif player.weapon_type == 2: shoot_cd = 20
            elif player.weapon_type == 3: shoot_cd = 20
            elif player.weapon_type == 4: shoot_cd = 20

        if not bosses:
            spawn_timer -= 1
            if spawn_timer <= 0:
                e_type = 'kamikaze' if random.random() < 0.7 else 'shooter'
                if e_type == 'kamikaze':
                    for _ in range(2): enemies.append(Enemy('kamikaze'))
                else: enemies.append(Enemy('shooter'))
                spawn_timer = max(20, 60 - (score // 50)) 

        player.update()
        
        for b in bullets:
            b.update()
            if b.type == 4:
                b.fuse -= 1
                if b.fuse <= 0:
                    b.active = False
                    explosions.append(Explosion(b.x, b.y, max_rad=200, color=ORANGE, growth_rate=15))
                    
        for e in enemies: e.update(player, enemies, bullets, bosses, emp_active=(emp_timer > 0))
        for ex in explosions: ex.update()
        for boss in bosses: boss.update(player, bullets, warnings, enemies)
            
        for w in warnings:
            w.update()
            if not w.active:
                explosions.append(Explosion(w.x, w.y, max_rad=90, color=RED))
                if player.invincible <= 0 and math.hypot(w.x - player.x, w.y - player.y) < 90 + player.radius:
                    player.lives -= 1; player.invincible = 60

        bullets = [b for b in bullets if b.active]
        explosions = [ex for ex in explosions if ex.active]
        warnings = [w for w in warnings if w.active]

        for b in bullets:
            if not b.active: continue
            if b.is_enemy:
                if player.invincible <= 0 and math.hypot(b.x - player.x, b.y - player.y) < player.radius + b.radius:
                    player.lives -= 1; player.invincible = 60; b.active = False
            else:
                hit_something = False
                for boss in bosses:
                    if boss.active and lshift_pressed:
                        if math.hypot(b.x - boss.wx, b.y - boss.wy) < boss.weakpoint_radius + b.radius:
                            b.active = False; hit_something = True
                            if b.type == 4: dmg = 50; explosions.append(Explosion(b.x, b.y, max_rad=200, color=ORANGE, growth_rate=15))
                            elif b.type == 2: dmg = 20; explosions.append(Explosion(b.x, b.y, max_rad=40))
                            else: dmg = 10
                            boss.take_damage(dmg, enemies, explosions)
                            break
                if hit_something: continue
                
                for e in enemies:
                    if not e.active or e.is_ally: continue
                    if math.hypot(b.x - e.x, b.y - e.y) < e.radius + b.radius:
                        b.active = False
                        if b.type == 1: e.active = False; score += 10
                        elif b.type == 2: 
                            e.active = False; score += 10; explosions.append(Explosion(b.x, b.y))
                        elif b.type == 3: e.is_ally = True
                        elif b.type == 4: explosions.append(Explosion(b.x, b.y, max_rad=200, color=ORANGE, growth_rate=15))
                        break

        for boss in bosses:
            if boss.active:
                for e in enemies:
                    if e.active and e.is_ally:
                        if math.hypot(e.x - boss.x, e.y - boss.y) < e.radius + boss.radius:
                            e.active = False; explosions.append(Explosion(e.x, e.y, max_rad=60, color=ORANGE))
                            score += 30; boss.take_damage(50, enemies, explosions)

        for ex in explosions:
            if ex.color == RED and player.invincible <= 0: 
                if math.hypot(ex.x - player.x, ex.y - player.y) < ex.radius + player.radius:
                    player.lives -= 1; player.invincible = 60
            elif ex.color == ORANGE: 
                for e in enemies:
                    if e.active and not e.is_ally and math.hypot(ex.x - e.x, ex.y - e.y) < ex.radius + e.radius:
                        e.active = False; score += 15
                for boss in bosses:
                    if boss.active and math.hypot(ex.x - boss.x, ex.y - boss.y) < ex.radius + boss.radius:
                        boss.take_damage(2, enemies, explosions) 

        for i, e1 in enumerate(enemies):
            if e1.active and e1.is_ally:
                for j, e2 in enumerate(enemies):
                    if i != j and e2.active and not e2.is_ally:
                        if math.hypot(e1.x - e2.x, e1.y - e2.y) < e1.radius + e2.radius:
                            e1.active = False; e2.active = False
                            explosions.append(Explosion(e1.x, e1.y)); score += 20; break

        for e in enemies:
            if e.active and not e.is_ally and player.invincible <= 0:
                if math.hypot(e.x - player.x, e.y - player.y) < e.radius + player.radius:
                    player.lives -= 1; player.invincible = 60
                    e.active = False; explosions.append(Explosion(player.x, player.y))

        enemies = [e for e in enemies if e.active]

        new_bosses = []
        for boss in bosses:
            if boss.active:
                if not boss.is_split and boss.hp <= 10:
                    boss.active = False
                    explosions.append(Explosion(boss.x, boss.y, max_rad=400, color=PURPLE, growth_rate=20))
                    b1 = Boss(boss.x - 120, boss.y, is_split=True)
                    b2 = Boss(boss.x + 120, boss.y, is_split=True)
                    new_bosses.extend([b1, b2])
                    weapon_4_unlocked = True; unlock_message_timer = 240
                elif boss.hp <= 0:
                    boss.active = False; explosions.append(Explosion(boss.x, boss.y, max_rad=200))
                    score += 1000 if not boss.is_split else 500
                else: new_bosses.append(boss)
        bosses = new_bosses

        if player.lives <= 0: running = False

        screen.fill(GRAY)
        for s in stars: pygame.draw.circle(screen, WHITE, (s[0], s[1]), s[2])
        
        for w in warnings: w.draw(screen)
        for ex in explosions: ex.draw(screen)
        for boss in bosses: boss.draw(screen, lshift_pressed)
        for e in enemies: e.draw(screen, emp_active=(emp_timer > 0))
        for b in bullets: b.draw(screen)
        player.draw(screen)

        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Lives: {'♥ ' * player.lives}", True, RED), (10, 40))
        
        if emp_timer > 0: screen.blit(font.render("EMP ACTIVE!", True, CYAN), (10, 70))
            
        for boss in bosses:
             if boss.enraged and not boss.is_split:
                 enrage_msg = font.render("WARNING: BOSS ENRAGED!", True, RED)
                 screen.blit(enrage_msg, (WIDTH//2 - enrage_msg.get_width()//2, 60))
                 break
        
        if boss_spawned and not bosses:
            boss_defeat_msg = font_big.render("BOSS DEFEATED!", True, YELLOW)
            screen.blit(boss_defeat_msg, (WIDTH//2 - boss_defeat_msg.get_width()//2, HEIGHT//2 - 50))
            
        if bosses: screen.blit(font.render("HOLD [LSHIFT] to reveal weakpoint!", True, CYAN), (10, HEIGHT - 30))
            
        if unlock_message_timer > 0:
            msg = font_big.render("시스템: 4번 무기(미사일) 잠금 해제!", True, GREEN)
            pygame.draw.rect(screen, BLACK, (WIDTH//2 - msg.get_width()//2 - 20, HEIGHT//2 - 20, msg.get_width() + 40, msg.get_height() + 40))
            pygame.draw.rect(screen, GREEN, (WIDTH//2 - msg.get_width()//2 - 20, HEIGHT//2 - 20, msg.get_width() + 40, msg.get_height() + 40), 3)
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))

        ui_x_offset = WIDTH - 350
        weapon_names = {1: "1: Basic Gun", 2: "2: Launcher", 3: "3: Mind Control"}
        if weapon_4_unlocked: weapon_names[4] = "4: Missile (AoE)"
        
        weapon_text = font.render(weapon_names[player.weapon_type], True, BLUE)
        screen.blit(weapon_text, (ui_x_offset, 10))

        emp_text_str = "EMP [SPACE]: READY" if emp_cd <= 0 else f"EMP [SPACE]: CD {emp_cd // 60 + 1}s"
        emp_color = CYAN if emp_cd <= 0 else (150, 150, 150)
        emp_text = font.render(emp_text_str, True, emp_color)
        screen.blit(emp_text, (ui_x_offset, 40))

        pygame.display.flip()

    while True:
        screen.fill(BLACK)
        game_over_msg = font_big.render("GAME OVER", True, RED)
        screen.blit(game_over_msg, (WIDTH//2 - game_over_msg.get_width()//2, HEIGHT//2 - 100))
        score_msg = font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(score_msg, (WIDTH//2 - score_msg.get_width()//2, HEIGHT//2))
        restart_msg = font.render("Press 'R' to Restart, 'Q' or 'ESC' to Quit", True, YELLOW)
        screen.blit(restart_msg, (WIDTH//2 - restart_msg.get_width()//2, HEIGHT//2 + 60))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return main()
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()

