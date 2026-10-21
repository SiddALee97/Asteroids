from constants import SCREEN_WIDTH, SCREEN_HEIGHT



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

# One shared instance
world = World()

