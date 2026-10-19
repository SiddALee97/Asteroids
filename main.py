from cargodrone import CargoDrone
import random
from upgrades import Upgrade
from explosion import Explosion
from score import ScoreKeeper
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
from constants import DRONE_SPAWN_COOLDOWN



def main():
    x = SCREEN_WIDTH / 2
    y = SCREEN_HEIGHT / 2

    # initializing pygame early in order to draw menu
    pygame.init()
    font = pygame.font.Font(None, 48)

    # creating the groups
    shots = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    upgrades = pygame.sprite.Group()
    cargo_drones = pygame.sprite.Group()
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()

    # specifying containers the class belongs to
    Shot.containers = (shots, updatable, drawable)
    AsteroidField.containers = (updatable)
    Asteroid.containers = (updatable, drawable, asteroids)
    Player.containers = (updatable, drawable)
    ScoreKeeper.containers = (drawable)
    Explosion.containers = (drawable, updatable)
    Upgrade.containers = (upgrades, drawable, updatable)
    CargoDrone.containers = (drawable, updatable, cargo_drones)

    # initializing an instance of the objects
    field = AsteroidField()
    player = Player(x, y, PLAYER_RADIUS)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    score_keeper = ScoreKeeper()

    # prints startup message
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    # creates time keeper
    clock = pygame.time.Clock()
    dt = 0.0

    # Game State (possible: "PLAYING", "GAME_OVER", "PAUSED"
    game_state = "PLAYING"

    # drone initial timer
    drone_spawn_timer = 5.0

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
                        upgrades.empty()

                        # 2. Respawn brand new player, asteroid field, and score keeper
                        player = Player(x, y, PLAYER_RADIUS)
                        field = AsteroidField()
                        score_keeper = ScoreKeeper()

                        # 3. Resume the game loop
                        game_state = "PLAYING"


            screen.fill("black")

            # Draw everything in the background first to ensure objects stay visible and frozen
            for obj in drawable:
                obj.draw(screen)


            


            # Conditionally run game logic or popup menu
            if game_state == "PLAYING":
                # Normal gameplay loop

                # adding updating back inside loop since pause didn't work
                updatable.update(dt)

                player.cdt -= dt

                # new drone timer
                drone_spawn_timer -= dt
                if drone_spawn_timer <= 0:
                    # random spawn
                    spawn_x = random.choice([0, SCREEN_WIDTH])
                    spawn_y = random.randint(0, SCREEN_HEIGHT)
                    CargoDrone(spawn_x, spawn_y, radius = 25)

                    # reset timer
                    drone_spawn_timer = DRONE_SPAWN_COOLDOWN

                # checks drone collision
                for drone in cargo_drones:
                    for shot in shots:
                        if shot.collides_with(drone):
                            log_event("cargo_drone_hit")
                            shot.kill()
                            drone.take_damage(1)

                for obj in asteroids:
                    if player.collides_with(obj):
                        log_event("player_hit")
                        # create and explosion where player is
                        Explosion(player.position)
                        # make player ship disappear
                        player.kill()
                        # changes the game state
                        game_state = "GAME_OVER"

                # checks upgrade collision and applies
                if game_state == "PLAYING":
                    for upgrade in upgrades:
                        if player.collides_with(upgrade):
                            log_event(f"upgrade_collected_{upgrade.kind}")
                            upgrade.apply_to_player(player)
                            upgrade.kill()

                if game_state == "PLAYING":
                    for obj in asteroids:
                        for shot in shots:
                            if shot.collides_with(obj):
                                log_event("asteroid_shot")
                                shot.kill()

                                # inserting chance to spawn upgrade
                                if random.random() < 0.20:
                                    Upgrade(obj.position.x, obj.position.y, Upgrade.STANDARD_POOL)

                                obj.split()
                                score_keeper.add_points(10)

            elif game_state == "GAME_OVER":
                # adding updating in this loops so explosion particles keep moving when player dies
                updatable.update(dt)

                # draw game over overlay text
                menu_text = font.render("MAYDAY! MAYDAY! MAYDAY! - Press 'R' to Restart", True, "white")
                text_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
                score_text = font.render(f"Final Score: {score_keeper.score}", True, "white")
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, text_rect.bottom + 30))
                screen.blit(menu_text, text_rect)
                screen.blit(score_text, score_rect)

            elif game_state == "PAUSED":
                # draw transparent overlay for Pause Menu
                pause_text = font.render("PAUSED - Press ESC to Resume", True, "yellow")
                text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(pause_text, text_rect)



            pygame.display.flip()
            dt=clock.tick(60)/1000
            



if __name__ == "__main__":
    main()

