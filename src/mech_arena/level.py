"""Game level containing the player, enemies, and interpretability overlay."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, Iterable, List, Tuple

try:  # pragma: no cover - pygame is optional for tests
    import pygame
except Exception:  # pragma: no cover - fallback when pygame is missing
    pygame = None  # type: ignore[assignment]

from .enemy import Enemy
from .player import Player
from .projectile import Projectile


def rects_collide(a: Any, b: Any) -> bool:
    """Return ``True`` if two rect-like objects overlap."""
    if pygame is None:
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by
    return a.colliderect(b)


@dataclass
class Insight:
    """Collectible that teaches the player an interpretability concept."""

    title: str
    body: str
    x: float
    y: float
    radius: int = 18
    colour: Tuple[int, int, int] = (120, 255, 180)
    collected: bool = False

    @property
    def rect(self) -> Any:
        diameter = self.radius * 2
        if pygame is None:
            return (self.x - self.radius, self.y - self.radius, diameter, diameter)
        return pygame.Rect(
            self.x - self.radius, self.y - self.radius, diameter, diameter
        )


DEFAULT_KNOWLEDGE: Dict[str, str] = {
    "Residual Stream": "Residual connections keep information flowing forward so that"
    " attention and MLPs can remix context without forgetting earlier tokens.",
    "Induction Head": "A pattern-matching attention head that copies the next token in a"
    " repeated sequence—often the first structure people reverse-engineer.",
    "Circuit Breaker": "A bundle of neurons whose joint activation implements a behaviour;"
    " tracing it explains how features combine.",
}


@dataclass
class Level:
    name: str
    description: str
    player: Player
    width: int = 960
    height: int = 600
    enemies: List[Enemy] = field(default_factory=list)
    knowledge_base: Dict[str, str] = field(default_factory=dict)
    projectiles: List[Projectile] = field(default_factory=list, init=False)
    insights: List[Insight] = field(default_factory=list, init=False)
    knowledge_log: List[Tuple[str, str]] = field(default_factory=list, init=False)
    messages: Deque[str] = field(default_factory=lambda: deque(maxlen=6), init=False)
    scan_timer: float = 0.0
    objective: str = "Stabilise the residual stream"
    background: Tuple[int, int, int] = (18, 20, 40)

    def __post_init__(self) -> None:
        if not self.knowledge_base:
            self.knowledge_base = dict(DEFAULT_KNOWLEDGE)
        self.add_message(f"Entering {self.name}: {self.description}")

    # ------------------------------------------------------------------
    # Update & simulation helpers
    # ------------------------------------------------------------------
    def update(
        self,
        dt: float = 1 / 60,
        move: Tuple[float, float] = (0.0, 0.0),
        fire_target: Tuple[float, float] | None = None,
        trigger_scan: bool = False,
    ) -> None:
        """Advance the simulation by ``dt`` seconds."""
        self.player.move(*move, dt=dt)
        self.player.clamp_to_bounds(self.width - 280, self.height)
        self.player.update(dt)

        if trigger_scan and self.player.consume_scan_energy():
            self.scan_timer = 2.5
            self.add_message("Scan pulse: latent connections highlighted.")
        else:
            self.scan_timer = max(0.0, self.scan_timer - dt)

        if fire_target is not None:
            projectile = self.player.try_fire(fire_target)
            if projectile is not None:
                self.projectiles.append(projectile)

        self._update_projectiles(dt)
        self._update_enemies(dt)
        self._check_insight_collection()

    def _update_projectiles(self, dt: float) -> None:
        remaining: List[Projectile] = []
        for projectile in self.projectiles:
            projectile.update(dt)
            if not projectile.alive:
                continue
            if not self._inside_bounds(projectile.x, projectile.y):
                continue
            hit_enemy = False
            for enemy in self.enemies:
                if rects_collide(projectile.rect, enemy.rect):
                    enemy.take_damage(projectile.damage)
                    hit_enemy = True
                    if enemy.health <= 0:
                        self._handle_enemy_defeated(enemy)
                    break
            if not hit_enemy:
                remaining.append(projectile)
        self.projectiles = remaining

    def _update_enemies(self, dt: float) -> None:
        remaining: List[Enemy] = []
        slow_factor = 0.35 if self.scan_timer > 0.0 else 1.0
        for enemy in self.enemies:
            if enemy.health <= 0:
                continue
            enemy.update(self.player, dt * slow_factor)
            if rects_collide(enemy.rect, self.player.rect):
                self.player.take_damage(enemy.damage)
                self.add_message(f"Warning: {enemy.topic} inflicted damage!")
            if enemy.health > 0:
                remaining.append(enemy)
        self.enemies = remaining

    def _check_insight_collection(self) -> None:
        for insight in self.insights:
            if not insight.collected and rects_collide(insight.rect, self.player.rect):
                insight.collected = True
                self.knowledge_log.append((insight.title, insight.body))
                self.add_message(f"Insight logged: {insight.title}")
        self.insights = [ins for ins in self.insights if not ins.collected]

    def _handle_enemy_defeated(self, enemy: Enemy) -> None:
        summary = self.knowledge_base.get(enemy.topic, enemy.summary)
        insight = Insight(
            title=enemy.topic,
            body=summary,
            x=enemy.x + enemy.size / 2,
            y=enemy.y + enemy.size / 2,
        )
        self.insights.append(insight)
        self.add_message(f"Subsystem neutralised: {enemy.topic}")

    def _inside_bounds(self, x: float, y: float) -> bool:
        return 0 <= x <= self.width - 280 and 0 <= y <= self.height

    def add_message(self, text: str) -> None:
        self.messages.appendleft(text)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def draw(
        self, surface: Any, font: Any | None = None
    ) -> None:  # pragma: no cover - UI
        if pygame is None:
            return
        width, height = surface.get_size()
        arena_width = max(0, width - 280)
        overlay_x = arena_width

        surface.fill(self.background)
        self._draw_grid(surface, arena_width, height)
        self._draw_insights(surface)
        self._draw_projectiles(surface)
        self._draw_enemies(surface)
        self._draw_player(surface)
        if self.scan_timer > 0.0:
            self._draw_scan_overlay(surface, arena_width, height)
        self._draw_hud(surface, font, overlay_x, height)

    def _draw_grid(self, surface: Any, arena_width: int, height: int) -> None:
        if pygame is None:
            return
        grid_colour = (40, 45, 70)
        for x in range(0, arena_width, 40):
            pygame.draw.line(surface, grid_colour, (x, 0), (x, height))
        for y in range(0, height, 40):
            pygame.draw.line(surface, grid_colour, (0, y), (arena_width, y))

    def _draw_player(self, surface: Any) -> None:
        if pygame is None:
            return
        pygame.draw.rect(surface, (120, 200, 255), self.player.rect, border_radius=6)

    def _draw_enemies(self, surface: Any) -> None:
        if pygame is None:
            return
        for enemy in self.enemies:
            pygame.draw.rect(surface, enemy.colour, enemy.rect, border_radius=6)

    def _draw_projectiles(self, surface: Any) -> None:
        if pygame is None:
            return
        for projectile in self.projectiles:
            pygame.draw.circle(
                surface,
                projectile.color,
                (int(projectile.x), int(projectile.y)),
                projectile.radius,
            )

    def _draw_insights(self, surface: Any) -> None:
        if pygame is None:
            return
        for insight in self.insights:
            pygame.draw.circle(
                surface,
                insight.colour,
                (int(insight.x), int(insight.y)),
                insight.radius,
                width=2,
            )

    def _draw_scan_overlay(self, surface: Any, arena_width: int, height: int) -> None:
        if pygame is None:
            return
        overlay = pygame.Surface((arena_width, height), pygame.SRCALPHA)
        alpha = int(120 * (self.scan_timer / 2.5))
        overlay.fill((80, 200, 255, max(40, alpha)))
        surface.blit(overlay, (0, 0))
        player_center = (
            int(self.player.x + self.player.size / 2),
            int(self.player.y + self.player.size / 2),
        )
        for enemy in self.enemies:
            enemy_center = (
                int(enemy.x + enemy.size / 2),
                int(enemy.y + enemy.size / 2),
            )
            pygame.draw.line(surface, (160, 255, 200), player_center, enemy_center, 2)

    def _draw_hud(
        self, surface: Any, font: Any | None, overlay_x: int, height: int
    ) -> None:
        if pygame is None:
            return
        panel_rect = pygame.Rect(overlay_x, 0, surface.get_width() - overlay_x, height)
        pygame.draw.rect(surface, (12, 13, 24), panel_rect)
        if font is None:
            font = pygame.font.SysFont("Fira Code", 16)
        text_y = 12
        text_y = self._draw_wrapped_text(
            surface, font, panel_rect.x + 12, text_y, f"{self.name}\n{self.description}"
        )
        text_y = self._draw_wrapped_text(
            surface,
            font,
            panel_rect.x + 12,
            text_y + 12,
            f"Objective: {self.objective}",
            (180, 200, 255),
        )
        text_y += 8
        text_y = self._draw_section(
            surface, font, panel_rect.x + 12, text_y, "Messages", self.messages
        )
        text_y = self._draw_section(
            surface,
            font,
            panel_rect.x + 12,
            text_y,
            "Insights Logged",
            (f"{title}: {body}" for title, body in self.knowledge_log[-4:]),
        )
        stats = f"Health: {self.player.health}\nEnergy: {int(self.player.energy)}/{int(self.player.max_energy)}"
        self._draw_wrapped_text(surface, font, panel_rect.x + 12, height - 64, stats)

    def _draw_section(
        self,
        surface: Any,
        font: Any,
        x: int,
        y: int,
        title: str,
        lines: Iterable[str],
    ) -> int:
        title_colour = (255, 198, 109)
        y = self._draw_wrapped_text(surface, font, x, y, title, title_colour)
        for line in lines:
            y = self._draw_wrapped_text(
                surface, font, x, y, f"- {line}", (210, 210, 240)
            )
        return y + 8

    def _draw_wrapped_text(
        self,
        surface: Any,
        font: Any,
        x: int,
        y: int,
        text: str,
        colour: Tuple[int, int, int] = (230, 230, 255),
        max_width: int = 240,
    ) -> int:
        if pygame is None:
            return y
        lines = self._wrap_text(font, text, max_width)
        for line in lines:
            rendered = font.render(line, True, colour)
            surface.blit(rendered, (x, y))
            y += rendered.get_height() + 2
        return y

    def _wrap_text(self, font: Any, text: str, max_width: int) -> List[str]:
        if pygame is None:
            return [text]
        words = text.replace("\n", " \n ").split()
        lines: List[str] = []
        current = ""
        for word in words:
            if word == "\n":
                lines.append(current.rstrip())
                current = ""
                continue
            trial = f"{current} {word}".strip()
            if current and font.size(trial)[0] > max_width:
                lines.append(current.rstrip())
                current = word
            else:
                current = trial
        if current:
            lines.append(current.rstrip())
        return lines or [""]
