#ifndef PROPAGATION_CHESS_VARIANT_CELL_HPP
#define PROPAGATION_CHESS_VARIANT_CELL_HPP

#include <cadmium/modeling/celldevs/grid/cell.hpp>
#include <cadmium/modeling/celldevs/grid/config.hpp>
#include <cmath>
#include "propagationChessVariantState.hpp"

using namespace cadmium::celldevs;

// propagation chess variant cell
//
// transition function for the influence propagation model.
// handles the neutral -> active -> exhausted -> neutral cycle
// and computes neighbor-driven spreading.

class PropagationChessVariantCell
    : public GridCell<PropagationChessVariantState, double> {
public:
    using GridCell<PropagationChessVariantState, double>::GridCell;

    [[nodiscard]] PropagationChessVariantState localComputation(
        PropagationChessVariantState state,
        const std::unordered_map<
            coordinates,
            NeighborData<PropagationChessVariantState, double>
        >& neighborhood) const override {

        // increment step counter to keep all cells active in the simulation.
        // without this, neutral cells go passive and never check for new
        // active neighbors, so the wavefront never spreads.
        state.step++;

        switch (state.phase) {
            case 0: { // neutral — check if neighbors trigger activation
                int activeNeighbors = 0;
                int totalNeighbors = 0;

                for (const auto& [neighborId, neighborData] : neighborhood) {
                    if (neighborId[0] == 0 && neighborId[1] == 0) continue; // skip self
                    totalNeighbors++;
                    if (neighborData.state->phase == 1) { // count active neighbors
                        activeNeighbors++;
                    }
                }

                if (totalNeighbors > 0) {
                    double activeFraction = static_cast<double>(activeNeighbors) / totalNeighbors;
                    if (activeFraction >= state.spreadThreshold && activeNeighbors >= 1) {
                        // activate: transition to active phase
                        state.phase = 1;
                        state.activity = 1.0;
                        state.stepsInPhase = 0;
                    }
                }
                break;
            }

            case 1: { // active — stay active for activeDuration steps
                state.stepsInPhase++;
                if (state.stepsInPhase >= state.activeDuration) {
                    // exhausted: begin cooldown
                    state.phase = 2;
                    state.stepsInPhase = 0;
                    // activity starts decaying from 1.0
                }
                break;
            }

            case 2: { // exhausted — decay toward neutral
                state.stepsInPhase++;
                state.activity -= state.decayRate;
                if (state.activity <= 0.001) {
                    // fully cooled down, return to neutral
                    state.activity = 0.0;
                    state.phase = 0;
                    state.stepsInPhase = 0;
                }
                break;
            }
        }

        return state;
    }

    [[nodiscard]] double outputDelay(
        const PropagationChessVariantState& /* state */) const override {
        return 1.0;
    }
};

#endif // PROPAGATION_CHESS_VARIANT_CELL_HPP
