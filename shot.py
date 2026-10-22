from camera import camera
from world import world
import pygame
from circleshape import CircleShape
from constants import SHOT_RADIUS, LINE_WIDTH, LASER_TRAIL_LENGTH


class Shot(CircleShape):
    def __init__(self, x, y, damage = 1, pierce = False):
        super().__init__(x, y, SHOT_RADIUS)
        self.damage = damage
        self.pierce = pierce
        self.already_hit = set()

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
        if not camera.visible(self.position, self.radius + LASER_TRAIL_LENGTH):
            return
        head = camera.world_to_screen(self.position)
        if self.pierce and self.velocity.length() > 0:
            # laser is just the streak behind the shot's position
            tail = camera.world_to_screen(
                self.position - self.velocity.normalize() * LASER_TRAIL_LENGTH)
            pygame.draw.line(screen, "purple", head, tail, camera.line(3))
        else:
            pygame.draw.circle(
                screen, "white", head,
                max(1, self.radius * camera.zoom),
                camera.line(LINE_WIDTH),
            )

    def update(self, dt):
        self.position += self.velocity * dt

        # kill shots that leave the play area (follows boss-arena resizes)
        if (self.position.x < -self.radius or self.position.x > world.width + self.radius
                or self.position.y < -self.radius or self.position.y > world.height + self.radius):
            self.kill()
