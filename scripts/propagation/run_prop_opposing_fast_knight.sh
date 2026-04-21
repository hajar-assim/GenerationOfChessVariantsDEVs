#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running prop_opposing_fast_knight..."
./bin/chess_variant config/propagation/prop_opposing_fast_knight_config.json 60
