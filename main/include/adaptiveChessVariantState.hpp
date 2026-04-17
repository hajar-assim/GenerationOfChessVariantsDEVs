#ifndef ADAPTIVE_CHESS_VARIANT_STATE_HPP
#define ADAPTIVE_CHESS_VARIANT_STATE_HPP

#include <iostream>
#include <nlohmann/json.hpp>

// adaptive cell state for the chess variant model
// extends the original binary alive/dead state with density-based thresholds
// birth and survival conditions are expressed as fractions of the neighborhood size
// so the same rule set can work across different neighborhood topologies
// (moore ~8 neighbors, bishop ~28, rook ~28, queen ~56, knight 8)
struct AdaptiveChessVariantState {
    int alive;           // 0 = dead, 1 = alive

    // density thresholds (fractions of neighborhood size)
    // a cell is born (0->1) if neighbor density is in [birthLow, birthHigh]
    // a cell survives (1->1) if neighbor density is in [survivalLow, survivalHigh]
    double birthLow;     // minimum fraction of live neighbors for birth
    double birthHigh;    // maximum fraction of live neighbors for birth
    double survivalLow;  // minimum fraction of live neighbors for survival
    double survivalHigh; // maximum fraction of live neighbors for survival

    AdaptiveChessVariantState()
        : alive(0),
          birthLow(0.25), birthHigh(0.375),
          survivalLow(0.25), survivalHigh(0.375) {}

    AdaptiveChessVariantState(int a, double bL, double bH, double sL, double sH)
        : alive(a), birthLow(bL), birthHigh(bH),
          survivalLow(sL), survivalHigh(sH) {}
};

inline bool operator!=(const AdaptiveChessVariantState& a, const AdaptiveChessVariantState& b) {
    return a.alive != b.alive;
}

inline std::ostream& operator<<(std::ostream& os, const AdaptiveChessVariantState& s) {
    os << "<" << s.alive << ">";
    return os;
}

inline void from_json(const nlohmann::json& j, AdaptiveChessVariantState& s) {
    j.at("alive").get_to(s.alive);
    if (j.contains("birthLow"))    j.at("birthLow").get_to(s.birthLow);
    if (j.contains("birthHigh"))   j.at("birthHigh").get_to(s.birthHigh);
    if (j.contains("survivalLow")) j.at("survivalLow").get_to(s.survivalLow);
    if (j.contains("survivalHigh")) j.at("survivalHigh").get_to(s.survivalHigh);
}

#endif // ADAPTIVE_CHESS_VARIANT_STATE_HPP
