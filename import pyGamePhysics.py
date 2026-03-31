import pygame
import random
import math

pygame.init()

WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fancy Star & Circle Playground")

clock = pygame.time.Clock()
particles = []

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 6)
        
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.life = random.randint(40, 80)
        self.size = random.randint(4, 8) # 크기를 조금 더 키웠습니다.
        
        # 0은 원, 1은 별
        self.shape_type = random.choice(['circle', 'star'])
        
        self.color = (
            random.randint(150, 255),
            random.randint(100, 255),
            random.randint(150, 255)
        )

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08  # 중력 효과
        self.life -= 1

    def draw_star(self, surf, color, pos, size):
        """별 모양을 그리는 헬퍼 함수"""
        points = []
        n = 5  # 꼭짓점 개수
        for i in range(n * 2):
            # 바깥쪽 점과 안쪽 점을 번갈아가며 계산
            radius = size if i % 2 == 0 else size // 2
            angle = i * math.pi / n - math.pi / 2
            px = pos[0] + math.cos(angle) * radius
            py = pos[1] + math.sin(angle) * radius
            points.append((px, py))
        pygame.draw.polygon(surf, color, points)

    def draw(self, surf):
        if self.life > 0:
            if self.shape_type == 'circle':
                pygame.draw.circle(
                    surf,
                    self.color,
                    (int(self.x), int(self.y)),
                    self.size
                )
            else:
                self.draw_star(surf, self.color, (self.x, self.y), self.size * 1.5)

    def alive(self):
        return self.life > 0

def draw_background(surface, t):
    for y in range(0, HEIGHT, 2): # 성능을 위해 간격을 2로 조정
        c = int(40 + 30 * math.sin(y * 0.01 + t))
        color = (10, c, 50 + c//2)
        pygame.draw.line(surface, color, (0, y), (WIDTH, y), 2)

running = True
time_val = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    mouse = pygame.mouse.get_pos()
    buttons = pygame.mouse.get_pressed()

    if buttons[0]:
        for _ in range(8):
            particles.append(Particle(mouse[0], mouse[1]))

    time_val += 0.03
    draw_background(screen, time_val)

    for p in particles:
        p.update()
        p.draw(screen)

    particles = [p for p in particles if p.alive()]

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
