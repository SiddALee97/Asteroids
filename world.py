from constants import SCREEN_WIDTH, SCREEN_HEIGHT
import pygame


class World:
    def __init__(self):
        # start at exactly one screen size so it feels normal
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT

    def resize(self, scale):
        # resizing only changes the rules of the play area not the camera,
        # need to call camera helper to frame new size
        self.width = SCREEN_WIDTH * scale
        self.height = SCREEN_HEIGHT * scale

    def pull_inside(self, obj, dt, margin, strength):
        # soft border ( gravity sort of )
        # How far past each edge is the object? 0 while inside the world.
        # The sign points back toward the inside.
        dx = dy = 0
        if obj.position.x < 0:
            dx = -obj.position.x                 # past left  -> push right
        elif obj.position.x > self.width:
            dx = self.width - obj.position.x     # past right -> push left
        if obj.position.y < 0:
            dy = -obj.position.y
        elif obj.position.y > self.height:
            dy = self.height - obj.position.y

        # Spring: acceleration is proportional to depth.
        obj.velocity += pygame.Vector2(dx, dy) * strength * dt

        # Hard limit so a fast object can't escape the margin entirely.
        obj.position.x = max(-margin, min(self.width + margin, obj.position.x))
        obj.position.y = max(-margin, min(self.height + margin, obj.position.y))


# One shared instance
world = World()
