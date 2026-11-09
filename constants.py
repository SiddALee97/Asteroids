
#----------------------- WORLD CONSTANTS -----------------------#
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
WORLD_BASE_SCALE = 1.5
BOSS_WORLD_SCALE = 3.5
LINE_WIDTH = 2

#----------------------- HUD CONSTANTS --------------------------#

PLAY_WIDTH = SCREEN_WIDTH
PLAY_HEIGHT = SCREEN_HEIGHT
HUD_MARGIN = 25
#----------------------- COMMS CONSTANTS -----------------------#
COMMS_WIDTH = 420
COMMS_HEIGHT = 132
COMMS_CHARS_PER_SECOND = 30.0
COMMS_HOLD_TIME = 3.0
COMMS_SPRITE_SCALE = 2.0
#----------------------- PANEL CONSTANTS -----------------------#
H_PANEL_WIDTH = 300
H_PANEL_HEIGHT = 400
H_SLOT_RECTS =((32, 260, 78, 22),(158, 260, 78, 22), (32, 292, 78, 22), (158, 292, 78, 22))
H_SCREEN_RECT = (32, 56, 236, 178)
H_LIGHT_RECTS = ((118, 260, 24, 22), (244, 260, 24, 22), (118, 292, 24, 22), (244, 292, 24, 22))
H_AUTO_RECT = (240, 332, 32, 46)
B_PANEL_WIDTH = 300
B_PANEL_HEIGHT = 400
B_SLOT_RECTS =((64, 260, 78, 22), (190, 260, 78, 22), (64, 292, 78, 22), (190, 292, 78, 22))
B_SCREEN_RECT = (32, 56, 236, 178)
B_LIGHT_RECTS = ((32, 260, 24, 22), (158, 260, 24, 22), (32, 292, 24, 22), (158, 292, 24, 22))
B_AUTO_RECT = (28, 332, 32, 46)
PANEL_SLIDE_TIME = 0.25   # lower is faster
PANEL_BOOT_TIME = 0.7
PANEL_CLOSE_TIME = 0.10
PANEL_BOTTOM_GAP = 100
PANEL_OPEN_TIME_SCALE = 0.25   # how much the auto buy timer slows down if panel is open
PANEL_IDLE_TIME = 8.0          # the timer for auto buy
PANEL_PULSE_SPEED = 3.0


#----------------------- PLAYER CONSTANTS -----------------------#
PLAYER_RADIUS = 20
PLAYER_TURN_SPEED = 300
PLAYER_SPEED = 200
PLAYER_REVERSE_MULT = 0.5 # mult speed going backwards
PLAYER_SHOOT_SPEED = 500
PLAYER_SHOOT_COOLDOWN_SECONDS = 0.3
SHOT_RADIUS = 5
SHIP_SPRITE_SCALE = 2.0 # on screen size mult for ship sprite
PLAYER_HITBOX_SCALE = 1.1
PLAYER_HITBOX_WIDTH = 1.4
THRUSTER_FRAME_TIME = 0.125   # seconds per frame
THRUSTER_OFFSET = 41         # world units behind ship center   
PLAYER_START_HULL = 3
PLAYER_MASS = 20
PLAYER_INVULNERABILITY_TIME = 1.5
RAM_DAMAGE_CAP = 100
ASTEROID_CONTACT_DAMAGE = (1, 1, 2) # damage for each tier as a tuple, must be same length as asteroid tiers
PLAYER_CONTACT_RADIUS = 26
SHIELD_BOUNCE = 0.1  


#----------------------- ASTEROID CONSTANTS -----------------------#
ASTEROID_SCORES = (5, 10, 15)
ASTEROID_HEALTHS = (1, 2, 3) # scores sizes and healths have to be the same tuple length
ASTEROID_SIZES = (28, 42, 56)
ASTEROID_SPAWN_TIERS = 3
ASTEROID_MIN_RADIUS = max(ASTEROID_SIZES)
ASTEROID_KINDS = 3
ASTEROID_SPAWN_RATE_SECONDS = 2.4    # in seconds so higher is slower
ASTEROID_SPAWN_RATE_SCALE = 0.95   # how much the spawn rate increases every inst
ASTEROID_SPAWN_SCALE_TIMER = 25 
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS
ASTEROID_MAX_SPEED = 400
ASTEROID_MASS_EXPONENT = 1 
ASTEROID_SPRITE_SCALE = 2.0
ASTEROID_SPIN_RANGE = 60  # max degrees per second



#----------------------- CARGO DRONE -----------------------#
DRONE_SPAWN_COOLDOWN = 20
DRONE_SCORE = 5
DRONE_SPRITE_SCALE = 1.25



#----------------------- SALVAGE / SCRAP ------------------------#

STANDARD_DROP_TABLE = [1, 1, 1, 2, 2]
RARE_DROP_TABLE = [1, 1, 1, 2, 5]
SCRAP_DROP_CHANCE = (0.10, 0.15, 0.25) # one per tier, same length as len(asteroid_sizes)
SCRAP_DROP_TABLES = (STANDARD_DROP_TABLE, STANDARD_DROP_TABLE, RARE_DROP_TABLE) # which table does each tier pull from


#----------------------- UPGRADES ------------------------------#

SPEED_BONUS = (0, 40, 80, 120, 160) # 4 purchases -> 5 entries
HULL_BONUS = (0, 1, 2, 3)


#----------------------- WEAPON CONSTANTS -----------------------#

MAX_WEAPON_LEVEL = 5
FORCE_SCALE = 20

#----------------------- SHOT CONSTANTS -----------------------#

SHOT_SPRTIE_SCALE = 2.0 


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
TURRET_LENGTH = 45
TURRET_WIDTH = 6
TURRET_TURN_SPEED = 300

#----------------------- SHOCKWAVE CONSTANTS -----------------------#
SHOCKWAVE_SPLITS = (0, 1, 2, 3, 4, 5)
SHOCKWAVE_COOLDOWN_MULT = 6.0
SHOCKWAVE_DAMAGE = (0, 1, 1, 1, 2, 3)
SHOCKWAVE_FORCE = (0, 400, 450, 500, 550, 600) # force applied to asteroids when hit by shockwave
FORCE_FALLOFF_FLOOR = 0.25 





