#ifndef BOARD_CONTROL_CELL_HPP
#define BOARD_CONTROL_CELL_HPP

#include <cadmium/modeling/celldevs/grid/cell.hpp>
#include <cadmium/modeling/celldevs/grid/config.hpp>
#include <cmath>
#include <cstdlib>
#include <algorithm>
#include "boardControlState.hpp"

using namespace cadmium::celldevs;

// board control cell - influence propagation model
//
// this cell computes territorial control on a chess board by simulating
// how pieces project influence along their movement patterns.
//
// the transition function has two components:
//
// 1. DIRECT INFLUENCE: each piece in the neighborhood contributes influence
//    to the current cell based on whether the piece can "see" this cell
//    through its movement pattern. sliding pieces (bishop, rook, queen)
//    are blocked by intervening pieces (line of sight). influence decays
//    with distance for sliding pieces (strength / distance).
//
// 2. PROPAGATION: a fraction of each neighbor's accumulated influence
//    spreads to this cell, simulating secondary/indirect control.
//    this causes influence to ripple outward over simulation steps.
//
// the combination produces a heatmap showing which side controls
// which regions of the board, accounting for piece mobility,
// line-of-sight blocking, and cascading territorial pressure.

class BoardControlCell
    : public GridCell<BoardControlState, double> {
public:
    using GridCell<BoardControlState, double>::GridCell;

    // piece strength values (standard chess piece values)
    static constexpr double STRENGTH[] = {0.0, 1.0, 3.0, 3.25, 5.0, 9.0, 4.0};
    //                                    empty pawn  knight bishop rook queen king

    [[nodiscard]] BoardControlState localComputation(
        BoardControlState state,
        const std::unordered_map<
            coordinates,
            NeighborData<BoardControlState, double>
        >& neighborhood) const override {

        // === COMPONENT 1: DIRECT PIECE INFLUENCE (constant base) ===
        // this is the same every step — pieces project influence along
        // their movement patterns with line-of-sight blocking
        double directWhite = 0.0;
        double directBlack = 0.0;

        // if this cell has a piece, it strongly influences itself
        if (state.pieceType > 0) {
            double selfStrength = STRENGTH[state.pieceType];
            if (state.pieceColor == 1) directWhite += selfStrength;
            else if (state.pieceColor == 2) directBlack += selfStrength;
        }

        for (const auto& [nId, nData] : neighborhood) {
            const auto& ns = *nData.state;
            int dr = nId[0];
            int dc = nId[1];

            if (ns.pieceType > 0 && (dr != 0 || dc != 0)) {
                double influence = computePieceInfluence(
                    ns.pieceType, ns.pieceColor, dr, dc, neighborhood);

                if (ns.pieceColor == 1) directWhite += influence;
                else if (ns.pieceColor == 2) directBlack += influence;
            }
        }

        // === COMPONENT 2: PROPAGATION (accumulates over time) ===
        // each step, cells absorb a fraction of their immediate neighbors'
        // accumulated influence. this causes control to ripple outward
        // from pieces over multiple simulation steps, like heat diffusion.
        double propagatedWhite = 0.0;
        double propagatedBlack = 0.0;

        for (const auto& [nId, nData] : neighborhood) {
            int dr = nId[0];
            int dc = nId[1];
            // only immediate neighbors (Moore range 1)
            if (std::abs(dr) <= 1 && std::abs(dc) <= 1 && (dr != 0 || dc != 0)) {
                propagatedWhite += nData.state->whiteInfluence;
                propagatedBlack += nData.state->blackInfluence;
            }
        }

        // new influence = direct (constant) + propagated (grows over time)
        // the propagation term uses a decay factor so it doesn't explode
        state.whiteInfluence = directWhite + propagatedWhite * state.propagationRate;
        state.blackInfluence = directBlack + propagatedBlack * state.propagationRate;

        // control field for the viewer: positive = white, negative = black
        state.control = state.whiteInfluence - state.blackInfluence;
        state.step += 1;

        return state;
    }

    [[nodiscard]] double outputDelay(
        const BoardControlState& /* state */) const override {
        return 1.0;
    }

private:
    // compute how much influence a piece at relative offset (dr, dc) exerts on cell (0,0)
    // returns 0 if the piece cannot reach this cell through its movement pattern
    double computePieceInfluence(
        int pieceType, int pieceColor, int dr, int dc,
        const std::unordered_map<coordinates, NeighborData<BoardControlState, double>>& neighborhood
    ) const {
        double strength = STRENGTH[pieceType];
        // dr, dc is offset FROM SELF TO NEIGHBOR (where the piece is)
        // so the piece at (dr, dc) attacks us at (0, 0)
        // the piece needs to be able to reach (0,0) from (dr, dc)
        // equivalently: can a piece at origin reach (-dr, -dc)?
        int targetDr = -dr;
        int targetDc = -dc;

        switch (pieceType) {
            case 1: { // pawn - attacks diagonally forward
                int forward = (pieceColor == 1) ? -1 : 1; // white moves up (negative row)
                // pawn at (dr,dc) attacks forward diagonals from its position
                // it attacks (dr+forward, dc-1) and (dr+forward, dc+1)
                // we are at (0,0), so check if (0,0) is one of those squares
                if (dr + forward == 0 && (dc - 1 == 0 || dc + 1 == 0)) {
                    return strength;
                }
                return 0.0;
            }
            case 2: { // knight - L-shape, no blocking
                int adr = std::abs(targetDr), adc = std::abs(targetDc);
                if ((adr == 2 && adc == 1) || (adr == 1 && adc == 2)) {
                    return strength;
                }
                return 0.0;
            }
            case 3: { // bishop - diagonal rays, blocked by pieces
                if (std::abs(targetDr) != std::abs(targetDc) || targetDr == 0) return 0.0;
                return slidingInfluence(dr, dc, targetDr, targetDc, strength, neighborhood);
            }
            case 4: { // rook - rank/file rays, blocked by pieces
                if (targetDr != 0 && targetDc != 0) return 0.0;
                if (targetDr == 0 && targetDc == 0) return 0.0;
                return slidingInfluence(dr, dc, targetDr, targetDc, strength, neighborhood);
            }
            case 5: { // queen - diagonal + rank/file
                bool isDiag = (std::abs(targetDr) == std::abs(targetDc) && targetDr != 0);
                bool isStraight = ((targetDr == 0) != (targetDc == 0));
                if (!isDiag && !isStraight) return 0.0;
                return slidingInfluence(dr, dc, targetDr, targetDc, strength, neighborhood);
            }
            case 6: { // king - adjacent squares
                if (std::abs(targetDr) <= 1 && std::abs(targetDc) <= 1 &&
                    (targetDr != 0 || targetDc != 0)) {
                    return strength;
                }
                return 0.0;
            }
            default:
                return 0.0;
        }
    }

    // check line of sight for sliding pieces and compute distance-decayed influence
    // the piece is at (pieceDr, pieceDc) relative to us
    // it needs to reach (0,0) along direction (targetDr, targetDc) from origin
    double slidingInfluence(
        int pieceDr, int pieceDc, int targetDr, int targetDc,
        double strength,
        const std::unordered_map<coordinates, NeighborData<BoardControlState, double>>& neighborhood
    ) const {
        int dist = std::max(std::abs(targetDr), std::abs(targetDc));
        if (dist == 0) return 0.0;

        // direction from piece toward us (step by step)
        int stepR = (targetDr > 0) ? 1 : (targetDr < 0) ? -1 : 0;
        int stepC = (targetDc > 0) ? 1 : (targetDc < 0) ? -1 : 0;

        // walk from the piece toward us, checking for blocking pieces
        // piece is at relative (pieceDr, pieceDc), we walk toward (0,0)
        for (int i = 1; i < dist; i++) {
            // intermediate square (relative to self)
            int midR = pieceDr + stepR * i;
            int midC = pieceDc + stepC * i;
            coordinates midCoord = {midR, midC};

            auto it = neighborhood.find(midCoord);
            if (it != neighborhood.end() && it->second.state->pieceType > 0) {
                return 0.0; // blocked by a piece
            }
        }

        // not blocked — return distance-decayed influence
        return strength / static_cast<double>(dist);
    }
};

#endif // BOARD_CONTROL_CELL_HPP
