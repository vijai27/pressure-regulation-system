# hardware/rpi_hardware.py — Real Raspberry Pi hardware interface
#
# Wiring:
#   ADS1115 (I²C):
#     A0 → Pressure transducer 4–20 mA via 250 Ω shunt (1–5 V)
#     A1 → Thermocouple amplifier output (0–5 V → 0–100 °C)
#   A4988 stepper driver:
#     STEP → GPIO 17 (BCM)
#     DIR  → GPIO 27 (BCM)
#     ENA  → GPIO 22 (BCM)  (active LOW)
#   Relay for solenoid:
#     IN   → GPIO 18 (BCM)
#   E-stop (NC momentary):
#     → GPIO 23 (BCM)  (pulled HIGH internally, LOW when pressed)

import logging
import time

from hardware.base import HardwareBase
from config import (
    RPI_VALVE_STEP_PIN, RPI_VALVE_DIR_PIN, RPI_VALVE_ENABLE_PIN,
    RPI_SOLENOID_PIN, RPI_ESTOP_PIN,
    ADS_PRESSURE_CHANNEL, ADS_TEMP_CHANNEL,
    PT_VOLT_MIN, PT_VOLT_MAX, PT_PRESS_MIN, PT_PRESS_MAX,
    VALVE_TOTAL_STEPS,
)

log = logging.getLogger(__name__)

_ADS_CHANNEL_MAP = {0: 0, 1: 1, 2: 2, 3: 3}


class RPiHardware(HardwareBase):
    """Real hardware interface. Requires: adafruit-circuitpython-ads1x15, RPi.GPIO."""

    def __init__(self):
        import board
        import busio
        import adafruit_ads1x15.ads1115 as ADS
        from adafruit_ads1x15.ads1115 import P0, P1, P2, P3
        from adafruit_ads1x15.analog_in import AnalogIn
        import RPi.GPIO as GPIO

        self._GPIO = GPIO

        self._i2c = busio.I2C(board.SCL, board.SDA)
        self._ads = ADS.ADS1115(self._i2c)

        # Map integer channel numbers to ADS channel constants
        _ch_map = {0: P0, 1: P1, 2: P2, 3: P3}
        self._ch_press = AnalogIn(self._ads, _ch_map[ADS_PRESSURE_CHANNEL])
        self._ch_temp  = AnalogIn(self._ads, _ch_map[ADS_TEMP_CHANNEL])

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(RPI_VALVE_STEP_PIN,   GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(RPI_VALVE_DIR_PIN,    GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(RPI_VALVE_ENABLE_PIN, GPIO.OUT, initial=GPIO.HIGH)  # disabled
        GPIO.setup(RPI_SOLENOID_PIN,     GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(RPI_ESTOP_PIN,        GPIO.IN,  pull_up_down=GPIO.PUD_UP)

        self._valve_steps   = 0
        self._solenoid_duty = 0.0

        # PWM on solenoid pin at 1 Hz
        self._pwm = GPIO.PWM(RPI_SOLENOID_PIN, 1)
        self._pwm.start(0)

        log.info("RPiHardware initialised — ADS1115 on I²C, GPIO BCM mode.")

    # ── Sensor reads ──────────────────────────────────────────────────────────

    def read_pressure(self) -> float:
        """Read ADS1115 A0, convert 1–5 V → 0–28 MPa."""
        voltage  = self._ch_press.voltage
        pressure = (voltage - PT_VOLT_MIN) / (PT_VOLT_MAX - PT_VOLT_MIN) * PT_PRESS_MAX
        return max(0.0, pressure)

    def read_temperature(self) -> float:
        """Read ADS1115 A1, convert 0–5 V → 0–100 °C."""
        voltage = self._ch_temp.voltage
        return voltage / 5.0 * 100.0

    # ── Actuator commands ─────────────────────────────────────────────────────

    def set_valve_position(self, pct: float) -> None:
        """Move stepper to correspond to pct % of full open."""
        target_steps = int(pct / 100.0 * VALVE_TOTAL_STEPS)
        delta = target_steps - self._valve_steps
        self._move_stepper(delta)
        self._valve_steps = target_steps

    def set_solenoid_pwm(self, duty: float) -> None:
        """Set PWM duty cycle on relay-controlled solenoid (1 Hz carrier)."""
        duty = max(0.0, min(100.0, duty))
        self._pwm.ChangeDutyCycle(duty)
        self._solenoid_duty = duty

    def read_estop(self) -> bool:
        """Return True if E-stop pressed (NC contact opened → pin LOW)."""
        return self._GPIO.input(RPI_ESTOP_PIN) == self._GPIO.LOW

    def get_valve_position(self) -> float:
        return self._valve_steps / VALVE_TOTAL_STEPS * 100.0

    def get_solenoid_pwm(self) -> float:
        return self._solenoid_duty

    def emergency_stop(self) -> None:
        """Immediately disable stepper and close solenoid."""
        self._GPIO.output(RPI_VALVE_ENABLE_PIN, self._GPIO.HIGH)  # disable stepper
        self._pwm.ChangeDutyCycle(0)
        self._GPIO.output(RPI_SOLENOID_PIN, self._GPIO.LOW)
        self._solenoid_duty = 0.0
        log.warning("Emergency stop triggered.")

    def close(self) -> None:
        """Release GPIO resources."""
        try:
            self.emergency_stop()
        except Exception:
            pass
        self._pwm.stop()
        self._GPIO.cleanup()
        log.info("RPiHardware closed.")

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _move_stepper(self, steps: int) -> None:
        """Send step pulses to A4988 driver. Positive = open, negative = close."""
        if steps == 0:
            return
        GPIO = self._GPIO
        direction = GPIO.HIGH if steps > 0 else GPIO.LOW
        GPIO.output(RPI_VALVE_DIR_PIN,    direction)
        GPIO.output(RPI_VALVE_ENABLE_PIN, GPIO.LOW)   # enable
        for _ in range(abs(steps)):
            GPIO.output(RPI_VALVE_STEP_PIN, GPIO.HIGH)
            time.sleep(0.001)
            GPIO.output(RPI_VALVE_STEP_PIN, GPIO.LOW)
            time.sleep(0.001)
        GPIO.output(RPI_VALVE_ENABLE_PIN, GPIO.HIGH)  # disable when done
