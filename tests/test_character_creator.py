import json
from pathlib import Path
import tempfile
import unittest

from src.drakmor.catalog import default_character, load_character_catalog, load_classes
from src.drakmor.creator import CharacterCreator
from src.drakmor.models import (
    CharacterChoices,
    load_character,
    save_character,
    validate_character,
)
from src.drakmor.sprite_manager import SpriteManager


class CharacterCreatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.classes = load_classes()
        cls.catalog = load_character_catalog()

    def test_all_six_classes_have_valid_starters_and_class_specific_equipment(self):
        self.assertEqual(
            set(self.classes),
            {"warrior", "mage", "archer", "rogue", "paladin", "druid"},
        )
        creator = CharacterCreator(
            self.classes,
            self.catalog,
            default_character(self.classes),
        )
        starting_weapons = set()
        for class_id, profile in self.classes.items():
            creator.select_class(class_id)
            creator.character.class_id = class_id
            validate_character(creator.character, self.classes, self.catalog)
            self.assertEqual(creator.character.weapon_id, profile["equipment"]["weapon_id"])
            self.assertEqual(creator.character.armor_id, profile["equipment"]["armor_id"])
            starting_weapons.add(creator.character.weapon_id)
        self.assertEqual(len(starting_weapons), 6)

    def test_appearance_options_cycle_and_randomize(self):
        creator = CharacterCreator(
            self.classes,
            self.catalog,
            default_character(self.classes),
        )
        original_gender = creator.character.gender_id
        creator.cycle("genders", 1)
        self.assertNotEqual(creator.character.gender_id, original_gender)
        creator.randomize()
        self.assertIn(creator.character.class_id, self.classes)
        self.assertIn(creator.character.hair_style_id, {item["id"] for item in self.catalog["hair_styles"]})
        self.assertIn(creator.character.eye_color_id, {item["id"] for item in self.catalog["eye_colors"]})

    def test_save_and_load_round_trip_json(self):
        character = default_character(self.classes)
        character.name = "Lina"
        character.gender_id = "girl"
        character.eye_color_id = "green"
        character.class_id = "druid"
        character = CharacterChoices(
            **{
                **character.to_dict(),
                **self.classes["druid"]["equipment"],
                **self.classes["druid"]["appearance"],
            }
        )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "player.json"
            save_character(path, character, self.classes, self.catalog)
            loaded = load_character(path, self.classes, self.catalog)

        self.assertEqual(loaded, character)

    def test_invalid_saved_selection_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "player.json"
            path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "character": {"class_id": "unknown"},
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_character(path, self.classes, self.catalog)

    def test_missing_assets_are_listed_by_exact_path(self):
        character = default_character(self.classes)
        creator = CharacterCreator(self.classes, self.catalog, character)
        with tempfile.TemporaryDirectory() as directory:
            missing = creator.missing_assets(SpriteManager(Path(directory)))
        self.assertIn("assets/characters/base/boy_light.png", missing)
        self.assertIn("assets/characters/weapons/steel_sword.png", missing)
        self.assertEqual(len(missing), len(set(missing)))


if __name__ == "__main__":
    unittest.main()
