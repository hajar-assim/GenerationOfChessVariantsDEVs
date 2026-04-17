#!/bin/bash
# Run all Fridenfalk rule scenarios (rules 1-4, all 5 piece types)
for r in 1 2 3 4; do
    for f in scripts/rules/rule${r}/run_*.sh; do
        bash "$f"
    done
done
