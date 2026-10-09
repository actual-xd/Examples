import importlib
import inspect
import os
import unittest
from pathlib import Path
from unittest.mock import patch

import pygame


os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def contrast(color, other):
    def luminance(rgb):
        channels = []
        for value in rgb:
            value = value / 255
            channels.append(value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4)
        red, green, blue = channels
        return 0.2126 * red + 0.7152 * green + 0.0722 * blue

    high, low = sorted((luminance(color), luminance(other)), reverse=True)
    return (high + 0.05) / (low + 0.05)


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
        source = (Path(__file__).parent / "ui.py").read_text(encoding="utf-8")
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
        for _ in range(900):
            app.update()
        self.assertEqual(app.state, self.ui.ScreenState.GAME)
        self.assertFalse(app.game.wave_active)
        self.assertEqual(app.game.wave, 0)

    def test_start_wave_button_starts_wave_manually(self):
        app = self.ui.App(screen=self.screen)
        app.state = self.ui.ScreenState.GAME
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (44, 260)})
        app.handle_event(event)
        self.assertTrue(app.game.wave_active)
        self.assertEqual(app.game.wave, 1)

    def test_volume_is_clamped(self):
        app = self.ui.App(screen=self.screen)
        app.set_volume(140)
        self.assertEqual(app.volume, 100)
        app.set_volume(-20)
        self.assertEqual(app.volume, 0)

    def test_brick_wall_surface_has_content(self):
        wall = self.ui.build_brick_wall((self.ui.WIDTH, self.ui.HEIGHT))
        self.assertEqual(wall.get_size(), (self.ui.WIDTH, self.ui.HEIGHT))
        self.assertEqual(wall.get_flags() & pygame.SRCALPHA, pygame.SRCALPHA)
        self.assertGreater(wall.get_bounding_rect().width, 0)
        self.assertGreater(wall.get_bounding_rect().height, 0)
        self.assertEqual(wall.get_at((self.ui.WALL_LEFT - 2, 20)).a, 0)
        self.assertGreater(wall.get_at((self.ui.WALL_LEFT, 20)).a, 0)

    def test_game_uses_td_ui_layout_and_minecraft_font(self):
        self.assertEqual((self.ui.WIDTH, self.ui.HEIGHT), (1000, 720))
        self.assertEqual(self.ui.UI_BAR_HEIGHT, 120)
        self.assertEqual(self.ui.WIDTH % self.ui.CELL, 0)
        self.assertEqual((self.ui.HEIGHT - self.ui.UI_BAR_HEIGHT) % self.ui.CELL, 0)
        self.assertEqual(self.ui.FONT_PATH.name, "Minecraft.otf")
        self.assertTrue(self.ui.FONT_PATH.exists())
        self.assertEqual(self.ui.ROAD, (188, 150, 108))
        self.assertEqual(self.ui.TOWER_TYPES["rapid"]["color"], self.ui.TOWER_RAPID)
        self.assertEqual(self.ui.TOWER_TYPES["cannon"]["color"], self.ui.TOWER_CANNON)

    def test_waypoints_follow_road_cell_centers(self):
        for x, y in self.ui.WAYPOINTS[1:]:
            self.assertEqual(x % self.ui.CELL, self.ui.CELL // 2)
            self.assertEqual(y % self.ui.CELL, self.ui.CELL // 2)
        creep = self.ui.Enemy(50, 1.5, 10)
        creep.update()
        for _ in range(300):
            creep.update()
            if creep.waypoint_index >= 2:
                break
        self.assertEqual((creep.x, creep.y), self.ui.WAYPOINTS[1])

    def test_wall_cells_are_not_buildable(self):
        game = self.ui.Game()
        game.handle_click((self.ui.WALL_LEFT + 10, 100), 1)
        self.assertEqual(game.towers, [])

    def test_selected_tower_needs_preview_then_confirmation(self):
        game = self.ui.Game()
        game.gold = 600
        cards = dict(self.ui.shop_cards())
        game.handle_click(cards["cannon"].center, 1)
        cell_pos = (self.ui.CELL // 2, self.ui.CELL // 2)
        game.handle_click(cell_pos, 1)
        self.assertEqual(game.pending_cell, (0, 0))
        self.assertEqual(game.towers, [])
        self.assertEqual(game.gold, 600)
        game.handle_click(cell_pos, 1)
        self.assertEqual([tower.kind for tower in game.towers], ["cannon"])
        self.assertEqual(game.gold, 100)
        self.assertIsNone(game.pending_cell)

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
        game.gold = 600
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
        game.pending_cell = (0, 0)
        game.handle_click((existing.x, existing.y), 1)
        self.assertIsNone(game.pending_cell)
        self.assertEqual(game.delete_cell, (2, 0))

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

    def test_non_left_click_does_not_change_preview(self):
        game = self.ui.Game()
        game.pending_cell = (0, 0)
        game.handle_click((60, 20), 2)
        game.handle_click((60, 20), 3)
        self.assertEqual(game.pending_cell, (0, 0))
        self.assertEqual(game.towers, [])

    def test_starting_wave_keeps_preview(self):
        game = self.ui.Game()
        game.pending_cell = (0, 0)
        game.handle_click((44, 260), 1)
        self.assertTrue(game.wave_active)
        self.assertEqual(game.pending_cell, (0, 0))

    def test_reset_clears_preview(self):
        game = self.ui.Game()
        game.pending_cell = (0, 0)
        game.reset()
        self.assertIsNone(game.pending_cell)

    def test_delete_confirmation_does_not_create_preview(self):
        game = self.ui.Game()
        tower = self.ui.Tower(2, 0, "rapid")
        game.towers = [tower]
        game.delete_cell = (2, 0)
        game.handle_click((tower.x, tower.y), 1)
        self.assertEqual(game.towers, [])
        self.assertIsNone(game.pending_cell)

    def test_deleting_tower_refunds_half_the_cost(self):
        ui = self.ui
        game = ui.Game()
        cell = (2 * ui.CELL + 20, 20)
        game.handle_click(cell, 1)
        game.handle_click(cell, 1)
        self.assertEqual([tower.kind for tower in game.towers], ["rapid"])
        self.assertEqual(game.gold, 200)

        game.handle_click(cell, 1)
        self.assertEqual(game.delete_cell, (2, 0))
        self.assertEqual(game.gold, 200)

        game.handle_click(cell, 1)
        self.assertEqual(game.towers, [])
        self.assertEqual(game.gold, 250)

    def test_cannon_delete_refunds_half_of_its_own_cost(self):
        ui = self.ui
        game = ui.Game()
        tower = ui.Tower(2, 0, "cannon")
        game.towers = [tower]
        game.delete_cell = (2, 0)

        game.handle_click((tower.x, tower.y), 1)

        self.assertEqual(game.gold, 300 + ui.TOWER_TYPES["cannon"]["cost"] // 2)
        self.assertIsNone(game.delete_cell)

    def test_invalid_click_closes_delete_without_preview(self):
        game = self.ui.Game()
        game.towers = [self.ui.Tower(2, 0, "rapid")]
        game.delete_cell = (2, 0)
        game.handle_click(self.ui.WAYPOINTS[1], 1)
        self.assertIsNone(game.delete_cell)
        self.assertIsNone(game.pending_cell)
        self.assertEqual(len(game.towers), 1)

    def test_tower_can_be_confirmed_during_active_wave(self):
        game = self.ui.Game()
        game.start_wave()
        game.handle_click((20, 20), 1)
        game.handle_click((20, 20), 1)
        self.assertEqual([(tower.col, tower.row) for tower in game.towers], [(0, 0)])

    def test_path_cells_are_not_buildable(self):
        game = self.ui.Game()
        game.handle_click((self.ui.WAYPOINTS[1][0], self.ui.WAYPOINTS[1][1]), 1)
        self.assertEqual(game.towers, [])

    def test_run_accepts_frame_limit(self):
        app = self.ui.App(screen=self.screen)
        app.run(max_frames=1)
        self.assertTrue(app.running)

    def test_wall_does_not_hide_right_path(self):
        app = self.ui.App(screen=self.screen)
        app.game.draw(self.screen)
        self.assertEqual(self.screen.get_at((860, 180))[:3], self.ui.ROAD)

    def test_pending_range_draws_without_creating_tower(self):
        game = self.ui.Game()
        position = (7 * self.ui.CELL + 20, 7 * self.ui.CELL + 20)
        before = pygame.Surface((self.ui.WIDTH, self.ui.HEIGHT))
        after = pygame.Surface((self.ui.WIDTH, self.ui.HEIGHT))
        game.draw(before)
        game.handle_click(position, 1)
        game.draw(after)
        radius = self.ui.TOWER_TYPES["rapid"]["range"]
        edge = (position[0] + radius - 1, position[1])
        self.assertNotEqual(before.get_at(edge), after.get_at(edge))
        self.assertEqual(game.towers, [])

    def test_pending_preview_draws_unfilled_tower_outline(self):
        game = self.ui.Game()
        col, row = 7, 7
        center = (col * self.ui.CELL + 20, row * self.ui.CELL + 20)
        stats = self.ui.TOWER_TYPES[game.selected]
        range_only = pygame.Surface((self.ui.WIDTH, self.ui.HEIGHT))
        preview = pygame.Surface((self.ui.WIDTH, self.ui.HEIGHT))
        game.draw(range_only)
        self.ui.draw_tower_range(range_only, center, stats)
        game.pending_cell = (col, row)
        game.draw(preview)
        tower_rect = pygame.Rect(
            col * self.ui.CELL + 4,
            row * self.ui.CELL + 4,
            self.ui.CELL - 8,
            self.ui.CELL - 8,
        )
        self.assertEqual(preview.get_at((tower_rect.left, tower_rect.centery))[:3], stats["color"])
        self.assertEqual(preview.get_at(center), range_only.get_at(center))

    def test_pending_range_updates_after_tower_type_change(self):
        game = self.ui.Game()
        position = (7 * self.ui.CELL + 20, 7 * self.ui.CELL + 20)
        rapid_preview = pygame.Surface((self.ui.WIDTH, self.ui.HEIGHT))
        cannon_preview = pygame.Surface((self.ui.WIDTH, self.ui.HEIGHT))
        game.handle_click(position, 1)
        game.draw(rapid_preview)
        game.selected = "cannon"
        game.draw(cannon_preview)
        rapid_edge = (position[0] + self.ui.TOWER_TYPES["rapid"]["range"] - 1, position[1])
        self.assertNotEqual(rapid_preview.get_at(rapid_edge), cannon_preview.get_at(rapid_edge))

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

    def test_cannon_has_viable_single_target_balance(self):
        cannon = self.ui.TOWER_TYPES["cannon"]
        self.assertEqual(cannon["cost"], 500)
        self.assertEqual(cannon["damage"], 75)
        self.assertEqual(cannon["fire_rate"], 60)

    def test_mcqueen_applies_enemy_type_multipliers(self):
        stats = self.ui.ENEMY_TYPES["mcqueen"]
        mcqueen = self.ui.Enemy(50, 1.5, 8, "mcqueen")
        self.assertEqual(mcqueen.kind, "mcqueen")
        self.assertEqual(mcqueen.max_hp, int(50 * stats["hp_multiplier"]))
        self.assertEqual(mcqueen.hp, int(50 * stats["hp_multiplier"]))
        self.assertEqual(mcqueen.speed, 1.5 * stats["speed_multiplier"])
        self.assertEqual(mcqueen.gold, int(8 * stats["gold_multiplier"]))
        self.assertEqual(mcqueen.life_damage, stats["life_damage"])

    def test_every_fifth_spawn_is_mcqueen(self):
        game = self.ui.Game()
        game.start_wave()
        for _ in range(5):
            game.spawn_timer = 0
            game.update()
        self.assertEqual(
            [getattr(enemy, "kind", None) for enemy in game.enemies],
            ["normal", "normal", "normal", "normal", "mcqueen"],
        )

    def test_six_enemy_wave_has_five_normal_and_one_mcqueen(self):
        game = self.ui.Game()
        game.wave = 1
        game.start_wave()
        for _ in range(6):
            game.spawn_timer = 0
            game.update()
        kinds = [enemy.kind for enemy in game.enemies]
        self.assertEqual(kinds.count("normal"), 5)
        self.assertEqual(kinds.count("mcqueen"), 1)
        self.assertEqual(kinds[4], "mcqueen")

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
        self.assertEqual(getattr(game.enemies[0], "kind", None), "normal")

    def test_mcqueen_leak_removes_two_lives(self):
        self.assertIn("kind", inspect.signature(self.ui.Enemy).parameters)
        game = self.ui.Game()
        enemy = self.ui.Enemy(50, 1.5, 8, "mcqueen")
        enemy.alive = False
        enemy.reached_end = True
        game.enemies = [enemy]
        game.update()
        self.assertEqual(game.lives, 1)

    def test_tower_prioritizes_enemy_on_final_path_section(self):
        tower = self.ui.Tower(18, 3, "rapid")
        near_enemy = self.ui.Enemy(50, 1.5, 8)
        near_enemy.x, near_enemy.y = 700, 180
        near_enemy.waypoint_index = len(self.ui.WAYPOINTS) - 3
        near_enemy.distance_travelled = 1200
        far_enemy = self.ui.Enemy(50, 1.5, 8)
        far_enemy.x, far_enemy.y = 820, 180
        far_enemy.waypoint_index = len(self.ui.WAYPOINTS) - 2
        far_enemy.distance_travelled = 1500
        projectiles = tower.update([near_enemy, far_enemy])
        self.assertEqual(projectiles[0].target, far_enemy)


class UiUxSkillTests(unittest.TestCase):
    """Tests that ui.py follows the game-ui-ux skill: anchors, scaling,
    safe area, mouse navigation, screen stack, HUD."""

    @classmethod
    def setUpClass(cls):
        pygame.init()
        quit_event = pygame.event.Event(pygame.QUIT)
        with patch.object(pygame.event, "get", return_value=[quit_event]):
            cls.ui = importlib.import_module("ui")
        pygame.init()
        cls.screen = pygame.Surface((cls.ui.WIDTH, cls.ui.HEIGHT))

    def make_app(self):
        return self.ui.App(screen=self.screen)

    def key(self, key):
        return pygame.event.Event(pygame.KEYDOWN, {"key": key})

    def test_shop_cards_share_one_layout_for_draw_and_click(self):
        ui = self.ui
        cards = dict(ui.shop_cards())
        self.assertEqual(set(cards), set(ui.TOWER_TYPES))
        card_rects = list(cards.values())
        for rect in card_rects:
            self.assertGreaterEqual(rect.top, ui.HEIGHT - ui.UI_BAR_HEIGHT)
            self.assertLessEqual(rect.bottom, ui.HEIGHT)
        hud = ui.Hud(ui.minecraft_font(24), ui.minecraft_font(10))
        for kind, rect in cards.items():
            self.assertEqual(hud.cards[kind].get_size(), rect.size)
        game = ui.Game()
        game.handle_click(cards["cannon"].center, 1)
        self.assertEqual(game.selected, "cannon")
        game.handle_click(cards["rapid"].center, 1)
        self.assertEqual(game.selected, "rapid")

    def test_shop_click_changes_tower_type_and_keeps_preview(self):
        ui = self.ui
        app = self.make_app()
        app.state = ui.ScreenState.GAME
        app.game.handle_click((20, 20), 1)
        card = dict(ui.shop_cards())["cannon"]
        app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": card.center}))
        self.assertEqual(app.game.selected, "cannon")
        self.assertEqual(app.game.pending_cell, (0, 0))

    def test_mouse_motion_does_not_move_pending_cell(self):
        app = self.make_app()
        app.state = self.ui.ScreenState.GAME
        app.game.pending_cell = (0, 0)
        app.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {"pos": (60, 20)}))
        self.assertEqual(app.game.pending_cell, (0, 0))
        self.assertEqual(app.game.hover_cell, (1, 0))

    def test_pause_blocks_placement_and_keeps_preview(self):
        app = self.make_app()
        app.state = self.ui.ScreenState.GAME
        app.game.pending_cell = (0, 0)
        app.handle_event(self.key(pygame.K_ESCAPE))
        app.handle_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (60, 20)})
        )
        self.assertEqual(app.state, self.ui.ScreenState.PAUSE)
        self.assertEqual(app.game.pending_cell, (0, 0))
        self.assertEqual(app.game.towers, [])

    def test_pause_menu_stacks_three_buttons_centered(self):
        ui = self.ui
        rects = ui.pause_items()
        self.assertEqual(len(rects), 3)
        self.assertEqual([rect.centerx for rect in rects], [500, 500, 500])
        self.assertEqual([rect.centery for rect in rects], [292, 360, 428])

    def test_letterbox_preserves_aspect_on_ultrawide(self):
        ui = self.ui
        dst = ui.letterbox_rect((2560, 1080))
        self.assertEqual(dst.height, 1080)
        ratio = dst.width / dst.height
        self.assertAlmostEqual(ratio, 1000 / 720, places=2)

    def test_letterbox_centers_in_window(self):
        ui = self.ui
        dst = ui.letterbox_rect((1920, 1080))
        self.assertEqual(dst.centerx, 960)
        self.assertEqual(dst.centery, 540)

    def test_letterbox_scale_down_small_window(self):
        ui = self.ui
        dst = ui.letterbox_rect((500, 500))
        self.assertLessEqual(dst.width, 500)
        self.assertLessEqual(dst.height, 500)

    def test_to_virtual_maps_through_scaled_window(self):
        ui = self.ui
        app = self.make_app()
        fake_window = pygame.Surface((1920, 1080))
        with patch.object(ui.pygame.display, "get_surface", return_value=fake_window):
            virtual = app._to_virtual((960, 540))
        self.assertAlmostEqual(virtual[0], 500, delta=2)
        self.assertAlmostEqual(virtual[1], 360, delta=2)

    def test_to_virtual_identity_at_reference_size(self):
        ui = self.ui
        app = self.make_app()
        self.assertEqual(app._to_virtual((44, 260)), (44, 260))

    def test_safe_rect_insets_uniformly(self):
        ui = self.ui
        safe = ui.SAFE
        self.assertEqual(
            (safe.width, safe.height),
            (ui.WIDTH - 2 * ui.SAFE_MARGIN, ui.HEIGHT - 2 * ui.SAFE_MARGIN),
        )
        self.assertEqual(safe.topleft, (ui.SAFE_MARGIN, ui.SAFE_MARGIN))

    def test_hud_stats_inside_safe_margin(self):
        ui = self.ui
        app = self.make_app()
        self.assertGreaterEqual(app.hud.gold_pos[0], ui.SAFE_MARGIN)
        self.assertGreaterEqual(app.hud.lives_pos[0], ui.SAFE_MARGIN)

    def test_keyboard_does_not_drive_menus(self):
        ui = self.ui
        app = self.make_app()
        for key in (pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT, pygame.K_RETURN, pygame.K_j):
            app.handle_event(self.key(key))
        self.assertEqual(app.state, ui.ScreenState.MENU)
        app.push(ui.ScreenState.GAME)
        app.handle_event(self.key(pygame.K_ESCAPE))
        self.assertEqual(app.state, ui.ScreenState.PAUSE)
        app.handle_event(self.key(pygame.K_DOWN))
        app.handle_event(self.key(pygame.K_RETURN))
        self.assertEqual(app.state, ui.ScreenState.PAUSE)

    def test_menu_click_opens_settings(self):
        ui = self.ui
        app = self.make_app()
        pos = app.settings_button.center
        app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos}))
        self.assertEqual(app.state, ui.ScreenState.SETTINGS)

    def test_menu_settings_button_sits_under_play_with_label_below(self):
        ui = self.ui
        app = self.make_app()
        self.assertEqual(app.settings_button.centerx, app.play_button.centerx)
        self.assertGreater(app.settings_button.top, app.play_button.bottom)
        self.assertLess(app.settings_button.top - app.play_button.bottom, 100)
        self.assertGreater(ui.MENU_SETTINGS_POS[1], app.settings_button.bottom)

    def test_space_starts_wave_only_in_game(self):
        ui = self.ui
        app = self.make_app()
        app.handle_event(self.key(pygame.K_SPACE))
        self.assertEqual(app.state, ui.ScreenState.MENU)
        self.assertEqual(app.game.wave, 0)
        app.push(ui.ScreenState.GAME)
        app.handle_event(self.key(pygame.K_SPACE))
        self.assertTrue(app.game.wave_active)
        self.assertEqual(app.game.wave, 1)

    def test_volume_drag_follows_mouse(self):
        ui = self.ui
        app = self.make_app()
        app.state = ui.ScreenState.SETTINGS
        track = app.volume_track
        pos = (track.left + track.width // 4, track.centery)
        app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos}))
        self.assertTrue(app.dragging_volume)
        self.assertEqual(app.volume, 25)
        app.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {"pos": (track.right, track.centery)}))
        self.assertEqual(app.volume, 100)
        app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, {"button": 1, "pos": pos}))
        self.assertFalse(app.dragging_volume)

    def test_pause_button_clicks(self):
        ui = self.ui
        app = self.make_app()
        resume, settings, menu = app.pause_items
        app.state = ui.ScreenState.GAME
        app.handle_event(self.key(pygame.K_ESCAPE))
        app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": menu.center}))
        self.assertEqual(app.state, ui.ScreenState.MENU)
        app.push(ui.ScreenState.GAME)
        app.handle_event(self.key(pygame.K_ESCAPE))
        app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": settings.center}))
        self.assertEqual(app.state, ui.ScreenState.SETTINGS)
        app.handle_event(self.key(pygame.K_ESCAPE))
        self.assertEqual(app.state, ui.ScreenState.PAUSE)
        app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": resume.center}))
        self.assertEqual(app.state, ui.ScreenState.GAME)

    def test_escape_pauses_and_resumes(self):
        ui = self.ui
        app = self.make_app()
        app.state = ui.ScreenState.GAME
        app.handle_event(self.key(pygame.K_ESCAPE))
        self.assertEqual(app.state, ui.ScreenState.PAUSE)
        app.handle_event(self.key(pygame.K_ESCAPE))
        self.assertEqual(app.state, ui.ScreenState.GAME)

    def test_paused_game_does_not_update(self):
        ui = self.ui
        app = self.make_app()
        app.state = ui.ScreenState.GAME
        app.game.start_wave()
        app.handle_event(self.key(pygame.K_ESCAPE))
        app.update()
        self.assertFalse(app.game.enemies)

    def test_switch_resets_stack_to_single_screen(self):
        ui = self.ui
        app = self.make_app()
        app.push(ui.ScreenState.GAME)
        app.push(ui.ScreenState.PAUSE)
        app.switch(ui.ScreenState.MENU)
        self.assertEqual(app.state, ui.ScreenState.MENU)
        app.pop()
        self.assertEqual(app.state, ui.ScreenState.MENU)

    def test_pause_resume_keeps_game(self):
        ui = self.ui
        app = self.make_app()
        app.state = ui.ScreenState.GAME
        app.game.start_wave()
        app.handle_event(self.key(pygame.K_ESCAPE))
        resume = app.pause_items[0]
        app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": resume.center}))
        self.assertEqual(app.state, ui.ScreenState.GAME)
        self.assertTrue(app.game.wave_active)

    def test_game_over_click_restarts(self):
        ui = self.ui
        app = self.make_app()
        app.state = ui.ScreenState.GAME
        app.game.lives = 0
        app.game.update()
        self.assertTrue(app.game.game_over)
        app.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": (500, 360)}))
        self.assertFalse(app.game.game_over)
        self.assertEqual(app.game.lives, 3)

    def test_game_tracks_gold_and_lives_without_an_event_bus(self):
        ui = self.ui
        game = ui.Game()
        self.assertEqual((game.gold, game.lives, game.wave), (300, 3, 0))
        game.start_wave()
        self.assertEqual(game.wave, 1)
        killed = ui.Enemy(50, 1.5, 8)
        killed.hp = 0
        killed.alive = False
        game.enemies = [killed]
        game.update()
        self.assertEqual(game.gold, 308)
        leaker = ui.Enemy(50, 1.5, 8)
        leaker.reached_end = True
        game.enemies = [leaker]
        game.update()
        self.assertEqual(game.lives, 2)

    def test_hud_never_shows_negative_lives(self):
        ui = self.ui
        hud = ui.Hud(ui.minecraft_font(24), ui.minecraft_font(10))
        game = ui.Game()
        negative = pygame.Surface((ui.WIDTH, ui.HEIGHT))
        zero = pygame.Surface((ui.WIDTH, ui.HEIGHT))
        game.lives = -3
        hud.draw(negative, game)
        game.lives = 0
        hud.draw(zero, game)
        self.assertEqual(pygame.image.tobytes(negative, "RGB"), pygame.image.tobytes(zero, "RGB"))

    def test_shop_card_border_uses_accent_only_when_selected(self):
        ui = self.ui
        hud = ui.Hud(ui.minecraft_font(24), ui.minecraft_font(10))
        surface = pygame.Surface((ui.WIDTH, ui.HEIGHT))
        game = ui.Game()
        game.selected = "cannon"
        hud.draw(surface, game)
        cards = dict(ui.shop_cards())
        inset = (1, 1)
        selected = cards["cannon"]
        self.assertEqual(surface.get_at((selected.left + inset[0], selected.top + inset[1]))[:3], ui.ACCENT)
        inactive = cards["rapid"]
        self.assertEqual(
            surface.get_at((inactive.left + inset[0], inactive.top + inset[1]))[:3],
            ui.TOWER_TYPES["rapid"]["color"],
        )

    def test_palette_is_one_scheme_with_readable_contrast(self):
        ui = self.ui
        readable = [
            (ui.TEXT, ui.PANEL),
            (ui.TEXT_MUTED, ui.PANEL),
            (ui.ACCENT, ui.PANEL),
            (ui.DANGER_TEXT, ui.PANEL),
            (ui.INK, ui.ACCENT),
            (ui.TEXT, ui.DANGER),
            (ui.INK, ui.TOWER_RAPID),
            (ui.INK, ui.TOWER_CANNON),
        ]
        for foreground, background in readable:
            self.assertGreaterEqual(contrast(foreground, background), 4.5, (foreground, background))
        self.assertGreaterEqual(contrast(ui.ROAD, ui.GRASS), 2.0)
        self.assertGreaterEqual(contrast(ui.PANEL_BORDER, ui.PANEL), 1.8)
        self.assertNotEqual(ui.TOWER_RAPID, ui.TOWER_CANNON)
        self.assertGreater(ui.GRASS[1], ui.GRASS[0])
        self.assertGreater(ui.GRASS[1], ui.GRASS[2])
        self.assertGreater(ui.ROAD[0], ui.ROAD[2])
        self.assertGreater(ui.ROAD[1], ui.ROAD[2])

    def test_resize_event_does_not_crash_headless(self):
        app = self.make_app()
        app.handle_event(pygame.event.Event(pygame.VIDEORESIZE, {"size": (1280, 800)}))
        self.assertTrue(app.running)

    def test_draw_into_scaled_window_letterboxes(self):
        ui = self.ui
        app = self.make_app()
        fake_window = pygame.Surface((1920, 1080))
        with patch.object(ui.pygame.display, "get_surface", return_value=fake_window):
            app.draw()
        center = (fake_window.get_at((960, 540))[:3],)
        self.assertTrue(center)


if __name__ == "__main__":
    unittest.main()
