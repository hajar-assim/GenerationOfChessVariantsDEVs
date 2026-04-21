#ifndef CHESS_INFECTION_STATE_HPP
#define CHESS_INFECTION_STATE_HPP

#include <iostream>
#include <nlohmann/json.hpp>

// chess infection propagation state
//
// models SIR-style disease spread over chess-piece movement patterns.
// two competing infections (white=1, black=2) start on opposite sides of
// the board and spread outward through the configured piece topology.
// cells move one-way: susceptible -> infected -> recovered. recovered
// cells are immune and permanently block line-of-sight for sliding
// pieces, producing natural territorial barriers where fronts collide.
//
//   status:     0 = susceptible, 1 = infected, 2 = recovered
//   color:      0 = none, 1 = white, 2 = black
//   pieceType:  3 = bishop, 4 = rook, 5 = queen, 6 = king, 2 = knight
//               (pieceType is scenario-wide; read from JSON on every cell
//                since Cadmium does not expose a global-config hook)
//
// the `display` field packs status+color into a signed integer that
// viewer colour bands can render cleanly:
//
//   -2 = black recovered (dark red)
//   -1 = black infected  (red)
//    0 = susceptible     (grey)
//   +1 = white infected  (light blue)
//   +2 = white recovered (dark blue)
struct ChessInfectionState {
    int status;
    int color;
    int infectedSteps;
    int recoveryDuration;
    int pieceType;
    int display;

    ChessInfectionState()
        : status(0), color(0),
          infectedSteps(0), recoveryDuration(5),
          pieceType(6), display(0) {}
};

inline bool operator!=(const ChessInfectionState& a, const ChessInfectionState& b) {
    return a.status != b.status ||
           a.color != b.color ||
           a.infectedSteps != b.infectedSteps ||
           a.display != b.display;
}

inline std::ostream& operator<<(std::ostream& os, const ChessInfectionState& s) {
    os << "<" << s.display << ">";
    return os;
}

inline void from_json(const nlohmann::json& j, ChessInfectionState& s) {
    if (j.contains("status"))           j.at("status").get_to(s.status);
    if (j.contains("color"))            j.at("color").get_to(s.color);
    if (j.contains("infectedSteps"))    j.at("infectedSteps").get_to(s.infectedSteps);
    if (j.contains("recoveryDuration")) j.at("recoveryDuration").get_to(s.recoveryDuration);
    if (j.contains("pieceType"))        j.at("pieceType").get_to(s.pieceType);

    // derive display from (status, color) so configs don't have to specify it
    if (s.status == 0) {
        s.display = 0;
    } else if (s.status == 1) {
        s.display = (s.color == 1) ? 1 : (s.color == 2) ? -1 : 0;
    } else {
        s.display = (s.color == 1) ? 2 : (s.color == 2) ? -2 : 0;
    }
}

#endif // CHESS_INFECTION_STATE_HPP
