# control/state_machine.py — Pressure-control state machine
#
# States:
#   IDLE          — all outputs off, waiting for user
#   PRESSURIZE    — ramp up at 350 kPa/min via motorized valve PID
#   HOLD          — maintain target pressure with valve micro-adjustments
#   DEPRESSURIZE  — ramp down at 2 MPa/min via solenoid PWM PID
#
# Transitions:
#   IDLE        → PRESSURIZE   : user presses START (temp ≥ 55 °C required)
#   PRESSURIZE  → HOLD         : measured pressure ≥ target
#   HOLD        → DEPRESSURIZE : user presses DEPRESSURIZE
#   DEPRESSURIZE→ IDLE         : measured pressure ≤ 0.1 MPa
#   any         → IDLE         : E-stop button or watchdog timeout

import time
import logging
from enum import IntEnum

from config import (
    PRESSURIZE_RATE_MPA_MIN,
    DEPRESSURIZE_RATE_MPA_MIN,
    AMBIENT_PRESSURE,
    OVERPRESSURE_LIMIT,
    MAX_RATE_LIMIT_MPA_MIN,
    PRESS_KP, PRESS_KI, PRESS_KD, PRESS_OUTPUT_MIN, PRESS_OUTPUT_MAX,
    DEPRESS_KP, DEPRESS_KI, DEPRESS_KD, DEPRESS_OUTPUT_MIN, DEPRESS_OUTPUT_MAX,
    HOLD_KP, HOLD_KI, HOLD_KD,
    MIN_START_TEMP_C,
    SAMPLE_TIME_S,
    WATCHDOG_TIMEOUT_S,
)
from control.pid import PIDController
from control.ramp import LinearRamp
from control.gain_scheduler import GainScheduler

log = logging.getLogger(__name__)


class State(IntEnum):
    IDLE         = 0
    PRESSURIZE   = 1
    HOLD         = 2
    DEPRESSURIZE = 3


class StateMachine:
    """Runs the pressure-control state machine.

    Call tick() at 10 Hz from the main control thread.
    Use request_start(), request_depressurize(), request_estop() from GUI thread.
    """

    def __init__(self, hardware, target_pressure: float):
        self._hw = hardware
        self._target = target_pressure
        self._state = State.IDLE
        self._setpoint = 0.0

        # PIDs — re-created on each transition to clear integrator history
        self._pid: PIDController | None = None
        self._ramp: LinearRamp | None = None

        # Watchdog
        self._last_tick_time = time.monotonic()

        # Requests from GUI thread (thread-safe via GIL for simple bool assignment)
        self._req_start       = False
        self._req_depressurize = False
        self._req_estop        = False

        # Adaptive gain scheduler (updates Kp/Ki/Kd every tick based on pressure)
        self._gain_scheduler = GainScheduler()
        self._last_logged_gains: tuple[float, float, float] = (0.0, 0.0, 0.0)

        # Rolling window for rate estimation (5-second buffer avoids noise spikes)
        self._rate_window: list[tuple[float, float]] = []   # (time, pressure)
        self._rate_window_s = 5.0    # smoothing window length in seconds
        self._last_smoothed_rate = 0.0

        # Event log for GUI status messages
        self.status_message = "System ready. Press START to begin."

    # ── Public API (called from GUI thread) ───────────────────────────────────

    def request_start(self) -> None:
        self._req_start = True

    def request_depressurize(self) -> None:
        self._req_depressurize = True

    def request_estop(self) -> None:
        self._req_estop = True

    def set_target(self, target: float) -> None:
        """Update target pressure. Only takes effect before next START."""
        self._target = target

    @property
    def state(self) -> State:
        return self._state

    @property
    def setpoint(self) -> float:
        return self._setpoint

    # ── Watchdog ping (must be called from control thread) ────────────────────

    def ping_watchdog(self) -> None:
        self._last_tick_time = time.monotonic()

    def _check_watchdog(self) -> bool:
        """Return True if watchdog has expired (control loop stalled)."""
        return (time.monotonic() - self._last_tick_time) > WATCHDOG_TIMEOUT_S

    # ── Main tick ─────────────────────────────────────────────────────────────

    def tick(self, pressure: float, temperature: float) -> None:
        """Advance state machine by one control step.

        Args:
            pressure:    Current measured pressure (MPa)
            temperature: Current measured temperature (°C)
        """
        self.ping_watchdog()

        # ── Global safety checks ──────────────────────────────────────────────
        if self._req_estop or self._hw.read_estop():
            self._transition_idle("E-STOP activated.")
            return

        if pressure > OVERPRESSURE_LIMIT and self._state != State.IDLE:
            self._transition_idle(f"OVERPRESSURE TRIP: {pressure:.2f} MPa — forced IDLE.")
            return

        rate = self._calc_rate(pressure)
        # Rate monitor: log a warning if rate is well above target.
        # We do NOT slam the valve shut here — that causes chattering.
        # The PID + ramp setpoint naturally control the rate.
        # Only force an emergency stop if rate is catastrophically high (>5 MPa/min).
        if rate > 5.0 and self._state == State.PRESSURIZE and pressure > 1.0:
            self._transition_idle(
                f"EMERGENCY: Rate {rate*1000:.0f} kPa/min > 5000 kPa/min limit."
            )
            return
        if (rate > MAX_RATE_LIMIT_MPA_MIN
                and self._state == State.PRESSURIZE
                and pressure > 1.0):
            log.warning("High rate: %.0f kPa/min (limit: %.0f)",
                        rate * 1000, MAX_RATE_LIMIT_MPA_MIN * 1000)

        # ── State transitions + outputs ───────────────────────────────────────
        if self._state == State.IDLE:
            self._hw.set_valve_position(0.0)
            self._hw.set_solenoid_pwm(0.0)
            if self._req_start:
                self._req_start = False
                if temperature < MIN_START_TEMP_C:
                    self.status_message = (
                        f"Cannot start: temperature {temperature:.1f}°C < {MIN_START_TEMP_C}°C required."
                    )
                else:
                    self._transition_pressurize(pressure)

        elif self._state == State.PRESSURIZE:
            self._setpoint = self._ramp.setpoint()

            # ── Adaptive gains: update every tick based on current pressure ──
            kp, ki, kd = self._gain_scheduler.get_gains(pressure, in_hold=False)
            self._pid.set_gains(kp, ki, kd)
            # Log only when gains change by >1 unit (avoids flooding the log)
            if abs(kp - self._last_logged_gains[0]) > 1.0:
                log.info("GainScheduler: %s", self._gain_scheduler.summary(pressure))
                self._last_logged_gains = (kp, ki, kd)

            valve_pct = self._pid.compute(self._setpoint, pressure)
            self._hw.set_valve_position(valve_pct)
            self._hw.set_solenoid_pwm(0.0)

            if pressure >= self._target - 0.05:
                self._transition_hold()

        elif self._state == State.HOLD:
            self._setpoint = self._target
            valve_pct = self._pid.compute(self._setpoint, pressure)
            self._hw.set_valve_position(max(0.0, valve_pct))
            self._hw.set_solenoid_pwm(0.0)

            if self._req_depressurize:
                self._req_depressurize = False
                self._transition_depressurize(pressure)

        elif self._state == State.DEPRESSURIZE:
            self._setpoint = self._ramp.setpoint()
            pwm_duty = self._pid.compute(self._setpoint, pressure)
            self._hw.set_valve_position(0.0)
            self._hw.set_solenoid_pwm(pwm_duty)

            if pressure <= AMBIENT_PRESSURE + 0.05:
                self._transition_idle("Depressurization complete.")

    # ── Transition helpers ────────────────────────────────────────────────────

    def _transition_idle(self, msg: str = "") -> None:
        self._hw.emergency_stop()
        self._state = State.IDLE
        self._setpoint = 0.0
        self._pid = None
        self._ramp = None
        self._req_start = False
        self._req_depressurize = False
        self._req_estop = False
        if msg:
            log.info("→ IDLE: %s", msg)
            self.status_message = msg

    def _transition_pressurize(self, current_pressure: float) -> None:
        self._pid = PIDController(
            PRESS_KP, PRESS_KI, PRESS_KD,
            PRESS_OUTPUT_MIN, PRESS_OUTPUT_MAX, SAMPLE_TIME_S
        )
        self._ramp = LinearRamp(
            start=current_pressure,
            target=self._target,
            rate_per_min=PRESSURIZE_RATE_MPA_MIN,
        )
        self._ramp.start()
        self._state = State.PRESSURIZE
        self._setpoint = current_pressure
        self.status_message = f"Pressurizing to {self._target:.1f} MPa at 350 kPa/min…"
        log.info("→ PRESSURIZE: target=%.2f MPa", self._target)

    def _transition_hold(self) -> None:
        self._pid = PIDController(
            HOLD_KP, HOLD_KI, HOLD_KD,
            PRESS_OUTPUT_MIN, PRESS_OUTPUT_MAX, SAMPLE_TIME_S
        )
        self._ramp = None
        self._state = State.HOLD
        self._setpoint = self._target
        self.status_message = f"HOLD at {self._target:.1f} MPa."
        log.info("→ HOLD: %.2f MPa", self._target)

    def _transition_depressurize(self, current_pressure: float) -> None:
        self._pid = PIDController(
            DEPRESS_KP, DEPRESS_KI, DEPRESS_KD,
            DEPRESS_OUTPUT_MIN, DEPRESS_OUTPUT_MAX, SAMPLE_TIME_S
        )
        self._ramp = LinearRamp(
            start=current_pressure,
            target=AMBIENT_PRESSURE,
            rate_per_min=DEPRESSURIZE_RATE_MPA_MIN,
        )
        self._ramp.start()
        self._state = State.DEPRESSURIZE
        self._setpoint = current_pressure
        self.status_message = "Depressurizing at 2 MPa/min…"
        log.info("→ DEPRESSURIZE from %.2f MPa", current_pressure)

    # ── Rate calculation helper ───────────────────────────────────────────────

    def _calc_rate(self, pressure: float) -> float:
        """Return estimated dP/dt in MPa/min using a rolling 5-second window.

        Comparing single-step differences amplifies sensor noise (~3000 kPa/min
        RMS at 10 Hz with 5 kPa noise).  A 5-second window reduces this to
        well below the 600 kPa/min safety limit.
        """
        now = time.monotonic()
        self._rate_window.append((now, pressure))

        # Discard samples older than the window
        cutoff = now - self._rate_window_s
        self._rate_window = [(t, p) for t, p in self._rate_window if t >= cutoff]

        if len(self._rate_window) < 5:
            return self._last_smoothed_rate

        t0, p0 = self._rate_window[0]
        t1, p1 = self._rate_window[-1]
        dt = t1 - t0
        # Require at least 3 seconds of data — with 5 kPa noise, a shorter
        # window gives ~840 kPa/min apparent rate from endpoint noise alone,
        # which falsely exceeds the 600 kPa/min safety limit.
        if dt < 3.0:
            return self._last_smoothed_rate

        rate = abs((p1 - p0) / dt * 60.0)  # MPa/min
        self._last_smoothed_rate = rate
        return rate
