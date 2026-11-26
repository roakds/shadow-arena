"""Enemy: chases the player, winds up an attack, can be staggered."""
from enum import Enum, auto

import pygame

import settings as cfg


class EnemyState(Enum):
    """Behaviour phases of an enemy."""

    CHASE = auto()
    WINDUP = auto()
    RECOVER = auto()
    STAGGERED = auto()


_STATE_COLORS = {
    EnemyState.CHASE: cfg.COLOR_ENEMY,
    EnemyState.WINDUP: cfg.COLOR_ENEMY_WINDUP,
    EnemyState.RECOVER: cfg.COLOR_ENEMY,
    EnemyState.STAGGERED: cfg.COLOR_ENEMY_STAGGER,
}


class Enemy(pygame.sprite.Sprite):
    """A melee enemy. The orange flash warns about the incoming strike."""

    def __init__(self, position, wave):
        super().__init__()
        self.image = pygame.Surface(cfg.ENEMY_SIZE)
        self.rect = self.image.get_rect(center=position)
        self.pos = pygame.Vector2(position)
        self.hp = cfg.ENEMY_BASE_HP + (wave - 1) // cfg.ENEMY_HP_WAVE_STEP
        self.speed = min(
            cfg.ENEMY_BASE_SPEED + (wave - 1) * cfg.ENEMY_SPEED_PER_WAVE,
            cfg.ENEMY_MAX_SPEED,
        )
        self.damage = cfg.ENEMY_DAMAGE
        self.state = EnemyState.CHASE
        self.state_timer = 0.0
        self._strike_pending = False

    @property
    def is_staggered(self):
        return self.state is EnemyState.STAGGERED

    def update(self, dt, target_pos):
        if self.state is EnemyState.CHASE:
            self._chase(dt, target_pos)
        else:
            self.state_timer -= dt
            if self.state_timer <= 0:
                self._finish_state()
        self._sync_rect()
        self.image.fill(_STATE_COLORS[self.state])

    def consume_strike(self):
        """True once, in the frame when the wind-up ends."""
        pending = self._strike_pending
        self._strike_pending = False
        return pending

    def stagger(self):
        """Interrupt the enemy (called after a successful parry)."""
        self._strike_pending = False
        self._set_state(EnemyState.STAGGERED, cfg.ENEMY_STAGGER_TIME)

    def take_damage(self, amount):
        """Lose HP (more if staggered). Returns True if the enemy died."""
        if self.is_staggered:
            amount *= cfg.STAGGER_DAMAGE_MULTIPLIER
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            return True
        return False

    def _chase(self, dt, target_pos):
        offset = target_pos - self.pos
        distance = offset.length()
        if distance <= cfg.ENEMY_ATTACK_TRIGGER_RANGE:
            self._set_state(EnemyState.WINDUP, cfg.ENEMY_WINDUP_TIME)
            return
        self.pos += offset / distance * self.speed * dt

    def _finish_state(self):
        if self.state is EnemyState.WINDUP:
            self._strike_pending = True
            self._set_state(EnemyState.RECOVER, cfg.ENEMY_RECOVER_TIME)
        else:
            self._set_state(EnemyState.CHASE, 0.0)

    def _set_state(self, state, duration):
        self.state = state
        self.state_timer = duration

    def _sync_rect(self):
        self.rect.center = self.pos
        if not cfg.ARENA_RECT.contains(self.rect):
            self.rect.clamp_ip(cfg.ARENA_RECT)
            self.pos.update(self.rect.center)
