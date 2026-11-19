from __future__ import annotations

import json
from pathlib import Path

from .models import CharacterChoices
from .paths import DATA_ROOT


def _read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as source:
        document = json.load(source)
    if not isinstance(document, dict):
        raise ValueError(f"O catálogo precisa ser um objeto JSON: {path}")
    return document


def load_classes(path: Path | None = None) -> dict:
    document = _read_json(path or DATA_ROOT / "classes.json")
    classes = document.get("classes")
    if not isinstance(classes, dict) or not classes:
        raise ValueError("data/classes.json precisa definir pelo menos uma classe.")
    for class_id, profile in classes.items():
        for key in ("name", "description", "ability", "stats", "growth", "equipment", "appearance"):
            if key not in profile:
                raise ValueError(f"Campo {key} ausente na classe {class_id}.")
    return classes


def load_character_catalog(path: Path | None = None) -> dict:
    catalog = _read_json(path or DATA_ROOT / "character_catalog.json")
    required = (
        "genders",
        "skin_tones",
        "hair_styles",
        "hair_colors",
        "eye_colors",
        "shirts",
        "armor",
        "pants",
        "boots",
        "cloaks",
        "weapons",
        "accessories",
    )
    for category in required:
        items = catalog.get(category)
        if not isinstance(items, list) or not items:
            raise ValueError(f"Categoria ausente ou vazia no catálogo: {category}")
        if len({item.get("id") for item in items}) != len(items):
            raise ValueError(f"IDs repetidos na categoria: {category}")
    return catalog


def default_character(classes: dict) -> CharacterChoices:
    class_id = next(iter(classes))
    profile = classes[class_id]
    return CharacterChoices(
        class_id=class_id,
        **profile["appearance"],
        **profile["equipment"],
    )


def layer_assets(character: CharacterChoices, catalog: dict) -> dict[str, str | None]:
    gender = _item(catalog, "genders", character.gender_id)
    skin = _item(catalog, "skin_tones", character.skin_tone_id)
    hair_style = _item(catalog, "hair_styles", character.hair_style_id)
    hair_color = _item(catalog, "hair_colors", character.hair_color_id)
    eyes = _item(catalog, "eye_colors", character.eye_color_id)

    def path_for(category: str, item_id: str) -> str | None:
        return _item(catalog, category, item_id).get("asset")

    return {
        "cloak": path_for("cloaks", character.cloak_id),
        "body": gender["asset"].format(
            gender=character.gender_id,
            skin=character.skin_tone_id,
        ),
        "pants": path_for("pants", character.pants_id),
        "boots": path_for("boots", character.boots_id),
        "shirt": path_for("shirts", character.shirt_id),
        "armor": path_for("armor", character.armor_id),
        "face": skin["asset"],
        "eyes": eyes["asset"],
        "hair": hair_style["asset"].format(
            style=character.hair_style_id,
            color=character.hair_color_id,
        ),
        "weapon": path_for("weapons", character.weapon_id),
        "accessory": path_for("accessories", character.accessory_id),
    }


def item_for_character(character: CharacterChoices, catalog: dict, category: str) -> dict:
    field_name = {
        "genders": "gender_id",
        "skin_tones": "skin_tone_id",
        "hair_styles": "hair_style_id",
        "hair_colors": "hair_color_id",
        "eye_colors": "eye_color_id",
        "shirts": "shirt_id",
        "armor": "armor_id",
        "pants": "pants_id",
        "boots": "boots_id",
        "cloaks": "cloak_id",
        "weapons": "weapon_id",
        "accessories": "accessory_id",
    }[category]
    return _item(catalog, category, getattr(character, field_name))


def _item(catalog: dict, category: str, item_id: str) -> dict:
    for item in catalog[category]:
        if item["id"] == item_id:
            return item
    raise ValueError(f"Opção '{item_id}' não existe na categoria '{category}'.")

