import pygame
from enum import Enum, auto
from dataclasses import dataclass, field

class HitOutcome(Enum):
    NOTHING = auto()    # hit doesn't register
    CHIPPED = auto()    # main cannon did a little damage
    SHRUNK = auto()     # laser reduced the asteroid
    DESTROYED = auto()  # object removed (with or without fragmentation)

class HitKind(Enum):
    LASER = auto()
    BLAST = auto()
    SHOT = auto()

@dataclass(frozen = True)
class HitResult():
    outcome: HitOutcome
    points: int = 0
    spawned: list = field(default_factory = list)  # list of spawned asteroids

@dataclass(frozen = True)
class Hit():
    kind: HitKind
    damage: float
    force: float      # push force
    breakage: int     # how many tiers of breakage
    direction: pygame.Vector2 | None = None
    origin: pygame.Vector2 | None = None
