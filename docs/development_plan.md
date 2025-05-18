# Development Plan for Mechanistic Mech Arena

This document outlines the steps required to evolve the existing prototype into a fully playable educational game. Each step corresponds to new modules or features in the codebase.

## 1. Core Game Loop
- Initialize Pygame and create the main window.
- Maintain a fixed update loop running at 60 FPS.
- Delegate update and render logic to a `Level` object.

## 2. Player Implementation
- Create a `Player` class with position and movement speed.
- Handle keyboard input to move the player sprite left, right, up, and down.
- Expose a `rect` property for collision handling.

## 3. Enemy Implementation
- Introduce an `Enemy` class with very simple AI (moves towards the player).
- Provide update and draw methods so enemies can be managed by a level.

## 4. Level Management
- Expand the existing `Level` dataclass to hold the player and a list of enemies.
- Implement `update()` and `draw()` methods.
- Future chapters can subclass `Level` to add narrative and boss behavior.

## 5. Game Entry Point
- Instantiate a `Level` in `game.py` and run its update/draw loop.
- Keep placeholder assets to reduce complexity.

## 6. Testing Strategy
- Use `pytest` to exercise the non-graphical logic of `Player` movement and `Level` initialization.
- Pygame specific functionality will be kept minimal in tests by avoiding the need for a display.

This plan focuses on providing a structured foundation that is easy to extend with art, sound and additional mechanics.

## 7. Collisions and Health
- Detect collisions between the player and enemies each frame.
- Reduce the player's health whenever a collision occurs.
- End the level if the player's health reaches zero.
