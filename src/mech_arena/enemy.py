"""Enemy logic with simple behaviour and interpretability metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:  # pragma: no cover - pygame may not be installed during unit tests
    import pygame
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None  # type: ignore[assignment]

from .player import Player


@dataclass
class Enemy:
    """Enemy entity that drifts toward the player."""

    x: float
    y: float
    topic: str
    summary: str
    speed: float = 110.0
    size: int = 32
    health: int = 3
    damage: int = 1
    colour: tuple[int, int, int] = (244, 96, 137)

    def update(self, player: Player, dt: float) -> None:
        """Move toward the player's current position."""
        dx = player.x - self.x
        dy = player.y - self.y
        distance = (dx**2 + dy**2) ** 0.5 or 1.0
        self.x += (dx / distance) * self.speed * dt
        self.y += (dy / distance) * self.speed * dt

    def take_damage(self, amount: int) -> None:
        """Reduce the enemy's health."""
        self.health = max(0, self.health - amount)

    @property
    def rect(self) -> Any:
        if pygame is None:
            return (self.x, self.y, self.size, self.size)
        return pygame.Rect(self.x, self.y, self.size, self.size)
