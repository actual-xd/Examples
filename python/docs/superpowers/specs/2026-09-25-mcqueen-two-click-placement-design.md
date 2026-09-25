# McQueen enemy and two-click tower placement

## Goal

Add a data-driven `mcqueen` enemy type and replace immediate tower placement with a two-click preview flow.

## Enemy types

Define `ENEMY_TYPES` beside `TOWER_TYPES`.

| Type | HP multiplier | Speed multiplier | Gold multiplier | Life damage |
|---|---:|---:|---:|---:|
| `normal` | 1.0 | 1.0 | 1.0 | 1 |
| `mcqueen` | 0.6 | 2.0 | 0.8 | 2 |

`Enemy` accepts an optional type that defaults to `normal`, preserving existing callers. It applies the selected type's multipliers to each wave's base HP, speed, and gold. HP and gold use `int()` to retain integer game values.

Each wave counts spawned enemies from one. Every fifth enemy, including the 10th and 15th, is `mcqueen`. All others are `normal`. The count restarts for each wave.

When an enemy reaches the end, `Game` subtracts that enemy's configured life damage instead of one fixed life.

## Two-click placement state

`Game.pending_cell` stores the one cell with an active placement preview. No temporary `Tower` enters `Game.towers`.

A first left-click on a valid free cell stores that cell in `pending_cell`. It does not create a tower or spend gold. A second left-click on the same cell revalidates the cell and current tower cost. If valid and affordable, it creates the currently selected tower, spends its cost, emits `gold_changed`, and clears `pending_cell`.

A left-click on another valid free cell moves `pending_cell` there. That click never installs a tower. Installation requires another click on the new cell.

## Type changes during preview

Changing the selected tower through a shop card or keyboard shortcut keeps `pending_cell`. Preview radius and color immediately use the new `TOWER_TYPES[selected]` values. Confirmation installs the current type and checks its current cost.

If the new type is unaffordable, confirmation creates nothing and keeps the preview. Selecting an affordable type later allows confirmation on the same cell.

## Placement validation

Both preview selection and confirmation require a cell that is:

- inside the playable grid;
- left of the wall;
- outside `PATH_CELLS`;
- not occupied by a tower;
- available while the game is not over.

Confirmation repeats every check. This prevents stale preview state from placing onto a cell that became invalid or occupied.

Invalid left-clicks on the path, wall, or outside the field do not replace or clear an existing preview. Right and middle clicks do not change it.

## Existing controls and competing states

- Clicking a shop card changes `selected`, keeps `pending_cell`, and closes any delete menu.
- Keyboard keys `1` and `2` change `selected` and keep `pending_cell`.
- Clicking the wave-start button starts the wave and keeps `pending_cell`.
- Clicking an existing tower clears `pending_cell` and opens the existing delete menu.
- Clicking a valid free cell while the delete menu is open closes that menu and selects the clicked cell for preview in the same click.
- Clicking an invalid location while the delete menu is open closes that menu without creating a preview.
- Confirming deletion does not create a preview.
- Pause prevents game clicks because the pause screen owns input. Returning to the same game restores its preview unchanged.
- Returning to the main menu does not reset the existing game, matching current behavior. Starting a reset game clears the preview.
- Entering game-over state clears pending and delete state, so stale controls do not remain under the overlay.
- `Game.reset()` clears pending, hover, and delete state.
- Successful placement clears `pending_cell`; the next click on that tower follows deletion behavior.

Tower placement remains available during active waves, matching current behavior. Mouse movement only updates `hover_cell`; it never moves or confirms `pending_cell`.

## Rendering

Draw pending range independently from built towers:

- center on `pending_cell`;
- use current selected tower's range and color;
- draw translucent fill and visible outline;
- do not create a temporary tower or include preview in targeting, firing, collision, or occupied-cell checks;
- keep preview visible when the pointer leaves its cell;
- skip drawing if external state makes the pending cell invalid, without creating or moving a tower.

Built tower ranges retain current behavior and appear only when `hover_cell` matches that tower's cell. A pending range and a hovered built-tower range can appear together. Leaving the playfield clears hover range but not pending range.

## Verification

Add focused tests before implementation:

1. First click selects preview without spending gold or creating a tower.
2. Second click on the same cell installs and clears preview.
3. Clicking another valid cell moves preview and requires a new confirmation.
4. Card and keyboard type changes update the tower installed by confirmation.
5. Confirmation uses the current type's price.
6. Insufficient gold leaves preview active without creating a tower.
7. Path, wall, occupied, and out-of-bounds cells cannot become confirmed placements.
8. Reset, game over, and successful placement clear preview state.
9. Delete-menu transitions neither place a tower nor leave conflicting pending state.
10. Preview is not a live tower and built ranges remain hover-only.
11. Pause and mouse movement do not mutate pending placement.
12. `mcqueen` uses 0.6 HP, 2.0 speed, 0.8 gold, and two life damage.
13. Every fifth spawn is `mcqueen`, with counting reset for each wave.
14. A leaked `mcqueen` removes two lives.

Run the focused tests, full `test_ui.py`, `py_compile`, and `git diff --check`.

## Scope limits

No new tower types, refunds, keyboard grid cursor, wave composition UI, or changes to wave scaling. Existing unrelated working-tree changes remain untouched.
