import sys
from shot import Shot
from logger import log_event
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

    # initializing pygame early in order to draw menu
    pygame.init()
    font = pygame.font.Font(None, 48)

    # creating the groups
    shots = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()

    # specifying which groups the class belongs to
    Shot.containers = (shots, updatable, drawable)
    AsteroidField.containers = (updatable)
    Asteroid.containers = (updatable, drawable, asteroids)
    Player.containers = (updatable, drawable)

    # initializing an instance of the objects
    field = AsteroidField()
    player = Player(x, y, PLAYER_RADIUS)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # prints startup message
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    # creates time keeper
    clock = pygame.time.Clock()
    dt = 0.0

    # Game State (possible: "PLAYING", "GAME_OVER", "PAUSED"
    game_state = "PLAYING"



    while True:
            log_state()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        return

                # Global inputs
                if event.type == pygame.KEYDOWN:

                    # check for pause
                    if event.key == pygame.K_ESCAPE:
                        if game_state == "PLAYING":
                            game_state = "PAUSED"
                        elif game_state == "PAUSED":
                            game_state = "PLAYING"



                    # check for restart input
                    if game_state == "GAME_OVER" and event.key == pygame.K_r:
                        # 1. clear everything currently on screen
                        updatable.empty()
                        drawable.empty()
                        asteroids.empty()
                        shots.empty()

                        # 2. Respawn brand new player and asteroid field
                        player = Player(x, y, PLAYER_RADIUS)
                        field = AsteroidField()

                        # 3. Resume the game loop
                        game_state = "PLAYING"


            screen.fill("black")

            # Draw everything in the background first to ensure objects stay visible and frozen
            for obj in drawable:
                obj.draw(screen)


            # Conditionally run game logic or popup menu
            if game_state == "PLAYING":
                # Normal gameplay loop

                updatable.update(dt)
                player.cdt -= dt

                for obj in asteroids:
                    if player.collides_with(obj):
                        log_event("player_hit")
                        print("Game over!")
                        # changes the game state
                        game_state = "GAME_OVER"

                for obj in asteroids:
                    for shot in shots:
                        if shot.collides_with(obj):
                            log_event("asteroid_shot")
                            shot.kill()
                            obj.split()

            elif game_state == "GAME_OVER":
                # draw game over overlay text
                menu_text = font.render("MAYDAY! MAYDAY! MAYDAY! - Press 'R' to Restart", True, "white")
                text_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(menu_text, text_rect)

            elif game_state == "PAUSED":
                # draw transparent overlay for Pause Menu
                pause_text = font.render("PAUSED - Press ESC to Resume", True, "yellow")
                text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(pause_text, text_rect)



            pygame.display.flip()
            dt=clock.tick(60)/1000
            



if __name__ == "__main__":
    main()

