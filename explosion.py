import pygame
import random

class Explosion(pygame.sprite.Sprite):
    def __init__(self, position):
        if hasattr(self.__class__, "containers"):
            super().__init__(self.__class__.containers)
        else:
            super().__init__()

        self.position = pygame.Vector2(position)
        # how long explosion lasts
        self.lifetime = 0.5

        # generate ran vectors for 15 explosion shards
        self.particles = []
        for _ in range(15):
            velocity = pygame.Vector2(random.uniform(-180, 180), random.uniform(-180, 180))
            # track both start pos copy and its ind speed vector
            self.particles.append({"pos": pygame.Vector2(self.position), "vel": velocity})

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
            return

        # move each particle pos vector by its vel over dt
        for p in self.particles:
            p["pos"] += p["vel"] * dt

    def draw(self, screen):
        # fiery neon color
        color = (255, random.randint(120, 220), 0)

        for p in self.particles:
            # draw tiny 3px circles for the debris shards
            pygame.draw.circle(screen, color, (int(p["pos"].x), int(p["pos"].y)), 3)
