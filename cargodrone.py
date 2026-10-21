from camera import camera
from world import world
import pygame
import random
from circleshape import CircleShape
from upgrades import Upgrade
from constants import LINE_WIDTH

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

        # creat rect
        oval_rect = pygame.Rect(c.x - w, c.y - h, w * 2, h * 2)

        # visual effects for hits
        color = "cyan"
        if self.health == 2:
            color = "yellow"
        elif self.health == 1:
            color = "orange"



        # draw oval ( will still have rect hitbox )
        pygame.draw.ellipse(screen, color, oval_rect, camera.line(LINE_WIDTH))

    def update(self, dt: float):
        self.position += self.velocity * dt

        # no more screen wrapping! time for gravity!
        world.pull_inside(self, dt, margin=150, strength=3)

    def take_damage(self, amount: int = 1):
        self.health -= amount
        if self.health <= 0:
            self.break_open()

    def break_open(self):
        Upgrade(self.position.x, self.position.y, Upgrade.CARGO_POOL)
        self.kill()
