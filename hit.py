import pygame
from enum import Enum, auto
from dataclasses import dataclass


class HitKind(Enum):
    LASER = auto()
    BLAST = auto()

@dataclass(frozen = True)
class Hit():
    kind: HitKind
    damage: float
    force: float
    direction: pygame.Vector2 | None = None
    origin: pygame.Vector2 | None = None
