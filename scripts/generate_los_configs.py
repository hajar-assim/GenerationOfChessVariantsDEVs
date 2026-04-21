#!/usr/bin/env python3
"""Generate JSON configs for line-of-sight chess variant scenarios.

Creates Cell-DEVS configurations using the LOS blocking model.
This model extends the adaptive model by adding line-of-sight checks
for sliding piece neighborhoods (bishop, rook, queen). A live cell
between two cells on the same line blocks the connection, making
the effective neighborhood dynamic.

Only generates configs for sliding piece topologies (bishop, rook, queen)
since Moore and knight neighborhoods have no straight-line paths to block.
Standard adaptive configs are generated for Moore and knight as baselines.
"""

import json
import os

ROWS, COLS = 8, 8

# sliding piece neighborhoods (these benefit from LOS blocking)
SLIDING_NEIGHBORHOODS = {
    "bishop": [{"type": "relative", "neighbors": (
        [[0, 0]] +
        [[d * i, e * i] for i in range(1, 8)
         for d, e in [(-1, -1), (-1, 1), (1, -1), (1, 1)]]
    )}],
    "rook": [{"type": "relative", "neighbors": (
        [[0, 0]] +
        [[i, 0] for i in range(-7, 8) if i != 0] +
        [[0, i] for i in range(-7, 8) if i != 0]
    )}],
    "queen": [{"type": "relative", "neighbors": (
        [[0, 0]] +
        [[d * i, e * i] for i in range(1, 8)
         for d, e in [(-1, -1), (-1, 1), (1, -1), (1, 1)]] +
        [[i, 0] for i in range(-7, 8) if i != 0] +
        [[0, i] for i in range(-7, 8) if i != 0]
    )}],
}

# Fridenfalk rules (same as adaptive model)
RULES = {
    1: {"birthLow": 0.25, "birthHigh": 0.375, "survivalLow": 0.25, "survivalHigh": 0.375},
    2: {"birthLow": 0.25, "birthHigh": 0.50,  "survivalLow": 0.25, "survivalHigh": 0.50},
    3: {"birthLow": 0.25, "birthHigh": 0.625, "survivalLow": 0.25, "survivalHigh": 0.625},
}

# seed pattern — 9-cell cluster, same as adaptive model for direct comparison.
# showcase subset of LOS scenarios: 3 rules x 3 sliding pieces = 9 configs total.
# (the dense/sparse ablations were dropped in favour of a focused 3x3 demo)
SEED_PATTERN = [(3, 6), (4, 5), (4, 6), (4, 7), (5, 5), (5, 7), (6, 5), (6, 6), (6, 7)]

VIEWER = [{"colors": [[255, 255, 255], [0, 0, 0]], "breaks": [0, 0.5, 1], "field": "alive"}]


def build_config(piece_name, rule_num, rule_thresholds, seed_cells):
    """Build a LOS config for one piece + rule combo."""
    neighborhood = SLIDING_NEIGHBORHOODS[piece_name]

    default_state = {"alive": 0, **rule_thresholds}
    seed_state = {"alive": 1, **rule_thresholds}

    return {
        "scenario": {
            "shape": [ROWS, COLS],
            "origin": [0, 0],
            "wrapped": False
        },
        "cells": {
            "default": {
                "delay": "transport",
                "model": "losChessVariant",
                "state": default_state,
                "neighborhood": neighborhood
            },
            "seeds": {
                "state": seed_state,
                "cell_map": seed_cells
            }
        },
        "viewer": VIEWER
    }


# generate configs and run scripts
base_dir = os.path.join(os.path.dirname(__file__), "..")
config_dir = os.path.join(base_dir, "config", "los")
script_dir = os.path.join(base_dir, "scripts", "los")

os.makedirs(config_dir, exist_ok=True)
os.makedirs(script_dir, exist_ok=True)

generated = []

for rule_num, rule_thresholds in RULES.items():
    for piece_name in SLIDING_NEIGHBORHOODS:
        config_name = f"los_rule{rule_num}_{piece_name}"
        filename = f"{config_name}_config.json"

        config = build_config(piece_name, rule_num, rule_thresholds, SEED_PATTERN)

        filepath = os.path.join(config_dir, filename)
        with open(filepath, "w", newline="\n") as f:
            json.dump(config, f, indent=2)
            f.write("\n")

        script_name = f"run_{config_name}.sh"
        script_content = f"""#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running {config_name}..."
./bin/chess_variant config/los/{filename} 60
"""
        script_path = os.path.join(script_dir, script_name)
        with open(script_path, "w", newline="\n") as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)

        generated.append(config_name)
        print(f"  {filename}")

# master run script
master = "#!/bin/bash\n# Run all LOS scenarios\n"
master += "for f in scripts/los/run_los_*.sh; do\n"
master += '    bash \"$f\"\n'
master += "done\n"
master_path = os.path.join(script_dir, "run_all_los.sh")
with open(master_path, "w", newline="\n") as f:
    f.write(master)
os.chmod(master_path, 0o755)

print(f"\nGenerated {len(generated)} LOS configs and run scripts")
