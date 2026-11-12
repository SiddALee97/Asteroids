import pygame

class Slider:
    def __init__(self, x, y, width, label, value = 0.5):
        self.rect = pygame.Rect(x, y, width, 12)   # the track for the slider
        self.label = label
        self.value = value
        self.dragging = False
        self.font = None

    def _set_from_mouse(self, mouse_x):
        v = (mouse_x - self.rect.x) / self.rect.width
        self.value = max(0.0, min(1.0, v))  # clamped between 0 and 1

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # slightly taller hit box so its easier to grab
            if self.rect.inflate(0, 24).collidepoint(event.pos):
                self.dragging = True
                self._set_from_mouse(event.pos[0])
                return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_from_mouse(event.pos[0])
            return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        return False

    def draw(self, screen):
        if self.font is None:
            self.font = pygame.font.Font(None, 28)

        # track, fill, and border
        pygame.draw.rect(screen, (40, 28, 10), self.rect)           # track
        fill = self.rect.copy()
        fill.width = int(self.rect.width * self.value)
        pygame.draw.rect(screen, (224, 160, 48), fill)              # fill
        pygame.draw.rect(screen, (120, 125, 135), self.rect, 1)     # border

        # knob
        knob_x = self.rect.x + int(self.rect.width * self.value)
        knob = pygame.Rect(0, 0, 10, 24)
        knob.center = (knob_x, self.rect.centery)
        pygame.draw.rect(screen, (255, 220, 120), knob)

        # label and value as percentage
        text = f"{self.label} {int(self.value * 100)}%"
        surf = self.font.render(text, True, (255, 220, 120))
        screen.blit(surf, (self.rect.x, self.rect.y - 28))