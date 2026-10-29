from hit import HitResult, HitOutcome, HitKind
from camera import camera
from world import world
import pygame
from circleshape import CircleShape
from constants import ASTEROID_SCORES, ASTEROID_HEALTHS, ASTEROID_KINDS, ASTEROID_MASS_EXPONENT, ASTEROID_MAX_RADIUS, ASTEROID_MAX_SPEED, ASTEROID_MIN_RADIUS, ASTEROID_SIZES, ASTEROID_SPAWN_RATE_SCALE, ASTEROID_SPAWN_RATE_SECONDS, ASTEROID_SPAWN_SCALE_TIMER, ASTEROID_SPAWN_TIERS, ASTEROID_SPIN_RANGE, ASTEROID_SPRITE_SCALE, LINE_WIDTH, FORCE_SCALE
from logger import log_event
import random


class Asteroid(CircleShape):
    def __init__(self, x: float, y: float, tier: int) -> None:
        super().__init__(x, y, ASTEROID_SIZES[tier])
        self.tier = tier
        self.health = ASTEROID_HEALTHS[tier]
        self.angle = random.uniform(0, 360)
        self.spin = random.uniform(-ASTEROID_SPIN_RANGE, ASTEROID_SPIN_RANGE)


    def draw(self, screen):
        # skip drawing when completely off-screen
        if not camera.visible(self.position, self.radius):
            return
        image = self.sprites.get(self.tier)
        if image is None:
            pygame.draw.circle(
                screen, "white",
                camera.world_to_screen(self.position),   # where
                self.radius * camera.zoom,                # how big
                camera.line(LINE_WIDTH),                  # line thickness
            )
            return

        size = int(max(1, image.get_width() * ASTEROID_SPRITE_SCALE * camera.zoom))
        scaled = pygame.transform.scale(image, (size, size))
        rotated = pygame.transform.rotate(scaled, self.angle)
        rect = rotated.get_rect(center = camera.world_to_screen(self.position))
        screen.blit(rotated, rect)



    def update(self, dt):
        self.angle += self.spin * dt
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


    def fragment(self, tiers, hit, strength):
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
                fragment.apply_force(hit, strength)
                new_spawns.append(fragment)
        return new_spawns

    def take_shot(self, hit):
        self.health -= hit.damage
        if self.health > 0:
            return HitResult(HitOutcome.CHIPPED)
        self.kill()
        strength = hit.force_at(self.position)
        fragments = self.fragment(hit.breakage, hit, strength)
        return HitResult(HitOutcome.DESTROYED, points = ASTEROID_SCORES[self.tier], spawned = fragments)

    def take_laser(self, hit):
        new_tier = self.tier - hit.breakage
        if new_tier < 0:
            self.kill()
            return HitResult(HitOutcome.DESTROYED, points = ASTEROID_SCORES[self.tier])
        if new_tier >= 0:
            new_points = ASTEROID_SCORES[self.tier] - ASTEROID_SCORES[new_tier]
            strength = hit.force_at(self.position)
            self.tier = new_tier
            self.radius = ASTEROID_SIZES[new_tier]
            self.apply_force(hit, strength)
            self.health = min(self.health, ASTEROID_HEALTHS[new_tier])
            return HitResult(HitOutcome.SHRUNK, points = new_points)

    def take_blast(self, hit):
        new_tier = max(0, self.tier - hit.breakage)
        tiers = self.tier - new_tier
        self.kill()
        strength = hit.force_at(self.position)
        fragments = self.fragment(tiers, hit, strength)
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


    def apply_force(self, hit, strength):
        # apply force to asteroid's velocity
        if not self.alive():
            return
        if hit.direction is None and hit.origin is None:
            return
        if hit.direction is not None:
            direction = hit.direction
        else:
            direction = self.position - hit.origin
        mass = self.radius ** ASTEROID_MASS_EXPONENT
        if direction.length_squared() == 0:
            return
        self.velocity += direction.normalize() * strength * FORCE_SCALE / mass
        self.velocity = self.velocity.clamp_magnitude(0, ASTEROID_MAX_SPEED)
       





