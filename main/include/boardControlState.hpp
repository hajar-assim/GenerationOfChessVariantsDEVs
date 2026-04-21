#ifndef BOARD_CONTROL_STATE_HPP
#define BOARD_CONTROL_STATE_HPP

#include <iostream>
#include <nlohmann/json.hpp>

// board control analysis state for chess position evaluation
//
// each cell represents a square on the chess board and tracks:
//   - what piece (if any) occupies it
//   - accumulated white and black influence from nearby pieces
//
// pieces project influence along their movement patterns:
//   pawn:   diagonal forward squares
//   knight: L-shaped jumps (no blocking)
//   bishop: diagonal rays (blocked by pieces)
//   rook:   rank/file rays (blocked by pieces)
//   queen:  diagonal + rank/file rays (blocked by pieces)
//   king:   adjacent squares
//
// influence decays with distance for sliding pieces (1/d)
// and propagates to adjacent cells each simulation step
//
// piece types: 0=empty, 1=pawn, 2=knight, 3=bishop, 4=rook, 5=queen, 6=king
// piece colors: 0=none, 1=white, 2=black
struct BoardControlState {
    int pieceType;         // 0-6 (empty, pawn, knight, bishop, rook, queen, king)
    int pieceColor;        // 0=none, 1=white, 2=black
    double whiteInfluence; // accumulated white control on this square
    double blackInfluence; // accumulated black control on this square
    double control;        // whiteInfluence - blackInfluence (for viewer)
    double propagationRate; // fraction of influence that spreads to neighbors each step
    int step;              // internal step counter for time-varying behavior

    BoardControlState()
        : pieceType(0), pieceColor(0),
          whiteInfluence(0.0), blackInfluence(0.0),
          control(0.0), propagationRate(0.15),
          step(0) {}

    BoardControlState(int pt, int pc, double wi, double bi, double ctrl, double pr, int s)
        : pieceType(pt), pieceColor(pc),
          whiteInfluence(wi), blackInfluence(bi),
          control(ctrl), propagationRate(pr),
          step(s) {}
};

// state changes when influence or step changes
inline bool operator!=(const BoardControlState& a, const BoardControlState& b) {
    const double threshold = 0.001;
    return a.step != b.step ||
           std::abs(a.whiteInfluence - b.whiteInfluence) > threshold ||
           std::abs(a.blackInfluence - b.blackInfluence) > threshold;
}

inline std::ostream& operator<<(std::ostream& os, const BoardControlState& s) {
    os << "<" << s.pieceType << "," << s.pieceColor << ","
       << s.whiteInfluence << "," << s.blackInfluence << ","
       << s.control << ">";
    return os;
}

inline void from_json(const nlohmann::json& j, BoardControlState& s) {
    j.at("pieceType").get_to(s.pieceType);
    j.at("pieceColor").get_to(s.pieceColor);
    if (j.contains("whiteInfluence"))  j.at("whiteInfluence").get_to(s.whiteInfluence);
    if (j.contains("blackInfluence"))  j.at("blackInfluence").get_to(s.blackInfluence);
    if (j.contains("control"))         j.at("control").get_to(s.control);
    if (j.contains("propagationRate")) j.at("propagationRate").get_to(s.propagationRate);
    if (j.contains("step"))            j.at("step").get_to(s.step);
}

#endif // BOARD_CONTROL_STATE_HPP
