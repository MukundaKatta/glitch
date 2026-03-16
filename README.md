# GLITCH

> *"A deja vu is usually a glitch in the Matrix. It happens when they change something."*
> — **Trinity**

---

**Detecting World Model Inconsistencies in Large Language Models**

`PROJECT STATUS: RESEARCH PHASE`

## Overview

In The Matrix, deja vu revealed that the simulation had been altered. LLMs build internal world models, but these models have inconsistencies — "glitches" where the model's reality breaks down.

Finding these glitches is scientifically valuable because they reveal HOW the model represents the world. This project systematically hunts for world model inconsistencies, then uses mechanistic interpretability to understand WHY each glitch occurs.

## Research Question

Can we find "glitches" in LLMs — inconsistencies in their world model that reveal the structure and limitations of their internal representations?

## Methodology

### 1. Glitch Probes Across 6 Domains

| Domain | Example Probe |
|--------|--------------|
| **Spatial** | "A is left of B, B is left of C. Is A left of C?" |
| **Temporal** | Ask about event ordering, then reverse it — does the model catch the contradiction? |
| **Causal** | Set up causal chains, then violate them — does the model notice? |
| **Physical** | Violate conservation laws, gravity, basic physics — at what point does the model object? |
| **Social** | Give inconsistent character motivations — does the model detect incoherence? |
| **Self** | Give the model contradictory information about itself — does it notice? |

### 2. Analysis
- Catalog glitches by type, severity, and frequency
- Mechanistic interpretability to trace each glitch to specific model components
- Test: do larger models have fewer glitches? Do some architectures have systematic blind spots?

### 3. World Model Consistency Score
A comprehensive metric that measures overall coherence of an LLM's world model.

### 4. Simulation Theory Connection
If we're in a simulation, what would the glitches look like? What do LLM glitches tell us about the structure of a simulated reality?

## Expected Outputs

- **Paper:** *"Deja Vu in the Machine: Detecting and Analyzing World Model Inconsistencies in Large Language Models"*
- **Benchmark:** `glitch-bench` — open-source world model consistency benchmark
- **Blog:** *"Finding Glitches in the Matrix: What LLM Failures Reveal About Artificial Reality"*

## Tech Stack

- Python 3.11+
- Multiple LLM APIs
- TransformerLens (mechanistic interpretability)
- Statistical analysis frameworks

---

*Part of the [Matrix Research Series](https://github.com/MukundaKatta) by [Officethree Technologies](https://github.com/MukundaKatta/Office3)*

**Mukunda Katta** · Officethree Technologies · 2026

> *"There is no spoon."*
