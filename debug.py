import pygame
from camera import camera
from world import world
from cargodrone import CargoDrone
from upgrades import Upgrade
from constants import SCREEN_WIDTH, MAX_WEAPON_LEVEL

# Master switch: change to False to disable debug feature
DEBUG = True

# Weapon names as listed in Player.shoot()
WEAPONS = ["MULTISHOT", "SHOCKWAVE", "LASER"]


class Debug:
    def __init__(self):
        self.visible = False        # toggle the overlay
        self.god_mode = False       # invincibility
        self.no_spawns = False      # stops asteroid spawning
        self.show_hitboxes = False  # toggles all hitboxes
        self.font = None            # pygame.init() must run first
        self.selected = 0

    # hitbox method
    def draw_hitboxes(self, screen, player, groups):
        for group, color in groups:
            for s in group:
                pygame.draw.circle(screen, color, camera.world_to_screen(s.position), s.radius * camera.zoom, 1)
        if player != None:
            pts = [camera.world_to_screen(p) for p in player.triangle()]
            pygame.draw.polygon(screen, "yellow", pts, 1)

    # handle inputs
    def handle_key(self, event, player, game_state):
        if not DEBUG:
            return
        if event.key == pygame.K_F1:
            self.visible = not self.visible
            return
        # hotkeys only work when overlay is on (besides f1 obviously)
        if not self.visible or game_state != "PLAYING" or player is None:
            return

        k = event.key
        # F2 spawns cargo drone near player
        if k == pygame.K_F2:
            CargoDrone(player.position.x + 200, player.position.y, radius=25)

        # F3 select weapon type
        elif k == pygame.K_F3:
            self.selected = (self.selected + 1) % len(WEAPONS)

        # F4 weapon level up
        elif k == pygame.K_F4:
            name = WEAPONS[self.selected]
            player.weapon_levels[name] = min(player.weapon_levels[name] + 1, MAX_WEAPON_LEVEL)

        # F5 weapon level down
        elif k == pygame.K_F5:
            name = WEAPONS[self.selected]
            player.weapon_levels[name] = max(player.weapon_levels[name] - 1, 0)

        # F6 toggle god mode
        elif k == pygame.K_F6:
            self.god_mode = not self.god_mode

        # F7 toggle asteroid spawing
        elif k == pygame.K_F7:
            self.no_spawns = not self.no_spawns

        # F8 toggle zoom (boss arena)
        elif k == pygame.K_F8:
            if not world.is_boss:
                world.enter_boss()
                camera.fit_world(speed=0.8)
            else:
                world.reset_base()
                camera.fit_world(speed=1.5)
            # re-center player
            player.position = pygame.Vector2(world.width / 2, world.height / 2)
            player.velocity = pygame.Vector2(0, 0)

        # F9 drop a standard upgrade
        elif k == pygame.K_F9:
            Upgrade(player.position.x + 120, player.position.y, Upgrade.STANDARD_POOL)

        # F10 toggles visible hitboxes
        elif k == pygame.K_F10:
            self.show_hitboxes = not self.show_hitboxes


        # ------------- DEBUG HUD -------------
    def draw(self, screen, player, groups, clock):
        # Call last in the frame. Draws fixed px positions ignores camera
        if not DEBUG or not self.visible:
            return
        if self.font is None:
            self.font = pygame.font.Font(None, 22)

        lines = [f"FPS {clock.get_fps():.0f}"]
        if player is not None:
            lines += [
                "levels: " + " ".join(
                    f"{'>' if WEAPONS[self.selected] == n else ''}{n} {player.weapon_levels[n]}"
                    for n in WEAPONS),
                f"speed: {player.speed:.0f} turn: {player.turn_speed:.0f}",
                f"cooldown: {player.shoot_cooldown:.2f} shot speed: {player.shoot_speed:.0f}",
                f"radius {player.radius:.1f}",
            ]
        lines += [
            f"world: {world.width:.0f}x{world.height:.0f} zoom: {camera.zoom:.2f}",
            "asteroids: {} drones: {} shots: {} upgrades {}".format(
                len(groups["asteroids"]), len(groups["drones"]),
                len(groups["shots"]), len(groups["upgrades"])),
            f"god mode: {'ON' if self.god_mode else 'OFF'}   "
            f"spawns: {'PAUSED' if self.no_spawns else 'ON'}",
            "",
            "F1: debug  F2: drone  F3: pick weapon  F4/F5: its lvl +/-",
            "F6: god mode  F7: spawns  F8: zoom  F9: upgrade  F10: hitboxes"
        ]

        # position it on the top right of screen
        y = 10
        for text in lines:
            surf = self.font.render(text, True, "lime")
            screen.blit(surf, (SCREEN_WIDTH - surf.get_width() - 10, y))
            y += surf.get_height() + 2


# Shared instance
debug = Debug()


