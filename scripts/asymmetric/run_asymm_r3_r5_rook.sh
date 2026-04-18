#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running asymm_r3_r5_rook..."
./bin/chess_variant config/asymmetric/asymm_r3_r5_rook_config.json 60
