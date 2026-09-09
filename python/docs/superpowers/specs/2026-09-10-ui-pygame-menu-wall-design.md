# `ui.py` Menu, Settings, and Curved Brick Wall

## Goal

Improve the Pygame application in `ui.py` without modifying `tower_defence.py`.
Add a menu-first flow, volume settings, manual wave start, and a solid curved
brick wall on the right side. Keep the existing tower-defence mechanics, but
remove global state and separate game behavior from screen flow.

## Scope

### In scope

- `MENU`, `SETTINGS`, and `GAME` screen states.
- Centered green circular Play button with a play icon.
- Settings button on the left side of the menu.
- Settings screen with a 0-100 volume slider stored in memory.
- Play opens the game; wave never starts automatically.
- Existing Start Wave button remains visible in the game.
- `SPACE` starts a wave; `ESC` returns to menu without resetting the game;
  `R` restarts after Game Over.
- Replace the current sine-shifted wall, gate, flags, crenellations, and shadow
  with a solid right-side semicircular brick wall.
- Draw brick fills with varied brown tones, black curved horizontal mortar
  lines, and staggered vertical seams.
- Improve visual hierarchy, hover states, panels, status display, and Game Over
  overlay using Pygame primitives and system fonts only.
- Add focused tests for screen flow, manual wave behavior, volume bounds, and
  wall geometry helpers where practical.

### Out of scope

- Changes to `tower_defence.py`.
- New external dependencies.
- Audio assets or actual sound playback. Volume is persisted in the current
  process and ready for future audio integration.
- New gameplay systems, enemy types, or tower types.

## Architecture

`main()` owns Pygame initialization, the event loop, clock, current screen, and
shutdown. A `Game` object owns tower-defence state and game rendering. Small
helpers own reusable drawing and hit-testing logic. Screen transitions are
explicit and do not rely on implicit global flags.

The initial state is `MENU`. Menu Play changes state to `GAME`; menu Settings
changes state to `SETTINGS`; Settings Back changes state to `MENU`. Returning to
`MENU` does not reset the current `Game` object. A wave starts only through the
Start Wave button or `SPACE` while in the game screen.

## Visual design

- Dark navy-green menu background with green accent `#50D890`.
- Deep green play field with a warm path and dark translucent UI panels.
- Gold currency, white labels, red danger states, and consistent shadows.
- Menu title `TOWER DEFENCE` with subtitle `BUILD · DEFEND · SURVIVE`.
- Circular Play button has shadow, outline, hover color, and white triangle.
- Settings uses a clear slider track, knob, percentage label, and Back button.
- Game status is compact and readable; tower selection and wave control are
  visually distinct.

## Curved wall

The wall is rendered to a transparent surface clipped by a filled semicircle
near the right edge. The surface is filled with staggered brick rows. Each row
uses a curved horizontal seam derived from the semicircle boundary. Vertical
seams are placed between neighboring bricks and clipped to the wall mask.
Brick colors are deterministic and varied among dark, base, and highlighted
brown tones. Mortar lines are black with a small width. The wall must not
reintroduce the old gate, flags, crenellations, sine offsets, or strip shadow.

## Behavior requirements

- No auto-start timer exists after entering the game.
- Start Wave remains available whenever no wave is active and the game is not
  over.
- Volume slider clamps to `[0, 100]`.
- Menu and settings controls react to mouse clicks and hover.
- Game controls retain existing mouse placement/deletion and keyboard tower
  selection behavior.
- Closing the window exits cleanly.

## Verification

- Add tests before production changes for screen transitions, manual-only wave
  start, volume clamping, and curved wall helper output.
- Run focused tests and the complete test suite.
- Run `python -m py_compile ui.py`.
- Run a headless Pygame smoke test with `SDL_VIDEODRIVER=dummy` that creates the
  app and renders each screen without opening a window.
- Confirm `tower_defence.py` remains unchanged.
