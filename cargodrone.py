from camera import camera
from world import world
import pygame
import random
from circleshape import CircleShape
from upgrades import Upgrade
from constants import ASTEROID_MASS_EXPONENT, LINE_WIDTH, DRONE_SCORE, FORCE_SCALE, ASTEROID_MAX_SPEED, DRONE_SPRITE_SCALE
from hit import HitResult, HitOutcome
from explosion import Explosion



class CargoDrone(CircleShape):
    
    def __init__(self, x: float, y: float, radius: float):
        super().__init__(x, y, radius)

        # change the speed profile (random direction * speed scalar)
        angle = random.uniform(0, 360)
        speed = random.uniform(40, 80) # px per second
        self.velocity = pygame.Vector2(0, 1).rotate(angle) * speed
        
        # amount of shots to break
        self.health = 3

        


    def draw(self, screen):
        # skip drawing if off screen
        if not camera.visible(self.position, self.radius * 1.65):
            return

        z = camera.zoom
        w = self.radius * 1.65 * z  # half-width on screen
        h = self.radius * 0.9 * z  # half-height on screen
        c = camera.world_to_screen(self.position)

        # grab the exact image linked to drones health
        current_sprite = self.sprites.get(self.health, self.sprites[1])

        # scale the image
        size = int(max(1, current_sprite.get_width() * DRONE_SPRITE_SCALE * camera.zoom))

        scaled_image = pygame.transform.scale(current_sprite, (size, size))

        # position and draw to world coordinates
        image_rect = scaled_image.get_rect(center = (c.x, c.y))
        screen.blit(scaled_image, image_rect)


    def update(self, dt: float):
        self.position += self.velocity * dt

        # no more screen wrapping! time for gravity!
        world.pull_inside(self, dt, margin=150, strength=3)

    def take_hit(self, hit):
        if not self.alive():
            return HitResult(HitOutcome.NOTHING)
        self.health -= hit.damage
        if self.health > 0:
            strength = hit.force_at(self.position)
            self.apply_force(hit, strength)
            return HitResult(HitOutcome.CHIPPED, points = 0)
        self.break_open()
        return HitResult(HitOutcome.DESTROYED, points = DRONE_SCORE)

    def break_open(self):
        # trigger same explosion from player death
        Explosion(self.position)

        Upgrade(self.position.x, self.position.y, Upgrade.CARGO_POOL)
        self.kill()

    def apply_force(self, hit, strength):
        # apply force to drones's velocity
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