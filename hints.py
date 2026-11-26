import pygame
from dataclasses import dataclass
from constants import HINT_LINGER
from enum import Enum, auto



class HintState(Enum):
    SHOWING = auto()
    LINGER = auto()
    FADING = auto()

@dataclass(frozen=True)
class Hint:
    text : str                           # the hint that will be displayed
    keys : set                           # set of keys that will trigger the end of a hint
    linger : float = HINT_LINGER         # time the beat will linger after a key trigger
    state : HintState                    # the current state of the hint
    seen : str                           # the key for the seen set





HINTS = {
    "move": Hint("USE (W A S D) keys TO MOVE", keys = {K_w, K_a, K_s, K_d}),
    "panels": Hint("PRESS 1 FOR HARRYS PANEL  2 FOR BARRYS  AND TAB TO CLOSE", keys = {K_1, K_2, K_TAB}),
}
