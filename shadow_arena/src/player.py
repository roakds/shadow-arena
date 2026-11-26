"""Player character: movement, dodge roll, attack and parry."""
import pygame

import settings as cfg


def _pressed(keys, key_group):
    return any(keys[key] for key in key_group)


class Player(pygame.sprite.Sprite):
    """The hero: WASD to move, mouse to aim, LMB attack, RMB parry."""

    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface(cfg.PLAYER_SIZE)
        self.rect = self.image.get_rect(center=position)
        self.pos = pygame.Vector2(position)
        self.facing = pygame.Vector2(1, 0)
        self.max_hp = cfg.PLAYER_MAX_HP
        self.hp = cfg.PLAYER_MAX_HP
        self.attack_timer = 0.0
        self.attack_cooldown = 0.0
        self.parry_timer = 0.0
        self.parry_cooldown = 0.0
        self.dodge_timer = 0.0
        self.dodge_cooldown = 0.0
        self.invulnerable_timer = 0.0
        self._dodge_direction = pygame.Vector2()
        self._hit_targets = set()

    @property
    def is_attacking(self):
        return self.attack_timer > 0

    @property
    def is_parrying(self):
        return self.parry_timer > 0

    @property
    def is_dodging(self):
        return self.dodge_timer > 0

    @property
    def is_invulnerable(self):
        return self.is_dodging or self.invulnerable_timer > 0

    def start_attack(self):
        """Begin a swing. Returns True if the swing really started."""
        if self.attack_cooldown > 0 or self.is_dodging or self.is_parrying:
            return False
        self.attack_timer = cfg.ATTACK_DURATION
        self.attack_cooldown = cfg.ATTACK_COOLDOWN
        self._hit_targets.clear()
        return True

    def start_parry(self):
        """Open the parry window. Returns True if it started."""
        if self.parry_cooldown > 0 or self.is_dodging or self.is_attacking:
            return False
        self.parry_timer = cfg.PARRY_WINDOW
        self.parry_cooldown = cfg.PARRY_COOLDOWN
        return True

    def start_dodge(self):
        """Roll in the movement direction (backwards if standing)."""
        if self.dodge_cooldown > 0:
            return False
        direction = self._read_direction()
        if direction.length_squared() == 0:
            direction = -self.facing
        self._dodge_direction = direction
        self.dodge_timer = cfg.DODGE_DURATION
        self.dodge_cooldown = cfg.DODGE_COOLDOWN
        self.attack_timer = 0.0
        self.parry_timer = 0.0
        return True

    def hits(self, enemy):
        """True once per swing if the enemy is inside the attack arc."""
        if not self.is_attacking or enemy in self._hit_targets:
            return False
        offset = enemy.pos - self.pos
        distance = offset.length()
        if distance > cfg.ATTACK_RANGE:
            return False
        if distance > 0 and self.facing.dot(offset / distance) < (
                cfg.ATTACK_ARC_DOT):
            return False
        self._hit_targets.add(enemy)
        return True

    def take_damage(self, amount):
        """Lose HP unless invulnerable. Returns True if damage was dealt."""
        if self.is_invulnerable:
            return False
        self.hp -= amount
        self.invulnerable_timer = cfg.HIT_INVULNERABLE_TIME
        return True

    def heal(self, amount):
        self.hp = min(self.max_hp, self.hp + amount)

    def update(self, dt):
        self._tick_timers(dt)
        self._update_facing()
        self._move(dt)
        self._update_image()

    def draw_effects(self, screen):
        """Draw the slash lines and the parry ring."""
        if self.is_attacking:
            for angle in cfg.SLASH_ANGLES:
                end = self.pos + self.facing.rotate(angle) * cfg.ATTACK_RANGE
                pygame.draw.line(
                    screen, cfg.COLOR_SLASH, self.pos, end, cfg.SLASH_WIDTH
                )
        if self.is_parrying:
            pygame.draw.circle(
                screen, cfg.COLOR_PARRY, self.pos,
                cfg.PARRY_RING_RADIUS, cfg.PARRY_RING_WIDTH,
            )

    @staticmethod
    def _read_direction():
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            _pressed(keys, cfg.KEYS_RIGHT) - _pressed(keys, cfg.KEYS_LEFT),
            _pressed(keys, cfg.KEYS_DOWN) - _pressed(keys, cfg.KEYS_UP),
        )
        if direction.length_squared() > 0:
            direction.normalize_ip()
        return direction

    def _tick_timers(self, dt):
        self.attack_timer = max(0.0, self.attack_timer - dt)
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        self.parry_timer = max(0.0, self.parry_timer - dt)
        self.parry_cooldown = max(0.0, self.parry_cooldown - dt)
        self.dodge_timer = max(0.0, self.dodge_timer - dt)
        self.dodge_cooldown = max(0.0, self.dodge_cooldown - dt)
        self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)

    def _update_facing(self):
        if self.is_attacking:
            return
        to_mouse = pygame.Vector2(pygame.mouse.get_pos()) - self.pos
        if to_mouse.length_squared() > 0:
            self.facing = to_mouse.normalize()

    def _move(self, dt):
        if self.is_dodging:
            velocity = self._dodge_direction * cfg.DODGE_SPEED
        else:
            speed = cfg.PLAYER_SPEED
            if self.is_attacking:
                speed *= cfg.ATTACK_MOVE_FACTOR
            velocity = self._read_direction() * speed
        self.pos += velocity * dt
        self.rect.center = self.pos
        if not cfg.ARENA_RECT.contains(self.rect):
            self.rect.clamp_ip(cfg.ARENA_RECT)
            self.pos.update(self.rect.center)

    def _update_image(self):
        if self.is_dodging:
            color = cfg.COLOR_PLAYER_DODGE
        elif self._is_blinking():
            color = cfg.COLOR_PLAYER_HURT
        else:
            color = cfg.COLOR_PLAYER
        self.image.fill(color)

    def _is_blinking(self):
        phase = int(self.invulnerable_timer / cfg.HURT_BLINK_INTERVAL)
        return self.invulnerable_timer > 0 and phase % 2 == 0
