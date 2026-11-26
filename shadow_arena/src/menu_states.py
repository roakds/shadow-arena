"""Menu-like states: main menu, controls, pause and game over."""
import pygame

import settings as cfg
from state_manager import BaseState, StateId
from ui import MenuList, draw_text


def _center(y):
    return (cfg.SCREEN_CENTER_X, y)


class MenuState(BaseState):
    """Start screen with play, controls and exit buttons."""

    def __init__(self, game):
        super().__init__(game)
        self.menu = MenuList(
            game.fonts["medium"],
            [
                ("Играть", self._play),
                ("Управление", self._show_controls),
                ("Выход", game.quit),
            ],
            cfg.SCREEN_CENTER_X,
            cfg.MENU_TOP,
        )

    def _play(self):
        self.game.states.change(StateId.PLAY)

    def _show_controls(self):
        self.game.states.push(StateId.CONTROLS)

    def handle_event(self, event):
        self.menu.handle_event(event)

    def draw(self, screen):
        fonts = self.game.fonts
        screen.fill(cfg.COLOR_BACKGROUND)
        draw_text(
            screen, cfg.TITLE.upper(), fonts["large"], cfg.COLOR_ACCENT,
            center=_center(cfg.TITLE_Y),
        )
        draw_text(
            screen, f"Рекорд: {self.game.high_score}", fonts["small"],
            cfg.COLOR_TEXT_DIM, center=_center(cfg.INFO_Y),
        )
        self.menu.draw(screen)


class ControlsState(BaseState):
    """Screen with the list of controls; any key goes back."""

    def handle_event(self, event):
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.game.states.pop()

    def draw(self, screen):
        fonts = self.game.fonts
        screen.fill(cfg.COLOR_BACKGROUND)
        draw_text(
            screen, "Управление", fonts["large"], cfg.COLOR_ACCENT,
            center=_center(cfg.TITLE_Y),
        )
        for index, line in enumerate(cfg.CONTROLS_LINES):
            draw_text(
                screen, line, fonts["small"], cfg.COLOR_TEXT,
                center=_center(cfg.CONTROLS_TOP + index * cfg.LINE_SPACING),
            )
        hint_y = cfg.CONTROLS_TOP + len(cfg.CONTROLS_LINES) * cfg.LINE_SPACING
        draw_text(
            screen, cfg.CONTROLS_HINT, fonts["small"], cfg.COLOR_TEXT_DIM,
            center=_center(hint_y + cfg.LINE_SPACING),
        )


class PauseState(BaseState):
    """Pause menu drawn over the frozen gameplay."""

    is_overlay = True

    def __init__(self, game):
        super().__init__(game)
        self.overlay = pygame.Surface(
            (cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT), pygame.SRCALPHA
        )
        self.overlay.fill(cfg.OVERLAY_COLOR)
        self.menu = MenuList(
            game.fonts["medium"],
            [("Продолжить", self._resume), ("В меню", self._to_menu)],
            cfg.SCREEN_CENTER_X,
            cfg.MENU_TOP,
        )

    def _resume(self):
        self.game.states.pop()

    def _to_menu(self):
        self.game.states.change(StateId.MENU)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in cfg.KEYS_PAUSE:
            self._resume()
        else:
            self.menu.handle_event(event)

    def draw(self, screen):
        screen.blit(self.overlay, (0, 0))
        draw_text(
            screen, "ПАУЗА", self.game.fonts["large"], cfg.COLOR_TEXT,
            center=_center(cfg.TITLE_Y),
        )
        self.menu.draw(screen)


class GameOverState(BaseState):
    """Victory / game over screen with score and restart."""

    def __init__(self, game, score=0, wave=1, won=False):
        super().__init__(game)
        self.score = score
        self.wave = wave
        self.won = won
        self.is_record = game.submit_score(score)
        self.menu = MenuList(
            game.fonts["medium"],
            [("Играть снова", self._restart), ("В меню", self._to_menu)],
            cfg.SCREEN_CENTER_X,
            cfg.MENU_TOP,
        )

    def _restart(self):
        self.game.states.change(StateId.PLAY)

    def _to_menu(self):
        self.game.states.change(StateId.MENU)

    def handle_event(self, event):
        self.menu.handle_event(event)

    def draw(self, screen):
        fonts = self.game.fonts
        screen.fill(cfg.COLOR_BACKGROUND)
        title = "ПОБЕДА!" if self.won else "ВЫ ПОГИБЛИ"
        title_color = cfg.COLOR_SELECTED if self.won else cfg.COLOR_ACCENT
        draw_text(
            screen, title, fonts["large"], title_color,
            center=_center(cfg.TITLE_Y),
        )
        lines = (
            f"Счёт: {self.score}",
            f"Волна: {self.wave}/{cfg.FINAL_WAVE}",
            f"Рекорд: {self.game.high_score}",
        )
        for index, line in enumerate(lines):
            draw_text(
                screen, line, fonts["small"], cfg.COLOR_TEXT,
                center=_center(cfg.INFO_Y + index * cfg.LINE_SPACING),
            )
        if self.is_record:
            draw_text(
                screen, "Новый рекорд!", fonts["small"], cfg.COLOR_SELECTED,
                center=_center(cfg.INFO_Y + len(lines) * cfg.LINE_SPACING),
            )
        self.menu.draw(screen)
