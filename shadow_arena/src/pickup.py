"""Health pickup dropped by defeated enemies."""
import pygame

import settings as cfg


class HealPickup(pygame.sprite.Sprite):
    """Restores HP when the player touches it; disappears over time."""

    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface(cfg.PICKUP_SIZE)
        self.image.fill(cfg.COLOR_PICKUP)
        self.rect = self.image.get_rect(center=position)
        self.lifetime = cfg.PICKUP_LIFETIME

    def update(self, dt):
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.kill()
