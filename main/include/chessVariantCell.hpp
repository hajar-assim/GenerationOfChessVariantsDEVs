#ifndef CHESS_VARIANT_CELL_HPP
#define CHESS_VARIANT_CELL_HPP

#include <cadmium/modeling/celldevs/grid/cell.hpp>
#include <cadmium/modeling/celldevs/grid/config.hpp>
#include "chessVariantState.hpp"

// chess variant cell - implements the transition logic
// counts live neighbors and applies B23/S23 rules
// the original cd++ model uses trueCount which includes self in the count
// so we count all neighbors then subtract self to get the actual neighbor count
// both birth and survival conditions end up being the same: alive if 2 or 3 neighbors
// transport delay of 1.0 per generation (rescaled from the original 100 units)
class ChessVariantCell
    : public cadmium::celldevs::GridCell<ChessVariantState, double> {
public:
    using cadmium::celldevs::GridCell<ChessVariantState, double>::GridCell;

    // count live neighbors and apply transition rules
    [[nodiscard]] ChessVariantState localComputation(
        ChessVariantState state,
        const std::unordered_map<
            cadmium::celldevs::coordinates,
            cadmium::celldevs::NeighborData<ChessVariantState, double>
        >& neighborhood) const override {

        // count all live cells in neighborhood including self
        int liveCount = 0;
        for (const auto& [neighborId, neighborData] : neighborhood) {
            if (neighborData.state->alive == 1) {
                liveCount++;
            }
        }
        // subtract self so we only count actual neighbors
        liveCount -= state.alive;

        // alive if exactly 2 or 3 neighbors are alive otherwise dead
        if (liveCount == 2 || liveCount == 3) {
            state.alive = 1;
        } else {
            state.alive = 0;
        }

        return state;
    }

    // transport delay of 1 time unit per generation
    [[nodiscard]] double outputDelay(
        const ChessVariantState& /* state */) const override {
        return 1.0;
    }
};

#endif // CHESS_VARIANT_CELL_HPP
