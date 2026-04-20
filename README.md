# Generation of Chess Variants — Adaptive & Asymmetric Cell-DEVS

**Authors:** Hajar Assim 101232456, Hasib Khodayar 101225523

**Course:** SYSC 5104/4906G — Methodologies for Discrete Event Modelling and Simulation

**Instructor:** Dr. Gabriel Wainer

**Due Date:** April 23, 2026

**Track:** Project I(a) — Redefining and Expanding the Assignment 2 Model

---

## Introduction

This repository is the final-project extension of our Assignment 2 Cadmium v2 port of Fridenfalk's "Generation of Chess Variants" cellular automaton. The original model applied a modified Game of Life rule (B23/S23) on small wrapped grids to generate chess-board-like patterns. Assignment 2 exposed a hard limitation: the fixed 2-or-3-neighbor rule is calibrated for ~8-neighbor topologies, so chess-piece neighborhoods with larger reach (rook, bishop, queen) collapsed within 2–3 generations.

The final project adds six extensions:

1. **Adaptive density-based thresholds** — birth/survival conditions expressed as fractions of neighborhood size, so one rule family works across topologies of any cardinality.
2. **All five Fridenfalk rules** — B23/S23, B24/S24, B25/S25, B26/S26, and the non-contiguous B235/S235 (which required a gap-exclusion mechanism).
3. **Queen neighborhood** — never modeled in prior Cell-DEVS work.
4. **Accumulation-grid pipeline** — converts simulation output into static binary chess boards (Fridenfalk's original method).
5. **Board quality metrics** — quantitative evaluation (coverage, symmetry, connectivity, hole count).
6. **Asymmetric Cell-DEVS rule-zone model** — different regions of the board run different Fridenfalk rules simultaneously, using Cadmium's `AsymmCell` formalism with string cell IDs and per-cell neighborhood maps.

The full write-up is `FinalProject_Report.docx` / `.pdf`.

---

## Repository Structure

```
.
├── main/
│   ├── main.cpp                              # driver — dispatches to one of 3 models by JSON config
│   └── include/
│       ├── chessVariantState.hpp             # A2 fixed-threshold state (binary alive/dead)
│       ├── chessVariantCell.hpp              # A2 fixed-threshold cell (B23/S23)
│       ├── adaptiveChessVariantState.hpp     # adaptive state (binary + density fields + gap)
│       ├── adaptiveChessVariantCell.hpp      # adaptive cell (density-scaled thresholds)
│       └── asymmChessVariantCell.hpp         # asymmetric cell (string IDs, per-cell neighborhoods)
├── config/
│   ├── baseline/                             # 14 A2 scenarios (fixed B23/S23)
│   ├── adaptive/                             #  5 hand-tuned adaptive scenarios
│   ├── rules/rule{1..5}/                     # 25 Fridenfalk rule × piece configs (5 × 5)
│   └── asymmetric/                           # 12 rule-zone configs (3 layouts × 4 pieces)
├── scripts/
│   ├── generate_rule_configs.py              # emits config/rules/* and scripts/rules/*
│   ├── generate_asymmetric_configs.py        # emits config/asymmetric/* and scripts/asymmetric/*
│   ├── verify_asymmetric_configs.py          # structural validator for the 12 asymm configs
│   ├── accumulate_board.py                   # last-N-gen accumulation → binary chess board
│   ├── board_metrics.py                      # coverage / symmetry / connectivity / holes
│   ├── run_everything.sh                     # orchestrate: run all 56 + build metrics_summary.csv
│   ├── baseline/                             # per-scenario run scripts (baseline)
│   ├── adaptive/                             # per-scenario run scripts (adaptive)
│   ├── rules/rule{1..5}/                     # per-scenario run scripts (rule sweep)
│   └── asymmetric/                           # per-scenario run scripts (asymmetric)
├── logs/                                     # simulation CSV outputs (viewer-compatible)
├── simulation_videos/                        # screen recordings of representative scenarios
├── CMakeLists.txt
├── build_sim.sh
├── .gitattributes                            # enforces LF line endings on clone
└── README.md                                 # this file
```

---

## Prerequisites

- **C++20 compiler** (g++ 11+ or clang++ 14+)
- **CMake** 3.16+
- **Cadmium v2** (the `dev-rt` branch)
- **Python 3** for post-processing scripts
- **Linux-based environment** (Ubuntu, WSL Ubuntu, or DEVSsim server)

### Installing build tools (Ubuntu/WSL)

```bash
sudo apt-get update
sudo apt-get install -y g++ cmake python3
```

---

## Setup

### 1. Clone this repository

```bash
git clone https://github.com/hajar-assim/GenerationOfChessVariantsDEVs.git
cd GenerationOfChessVariantsDEVs
```

### 2. Clone Cadmium v2 (if not already installed)

```bash
cd ~
git clone https://github.com/SimulationEverywhere/cadmium_v2 -b dev-rt
cd cadmium_v2
git submodule update --init --recursive
```

> The submodule step pulls in `nlohmann/json`. Without it the build fails with `nlohmann/json.hpp: No such file or directory`.

### 3. Set the Cadmium path

```bash
export CADMIUM=~/cadmium_v2/include
```

On the DEVSsim servers Cadmium v2 is pre-installed and `$CADMIUM` is already configured.

---

## Building

```bash
bash build_sim.sh
```

Produces the executable at `bin/chess_variant`. The driver reads a config JSON and dispatches to one of three model types based on the `cells.default.model` field:

- `"chessVariant"` → `GridCellDEVSCoupled` with `ChessVariantCell` (fixed B23/S23)
- `"adaptiveChessVariant"` → `GridCellDEVSCoupled` with `AdaptiveChessVariantCell` (density-scaled)
- `"asymmChessVariant"` → `AsymmCellDEVSCoupled` with `AsymmChessVariantCell` (per-cell rule parameterization)

---

## Running Simulations

### Run a single scenario

```bash
./bin/chess_variant <config.json> [sim_time]
```

Examples:

```bash
./bin/chess_variant config/baseline/chessVariantKernel1_config.json 60
./bin/chess_variant config/adaptive/adaptiveQueen_8x8_config.json 60
./bin/chess_variant config/rules/rule3/rule3_rook_config.json 60
./bin/chess_variant config/asymmetric/asymm_r3_r5_bishop_config.json 60
```

Output is written to `logs/<scenario_name>_grid_log.csv`.

### Run a batch

```bash
bash scripts/baseline/run_all_scenarios.sh          # 14 scenarios
bash scripts/adaptive/run_all_adaptive_scenarios.sh #  5 scenarios
bash scripts/rules/run_all_rules.sh                 # 25 scenarios
bash scripts/asymmetric/run_all_asymm.sh            # 12 scenarios
```

### Run everything + collect metrics (recommended)

```bash
bash scripts/run_everything.sh
```

Runs all 56 scenarios, writes per-scenario CSV logs, aggregates into `logs/metrics_summary.csv`, and captures the combined stdout in `logs/run_everything.log`.

---

## Post-Processing

### Accumulation grid → binary chess board

```bash
python3 scripts/accumulate_board.py <log.csv> [--last N] [--threshold T] [--out FILE]
```

- `--last N` — number of final generations to accumulate (default 20)
- `--threshold T` — fraction of accumulated generations a cell must be alive to count as filled (default 0.5)
- `--out FILE` — output file (default stdout)

Example:

```bash
python3 scripts/accumulate_board.py logs/rule3_rook_grid_log.csv --out logs/rule3_rook_board.txt
```

### Board quality metrics

```bash
python3 scripts/board_metrics.py <board_file>
python3 scripts/board_metrics.py --from-log <log.csv> [--last N] [--threshold T]
```

Computes:

- **Coverage** — fraction of filled cells (ideal for a chess board: 0.500)
- **Symmetry** — average of horizontal, vertical, and 180° rotational symmetry (ideal: 1.000)
- **Connectivity** — number of 4-connected components of filled cells (ideal: 1)
- **Holes** — number of enclosed empty regions not touching the grid border (ideal: 0)

---

## Scenarios

### Group A — Baseline (A2, fixed B23/S23)

14 scenarios in `config/baseline/` covering the original four Fridenfalk kernels, Moore seed variations (glider, line, no-wrap, large), and chess-piece neighborhood experiments (bishop, rook, knight, multi-piece).

### Group B — Adaptive (hand-tuned density windows)

5 scenarios in `config/adaptive/`:

| Scenario | Grid | Window | Purpose |
|---|---|---|---|
| `adaptiveMoore_9x13` | 9×13 wrapped | [0.25, 0.375] | Validates adaptive reproduces B23/S23 on Moore |
| `adaptiveBishop_8x8` | 8×8 | [0.25, 0.375] | Bishop with Rule 1 window |
| `adaptiveRook_8x8` | 8×8 | [0.25, 0.375] | Rook — demonstrates viability recovery |
| `adaptiveQueen_8x8` | 8×8 | [0.15, 0.45] | Queen with wider tuned window |
| `adaptiveQueen_9x13` | 9×13 wrapped | [0.25, 0.375] | Queen on wrapped grid |

### Group C — Rule sweep (5 rules × 5 pieces)

25 scenarios in `config/rules/rule{1..5}/`:

| Rule | B/S | Density window | Gap |
|---|---|---|---|
| 1 | B23/S23 | [0.25, 0.375] | — |
| 2 | B24/S24 | [0.25, 0.50]  | — |
| 3 | B25/S25 | [0.25, 0.625] | — |
| 4 | B26/S26 | [0.25, 0.75]  | — |
| 5 | B235/S235 | [0.25, 0.625] | exclude density 0.5 |

Each rule runs against Moore, knight, bishop, rook, and queen neighborhoods. Regenerate with `python3 scripts/generate_rule_configs.py`.

### Group D — Asymmetric rule zones

12 scenarios in `config/asymmetric/`. Each 8×8 board is split into regions where different cells use different Fridenfalk rules.

**Zone layouts:**
- `r1_r3` — diagonal split: upper-left triangle runs Rule 1, lower-right runs Rule 3
- `r1_r2_r3_r4` — four quadrants, one rule each (1/2/3/4)
- `r3_r5` — top half runs contiguous Rule 3, bottom half runs non-contiguous Rule 5

**Piece topologies:** knight, bishop, rook, queen (4 per layout).

Validate with `python3 scripts/verify_asymmetric_configs.py`. Regenerate with `python3 scripts/generate_asymmetric_configs.py`.

---

## Visualization

Simulation logs are compatible with the Cell-DEVS Web Viewer at
**https://devssim.carleton.ca/cell-devs-viewer/**

1. Upload the JSON configuration file (e.g. `config/asymmetric/asymm_r3_r5_bishop_config.json`)
2. Upload the matching CSV (e.g. `logs/asymm_r3_r5_bishop_grid_log.csv`)
3. Step through generations or play the animation

Filled cells (`alive = 1`) render black; empty cells render white.

Screen recordings of representative scenarios are in `simulation_videos/`.

---

## Key Findings

The full analysis is in the report. Highlights:

- **Adaptive scaling** reproduces B23/S23 exactly on ~8-neighbor topologies (Moore, Knight) and recovers viability for the rook (from extinction at gen 2 → full 60-gen oscillation).
- **Rule 5's gap mechanism** produces meaningfully different dynamics from contiguous Rule 3 despite sharing the outer density range.
- **Bishop remains structurally constrained** regardless of rule — the colour-parity property of diagonal-only movement splits the 8×8 board into two independent halves.
- **Queen viability is seed-dependent** — wide density windows or larger seeds are required; narrow Rule 1 with a 7–8 cell seed is not sufficient to satisfy the 6+ live-neighbor threshold anywhere on the board.
- **Asymmetric rule zones produce measurably non-symmetric output** — symmetry scores drop from 1.0 (uniform) to the 0.4–0.8 range when zone boundaries run diagonally or through horizontal halves, confirming that the per-cell rule parameterization propagates into the accumulated board.
- **`asymm_r3_r5_bishop`** is the strongest asymmetric showcase: 48.4% coverage (near the 50% chess-board ideal), symmetry 0.427 (zone geometry clearly visible), sustained oscillation across all 60 generations.

---

## Asymmetric Cell-DEVS — Implementation & Visualization Notes

The asymmetric rule-zone model (`main/include/asymmChessVariantCell.hpp`) uses Cadmium's `AsymmCell<S,V>` formalism: cell IDs are strings (`"r3_c4"`) and each cell declares its own neighborhood as a `{neighborId: vicinity_weight}` map rather than inheriting from a grid shape. The transition logic is identical to the adaptive cell — what changes is that each cell's density thresholds are written directly into its JSON `state` block based on which zone it belongs to, so different regions of the board apply different Fridenfalk rules simultaneously.

**Web-viewer compatibility via `scripts/asymm_to_viewer.py`.** The Cell-DEVS Web Viewer (https://devssim.carleton.ca/cell-devs-viewer/) only supports `GridCell` models — it requires `scenario.shape` and expects cell IDs in `(r,c)` form, neither of which asymm configs have. The translator script rewrites an asymm log so IDs match the grid format (`r3_c4` → `(3,4)`) and emits a minimal stub config that the viewer will accept. Stubs are written to `logs/viewer_stubs/`. Simulation behavior is unchanged — this is purely a visualization adapter.

**Zone-colored visualization via `scripts/visualize_asymm.py`.** The web viewer shows only alive/dead in black/white, so the rule boundary is invisible no matter how many generations you scrub through. This script renders a matplotlib animation where each cell is tinted by its rule zone (Rule 1 light blue, Rule 3 yellow, Rule 5 purple, etc.) with alive cells overlaid as black dots. The boundary between zones is visible in every frame. Output is a `.gif` per scenario in `simulation_videos/`.

Usage:
```bash
python3 scripts/asymm_to_viewer.py --all     # upload stubs to the web viewer
python3 scripts/visualize_asymm.py --all     # zone-colored animations
```

---

## References

Fridenfalk, M. (2013). *Application of Cellular Automata for Generation of Chess Variants.* Uppsala University, Department of Game Design.

Wainer, G. A. (2009). *Discrete-Event Modeling and Simulation: A Practitioner's Approach.* CRC Press.

Cárdenas Rodríguez, R. (2022). *Cadmium v2: A C++ Simulation Framework for Cell-DEVS Models.* ARSLab, Carleton University. https://github.com/SimulationEverywhere/cadmium_v2

Original CD++ model: https://www.sce.carleton.ca/faculty/wainer/wbgraf/doku.php?id=model_samples:start
