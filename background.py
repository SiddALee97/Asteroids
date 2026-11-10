import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

class BackgroundLayer():
    def __init__(self, image, speed):
        self.image = pygame.transform.scale(
            image, (image.get_width() * 2, image.get_height() * 2)
        )
        self.speed = pygame.Vector2(speed)     # pixels per second
        self.offset = pygame.Vector2(0, 0)

    def update(self, dt):
        self.offset += self.speed * dt
        # wrapping with the cool modulo trick
        self.offset.x %= self.image.get_width()
        self.offset.y %= self.image.get_height()

    def draw(self, screen):
        w, h = self.image.get_size()
        start_x = -int(self.offset.x)
        start_y = -int(self.offset.y)
        for x in range(start_x, SCREEN_WIDTH, w):
            for y in range(start_y, SCREEN_HEIGHT, h):
                screen.blit(self.image, (x, y))