import pygame
from constants import SFX_VOLUME, MUSIC_VOLUME

sounds = {}

def load_sounds():
    # call this in main to load all the sounds
    names = {
        "shot": "assets/audio/sfx/shot.wav",
        "shockwave": "assets/audio/sfx/shockwave.wav",
        "laser": "assets/audio/sfx/laser.wav",
        "panel_boot": "assets/audio/sfx/panel_boot.oog",
        "panel_opening_closing": "assets/audio/sfx/panel_opening_closing.wav",
        "player_hit": "assets/audio/sfx/player_hit.wav",
        "player_death": "assets/audio/sfx/player_death.wav"
    }
    for name, path in names.items():
        try:
            s = pygame.mixer.Sound(path)
            if name is "shot":
                s.set_volume(SFX_VOLUME * 0.2)
            elif name in ("laser", "player_death"):
                s.set_volume(SFX_VOLUME * 0.5)
            elif name is "player_hit":
                s.set_volume(SFX_VOLUME * 0.75)            
            else:
                s.set_volume(SFX_VOLUME)
            sounds[name] = s
        except (FileNotFoundError, pygame.error):
            print(f"missing sound: {path}")

def play(name):
    s = sounds.get(name)
    if s:
        s.play()

def play_music(path, loop=True):
    pygame.mixer.music.load(path)
    pygame.mixer.music.set_volume(MUSIC_VOLUME)
    pygame.mixer.music.play(-1 if loop else 0)

def stop_music():
    pygame.mixer.music.stop()
    