import pygame
from constants import SFX_VOLUME, MUSIC_VOLUME

sounds = {}
_current_playlist = None
_current_track = 0
sfx_volume = SFX_VOLUME
music_volume = MUSIC_VOLUME
SOUNDS = {
    "shot": ("assets/audio/sfx/shot.wav", 0.2),
    "shockwave": ("assets/audio/sfx/shockwave.wav", 1.0),
    "laser": ("assets/audio/sfx/laser.wav", 0.5),
    "panel_booting": ("assets/audio/sfx/panel_booting.wav", 0.75),
    "panel_opening": ("assets/audio/sfx/panel_opening.wav", 0.25),
    "panel_closing": ("assets/audio/sfx/panel_closing.wav", 0.40),
    "player_hit": ("assets/audio/sfx/player_hit.wav", 0.75),
    "player_death": ("assets/audio/sfx/player_death.wav", 0.5),
    "scrap_1": ("assets/audio/sfx/scrap_1.wav", 1.0),
    "scrap_2": ("assets/audio/sfx/scrap_2.wav", 1.0),
    "scrap_3": ("assets/audio/sfx/scrap_3.wav", 1.0),
    "scrap_4": ("assets/audio/sfx/scrap_4.wav", 1.0),
    "scrap_5": ("assets/audio/sfx/scrap_5.wav", 1.0),
    "scrap_6": ("assets/audio/sfx/scrap_6.wav", 1.0),
    "scrap_7": ("assets/audio/sfx/scrap_7.wav", 1.0),
    "scrap_8": ("assets/audio/sfx/scrap_8.wav", 1.0),
    "scrap_9": ("assets/audio/sfx/scrap_9.wav", 1.0),
    "scrap_10": ("assets/audio/sfx/scrap_10.wav", 1.0),
    "scrap_11": ("assets/audio/sfx/scrap_11.wav", 1.0),
}

menu_playlist = [
    "assets/audio/music/cb_green_bird.mp3",
]

game_playlist = [
    "assets/audio/music/cb_too_good_too_bad.mp3",
    "assets/audio/music/cb_piano_black.mp3",
    "assets/audio/music/cb_ganymade.mp3",
]



def set_sfx_volume(v):
    global sfx_volume
    sfx_volume = max(0.0, min(1.0, v))
    for name, (path, base) in SOUNDS.items():
        if name in sounds:
            sounds[name].set_volume(sfx_volume * base)

def set_music_volume(v):
    global music_volume
    music_volume = max(0.0, min(1.0, v))
    pygame.mixer.music.set_volume(music_volume)

def load_sounds():
    # so rapid cannon doesnt drop sounds
    pygame.mixer.set_num_channels(32)
    # call this in main to load all the sounds
    for name, (path, volume) in SOUNDS.items():
        try:
            s = pygame.mixer.Sound(path)
            s.set_volume(SFX_VOLUME * volume)
            sounds[name] = s
        except (FileNotFoundError, pygame.error):
            print(f"missing sound: {path}")

def play(name):
    s = sounds.get(name)
    if s:
        s.play()

def play_music(playlist, loop=False):
    global _current_playlist, _current_track

    if playlist == _current_playlist:
        return

    _current_playlist = playlist
    _current_track = 0
    start_track(loop)

def start_track(loop = False):
    track_path = _current_playlist[_current_track]
    try:
        pygame.mixer.music.load(track_path)
        pygame.mixer.music.set_volume(music_volume)
        pygame.mixer.music.play(-1 if loop else 0)
    except (FileNotFoundError, pygame.error):
        print(f"missing music: {track_path}")

def next_track():
    global _current_track
    if not _current_playlist:
        return

    _current_track = (_current_track + 1) % len(_current_playlist)
    start_track(loop = False)



def stop_music():
    global _current_playlist
    _current_playlist = None
    pygame.mixer.music.stop()
    