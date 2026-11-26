from dataclasses import dataclass
import pygame
from speech import Bubble
from hud import open_panel_for
from constants import BEAT_DIM


@dataclass(frozen=True)
class Beat:
    speaker : str                   # harry barry or a cutscene etc.
    text : str                      
    open_panel : bool = False       # tutorial will change it to slide out
    highlight : tuple | None = None # tutorial: rect to point at
    zoom : float | None = None      # camera zoom mult on ship         
    dim : float = BEAT_DIM          # overlay dim strength
    key : str | None = None         # for the seen set (None is always plays)
    wait_for : str | None = None    # a slot key for when to advance for interactive beats


class Sequence:
    def __init__(self, camera):
        self.queue = []         # beats waiting
        self.current = None     # the beat on screen
        self.seen = set()
        self.bubble = None
        self.dim_alpha = 0.0
        self.dim_target = 0.0
        self.camera = camera
        self.player = None

    @property
    def active(self):
        return self.current is not None

    def start(self, beats, player = None):
        if player is not None:
            self.player = player
        for beat in beats:
            if beat.key is None or beat.key not in self.seen:
                self.queue.append(beat)
        if self.current is None:
            self.next()

    def next(self):
        if self.current is not None and self.current.key is not None:
            self.seen.add(self.current.key)
        if not self.queue:
            self.end()
            return
        self.current = self.queue.pop(0)
        self.dim_target = self.current.dim
        if self.current.zoom is not None and self.player is not None:
            self.camera.focus(self.player.position, self.current.zoom)
        side = 1 if self.current.speaker == "harry" else -1
        self.bubble = Bubble(self.current.text, side)
        open_panel_for(self.current.speaker)

    def end(self):
        self.current = None
        self.bubble = None
        self.dim_target = 0.0
        self.camera.fit_world()

    def advance(self):
        if self.current is None or self.current.wait_for is not None:
            return
        if self.bubble.chars < len(self.current.text):
            self.bubble.chars = len(self.current.text)      # first call finishes the text
        elif self.current.wait_for is None:                 # only non interactive beats advance
            self.next()

    def notify(self, slot_key):
        # called in main.py when player buys something
        if self.current and self.current.wait_for in (slot_key, "any"):
            self.next()

    def skip(self):
        for beat in self.queue + ([self.current] if self.current else []):
            if beat.key is not None:
                self.seen.add(beat.key)
        self.queue.clear()
        self.end()


    def update(self, dt):
        self.dim_alpha += (self.dim_target - self.dim_alpha) * min(1.0, dt * 8)
        if self.bubble:
            self.bubble.update(dt)

    def draw_dim(self, screen, dim_surface):
        if self.dim_alpha > 1:
            dim_surface.fill((0, 0, 0, int(self.dim_alpha)))
            screen.blit(dim_surface, (0, 0))

    