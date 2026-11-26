import pygame
from dataclasses import dataclass
from constants import HINT_LINGER, SCREEN_WIDTH, HINT_FADE, HINT_Y
from enum import Enum, auto



class HintState(Enum):
    SHOWING = auto()
    LINGER = auto()
    FADING = auto()

@dataclass(frozen=True)
class Hint:
    text : str                           # the hint that will be displayed
    keys : frozenset | None = None       # set of keys that will trigger the end of a hint
    buttons : frozenset | None = None    # set of mouse clicks that will trigger end


HINTS = {
    "move": Hint("USE (W A S D) keys TO MOVE",
                keys = frozenset({pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d})),
    "panels": Hint("PRESS 1 FOR HARRYS PANEL  2 FOR BARRYS  AND TAB TO CLOSE",
                keys = frozenset({pygame.K_1, pygame.K_2, pygame.K_TAB})),
    "dash": Hint("PRESS SHIFT TO DASH",
                keys = frozenset({pygame.K_LSHIFT})),
    "laser": Hint("USE MOUSE TO AIM AND LEFT CLICK TO FIRE LASER",
                buttons = frozenset({1}))
}

class HintManager:
    def __init__(self):
        self.queue = []                     # hint keys waiting
        self.current = None
        self.current_key = None
        self.pressed = False                # player has pressed a key
        self.timer = 0.0                    # starts whe self pressed
        self.seen = set()
        self.font = None

    def show(self, key):
        if key in self.seen or key not in HINTS or key in self.queue or key == self.current_key:
            return
        self.queue.append(key)
        if self.current is None:
            self.next()

    def next(self):
        if not self.queue:
            self.current = None
            self.current_key = None
            return
        self.current_key = self.queue.pop()
        self.current = HINTS[self.current_key]
        self.seen.add(self.current_key)
        self.pressed = False
        self.timer = 0.0

    def mouse_clicked(self, button):
        if self.current and not self.pressed and self.current.buttons and button in self.current.buttons:
            self.pressed = True

    def key_pressed(self, key):
        if self.current and not self.pressed and self.current.keys and key in self.current.keys:
            self.pressed = True

    def update(self, dt):
        if self.current is None or not self.pressed:
            return
        self.timer += dt
        if self.timer >= HINT_LINGER + HINT_FADE:
            self.next()

    def reset(self):
        self.queue.clear()
        self.current = None
        self.current_key = None
        self.pressed = False
        self.timer = 0.0

    def draw(self, screen):
        if self.current is None:
            return
        if self.font is None:
            self.font = pygame.font.Font("assets/fonts/upheavtt.ttf", 22)

        alpha = 1.0
        if self.timer > HINT_LINGER:
            alpha = 1.0 - (self.timer - HINT_LINGER) / HINT_FADE
        alpha = max(0.0, min(1.0, alpha))

        text = self.font.render(self.current.text, True, (255, 220, 120))
        pad = 10
        box = pygame.Surface((text.get_width() + pad * 2, text.get_height() + pad * 2), pygame.SRCALPHA)
        box.fill((0, 0, 0, 150))
        box.blit(text, (pad, pad))
        box.set_alpha(int(255 * alpha))
        screen.blit(box, box.get_rect(midtop=(SCREEN_WIDTH // 2, HINT_Y)))