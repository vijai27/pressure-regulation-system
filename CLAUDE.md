# scCO₂ Automated Pressure Regulation System — Project Brief

This file gives full context to continue development. Read it completely before
touching any code.

---

## What This Project Is

An automated closed-loop pressure control system for a supercritical CO₂ (scCO₂)
research vessel. The system pressurizes a sealed PARR vessel with CO₂ to a target
pressure (up to 28 MPa), holds it stable, then safely depressurizes — all under
Raspberry Pi computer control with a Python PID controller.

CO₂ becomes supercritical above 31.1°C / 7.38 MPa. We operate at 60°C so CO₂
enters the supercritical phase immediately after crossing 7.38 MPa during the ramp.

**Research context:** Multiple gases are used across experiments:
- CO₂ (Bone Dry, UN1013) — primary process gas
- N₂ (Ultra High Purity, UN1066) — alternate experiment gas
- Ar (Prepurified, UN1006) — alternate experiment gas
- Air (Dry Grade, UN1002) — drives the booster pump only, never enters vessel

All cylinders are from Metro Welding Supply, Detroit MI 48223.

---

## Current Status

### ✅ Complete
- Full Python control app (`pressure_control/`) — 13 files, runs in simulation on Windows
- Peng-Robinson EOS for real CO₂ physics (`control/eos.py`)
- Adaptive gain scheduler (`control/gain_scheduler.py`) — gains change with pressure
- Windows physics simulator (`hardware/simulator.py`) — 10 Hz, uses PR-EOS
- Tkinter + Matplotlib live GUI (`gui.py`)
- CSV data logger (`logger.py`)
- ThingSpeak cloud uploader (`cloud.py`)
- Simulink MATLAB scripts (`simulink/`) — digital twin, not yet tested
- PowerPoint deck (`scCO2_System_Presentation.pptx`) — for professor
- Schematic diagram (`scCO2_Schematic.png`) — P&ID style
- `install_dependencies.py` — one-shot Windows setup
- `make_ppt.js` / `make_schematic.py` — regenerate deliverables

### 🔴 Immediate Next (blocking hardware deployment)
1. **Fill in `rpi_hardware.py`** — it is a stub with `raise NotImplementedError` everywhere.
   All the code is commented out inside each method. Just uncomment and fix imports.
   Needs: `adafruit-circuitpython-ads1x15`, `RPi.GPIO`, `adafruit-blinka`

2. **Re-tune HOLD PID gains** — PR-EOS shows a 0.01°C flicker moves pressure by
   3.5–4.7 kPa at 20–28 MPa (5–6× more than ideal gas predicted). Run simulation
   to 20 MPa, watch hold behavior, adjust `HOLD_KP/KI/KD` in `config.py`.

### 🟡 Soon
3. **Valve Cv calibration** — run timed pressurization at a fixed valve opening,
   back-calculate Cv from pressure rise + PR-EOS. Replaces the empirical `SIM_K_FLOW`.

4. **Simulink PID tuning** — `simulink/build_model.m` builds the plant in Simscape
   Fluids. Needs MATLAB + Simscape Fluids toolbox. Not yet tested.

5. **ThingSpeak** — create account, set `THINGSPEAK_API_KEY` in `config.py`.

---

## Hardware Inventory (confirmed from lab photos)

### Pressure Vessel
- **PARR Instrument Company**, Moline IL
- Model: 2302HC, S/M: 4540-1803-78845A
- Volume: **~1 L**
- Material: **316 SS** (T316-T per nameplate)
- **MAWP: 5000 PSI (34.47 MPa) at 350°C**
- Operating max in this system: 28 MPa (safety margin ~23%)

### Gas Booster (Pump)
- **Hydraulics International, Inc.** (HII), Chatsworth CA
- Model: **5G-TD-28/150-CO2**, Serial: 1205101
- Type: Air-driven, twin-drive, CO₂ service
- **Max inlet: 4500 PSIG (31.0 MPa)**
- **Max outlet: 25,000 PSIG (172.4 MPa)**
- **Max drive air: 150 PSIG (10 bar)**
- At typical 100 PSI shop air: outlet >> 28 MPa — effectively infinite supply pressure
  relative to our operating range. Modeled in sim as `SIM_P_BOOSTER_EFFECTIVE = 50.0 MPa`.

### Pressure Transducer
- Ashcroft, 0–5000 PSI, 4–20 mA output, SS, IP67
- Grainger item K4708
- Wired to ADS1115 channel A0 via 250 Ω shunt resistor (4–20 mA → 1–5 V)

### Temperature Control
- **INKBIRD** temperature controller
- Setpoint: **60°C**
- Stability once settled: **±0.01°C** (observed in lab)
- During heat-up: oscillates ±0.3–0.5°C until temperature stabilizes (~30–60 s)
- Wired to ADS1115 channel A1 via thermocouple amplifier (0–5 V → 0–100°C)

### Controller
- Raspberry Pi 4
- Python 3.11
- `SIMULATION = True` in `config.py` for Windows testing
- `SIMULATION = False` for real RPi deployment

### Other Electronics
- ADS1115 16-bit I²C ADC — reads pressure transducer + temp sensor
- A4988 stepper driver (1/16 microstepping) — drives needle valve motor
- NEMA 17 stepper motor (200 steps/rev) — actuates needle valve
- 24VDC relay module — GPIO drives vent solenoid
- Dayton 33NT20 DIN rail PSU, 24VDC 50W (Grainger)

---

## How to Run (Windows Simulation)

```bash
# Install dependencies (one time)
cd "C:/path/to/Pressure Regulation System"
python install_dependencies.py

# Run the app
cd pressure_control
python main.py
```

`SIMULATION = True` is set in `config.py`. No hardware needed.
The GUI opens with a live pressure/temperature plot and START/STOP buttons.

---

## File Structure

```
Pressure Regulation System/
├── CLAUDE.md                        ← YOU ARE HERE
├── install_dependencies.py          ← pip install for Windows sim
├── make_ppt.js                      ← regenerates PowerPoint (node make_ppt.js)
├── make_schematic.py                ← regenerates P&ID schematic (python)
├── scCO2_System_Presentation.pptx   ← 10-slide professor deck
├── scCO2_Schematic.png              ← P&ID schematic diagram
│
├── pressure_control/                ← MAIN APPLICATION
│   ├── main.py                      ← Entry point. Set SIMULATION flag here.
│   ├── config.py                    ← ALL constants. Edit this first for any tuning.
│   ├── gui.py                       ← Tkinter + Matplotlib live dashboard
│   ├── logger.py                    ← CSV log to logs/ directory
│   ├── cloud.py                     ← ThingSpeak uploader (background thread)
│   │
│   ├── hardware/
│   │   ├── base.py                  ← Abstract HAL interface (do not edit)
│   │   ├── simulator.py             ← Windows physics sim (PR-EOS, 10 Hz thread)
│   │   └── rpi_hardware.py          ← RPi stub — NEEDS COMPLETING (see below)
│   │
│   └── control/
│       ├── pid.py                   ← PID with anti-windup, derivative on measurement
│       ├── ramp.py                  ← Linear ramp setpoint generator
│       ├── state_machine.py         ← IDLE/PRESSURIZE/HOLD/DEPRESSURIZE logic
│       ├── gain_scheduler.py        ← Adaptive Kp/Ki/Kd vs pressure lookup table
│       └── eos.py                   ← Peng-Robinson EOS for CO₂ (new, key file)
│
└── simulink/
    ├── build_model.m                ← Creates scCO2_plant.slx programmatically
    ├── run_simulation.m             ← Runs sim, plots results
    └── export_gains.m               ← Exports Kp/Ki/Kd after PID Tuner
```

---

## Key Design Decisions (do not change without understanding why)

### 1. Hardware Abstraction Layer
`SimulatedHardware` and `RPiHardware` both inherit from `HardwareBase`.
To switch between simulation and real hardware, change ONE line in `main.py`:
```python
hw = SimulatedHardware()   # Windows
hw = RPiHardware()          # Raspberry Pi
```
The `SIMULATION` flag in `config.py` controls which one `main.py` picks.

### 2. Rate Limiter is WARNING-only (not bang-bang)
The rate limiter logs a warning when rate > 600 kPa/min and only forces IDLE
if rate > 5000 kPa/min (catastrophic). The ramp setpoint does the actual rate
control. Do not add bang-bang valve close logic — it causes chattering.

### 3. Adaptive Gain Scheduler
PID gains are NOT fixed. They change every 100 ms based on current pressure.
See `control/gain_scheduler.py` for the full table. Key insight:
- 0–17.2 MPa: gains INCREASE (gas is highly compressible, needs more valve)
- 17.2–28 MPa: gains DECREASE (dense fluid, hair-trigger response)
- 17.2 MPa = 2500 PSI crossover observed in lab
- gas_factor multiplies Kp: CO₂=1.0, N₂=0.80, Ar=0.85

### 4. Peng-Robinson EOS (not ideal gas)
`control/eos.py` replaces ideal gas law for the temperature-pressure coupling.
Key numbers at 60°C:
- At 20 MPa: Z = 0.46 (CO₂ is 118% denser than ideal gas predicts)
- A 0.01°C flicker → 3.5 kPa pressure change at 20 MPa (5.9× ideal gas)
- This is critical for HOLD accuracy
The main function used in simulator: `eos.dP_from_dT(P_MPa, T_K, dT_K)`

### 5. Booster modeled as fixed high-pressure source
Real booster (HII 5G-TD): at 100 PSI shop air, outlet >> 28 MPa.
`SIM_P_BOOSTER_EFFECTIVE = 50.0 MPa` in config.py.
Flow model: `dP_flow = K_FLOW × valve_pct × sqrt(P_booster - P_vessel)`
`K_FLOW = 0.003` is empirical — replace with Cv-based value after calibration.

### 6. Temperature model
INKBIRD oscillates during heat-up, settles to ±0.01°C.
Simulator models this: noise σ = 0.30°C when far from setpoint, 0.01°C when settled.
Transition is smooth via: `settled = 1 / (1 + (|error| / 2.0)²)`

### 7. 5-second rolling window for rate estimation
Single-step dP/dt at 10 Hz with 5 kPa noise = ~3000 kPa/min apparent rate.
5-second window reduces this to well below the 600 kPa/min safety threshold.
Requires ≥3 seconds of data before producing a rate estimate.

---

## Key Parameters (all in `config.py`)

| Parameter | Value | Source |
|---|---|---|
| `MAX_PRESSURE` | 28.0 MPa | System design limit |
| `VESSEL_MAWP_MPA` | 34.47 MPa | PARR nameplate (5000 PSI) |
| `PRESSURIZE_RATE_MPA_MIN` | 0.350 MPa/min | 350 kPa/min spec |
| `DEPRESSURIZE_RATE_MPA_MIN` | 2.0 MPa/min | Safety spec |
| `INKBIRD_SETPOINT_C` | 60.0°C | Above CO₂ Tc = 31.1°C |
| `MIN_START_TEMP_C` | 55.0°C | Temperature gate |
| `VESSEL_VOLUME_L` | 1.0 L | PARR vessel (user measured) |
| `SIM_P_BOOSTER_EFFECTIVE` | 50.0 MPa | HII booster at 100 PSI air |
| `SIM_K_FLOW` | 0.003 | Empirical — replace with Cv |
| `SAMPLE_TIME_S` | 0.1 s | 10 Hz control loop |
| `OVERPRESSURE_LIMIT` | 28.5 MPa | Software safety trip |

---

## PR-EOS Constants for CO₂ (in `control/eos.py`)

```
Tc    = 304.13 K     (31.0°C critical temperature)
Pc    = 7.3773 MPa   (critical pressure)
omega = 0.22394      (acentric factor)
R     = 8.314462e-6  (MPa·m³/mol·K)
b     = 2.664e-5     (m³/mol, computed from Tc/Pc)
```

---

## Completing `rpi_hardware.py` (next hardware task)

The file has all code written but commented out. Steps:
1. On RPi: `pip install adafruit-circuitpython-ads1x15 adafruit-blinka RPi.GPIO`
2. In `rpi_hardware.py`: uncomment everything in `__init__`, remove `raise NotImplementedError`
3. Fix each method — all code is already written in comments
4. Key wiring:
   - ADS1115 A0: pressure transducer 4–20 mA via 250 Ω shunt → 1–5 V
   - ADS1115 A1: thermocouple amplifier 0–5 V → 0–100°C
   - GPIO 17 (BCM): stepper STEP
   - GPIO 27 (BCM): stepper DIR
   - GPIO 22 (BCM): stepper ENABLE (active LOW)
   - GPIO 18 (BCM): solenoid PWM (hardware PWM channel 0)
   - GPIO 23 (BCM): E-stop (NC, pulled HIGH, LOW when pressed)

---

## Parts Still to Buy

### Grainger
- Ashcroft PT transducer 0–5000 PSI 4–20 mA (K4708) ~$400
- Ashcroft pressure gauge 0–5000 PSI (K4201) ~$100
- Parker relief valve SS316 1/4" MNPT (442F42) ~$165
- Dayton DIN rail PSU 24VDC 50W (33NT20) ~$55
- DIN rail relay 24VDC coil ~$20
- PTFE tape (34P209) ~$5

### Amazon
- Raspberry Pi 4 (4GB) ~$55
- ADS1115 ADC module ~$10
- NEMA 17 stepper motor ~$15
- A4988 stepper driver ~$8
- 32 GB microSD card ~$10
- Relay module 24VDC ~$10

### High Pressure (Swagelok / Parker / HIP)
- Motorized needle valve, SS, 1/4" tube, >5000 PSI ~$400
- Check valve SS316 1/4" tube >5000 PSI ~$150
- Manual ball valves ×3, SS, 1/4" tube >5000 PSI ~$300
- SS tubing 1/4" OD × 0.065" wall 316SS 10 ft ~$80
- Swagelok compression fittings assorted ~$200

---

## Windows Encoding Note

Always open Python files with `encoding='utf-8'` on Windows.
The default cp1252 breaks on °C, CO₂ subscripts, and similar Unicode characters.

---

## Running the PPT / Schematic generators

```bash
# PowerPoint (needs Node.js + pptxgenjs)
cd "Pressure Regulation System"
npm install          # first time only
node make_ppt.js     # outputs scCO2_System_Presentation.pptx

# Schematic diagram
python make_schematic.py   # outputs scCO2_Schematic.png
```

---

## What Not to Change

- `hardware/base.py` — abstract interface, never edit directly
- `control/eos.py` — PR-EOS constants are from published CO₂ data, not tunable
- The rate limiter logic in `state_machine.py` — WARNING-only is intentional
- `SIM_T_NOISE_SETTLED_C = 0.01` — matches actual lab measurement (±0.01°C)
