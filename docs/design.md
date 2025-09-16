# Mechanistic Mech Arena – Updated Design Document

## Vision
Mechanistic Mech Arena is a top-down action game where players pilot an interpretability
mech that navigates inside the latent space of a large language model. The player learns
mechanistic interpretability concepts by defeating hostile subsystems, scanning circuit
structures, and collecting "insight cards" that explain what each component of the model
does. Combat is kinetic and readable; educational content is woven into every mechanic
instead of being relegated to a codex.

## Core Pillars
1. **Kinetic Learning:** Every enemy archetype dramatizes a real interpretability topic.
   For example, attention drones reroute residual streams until the player disrupts them
   with a targeted insight pulse.
2. **Interactive Visualisation:** The right side of the screen hosts a live schematic of
   the transformer layer currently under attack. Scanning reveals new edges and updates a
   knowledge log that persists between runs.
3. **Player Agency:** Players choose when to scan, when to attack, and which insights to
   unlock. The level sandbox can be replayed with different loadouts to reinforce learning.

## Gameplay Loop
1. Enter a layer of the model. The arena maps to an attention block with residual stream
   nodes rendered along the edges.
2. Move and dash to avoid hostile components while firing "interpretability pulses"
   (projectiles).
3. Damage enemies to expose their hidden mechanisms. When they destabilise, they emit an
   **Insight Pickup**. Collecting it adds an entry to the knowledge log and updates the
   schematic overlay.
4. Trigger **Scan Mode** (TAB) to temporarily freeze enemies and reveal connections between
   tokens, neurons, and attention heads. Use this window to plan the next attack.
5. Defeat all hostile components to stabilise the layer and move on to the next lesson.

## Systems Overview
- **Game Loop:** `Game` manages Pygame initialisation, input handling, and dispatches to a
  `Level` object each frame.
- **Level:** Holds the player, enemies, projectiles, and insight pickups. Maintains the
  knowledge log, narrative timeline, and scan state. Exposes `update()` and `draw()`.
- **Player:** Moves with smooth physics, fires projectiles, and regenerates energy used
  for scanning and special attacks.
- **Enemy Archetypes:** Each enemy stores metadata about the interpretability concept it
  represents (topic, summary text, current behaviour). When destroyed, it produces an
  insight pickup tied to that metadata.
- **Insight Pickup:** Collectible orb that logs a new piece of knowledge and triggers UI
  updates.
- **Overlay & HUD:** Draws health, energy, current objective, and a simplified transformer
  schematic that reacts to the player's discoveries.

## Art & Audio Direction
- Minimalist neon aesthetic inspired by circuit diagrams.
- Friendly UI fonts with high legibility; colours encode concept categories (attention,
  circuits, scaling, etc.).
- Ambient synth soundtrack with adaptive layers that intensify during scans.

## Content Structure
- **Layer 1 – Signal Flow:** Introduces movement, shooting, and insight pickups. Enemies
  are slow and emphasise the idea of residual streams.
- **Layer 2 – Attention Heads:** Adds multi-target enemies whose behaviour changes when
  scanned. Highlights how attention selects tokens.
- **Layer 3 – Circuits:** Combines previous lessons and requires the player to chain scans
  and projectiles to isolate subcircuits.

## Educational Touchpoints
- Each insight card references a real research artifact (e.g. Anthropic's induction heads
  post) with a one-sentence summary.
- Scan overlays highlight active neurons and attention edges using animated polylines.
- Boss fights integrate short dialogue sequences that explain why a mechanic matters in
  real-world interpretability research.

## Implementation Notes
- The initial release focuses on a single arena that showcases the full system: movement,
  enemies, projectiles, scanning, and the interpretability overlay.
- All in-game text lives in Python data structures for now, but the architecture allows
  migrating to JSON later.
- Unit tests cover deterministic systems (movement, collisions, insight logging) while
  integration tests can stub out Pygame surfaces.
