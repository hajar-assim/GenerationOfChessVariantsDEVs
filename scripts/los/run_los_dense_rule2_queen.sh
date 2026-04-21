#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running los_dense_rule2_queen..."
./bin/chess_variant config/los/los_dense_rule2_queen_config.json 60
