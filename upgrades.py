import pygame
import random
from circleshape import CircleShape

class Upgrade(CircleShape):

    # adding groups so we can spawn certain tiers of upgrades when we want
    STANDARD_POOL = ["THRUSTERS", "BLASTERS", "SHRINK"]
    CARGO_POOL = ["MULTISHOT", "BURST", "LASER"]

    # adding the upgrade pool to args for init and setting to None 
    def __init__(self, x: float, y: float, upgrade_pool=None):
        super().__init__(x, y, radius = 12)

        # if no pool is chosen just use standard pool
        if upgrade_pool is None:
            upgrade_pool = STANDARD_POOL

        self.kind = random.choice(upgrade_pool)  # random choice what kind of upgrade
        self.velocity = pygame.Vector2(0, 1).rotate(random.uniform(0, 360)) * 40
        

    def apply_to_player(self, player):

        if self.kind == "THRUSTERS":
            player.speed *= 1.5
            player.turn_speed *= 1.15

        if self.kind == "BLASTERS":
            player.shoot_speed *= 1.1
            player.shoot_cooldown *= 0.9

        if self.kind == "SHRINK":
            player.radius *= 0.80


    def draw(self, screen: pygame.Surface) -> None:
        # Assign colors
        colors = {
            "THRUSTERS": "green",
            "BLASTERS": "red",
            "SHRINK": "blue"
        }
        color = colors.get(self.kind, "white")

        # using a diamond shape (there really should be a func for these shapes)
        p = self.position
        r = self.radius
        points = [
            pygame.Vector2(p.x, p.y - r),
            pygame.Vector2(p.x + r, p.y),
            pygame.Vector2(p.x, p.y + r),
            pygame.Vector2(p.x - r, p.y)
        ]
        pygame.draw.polygon(screen, color, points, 2)

    def update(self, dt: float):
        self.position += self.velocity * dt
