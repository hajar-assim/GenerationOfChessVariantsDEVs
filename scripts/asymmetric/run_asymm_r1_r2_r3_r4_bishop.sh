#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running asymm_r1_r2_r3_r4_bishop..."
./bin/chess_variant config/asymmetric/asymm_r1_r2_r3_r4_bishop_config.json 60
