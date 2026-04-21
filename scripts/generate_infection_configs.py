#!/usr/bin/env python3
"""Generate chess infection propagation configs.

Each scenario seeds two competing infections (white and black) on opposite
sides of an 8x8 board and lets them spread via a specific chess piece's
movement pattern. Territorial boundaries emerge where fronts collide.

Produces 5 scenarios — one per piece topology — using piece-historically
accurate starting-square seeds (rooks on corners, knights on b/g files,
bishops on c/f files, queens on d-file, kings on e-file). This turns each
config into a narrative: "if only rooks could carry the infection, here is
how the board fills."
"""

import json
import os

GRID_SIZE = 8
RECOVERY_DURATION = 5

# piece type encoding: matches the state header enum
PIECE_TYPE_ID = {
    "knight": 2,
    "bishop": 3,
    "rook":   4,
    "queen":  5,
    "king":   6,
}

# neighborhood offsets per piece type (no self — self is added separately)
def knight_offsets():
    return [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]

def bishop_offsets():
    return [(dr, dc) for k in range(1, GRID_SIZE)
            for dr, dc in [(-k,-k), (-k,k), (k,-k), (k,k)]]

def rook_offsets():
    return ([(-k, 0) for k in range(1, GRID_SIZE)]
          + [( k, 0) for k in range(1, GRID_SIZE)]
          + [(0, -k) for k in range(1, GRID_SIZE)]
          + [(0,  k) for k in range(1, GRID_SIZE)])

def queen_offsets():
    return rook_offsets() + bishop_offsets()

def king_offsets():
    return [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

OFFSETS = {
    "knight": knight_offsets,
    "bishop": bishop_offsets,
    "rook":   rook_offsets,
    "queen":  queen_offsets,
    "king":   king_offsets,
}

# piece-historically accurate seed squares for each scenario:
# black on rank 0 (top), white on rank 7 (bottom), matching a real board.
SEEDS = {
    "knight": {"black": [[0, 1], [0, 6]], "white": [[7, 1], [7, 6]]},
    "bishop": {"black": [[0, 2], [0, 5]], "white": [[7, 2], [7, 5]]},
    "rook":   {"black": [[0, 0], [0, 7]], "white": [[7, 0], [7, 7]]},
    "queen":  {"black": [[0, 3]],          "white": [[7, 3]]},
    "king":   {"black": [[0, 4]],          "white": [[7, 4]]},
}

# viewer: 5 signed-integer bands (dark red -> red -> grey -> light blue -> dark blue)
VIEWER = [
    {
        "colors": [
            [120, 0, 0],      # -2: black recovered
            [220, 60, 60],    # -1: black infected
            [200, 200, 200],  #  0: susceptible
            [60, 120, 220],   # +1: white infected
            [0, 30, 140]      # +2: white recovered
        ],
        "breaks": [-2.5, -1.5, -0.5, 0.5, 1.5, 2.5],
        "field": "display"
    }
]


def neighborhood_block(offsets):
    # Cadmium "relative" neighborhood; self (0,0) must be included so the
    # LoS walker can find intermediate cells when checking sliding pieces
    return [{
        "type": "relative",
        "neighbors": [[0, 0]] + [list(o) for o in offsets]
    }]


def build_config(piece_name):
    piece_id = PIECE_TYPE_ID[piece_name]
    nbr = neighborhood_block(OFFSETS[piece_name]())
    seeds = SEEDS[piece_name]

    default_state = {
        "status": 0,
        "color": 0,
        "infectedSteps": 0,
        "recoveryDuration": RECOVERY_DURATION,
        "pieceType": piece_id,
    }

    def seed_state(color_id):
        s = dict(default_state)
        s["status"] = 1
        s["color"] = color_id
        return s

    return {
        "scenario": {"shape": [GRID_SIZE, GRID_SIZE], "origin": [0, 0], "wrapped": False},
        "cells": {
            "default": {
                "delay": "transport",
                "model": "chessInfection",
                "state": default_state,
                "neighborhood": nbr,
            },
            "white_seeds": {
                "state": seed_state(1),
                "cell_map": seeds["white"],
            },
            "black_seeds": {
                "state": seed_state(2),
                "cell_map": seeds["black"],
            },
        },
        "viewer": VIEWER,
    }


def main():
    base = os.path.join(os.path.dirname(__file__), "..")
    config_dir = os.path.join(base, "config", "infection")
    script_dir = os.path.join(base, "scripts", "infection")
    os.makedirs(config_dir, exist_ok=True)
    os.makedirs(script_dir, exist_ok=True)

    generated = []
    for piece in OFFSETS.keys():
        name = f"infection_{piece}"
        filename = f"{name}_config.json"

        cfg = build_config(piece)
        with open(os.path.join(config_dir, filename), "w", newline="\n") as f:
            json.dump(cfg, f, indent=2)
            f.write("\n")

        script_path = os.path.join(script_dir, f"run_{name}.sh")
        with open(script_path, "w", newline="\n") as f:
            f.write(f"""#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running {name}..."
./bin/chess_variant config/infection/{filename} 60
""")
        os.chmod(script_path, 0o755)
        generated.append(name)
        print(f"  {filename}")

    master = os.path.join(script_dir, "run_all_infection.sh")
    with open(master, "w", newline="\n") as f:
        f.write("#!/bin/bash\n"
                "# Run all chess infection propagation scenarios (5 piece topologies)\n"
                'for f in scripts/infection/run_infection_*.sh; do\n'
                '    bash "$f"\n'
                'done\n')
    os.chmod(master, 0o755)

    print(f"\nGenerated {len(generated)} infection configs + run scripts")
    print("Master script: scripts/infection/run_all_infection.sh")


if __name__ == "__main__":
    main()
