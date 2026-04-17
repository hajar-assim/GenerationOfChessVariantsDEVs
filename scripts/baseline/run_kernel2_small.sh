#!/bin/bash
# run kernel 2 on 5x9 grid with asymmetric seed
SIM_TIME="${1:-60}"
./bin/chess_variant config/baseline/chessVariantKernel2SmallGrid_config.json "$SIM_TIME"
