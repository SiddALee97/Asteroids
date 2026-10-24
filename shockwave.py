from camera import camera
import pygame
from circleshape import CircleShape
from hit import Hit, HitKind



class Shockwave(CircleShape):
    def __init__(self, x, y, max_radius, force = 0, speed=500, damage = 1, breakage = 1):
        super().__init__(x, y, radius=10)
        self.max_radius = max_radius
        self.speed = speed
        self.damage = damage
        self.breakage = breakage
        self.force = force
        self.already_hit = set() # this will track which obj are hit so we dont double hit same target in mult frames

    def update(self, dt):
        self.radius += self.speed * dt
        if self.radius >= self.max_radius:
            self.kill()

    def draw(self, screen):
        pygame.draw.circle(
            screen, "yellow",
            camera.world_to_screen(self.position),   # where
            self.radius * camera.zoom,               # how big
            camera.line(2),                          # line thickness
        )

    def make_hit(self):
        return Hit(kind = HitKind.BLAST, damage = self.damage, force = self.force, breakage = self.breakage, origin = self.position.copy(), reach = self.max_radius)

    def register_hit(self, target):
        self.already_hit.add(target)