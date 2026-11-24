import pygame
import math
from constants import TUTORIAL_TEXT_SPEED

BUBBLE_MAX_WIDTH = 220
BUBBLE_PAD = 10
BUBBLE_POP_TIME = 0.25


def wrap_text(text, font, width):
    lines, current = [], ""
    for word in text.split(" "):
        test = current + word + " "
        if font.size(test)[0] <= width:
            current = test
        else:
            lines.append(current.strip())
            current = word + " "
    lines.append(current.strip())
    return lines


class Bubble:
    def __init__(self, text, side):
        self.text = text
        self.side = side          # +1 for Harry (left panel), -1 for Barry (right panel)
        self.chars = 0.0
        self.age = 0.0
        self.font = None

    def update(self, dt):
        self.age += dt
        if self.age >= BUBBLE_POP_TIME and self.chars < len(self.text):
            self.chars += TUTORIAL_TEXT_SPEED * dt

    def draw(self, screen, anchor, panel_rect):
        if self.font is None:
            self.font = pygame.font.Font("assets/fonts/upheavtt.ttf", 18)

        # size from the FULL text so the box doesn't grow while typing
        lines = wrap_text(self.text, self.font, BUBBLE_MAX_WIDTH - 2 * BUBBLE_PAD)
        line_h = self.font.get_linesize()
        w = BUBBLE_MAX_WIDTH
        h = len(lines) * line_h + 2 * BUBBLE_PAD

        # pop-in: scale 0 -> 1, hold text until fully popped
        pop = min(1.0, self.age / BUBBLE_POP_TIME)
        bob = math.sin(self.age * 1.5) * 4

        base = pygame.Rect(0, 0, w, h)
        base.midbottom = (anchor[0] + self.side * 70, anchor[1] - 30 + bob)
        gap = 12
        if self.side == 1:      # Harrys side
            base.midleft = (panel_rect.right + gap, anchor[1] + bob - 100)
        else:                   # Barrys side
            base.midright = (panel_rect.left - gap, anchor[1] + bob - 150)
        base.clamp_ip(screen.get_rect())

        rect = pygame.Rect(0, 0, int(w * pop), int(h * pop))
        rect.center = base.center
        if rect.width < 2 or rect.height < 2:
            return

        # tail from the box toward the speaker
        tail = [(rect.centerx - 8, rect.bottom), (rect.centerx + 8, rect.bottom), anchor]
        pygame.draw.polygon(screen, (230, 215, 170), tail)
        pygame.draw.rect(screen, (230, 215, 170), rect, border_radius=6)
        pygame.draw.rect(screen, (60, 45, 30), rect, 2, border_radius=6)

        if pop < 1.0:
            return

        remaining = int(self.chars)
        y = rect.y + BUBBLE_PAD
        for line in lines:
            if remaining <= 0:
                break
            surf = self.font.render(line[:remaining], True, (60, 45, 30))
            screen.blit(surf, (rect.x + BUBBLE_PAD, y))
            remaining -= len(line)
            y += line_h