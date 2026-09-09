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


if __name__ == "__main__":
    unittest.main()
