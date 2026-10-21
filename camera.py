import math
import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from world import world


class Camera:

    """Converts WORLD coordinates (where things live) to SCREEN coordinates
    (where they get drawn). Game logic never touches the camera; only draw()
    methods do.

        The two numbers that define a view:
    zoom   1.0 = normal, 0.5 = everything half size (see 2x as much)
    center the world point shown in the middle of the window
    """

    def __init__(self):

        # middle of the window in px
        self.half = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

        # Current view
        self.zoom = 1.0
        self.center = pygame.Vector2(self.half)

        # where you view is going
        self.target_zoom = 1.0
        self.target_center = pygame.Vector2(self.half)

        # zoom speed
        self.speed = 2.0


    def fit_world(self, speed=None, instant=False):

        """Frame the ENTIRE current world in the window.

        Zoom is the smaller of the two ratios so the whole world fits even if
        the world's shape differs from the window's. At world = 1 screen this
        gives zoom 1.0 and center = screen middle (the identity view).
        """

        self.target_zoom = min(SCREEN_WIDTH / world.width, SCREEN_HEIGHT / world.height)
        self.target_center = pygame.Vector2(world.width / 2, world.height / 2)
        if speed:
            self.speed = speed # remembered but gets reset if passed a new one
        if instant:             # skip animation for new game and menu
            self.zoom = self.target_zoom
            self.center = self.target_center.copy()


    def update(self, dt):

        # call once per frame for easy transition using nice curvy func (exp)

        t = 1 - math.exp(-self.speed * dt)
        self.zoom += (self.target_zoom - self.zoom) * t
        self.center = self.center.lerp(self.target_center, t)

    def world_to_screen(self, pos):

        # shifting view to line up with middle

        return (pygame.Vector2(pos) - self.center) * self.zoom + self.half

    def visible(self, pos, radius):

        # False if object is off screen so we dont have to draw it
        s = self.world_to_screen(pos)
        r = radius * self.zoom
        return -r < s.x < SCREEN_WIDTH + r and -r < s.y < SCREEN_HEIGHT + r

    def line(self, width):

        # scale the line width with the zoom so lines dont dissapear

        return max(1, round(width * self.zoom))


# Shared instance
camera = Camera()








