from __future__ import annotations

import pygame

from .paths import SPRITE_SIZE
from .sprite_manager import Direction, SpriteAssetError, SpriteManager


LAYER_ORDER = (
    "cloak",
    "body",
    "pants",
    "boots",
    "shirt",
    "armor",
    "face",
    "eyes",
    "hair",
    "weapon",
    "accessory",
)


def compose_character(
    manager: SpriteManager,
    layers: dict[str, str | None],
    direction: Direction = Direction.SOUTH,
    frame_index: int = 0,
) -> pygame.Surface:
    unknown_layers = set(layers) - set(LAYER_ORDER)
    if unknown_layers:
        raise ValueError(f"Camadas desconhecidas: {', '.join(sorted(unknown_layers))}")
    if not layers.get("body"):
        raise ValueError("A camada base do corpo é obrigatória.")

    selected = [(name, layers[name]) for name in LAYER_ORDER if layers.get(name)]
    base_sheet = manager.load_sheet(layers["body"])
    output = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA, 32)
    for layer_name, asset_path in selected:
        sheet = manager.load_sheet(asset_path)
        if sheet.frame_count != base_sheet.frame_count:
            raise SpriteAssetError(
                f"A camada '{layer_name}' tem {sheet.frame_count} quadros, "
                f"mas a base tem {base_sheet.frame_count}; todas as camadas "
                "precisam usar o mesmo alinhamento."
            )
        output.blit(sheet.frame(direction, frame_index), (0, 0))
    return output

