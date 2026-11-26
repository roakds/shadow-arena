"""State machine: state identifiers, base state and the manager."""
from enum import Enum, auto


class StateId(Enum):
    """Names of all game states."""

    MENU = auto()
    CONTROLS = auto()
    PLAY = auto()
    PAUSE = auto()
    GAME_OVER = auto()


class BaseState:
    """Base class for every game state."""

    is_overlay = False

    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        """React to a single pygame event."""

    def update(self, dt):
        """Advance the state by dt seconds."""

    def draw(self, screen):
        """Draw the state on the screen."""


class StateManager:
    """Keeps a stack of states and forwards the game loop calls."""

    def __init__(self, game):
        self._game = game
        self._factories = {}
        self._stack = []

    def register(self, state_id, state_class):
        """Tell the manager how to create the state with this id."""
        self._factories[state_id] = state_class

    def change(self, state_id, **kwargs):
        """Replace the whole stack with a new state."""
        self._stack.clear()
        self.push(state_id, **kwargs)

    def push(self, state_id, **kwargs):
        """Put a new state on top (for example, pause over gameplay)."""
        state = self._factories[state_id](self._game, **kwargs)
        self._stack.append(state)

    def pop(self):
        """Remove the top state and return to the one below."""
        self._stack.pop()

    def handle_event(self, event):
        if self._stack:
            self._stack[-1].handle_event(event)

    def update(self, dt):
        if self._stack:
            self._stack[-1].update(dt)

    def draw(self, screen):
        """Draw the top state and the states under its overlays."""
        start = len(self._stack) - 1
        while start > 0 and self._stack[start].is_overlay:
            start -= 1
        for state in self._stack[start:]:
            state.draw(screen)
