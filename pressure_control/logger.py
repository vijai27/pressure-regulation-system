# logger.py — CSV data logger
#
# Writes one row every control loop tick (100 ms) to:
#   logs/experiment_YYYYMMDD_HHMMSS.csv
#
# Columns:
#   timestamp        — wall-clock ISO-8601 string
#   elapsed_s        — seconds since experiment started
#   pressure_MPa     — measured pressure
#   temperature_C    — measured temperature
#   setpoint_MPa     — PID setpoint at this tick
#   state            — IDLE / PRESSURIZE / HOLD / DEPRESSURIZE
#   valve_pct        — motorized valve position (0–100 %)
#   solenoid_pwm_pct — vent solenoid duty cycle (0–100 %)

import csv
import os
import time
from datetime import datetime


class DataLogger:
    """Opens a new CSV file per experiment session and appends rows."""

    COLUMNS = [
        "timestamp",
        "elapsed_s",
        "pressure_MPa",
        "temperature_C",
        "setpoint_MPa",
        "state",
        "valve_pct",
        "solenoid_pwm_pct",
    ]

    def __init__(self, log_dir: str = "logs"):
        os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._path = os.path.join(log_dir, f"experiment_{timestamp}.csv")
        self._file = open(self._path, "w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=self.COLUMNS)
        self._writer.writeheader()
        self._file.flush()
        self._start_time = time.monotonic()
        print(f"[Logger] Logging to: {self._path}")

    def log(
        self,
        pressure: float,
        temperature: float,
        setpoint: float,
        state: str,
        valve_pct: float,
        solenoid_pct: float,
    ) -> None:
        """Write one row. Called from the control thread at 10 Hz."""
        elapsed = time.monotonic() - self._start_time
        row = {
            "timestamp":        datetime.now().isoformat(timespec="milliseconds"),
            "elapsed_s":        f"{elapsed:.2f}",
            "pressure_MPa":     f"{pressure:.4f}",
            "temperature_C":    f"{temperature:.3f}",
            "setpoint_MPa":     f"{setpoint:.4f}",
            "state":            state,
            "valve_pct":        f"{valve_pct:.1f}",
            "solenoid_pwm_pct": f"{solenoid_pct:.1f}",
        }
        self._writer.writerow(row)
        # Flush every row so data is not lost if app crashes
        self._file.flush()

    def close(self) -> None:
        self._file.close()
        print(f"[Logger] Log closed: {self._path}")

    @property
    def path(self) -> str:
        return self._path
