import pygame
from constants import SFX_VOLUME, MUSIC_VOLUME

sounds = {}

def load_sounds():
    # call this in main to load all the sounds
    names = {
        "shot": "assets/audio/sfx/shot.wav",
        "radio": "assets/audio/sfs/radio.wav",
    }
    for name, path in names.items():
        try:
            s = pygame.mixer.Sound(path)
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
    