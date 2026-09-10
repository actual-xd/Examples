import importlib
import os
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
        self.assertEqual(self.ui.PATH, (176, 163, 44))
        self.assertEqual(self.ui.TOWER_TYPES["rapid"]["color"], (0, 0, 200))

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
        self.assertIsNone(game.placing_cell)

    def test_clamp_handles_middle_value(self):
        self.assertEqual(self.ui.clamp(55, 0, 100), 55)

    def test_run_accepts_frame_limit(self):
        app = self.ui.App(screen=self.screen)
        app.run(max_frames=1)
        self.assertTrue(app.running)

    def test_wall_does_not_hide_right_path(self):
        app = self.ui.App(screen=self.screen)
        app.game.draw(self.screen)
        self.assertEqual(self.screen.get_at((860, 180))[:3], self.ui.PATH)

    def test_cannon_has_viable_single_target_balance(self):
        cannon = self.ui.TOWER_TYPES["cannon"]
        self.assertEqual(cannon["cost"], 200)
        self.assertEqual(cannon["damage"], 75)
        self.assertEqual(cannon["fire_rate"], 60)

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
    safe area, focus navigation, screen stack, event-driven HUD."""

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

    # --- anchors + containers ---

    def test_anchor_place_centers_in_canvas(self):
        ui = self.ui
        rect = ui.Layout.place(ui.SCREEN_RECT, ("center", "middle"), 100, 50)
        self.assertEqual(rect.center, (500, 360))

    def test_anchor_point_offsets_from_edge(self):
        ui = self.ui
        point = ui.Layout.anchor_point(ui.SCREEN_RECT, ("left", "bottom"), (30, -40))
        self.assertEqual(point, (30, 680))

    def test_hbox_flows_children_with_gap(self):
        ui = self.ui
        area = ui.pygame.Rect(300, 638, 200, 70)
        rects = ui.Layout.hbox(area, [80, 80], 70, 40)
        self.assertEqual(len(rects), 2)
        self.assertEqual(rects[0].topleft, (300, 638))
        self.assertEqual(rects[1].left - rects[0].right, 40)

    def test_vbox_flows_children_vertically(self):
        ui = self.ui
        rects = ui.Layout.vbox(ui.SCREEN_RECT, 3, 260, 52, 16)
        self.assertEqual(len(rects), 3)
        self.assertEqual(rects[1].top - rects[0].bottom, 16)
        self.assertEqual(rects[0].centerx, 500)

    def test_shop_cards_share_one_layout_for_draw_and_click(self):
        ui = self.ui
        cards = dict(ui.shop_cards())
        self.assertEqual(set(cards), set(ui.TOWER_TYPES))
        card_rects = list(cards.values())
        for rect in card_rects:
            # cards live inside the bottom UI bar
            self.assertGreaterEqual(rect.top, ui.HEIGHT - ui.UI_BAR_HEIGHT)
        # clicking the drawn card center selects that tower
        game = ui.Game()
        game.handle_click(cards["cannon"].center, 1)
        self.assertEqual(game.selected, "cannon")
        game.handle_click(cards["rapid"].center, 1)
        self.assertEqual(game.selected, "rapid")

    # --- scaling / letterbox ---

    def test_letterbox_preserves_aspect_on_ultrawide(self):
        ui = self.ui
        dst = ui.letterbox_rect((2560, 1080), (1000, 720))
        self.assertEqual(dst.height, 1080)
        ratio = dst.width / dst.height
        self.assertAlmostEqual(ratio, 1000 / 720, places=2)

    def test_letterbox_centers_in_window(self):
        ui = self.ui
        dst = ui.letterbox_rect((1920, 1080), (1000, 720))
        self.assertEqual(dst.centerx, 960)
        self.assertEqual(dst.centery, 540)

    def test_letterbox_scale_down_small_window(self):
        ui = self.ui
        dst = ui.letterbox_rect((500, 500), (1000, 720))
        self.assertLessEqual(dst.width, 500)
        self.assertLessEqual(dst.height, 500)

    def test_to_virtual_maps_through_scaled_window(self):
        ui = self.ui
        app = self.make_app()
        fake_window = pygame.Surface((1920, 1080))
        with patch.object(ui.pygame.display, "get_surface", return_value=fake_window):
            virtual = app._to_virtual((960, 540))
        # window center maps to canvas center, not to (500, 360) -> (480, 260)-ish
        self.assertAlmostEqual(virtual[0], 500, delta=2)
        self.assertAlmostEqual(virtual[1], 360, delta=2)

    def test_to_virtual_identity_at_reference_size(self):
        ui = self.ui
        app = self.make_app()
        self.assertEqual(app._to_virtual((44, 260)), (44, 260))

    # --- safe area ---

    def test_safe_rect_insets_uniformly(self):
        ui = self.ui
        safe = ui.safe_rect(ui.SCREEN_RECT, ui.SAFE_MARGIN)
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

    # --- focus navigation ---

    def test_menu_initial_focus_is_play(self):
        ui = self.ui
        app = self.make_app()
        self.assertEqual(app.state, ui.ScreenState.MENU)
        self.assertIs(app.focus.current, app.focus.items[0])

    def test_menu_arrow_moves_focus_and_enter_activates(self):
        ui = self.ui
        app = self.make_app()
        app.handle_event(self.key(pygame.K_DOWN))
        self.assertIs(app.focus.current, app.focus.items[1])
        app.handle_event(self.key(pygame.K_RETURN))
        self.assertEqual(app.state, ui.ScreenState.SETTINGS)

    def test_enter_on_focused_play_opens_game(self):
        ui = self.ui
        app = self.make_app()
        app.handle_event(self.key(pygame.K_RETURN))
        self.assertEqual(app.state, ui.ScreenState.GAME)

    def test_mouse_hover_moves_focus(self):
        app = self.make_app()
        app.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {"pos": app.settings_button.center}))
        self.assertIs(app.focus.current, app.focus.items[1])

    def test_settings_arrows_adjust_volume_when_focused(self):
        ui = self.ui
        app = self.make_app()
        app.state = ui.ScreenState.SETTINGS
        initial = app.volume
        app.handle_event(self.key(pygame.K_RIGHT))
        self.assertEqual(app.volume, min(100, initial + 5))
        app.handle_event(self.key(pygame.K_LEFT))
        self.assertEqual(app.volume, initial)

    def test_settings_back_pops_to_previous_screen(self):
        ui = self.ui
        app = self.make_app()
        app.handle_event(self.key(pygame.K_RETURN))  # menu -> game
        app.handle_event(self.key(pygame.K_ESCAPE))  # game -> pause
        app.focus.move("down")  # pause: resume -> settings
        app.focus.move("down")  # pause: settings -> main menu
        app.focus.move("up")  # back to settings
        app.handle_event(self.key(pygame.K_RETURN))  # open settings
        self.assertEqual(app.state, ui.ScreenState.SETTINGS)
        app.handle_event(self.key(pygame.K_ESCAPE))  # pop settings
        # stack returns to the screen settings was pushed from
        self.assertEqual(app.state, ui.ScreenState.PAUSE)

    # --- screen stack ---

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
        app.focus.activate()  # RESUME
        self.assertEqual(app.state, ui.ScreenState.GAME)
        self.assertTrue(app.game.wave_active)

    def test_game_over_enter_restarts(self):
        ui = self.ui
        app = self.make_app()
        app.state = ui.ScreenState.GAME
        app.game.lives = 0
        app.game.update()
        self.assertTrue(app.game.game_over)
        app.handle_event(self.key(pygame.K_RETURN))
        self.assertFalse(app.game.game_over)
        self.assertEqual(app.game.lives, 3)

    # --- event-driven HUD ---

    def test_game_emits_events_on_state_changes(self):
        ui = self.ui
        game = ui.Game()
        self.assertIn("gold_changed", game.drain_events())
        game.start_wave()
        events = game.drain_events()
        self.assertIn("wave_changed", events)

    def test_game_emits_gold_on_kill_and_lives_on_leak(self):
        ui = self.ui
        game = ui.Game()
        game.drain_events()
        enemy = ui.Enemy(50, 1.5, 8)
        enemy.hp = 0
        enemy.alive = False
        game.enemies = [enemy]
        game.update()
        self.assertIn("gold_changed", game.drain_events())
        game.drain_events()
        leaker = ui.Enemy(50, 1.5, 8)
        leaker.reached_end = True
        game.enemies = [leaker]
        game.update()
        self.assertIn("lives_changed", game.drain_events())

    def test_hud_rerenders_only_on_events(self):
        ui = self.ui
        app = self.make_app()
        app.state = ui.ScreenState.GAME
        app.draw()  # first frame: consumes initial events, renders HUD
        wave_before = app.hud.wave_surf
        gold_before = app.hud.gold_surf
        self.assertIsNotNone(wave_before)
        self.assertIsNotNone(gold_before)
        app.hud.handle([], 0, 0, 0)  # no events -> no re-render
        self.assertIs(app.hud.wave_surf, wave_before)
        self.assertIs(app.hud.gold_surf, gold_before)
        app.hud.handle(["wave_changed"], 0, 0, 5)
        self.assertIsNot(app.hud.wave_surf, wave_before)
        self.assertIs(app.hud.gold_surf, gold_before)

    # --- resize / presentation ---

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
