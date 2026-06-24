# config.py — All system constants and configuration
# Change SIMULATION = False and fill in RPi pins when deploying to hardware.

# ── Runtime mode ─────────────────────────────────────────────────────────────
SIMULATION = True           # True = desktop sim (Windows/macOS), False = real RPi hardware

# ── Pressure limits (MPa) ────────────────────────────────────────────────────
MAX_PRESSURE          = 28.0    # Absolute hardware maximum
SOFTWARE_MAX_SETPOINT = 28.0    # Cannot set target above this in GUI
AMBIENT_PRESSURE      = 0.34    # "Empty" threshold — vessel rests at ~35 PSI (0.34 MPa abs)
OVERPRESSURE_LIMIT    = 28.5    # Software safety cutoff → forces IDLE

# ── Rate limits ───────────────────────────────────────────────────────────────
PRESSURIZE_RATE_MPA_MIN   = 0.350   # 350 kPa/min = 0.35 MPa/min
DEPRESSURIZE_RATE_MPA_MIN = 2.0     # 2.0 MPa/min
MAX_RATE_LIMIT_MPA_MIN    = 0.600   # Safety: >600 kPa/min triggers valve close

# ── Hold accuracy ─────────────────────────────────────────────────────────────
HOLD_BAND_MPA = 0.30            # ±0.30 MPa dead-band around setpoint in HOLD

# ── Control loop ──────────────────────────────────────────────────────────────
SAMPLE_TIME_S = 0.1             # 100 ms (10 Hz)

# ── PID gains (tuned via Simulink — update after Phase 1) ────────────────────
# Units: error in MPa, output in 0–100 % valve/solenoid opening.
#
# Sizing rationale (sim physics: dP ≈ K_FLOW × valve% × sqrt(ΔP)):
#   At P=0.1 MPa: ~3.7 % valve needed for 350 kPa/min → Kp ≈ 40 (per MPa error)
#   Near max (ΔP small): valve must open ~100 % → integral compensates via Ki.
# Replace with Simulink-exported values after Phase 1 tuning.

# Pressurize PID: drives motorized valve (output 0–100 %)
PRESS_KP = 40.0
PRESS_KI = 5.0
PRESS_KD = 2.0
PRESS_OUTPUT_MIN = 0.0
PRESS_OUTPUT_MAX = 100.0

# Depressurize PID: drives solenoid PWM (output 0–100 %)
DEPRESS_KP = 60.0
DEPRESS_KI = 8.0
DEPRESS_KD = 1.0
DEPRESS_OUTPUT_MIN = 0.0
DEPRESS_OUTPUT_MAX = 100.0

# Hold PID: small adjustments to maintain setpoint (uses pressurize path)
HOLD_KP = 20.0
HOLD_KI = 2.0
HOLD_KD = 1.0

# ── Temperature pre-condition ─────────────────────────────────────────────────
MIN_START_TEMP_C = 55.0         # START disabled below this temperature
INKBIRD_SETPOINT_C = 60.0       # INKBIRD temperature controller target

# ── Watchdog ──────────────────────────────────────────────────────────────────
WATCHDOG_TIMEOUT_S = 1.0        # Control loop stall → force IDLE

# ── Hardware specs (from nameplates) ──────────────────────────────────────────
# Vessel: PARR Instrument Company, Moline IL, Model 2302HC, S/M 4540-1803-78845A
VESSEL_VOLUME_L  = 1.0      # L   (user measurement — 1 L PARR vessel)
VESSEL_MAWP_MPA  = 34.47    # MPa (5000 PSI at 350°C per nameplate)
VESSEL_MATERIAL  = "316 SS" # T316-T per nameplate

# Booster: Hydraulics International 5G-TD-28/150-CO2, S/N 1205101
BOOSTER_MAX_IN_PSIG   = 4500    # PSIG  max inlet pressure
BOOSTER_MAX_OUT_PSIG  = 25000   # PSIG  max outlet pressure (172.4 MPa)
BOOSTER_DRIVE_MAX_PSI = 150     # PSIG  max air drive pressure (10 bar)
BOOSTER_MAX_IN_MPA    = 31.03   # MPa   = 4500 PSIG
BOOSTER_MAX_OUT_MPA   = 172.4   # MPa   = 25,000 PSIG

# CO₂ supply cylinder (Bone Dry, UN1013, Metro Welding Supply Detroit)
CO2_CYLINDER_PRESSURE_MPA = 5.7    # MPa  approx. head pressure at room temp

# ── Simulation physics constants ──────────────────────────────────────────────
# Booster outlet is well above our 28 MPa operating range at any reasonable drive
# air pressure (100 PSI typical × 166:1 ratio = 115 MPa >> 28 MPa).
# Model as a fixed effective supply pressure to the needle valve.
SIM_P_BOOSTER_EFFECTIVE = 50.0  # MPa — sim supply pressure (constant; >> 28 MPa)

# Flow / vent constants
SIM_K_FLOW   = 0.003    # Pressurize: dP_flow = K_flow × valve_pct × sqrt(delta_P)  [MPa per step at 100%]
SIM_K_VENT   = 0.003    # Depressurize: dP_vent = K_vent × pwm_duty × P_vessel       [MPa per step]

# Temperature coupling (adiabatic heating, JT cooling — small effects at 60°C hold)
SIM_K_COMPRESS  = 0.8    # Adiabatic heating: dT = K × max(dP_flow,0) / P_booster
SIM_K_JT        = 0.25   # Joule-Thomson cooling: dT = K × min(dP_vent,0)
SIM_K_INKBIRD   = 0.067  # INKBIRD correction rate (τ ≈ 15 s)

# Temperature noise model (matches observed INKBIRD behavior):
#   Far from setpoint (INKBIRD hunting): ±0.3°C fluctuations during ramp
#   At setpoint (settled):               ±0.01°C as observed in lab
SIM_T_NOISE_FAR_C     = 0.30   # °C noise std when |error| >> settle band
SIM_T_NOISE_SETTLED_C = 0.01   # °C noise std when at setpoint (observed ±0.01°C)
SIM_T_SETTLE_BAND_C   = 2.0    # °C half-band — noise transitions from far→settled

# Pressure sensor noise
SIM_NOISE_P_MPA = 0.005  # MPa std-dev

# Initial conditions
SIM_INITIAL_PRESSURE_MPA = 0.34    # 35 PSI — vessel at rest
SIM_INITIAL_TEMP_C       = 25.0
SIM_HEAT_RATE_C_S        = 1.5     # INKBIRD warms at ~1.5 °C/s when cold

# ── RPi GPIO pin assignments (real hardware only) ─────────────────────────────
# ADS1115 is I²C — no GPIO pin needed; wired to SDA/SCL
RPI_VALVE_STEP_PIN   = 17   # BCM pin: stepper step pulse
RPI_VALVE_DIR_PIN    = 27   # BCM pin: stepper direction
RPI_VALVE_ENABLE_PIN = 22   # BCM pin: stepper enable (active LOW)
RPI_SOLENOID_PIN     = 18   # BCM pin: solenoid PWM (hardware PWM channel 0)
RPI_ESTOP_PIN        = 23   # BCM pin: E-stop button (NC, pulled HIGH)

# ADS1115 channel mapping
ADS_PRESSURE_CHANNEL = 0    # Channel A0: 4–20 mA pressure transducer
ADS_TEMP_CHANNEL     = 1    # Channel A1: thermocouple amplifier (0-5V → 0-100°C)

# Pressure transducer scaling (4–20 mA → 0–28 MPa via 250 Ω shunt = 1–5 V)
PT_VOLT_MIN  = 1.0
PT_VOLT_MAX  = 5.0
PT_PRESS_MIN = 0.0
PT_PRESS_MAX = 28.0

# Stepper motor: steps per full valve rotation, mechanical stops
VALVE_STEPS_PER_REV  = 200 * 16    # 200 step motor × 1/16 microstepping
VALVE_MAX_TURNS      = 5           # Full open = 5 turns from closed
VALVE_TOTAL_STEPS    = VALVE_STEPS_PER_REV * VALVE_MAX_TURNS

# ── ThingSpeak cloud monitoring ───────────────────────────────────────────────
THINGSPEAK_API_KEY     = "YOUR_API_KEY_HERE"    # Replace after account setup
THINGSPEAK_CHANNEL_ID  = 0                      # Replace after channel creation
THINGSPEAK_URL         = "https://api.thingspeak.com/update"
THINGSPEAK_INTERVAL_S  = 2.0   # Upload every 2 seconds (background thread)

# Field mapping (ThingSpeak fields 1–4)
# Field 1: pressure_MPa
# Field 2: temperature_C
# Field 3: setpoint_MPa
# Field 4: state_code  (0=IDLE, 1=PRESSURIZE, 2=HOLD, 3=DEPRESSURIZE)

# ── Data logging ──────────────────────────────────────────────────────────────
LOG_DIR = "logs"    # Relative to pressure_control/ directory
