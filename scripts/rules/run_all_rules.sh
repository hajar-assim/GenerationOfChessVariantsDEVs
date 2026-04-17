#!/bin/bash
# Run all Fridenfalk rule scenarios (rules 1-2-3-4-5, all 5 piece types)
for r in 1 2 3 4 5; do
    for f in scripts/rules/rule${r}/run_*.sh; do
        bash "$f"
    done
done
