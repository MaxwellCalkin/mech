# Mechanistic Mech Arena

Mechanistic Mech Arena is a browser-inspired (Pygame) action game that doubles as an
interactive primer on mechanistic interpretability. You pilot an experimental mech inside
a large language model, disrupt rogue subsystems, and collect insights that explain how
transformers really work.

## Features
- Moment-to-moment top-down combat with smooth movement and projectile-based attacks.
- A living schematic of the active transformer layer that updates as you discover new
  insights.
- Collectible insight cards that narrate real interpretability concepts such as attention
  heads, induction circuits, and activation patching.
- Scan mode that freezes the arena, highlights token flows, and surfaces contextual tips.

## Getting Started
1. Install Python 3.10 or newer.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the game:
   ```bash
   python -m mech_arena
   ```

The game automatically degrades to a headless mode for unit tests, so running the test
suite does not require a graphical environment.

## Project Structure
- `src/mech_arena/` – Game source code (entities, levels, main loop).
- `docs/` – Design documents and development plans.
- `tests/` – Automated tests covering the deterministic gameplay systems.

## Development
See `AGENTS.md` for formatting and testing guidelines. Contributions should maintain the
educational tone of the project and keep interpretability explanations accurate.
