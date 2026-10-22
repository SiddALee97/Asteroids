from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_BASE_SCALE, BOSS_WORLD_SCALE
import pygame


class World:
    def __init__(self):
        # Using world base scale to set the normal window
        self.width = SCREEN_WIDTH * WORLD_BASE_SCALE
        self.height = SCREEN_HEIGHT * WORLD_BASE_SCALE
        self.is_boss = False

    @property
    def scale(self):
        # how many windows wide the world is at a moment
        return self.width / SCREEN_WIDTH

    def resize(self, scale):
        # resizing only changes the rules of the play area not the camera,
        # need to call camera helper to frame new size
        self.width = SCREEN_WIDTH * scale
        self.height = SCREEN_HEIGHT * scale

    def reset_base(self):
        self.resize(WORLD_BASE_SCALE)
        self.is_boss = False

    def enter_boss(self):
        self.resize(BOSS_WORLD_SCALE)
        self.is_boss = True

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
