from camera import camera
import pygame
from circleshape import CircleShape
from hit import Hit, HitKind



class Shockwave(CircleShape):

    # trying to use sprite sheet for animation
    SHEET = None
    FRAMES = []


    def __init__(self, x, y, max_radius, force = 0, speed=500, damage = 1, breakage = 1):
        super().__init__(x, y, radius=10)
        self.max_radius = max_radius
        self.speed = speed
        self.damage = damage
        self.breakage = breakage
        self.force = force
        self.already_hit = set() # this will track which obj are hit so we dont double hit same target in mult frames

        # load and slice 64x64 sprite sheet
        if Shockwave.SHEET is None:
            # use file path to load sheet
            Shockwave.SHEET = pygame.image.load("assets/shockwave_sheet.png").convert_alpha()

            # based on 64 x 64 setup
            frame_w, frame_h = 64, 64
            total_width = Shockwave.SHEET.get_width()

            # slice the sheet into frames automatically
            for i in range(total_width // frame_w):
                rect = pygame.Rect(i * frame_w, 0, frame_w, frame_h)
                Shockwave.FRAMES.append(Shockwave.SHEET.subsurface(rect))

    def update(self, dt):
        # expansion logic
        self.radius += self.speed * dt
        if self.radius >= self.max_radius:
            self.kill()

    def draw(self, screen):

        # guard against empty frame list
        if not Shockwave.FRAMES:
            return

        # track animation frame index based on circle progress
        progress = self.radius / self.max_radius
        total_frames = len(Shockwave.FRAMES)
        frame_idx = min(int(progress * total_frames), total_frames -1)

        # grab the active pixel art frame
        img = Shockwave.FRAMES[frame_idx]

        # scale it to growth of radius
        screen_diameter = int(self.radius * 2 * camera.zoom)
        if screen_diameter < 1:
            screen_diameter = 1

        scaled_img = pygame.transform.scale(img, (screen_diameter, screen_diameter))

        # position and blit centered on player world coordinate
        screen_pos = camera.world_to_screen(self.position)
        rect = scaled_img.get_rect(center = screen_pos)
        screen.blit(scaled_img, rect)


    def make_hit(self):
        return Hit(kind = HitKind.BLAST, damage = self.damage, force = self.force, breakage = self.breakage, origin = self.position.copy(), reach = self.max_radius)

    def register_hit(self, target):
        self.already_hit.add(target)