import pygame
import math

from tower_defence import BLACK

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

# ===== Цвета =====
WHITE = (255, 255, 255)
DARK_GREEN = (30, 100, 30)
BROWN = (160, 130, 90)
DARK_BROWN = (120, 90, 60)
GOLD = (255, 215, 0)
GRAY = (100, 100, 100)
CYAN = (0, 200, 200)
HP_GREEN = (80, 200, 80)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# ===== Цвета для кирпичной стены =====
BRICK_RED = (139, 69, 19)  # Основной цвет кирпича
DARK_BRICK = (101, 67, 33)  # Темный кирпич
MORTAR = (200, 200, 200)  # Цемент между кирпичами
BRICK_HIGHLIGHT = (160, 82, 45)  # Светлый кирпич для бликов
# ===== Конец цветов стены =====

tower_types = {
    "fast": {"name": "fast", "color": blue, "cost": 25, "damage": 10, "fire_rate": 20, "range": 150},
    "cannon": {"name": "Cannon", "damage": 60, "fire_rate": 75, "range": 120, "color": orange, "cost": 250}
}

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

selected_tower = "fast"
hover_cell = None
placing_cell = None
delete_cell = None

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

for c in range(17, 20):
    road_cells.add((c, 4))

# ===== ДОБАВЛЕНО: Функция для отрисовки кирпичной стены =====
def draw_brick_wall(screen):
    """Отрисовка кирпичной стены с эффектом кривизны"""

    # Центр кривизны стены (правая часть экрана)
    curve_center_x = width + 200  # Центр кривой за экраном
    curve_center_y = height // 2

    # Параметры стены
    wall_start_x = width - 80  # Начало стены
    wall_end_x = width  # Конец стены

    # Рисуем стену по слоям (рядам кирпичей)
    brick_height = 30
    brick_width = 50
    rows = height // brick_height + 2

    for row in range(rows):
        # Вычисляем Y позицию с учетом кривизны
        y_offset = (row * brick_height) - brick_height

        # Смещение для эффекта кривизны
        curve_offset = math.sin(row * 0.1) * 30  # Волнообразная кривизна

        # Смещение кирпичей в ряду (для имитации кирпичной кладки)
        row_offset = (row % 2) * (brick_width // 2)

        # Рисуем кирпичи в ряду
        for x_pos in range(-brick_width, wall_end_x - wall_start_x + brick_width, brick_width):
            brick_x = wall_start_x + x_pos + row_offset + curve_offset

            # Создаем кирпич с эффектом кривизны
            brick_rect = pygame.Rect(
                brick_x,
                y_offset,
                brick_width - 4,  # Небольшой зазор между кирпичами
                brick_height - 4
            )

            # Проверяем, виден ли кирпич
            if brick_x < width and brick_x + brick_width > wall_start_x:
                # Основной цвет кирпича с вариациями
                if (row + int(x_pos // brick_width)) % 3 == 0:
                    brick_color = BRICK_HIGHLIGHT
                elif (row + int(x_pos // brick_width)) % 3 == 1:
                    brick_color = BRICK_RED
                else:
                    brick_color = DARK_BRICK

                # Рисуем кирпич
                pygame.draw.rect(screen, brick_color, brick_rect)

                # Добавляем текстуру кирпича (линии)
                pygame.draw.line(screen, DARK_BRICK,
                               (brick_rect.left, brick_rect.centery),
                               (brick_rect.right, brick_rect.centery), 1)

                # Светлый блик на кирпиче
                pygame.draw.line(screen, WHITE,
                               (brick_rect.left + 5, brick_rect.top + 3),
                               (brick_rect.right - 5, brick_rect.top + 3), 1)

    # Рисуем зубцы на верху стены
    crenellation_width = 25
    crenellation_height = 20
    crenellation_spacing = 50

    for x_pos in range(wall_start_x - 20, width, crenellation_spacing):
        # Зубец с эффектом кривизны
        curve_offset = math.sin(x_pos * 0.02) * 15
        crenellation_x = x_pos + curve_offset

        crenellation_rect = pygame.Rect(
            crenellation_x,
            -5,
            crenellation_width,
            crenellation_height
        )

        if crenellation_x < width:
            pygame.draw.rect(screen, BRICK_RED, crenellation_rect)
            pygame.draw.rect(screen, DARK_BRICK, crenellation_rect, 2)

    # Добавляем ворота в стене
    gate_width = 60
    gate_height = 100
    gate_x = wall_start_x + 20  # Позиция ворот
    gate_y = height // 2 - gate_height // 2 + 30

    # Арка ворот
    gate_rect = pygame.Rect(gate_x, gate_y, gate_width, gate_height)
    pygame.draw.rect(screen, DARK_BROWN, gate_rect)
    pygame.draw.rect(screen, BLACK, gate_rect, 3)

    # Арка (полукруг сверху ворот)
    pygame.draw.arc(screen, BLACK,
                   (gate_x - 5, gate_y - 30, gate_width + 10, 60),
                   math.pi, 2 * math.pi, 3)

    # Решетка на воротах
    for i in range(1, 6):
        bar_x = gate_x + (gate_width // 6) * i
        pygame.draw.line(screen, BLACK, (bar_x, gate_y), (bar_x, gate_y + gate_height), 2)

    for i in range(1, 4):
        bar_y = gate_y + (gate_height // 4) * i
        pygame.draw.line(screen, BLACK, (gate_x, bar_y), (gate_x + gate_width, bar_y), 2)

    # Добавляем флаги на стену
    flag_positions = [wall_start_x + 40, wall_start_x + 120, wall_start_x + 200]
    for flag_x in flag_positions:
        if flag_x < width:
            # Древко флага
            pygame.draw.line(screen, BLACK, (flag_x, 10), (flag_x, -30), 3)

            # Флаг (треугольник)
            flag_points = [
                (flag_x, -30),
                (flag_x + 20, -20),
                (flag_x, -10)
            ]
            pygame.draw.polygon(screen, RED, flag_points)
            pygame.draw.polygon(screen, GOLD, flag_points, 2)

    # Добавляем тень для создания объема
    shadow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(0, 80, 10):
        alpha = max(0, 50 - i // 2)
        pygame.draw.rect(shadow_surface, (0, 0, 0, alpha),
                        (wall_start_x + i, 0, 10, height))
    screen.blit(shadow_surface, (0, 0))
# ===== КОНЕЦ ФУНКЦИИ СТЕНЫ =====

def draw_text(surf, font, text, color, x, y, shadow=(0,0,0)):
    if shadow:
        s = font.render(text, True, shadow)
        surf.blit(s, (x+1, y+1))
    t = font.render(text, True, color)
    surf.blit(t, (x, y))

def draw_road(screen):
    for gx, gy in road_cells:
        rect = pygame.Rect(gx * cell, gy * cell, cell, cell)
        pygame.draw.rect(screen, yellow, rect)
        pygame.draw.rect(screen, black, rect, 1)

class Projectile:
    def __init__(self, x, y, damage, target, piercing=False, vx=0, vy=0, max_range=None):
        self.x = x
        self.y = y
        self.damage = damage
        self.target = target
        self.speed = 5
        self.alive = True
        self.piercing = piercing
        self.vx = vx
        self.vy = vy
        self.max_range = max_range
        self.src_x = x
        self.src_y = y
        self.hit_enemies = set()

    def update(self, enemies=None):
        if not self.alive:
            return
        if self.max_range is not None and math.hypot(self.x - self.src_x, self.y - self.src_y) > self.max_range:
            self.alive = False
            return

        if self.piercing:
            self.x += self.vx * self.speed
            self.y += self.vy * self.speed
            if enemies:
                for e in enemies:
                    if e.alive and id(e) not in self.hit_enemies:
                        if math.hypot(self.x - e.x, self.y - e.y) < 12:
                            e.hp -= self.damage
                            self.hit_enemies.add(id(e))
                            if e.hp <= 0:
                                e.alive = False
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
            size = 6 if self.piercing else 4
            pygame.draw.circle(screen, orange if self.piercing else yellow, (int(self.x), int(self.y)), size)

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
            return []

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
            if self.kind == "cannon":
                result = []
                for angle_offset in [-0.7, -0.35, 0, 0.35, 0.7]:
                    dx = best_target.x - (self.x * cell + cell // 2)
                    dy = best_target.y - (self.y * cell + cell // 2)
                    dist = math.hypot(dx, dy) or 1
                    base_angle = math.atan2(dy, dx)
                    angle = base_angle + angle_offset
                    result.append(Projectile(
                        self.x * cell + cell // 2,
                        self.y * cell + cell // 2,
                        self.stats["damage"],
                        best_target,
                        piercing=True,
                        vx=math.cos(angle),
                        vy=math.sin(angle),
                        max_range=self.stats["range"]
                    ))
                return result

            return [Projectile(self.x * cell + cell // 2, self.y * cell + cell // 2, self.stats["damage"], best_target)]
        return []

    def draw(self, screen, show_range=False):
        tower = pygame.Rect(self.x * cell + 3, self.y * cell + 3, cell - 6, cell - 6)
        pygame.draw.rect(screen, self.stats["color"], tower)
        if show_range:
            center_x = self.x * cell + cell // 2
            center_y = self.y * cell + cell // 2
            s = pygame.Surface((self.stats["range"] * 2,) * 2, pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, 60), (self.stats["range"],) * 2, self.stats["range"])
            screen.blit(s, (center_x - self.stats["range"], center_y - self.stats["range"]))

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
        pygame.draw.rect(screen, HP_GREEN, (bx, by, bar_w * ratio, bar_h))

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

def is_cell_available(gx, gy):
    if gx < 0 or gx >= width // cell or gy < 0 or gy >= height // cell - 1:
        return False
    if (gx, gy) in road_cells:
        return False

    if gy * cell >= height - 120:
            return False
    for i in Towers:
        if gx == i.x and gy == i.y:
            return False
    return True

def draw_ui():
    pygame.draw.rect(screen, black, (0, height - 60, width, 60))

    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 20)

    draw_text(screen, font, f"${gold}", GOLD, 10, height - 50)
    draw_text(screen, font, f"Lives: {lives}", RED if lives < 3 else WHITE, 10, height - 30)
    draw_text(screen, small_font, "GOLD", GRAY, 10, height - 15)
    draw_text(screen, small_font, "LIVES", GRAY, 80, height - 15)

    draw_text(screen, font, f"Wave {wave_number}", WHITE, 150, height - 50)

    types = list(tower_types.items())
    for i, (k, v) in enumerate(types):
        x = 250 + i * 180
        pygame.draw.rect(screen, v["color"], (x, height - 52, 80, 44))
        border = YELLOW if k == selected_tower else WHITE
        pygame.draw.rect(screen, border, (x, height - 52, 80, 44), 2)
        draw_text(screen, font, f"{v['name']}", BLACK, x + 5, height - 48)
        draw_text(screen, font, f"${v['cost']}", BLACK, x + 5, height - 30)

    if not wave_active:
        sx, sy = 25, 260
        pygame.draw.circle(screen, red if wave_number > 0 else green, (sx, sy), 20)
        pygame.draw.circle(screen, WHITE, (sx, sy), 20, 2)
        pts = [(sx - 6, sy - 8), (sx - 6, sy + 8), (sx + 10, sy)]
        pygame.draw.polygon(screen, WHITE, pts)
        draw_text(screen, small_font, "Start", WHITE, sx + 26, sy - 8)

def draw_place_menu():
    if not placing_cell:
        return

    gx, gy = placing_cell
    cx = gx * cell + cell // 2
    cy = gy * cell + cell // 2
    rd = 50

    s = pygame.Surface((rd * 2, rd * 2), pygame.SRCALPHA)
    pygame.draw.circle(s, (40, 40, 40, 220), (rd, rd), rd)

    s2 = pygame.Surface((rd * 2, rd * 2), pygame.SRCALPHA)
    colors = [info["color"] + (180,) for info in tower_types.values()]
    s2.set_clip(pygame.Rect(rd, 0, rd, rd * 2))
    pygame.draw.circle(s2, colors[0], (rd, rd), rd)
    s2.set_clip(pygame.Rect(0, 0, rd, rd * 2))
    pygame.draw.circle(s2, colors[1] if len(colors) > 1 else colors[0], (rd, rd), rd)

    screen.blit(s, (cx - rd, cy - rd))
    screen.blit(s2, (cx - rd, cy - rd))
    pygame.draw.circle(screen, WHITE, (cx, cy), rd, 2)
    pygame.draw.line(screen, WHITE, (cx, cy - rd), (cx, cy + rd), 2)

    font = pygame.font.Font(None, 20)
    for lx, (key, info) in zip((cx + rd * 0.55, cx - rd * 0.55), tower_types.items()):
        draw_text(screen, font, info["name"], BLACK, lx - font.size(info["name"])[0] // 2, cy - 10)
        draw_text(screen, font, f"${info['cost']}", BLACK, lx - font.size(f"${info['cost']}")[0] // 2, cy + 4)

def draw_delete_menu():
    if not delete_cell:
        return

    gx, gy = delete_cell
    cx = gx * cell + cell // 2
    cy = gy * cell + cell // 2
    rd = 25

    s = pygame.Surface((rd * 2,) * 2, pygame.SRCALPHA)
    pygame.draw.circle(s, (180, 40, 40, 220), (rd, rd), rd)
    screen.blit(s, (cx - rd, cy - rd))
    pygame.draw.circle(screen, WHITE, (cx, cy), rd, 2)

    font = pygame.font.Font(None, 20)
    draw_text(screen, font, "Delete", WHITE, cx - font.size("Delete")[0] // 2, cy - font.size("Delete")[1] // 2)

running = True
while running:
    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not wave_active:
                    start_wave()
            elif event.key == pygame.K_1:
                selected_tower = "fast"
            elif event.key == pygame.K_2 and "cannon" in tower_types:
                selected_tower = "cannon"

        if event.type == pygame.MOUSEBUTTONDOWN:
            position = event.pos

            if not wave_active:
                sx, sy = 25, 260
                if math.hypot(position[0] - sx, position[1] - sy) <= 20:
                    start_wave()
                    placing_cell = None
                    delete_cell = None
                    continue

            if position[1] >= height - 60:
                types = list(tower_types.keys())
                for i, k in enumerate(types):
                    x = 250 + i * 180
                    if x <= position[0] <= x + 80:
                        selected_tower = k
                placing_cell = None
                delete_cell = None
                continue

            if delete_cell:
                gx, gy = delete_cell
                cx = gx * cell + cell // 2
                cy = gy * cell + cell // 2
                if math.hypot(position[0] - cx, position[1] - cy) <= 25:
                    Towers = [t for t in Towers if not (t.x == gx and t.y == gy)]
                delete_cell = None
                continue

            if placing_cell:
                gx, gy = placing_cell
                cx = gx * cell + cell // 2
                cy = gy * cell + cell // 2
                if math.hypot(position[0] - cx, position[1] - cy) <= 50:
                    kind = list(tower_types.keys())[1] if position[0] - cx < 0 else list(tower_types.keys())[0]
                    cost = tower_types[kind]["cost"]
                    if gold >= cost:
                        Towers.append(Tower(gx, gy, kind))
                        gold -= cost
                placing_cell = None
                continue

            ux = position[0] // cell
            uy = position[1] // cell

            for t in Towers:
                if t.x == ux and t.y == uy:
                    delete_cell = (ux, uy)
                    break
            else:
                if is_cell_available(ux, uy):
                    placing_cell = (ux, uy)

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEMOTION:
            gx, gy = event.pos[0] // cell, event.pos[1] // cell
            in_grid = 0 <= gx < width // cell and 0 <= gy < height // cell - 1
            hover_cell = (gx, gy) if in_grid else None

    update_wave()

    for tower in Towers:
        projs = tower.update(enemies)
        for proj in projs:
            Projectiles.append(proj)

    for proj in Projectiles:
        proj.update(enemies if proj.piercing else None)

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

    # ===== ДОБАВЛЕНО: Отрисовка кирпичной стены =====
    draw_brick_wall(screen)
    # ===== КОНЕЦ ДОБАВЛЕНИЯ =====

    for tower in Towers:
        show_range = hover_cell and tower.x == hover_cell[0] and tower.y == hover_cell[1]
        tower.draw(screen, show_range)

    for e in enemies:
        e.draw(screen)

    for proj in Projectiles:
        proj.draw(screen)

    draw_place_menu()
    draw_delete_menu()
    draw_ui()

    enemies = [e for e in enemies if e.alive]
    Projectiles = [p for p in Projectiles if p.alive]

    if lives <= 0:
        print("Game Over!")
        running = False

    pygame.display.flip()
pygame.quit()
