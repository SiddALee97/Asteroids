import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


scale = 1.0
offset = (0, 0)


def present(game_surface):
    """Scale the game surface into the window, keeping 16:9 with black bars if needed."""
    global scale, offset
    window = pygame.display.get_surface()
    ww, wh = window.get_size()
    scale = min(ww / SCREEN_WIDTH, wh / SCREEN_HEIGHT)
    w, h = int(SCREEN_WIDTH * scale), int(SCREEN_HEIGHT * scale)
    if w < 1 or h < 1:      # minimized
        return
    offset = ((ww - w) // 2, (wh - h) // 2)
    window.fill("black")
    window.blit(pygame.transform.smoothscale(game_surface, (w, h)), offset)

def to_game(pos):
    """Window pixel -> game pixel."""
    return ((pos[0] - offset[0]) / scale, (pos[1] - offset[1]) / scale)

def mouse_pos():
    return to_game(pygame.mouse.get_pos())
