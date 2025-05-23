"""Enemy logic with simple homing behavior."""

from dataclasses import dataclass
from typing import Any

try:
    import pygame
except Exception:  # pragma: no cover - pygame may not be installed
    pygame = None

from .player import Player


@dataclass
class Enemy:
    """Very simple enemy that moves toward the player."""

    x: int
    y: int
    speed: int = 2
    size: int = 30

    def update(self, player: Player) -> None:
        if player.x > self.x:
            self.x += self.speed
        elif player.x < self.x:
            self.x -= self.speed

        if player.y > self.y:
            self.y += self.speed
        elif player.y < self.y:
            self.y -= self.speed

    @property
    def rect(self) -> Any:
        if pygame is None:
            return (self.x, self.y, self.size, self.size)
        return pygame.Rect(self.x, self.y, self.size, self.size)
