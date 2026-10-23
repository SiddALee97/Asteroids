from hit import HitResult, HitOutcome, HitKind
from camera import camera
from world import world
import pygame
from circleshape import CircleShape
from constants import *
from logger import log_event
import random


class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, tier: int) -> None:
        super().__init__(x, y, ASTEROID_SIZES[tier])
        self.tier = tier
        self.health = ASTEROID_HEALTHS[tier]



    def draw(self, screen):
        # skip drawing when completely off-screen
        if not camera.visible(self.position, self.radius):
            return
        pygame.draw.circle(
            screen, "white",
            camera.world_to_screen(self.position),   # where
            self.radius * camera.zoom,                # how big
            camera.line(LINE_WIDTH),                  # line thickness
        )


    def update(self, dt):
        self.position += self.velocity * dt
        # cleanup: delete asteroids that drift far outside the world.
        # the margin must be bigger than the spawn offset (ASTEROID_MAX_RADIUS),
        # or asteroids would be deleted the moment they spawn.
        m = ASTEROID_MAX_RADIUS * 2
        if not (-m < self.position.x < world.width + m
                and -m < self.position.y < world.height + m):
            self.kill()

    def split(self):
        if not self.alive():
            return
        self.kill()
        old_radius = self.radius
        if self.radius <= ASTEROID_MIN_RADIUS:
            return
        else:
            log_event("asteroid_split")
            x, y = self.position
            random_angle = random.uniform(20, 50)
            new_vector1 = self.velocity.rotate(random_angle)
            new_vector2 = self.velocity.rotate(-random_angle)
            new_radius = old_radius - ASTEROID_MIN_RADIUS
            new_1 = Asteroid(x, y, new_radius)
            new_2 = Asteroid(x, y, new_radius)
            new_1.velocity = new_vector1 * 1.2
            new_2.velocity = new_vector2 * 1.2


    def fragment(self, tiers):
        new_tier = self.tier - tiers
        new_spawns = []
        if tiers <= 0:
            return new_spawns
        if new_tier >= 0:
            x, y = self.position
            log_event("asteroid_fragmented")
            for _ in range(2 ** tiers):
                random_angle = random.uniform(-50, 50)
                fragment = Asteroid(x, y, new_tier)
                fragment.velocity = self.velocity.rotate(random_angle) * 1.2
                new_spawns.append(fragment)
        return new_spawns

    def take_shot(self, hit):
        self.health -= hit.damage
        if self.health > 0:
            return HitResult(HitOutcome.CHIPPED)
        self.kill()
        fragments = self.fragment(hit.breakage)
        return HitResult(HitOutcome.DESTROYED, points = ASTEROID_SCORES[self.tier], spawned = fragments)

    def take_laser(self, hit):
        new_tier = self.tier - hit.breakage
        if new_tier < 0:
            self.kill()
            return HitResult(HitOutcome.DESTROYED, points = ASTEROID_SCORES[self.tier])
        if new_tier >= 0:
            new_points = ASTEROID_SCORES[self.tier] - ASTEROID_SCORES[new_tier]
            self.tier = new_tier
            self.radius = ASTEROID_SIZES[new_tier]
            self.health = min(self.health, ASTEROID_HEALTHS[new_tier])
            return HitResult(HitOutcome.SHRUNK, points = new_points)

    def take_blast(self, hit):
        new_tier = max(0, self.tier - hit.breakage)
        tiers = self.tier - new_tier
        self.kill()
        fragments = self.fragment(tiers)
        return HitResult(HitOutcome.DESTROYED, points = ASTEROID_SCORES[self.tier], spawned = fragments)


    def take_hit(self, hit):
        if not self.alive():
            return HitResult(HitOutcome.NOTHING)

        if hit.kind is HitKind.SHOT:
            return self.take_shot(hit)

        if hit.kind is HitKind.LASER:
            return self.take_laser(hit)

        if hit.kind is HitKind.BLAST:
            return self.take_blast(hit)

        return HitResult(HitOutcome.NOTHING)






