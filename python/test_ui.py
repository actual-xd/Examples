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
        cls.screen = pygame.Surface((800, 600))

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
