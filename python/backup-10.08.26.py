import pygame
import math
import os

pygame.init()

yellow = (176, 163, 44)

cell = 40
width = 800
height = 600
UI_BAR_HEIGHT = 120
PLAYFIELD_HEIGHT = height - UI_BAR_HEIGHT
WALL_WIDTH = 120
GRID_COLS = width // cell
GRID_ROWS = PLAYFIELD_HEIGHT // cell
SHOP_CARD_GAP = 40






screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("TDR")
clock = pygame.time.Clock()
green = (0, 100, 0)
black = (0, 0, 0)
fps = 60
red = (200, 0, 0)
mqeen_red = (155,0,0)
blue = (0, 0, 200)
orange = (255, 229, 84)
tower_types = {"fast": {"name": "fast", "color": blue, "cost": 25, "damage": 10, "fire_rate": 20, "range": 150}}
enemy_types = {"normal": {"hp_mult" : 1.0, "speed_mult": 1.0, "gold_mult": 1.0, "damage": 1}, "mcqueen": {"hp_mult": 0.6, "speed_mult": 2.0, "gold_mult": 0.8, "damage": 2}}



Gold = (255, 230, 20)
lives = 4
white = (255, 255, 255)

SCREEN_RECT = pygame.Rect(0, 0, WIDTH, HEIGHT)



font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Minecraft.otf")


@lru_cache
def minecraft_font(size):
    if font_path.exists():
        return pygame.font.Font(str(font_path), size)
    return pygame.font.SysFont("arial", size)



wave_number = 0
wave_active = False
enemies_tospawn = 0
gold = 75
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
    def __init__(self, speed, hp, money, kind):
        stats = enemy_types[kind]
        self.speed = speed * stats["speed_mult"]
        self.hp = hp
        self.money = int(money * stats["gold_mult"])
        self.max_hp = int(hp * stats["hp_mult"])
        self.alive = True
        self.end = False
        self.x, self.y = waypoints[0]
        self.way_point = 0
        self.radius = cell // 2 - 1
        self.damage = damage
        self.kind = kind


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
        center = (int(self.x), int(self.y))


        if self.kind = "mcqueen":
            points = [(center[0],center[1] - 15), (center[0] - 15, center[1] + 15) (center[0] +15, center[1] + 15)]
            pygame.draw.polygon(surface, mqeen_red, points)
            pygame.draw.polygon(surface, black, points, 2)

        else:
            pygame.draw.circle(screen, red, center, self.radius)
            pygame.draw.circle(screen, (247, 120, 92), center, self.radius - 4)

        bar_w, bar_h = 20, 3
        ratio = max(0, self.hp / self.max_hp)
        bx = self.x - bar_w // 2
        by = self.y - 26
        pygame.draw.rect(screen, black, (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        pygame.draw.rect(screen, green, (bx, by, bar_w * ratio, bar_h))


def is_cell_available(gx, gy):
    if gx < 0 or gx >= width // cell or gy < 0 or gy >= height // cell:
        return False
    if (gx, gy) in road_cells:
        return False
    if (gy * cell >= height - 120):
        return False

    for i in Towers:
        if gx == i.x and gy == i.y:
            return False
    return True


def draw_text(surface, font, text, color, position):
    x, y = position
    surface.blit(font.render(text, True, color), (x, y))


def draw_centered_text(surface, font, text, color, center):
    text = font.render(text, True, color)
    position = (center[0] - text.get_width // 2, center[1] - text.get_height //2)
    draw_text(surface, font, text, color, position)


def draw_focus_hightlight(surface, rect):



def draw_tower_range(surface, center, stats):
    radius = stats["range"]
    layer = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(layer, (*stats["color"], 40), (radius, radius), radius)
    pygame.draw.circle(layer, (*stats["color"], 150), (radius, radius), radius, 2)
    surface.blit(layer, (center[0] - radius, center[1] - radius))






def draw_ui():
    pygame.draw.rect(screen, black, (0, height - 120, width, 120))
    font = minecraft_font(24)
    font_small = minecraft_font(10)

    draw_text(screen, font, f"Gold: {gold}", Gold, 40, height - 80)
    draw_text(screen, font, f"Lives: {lives}", white, 40, height - 40)
    draw_text(screen, font, f"Wave: {wave_number}", white, 220, height - 80)

    types = list(tower_types.items())

    for i, (k, v) in enumerate(types):
        x = 400 + i * 180
        pygame.draw.rect(screen, v["color"], (x, height - 82, 80, 70))
        draw_text(screen, font, f"{v["name"]}", black, x + 5, height - 80)
        draw_text(screen, font, f"{v["cost"]}", black, x + 5, height - 40)

class GAME:
    def __init__(self):
        self.event = []
        self.reset()


    def emit(self, name):
        self.events.append(name)


    def reset(self):
        self.selected = "fast"
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.lives = 4
        self.gold = 75
        self.wave = 0
        self.spawn_timer = 0
        self.spawn_queue = 0
        self.wave_active = False
        self.delete_cell = False
        self.hover_cell = False
        self.game_over = False
        self.pending_cell = None
        for event_name in ("gold_changed", "lives_changed", "wave_changed"):
          self.emit(event_name)

    def start_wave(self):
        if self.wave_active or self.game_over:
            return


        self.wave += 1
        scale = 1 + ((self.wave // 2 ) - 1) # подумать

        self.wave_conf = {"count": int(5 * scale), "hp": int(50 * scale), "speed": 1.5 + (self.wave - 1) * 0.05, "gold": int(10 + self.wave - 1) * 1.5}
        self.spawn_queue = self.wave_conf["count"]

        self.wave_active = True
        self.enemies_tospawn = 5 + wave * 3
        self.spawn_timer = 0
        self.emit("wave_changed")



    def update(self):
        if self.game_over:
            return
        if self.spawn_queue != 0 and self.wave_active:
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                spawn_number = self.wave_conf["count"] - self.spawn_queue + 1
                kind = "mqceen" if spawn_number % 5 == 0 else "normal"

                self.enemies.append(enemy(self.wave_conf["hp"], self.wave_conf["speed"], self.wave_conf["gold"], kind))
                self.spawn_queue -= 1
                self.spawn_timer = 25

        for enemy in enemies:
            enemy.update()
            if enemy.end:
                self.lives -= 1
                self.emit("lives_changed")

        for tower in self.towers:
            self.projectiles.extend(towers.update(self.enemies))

        for projectile in self.projectiles:
            projectile.update(self.enemies)


        self.projectiles = [bullet for bullet in self.projectile if bullet.alive]

        gold_gained = False
        survivors = []
        for enemy in self.enemies:
            if self.enemy.alive:
                survivors.append(enemy)
            elif not enemy.end:
                self.gold += enemy.gold
                gold_gained = True
        if gold_gained:
            self.emit("gold_changed")
        self.enemies = survivors

        if (self.wave_active) and (not self.spawn_queue) and (not self.enemies):
            self.wave_active = False
        if self.lives <= 0:
            self.game_over = True


    def handle_click(self, position, button):
        if button != 1 or self.game_over:
            return

        if self.delete_cell:
            col, row = self.delete_cell
            center = (col * cell + cell // 2, row * cell + cell // 2)
            if math.hypot(position[0] - center[0], position[1] - center[1]) <= 28:
                self.towers = [tower for tower in self.towers if (tower.col, tower.row) != (col, row)]
            self.delete_cell = None
            return

        col = position[0] // cell
        row = position[1] // cell


        if not (col >= 0 and col < GRID_COLS and row >= 0 and row <GRID_ROWS):
            return


        if self.pending_cell != (col, row):
            self.pending_cell = col, row
            return

        if (col, row) in waypoints:
            return

        cost = tower_types[self.selected][cost]
        if self.gold >= cost:
            self.towers.append(Tower(col , row , self.selected))
            self.gold -= cost
            self.emit("gold_changed")



            self.pending_cell = None

class HUD:
    def __init__(self, font, small_font):
        self.font = font
        self.small_font = small_font
        self.gold_surf = None
        self.lives_surf = None
        self.wave_surf = None
        self.start_surf = small_font.render("START", True, WHITE)
        self.gold_pos = Layout.anchor_point(SCREEN_RECT, ("left", "bottom"), (SAFE_MARGIN, -80))
        self.lives_pos = Layout.anchor_point(SCREEN_RECT, ("left", "bottom"), (SAFE_MARGIN, -40))
        self.wave_pos = Layout.anchor_point(SCREEN_RECT, ("left", "bottom"), (220, -80))
        self.cards = {kind: self._make_card(kind, info) for kind, info in tower_types.intems()}

    def _make_card(self, kind, info):
        card = pygame.Surface(SHOP_CARD_SIZE)
        card.fill(info["color"])
        card.blit(self.small_font.render(info["name"], True, black, (6, 6)))
        card.blit(self.small_font.render(info["cost"], True, black, (6, 44)))
        return card

    def draw(self, surface, selected):
        if self.gold_surf:
            surface.blit(self.gold_surf, self.gold_pos)
        if self.wave_surf:
            surface.blit(self.wave_surf, self.wave_pos)
        if self.lives_surf:
            surface.blit(self.lives_surf, self.lives_pos)
        for kind, rect in shop_cards():
            surface.blit(self.cards[kind], rect)
            border: white if kind == selected else tower_types[kind]["color"]
            pygame.draw.rect(surface, border, rect, 2)


def shop_cards():
    width, height = SHOP_CARD_SIZE
    area: pygame.Rect(0, 0, 2 * width + SHOP_CARD_GAP, height)
    area.midbottom = Layout.anchor_point(SCREEN_RECT, ("center", "bottom"), (0, -12))
    return list(zip(tower_types, Layout.hbox(area, [width] * 2, height, SHOP_CARD_GAP))

    running = True





def main():
    pygame.init()
    app: App()
    app.run()
    pygame.quit()


pygame.quit()




