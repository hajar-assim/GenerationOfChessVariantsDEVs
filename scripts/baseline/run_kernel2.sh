#!/bin/bash
# run kernel 2 on 9x13 grid with asymmetric seed
SIM_TIME="${1:-60}"
./bin/chess_variant config/baseline/chessVariantKernel2_config.json "$SIM_TIME"
