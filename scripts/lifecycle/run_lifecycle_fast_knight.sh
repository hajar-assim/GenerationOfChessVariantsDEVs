#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running lifecycle_fast_knight..."
./bin/chess_variant config/lifecycle/lifecycle_fast_knight_config.json 60
