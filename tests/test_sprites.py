import os
from pathlib import Path
import tempfile
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.drakmor.compositor import compose_character
from src.drakmor.sprite_manager import (
    DIRECTION_ROWS,
    Direction,
    SpriteAssetError,
    SpriteManager,
    SpriteSheet,
)


class SpriteSheetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1, 1))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_reads_four_directions_and_animation_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            image = pygame.Surface((128, 256), pygame.SRCALPHA, 32)
            expected = {
                Direction.SOUTH: (255, 0, 0, 255),
                Direction.NORTH: (0, 255, 0, 255),
                Direction.WEST: (0, 0, 255, 255),
                Direction.EAST: (255, 255, 0, 255),
            }
            for direction, row in DIRECTION_ROWS.items():
                image.fill(expected[direction], pygame.Rect(64, row * 64, 64, 64))
            image_path = root / "directions.png"
            pygame.image.save(image, image_path)

            manager = SpriteManager(root)
            for direction, color in expected.items():
                frame = manager.frame("directions.png", direction, 1)
                self.assertEqual(frame.get_size(), (64, 64))
                self.assertEqual(frame.get_at((8, 8)), color)

    def test_requires_four_rows_of_64_pixel_cells(self):
        surface = pygame.Surface((64, 192), pygame.SRCALPHA, 32)
        with self.assertRaisesRegex(SpriteAssetError, "4 linhas"):
            SpriteSheet.from_surface(surface, Path("bad.png"))

    def test_missing_file_is_reported_instead_of_substituted(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = SpriteManager(Path(directory))
            with self.assertRaisesRegex(SpriteAssetError, "PNG de sprite ausente"):
                manager.load_sheet("characters/base/boy_light.png")

    def test_layer_composition_preserves_transparency_and_order(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = pygame.Surface((64, 256), pygame.SRCALPHA, 32)
            base.fill((20, 40, 120, 255))
            hair = pygame.Surface((64, 256), pygame.SRCALPHA, 32)
            hair.fill((190, 30, 40, 255), pygame.Rect(0, 0, 64, 32))
            pygame.image.save(base, root / "body.png")
            pygame.image.save(hair, root / "hair.png")

            result = compose_character(
                SpriteManager(root),
                {"body": "body.png", "hair": "hair.png"},
                Direction.SOUTH,
            )

            self.assertEqual(result.get_at((5, 5)), (190, 30, 40, 255))
            self.assertEqual(result.get_at((5, 40)), (20, 40, 120, 255))

    def test_layers_must_have_matching_animation_frame_count(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            pygame.image.save(
                pygame.Surface((64, 256), pygame.SRCALPHA, 32),
                root / "body.png",
            )
            pygame.image.save(
                pygame.Surface((128, 256), pygame.SRCALPHA, 32),
                root / "hair.png",
            )
            with self.assertRaisesRegex(SpriteAssetError, "mesmo alinhamento"):
                compose_character(
                    SpriteManager(root),
                    {"body": "body.png", "hair": "hair.png"},
                )

    def test_asset_paths_cannot_escape_the_asset_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            manager = SpriteManager(Path(directory) / "assets")
            with self.assertRaisesRegex(SpriteAssetError, "fora de assets"):
                manager.resolve("../outside.png")


if __name__ == "__main__":
    unittest.main()
