#========================== IMPORTS =========================

import os
import sys
if sys.platform != "win32":                         # only run pulse audio when on linux
    os.environ["SDL_AUDIODRIVER"] = "pulseaudio"   
import random
import pygame

#-------- game systems ---------
import audio
from audio import menu_playlist, game_playlist
import viewport
from constants import *
from camera import camera
from world import world
from hit import Hit, HitKind, HitOutcome, HitResult
from logger import log_event, log_state
from debug import debug
from ships import BARRY_SLOTS, HARRY_SLOTS         # ToDo: unused?
from upgrades_shop import buy                      # ToDo: unused?
from states import GameState
from speech import Bubble
from sequence import Sequence, Beat
from tutorial import STEPS, trigger
from hints import HintManager

#-------- game objects --------
from player import Player, DashState
from asteroid import Asteroid
from asteroidfield import AsteroidField
from cargodrone import CargoDrone
from shot import Shot
from shockwave import Shockwave
from explosion import Explosion
from pickups import Pickup
from upgrades import Upgrade
from score import ScoreKeeper

#---------- UI --------------
from button import Button
from slider import Slider
from background import BackgroundLayer
from comms import hud_comms
from hud import (
    comms_rect, harry_panel, barry_panel, update_hud, kick_hud, PanelState,
    mouse_over_panel, open_panel_for,
)
from upgrades_shop import affordable_slots



#============================== MODULE-LEVEL HELPERS ================


def resolve_hit(source, target):
    # Connects anu hit source to any target
    # source builds the Hit, target decides the result, source records it
    hit = source.make_hit()
    result = target.take_hit(hit)
    if result.outcome == HitOutcome.NOTHING:
        return result
    source.register_hit(target)
    source.already_hit.update(result.spawned)
    # deleted upgrade check to handle it in asteroids.py
    return result

def draw_reticle(screen, pos):
    # Fallback circle reticle, drawn on top of reticle sprite
    if pos[1] >= PLAY_HEIGHT:
        return
    center = (int(pos[0]), int(pos[1]))
    pygame.draw.circle(screen, "white", center, 8, 1)

    
def main():

    #================== SETUP ==============
 
    pygame.mixer.pre_init(44100, -16, 2, 128)
    pygame.init()
    
    font = pygame.font.Font("assets/fonts/future_earth.ttf", 36)
    hints = HintManager()
    sequence = Sequence(camera)
    
    #---------- creating sprite groups ----------
    
    pickups = pygame.sprite.Group()
    shockwaves = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    upgrades = pygame.sprite.Group()
    cargo_drones = pygame.sprite.Group()
    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()

    # specifying containers the class belongs to which adds any new objects too the assigned groups

    Pickup.containers = (pickups, drawable, updatable)
    Shockwave.containers = (shockwaves, updatable, drawable)
    Shot.containers = (shots, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Asteroid.containers = (updatable, drawable, asteroids)
    Player.containers = (updatable, drawable)
    ScoreKeeper.containers = (drawable,)
    Explosion.containers = (drawable, updatable)
    Upgrade.containers = (upgrades, drawable, updatable)
    CargoDrone.containers = (drawable, updatable, cargo_drones)



    #================= HELPER FUNCTIONS =======================
    #      (local to main because they use the groups)

    def load_sprite(path: str):
        return pygame.image.load(path).convert_alpha()


    def slice_sheet(path, count = 5, size = 16):
        # cuts a horizontal sprite strip into "count" frames with "size" amount of pixels each frame
        sheet = load_sprite(path)
        return [sheet.subsurface(pygame.Rect(i * size, 0, size, size)) for i in range(count)]
    

    def clear_map():
        for group in (updatable, drawable, cargo_drones, upgrades, asteroids, shots, shockwaves,):
            group.empty()
        # every new game and every return to the menu starts from the normal
        world.reset_base()
        camera.fit_world(instant=True)
        hud_comms.reset()
        harry_panel.reset()
        barry_panel.reset()
        hints.reset()
        

    def new_game():
        clear_map()
        return AsteroidField(), Player(world.width / 2, world.height / 2, PLAYER_RADIUS), ScoreKeeper()

    def fire(key):
        nonlocal game_state
        if game_state is GameState.PLAYING and trigger(sequence, key, player):
            game_state = GameState.TUTORIAL
            open_panel_for(sequence.current.speaker)

    # asteroid field runs on the menu for background
    field = AsteroidField()
    camera.fit_world(instant=True)

    #=================== WINDOW AND CLOCK ==========================
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)) # we draw here, viewport.present() scales it to the window
    clock = pygame.time.Clock()
    dt = 0.0
    fullscreen = False
    window_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    player = None
    dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dim_alpha = 0.0

    #===================== LOAD AUDIO ==================================
    #                  (after mixer init)
    SONG_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(SONG_END)
    audio.load_sounds()
    audio.play_music(menu_playlist) # opening menu track

    #===================== LOAD SPRITES ================================
    #                 (must be after set mode)

    #-------- title -------------
    title_image = load_sprite("assets/sprites/title.png")

    #-------- backgrounds ---------
    background_default = load_sprite("assets/sprites/background_default.png")
    bg_far = BackgroundLayer(load_sprite("assets/sprites/background_1.png"), (-2, 1))
    bg_near = BackgroundLayer(load_sprite("assets/sprites/background_2.png"), (-8, 2))
    bg_images = [
        load_sprite("assets/sprites/background_1.png"),
        load_sprite("assets/sprites/background_2.png"),
    ]

    #---------- UI art -----------
    reticle_image = load_sprite("assets/sprites/reticle.png")
    reticle_image_armed = load_sprite("assets/sprites/reticle_2.png")
    reticle_cursor = load_sprite("assets/sprites/reticle_3.png")
    
    comms_image = load_sprite("assets/sprites/comms_panel.png")
    harry_panel.set_image(load_sprite("assets/sprites/harry_panel.png"))
    barry_panel.set_image(load_sprite("assets/sprites/barry_panel.png"))

    #---------- pickups ----------
    Pickup.scrap_sprite_lucky = load_sprite("assets/sprites/scrap_1.png")
    Pickup.scrap_sprites_rare = [
        load_sprite("assets/sprites/scrap_3.png"),
    ]
    Pickup.scrap_sprites_common = [
        load_sprite("assets/sprites/scrap_2.png"),
    ]

    Pickup.salvage_sprite_lucky = load_sprite("assets/sprites/salvage_3.png")
    Pickup.salvage_sprites_rare = [
        load_sprite("assets/sprites/salvage_2.png"),
    ]
    Pickup.salvage_sprites_common = [
        load_sprite("assets/sprites/salvage_1.png"),
    ]

    #---------- cargo drone (one sprite per health value 3=healthy) -------------------
    cargo_sprites = {}
    for h in (3, 2, 1):
        n = 4 - h # health 3 -> file 1, health 1 -> file
        try:
            cargo_sprites[h] = load_sprite(f"assets/sprites/cargo_drone_{n}.png")
        except FileNotFoundError:
            # fallback if file is missing
            cargo_sprites[h] = pygame.Surface((64, 64), pygame.SRCALPHA)
            fallback_color = "cyan" if h == 3 else ("yellow" if h == 2 else "orange")
            pygame.draw.ellipse(cargo_sprites[h], fallback_color, (0, 0, 100, 100))
                # specifying sprites
    CargoDrone.sprites = cargo_sprites

    #--------- asteroids: list of variants per tier, random selected on spawn ---------------
    Asteroid.sprites = {
        0: [load_sprite("assets/sprites/asteroid_small_1.png"), load_sprite("assets/sprites/asteroid_small_2.png")],
        1: [load_sprite("assets/sprites/asteroid_medium_1.png")],
        2: [load_sprite("assets/sprites/asteroid_large_1.png"), load_sprite("assets/sprites/asteroid_large_2.png")],
        }

    #----------- ship thruster animation strips ----------
    Player.thruster_frames = {
        "start": slice_sheet("assets/sprites/ship_startup_1.png"),
        "run": slice_sheet("assets/sprites/ship_trail_1.png"),
        "stop": slice_sheet("assets/sprites/ship_stop_1.png"),
    }

    #-------------- shots -----------------
    Shot.sprites = {
        "shot": load_sprite("assets/sprites/shot_1.png"),
        "laser_head": load_sprite("assets/sprites/laser_head_1.png"),
        # later will add "laser_trail": load_sprite("assets/laser_trail_1.png"),
    }



    # prints startup message
    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")


    #========================== GAME STATE =====================


    # Game State (possible: TITLE, MENU, TUTORIAL, PLAYING, PAUSED, GAME_OVER, SETTINGS)

    game_state = GameState.TITLE
    settings_return = GameState.MENU
    # drone initial timer
    drone_spawn_timer = 5.0

    #======================= MENU UI ================================
    #                 (on block per screen)
    btn_width, btn_height = 240, 50
    center_x = (SCREEN_WIDTH // 2) - (btn_width // 2)
    center_y = PLAY_HEIGHT // 2


    #--------------- settings screen ---------------------
    music_slider = Slider(center_x - 60, 260, 360, "MUSIC", audio.music_volume)
    sfx_slider = Slider(center_x - 60, 340, 360, "SOUND", audio.sfx_volume)
    back_button = Button(center_x, 460, btn_width, btn_height, "Back", font, "darkgray", "cyan")
    
    #--------------- main menu ----------------
    play_button = Button(center_x, center_y - 100, btn_width, btn_height, "Commence", font, "darkgray", "cyan")
    menu_settings_button = Button(center_x, center_y - 30, btn_width, btn_height, "Settings", font, "darkgrey", "cyan")
    quit_button = Button(center_x, center_y + 40, btn_width, btn_height, "Quit", font, "darkgray", "cyan")   
    menu_buttons = [play_button, menu_settings_button, quit_button]

    #----------------- game over -----------------------
    game_over_r = Button(center_x, center_y - 100, btn_width, btn_height, "Restart", font, "darkgray", "cyan")
    game_over_m = Button(center_x, center_y - 30, btn_width, btn_height, "Main Menu", font, "darkgray", "cyan")
    game_over_settings_button = Button(center_x, center_y + 40, btn_width, btn_height, "Settings", font, "darkgrey", "cyan")  
    game_over_buttons = [game_over_r, game_over_m, game_over_settings_button]

    #---------------- pause ------------------
    pause_m = Button(center_x, center_y + 10, btn_width, btn_height, "Main Menu", font, "darkgray", "cyan")
    pause_settings_button = Button(center_x, center_y + 80, btn_width, btn_height, "Settings", font, "darkgrey", "cyan")
    pause_buttons = [pause_m, pause_settings_button]

    #============================ MAIN LOOP ===================================
    while True:
            log_state()
            

            #======================== EVENT HANDLING ======================

            for event in pygame.event.get():

                # audio loop for playlists
                if event.type == SONG_END:
                    audio.next_track()
                    

                if game_state == GameState.PLAYING and event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    player.try_dash()
                if game_state == GameState.PLAYING and event.type == pygame.KEYDOWN and event.key == pygame.K_LSHIFT:
                    player.press_shift()


                #------ convert window mouse positions to game-surface positions ------
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                    event = pygame.event.Event(event.type, {**event.dict, "pos": viewport.to_game(event.pos)})
                if event.type == pygame.QUIT:
                        return

                #----- in-game panel clicks (shop buttons, slots, AUTO toggle) -------
                if game_state == GameState.PLAYING and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    harry_panel.handle_click(event.pos, player)
                    barry_panel.handle_click(event.pos, player)

                #----- per-state button clicks -------
                if game_state == GameState.MENU:
                    if play_button.is_clicked(event):
                        # audio
                        audio.play_music(game_playlist)
                        # use helper to create new game
                        field, player, score_keeper = new_game()
                        # reset timer and change game state
                        drone_spawn_timer = DRONE_SPAWN_COOLDOWN
                        game_state = GameState.PLAYING
                        fire("game_start")
                        break
                    elif quit_button.is_clicked(event):
                        pygame.quit()
                        sys.exit()
                    elif menu_settings_button.is_clicked(event):
                        settings_return = GameState.MENU
                        game_state = GameState.SETTINGS
                        break

                elif game_state == GameState.GAME_OVER:
                    if game_over_r.is_clicked(event):
                        # use helper to start new game
                        field, player, score_keeper = new_game()
                        drone_spawn_timer = DRONE_SPAWN_COOLDOWN
                        game_state = GameState.PLAYING
                        break
                    elif game_over_m.is_clicked(event):
                        # use helper to clear map
                        clear_map()
                        field = AsteroidField()
                        game_state = GameState.MENU
                        break
                    elif game_over_settings_button.is_clicked(event):
                        settings_return = GameState.GAME_OVER
                        game_state = GameState.SETTINGS
                        break

                elif game_state == GameState.PAUSED:
                    if pause_m.is_clicked(event):
                        # helper to clear map
                        clear_map()
                        field = AsteroidField()
                        game_state = GameState.MENU
                        break
                    elif pause_settings_button.is_clicked(event):
                        settings_return = GameState.PAUSED
                        game_state = GameState.SETTINGS
                        break

                elif game_state == GameState.SETTINGS:
                    if music_slider.handle_event(event):
                        audio.set_music_volume(music_slider.value)
                    if sfx_slider.handle_event(event):
                        audio.set_sfx_volume(sfx_slider.value)
                    if back_button.is_clicked(event):
                        game_state = settings_return
                        break

                elif game_state is GameState.TUTORIAL:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            sequence.advance()

                elif game_state is GameState.TITLE:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            game_state = GameState.MENU

                #-------- keyboard -----------
                if event.type == pygame.KEYDOWN:

                    # continue to next state if in title
                    if game_state is GameState.TITLE:
                        game_state = GameState.MENU

                    debug.handle_key(event, player, game_state)  # debug injection F1 - F10 hotkeys

                    if debug.visible:
                        if event.key == pygame.K_t:
                            hud_comms.say("Test message for comms panel display. This message should wrap correctly and be displayed character by character. Still not sure if I will fix the issue of the text going of the screen or just make sure i dont render any long texts but that kind of sounds annoying. So i will probably just fix it.")

                        if event.key == pygame.K_h:
                            hints.show("move")

                        if event.key == pygame.K_F12 and game_state is GameState.PLAYING:
                            beats = [
                                Beat("harry", "I am supposed to test the comms. Am I coming through the speaker", open_panel=True),
                                Beat("barry", "this one should only play once", open_panel=False, zoom = 3, key = "once"),
                            ]
                            sequence.start(beats, player)
                            if sequence.active:
                                game_state = GameState.TUTORIAL
                                open_panel_for(sequence.current.speaker)
                                            

                    if event.key == pygame.K_F11:   # fullscreen toggle (restore scale is buggy in WSL but works in native windows)
                        if not fullscreen:
                            window_size = pygame.display.get_surface().get_size()
                            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                            fullscreen = True
                        else:
                            pygame.display.set_mode(window_size, pygame.RESIZABLE)
                            fullscreen = False
                        continue



                    if game_state == GameState.TUTORIAL:
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            sequence.advance()
                        if event.key == pygame.K_ESCAPE:
                            sequence.skip()
   
                    if game_state == GameState.PLAYING:
                        hints.key_pressed(event.key)
                        if event.key == pygame.K_1:
                            harry_panel.toggle()
                            fire("open_panel")
                        elif event.key == pygame.K_2:
                            barry_panel.toggle()
                            fire("open_panel")
                        elif event.key == pygame.K_TAB:
                            harry_panel.close_panel()
                            barry_panel.close_panel()

                    if event.key == pygame.K_ESCAPE:    # pause / resume / back out of settings
                        if game_state == GameState.PLAYING:
                            game_state = GameState.PAUSED
                        elif game_state == GameState.PAUSED:
                            game_state = GameState.PLAYING
                        elif game_state == GameState.SETTINGS:
                            game_state = settings_return

                    elif game_state == GameState.GAME_OVER and event.key == pygame.K_r:     # quick restart on death
                        # use helper to start new game
                        field, player, score_keeper = new_game()
                        drone_spawn_timer = DRONE_SPAWN_COOLDOWN
                        game_state = GameState.PLAYING


            #======================= FRAME SETUP ===================================
            #                 (camera, background, cursor)

            camera.update(dt)  # runs in every state so zooms keep easing during pause and cutscenes
            screen.blit(background_default, (0, 0))
            bg_far.draw(screen)
            bg_near.draw(screen)

            mx, my = viewport.mouse_pos()
            



            #=================== DRAW THE WORLD ==================================
            #      (always, so objects stay visible when paused)
            screen.set_clip(pygame.Rect(0, 0, PLAY_WIDTH, PLAY_HEIGHT))
            for obj in drawable:
                obj.draw(screen)
            screen.set_clip(None)

            # draw hitboxes (debug)
            if debug.show_hitboxes:                         # F10 overlay
                debug.draw_hitboxes(screen, player, (
                    (asteroids, "red"),
                    (shockwaves, "orange"),
                    (cargo_drones, "cyan"),
                    (shots, "orange"),
                    (upgrades, "green")                 # ToDo: add pickup hitboxes here
                ))

            #============================ PER-STATE UPDATE and DRAW =======================

            #---------------------------- TITLE ------------------------------
            if game_state is GameState.TITLE:
                updatable.update(dt)      # asteroid field keeps moving
                bg_far.update(dt)
                bg_near.update(dt)

                title_w, title_h = title_image.get_size()
                title_img = pygame.transform.scale(title_image, (title_w * 2, title_h * 2))

                title_rect = title_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(title_img, title_rect)



            #------------------------------ MENU -------------------------------
            if game_state is GameState.MENU:
                updatable.update(dt)      # asteroid field keeps moving
                bg_far.update(dt)
                bg_near.update(dt)

                for button in menu_buttons:
                    button.draw(screen)
            #----------------------------- TUTORIAL -----------------------------
            if game_state is GameState.TUTORIAL:
                sequence.update(dt)
                update_hud(dt, player)
                harry_panel.update_animation(dt)
                barry_panel.update_animation(dt)
                bg_far.update(dt)
                bg_near.update(dt)
                
                if not sequence.active and sequence.dim_alpha < 1:
                    harry_panel.close_panel()
                    barry_panel.close_panel()
                    game_state = GameState.PLAYING
                    



            #----------------------------- PLAYING -------------------------------
            if game_state is GameState.PLAYING:

                
                # ---- updates ----
                if debug.no_spawns:
                    field.spawn_timer = 0

                updatable.update(dt)
                player.dash_graze(asteroids)
                player.update_dash_preview(asteroids)
                update_hud(dt, player)                      # spring sway and shake targets
                hud_comms.update(dt)
                hud_comms.update_lights(dt, player, harry_panel, barry_panel)
                harry_panel.update(dt, player)              # animation + auto_buy + repair
                barry_panel.update(dt, player)
                bg_far.update(dt)
                bg_near.update(dt)
                hints.update(dt)

                # ---- updates check for fire on tutorials ----
                if harry_panel.auto_bought or barry_panel.auto_bought:
                    fire("auto_buy")

                if player.overheated and player.heat <= 0.9:
                    fire("cannon_heat")

                if player.dash_state is DashState.COOLDOWN:
                    fire("first_dash")
                
                # ---- cargo drone spawning (max one at a time) ----
                drone_spawn_timer -= dt
                if drone_spawn_timer <= 0:
                    # random spawn and capped number
                    if len(cargo_drones) < 1:
                        spawn_x = random.choice([0, world.width])
                        spawn_y = random.uniform(0, world.height)
                        CargoDrone(spawn_x, spawn_y, radius = 25,)     # ToDo: use a DRONE_RADIUS constant
                    drone_spawn_timer = DRONE_SPAWN_COOLDOWN

                # ---- shots vs drones ----
                for drone in cargo_drones:
                    for shot in shots:
                        if shot.can_hit(drone) and shot.collides_with(drone):
                            log_event("cargo_drone_hit")
                            result = resolve_hit(shot, drone)
                            score_keeper.add_points(result.points)
                            break
                            
                # ---- asteroids vs player ----
                # seperate() runs first so the ship never overlaps a rock, even in god mode
                for obj in asteroids:
                    if player.dash_state is DashState.DASHING and player.dash_gravitron: # grav dash goes thru asteroids
                        continue
                    touched = player.separate(obj)
                    if touched and not debug.god_mode:   
                        fire("first_hit")           
                        result = resolve_hit(obj, player)
                        if result.outcome is HitOutcome.NOTHING:        # still invulnerable
                            continue        

                        if result.outcome is HitOutcome.CHIPPED:       
                            log_event("player_hit")
                            audio.play("player_hit")
                            kick_hud(player.position - obj.position)    # panels rattle away from the rock


                        if result.outcome is HitOutcome.DESTROYED:      # hull reached 0
                            log_event("player_destroyed")
                            Explosion(player.position)
                            audio.play("player_death")
                            kick_hud(player.position - obj.position)
                            player.kill()
                            game_state = GameState.GAME_OVER
                            break

                # ---- pickups (old upgrades, then scrap/salvage) ----
            
                for upgrade in upgrades:                    # ToDo: old system, may reuse later
                    if player.collides_with(upgrade):
                        log_event(f"upgrade_collected_{upgrade.kind}")
                        upgrade.apply_to_player(player)
                        upgrade.kill()
                        break

                
                for pickup in pickups:
                    if player.collides_with(pickup):
                        log_event(f"{pickup.kind}_collected")
                        audio.play(f"scrap_{random.randint(1, 11)}")
                        pickup.apply_to_player(player)
                        if pickup.kind == "SCRAP":
                            fire("first_scrap")
                        if pickup.kind == "SALVAGE":
                            fire("first_salvage")
                        hud_comms.alert(f"+{pickup.amount} {pickup.kind}")
                        pickup.kill()
                        break

                # ---- weapons vs targets ----
                
                    # shots (cannon + laser) vs asteroids
                for obj in asteroids:
                    for shot in shots:
                        if shot.can_hit(obj) and shot.collides_with(obj):
                            log_event("asteroid_shot")
                            result = resolve_hit(shot, obj)
                            score_keeper.add_points(result.points)
                            if shot.kind is HitKind.LASER:
                                fire("laser")
                            break

                    # shockwave vs asteroids and drones (list() because fragments spawn mid-loop)
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

            #--------------------------------- GAME OVER ---------------------------------------
            elif game_state == GameState.GAME_OVER:
                updatable.update(dt)    # explosion particles keep moving

                # draw game over overlay text
                menu_text = font.render("MAYDAY! MAYDAY! MAYDAY! - Press 'R' to Restart", True, "white")
                text_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, PLAY_HEIGHT // 2 - 200))
                score_text = font.render(f"Final Score: {score_keeper.score}", True, "white")
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, text_rect.bottom + 30))
                screen.blit(menu_text, text_rect)
                screen.blit(score_text, score_rect)

                for button in game_over_buttons:
                    button.draw(screen)

            #--------------------------------- PAUSED ------------------------------------
            elif game_state == GameState.PAUSED:
                # nothing updates here, which freezes the world, panels and HUD
                pause_text = font.render("PAUSED - Press ESC to Resume", True, "yellow")
                text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, center_y - 200))
                screen.blit(pause_text, text_rect)

                for button in pause_buttons:
                    button.draw(screen)

            #------------------------------- SETTINGS -------------------------------------
            elif game_state == GameState.SETTINGS:
                if settings_return == GameState.MENU:
                    updatable.update(dt)
                title = font.render("Settings", True, "white")
                screen.blit(title, title.get_rect(center = (SCREEN_WIDTH // 2, 180)))
                music_slider.draw(screen)
                sfx_slider.draw(screen)
                back_button.draw(screen)


            #================================= OVERLAYS ==================================
            #                (debug text, reticle, HUD (drawn last, on top))

            #--- tutorial dimmer ---
            sequence.draw_dim(screen, dim)
            #--- hint ---
            if game_state is GameState.PLAYING:
                hints.draw(screen)


            debug.draw(screen, player,
                       {"asteroids": asteroids, "drones": cargo_drones,
                        "shots": shots, "upgrades": upgrades},
                        clock)

            if game_state is not GameState.TITLE:
                hud_comms.draw(screen, comms_rect, comms_image, player, harry_panel, barry_panel)
            harry_panel.draw(screen, player)
            barry_panel.draw(screen, player)

        
            if game_state is GameState.TUTORIAL and sequence.bubble:
                panel, pos = (harry_panel, H_SPEAKER_POS) if sequence.current.speaker == "harry" else (barry_panel, B_SPEAKER_POS)
                if panel.drawn_rect is not None:
                    anchor = (panel.drawn_rect.x + pos[0], panel.drawn_rect.y + pos[1])
                    sequence.bubble.draw(screen, anchor, panel.rect)

                    
            over_panel = mouse_over_panel((mx, my))
            if game_state is GameState.PLAYING and over_panel:
                cursor, hot = reticle_cursor, HAND_HOTSPOT      # fingertip pixel, in screen pixels
            elif game_state is GameState.TUTORIAL:
                cursor, hot = reticle_cursor, HAND_HOTSPOT     
            else:
                cursor, hot = reticle_image, (reticle_image.get_width() // 2, reticle_image.get_height() // 2)
            if cursor:
                screen.blit(cursor, (mx - hot[0], my - hot[1]))
            pygame.mouse.set_visible(cursor is None)

            #================================ PRESENT ===================================
            #                        (scale to window and show)
            viewport.present(screen)
            pygame.display.flip()
            dt=clock.tick(60)/1000
            

if __name__ == "__main__":
    main()

