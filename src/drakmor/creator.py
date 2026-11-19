from __future__ import annotations

import random

from .catalog import layer_assets
from .models import CharacterChoices
from .sprite_manager import SpriteManager


CATEGORY_SPECS = (
    ("Gênero", "genders", "gender_id"),
    ("Tom de pele", "skin_tones", "skin_tone_id"),
    ("Modelo de cabelo", "hair_styles", "hair_style_id"),
    ("Cor do cabelo", "hair_colors", "hair_color_id"),
    ("Cor dos olhos", "eye_colors", "eye_color_id"),
    ("Camisa", "shirts", "shirt_id"),
    ("Calças", "pants", "pants_id"),
    ("Botas e sapatos", "boots", "boots_id"),
    ("Armadura", "armor", "armor_id"),
    ("Capa", "cloaks", "cloak_id"),
    ("Arma", "weapons", "weapon_id"),
    ("Acessório", "accessories", "accessory_id"),
)


class CharacterCreator:
    def __init__(self, classes: dict, catalog: dict, character: CharacterChoices) -> None:
        self.classes = classes
        self.catalog = catalog
        self.character = character

    def select_class(self, class_id: str) -> None:
        if class_id not in self.classes:
            raise ValueError(f"Classe desconhecida: {class_id}")
        profile = self.classes[class_id]
        self.character.class_id = class_id
        for field_name, value in profile["appearance"].items():
            setattr(self.character, field_name, value)
        for field_name, value in profile["equipment"].items():
            setattr(self.character, field_name, value)

    def cycle(self, category: str, step: int) -> None:
        for _, catalog_key, field_name in CATEGORY_SPECS:
            if catalog_key == category:
                options = self.catalog[catalog_key]
                current = getattr(self.character, field_name)
                index = next(
                    (position for position, item in enumerate(options) if item["id"] == current),
                    None,
                )
                if index is None:
                    raise ValueError(f"Opção atual não existe em {category}: {current}")
                setattr(self.character, field_name, options[(index + step) % len(options)]["id"])
                return
        raise ValueError(f"Categoria desconhecida: {category}")

    def randomize(self, rng: random.Random | None = None) -> None:
        chooser = rng or random
        self.select_class(chooser.choice(tuple(self.classes)))
        for _, category, field_name in CATEGORY_SPECS:
            choices = self.catalog[category]
            setattr(self.character, field_name, chooser.choice(choices)["id"])

    def layer_assets(self) -> dict[str, str | None]:
        return layer_assets(self.character, self.catalog)

    def missing_assets(self, sprites: SpriteManager) -> list[str]:
        selected_paths = [
            path for path in self.layer_assets().values() if path is not None
        ]
        return sprites.missing(selected_paths)

