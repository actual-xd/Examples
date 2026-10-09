from enum import Enum, auto
from functools import lru_cache
import math
from pathlib import Path
import pygame


WIDTH, HEIGHT = 1000, 720
FPS = 60

NEXT_WAVE_DELAY = 15 * FPS
CELL = 40
UI_BAR_HEIGHT = 120
SHOP_CARD_SIZE = (80, 80)
SHOP_CARD_GAP = 40
PLAYFIELD_HEIGHT = HEIGHT - UI_BAR_HEIGHT
WALL_WIDTH = 120
WALL_LEFT = WIDTH - WALL_WIDTH
GRID_COLS = WIDTH // CELL
GRID_ROWS = PLAYFIELD_HEIGHT // CELL
FONT_PATH = Path(__file__).with_name("Minecraft.otf")

SCREEN_RECT = pygame.Rect(0, 0, WIDTH, HEIGHT)
LETTERBOX = (12, 17, 14)

SAFE_MARGIN = int(0.04 * min(WIDTH, HEIGHT))

PAUSE_LABELS = ("RESUME", "SETTINGS", "MAIN MENU")


INK = (20, 26, 22)
TEXT = (240, 238, 230)
TEXT_MUTED = (162, 176, 164)
BG_TOP = (16, 26, 21)
BG_BOTTOM = (32, 50, 39)
PANEL = (26, 38, 32)
PANEL_LIGHT = (42, 58, 49)
PANEL_BORDER = (66, 88, 76)
ACCENT = (232, 178, 62)
ACCENT_HOVER = (245, 199, 96)
ACCENT_DARK = (188, 140, 38)
GRASS = (58, 105, 66)
GRASS_LINE = (46, 84, 53)
ROAD = (188, 150, 108)
ROAD_EDGE = (128, 98, 68)
WALL_BASE = (132, 86, 62)
BRICK = (168, 110, 78)
BRICK_LIGHT = (196, 140, 104)
BRICK_DARK = (120, 76, 56)
TOWER_RAPID = (86, 158, 205)
TOWER_CANNON = (178, 132, 208)
ENEMY = (214, 112, 98)
ENEMY_CORE = (240, 168, 150)
ENEMY_FAST = (176, 68, 56)
DANGER = (176, 68, 58)
DANGER_TEXT = (232, 120, 104)
HEALTH = (124, 196, 128)
OVERLAY = (10, 16, 13)

WAYPOINTS = [
    (-40, 260),
    (220, 260),
    (220, 100),
    (460, 100),
    (460, 420),
    (700, 420),
    (700, 180),
    (860, 180),
]

TOWER_TYPES = {
    "rapid": {
        "name": "Rapid",
        "damage": 10,
        "fire_rate": 10,
        "range": 150,
        "color": TOWER_RAPID,
        "cost": 100,
    },
    "cannon": {
        "name": "Cannon",
        "damage": 75,
        "fire_rate": 60,
        "range": 120,
        "color": TOWER_CANNON,
        "cost": 500,
    },
}

ENEMY_TYPES = {
    "normal": {
        "hp_multiplier": 1.0,
        "speed_multiplier": 1.0,
        "gold_multiplier": 1.0,
        "life_damage": 1,
    },
    "mcqueen": {
        "hp_multiplier": 0.6,
        "speed_multiplier": 2.0,
        "gold_multiplier": 0.8,
        "life_damage": 2,
    },
}

PATH_CELLS = set()
for (x1, y1), (x2, y2) in zip(WAYPOINTS, WAYPOINTS[1:]):
    c1, r1 = x1 // CELL, y1 // CELL
    c2, r2 = x2 // CELL, y2 // CELL
    for col in range(min(c1, c2), max(c1, c2) + 1):
        for row in range(min(r1, r2), max(r1, r2) + 1):
            PATH_CELLS.add((col, row))


class ScreenState(Enum):
    MENU = auto()
    SETTINGS = auto()
    GAME = auto()
    PAUSE = auto()


SAFE = SCREEN_RECT.inflate(-2 * SAFE_MARGIN, -2 * SAFE_MARGIN)
PLAY_BUTTON = pygame.Rect(0, 0, 124, 124)
PLAY_BUTTON.center = (WIDTH // 2, HEIGHT // 2 - 84)
SETTINGS_BUTTON = pygame.Rect(0, 0, 64, 64)
SETTINGS_BUTTON.midtop = (WIDTH // 2, PLAY_BUTTON.bottom + 62)
BACK_BUTTON = pygame.Rect(58, 22, 116, 44)
SETTINGS_PANEL = pygame.Rect(0, 0, SAFE.width - 80, 400)
SETTINGS_PANEL.midtop = (SAFE.centerx, SAFE.top + 150)
VOLUME_TRACK = pygame.Rect(0, 0, 480, 8)
VOLUME_TRACK.center = (SETTINGS_PANEL.centerx, SETTINGS_PANEL.top + 200)
VOLUME_HIT = VOLUME_TRACK.inflate(10, 10)
PAUSE_PANEL = pygame.Rect(0, 0, 340, 220)
PAUSE_PANEL.center = (WIDTH // 2, HEIGHT // 2)

MENU_TITLE_POS = (SAFE.centerx, SAFE.top + 97)
MENU_SUBTITLE_POS = (SAFE.centerx, SAFE.top + 142)
MENU_HINT_POS = (SAFE.centerx, SAFE.bottom - 42)
MENU_SETTINGS_POS = (SETTINGS_BUTTON.centerx, SETTINGS_BUTTON.bottom + 18)
SETTINGS_TITLE_POS = (SETTINGS_PANEL.left + 32, SETTINGS_PANEL.top + 40)
SETTINGS_AUDIO_POS = (SETTINGS_PANEL.left + 32, SETTINGS_PANEL.top + 100)
SETTINGS_VOLUME_POS = (SETTINGS_PANEL.left + 32, SETTINGS_PANEL.top + 154)
SETTINGS_HINT_POS = (SAFE.centerx, SAFE.bottom - 24)


def pause_items():
    rects = [pygame.Rect(0, 0, 260, 52) for _ in range(3)]
    for index, rect in enumerate(rects):
        rect.center = (WIDTH // 2, HEIGHT // 2 + (index - 1) * 68)
    return rects


def letterbox_rect(window_size):
    scale = min(window_size[0] / WIDTH, window_size[1] / HEIGHT)
    width, height = int(WIDTH * scale), int(HEIGHT * scale)
    return pygame.Rect(
        (window_size[0] - width) // 2, (window_size[1] - height) // 2, width, height
    )


def shop_cards():
    width, height = SHOP_CARD_SIZE
    left = (WIDTH - (2 * width + SHOP_CARD_GAP)) // 2
    top = HEIGHT - 12 - height
    return [
        (kind, pygame.Rect(left + index * (width + SHOP_CARD_GAP), top, width, height))
        for index, kind in enumerate(TOWER_TYPES)
    ]


SHOP_CARDS = shop_cards()


@lru_cache
def minecraft_font(size):
    if FONT_PATH.exists():
        return pygame.font.Font(str(FONT_PATH), size)
    return pygame.font.SysFont("arial", size)


def draw_text(surface, font, text, color, position):
    surface.blit(font.render(text, True, color), position)


def draw_centered_text(surface, font, text, color, center):
    text_surface = font.render(text, True, color)
    position = (center[0] - text_surface.get_width() // 2, center[1] - text_surface.get_height() // 2)
    draw_text(surface, font, text, color, position)


def draw_vertical_gradient(surface, top, bottom):
    height = surface.get_height()
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
        pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))


def draw_panel(surface, rect, color=PANEL, alpha=225, border=PANEL_BORDER, radius=14):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (*color, alpha), panel.get_rect(), border_radius=radius)
    if border:
        pygame.draw.rect(panel, (*border, min(255, alpha + 20)), panel.get_rect(), 1, border_radius=radius)
    surface.blit(panel, rect.topleft)


def draw_play_icon(surface, center, radius, color=INK):
    cx, cy = center
    points = [
        (cx - radius // 4, cy - radius // 2),
        (cx - radius // 4, cy + radius // 2),
        (cx + radius // 2, cy),
    ]
    pygame.draw.polygon(surface, color, points)


def draw_gear_icon(surface, center, radius, color=TEXT):
    cx, cy = center
    for angle in range(0, 360, 45):
        radians = math.radians(angle)
        inner = radius * 0.65
        outer = radius * 1.05
        start = (cx + math.cos(radians) * inner, cy + math.sin(radians) * inner)
        end = (cx + math.cos(radians) * outer, cy + math.sin(radians) * outer)
        pygame.draw.line(surface, color, start, end, max(3, radius // 4))
    pygame.draw.circle(surface, color, center, int(radius * 0.68))
    pygame.draw.circle(surface, INK, center, int(radius * 0.3))


def draw_hover_highlight(surface, rect):
    pygame.draw.rect(surface, ACCENT, rect.inflate(14, 14), 4, border_radius=12)


def build_brick_wall(size):
    width, height = size
    wall = pygame.Surface(size, pygame.SRCALPHA)
    wall_width = min(WALL_WIDTH, width)
    left = width - wall_width
    pygame.draw.rect(wall, WALL_BASE, (left, 0, wall_width, height))
    brick_height = 32
    brick_width = 64
    for row, y in enumerate(range(0, height, brick_height)):
        offset = 0 if row % 2 == 0 else brick_width // 2
        pygame.draw.line(wall, INK, (left, y), (width, y), 3)
        for column, x in enumerate(range(left - brick_width + offset, width, brick_width)):
            brick_left = max(left + 2, x + 2)
            brick_right = min(width - 2, x + brick_width - 2)
            if brick_right <= brick_left:
                continue
            color = (BRICK_DARK, BRICK, BRICK_LIGHT)[(row + column) % 3]
            pygame.draw.rect(wall, color, (brick_left, y + 2, brick_right - brick_left, brick_height - 4))
            pygame.draw.line(
                wall,
                tuple(min(255, channel + 24) for channel in color),
                (brick_left + 3, y + 4),
                (brick_right - 3, y + 4),
                1,
            )
        for seam_x in range(left + offset, width, brick_width):
            pygame.draw.line(wall, INK, (seam_x, y), (seam_x, min(height, y + brick_height)), 3)
    pygame.draw.rect(wall, INK, (left, 0, wall_width, height), 2)
    return wall


BRICK_WALL = build_brick_wall((WIDTH, PLAYFIELD_HEIGHT))


def draw_field(surface):
    surface.fill(GRASS)
    for y in range(0, PLAYFIELD_HEIGHT, CELL):
        pygame.draw.line(surface, INK, (0, y), (WIDTH, y), 1)
    for x in range(0, WIDTH + 1, CELL):
        pygame.draw.line(surface, INK, (x, 0), (x, PLAYFIELD_HEIGHT), 1)


def draw_path(surface):
    for col, row in PATH_CELLS:
        rect = pygame.Rect(col * CELL, row * CELL, CELL, CELL)
        pygame.draw.rect(surface, ROAD, rect)
        pygame.draw.rect(surface, INK, rect, 1)


class Enemy:
    def __init__(self, hp, speed, gold, kind="normal"):
        stats = ENEMY_TYPES[kind]
        self.kind = kind
        self.max_hp = int(hp * stats["hp_multiplier"])
        self.hp = self.max_hp
        self.speed = speed * stats["speed_multiplier"]
        self.gold = int(gold * stats["gold_multiplier"])
        self.life_damage = stats["life_damage"]
        self.waypoint_index = 0
        self.distance_travelled = 0
        self.x, self.y = WAYPOINTS[0]
        self.alive = True
        self.reached_end = False

    def update(self):
        if not self.alive or self.reached_end:
            return
        target_x, target_y = WAYPOINTS[self.waypoint_index]
        dx, dy = target_x - self.x, target_y - self.y
        distance = math.hypot(dx, dy)
        if distance <= self.speed:
            self.distance_travelled += distance
            self.x, self.y = target_x, target_y
            self.waypoint_index += 1
            if self.waypoint_index >= len(WAYPOINTS):
                self.alive = False
                self.reached_end = True
        else:
            self.distance_travelled += self.speed
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed

    def draw(self, surface):
        if not self.alive:
            return
        center = (int(self.x), int(self.y))
        if self.kind == "mcqueen":
            color = ENEMY_FAST
            points = [
                (center[0], center[1] - 17),
                (center[0] - 15, center[1] + 12),
                (center[0] + 15, center[1] + 12),
            ]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, INK, points, 2)
        else:
            pygame.draw.circle(surface, DANGER, center, 15)
            pygame.draw.circle(surface, ENEMY_CORE, center, 9)
        bar = pygame.Rect(int(self.x - 12), int(self.y - 25), 24, 4)
        pygame.draw.rect(surface, INK, bar.inflate(2, 2))
        pygame.draw.rect(surface, HEALTH, (bar.x, bar.y, int(bar.width * max(0, self.hp / self.max_hp)), bar.height))


class Projectile:
    def __init__(self, x, y, target, damage, *, piercing=False, size=3, vx=0, vy=0, color=ACCENT, max_range=None):
        self.x, self.y = x, y
        self.target = target
        self.damage = damage
        self.speed = 6
        self.alive = True
        self.piercing = piercing
        self.size = size
        self.vx, self.vy = vx, vy
        self.color = color
        self.source = (x, y)
        self.max_range = max_range
        self.hit_enemies = set()

    def update(self, enemies=None):
        if not self.alive:
            return
        if self.max_range is not None and math.hypot(self.x - self.source[0], self.y - self.source[1]) > self.max_range:
            self.alive = False
            return
        if self.piercing:
            self.x += self.vx * self.speed
            self.y += self.vy * self.speed
            for enemy in enemies or []:
                if enemy.alive and id(enemy) not in self.hit_enemies and math.hypot(self.x - enemy.x, self.y - enemy.y) < self.size + 8:
                    enemy.hp -= self.damage
                    self.hit_enemies.add(id(enemy))
                    if enemy.hp <= 0:
                        enemy.alive = False
            return
        if not self.target.alive or self.target.reached_end:
            self.alive = False
            return
        dx, dy = self.target.x - self.x, self.target.y - self.y
        distance = math.hypot(dx, dy)
        if distance <= self.speed:
            self.target.hp -= self.damage
            if self.target.hp <= 0:
                self.target.alive = False
            self.alive = False
        else:
            self.x += dx / distance * self.speed
            self.y += dy / distance * self.speed

    def draw(self, surface):
        if self.alive:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)


def draw_tower_range(surface, center, stats):
    radius = stats["range"]
    layer = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(layer, (*stats["color"], 35), (radius, radius), radius)
    pygame.draw.circle(layer, (*stats["color"], 150), (radius, radius), radius, 2)
    surface.blit(layer, (center[0] - radius, center[1] - radius))


class Tower:
    def __init__(self, col, row, kind):
        self.col, self.row = col, row
        self.x = col * CELL + CELL // 2
        self.y = row * CELL + CELL // 2
        self.kind = kind
        self.stats = TOWER_TYPES[kind]
        self.cooldown = 0

    def update(self, enemies):
        if self.cooldown:
            self.cooldown -= 1
            return []
        in_range = []
        for enemy in enemies:
            if not enemy.alive or enemy.reached_end:
                continue
            distance = math.hypot(self.x - enemy.x, self.y - enemy.y)
            if distance < self.stats["range"]:
                in_range.append(enemy)
        if not in_range:
            return []
        final_section = [
            enemy for enemy in in_range if enemy.waypoint_index >= len(WAYPOINTS) - 2
        ]
        target = max(final_section, key=lambda enemy: enemy.distance_travelled) if final_section else min(
            in_range, key=lambda enemy: math.hypot(self.x - enemy.x, self.y - enemy.y)
        )
        self.cooldown = self.stats["fire_rate"]
        if self.kind == "cannon":
            dx, dy = target.x - self.x, target.y - self.y
            distance = math.hypot(dx, dy) or 1
            ux, uy = dx / distance, dy / distance
            projectiles = []
            for spread in (-0.7, -0.35, 0, 0.35, 0.7):
                angle = math.atan2(uy, ux) + spread
                projectiles.append(
                    Projectile(
                        self.x,
                        self.y,
                        target,
                        self.stats["damage"],
                        piercing=True,
                        size=6,
                        vx=math.cos(angle),
                        vy=math.sin(angle),
                        color=TOWER_CANNON,
                        max_range=self.stats["range"],
                    )
                )
            return projectiles
        return [Projectile(self.x, self.y, target, self.stats["damage"], max_range=self.stats["range"])]

    def draw(self, surface, show_range=False):
        rect = pygame.Rect(self.col * CELL + 4, self.row * CELL + 4, CELL - 8, CELL - 8)
        pygame.draw.rect(surface, self.stats["color"], rect, border_radius=7)
        pygame.draw.rect(surface, INK, rect, 2, border_radius=7)
        pygame.draw.circle(surface, TEXT, (self.x, self.y), 3)
        if show_range:
            draw_tower_range(surface, (self.x, self.y), self.stats)


class Game:
    def __init__(self):
        self.reset()

    def reset(self):
        self.selected = "rapid"
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.gold = 300
        self.lives = 3
        self.wave = 0
        self.spawn_q = 0
        self.spawn_timer = 0
        self.wave_active = False
        self.hover_cell = None
        self.delete_cell = None
        self.game_over = False
        self.pending_cell = None
        self.next_wave_timer = None

    @property
    def can_start_wave(self):
        return not self.game_over and self.spawn_q == 0

    def start_wave(self):
        if not self.can_start_wave:
            return
        self.next_wave_timer = None
        self.wave += 1
        scale = 1 + (self.wave - 1) * 0.35
        self.wave_count = int(5 * scale)
        self.wave_hp = int(50 * scale)
        self.wave_speed = 1.5 + (self.wave - 1) * 0.05
        self.wave_gold = int(8 + (self.wave - 1) * 1.5)
        self.spawn_q = self.wave_count
        self.spawn_timer = 0
        self.wave_active = True

    def update(self):
        if self.game_over:
            return
        if self.wave_active and self.spawn_q:
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                number = self.wave_count - self.spawn_q + 1
                kind = "mcqueen" if number % 5 == 0 else "normal"
                self.enemies.append(Enemy(self.wave_hp, self.wave_speed, self.wave_gold, kind))
                self.spawn_q -= 1
                self.spawn_timer = 25
        for enemy in self.enemies:
            enemy.update()
            if enemy.reached_end:
                self.lives -= enemy.life_damage
        for tower in self.towers:
            self.projectiles.extend(tower.update(self.enemies))
        for projectile in self.projectiles:
            projectile.update(self.enemies if projectile.piercing else None)
        self.projectiles = [projectile for projectile in self.projectiles if projectile.alive]
        survivors = []
        for enemy in self.enemies:
            if enemy.alive:
                survivors.append(enemy)
            elif not enemy.reached_end:
                self.gold += enemy.gold
        self.enemies = survivors
        if self.next_wave_timer is not None:
            self.next_wave_timer -= 1
            if self.next_wave_timer <= 0:
                self.start_wave()
        if self.wave_active and self.spawn_q == 0 and not self.enemies:
            self.wave_active = False
            self.next_wave_timer = NEXT_WAVE_DELAY
        if self.lives <= 0:
            self.game_over = True
            self.pending_cell = None
            self.delete_cell = None
            self.next_wave_timer = None

    def buildable_cell(self, cell):
        col, row = cell
        return (
            0 <= col < GRID_COLS
            and 0 <= row < GRID_ROWS
            and col * CELL < WALL_LEFT
            and cell not in PATH_CELLS
            and all((tower.col, tower.row) != cell for tower in self.towers)
        )

    def handle_click(self, position, button):
        if button != 1 or self.game_over:
            return
        if self.can_start_wave and math.hypot(position[0] - 44, position[1] - 260) <= 26:
            self.start_wave()
            self.delete_cell = None
            return
        if position[1] >= HEIGHT - UI_BAR_HEIGHT:
            for kind, rect in SHOP_CARDS:
                if rect.collidepoint(position):
                    self.selected = kind
            self.delete_cell = None
            return
        if self.delete_cell:
            col, row = self.delete_cell
            center = (col * CELL + CELL // 2, row * CELL + CELL // 2)
            if math.hypot(position[0] - center[0], position[1] - center[1]) <= 28:
                tower = next(tower for tower in self.towers if (tower.col, tower.row) == (col, row))
                self.gold += TOWER_TYPES[tower.kind]["cost"] // 2
                self.towers.remove(tower)
                self.delete_cell = None
                return
            self.delete_cell = None
        col, row = position[0] // CELL, position[1] // CELL
        cell = (col, row)
        for tower in self.towers:
            if (tower.col, tower.row) == cell:
                self.pending_cell = None
                self.delete_cell = cell
                return
        if not self.buildable_cell(cell):
            return
        if self.pending_cell != cell:
            self.pending_cell = cell
            return
        cost = TOWER_TYPES[self.selected]["cost"]
        if self.gold >= cost:
            self.towers.append(Tower(col, row, self.selected))
            self.gold -= cost
            self.pending_cell = None

    def draw(self, surface):
        draw_field(surface)
        draw_path(surface)
        surface.blit(BRICK_WALL, (0, 0))
        if self.pending_cell and self.buildable_cell(self.pending_cell):
            col, row = self.pending_cell
            stats = TOWER_TYPES[self.selected]
            center = (col * CELL + CELL // 2, row * CELL + CELL // 2)
            draw_tower_range(surface, center, stats)
            rect = pygame.Rect(col * CELL + 4, row * CELL + 4, CELL - 8, CELL - 8)
            pygame.draw.rect(surface, stats["color"], rect, 3, border_radius=7)
        for tower in self.towers:
            show_range = self.hover_cell == (tower.col, tower.row)
            tower.draw(surface, show_range)
        for enemy in self.enemies:
            enemy.draw(surface)
        for projectile in self.projectiles:
            projectile.draw(surface)
        self.draw_delete_menu(surface)
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((*OVERLAY, 185))
            surface.blit(overlay, (0, 0))
            draw_panel(surface, pygame.Rect(WIDTH // 2 - 300, HEIGHT // 2 - 75, 600, 150), PANEL, 245, DANGER)
            draw_centered_text(surface, minecraft_font(28), "GAME OVER", DANGER_TEXT, (WIDTH // 2, HEIGHT // 2 - 22))
            draw_centered_text(surface, minecraft_font(24), "Click to restart  ·  Esc for menu", TEXT, (WIDTH // 2, HEIGHT // 2 + 20))

    def draw_delete_menu(self, surface):
        if not self.delete_cell:
            return
        col, row = self.delete_cell
        center = (col * CELL + CELL // 2, row * CELL + CELL // 2)
        pygame.draw.circle(surface, DANGER, center, 28)
        pygame.draw.circle(surface, TEXT, center, 28, 2)
        draw_centered_text(surface, minecraft_font(12), "DELETE", TEXT, center)


class Hud:
    def __init__(self, font, small_font):
        self.font = font
        self.small_font = small_font
        self.start_surf = small_font.render("START", True, TEXT)
        self.gold_pos = (SAFE_MARGIN, HEIGHT - 80)
        self.lives_pos = (SAFE_MARGIN, HEIGHT - 40)
        self.wave_pos = (220, HEIGHT - 80)
        self.cards = {kind: self.make_card(info) for kind, info in TOWER_TYPES.items()}

    def make_card(self, info):
        card = pygame.Surface(SHOP_CARD_SIZE)
        card.fill(info["color"])
        card.blit(self.small_font.render(info["name"], True, INK), (6, 6))
        card.blit(self.small_font.render(str(info["cost"]), True, INK), (6, 44))
        return card

    def draw(self, surface, game):
        surface.blit(self.font.render(f"Gold: {game.gold}", True, ACCENT), self.gold_pos)
        surface.blit(self.font.render(f"Lives: {max(0, game.lives)}", True, TEXT), self.lives_pos)
        surface.blit(self.font.render(f"Wave: {game.wave}", True, TEXT), self.wave_pos)
        for kind, rect in SHOP_CARDS:
            surface.blit(self.cards[kind], rect)
            border = ACCENT if kind == game.selected else TOWER_TYPES[kind]["color"]
            pygame.draw.rect(surface, border, rect, 2)


class App:
    def __init__(self, screen=None):
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.screen = screen or pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.volume = 60
        self.dragging_volume = False
        self.mouse_pos = (0, 0)
        self.title_font = minecraft_font(42)
        self.button_font = minecraft_font(18)
        self.font = minecraft_font(16)
        self.hud = Hud(minecraft_font(24), minecraft_font(10))
        self.play_button = PLAY_BUTTON
        self.settings_button = SETTINGS_BUTTON
        self.back_button = BACK_BUTTON
        self.volume_track = VOLUME_TRACK
        self.volume_hit = VOLUME_HIT
        self.pause_items = pause_items()
        self.screens = [ScreenState.MENU]
        self.game = Game()

    @property
    def state(self):
        return self.screens[-1]

    @state.setter
    def state(self, screen):
        self.screens = [screen]

    def push(self, screen):
        self.screens.append(screen)

    def pop(self):
        if len(self.screens) > 1:
            self.screens.pop()

    def switch(self, screen):
        self.state = screen

    def set_volume(self, value):
        self.volume = max(0, min(100, int(value)))

    def set_volume_from_x(self, x):
        track = self.volume_track
        self.set_volume(round((x - track.left) / track.width * 100))

    def to_virtual(self, pos):
        window = pygame.display.get_surface()
        if window is None:
            return pos
        dst = letterbox_rect(window.get_size())
        scale = dst.width / WIDTH
        return ((pos[0] - dst.x) / scale, (pos[1] - dst.y) / scale)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.VIDEORESIZE:
            if pygame.display.get_surface() is self.screen and self.screen is not None:
                self.screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
            return
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = self.to_virtual(event.pos)
            if self.state is ScreenState.SETTINGS and self.dragging_volume:
                self.set_volume_from_x(self.mouse_pos[0])
            elif self.state is ScreenState.GAME:
                col, row = self.mouse_pos[0] // CELL, self.mouse_pos[1] // CELL
                self.game.hover_cell = (
                    (col, row)
                    if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS and self.mouse_pos[0] < WALL_LEFT
                    else None
                )
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.escape()
            elif event.key == pygame.K_SPACE and self.state is ScreenState.GAME:
                self.game.start_wave()
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.click(self.to_virtual(event.pos))
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_volume = False

    def escape(self):
        if self.state is ScreenState.GAME:
            if self.game.game_over:
                self.switch(ScreenState.MENU)
            else:
                self.push(ScreenState.PAUSE)
        elif self.state in (ScreenState.PAUSE, ScreenState.SETTINGS):
            self.dragging_volume = False
            self.pop()

    def click(self, pos):
        if self.state is ScreenState.MENU:
            if self.play_button.collidepoint(pos):
                if self.game.game_over:
                    self.game.reset()
                self.push(ScreenState.GAME)
            elif self.settings_button.collidepoint(pos):
                self.push(ScreenState.SETTINGS)
        elif self.state is ScreenState.SETTINGS:
            if self.back_button.collidepoint(pos):
                self.pop()
            elif self.volume_hit.collidepoint(pos):
                self.dragging_volume = True
                self.set_volume_from_x(pos[0])
        elif self.state is ScreenState.PAUSE:
            resume, settings, menu = self.pause_items
            if resume.collidepoint(pos):
                self.pop()
            elif settings.collidepoint(pos):
                self.push(ScreenState.SETTINGS)
            elif menu.collidepoint(pos):
                self.switch(ScreenState.MENU)
        elif self.game.game_over:
            self.game.reset()
        else:
            self.game.handle_click(pos, 1)

    def update(self):
        if self.state is ScreenState.GAME:
            self.game.update()

    def draw(self):
        if self.state is ScreenState.MENU:
            self.draw_menu(self.canvas)
        elif self.state is ScreenState.SETTINGS:
            self.draw_settings(self.canvas)
        else:
            self.game.draw(self.canvas)
            self.draw_game_ui(self.canvas)
            if self.state is ScreenState.PAUSE:
                self.draw_pause(self.canvas)
        self.present()

    def present(self):
        window = pygame.display.get_surface()
        if window is None:
            self.screen.blit(self.canvas, (0, 0))
            return
        if window.get_size() == (WIDTH, HEIGHT):
            window.blit(self.canvas, (0, 0))
        else:
            window.fill(LETTERBOX)
            dst = letterbox_rect(window.get_size())
            window.blit(pygame.transform.smoothscale(self.canvas, dst.size), dst)
        if window is self.screen:
            pygame.display.flip()

    def run(self, max_frames=None):
        frames = 0
        while self.running and (max_frames is None or frames < max_frames):
            self.clock.tick(FPS)
            for event in pygame.event.get():
                self.handle_event(event)
            self.update()
            self.draw()
            frames += 1

    def draw_menu(self, surface):
        draw_vertical_gradient(surface, BG_TOP, BG_BOTTOM)
        draw_centered_text(surface, self.title_font, "TOWER DEFENCE", TEXT, MENU_TITLE_POS)
        draw_centered_text(surface, self.font, "BUILD  ·  DEFEND  ·  SURVIVE", TEXT_MUTED, MENU_SUBTITLE_POS)
        center = self.play_button.center
        pygame.draw.circle(
            surface, ACCENT_HOVER if self.play_button.collidepoint(self.mouse_pos) else ACCENT, center, 62
        )
        pygame.draw.circle(surface, INK, center, 62, 2)
        draw_play_icon(surface, center, 34)
        draw_centered_text(surface, self.button_font, "PLAY", TEXT, (center[0], center[1] + 90))
        settings_hovered = self.settings_button.collidepoint(self.mouse_pos)
        if settings_hovered:
            draw_hover_highlight(surface, self.settings_button)
        pygame.draw.rect(surface, PANEL_LIGHT if settings_hovered else INK, self.settings_button, border_radius=14)
        pygame.draw.rect(
            surface, ACCENT if settings_hovered else PANEL_BORDER, self.settings_button, 2, border_radius=14
        )
        draw_gear_icon(surface, self.settings_button.center, 20)
        draw_centered_text(surface, self.font, "SETTINGS", TEXT_MUTED, MENU_SETTINGS_POS)
        draw_centered_text(
            surface, self.font, "Press the play button to enter the battlefield", TEXT_MUTED, MENU_HINT_POS
        )

    def draw_settings(self, surface):
        draw_vertical_gradient(surface, BG_TOP, BG_BOTTOM)
        draw_panel(surface, SETTINGS_PANEL, PANEL, 235, PANEL_BORDER)
        draw_text(surface, self.title_font, "SETTINGS", TEXT, SETTINGS_TITLE_POS)
        draw_text(surface, self.font, "AUDIO", TEXT_MUTED, SETTINGS_AUDIO_POS)
        draw_text(surface, self.font, f"MASTER VOLUME   {self.volume}%", TEXT, SETTINGS_VOLUME_POS)
        track = self.volume_track
        if self.dragging_volume or self.volume_hit.collidepoint(self.mouse_pos):
            draw_hover_highlight(surface, self.volume_hit)
        fraction = track.width * self.volume // 100
        pygame.draw.rect(surface, PANEL_BORDER, track.inflate(0, 10), border_radius=8)
        pygame.draw.rect(surface, ACCENT, (track.left, track.top, fraction, track.height), border_radius=8)
        knob = (track.left + fraction, track.centery)
        pygame.draw.circle(surface, TEXT, knob, 12)
        pygame.draw.circle(surface, ACCENT_DARK, knob, 6)
        if self.back_button.collidepoint(self.mouse_pos):
            draw_hover_highlight(surface, self.back_button)
        hovered = self.back_button.collidepoint(self.mouse_pos)
        pygame.draw.rect(surface, PANEL_LIGHT if hovered else INK, self.back_button, border_radius=10)
        pygame.draw.rect(surface, ACCENT if hovered else PANEL_BORDER, self.back_button, 1, border_radius=10)
        draw_text(surface, self.font, "<-  BACK", TEXT, (self.back_button.x + 18, self.back_button.y + 12))
        draw_centered_text(
            surface, self.font, "Drag the slider to set the volume  ·  Esc back", TEXT_MUTED, SETTINGS_HINT_POS
        )

    def draw_pause(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((*OVERLAY, 160))
        surface.blit(overlay, (0, 0))
        panel = PAUSE_PANEL
        draw_panel(surface, panel, PANEL_LIGHT, 245, ACCENT)
        draw_centered_text(surface, self.title_font, "PAUSED", TEXT, (WIDTH // 2, panel.top + 40))
        for rect, label in zip(self.pause_items, PAUSE_LABELS):
            if rect.collidepoint(self.mouse_pos):
                draw_hover_highlight(surface, rect)
            pygame.draw.rect(surface, PANEL_LIGHT if rect.collidepoint(self.mouse_pos) else INK, rect, border_radius=8)
            pygame.draw.rect(surface, TEXT_MUTED, rect, 1, border_radius=8)
            draw_centered_text(surface, self.button_font, label, TEXT, rect.center)

    def draw_game_ui(self, surface):
        pygame.draw.rect(surface, INK, (0, PLAYFIELD_HEIGHT, WIDTH, UI_BAR_HEIGHT))
        self.hud.draw(surface, self.game)
        if self.game.can_start_wave:
            center = (44, 260)
            pygame.draw.circle(surface, ACCENT, center, 28)
            pygame.draw.circle(surface, INK, center, 28, 2)
            draw_play_icon(surface, center, 20)
            surface.blit(self.hud.start_surf, (79, 250))
            if self.game.next_wave_timer is not None:
                seconds = math.ceil(self.game.next_wave_timer / FPS)
                draw_centered_text(surface, self.button_font, f"{seconds}", ACCENT, (center[0], center[1] - 48))

def main():
    pygame.init()
    pygame.display.set_caption("Tower Defence")
    app = App()
    app.run()
    pygame.quit()

if __name__ == "__main__":
    main()
