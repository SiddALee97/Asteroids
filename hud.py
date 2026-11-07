from enum import Enum, auto

import pygame
from constants import (
    PANEL_CLOSE_TIME, SCREEN_WIDTH, SCREEN_HEIGHT, COMMS_WIDTH,
    COMMS_HEIGHT, HUD_MARGIN, H_PANEL_WIDTH,
    H_PANEL_HEIGHT, B_PANEL_WIDTH, B_PANEL_HEIGHT,
    PANEL_BOTTOM_GAP, PANEL_SLIDE_TIME, PANEL_BOOT_TIME,
    H_SLOT_RECTS, B_SLOT_RECTS, H_LIGHT_RECTS, B_LIGHT_RECTS,
    H_SCREEN_RECT, B_SCREEN_RECT
)
from ships import HARRY_SLOTS, BARRY_SLOTS

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
    PanelState.OPENING: PanelState.BOOTING,
    PanelState.BOOTING: PanelState.OPEN,
    PanelState.CLOSING: PanelState.CLOSED,
}


class Panel:
    def __init__(self, rect, side, slots, slot_rects, lights, screen_rect,):
        self.side = side
        self.rect = rect
        self.state = PanelState.CLOSED
        self.timer = 0.0
        self.drawn_rect = None
        self.image = None
        self.slots = slots
        self.selected = 0
        self.slot_rects = slot_rects
        self.font = None
        self.light_rects = lights
        self.screen_rect = screen_rect

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
        self.drawn_rect = r

        if self.image is None:
            draw_panel(screen, r)
            return
        screen.blit(self.image, r.topleft)

        if self.state == PanelState.OPEN:
            for slot in self.slot_rects:
                rect = pygame.Rect(slot)
                pygame.draw.rect(screen, "red", rect.move(r.topleft), 1)
            for light in self.light_rects:
                rect = pygame.Rect(light)
                pygame.draw.rect(screen, "yellow", rect.move(r.topleft), 1)
            panel_screen = pygame.Rect(self.screen_rect)   
            pygame.draw.rect(screen, "green", panel_screen.move(r.topleft), 1)
            pygame.draw.rect(screen, (24, 16, 6), panel_screen.move(r.topleft))  # Draw the background
            pygame.draw.rect(screen, (120, 125, 135), panel_screen.move(r.topleft), 2)  # Draw the outline


    def set_image(self, image):
        self.image = pygame.transform.scale(
            image, (image.get_width() * 2, image.get_height() * 2)
        )
        


harry_panel = Panel(harry_rect, -1, HARRY_SLOTS, H_SLOT_RECTS, H_LIGHT_RECTS, H_SCREEN_RECT)
barry_panel = Panel(barry_rect, 1, BARRY_SLOTS, B_SLOT_RECTS, B_LIGHT_RECTS, B_SCREEN_RECT)
            