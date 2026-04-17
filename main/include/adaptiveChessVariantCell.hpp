#ifndef ADAPTIVE_CHESS_VARIANT_CELL_HPP
#define ADAPTIVE_CHESS_VARIANT_CELL_HPP

#include <cadmium/modeling/celldevs/grid/cell.hpp>
#include <cadmium/modeling/celldevs/grid/config.hpp>
#include <cmath>
#include "adaptiveChessVariantState.hpp"

// adaptive chess variant cell - density-based transition logic
//
// instead of fixed thresholds (alive if exactly 2 or 3 neighbors),
// the birth and survival thresholds scale with the actual neighborhood size.
// this allows the same model to produce sustained patterns across
// different neighborhood topologies:
//
//   moore (8 neighbors):   thresholds 2-3  (density 0.25-0.375)
//   knight (8 neighbors):  thresholds 2-3  (density 0.25-0.375)
//   bishop (~14 on 8x8):   thresholds 4-5  (density 0.25-0.375)
//   rook (~14 on 8x8):     thresholds 4-5  (density 0.25-0.375)
//   queen (~28 on 8x8):    thresholds 7-11 (density 0.25-0.375)
//
// the neighborhood size is computed dynamically from the actual neighbor
// map passed to localComputation, so edge cells on non-wrapped grids
// automatically get adjusted thresholds.
class AdaptiveChessVariantCell
    : public cadmium::celldevs::GridCell<AdaptiveChessVariantState, double> {
public:
    using cadmium::celldevs::GridCell<AdaptiveChessVariantState, double>::GridCell;

    [[nodiscard]] AdaptiveChessVariantState localComputation(
        AdaptiveChessVariantState state,
        const std::unordered_map<
            cadmium::celldevs::coordinates,
            cadmium::celldevs::NeighborData<AdaptiveChessVariantState, double>
        >& neighborhood) const override {

        // count live neighbors and total neighbor count (excluding self)
        int liveCount = 0;
        int totalNeighbors = 0;

        for (const auto& [neighborId, neighborData] : neighborhood) {
            if (neighborData.state->alive == 1) {
                liveCount++;
            }
            totalNeighbors++;
        }

        // subtract self from both counts
        liveCount -= state.alive;
        totalNeighbors -= 1;  // self is always in the neighborhood map

        if (totalNeighbors <= 0) {
            state.alive = 0;
            return state;
        }

        // compute density-scaled thresholds
        // use floor for low bound and ceil for high bound to give inclusive integer ranges
        if (state.alive == 0) {
            // birth condition
            int minNeeded = static_cast<int>(std::floor(state.birthLow * totalNeighbors));
            int maxAllowed = static_cast<int>(std::ceil(state.birthHigh * totalNeighbors));
            if (minNeeded < 1) minNeeded = 1;  // need at least 1 neighbor to be born
            state.alive = (liveCount >= minNeeded && liveCount <= maxAllowed) ? 1 : 0;
        } else {
            // survival condition
            int minNeeded = static_cast<int>(std::floor(state.survivalLow * totalNeighbors));
            int maxAllowed = static_cast<int>(std::ceil(state.survivalHigh * totalNeighbors));
            if (minNeeded < 1) minNeeded = 1;
            state.alive = (liveCount >= minNeeded && liveCount <= maxAllowed) ? 1 : 0;
        }

        return state;
    }

    [[nodiscard]] double outputDelay(
        const AdaptiveChessVariantState& /* state */) const override {
        return 1.0;
    }
};

#endif // ADAPTIVE_CHESS_VARIANT_CELL_HPP
