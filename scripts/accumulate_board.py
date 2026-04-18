#!/usr/bin/env python3
"""Accumulation grid post-processing.

Reads a Cell-DEVS simulation log CSV, sums the alive state of each cell
over the last N generations, and thresholds the result into a binary
chess board.

Usage:
    python3 scripts/accumulate_board.py <log_csv> [--last N] [--threshold T]

Options:
    --last N        Number of final generations to accumulate (default: 20)
    --threshold T   Fraction of accumulated generations a cell must be alive
                    to count as a filled (black) square (default: 0.5)
    --out FILE      Output file path (default: prints to stdout)
"""

import argparse
import csv
import re
import sys

# Cell IDs come in two formats:
#   "(r,c)"   - GridCell (symmetric)
#   "rR_cC"   - AsymmCell (asymmetric rule-zone configs)
_ASYMM_ID = re.compile(r"^r(\d+)_c(\d+)$")


def parse_cell_id(model_name):
    """Return (row, col) for either grid or asymm cell IDs, or None."""
    name = model_name.strip()
    if name.startswith("(") and name.endswith(")"):
        parts = name[1:-1].split(",")
        if len(parts) == 2:
            try:
                return int(parts[0]), int(parts[1])
            except ValueError:
                return None
    m = _ASYMM_ID.match(name)
    if m:
        return int(m.group(1)), int(m.group(2))
    return None


def parse_log(filepath):
    """Parse simulation CSV into {time: {(row,col): alive}}."""
    grid_states = {}

    with open(filepath, "r") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)  # skip header (sep=;)
        next(reader)  # skip column names

        for row in reader:
            if len(row) < 5:
                continue
            time_str, _, model_name, port_name, data = row

            # only take state output rows (empty port_name), skip neighborhood
            if port_name != "":
                continue

            # parse coordinate from either "(r,c)" grid IDs or "rR_cC" asymm IDs
            rc = parse_cell_id(model_name)
            if rc is None:
                continue
            r, c = rc

            # parse alive value from data like "<1>" or "<0>"
            alive = int(data.strip().strip("<>"))

            time_val = int(time_str)
            if time_val not in grid_states:
                grid_states[time_val] = {}
            grid_states[time_val][(r, c)] = alive

    return grid_states


def accumulate(grid_states, last_n, threshold):
    """Sum alive counts over last N generations and threshold to binary."""
    times = sorted(grid_states.keys())
    if len(times) == 0:
        print("Error: no timesteps found in log.", file=sys.stderr)
        sys.exit(1)

    # use the last N timesteps (or all if fewer than N exist)
    window = times[-last_n:] if len(times) >= last_n else times
    actual_window = len(window)

    # find grid dimensions from all coordinates
    all_coords = set()
    for t in times:
        all_coords.update(grid_states[t].keys())

    max_row = max(r for r, c in all_coords)
    max_col = max(c for r, c in all_coords)
    rows = max_row + 1
    cols = max_col + 1

    # accumulate alive counts
    accum = [[0] * cols for _ in range(rows)]
    for t in window:
        for (r, c), alive in grid_states[t].items():
            accum[r][c] += alive

    # threshold to binary board
    cutoff = threshold * actual_window
    board = [[1 if accum[r][c] >= cutoff else 0 for c in range(cols)]
             for r in range(rows)]

    return board, accum, actual_window


def print_board(board, file=sys.stdout):
    """Print binary board as a grid of 1s and 0s."""
    for row in board:
        print(" ".join(str(v) for v in row), file=file)


def print_visual(board, file=sys.stdout):
    """Print board with unicode blocks for visual inspection."""
    for row in board:
        print("".join("\u2588\u2588" if v == 1 else "  " for v in row), file=file)


def main():
    parser = argparse.ArgumentParser(
        description="Accumulate Cell-DEVS simulation into a chess board")
    parser.add_argument("log_csv", help="Path to simulation log CSV")
    parser.add_argument("--last", type=int, default=20,
                        help="Number of final generations to accumulate (default: 20)")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="Alive fraction cutoff for filled square (default: 0.5)")
    parser.add_argument("--out", type=str, default=None,
                        help="Output file path (default: stdout)")
    args = parser.parse_args()

    grid_states = parse_log(args.log_csv)
    board, accum, window_size = accumulate(grid_states, args.last, args.threshold)

    rows = len(board)
    cols = len(board[0])
    filled = sum(sum(row) for row in board)
    total = rows * cols

    # summary
    times = sorted(grid_states.keys())
    print(f"Log: {args.log_csv}", file=sys.stderr)
    print(f"Timesteps: {len(times)} (using last {window_size})", file=sys.stderr)
    print(f"Grid: {rows}x{cols}", file=sys.stderr)
    print(f"Threshold: {args.threshold}", file=sys.stderr)
    print(f"Filled squares: {filled}/{total} ({100*filled/total:.1f}%)", file=sys.stderr)
    print(file=sys.stderr)

    # output
    out = open(args.out, "w") if args.out else sys.stdout

    print(f"# Accumulation board ({rows}x{cols})", file=out)
    print(f"# Window: last {window_size} generations, threshold: {args.threshold}", file=out)
    print(f"# Filled: {filled}/{total}", file=out)
    print_board(board, file=out)
    print(file=out)

    # raw accumulation counts for reference
    print(f"# Raw accumulation counts (out of {window_size}):", file=out)
    for row in accum:
        print(" ".join(f"{v:2d}" for v in row), file=out)
    print(file=out)

    # visual representation
    print("# Visual:", file=out)
    print_visual(board, file=out)

    if args.out:
        out.close()
        print(f"Output written to: {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
