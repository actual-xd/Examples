"""Standalone Pygame tower-defence game.

Run with: python ui.py
"""

from enum import Enum, auto
import math
from pathlib import Path

import pygame


WIDTH, HEIGHT = 1000, 720
FPS = 60
CELL = 40
UI_BAR_HEIGHT = 120
PLAYFIELD_HEIGHT = HEIGHT - UI_BAR_HEIGHT
WALL_WIDTH = 120
WALL_LEFT = WIDTH - WALL_WIDTH
GRID_COLS = WIDTH // CELL
GRID_ROWS = PLAYFIELD_HEIGHT // CELL
FONT_PATH = Path(__file__).with_name("Minecraft.otf")

# Palette follows td-ui.py for field, path, panel, and tower colors.
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
INK = BLACK
PANEL = BLACK
PANEL_LIGHT = (35, 35, 35)
FIELD = (0, 100, 0)
FIELD_DARK = BLACK
PATH = (176, 163, 44)
PATH_EDGE = BLACK
GOLD = (255, 230, 20)
RED = (200, 0, 0)
HP_GREEN = (0, 100, 0)
GREEN = (0, 100, 0)
GREEN_DARK = (0, 70, 0)
GREEN_HOVER = (60, 170, 60)
BLUE = (0, 0, 200)
ORANGE = (255, 229, 84)
GRAY = (145, 145, 145)
DARK_GRAY = (80, 80, 80)
BRICK_RED = (139, 69, 43)
DARK_BRICK = (91, 54, 39)
BRICK_HIGHLIGHT = (171, 91, 54)
WALL_BASE = (116, 64, 43)
MORTAR = BLACK

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


def clamp(value, low, high):
    return max(low, min(high, value))


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


def draw_panel(surface, rect, color=PANEL, alpha=225, border=DARK_GRAY, radius=14):
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
    pygame.draw.circle(surface, PANEL, center, int(radius * 0.3))


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
        pygame.draw.line(wall, MORTAR, (left, y), (width, y), 3)
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
            pygame.draw.line(wall, MORTAR, (seam_x, y), (seam_x, min(height, y + brick_height)), 3)

    pygame.draw.rect(wall, BLACK, (left, 0, wall_width, height), 2)
    return wall


def draw_field(surface):
    surface.fill(FIELD)
    for y in range(0, PLAYFIELD_HEIGHT, CELL):
        pygame.draw.line(surface, FIELD_DARK, (0, y), (WIDTH, y), 1)
    for x in range(0, WIDTH + 1, CELL):
        pygame.draw.line(surface, FIELD_DARK, (x, 0), (x, PLAYFIELD_HEIGHT), 1)


def draw_path(surface):
    for col, row in PATH_CELLS:
        rect = pygame.Rect(col * CELL, row * CELL, CELL, CELL)
        pygame.draw.rect(surface, PATH, rect)
        pygame.draw.rect(surface, PATH_EDGE, rect, 1)


def draw_grid_and_path(surface):
    draw_field(surface)
    draw_path(surface)


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
        pygame.draw.rect(surface, HP_GREEN, (bar.x, bar.y, int(bar.width * max(0, self.hp / self.max_hp)), bar.height))


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
        pygame.draw.rect(surface, INK, rect, 2, border_radius=7)
        pygame.draw.circle(surface, WHITE, (self.x, self.y), 3)
        if show_range:
            range_layer = pygame.Surface((self.stats["range"] * 2,) * 2, pygame.SRCALPHA)
            pygame.draw.circle(range_layer, (*self.stats["color"], 35), (self.stats["range"],) * 2, self.stats["range"])
            pygame.draw.circle(range_layer, (*self.stats["color"], 150), (self.stats["range"],) * 2, self.stats["range"], 2)
            surface.blit(range_layer, (self.x - self.stats["range"], self.y - self.stats["range"]))


class Game:
    def __init__(self):
        self.font = minecraft_font(24)
        self.small_font = minecraft_font(12)
        self.big_font = minecraft_font(28)
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
        self.wave_conf = None
        self.hover_cell = None
        self.placing_cell = None
        self.delete_cell = None
        self.game_over = False

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

        for tower in self.towers:
            self.projectiles.extend(tower.update(self.enemies))
        for projectile in self.projectiles:
            projectile.update(self.enemies if projectile.piercing else None)

        survivors = []
        for enemy in self.enemies:
            if enemy.alive and not enemy.reached_end:
                survivors.append(enemy)
            elif not enemy.reached_end and enemy.hp <= 0:
                self.gold += enemy.gold
        self.enemies = survivors
        self.projectiles = [projectile for projectile in self.projectiles if projectile.alive]

        if self.wave_active and self.spawn_q == 0 and not self.enemies:
            self.wave_active = False
        if self.lives <= 0:
            self.game_over = True

    def handle_click(self, position, button):
        if button != 1 or self.game_over:
            return
        if not self.wave_active and math.hypot(position[0] - 44, position[1] - 260) <= 26:
            self.start_wave()
            self.placing_cell = None
            self.delete_cell = None
            return
        if position[1] >= HEIGHT - UI_BAR_HEIGHT:
            for index, kind in enumerate(TOWER_TYPES):
                rect = pygame.Rect(220 + index * 180, HEIGHT - 58, 125, 48)
                if rect.collidepoint(position):
                    self.selected = kind
            self.placing_cell = None
            self.delete_cell = None
            return
        if self.delete_cell:
            col, row = self.delete_cell
            center = (col * CELL + CELL // 2, row * CELL + CELL // 2)
            if math.hypot(position[0] - center[0], position[1] - center[1]) <= 28:
                self.towers = [tower for tower in self.towers if (tower.col, tower.row) != (col, row)]
            self.delete_cell = None
            return
        if self.placing_cell:
            col, row = self.placing_cell
            center = (col * CELL + CELL // 2, row * CELL + CELL // 2)
            if math.hypot(position[0] - center[0], position[1] - center[1]) <= 52:
                kind = "cannon" if position[0] < center[0] else "rapid"
                if self.gold >= TOWER_TYPES[kind]["cost"]:
                    self.towers.append(Tower(col, row, kind))
                    self.gold -= TOWER_TYPES[kind]["cost"]
            self.placing_cell = None
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
        if (col, row) not in PATH_CELLS:
            self.placing_cell = (col, row)

    def draw(self, surface):
        draw_grid_and_path(surface)
        surface.blit(build_brick_wall((WIDTH, PLAYFIELD_HEIGHT)), (0, 0))
        for tower in self.towers:
            show_range = self.hover_cell == (tower.col, tower.row)
            tower.draw(surface, show_range)
        for enemy in self.enemies:
            enemy.draw(surface)
        for projectile in self.projectiles:
            projectile.draw(surface)
        self._draw_place_menu(surface)
        self._draw_delete_menu(surface)
        self._draw_ui(surface)
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((5, 10, 10, 185))
            surface.blit(overlay, (0, 0))
            draw_panel(surface, pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 75, 300, 150), PANEL_LIGHT, 245, RED)
            draw_centered_text(surface, self.big_font, "GAME OVER", RED, (WIDTH // 2, HEIGHT // 2 - 22))
            draw_centered_text(surface, self.font, "Press R to restart", WHITE, (WIDTH // 2, HEIGHT // 2 + 20))

    def _draw_ui(self, surface):
        bar = pygame.Rect(0, HEIGHT - UI_BAR_HEIGHT, WIDTH, UI_BAR_HEIGHT)
        pygame.draw.rect(surface, BLACK, bar)
        font = minecraft_font(24)
        small_font = minecraft_font(10)
        draw_text(surface, font, f"Gold: {self.gold}", GOLD, (40, HEIGHT - 80), None)
        draw_text(surface, font, f"Lives: {self.lives}", WHITE, (40, HEIGHT - 40), None)
        draw_text(surface, font, f"Wave: {self.wave}", WHITE, (220, HEIGHT - 80), None)

        for index, (kind, info) in enumerate(TOWER_TYPES.items()):
            rect = pygame.Rect(400 + index * 180, HEIGHT - 82, 80, 70)
            pygame.draw.rect(surface, info["color"], rect)
            border = GOLD if self.selected == kind else WHITE
            pygame.draw.rect(surface, border, rect, 2)
            draw_text(surface, small_font, info["name"], BLACK, (rect.x + 5, HEIGHT - 80), None)
            draw_text(surface, small_font, str(info["cost"]), BLACK, (rect.x + 5, HEIGHT - 40), None)

        if not self.wave_active and not self.game_over:
            center = (44, 260)
            pygame.draw.circle(surface, GREEN, center, 28)
            pygame.draw.circle(surface, WHITE, center, 28, 2)
            draw_play_icon(surface, center, 20)
            draw_text(surface, small_font, "START", WHITE, (79, 250), None)

    def _draw_place_menu(self, surface):
        if not self.placing_cell:
            return
        col, row = self.placing_cell
        center = (col * CELL + CELL // 2, row * CELL + CELL // 2)
        radius = 52
        pygame.draw.circle(surface, PANEL, center, radius)
        pygame.draw.circle(surface, WHITE, center, radius, 2)
        pygame.draw.line(surface, WHITE, (center[0], center[1] - radius), (center[0], center[1] + radius), 2)
        draw_centered_text(surface, self.small_font, "CANNON", WHITE, (center[0] - 24, center[1] - 10), None)
        draw_centered_text(surface, self.small_font, "RAPID", WHITE, (center[0] + 25, center[1] - 10), None)

    def _draw_delete_menu(self, surface):
        if not self.delete_cell:
            return
        col, row = self.delete_cell
        center = (col * CELL + CELL // 2, row * CELL + CELL // 2)
        pygame.draw.circle(surface, RED, center, 28)
        pygame.draw.circle(surface, WHITE, center, 28, 2)
        draw_centered_text(surface, self.small_font, "DELETE", WHITE, center, None)


class App:
    def __init__(self, screen=None):
        self.screen = screen or pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.state = ScreenState.MENU
        self.running = True
        self.volume = 60
        self.dragging_volume = False
        self.mouse_pos = (0, 0)
        self.title_font = minecraft_font(42)
        self.subtitle_font = minecraft_font(16)
        self.button_font = minecraft_font(18)
        self.font = minecraft_font(16)
        self.play_button = pygame.Rect(WIDTH // 2 - 62, 276, 124, 124)
        self.settings_button = pygame.Rect(34, HEIGHT // 2 - 32, 64, 64)
        self.back_button = pygame.Rect(34, 34, 116, 44)
        self.volume_track = pygame.Rect(160, 280, 480, 8)
        self.game = Game()

    def set_volume(self, value):
        self.volume = int(clamp(int(value), 0, 100))

    def set_volume_from_x(self, x):
        ratio = (x - self.volume_track.left) / self.volume_track.width
        self.set_volume(round(clamp(ratio, 0, 1) * 100))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            if self.state is ScreenState.SETTINGS and self.dragging_volume:
                self.set_volume_from_x(event.pos[0])
            elif self.state is ScreenState.GAME:
                col, row = event.pos[0] // CELL, event.pos[1] // CELL
                self.game.hover_cell = (
                    (col, row)
                    if 0 <= col < GRID_COLS and 0 <= row < GRID_ROWS and event.pos[0] < WALL_LEFT
                    else None
                )
            return
        if self.state is ScreenState.MENU:
            self._handle_menu_event(event)
        elif self.state is ScreenState.SETTINGS:
            self._handle_settings_event(event)
        else:
            self._handle_game_event(event)

    def _handle_menu_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.play_button.collidepoint(event.pos):
                self.state = ScreenState.GAME
            elif self.settings_button.collidepoint(event.pos):
                self.state = ScreenState.SETTINGS

    def _handle_settings_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.dragging_volume = False
            self.state = ScreenState.MENU
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging_volume = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.collidepoint(event.pos):
                self.dragging_volume = False
                self.state = ScreenState.MENU
            elif self.volume_track.inflate(40, 30).collidepoint(event.pos):
                self.dragging_volume = True
                self.set_volume_from_x(event.pos[0])

    def _handle_game_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = ScreenState.MENU
            elif event.key == pygame.K_SPACE:
                self.game.start_wave()
            elif event.key == pygame.K_1:
                self.game.selected = "rapid"
            elif event.key == pygame.K_2:
                self.game.selected = "cannon"
            elif event.key == pygame.K_r and self.game.game_over:
                self.game.reset()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.game.handle_click(event.pos, event.button)

    def update(self):
        if self.state is ScreenState.GAME:
            self.game.update()

    def draw(self):
        if self.state is ScreenState.MENU:
            self._draw_menu()
        elif self.state is ScreenState.SETTINGS:
            self._draw_settings()
        else:
            self.game.draw(self.screen)
        display = pygame.display.get_surface()
        if display is self.screen:
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

    def _draw_menu(self):
        draw_vertical_gradient(self.screen, (11, 29, 32), (20, 62, 54))
        pygame.draw.circle(self.screen, (29, 100, 76), (WIDTH - 65, 70), 145, 2)
        pygame.draw.circle(self.screen, (29, 100, 76), (WIDTH - 65, 70), 105, 1)
        draw_centered_text(self.screen, self.title_font, "TOWER DEFENCE", WHITE, (WIDTH // 2, 125))
        draw_centered_text(self.screen, self.subtitle_font, "BUILD  ·  DEFEND  ·  SURVIVE", GRAY, (WIDTH // 2, 170), None)

        hovered = self.play_button.collidepoint(self.mouse_pos)
        center = self.play_button.center
        pygame.draw.circle(self.screen, (4, 12, 12), (center[0] + 6, center[1] + 8), 67)
        pygame.draw.circle(self.screen, GREEN_HOVER if hovered else GREEN, center, 62)
        pygame.draw.circle(self.screen, WHITE, center, 62, 2)
        draw_play_icon(self.screen, center, 34)
        draw_centered_text(self.screen, self.button_font, "PLAY", WHITE, (center[0], center[1] + 90), None)

        settings_hovered = self.settings_button.collidepoint(self.mouse_pos)
        pygame.draw.rect(self.screen, GREEN_DARK if settings_hovered else PANEL, self.settings_button, border_radius=14)
        pygame.draw.rect(self.screen, GREEN if settings_hovered else PANEL_LIGHT, self.settings_button, 2, border_radius=14)
        draw_gear_icon(self.screen, self.settings_button.center, 20)
        draw_text(self.screen, self.subtitle_font, "SETTINGS", GRAY, (self.settings_button.right + 14, self.settings_button.centery - 8), None)
        draw_centered_text(self.screen, self.subtitle_font, "Press the play button to enter the battlefield", GRAY, (WIDTH // 2, HEIGHT - 42), None)

    def _draw_settings(self):
        draw_vertical_gradient(self.screen, (11, 29, 32), (20, 62, 54))
        draw_panel(self.screen, pygame.Rect(90, 90, WIDTH - 180, 400), PANEL, 235, PANEL_LIGHT)
        draw_text(self.screen, self.title_font, "SETTINGS", WHITE, (140, 135))
        draw_text(self.screen, self.subtitle_font, "AUDIO", GRAY, (140, 224), None)
        draw_text(self.screen, self.font, f"MASTER VOLUME   {self.volume}%", WHITE, (140, 248), None)
        track = self.volume_track
        pygame.draw.rect(self.screen, DARK_GRAY, track.inflate(0, 10), border_radius=8)
        pygame.draw.rect(self.screen, GREEN, (track.left, track.top, int(track.width * self.volume / 100), track.height), border_radius=8)
        knob_x = track.left + int(track.width * self.volume / 100)
        pygame.draw.circle(self.screen, WHITE, (knob_x, track.centery), 12)
        pygame.draw.circle(self.screen, GREEN, (knob_x, track.centery), 6)
        hovered = self.back_button.collidepoint(self.mouse_pos)
        pygame.draw.rect(self.screen, GREEN_DARK if hovered else PANEL_LIGHT, self.back_button, border_radius=10)
        pygame.draw.rect(self.screen, GREEN if hovered else GRAY, self.back_button, 1, border_radius=10)
        draw_text(self.screen, self.font, "‹  BACK", WHITE, (self.back_button.x + 18, self.back_button.y + 12), None)


def main():
    pygame.init()
    pygame.display.set_caption("Tower Defence")
    app = App()
    app.run()
    pygame.quit()


if __name__ == "__main__":
    main()
