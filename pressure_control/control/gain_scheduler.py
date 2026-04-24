# control/gain_scheduler.py — Pressure-adaptive PID gain scheduler
#
# Why gain scheduling?
#   High-pressure vessel pressurisation is highly non-linear:
#
#   1. Shrinking booster differential
#      ΔP = P_boost − P_vessel decreases as the vessel fills.
#      Same valve opening → LESS flow at high pressure.
#      Kp must INCREASE to compensate.
#
#   2. Critical-point sensitivity (varies by gas — 7.4 MPa/31°C for CO2)
#      Compressibility and density change sharply here.
#      Smaller Kd avoids exciting this region.
#
#   3. HOLD vs PRESSURIZE objectives differ
#      PRESSURIZE: track a moving ramp → balanced P/I/D
#      HOLD:       reject slow drift   → strong I, gentle P, almost no D
#
#   4. Gas identity effect
#      CO2 near its critical point (7.4 MPa, 31°C) has very high compressibility
#      and density → heavy, sluggish → needs full Kp (gas_factor=1.00).
#      N2 and Ar are well above their critical points at 60°C → behave more
#      like ideal compressible gases → lower density → vessel pressure rises
#      faster per kg of gas added → Kp should be reduced slightly.
#      TiO2 nanoparticles (1 wt%) do not significantly alter gas-phase dynamics.
#
#      Experiment gas_factor table (tune after first real run if needed):
#        Exp 1  CO2        → 1.00   (reference)
#        Exp 2  CO2+TiO2   → 1.00   (TiO2 doesn't change gas dynamics)
#        Exp 3  N2         → 0.80   (lower density, faster response)
#        Exp 4  N2+TiO2    → 0.80
#        Exp 5  Ar         → 0.85   (intermediate density)
#        Exp 6  Ar+TiO2    → 0.85
#
#      Pass gas_factor when creating GainScheduler:
#        GainScheduler(gas_factor=0.80)   # for N2 experiments
#
# Default gain table (tuned for 1 L vessel, booster ~37 MPa, 350 kPa/min ramp):
#
# TWO-REGIME BEHAVIOUR (observed in lab):
#   0 – 2500 psi (0 – 17.2 MPa):  HARDER to pressurize.
#       Gas is highly compressible; dP/dm is small.  Valve must be opened wide
#       to maintain the ramp.  Gains must INCREASE toward the crossover point.
#
#   2500 – 4000 psi (17.2 – 27.6 MPa):  FASTER response, easier to overshoot.
#       Gas/fluid density rises sharply (CO₂ goes supercritical ~7.4 MPa/31°C
#       but packs tighter above 17 MPa; N₂/Ar similarly denser).
#       dP/dm is large → small valve change → big pressure jump.
#       Gains must DECREASE quickly to prevent overshoot.
#
#   Pressure (MPa) | Kp   | Ki   | Kd   | Notes
#   ───────────────┼──────┼──────┼──────┼──────────────────────────────────────
#      0.0         |  50  |  6.0 | 2.5  | high compressibility, needs lots of flow
#      5.0         |  58  |  7.0 | 2.5  | building up
#     10.0         |  65  |  8.0 | 2.0  | peak effort — hardest region
#     17.2         |  60  |  7.0 | 1.5  | ← 2500 psi crossover, system gets faster
#     20.0         |  45  |  5.0 | 1.0  | dense fluid: hair-trigger response
#     24.0         |  32  |  4.0 | 0.8  | approaching target
#     27.0         |  22  |  3.0 | 0.5  | near target: avoid overshoot
#     28.0         |  18  |  3.0 | 0.5  | at target ceiling
#    HOLD (any P)  |  35  | 12.0 | 0.5  | tight integral, gentle P

import bisect
from typing import NamedTuple


class GainPoint(NamedTuple):
    """Single entry in the gain schedule."""
    pressure: float   # MPa
    kp:       float
    ki:       float
    kd:       float


# ── Default schedule — edit these to match your hardware after lab testing ────
# Shape: gains RISE from 0→17.2 MPa (high compressibility, needs more flow)
#        then FALL from 17.2→28 MPa (dense fluid, faster/hair-trigger response)
# 17.2 MPa = 2500 psi crossover observed in lab.
DEFAULT_SCHEDULE: list[GainPoint] = [
    GainPoint(  0.0,  50.0,  6.0,  2.5),   # low P: lots of valve needed
    GainPoint(  5.0,  58.0,  7.0,  2.5),
    GainPoint( 10.0,  65.0,  8.0,  2.0),   # peak effort
    GainPoint( 17.2,  60.0,  7.0,  1.5),   # ← 2500 psi crossover
    GainPoint( 20.0,  45.0,  5.0,  1.0),   # dense fluid: reduce gains
    GainPoint( 24.0,  32.0,  4.0,  0.8),
    GainPoint( 27.0,  22.0,  3.0,  0.5),   # near target
    GainPoint( 28.0,  18.0,  3.0,  0.5),   # at ceiling
]

# Hold-phase override: strong integral eliminates slow drift; low D avoids noise
HOLD_GAINS: tuple[float, float, float] = (35.0, 12.0, 0.5)

# Depressurise schedule (inverted: high pressure → need more valve authority)
DEPRESS_SCHEDULE: list[GainPoint] = [
    GainPoint(  0.0,  40.0,  5.0,  1.0),
    GainPoint( 10.0,  50.0,  6.0,  1.0),
    GainPoint( 20.0,  60.0,  8.0,  0.5),
    GainPoint( 28.0,  70.0, 10.0,  0.5),
]


class GainScheduler:
    """
    Returns (Kp, Ki, Kd) as a function of current pressure and control phase.

    Usage (inside StateMachine.tick):
        kp, ki, kd = self._gain_scheduler.get_gains(pressure, in_hold=False)
        self._pid.set_gains(kp, ki, kd)

    Args:
        schedule:     Override the default PRESSURIZE schedule.
        gas_factor:   Multiplier on Kp for the working gas.
                      1.00 = CO2 or CO2+TiO2 (reference)
                      0.80 = N2 or N2+TiO2  (lower density, faster response)
                      0.85 = Ar or Ar+TiO2  (intermediate density)
    """

    def __init__(
        self,
        schedule: list[GainPoint] | None = None,
        gas_factor: float = 1.0,
    ):
        self._schedule    = schedule or DEFAULT_SCHEDULE
        self._gas_factor  = gas_factor
        self._P  = [g.pressure for g in self._schedule]
        self._Kp = [g.kp       for g in self._schedule]
        self._Ki = [g.ki       for g in self._schedule]
        self._Kd = [g.kd       for g in self._schedule]

    # ── Public API ────────────────────────────────────────────────────────────

    def get_gains(
        self,
        pressure_mpa: float,
        in_hold: bool = False,
    ) -> tuple[float, float, float]:
        """
        Return (Kp, Ki, Kd) for the given pressure and phase.

        Args:
            pressure_mpa:  current vessel pressure [MPa]
            in_hold:       True when state machine is in HOLD state

        Returns:
            (Kp, Ki, Kd) tuple
        """
        if in_hold:
            return HOLD_GAINS

        P  = max(self._P[0], min(pressure_mpa, self._P[-1]))
        kp = self._interp(P, self._Kp) * self._gas_factor
        ki = self._interp(P, self._Ki)
        kd = self._interp(P, self._Kd)
        return kp, ki, kd

    def summary(self, pressure_mpa: float) -> str:
        """Return a human-readable string of active gains (for logging/GUI)."""
        kp, ki, kd = self.get_gains(pressure_mpa)
        return f"Kp={kp:.1f}  Ki={ki:.1f}  Kd={kd:.1f}  @ {pressure_mpa:.2f} MPa"

    # ── Internal ──────────────────────────────────────────────────────────────

    def _interp(self, P: float, values: list[float]) -> float:
        """Linear interpolation of values at breakpoints self._P."""
        idx = max(0, min(bisect.bisect_right(self._P, P) - 1, len(self._P) - 2))
        P0, P1 = self._P[idx], self._P[idx + 1]
        V0, V1 = values[idx], values[idx + 1]
        alpha = (P - P0) / (P1 - P0) if P1 != P0 else 0.0
        return V0 + alpha * (V1 - V0)
