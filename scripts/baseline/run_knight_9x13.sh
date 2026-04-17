#!/bin/bash
# run knight L-shape neighborhood on 9x13 wrapped grid
SIM_TIME="${1:-60}"
./bin/chess_variant config/baseline/knightNeighborhood_9x13_config.json "$SIM_TIME"
