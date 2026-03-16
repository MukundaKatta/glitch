"""Tests for GLITCH probe modules."""

from __future__ import annotations

import pytest

from glitch.probes import BaseProbe, ProbeDomain, ProbeItem, ProbeResult
from glitch.probes.spatial import SpatialProbe
from glitch.probes.temporal import TemporalProbe
from glitch.probes.causal import CausalProbe
from glitch.probes.physical import PhysicalProbe
from glitch.probes.social import SocialProbe
from glitch.probes.self_model import SelfModelProbe
from glitch.analyzer import GlitchAnalyzer, GlitchType, Severity


ALL_PROBE_CLASSES: list[type[BaseProbe]] = [
    SpatialProbe,
    TemporalProbe,
    CausalProbe,
    PhysicalProbe,
    SocialProbe,
    SelfModelProbe,
]


class TestProbeStructure:
    """Verify that all probe modules conform to the expected structure."""

    @pytest.mark.parametrize("probe_cls", ALL_PROBE_CLASSES)
    def test_probe_has_domain(self, probe_cls: type[BaseProbe]) -> None:
        probe = probe_cls()
        assert isinstance(probe.domain, ProbeDomain)

    @pytest.mark.parametrize("probe_cls", ALL_PROBE_CLASSES)
    def test_probe_returns_items(self, probe_cls: type[BaseProbe]) -> None:
        probe = probe_cls()
        items = probe.get_probes()
        assert isinstance(items, list)
        assert len(items) >= 15, f"{probe_cls.__name__} has {len(items)} probes (need >= 15)"

    @pytest.mark.parametrize("probe_cls", ALL_PROBE_CLASSES)
    def test_probe_items_are_valid(self, probe_cls: type[BaseProbe]) -> None:
        probe = probe_cls()
        for item in probe.get_probes():
            assert isinstance(item, ProbeItem)
            assert item.id, "Probe ID must not be empty"
            assert item.setup, "Probe setup must not be empty"
            assert item.question, "Probe question must not be empty"
            assert item.expected_answer, "Expected answer must not be empty"
            assert 1 <= item.difficulty <= 5

    @pytest.mark.parametrize("probe_cls", ALL_PROBE_CLASSES)
    def test_probe_ids_are_unique(self, probe_cls: type[BaseProbe]) -> None:
        probe = probe_cls()
        ids = [item.id for item in probe.get_probes()]
        assert len(ids) == len(set(ids)), f"Duplicate probe IDs in {probe_cls.__name__}"

    @pytest.mark.parametrize("probe_cls", ALL_PROBE_CLASSES)
    def test_probes_have_consistency_checks(self, probe_cls: type[BaseProbe]) -> None:
        probe = probe_cls()
        for item in probe.get_probes():
            assert len(item.consistency_checks) >= 1, (
                f"Probe {item.id} needs at least one consistency check"
            )

    def test_all_ids_globally_unique(self) -> None:
        all_ids: list[str] = []
        for probe_cls in ALL_PROBE_CLASSES:
            all_ids.extend(item.id for item in probe_cls().get_probes())
        assert len(all_ids) == len(set(all_ids)), "Duplicate probe IDs across domains"

    def test_all_domains_covered(self) -> None:
        covered = {probe_cls().domain for probe_cls in ALL_PROBE_CLASSES}
        expected = set(ProbeDomain)
        assert covered == expected, f"Missing domains: {expected - covered}"

    def test_total_probe_count(self) -> None:
        total = sum(len(probe_cls().get_probes()) for probe_cls in ALL_PROBE_CLASSES)
        assert total >= 90, f"Expected >= 90 probes total, got {total}"


class TestProbeResult:
    """Test the ProbeResult model."""

    def _make_probe(self) -> ProbeItem:
        return ProbeItem(
            id="test-001",
            domain=ProbeDomain.SPATIAL,
            category="test",
            setup="Test setup",
            question="Test question?",
            expected_answer="Test answer",
            explanation="Test explanation",
            difficulty=1,
            consistency_checks=["Check 1", "Check 2"],
        )

    def test_consistency_rate_all_correct(self) -> None:
        result = ProbeResult(
            probe=self._make_probe(),
            model_answer="Test answer",
            is_correct=True,
            consistency_scores=[True, True],
        )
        assert result.consistency_rate == 1.0

    def test_consistency_rate_half_correct(self) -> None:
        result = ProbeResult(
            probe=self._make_probe(),
            model_answer="Test answer",
            is_correct=True,
            consistency_scores=[True, False],
        )
        assert result.consistency_rate == 0.5

    def test_consistency_rate_none_correct(self) -> None:
        result = ProbeResult(
            probe=self._make_probe(),
            model_answer="Wrong",
            is_correct=False,
            consistency_scores=[False, False],
        )
        assert result.consistency_rate == 0.0

    def test_consistency_rate_no_checks(self) -> None:
        result = ProbeResult(
            probe=self._make_probe(),
            model_answer="Answer",
            is_correct=True,
        )
        assert result.consistency_rate == 1.0

    def test_consistency_rate_no_checks_incorrect(self) -> None:
        result = ProbeResult(
            probe=self._make_probe(),
            model_answer="Wrong",
            is_correct=False,
        )
        assert result.consistency_rate == 0.0


class TestGlitchAnalyzer:
    """Test the GlitchAnalyzer."""

    def _make_result(
        self,
        is_correct: bool = True,
        consistency_scores: list[bool] | None = None,
        difficulty: int = 1,
        category: str = "test",
    ) -> ProbeResult:
        probe = ProbeItem(
            id="test-001",
            domain=ProbeDomain.SPATIAL,
            category=category,
            setup="Test",
            question="Test?",
            expected_answer="Expected",
            explanation="Because",
            difficulty=difficulty,
            consistency_checks=["Check"],
        )
        return ProbeResult(
            probe=probe,
            model_answer="Answer",
            is_correct=is_correct,
            consistency_scores=consistency_scores or [],
        )

    def test_analyze_correct_consistent(self) -> None:
        result = self._make_result(is_correct=True, consistency_scores=[True, True])
        analyzer = GlitchAnalyzer()
        report = analyzer.analyze(result)
        assert report.severity == Severity.MINOR
        assert report.passed

    def test_analyze_correct_inconsistent(self) -> None:
        result = self._make_result(is_correct=True, consistency_scores=[True, False, False])
        analyzer = GlitchAnalyzer()
        report = analyzer.analyze(result)
        assert report.glitch_type == GlitchType.INCONSISTENCY
        assert report.severity in (Severity.MODERATE, Severity.SEVERE)

    def test_analyze_incorrect_consistent(self) -> None:
        result = self._make_result(is_correct=False, consistency_scores=[True, True])
        analyzer = GlitchAnalyzer()
        report = analyzer.analyze(result)
        assert report.glitch_type == GlitchType.CONFABULATION
        assert report.severity == Severity.SEVERE

    def test_analyze_incorrect_inconsistent(self) -> None:
        result = self._make_result(is_correct=False, consistency_scores=[False, False])
        analyzer = GlitchAnalyzer()
        report = analyzer.analyze(result)
        assert report.severity == Severity.CRITICAL

    def test_analyze_batch(self) -> None:
        results = [
            self._make_result(is_correct=True, consistency_scores=[True]),
            self._make_result(is_correct=False, consistency_scores=[False]),
        ]
        analyzer = GlitchAnalyzer()
        reports = analyzer.analyze_batch(results)
        assert len(reports) == 2

    def test_summary(self) -> None:
        results = [
            self._make_result(is_correct=True, consistency_scores=[True]),
            self._make_result(is_correct=False, consistency_scores=[False]),
        ]
        analyzer = GlitchAnalyzer()
        reports = analyzer.analyze_batch(results)
        summary = analyzer.summary(reports)
        assert summary["total"] == 2
        assert summary["passed"] == 1
        assert summary["failed"] == 1
