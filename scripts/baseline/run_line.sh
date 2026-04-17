#!/bin/bash
# run horizontal line seed on 9x13 wrapped grid
SIM_TIME="${1:-60}"
./bin/chess_variant config/baseline/chessVariantKernel1_line_config.json "$SIM_TIME"
