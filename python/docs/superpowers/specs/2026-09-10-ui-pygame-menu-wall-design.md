# `ui.py` Menu, Settings, and Curved Brick Wall

## Goal

Improve the Pygame application in `ui.py` as a fully standalone file.
`ui.py` must not import or depend on `tower_defence.py`. Add a menu-first flow,
volume settings, manual wave start, and a straight brick wall on the far right
outside the road. Keep the existing tower-defence mechanics, but remove global
state and
separate game behavior from screen flow.

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
  with a straight solid brick wall beyond the road on the far right.
- Draw brick fills with varied brown tones, black horizontal mortar lines, and
  staggered vertical seams.
- Keep the gameplay grid aligned to 40x40 cells and keep enemy waypoints on cell
  center lines.
- Use `Minecraft.otf` and copy game UI panel colors and margins from `td-ui.py`:
  120px bottom bar, black panel, Gold/Lives at x=40, Wave at x=220, and 80x70
  tower buttons starting at x=400.
- Improve visual hierarchy, hover states, panels, status display, and Game Over
  overlay using Pygame primitives and the bundled Minecraft font.
- Add focused tests for screen flow, manual wave behavior, volume bounds, and
  wall geometry helpers where practical.

### Out of scope

- Changes to `tower_defence.py`; that file remains untouched.
- Any import or runtime dependency from `ui.py` to `tower_defence.py`.
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

- Dark navy-green menu background with green accent.
- `td-ui.py` game palette: green field `(0, 100, 0)`, yellow path `(176, 163,
  44)`, black bottom panel, blue rapid tower `(0, 0, 200)`, yellow-orange
  cannon `(255, 229, 84)`, and gold `(255, 230, 20)`.
- Gold currency, white labels, red danger states, and consistent shadows.
- Menu title `TOWER DEFENCE` with subtitle `BUILD · DEFEND · SURVIVE`.
- Circular Play button has shadow, outline, hover color, and white triangle.
- Settings uses a clear slider track, knob, percentage label, and Back button.
- Game status is compact and readable; tower selection and wave control are
  visually distinct.

## Right brick wall

The wall is rendered to a transparent rectangular surface at the far right,
starting after the last road cell. The surface is filled with staggered brick
rows. Horizontal and vertical mortar lines are straight black lines. Brick
colors are deterministic and varied among dark, base, and highlighted brown
tones. The wall must not reintroduce the old gate, flags, crenellations,
semicircle, sine offsets, or strip shadow. Wall cells are not buildable.

## Behavior requirements

- No auto-start timer exists after entering the game.
- Start Wave remains available whenever no wave is active and the game is not
  over.
- Volume slider clamps to `[0, 100]`.
- Menu and settings controls react to mouse clicks and hover.
- The gameplay grid is `40x40` with no visual offsets; towers and enemies use
  its cell centers.
- Enemy waypoints are centered on road cells.
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
- Confirm `ui.py` has no `tower_defence` import or runtime reference.
