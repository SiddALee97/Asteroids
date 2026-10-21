from shockwave import Shockwave
from button import Button
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

# helper for future weapons that dont use shots
def destroy_asteroid(obj, score_keeper):
    if random.random() < 0.20:
        Upgrade(obj.position.x, obj.position.y, Upgrade.STANDARD_POOL)
    obj.split()
    score_keeper.add_points(10)

def main():
    x = SCREEN_WIDTH / 2
    y = SCREEN_HEIGHT / 2

    # initializing pygame early in order to draw menu
    pygame.init()
    font = pygame.font.Font(None, 48)

    # creating the groups
    shockwaves = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    upgrades = pygame.sprite.Group()
    cargo_drones = pygame.sprite.Group()
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()

    # specifying containers the class belongs to
    Shockwave.containers = (shockwaves, updatable, drawable)
    Shot.containers = (shots, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Asteroid.containers = (updatable, drawable, asteroids)
    Player.containers = (updatable, drawable)
    ScoreKeeper.containers = (drawable,)
    Explosion.containers = (drawable, updatable)
    Upgrade.containers = (upgrades, drawable, updatable)
    CargoDrone.containers = (drawable, updatable, cargo_drones)

    # making some helper functions to clean up some code in main ( clear board and reset board )
    def clear_map():
        for group in (updatable, drawable, cargo_drones, upgrades, asteroids, shots, shockwaves,):
            group.empty()

    def new_game():
        clear_map()
        return AsteroidField(), Player(x, y, PLAYER_RADIUS), ScoreKeeper()

    # initializing an instance of the objects ( we will only init asteroid field on startup for background of main menu )
    field = AsteroidField()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # prints startup message
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    # creates time keeper
    clock = pygame.time.Clock()
    dt = 0.0

    # Game State (possible: "PLAYING", "GAME_OVER", "PAUSED", "MENU"
    game_state = "MENU"

    # drone initial timer
    drone_spawn_timer = 5.0

    # Future proofing the UI setup for buttons
    btn_width, btn_height = 240, 50
    center_x = (SCREEN_WIDTH // 2) - (btn_width // 2)
    center_y = SCREEN_HEIGHT // 2

    # Main Menu buttons config
    play_button = Button(center_x, center_y, btn_width, btn_height, "Commence", font, "darkgray", "cyan")
    quit_button = Button(center_x, center_y + 70, btn_width, btn_height, "Quit", font, "darkgray", "cyan")
    menu_buttons = [play_button, quit_button]

    # Game Over buttons config
    game_over_r = Button(center_x, center_y + 60, btn_width, btn_height, "Restart", font, "darkgray", "cyan")
    game_over_m = Button(center_x, center_y + 130, btn_width, btn_height, "Main Menu", font, "darkgray", "cyan")
    game_over_buttons = [game_over_r, game_over_m]

    # Pause Menu buttons config:
    pause_m = Button(center_x, center_y + 50, btn_width, btn_height, "Main Menu", font, "darkgray", "cyan")
    pause_buttons = [pause_m]


    while True:
            log_state()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                        return

                # boot menu first
                if game_state == "MENU":
                    if play_button.is_clicked(event):
                        # use helper to create new game
                        field, player, score_keeper = new_game()

                        # reset timer and change game state
                        drone_spawn_timer = DRONE_SPAWN_COOLDOWN
                        game_state = "PLAYING"
                        break

                    elif quit_button.is_clicked(event):
                        pygame.quit()
                        sys.exit()

                elif game_state == "GAME_OVER":
                    if game_over_r.is_clicked(event):
                        # use helper to start new game
                        field, player, score_keeper = new_game()

                        drone_spawn_timer = DRONE_SPAWN_COOLDOWN
                        game_state = "PLAYING"
                        break

                    elif game_over_m.is_clicked(event):
                        # use helper to clear map
                        clear_map()

                        field = AsteroidField()
                        game_state = "MENU"
                        break

                elif game_state == "PAUSED":
                    if pause_m.is_clicked(event):
                        # helper to clear map
                        clear_map()

                        field = AsteroidField()
                        game_state = "MENU"
                        break

                # keyboard events
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if game_state == "PLAYING":
                            game_state = "PAUSED"
                        elif game_state == "PAUSED":
                            game_state = "PLAYING"

                    # keep r hotkey for restart on game over
                    elif game_state == "GAME_OVER" and event.key == pygame.K_r:
                        # use helper to start new game
                        field, player, score_keeper = new_game()

                        drone_spawn_timer = DRONE_SPAWN_COOLDOWN
                        game_state = "PLAYING"


            screen.fill("black")

            # Draw everything in the background first to ensure objects stay visible and frozen
            for obj in drawable:
                obj.draw(screen)

            # render different states and new menus
            if game_state == "MENU":
                updatable.update(dt)

                title_font = pygame.font.Font(None, 80)
                title_text = title_font.render("ASS*ROIDS", True, "white")
                title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, center_y - 100))
                screen.blit(title_text, title_rect)

                for button in menu_buttons:
                    button.draw(screen)

            # Conditionally run game logic or popup menu
            if game_state == "PLAYING":
                # Normal gameplay loop


                # adding updating back inside loop since pause didn't work
                updatable.update(dt)

                player.cdt -= dt

                # new drone timer
                drone_spawn_timer -= dt
                if drone_spawn_timer <= 0:
                    # random spawn and capped number
                    if len(cargo_drones) < 1:
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
                            if not drone.alive():
                                break

                # checks player death
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
                            break


                if game_state == "PLAYING":
                    # checks shot on asteroid
                    for obj in asteroids:
                        for shot in shots:
                            if shot.collides_with(obj):
                                log_event("asteroid_shot")
                                shot.kill()
                                destroy_asteroid(obj, score_keeper)
                                # need to add break so duplicates dont spawn
                                break

                    # check shockwave
                    for wave in shockwaves:
                        for obj in asteroids:
                            if obj not in wave.already_hit and wave.collides_with(obj):
                                wave.already_hit.add(obj)
                                before = set(asteroids)
                                destroy_asteroid(obj, score_keeper)
                                wave.already_hit |= (set(asteroids) - before)
                        for drone in cargo_drones:
                            if drone not in wave.already_hit and wave.collides_with(drone):
                                wave.already_hit.add(drone)
                                drone.take_damage(1)





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

                # add buttons to GAME OVER
                for button in game_over_buttons:
                    button.draw(screen)

            elif game_state == "PAUSED":
                # draw transparent overlay for Pause Menu
                pause_text = font.render("PAUSED - Press ESC to Resume", True, "yellow")
                text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(pause_text, text_rect)

                # add buttons to PAUSED
                for button in pause_buttons:
                    button.draw(screen)



            pygame.display.flip()
            dt=clock.tick(60)/1000
            



if __name__ == "__main__":
    main()

