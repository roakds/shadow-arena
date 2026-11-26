"""Loading and playing music and sound effects."""
import pygame

import settings as cfg


class SoundManager:
    """Plays sound effects and music; silently disabled without audio."""

    def __init__(self):
        self._sounds = {}
        self.enabled = self._init_mixer()
        if self.enabled:
            self._load_sounds()

    @staticmethod
    def _init_mixer():
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            return False
        return True

    def _load_sounds(self):
        for name, filename in cfg.SFX_FILES.items():
            path = cfg.SOUNDS_DIR / filename
            if path.exists():
                sound = pygame.mixer.Sound(str(path))
                sound.set_volume(cfg.SFX_VOLUME)
                self._sounds[name] = sound

    def play(self, name):
        """Play a sound effect by its name from settings.SFX_FILES."""
        sound = self._sounds.get(name)
        if sound is not None:
            sound.play()

    def play_music(self):
        """Start looping background music."""
        if self.enabled and cfg.MUSIC_FILE.exists():
            pygame.mixer.music.load(str(cfg.MUSIC_FILE))
            pygame.mixer.music.set_volume(cfg.MUSIC_VOLUME)
            pygame.mixer.music.play(loops=cfg.MUSIC_LOOPS)
