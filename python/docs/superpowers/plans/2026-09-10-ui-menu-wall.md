# Standalone Pygame UI Menu and Curved Wall Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `ui.py` a standalone Pygame tower-defence application with a menu, volume settings, manual-only waves, a Minecraft-font UI, and a straight brick wall outside the road.

**Architecture:** Replace the import-time global loop with `App`, `Game`, and small rendering helpers in one file. `App` owns `MENU`, `SETTINGS`, and `GAME` state; `Game` owns tower-defence mechanics and a 40x40 cell grid; `build_brick_wall()` owns deterministic straight-wall rendering outside the route. `ui.py` imports only Python standard library and `pygame`.

**Tech Stack:** Python 3.13, Pygame 2.6.1, `unittest`, SDL dummy video driver for smoke tests.

## Global Constraints

- Modify only `ui.py`, `test_ui.py`, and docs/plan artifacts; do not modify `tower_defence.py`.
- `ui.py` has no `tower_defence` import or runtime reference.
- No new dependency.
- Initial screen is `MENU`.
- Wave starts only from Start Wave click or `SPACE`; no auto-start timer.
- Volume is clamped to `[0, 100]` and stored in memory.
- Right wall is a straight rectangular brick surface outside the road with brown variation and black seams; no semicircle, gate, flags, crenellations, sine strips, or shadow.
- Use `Minecraft.otf` and `td-ui.py` game UI margins: 120px bottom bar, Gold/Lives x=40, Wave x=220, tower buttons x=400, y=height-82, size 80x70.
- Keep `WIDTH=1000`, `HEIGHT=720`, `CELL=40`, and route waypoints on cell centers.

---

### Task 1: Add failing behavior tests

**Files:**
- Create: `test_ui.py`

**Interfaces:**
- Consumes future `ui.ScreenState`, `ui.App`, `ui.build_brick_wall`, and `ui.clamp`.
- Produces executable regression tests for later implementation.

- [ ] **Step 1: Write the failing tests**

```python
import importlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pygame


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


class UiBehaviorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        quit_event = pygame.event.Event(pygame.QUIT)
        with patch.object(pygame.event, "get", return_value=[quit_event]):
            cls.ui = importlib.import_module("ui")
        pygame.init()
        cls.screen = pygame.Surface((cls.ui.WIDTH, cls.ui.HEIGHT))

    def test_ui_is_standalone(self):
        source = Path("ui.py").read_text(encoding="utf-8")
        self.assertNotIn("tower_defence", source)

    def test_app_starts_in_menu(self):
        app = self.ui.App(screen=self.screen)
        self.assertEqual(app.state, self.ui.ScreenState.MENU)
        self.assertFalse(app.game.wave_active)

    def test_play_opens_game_without_starting_wave(self):
        app = self.ui.App(screen=self.screen)
        x, y = app.play_button.center
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (x, y)})
        app.handle_event(event)
        self.assertEqual(app.state, self.ui.ScreenState.GAME)
        self.assertFalse(app.game.wave_active)
        self.assertEqual(app.game.wave, 0)

    def test_volume_is_clamped(self):
        app = self.ui.App(screen=self.screen)
        app.set_volume(140)
        self.assertEqual(app.volume, 100)
        app.set_volume(-20)
        self.assertEqual(app.volume, 0)

    def test_brick_wall_surface_has_content(self):
        wall = self.ui.build_brick_wall((self.ui.WIDTH, self.ui.HEIGHT))
        self.assertEqual(wall.get_size(), (self.ui.WIDTH, self.ui.HEIGHT))
        self.assertGreater(wall.get_bounding_rect().width, 0)
        self.assertGreater(wall.get_bounding_rect().height, 0)

    def test_clamp_handles_middle_value(self):
        self.assertEqual(self.ui.clamp(55, 0, 100), 55)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run focused tests and verify expected failure**

Run:

```bash
python -m unittest test_ui -v
```

Expected: FAIL because current `ui.py` has no `App`, `ScreenState`, `build_brick_wall`, or `clamp`, while the patched QUIT event prevents the legacy import loop from hanging.

- [ ] **Step 3: Commit the red tests**

```bash
git add test_ui.py
git commit -m "test: define standalone ui behavior"
```

---

### Task 2: Replace import-time global loop with standalone app architecture

**Files:**
- Modify: `ui.py`

**Interfaces:**
- `ScreenState`: enum values `MENU`, `SETTINGS`, `GAME`.
- `clamp(value, low, high) -> int|float`.
- `App(screen=None)`, `.handle_event(event)`, `.set_volume(value)`, `.draw()`, `.update()`, `.run()`.
- `Game()`, `.start_wave()`, `.update()`, `.draw(surface)`, `.handle_click(pos, button)`.

- [ ] **Step 1: Replace the file with side-effect-free definitions**

Keep all Pygame startup and shutdown inside `main()`. Define `if __name__ == "__main__": main()` so importing `ui` never opens a window or enters a loop. Copy tower, projectile, enemy, and wave mechanics into this file rather than importing them. Remove `wave_timer` and every automatic `start_wave()` call from `Game.update()`.

Use this event transition logic:

```python
if self.state is ScreenState.MENU:
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if self.play_button.collidepoint(event.pos):
            self.state = ScreenState.GAME
        elif self.settings_button.collidepoint(event.pos):
            self.state = ScreenState.SETTINGS
elif self.state is ScreenState.SETTINGS:
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        self.state = ScreenState.MENU
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        if self.back_button.collidepoint(event.pos):
            self.state = ScreenState.MENU
        elif self.volume_track.inflate(40, 30).collidepoint(event.pos):
            self.dragging_volume = True
            self.set_volume_from_x(event.pos[0])
elif self.state is ScreenState.GAME:
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            self.state = ScreenState.MENU
        elif event.key == pygame.K_SPACE:
            self.game.start_wave()
```

`set_volume()` must assign `self.volume = clamp(int(value), 0, 100)`. `set_volume_from_x()` maps the slider track to that range. `App.handle_event()` delegates game mouse events to `Game.handle_click()` and never starts a wave when entering the game.

- [ ] **Step 2: Run focused tests and verify green**

Run:

```bash
python -m unittest test_ui -v
```

Expected: all tests pass.

- [ ] **Step 3: Run syntax verification**

Run:

```bash
python -m py_compile ui.py test_ui.py
```

Expected: exit code 0 and no output.

- [ ] **Step 4: Commit the architecture**

```bash
git add ui.py test_ui.py
git commit -m "feat: make pygame ui standalone"
```

---

### Task 3: Add visual system and curved brick wall

**Files:**
- Modify: `ui.py`
- Modify: `test_ui.py` only if a geometry assertion needs strengthening

**Interfaces:**
- `build_brick_wall(size: tuple[int, int]) -> pygame.Surface` returns a transparent full-screen layer.
- `draw_menu(surface, app)`, `draw_settings(surface, app)`, and `Game.draw(surface)` render complete screens.
- `draw_play_icon(surface, center, radius, color)` and `draw_gear_icon(surface, center, radius, color)` draw primitive-only icons.

- [ ] **Step 1: Write or strengthen wall assertions before visual implementation**

Add this assertion to `test_brick_wall_surface_has_content`:

```python
self.assertEqual(wall.get_flags() & pygame.SRCALPHA, pygame.SRCALPHA)
```

Run the focused test and confirm it fails if the surface is not alpha-enabled.

- [ ] **Step 2: Implement deterministic wall rendering**

`build_brick_wall()` creates an alpha surface, fills a straight right-side rectangle outside the road, then draws staggered brown brick rectangles and black mortar. Use a fixed color sequence indexed by `(row + column) % 3`; do not use random state. Do not draw a semicircle, gate, flags, crenellations, sine strips, or the old shadow.

Required core shape and palette:

```python
wall = pygame.Surface(size, pygame.SRCALPHA)
wall_width = 120
left = width - wall_width
pygame.draw.rect(wall, WALL_BASE, (left, 0, wall_width, height))
brick_colors = (DARK_BRICK, BRICK_RED, BRICK_HIGHLIGHT)
```

Brick and seam drawing must remain inside the right-side wall area. Blit the wall after the field/path and before towers, enemies, projectiles, and UI panels.

- [ ] **Step 3: Implement menu, settings, and polished game rendering**

Use dark background bands for the menu, centered green play circle with white triangle, left settings button with a gear made from circles/lines, hover colors, and a 0-100 slider. Game rendering uses deep green bands, warm path tiles, translucent panels, readable status labels, selected tower borders, a visible Start Wave button, and a centered Game Over card.

- [ ] **Step 4: Run focused tests and headless render smoke test**

Run:

```bash
python -m unittest test_ui -v
SDL_VIDEODRIVER=dummy python -c "import pygame; import ui; pygame.init(); s=pygame.Surface((ui.WIDTH, ui.HEIGHT)); a=ui.App(screen=s); a.draw(); a.state=ui.ScreenState.SETTINGS; a.draw(); a.state=ui.ScreenState.GAME; a.draw(); print('render smoke ok'); pygame.quit()"
```

Expected: all tests pass and output contains `render smoke ok`.

- [ ] **Step 5: Commit visuals**

```bash
git add ui.py test_ui.py
git commit -m "feat: add menu settings and curved brick wall"
```

---

### Task 4: Full verification and audit cleanup

**Files:**
- Modify: `ui.py` only for defects found by verification

- [ ] **Step 1: Run all checks**

```bash
python -m unittest discover -v
python -m py_compile ui.py test_ui.py
SDL_VIDEODRIVER=dummy python -c "import pygame; import ui; pygame.init(); s=pygame.Surface((ui.WIDTH, ui.HEIGHT)); a=ui.App(screen=s); a.run(max_frames=1); pygame.quit(); print('app smoke ok')"
```

Expected: tests pass, compilation exits 0, and output contains `app smoke ok`.

- [ ] **Step 2: Audit independence and diff scope**

```bash
rg -n "tower_defence|auto|wave_timer|pygame\.init\(\)" ui.py
rtk git diff --check
rtk git status --short
```

Expected: no `tower_defence` match, no automatic-wave timer, startup only in `main()`, no whitespace errors, and `tower_defence.py` absent from changed files.

- [ ] **Step 3: Commit any verification fixes**

```bash
git add ui.py test_ui.py
git commit -m "fix: polish standalone pygame ui"
```
