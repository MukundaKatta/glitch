"""Tests for the World Model Consistency Scorer."""

from __future__ import annotations

import pytest

from glitch.probes import ProbeDomain, ProbeItem, ProbeResult
from glitch.scorer import WorldModelConsistencyScorer, _letter_grade


def _make_probe(domain: ProbeDomain, probe_id: str = "test-001") -> ProbeItem:
    return ProbeItem(
        id=probe_id,
        domain=domain,
        category="test",
        setup="Test",
        question="Test?",
        expected_answer="Expected",
        explanation="Because",
        difficulty=1,
        consistency_checks=["Check"],
    )


def _make_result(
    domain: ProbeDomain,
    is_correct: bool,
    consistency_scores: list[bool],
    probe_id: str = "test-001",
) -> ProbeResult:
    return ProbeResult(
        probe=_make_probe(domain, probe_id),
        model_answer="Answer",
        is_correct=is_correct,
        consistency_scores=consistency_scores,
    )


class TestLetterGrade:
    def test_a_grade(self) -> None:
        assert _letter_grade(0.95) == "A"

    def test_c_grade(self) -> None:
        assert _letter_grade(0.50) == "C"

    def test_f_grade(self) -> None:
        assert _letter_grade(0.10) == "F"

    def test_boundary(self) -> None:
        assert _letter_grade(0.93) == "A"
        assert _letter_grade(0.92) == "A-"


class TestScorer:
    def test_perfect_score(self) -> None:
        results = [
            _make_result(ProbeDomain.SPATIAL, True, [True, True], f"s-{i}")
            for i in range(5)
        ]
        scorer = WorldModelConsistencyScorer()
        score = scorer.score(results, model_name="test", model_id="test-1")
        assert score.overall == 1.0
        assert score.grade == "A"
        assert score.total_correct == 5
        assert score.total_consistent == 5

    def test_zero_score(self) -> None:
        results = [
            _make_result(ProbeDomain.SPATIAL, False, [False, False], f"s-{i}")
            for i in range(5)
        ]
        scorer = WorldModelConsistencyScorer()
        score = scorer.score(results, model_name="test", model_id="test-1")
        assert score.overall == 0.0
        assert score.grade == "F"

    def test_mixed_domains(self) -> None:
        results = [
            _make_result(ProbeDomain.SPATIAL, True, [True], "sp-1"),
            _make_result(ProbeDomain.SPATIAL, True, [True], "sp-2"),
            _make_result(ProbeDomain.TEMPORAL, False, [False], "tp-1"),
            _make_result(ProbeDomain.TEMPORAL, False, [False], "tp-2"),
        ]
        scorer = WorldModelConsistencyScorer()
        score = scorer.score(results, model_name="test", model_id="test-1")

        assert score.domain_scores["spatial"].accuracy == 1.0
        assert score.domain_scores["temporal"].accuracy == 0.0
        # Overall should be ~0.5
        assert 0.4 <= score.overall <= 0.6

    def test_domain_score_structure(self) -> None:
        results = [
            _make_result(ProbeDomain.CAUSAL, True, [True, False], "c-1"),
        ]
        scorer = WorldModelConsistencyScorer()
        score = scorer.score(results, model_name="test", model_id="test-1")

        ds = score.domain_scores["causal"]
        assert ds.accuracy == 1.0
        assert ds.consistency == 0.5
        assert ds.num_probes == 1
        assert ds.num_correct == 1

    def test_custom_weights(self) -> None:
        results = [
            _make_result(ProbeDomain.SPATIAL, True, [True], "sp-1"),
            _make_result(ProbeDomain.TEMPORAL, False, [False], "tp-1"),
        ]
        # Weight spatial 3x more than temporal
        weights = {
            ProbeDomain.SPATIAL: 3.0,
            ProbeDomain.TEMPORAL: 1.0,
        }
        scorer = WorldModelConsistencyScorer(weights=weights)
        score = scorer.score(results, model_name="test", model_id="test-1")
        # Should be closer to 1.0 than 0.5 because spatial is weighted more
        assert score.overall > 0.6

    def test_empty_results(self) -> None:
        scorer = WorldModelConsistencyScorer()
        score = scorer.score([], model_name="test", model_id="test-1")
        assert score.overall == 0.0
        assert score.total_probes == 0


class TestComparison:
    def test_compare_different_scores(self) -> None:
        scorer = WorldModelConsistencyScorer()

        results_a = [
            _make_result(ProbeDomain.SPATIAL, True, [True], f"sp-{i}") for i in range(5)
        ]
        results_b = [
            _make_result(ProbeDomain.SPATIAL, False, [False], f"sp-{i}") for i in range(5)
        ]

        score_a = scorer.score(results_a, model_name="ModelA", model_id="a-1")
        score_b = scorer.score(results_b, model_name="ModelB", model_id="b-1")

        comparison = scorer.compare(score_a, score_b)
        assert comparison.winner == "ModelA"
        assert comparison.overall_a > comparison.overall_b

    def test_compare_equal_scores(self) -> None:
        scorer = WorldModelConsistencyScorer()

        results = [
            _make_result(ProbeDomain.SPATIAL, True, [True], f"sp-{i}") for i in range(5)
        ]

        score_a = scorer.score(results, model_name="ModelA", model_id="a-1")
        score_b = scorer.score(results, model_name="ModelB", model_id="b-1")

        comparison = scorer.compare(score_a, score_b)
        assert comparison.winner == "tie"
