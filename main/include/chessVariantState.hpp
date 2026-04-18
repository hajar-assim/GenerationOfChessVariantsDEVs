#ifndef CHESS_VARIANT_STATE_HPP
#define CHESS_VARIANT_STATE_HPP

#include <iostream>
#include <nlohmann/json.hpp>

// cell state for the chess variant model
// each cell is just alive (1) or dead (0)
// uses B23/S23 rules - cell is alive if 2 or 3 neighbors are alive
struct ChessVariantState {
    int alive;  // 0 = dead 1 = alive

    ChessVariantState() : alive(0) {}
    explicit ChessVariantState(int a) : alive(a) {}
};

inline bool operator!=(const ChessVariantState& a, const ChessVariantState& b) {
    return a.alive != b.alive;
}

inline std::ostream& operator<<(std::ostream& os, const ChessVariantState& s) {
    os << "<" << s.alive << ">";
    return os;
}

inline void from_json(const nlohmann::json& j, ChessVariantState& s) {
    j.at("alive").get_to(s.alive);
}

#endif // CHESS_VARIANT_STATE_HPP
