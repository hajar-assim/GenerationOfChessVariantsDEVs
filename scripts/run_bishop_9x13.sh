#!/bin/bash
# run bishop diagonal neighborhood on 9x13 wrapped grid
SIM_TIME="${1:-60}"
./bin/chess_variant config/bishopNeighborhood_9x13_config.json "$SIM_TIME"
