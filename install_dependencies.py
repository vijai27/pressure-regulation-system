"""
install_dependencies.py — Install all libraries required to run the scCO2
Pressure Regulation System on Windows (simulation mode).

Run once before launching main.py:
    python install_dependencies.py
"""

import subprocess
import sys


def pip(package: str) -> None:
    # --user avoids permission errors on Windows; skip if already importable
    import importlib
    module = package.split("[")[0].replace("-", "_").lower()
    try:
        importlib.import_module(module)
        print(f"    {package} already installed — skipping")
        return
    except ImportError:
        pass
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--user", package]
    )


WINDOWS_SIM = [
    "numpy",           # PR-EOS cubic solver (control/eos.py)
    "matplotlib",      # Live pressure/temperature plot in GUI (gui.py)
    "requests",        # ThingSpeak cloud upload (cloud.py)
]

RPI_ONLY = [
    # Uncomment when deploying to Raspberry Pi (SIMULATION = False)
    # "RPi.GPIO",      # GPIO step/dir/enable pins for stepper + solenoid relay
    # "adafruit-circuitpython-ads1x15",  # ADS1115 ADC for 4-20 mA pressure transducer
    # "adafruit-blinka",                 # CircuitPython compatibility layer for RPi
]

if __name__ == "__main__":
    print("=" * 55)
    print("  scCO2 Pressure Regulation System — dependency install")
    print("=" * 55)

    for pkg in WINDOWS_SIM:
        print(f"\n>>> Installing {pkg} ...")
        try:
            pip(pkg)
            print(f"    {pkg} OK")
        except subprocess.CalledProcessError as e:
            print(f"    ERROR installing {pkg}: {e}")
            sys.exit(1)

    print("\n" + "=" * 55)
    print("  All dependencies installed.")
    print("  Run the app with:")
    print("    cd pressure_control")
    print("    python main.py")
    if RPI_ONLY:
        print("\n  RPi hardware libraries are commented out in this")
        print("  script — uncomment them when deploying to the Pi.")
    print("=" * 55)
