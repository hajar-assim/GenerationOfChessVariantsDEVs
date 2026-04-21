#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running board_control_sicilian_najdorf..."
./bin/chess_variant config/board_control/board_control_sicilian_najdorf_config.json 30
