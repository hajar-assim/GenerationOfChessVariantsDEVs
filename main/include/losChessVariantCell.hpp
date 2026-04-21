#ifndef LOS_CHESS_VARIANT_CELL_HPP
#define LOS_CHESS_VARIANT_CELL_HPP

#include <cadmium/modeling/celldevs/grid/cell.hpp>
#include <cadmium/modeling/celldevs/grid/config.hpp>
#include <cmath>
#include <cstdlib>
#include "adaptiveChessVariantState.hpp"

using namespace cadmium::celldevs;

// line-of-sight chess variant cell
//
// extends the adaptive chess variant with line-of-sight blocking for
// sliding piece neighborhoods (bishop, rook, queen).
//
// in the standard adaptive model, all cells in the neighborhood are
// counted equally. a rook cell counts neighbors at distance 1 and
// distance 7 the same way, regardless of whether cells in between
// are alive and would block the line of sight.
//
// this model adds blocking: for each neighbor along a straight line
// (diagonal, rank, or file), the transition function checks whether
// any intermediate cell on that line is alive. if so, the distant
// neighbor is blocked and not counted.
//
// this makes the effective neighborhood dynamic — it changes as cells
// flip between alive and dead, because live cells create "shadows"
// that block influence from reaching cells behind them.
//
// the blocking check applies to neighbors at distance > 1 that lie on
// a straight line (same row, same column, or same diagonal). neighbors
// that don't fit a straight line pattern (like knight offsets) or are
// at distance 1 are always counted normally.
//
// uses the same AdaptiveChessVariantState as the adaptive model,
// so all existing threshold and gap logic is preserved.

class LOSChessVariantCell
    : public GridCell<AdaptiveChessVariantState, double> {
public:
    using GridCell<AdaptiveChessVariantState, double>::GridCell;

    [[nodiscard]] AdaptiveChessVariantState localComputation(
        AdaptiveChessVariantState state,
        const std::unordered_map<
            coordinates,
            NeighborData<AdaptiveChessVariantState, double>
        >& neighborhood) const override {

        int liveCount = 0;
        int totalNeighbors = 0;

        for (const auto& [neighborId, neighborData] : neighborhood) {
            int dr = neighborId[0];
            int dc = neighborId[1];

            // skip self
            if (dr == 0 && dc == 0) continue;

            // check if this neighbor is blocked by an intervening live cell
            if (isBlocked(dr, dc, neighborhood)) {
                // blocked neighbors don't count toward density at all.
                // they are excluded from both liveCount AND totalNeighbors,
                // so the effective neighborhood size shrinks dynamically.
                continue;
            }

            totalNeighbors++;
            if (neighborData.state->alive == 1) {
                liveCount++;
            }
        }

        if (totalNeighbors <= 0) {
            state.alive = 0;
            return state;
        }

        // same threshold logic as the adaptive model
        if (state.alive == 0) {
            int minNeeded = static_cast<int>(std::floor(state.birthLow * totalNeighbors));
            int maxAllowed = static_cast<int>(std::ceil(state.birthHigh * totalNeighbors));
            if (minNeeded < 1) minNeeded = 1;
            bool inRange = (liveCount >= minNeeded && liveCount <= maxAllowed);
            if (inRange && state.birthGapLow >= 0) {
                int gapMin = static_cast<int>(std::floor(state.birthGapLow * totalNeighbors));
                int gapMax = static_cast<int>(std::ceil(state.birthGapHigh * totalNeighbors));
                if (liveCount >= gapMin && liveCount <= gapMax) inRange = false;
            }
            state.alive = inRange ? 1 : 0;
        } else {
            int minNeeded = static_cast<int>(std::floor(state.survivalLow * totalNeighbors));
            int maxAllowed = static_cast<int>(std::ceil(state.survivalHigh * totalNeighbors));
            if (minNeeded < 1) minNeeded = 1;
            bool inRange = (liveCount >= minNeeded && liveCount <= maxAllowed);
            if (inRange && state.survivalGapLow >= 0) {
                int gapMin = static_cast<int>(std::floor(state.survivalGapLow * totalNeighbors));
                int gapMax = static_cast<int>(std::ceil(state.survivalGapHigh * totalNeighbors));
                if (liveCount >= gapMin && liveCount <= gapMax) inRange = false;
            }
            state.alive = inRange ? 1 : 0;
        }

        return state;
    }

    [[nodiscard]] double outputDelay(
        const AdaptiveChessVariantState& /* state */) const override {
        return 1.0;
    }

private:
    // check if a neighbor at relative offset (dr, dc) is blocked by
    // an intervening live cell on the same line.
    //
    // blocking only applies to cells on a straight line (diagonal, rank,
    // or file) at distance > 1. this covers bishop, rook, and queen
    // movement patterns. knight offsets and adjacent cells (distance 1)
    // are never blocked.
    bool isBlocked(
        int dr, int dc,
        const std::unordered_map<
            coordinates,
            NeighborData<AdaptiveChessVariantState, double>
        >& neighborhood) const {

        int absDr = std::abs(dr);
        int absDc = std::abs(dc);

        // determine if this offset lies on a straight line (slideable)
        bool isStraightLine = false;
        int distance = 0;

        if (dr == 0 && dc != 0) {
            // same row (rook-like horizontal)
            isStraightLine = true;
            distance = absDc;
        } else if (dc == 0 && dr != 0) {
            // same column (rook-like vertical)
            isStraightLine = true;
            distance = absDr;
        } else if (absDr == absDc) {
            // diagonal (bishop-like)
            isStraightLine = true;
            distance = absDr;
        }

        // not on a straight line (e.g. knight offset) or adjacent: never blocked
        if (!isStraightLine || distance <= 1) {
            return false;
        }

        // compute step direction from self toward the neighbor
        int stepR = (dr > 0) ? 1 : (dr < 0) ? -1 : 0;
        int stepC = (dc > 0) ? 1 : (dc < 0) ? -1 : 0;

        // walk along the line from self toward the neighbor,
        // checking each intermediate cell
        for (int i = 1; i < distance; i++) {
            coordinates midPoint = {stepR * i, stepC * i};
            auto it = neighborhood.find(midPoint);
            if (it != neighborhood.end() && it->second.state->alive == 1) {
                return true; // blocked by a live cell
            }
        }

        return false; // line of sight is clear
    }
};

#endif // LOS_CHESS_VARIANT_CELL_HPP
