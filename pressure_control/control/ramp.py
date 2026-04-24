# control/ramp.py — Linear ramp setpoint generator
#
# Generates a time-varying setpoint that ramps from a start value toward
# a target at a constant rate.  Used for both pressurization and
# depressurization phases.

import time


class LinearRamp:
    """Produces a linearly-changing setpoint that clamps at the target.

    Usage:
        ramp = LinearRamp(start=0.1, target=28.0, rate_per_min=0.35)
        ramp.start()
        ...
        sp = ramp.setpoint()   # call at 10 Hz in the control loop
    """

    def __init__(self, start: float, target: float, rate_per_min: float):
        """
        Args:
            start:         Initial value (MPa or other unit)
            target:        Final clamped value (MPa)
            rate_per_min:  Magnitude of change per minute (always positive)
        """
        self._start = start
        self._target = target
        self._rate_per_s = rate_per_min / 60.0  # convert to per-second
        self._t0: float | None = None
        self._ascending = target >= start

    def start(self) -> None:
        """Record the start time. Call once when entering PRESSURIZE/DEPRESSURIZE."""
        self._t0 = time.monotonic()

    def setpoint(self) -> float:
        """Return the current ramp setpoint.  Clamps when target is reached."""
        if self._t0 is None:
            return self._start
        elapsed = time.monotonic() - self._t0
        delta = self._rate_per_s * elapsed
        if self._ascending:
            return min(self._start + delta, self._target)
        else:
            return max(self._start - delta, self._target)

    def is_complete(self, measurement: float, tolerance: float = 0.2) -> bool:
        """Return True when measurement is within tolerance of target."""
        return abs(measurement - self._target) <= tolerance

    @property
    def target(self) -> float:
        return self._target

    @property
    def start_value(self) -> float:
        return self._start
