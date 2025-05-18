"""Player character logic."""

from dataclasses import dataclass
from typing import Any

try:
    import pygame
except Exception:  # pragma: no cover - pygame may not be installed
    pygame = None


@dataclass
class Player:
    """Represents the user's mech on screen."""

    x: int
    y: int
    speed: int = 5
    size: int = 40
    health: int = 3

    def move(self, dx: int, dy: int) -> None:
        """Move the player by ``dx`` and ``dy`` units."""
        self.x += dx * self.speed
        self.y += dy * self.speed

    def take_damage(self, amount: int = 1) -> None:
        """Reduce the player's health by ``amount``."""
        self.health = max(0, self.health - amount)

    @property
    def rect(self) -> Any:
        if pygame is None:
            return (self.x, self.y, self.size, self.size)
        return pygame.Rect(self.x, self.y, self.size, self.size)
