#!/usr/bin/env python3
"""Zone-aware animation of an asymmetric Cell-DEVS simulation.

Unlike the Cell-DEVS Web Viewer (which only shows alive/dead in black/white),
this visualizer colors each cell by which Fridenfalk rule zone it belongs to
and overlays alive cells as dark circles. The rule boundary is visible at all
times, making the asymmetric contribution obvious.

Usage:
    python3 scripts/visualize_asymm.py logs/asymmetric/asymm_r3_r5_bishop_grid_log.csv
    python3 scripts/visualize_asymm.py --all

Output:
    simulation_videos/<name>.gif   (uses matplotlib PillowWriter — no ffmpeg needed)

Layout is inferred from the filename (expects "asymm_<layout>_<piece>_grid_log.csv").
"""

import argparse
import csv
import glob
import os
import re
import sys

GRID_SIZE = 8

# Rule color palette (background tint for each zone's cells)
RULE_COLORS = {
    1: (0.85, 0.92, 1.00),  # light blue   — Rule 1 (narrowest)
    2: (0.80, 0.95, 0.80),  # light green  — Rule 2
    3: (1.00, 0.95, 0.78),  # light yellow — Rule 3
    4: (1.00, 0.82, 0.78),  # light red    — Rule 4 (widest)
    5: (0.92, 0.82, 1.00),  # light purple — Rule 5 (non-contiguous)
}


def zone_r1_r3(r, c):
    return 1 if r + c < GRID_SIZE else 3

def zone_r1_r2_r3_r4(r, c):
    h = GRID_SIZE // 2
    if r < h and c < h:  return 1
    if r < h and c >= h: return 2
    if r >= h and c < h: return 3
    return 4

def zone_r3_r5(r, c):
    return 3 if r < GRID_SIZE // 2 else 5

ZONES = {"r1_r3": zone_r1_r3, "r1_r2_r3_r4": zone_r1_r2_r3_r4, "r3_r5": zone_r3_r5}

_FNAME = re.compile(r"asymm_(r1_r3|r1_r2_r3_r4|r3_r5)_(knight|bishop|rook|queen)_grid_log\.csv")
_CELL_ID = re.compile(r"^r(\d+)_c(\d+)$")


def parse_layout(logpath):
    m = _FNAME.search(os.path.basename(logpath))
    if not m:
        raise ValueError(f"Cannot parse layout from filename: {logpath}")
    return m.group(1), m.group(2)


def parse_log(logpath):
    """Return (times, states) where states[t][r][c] is 0/1."""
    # events[t] = list of (r, c, alive)
    events = {}
    with open(logpath) as f:
        reader = csv.reader(f, delimiter=";")
        next(reader); next(reader)
        for row in reader:
            if len(row) < 5 or row[3] != "":
                continue
            m = _CELL_ID.match(row[2].strip())
            if not m:
                continue
            r, c = int(m.group(1)), int(m.group(2))
            t = int(row[0])
            alive = int(row[4].strip("<>"))
            events.setdefault(t, []).append((r, c, alive))

    times = sorted(events)
    if not times:
        return [], []

    # reconstruct per-generation state by applying deltas
    state = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    frames = []
    for t in times:
        for r, c, a in events[t]:
            state[r][c] = a
        frames.append([row[:] for row in state])
    return times, frames


def render(logpath, out_path, layout_name, piece_name, times, frames):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import matplotlib.patches as patches
    from matplotlib.animation import PillowWriter
    import numpy as np

    zone_fn = ZONES[layout_name]

    fig, ax = plt.subplots(figsize=(9, 6))
    fig.subplots_adjust(left=0.08, right=0.72, top=0.93, bottom=0.05)
    ax.set_xlim(-0.5, GRID_SIZE - 0.5)
    ax.set_ylim(GRID_SIZE - 0.5, -0.5)  # invert y so row 0 is on top
    ax.set_aspect("equal")
    ax.set_xticks(range(GRID_SIZE))
    ax.set_yticks(range(GRID_SIZE))
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.grid(True, color="gray", linewidth=0.3)

    # background tints (static — zones never change)
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            rule = zone_fn(r, c)
            ax.add_patch(patches.Rectangle(
                (c - 0.5, r - 0.5), 1, 1,
                facecolor=RULE_COLORS[rule], edgecolor="none", zorder=0))

    # alive-cell dots (updated per frame)
    scat = ax.scatter([], [], s=260, c="black", zorder=2)
    title = ax.set_title("", fontsize=11)

    rules_shown = sorted({zone_fn(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE)})
    legend_handles = [
        patches.Patch(facecolor=RULE_COLORS[rn], edgecolor="gray", label=f"Rule {rn}")
        for rn in rules_shown
    ]
    legend_handles.append(patches.Patch(facecolor="black", label="alive"))
    ax.legend(handles=legend_handles, loc="center left", bbox_to_anchor=(1.05, 0.5),
              frameon=False, fontsize=10)

    def animate(i):
        grid = frames[i]
        xs, ys = [], []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if grid[r][c] == 1:
                    xs.append(c); ys.append(r)
        scat.set_offsets(np.array(list(zip(xs, ys))) if xs else np.empty((0, 2)))
        alive_count = sum(sum(row) for row in grid)
        title.set_text(f"{layout_name} / {piece_name}   t = {times[i]}   alive = {alive_count}")
        return scat, title

    anim = animation.FuncAnimation(fig, animate, frames=len(frames),
                                   interval=300, blit=False, repeat=False)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    anim.save(out_path, writer=PillowWriter(fps=3))
    plt.close(fig)


def process(logpath, out_dir):
    layout, piece = parse_layout(logpath)
    times, frames = parse_log(logpath)
    if not frames:
        print(f"  SKIP {os.path.basename(logpath)}: no state events")
        return
    name = f"asymm_{layout}_{piece}"
    out_path = os.path.join(out_dir, f"{name}.gif")
    render(logpath, out_path, layout, piece, times, frames)
    print(f"  {name}.gif  ({len(frames)} frames)")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("log", nargs="?", help="asymm log CSV")
    p.add_argument("--all", action="store_true", help="render every asymm log in logs/")
    p.add_argument("--out-dir", default="simulation_videos",
                   help="output directory (default: simulation_videos)")
    args = p.parse_args()

    if args.all:
        logs = sorted(glob.glob("logs/asymmetric/asymm_*_grid_log.csv"))
        if not logs:
            print("No asymm logs found in logs/asymmetric/", file=sys.stderr)
            sys.exit(1)
        for lg in logs:
            process(lg, args.out_dir)
        print(f"\nRendered {len(logs)} asymm animations to {args.out_dir}/")
    elif args.log:
        if not os.path.exists(args.log):
            print(f"Log not found: {args.log}", file=sys.stderr)
            sys.exit(1)
        process(args.log, args.out_dir)
    else:
        p.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
