#!/bin/bash
# Run every scenario in the project and produce a metrics summary.
# Usage (from repo root): bash scripts/run_everything.sh
#
# Output:
#   logs/*_grid_log.csv          — one per scenario (56 total)
#   logs/metrics_summary.csv     — coverage/symmetry/connectivity/holes per log
#   logs/run_everything.log      — stdout/stderr from all simulator runs

set -u
cd "$(dirname "$0")/.."

if [ ! -x bin/chess_variant ]; then
    echo "ERROR: bin/chess_variant not found. Run build_sim.sh first." >&2
    exit 1
fi

mkdir -p logs
rm -f logs/*_grid_log.csv logs/metrics_summary.csv logs/run_everything.log

BATCHES=(
    "scripts/baseline/run_all_scenarios.sh"
    "scripts/adaptive/run_all_adaptive_scenarios.sh"
    "scripts/rules/run_all_rules.sh"
    "scripts/asymmetric/run_all_asymm.sh"
)

echo "=== Running all scenario batches ==="
for batch in "${BATCHES[@]}"; do
    echo ""
    echo "--- $batch ---"
    bash "$batch" 2>&1 | tee -a logs/run_everything.log
done

echo ""
echo "=== Collecting metrics ==="
{
    echo "scenario,coverage,symmetry,connectivity,holes"
    for log in logs/*_grid_log.csv; do
        name=$(basename "$log" _grid_log.csv)
        out=$(python3 scripts/board_metrics.py --from-log "$log" 2>/dev/null) || {
            echo "$name,ERROR,ERROR,ERROR,ERROR"
            continue
        }
        cov=$(echo "$out" | awk '/Coverage:/ {print $2}')
        sym=$(echo "$out" | awk '/Symmetry:/ {print $2}')
        con=$(echo "$out" | awk '/Connectivity:/ {print $2}')
        hol=$(echo "$out" | awk '/Holes:/ {print $2}')
        echo "$name,$cov,$sym,$con,$hol"
    done
} > logs/metrics_summary.csv

echo ""
echo "=== Done ==="
echo "Logs:     logs/*_grid_log.csv ($(ls logs/*_grid_log.csv 2>/dev/null | wc -l) files)"
echo "Metrics:  logs/metrics_summary.csv"
echo "Run log:  logs/run_everything.log"
