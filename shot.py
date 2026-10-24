from hit import HitKind, Hit
from camera import camera
from world import world
import pygame
from circleshape import CircleShape
from constants import SHOT_RADIUS, LINE_WIDTH, LASER_TRAIL_LENGTH


class Shot(CircleShape):
    def __init__(self, x, y, damage = 1, pierce = False, trail_length = LASER_TRAIL_LENGTH, kind = HitKind.SHOT, breakage = 1, force = 0):
        super().__init__(x, y, SHOT_RADIUS)
        self.damage = damage
        self.pierce = pierce
        self.already_hit = set()
        self.travelled = 0.0   # distance flown since spawn (limits the trail and may be used later)
        self.trail_length = trail_length
        self.kind = kind
        self.breakage = breakage 
        self.force = force

    def make_hit(self):
        direction = None
        if self.kind == HitKind.LASER:
            if self.velocity.length() > 0:
                direction = self.velocity.normalize()
        return Hit(kind = self.kind, damage = self.damage, force = self.force, breakage = self.breakage, direction = direction, origin = self.position.copy(), reach = self.radius)


    def can_hit(self, target):
        # stops piercing objects from multi hitting
        return target not in self.already_hit

    def register_hit(self, target):
        # piercing check and kill (also adds to the already hit list)
        self.already_hit.add(target)
        if not self.pierce:
            self.kill()

    def draw(self, screen):
        # skip drawing when completely off-screen
        if not camera.visible(self.position, self.radius + self.trail_length):
            return

        head = camera.world_to_screen(self.position)
        if self.pierce and self.velocity.length() > 0:
            # trail cant be longer than disance travelled so far so it grows out the nose instead
            trail = min(self.trail_length, self.travelled)
            tail = camera.world_to_screen(
                self.position - self.velocity.normalize() * trail)
            pygame.draw.line(screen, "purple", head, tail, camera.line(3))
        else:
            pygame.draw.circle(
                screen, "white", head,
                max(1, self.radius * camera.zoom),
                camera.line(LINE_WIDTH),
            )

    def update(self, dt):
        self.position += self.velocity * dt
        self.travelled += self.velocity.length() * dt

        # kill shots that leave the play area (follows boss-arena resizes)
        if (self.position.x < -self.radius or self.position.x > world.width + self.radius
                or self.position.y < -self.radius or self.position.y > world.height + self.radius):
            self.kill()
