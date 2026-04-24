#!/usr/bin/env python3
# main.py — Entry point for the High-Pressure Vessel Control System
#
# Usage (Windows simulation):
#   cd pressure_control
#   python main.py
#
# Usage (Raspberry Pi, real hardware):
#   Set SIMULATION = False in config.py, then:
#   python main.py
#
# Architecture:
#   - Control thread runs at 10 Hz, owns the state machine and hardware
#   - GUI thread (Tkinter main loop) reads SharedData and dispatches commands
#   - Cloud thread uploads to ThingSpeak every 2 s (daemon, optional)
#   - Logger writes CSV every 100 ms from the control thread

import logging
import sys
import threading
import time
import tkinter as tk
from pathlib import Path

# Add parent directory so imports work when running from inside pressure_control/
sys.path.insert(0, str(Path(__file__).parent))

from config import SIMULATION, SAMPLE_TIME_S, WATCHDOG_TIMEOUT_S, LOG_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("main")


def build_hardware():
    """Instantiate the correct hardware backend."""
    if SIMULATION:
        from hardware.simulator import SimulatedHardware
        log.info("Mode: SIMULATION (Windows)")
        return SimulatedHardware()
    else:
        from hardware.rpi_hardware import RPiHardware
        log.info("Mode: REAL HARDWARE (Raspberry Pi)")
        return RPiHardware()


def control_loop(hardware, sm, shared, logger, cloud):
    """Main control thread — runs at 10 Hz."""
    log.info("Control loop started.")
    prev_pressure = hardware.read_pressure()
    prev_time     = time.monotonic()

    while not stop_event.is_set():
        loop_start = time.monotonic()

        pressure    = hardware.read_pressure()
        temperature = hardware.read_temperature()
        valve_pct   = hardware.get_valve_position()
        solenoid_pct = hardware.get_solenoid_pwm()

        # Compute rate of pressure change (kPa/min)
        now = time.monotonic()
        dt  = now - prev_time
        rate_kpa_min = abs((pressure - prev_pressure) / dt * 60.0 * 1000) if dt > 0 else 0.0
        prev_pressure = pressure
        prev_time     = now

        # Run state machine
        sm.tick(pressure, temperature)

        # Update shared data for GUI
        shared.update(
            pressure     = pressure,
            temperature  = temperature,
            setpoint     = sm.setpoint,
            valve_pct    = valve_pct,
            solenoid_pct = solenoid_pct,
            state        = sm.state,
            rate_kpa_min = rate_kpa_min,
            status_msg   = sm.status_message,
        )

        # Log row
        logger.log(
            pressure    = pressure,
            temperature = temperature,
            setpoint    = sm.setpoint,
            state       = sm.state.name,
            valve_pct   = valve_pct,
            solenoid_pct = solenoid_pct,
        )

        # Update cloud uploader
        cloud.update(
            pressure    = pressure,
            temperature = temperature,
            setpoint    = sm.setpoint,
            state_code  = int(sm.state),
        )

        # Sleep for remainder of sample period
        elapsed   = time.monotonic() - loop_start
        sleep_for = SAMPLE_TIME_S - elapsed
        if sleep_for > 0:
            time.sleep(sleep_for)
        else:
            log.warning("Control loop overrun by %.1f ms", -sleep_for * 1000)

    log.info("Control loop stopped.")


def main():
    global stop_event
    stop_event = threading.Event()

    # ── Hardware ──────────────────────────────────────────────────────────────
    hardware = build_hardware()

    # ── State machine ─────────────────────────────────────────────────────────
    from control.state_machine import StateMachine
    sm = StateMachine(hardware, target_pressure=28.0)

    # ── Shared data (control → GUI) ───────────────────────────────────────────
    from gui import SharedData
    shared = SharedData()

    # ── Logger ────────────────────────────────────────────────────────────────
    from logger import DataLogger
    logger = DataLogger(log_dir=LOG_DIR)

    # ── Cloud uploader ────────────────────────────────────────────────────────
    from cloud import CloudUploader
    cloud = CloudUploader()
    cloud.start()

    # ── Control thread ────────────────────────────────────────────────────────
    ctrl_thread = threading.Thread(
        target=control_loop,
        args=(hardware, sm, shared, logger, cloud),
        daemon=True,
        name="ControlLoop",
    )
    ctrl_thread.start()

    # ── GUI (runs on main thread) ─────────────────────────────────────────────
    from gui import App
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda: _shutdown(root, hardware, logger, cloud))
    app = App(root, shared, sm)

    log.info("GUI starting.")
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        _shutdown(root, hardware, logger, cloud)


def _shutdown(root, hardware, logger, cloud):
    log.info("Shutting down…")
    stop_event.set()
    hardware.emergency_stop()
    hardware.close()
    logger.close()
    cloud.stop()
    try:
        root.destroy()
    except Exception:
        pass
    log.info("Shutdown complete.")


if __name__ == "__main__":
    main()
