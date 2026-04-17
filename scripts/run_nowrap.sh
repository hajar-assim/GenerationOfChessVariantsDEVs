#!/bin/bash
# run kernel 1 on 9x13 non-wrapped grid
SIM_TIME="${1:-60}"
./bin/chess_variant config/chessVariantKernel1_noWrap_config.json "$SIM_TIME"
