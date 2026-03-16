"""World Model Consistency Scorer.

Computes per-domain and overall consistency scores for LLM world models,
and provides comparison utilities across models.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from glitch.probes import ProbeDomain, ProbeResult


class DomainScore(BaseModel):
    """Consistency score for a single domain."""

    domain: ProbeDomain
    accuracy: float = Field(ge=0.0, le=1.0, description="Fraction of correct main answers")
    consistency: float = Field(ge=0.0, le=1.0, description="Average consistency across follow-ups")
    composite: float = Field(ge=0.0, le=1.0, description="Weighted combination of accuracy and consistency")
    num_probes: int
    num_correct: int
    num_consistent: int = Field(description="Probes with consistency >= 0.8")


class ConsistencyScore(BaseModel):
    """Overall world-model consistency score for a model."""

    model_name: str
    model_id: str
    overall: float = Field(ge=0.0, le=1.0)
    domain_scores: dict[str, DomainScore]
    total_probes: int
    total_correct: int
    total_consistent: int
    grade: str = Field(description="Letter grade A-F")


class ComparisonReport(BaseModel):
    """Comparison between two model scores."""

    model_a: str
    model_b: str
    overall_a: float
    overall_b: float
    winner: str
    domain_comparisons: dict[str, dict[str, float]]
    analysis: str


# Default domain weights — all equal, but can be customized
DEFAULT_WEIGHTS: dict[ProbeDomain, float] = {
    ProbeDomain.SPATIAL: 1.0,
    ProbeDomain.TEMPORAL: 1.0,
    ProbeDomain.CAUSAL: 1.0,
    ProbeDomain.PHYSICAL: 1.0,
    ProbeDomain.SOCIAL: 1.0,
    ProbeDomain.SELF_MODEL: 1.0,
}

# Accuracy vs consistency blend for composite score
ACCURACY_WEIGHT = 0.6
CONSISTENCY_WEIGHT = 0.4


def _letter_grade(score: float) -> str:
    """Convert a 0-1 score to a letter grade."""
    if score >= 0.93:
        return "A"
    if score >= 0.85:
        return "A-"
    if score >= 0.80:
        return "B+"
    if score >= 0.73:
        return "B"
    if score >= 0.65:
        return "B-"
    if score >= 0.58:
        return "C+"
    if score >= 0.50:
        return "C"
    if score >= 0.42:
        return "C-"
    if score >= 0.35:
        return "D"
    return "F"


class WorldModelConsistencyScorer:
    """Computes world-model consistency scores from probe results."""

    def __init__(
        self,
        weights: dict[ProbeDomain, float] | None = None,
        accuracy_weight: float = ACCURACY_WEIGHT,
        consistency_weight: float = CONSISTENCY_WEIGHT,
    ) -> None:
        self.weights = weights or DEFAULT_WEIGHTS.copy()
        self.accuracy_weight = accuracy_weight
        self.consistency_weight = consistency_weight

    def score(
        self,
        results: list[ProbeResult],
        model_name: str = "unknown",
        model_id: str = "unknown",
    ) -> ConsistencyScore:
        """Compute the full consistency score from probe results."""
        # Group results by domain
        by_domain: dict[ProbeDomain, list[ProbeResult]] = {}
        for r in results:
            by_domain.setdefault(r.probe.domain, []).append(r)

        domain_scores: dict[str, DomainScore] = {}
        for domain, domain_results in by_domain.items():
            domain_scores[domain.value] = self._score_domain(domain, domain_results)

        # Overall score: weighted average of composite domain scores
        total_weight = 0.0
        weighted_sum = 0.0
        for domain, ds in domain_scores.items():
            w = self.weights.get(ProbeDomain(domain), 1.0)
            weighted_sum += ds.composite * w
            total_weight += w

        overall = weighted_sum / total_weight if total_weight > 0 else 0.0

        total_probes = len(results)
        total_correct = sum(1 for r in results if r.is_correct)
        total_consistent = sum(1 for r in results if r.consistency_rate >= 0.8)

        return ConsistencyScore(
            model_name=model_name,
            model_id=model_id,
            overall=round(overall, 4),
            domain_scores=domain_scores,
            total_probes=total_probes,
            total_correct=total_correct,
            total_consistent=total_consistent,
            grade=_letter_grade(overall),
        )

    def _score_domain(
        self, domain: ProbeDomain, results: list[ProbeResult]
    ) -> DomainScore:
        """Compute score for a single domain."""
        n = len(results)
        if n == 0:
            return DomainScore(
                domain=domain,
                accuracy=0.0,
                consistency=0.0,
                composite=0.0,
                num_probes=0,
                num_correct=0,
                num_consistent=0,
            )

        num_correct = sum(1 for r in results if r.is_correct)
        accuracy = num_correct / n

        avg_consistency = sum(r.consistency_rate for r in results) / n
        num_consistent = sum(1 for r in results if r.consistency_rate >= 0.8)

        composite = (
            self.accuracy_weight * accuracy
            + self.consistency_weight * avg_consistency
        )

        return DomainScore(
            domain=domain,
            accuracy=round(accuracy, 4),
            consistency=round(avg_consistency, 4),
            composite=round(composite, 4),
            num_probes=n,
            num_correct=num_correct,
            num_consistent=num_consistent,
        )

    def compare(
        self,
        score_a: ConsistencyScore,
        score_b: ConsistencyScore,
    ) -> ComparisonReport:
        """Compare two model scores and produce a comparison report."""
        domain_comparisons: dict[str, dict[str, float]] = {}

        all_domains = set(score_a.domain_scores.keys()) | set(score_b.domain_scores.keys())
        for domain in sorted(all_domains):
            ds_a = score_a.domain_scores.get(domain)
            ds_b = score_b.domain_scores.get(domain)
            domain_comparisons[domain] = {
                f"{score_a.model_name}_composite": ds_a.composite if ds_a else 0.0,
                f"{score_b.model_name}_composite": ds_b.composite if ds_b else 0.0,
                "delta": (ds_a.composite if ds_a else 0.0) - (ds_b.composite if ds_b else 0.0),
            }

        if score_a.overall > score_b.overall:
            winner = score_a.model_name
        elif score_b.overall > score_a.overall:
            winner = score_b.model_name
        else:
            winner = "tie"

        # Build analysis text
        lines: list[str] = [
            f"Overall: {score_a.model_name} ({score_a.overall:.2%}) vs "
            f"{score_b.model_name} ({score_b.overall:.2%}).",
            f"Winner: {winner}.",
        ]

        a_wins: list[str] = []
        b_wins: list[str] = []
        for domain, comp in domain_comparisons.items():
            delta = comp["delta"]
            if delta > 0.05:
                a_wins.append(domain)
            elif delta < -0.05:
                b_wins.append(domain)

        if a_wins:
            lines.append(f"{score_a.model_name} is stronger in: {', '.join(a_wins)}.")
        if b_wins:
            lines.append(f"{score_b.model_name} is stronger in: {', '.join(b_wins)}.")

        return ComparisonReport(
            model_a=score_a.model_name,
            model_b=score_b.model_name,
            overall_a=score_a.overall,
            overall_b=score_b.overall,
            winner=winner,
            domain_comparisons=domain_comparisons,
            analysis=" ".join(lines),
        )
