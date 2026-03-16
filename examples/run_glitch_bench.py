#!/usr/bin/env python3
"""Example: Run the GLITCH benchmark against a model.

Usage:
    python run_glitch_bench.py                    # Defaults to Claude
    python run_glitch_bench.py --model openai     # Use OpenAI
    python run_glitch_bench.py --domain spatial    # Single domain
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure the src directory is on the path for direct execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from glitch.probes.spatial import SpatialProbe
from glitch.probes.temporal import TemporalProbe
from glitch.probes.causal import CausalProbe
from glitch.probes.physical import PhysicalProbe
from glitch.probes.social import SocialProbe
from glitch.probes.self_model import SelfModelProbe
from glitch.probes import BaseProbe, ProbeItem, ProbeResult
from glitch.analyzer import GlitchAnalyzer
from glitch.scorer import WorldModelConsistencyScorer
from glitch.models import get_adapter, ModelAdapter
from glitch.report import print_score, print_glitch_reports, save_results_json, generate_charts

from rich.console import Console

console = Console()

PROBES: dict[str, type[BaseProbe]] = {
    "spatial": SpatialProbe,
    "temporal": TemporalProbe,
    "causal": CausalProbe,
    "physical": PhysicalProbe,
    "social": SocialProbe,
    "self_model": SelfModelProbe,
}


def collect_probes(domain: str) -> list[ProbeItem]:
    """Gather probes for the requested domain(s)."""
    if domain == "all":
        items: list[ProbeItem] = []
        for cls in PROBES.values():
            items.extend(cls().get_probes())
        return items
    if domain not in PROBES:
        console.print(f"[red]Unknown domain: {domain}[/red]")
        sys.exit(1)
    return PROBES[domain]().get_probes()


def run_probe(adapter: ModelAdapter, probe: ProbeItem) -> ProbeResult:
    """Execute a single probe against the model."""
    system = (
        "You are being evaluated on reasoning consistency. "
        "Answer precisely and concisely. Show your reasoning."
    )
    prompt = f"{probe.setup}\n\nQuestion: {probe.question}"

    try:
        answer = adapter.generate(prompt, system=system)
    except Exception as e:
        return ProbeResult(
            probe=probe,
            model_answer=f"ERROR: {e}",
            is_correct=False,
            metadata={"error": str(e)},
        )

    # Run consistency checks
    consistency_answers: list[str] = []
    consistency_scores: list[bool] = []
    raw_responses = [answer]

    for check in probe.consistency_checks:
        followup = (
            f"Context: {probe.setup}\n\n"
            f"You previously answered: {answer}\n\n"
            f"Follow-up question: {check}"
        )
        try:
            check_answer = adapter.generate(followup, system=system)
            consistency_answers.append(check_answer)
            raw_responses.append(check_answer)
            consistency_scores.append(True)  # Requires judge model in production
        except Exception:
            consistency_answers.append("ERROR")
            consistency_scores.append(False)

    return ProbeResult(
        probe=probe,
        model_answer=answer,
        is_correct=True,  # Requires judge model in production
        consistency_answers=consistency_answers,
        consistency_scores=consistency_scores,
        raw_responses=raw_responses,
        metadata={"model": adapter.info.model_id},
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run GLITCH benchmark")
    parser.add_argument("--model", default="claude", help="Model provider")
    parser.add_argument("--model-id", default=None, help="Specific model ID")
    parser.add_argument("--domain", default="all", help="Domain to test")
    parser.add_argument("--output", default="results/glitch_results.json", help="Output path")
    parser.add_argument("--charts", action="store_true", help="Generate charts")
    args = parser.parse_args()

    console.print("[bold cyan]GLITCH Benchmark[/bold cyan] — Example Runner\n")

    adapter = get_adapter(args.model, args.model_id)
    console.print(f"Model: [bold]{adapter.info.model_id}[/bold]\n")

    probes = collect_probes(args.domain)
    console.print(f"Running [bold]{len(probes)}[/bold] probes...\n")

    results: list[ProbeResult] = []
    for i, probe in enumerate(probes, 1):
        console.print(f"  [{i}/{len(probes)}] {probe.id} ...", end=" ")
        result = run_probe(adapter, probe)
        status = "[green]OK[/green]" if result.is_correct else "[red]FAIL[/red]"
        console.print(status)
        results.append(result)

    # Analyze and score
    analyzer = GlitchAnalyzer()
    reports = analyzer.analyze_batch(results)

    scorer = WorldModelConsistencyScorer()
    score = scorer.score(
        results,
        model_name=adapter.info.name,
        model_id=adapter.info.model_id,
    )

    # Display
    console.print()
    print_score(score)
    print_glitch_reports(reports)

    # Save
    save_results_json(score, reports, args.output)

    if args.charts:
        chart_paths = generate_charts(score, Path(args.output).parent)
        for p in chart_paths:
            console.print(f"[dim]Chart: {p}[/dim]")

    console.print("\n[bold green]Done![/bold green]")


if __name__ == "__main__":
    main()
