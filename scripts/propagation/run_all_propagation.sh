#!/bin/bash
# Run all propagation scenarios
for f in scripts/propagation/run_prop_*.sh; do
    bash "$f"
done
