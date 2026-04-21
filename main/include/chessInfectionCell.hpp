#ifndef CHESS_INFECTION_CELL_HPP
#define CHESS_INFECTION_CELL_HPP

#include <cadmium/modeling/celldevs/grid/cell.hpp>
#include <cadmium/modeling/celldevs/grid/config.hpp>
#include <cmath>
#include "chessInfectionState.hpp"

using namespace cadmium::celldevs;

// chess infection cell - SIR propagation over chess-piece movement patterns
//
// transition logic:
//   recovered -> no change (terminal, immune)
//   infected  -> increment step counter; if >= recoveryDuration, recover
//                (colour persists into the recovered state)
//   susceptible -> look at infected neighbours visible through the piece's
//                  movement pattern. for sliding pieces (bishop/rook/queen)
//                  an intermediate non-susceptible cell blocks line of sight.
//                  compare white-infected count vs black-infected count:
//                    * strict majority of white -> become white-infected
//                    * strict majority of black -> become black-infected
//                    * tied or zero -> stay susceptible (contested / untouched)
//
// this produces expanding fronts from each coloured seed. where fronts
// meet with equal pressure, cells stay susceptible — giving a visible
// neutral boundary. where one front arrives first, it wins the territory,
// then recovers into a permanent barrier that deflects further spread.
class ChessInfectionCell : public GridCell<ChessInfectionState, double> {
public:
    using GridCell<ChessInfectionState, double>::GridCell;

    [[nodiscard]] ChessInfectionState localComputation(
        ChessInfectionState state,
        const std::unordered_map<
            coordinates,
            NeighborData<ChessInfectionState, double>
        >& neighborhood) const override {

        if (state.status == 2) {
            // recovered cells are terminal
            return state;
        }

        if (state.status == 1) {
            // infected cells tick toward recovery
            state.infectedSteps++;
            if (state.infectedSteps >= state.recoveryDuration) {
                state.status = 2;
                state.display = (state.color == 1) ? 2 : -2;
            }
            return state;
        }

        // susceptible: look for infection from neighbours
        bool slidingPiece = (state.pieceType == 3 ||  // bishop
                              state.pieceType == 4 ||  // rook
                              state.pieceType == 5);   // queen

        int whiteCount = 0;
        int blackCount = 0;

        for (const auto& [nId, nData] : neighborhood) {
            int dr = nId[0];
            int dc = nId[1];
            if (dr == 0 && dc == 0) continue;   // skip self

            const auto& ns = *nData.state;
            if (ns.status != 1) continue;        // only infected cells transmit

            // sliding pieces: block if any intermediate cell is non-susceptible
            if (slidingPiece && !hasLineOfSight(dr, dc, neighborhood)) continue;

            if (ns.color == 1) whiteCount++;
            else if (ns.color == 2) blackCount++;
        }

        if (whiteCount > blackCount) {
            state.status = 1;
            state.color = 1;
            state.infectedSteps = 0;
            state.display = 1;
        } else if (blackCount > whiteCount) {
            state.status = 1;
            state.color = 2;
            state.infectedSteps = 0;
            state.display = -1;
        }
        // tied (including 0/0) -> stay susceptible

        return state;
    }

    [[nodiscard]] double outputDelay(const ChessInfectionState& /*state*/) const override {
        return 1.0;
    }

private:
    // walk one step at a time from origin toward the neighbour at (dr,dc);
    // return false if any intermediate cell is infected or recovered
    bool hasLineOfSight(
        int dr, int dc,
        const std::unordered_map<coordinates, NeighborData<ChessInfectionState, double>>& neighborhood
    ) const {
        int dist = std::max(std::abs(dr), std::abs(dc));
        if (dist <= 1) return true;

        int stepR = (dr > 0) ? 1 : (dr < 0) ? -1 : 0;
        int stepC = (dc > 0) ? 1 : (dc < 0) ? -1 : 0;

        for (int i = 1; i < dist; i++) {
            coordinates mid = {stepR * i, stepC * i};
            auto it = neighborhood.find(mid);
            if (it != neighborhood.end() && it->second.state->status != 0) {
                return false;   // blocked by infected or recovered cell
            }
        }
        return true;
    }
};

#endif // CHESS_INFECTION_CELL_HPP
