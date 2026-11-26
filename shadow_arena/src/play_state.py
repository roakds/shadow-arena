"""Main gameplay state: waves, combat, score and drawing."""
import random

import pygame

import settings as cfg
from enemy import Enemy
from pickup import HealPickup
from player import Player
from state_manager import BaseState, StateId
from ui import draw_hud, draw_text


class PlayState(BaseState):
    """The arena fight: survive all waves to win."""

    def __init__(self, game):
        super().__init__(game)
        self.player = Player(cfg.ARENA_RECT.center)
        self.player_group = pygame.sprite.GroupSingle(self.player)
        self.enemies = pygame.sprite.Group()
        self.pickups = pygame.sprite.Group()
        self.score = 0
        self.wave = 1
        self.enemies_to_spawn = 0
        self.spawn_timer = 0.0
        self.break_timer = cfg.WAVE_BREAK_TIME

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in cfg.KEYS_PAUSE:
                self.game.states.push(StateId.PAUSE)
            elif event.key == cfg.KEY_DODGE:
                self.player.start_dodge()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == pygame.BUTTON_LEFT:
                if self.player.start_attack():
                    self.game.sounds.play("attack")
            elif event.button == pygame.BUTTON_RIGHT:
                self.player.start_parry()

    def update(self, dt):
        self.player.update(dt)
        self.enemies.update(dt, self.player.pos)
        self.pickups.update(dt)
        self._resolve_player_attack()
        self._resolve_enemy_strikes()
        self._collect_pickups()
        if self.player.hp <= 0:
            self._finish(won=False)
        else:
            self._update_waves(dt)

    def draw(self, screen):
        screen.fill(cfg.COLOR_BACKGROUND)
        pygame.draw.rect(screen, cfg.COLOR_ARENA, cfg.ARENA_RECT)
        pygame.draw.rect(
            screen, cfg.COLOR_ARENA_BORDER, cfg.ARENA_RECT,
            cfg.ARENA_BORDER_WIDTH,
        )
        self.pickups.draw(screen)
        self.enemies.draw(screen)
        self.player_group.draw(screen)
        self.player.draw_effects(screen)
        draw_hud(
            screen, self.game.fonts, self.player, self.score, self.wave,
            max(self.game.high_score, self.score),
        )
        if self.break_timer > 0:
            draw_text(
                screen, f"Волна {self.wave}", self.game.fonts["large"],
                cfg.COLOR_TEXT, center=cfg.ARENA_RECT.center,
            )

    def _resolve_player_attack(self):
        for enemy in self.enemies:
            if self.player.hits(enemy):
                if enemy.take_damage(cfg.PLAYER_ATTACK_DAMAGE):
                    self._on_enemy_killed(enemy)

    def _on_enemy_killed(self, enemy):
        self.score += cfg.SCORE_KILL
        if random.random() < cfg.PICKUP_DROP_CHANCE:
            self.pickups.add(HealPickup(enemy.pos))

    def _resolve_enemy_strikes(self):
        for enemy in self.enemies:
            if not enemy.consume_strike():
                continue
            distance = enemy.pos.distance_to(self.player.pos)
            if distance > cfg.ENEMY_ATTACK_RANGE:
                continue
            if self.player.is_parrying:
                enemy.stagger()
                self.score += cfg.SCORE_PARRY
                self.game.sounds.play("parry")
            elif self.player.take_damage(enemy.damage):
                self.game.sounds.play("hurt")

    def _collect_pickups(self):
        collected = pygame.sprite.spritecollide(
            self.player, self.pickups, True
        )
        for _ in collected:
            self.player.heal(cfg.PICKUP_HEAL)
            self.score += cfg.SCORE_PICKUP
            self.game.sounds.play("pickup")

    def _update_waves(self, dt):
        if self.break_timer > 0:
            self.break_timer -= dt
            if self.break_timer <= 0:
                self.enemies_to_spawn = (
                    cfg.WAVE_BASE_ENEMIES
                    + (self.wave - 1) * cfg.WAVE_ENEMY_STEP
                )
                self.spawn_timer = 0.0
        elif self.enemies_to_spawn > 0:
            self._spawn_step(dt)
        elif not self.enemies:
            self._complete_wave()

    def _spawn_step(self, dt):
        self.spawn_timer -= dt
        if self.spawn_timer > 0 or len(self.enemies) >= cfg.MAX_ENEMIES_ALIVE:
            return
        self.enemies.add(Enemy(self._pick_spawn_point(), self.wave))
        self.enemies_to_spawn -= 1
        self.spawn_timer = cfg.SPAWN_INTERVAL

    def _pick_spawn_point(self):
        rect = cfg.ARENA_RECT
        point = pygame.Vector2(rect.topleft)
        for _ in range(cfg.SPAWN_ATTEMPTS):
            x = random.randint(rect.left, rect.right)
            y = random.randint(rect.top, rect.bottom)
            point = pygame.Vector2(random.choice([
                (x, rect.top), (x, rect.bottom),
                (rect.left, y), (rect.right, y),
            ]))
            if point.distance_to(self.player.pos) >= cfg.SPAWN_MIN_DISTANCE:
                break
        return point

    def _complete_wave(self):
        self.score += cfg.SCORE_WAVE_CLEAR
        if self.wave >= cfg.FINAL_WAVE:
            self._finish(won=True)
            return
        self.wave += 1
        self.player.heal(cfg.WAVE_CLEAR_HEAL)
        self.break_timer = cfg.WAVE_BREAK_TIME

    def _finish(self, won):
        self.game.states.change(
            StateId.GAME_OVER, score=self.score, wave=self.wave, won=won
        )
