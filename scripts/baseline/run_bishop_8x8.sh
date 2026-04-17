#!/bin/bash
# run bishop diagonal neighborhood on 8x8 grid
SIM_TIME="${1:-60}"
./bin/chess_variant config/baseline/bishopNeighborhood_8x8_config.json "$SIM_TIME"
