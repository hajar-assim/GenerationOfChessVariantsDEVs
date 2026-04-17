#!/bin/bash
# run kernel 1 on 20x20 wrapped grid
SIM_TIME="${1:-60}"
./bin/chess_variant config/baseline/chessVariantKernel1_large_config.json "$SIM_TIME"
