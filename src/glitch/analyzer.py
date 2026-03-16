"""Glitch analysis and classification engine.

Analyzes probe results to classify the type, severity, and characteristics
of detected world-model inconsistencies.
"""

from __future__ import annotations

import enum
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from glitch.probes import ProbeDomain, ProbeResult


class GlitchType(str, enum.Enum):
    """Classification of world-model glitch types."""

    INCONSISTENCY = "inconsistency"
    """Model gives contradictory answers to logically equivalent questions."""

    CONTRADICTION = "contradiction"
    """Model fails to detect an explicit contradiction in the input."""

    HALLUCINATION = "hallucination"
    """Model fabricates facts not supported by the context."""

    BLIND_SPOT = "blind_spot"
    """Model systematically fails on a category of reasoning."""

    CONFABULATION = "confabulation"
    """Model produces confident but wrong explanations for its answers."""


class Severity(str, enum.Enum):
    """Severity level of a detected glitch."""

    MINOR = "minor"
    """Slight imprecision that doesn't change the core answer."""

    MODERATE = "moderate"
    """Meaningful error that affects reasoning quality."""

    SEVERE = "severe"
    """Fundamental reasoning failure in the domain."""

    CRITICAL = "critical"
    """Complete breakdown of world-model coherence."""


class GlitchReport(BaseModel):
    """Detailed report for a single detected glitch."""

    probe_id: str
    domain: ProbeDomain
    category: str
    glitch_type: GlitchType
    severity: Severity
    is_correct: bool
    consistency_rate: float = Field(ge=0.0, le=1.0)
    model_answer: str
    expected_answer: str
    analysis: str = Field(description="Human-readable analysis of the glitch")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def passed(self) -> bool:
        """Whether the probe was passed (correct and consistent)."""
        return self.is_correct and self.consistency_rate >= 0.8


class GlitchAnalyzer:
    """Analyzes probe results to classify and characterize glitches."""

    # Weights for severity classification based on consistency rate and correctness
    _SEVERITY_THRESHOLDS = {
        # (correct, consistency_rate_range) -> Severity
        (True, 0.8): Severity.MINOR,       # correct but some inconsistency
        (True, 0.5): Severity.MODERATE,     # correct but significant inconsistency
        (True, 0.0): Severity.SEVERE,       # correct answer but totally inconsistent follow-ups
        (False, 0.5): Severity.SEVERE,      # wrong answer with some consistency
        (False, 0.0): Severity.CRITICAL,    # wrong answer and inconsistent
    }

    def analyze(self, result: ProbeResult) -> GlitchReport:
        """Analyze a single probe result and produce a glitch report."""
        glitch_type = self._classify_type(result)
        severity = self._classify_severity(result)
        analysis = self._generate_analysis(result, glitch_type, severity)

        return GlitchReport(
            probe_id=result.probe.id,
            domain=result.probe.domain,
            category=result.probe.category,
            glitch_type=glitch_type,
            severity=severity,
            is_correct=result.is_correct,
            consistency_rate=result.consistency_rate,
            model_answer=result.model_answer,
            expected_answer=result.probe.expected_answer,
            analysis=analysis,
        )

    def analyze_batch(self, results: list[ProbeResult]) -> list[GlitchReport]:
        """Analyze a batch of probe results."""
        return [self.analyze(r) for r in results]

    def _classify_type(self, result: ProbeResult) -> GlitchType:
        """Determine the type of glitch based on the probe result pattern."""
        if result.is_correct and result.consistency_rate < 1.0:
            # Got the main answer right but follow-ups are inconsistent
            return GlitchType.INCONSISTENCY

        if not result.is_correct and result.consistency_rate > 0.5:
            # Wrong answer but internally consistent — model has a wrong but stable model
            return GlitchType.CONFABULATION

        if not result.is_correct and result.consistency_rate <= 0.5:
            # Wrong and inconsistent — could be hallucination or blind spot
            if result.probe.difficulty >= 3:
                return GlitchType.BLIND_SPOT
            return GlitchType.HALLUCINATION

        # Probe involves contradiction detection (check category keywords)
        contradiction_categories = {
            "impossibility", "contradiction_detection", "reversal", "paradox"
        }
        if result.probe.category in contradiction_categories and not result.is_correct:
            return GlitchType.CONTRADICTION

        # Default for incorrect results
        if not result.is_correct:
            return GlitchType.HALLUCINATION

        # Passed cleanly
        return GlitchType.INCONSISTENCY  # Minor inconsistency at most

    def _classify_severity(self, result: ProbeResult) -> Severity:
        """Determine severity based on correctness and consistency."""
        rate = result.consistency_rate

        if result.is_correct:
            if rate >= 0.8:
                return Severity.MINOR
            if rate >= 0.5:
                return Severity.MODERATE
            return Severity.SEVERE
        else:
            if rate >= 0.5:
                return Severity.SEVERE
            return Severity.CRITICAL

    def _generate_analysis(
        self,
        result: ProbeResult,
        glitch_type: GlitchType,
        severity: Severity,
    ) -> str:
        """Generate a human-readable analysis string."""
        parts: list[str] = []

        if result.is_correct:
            parts.append(
                f"The model correctly answered the {result.probe.category} probe "
                f"(difficulty {result.probe.difficulty}/5)."
            )
        else:
            parts.append(
                f"The model incorrectly answered the {result.probe.category} probe "
                f"(difficulty {result.probe.difficulty}/5)."
            )

        parts.append(
            f"Consistency rate across follow-up checks: {result.consistency_rate:.0%}."
        )

        type_descriptions = {
            GlitchType.INCONSISTENCY: (
                "The model showed INCONSISTENCY: its follow-up answers contradict "
                "its initial response, indicating an unstable world model in this domain."
            ),
            GlitchType.CONTRADICTION: (
                "The model failed CONTRADICTION DETECTION: it did not notice an "
                "explicit logical or factual contradiction in the input."
            ),
            GlitchType.HALLUCINATION: (
                "The model HALLUCINATED: it produced a confident but factually wrong answer "
                "not supported by the given context."
            ),
            GlitchType.BLIND_SPOT: (
                "The model hit a BLIND SPOT: it systematically fails at this type of "
                "reasoning, suggesting a structural limitation."
            ),
            GlitchType.CONFABULATION: (
                "The model CONFABULATED: it gave a wrong answer but maintained internal "
                "consistency, suggesting a stable but incorrect world model."
            ),
        }
        parts.append(type_descriptions[glitch_type])

        severity_notes = {
            Severity.MINOR: "This is a minor glitch with limited practical impact.",
            Severity.MODERATE: "This is a moderate glitch that could affect reasoning quality.",
            Severity.SEVERE: "This is a severe glitch indicating a fundamental reasoning failure.",
            Severity.CRITICAL: "This is a CRITICAL glitch — complete breakdown of world-model coherence.",
        }
        parts.append(severity_notes[severity])

        return " ".join(parts)

    def summary(self, reports: list[GlitchReport]) -> dict:
        """Generate a summary of glitch analysis results."""
        total = len(reports)
        if total == 0:
            return {"total": 0, "passed": 0, "failed": 0}

        passed = sum(1 for r in reports if r.passed)
        by_type = {}
        for gt in GlitchType:
            count = sum(1 for r in reports if r.glitch_type == gt and not r.passed)
            if count > 0:
                by_type[gt.value] = count

        by_severity = {}
        for sev in Severity:
            count = sum(1 for r in reports if r.severity == sev and not r.passed)
            if count > 0:
                by_severity[sev.value] = count

        by_domain = {}
        for domain in ProbeDomain:
            domain_reports = [r for r in reports if r.domain == domain]
            if domain_reports:
                domain_passed = sum(1 for r in domain_reports if r.passed)
                by_domain[domain.value] = {
                    "total": len(domain_reports),
                    "passed": domain_passed,
                    "rate": domain_passed / len(domain_reports),
                }

        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": passed / total,
            "by_glitch_type": by_type,
            "by_severity": by_severity,
            "by_domain": by_domain,
        }
