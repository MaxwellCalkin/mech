"""Enemy logic with behaviour tied to interpretability concepts."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

try:  # pragma: no cover - pygame may not be installed during unit tests
    import pygame
except Exception:  # pragma: no cover - allow running tests without pygame
    pygame = None  # type: ignore[assignment]

if False:  # pragma: no cover - type checking only
    from .level import Level

from .player import Player


def _distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


@dataclass
class Enemy:
    """Enemy entity whose behaviour reflects its underlying circuit."""

    x: float
    y: float
    topic: str
    summary: str
    speed: float = 110.0
    size: int = 32
    health: int = 3
    damage: int = 1
    colour: tuple[int, int, int] = (244, 96, 137)
    archetype: str | None = None
    support_charge: float = field(default=0.0, init=False)
    activation: float = field(default=0.0, init=False)
    ablated: bool = field(default=False, init=False)
    induction_index: int = field(default=0, init=False)
    circuit_charge: float = field(default=0.0, init=False)
    analysis_notes: Dict[str, str] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        if self.archetype is None:
            self.archetype = self.topic

    # ------------------------------------------------------------------
    # Core behaviour
    # ------------------------------------------------------------------
    def update(self, level: "Level", dt: float) -> None:
        """Advance the enemy based on its interpretability role."""

        self.support_charge = max(0.0, self.support_charge - dt * 0.4)
        self.activation = max(0.0, self.activation - dt * 0.6)
        self.analysis_notes.clear()

        if self.ablated:
            self.activation = max(0.0, self.activation - dt * 2)
            return

        archetype = (self.archetype or self.topic).lower()
        if "residual" in archetype:
            self._update_residual(level, dt)
        elif "induction" in archetype:
            self._update_induction(level, dt)
        elif "circuit" in archetype or "breaker" in archetype:
            self._update_circuit(level, dt)
        else:
            self._drift_toward(level.player, dt)

    def _drift_toward(
        self, player: Player, dt: float, speed_scale: float = 1.0
    ) -> None:
        dx = player.x - self.x
        dy = player.y - self.y
        distance = math.hypot(dx, dy) or 1.0
        velocity = self.speed * (1.0 + 0.65 * self.support_charge) * speed_scale
        self.x += (dx / distance) * velocity * dt
        self.y += (dy / distance) * velocity * dt

    # ------------------------------------------------------------------
    # Behaviour specialisations
    # ------------------------------------------------------------------
    def _update_residual(self, level: "Level", dt: float) -> None:
        player = level.player
        allies = [ally for ally in level.living_enemies if ally is not self]
        if allies:
            avg_x = sum(ally.x for ally in allies) / len(allies)
            avg_y = sum(ally.y for ally in allies) / len(allies)
            target = ((player.x + avg_x) / 2, (player.y + avg_y) / 2)
        else:
            target = (player.x, player.y)
        self._move_towards(target, dt, speed_scale=0.75)

        for ally in allies:
            dist = _distance(self.center, ally.center)
            if dist < 260:
                ally.receive_support(0.6 * dt)
                level.register_link(
                    self, ally, intensity=_clamp(1.0 - dist / 260, 0.2, 1.0)
                )
                level.analysis_tags["residual_linking"] = True
        if allies:
            self.analysis_notes["Links"] = str(len(allies))
        self.analysis_notes["Support"] = f"{self.support_charge:.1f}"
        self.activation = _clamp(self.activation + 0.8 * dt, 0.0, 1.5)
        self.analysis_notes["Role"] = "Buffering allied activations"

    def _update_induction(self, level: "Level", dt: float) -> None:
        marker = level.token_marker_for(self.induction_index)
        self.analysis_notes["Predicting"] = marker.label
        self.analysis_notes["Step"] = (
            f"{self.induction_index + 1}/{level.token_cycle_length}"
        )
        target = marker.position
        self._move_towards(target, dt, speed_scale=1.05)
        level.register_prediction(self, marker)
        if _distance(self.center, target) < marker.radius + self.size * 0.25:
            self.induction_index = (self.induction_index + 1) % level.token_cycle_length
            level.analysis_tags["induction_prediction"] = True
        self.activation = _clamp(self.activation + 0.7 * dt, 0.0, 1.2)

    def _update_circuit(self, level: "Level", dt: float) -> None:
        player = level.player
        allies = [ally for ally in level.living_enemies if ally is not self]
        if allies:
            focus = min(allies, key=lambda ally: _distance(self.center, ally.center))
            target = ((focus.x + player.x) / 2, (focus.y + player.y) / 2)
            dist = _distance(self.center, focus.center)
            if dist < 220:
                self.circuit_charge += dt
                intensity = _clamp(1.0 - dist / 220, 0.2, 1.0)
                level.register_link(
                    self, focus, intensity=intensity, colour=(255, 150, 120)
                )
                level.analysis_tags["circuit_chain"] = True
                if self.circuit_charge > 2.4:
                    level.trigger_circuit_burst(self, focus)
                    self.circuit_charge = 0.0
            else:
                self.circuit_charge = max(0.0, self.circuit_charge - dt)
        else:
            target = (player.x, player.y)

        self._move_towards(target, dt, speed_scale=0.9)
        self.activation = _clamp(
            self.activation + (self.circuit_charge + 0.2) * dt, 0.0, 1.5
        )
        self.analysis_notes["Charge"] = f"{self.circuit_charge:0.1f}s"

    def _move_towards(
        self, target: Tuple[float, float], dt: float, speed_scale: float = 1.0
    ) -> None:
        tx, ty = target
        dx = tx - self.x
        dy = ty - self.y
        distance = math.hypot(dx, dy) or 1.0
        velocity = self.speed * (1.0 + 0.65 * self.support_charge) * speed_scale
        self.x += (dx / distance) * velocity * dt
        self.y += (dy / distance) * velocity * dt

    # ------------------------------------------------------------------
    # Combat helpers
    # ------------------------------------------------------------------
    def take_damage(self, amount: int) -> None:
        """Reduce the enemy's health."""
        self.health = max(0, self.health - amount)

    def receive_support(self, strength: float) -> None:
        self.support_charge = _clamp(self.support_charge + strength, 0.0, 2.0)

    def toggle_ablation(self) -> None:
        self.ablated = not self.ablated
        if self.ablated:
            self.activation = 0.0

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------
    @property
    def center(self) -> Tuple[float, float]:
        return (self.x + self.size / 2, self.y + self.size / 2)

    @property
    def rect(self) -> Any:
        if pygame is None:
            return (self.x, self.y, self.size, self.size)
        return pygame.Rect(self.x, self.y, self.size, self.size)
