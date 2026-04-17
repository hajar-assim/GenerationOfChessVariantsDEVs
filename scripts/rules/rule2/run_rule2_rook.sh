#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running rule2_rook..."
./bin/chess_variant config/rules/rule2/rule2_rook_config.json 60
