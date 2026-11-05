from camera import camera
from world import world
import pygame
import random
from circleshape import CircleShape
from constants import STANDARD_DROP_TABLE, RARE_DROP_TABLE

class Pickup(CircleShape):

    # adding pickup which will act as currency counter

    KINDS = ["SCRAP", "SALVAGE"]
    scrap_sprites = {}
    salvage_sprites = {}
    def __init__(self, x, y, kind, amount_pool = None):
        super().__init__(x, y, 12)

        self.kind = kind
        if amount_pool is None:
            amount_pool = STANDARD_DROP_TABLE
        self.amount = random.choice(amount_pool)
        self.velocity = pygame.Vector2(0, 1).rotate(random.uniform(0, 360)) * 40

        scrap_sprite_pool = Pickup.scrap_sprites
        salvage_sprite_pool = Pickup.salvage_sprites

        if self.kind == "SCRAP" and scrap_sprite_pool:
            self.image = random.choice(scrap_sprite_pool)
        elif self.kind == "SALVAGE" and salvage_sprite_pool:
            self.image = random.choice(salvage_sprite_pool)
        else:
            self.image = None

    def apply_to_player(self, player):

        if self.kind == "SCRAP":
            player.scrap += self.amount

        if self.kind == "SALVAGE":
            player.salvage += self.amount

    def draw(self, screen):

        if self.image is None:
            p = self.position
            r = self.radius
            corners = [
                pygame.Vector2(p.x, p.y - r),
                pygame.Vector2(p.x + r, p.y),
                pygame.Vector2(p.x, p.y + r),
                pygame.Vector2(p.x - r, p.y)
            ]
            points = [camera.world_to_screen(c) for c in corners]  # world -> screen
            pygame.draw.polygon(screen, "green", points, camera.line(2))
            return

        pos = camera.world_to_screen(self.position)
        size_w = int(max(self.image.get_width() * 2.0 * camera.zoom, 1))
        size_h = int(max(self.image.get_height() * 2.0 * camera.zoom, 1))
        scaled = pygame.transform.scale(self.image, (size_w, size_h))
        rect = scaled.get_rect(center=pos)

        screen.blit(scaled, rect)

    def update(self, dt: float):
        self.position += self.velocity * dt

        # cleanup: delete once they drift away
        # margin is generous so they dont dissapear to early
        m = 50
        if not (-m < self.position.x < world.width + m
                and -m < self.position.y < world.height + m):
            self.kill()