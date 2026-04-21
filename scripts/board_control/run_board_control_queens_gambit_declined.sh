#!/bin/bash
if [ ! -f bin/chess_variant ]; then
    echo "Error: bin/chess_variant not found. Run build_sim.sh first."
    exit 1
fi
echo "Running board_control_queens_gambit_declined..."
./bin/chess_variant config/board_control/board_control_queens_gambit_declined_config.json 30
