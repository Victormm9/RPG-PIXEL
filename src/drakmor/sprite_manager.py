from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import pygame

from .paths import ASSET_ROOT, SPRITE_SIZE


class SpriteAssetError(RuntimeError):
    """Raised when a sprite file is missing, invalid, or misaligned."""


class EmptySpriteAssetError(SpriteAssetError):
    """Raised when a sprite sheet has no visible pixels."""


class Direction(str, Enum):
    SOUTH = "south"
    NORTH = "north"
    WEST = "west"
    EAST = "east"


DIRECTION_ROWS = {
    Direction.SOUTH: 0,
    Direction.NORTH: 1,
    Direction.WEST: 2,
    Direction.EAST: 3,
}


@dataclass(slots=True)
class SpriteSheet:
    surface: pygame.Surface
    frame_count: int
    source: Path

    @classmethod
    def from_surface(cls, surface: pygame.Surface, source: Path) -> SpriteSheet:
        width, height = surface.get_size()
        if width < SPRITE_SIZE or width % SPRITE_SIZE:
            raise SpriteAssetError(
                f"{source}: a largura deve ser múltipla de {SPRITE_SIZE}px."
            )
        if height != SPRITE_SIZE * len(DIRECTION_ROWS):
            raise SpriteAssetError(
                f"{source}: esperado 4 linhas de {SPRITE_SIZE}px "
                f"(altura total {SPRITE_SIZE * len(DIRECTION_ROWS)}px), recebido {height}px."
            )
        if surface.get_bounding_rect(min_alpha=1).width == 0:
            raise EmptySpriteAssetError(f"{source}: spritesheet totalmente transparente.")
        return cls(surface=surface, frame_count=width // SPRITE_SIZE, source=source)

    def frame(self, direction: Direction, frame_index: int = 0) -> pygame.Surface:
        if frame_index < 0 or frame_index >= self.frame_count:
            raise IndexError(
                f"Quadro {frame_index} fora do intervalo 0..{self.frame_count - 1} "
                f"em {self.source}."
            )
        row = DIRECTION_ROWS[direction]
        frame_rect = pygame.Rect(
            frame_index * SPRITE_SIZE,
            row * SPRITE_SIZE,
            SPRITE_SIZE,
            SPRITE_SIZE,
        )
        return self.surface.subsurface(frame_rect).copy()


class SpriteManager:
    def __init__(self, asset_root: Path = ASSET_ROOT) -> None:
        self.asset_root = asset_root.resolve()
        self._sheets: dict[Path, SpriteSheet] = {}

    def resolve(self, relative_path: str) -> Path:
        path = (self.asset_root / relative_path).resolve()
        try:
            path.relative_to(self.asset_root)
        except ValueError as error:
            raise SpriteAssetError(f"Caminho de sprite fora de assets/: {relative_path}") from error
        return path

    def exists(self, relative_path: str | None) -> bool:
        return relative_path is not None and self.resolve(relative_path).is_file()

    def missing(self, relative_paths: list[str]) -> list[str]:
        missing_paths = []
        for relative_path in dict.fromkeys(relative_paths):
            if not self.exists(relative_path):
                missing_paths.append(f"assets/{relative_path}")
                continue
            try:
                self.load_sheet(relative_path)
            except EmptySpriteAssetError:
                missing_paths.append(f"assets/{relative_path}")
        return missing_paths

    def load_sheet(self, relative_path: str) -> SpriteSheet:
        path = self.resolve(relative_path)
        if not path.is_file():
            raise SpriteAssetError(f"PNG de sprite ausente: assets/{relative_path}")
        if path not in self._sheets:
            try:
                image = pygame.image.load(str(path)).convert_alpha()
            except (OSError, pygame.error) as error:
                raise SpriteAssetError(f"Não foi possível carregar assets/{relative_path}: {error}") from error
            self._sheets[path] = SpriteSheet.from_surface(image, path)
        return self._sheets[path]

    def frame(
        self,
        relative_path: str,
        direction: Direction = Direction.SOUTH,
        frame_index: int = 0,
    ) -> pygame.Surface:
        return self.load_sheet(relative_path).frame(direction, frame_index)

