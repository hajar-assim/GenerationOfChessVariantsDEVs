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

    // optional gap: exclude a sub-range from birth/survival
    // used by Rule 5 (B235/S235) where count 4 is excluded from the [2,5] range
    // set to -1 to disable (no gap)
    double birthGapLow;
    double birthGapHigh;
    double survivalGapLow;
    double survivalGapHigh;

    AdaptiveChessVariantState()
        : alive(0),
          birthLow(0.25), birthHigh(0.375),
          survivalLow(0.25), survivalHigh(0.375),
          birthGapLow(-1), birthGapHigh(-1),
          survivalGapLow(-1), survivalGapHigh(-1) {}

    AdaptiveChessVariantState(int a, double bL, double bH, double sL, double sH,
                              double bgL = -1, double bgH = -1,
                              double sgL = -1, double sgH = -1)
        : alive(a), birthLow(bL), birthHigh(bH),
          survivalLow(sL), survivalHigh(sH),
          birthGapLow(bgL), birthGapHigh(bgH),
          survivalGapLow(sgL), survivalGapHigh(sgH) {}
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
    if (j.contains("birthGapLow"))    j.at("birthGapLow").get_to(s.birthGapLow);
    if (j.contains("birthGapHigh"))   j.at("birthGapHigh").get_to(s.birthGapHigh);
    if (j.contains("survivalGapLow")) j.at("survivalGapLow").get_to(s.survivalGapLow);
    if (j.contains("survivalGapHigh")) j.at("survivalGapHigh").get_to(s.survivalGapHigh);
}

#endif // ADAPTIVE_CHESS_VARIANT_STATE_HPP
