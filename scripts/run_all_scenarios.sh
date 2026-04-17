#!/bin/bash
# runs all chess variant scenarios
# output csvs go to logs/

EXE="bin/chess_variant"
SIM_TIME=60

if [ ! -f "$EXE" ]; then
    echo "ERROR: Executable not found at $EXE"
    echo "Please build first:  bash build_sim.sh"
    exit 1
fi

echo "============================================"
echo " Chess Variant Cell-DEVS — Running all scenarios"
echo "============================================"

for CONFIG in config/chessVariantKernel1_config.json \
              config/chessVariantKernel2_config.json \
              config/chessVariantKernel1SmallGrid_config.json \
              config/chessVariantKernel2SmallGrid_config.json \
              config/chessVariantKernel1_glider_config.json \
              config/chessVariantKernel1_line_config.json \
              config/chessVariantKernel1_noWrap_config.json \
              config/chessVariantKernel1_large_config.json \
              config/knightNeighborhood_8x8_config.json \
              config/bishopNeighborhood_8x8_config.json \
              config/rookNeighborhood_8x8_config.json \
              config/knightNeighborhood_9x13_config.json \
              config/bishopNeighborhood_9x13_config.json \
              config/multiPiece_8x8_config.json; do
    NAME=$(basename "$CONFIG" .json)
    echo ""
    echo "--- Running: $NAME (sim time = $SIM_TIME) ---"
    "$EXE" "$CONFIG" "$SIM_TIME"
    echo "--- Finished: $NAME ---"
done

echo ""
echo "============================================"
echo " All scenarios complete. Results in logs/"
echo "============================================"
