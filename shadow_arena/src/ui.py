"""Reusable UI helpers: fonts, text, bars, menu list and HUD."""
import pygame

import settings as cfg


def load_fonts():
    """Create the fonts from settings.FONT_SIZES."""
    path = str(cfg.FONT_FILE) if cfg.FONT_FILE.exists() else None
    return {
        name: pygame.font.Font(path, size)
        for name, size in cfg.FONT_SIZES.items()
    }


def draw_text(surface, text, font, color, **anchor):
    """Render text; anchor is a rect keyword, e.g. center=(x, y)."""
    image = font.render(text, True, color)
    surface.blit(image, image.get_rect(**anchor))


def draw_bar(surface, rect, ratio, fill_color, back_color):
    """Draw a progress bar filled by ratio (0..1)."""
    pygame.draw.rect(surface, back_color, rect)
    fill_rect = rect.copy()
    fill_rect.width = int(rect.width * max(0.0, min(1.0, ratio)))
    pygame.draw.rect(surface, fill_color, fill_rect)
    pygame.draw.rect(surface, cfg.COLOR_TEXT, rect, cfg.BAR_BORDER_WIDTH)


def draw_hud(surface, fonts, player, score, wave, high_score):
    """Draw HP, score, wave and high score over the game field."""
    font = fonts["small"]
    pygame.draw.rect(
        surface, cfg.COLOR_HUD_BACK, (0, 0, cfg.SCREEN_WIDTH, cfg.HUD_HEIGHT)
    )
    bar_rect = pygame.Rect(
        cfg.HUD_PADDING, cfg.HUD_PADDING, cfg.HP_BAR_WIDTH, cfg.HP_BAR_HEIGHT
    )
    draw_bar(
        surface, bar_rect, player.hp / player.max_hp,
        cfg.COLOR_HP, cfg.COLOR_HP_BACK,
    )
    draw_text(
        surface, f"HP {player.hp}/{player.max_hp}", font, cfg.COLOR_TEXT,
        center=bar_rect.center,
    )
    draw_text(
        surface, f"Счёт: {score}", font, cfg.COLOR_TEXT,
        midleft=(cfg.HUD_SCORE_X, cfg.HUD_TEXT_Y),
    )
    draw_text(
        surface, f"Волна: {wave}/{cfg.FINAL_WAVE}", font, cfg.COLOR_TEXT,
        midleft=(cfg.HUD_WAVE_X, cfg.HUD_TEXT_Y),
    )
    draw_text(
        surface, f"Рекорд: {high_score}", font, cfg.COLOR_TEXT_DIM,
        midright=(cfg.SCREEN_WIDTH - cfg.HUD_PADDING, cfg.HUD_TEXT_Y),
    )


class MenuList:
    """Vertical menu controlled by keyboard and mouse."""

    def __init__(self, font, options, center_x, top):
        self._font = font
        self._options = options
        self._selected = 0
        self._rects = []
        for index, (label, _) in enumerate(options):
            rect = pygame.Rect((0, 0), font.size(label))
            rect.center = (center_x, top + index * cfg.MENU_ITEM_SPACING)
            self._rects.append(rect)

    def handle_event(self, event):
        """Move the selection or activate an option."""
        if event.type == pygame.KEYDOWN:
            if event.key in cfg.KEYS_UP:
                self._move(-1)
            elif event.key in cfg.KEYS_DOWN:
                self._move(1)
            elif event.key in cfg.KEYS_CONFIRM:
                self._activate()
        elif event.type == pygame.MOUSEMOTION:
            hovered = self._index_at(event.pos)
            if hovered is not None:
                self._selected = hovered
        elif (event.type == pygame.MOUSEBUTTONDOWN
              and event.button == pygame.BUTTON_LEFT):
            hovered = self._index_at(event.pos)
            if hovered is not None:
                self._selected = hovered
                self._activate()

    def draw(self, screen):
        for index, (label, _) in enumerate(self._options):
            color = (
                cfg.COLOR_SELECTED if index == self._selected
                else cfg.COLOR_TEXT
            )
            draw_text(
                screen, label, self._font, color,
                center=self._rects[index].center,
            )

    def _move(self, step):
        self._selected = (self._selected + step) % len(self._options)

    def _activate(self):
        self._options[self._selected][1]()

    def _index_at(self, position):
        for index, rect in enumerate(self._rects):
            pad = cfg.MENU_HIT_PADDING
            if rect.inflate(pad, pad).collidepoint(position):
                return index
        return None
