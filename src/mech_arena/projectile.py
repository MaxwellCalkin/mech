"""Projectile logic for the player's interpretability pulses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple

try:  # pragma: no cover - pygame might be unavailable during unit tests
    import pygame
except Exception:  # pragma: no cover - fallback for headless testing
    pygame = None  # type: ignore[assignment]


@dataclass
class Projectile:
    """Represents a projectile fired by the player."""

    x: float
    y: float
    velocity: Tuple[float, float]
    speed: float = 420.0
    radius: int = 6
    damage: int = 1
    lifetime: float = 1.5
    color: Tuple[int, int, int] = (120, 220, 255)

    def update(self, dt: float) -> None:
        """Advance the projectile forward and tick down its lifetime."""
        vx, vy = self.velocity
        self.x += vx * self.speed * dt
        self.y += vy * self.speed * dt
        self.lifetime -= dt

    @property
    def alive(self) -> bool:
        """Return ``True`` while the projectile should remain active."""
        return self.lifetime > 0

    @property
    def rect(self) -> Any:
        """Return a rect-like object for collision checks."""
        diameter = self.radius * 2
        if pygame is None:
            return (self.x - self.radius, self.y - self.radius, diameter, diameter)
        return pygame.Rect(
            self.x - self.radius, self.y - self.radius, diameter, diameter
        )
