"""Probe modules for testing world model consistency across six domains."""

from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ProbeDomain(str, enum.Enum):
    """The six domains of world-model probing."""

    SPATIAL = "spatial"
    TEMPORAL = "temporal"
    CAUSAL = "causal"
    PHYSICAL = "physical"
    SOCIAL = "social"
    SELF_MODEL = "self_model"


class ProbeItem(BaseModel):
    """A single probe question with its expected answer and metadata."""

    id: str = Field(description="Unique probe identifier")
    domain: ProbeDomain
    category: str = Field(description="Sub-category within the domain")
    setup: str = Field(description="Context or scenario provided to the model")
    question: str = Field(description="The question posed to the model")
    expected_answer: str = Field(description="The correct / consistent answer")
    explanation: str = Field(description="Why the expected answer is correct")
    difficulty: int = Field(ge=1, le=5, description="1 (easy) to 5 (hard)")
    consistency_checks: list[str] = Field(
        default_factory=list,
        description="Follow-up questions that should yield consistent answers",
    )


class ProbeResult(BaseModel):
    """Result of running a single probe against a model."""

    probe: ProbeItem
    model_answer: str = ""
    is_correct: bool = False
    consistency_answers: list[str] = Field(default_factory=list)
    consistency_scores: list[bool] = Field(default_factory=list)
    raw_responses: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def consistency_rate(self) -> float:
        if not self.consistency_scores:
            return 1.0 if self.is_correct else 0.0
        correct = sum(1 for s in self.consistency_scores if s)
        return correct / len(self.consistency_scores)


class BaseProbe(ABC):
    """Abstract base class for all probe modules."""

    domain: ProbeDomain

    @abstractmethod
    def get_probes(self) -> list[ProbeItem]:
        """Return all probes for this domain."""
        ...

    def __len__(self) -> int:
        return len(self.get_probes())

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} domain={self.domain.value} probes={len(self)}>"
