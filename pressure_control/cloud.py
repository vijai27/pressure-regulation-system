# cloud.py — ThingSpeak cloud uploader (background thread)
#
# Runs in a daemon thread started by main.py.
# Reads the latest sensor data from a shared data object and POSTs
# to ThingSpeak every THINGSPEAK_INTERVAL_S seconds (non-blocking).
#
# ThingSpeak field mapping:
#   field1 → pressure_MPa
#   field2 → temperature_C
#   field3 → setpoint_MPa
#   field4 → state_code  (0=IDLE, 1=PRESSURIZE, 2=HOLD, 3=DEPRESSURIZE)
#
# Setup:
#   1. Create free account at https://thingspeak.com
#   2. Create a channel with 4 fields
#   3. Set THINGSPEAK_API_KEY and THINGSPEAK_CHANNEL_ID in config.py

import logging
import threading
import time

import requests

from config import (
    THINGSPEAK_API_KEY,
    THINGSPEAK_URL,
    THINGSPEAK_INTERVAL_S,
)

log = logging.getLogger(__name__)


class CloudUploader:
    """Uploads experiment data to ThingSpeak at a fixed interval."""

    def __init__(self):
        self._lock = threading.Lock()
        self._data = {
            "pressure":    0.0,
            "temperature": 25.0,
            "setpoint":    0.0,
            "state_code":  0,
        }
        self._running = False
        self._thread: threading.Thread | None = None
        self._enabled = THINGSPEAK_API_KEY not in ("YOUR_API_KEY_HERE", "", None)
        if not self._enabled:
            log.warning("ThingSpeak API key not set — cloud upload disabled.")

    def start(self) -> None:
        """Start background upload thread."""
        if not self._enabled:
            return
        self._running = True
        self._thread = threading.Thread(target=self._upload_loop, daemon=True)
        self._thread.start()
        log.info("Cloud uploader started (%.1f s interval).", THINGSPEAK_INTERVAL_S)

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)

    def update(
        self,
        pressure: float,
        temperature: float,
        setpoint: float,
        state_code: int,
    ) -> None:
        """Update the latest values to upload. Thread-safe. Called at 10 Hz."""
        with self._lock:
            self._data["pressure"]    = pressure
            self._data["temperature"] = temperature
            self._data["setpoint"]    = setpoint
            self._data["state_code"]  = state_code

    def _upload_loop(self) -> None:
        while self._running:
            start = time.monotonic()
            with self._lock:
                snapshot = dict(self._data)

            try:
                params = {
                    "api_key": THINGSPEAK_API_KEY,
                    "field1":  round(snapshot["pressure"],    4),
                    "field2":  round(snapshot["temperature"], 3),
                    "field3":  round(snapshot["setpoint"],    4),
                    "field4":  snapshot["state_code"],
                }
                resp = requests.get(THINGSPEAK_URL, params=params, timeout=5)
                if resp.status_code != 200 or resp.text == "0":
                    log.warning("ThingSpeak upload failed: %s %s", resp.status_code, resp.text)
            except requests.RequestException as exc:
                log.debug("ThingSpeak network error (will retry): %s", exc)

            elapsed = time.monotonic() - start
            sleep = THINGSPEAK_INTERVAL_S - elapsed
            if sleep > 0:
                time.sleep(sleep)
