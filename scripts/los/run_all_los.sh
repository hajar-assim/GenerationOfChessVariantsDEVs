#!/bin/bash
# Run all LOS scenarios
for f in scripts/los/run_los_*.sh; do
    bash "$f"
done
