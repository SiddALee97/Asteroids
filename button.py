import viewport
import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, base_color="gray", hover_color="white", text_color="black"):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color

        # render text once to save performance (instead of drawing every update)
        self.text_surf = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, screen):
        # check if mouse is hovering over button
        mouse_pos = viewport.mouse_pos()
        if self.rect.collidepoint(mouse_pos):
            color = self.hover_color
        else:
            color = self.base_color

        # draw button
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        screen.blit(self.text_surf, self.text_rect)

    def is_clicked(self, event):
        # returns true if mouse click event hapened inside button
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # handles if multiple buttons get pressed at the same time
            if self.rect.collidepoint(event.pos):
                return True
        return False
