"""Research task primitives that unlock deeper interpretability practice."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, List

if False:  # pragma: no cover - imported only for typing during analysis
    from .level import Level


Condition = Callable[["Level"], bool]


def _never(_: "Level") -> bool:
    return False


@dataclass
class ResearchTask:
    """A multi-step objective attached to a collected insight."""

    identifier: str
    concept: str
    description: str
    tip: str = ""
    requirement: Condition = field(default_factory=lambda: _never)
    completed: bool = False
    requires_scan: bool = False

    def evaluate(self, level: "Level") -> bool:
        """Mark the task complete if its requirement now holds."""
        if self.completed:
            return False
        if self.requirement(level):
            self.completed = True
            return True
        return False

    def progress_line(self) -> str:
        status = "✓" if self.completed else "…"
        return f"{status} {self.description}"


def build_residual_tasks() -> List[ResearchTask]:
    """Tasks that reinforce the residual stream concept."""

    return [
        ResearchTask(
            identifier="residual_scan",
            concept="Residual Stream",
            description="Scan while the residual stream is linking allies.",
            tip="Use Tab when it tethers to reveal how support flows.",
            requirement=lambda level: bool(
                level.scan_timer > 0 and level.analysis_tags.get("residual_linking")
            ),
            requires_scan=True,
        ),
        ResearchTask(
            identifier="residual_ablate",
            concept="Residual Stream",
            description="Ablate the residual stream to watch buffs collapse.",
            tip="Toggle analysis ablation with number keys while scanning.",
            requirement=lambda level: level.analysis_tags.get(
                "residual_ablation", False
            ),
        ),
    ]


def build_induction_tasks() -> List[ResearchTask]:
    return [
        ResearchTask(
            identifier="induction_prediction",
            concept="Induction Head",
            description="Witness the token prediction arc during a scan.",
            tip="Line up with the projected token beads.",
            requirement=lambda level: bool(
                level.scan_timer > 0 and level.analysis_tags.get("induction_prediction")
            ),
            requires_scan=True,
        ),
        ResearchTask(
            identifier="induction_ablate",
            concept="Induction Head",
            description="Ablate the induction head after observing the pattern.",
            tip="Press the matching number to freeze it mid-copy.",
            requirement=lambda level: level.analysis_tags.get(
                "induction_ablation", False
            ),
        ),
    ]


def build_circuit_tasks() -> List[ResearchTask]:
    return [
        ResearchTask(
            identifier="circuit_overlap",
            concept="Circuit Breaker",
            description="Trigger a scan while two enemies share a circuit.",
            tip="Wait until the breaker chains lightning between allies.",
            requirement=lambda level: bool(
                level.scan_timer > 0 and level.analysis_tags.get("circuit_chain")
            ),
            requires_scan=True,
        ),
        ResearchTask(
            identifier="circuit_interrupt",
            concept="Circuit Breaker",
            description="Disrupt a charged circuit breaker via ablation.",
            tip="Freeze it mid-charge to see the cascade stop.",
            requirement=lambda level: level.analysis_tags.get(
                "circuit_ablation", False
            ),
        ),
    ]


TASK_BUILDERS = {
    "Residual Stream": build_residual_tasks,
    "Induction Head": build_induction_tasks,
    "Circuit Breaker": build_circuit_tasks,
}


def build_tasks_for(topic: str) -> Iterable[ResearchTask]:
    factory = TASK_BUILDERS.get(topic)
    return factory() if factory else []
