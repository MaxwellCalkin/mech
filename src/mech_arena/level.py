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


def rects_collide(a: Any, b: Any) -> bool:
    """Return ``True`` if two rect-like objects overlap."""
    if pygame is None:
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by
    return a.colliderect(b)


@dataclass
class Level:
    name: str
    description: str
    player: Player
    enemies: List[Enemy] = field(default_factory=list)

    def start(self) -> None:
        print(f"Starting level: {self.name}")

    def update(self) -> None:
        for enemy in self.enemies:
            enemy.update(self.player)
            if rects_collide(enemy.rect, self.player.rect):
                self.player.take_damage(1)

    def draw(self, surface: Any) -> None:
        if pygame is None:
            return
        pygame.draw.rect(surface, (0, 255, 0), self.player.rect)
        for enemy in self.enemies:
            pygame.draw.rect(surface, (255, 0, 0), enemy.rect)
