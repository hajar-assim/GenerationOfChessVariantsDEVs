#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running lifecycle_slow_knight..."
./bin/chess_variant config/lifecycle/lifecycle_slow_knight_config.json 60
