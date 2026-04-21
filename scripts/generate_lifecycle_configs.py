#!/usr/bin/env python3
"""Generate JSON configs for lifecycle chess variant scenarios.

Creates Cell-DEVS configurations using the continuous activation lifecycle
model. Each config pairs a chess piece neighborhood topology with a set of
lifecycle parameters (activation rate, decay rate, active duration) and
density thresholds.

The lifecycle model extends the adaptive model by replacing binary alive/dead
with a continuous activity value that progresses through four phases:
dormant -> activating -> active -> decaying -> dormant.
"""

import json
import os

ROWS, COLS = 8, 8

# chess piece neighborhood definitions (same offsets as adaptive model)
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

# lifecycle parameter sets to explore
LIFECYCLE_PARAMS = {
    "slow": {
        "activationRate": 0.1,
        "decayRate": 0.1,
        "activeDuration": 12,
    },
    "medium": {
        "activationRate": 0.2,
        "decayRate": 0.15,
        "activeDuration": 8,
    },
    "fast": {
        "activationRate": 0.35,
        "decayRate": 0.25,
        "activeDuration": 5,
    },
}

# density thresholds (Rule 1 - classic B23/S23 equivalent)
THRESHOLDS = {
    "birthLow": 0.25,
    "birthHigh": 0.375,
    "survivalLow": 0.25,
    "survivalHigh": 0.375,
}

# seed cells (same as adaptive model for fair comparison)
SEED_CELLS = [(3, 6), (4, 5), (4, 6), (4, 7), (5, 5), (5, 7), (6, 5), (6, 6), (6, 7)]

# viewer: gradient from black (dormant) through gray (activating/decaying) to white (active)
VIEWER = [
    {
        "colors": [
            [0, 0, 0],         # dormant (activity = 0)
            [80, 80, 80],      # low activity
            [160, 160, 160],   # mid activity
            [255, 255, 255]    # fully active (activity = 1)
        ],
        "breaks": [0, 0.33, 0.66, 1.0],
        "field": "activity"
    }
]


def build_config(piece_name, lifecycle_name, lifecycle_params):
    """Build a lifecycle config for one piece + lifecycle combo."""
    neighborhood = PIECE_NEIGHBORHOODS[piece_name]

    default_state = {
        "activity": 0.0,
        "phase": 0,
        "stepsInPhase": 0,
        **lifecycle_params,
        **THRESHOLDS,
    }

    # seed cells start in active phase
    seed_state = {
        "activity": 1.0,
        "phase": 2,
        "stepsInPhase": 0,
        **lifecycle_params,
        **THRESHOLDS,
    }

    config = {
        "scenario": {
            "shape": [ROWS, COLS],
            "origin": [0, 0],
            "wrapped": False
        },
        "cells": {
            "default": {
                "delay": "transport",
                "model": "lifecycleChessVariant",
                "state": default_state,
                "neighborhood": neighborhood
            },
            "seeds": {
                "state": seed_state,
                "cell_map": SEED_CELLS
            }
        },
        "viewer": VIEWER
    }

    return config


# generate configs and run scripts
base_dir = os.path.join(os.path.dirname(__file__), "..")
config_dir = os.path.join(base_dir, "config", "lifecycle")
script_dir = os.path.join(base_dir, "scripts", "lifecycle")

os.makedirs(config_dir, exist_ok=True)
os.makedirs(script_dir, exist_ok=True)

generated = []

for lifecycle_name, lifecycle_params in LIFECYCLE_PARAMS.items():
    for piece_name in PIECE_NEIGHBORHOODS:
        config_name = f"lifecycle_{lifecycle_name}_{piece_name}"
        filename = f"{config_name}_config.json"

        config = build_config(piece_name, lifecycle_name, lifecycle_params)

        filepath = os.path.join(config_dir, filename)
        with open(filepath, "w") as f:
            json.dump(config, f, indent=2)
            f.write("\n")

        # run script (60 steps to see full lifecycle waves)
        script_name = f"run_{config_name}.sh"
        script_content = f"""#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running {config_name}..."
./bin/chess_variant config/lifecycle/{filename} 60
"""
        script_path = os.path.join(script_dir, script_name)
        with open(script_path, "w") as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)

        generated.append(config_name)
        print(f"  {filename}")

# master run script
master = "#!/bin/bash\n# Run all lifecycle scenarios\n"
master += "for f in scripts/lifecycle/run_lifecycle_*.sh; do\n"
master += '    bash "$f"\n'
master += "done\n"
master_path = os.path.join(script_dir, "run_all_lifecycle.sh")
with open(master_path, "w") as f:
    f.write(master)
os.chmod(master_path, 0o755)

print(f"\nGenerated {len(generated)} lifecycle configs and run scripts")
