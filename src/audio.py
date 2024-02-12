from enum import Enum
import time
from small_ass_cache import AssetCache, loader

import pygame


def load_sound(path):
    return pygame.mixer.Sound(path)


def load_song(path):
    return path
    # return pygame.mixer.music.load(path)


class Audio:
    def __init__(self) -> None:
        pygame.mixer.init()
        self.sounds = AssetCache()
        self.music = AssetCache()

        self.events = []


@loader(load_sound, path="assets/sounds/")
class Sounds(Enum):
    pass


@loader(load_song, path="assets/music/")
class Music(Enum):
    FRENCH_JAZZ = "unfree_french_jazz.mp3"


################################ AUDIO EVENTS ################################
class AudioEvent:
    pass


class PlaySong(AudioEvent):
    def __init__(self, song) -> None:
        super().__init__()
        self.song = song


class PlaySound(AudioEvent):
    def __init__(self, sound) -> None:
        super().__init__()
        self.sound = sound


########################### AUDIO EVENT HANDLER ##############################
def handle_audio_events(audio):
    for event in audio.events:
        match event:
            case PlaySong():
                song_path = audio.music.get(event.song)
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                pygame.mixer.music.set_volume(1.0)
            case PlaySound():
                sound = audio.sounds.get(event.sound)
                sound.play()
            case _:
                pass

    audio.events.clear()


if __name__ == "__main__":
    audio = Audio()
    # while True:
    #     jump_sound = audio.sounds.get(Sounds.JUMP)
    #     jump_sound.set_volume(0.1)
    #     jump_sound.play()
    #     time.sleep(1)

    music_path = audio.sounds.get(Music.SHITTING)
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.1)

    # lower volume
    # pygame.mixer.music.fadeout(5000)

    while True:
        pass
