import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.drakmor.app import DrakmorApp
from src.drakmor.paths import SAVE_PATH


class CharacterCreatorUITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280, 800))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_creator_renders_without_sprite_substitutes_and_lists_missing_files(self):
        app = DrakmorApp()
        app.state = "creator"
        app.draw()
        self.assertTrue(app.creator.missing_assets(app.sprites))
        self.assertEqual(app.screen.get_size(), (1280, 800))

    def test_confirm_button_saves_character_to_json(self):
        app = DrakmorApp()
        app._new_character()
        app.character.name = "Teste"
        with tempfile.TemporaryDirectory() as directory:
            save_path = Path(directory) / "player.json"
            with patch("src.drakmor.app.SAVE_PATH", save_path):
                confirm = app._creator_layout()["buttons"]["confirm"]
                app._handle_creator_click(confirm.center)
                self.assertTrue(save_path.is_file())
                self.assertEqual(app.state, "menu")
        self.assertIn("personagem salvo", app.status_message.lower())

    def test_class_and_appearance_controls_update_the_draft(self):
        app = DrakmorApp()
        app._new_character()

        mage_card = app._creator_layout()["classes"]["mage"]
        app._handle_creator_click(mage_card.center)
        self.assertEqual(app.character.class_id, "mage")
        self.assertEqual(app.character.weapon_id, "weapon_arcane_staff")

        gender_card = next(
            rects
            for _, category, rects in app._creator_layout()["categories"]
            if category == "genders"
        )
        app._handle_creator_click(gender_card[1].center)
        self.assertEqual(app.character.gender_id, "girl")

    def test_name_field_accepts_text_input(self):
        app = DrakmorApp()
        app._new_character()
        app.character.name = ""
        app._handle_creator_click(app._creator_layout()["name"].center)
        app.handle_event(pygame.event.Event(pygame.TEXTINPUT, text="Ayla"))
        self.assertEqual(app.character.name, "Ayla")
        self.assertTrue(app.name_focused)


if __name__ == "__main__":
    unittest.main()
