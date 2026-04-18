#!/usr/bin/env python3
"""Generate asymmetric Cell-DEVS configs for rule-zone scenarios.

Each config enumerates every cell on an 8x8 board explicitly, with string IDs
of the form "rR_cC". A cell's density thresholds come from which zone it sits
in (per-cell state overrides), and its neighborhood is the chess-piece move
set filtered to valid grid coordinates.

Produces 12 configs total: 3 zone layouts x 4 piece types (knight, bishop,
rook, queen). Moore is omitted — the per-cell rule dispatch is only
interesting when the neighborhood reaches across zone boundaries.
"""

import json
import os

GRID_SIZE = 8

# Rule density windows (same as generate_rule_configs.py)
RULES = {
    1: {"birthLow": 0.25, "birthHigh": 0.375, "survivalLow": 0.25, "survivalHigh": 0.375,
        "birthGapLow": -1, "birthGapHigh": -1, "survivalGapLow": -1, "survivalGapHigh": -1},
    2: {"birthLow": 0.25, "birthHigh": 0.50,  "survivalLow": 0.25, "survivalHigh": 0.50,
        "birthGapLow": -1, "birthGapHigh": -1, "survivalGapLow": -1, "survivalGapHigh": -1},
    3: {"birthLow": 0.25, "birthHigh": 0.625, "survivalLow": 0.25, "survivalHigh": 0.625,
        "birthGapLow": -1, "birthGapHigh": -1, "survivalGapLow": -1, "survivalGapHigh": -1},
    4: {"birthLow": 0.25, "birthHigh": 0.75,  "survivalLow": 0.25, "survivalHigh": 0.75,
        "birthGapLow": -1, "birthGapHigh": -1, "survivalGapLow": -1, "survivalGapHigh": -1},
    5: {"birthLow": 0.25, "birthHigh": 0.625, "survivalLow": 0.25, "survivalHigh": 0.625,
        "birthGapLow": 0.50, "birthGapHigh": 0.50,
        "survivalGapLow": 0.50, "survivalGapHigh": 0.50},
}

# Zone layouts: (r, c) -> rule number. GRID_SIZE=8 assumed.
def zone_r1_r3(r, c):
    # diagonal split: upper-left triangle = Rule 1, lower-right = Rule 3
    return 1 if r + c < GRID_SIZE else 3

def zone_r1_r2_r3_r4(r, c):
    # four quadrants, one rule each
    half = GRID_SIZE // 2
    if r < half and c < half:  return 1
    if r < half and c >= half: return 2
    if r >= half and c < half: return 3
    return 4

def zone_r3_r5(r, c):
    # top half = contiguous Rule 3, bottom half = non-contiguous Rule 5 (gap at 0.5)
    return 3 if r < GRID_SIZE // 2 else 5

ZONE_LAYOUTS = {
    "r1_r3":       zone_r1_r3,
    "r1_r2_r3_r4": zone_r1_r2_r3_r4,
    "r3_r5":       zone_r3_r5,
}

# Neighborhood offsets per piece type (self is added separately).
def knight_offsets():
    return [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]

def bishop_offsets():
    return [(dr, dc)
            for k in range(1, GRID_SIZE)
            for dr, dc in [(-k,-k), (-k,k), (k,-k), (k,k)]]

def rook_offsets():
    return ([(-k, 0) for k in range(1, GRID_SIZE)]
          + [( k, 0) for k in range(1, GRID_SIZE)]
          + [(0, -k) for k in range(1, GRID_SIZE)]
          + [(0,  k) for k in range(1, GRID_SIZE)])

def queen_offsets():
    return rook_offsets() + bishop_offsets()

PIECES = {
    "knight": knight_offsets,
    "bishop": bishop_offsets,
    "rook":   rook_offsets,
    "queen":  queen_offsets,
}

# Central seed patterns chosen to straddle every zone boundary used below.
# A plus-shaped 5-cell cluster at the center works for all three layouts
# because the center of the 8x8 board (rows 3-4, cols 3-4) is on the
# boundary of every zone scheme.
SEED_CELLS = {(3, 3), (3, 4), (4, 3), (4, 4), (3, 5), (4, 5), (5, 4)}


def cell_id(r, c):
    return f"r{r}_c{c}"


def build_neighborhood(r, c, offsets):
    # self + filtered chess-piece reach
    nbrs = {cell_id(r, c): 1}
    for dr, dc in offsets:
        nr, nc = r + dr, c + dc
        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
            nbrs[cell_id(nr, nc)] = 1
    return nbrs


def build_config(layout_name, layout_fn, piece_name, offset_fn):
    cells = {
        "default": {
            "delay": "transport",
            "model": "asymmChessVariant",
            # default state uses Rule 1 thresholds; every cell overrides below
            "state": {
                "alive": 0,
                **RULES[1],
            },
        }
    }

    offsets = offset_fn()
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            rule_num = layout_fn(r, c)
            alive = 1 if (r, c) in SEED_CELLS else 0
            cells[cell_id(r, c)] = {
                "state": {"alive": alive, **RULES[rule_num]},
                "neighborhood": build_neighborhood(r, c, offsets),
            }

    return {
        "cells": cells,
        "viewer": [{
            "colors": [[255, 255, 255], [0, 0, 0]],
            "breaks": [0, 0.5, 1],
            "field": "alive",
        }],
    }


def main():
    base_dir = os.path.join(os.path.dirname(__file__), "..")
    config_dir = os.path.join(base_dir, "config", "asymmetric")
    script_dir = os.path.join(base_dir, "scripts", "asymmetric")
    os.makedirs(config_dir, exist_ok=True)
    os.makedirs(script_dir, exist_ok=True)

    generated = []
    for layout_name, layout_fn in ZONE_LAYOUTS.items():
        for piece_name, offset_fn in PIECES.items():
            name = f"asymm_{layout_name}_{piece_name}"
            filename = f"{name}_config.json"

            config = build_config(layout_name, layout_fn, piece_name, offset_fn)
            with open(os.path.join(config_dir, filename), "w", newline="\n") as f:
                json.dump(config, f, indent=2)
                f.write("\n")

            script_path = os.path.join(script_dir, f"run_{name}.sh")
            with open(script_path, "w", newline="\n") as f:
                f.write(f"""#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running {name}..."
./bin/chess_variant config/asymmetric/{filename} 60
""")
            os.chmod(script_path, 0o755)

            generated.append(name)
            print(f"  {filename}")

    master = os.path.join(script_dir, "run_all_asymm.sh")
    with open(master, "w", newline="\n") as f:
        f.write("#!/bin/bash\n"
                "# Run all asymmetric rule-zone scenarios "
                f"({len(ZONE_LAYOUTS)} layouts x {len(PIECES)} pieces)\n"
                'for f in scripts/asymmetric/run_asymm_*.sh; do\n'
                '    bash "$f"\n'
                'done\n')
    os.chmod(master, 0o755)

    print(f"\nGenerated {len(generated)} asymmetric configs + run scripts")
    print("Master script: scripts/asymmetric/run_all_asymm.sh")


if __name__ == "__main__":
    main()
