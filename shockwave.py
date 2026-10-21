import pygame
from circleshape import CircleShape

class Shockwave(CircleShape):
    def __init__(self, x, y, max_radius, speed=500):
        super().__init__(x, y, radius=10)
        self.max_radius = max_radius
        self.speed = speed
        self.already_hit = set() # this will track which obj are hit so we dont double hit same target in mult frames

    def update(self, dt):
        self.radius += self.speed * dt
        if self.radius >= self.max_radius:
            self.kill()

    def draw(self, screen):
        pygame.draw.circle(screen, "yellow", self.position, self.radius, 2)


