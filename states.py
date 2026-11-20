from enum import Enum, auto


class GameState(Enum):
    TITLE = auto()
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    SETTINGS = auto()
    TUTORIAL = auto()
    