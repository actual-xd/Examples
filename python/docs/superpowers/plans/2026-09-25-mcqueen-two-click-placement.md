# McQueen and Two-Click Placement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add every-fifth McQueen enemies and a safe two-click tower placement preview.

**Architecture:** Keep both features data-driven inside existing `ui.py`. `ENEMY_TYPES` scales wave base stats, while `Game.pending_cell` acts as the complete placement state; preview rendering never creates a live `Tower`.

**Tech Stack:** Python 3.13, Pygame 2.6.1, standard-library `unittest`.

## Global Constraints

- Preserve existing `Enemy(hp, speed, gold)` callers by defaulting to `normal`.
- McQueen uses 0.6 HP, 2.0 speed, 0.8 gold, and two life damage.
- Every fifth spawn in each wave is McQueen; counting restarts per wave.
- Tower selection changes update active preview without moving it.
- Another valid cell moves preview and requires another click to confirm.
- Existing unrelated working-tree changes stay untouched.
- Work directly on `main` as requested; branch protection may leave work uncommitted.

---

### Task 1: Data-driven McQueen enemy

**Files:**
- Modify: `ui.py:64-91,332-372,522-575`
- Test: `test_ui.py:70-145,374-391`

**Interfaces:**
- Produces: `ENEMY_TYPES: dict[str, dict[str, float | int]]`
- Produces: `Enemy(hp, speed, gold, kind="normal")`
- Produces fields: `Enemy.kind: str`, `Enemy.life_damage: int`
- Consumes: existing `Game.wave_conf`, `Game.spawn_q`, and wave base stats.

- [ ] **Step 1: Write failing enemy-type tests**

Add tests equivalent to:

```python
def test_mcqueen_applies_enemy_type_multipliers(self):
    mcqueen = self.ui.Enemy(50, 1.5, 8, "mcqueen")
    self.assertEqual(mcqueen.kind, "mcqueen")
    self.assertEqual(mcqueen.max_hp, 30)
    self.assertEqual(mcqueen.hp, 30)
    self.assertEqual(mcqueen.speed, 3.0)
    self.assertEqual(mcqueen.gold, 6)
    self.assertEqual(mcqueen.life_damage, 2)


def test_every_fifth_spawn_is_mcqueen(self):
    game = self.ui.Game()
    game.start_wave()
    for _ in range(5):
        game.spawn_timer = 0
        game.update()
    self.assertEqual(
        [enemy.kind for enemy in game.enemies],
        ["normal", "normal", "normal", "normal", "mcqueen"],
    )


def test_mcqueen_spawn_count_restarts_each_wave(self):
    game = self.ui.Game()
    game.start_wave()
    for _ in range(5):
        game.spawn_timer = 0
        game.update()
    game.enemies.clear()
    game.wave_active = False
    game.start_wave()
    game.spawn_timer = 0
    game.update()
    self.assertEqual(game.enemies[0].kind, "normal")


def test_mcqueen_leak_removes_two_lives(self):
    game = self.ui.Game()
    game.drain_events()
    enemy = self.ui.Enemy(50, 1.5, 8, "mcqueen")
    enemy.alive = False
    enemy.reached_end = True
    game.enemies = [enemy]
    game.update()
    self.assertEqual(game.lives, 1)
    self.assertIn("lives_changed", game.drain_events())
```

- [ ] **Step 2: Run enemy tests and verify RED**

Run:

```bash
.venv/Scripts/python.exe -m unittest \
  test_ui.UiBehaviorTests.test_mcqueen_applies_enemy_type_multipliers \
  test_ui.UiBehaviorTests.test_every_fifth_spawn_is_mcqueen \
  test_ui.UiBehaviorTests.test_mcqueen_spawn_count_restarts_each_wave \
  test_ui.UiBehaviorTests.test_mcqueen_leak_removes_two_lives -v
```

Expected: FAIL because `Enemy` does not accept `kind` and `ENEMY_TYPES` does not exist.

- [ ] **Step 3: Add `ENEMY_TYPES` and apply it in `Enemy`**

Add beside `TOWER_TYPES`:

```python
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
```

Change initialization to:

```python
class Enemy:
    def __init__(self, hp, speed, gold, kind="normal"):
        stats = ENEMY_TYPES[kind]
        self.kind = kind
        self.max_hp = int(hp * stats["hp_multiplier"])
        self.hp = self.max_hp
        self.speed = speed * stats["speed_multiplier"]
        self.gold = int(gold * stats["gold_multiplier"])
        self.life_damage = stats["life_damage"]
```

Keep remaining movement fields unchanged.

- [ ] **Step 4: Spawn each fifth enemy as McQueen and apply leak damage**

In the spawn block, derive the one-based position before decrementing `spawn_q`:

```python
spawn_number = config["count"] - self.spawn_q + 1
kind = "mcqueen" if spawn_number % 5 == 0 else "normal"
self.enemies.append(
    Enemy(config["hp"], config["speed"], config["gold"], kind)
)
```

Change fixed leak loss to:

```python
self.lives -= enemy.life_damage
```

- [ ] **Step 5: Run enemy tests and full suite**

Run:

```bash
.venv/Scripts/python.exe -m unittest \
  test_ui.UiBehaviorTests.test_mcqueen_applies_enemy_type_multipliers \
  test_ui.UiBehaviorTests.test_every_fifth_spawn_is_mcqueen \
  test_ui.UiBehaviorTests.test_mcqueen_spawn_count_restarts_each_wave \
  test_ui.UiBehaviorTests.test_mcqueen_leak_removes_two_lives -v
.venv/Scripts/python.exe -m unittest test_ui -v
```

Expected: focused tests PASS; existing placement test may still expect one-click behavior and remains unchanged until Task 2.

---

### Task 2: Two-click placement state and range preview

**Files:**
- Modify: `ui.py:446-489,500-642,806-849`
- Test: `test_ui.py:90-110,180-215,350-425`

**Interfaces:**
- Consumes: `Game.pending_cell: tuple[int, int] | None`, `Game.selected`, `TOWER_TYPES`.
- Produces: `Game._buildable_cell(cell) -> bool`.
- Produces: `draw_tower_range(surface, center, stats) -> None`.
- Preserves: built tower radius appears only when `hover_cell` matches its cell.

- [ ] **Step 1: Change the existing placement test to RED**

Replace immediate-placement expectations with:

```python
def test_selected_tower_needs_preview_then_confirmation(self):
    game = self.ui.Game()
    cards = dict(self.ui.shop_cards())
    game.handle_click(cards["cannon"].center, 1)
    cell_pos = (self.ui.CELL // 2, self.ui.CELL // 2)

    game.handle_click(cell_pos, 1)
    self.assertEqual(game.pending_cell, (0, 0))
    self.assertEqual(game.towers, [])
    self.assertEqual(game.gold, 300)

    game.handle_click(cell_pos, 1)
    self.assertEqual([tower.kind for tower in game.towers], ["cannon"])
    self.assertEqual(game.gold, 100)
    self.assertIsNone(game.pending_cell)
```

- [ ] **Step 2: Add failing transition tests**

Add focused tests:

```python
def test_clicking_another_cell_moves_preview(self):
    game = self.ui.Game()
    first = (self.ui.CELL // 2, self.ui.CELL // 2)
    second = (self.ui.CELL + self.ui.CELL // 2, self.ui.CELL // 2)
    game.handle_click(first, 1)
    game.handle_click(second, 1)
    self.assertEqual(game.pending_cell, (1, 0))
    self.assertEqual(game.towers, [])
    game.handle_click(second, 1)
    self.assertEqual([(tower.col, tower.row) for tower in game.towers], [(1, 0)])


def test_type_change_updates_pending_purchase(self):
    game = self.ui.Game()
    cell_pos = (self.ui.CELL // 2, self.ui.CELL // 2)
    game.handle_click(cell_pos, 1)
    game.handle_click(dict(self.ui.shop_cards())["cannon"].center, 1)
    game.handle_click(cell_pos, 1)
    self.assertEqual(game.towers[0].kind, "cannon")
    self.assertEqual(game.gold, 100)


def test_current_price_is_checked_on_confirmation(self):
    game = self.ui.Game()
    cell_pos = (self.ui.CELL // 2, self.ui.CELL // 2)
    game.handle_click(cell_pos, 1)
    game.gold = 150
    game.handle_click(dict(self.ui.shop_cards())["cannon"].center, 1)
    game.handle_click(cell_pos, 1)
    self.assertEqual(game.towers, [])
    self.assertEqual(game.pending_cell, (0, 0))
    game.handle_click(dict(self.ui.shop_cards())["rapid"].center, 1)
    game.handle_click(cell_pos, 1)
    self.assertEqual(game.towers[0].kind, "rapid")
    self.assertEqual(game.gold, 50)


def test_invalid_click_keeps_existing_preview(self):
    game = self.ui.Game()
    cell_pos = (self.ui.CELL // 2, self.ui.CELL // 2)
    game.handle_click(cell_pos, 1)
    invalid_positions = [
        self.ui.WAYPOINTS[1],
        (self.ui.WALL_LEFT + 10, 100),
        (-20, -20),
    ]
    for position in invalid_positions:
        game.handle_click(position, 1)
        self.assertEqual(game.pending_cell, (0, 0))
        self.assertEqual(game.towers, [])


def test_existing_tower_replaces_preview_with_delete_state(self):
    game = self.ui.Game()
    existing = self.ui.Tower(2, 0, "rapid")
    game.towers = [existing]
    game.handle_click((20, 20), 1)
    game.handle_click((existing.x, existing.y), 1)
    self.assertIsNone(game.pending_cell)
    self.assertEqual(game.delete_cell, (2, 0))
```

Add an app-level keyboard test:

```python
def test_keyboard_type_change_updates_pending_selection(self):
    app = self.make_app()
    app.state = self.ui.ScreenState.GAME
    app.game.handle_click((20, 20), 1)
    app.handle_event(self.key(pygame.K_2))
    self.assertEqual(app.game.selected, "cannon")
    self.assertEqual(app.game.pending_cell, (0, 0))
```

- [ ] **Step 3: Run placement tests and verify RED**

Run:

```bash
.venv/Scripts/python.exe -m unittest \
  test_ui.UiBehaviorTests.test_selected_tower_needs_preview_then_confirmation \
  test_ui.UiBehaviorTests.test_clicking_another_cell_moves_preview \
  test_ui.UiBehaviorTests.test_type_change_updates_pending_purchase \
  test_ui.UiBehaviorTests.test_current_price_is_checked_on_confirmation \
  test_ui.UiBehaviorTests.test_invalid_click_keeps_existing_preview \
  test_ui.UiBehaviorTests.test_existing_tower_replaces_preview_with_delete_state \
  test_ui.UiUxSkillTests.test_keyboard_type_change_updates_pending_selection -v
```

Expected: FAIL because first valid click still immediately builds a tower.

- [ ] **Step 4: Implement one validation path and two-click transitions**

Add to `Game`:

```python
def _buildable_cell(self, cell):
    col, row = cell
    return (
        0 <= col < GRID_COLS
        and 0 <= row < GRID_ROWS
        and col * CELL < WALL_LEFT
        and cell not in PATH_CELLS
        and all((tower.col, tower.row) != cell for tower in self.towers)
    )
```

Refactor `handle_click` so it:

1. Keeps start-button and shop-card precedence.
2. Resolves an open delete action, then continues if the click was not deletion.
3. Converts valid playfield coordinates to one cell.
4. Clears pending and opens deletion when the cell contains a tower.
5. Preserves pending for invalid cells.
6. Stores a new valid cell and returns.
7. Confirms only when the valid cell equals `pending_cell`.
8. Checks current selected cost, builds, emits `gold_changed`, and clears pending only on success.

The confirmation block is:

```python
cell = (col, row)
if not self._buildable_cell(cell):
    return
if self.pending_cell != cell:
    self.pending_cell = cell
    return
cost = TOWER_TYPES[self.selected]["cost"]
if self.gold >= cost:
    self.towers.append(Tower(col, row, self.selected))
    self.gold -= cost
    self.pending_cell = None
    self.emit("gold_changed")
```

- [ ] **Step 5: Add game-over cleanup and delete-menu transition tests**

Add:

```python
def test_game_over_clears_pending_and_delete_state(self):
    game = self.ui.Game()
    game.pending_cell = (0, 0)
    game.delete_cell = (1, 0)
    game.lives = 0
    game.update()
    self.assertIsNone(game.pending_cell)
    self.assertIsNone(game.delete_cell)


def test_free_cell_closes_delete_menu_and_becomes_preview(self):
    game = self.ui.Game()
    game.towers = [self.ui.Tower(2, 0, "rapid")]
    game.delete_cell = (2, 0)
    game.handle_click((20, 20), 1)
    self.assertIsNone(game.delete_cell)
    self.assertEqual(game.pending_cell, (0, 0))
```

Update the game-over branch:

```python
if self.lives <= 0:
    self.game_over = True
    self.pending_cell = None
    self.delete_cell = None
```

Run both tests and expect PASS.

- [ ] **Step 6: Add reusable range drawing and pending preview**

Extract current range rendering into:

```python
def draw_tower_range(surface, center, stats):
    radius = stats["range"]
    layer = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(layer, (*stats["color"], 35), (radius, radius), radius)
    pygame.draw.circle(layer, (*stats["color"], 150), (radius, radius), radius, 2)
    surface.blit(layer, (center[0] - radius, center[1] - radius))
```

Use it from `Tower.draw` only when `show_range` is true. In `Game.draw`, before built towers, render pending state only when `_buildable_cell(pending_cell)` remains true:

```python
if self.pending_cell and self._buildable_cell(self.pending_cell):
    col, row = self.pending_cell
    center = (col * CELL + CELL // 2, row * CELL + CELL // 2)
    draw_tower_range(surface, center, TOWER_TYPES[self.selected])
```

- [ ] **Step 7: Add headless rendering regression tests**

Add:

```python
def test_pending_range_draws_without_creating_tower(self):
    game = self.ui.Game()
    position = (7 * self.ui.CELL + 20, 7 * self.ui.CELL + 20)
    before = pygame.Surface((self.ui.WIDTH, self.ui.HEIGHT))
    after = pygame.Surface((self.ui.WIDTH, self.ui.HEIGHT))
    game.draw(before)
    game.handle_click(position, 1)
    game.draw(after)
    center = (7 * self.ui.CELL + 20, 7 * self.ui.CELL + 20)
    edge = (center[0] + self.ui.TOWER_TYPES["rapid"]["range"] - 1, center[1])
    self.assertNotEqual(before.get_at(edge), after.get_at(edge))
    self.assertEqual(game.towers, [])


def test_built_tower_range_stays_hover_only(self):
    game = self.ui.Game()
    game.towers = [self.ui.Tower(7, 7, "rapid")]
    plain = pygame.Surface((self.ui.WIDTH, self.ui.HEIGHT))
    hovered = pygame.Surface((self.ui.WIDTH, self.ui.HEIGHT))
    game.draw(plain)
    game.hover_cell = (7, 7)
    game.draw(hovered)
    center = (7 * self.ui.CELL + 20, 7 * self.ui.CELL + 20)
    edge = (center[0] + self.ui.TOWER_TYPES["rapid"]["range"] - 1, center[1])
    self.assertNotEqual(plain.get_at(edge), hovered.get_at(edge))
```

Run these two tests. Expected: PASS.

- [ ] **Step 8: Run complete verification**

Run:

```bash
.venv/Scripts/python.exe -m unittest test_ui -v
.venv/Scripts/python.exe -m py_compile ui.py test_ui.py
rtk git diff --check
```

Expected: all tests PASS, compilation PASS, no whitespace errors.

Review `git diff -- ui.py test_ui.py` and confirm every changed line belongs to McQueen or two-click placement.

---

### Task 3: Pending tower outline

**Files:**
- Modify: `ui.py:660-667`
- Test: `test_ui.py` pending-range rendering tests

**Interfaces:**
- Consumes: `Game.pending_cell`, `Game.selected`, and `TOWER_TYPES`.
- Produces: an unfilled 3 px rounded outline matching installed tower geometry.

- [ ] **Step 1: Add a failing render test**

Draw a pending preview and assert its border pixel matches the selected tower color while its center pixel remains unchanged from the field.

- [ ] **Step 2: Verify RED**

Run the focused test. Expected: border assertion fails because only the range is drawn.

- [ ] **Step 3: Draw the pending tower outline**

Use the installed tower geometry without creating a temporary `Tower`:

```python
rect = pygame.Rect(col * CELL + 4, row * CELL + 4, CELL - 8, CELL - 8)
pygame.draw.rect(surface, TOWER_TYPES[self.selected]["color"], rect, 3, border_radius=7)
```

- [ ] **Step 4: Verify GREEN and regressions**

Run the focused test, full `test_ui` suite, `py_compile`, and `git diff --check`.
