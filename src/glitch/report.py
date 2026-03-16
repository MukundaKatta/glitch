"""Report generation and visualization for GLITCH benchmark results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from glitch.analyzer import GlitchReport, Severity
from glitch.probes import ProbeDomain
from glitch.scorer import ComparisonReport, ConsistencyScore


console = Console()


def print_score(score: ConsistencyScore) -> None:
    """Print a formatted consistency score to the terminal."""
    grade_colors = {
        "A": "bold green", "A-": "green",
        "B+": "cyan", "B": "cyan", "B-": "blue",
        "C+": "yellow", "C": "yellow", "C-": "dark_orange",
        "D": "red", "F": "bold red",
    }
    grade_style = grade_colors.get(score.grade, "white")

    header = Text()
    header.append("GLITCH World Model Consistency Score\n", style="bold")
    header.append(f"Model: {score.model_name} ({score.model_id})\n")
    header.append(f"Overall: {score.overall:.2%}  Grade: ")
    header.append(score.grade, style=grade_style)

    console.print(Panel(header, title="[bold]GLITCH Benchmark[/bold]", border_style="cyan"))

    # Domain breakdown table
    table = Table(title="Domain Scores", show_header=True, header_style="bold magenta")
    table.add_column("Domain", style="cyan")
    table.add_column("Accuracy", justify="right")
    table.add_column("Consistency", justify="right")
    table.add_column("Composite", justify="right")
    table.add_column("Probes", justify="right")

    for domain_name, ds in sorted(score.domain_scores.items()):
        composite_color = "green" if ds.composite >= 0.7 else "yellow" if ds.composite >= 0.5 else "red"
        table.add_row(
            domain_name.replace("_", " ").title(),
            f"{ds.accuracy:.0%}",
            f"{ds.consistency:.0%}",
            f"[{composite_color}]{ds.composite:.0%}[/{composite_color}]",
            str(ds.num_probes),
        )

    console.print(table)

    console.print(
        f"\n[dim]Total probes: {score.total_probes} | "
        f"Correct: {score.total_correct} | "
        f"Consistent: {score.total_consistent}[/dim]"
    )


def print_comparison(report: ComparisonReport) -> None:
    """Print a formatted model comparison to the terminal."""
    console.print(
        Panel(
            f"[bold]{report.model_a}[/bold] vs [bold]{report.model_b}[/bold]\n"
            f"Winner: [bold green]{report.winner}[/bold green]",
            title="[bold]Model Comparison[/bold]",
            border_style="yellow",
        )
    )

    table = Table(title="Domain Comparison", show_header=True, header_style="bold magenta")
    table.add_column("Domain", style="cyan")
    table.add_column(report.model_a, justify="right")
    table.add_column(report.model_b, justify="right")
    table.add_column("Delta", justify="right")

    for domain_name, comp in sorted(report.domain_comparisons.items()):
        keys = list(comp.keys())
        val_a = comp[keys[0]]
        val_b = comp[keys[1]]
        delta = comp["delta"]
        delta_color = "green" if delta > 0 else "red" if delta < 0 else "white"
        table.add_row(
            domain_name.replace("_", " ").title(),
            f"{val_a:.0%}",
            f"{val_b:.0%}",
            f"[{delta_color}]{delta:+.0%}[/{delta_color}]",
        )

    console.print(table)
    console.print(f"\n[dim]{report.analysis}[/dim]")


def print_glitch_reports(reports: list[GlitchReport], *, verbose: bool = False) -> None:
    """Print glitch analysis reports to the terminal."""
    severity_styles = {
        Severity.MINOR: "dim",
        Severity.MODERATE: "yellow",
        Severity.SEVERE: "red",
        Severity.CRITICAL: "bold red",
    }

    failed = [r for r in reports if not r.passed]
    passed = [r for r in reports if r.passed]

    console.print(
        f"\n[bold]Glitch Analysis:[/bold] {len(passed)} passed, {len(failed)} failed "
        f"out of {len(reports)} probes\n"
    )

    if not failed:
        console.print("[bold green]No glitches detected![/bold green]")
        return

    table = Table(title="Detected Glitches", show_header=True, header_style="bold red")
    table.add_column("Probe", style="cyan", width=15)
    table.add_column("Domain", width=10)
    table.add_column("Type", width=15)
    table.add_column("Severity", width=10)
    table.add_column("Consistency", justify="right", width=12)

    for r in failed:
        style = severity_styles.get(r.severity, "white")
        table.add_row(
            r.probe_id,
            r.domain.value,
            r.glitch_type.value,
            f"[{style}]{r.severity.value.upper()}[/{style}]",
            f"{r.consistency_rate:.0%}",
        )

    console.print(table)

    if verbose:
        console.print("\n[bold]Detailed Analysis:[/bold]\n")
        for r in failed:
            style = severity_styles.get(r.severity, "white")
            console.print(
                Panel(
                    f"[bold]Expected:[/bold] {r.expected_answer}\n\n"
                    f"[bold]Got:[/bold] {r.model_answer}\n\n"
                    f"[bold]Analysis:[/bold] {r.analysis}",
                    title=f"[{style}]{r.probe_id} ({r.severity.value.upper()})[/{style}]",
                    border_style=style.split()[-1] if " " in style else style,
                )
            )


def save_results_json(
    score: ConsistencyScore,
    reports: list[GlitchReport],
    output_path: str | Path,
) -> Path:
    """Save results to a JSON file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    data: dict[str, Any] = {
        "score": score.model_dump(mode="json"),
        "reports": [r.model_dump(mode="json") for r in reports],
    }

    path.write_text(json.dumps(data, indent=2, default=str))
    console.print(f"[dim]Results saved to {path}[/dim]")
    return path


def generate_charts(score: ConsistencyScore, output_dir: str | Path) -> list[Path]:
    """Generate visualization charts for the benchmark results.

    Returns a list of paths to the generated chart files.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    generated: list[Path] = []

    # --- Radar chart of domain scores ---
    domains = sorted(score.domain_scores.keys())
    if domains:
        values = [score.domain_scores[d].composite for d in domains]
        labels = [d.replace("_", " ").title() for d in domains]

        angles = np.linspace(0, 2 * np.pi, len(domains), endpoint=False).tolist()
        values_closed = values + [values[0]]
        angles_closed = angles + [angles[0]]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        ax.fill(angles_closed, values_closed, alpha=0.25, color="teal")
        ax.plot(angles_closed, values_closed, color="teal", linewidth=2)
        ax.set_xticks(angles)
        ax.set_xticklabels(labels, size=11)
        ax.set_ylim(0, 1)
        ax.set_title(
            f"GLITCH World Model Profile\n{score.model_name} (Overall: {score.overall:.0%})",
            size=14,
            fontweight="bold",
            pad=20,
        )
        radar_path = output_path / "glitch_radar.png"
        fig.savefig(radar_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        generated.append(radar_path)

    # --- Bar chart of accuracy vs consistency per domain ---
    if domains:
        accuracies = [score.domain_scores[d].accuracy for d in domains]
        consistencies = [score.domain_scores[d].consistency for d in domains]
        x = np.arange(len(domains))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 6))
        bars1 = ax.bar(x - width / 2, accuracies, width, label="Accuracy", color="#2ecc71")
        bars2 = ax.bar(x + width / 2, consistencies, width, label="Consistency", color="#3498db")

        ax.set_ylabel("Score")
        ax.set_title(f"GLITCH Accuracy vs Consistency — {score.model_name}")
        ax.set_xticks(x)
        ax.set_xticklabels([d.replace("_", " ").title() for d in domains], rotation=30, ha="right")
        ax.legend()
        ax.set_ylim(0, 1.1)

        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.annotate(
                    f"{height:.0%}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=9,
                )

        bar_path = output_path / "glitch_bars.png"
        fig.savefig(bar_path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        generated.append(bar_path)

    return generated
