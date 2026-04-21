#ifndef LIFECYCLE_CHESS_VARIANT_STATE_HPP
#define LIFECYCLE_CHESS_VARIANT_STATE_HPP

#include <iostream>
#include <nlohmann/json.hpp>

// lifecycle chess variant cell state
//
// extends the adaptive model with continuous activity and multi-phase behavior.
// instead of binary alive/dead transitions, cells progress through four phases:
//
//   dormant (activity = 0):
//       cell is inactive. transitions to activating when enough neighbors
//       have sufficient activity (density within birth threshold range).
//
//   activating (0 < activity < 1):
//       cell is gradually turning on. activity increases by activationRate
//       each step. transitions to active when activity reaches 1.0.
//
//   active (activity = 1):
//       cell is fully alive and contributes maximum influence to neighbors.
//       remains active for activeDuration steps, then transitions to decaying.
//       can also begin decaying early if neighbor support drops below
//       the survival threshold range.
//
//   decaying (activity dropping from 1 toward 0):
//       cell is winding down. activity decreases by decayRate each step.
//       transitions to dormant when activity reaches 0. can be reactivated
//       in a future cycle if neighbor conditions are met again.
//
// phase encoding: 0 = dormant, 1 = activating, 2 = active, 3 = decaying

struct LifecycleChessVariantState {
    double activity;        // continuous value 0.0 to 1.0
    int phase;              // 0=dormant, 1=activating, 2=active, 3=decaying
    int stepsInPhase;       // how many steps spent in current phase

    // lifecycle parameters
    double activationRate;  // activity increase per step during activating phase
    double decayRate;       // activity decrease per step during decaying phase
    int activeDuration;     // steps to remain in active phase before decaying

    // density thresholds (same as adaptive model)
    double birthLow;
    double birthHigh;
    double survivalLow;
    double survivalHigh;

    LifecycleChessVariantState()
        : activity(0.0), phase(0), stepsInPhase(0),
          activationRate(0.2), decayRate(0.15), activeDuration(8),
          birthLow(0.25), birthHigh(0.375),
          survivalLow(0.25), survivalHigh(0.375) {}
};

// state has changed if activity shifted, phase changed, or steps advanced.
// the stepsInPhase check is critical: without it, cells in the active phase
// (where activity=1.0 and phase=2 are constant) go passive and never
// advance to the decaying phase, freezing the entire simulation.
inline bool operator!=(const LifecycleChessVariantState& a,
                        const LifecycleChessVariantState& b) {
    return a.phase != b.phase ||
           a.stepsInPhase != b.stepsInPhase ||
           std::abs(a.activity - b.activity) > 0.001;
}

// output: activity value only, matching the viewer field.
// the viewer parses this positionally against the state fields in the config,
// so we output only the first field (activity) to keep it simple and compatible.
inline std::ostream& operator<<(std::ostream& os,
                                 const LifecycleChessVariantState& s) {
    os << "<" << s.activity << ">";
    return os;
}

inline void from_json(const nlohmann::json& j, LifecycleChessVariantState& s) {
    if (j.contains("activity"))       j.at("activity").get_to(s.activity);
    if (j.contains("phase"))          j.at("phase").get_to(s.phase);
    if (j.contains("stepsInPhase"))   j.at("stepsInPhase").get_to(s.stepsInPhase);
    if (j.contains("activationRate")) j.at("activationRate").get_to(s.activationRate);
    if (j.contains("decayRate"))      j.at("decayRate").get_to(s.decayRate);
    if (j.contains("activeDuration")) j.at("activeDuration").get_to(s.activeDuration);
    if (j.contains("birthLow"))       j.at("birthLow").get_to(s.birthLow);
    if (j.contains("birthHigh"))      j.at("birthHigh").get_to(s.birthHigh);
    if (j.contains("survivalLow"))    j.at("survivalLow").get_to(s.survivalLow);
    if (j.contains("survivalHigh"))   j.at("survivalHigh").get_to(s.survivalHigh);
}

#endif // LIFECYCLE_CHESS_VARIANT_STATE_HPP
