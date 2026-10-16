import pygame

class ScoreKeeper(pygame.sprite.Sprite):
    def __init__(self):
        # read containers in main.py and set automatically
        if hasattr(self.__class__, "containers"):
            super().__init__(self.__class__.containers)
        else:
            super().__init__()

        self.score = 0
        self.font = pygame.font.Font(None, 36)


    def reset(self):
        self.score = 0

    def add_points(self, points):
        self.score += points

    def update(self, dt):
        # we dont move score but pygame groups need an update method
        pass

    def draw(self, screen):
        # render score text
        score_surface = self.font.render(f"Score: {self.score}", True, "white")
        # position it on screen (top-left corner with 10px margin)
        screen.blit(score_surface, (10, 10))
