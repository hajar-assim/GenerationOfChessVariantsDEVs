#ifndef LIFECYCLE_CHESS_VARIANT_CELL_HPP
#define LIFECYCLE_CHESS_VARIANT_CELL_HPP

#include <cadmium/modeling/celldevs/grid/cell.hpp>
#include <cadmium/modeling/celldevs/grid/config.hpp>
#include <cmath>
#include <algorithm>
#include "lifecycleChessVariantState.hpp"

using namespace cadmium::celldevs;

// lifecycle chess variant cell - continuous activity with phase transitions
//
// this cell extends the adaptive chess variant model by replacing the
// binary alive/dead state with a continuous activity lifecycle.
//
// the transition function evaluates differently depending on the current phase:
//
//   dormant:    compute neighbor density (weighted by activity).
//               if density falls within birth threshold range,
//               transition to activating phase.
//
//   activating: increase activity by activationRate.
//               if activity reaches 1.0, transition to active phase.
//               if neighbor density drops below birth range, revert to dormant.
//
//   active:     cell is fully on (activity = 1.0).
//               increment stepsInPhase counter.
//               if counter exceeds activeDuration, transition to decaying.
//               can also begin decaying early if neighbor density drops
//               below survival threshold range.
//
//   decaying:   decrease activity by decayRate.
//               if activity reaches 0.0, transition to dormant.
//
// neighbor density is computed as a weighted sum: each neighbor contributes
// its activity value (0.0 to 1.0) rather than a binary 0 or 1. this means
// partially active neighbors exert partial influence, creating smoother
// wavefront dynamics as activation ripples across the grid.

class LifecycleChessVariantCell
    : public GridCell<LifecycleChessVariantState, double> {
public:
    using GridCell<LifecycleChessVariantState, double>::GridCell;

    [[nodiscard]] LifecycleChessVariantState localComputation(
        LifecycleChessVariantState state,
        const std::unordered_map<
            coordinates,
            NeighborData<LifecycleChessVariantState, double>
        >& neighborhood) const override {

        // compute weighted neighbor density
        // each neighbor contributes its activity level (0.0 to 1.0)
        // instead of binary 0/1, giving smoother gradients
        double activeSum = 0.0;
        int totalNeighbors = 0;

        for (const auto& [neighborId, neighborData] : neighborhood) {
            activeSum += neighborData.state->activity;
            totalNeighbors++;
        }

        // subtract self contribution
        activeSum -= state.activity;
        totalNeighbors -= 1;

        if (totalNeighbors <= 0) {
            state.activity = 0.0;
            state.phase = 0;
            return state;
        }

        double density = activeSum / static_cast<double>(totalNeighbors);

        switch (state.phase) {
            case 0: { // dormant
                // check birth condition: is neighbor density in birth range?
                if (density >= state.birthLow && density <= state.birthHigh) {
                    state.phase = 1; // begin activating
                    state.stepsInPhase = 0;
                    state.activity = state.activationRate; // first step of activation
                }
                break;
            }

            case 1: { // activating
                // once activation has begun, continue regardless of density.
                // the birth threshold was the gate to START activating;
                // once past that gate, the cell commits to full activation.
                // this prevents fragile wavefronts where partially active
                // cells kill each other by lowering their mutual density.
                state.activity += state.activationRate;
                state.stepsInPhase++;
                if (state.activity >= 1.0) {
                    state.activity = 1.0;
                    state.phase = 2; // transition to active
                    state.stepsInPhase = 0;
                }
                break;
            }

            case 2: { // active
                state.stepsInPhase++;
                state.activity = 1.0;

                // cell remains active for exactly activeDuration steps.
                // this guarantees enough time for neighbors to detect the
                // active cell and begin their own activation, enabling
                // the wavefront to propagate outward before the source decays.
                if (state.stepsInPhase >= state.activeDuration) {
                    state.phase = 3; // begin decaying
                    state.stepsInPhase = 0;
                }
                break;
            }

            case 3: { // decaying
                state.activity -= state.decayRate;
                state.stepsInPhase++;

                if (state.activity <= 0.0) {
                    state.activity = 0.0;
                    state.phase = 0; // return to dormant
                    state.stepsInPhase = 0;
                }
                break;
            }
        }

        return state;
    }

    [[nodiscard]] double outputDelay(
        const LifecycleChessVariantState& /* state */) const override {
        return 1.0;
    }
};

#endif // LIFECYCLE_CHESS_VARIANT_CELL_HPP
