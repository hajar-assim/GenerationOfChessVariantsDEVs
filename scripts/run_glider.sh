#!/bin/bash
# run glider seed on 9x13 wrapped grid
SIM_TIME="${1:-60}"
./bin/chess_variant config/chessVariantKernel1_glider_config.json "$SIM_TIME"
