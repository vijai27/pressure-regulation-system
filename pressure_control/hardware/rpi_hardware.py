# hardware/rpi_hardware.py — Real Raspberry Pi hardware interface
#
# Wiring:
#   ADS1115 (I²C):
#     A0 → Pressure transducer 4–20 mA via 250 Ω shunt (1–5 V)
#     A1 → Thermocouple amplifier output (0–5 V → 0–100 °C)
#   TB6600 stepper driver:
#     STEP → GPIO RPI_VALVE_STEP_PIN (BCM)
#     DIR  → GPIO RPI_VALVE_DIR_PIN
#     ENA  → GPIO RPI_VALVE_ENABLE_PIN  (active LOW)
#   SSR for solenoid:
#     IN   → GPIO RPI_SOLENOID_PIN  (hardware PWM, 1 Hz)
#   E-stop (NC momentary):
#     → GPIO RPI_ESTOP_PIN  (pulled HIGH internally, LOW when pressed)
#
# This file is a STUB — complete it when hardware arrives.
# All methods raise NotImplementedError until wired up.

import logging

from hardware.base import HardwareBase
from config import (
    RPI_VALVE_STEP_PIN, RPI_VALVE_DIR_PIN, RPI_VALVE_ENABLE_PIN,
    RPI_SOLENOID_PIN, RPI_ESTOP_PIN,
    ADS_PRESSURE_CHANNEL, ADS_TEMP_CHANNEL,
    PT_VOLT_MIN, PT_VOLT_MAX, PT_PRESS_MIN, PT_PRESS_MAX,
    VALVE_TOTAL_STEPS,
)

log = logging.getLogger(__name__)


class RPiHardware(HardwareBase):
    """Real hardware interface.  Requires: adafruit-ads1x15, RPi.GPIO."""

    def __init__(self):
        # -- Uncomment and complete when hardware arrives --
        #
        # import board
        # import busio
        # import adafruit_ads1x15.ads1115 as ADS
        # from adafruit_ads1x15.analog_in import AnalogIn
        # import RPi.GPIO as GPIO
        #
        # self._i2c = busio.I2C(board.SCL, board.SDA)
        # self._ads = ADS.ADS1115(self._i2c)
        # self._ch_press = AnalogIn(self._ads, ADS_PRESSURE_CHANNEL)
        # self._ch_temp  = AnalogIn(self._ads, ADS_TEMP_CHANNEL)
        #
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(RPI_VALVE_STEP_PIN,   GPIO.OUT, initial=GPIO.LOW)
        # GPIO.setup(RPI_VALVE_DIR_PIN,    GPIO.OUT, initial=GPIO.LOW)
        # GPIO.setup(RPI_VALVE_ENABLE_PIN, GPIO.OUT, initial=GPIO.HIGH)  # disabled
        # GPIO.setup(RPI_SOLENOID_PIN,     GPIO.OUT, initial=GPIO.LOW)
        # GPIO.setup(RPI_ESTOP_PIN,        GPIO.IN,  pull_up_down=GPIO.PUD_UP)
        #
        # self._valve_steps = 0   # Current position in steps (0 = fully closed)
        # self._solenoid_duty = 0.0

        raise NotImplementedError(
            "RPiHardware is a stub — complete wiring and uncomment GPIO/ADS code."
        )

    # ── Sensor reads ──────────────────────────────────────────────────────────

    def read_pressure(self) -> float:
        """Read ADS1115 A0, convert 1–5 V → 0–28 MPa."""
        # voltage = self._ch_press.voltage
        # pressure = (voltage - PT_VOLT_MIN) / (PT_VOLT_MAX - PT_VOLT_MIN) * PT_PRESS_MAX
        # return max(0.0, pressure)
        raise NotImplementedError

    def read_temperature(self) -> float:
        """Read ADS1115 A1, convert voltage → °C (depends on amplifier used)."""
        # voltage = self._ch_temp.voltage
        # temp_c = voltage / 5.0 * 100.0   # Example: 0–5 V → 0–100 °C
        # return temp_c
        raise NotImplementedError

    # ── Actuator commands ─────────────────────────────────────────────────────

    def set_valve_position(self, pct: float) -> None:
        """Move stepper to correspond to pct % of full open."""
        # target_steps = int(pct / 100.0 * VALVE_TOTAL_STEPS)
        # delta = target_steps - self._valve_steps
        # self._move_stepper(delta)
        # self._valve_steps = target_steps
        raise NotImplementedError

    def set_solenoid_pwm(self, duty: float) -> None:
        """Set PWM duty cycle on SSR-controlled solenoid (1 Hz carrier)."""
        # GPIO.PWM(RPI_SOLENOID_PIN, 1).ChangeDutyCycle(duty)
        # self._solenoid_duty = duty
        raise NotImplementedError

    def read_estop(self) -> bool:
        """Return True if E-stop pressed (NC contact opened → pin LOW)."""
        # return GPIO.input(RPI_ESTOP_PIN) == GPIO.LOW
        raise NotImplementedError

    def get_valve_position(self) -> float:
        # return self._valve_steps / VALVE_TOTAL_STEPS * 100.0
        raise NotImplementedError

    def get_solenoid_pwm(self) -> float:
        # return self._solenoid_duty
        raise NotImplementedError

    def emergency_stop(self) -> None:
        """Immediately disable stepper and close solenoid."""
        # GPIO.output(RPI_VALVE_ENABLE_PIN, GPIO.HIGH)  # disable stepper
        # GPIO.output(RPI_SOLENOID_PIN, GPIO.LOW)
        # self._solenoid_duty = 0.0
        raise NotImplementedError

    def close(self) -> None:
        """Release GPIO resources."""
        # GPIO.cleanup()
        raise NotImplementedError

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _move_stepper(self, steps: int) -> None:
        """Send step pulses to TB6600 driver.  Positive = open, negative = close."""
        # import RPi.GPIO as GPIO
        # import time
        # direction = GPIO.HIGH if steps > 0 else GPIO.LOW
        # GPIO.output(RPI_VALVE_DIR_PIN,    direction)
        # GPIO.output(RPI_VALVE_ENABLE_PIN, GPIO.LOW)   # enable
        # for _ in range(abs(steps)):
        #     GPIO.output(RPI_VALVE_STEP_PIN, GPIO.HIGH)
        #     time.sleep(0.001)
        #     GPIO.output(RPI_VALVE_STEP_PIN, GPIO.LOW)
        #     time.sleep(0.001)
        raise NotImplementedError
