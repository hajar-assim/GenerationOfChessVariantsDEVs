#!/usr/bin/env python3
"""Board quality metrics for generated chess variant boards.

Computes coverage, symmetry, connectivity, and hole count for a binary
board produced by the accumulation grid script.

Can be used standalone or imported by other scripts.

Usage:
    python3 scripts/board_metrics.py <board_file>
    python3 scripts/board_metrics.py --from-log <log_csv> [--last N] [--threshold T]
"""

import argparse
import sys
from collections import deque


def parse_board_file(filepath):
    """Read a board text file (output of accumulate_board.py)."""
    board = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            vals = line.split()
            # stop if we hit the raw accumulation section (values > 1)
            if any(int(v) > 1 for v in vals):
                break
            board.append([int(v) for v in vals])
    return board


def coverage(board):
    """Fraction of filled squares. Ideal chess board = 0.5."""
    rows, cols = len(board), len(board[0])
    total = rows * cols
    filled = sum(board[r][c] for r in range(rows) for c in range(cols))
    return filled / total


def symmetry(board):
    """Average of horizontal, vertical, and 180-degree rotational symmetry.

    Each sub-score is the fraction of cells that match their mirrored
    counterpart. Returns a value in [0, 1] where 1 = perfectly symmetric.
    """
    rows, cols = len(board), len(board[0])
    total = rows * cols

    # horizontal symmetry (left-right mirror)
    h_match = sum(1 for r in range(rows) for c in range(cols)
                  if board[r][c] == board[r][cols - 1 - c])

    # vertical symmetry (top-bottom mirror)
    v_match = sum(1 for r in range(rows) for c in range(cols)
                  if board[r][c] == board[rows - 1 - r][c])

    # 180-degree rotational symmetry
    r_match = sum(1 for r in range(rows) for c in range(cols)
                  if board[r][c] == board[rows - 1 - r][cols - 1 - c])

    h_sym = h_match / total
    v_sym = v_match / total
    r_sym = r_match / total

    return (h_sym + v_sym + r_sym) / 3


def _bfs_region(board, visited, start_r, start_c, target):
    """BFS flood fill, returns the set of cells in the connected region."""
    rows, cols = len(board), len(board[0])
    queue = deque([(start_r, start_c)])
    visited[start_r][start_c] = True
    region = set()
    region.add((start_r, start_c))

    while queue:
        r, c = queue.popleft()
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                if not visited[nr][nc] and board[nr][nc] == target:
                    visited[nr][nc] = True
                    queue.append((nr, nc))
                    region.add((nr, nc))

    return region


def connectivity(board):
    """Number of connected components of filled (1) cells.

    Uses 4-connected BFS. Returns the count — 1 is ideal (single
    connected region), higher means more fragmented.
    """
    rows, cols = len(board), len(board[0])
    visited = [[False] * cols for _ in range(rows)]
    components = 0

    for r in range(rows):
        for c in range(cols):
            if board[r][c] == 1 and not visited[r][c]:
                _bfs_region(board, visited, r, c, target=1)
                components += 1

    return components


def hole_count(board):
    """Number of enclosed empty regions (holes).

    An empty region is a "hole" if it does not touch the grid border.
    Uses 4-connected BFS on empty (0) cells.
    """
    rows, cols = len(board), len(board[0])
    visited = [[False] * cols for _ in range(rows)]
    holes = 0

    for r in range(rows):
        for c in range(cols):
            if board[r][c] == 0 and not visited[r][c]:
                region = _bfs_region(board, visited, r, c, target=0)
                # check if region touches any border
                touches_border = any(
                    r == 0 or r == rows - 1 or c == 0 or c == cols - 1
                    for r, c in region
                )
                if not touches_border:
                    holes += 1

    return holes


def compute_all(board):
    """Compute all metrics and return as a dict."""
    return {
        "coverage": coverage(board),
        "symmetry": symmetry(board),
        "connectivity": connectivity(board),
        "holes": hole_count(board),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Compute board quality metrics")
    parser.add_argument("board_file", nargs="?", default=None,
                        help="Board text file (from accumulate_board.py)")
    parser.add_argument("--from-log", type=str, default=None,
                        help="Compute directly from a simulation log CSV")
    parser.add_argument("--last", type=int, default=20,
                        help="Generations to accumulate (with --from-log)")
    parser.add_argument("--threshold", type=float, default=0.5,
                        help="Accumulation threshold (with --from-log)")
    args = parser.parse_args()

    if args.from_log:
        # import accumulate_board to reuse its parsing
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        from accumulate_board import parse_log, accumulate
        grid_states = parse_log(args.from_log)
        board, _, _ = accumulate(grid_states, args.last, args.threshold)
    elif args.board_file:
        board = parse_board_file(args.board_file)
    else:
        parser.error("Provide either a board file or --from-log <csv>")

    if not board:
        print("Error: empty board", file=sys.stderr)
        sys.exit(1)

    metrics = compute_all(board)
    rows, cols = len(board), len(board[0])

    print(f"Board: {rows}x{cols}")
    print(f"Coverage:     {metrics['coverage']:.3f}  (ideal: 0.500)")
    print(f"Symmetry:     {metrics['symmetry']:.3f}  (ideal: 1.000)")
    print(f"Connectivity: {metrics['connectivity']}  (ideal: 1)")
    print(f"Holes:        {metrics['holes']}")


if __name__ == "__main__":
    main()
