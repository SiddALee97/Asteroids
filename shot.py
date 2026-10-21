from camera import camera
from world import world
import pygame
from circleshape import CircleShape
from constants import SHOT_RADIUS
from constants import LINE_WIDTH


class Shot(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, SHOT_RADIUS)

    def draw(self, screen):
        # skip drawing when completely off-screen
        if not camera.visible(self.position, self.radius):
            return
        pygame.draw.circle(
            screen, "white",
            camera.world_to_screen(self.position),      # where
            max(1, self.radius * camera.zoom),          # how big (never below 1px)
            camera.line(LINE_WIDTH),                    # line thickness
        )


    def update(self, dt):
        self.position += self.velocity * dt

        # kill shots that leave the play area (follows boss-arena resizes)
        if (self.position.x < -self.radius or self.position.x > world.width + self.radius
                or self.position.y < -self.radius or self.position.y > world.height + self.radius):
            self.kill()
