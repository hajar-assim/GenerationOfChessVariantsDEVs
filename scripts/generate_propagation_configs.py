#!/usr/bin/env python3
"""Generate JSON configs for propagation chess variant scenarios.

Creates Cell-DEVS configurations using the influence propagation model.
This model simulates how territorial control spreads across a chessboard
through different piece movement topologies.

Cells cycle through neutral -> active -> exhausted -> neutral, with
active cells spreading influence to their neighbors. The wavefront
shape depends on the piece topology: rooks spread along ranks/files,
bishops along diagonals, queens in all directions, etc.
"""

import json
import os

ROWS, COLS = 8, 8

# chess piece neighborhood definitions
PIECE_NEIGHBORHOODS = {
    "moore": [{"type": "moore", "range": 1}],
    "knight": [{"type": "relative", "neighbors": [
        [0, 0], [-2, -1], [-2, 1], [-1, -2], [-1, 2],
        [1, -2], [1, 2], [2, -1], [2, 1]
    ]}],
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

# propagation parameter sets
PROPAGATION_PARAMS = {
    "slow": {
        "activeDuration": 6,
        "decayRate": 0.15,
        "spreadThreshold": 0.05,
    },
    "fast": {
        "activeDuration": 3,
        "decayRate": 0.3,
        "spreadThreshold": 0.05,
    },
}

# seed patterns — origin points where influence starts spreading from
SEED_PATTERNS = {
    # single corner origin — shows how wavefront expands from one point
    "corner": [(0, 0)],
    # center origin — shows symmetric expansion
    "center": [(3, 3), (3, 4), (4, 3), (4, 4)],
    # two opposing corners — shows how wavefronts interact when they meet
    "opposing": [(0, 0), (7, 7)],
}

# viewer: gradient showing propagation wave
VIEWER = [
    {
        "colors": [
            [0, 0, 0],         # neutral (activity = 0)
            [80, 80, 80],      # low activity (exhausted, decaying)
            [160, 160, 160],   # mid activity
            [255, 255, 255]    # fully active (activity = 1)
        ],
        "breaks": [0, 0.33, 0.66, 1.0],
        "field": "activity"
    }
]


def build_config(piece_name, prop_params, seed_cells):
    """Build a propagation config for one piece + parameter combo."""
    neighborhood = PIECE_NEIGHBORHOODS[piece_name]

    default_state = {
        "activity": 0.0,
        "phase": 0,
        "stepsInPhase": 0,
        **prop_params,
    }

    # seed cells start active
    seed_state = {
        "activity": 1.0,
        "phase": 1,
        "stepsInPhase": 0,
        **prop_params,
    }

    return {
        "scenario": {
            "shape": [ROWS, COLS],
            "origin": [0, 0],
            "wrapped": False
        },
        "cells": {
            "default": {
                "delay": "transport",
                "model": "propagationChessVariant",
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
config_dir = os.path.join(base_dir, "config", "propagation")
script_dir = os.path.join(base_dir, "scripts", "propagation")

os.makedirs(config_dir, exist_ok=True)
os.makedirs(script_dir, exist_ok=True)

generated = []

for seed_name, seed_cells in SEED_PATTERNS.items():
    for prop_name, prop_params in PROPAGATION_PARAMS.items():
        for piece_name in PIECE_NEIGHBORHOODS:
            config_name = f"prop_{seed_name}_{prop_name}_{piece_name}"
            filename = f"{config_name}_config.json"

            config = build_config(piece_name, prop_params, seed_cells)

            filepath = os.path.join(config_dir, filename)
            with open(filepath, "w") as f:
                json.dump(config, f, indent=2)
                f.write("\n")

            script_name = f"run_{config_name}.sh"
            script_content = f"""#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running {config_name}..."
./bin/chess_variant config/propagation/{filename} 60
"""
            script_path = os.path.join(script_dir, script_name)
            with open(script_path, "w") as f:
                f.write(script_content)
            os.chmod(script_path, 0o755)

            generated.append(config_name)
            print(f"  {filename}")

# master run script
master = "#!/bin/bash\n# Run all propagation scenarios\n"
master += "for f in scripts/propagation/run_prop_*.sh; do\n"
master += '    bash "$f"\n'
master += "done\n"
master_path = os.path.join(script_dir, "run_all_propagation.sh")
with open(master_path, "w") as f:
    f.write(master)
os.chmod(master_path, 0o755)

print(f"\nGenerated {len(generated)} propagation configs and run scripts")
