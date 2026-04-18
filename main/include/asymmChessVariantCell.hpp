#ifndef ASYMM_CHESS_VARIANT_CELL_HPP
#define ASYMM_CHESS_VARIANT_CELL_HPP

#include <cadmium/modeling/celldevs/asymm/cell.hpp>
#include <cadmium/modeling/celldevs/asymm/config.hpp>
#include <cmath>
#include <string>
#include "adaptiveChessVariantState.hpp"

// asymmetric chess variant cell - density-based transition over an asymmetric
// topology (string cell IDs, per-cell neighborhood maps).
//
// reuses AdaptiveChessVariantState: each cell's "state" block in JSON can
// override birthLow/birthHigh/survivalLow/survivalHigh (plus the optional
// gap fields). this is how rule-zones work - cells in one zone get Rule 1
// thresholds, cells in another zone get Rule 3, etc. the transition logic
// is otherwise identical to AdaptiveChessVariantCell.
class AsymmChessVariantCell
    : public cadmium::celldevs::AsymmCell<AdaptiveChessVariantState, double> {
public:
    using cadmium::celldevs::AsymmCell<AdaptiveChessVariantState, double>::AsymmCell;

    [[nodiscard]] AdaptiveChessVariantState localComputation(
        AdaptiveChessVariantState state,
        const std::unordered_map<
            std::string,
            cadmium::celldevs::NeighborData<AdaptiveChessVariantState, double>
        >& neighborhood) const override {

        int liveCount = 0;
        int totalNeighbors = 0;
        for (const auto& [neighborId, neighborData] : neighborhood) {
            if (neighborData.state->alive == 1) {
                liveCount++;
            }
            totalNeighbors++;
        }

        // self is included in its own neighborhood map; subtract it out
        liveCount -= state.alive;
        totalNeighbors -= 1;

        if (totalNeighbors <= 0) {
            state.alive = 0;
            return state;
        }

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
        const AdaptiveChessVariantState& /*state*/) const override {
        return 1.0;
    }
};

#endif // ASYMM_CHESS_VARIANT_CELL_HPP
