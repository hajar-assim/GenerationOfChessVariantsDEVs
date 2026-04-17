#!/bin/bash
# run kernel 1 on 7x7 grid with plus seed
SIM_TIME="${1:-60}"
./bin/chess_variant config/baseline/chessVariantKernel1SmallGrid_config.json "$SIM_TIME"
