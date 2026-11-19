from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json


SAVE_VERSION = 1


@dataclass(slots=True)
class CharacterChoices:
    name: str = "Aventureiro"
    gender_id: str = "boy"
    class_id: str = "warrior"
    skin_tone_id: str = "light"
    hair_style_id: str = "short"
    hair_color_id: str = "brown"
    eye_color_id: str = "brown"
    shirt_id: str = "shirt_crimson"
    armor_id: str = "armor_chainmail"
    pants_id: str = "pants_charcoal"
    boots_id: str = "boots_leather"
    cloak_id: str = "none"
    weapon_id: str = "weapon_steel_sword"
    accessory_id: str = "accessory_iron_shield"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def validate_character(
    character: CharacterChoices,
    classes: dict,
    catalog: dict,
) -> None:
    if any(not isinstance(value, str) for value in character.to_dict().values()):
        raise ValueError("Todos os campos do personagem precisam ser texto.")
    if not character.name.strip():
        raise ValueError("O personagem precisa ter um nome.")
    if len(character.name) > 24:
        raise ValueError("O nome do personagem pode ter no máximo 24 caracteres.")
    if character.class_id not in classes:
        raise ValueError(f"Classe desconhecida: {character.class_id}")

    valid_ids = {
        "gender_id": "genders",
        "skin_tone_id": "skin_tones",
        "hair_style_id": "hair_styles",
        "hair_color_id": "hair_colors",
        "eye_color_id": "eye_colors",
        "shirt_id": "shirts",
        "armor_id": "armor",
        "pants_id": "pants",
        "boots_id": "boots",
        "cloak_id": "cloaks",
        "weapon_id": "weapons",
        "accessory_id": "accessories",
    }
    for field_name, catalog_key in valid_ids.items():
        available = {item["id"] for item in catalog[catalog_key]}
        value = getattr(character, field_name)
        if value not in available:
            raise ValueError(f"Opção inválida para {field_name}: {value}")


def save_character(
    path: Path,
    character: CharacterChoices,
    classes: dict,
    catalog: dict,
) -> None:
    validate_character(character, classes, catalog)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    try:
        with temporary_path.open("w", encoding="utf-8", newline="\n") as save_file:
            json.dump(
                {"version": SAVE_VERSION, "character": character.to_dict()},
                save_file,
                ensure_ascii=False,
                indent=2,
            )
            save_file.write("\n")
        temporary_path.replace(path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def load_character(path: Path, classes: dict, catalog: dict) -> CharacterChoices:
    with path.open("r", encoding="utf-8") as save_file:
        document = json.load(save_file)
    if not isinstance(document, dict) or document.get("version") != SAVE_VERSION:
        raise ValueError("O arquivo de personagem tem uma versão inválida.")
    values = document.get("character")
    if not isinstance(values, dict):
        raise ValueError("O arquivo não contém os dados de um personagem.")

    valid_fields = set(CharacterChoices.__dataclass_fields__)
    character = CharacterChoices(
        **{key: value for key, value in values.items() if key in valid_fields}
    )
    validate_character(character, classes, catalog)
    return character

