from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

import gerar_assets


class AssetGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.source = self.root / "source"
        self.destination = self.root / "assets"
        self.source.mkdir()
        self.patches = [
            patch.object(gerar_assets, "SOURCE_DIR", str(self.source)),
            patch.object(gerar_assets, "DEST_DIR", str(self.destination)),
            patch.object(gerar_assets, "criados", []),
            patch.object(gerar_assets, "faltando_fontes", []),
            patch.object(gerar_assets, "erros", []),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)

    def criar_imagem(self, nome, tamanho):
        Image.new("RGBA", tamanho, (255, 0, 0, 255)).save(self.source / nome)

    def test_character_sheet_with_wrong_dimensions_is_not_copied(self):
        self.criar_imagem("boy_light.png", (64, 64))

        resultado = gerar_assets.copiar_arquivo(
            "boy_light.png",
            "characters/base/boy_light.png",
        )

        self.assertFalse(resultado)
        self.assertFalse(
            (self.destination / "characters" / "base" / "boy_light.png").exists()
        )
        self.assertIn("4 linhas de 64 px", gerar_assets.erros[0][1])

    def test_transparent_character_sheet_is_not_copied(self):
        Image.new("RGBA", (256, 256), (0, 0, 0, 0)).save(
            self.source / "boy_light.png"
        )

        resultado = gerar_assets.copiar_arquivo(
            "boy_light.png",
            "characters/base/boy_light.png",
        )

        self.assertFalse(resultado)
        self.assertFalse(
            (self.destination / "characters" / "base" / "boy_light.png").exists()
        )
        self.assertIn("totalmente transparente", gerar_assets.erros[0][1])

    def test_complete_sprite_sheet_is_copied_without_cropping(self):
        self.criar_imagem("slime.png", (448, 256))

        resultado = gerar_assets.copiar_arquivo(
            "slime.png",
            "enemies/slime.png",
            dimensoes_esperadas=(448, 256),
        )

        self.assertTrue(resultado)
        with Image.open(self.destination / "enemies" / "slime.png") as imagem:
            self.assertEqual(imagem.size, (448, 256))

    def test_tileset_and_props_are_both_processed(self):
        self.criar_imagem("eldoria.png", (256, 128))
        self.criar_imagem("props.png", (256, 128))

        gerar_assets.processar_tileset_props_efeitos()

        self.assertTrue((self.destination / "tilesets" / "eldoria.png").is_file())
        self.assertTrue((self.destination / "tilesets" / "props.png").is_file())


if __name__ == "__main__":
    unittest.main()
