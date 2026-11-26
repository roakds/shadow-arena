"""Game class: window, main loop and shared resources."""
import pygame

import settings as cfg
from menu_states import ControlsState, GameOverState, MenuState, PauseState
from play_state import PlayState
from sound import SoundManager
from state_manager import StateId, StateManager
from storage import load_high_score, save_high_score
from ui import load_fonts


class Game:
    """Owns the window and runs the main loop."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(cfg.TITLE)
        self.clock = pygame.time.Clock()
        self.fonts = load_fonts()
        self.sounds = SoundManager()
        self.high_score = load_high_score()
        self.running = False
        self.states = StateManager(self)
        self.states.register(StateId.MENU, MenuState)
        self.states.register(StateId.CONTROLS, ControlsState)
        self.states.register(StateId.PLAY, PlayState)
        self.states.register(StateId.PAUSE, PauseState)
        self.states.register(StateId.GAME_OVER, GameOverState)

    def submit_score(self, score):
        """Save the score if it beats the record. Returns True if so."""
        if score <= self.high_score:
            return False
        self.high_score = score
        save_high_score(score)
        return True

    def quit(self):
        """Stop the main loop after the current frame."""
        self.running = False

    def run(self):
        """Run the game until the window is closed."""
        self.running = True
        self.states.change(StateId.MENU)
        self.sounds.play_music()
        while self.running:
            dt = self.clock.tick(cfg.FPS) / cfg.MS_PER_SECOND
            dt = min(dt, cfg.MAX_FRAME_TIME)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                else:
                    self.states.handle_event(event)
            self.states.update(dt)
            self.states.draw(self.screen)
            pygame.display.flip()
        pygame.quit()
