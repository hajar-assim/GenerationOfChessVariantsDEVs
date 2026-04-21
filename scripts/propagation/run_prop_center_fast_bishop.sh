#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running prop_center_fast_bishop..."
./bin/chess_variant config/propagation/prop_center_fast_bishop_config.json 60
