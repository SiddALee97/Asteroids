import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COMMS_WIDTH,
    COMMS_HEIGHT, HUD_MARGIN, H_PANEL_WIDTH,
    H_PANEL_HEIGHT, B_PANEL_WIDTH, B_PANEL_HEIGHT,
    PANEL_BOTTOM_GAP
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
    draw_panel(screen, harry_rect)
    draw_panel(screen, barry_rect)

