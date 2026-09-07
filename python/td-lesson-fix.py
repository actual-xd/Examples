import pygame
import math

pygame.init()
width = 800
yellow = (176, 163, 44)
height = 600
cell = 40
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("TDR")
clock = pygame.time.Clock()
green = (0, 100, 0)
black = (0, 0, 0)
fps = 60
red = (200, 0, 0)
blue = (0, 0, 200)
orange = (255, 229, 84)
tower_types = {"fast": {"name": "fast", "color": blue, "cost": 25, "damage": 10, "fire_rate": 20, "range": 150}}

lives = 4

wave_number = 0
wave_active = False
enemies_tospawn = 0
gold = 10000000000
spawn_timer = 0
placing = None

Towers = []
enemies = []
Projectiles = []

waypoints = [
    (-40, 260),
    (220, 260),
    (220, 100),
    (460, 100),
    (460, 420),
    (700, 420),
    (700, 180),
    (840, 180),
]

road_cells = set()


for x in range(0, 6):
    road_cells.add((x, 6))

for y in range(2, 7):
    road_cells.add((5, y))

for x in range(5, 12):
    road_cells.add((x, 2))

for r in range(2, 11):
    road_cells.add((11, r))

for c in range(11, 18):
    road_cells.add((c, 10))

for r in range(4, 11):
    road_cells.add((17, r))
for c in range(17, 21):
    road_cells.add((c, 4))


def draw_road(screen):
    for gx, gy in road_cells:
        rect = pygame.Rect(gx * cell, gy * cell, cell, cell)
        pygame.draw.rect(screen, yellow, rect)
        pygame.draw.rect(screen, black, rect, 1)


class Projectile:
    def __init__(self, x, y, damage, target):
        self.x = x
        self.y = y
        self.damage = damage
        self.target = target
        self.speed = 5
        self.alive = True

    def update(self):
        if not self.alive:
            return
        if not self.target.alive:
            self.alive = False
            return
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        dist = math.hypot(dx, dy)

        if dist < self.speed:
            self.target.hp -= self.damage
            if self.target.hp <= 0:
                self.target.alive = False

                global gold
                gold += self.target.money
            self.alive = False
        else:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

    def draw(self, screen):
        if self.alive:

            pygame.draw.circle(screen, orange, (int(self.x), int(self.y)), 4)


class Tower:
    def __init__(self, x, y, kind):
        self.x = x
        self.y = y
        self.cooldown = 0
        self.kind = kind
        self.stats = tower_types[kind]

    def update(self, enemies):
        if self.cooldown > 0:
            self.cooldown -= 1
            return None

        best_target = None
        best_dist = self.stats["range"]

        for e in enemies:
            if not e.alive:
                continue
            d = math.hypot((self.x * cell + cell // 2) - e.x, (self.y * cell + cell // 2) - e.y)
            if d < best_dist:
                best_target = e
                best_dist = d

        if best_target:
            self.cooldown = self.stats["fire_rate"]
            return Projectile(self.x * cell + cell // 2, self.y * cell + cell // 2, self.stats["damage"], best_target)
        return None

    def draw(self, screen):
        tower = pygame.Rect(self.x * cell + 3, self.y * cell + 3, cell - 6, cell - 6)
        pygame.draw.rect(screen, self.stats["color"], tower)


class enemy:
    def __init__(self, speed, hp, money):
        self.speed = speed
        self.hp = hp
        self.money = money
        self.max_hp = hp
        self.alive = True
        self.end = False
        self.x, self.y = waypoints[0]
        self.way_point = 0
        self.radius = cell // 2 - 1

    def update(self):
        if not self.alive or self.end:
            return

        if self.way_point >= len(waypoints):
            self.end = True
            self.alive = False
            return

        new_x, new_y = waypoints[self.way_point]
        d_x, d_y = new_x - self.x, new_y - self.y
        dista = math.hypot(d_x, d_y)
        if dista < self.speed:
            self.x, self.y = new_x, new_y
            self.way_point = self.way_point + 1
            if self.way_point >= len(waypoints):
                self.end = True
                self.alive = False
        else:
            self.x += d_x / dista * self.speed
            self.y += d_y / dista * self.speed

    def draw(self, screen):
        if not self.alive:
            return
        pygame.draw.circle(screen, red, (int(self.x), int(self.y)), self.radius)

        bar_w, bar_h = 20, 3
        ratio = max(0, self.hp / self.max_hp)
        bx = self.x - bar_w // 2
        by = self.y - 26
        pygame.draw.rect(screen, black, (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        pygame.draw.rect(screen, green, (bx, by, bar_w * ratio, bar_h))


def start_wave():
    global wave_active, gold, lives, wave_number, enemies_tospawn, spawn_timer
    wave_number += 1
    wave_active = True
    enemies_tospawn = 5 + wave_number * 3
    spawn_timer = 30


def update_wave():
    global wave_active, enemies_tospawn, spawn_timer

    if not wave_active:
        return


    if enemies_tospawn <= 0 and len(enemies) == 0:
        wave_active = False
        return

    if enemies_tospawn > 0:
        spawn_timer -= 1

        if spawn_timer <= 0:
            enemies.append(enemy(1.5, 50, 10))
            enemies_tospawn -= 1
            spawn_timer = 30


class game:
    def __init__(self):
        self.x = cell // 2
        self.y = cell // 2


def is_cell_available(gx, gy):

    if gx < 0 or gx >= width // cell or gy < 0 or gy >= height // cell:
        return False
    if (gx, gy) in road_cells:
        return False
    for i in Towers:
        if gx == i.x and gy == i.y:
            return False
    return True


running = True
while running:
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:

                if not wave_active:
                    start_wave()

        if event.type == pygame.MOUSEBUTTONDOWN:
            position = event.pos
            ux = position[0] // cell
            uy = position[1] // cell
            if is_cell_available(ux, uy):
                placing = (ux, uy)
                kind = "fast"
                cost = tower_types[kind]["cost"]
                if gold >= cost:
                    Towers.append(Tower(placing[0], placing[1], kind))
                    gold = gold - cost
                    placing = None
                else:
                    placing = None

        if event.type == pygame.QUIT:
            running = False

    update_wave()

    for tower in Towers:
        proj = tower.update(enemies)
        if proj:
            Projectiles.append(proj)

    for proj in Projectiles:
        proj.update()

    for e in enemies:
        e.update()

        if e.end:
            lives -= 1
            e.end = False

    screen.fill(green)
    for x in range(0, width, cell):
        pygame.draw.line(screen, black, (x, 0), (x, height), 1)
    for y in range(0, height, cell):
        pygame.draw.line(screen, black, (0, y), (width, y), 1)

    draw_road(screen=screen)
    for tower in Towers:
        tower.draw(screen)

    for e in enemies:
        e.draw(screen)

    for proj in Projectiles:
        proj.draw(screen)


    enemies = [e for e in enemies if e.alive]
    Projectiles = [p for p in Projectiles if p.alive]


    if lives <= 0:
        print("Game Over!")
        running = False

    pygame.display.flip()
pygame.quit()
