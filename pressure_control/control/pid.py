# control/pid.py — Discrete PID controller
#
# Design choices:
#   - Derivative on measurement (not error) to avoid derivative kick on setpoint jumps
#   - Anti-windup: integral term clamped to output limits when output is saturated
#   - Each PRESSURIZE / DEPRESSURIZE / HOLD phase uses a fresh PID instance
#     so integral history does not carry across transitions

import time


class PIDController:
    """Discrete PID controller with anti-windup and derivative-on-measurement."""

    def __init__(
        self,
        kp: float,
        ki: float,
        kd: float,
        output_min: float = 0.0,
        output_max: float = 100.0,
        sample_time: float = 0.1,
    ):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.output_min = output_min
        self.output_max = output_max
        self.sample_time = sample_time

        self._integral = 0.0
        self._prev_measurement = None
        self._last_output = 0.0

    def reset(self) -> None:
        """Clear integrator and derivative history. Call when entering a new state."""
        self._integral = 0.0
        self._prev_measurement = None
        self._last_output = 0.0

    def compute(self, setpoint: float, measurement: float) -> float:
        """Compute PID output.

        Args:
            setpoint:    Desired value (MPa, etc.)
            measurement: Actual measured value (same units as setpoint)

        Returns:
            Control output clamped to [output_min, output_max].
        """
        error = setpoint - measurement

        # Proportional term
        p_term = self.kp * error

        # Integral term with anti-windup (only integrate when not fully saturated)
        if self.output_min < self._last_output < self.output_max:
            self._integral += error * self.sample_time
        i_term = self.ki * self._integral

        # Derivative on measurement (avoids kick when setpoint changes)
        if self._prev_measurement is None:
            d_term = 0.0
        else:
            d_measurement = (measurement - self._prev_measurement) / self.sample_time
            d_term = -self.kd * d_measurement  # negative: rising meas → negative D

        self._prev_measurement = measurement

        raw = p_term + i_term + d_term
        output = max(self.output_min, min(self.output_max, raw))
        self._last_output = output
        return output

    def set_gains(self, kp: float, ki: float, kd: float) -> None:
        """Update PID gains at runtime.

        Called by GainScheduler every tick so gains adapt to current pressure.
        The integral state is preserved across gain changes — no bump on switch.
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd

    @property
    def gains(self) -> tuple[float, float, float]:
        """Return current (Kp, Ki, Kd)."""
        return self.kp, self.ki, self.kd

    @property
    def integral(self) -> float:
        return self._integral

    @integral.setter
    def integral(self, value: float) -> None:
        self._integral = value
