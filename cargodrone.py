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
        # make it look different ( lets try an oval )
        # give it the dimensions
        width_radius = self.radius * 1.65
        height_radius = self.radius * 0.9

        # find top left bounding rectangle point
        top_left_x = self.position.x - width_radius
        top_left_y = self.position.y - height_radius

        # getting the measurements for the rect hitbox
        rect_width = width_radius * 2
        rect_height = height_radius * 2

        # creat rect
        oval_rect = pygame.Rect(top_left_x, top_left_y, rect_width, rect_height)

        # visual effects for hits
        color = "cyan"
        if self.health == 2:
            color = "yellow"
        elif self.health == 1:
            color = "orange"



        # draw oval ( will still have rect hitbox )
        pygame.draw.ellipse(screen, color, oval_rect, LINE_WIDTH)

    def update(self, dt: float):
        self.position += self.velocity * dt

        # trying screen wrapping for only cargo drone (copy pasted)
        from constants import SCREEN_WIDTH, SCREEN_HEIGHT
        if self.position.x < -self.radius:
            self.position.x = SCREEN_WIDTH + self.radius
        elif self.position.x > SCREEN_WIDTH + self.radius:
            self.position.x = -self.radius
            
        if self.position.y < -self.radius:
            self.position.y = SCREEN_HEIGHT + self.radius
        elif self.position.y > SCREEN_HEIGHT + self.radius:
            self.position.y = -self.radius

    def take_damage(self, amount: int = 1):
        self.health -= amount
        if self.health <= 0:
            self.break_open()

    def break_open(self):
        Upgrade(self.position.x, self.position.y, Upgrade.CARGO_POOL)
        self.kill()
