from enum import Enum, auto

import pygame
from constants import (
    PANEL_CLOSE_TIME, SCREEN_WIDTH, SCREEN_HEIGHT, COMMS_WIDTH,
    COMMS_HEIGHT, HUD_MARGIN, H_PANEL_WIDTH,
    H_PANEL_HEIGHT, B_PANEL_WIDTH, B_PANEL_HEIGHT,
    PANEL_BOTTOM_GAP, PANEL_SLIDE_TIME, PANEL_BOOT_TIME,
)


comms_rect = pygame.Rect(
    (SCREEN_WIDTH - COMMS_WIDTH) // 2,
    SCREEN_HEIGHT - HUD_MARGIN - COMMS_HEIGHT,
    COMMS_WIDTH,
    COMMS_HEIGHT,
)


harry_rect = pygame.Rect(
    HUD_MARGIN,
    SCREEN_HEIGHT - PANEL_BOTTOM_GAP - H_PANEL_HEIGHT,
    H_PANEL_WIDTH,
    H_PANEL_HEIGHT,
)


barry_rect = pygame.Rect(
    SCREEN_WIDTH - HUD_MARGIN - B_PANEL_WIDTH,
    SCREEN_HEIGHT - PANEL_BOTTOM_GAP - B_PANEL_HEIGHT,
    B_PANEL_WIDTH,
    B_PANEL_HEIGHT,
)


def draw_panel(screen, rect):
    pygame.draw.rect(screen, (42, 45, 51), rect)        # fill color first
    pygame.draw.rect(screen, (120, 125, 135), rect, 2)  # then the outline


def draw_hud(screen):
    draw_panel(screen, comms_rect)


class PanelState(Enum):
    CLOSED = auto()
    OPENING = auto()
    BOOTING = auto()
    OPEN = auto()
    CLOSING = auto()

PANEL_DURATION = {
    PanelState.OPENING: PANEL_SLIDE_TIME,
    PanelState.BOOTING: PANEL_BOOT_TIME,
    PanelState.CLOSING: PANEL_CLOSE_TIME,
}

PANEL_NEXT = {
    PanelState.CLOSED: PanelState.OPENING,
    PanelState.OPENING: PanelState.BOOTING,
    PanelState.BOOTING: PanelState.OPEN,
     PanelState.OPEN: PanelState.CLOSING,
    PanelState.CLOSING: PanelState.CLOSED,
}


class Panel:
    def __init__(self, rect, side):
        self.side = side
        self.rect = rect
        self.state = PanelState.CLOSED
        self.timer = 0.0

    def set_state(self, state):
        self.state = state
        self.timer = 0.0
    

    def toggle(self):
        if self.state is PanelState.CLOSED:
            self.set_state(PanelState.OPENING)
        elif self.state in (PanelState.OPEN, PanelState.BOOTING): 
            self.set_state(PanelState.CLOSING)

    def update(self, dt):
        if self.state not in PANEL_DURATION:
            return
        self.timer += dt
        if self.timer >= PANEL_DURATION[self.state]:
            self.set_state(PANEL_NEXT[self.state])

    def reset(self):
        self.set_state(PanelState.CLOSED)


    def draw(self, screen):
        if self.state is PanelState.CLOSED:
            return
        if self.state is PanelState.OPENING:
            progress = self.timer / PANEL_SLIDE_TIME
        elif self.state is PanelState.BOOTING:
            progress = 1.0
        elif self.state is PanelState.CLOSING:
            progress = 1.0 - (self.timer / PANEL_CLOSE_TIME)
        else:
            progress = 1.0
        progress = max(0.0, min(1.0, progress))

        r = self.rect.move(self.side * (1.0 - progress) * (self.rect.width + HUD_MARGIN), 0)

        


        draw_panel(screen, r)


harry_panel = Panel(harry_rect, -1)
barry_panel = Panel(barry_rect, 1)
            