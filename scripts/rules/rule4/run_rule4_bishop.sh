#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running rule4_bishop..."
./bin/chess_variant config/rules/rule4/rule4_bishop_config.json 60
