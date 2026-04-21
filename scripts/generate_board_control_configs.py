#!/usr/bin/env python3
"""Generate JSON configs for board control analysis scenarios.

Creates Cell-DEVS configurations that place chess pieces on an 8x8 grid
and simulate influence propagation. Each piece projects control along
its movement pattern (blocked by line of sight for sliding pieces),
and influence propagates outward over simulation steps.

The grid uses a queen-sized neighborhood (range 7 in all directions)
so that every cell can see every other cell — this lets the transition
function compute line-of-sight blocking across the full board.
"""

import json
import os

ROWS, COLS = 8, 8

# piece types: 0=empty, 1=pawn, 2=knight, 3=bishop, 4=rook, 5=queen, 6=king
EMPTY, PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING = 0, 1, 2, 3, 4, 5, 6
# colors: 0=none, 1=white, 2=black
NONE, WHITE, BLACK = 0, 1, 2

# viewer config: blue-white-red gradient for control balance
# positive control = white dominance (blue), negative = black dominance (red)
VIEWER = [
    {
        "colors": [
            [220, 38, 38],    # strong black control (red)
            [235, 147, 147],  # moderate black
            [255, 255, 255],  # neutral / contested
            [147, 175, 235],  # moderate white
            [37, 99, 235]     # strong white control (blue)
        ],
        "breaks": [-10, -2, 0, 2, 10],
        "field": "control"
    }
]


def make_cell_state(piece_type=EMPTY, piece_color=NONE, propagation_rate=0.15):
    """Create a cell state dict."""
    state = {
        "pieceType": piece_type,
        "pieceColor": piece_color,
        "whiteInfluence": 0.0,
        "blackInfluence": 0.0,
        "control": 0.0,
        "propagationRate": propagation_rate,
        "step": 0,
    }
    return state


# --- Chess positions ---

def starting_position():
    """Standard chess starting position."""
    board = [[None]*COLS for _ in range(ROWS)]
    back_rank = [ROOK, KNIGHT, BISHOP, QUEEN, KING, BISHOP, KNIGHT, ROOK]

    for c in range(8):
        board[0][c] = (back_rank[c], BLACK)   # black back rank
        board[1][c] = (PAWN, BLACK)            # black pawns
        board[6][c] = (PAWN, WHITE)            # white pawns
        board[7][c] = (back_rank[c], WHITE)    # white back rank

    return board


def italian_game():
    """Italian Game after 1.e4 e5 2.Nf3 Nc6 3.Bc4 Bc5 4.c3 Nf6 5.d4"""
    board = [[None]*COLS for _ in range(ROWS)]

    # Black pieces
    board[0][0] = (ROOK, BLACK)
    board[0][3] = (QUEEN, BLACK)
    board[0][4] = (KING, BLACK)
    board[0][7] = (ROOK, BLACK)
    board[0][2] = (BISHOP, BLACK)   # dark bishop home
    board[2][2] = (KNIGHT, BLACK)   # Nc6
    board[2][5] = (KNIGHT, BLACK)   # Nf6
    board[3][2] = (BISHOP, BLACK)   # Bc5
    board[3][4] = (PAWN, BLACK)     # e5
    board[1][0] = (PAWN, BLACK)
    board[1][1] = (PAWN, BLACK)
    board[1][2] = (PAWN, BLACK)
    board[1][3] = (PAWN, BLACK)
    board[1][5] = (PAWN, BLACK)
    board[1][6] = (PAWN, BLACK)
    board[1][7] = (PAWN, BLACK)

    # White pieces
    board[7][0] = (ROOK, WHITE)
    board[7][1] = (KNIGHT, WHITE)
    board[7][3] = (QUEEN, WHITE)
    board[7][4] = (KING, WHITE)
    board[7][7] = (ROOK, WHITE)
    board[7][2] = (BISHOP, WHITE)   # dark bishop home
    board[5][5] = (KNIGHT, WHITE)   # Nf3
    board[4][2] = (BISHOP, WHITE)   # Bc4
    board[4][3] = (PAWN, WHITE)     # d4
    board[4][4] = (PAWN, WHITE)     # e4
    board[5][2] = (PAWN, WHITE)     # c3
    board[6][0] = (PAWN, WHITE)
    board[6][1] = (PAWN, WHITE)
    board[6][5] = (PAWN, WHITE)
    board[6][6] = (PAWN, WHITE)
    board[6][7] = (PAWN, WHITE)

    return board


def sicilian_najdorf():
    """Sicilian Najdorf after 1.e4 c5 2.Nf3 d6 3.d4 cxd4 4.Nxd4 Nf6 5.Nc3 a6"""
    board = [[None]*COLS for _ in range(ROWS)]

    # Black
    board[0][0] = (ROOK, BLACK)
    board[0][1] = (KNIGHT, BLACK)  # Nb8
    board[0][2] = (BISHOP, BLACK)
    board[0][3] = (QUEEN, BLACK)
    board[0][4] = (KING, BLACK)
    board[0][5] = (BISHOP, BLACK)
    board[0][7] = (ROOK, BLACK)
    board[2][5] = (KNIGHT, BLACK)  # Nf6
    board[2][3] = (PAWN, BLACK)    # d6
    board[1][1] = (PAWN, BLACK)
    board[1][4] = (PAWN, BLACK)
    board[1][5] = (PAWN, BLACK)
    board[1][6] = (PAWN, BLACK)
    board[1][7] = (PAWN, BLACK)
    board[2][0] = (PAWN, BLACK)    # a6

    # White
    board[7][0] = (ROOK, WHITE)
    board[7][3] = (QUEEN, WHITE)
    board[7][4] = (KING, WHITE)
    board[7][5] = (BISHOP, WHITE)
    board[7][7] = (ROOK, WHITE)
    board[5][2] = (KNIGHT, WHITE)  # Nc3
    board[4][3] = (KNIGHT, WHITE)  # Nd4
    board[7][2] = (BISHOP, WHITE)
    board[4][4] = (PAWN, WHITE)    # e4
    board[6][0] = (PAWN, WHITE)
    board[6][1] = (PAWN, WHITE)
    board[6][2] = (PAWN, WHITE)
    board[6][5] = (PAWN, WHITE)
    board[6][6] = (PAWN, WHITE)
    board[6][7] = (PAWN, WHITE)

    return board


def endgame_rook_vs_bishop():
    """Simplified endgame: rook vs bishop with pawns."""
    board = [[None]*COLS for _ in range(ROWS)]

    board[0][4] = (KING, BLACK)
    board[3][3] = (BISHOP, BLACK)
    board[1][2] = (PAWN, BLACK)
    board[1][5] = (PAWN, BLACK)

    board[7][4] = (KING, WHITE)
    board[4][4] = (ROOK, WHITE)
    board[6][2] = (PAWN, WHITE)
    board[6][5] = (PAWN, WHITE)

    return board


def queens_gambit():
    """Queen's Gambit Declined after 1.d4 d5 2.c4 e6 3.Nc3 Nf6 4.Bg5 Be7 5.e3"""
    board = [[None]*COLS for _ in range(ROWS)]

    # Black
    board[0][0] = (ROOK, BLACK)
    board[0][1] = (KNIGHT, BLACK)
    board[0][2] = (BISHOP, BLACK)
    board[0][3] = (QUEEN, BLACK)
    board[0][4] = (KING, BLACK)
    board[0][7] = (ROOK, BLACK)
    board[2][5] = (KNIGHT, BLACK)   # Nf6
    board[2][4] = (BISHOP, BLACK)   # Be7 (approximation)
    board[3][3] = (PAWN, BLACK)     # d5
    board[2][4] = (BISHOP, BLACK)   # Be7
    board[1][0] = (PAWN, BLACK)
    board[1][1] = (PAWN, BLACK)
    board[1][2] = (PAWN, BLACK)
    board[2][4] = (BISHOP, BLACK)
    board[1][5] = (PAWN, BLACK)
    board[1][6] = (PAWN, BLACK)
    board[1][7] = (PAWN, BLACK)
    board[2][3] = (PAWN, BLACK)     # e6

    # White
    board[7][0] = (ROOK, WHITE)
    board[7][3] = (QUEEN, WHITE)
    board[7][4] = (KING, WHITE)
    board[7][5] = (BISHOP, WHITE)
    board[7][7] = (ROOK, WHITE)
    board[5][2] = (KNIGHT, WHITE)   # Nc3
    board[5][4] = (PAWN, WHITE)     # e3
    board[3][6] = (BISHOP, WHITE)   # Bg5
    board[4][2] = (PAWN, WHITE)     # c4
    board[4][3] = (PAWN, WHITE)     # d4
    board[6][0] = (PAWN, WHITE)
    board[6][1] = (PAWN, WHITE)
    board[6][5] = (PAWN, WHITE)
    board[6][6] = (PAWN, WHITE)
    board[6][7] = (PAWN, WHITE)

    return board


SCENARIOS = {
    "starting_position": starting_position,
    "italian_game": italian_game,
    "sicilian_najdorf": sicilian_najdorf,
    "endgame_rook_vs_bishop": endgame_rook_vs_bishop,
    "queens_gambit_declined": queens_gambit,
}


def build_config(board_fn, propagation_rate=0.08):
    """Build a Cell-DEVS config for a board control scenario."""
    board = board_fn()

    # default state: empty cell
    default_state = make_cell_state(EMPTY, NONE, propagation_rate)

    # neighborhood: need full board visibility for line-of-sight checks
    # moore range 7 covers the entire 8x8 board from any cell
    config = {
        "scenario": {
            "shape": [ROWS, COLS],
            "origin": [0, 0],
            "wrapped": False
        },
        "cells": {
            "default": {
                "delay": "transport",
                "model": "boardControl",
                "state": default_state,
                "neighborhood": [
                    {"type": "moore", "range": 7}
                ]
            }
        },
        "viewer": VIEWER
    }

    # group pieces by type+color for cell_map overrides
    # cadmium uses named cell groups with cell_map arrays of coordinates
    piece_groups = {}
    for r in range(ROWS):
        for c in range(COLS):
            if board[r][c] is not None:
                piece_type, piece_color = board[r][c]
                key = f"piece_{piece_color}_{piece_type}"
                if key not in piece_groups:
                    piece_groups[key] = {
                        "state": make_cell_state(piece_type, piece_color, propagation_rate),
                        "cells": []
                    }
                piece_groups[key]["cells"].append([r, c])

    for group_name, group_data in piece_groups.items():
        config["cells"][group_name] = {
            "state": group_data["state"],
            "cell_map": group_data["cells"]
        }

    return config


# --- Generate configs and run scripts ---
base_dir = os.path.join(os.path.dirname(__file__), "..")
config_dir = os.path.join(base_dir, "config", "board_control")
script_dir = os.path.join(base_dir, "scripts", "board_control")

os.makedirs(config_dir, exist_ok=True)
os.makedirs(script_dir, exist_ok=True)

generated = []

for scenario_name, board_fn in SCENARIOS.items():
    config_name = f"board_control_{scenario_name}"
    filename = f"{config_name}_config.json"

    config = build_config(board_fn)

    filepath = os.path.join(config_dir, filename)
    with open(filepath, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    # run script
    script_name = f"run_{config_name}.sh"
    script_content = f"""#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running {config_name}..."
./bin/chess_variant config/board_control/{filename} 30
"""
    script_path = os.path.join(script_dir, script_name)
    with open(script_path, "w") as f:
        f.write(script_content)
    os.chmod(script_path, 0o755)

    generated.append(config_name)
    print(f"  {filename}")

# master run script
master = "#!/bin/bash\n# Run all board control scenarios\n"
master += "for f in scripts/board_control/run_board_control_*.sh; do\n"
master += '    bash "$f"\n'
master += "done\n"
master_path = os.path.join(script_dir, "run_all_board_control.sh")
with open(master_path, "w") as f:
    f.write(master)
os.chmod(master_path, 0o755)

print(f"\nGenerated {len(generated)} board control configs and run scripts")
