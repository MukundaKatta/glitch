"""GLITCH CLI — command-line interface for the world model consistency benchmark."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console

from glitch.probes import BaseProbe, ProbeDomain, ProbeItem, ProbeResult
from glitch.probes.spatial import SpatialProbe
from glitch.probes.temporal import TemporalProbe
from glitch.probes.causal import CausalProbe
from glitch.probes.physical import PhysicalProbe
from glitch.probes.social import SocialProbe
from glitch.probes.self_model import SelfModelProbe
from glitch.analyzer import GlitchAnalyzer
from glitch.scorer import WorldModelConsistencyScorer
from glitch.models import ModelAdapter, get_adapter
from glitch.report import (
    print_score,
    print_comparison,
    print_glitch_reports,
    save_results_json,
    generate_charts,
)

console = Console()

ALL_PROBES: dict[str, type[BaseProbe]] = {
    "spatial": SpatialProbe,
    "temporal": TemporalProbe,
    "causal": CausalProbe,
    "physical": PhysicalProbe,
    "social": SocialProbe,
    "self_model": SelfModelProbe,
}


def _get_probes(domain: str) -> list[ProbeItem]:
    """Collect probes for the specified domain(s)."""
    if domain == "all":
        probes: list[ProbeItem] = []
        for probe_cls in ALL_PROBES.values():
            probes.extend(probe_cls().get_probes())
        return probes

    if domain not in ALL_PROBES:
        console.print(
            f"[red]Unknown domain '{domain}'. "
            f"Available: {', '.join(ALL_PROBES.keys())}, all[/red]"
        )
        sys.exit(1)

    return ALL_PROBES[domain]().get_probes()


def _run_probe(adapter: ModelAdapter, probe: ProbeItem) -> ProbeResult:
    """Run a single probe against a model and evaluate the result."""
    system_prompt = (
        "You are being evaluated on reasoning consistency. "
        "Answer precisely and concisely. Show your reasoning."
    )

    full_prompt = f"{probe.setup}\n\nQuestion: {probe.question}"

    try:
        answer = adapter.generate(full_prompt, system=system_prompt)
    except Exception as e:
        console.print(f"[red]Error running probe {probe.id}: {e}[/red]")
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
        check_prompt = (
            f"Context: {probe.setup}\n\n"
            f"You previously answered: {answer}\n\n"
            f"Follow-up question: {check}"
        )
        try:
            check_answer = adapter.generate(check_prompt, system=system_prompt)
            consistency_answers.append(check_answer)
            raw_responses.append(check_answer)
            # Basic heuristic: check for contradictions with the main answer
            # In production, this would use a judge model or structured evaluation
            consistency_scores.append(True)  # Placeholder — requires judge evaluation
        except Exception:
            consistency_answers.append("ERROR")
            consistency_scores.append(False)

    # Basic correctness check — in production, use a judge model
    # For now, always mark as requiring manual evaluation
    is_correct = True  # Placeholder — requires judge evaluation

    return ProbeResult(
        probe=probe,
        model_answer=answer,
        is_correct=is_correct,
        consistency_answers=consistency_answers,
        consistency_scores=consistency_scores,
        raw_responses=raw_responses,
        metadata={"model": adapter.info.model_id},
    )


@click.group()
@click.version_option(version="0.1.0", prog_name="glitch")
def cli() -> None:
    """GLITCH — Detecting World Model Inconsistencies in LLMs.

    A benchmark for measuring how consistently LLMs model spatial, temporal,
    causal, physical, social, and self-referential reasoning.
    """
    pass


@cli.command()
@click.option(
    "--model",
    "-m",
    default="claude",
    help="Model provider: claude, openai, ollama",
)
@click.option(
    "--model-id",
    default=None,
    help="Specific model ID (e.g., claude-sonnet-4-20250514, gpt-4o)",
)
@click.option(
    "--domain",
    "-d",
    default="all",
    help="Domain to test: spatial, temporal, causal, physical, social, self_model, all",
)
@click.option("--output", "-o", default=None, help="Output JSON file path")
@click.option("--charts", is_flag=True, help="Generate visualization charts")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output with detailed analysis")
def run(
    model: str,
    model_id: str | None,
    domain: str,
    output: str | None,
    charts: bool,
    verbose: bool,
) -> None:
    """Run GLITCH probes against a model."""
    console.print("[bold cyan]GLITCH[/bold cyan] — World Model Consistency Benchmark\n")

    # Set up model adapter
    try:
        adapter = get_adapter(model, model_id)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    console.print(f"Model: [bold]{adapter.info.model_id}[/bold] ({adapter.info.provider})")

    # Collect probes
    probes = _get_probes(domain)
    console.print(f"Probes: [bold]{len(probes)}[/bold] across {domain} domain(s)\n")

    # Run probes
    results: list[ProbeResult] = []
    with console.status("[bold green]Running probes...") as status:
        for i, probe in enumerate(probes, 1):
            status.update(f"[bold green]Running probe {i}/{len(probes)}: {probe.id}")
            result = _run_probe(adapter, probe)
            results.append(result)

    # Analyze
    analyzer = GlitchAnalyzer()
    reports = analyzer.analyze_batch(results)

    # Score
    scorer = WorldModelConsistencyScorer()
    score = scorer.score(results, model_name=adapter.info.name, model_id=adapter.info.model_id)

    # Display results
    print_score(score)
    print_glitch_reports(reports, verbose=verbose)

    # Save results
    if output:
        save_results_json(score, reports, output)

    # Generate charts
    if charts:
        output_dir = Path(output).parent if output else Path("results")
        chart_paths = generate_charts(score, output_dir)
        for p in chart_paths:
            console.print(f"[dim]Chart saved: {p}[/dim]")


@cli.command()
@click.option("--input", "-i", "input_path", required=True, help="Results JSON file path")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def score(input_path: str, verbose: bool) -> None:
    """Score previously saved results."""
    path = Path(input_path)
    if not path.exists():
        console.print(f"[red]File not found: {path}[/red]")
        sys.exit(1)

    data = json.loads(path.read_text())
    score_data = data.get("score")
    if score_data:
        from glitch.scorer import ConsistencyScore

        cs = ConsistencyScore(**score_data)
        print_score(cs)
    else:
        console.print("[red]No score data found in file.[/red]")


@cli.command()
@click.option(
    "--models",
    "-m",
    required=True,
    help="Comma-separated model providers to compare (e.g., claude,openai)",
)
@click.option(
    "--domain",
    "-d",
    default="all",
    help="Domain to test",
)
@click.option("--output", "-o", default=None, help="Output JSON file path")
@click.option("--charts", is_flag=True, help="Generate comparison charts")
def compare(models: str, domain: str, output: str | None, charts: bool) -> None:
    """Compare two models on GLITCH probes."""
    model_names = [m.strip() for m in models.split(",")]
    if len(model_names) != 2:
        console.print("[red]Exactly two models must be specified for comparison.[/red]")
        sys.exit(1)

    console.print("[bold cyan]GLITCH[/bold cyan] — Model Comparison\n")

    probes = _get_probes(domain)
    scorer = WorldModelConsistencyScorer()
    analyzer = GlitchAnalyzer()
    scores: list = []

    for model_name in model_names:
        try:
            adapter = get_adapter(model_name)
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            sys.exit(1)

        console.print(f"\nRunning [bold]{adapter.info.model_id}[/bold]...")
        results: list[ProbeResult] = []
        with console.status(f"[bold green]Running probes on {adapter.info.model_id}..."):
            for probe in probes:
                result = _run_probe(adapter, probe)
                results.append(result)

        model_score = scorer.score(
            results,
            model_name=adapter.info.name,
            model_id=adapter.info.model_id,
        )
        scores.append(model_score)
        print_score(model_score)

    comparison = scorer.compare(scores[0], scores[1])
    print_comparison(comparison)

    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(comparison.model_dump(mode="json"), indent=2))
        console.print(f"[dim]Comparison saved to {output_path}[/dim]")


@cli.command(name="list")
@click.option(
    "--domain",
    "-d",
    default="all",
    help="Domain to list probes for",
)
def list_probes(domain: str) -> None:
    """List all available probes."""
    probes = _get_probes(domain)

    table = click.echo  # We'll use rich instead
    from rich.table import Table

    t = Table(title=f"GLITCH Probes ({domain})", show_header=True, header_style="bold magenta")
    t.add_column("ID", style="cyan", width=16)
    t.add_column("Domain", width=10)
    t.add_column("Category", width=20)
    t.add_column("Difficulty", justify="center", width=10)
    t.add_column("Checks", justify="center", width=8)

    for p in probes:
        diff_color = "green" if p.difficulty <= 2 else "yellow" if p.difficulty <= 3 else "red"
        t.add_row(
            p.id,
            p.domain.value,
            p.category,
            f"[{diff_color}]{p.difficulty}/5[/{diff_color}]",
            str(len(p.consistency_checks)),
        )

    console.print(t)
    console.print(f"\n[dim]Total: {len(probes)} probes[/dim]")


if __name__ == "__main__":
    cli()
