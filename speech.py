import pygame
import math
from constants import TUTORIAL_TEXT_SPEED, H_SPEAKER_POS, B_SPEAKER_POS

class Bubble():
    def __init__(self, text):
        self.text = text
        self.chars: 0.0
        self.age = 0.0
        self.font = None
        self.seen = set()

    def update(self, dt):
        self.age += dt
        # type and hold once finished    
        if self.chars < len(self.text):
            self.chars += TUTORIAL_TEXT_SPEED * dt  # Adjust the speed of character display here

    def wrap_text(self, text, font, width):
        # Wrap text to fit within a given width
        lines = []
        words = text.split(' ')
        current_line = ""

        for word in words:
            text_line = current_line + word + " "
            if font.size(text_line)[0] <= width:
                current_line = text_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        lines.append(current_line.strip())
        return lines

    def draw(self, screen, anchor):
        self.font = pygame.font.Font("assets/fonts/upheavtt.ttf", 18)
        y += math.sin(self.age * 1.5) * 4
        bubble_rect = pygame.Rect(anchor[0] + 50, anchor[1] + 50 + y, 236, 178)
        lines = self.wrap_text(self.text, self.font, bubble_rect.width - 10)
        remaining = int(self.chars)
        for line in lines:
            if remaining <= 0:
                break
            surf = self.font.render(line[:remaining], True, (115, 90, 70))
            screen.blit(surf, (bubble_rect.x + 8, y))
            remaining -= len(line)
            y += self.font.get_linesize()