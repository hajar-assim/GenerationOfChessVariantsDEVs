#!/usr/bin/env python3
"""Translate an asymmetric Cell-DEVS log + config into a grid-style pair that
the Cell-DEVS Web Viewer (https://devssim.carleton.ca/cell-devs-viewer/) can load.

The web viewer only supports GridCell models — it requires scenario.shape in the
config and parses cell IDs in "(r,c)" form. Asymm configs have neither.

This script:
  1. Rewrites the log CSV so cell IDs "rR_cC" become "(R,C)".
  2. Emits a minimal grid-style config with scenario.shape = [8, 8].

Usage:
    python3 scripts/asymm_to_viewer.py logs/asymmetric/asymm_r3_r5_bishop_grid_log.csv
    python3 scripts/asymm_to_viewer.py --all

Output:
    logs/viewer_stubs/<name>_config.json
    logs/viewer_stubs/<name>_grid_log.csv
"""

import argparse
import glob
import os
import re
import sys

GRID_SIZE = 8
STUB_DIR = os.path.join("logs", "viewer_stubs")
_ASYMM_ID = re.compile(r"\br(\d+)_c(\d+)\b")


def translate_log(src_csv, dst_csv):
    """Rewrite rR_cC ids as (R,C) in the CSV."""
    with open(src_csv, "r") as fin, open(dst_csv, "w", newline="\n") as fout:
        for line in fin:
            fout.write(_ASYMM_ID.sub(lambda m: f"({m.group(1)},{m.group(2)})", line))


def stub_config(name):
    """Minimal grid config that the viewer accepts. The cell model and neighborhood
    don't drive simulation here — the viewer only needs scenario.shape to render."""
    return {
        "scenario": {"shape": [GRID_SIZE, GRID_SIZE], "origin": [0, 0], "wrapped": False},
        "cells": {
            "default": {
                "delay": "transport",
                "model": "chessVariant",
                "state": {"alive": 0},
                "neighborhood": [{"type": "moore", "range": 1}],
            }
        },
        "viewer": [
            {
                "colors": [[255, 255, 255], [0, 0, 0]],
                "breaks": [0, 0.5, 1],
                "field": "alive",
            }
        ],
    }


def process(log_path):
    import json
    name = os.path.basename(log_path).replace("_grid_log.csv", "")
    os.makedirs(STUB_DIR, exist_ok=True)
    dst_log = os.path.join(STUB_DIR, f"{name}_grid_log.csv")
    dst_config = os.path.join(STUB_DIR, f"{name}_config.json")

    translate_log(log_path, dst_log)
    with open(dst_config, "w", newline="\n") as f:
        json.dump(stub_config(name), f, indent=2)
        f.write("\n")

    print(f"  {name}: {dst_config} + {dst_log}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("log", nargs="?", help="asymm log CSV (e.g. logs/asymmetric/asymm_*_grid_log.csv)")
    p.add_argument("--all", action="store_true", help="process every asymm log in logs/")
    args = p.parse_args()

    if args.all:
        logs = sorted(glob.glob("logs/asymmetric/asymm_*_grid_log.csv"))
        if not logs:
            print("No asymm logs found in logs/asymmetric/", file=sys.stderr)
            sys.exit(1)
        for lg in logs:
            process(lg)
        print(f"\nTranslated {len(logs)} asymm logs to {STUB_DIR}/")
    elif args.log:
        if not os.path.exists(args.log):
            print(f"Log not found: {args.log}", file=sys.stderr)
            sys.exit(1)
        process(args.log)
    else:
        p.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
