"""
install_dependencies.py — Install all libraries required to run the scCO2
Pressure Regulation System in simulation mode (Windows or macOS).

Run once before launching main.py:
    python install_dependencies.py
"""

import importlib
import platform
import subprocess
import sys


def pip(package: str) -> None:
    module = package.split("[")[0].replace("-", "_").lower()
    try:
        importlib.import_module(module)
        print(f"    {package} already installed — skipping")
        return
    except ImportError:
        pass
    # --user avoids permission errors when not inside a virtualenv
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "--user", package]
    )


def check_tkinter() -> bool:
    """Return True if tkinter is available, False otherwise."""
    try:
        import tkinter  # noqa: F401
        return True
    except ImportError:
        return False


DESKTOP_SIM = [
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
    os_name = platform.system()   # 'Windows', 'Darwin', 'Linux'
    display_os = "macOS" if os_name == "Darwin" else os_name

    print("=" * 55)
    print("  scCO2 Pressure Regulation System — dependency install")
    print(f"  Platform: {display_os} (simulation mode)")
    print("=" * 55)

    # macOS: tkinter ships with Python.org builds but NOT with Homebrew Python.
    # Check early so the user can fix it before pip installs everything else.
    if os_name == "Darwin" and not check_tkinter():
        print("\n  WARNING: tkinter not found.")
        print("  The GUI requires tkinter.  Install it with Homebrew:")
        print("    brew install python-tk")
        print("  Then re-run this script.")
        print("=" * 55)
        sys.exit(1)

    for pkg in DESKTOP_SIM:
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
