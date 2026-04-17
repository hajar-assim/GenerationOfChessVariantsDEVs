#!/bin/bash
# run kernel 1 on 9x13 grid with plus seed
SIM_TIME="${1:-60}"
./bin/chess_variant config/baseline/chessVariantKernel1_config.json "$SIM_TIME"
