from hit import Hit, HitKind, HitOutcome, HitResult
import viewport
from constants import *
from debug import debug
from camera import camera
from world import world
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
from logger import log_state

# helper for future weapons that dont use shots


def resolve_hit(source, target):
    hit = source.make_hit()
    result = target.take_hit(hit)
    if result.outcome == HitOutcome.NOTHING:
        return result
    source.register_hit(target)
    source.already_hit.update(result.spawned)
    if result.outcome == HitOutcome.DESTROYED:
        if (isinstance(target, Asteroid)
                and target.tier == ASTEROID_SPAWN_TIERS - 1
                and random.random() < UPGRADE_DROP_CHANCE):
            Upgrade(target.position.x, target.position.y, Upgrade.STANDARD_POOL)
    return result

def draw_reticle(screen, pos):
    if pos[1] >= PLAY_HEIGHT:
        return
    center = (int(pos[0]), int(pos[1]))
    pygame.draw.circle(screen, "white", center, 8, 1)

    
def main():

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



    # making some helper functions to clean up some code in main 
    def clear_map():
        for group in (updatable, drawable, cargo_drones, upgrades, asteroids, shots, shockwaves,):
            group.empty()
        # every new game and every return to the menu starts from the normal
        world.reset_base()
        camera.fit_world(instant=True)

    def new_game():
        clear_map()
        return AsteroidField(), Player(world.width / 2, world.height / 2, PLAYER_RADIUS), ScoreKeeper()

    # initializing an instance of the objects ( we will only init asteroid field on startup for background of main menu )
    field = AsteroidField()
    camera.fit_world(instant=True)
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    reticle_image = pygame.image.load("assets/reticle.png").convert_alpha()
    cargo_sprites = {}
    for h in (3, 2, 1):
        n = 4 - h # health 3 -> file 1, health 1 -> file
        try:
            cargo_sprites[h] = pygame.image.load(f"assets/cargo_drone_{n}.png").convert_alpha()
        except FileNotFoundError:
            # fallback if file is missing
            cargo_sprites[h] = pygame.Surface((64, 64), pygame.SRCALPHA)
            fallback_color = "cyan" if h == 3 else ("yellow" if h == 2 else "orange")
            pygame.draw.ellipse(cargo_sprites[h], fallback_color, (0, 0, 100, 100))
                # specifying sprites
    CargoDrone.sprites = cargo_sprites
    Asteroid.sprites = {
        0: pygame.image.load("assets/asteroid1.png").convert_alpha()
        }

    # prints startup message
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")

    # creates time keeper
    clock = pygame.time.Clock()
    dt = 0.0
    fullscreen = False
    window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)

    player = None

    # Game State (possible: "PLAYING", "GAME_OVER", "PAUSED", "MENU"
    game_state = "MENU"

    # drone initial timer
    drone_spawn_timer = 5.0

    # Future proofing the UI setup for buttons
    btn_width, btn_height = 240, 50
    center_x = (SCREEN_WIDTH // 2) - (btn_width // 2)
    center_y = PLAY_HEIGHT // 2

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
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    event = pygame.event.Event(event.type, {**event.dict, "pos": viewport.to_game(event.pos)})
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
                    if event.key == pygame.K_F11:
                        if not fullscreen:
                            window_size = pygame.display.get_surface().get_size()
                            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                            fullscreen = True
                        else:
                            pygame.display.set_mode(window_size, pygame.RESIZABLE)
                            fullscreen = False
                        continue
                    debug.handle_key(event, player, game_state)  # debug injection
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



            camera.update(dt)  # runs in every state so zooms keep easing during pause and cutscenes
            screen.fill("black")

            mx, my = viewport.mouse_pos() # hidden in game but bugged on WSL check on native windows
            pygame.mouse.set_visible(game_state != "PLAYING" or my >= PLAY_HEIGHT)

# -------------------Draw everything in the background first to ensure objects stay visible and frozen

            # make world objects draw inside play field
            screen.set_clip(pygame.Rect(0, 0, PLAY_WIDTH, PLAY_HEIGHT))
            for obj in drawable:
                obj.draw(screen)
            screen.set_clip(None)

            # draw hitboxes (debug)
            if debug.show_hitboxes:
                debug.draw_hitboxes(screen, player, (
                    (asteroids, "red"),
                    (shockwaves, "orange"),
                    (cargo_drones, "cyan"),
                    (shots, "orange"),
                    (upgrades, "green")
                ))

            # temp divider for testing will remove later
            pygame.draw.line(screen, "cyan", (0, PLAY_HEIGHT), (PLAY_WIDTH, PLAY_HEIGHT), 2)

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

#-----------------------Normal gameplay loop----------------------------

                # handle debug toggles for spawns
                if debug.no_spawns:
                    field.spawn_timer = 0

                # adding updating back inside loop since pause didn't work
                updatable.update(dt)


                # Drone Spawn

                drone_spawn_timer -= dt
                if drone_spawn_timer <= 0:
                    # random spawn and capped number
                    if len(cargo_drones) < 1:
                        spawn_x = random.choice([0, world.width])
                        spawn_y = random.uniform(0, world.height)
                        CargoDrone(spawn_x, spawn_y, radius = 25,)

                    # reset timer
                    drone_spawn_timer = DRONE_SPAWN_COOLDOWN

                # checks drone collision
                for drone in cargo_drones:
                    for shot in shots:
                        if shot.can_hit(drone) and shot.collides_with(drone):
                            log_event("cargo_drone_hit")
                            result = resolve_hit(shot, drone)
                            score_keeper.add_points(result.points)
                            break
                            
                        

                # checks player death
                for obj in asteroids:
                    if player.collides_with(obj) and not debug.god_mode:        # checks god mode toggle
                        log_event("player_hit")
                        # create and explosion where player is
                        Explosion(player.position)
                        # make player ship disappear
                        player.kill()
                        # changes the game state
                        game_state = "GAME_OVER"
                        break

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
                            if shot.can_hit(obj) and shot.collides_with(obj):
                                log_event("asteroid_shot")
                                result = resolve_hit(shot, obj)
                                score_keeper.add_points(result.points)
                                break


                    # check shockwave
                    for wave in shockwaves:
                        for obj in list(asteroids):
                            if obj not in wave.already_hit and wave.collides_with(obj):
                                result = resolve_hit(wave, obj)
                                score_keeper.add_points(result.points)
                                wave.already_hit.add(obj)
                        for drone in cargo_drones:
                            if drone not in wave.already_hit and wave.collides_with(drone):
                                result = resolve_hit(wave, drone)
                                score_keeper.add_points(result.points)






            elif game_state == "GAME_OVER":
                # adding updating in this loops so explosion particles keep moving when player dies
                updatable.update(dt)

                # draw game over overlay text
                menu_text = font.render("MAYDAY! MAYDAY! MAYDAY! - Press 'R' to Restart", True, "white")
                text_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, PLAY_HEIGHT // 2 - 20))
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
                text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, PLAY_HEIGHT // 2))
                screen.blit(pause_text, text_rect)

                # add buttons to PAUSED
                for button in pause_buttons:
                    button.draw(screen)


            debug.draw(screen, player,
                       {"asteroids": asteroids, "drones": cargo_drones,
                        "shots": shots, "upgrades": upgrades},
                        clock)


            if game_state == "PLAYING":
                reticle_rect = reticle_image.get_rect(center = (mx, my))
                screen.blit(reticle_image, reticle_rect)
                draw_reticle(screen, viewport.mouse_pos())
            viewport.present(screen)
            pygame.display.flip()
            dt=clock.tick(60)/1000




if __name__ == "__main__":
    main()

