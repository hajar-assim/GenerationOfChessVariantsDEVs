#!/bin/bash
# Run all chess infection propagation scenarios (5 piece topologies)
for f in scripts/infection/run_infection_*.sh; do
    bash "$f"
done
