#!/bin/bash
echo "===== Running All Adaptive Scenarios ====="
echo ""

echo "[1/5] Adaptive Moore 9x13 (validation)..."
./bin/chess_variant config/adaptive/adaptiveMoore_9x13_config.json 60
echo ""

echo "[2/5] Adaptive Bishop 8x8..."
./bin/chess_variant config/adaptive/adaptiveBishop_8x8_config.json 60
echo ""

echo "[3/5] Adaptive Rook 8x8..."
./bin/chess_variant config/adaptive/adaptiveRook_8x8_config.json 60
echo ""

echo "[4/5] Adaptive Queen 8x8..."
./bin/chess_variant config/adaptive/adaptiveQueen_8x8_config.json 60
echo ""

echo "[5/5] Adaptive Queen 9x13..."
./bin/chess_variant config/adaptive/adaptiveQueen_9x13_config.json 60
echo ""

echo "===== All Adaptive Scenarios Complete ====="
