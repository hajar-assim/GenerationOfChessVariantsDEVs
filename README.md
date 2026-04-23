# Generation of Chess Variants — Adaptive Cell-DEVS Extensions

**Authors:** Hajar Assim (101232456), Hasib Khodayar (101225523)

**Course:** SYSC 5104/4906G — Methodologies for Discrete Event Modelling and Simulation

**Instructor:** Dr. Gabriel Wainer

**Due Date:** April 23, 2026

**Track:** Project I(a) — Redefining and Expanding the Assignment 2 Model

---

## Introduction

This repository extends our Assignment 2 Cadmium v2 port of Fridenfalk's "Generation of Chess Variants" cellular automaton. The original model applied a modified Game of Life rule (B23/S23) on small wrapped grids. Assignment 2 exposed a hard limitation: the fixed 2-or-3-neighbor rule is calibrated for ~8-neighbor topologies, so chess-piece neighborhoods with larger reach (rook, bishop, queen) collapsed within 2-3 generations.

The core contribution is **adaptive density-scaled thresholds** that express birth/survival conditions as fractions of the neighborhood size, making Fridenfalk's rules work across all chess-piece topologies. On top of this we build six extensions:

1. **Adaptive density-based thresholds** — birth/survival as fractions of neighborhood size.
2. **All five Fridenfalk rules** — B23/S23 through B26/S26 plus the non-contiguous B235/S235 with a gap-exclusion mechanism.
3. **Asymmetric Cell-DEVS rule zones** — different regions of the board run different Fridenfalk rules simultaneously using Cadmium's `AsymmCell` formalism.
4. **Line-of-sight blocking** — sliding pieces (bishop, rook, queen) cannot see past live cells on straight lines, making the effective neighborhood dynamic.
5. **Continuous-activity lifecycle model** — four-phase cell dynamics (dormant, activating, active, decaying) with continuous activity values, enabling wavefront visualization.
6. **Board control influence analysis** — experimental model simulating territorial control via piece-movement-pattern influence projection with propagation.
7. **Post-processing pipeline** — accumulation grids and board-quality metrics (coverage, symmetry, connectivity, hole count).

The full write-up is `ChessVariantGeneration_CellDEVS_Report.docx` in the repository root.

---

## Repository Structure

```
.
├── main/
│   ├── main.cpp                              # driver — dispatches to one of 6 models by JSON config
│   └── include/
│       ├── chessVariantState.hpp             # A2 fixed-threshold state (binary alive/dead)
│       ├── chessVariantCell.hpp              # A2 fixed-threshold cell (B23/S23)
│       ├── adaptiveChessVariantState.hpp     # adaptive state (density thresholds + gap fields)
│       ├── adaptiveChessVariantCell.hpp      # adaptive cell (density-scaled thresholds)
│       ├── asymmChessVariantCell.hpp         # asymmetric cell (string IDs, per-cell neighborhoods)
│       ├── losChessVariantCell.hpp           # line-of-sight blocking cell for sliding pieces
│       ├── lifecycleChessVariantState.hpp    # continuous activity + 4-phase state
│       ├── lifecycleChessVariantCell.hpp     # lifecycle transition (dormant/activating/active/decaying)
│       ├── boardControlState.hpp             # board control state (piece type, influence, control)
│       └── boardControlCell.hpp              # board control cell (influence projection + propagation)
├── config/
│   ├── baseline/                             # 14 A2 scenarios (fixed B23/S23)
│   ├── adaptive/                             #  5 hand-tuned adaptive scenarios
│   ├── rules/rule{1..5}/                     # 25 Fridenfalk rule x piece configs (5 rules x 5 pieces)
│   ├── asymmetric/                           # 12 rule-zone configs (3 layouts x 4 pieces)
│   ├── los/                                  #  9 line-of-sight configs (3 rules x 3 sliding pieces)
│   ├── lifecycle/                            # 15 lifecycle configs (3 speeds x 5 topologies)
│   └── board_control/                        #  5 chess-position influence analysis configs
├── scripts/
│   ├── generate_rule_configs.py              # emits config/rules/* and scripts/rules/*
│   ├── generate_asymmetric_configs.py        # emits config/asymmetric/* and scripts/asymmetric/*
│   ├── generate_lifecycle_configs.py         # emits config/lifecycle/* and scripts/lifecycle/*
│   ├── generate_los_configs.py              # emits config/los/* and scripts/los/*
│   ├── generate_board_control_configs.py    # emits config/board_control/* and scripts/board_control/*
│   ├── accumulate_board.py                   # last-N-gen accumulation -> binary chess board
│   ├── board_metrics.py                      # coverage / symmetry / connectivity / holes
│   ├── asymm_to_viewer.py                    # converts asymm logs to web-viewer-compatible format
│   ├── visualize_asymm.py                    # zone-colored matplotlib animation for asymm scenarios
│   ├── run_everything.sh                     # orchestrate: run all scenarios + build metrics_summary.csv
│   ├── baseline/                             # per-scenario run scripts (baseline)
│   ├── adaptive/                             # per-scenario run scripts (adaptive)
│   ├── rules/rule{1..5}/                     # per-scenario run scripts (rule sweep)
│   ├── asymmetric/                           # per-scenario run scripts (asymmetric)
│   ├── los/                                  # per-scenario run scripts (line-of-sight)
│   ├── lifecycle/                            # per-scenario run scripts (lifecycle)
│   └── board_control/                        # per-scenario run scripts (board control)
├── logs/                                     # simulation CSV outputs organized by model type
│   ├── baseline/
│   ├── adaptive/
│   ├── rule{1..5}/
│   ├── asymmetric/
│   ├── los/
│   ├── lifecycle/
│   ├── board_control/
│   └── metrics_summary.csv                   # aggregated board-quality metrics
├── simulation_videos/                        # screen recordings of representative scenarios
├── report/                                   # final project report (.docx and .pdf)
├── CMakeLists.txt
├── build_sim.sh
└── README.md
```

---

## Prerequisites

- **C++20 compiler** (g++ 11+ or clang++ 14+)
- **CMake** 3.16+
- **Cadmium v2** (the `dev-rt` branch)
- **Python 3** for config generation and post-processing scripts
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

Produces the executable at `bin/chess_variant`. The driver reads a config JSON and dispatches to one of six model types based on the `cells.default.model` field:

| Model string | Coupled model | Cell class | State type |
|---|---|---|---|
| `chessVariant` | `GridCellDEVSCoupled` | `ChessVariantCell` | `ChessVariantState` |
| `adaptiveChessVariant` | `GridCellDEVSCoupled` | `AdaptiveChessVariantCell` | `AdaptiveChessVariantState` |
| `asymmChessVariant` | `AsymmCellDEVSCoupled` | `AsymmChessVariantCell` | `AdaptiveChessVariantState` |
| `losChessVariant` | `GridCellDEVSCoupled` | `LOSChessVariantCell` | `AdaptiveChessVariantState` |
| `lifecycleChessVariant` | `GridCellDEVSCoupled` | `LifecycleChessVariantCell` | `LifecycleChessVariantState` |
| `boardControl` | `GridCellDEVSCoupled` | `BoardControlCell` | `BoardControlState` |

---

## Running Simulations

### Run a single scenario

```bash
./bin/chess_variant <config.json> [sim_time]
```

Examples:

```bash
./bin/chess_variant config/baseline/chessVariantKernel1_config.json 60
./bin/chess_variant config/adaptive/adaptiveRook_8x8_config.json 60
./bin/chess_variant config/rules/rule3/rule3_rook_config.json 60
./bin/chess_variant config/asymmetric/asymm_r3_r5_bishop_config.json 60
./bin/chess_variant config/los/los_rule1_bishop_config.json 60
./bin/chess_variant config/lifecycle/lifecycle_medium_moore_config.json 60
./bin/chess_variant config/board_control/board_control_starting_position_config.json 30
```

Output is automatically routed to `logs/<subdir>/<scenario>_grid_log.csv`, mirroring the config directory structure.

### Run a batch

```bash
bash scripts/baseline/run_all_scenarios.sh           # 14 baseline scenarios
bash scripts/adaptive/run_all_adaptive_scenarios.sh   #  5 adaptive scenarios
bash scripts/rules/run_all_rules.sh                   # 25 rule sweep scenarios
bash scripts/asymmetric/run_all_asymm.sh              # 12 asymmetric scenarios
bash scripts/los/run_all_los.sh                       #  9 LoS scenarios
bash scripts/lifecycle/run_all_lifecycle.sh            # 15 lifecycle scenarios
bash scripts/board_control/run_all_board_control.sh   #  5 board control scenarios
```

### Run everything + collect metrics

```bash
bash scripts/run_everything.sh
```

Runs all 85 scenarios, writes per-scenario CSV logs, aggregates board-quality metrics into `logs/metrics_summary.csv`, and captures combined stdout in `logs/run_everything.log`.

---

## Post-Processing

### Accumulation grid -> binary chess board

```bash
python3 scripts/accumulate_board.py <log.csv> [--last N] [--threshold T] [--out FILE]
```

- `--last N` — number of final generations to accumulate (default 20)
- `--threshold T` — fraction of accumulated generations a cell must be alive to count as filled (default 0.5)
- `--out FILE` — output file (default stdout)

Example:

```bash
python3 scripts/accumulate_board.py logs/rule3/rule3_rook_grid_log.csv --out logs/rule3_rook_board.txt
```

### Board quality metrics

```bash
python3 scripts/board_metrics.py <board_file>
python3 scripts/board_metrics.py --from-log <log.csv> [--last N] [--threshold T]
```

Computes:

- **Coverage** — fraction of filled cells (ideal for a chess board: 0.500)
- **Symmetry** — average of horizontal, vertical, and 180-degree rotational symmetry (ideal: 1.000)
- **Connectivity** — number of 4-connected components of filled cells (ideal: 1)
- **Holes** — number of enclosed empty regions not touching the grid border

---

## Scenarios (85 total)

### Baseline (14 configs)
A2 scenarios in `config/baseline/` covering original Fridenfalk kernels, seed variations, and chess-piece neighborhood experiments.

### Adaptive (5 configs)
Hand-tuned density windows in `config/adaptive/`. Key scenario: `adaptiveRook_8x8` demonstrates viability recovery (0.031 -> 0.875 coverage vs baseline).

### Rule sweep (25 configs)
5 Fridenfalk rules x 5 piece topologies in `config/rules/rule{1..5}/`. Regenerate with `python3 scripts/generate_rule_configs.py`.

### Asymmetric rule zones (12 configs)
3 zone layouts x 4 pieces in `config/asymmetric/`. Regenerate with `python3 scripts/generate_asymmetric_configs.py`.

### Line-of-sight (9 configs)
3 rules x 3 sliding pieces in `config/los/`. Regenerate with `python3 scripts/generate_los_configs.py`.

### Lifecycle (15 configs)
3 speed variants x 5 topologies in `config/lifecycle/`. Regenerate with `python3 scripts/generate_lifecycle_configs.py`.

### Board control (5 configs)
Chess-position influence analysis in `config/board_control/`. Regenerate with `python3 scripts/generate_board_control_configs.py`.

---

## Visualization

Simulation logs are compatible with the **Cell-DEVS Web Viewer** at
https://devssim.carleton.ca/cell-devs-viewer/

1. Upload the JSON configuration file
2. Upload the matching CSV log file
3. Step through generations or play the animation

For asymmetric scenarios, the web viewer requires grid-format cell IDs. Use the converter:
```bash
python3 scripts/asymm_to_viewer.py --all
```
This writes viewer-compatible stubs to `logs/viewer_stubs/`.

For zone-colored visualizations of asymmetric scenarios:
```bash
python3 scripts/visualize_asymm.py --all
```

---

## Key Findings

- **Adaptive rook recovery** — fixed B23/S23 rook goes extinct at gen 3 (0.031 coverage); adaptive density sustains 60 gens (0.875 coverage). Same seed, same topology.
- **Rule 3 Moore near-ideal** — 0.496 coverage, 1.000 symmetry, within 0.4% of the theoretical 50% chess board.
- **Rule 5 gap mechanism** — produces 11 holes vs Rule 3's 0, despite identical outer density range.
- **Asymmetric zone boundaries** — symmetry drops from 1.000 to 0.427 when different zones run different rules.
- **LoS self-shielding** — bishop Rule 1 revives from 0.000 (extinct) to 0.125 with line-of-sight blocking.
- **Bishop colour-parity binding** — rule4_bishop has 0.500 coverage but 32 components and 18 holes due to diagonal-only reach.
- **Lifecycle rook invariant** — all three speed variants produce identical metrics (0.375 coverage).

Full analysis in the project report.

---

## References

Fridenfalk, P. (2023). Procedural Generation of Game Boards Using Cellular Automata with Conway's Game of Life Variants. International Journal of Computer Games Technology.

Wainer, G. A. (2009). Discrete-Event Modeling and Simulation: A Practitioner's Approach. CRC Press.

Cadmium v2: A Cell-DEVS Simulator. ARSLab, Carleton University. https://github.com/SimulationEverywhere/cadmium_v2

Cell-DEVS Web Viewer. ARSLab, Carleton University. https://devssim.carleton.ca/cell-devs-viewer/
