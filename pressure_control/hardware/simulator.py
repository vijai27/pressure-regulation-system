# hardware/simulator.py — Simulated pressure vessel for Windows testing
#
# Physics model (each SAMPLE_TIME_S step):
#
#   Booster: modelled as fixed effective supply pressure >> 28 MPa
#     (HII 5G-TD-28/150-CO2: max out 25,000 PSIG = 172 MPa; at typical 100 PSI
#      shop air the booster can easily maintain 50+ MPa to the needle valve)
#
#   Pressure dynamics:
#     delta_P   = max(P_booster_effective − P_vessel, 0)
#     dP_flow   = K_flow × valve_pct × sqrt(delta_P)     ← gas flowing in
#     dP_vent   = −K_vent × solenoid_duty × P_vessel      ← gas venting out
#     dP_temp   = PR-EOS (∂P/∂T)_V × dT                  ← real CO₂ (replaces ideal gas)
#     dP        = dP_flow + dP_vent + dP_temp + noise
#
#   Temperature dynamics:
#     dT_compress = K_compress × max(dP_flow, 0) / P_booster   ← adiabatic heating
#     dT_jt       = K_jt × min(dP_vent, 0)                     ← JT cooling
#     dT_inkbird  = −K_inkbird × (T − T_set) × dt              ← INKBIRD correction
#     noise       = Gaussian(0, σ)  where σ scales with distance from setpoint:
#                   σ = 0.30°C when hunting (far from 60°C) → 0.01°C when settled
#                   (matches observed ±0.01°C stable behaviour in lab)
#     dT          = dT_compress + dT_jt + dT_inkbird + noise
#
# Thread safety: all state mutated only inside the physics loop.
#   read_*() methods are read-only → safe to call from GUI.

import math
import random
import threading
import time

from hardware.base import HardwareBase
from control import eos
from config import (
    SAMPLE_TIME_S,
    SIM_P_BOOSTER_EFFECTIVE,
    SIM_K_FLOW, SIM_K_VENT,
    SIM_K_COMPRESS, SIM_K_JT, SIM_K_INKBIRD,
    SIM_NOISE_P_MPA,
    SIM_T_NOISE_FAR_C, SIM_T_NOISE_SETTLED_C, SIM_T_SETTLE_BAND_C,
    SIM_INITIAL_PRESSURE_MPA, SIM_INITIAL_TEMP_C, SIM_HEAT_RATE_C_S,
    INKBIRD_SETPOINT_C,
    AMBIENT_PRESSURE,
)


class SimulatedHardware(HardwareBase):
    """Simulated pressure vessel — runs physics in a background thread at 10 Hz."""

    def __init__(self):
        self._pressure   = SIM_INITIAL_PRESSURE_MPA
        self._temperature = SIM_INITIAL_TEMP_C

        self._valve_pct  = 0.0   # 0–100 %
        self._solenoid   = 0.0   # 0–100 % PWM duty

        self._estop = False
        self._lock  = threading.Lock()

        # Start the physics simulation thread
        self._running = True
        self._thread  = threading.Thread(target=self._physics_loop, daemon=True)
        self._thread.start()

    # ── HardwareBase interface ────────────────────────────────────────────────

    def read_pressure(self) -> float:
        with self._lock:
            return self._pressure

    def read_temperature(self) -> float:
        with self._lock:
            return self._temperature

    def set_valve_position(self, pct: float) -> None:
        with self._lock:
            self._valve_pct = max(0.0, min(100.0, pct))

    def set_solenoid_pwm(self, duty: float) -> None:
        with self._lock:
            self._solenoid = max(0.0, min(100.0, duty))

    def read_estop(self) -> bool:
        return self._estop

    def get_valve_position(self) -> float:
        with self._lock:
            return self._valve_pct

    def get_solenoid_pwm(self) -> float:
        with self._lock:
            return self._solenoid

    def emergency_stop(self) -> None:
        with self._lock:
            self._valve_pct = 0.0
            self._solenoid  = 0.0

    def close(self) -> None:
        self._running = False
        self._thread.join(timeout=2.0)

    # ── Simulation physics (runs in background thread) ────────────────────────

    def _physics_loop(self) -> None:
        dt = SAMPLE_TIME_S
        while self._running:
            start = time.monotonic()

            with self._lock:
                P = self._pressure
                T = self._temperature
                v = self._valve_pct / 100.0   # 0–1
                s = self._solenoid  / 100.0   # 0–1
                T_K = T + 273.15

            # Booster: HII 5G-TD-28/150-CO2 — max out 172 MPa, effectively constant
            # supply pressure to needle valve over our entire 0–28 MPa range.
            P_booster = SIM_P_BOOSTER_EFFECTIVE

            # ── Pressure step ────────────────────────────────────────────────
            delta_P = max(P_booster - P, 0.0)
            dP_flow = SIM_K_FLOW * v * math.sqrt(delta_P) if delta_P > 0 else 0.0
            dP_vent = -SIM_K_VENT * s * max(P - AMBIENT_PRESSURE, 0.0)

            # ── Temperature step ─────────────────────────────────────────────
            dT_compress = SIM_K_COMPRESS * max(dP_flow, 0.0) / P_booster
            dT_jt       = SIM_K_JT * min(dP_vent, 0.0)
            dT_inkbird  = -SIM_K_INKBIRD * (T - INKBIRD_SETPOINT_C) * dt

            # Cold-start: allow faster heating when vessel is well below setpoint
            if T < INKBIRD_SETPOINT_C - 1.0 and v < 0.01 and s < 0.01:
                dT_inkbird = max(dT_inkbird, SIM_HEAT_RATE_C_S * dt)

            # INKBIRD hunting noise: ±0.3°C when far from setpoint, ±0.01°C
            # when settled — matches observed ±0.01°C stable behaviour in lab.
            error_T = abs(T - INKBIRD_SETPOINT_C)
            settled = 1.0 / (1.0 + (error_T / SIM_T_SETTLE_BAND_C) ** 2)
            noise_std_T = SIM_T_NOISE_FAR_C * (1.0 - settled) + SIM_T_NOISE_SETTLED_C * settled
            noise_T = random.gauss(0, noise_std_T)

            dT    = dT_compress + dT_jt + dT_inkbird + noise_T
            T_new = T + dT

            # ── Pressure change from temperature shift ────────────────────────
            # PR-EOS (∂P/∂T)_V — replaces ideal-gas P/T approximation.
            # At 20 MPa / 60°C, CO₂ is ~20–30% stiffer than ideal gas predicts.
            dP_temp = eos.dP_from_dT(P, T_K, dT)

            # ── Total pressure change ─────────────────────────────────────────
            noise_P = random.gauss(0, SIM_NOISE_P_MPA)
            dP = dP_flow + dP_vent + dP_temp + noise_P

            P_new = max(AMBIENT_PRESSURE - 0.01, P + dP)

            with self._lock:
                self._pressure    = P_new
                self._temperature = T_new

            # Sleep for remainder of step
            elapsed = time.monotonic() - start
            sleep_time = dt - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
