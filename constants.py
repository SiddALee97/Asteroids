
#----------------------- WORLD CONSTANTS -----------------------#
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
WORLD_BASE_SCALE = 1.5
BOSS_WORLD_SCALE = 3.5
LINE_WIDTH = 2

#----------------------- HUD CONSTANTS --------------------------#
HUD_HEIGHT = 120
PLAY_WIDTH = SCREEN_WIDTH
PLAY_HEIGHT = SCREEN_HEIGHT - HUD_HEIGHT # 600
COMMS_WIDTH = 420
COMMS_HEIGHT = 130
HUD_MARGIN = 10
H_PANEL_WIDTH = 300
H_PANEL_HEIGHT = 400
B_PANEL_WIDTH = 300
B_PANEL_HEIGHT = 400
PANEL_SLIDE_TIME = 0.5
PANEL_BOOT_TIME = 0.7
PANEL_CLOSE_TIME = 0.15

#----------------------- PLAYER CONSTANTS -----------------------#
PLAYER_RADIUS = 20
PLAYER_TURN_SPEED = 300
PLAYER_SPEED = 200
PLAYER_SHOOT_SPEED = 500
PLAYER_SHOOT_COOLDOWN_SECONDS = 0.3
SHOT_RADIUS = 5

#----------------------- ASTEROID CONSTANTS -----------------------#
ASTEROID_SCORES = (5, 10, 15)
ASTEROID_HEALTHS = (1, 2, 3) # scores sizes and healths have to be the same tuple length
ASTEROID_SIZES = (20, 40, 60)
ASTEROID_SPAWN_TIERS = 3
ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3
ASTEROID_SPAWN_RATE_SECONDS = 1.2    # in seconds so higher is slower
ASTEROID_SPAWN_RATE_SCALE = 0.90   # how much the spawn rate increases every frame
ASTEROID_SPAWN_SCALE_TIMER = 15 
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS
ASTEROID_MAX_SPEED = 400
ASTEROID_MASS_EXPONENT = 1 



#----------------------- CARGO DRONE / UPGRADE CONSTANTS -----------------------#
DRONE_SPAWN_COOLDOWN = 20
DRONE_SCORE = 5

UPGRADE_DROP_CHANCE = 0.25

#----------------------- WEAPON CONSTANTS -----------------------#

MAX_WEAPON_LEVEL = 5
FORCE_SCALE = 20

#----------------------- LASER CONSTANTS -----------------------#
LASER_GENERATIONS = (0, 1, 1, 2, 2, 3)
LASER_COOLDOWN_MULT = 2.0
LASER_BASE_DAMAGE = 2
LASER_DAMAGE_PER_LEVEL = 1
LASER_SPEED_PER_LEVEL = 0.45
LASER_MAX_SPEED_MULT = 3.0  # cap so cant skip over small targets: 2.5
LASER_TRAIL_LENGTH = 45  # length of drawn streak in world units
LASER_TRAIL_PER_LEVEL = 15
LASER_FORCE = (0, 100, 100, 100, 150, 175)  # force applied to asteroids when hit by laser
TURRET_LENGTH = 30
TURRET_WIDTH = 6
TURRET_TURN_SPEED = 420

#----------------------- SHOCKWAVE CONSTANTS -----------------------#
SHOCKWAVE_SPLITS = (0, 1, 2, 3, 4, 5)
SHOCKWAVE_COOLDOWN_MULT = 6.0
SHOCKWAVE_DAMAGE = (0, 1, 1, 2, 2, 3)
SHOCKWAVE_FORCE = (0, 300, 350, 400, 450, 500) # force applied to asteroids when hit by shockwave
FORCE_FALLOFF_FLOOR = 0.25 





