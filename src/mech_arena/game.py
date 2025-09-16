"""Main game loop for Mechanistic Mech Arena."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import pygame

from .enemy import Enemy
from .level import Level
from .player import Player

WIDTH, HEIGHT = 1200, 720
ARENA_WIDTH = WIDTH - 280


@dataclass
class InputState:
    """Container for player intent during a single frame."""

    move: Tuple[float, float] = (0.0, 0.0)
    fire_target: Tuple[float, float] | None = None
    trigger_scan: bool = False


class Game:
    """Owns the main loop, pygame state, and the active level."""

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Mechanistic Mech Arena")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Fira Code", 16)
        self.level = self._create_demo_level()
        self.running = True

    def _create_demo_level(self) -> Level:
        player = Player(x=ARENA_WIDTH // 2, y=HEIGHT // 2)
        enemies = [
            Enemy(
                x=80, y=120, topic="Residual Stream", summary="Keep information alive."
            ),
            Enemy(
                x=300,
                y=400,
                topic="Induction Head",
                summary="Predicts repeating tokens.",
            ),
            Enemy(
                x=500,
                y=200,
                topic="Circuit Breaker",
                summary="Interlocking neuron circuit.",
            ),
        ]
        level = Level(
            name="Layer 3: Attention Bay",
            description="Expose hostile subsystems and stabilise the residual stream.",
            player=player,
            enemies=enemies,
        )
        return level

    def run(self) -> None:
        """Enter the main loop until the window is closed."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            inputs = self._gather_input()
            self.level.update(
                dt=dt,
                move=inputs.move,
                fire_target=inputs.fire_target,
                trigger_scan=inputs.trigger_scan,
            )
            self._draw()
        pygame.quit()

    def _gather_input(self) -> InputState:
        move_x = move_y = 0.0
        fire_target: Tuple[float, float] | None = None
        trigger_scan = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                fire_target = event.pos
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                trigger_scan = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x += 1

        if move_x or move_y:
            magnitude = (move_x**2 + move_y**2) ** 0.5
            move_x /= magnitude
            move_y /= magnitude

        if fire_target is None and pygame.mouse.get_pressed()[0]:
            fire_target = pygame.mouse.get_pos()

        return InputState(
            move=(move_x, move_y), fire_target=fire_target, trigger_scan=trigger_scan
        )

    def _draw(self) -> None:
        self.level.draw(self.screen, self.font)
        pygame.display.flip()


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
