from asteroid import Asteroid
from asteroidfield import AsteroidField
import pygame
from player import Player
from constants import SCREEN_HEIGHT, SCREEN_WIDTH
from logger import log_state
from constants import PLAYER_RADIUS


def main():
    x = SCREEN_WIDTH / 2
    y = SCREEN_HEIGHT / 2
    asteroids = pygame.sprite.Group()
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    AsteroidField.containers = (updatable)
    Asteroid.containers = (updatable, drawable, asteroids)
    Player.containers = (updatable, drawable)
    field = AsteroidField()
    player = Player(x, y, PLAYER_RADIUS)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.init()
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    clock = pygame.time.Clock()
    dt = 0.0
    while True:
            log_state()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        return

            screen.fill("black")

            for obj in drawable:
                obj.draw(screen)

            updatable.update(dt)
            pygame.display.flip()
            dt=clock.tick(60)/1000
            



if __name__ == "__main__":
    main()

