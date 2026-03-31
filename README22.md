[import_pygame.py](https://github.com/user-attachments/files/26044867/import_pygame.py)
import pygame
import sys
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Apple vs Human Game 🍎🧍‍♂️")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

clock = pygame.time.Clock()
running = True
game_over = False

# 폰트
font = pygame.font.SysFont(None, 30)
big_font = pygame.font.SysFont(None, 60)

# 🍎 사과 그리기
def draw_apple(screen, x, y):
    pygame.draw.circle(screen, (255, 0, 0), (x, y), 40)
    pygame.draw.circle(screen, (200, 0, 0), (x - 10, y - 10), 30)
    pygame.draw.rect(screen, (101, 67, 33), (x - 5, y - 55, 10, 20))
    pygame.draw.ellipse(screen, (0, 200, 0), (x + 5, y - 55, 25, 15))

# 🧍‍♂️ 사람 적 그리기
def draw_human(screen, x, y):
    # 머리
    pygame.draw.circle(screen, (255, 220, 177), (x, y - 40), 15)
    # 몸통
    pygame.draw.line(screen, (0, 0, 0), (x, y - 25), (x, y + 20), 3)
    # 팔
    pygame.draw.line(screen, (0, 0, 0), (x - 20, y - 10), (x + 20, y - 10), 3)
    # 다리
    pygame.draw.line(screen, (0, 0, 0), (x, y + 20), (x - 15, y + 40), 3)
    pygame.draw.line(screen, (0, 0, 0), (x, y + 20), (x + 15, y + 40), 3)

# 초기화 함수
def reset_game():
    return 400, 300, 100, 100, False

# 초기값
x, y, enemy_x, enemy_y, game_over = reset_game()

speed = 5
radius = 40
enemy_speed = 2

# 버튼
button_rect = pygame.Rect(300, 350, 200, 60)

while running:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_over and button_rect.collidepoint(event.pos):
                x, y, enemy_x, enemy_y, game_over = reset_game()

    if not game_over:
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_w]:
            y -= speed
        if keys[pygame.K_s]:
            y += speed
        if keys[pygame.K_a]:
            x -= speed
        if keys[pygame.K_d]:
            x += speed

        # 적 따라오기 (사람)
        if x > enemy_x:
            enemy_x += enemy_speed
        if x < enemy_x:
            enemy_x -= enemy_speed
        if y > enemy_y:
            enemy_y += enemy_speed
        if y < enemy_y:
            enemy_y -= enemy_speed

        # 충돌 체크 (거리 기준)
        distance = math.sqrt((x - enemy_x)**2 + (y - enemy_y)**2)
        if distance < radius + 30:  # 30 = 사람 크기 반 정도
            game_over = True

    screen.fill(WHITE)

    # 🍎 사과 (플레이어)
    draw_apple(screen, x, y)

    # 🧍‍♂️ 사람 적
    draw_human(screen, enemy_x, enemy_y)

    # FPS 표시
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, BLACK)
    screen.blit(fps_text, (10, 10))

    # 게임오버 UI
    if game_over:
        text = big_font.render("GAME OVER", True, (255, 0, 0))
        screen.blit(text, (250, 250))

        # RESTART 버튼
        pygame.draw.rect(screen, GRAY, button_rect)
        btn_text = font.render("RESTART", True, BLACK)
        screen.blit(btn_text, (button_rect.x + 50, button_rect.y + 15))

    pygame.display.flip()
    clock.tick(75)

pygame.quit()
sys.exit()
