import pygame
import sys
import math


WIDTH, HEIGHT = 800, 600
FPS = 60
CELL = 40
GRID_COLS = WIDTH // CELL
GRID_ROWS = HEIGHT // CELL

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50, 150, 50)
DARK_GREEN = (30, 100, 30)
BROWN = (160, 130, 90)
DARK_BROWN = (120, 90, 60)
RED = (220, 50, 50)
GOLD = (255, 215, 0)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
CYAN = (0, 200, 200)
ORANGE = (255, 165, 0)
HP_GREEN = (80, 200, 80)

WAYPOINTS = [
    (-40, 260),
    (200, 260),
    (200, 100),
    (460, 100),
    (460, 420),
    (700, 420),
    (700, 180),
    (840, 180),
]

# Cells the path crosses, derived from WAYPOINTS so they can't drift apart.
PATH_CELLS = set()
for (x1, y1), (x2, y2) in zip(WAYPOINTS, WAYPOINTS[1:]):
    c1, r1, c2, r2 = x1 // CELL, y1 // CELL, x2 // CELL, y2 // CELL
    for c in range(min(c1, c2), max(c1, c2) + 1):
        for r in range(min(r1, r2), max(r1, r2) + 1):
            PATH_CELLS.add((c, r))

# ponytail: cannon spread directions precomputed once -> no trig in the hot path.
_CANNON_DIRS = [(math.cos(i * 0.35), math.sin(i * 0.35)) for i in range(-2, 3)]

def draw_text(surf, font, text, color, x, y, shadow=(0,0,0)):
    if shadow:
        s = font.render(text, True, shadow)
        surf.blit(s, (x+1, y+1))
    t = font.render(text, True, color)
    surf.blit(t, (x, y))


TOWER_TYPES = {
    "rapid": {"name": "Rapid", "damage": 10, "fire_rate": 10, "range": 150, "color": CYAN, "cost": 100},
    "cannon": {"name": "Cannon", "damage": 60, "fire_rate": 75, "range": 120, "color": ORANGE, "cost": 250},
}




class Enemy:
    def __init__(self, hp, speed, gold):
        self.max_hp = hp
        self.hp = hp
        self.speed = speed
        self.gold = gold
        self.waypoint_index = 0
        self.x, self.y = WAYPOINTS[0]
        self.alive = True
        self.reached_end = False

    def update(self):
        if not self.alive or self.reached_end:
            return
        tx, ty = WAYPOINTS[self.waypoint_index]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed:
            self.x, self.y = tx, ty
            self.waypoint_index += 1
            if self.waypoint_index >= len(WAYPOINTS):
                self.alive = False
                self.reached_end = True
        else:
            self.x += dx / dist * self.speed
            self.y += dy / dist * self.speed

    def draw(self, screen):
        if not self.alive:
            return
        pygame.draw.rect(screen, RED, (self.x - 8, self.y - 8, 16, 16))
        bar_w, bar_h = 22, 3
        ratio = max(0, self.hp / self.max_hp)
        bx = self.x - bar_w // 2
        by = self.y - 14
        pygame.draw.rect(screen, BLACK, (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        pygame.draw.rect(screen, HP_GREEN, (bx, by, bar_w * ratio, bar_h))


class Projectile:
    def __init__(self, x, y, target, damage, piercing=False, size=3, vx=0, vy=0, color=YELLOW, src_x=None, src_y=None, max_range=None):
        self.x, self.y = x, y
        self.target = target
        self.damage = damage
        self.speed = 6
        self.alive = True
        self.piercing = piercing
        self.size = size
        self.color = color
        self.vx = vx
        self.vy = vy
        self.src_x = src_x if src_x is not None else x
        self.src_y = src_y if src_y is not None else y
        self.max_range = max_range
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
                    if e.alive and not e.reached_end and id(e) not in self.hit_enemies:
                        if math.hypot(self.x - e.x, self.y - e.y) < self.size + 8:
                            e.hp -= self.damage
                            self.hit_enemies.add(id(e))
                            if e.hp <= 0:
                                e.alive = False
        else:
            if not self.target.alive or self.target.reached_end:
                self.alive = False
                return
            tx, ty = self.target.x, self.target.y
            dx, dy = tx - self.x, ty - self.y
            dist = math.hypot(dx, dy)
            if dist < self.speed:
                self.target.hp -= self.damage
                if self.target.hp <= 0:
                    self.target.alive = False
                self.alive = False
            else:
                self.x += dx / dist * self.speed
                self.y += dy / dist * self.speed

    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)


class Tower:
    def __init__(self, gx, gy, kind):
        self.gx, self.gy = gx, gy
        self.x = gx * CELL + CELL // 2
        self.y = gy * CELL + CELL // 2
        self.kind = kind
        self.stats = TOWER_TYPES[kind]
        self.cooldown = 0

    def update(self, enemies):
        if self.cooldown > 0:
            self.cooldown -= 1
            return []
        best, best_dist = None, self.stats["range"]
        for e in enemies:
            if not e.alive or e.reached_end:
                continue
            d = math.hypot(self.x - e.x, self.y - e.y)
            if d < best_dist:
                best_dist = d
                best = e
        if not best:
            return []
        self.cooldown = self.stats["fire_rate"]
        rng = self.stats["range"]
        if self.kind == "cannon":
            dx = best.x - self.x
            dy = best.y - self.y
            d = math.hypot(dx, dy) or 1
            ux, uy = dx / d, dy / d  # unit aim vector = (cos base, sin base)
            result = []
            for co, so in _CANNON_DIRS:  # rotate each preset spread dir by the aim
                result.append(Projectile(self.x, self.y, best, self.stats["damage"],
                              piercing=True, size=6,
                              vx=ux * co - uy * so, vy=ux * so + uy * co,
                              color=ORANGE, src_x=self.x, src_y=self.y, max_range=rng))
            return result
        return [Projectile(self.x, self.y, best, self.stats["damage"],
                           src_x=self.x, src_y=self.y, max_range=rng)]

    def draw(self, screen, show_range=False):
        color = self.stats["color"]
        r = pygame.Rect(self.gx * CELL + 3, self.gy * CELL + 3, CELL - 6, CELL - 6)
        pygame.draw.rect(screen, color, r)
        pygame.draw.rect(screen, BLACK, r, 2)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), 3)
        if show_range:
            s = pygame.Surface((self.stats["range"] * 2,) * 2, pygame.SRCALPHA)
            s.fill((0, 0, 0, 0))
            pygame.draw.circle(s, (255, 255, 255, 60), (self.stats["range"],) * 2, self.stats["range"])
            screen.blit(s, (self.x - self.stats["range"], self.y - self.stats["range"]))


class Game:
    def __init__(self):
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
        self.wave_timer = 0
        self.font = pygame.font.SysFont("Inter", 14)
        self.big = pygame.font.SysFont("Inter", 20)
        self.game_over = False

    def start_wave(self):
        if self.wave_active or self.game_over:
            return
        secs = max(1, self.wave_timer // FPS)
        bonus = 30 // secs
        self.gold += bonus
        self.wave += 1
        n = self.wave
        self.wave_conf = {
            "count": int(5 * (1 + (n - 1) * 0.35)),
            "hp": int(50 * (1 + (n - 1) * 0.35)),
            "speed": 1.5 + (n - 1) * 0.05,
            "gold": int(8 + (n - 1) * 1.5),
        }
        self.spawn_q = self.wave_conf["count"]
        self.spawn_timer = 0
        self.wave_active = True
        self.wave_timer = 0

    def update(self):
        if self.game_over:
            return

        if self.wave_active and self.spawn_q > 0:
            self.spawn_timer -= 1
            if self.spawn_timer <= 0:
                c = self.wave_conf
                self.enemies.append(Enemy(c["hp"], c["speed"], c["gold"]))
                self.spawn_q -= 1
                self.spawn_timer = 25

        for e in self.enemies:
            e.update()
            if e.reached_end:
                self.lives -= 1

        for t in self.towers:
            for p in t.update(self.enemies):
                self.projectiles.append(p)

        for p in self.projectiles:
            p.update(self.enemies if p.piercing else None)

        alive = []
        for e in self.enemies:
            if e.alive and not e.reached_end:
                alive.append(e)
            elif not e.alive and not e.reached_end:
                self.gold += e.gold
        self.enemies = alive
        self.projectiles = [p for p in self.projectiles if p.alive]

        if self.wave_active and self.spawn_q == 0 and not self.enemies:
            self.wave_active = False

        if not self.wave_active and not self.game_over:
            self.wave_timer += 1
            if self.wave_timer >= 15 * FPS:
                self.start_wave()

        if self.lives <= 0:
            self.game_over = True

    def draw(self, screen):
        screen.fill(GREEN)
        for x in range(0, WIDTH, CELL):
            pygame.draw.line(screen, DARK_GREEN, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, CELL):
            pygame.draw.line(screen, DARK_GREEN, (0, y), (WIDTH, y), 1)

        for cx, cy in PATH_CELLS:
            pygame.draw.rect(screen, BROWN, (cx * CELL, cy * CELL, CELL, CELL))
            pygame.draw.rect(screen, DARK_BROWN, (cx * CELL, cy * CELL, CELL, CELL), 1)

        for t in self.towers:
            hl = self.hover_cell and t.gx == self.hover_cell[0] and t.gy == self.hover_cell[1]
            t.draw(screen, show_range=hl)

        for e in self.enemies:
            e.draw(screen)
        for p in self.projectiles:
            p.draw(screen)

        if self.placing_cell:
            gx, gy = self.placing_cell
            cx = gx * CELL + CELL // 2
            cy = gy * CELL + CELL // 2
            rd = 50
            s = pygame.Surface((rd * 2, rd * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (40, 40, 40, 220), (rd, rd), rd)
            # ponytail: two semicircles via rect clipping — no trig for the wedges.
            s2 = pygame.Surface((rd * 2, rd * 2), pygame.SRCALPHA)
            colors = [info["color"] + (180,) for info in TOWER_TYPES.values()]
            s2.set_clip(pygame.Rect(rd, 0, rd, rd * 2))
            pygame.draw.circle(s2, colors[0], (rd, rd), rd)  # right half = rapid
            s2.set_clip(pygame.Rect(0, 0, rd, rd * 2))
            pygame.draw.circle(s2, colors[1], (rd, rd), rd)  # left half = cannon
            screen.blit(s, (cx - rd, cy - rd))
            screen.blit(s2, (cx - rd, cy - rd))
            pygame.draw.circle(screen, WHITE, (cx, cy), rd, 2)
            pygame.draw.line(screen, WHITE, (cx, cy - rd), (cx, cy + rd), 2)
            for lx, (key, info) in zip((cx + rd * 0.55, cx - rd * 0.55), TOWER_TYPES.items()):
                draw_text(screen, self.font, info["name"], BLACK, lx - self.font.size(info["name"])[0] // 2, cy - 10)
                draw_text(screen, self.font, f"${info['cost']}", BLACK, lx - self.font.size(f"${info['cost']}")[0] // 2, cy + 4)

        if self.delete_cell:
            gx, gy = self.delete_cell
            cx = gx * CELL + CELL // 2
            cy = gy * CELL + CELL // 2
            rd = 25
            s = pygame.Surface((rd * 2,) * 2, pygame.SRCALPHA)
            s.fill((0, 0, 0, 0))
            pygame.draw.circle(s, (180, 40, 40, 220), (rd, rd), rd)
            screen.blit(s, (cx - rd, cy - rd))
            pygame.draw.circle(screen, WHITE, (cx, cy), rd, 2)
            draw_text(screen, self.font, "Delete", WHITE, cx - self.font.size("Delete")[0] // 2, cy - self.font.size("Delete")[1] // 2)

        # UI bar
        pygame.draw.rect(screen, BLACK, (0, HEIGHT - 60, WIDTH, 60))
        draw_text(screen, self.font, f"{self.gold}", GOLD, 10, HEIGHT - 50)
        draw_text(screen, self.font, f"{self.lives}", RED if self.lives < 3 else WHITE, 10, HEIGHT - 30)
        draw_text(screen, self.font, f"Wave {self.wave}", WHITE, 120, HEIGHT - 50)
        draw_text(screen, self.font, "GOLD", GRAY, 10, HEIGHT - 15)
        draw_text(screen, self.font, "LIVES", GRAY, 120, HEIGHT - 15)

        types = list(TOWER_TYPES.items())
        for i, (k, v) in enumerate(types):
            x = 230 + i * 180
            sel = k == self.selected
            pygame.draw.rect(screen, v["color"], (x, HEIGHT - 52, 80, 44))
            border = YELLOW if sel else WHITE
            pygame.draw.rect(screen, border, (x, HEIGHT - 52, 80, 44), 2)
            draw_text(screen, self.font, f"{v['name']}", BLACK, x + 5, HEIGHT - 48)
            draw_text(screen, self.font, f"{v['cost']}", BLACK, x + 5, HEIGHT - 30)

        if not self.wave_active and not self.game_over:
            sx, sy = 25, 260
            secs = self.wave_timer // FPS
            auto_in = max(0, 15 - secs)
            bonus = 30 // max(1, secs)
            # Button circle gets redder as timer runs out
            green = max(0, 180 - secs * 12)
            btn_color = (180 - green, green, 0) if secs < 15 else (180, 0, 0)
            pygame.draw.circle(screen, btn_color, (sx, sy), 20)
            pygame.draw.circle(screen, WHITE, (sx, sy), 20, 2)
            pts = [(sx - 6, sy - 8), (sx - 6, sy + 8), (sx + 10, sy)]
            pygame.draw.polygon(screen, WHITE, pts)
            # Timer and bonus
            time_text = f"Auto {auto_in}s" if auto_in > 0 else f"+{secs}s"
            draw_text(screen, self.font, time_text, WHITE, sx + 26, sy - 16)
            draw_text(screen, self.font, f"+{bonus}", GOLD, sx + 26, sy + 2)

        if self.game_over:
            bg = pygame.Surface((WIDTH, HEIGHT))
            bg.set_alpha(160)
            bg.fill(BLACK)
            screen.blit(bg, (0, 0))
            draw_text(screen, self.big, "GAME OVER", RED, WIDTH // 2 - 70, HEIGHT // 2 - 20)
            draw_text(screen, self.font, "Press R to restart", WHITE, WIDTH // 2 - 70, HEIGHT // 2 + 10)

    def handle_click(self, pos, button):
        if self.game_over or button != 1:
            return

        # Start wave button
        if not self.wave_active:
            sx, sy = 25, 260
            if math.hypot(pos[0] - sx, pos[1] - sy) <= 20:
                self.start_wave()
                self.placing_cell = None
                self.delete_cell = None
                return

        # UI bar — select tower type
        if pos[1] >= HEIGHT - 60:
            types = list(TOWER_TYPES.keys())
            for i, k in enumerate(types):
                x = 230 + i * 180
                if x <= pos[0] <= x + 80:
                    self.selected = k
            self.placing_cell = None
            self.delete_cell = None
            return

        # Delete menu open
        if self.delete_cell:
            gx, gy = self.delete_cell
            cx = gx * CELL + CELL // 2
            cy = gy * CELL + CELL // 2
            if math.hypot(pos[0] - cx, pos[1] - cy) <= 25:
                self.towers = [t for t in self.towers if not (t.gx == gx and t.gy == gy)]
            self.delete_cell = None
            return

        # Place menu open
        if self.placing_cell:
            gx, gy = self.placing_cell
            cx = gx * CELL + CELL // 2
            cy = gy * CELL + CELL // 2
            if math.hypot(pos[0] - cx, pos[1] - cy) <= 50:
                kind = "cannon" if pos[0] - cx < 0 else "rapid"  # left half = cannon
                cost = TOWER_TYPES[kind]["cost"]
                if self.gold >= cost:
                    self.towers.append(Tower(gx, gy, kind))
                    self.gold -= cost
            self.placing_cell = None
            return

        gx, gy = pos[0] // CELL, pos[1] // CELL
        if not (0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS):
            return

        # Click on existing tower → show delete menu
        for t in self.towers:
            if t.gx == gx and t.gy == gy:
                self.delete_cell = (gx, gy)
                return

        # Click on empty cell → show place menu
        if (gx, gy) in PATH_CELLS:
            return
        self.placing_cell = (gx, gy)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tower Defence")
    clock = pygame.time.Clock()
    game = Game()
    running = True

    while running:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1:
                    game.selected = "rapid"
                elif e.key == pygame.K_2:
                    game.selected = "cannon"
                elif e.key == pygame.K_SPACE:
                    game.start_wave()
                elif e.key == pygame.K_r and game.game_over:
                    game = Game()
            if e.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(e.pos, e.button)
            if e.type == pygame.MOUSEMOTION:
                gx, gy = e.pos[0] // CELL, e.pos[1] // CELL
                in_grid = 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS and e.pos[1] < HEIGHT - 60
                game.hover_cell = (gx, gy) if in_grid else None

        game.update()
        game.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
