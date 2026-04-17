#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running rule2_moore..."
./bin/chess_variant config/rules/rule2/rule2_moore_config.json 60
