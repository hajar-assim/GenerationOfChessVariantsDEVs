#!/bin/bash
# run multi-piece knight+bishop hybrid on 8x8 grid
SIM_TIME="${1:-60}"
./bin/chess_variant config/baseline/multiPiece_8x8_config.json "$SIM_TIME"
