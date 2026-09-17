"""A small tower-defence game made with Pygame.

Run it with: python ui.py
"""

from enum import Enum, auto
from functools import lru_cache
import math
from pathlib import Path

import pygame


WIDTH, HEIGHT = 1000, 720
FPS = 60
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
LETTERBOX = (5, 5, 8)
# 4% of the short edge — desktop stand-in for TV overscan / phone notch reserve.
SAFE_MARGIN = int(0.04 * min(WIDTH, HEIGHT))
DIRECTION_KEYS = {
    pygame.K_UP: "up",
    pygame.K_w: "up",
    pygame.K_DOWN: "down",
    pygame.K_s: "down",
    pygame.K_LEFT: "left",
    pygame.K_a: "left",
    pygame.K_RIGHT: "right",
    pygame.K_d: "right",
}

# Palette follows td-ui.py for field, path, panel, and tower colors.
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PANEL_LIGHT = (35, 35, 35)
GREEN = (0, 100, 0)
GREEN_DARK = (0, 70, 0)
GREEN_HOVER = (60, 170, 60)
PATH = (176, 163, 44)
BLUE = (0, 0, 200)
ORANGE = (255, 229, 84)
GOLD = (255, 230, 20)
RED = (200, 0, 0)
GRAY = (145, 145, 145)
DARK_GRAY = (80, 80, 80)
BRICK_RED = (139, 69, 43)
DARK_BRICK = (91, 54, 39)
BRICK_HIGHLIGHT = (171, 91, 54)
WALL_BASE = (116, 64, 43)

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
        "color": BLUE,
        "cost": 100,
    },
    "cannon": {
        "name": "Cannon",
        "damage": 75,
        "fire_rate": 60,
        "range": 120,
        "color": ORANGE,
        "cost": 200,
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


class Layout:
    """Put things on screen without guessing every pixel."""

    @staticmethod
    def anchor_point(area, anchor, offset=(0, 0)):
        x_map = {"left": area.left, "center": area.centerx, "right": area.right}
        y_map = {"top": area.top, "middle": area.centery, "bottom": area.bottom}
        return (x_map[anchor[0]] + offset[0], y_map[anchor[1]] + offset[1])

    @classmethod
    def place(cls, area, anchor, width, height, offset=(0, 0)):
        rect = pygame.Rect(0, 0, width, height)
        rect.center = cls.anchor_point(area, anchor, offset)
        return rect

    @staticmethod
    def hbox(area, widths, height, gap):
        """Flow children left-to-right inside area, centered as a group."""
        total = sum(widths) + gap * (len(widths) - 1)
        x = area.left + (area.width - total) // 2
        rects = []
        for width in widths:
            rects.append(pygame.Rect(x, area.top + (area.height - height) // 2, width, height))
            x += width + gap
        return rects

    @staticmethod
    def vbox(area, count, width, height, gap):
        """Flow children top-to-bottom inside area, centered as a group."""
        total = count * height + gap * (count - 1)
        y = area.top + (area.height - total) // 2
        rects = []
        for _ in range(count):
            rects.append(pygame.Rect(area.left + (area.width - width) // 2, y, width, height))
            y += height + gap
        return rects


def safe_rect(area, margin=SAFE_MARGIN):
    """Leave space around the edge for important buttons and text."""
    return area.inflate(-2 * margin, -2 * margin)


def letterbox_rect(window_size, reference_size):
    """Fit the game inside any window without stretching it."""
    scale = min(window_size[0] / reference_size[0], window_size[1] / reference_size[1])
    width = int(reference_size[0] * scale)
    height = int(reference_size[1] * scale)
    return pygame.Rect(
        (window_size[0] - width) // 2, (window_size[1] - height) // 2, width, height
    )


def shop_cards():
    """Return the two shop card positions."""
    width, height = SHOP_CARD_SIZE
    area = pygame.Rect(0, 0, 2 * width + SHOP_CARD_GAP, height)
    area.midbottom = Layout.anchor_point(SCREEN_RECT, ("center", "bottom"), (0, -12))
    return list(zip(TOWER_TYPES, Layout.hbox(area, [width] * 2, height, SHOP_CARD_GAP)))


def settings_panel_rect():
    """Return the settings panel position."""
    safe = safe_rect(SCREEN_RECT)
    panel = pygame.Rect(0, 0, safe.width - 80, 400)
    panel.midtop = Layout.anchor_point(safe, ("center", "top"), (0, 14))
    return panel


def clamp(value, low, high):
    return max(low, min(high, value))


@lru_cache
def minecraft_font(size):
    if FONT_PATH.exists():
        return pygame.font.Font(str(FONT_PATH), size)
    return pygame.font.SysFont("arial", size)


def draw_text(surface, font, text, color, position, shadow=BLACK):
    x, y = position
    if shadow:
        shadow_surface = font.render(text, True, shadow)
        surface.blit(shadow_surface, (x + 2, y + 2))
    surface.blit(font.render(text, True, color), (x, y))


def draw_centered_text(surface, font, text, color, center, shadow=BLACK):
    text_surface = font.render(text, True, color)
    position = (center[0] - text_surface.get_width() // 2, center[1] - text_surface.get_height() // 2)
    draw_text(surface, font, text, color, position, shadow)


def draw_vertical_gradient(surface, top, bottom):
    height = surface.get_height()
    for y in range(height):
        ratio = y / max(1, height - 1)
        color = tuple(int(top[i] + (bottom[i] - top[i]) * ratio) for i in range(3))
        pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))


def draw_panel(surface, rect, color=BLACK, alpha=225, border=DARK_GRAY, radius=14):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (*color, alpha), panel.get_rect(), border_radius=radius)
    if border:
        pygame.draw.rect(panel, (*border, min(255, alpha + 20)), panel.get_rect(), 1, border_radius=radius)
    surface.blit(panel, rect.topleft)


def draw_play_icon(surface, center, radius, color=WHITE):
    cx, cy = center
    points = [
        (cx - radius // 4, cy - radius // 2),
        (cx - radius // 4, cy + radius // 2),
        (cx + radius // 2, cy),
    ]
    pygame.draw.polygon(surface, color, points)


def draw_gear_icon(surface, center, radius, color=WHITE):
    cx, cy = center
    for angle in range(0, 360, 45):
        radians = math.radians(angle)
        inner = radius * 0.65
        outer = radius * 1.05
        start = (cx + math.cos(radians) * inner, cy + math.sin(radians) * inner)
        end = (cx + math.cos(radians) * outer, cy + math.sin(radians) * outer)
        pygame.draw.line(surface, color, start, end, max(3, radius // 4))
    pygame.draw.circle(surface, color, center, int(radius * 0.68))
    pygame.draw.circle(surface, BLACK, center, int(radius * 0.3))


def draw_focus_highlight(surface, rect):
    pygame.draw.rect(surface, GOLD, rect.inflate(14, 14), 4, border_radius=12)


class FocusItem:
    def __init__(self, rect, label, font, action=None):
        self.rect = rect
        self.label = label
        self.action = action or (lambda: None)
        self.label_surf = font.render(label, True, WHITE)


class Focus:
    """Remember which button keyboard or mouse is using."""

    def __init__(self, items, neighbors, initial=0):
        self.items = items
        self.neighbors = neighbors
        self.index = initial

    @property
    def current(self):
        return self.items[self.index]

    def move(self, direction):
        target = self.neighbors.get(self.index, {}).get(direction)
        if target is not None:
            self.index = target

    def hover(self, pos):
        for index, item in enumerate(self.items):
            if item.rect.collidepoint(pos):
                self.index = index
                return True
        return False

    def activate(self):
        return self.current.action()


def build_brick_wall(size):
    """Build a straight brick wall outside the road and buildable grid."""
    width, height = size
    wall = pygame.Surface(size, pygame.SRCALPHA)
    wall_width = min(WALL_WIDTH, width)
    left = width - wall_width
    pygame.draw.rect(wall, WALL_BASE, (left, 0, wall_width, height))

    brick_height = 32
    brick_width = 64
    for row, y in enumerate(range(0, height, brick_height)):
        offset = 0 if row % 2 == 0 else brick_width // 2
        pygame.draw.line(wall, BLACK, (left, y), (width, y), 3)
        for column, x in enumerate(range(left - brick_width + offset, width, brick_width)):
            brick_left = max(left + 2, x + 2)
            brick_right = min(width - 2, x + brick_width - 2)
            if brick_right <= brick_left:
                continue
            color = (DARK_BRICK, BRICK_RED, BRICK_HIGHLIGHT)[(row + column) % 3]
            pygame.draw.rect(wall, color, (brick_left, y + 2, brick_right - brick_left, brick_height - 4))
            pygame.draw.line(
                wall,
                tuple(min(255, channel + 24) for channel in color),
                (brick_left + 3, y + 4),
                (brick_right - 3, y + 4),
                1,
            )
        for seam_x in range(left + offset, width, brick_width):
            pygame.draw.line(wall, BLACK, (seam_x, y), (seam_x, min(height, y + brick_height)), 3)

    pygame.draw.rect(wall, BLACK, (left, 0, wall_width, height), 2)
    return wall


BRICK_WALL = build_brick_wall((WIDTH, PLAYFIELD_HEIGHT))


def draw_field(surface):
    surface.fill(GREEN)
    for y in range(0, PLAYFIELD_HEIGHT, CELL):
        pygame.draw.line(surface, BLACK, (0, y), (WIDTH, y), 1)
    for x in range(0, WIDTH + 1, CELL):
        pygame.draw.line(surface, BLACK, (x, 0), (x, PLAYFIELD_HEIGHT), 1)


def draw_path(surface):
    for col, row in PATH_CELLS:
        rect = pygame.Rect(col * CELL, row * CELL, CELL, CELL)
        pygame.draw.rect(surface, PATH, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)


class Enemy:
    def __init__(self, hp, speed, gold):
        self.max_hp = hp
        self.hp = hp
        self.speed = speed
        self.gold = gold
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
        pygame.draw.circle(surface, RED, center, 15)
        pygame.draw.circle(surface, (247, 124, 92), center, 9)
        bar = pygame.Rect(int(self.x - 12), int(self.y - 25), 24, 4)
        pygame.draw.rect(surface, BLACK, bar.inflate(2, 2))
        pygame.draw.rect(surface, GREEN, (bar.x, bar.y, int(bar.width * max(0, self.hp / self.max_hp)), bar.height))


class Projectile:
    def __init__(self, x, y, target, damage, *, piercing=False, size=3, vx=0, vy=0, color=GOLD, max_range=None):
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
                        color=ORANGE,
                        max_range=self.stats["range"],
                    )
                )
            return projectiles
        return [Projectile(self.x, self.y, target, self.stats["damage"], max_range=self.stats["range"])]

    def draw(self, surface, show_range=False):
        rect = pygame.Rect(self.col * CELL + 4, self.row * CELL + 4, CELL - 8, CELL - 8)
        pygame.draw.rect(surface, self.stats["color"], rect, border_radius=7)
        pygame.draw.rect(surface, BLACK, rect, 2, border_radius=7)
        pygame.draw.circle(surface, WHITE, (self.x, self.y), 3)
        if show_range:
            range_layer = pygame.Surface((self.stats["range"] * 2,) * 2, pygame.SRCALPHA)
            pygame.draw.circle(range_layer, (*self.stats["color"], 35), (self.stats["range"],) * 2, self.stats["range"])
            pygame.draw.circle(range_layer, (*self.stats["color"], 150), (self.stats["range"],) * 2, self.stats["range"], 2)
            surface.blit(range_layer, (self.x - self.stats["range"], self.y - self.stats["range"]))


class Game:
    """Rules and objects for one game."""

    def __init__(self):
        self.events = []
        self.reset()

    def emit(self, name):
        self.events.append(name)

    def drain_events(self):
        events, self.events = self.events, []
        return events

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
        self.wave_conf = None
        self.hover_cell = None
        self.delete_cell = None
        self.game_over = False
        for name in ("gold_changed", "lives_changed", "wave_changed"):
            self.emit(name)

    def start_wave(self):
        if self.wave_active or self.game_over:
            return
        self.wave += 1
        scale = 1 + (self.wave - 1) * 0.35
        self.wave_conf = {
            "count": int(5 * scale),
            "hp": int(50 * scale),
            "speed": 1.5 + (self.wave - 1) * 0.05,
            "gold": int(8 + (self.wave - 1) * 1.5),
        }
        self.spawn_q = self.wave_conf["count"]
        self.spawn_timer = 0
        self.wave_active = True
        self.emit("wave_changed")

    def update(self):
        if self.game_over:
            return
        if self.wave_active and self.spawn_q:
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                config = self.wave_conf
                self.enemies.append(Enemy(config["hp"], config["speed"], config["gold"]))
                self.spawn_q -= 1
                self.spawn_timer = 25

        for enemy in self.enemies:
            enemy.update()
            if enemy.reached_end:
                self.lives -= 1
                self.emit("lives_changed")

        for tower in self.towers:
            self.projectiles.extend(tower.update(self.enemies))
        for projectile in self.projectiles:
            projectile.update(self.enemies if projectile.piercing else None)
        self.projectiles = [projectile for projectile in self.projectiles if projectile.alive]

        gold_gained = False
        survivors = []
        for enemy in self.enemies:
            if enemy.alive:
                survivors.append(enemy)
            elif not enemy.reached_end:
                self.gold += enemy.gold
                gold_gained = True
        if gold_gained:
            self.emit("gold_changed")
        self.enemies = survivors

        if self.wave_active and self.spawn_q == 0 and not self.enemies:
            self.wave_active = False
        if self.lives <= 0:
            self.game_over = True

    def handle_click(self, position, button):
        if button != 1 or self.game_over:
            return
        if not self.wave_active and math.hypot(position[0] - 44, position[1] - 260) <= 26:
            self.start_wave()
            self.delete_cell = None
            return
        if position[1] >= HEIGHT - UI_BAR_HEIGHT:
            for kind, rect in shop_cards():
                if rect.collidepoint(position):
                    self.selected = kind
            self.delete_cell = None
            return
        if self.delete_cell:
            col, row = self.delete_cell
            center = (col * CELL + CELL // 2, row * CELL + CELL // 2)
            if math.hypot(position[0] - center[0], position[1] - center[1]) <= 28:
                self.towers = [tower for tower in self.towers if (tower.col, tower.row) != (col, row)]
            self.delete_cell = None
            return
        col, row = position[0] // CELL, position[1] // CELL
        if not (0 <= col < GRID_COLS and 0 <= row < GRID_ROWS):
            return
        if position[0] >= WALL_LEFT:
            return
        for tower in self.towers:
            if (tower.col, tower.row) == (col, row):
                self.delete_cell = (col, row)
                return
        if (col, row) in PATH_CELLS:
            return
        cost = TOWER_TYPES[self.selected]["cost"]
        if self.gold >= cost:
            self.towers.append(Tower(col, row, self.selected))
            self.gold -= cost
            self.emit("gold_changed")

    def draw(self, surface):
        draw_field(surface)
        draw_path(surface)
        surface.blit(BRICK_WALL, (0, 0))
        for tower in self.towers:
            show_range = self.hover_cell == (tower.col, tower.row)
            tower.draw(surface, show_range)
        for enemy in self.enemies:
            enemy.draw(surface)
        for projectile in self.projectiles:
            projectile.draw(surface)
        self._draw_delete_menu(surface)
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((5, 10, 10, 185))
            surface.blit(overlay, (0, 0))
            draw_panel(surface, pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 75, 300, 150), PANEL_LIGHT, 245, RED)
            draw_centered_text(surface, minecraft_font(28), "GAME OVER", RED, (WIDTH // 2, HEIGHT // 2 - 22))
            draw_centered_text(surface, minecraft_font(24), "Press R or Enter to restart", WHITE, (WIDTH // 2, HEIGHT // 2 + 20))

    def _draw_delete_menu(self, surface):
        if not self.delete_cell:
            return
        col, row = self.delete_cell
        center = (col * CELL + CELL // 2, row * CELL + CELL // 2)
        pygame.draw.circle(surface, RED, center, 28)
        pygame.draw.circle(surface, WHITE, center, 28, 2)
        draw_centered_text(surface, minecraft_font(12), "DELETE", WHITE, center, None)


class Hud:
    """Draw score, lives, wave, and tower buttons."""

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
        self.cards = {kind: self._make_card(kind, info) for kind, info in TOWER_TYPES.items()}

    def _make_card(self, kind, info):
        card = pygame.Surface(SHOP_CARD_SIZE)
        card.fill(info["color"])
        card.blit(self.small_font.render(info["name"], True, BLACK), (6, 6))
        card.blit(self.small_font.render(str(info["cost"]), True, BLACK), (6, 44))
        return card

    def handle(self, events, gold, lives, wave):
        for name in events:
            if name == "gold_changed":
                self.gold_surf = self.font.render(f"Gold: {gold}", True, GOLD)
            elif name == "lives_changed":
                self.lives_surf = self.font.render(f"Lives: {lives}", True, WHITE)
            elif name == "wave_changed":
                self.wave_surf = self.font.render(f"Wave: {wave}", True, WHITE)

    def draw(self, surface, selected):
        if self.gold_surf:
            surface.blit(self.gold_surf, self.gold_pos)
        if self.lives_surf:
            surface.blit(self.lives_surf, self.lives_pos)
        if self.wave_surf:
            surface.blit(self.wave_surf, self.wave_pos)
        for kind, rect in shop_cards():
            surface.blit(self.cards[kind], rect)
            border = WHITE if kind == selected else TOWER_TYPES[kind]["color"]
            pygame.draw.rect(surface, border, rect, 2)


class App:
    def __init__(self, screen=None):
        self.canvas = pygame.Surface((WIDTH, HEIGHT))
        self.screen = screen
        if screen is None:
            self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.volume = 60
        self.dragging_volume = False
        self.mouse_pos = (0, 0)

        self.title_font = minecraft_font(42)
        self.button_font = minecraft_font(18)
        self.font = minecraft_font(16)
        self.hud = Hud(minecraft_font(24), minecraft_font(10))

        # Layout-derived control rects (anchored, not hardcoded).
        self.play_button = Layout.place(SCREEN_RECT, ("center", "middle"), 124, 124, offset=(0, -84))
        self.settings_button = Layout.place(SCREEN_RECT, ("left", "middle"), 64, 64, offset=(64, 0))
        self.back_button = pygame.Rect(
            *Layout.anchor_point(SCREEN_RECT, ("left", "top"), (58, 22)), 116, 44
        )
        self.volume_track = Layout.place(settings_panel_rect(), ("center", "top"), 480, 8, offset=(0, 182))
        self.pause_items = Layout.vbox(SCREEN_RECT, 3, 260, 52, 16)

        # Screens as a stack: push (pause over game), pop (resume).
        self.screens = [ScreenState.MENU]
        self.focus = None
        self._rebuild_focus()

        self.game = Game()

    @property
    def state(self):
        return self.screens[-1]

    @state.setter
    def state(self, screen):
        self.screens = [screen]
        self._rebuild_focus()

    def push(self, screen):
        self.screens.append(screen)
        self._rebuild_focus()

    def pop(self):
        if len(self.screens) > 1:
            self.screens.pop()
        self._rebuild_focus()

    def switch(self, screen):
        self.state = screen

    def _rebuild_focus(self):
        item_font = self.button_font
        if self.state is ScreenState.MENU:
            items = [
                FocusItem(self.play_button, "PLAY", item_font, lambda: self.push(ScreenState.GAME)),
                FocusItem(self.settings_button, "SETTINGS", item_font, lambda: self.push(ScreenState.SETTINGS)),
            ]
            self.focus = Focus(items, {0: {"down": 1, "right": 1}, 1: {"up": 0, "left": 0}})
        elif self.state is ScreenState.SETTINGS:
            track_hit = self.volume_track.inflate(40, 30)
            items = [
                FocusItem(track_hit, "VOLUME", item_font),
                FocusItem(self.back_button, "BACK", item_font, lambda: self.pop()),
            ]
            self.focus = Focus(items, {0: {"down": 1, "right": 1}, 1: {"up": 0, "left": 0}})
        elif self.state is ScreenState.PAUSE:
            resume, settings, menu = self.pause_items
            items = [
                FocusItem(resume, "RESUME", item_font, lambda: self.pop()),
                FocusItem(settings, "SETTINGS", item_font, lambda: self.push(ScreenState.SETTINGS)),
                FocusItem(menu, "MAIN MENU", item_font, lambda: self.switch(ScreenState.MENU)),
            ]
            self.focus = Focus(items, {0: {"down": 1}, 1: {"up": 0, "down": 2}, 2: {"up": 1}})
        else:
            self.focus = None

    def set_volume(self, value):
        self.volume = int(clamp(int(value), 0, 100))

    def set_volume_from_x(self, x):
        ratio = (x - self.volume_track.left) / self.volume_track.width
        self.set_volume(round(clamp(ratio, 0, 1) * 100))

    @staticmethod
    def _is_activate(key):
        return key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_j)

    def _move_focus(self, key):
        direction = DIRECTION_KEYS.get(key)
        if direction:
            self.focus.move(direction)
        elif self._is_activate(key):
            self.focus.activate()

    def _click_focus(self, pos):
        if self.focus.hover(pos):
            self.focus.activate()

    def _to_virtual(self, pos):
        window = pygame.display.get_surface()
        if window is None:
            return pos
        dst = letterbox_rect(window.get_size(), (WIDTH, HEIGHT))
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
            self.mouse_pos = self._to_virtual(event.pos)
            if self.state is ScreenState.SETTINGS and self.dragging_volume:
                self.set_volume_from_x(self.mouse_pos[0])
            elif self.focus is not None:
                self.focus.hover(self.mouse_pos)
            elif self.state is ScreenState.GAME:
                col, row = self.mouse_pos[0] // CELL, self.mouse_pos[1] // CELL
                self.game.hover_cell = (
                    (col, row)
                    if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS and self.mouse_pos[0] < WALL_LEFT
                    else None
                )
            return
        if self.state is ScreenState.MENU:
            self._handle_focus_screen(event)
        elif self.state is ScreenState.SETTINGS:
            self._handle_settings_event(event)
        elif self.state is ScreenState.PAUSE:
            self._handle_focus_screen(event, esc_back=True)
        else:
            self._handle_game_event(event)

    def _handle_focus_screen(self, event, esc_back=False):
        if event.type == pygame.KEYDOWN:
            if esc_back and event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.pop()
            else:
                self._move_focus(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._click_focus(self._to_virtual(event.pos))

    def _handle_settings_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.dragging_volume = False
                self.pop()
            elif self.focus.index == 0 and event.key in (
                pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d
            ):
                delta = 5 if event.key in (pygame.K_RIGHT, pygame.K_d) else -5
                self.set_volume(self.volume + delta)
            else:
                self._move_focus(event.key)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_volume = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = self._to_virtual(event.pos)
            self.focus.hover(pos)
            if self.back_button.collidepoint(pos):
                self.dragging_volume = False
                self.pop()
            elif self.volume_track.inflate(40, 30).collidepoint(pos):
                self.dragging_volume = True
                self.set_volume_from_x(pos[0])

    def _handle_game_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.game.game_over:
                    self.switch(ScreenState.MENU)
                else:
                    self.push(ScreenState.PAUSE)
            elif event.key == pygame.K_SPACE:
                self.game.start_wave()
            elif event.key == pygame.K_1:
                self.game.selected = "rapid"
            elif event.key == pygame.K_2:
                self.game.selected = "cannon"
            elif event.key in (pygame.K_r, pygame.K_RETURN, pygame.K_KP_ENTER) and self.game.game_over:
                self.game.reset()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.game.handle_click(self._to_virtual(event.pos), event.button)

    def update(self):
        if self.state is ScreenState.GAME:
            self.game.update()

    def draw(self):
        if self.state is ScreenState.MENU:
            self._draw_menu(self.canvas)
        elif self.state is ScreenState.SETTINGS:
            self._draw_settings(self.canvas)
        else:
            self.game.draw(self.canvas)
            self._draw_game_ui(self.canvas)
            if self.state is ScreenState.PAUSE:
                self._draw_pause(self.canvas)
        self._present()

    def _present(self):
        window = pygame.display.get_surface()
        if window is None:
            self.screen.blit(self.canvas, (0, 0))
            return
        if window.get_size() == (WIDTH, HEIGHT):
            window.blit(self.canvas, (0, 0))
        else:
            window.fill(LETTERBOX)
            dst = letterbox_rect(window.get_size(), (WIDTH, HEIGHT))
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

    def _draw_menu(self, surface):
        safe = safe_rect(SCREEN_RECT)
        draw_vertical_gradient(surface, (11, 29, 32), (20, 62, 54))
        circle_center = Layout.anchor_point(safe, ("right", "top"), (-65, 70))
        pygame.draw.circle(surface, (29, 100, 76), circle_center, 145, 2)
        pygame.draw.circle(surface, (29, 100, 76), circle_center, 105, 1)
        draw_centered_text(surface, self.title_font, "TOWER DEFENCE", WHITE, Layout.anchor_point(safe, ("center", "top"), (0, 97)))
        draw_centered_text(surface, self.font, "BUILD  ·  DEFEND  ·  SURVIVE", GRAY, Layout.anchor_point(safe, ("center", "top"), (0, 142)), None)

        focused_play = self.focus.current is self.focus.items[0]
        center = self.play_button.center
        if focused_play:
            pygame.draw.circle(surface, GOLD, center, 66, 4)
        pygame.draw.circle(surface, (4, 12, 12), (center[0] + 6, center[1] + 8), 67)
        pygame.draw.circle(surface, GREEN_HOVER if self.play_button.collidepoint(self.mouse_pos) else GREEN, center, 62)
        pygame.draw.circle(surface, WHITE, center, 62, 2)
        draw_play_icon(surface, center, 34)
        draw_centered_text(surface, self.button_font, "PLAY", WHITE, (center[0], center[1] + 90), None)

        settings_hovered = self.settings_button.collidepoint(self.mouse_pos)
        if self.focus.current is self.focus.items[1]:
            draw_focus_highlight(surface, self.settings_button)
        pygame.draw.rect(surface, GREEN_DARK if settings_hovered else BLACK, self.settings_button, border_radius=14)
        pygame.draw.rect(surface, GREEN if settings_hovered else PANEL_LIGHT, self.settings_button, 2, border_radius=14)
        draw_gear_icon(surface, self.settings_button.center, 20)
        draw_text(surface, self.font, "SETTINGS", GRAY, (self.settings_button.right + 14, self.settings_button.centery - 8), None)
        draw_centered_text(surface, self.font, "Press the play button to enter the battlefield", GRAY, Layout.anchor_point(safe, ("center", "bottom"), (0, -42)), None)

    def _draw_settings(self, surface):
        safe = safe_rect(SCREEN_RECT)
        draw_vertical_gradient(surface, (11, 29, 32), (20, 62, 54))
        panel = settings_panel_rect()
        draw_panel(surface, panel, BLACK, 235, PANEL_LIGHT)
        draw_text(surface, self.title_font, "SETTINGS", WHITE, Layout.anchor_point(panel, ("left", "top"), (32, 40)))
        draw_text(surface, self.font, "AUDIO", GRAY, Layout.anchor_point(panel, ("left", "top"), (32, 130)), None)
        draw_text(surface, self.font, f"MASTER VOLUME   {self.volume}%", WHITE, Layout.anchor_point(panel, ("left", "top"), (32, 154)), None)
        track = self.volume_track
        if self.focus.current is self.focus.items[0]:
            draw_focus_highlight(surface, track.inflate(40, 30))
        pygame.draw.rect(surface, DARK_GRAY, track.inflate(0, 10), border_radius=8)
        fraction = track.width * self.volume // 100
        pygame.draw.rect(surface, GREEN, (track.left, track.top, fraction, track.height), border_radius=8)
        knob_x = track.left + fraction
        pygame.draw.circle(surface, WHITE, (knob_x, track.centery), 12)
        pygame.draw.circle(surface, GREEN, (knob_x, track.centery), 6)
        if self.focus.current is self.focus.items[1]:
            draw_focus_highlight(surface, self.back_button)
        hovered = self.back_button.collidepoint(self.mouse_pos)
        pygame.draw.rect(surface, GREEN_DARK if hovered else PANEL_LIGHT, self.back_button, border_radius=10)
        pygame.draw.rect(surface, GREEN if hovered else GRAY, self.back_button, 1, border_radius=10)
        draw_text(surface, self.font, "‹  BACK", WHITE, (self.back_button.x + 18, self.back_button.y + 12), None)
        draw_centered_text(surface, self.font, "← → adjust · ↑ ↓ move · Enter select · Esc back", GRAY, Layout.anchor_point(safe, ("center", "bottom"), (0, -24)), None)

    def _draw_pause(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 10, 10, 160))
        surface.blit(overlay, (0, 0))
        panel = Layout.place(SCREEN_RECT, ("center", "middle"), 340, 220)
        draw_panel(surface, panel, PANEL_LIGHT, 245, GOLD)
        draw_centered_text(surface, self.title_font, "PAUSED", WHITE, (WIDTH // 2, panel.top + 40))
        for item in self.focus.items:
            if item is self.focus.current:
                draw_focus_highlight(surface, item.rect)
            pygame.draw.rect(surface, BLACK, item.rect, border_radius=8)
            pygame.draw.rect(surface, GRAY, item.rect, 1, border_radius=8)
            label_pos = (item.rect.centerx - item.label_surf.get_width() // 2, item.rect.centery - item.label_surf.get_height() // 2)
            surface.blit(item.label_surf, label_pos)

    def _draw_game_ui(self, surface):
        bar = pygame.Rect(0, HEIGHT - UI_BAR_HEIGHT, WIDTH, UI_BAR_HEIGHT)
        pygame.draw.rect(surface, BLACK, bar)
        self.hud.handle(self.game.drain_events(), self.game.gold, self.game.lives, self.game.wave)
        self.hud.draw(surface, self.game.selected)
        if not self.game.wave_active and not self.game.game_over:
            center = (44, 260)
            pygame.draw.circle(surface, GREEN, center, 28)
            pygame.draw.circle(surface, WHITE, center, 28, 2)
            draw_play_icon(surface, center, 20)
            surface.blit(self.hud.start_surf, (79, 250))


def main():
    pygame.init()
    pygame.display.set_caption("Tower Defence")
    app = App()
    app.run()
    pygame.quit()


if __name__ == "__main__":
    main()
