"""Player character logic for the interpretability mech."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Tuple

try:  # pragma: no cover - pygame may be unavailable during headless tests
    import pygame
except Exception:  # pragma: no cover - degrade gracefully without pygame
    pygame = None  # type: ignore[assignment]

from .projectile import Projectile


@dataclass
class Player:
    """Represents the user's mech on screen."""

    x: float
    y: float
    speed: float = 260.0
    size: int = 40
    health: int = 5
    max_energy: float = 100.0
    energy: float = 100.0
    fire_cooldown: float = 0.25
    energy_regen: float = 18.0
    fire_cost: float = 12.0
    scan_cost: float = 25.0
    invulnerability: float = 0.0
    _cooldown_timer: float = field(default=0.0, init=False, repr=False)

    def move(self, dx: float, dy: float, dt: float = 1.0) -> None:
        """Move the player by ``dx`` and ``dy`` units over ``dt`` seconds."""
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt

    def update(self, dt: float) -> None:
        """Handle regeneration and cooldown timers."""
        self._cooldown_timer = max(0.0, self._cooldown_timer - dt)
        self.invulnerability = max(0.0, self.invulnerability - dt)
        self.energy = min(self.max_energy, self.energy + self.energy_regen * dt)

    def take_damage(self, amount: int = 1) -> None:
        """Reduce the player's health by ``amount`` if not invulnerable."""
        if self.invulnerability > 0.0:
            return
        self.health = max(0, self.health - amount)
        self.invulnerability = 0.5

    def try_fire(self, target: Tuple[float, float]) -> Projectile | None:
        """Attempt to fire a projectile toward ``target``."""
        if self._cooldown_timer > 0.0 or self.energy < self.fire_cost:
            return None
        tx, ty = target
        dx = tx - (self.x + self.size / 2)
        dy = ty - (self.y + self.size / 2)
        magnitude = (dx**2 + dy**2) ** 0.5 or 1.0
        direction = (dx / magnitude, dy / magnitude)
        self._cooldown_timer = self.fire_cooldown
        self.energy -= self.fire_cost
        return Projectile(
            x=self.x + self.size / 2, y=self.y + self.size / 2, velocity=direction
        )

    def consume_scan_energy(self) -> bool:
        """Spend energy to trigger a scan pulse."""
        if self.energy < self.scan_cost:
            return False
        self.energy -= self.scan_cost
        return True

    def clamp_to_bounds(self, width: int, height: int) -> None:
        """Keep the player inside the arena bounds."""
        self.x = max(0, min(self.x, width - self.size))
        self.y = max(0, min(self.y, height - self.size))

    @property
    def center(self) -> Tuple[float, float]:
        """Return the centre of the player's sprite."""
        return (self.x + self.size / 2, self.y + self.size / 2)

    @property
    def rect(self) -> Any:
        if pygame is None:
            return (self.x, self.y, self.size, self.size)
        return pygame.Rect(self.x, self.y, self.size, self.size)
