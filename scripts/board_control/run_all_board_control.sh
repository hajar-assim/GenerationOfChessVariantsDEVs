#!/bin/bash
# Run all board control scenarios
for f in scripts/board_control/run_board_control_*.sh; do
    bash "$f"
done
