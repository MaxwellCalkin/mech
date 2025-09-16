# Development Plan for Mechanistic Mech Arena

This plan rebuilds the project from the ground up so that the prototype evolves into a
rich, replayable learning experience about mechanistic interpretability. The work is
split into four production phases with deliverables, risks, and success criteria. Each
phase builds player-facing functionality as well as educational affordances.

## Phase 0 – Foundations (Week 0)
- Audit existing code and remove dead ends that block iteration.
- Establish coding standards (Black + type hints) and automated tests.
- Document the core learning goals for the project (attention, circuits, activation
  patching) so they can be referenced by designers and engineers alike.
- Outcome: a clean repo with CI-ready tooling and a single vertical slice target.

## Phase 1 – Core Systems (Weeks 1-2)
- Implement a modular entity-component architecture for the player, enemies, and
  interactable “insight nodes”.
- Replace the ad-hoc game loop with a `Game` object that owns scenes, a deterministic
  update tick, and input mapping.
- Build a flexible `Level` data model that tracks projectiles, insight pickups, and a
  knowledge log summarising everything the player has discovered.
- Ship a debug overlay that visualises the simulated transformer layer as a graph of
  nodes and attention edges.
- Outcome: a playable arena with movement, shooting, health, and a functioning
  interpretability overlay.

## Phase 2 – Learning Experiences (Weeks 3-5)
- Craft a mission scripting system that sequences narration, objectives, and puzzle
  triggers (e.g. “expose induction head by activating scan mode”).
- Introduce diverse enemy archetypes tied to interpretability topics:
  - Pattern Matching Drone (induction heads)
  - Circuit Sentinel (activation patching)
  - Scaling Juggernaut (scaling laws)
- Implement the **Insight Deck**: collecting pickups adds illustrated cards that explain
  the mechanic, include historical context, and link to further reading.
- Outcome: a 15-minute guided mission covering signal flow and attention.

## Phase 3 – Tooling & Progression (Weeks 6-8)
- Add persistent progression (pilot logs, achievements, unlocked missions).
- Expose a sandbox “Lab Mode” where players can spawn enemies and toggle interpretability
  tools such as logit lens overlays or neuron activation charts.
- Integrate scripted boss encounters that require combining insights learned so far.
- Outcome: multiple replayable missions and a self-directed exploration space.

## Phase 4 – Polish & Delivery (Weeks 9-10)
- Conduct usability tests with newcomers to AI alignment and incorporate feedback into
  onboarding, UI copy, and pacing.
- Optimise rendering, add accessibility options (colourblind palettes, input remapping).
- Prepare marketing material: trailer, screenshots, educator one-pager.
- Outcome: Version 1.0 release candidate with documentation for educators and modders.

## Cross-Cutting Concerns
- **Narrative Integration:** Story moments are implemented as light-weight timeline
  events that can pause combat, show portraits, and surface new insight cards.
- **Educational Validity:** All interpretability explanations are peer-reviewed by a
  subject-matter expert before shipping.
- **Testing:**
  - Unit tests cover entity behaviour, collision, and knowledge log bookkeeping.
  - Integration tests spin up a headless Pygame surface to simulate two minutes of play.
  - Manual QA scripts document expected behaviour for each mission beat.

## Immediate Next Steps
1. Finalise the core entity and level architecture (implemented in this PR).
2. Draft the first batch of insight cards referencing attention heads and residual
   streams.
3. Build tooling scripts that export narrative timelines to JSON so designers can tweak
   missions without touching Python code.
