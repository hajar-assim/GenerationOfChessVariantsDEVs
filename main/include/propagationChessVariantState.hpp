#ifndef PROPAGATION_CHESS_VARIANT_STATE_HPP
#define PROPAGATION_CHESS_VARIANT_STATE_HPP

#include <iostream>
#include <nlohmann/json.hpp>

// propagation chess variant cell state
//
// models how territorial control spreads across a chessboard through
// piece movement topologies. unlike the adaptive or lifecycle models
// which focus on local density thresholds, this model captures how
// influence radiates outward from an origin through a piece's
// reachable squares.
//
// each cell cycles through three phases:
//
//   neutral (phase = 0, activity = 0):
//       uncontrolled square. becomes active if at least one neighbor
//       (reachable via the piece's movement) is currently active.
//       this drives the spreading wavefront.
//
//   active (phase = 1, activity = 1):
//       controlled square. contributes to spreading influence to
//       its neutral neighbors. remains active for activeDuration
//       steps, then becomes exhausted.
//
//   exhausted (phase = 2, activity decreasing toward 0):
//       square that was recently controlled but has been depleted.
//       cannot be reactivated during cooldown. activity decreases
//       by decayRate each step. once activity reaches 0, the cell
//       returns to neutral and can be activated again in a future wave.
//
// the spreading threshold controls how easily influence propagates:
//   spreadThreshold = minimum fraction of active neighbors needed
//   to activate a neutral cell. lower values mean easier spreading.
//
// different piece topologies produce different wavefront shapes:
//   - rook: spreads along ranks and files (cross-shaped waves)
//   - bishop: spreads along diagonals (X-shaped waves)
//   - queen: spreads in all directions (star-shaped waves)
//   - knight: spreads in L-shaped jumps (scattered, non-contiguous waves)
//   - moore: spreads uniformly in all directions (circular waves)

struct PropagationChessVariantState {
    double activity;        // 0.0 to 1.0 continuous value
    int phase;              // 0=neutral, 1=active, 2=exhausted
    int stepsInPhase;       // steps spent in current phase

    // propagation parameters
    int activeDuration;     // steps to stay active before exhaustion
    double decayRate;       // activity decrease per step during exhausted phase
    double spreadThreshold; // min fraction of active neighbors to trigger activation

    PropagationChessVariantState()
        : activity(0.0), phase(0), stepsInPhase(0),
          activeDuration(4), decayRate(0.2), spreadThreshold(0.05) {}
};

// state changes when phase, steps, or activity changes
inline bool operator!=(const PropagationChessVariantState& a,
                        const PropagationChessVariantState& b) {
    return a.phase != b.phase ||
           a.stepsInPhase != b.stepsInPhase ||
           std::abs(a.activity - b.activity) > 0.001;
}

// output activity for viewer (single value, same approach as lifecycle)
inline std::ostream& operator<<(std::ostream& os,
                                 const PropagationChessVariantState& s) {
    os << "<" << s.activity << ">";
    return os;
}

inline void from_json(const nlohmann::json& j, PropagationChessVariantState& s) {
    if (j.contains("activity"))        j.at("activity").get_to(s.activity);
    if (j.contains("phase"))           j.at("phase").get_to(s.phase);
    if (j.contains("stepsInPhase"))    j.at("stepsInPhase").get_to(s.stepsInPhase);
    if (j.contains("activeDuration"))  j.at("activeDuration").get_to(s.activeDuration);
    if (j.contains("decayRate"))       j.at("decayRate").get_to(s.decayRate);
    if (j.contains("spreadThreshold")) j.at("spreadThreshold").get_to(s.spreadThreshold);
}

#endif // PROPAGATION_CHESS_VARIANT_STATE_HPP
