#!/bin/bash
# Run all lifecycle scenarios
for f in scripts/lifecycle/run_lifecycle_*.sh; do
    bash "$f"
done
