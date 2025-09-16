"""Game level containing the player, enemies, and interpretability overlay."""

from __future__ import annotations

import math
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, Iterable, List, Tuple

try:  # pragma: no cover - pygame is optional for tests
    import pygame
except Exception:  # pragma: no cover - fallback when pygame is missing
    pygame = None  # type: ignore[assignment]

from .enemy import Enemy
from .player import Player
from .progression import ResearchJournal
from .projectile import Projectile
from .tasks import ResearchTask, build_tasks_for


@dataclass
class TokenMarker:
    """Represents a token in a repeating induction pattern."""

    label: str
    anchor: Tuple[float, float]
    orbit_radius: float = 110.0
    phase_offset: float = 0.0
    speed: float = 0.35
    radius: float = 12.0
    colour: Tuple[int, int, int] = (140, 210, 255)
    glow_colour: Tuple[int, int, int] = (30, 60, 120)
    position: Tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))

    def update(self, clock: float) -> None:
        angle = (clock * self.speed + self.phase_offset) * 2 * math.pi
        ox = math.cos(angle) * self.orbit_radius
        oy = math.sin(angle) * self.orbit_radius * 0.55
        self.position = (self.anchor[0] + ox, self.anchor[1] + oy)


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
    "Residual Stream": (
        "Residual connections keep information flowing so attention and MLP layers "
        "can remix context without erasing earlier evidence. Watch how allied stats "
        "collapse when you ablate this stream."
    ),
    "Induction Head": (
        "Pattern-matching heads learn to copy the next token in repeated sequences. "
        "Scanning reveals the beads of the sequence and how the head anticipates "
        "its next target."
    ),
    "Circuit Breaker": (
        "Bundles of neurons can interlock like a breaker circuit, firing only when "
        "multiple pathways light up. When charged, they can cascade energy into "
        "neighbours—unless you intervene."
    ),
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
    coaching_tips: Deque[str] = field(
        default_factory=lambda: deque(maxlen=3), init=False
    )
    scan_timer: float = 0.0
    objective: str = "Stabilise the residual stream"
    background: Tuple[int, int, int] = (18, 20, 40)
    research_journal: ResearchJournal = field(default_factory=ResearchJournal.load)
    active_tasks: List[ResearchTask] = field(default_factory=list, init=False)
    completed_tasks: List[ResearchTask] = field(default_factory=list, init=False)
    analysis_links: List[
        Tuple[Tuple[float, float], Tuple[float, float], Tuple[int, int, int], float]
    ] = field(default_factory=list, init=False)
    analysis_predictions: List[Tuple[Tuple[float, float], TokenMarker]] = field(
        default_factory=list, init=False
    )
    analysis_tags: Dict[str, bool] = field(default_factory=dict, init=False)
    token_markers: List[TokenMarker] = field(default_factory=list, init=False)
    token_clock: float = field(default=0.0, init=False)
    journal_dirty: bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if not self.knowledge_base:
            self.knowledge_base = dict(DEFAULT_KNOWLEDGE)
        self._init_token_markers()
        self._seed_coaching_tips()
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
        analysis_commands: Iterable[Tuple[str, int]] = (),
    ) -> None:
        """Advance the simulation by ``dt`` seconds."""
        self.token_clock += dt
        for marker in self.token_markers:
            marker.update(self.token_clock)
        self.analysis_links.clear()
        self.analysis_predictions.clear()
        self.analysis_tags.clear()

        self.player.move(*move, dt=dt)
        self.player.clamp_to_bounds(self.width - 280, self.height)
        self.player.update(dt)

        if trigger_scan and self.player.consume_scan_energy():
            self.scan_timer = 3.0
            self.add_message("Scan pulse: latent topology slowed for analysis.")
        else:
            self.scan_timer = max(0.0, self.scan_timer - dt)

        for command in analysis_commands:
            self._handle_analysis_command(command)

        if fire_target is not None:
            projectile = self.player.try_fire(fire_target)
            if projectile is not None:
                self.projectiles.append(projectile)

        self._update_projectiles(dt)
        self._update_enemies(dt)
        self._check_insight_collection()
        self._update_tasks()
        if self.journal_dirty:
            self.research_journal.save()
            self.journal_dirty = False

    def _init_token_markers(self) -> None:
        if self.token_markers:
            return
        anchor = (self.width * 0.35, self.height * 0.45)
        phases = [0.0, 0.33, 0.66]
        labels = ["A", "B", "C"]
        for phase, label in zip(phases, labels):
            marker = TokenMarker(
                label=label,
                anchor=anchor,
                orbit_radius=130.0,
                phase_offset=phase,
                speed=0.28,
                radius=14.0,
            )
            marker.update(self.token_clock)
            self.token_markers.append(marker)

    def _seed_coaching_tips(self) -> None:
        self.coaching_tips.clear()
        self.coaching_tips.append(
            "Tab: pause the fray and surface hidden residual links."
        )
        self.coaching_tips.append(
            "Number keys: ablate a subsystem while the scan overlay is active."
        )
        self.coaching_tips.append(
            "Shift + number: patch energy back in to observe recovery dynamics."
        )

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
            enemy.update(self, dt * slow_factor)
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
                self.research_journal.log_insight(insight.title, insight.body)
                self.journal_dirty = True
                self._activate_tasks(insight.title)
                next_task = self._next_task_for(insight.title)
                if next_task and next_task.tip:
                    self.add_coaching_tip(next_task.tip)
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
        self.add_coaching_tip(
            f"Collect the {enemy.topic} insight to unlock deeper experiments."
        )

    def _inside_bounds(self, x: float, y: float) -> bool:
        return 0 <= x <= self.width - 280 and 0 <= y <= self.height

    def add_message(self, text: str) -> None:
        self.messages.appendleft(text)

    def add_coaching_tip(self, text: str) -> None:
        if text in self.coaching_tips:
            return
        self.coaching_tips.appendleft(text)

    def _handle_analysis_command(self, command: Tuple[str, int]) -> None:
        if not command:
            return
        action, index = command
        enemy = self._enemy_by_analysis_index(index)
        if enemy is None:
            return
        if action == "toggle_ablation":
            if self.scan_timer <= 0.0:
                self.add_message("Initiate a scan to run ablation experiments.")
                return
            enemy.toggle_ablation()
            state = "ablated" if enemy.ablated else "restored"
            self.add_message(f"{enemy.topic} {state} for analysis.")
            tag = self._analysis_tag_key(enemy.topic, "ablation")
            if enemy.ablated and tag:
                self.analysis_tags[tag] = True
                self.journal_dirty = True
        elif action == "pulse_patch":
            if self.scan_timer <= 0.0:
                self.add_message("Need an active scan to patch activations.")
                return
            enemy.ablated = False
            enemy.receive_support(0.8)
            enemy.activation = min(enemy.activation + 0.5, 1.5)
            self.add_message(f"Injected synthetic activation into {enemy.topic}.")
            tag = self._analysis_tag_key(enemy.topic, "patch")
            if tag:
                self.analysis_tags[tag] = True

    def _analysis_tag_key(self, topic: str, action: str) -> str | None:
        lookup = {
            ("Residual Stream", "ablation"): "residual_ablation",
            ("Induction Head", "ablation"): "induction_ablation",
            ("Circuit Breaker", "ablation"): "circuit_ablation",
            ("Residual Stream", "patch"): "residual_patch",
            ("Induction Head", "patch"): "induction_patch",
            ("Circuit Breaker", "patch"): "circuit_patch",
        }
        return lookup.get((topic, action))

    def register_link(
        self,
        source: Enemy,
        target: Enemy,
        intensity: float,
        colour: Tuple[int, int, int] | None = None,
    ) -> None:
        if self.scan_timer <= 0.0:
            return
        if colour is None:
            colour = (160, 255, 200)
        self.analysis_links.append((source.center, target.center, colour, intensity))

    def register_prediction(self, enemy: Enemy, marker: TokenMarker) -> None:
        if self.scan_timer <= 0.0:
            return
        self.analysis_predictions.append((enemy.center, marker))

    def trigger_circuit_burst(self, enemy: Enemy, partner: Enemy) -> None:
        player_centre = self.player.center
        enemy_centre = enemy.center
        distance = math.hypot(
            player_centre[0] - enemy_centre[0], player_centre[1] - enemy_centre[1]
        )
        if distance < 140:
            self.player.take_damage(1)
            self.add_message(
                "Circuit breaker overload rattled the hull! Study the chain."
            )
        else:
            self.add_message("Circuit breaker discharged; note the suppressed allies.")
        self.analysis_tags["circuit_chain"] = True

    def _activate_tasks(self, concept: str) -> None:
        existing_ids = {task.identifier for task in self.active_tasks}
        for task in build_tasks_for(concept):
            if task.identifier in existing_ids:
                continue
            if task.identifier in self.research_journal.tasks_for(concept):
                task.completed = True
            if self.research_journal.is_mastered(concept):
                task.completed = True
            self.active_tasks.append(task)
            if task.requires_scan:
                self.add_coaching_tip(
                    "Use scan mode to gather data for research tasks."
                )

    def _next_task_for(self, concept: str) -> ResearchTask | None:
        for task in self.active_tasks:
            if task.concept == concept and not task.completed:
                return task
        return None

    def _update_tasks(self) -> None:
        progress_made = False
        for task in self.active_tasks:
            if task.evaluate(self):
                self.research_journal.mark_task_completed(task.concept, task.identifier)
                self.add_message(f"Research breakthrough: {task.description}")
                self.completed_tasks.append(task)
                self.journal_dirty = True
                progress_made = True
        if progress_made:
            for concept in {task.concept for task in self.active_tasks}:
                concept_tasks = [t for t in self.active_tasks if t.concept == concept]
                if concept_tasks and all(t.completed for t in concept_tasks):
                    if not self.research_journal.is_mastered(concept):
                        self.research_journal.mark_mastered(concept)
                        self.journal_dirty = True
                        self.add_message(f"Concept mastered: {concept}")

    def _enemy_by_analysis_index(self, index: int) -> Enemy | None:
        living = sorted(self.living_enemies, key=lambda e: e.topic)
        if 0 <= index < len(living):
            return living[index]
        return None

    def token_marker_for(self, index: int) -> TokenMarker:
        if not self.token_markers:
            self._init_token_markers()
        if not self.token_markers:
            raise ValueError("Token markers not initialised")
        return self.token_markers[index % len(self.token_markers)]

    @property
    def token_cycle_length(self) -> int:
        return max(1, len(self.token_markers))

    @property
    def living_enemies(self) -> List[Enemy]:
        return [enemy for enemy in self.enemies if enemy.health > 0]

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
        self._draw_backdrop(surface, arena_width, height)
        self._draw_grid(surface, arena_width, height)
        self._draw_token_stream(surface, font)
        self._draw_insights(surface)
        self._draw_projectiles(surface)
        self._draw_enemies(surface)
        self._draw_player(surface)
        if self.scan_timer > 0.0:
            self._draw_scan_overlay(surface, arena_width, height, font)
        self._draw_hud(surface, font, overlay_x, height)

    def _draw_backdrop(self, surface: Any, arena_width: int, height: int) -> None:
        if pygame is None:
            return
        cache = getattr(self, "_backdrop_cache", None)
        if cache is None or cache.get_size() != (arena_width, height):
            cache = pygame.Surface((arena_width, height))
            for y in range(height):
                ratio = y / max(1, height - 1)
                r = int(18 + 45 * ratio)
                g = int(20 + 70 * ratio)
                b = int(40 + 110 * ratio)
                pygame.draw.line(cache, (r, g, b), (0, y), (arena_width, y))
            setattr(self, "_backdrop_cache", cache)
        surface.blit(cache, (0, 0))

    def _draw_grid(self, surface: Any, arena_width: int, height: int) -> None:
        if pygame is None:
            return
        grid_colour = (40, 45, 70)
        for x in range(0, arena_width, 40):
            pygame.draw.line(surface, grid_colour, (x, 0), (x, height))
        for y in range(0, height, 40):
            pygame.draw.line(surface, grid_colour, (0, y), (arena_width, y))

    def _draw_token_stream(self, surface: Any, font: Any | None) -> None:
        if pygame is None:
            return
        if font is None:
            font = pygame.font.SysFont("Fira Code", 16)
        for marker in self.token_markers:
            x, y = marker.position
            center = (int(x), int(y))
            glow_size = int(marker.radius * 3)
            glow_surface = pygame.Surface(
                (glow_size * 2, glow_size * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                glow_surface,
                (*marker.glow_colour, 80 if self.scan_timer > 0 else 40),
                (glow_size, glow_size),
                glow_size,
            )
            pygame.draw.circle(
                glow_surface,
                (*marker.colour, 220),
                (glow_size, glow_size),
                int(marker.radius),
            )
            surface.blit(glow_surface, (center[0] - glow_size, center[1] - glow_size))
            label = font.render(marker.label, True, (230, 245, 255))
            surface.blit(
                label,
                (
                    center[0] - label.get_width() // 2,
                    center[1] - label.get_height() // 2,
                ),
            )

    def _draw_player(self, surface: Any) -> None:
        if pygame is None:
            return
        rect = self.player.rect
        glow = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
        pygame.draw.ellipse(glow, (90, 160, 255, 100), glow.get_rect())
        surface.blit(glow, (rect.x - 10, rect.y - 10))
        pygame.draw.rect(surface, (120, 200, 255), rect, border_radius=12)
        inner = rect.inflate(-12, -12)
        pygame.draw.rect(surface, (28, 40, 70), inner, border_radius=10)
        # Visualise remaining energy as a luminous thruster bar.
        ratio = self.player.energy / max(1.0, self.player.max_energy)
        thruster_width = max(4, int(inner.width * ratio))
        thruster_rect = pygame.Rect(
            inner.x, inner.y + inner.height - 6, thruster_width, 4
        )
        pygame.draw.rect(surface, (120, 255, 220), thruster_rect, border_radius=2)

    def _draw_enemies(self, surface: Any) -> None:
        if pygame is None:
            return
        for enemy in self.enemies:
            rect = enemy.rect
            activation = min(1.5, enemy.activation)
            base = enemy.colour
            tint = (
                min(255, int(base[0] + 90 * activation)),
                min(255, int(base[1] + 70 * activation)),
                min(255, int(base[2] + 70 * activation)),
            )
            if enemy.support_charge > 0.1:
                aura_size = rect.width + 22
                aura = pygame.Surface((aura_size, aura_size), pygame.SRCALPHA)
                pygame.draw.ellipse(
                    aura,
                    (120, 220, 200, int(120 * min(enemy.support_charge, 1.0))),
                    aura.get_rect(),
                )
                surface.blit(aura, (rect.x - 11, rect.y - 11))
            pygame.draw.rect(surface, tint, rect, border_radius=10)
            core = rect.inflate(-12, -12)
            core_colour = (35, 40, 72) if enemy.ablated else (255, 255, 255)
            if enemy.ablated:
                overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                overlay.fill((30, 40, 80, 160))
                surface.blit(overlay, rect.topleft)
                pygame.draw.rect(
                    surface, (200, 220, 255), rect, width=2, border_radius=10
                )
                pygame.draw.rect(surface, core_colour, core, width=2, border_radius=8)
            else:
                pygame.draw.rect(surface, core_colour, core, border_radius=8)
                if enemy.circuit_charge > 0.1:
                    charge_ratio = min(1.0, enemy.circuit_charge / 2.4)
                    charge_height = max(2, int(core.height * charge_ratio))
                    charge_rect = pygame.Rect(
                        core.x + core.width - 6,
                        core.y + core.height - charge_height,
                        4,
                        charge_height,
                    )
                    pygame.draw.rect(surface, (255, 180, 120), charge_rect)

    def _draw_projectiles(self, surface: Any) -> None:
        if pygame is None:
            return
        for projectile in self.projectiles:
            pos = (int(projectile.x), int(projectile.y))
            glow_size = projectile.radius * 3
            glow_surface = pygame.Surface(
                (glow_size * 2, glow_size * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                glow_surface,
                (*projectile.color, 90),
                (glow_size, glow_size),
                glow_size,
            )
            surface.blit(glow_surface, (pos[0] - glow_size, pos[1] - glow_size))
            pygame.draw.circle(surface, projectile.color, pos, projectile.radius)

    def _draw_insights(self, surface: Any) -> None:
        if pygame is None:
            return
        for insight in self.insights:
            pos = (int(insight.x), int(insight.y))
            halo_size = insight.radius * 3
            halo = pygame.Surface((halo_size * 2, halo_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                halo,
                (*insight.colour, 70),
                (halo_size, halo_size),
                halo_size,
            )
            pygame.draw.circle(
                halo,
                (*insight.colour, 180),
                (halo_size, halo_size),
                insight.radius,
                width=3,
            )
            surface.blit(halo, (pos[0] - halo_size, pos[1] - halo_size))

    def _draw_scan_overlay(
        self, surface: Any, arena_width: int, height: int, font: Any | None
    ) -> None:
        if pygame is None:
            return
        overlay = pygame.Surface((arena_width, height), pygame.SRCALPHA)
        alpha = int(140 * (self.scan_timer / 3.0))
        overlay.fill((60, 130, 200, max(60, alpha)))
        surface.blit(overlay, (0, 0))
        player_center = (
            int(self.player.x + self.player.size / 2),
            int(self.player.y + self.player.size / 2),
        )
        pulse = pygame.Surface((arena_width, height), pygame.SRCALPHA)
        pygame.draw.circle(
            pulse,
            (120, 200, 255, 90),
            player_center,
            int(60 + 40 * math.sin(self.scan_timer * 4)),
            width=2,
        )
        surface.blit(pulse, (0, 0))
        for enemy in self.living_enemies:
            enemy_center = (
                int(enemy.x + enemy.size / 2),
                int(enemy.y + enemy.size / 2),
            )
            colour = (255, 170, 180) if enemy.ablated else (160, 255, 200)
            width_line = 1 if enemy.ablated else 2
            pygame.draw.line(surface, colour, player_center, enemy_center, width_line)

        for start, end, colour, intensity in self.analysis_links:
            start_pos = (int(start[0]), int(start[1]))
            end_pos = (int(end[0]), int(end[1]))
            pygame.draw.line(
                surface,
                colour,
                start_pos,
                end_pos,
                max(1, int(3 * intensity)),
            )

        for source, marker in self.analysis_predictions:
            start_pos = (int(source[0]), int(source[1]))
            end_pos = (int(marker.position[0]), int(marker.position[1]))
            pygame.draw.line(surface, (255, 220, 140), start_pos, end_pos, 2)
            pygame.draw.circle(surface, (255, 220, 140), end_pos, 4)

        self._draw_analysis_cards(surface, font, arena_width)

    def _draw_analysis_cards(
        self, surface: Any, font: Any | None, arena_width: int
    ) -> None:
        if pygame is None:
            return
        if font is None:
            font = pygame.font.SysFont("Fira Code", 14)
        for enemy in self.living_enemies:
            info_lines = [enemy.topic]
            for key, value in enemy.analysis_notes.items():
                info_lines.append(f"{key}: {value}")
            if enemy.support_charge > 0.05:
                info_lines.append(f"Support: {enemy.support_charge:.1f}")
            if enemy.circuit_charge > 0.05:
                info_lines.append(f"Charge: {enemy.circuit_charge:.1f}s")
            if enemy.ablated:
                info_lines.append("Ablated — outputs silenced")
            text_surfaces = [
                font.render(line, True, (225, 235, 255)) for line in info_lines
            ]
            panel_width = max(
                arena_width // 5, max(ts.get_width() for ts in text_surfaces) + 16
            )
            panel_height = sum(ts.get_height() for ts in text_surfaces) + 12
            panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            panel.fill((22, 34, 66, 210))
            pygame.draw.rect(
                panel, (120, 200, 255), panel.get_rect(), width=1, border_radius=6
            )
            cursor_y = 6
            for rendered in text_surfaces:
                panel.blit(
                    rendered, ((panel_width - rendered.get_width()) // 2, cursor_y)
                )
                cursor_y += rendered.get_height() + 2
            anchor_x = int(enemy.x + enemy.size / 2 - panel_width / 2)
            anchor_y = int(enemy.y) - panel_height - 12
            anchor_x = max(4, min(anchor_x, arena_width - panel_width - 4))
            anchor_y = max(4, anchor_y)
            surface.blit(panel, (anchor_x, anchor_y))

    def _draw_hud(
        self, surface: Any, font: Any | None, overlay_x: int, height: int
    ) -> None:
        if pygame is None:
            return
        panel_rect = pygame.Rect(overlay_x, 0, surface.get_width() - overlay_x, height)
        pygame.draw.rect(surface, (14, 16, 28), panel_rect)
        pygame.draw.rect(surface, (40, 48, 72), panel_rect, width=2)
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
        scan_status = (
            f"Scan active: {self.scan_timer:0.1f}s remaining"
            if self.scan_timer > 0
            else "Scan ready — press Tab to analyse"
        )
        text_y = self._draw_wrapped_text(
            surface,
            font,
            panel_rect.x + 12,
            text_y + 10,
            scan_status,
            (150, 205, 255),
        )
        text_y += 6
        tasks = [task.progress_line() for task in self.active_tasks]
        if not tasks:
            tasks = ["Collect insights to unlock research tasks."]
        text_y = self._draw_section(
            surface,
            font,
            panel_rect.x + 12,
            text_y,
            "Research Tasks",
            tasks[:5],
        )
        text_y = self._draw_section(
            surface,
            font,
            panel_rect.x + 12,
            text_y,
            "Coaching",
            list(self.coaching_tips),
        )
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
        mastered = [
            title
            for title, record in self.research_journal.records.items()
            if record.mastered
        ]
        if mastered:
            text_y = self._draw_section(
                surface,
                font,
                panel_rect.x + 12,
                text_y,
                "Mastered Concepts",
                mastered,
            )
        self._draw_stat_bars(surface, font, panel_rect)

    def _draw_stat_bars(self, surface: Any, font: Any, panel_rect: Any) -> None:
        if pygame is None:
            return
        base_x = panel_rect.x + 12
        health_max = getattr(self.player, "max_health", 5) or 5
        self._draw_stat_bar(
            surface,
            font,
            base_x,
            panel_rect.bottom - 110,
            "Health",
            self.player.health,
            health_max,
            (255, 140, 140),
            panel_rect.width - 24,
        )
        self._draw_stat_bar(
            surface,
            font,
            base_x,
            panel_rect.bottom - 60,
            "Energy",
            self.player.energy,
            self.player.max_energy,
            (120, 255, 220),
            panel_rect.width - 24,
        )

    def _draw_stat_bar(
        self,
        surface: Any,
        font: Any,
        x: int,
        y: int,
        label: str,
        value: float,
        maximum: float,
        colour: Tuple[int, int, int],
        width: int,
    ) -> None:
        if pygame is None:
            return
        max_value = max(1.0, float(maximum))
        ratio = max(0.0, min(1.0, float(value) / max_value))
        bar_rect = pygame.Rect(x, y, width, 16)
        pygame.draw.rect(surface, (28, 36, 60), bar_rect, border_radius=6)
        fill_rect = pygame.Rect(x, y, int(width * ratio), 16)
        pygame.draw.rect(surface, colour, fill_rect, border_radius=6)
        label_surface = font.render(
            f"{label}: {int(value)}/{int(max_value)}", True, (220, 225, 250)
        )
        surface.blit(label_surface, (x, y - label_surface.get_height() - 2))

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
