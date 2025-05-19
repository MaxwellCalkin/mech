"""Game level containing the player and enemies."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Any

try:
    import pygame
except Exception:  # pragma: no cover - pygame may not be installed
    pygame = None

from .enemy import Enemy
from .player import Player
from .utils import rects_collide


@dataclass
class Level:
    name: str
    description: str
    player: Player
    enemies: List[Enemy] = field(default_factory=list)

    def start(self) -> None:
        print(f"Starting level: {self.name}")

    def update(self) -> None:
        for enemy in list(self.enemies):
            enemy.update(self.player)
            if rects_collide(self.player.rect, enemy.rect):
                self.player.take_damage(10)
                enemy.take_damage(10)
            if not enemy.alive:
                self.enemies.remove(enemy)

    def draw(self, surface: Any) -> None:
        if pygame is None:
            return
        pygame.draw.rect(surface, (0, 255, 0), self.player.rect)
        for enemy in self.enemies:
            pygame.draw.rect(surface, (255, 0, 0), enemy.rect)
