# hardware/base.py — Abstract Hardware Abstraction Layer (HAL)
# All hardware implementations (simulated or real) must implement this interface.

from abc import ABC, abstractmethod


class HardwareBase(ABC):
    """Abstract interface for pressure-control hardware.

    Two concrete implementations exist:
    - SimulatedHardware  (hardware/simulator.py)  — runs on Windows for testing
    - RPiHardware        (hardware/rpi_hardware.py) — real Raspberry Pi hardware

    To switch between them, change one line in main.py.
    """

    @abstractmethod
    def read_pressure(self) -> float:
        """Return current vessel pressure in MPa."""

    @abstractmethod
    def read_temperature(self) -> float:
        """Return current vessel temperature in °C."""

    @abstractmethod
    def set_valve_position(self, pct: float) -> None:
        """Set motorized needle valve opening.

        Args:
            pct: 0.0 = fully closed, 100.0 = fully open
        """

    @abstractmethod
    def set_solenoid_pwm(self, duty: float) -> None:
        """Set vent solenoid PWM duty cycle.

        Args:
            duty: 0.0 = always closed, 100.0 = always open
        """

    @abstractmethod
    def read_estop(self) -> bool:
        """Return True if the emergency-stop button is pressed."""

    @abstractmethod
    def get_valve_position(self) -> float:
        """Return current valve position (0–100 %)."""

    @abstractmethod
    def get_solenoid_pwm(self) -> float:
        """Return current solenoid PWM duty cycle (0–100 %)."""

    @abstractmethod
    def emergency_stop(self) -> None:
        """Immediately close valve and solenoid. Called on E-stop or watchdog."""

    @abstractmethod
    def close(self) -> None:
        """Release all hardware resources (GPIO, serial, ADC handles)."""
