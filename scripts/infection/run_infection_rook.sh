#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running infection_rook..."
./bin/chess_variant config/infection/infection_rook_config.json 60
