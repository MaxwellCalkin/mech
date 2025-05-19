"""Main game loop for Mechanistic Mech Arena."""

import pygame

from .enemy import Enemy
from .level import Level
from .player import Player

WIDTH, HEIGHT = 800, 600


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mechanistic Mech Arena")

    player = Player(x=WIDTH // 2, y=HEIGHT // 2)
    enemies = [Enemy(x=100, y=100)]
    level = Level(
        name="Demo", description="Intro level", player=player, enemies=enemies
    )
    level.start()

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-1, 0)
        if keys[pygame.K_RIGHT]:
            player.move(1, 0)
        if keys[pygame.K_UP]:
            player.move(0, -1)
        if keys[pygame.K_DOWN]:
            player.move(0, 1)

        level.update()
        if not player.alive:
            print("Game Over!")
            running = False

        screen.fill((30, 30, 30))
        level.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
