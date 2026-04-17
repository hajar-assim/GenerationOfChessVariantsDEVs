#!/bin/bash
# run knight L-shape neighborhood on 8x8 grid
SIM_TIME="${1:-60}"
./bin/chess_variant config/knightNeighborhood_8x8_config.json "$SIM_TIME"
