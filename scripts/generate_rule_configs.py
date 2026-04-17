#!/usr/bin/env python3
"""Generate JSON configs for all 5 Fridenfalk rules x 5 piece types."""

import json
import os

# Fridenfalk rules mapped to adaptive density windows
# Rule 1: B23/S23, Rule 2: B24/S24, Rule 3: B25/S25, Rule 4: B26/S26
# Rule 5: B235/S235 (non-contiguous, uses gap to exclude count 4)
RULES = {
    1: {"birthLow": 0.25, "birthHigh": 0.375, "survivalLow": 0.25, "survivalHigh": 0.375},
    2: {"birthLow": 0.25, "birthHigh": 0.50,  "survivalLow": 0.25, "survivalHigh": 0.50},
    3: {"birthLow": 0.25, "birthHigh": 0.625, "survivalLow": 0.25, "survivalHigh": 0.625},
    4: {"birthLow": 0.25, "birthHigh": 0.75,  "survivalLow": 0.25, "survivalHigh": 0.75},
    # Rule 5: B235/S235 — non-contiguous. Range [2,5] with gap at 4.
    # Gap density 0.5 maps to count 4 on 8-neighbor topologies.
    5: {"birthLow": 0.25, "birthHigh": 0.625, "survivalLow": 0.25, "survivalHigh": 0.625,
        "birthGapLow": 0.50, "birthGapHigh": 0.50,
        "survivalGapLow": 0.50, "survivalGapHigh": 0.50},
}

# Neighbourhood definitions
MOORE_NEIGHBORHOOD = [{"type": "moore", "range": 1}]

KNIGHT_NEIGHBORHOOD = [{"type": "relative", "neighbors": [
    [0, 0],
    [-2, -1], [-2, 1], [-1, -2], [-1, 2],
    [1, -2], [1, 2], [2, -1], [2, 1]
]}]

BISHOP_NEIGHBORHOOD = [{"type": "relative", "neighbors": [
    [0, 0],
    [-1, -1], [-1, 1], [1, -1], [1, 1],
    [-2, -2], [-2, 2], [2, -2], [2, 2],
    [-3, -3], [-3, 3], [3, -3], [3, 3],
    [-4, -4], [-4, 4], [4, -4], [4, 4],
    [-5, -5], [-5, 5], [5, -5], [5, 5],
    [-6, -6], [-6, 6], [6, -6], [6, 6],
    [-7, -7], [-7, 7], [7, -7], [7, 7]
]}]

ROOK_NEIGHBORHOOD = [{"type": "relative", "neighbors": [
    [0, 0],
    [-1, 0], [-2, 0], [-3, 0], [-4, 0], [-5, 0], [-6, 0], [-7, 0],
    [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0],
    [0, -1], [0, -2], [0, -3], [0, -4], [0, -5], [0, -6], [0, -7],
    [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7]
]}]

QUEEN_NEIGHBORHOOD = [{"type": "relative", "neighbors": [
    [0, 0],
    # rook component (row + column)
    [-1, 0], [-2, 0], [-3, 0], [-4, 0], [-5, 0], [-6, 0], [-7, 0],
    [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0], [7, 0],
    [0, -1], [0, -2], [0, -3], [0, -4], [0, -5], [0, -6], [0, -7],
    [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [0, 7],
    # bishop component (diagonals)
    [-1, -1], [-1, 1], [1, -1], [1, 1],
    [-2, -2], [-2, 2], [2, -2], [2, 2],
    [-3, -3], [-3, 3], [3, -3], [3, 3],
    [-4, -4], [-4, 4], [4, -4], [4, 4],
    [-5, -5], [-5, 5], [5, -5], [5, 5],
    [-6, -6], [-6, 6], [6, -6], [6, 6],
    [-7, -7], [-7, 7], [7, -7], [7, 7]
]}]

# Piece configs: neighbourhood, grid, wrapped, seed
PIECES = {
    "moore": {
        "neighborhood": MOORE_NEIGHBORHOOD,
        "shape": [9, 13], "wrapped": True,
        "seed_name": "kernel1_seed",
        "seed_map": [[3, 6], [4, 5], [4, 6], [4, 7], [5, 6]]
    },
    "knight": {
        "neighborhood": KNIGHT_NEIGHBORHOOD,
        "shape": [8, 8], "wrapped": False,
        "seed_name": "knight_seed",
        "seed_map": [[3, 3], [3, 4], [4, 3], [4, 4]]
    },
    "bishop": {
        "neighborhood": BISHOP_NEIGHBORHOOD,
        "shape": [8, 8], "wrapped": False,
        "seed_name": "bishop_seed",
        "seed_map": [[2, 3], [3, 2], [4, 5], [5, 4], [3, 6], [6, 1]]
    },
    "rook": {
        "neighborhood": ROOK_NEIGHBORHOOD,
        "shape": [8, 8], "wrapped": False,
        "seed_name": "rook_seed",
        "seed_map": [[3, 2], [3, 3], [3, 4], [3, 5], [4, 3], [4, 4], [5, 3]]
    },
    "queen": {
        "neighborhood": QUEEN_NEIGHBORHOOD,
        "shape": [8, 8], "wrapped": False,
        "seed_name": "queen_seed",
        "seed_map": [[2, 3], [3, 2], [4, 5], [5, 4], [3, 6], [6, 1], [1, 5], [5, 1]]
    },
}

VIEWER = [{"colors": [[255, 255, 255], [0, 0, 0]], "breaks": [0, 0.5, 1], "field": "alive"}]

base_dir = os.path.join(os.path.dirname(__file__), "..")
config_dir = os.path.join(base_dir, "config", "rules")
script_dir = os.path.join(base_dir, "scripts", "rules")

generated_configs = []

for rule_num, thresholds in RULES.items():
    for piece_name, piece in PIECES.items():
        config_name = f"rule{rule_num}_{piece_name}"
        filename = f"{config_name}_config.json"
        rule_subdir = f"rule{rule_num}"

        state = {"alive": 0, **thresholds}
        seed_state = {"alive": 1, **thresholds}

        config = {
            "scenario": {
                "shape": piece["shape"],
                "origin": [0, 0],
                "wrapped": piece["wrapped"]
            },
            "cells": {
                "default": {
                    "delay": "transport",
                    "model": "adaptiveChessVariant",
                    "state": state,
                    "neighborhood": piece["neighborhood"]
                },
                piece["seed_name"]: {
                    "state": seed_state,
                    "cell_map": piece["seed_map"]
                }
            },
            "viewer": VIEWER
        }

        rule_config_dir = os.path.join(config_dir, rule_subdir)
        os.makedirs(rule_config_dir, exist_ok=True)
        filepath = os.path.join(rule_config_dir, filename)
        with open(filepath, "w") as f:
            json.dump(config, f, indent=2)
            f.write("\n")

        # Generate run script
        rule_script_dir = os.path.join(script_dir, rule_subdir)
        os.makedirs(rule_script_dir, exist_ok=True)
        script_name = f"run_{config_name}.sh"
        script_content = f"""#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running {config_name}..."
./bin/chess_variant config/rules/{rule_subdir}/{filename} 60
"""
        script_path = os.path.join(rule_script_dir, script_name)
        with open(script_path, "w") as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)

        generated_configs.append(config_name)
        print(f"  {filename}")

# Generate master run script (loop-based, uses subfolder paths)
rule_nums = sorted(RULES.keys())
master_script = "#!/bin/bash\n# Run all Fridenfalk rule scenarios (rules {}, all {} piece types)\n".format(
    "-".join(str(r) for r in rule_nums), len(PIECES))
master_script += "for r in {}; do\n".format(" ".join(str(r) for r in rule_nums))
master_script += '    for f in scripts/rules/rule${r}/run_*.sh; do\n'
master_script += '        bash "$f"\n'
master_script += '    done\n'
master_script += 'done\n'

master_path = os.path.join(script_dir, "run_all_rules.sh")
with open(master_path, "w") as f:
    f.write(master_script)
os.chmod(master_path, 0o755)

print(f"\nGenerated {len(generated_configs)} configs and run scripts")
print("Master script: scripts/run_all_rules.sh")
