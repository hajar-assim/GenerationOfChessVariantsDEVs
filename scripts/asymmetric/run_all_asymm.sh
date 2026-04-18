#!/bin/bash
# Run all asymmetric rule-zone scenarios (3 layouts x 4 pieces)
for f in scripts/asymmetric/run_asymm_*.sh; do
    bash "$f"
done
