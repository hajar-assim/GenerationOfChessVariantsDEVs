#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running rule5_queen..."
./bin/chess_variant config/rules/rule5/rule5_queen_config.json 60
