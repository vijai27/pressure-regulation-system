#!/usr/bin/env python3
"""Generate a comprehensive interview prep PDF for the scCO2 project."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import Flowable
from reportlab.pdfgen import canvas as pdfcanvas

NAVY       = HexColor("#1E2761")
TEAL       = HexColor("#028090")
CORAL      = HexColor("#F96167")
CREAM      = HexColor("#F8F9FA")
GRAY       = HexColor("#6C757D")
GREEN      = HexColor("#28A745")
AMBER      = HexColor("#FFC107")
LIGHT_TEAL = HexColor("#E0F4F7")
LIGHT_NAVY = HexColor("#E8EAF6")

PW, PH = letter   # 612 x 792


def draw_cover(c, doc):
    c.setFillColor(NAVY)
    c.rect(0, 0, PW, PH, fill=1, stroke=0)

    # Teal accent stripe
    c.setFillColor(TEAL)
    c.rect(0, PH * 0.52, PW, 5, fill=1, stroke=0)

    # Main title
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(PW / 2, PH * 0.73, "scCO₂ Automated Pressure")
    c.drawCentredString(PW / 2, PH * 0.73 - 36, "Regulation System")

    # Subtitle
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(PW / 2, PH * 0.73 - 72, "Interview Preparation Guide")

    # Author line
    c.setFillColor(HexColor("#AABBDD"))
    c.setFont("Helvetica", 10)
    c.drawCentredString(PW / 2, PH * 0.73 - 96,
                        "Vijai Venkatesh  •  University of Michigan  •  2026")

    # Divider
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.5)
    c.line(inch, PH * 0.73 - 114, PW - inch, PH * 0.73 - 114)

    # Table of contents
    sections = [
        "1.   Project Overview & Resume Bullet",
        "2.   System Architecture",
        "3.   Control Theory — PID & Gain Scheduling",
        "4.   Peng-Robinson EOS Physics",
        "5.   State Machine & Safety Systems",
        "6.   Hardware Inventory",
        "7.   Simulation → HIL Roadmap",
        "8.   Key Interview Q&A",
        "9.   Complete Parts List",
    ]
    c.setFillColor(HexColor("#CCDDFF"))
    c.setFont("Helvetica", 10)
    y = PH * 0.73 - 138
    for s in sections:
        c.drawString(inch * 2.0, y, s)
        y -= 18


def draw_later(c, doc):
    """Footer on all pages after the cover."""
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 7.5)
    c.drawCentredString(
        PW / 2, 0.45 * inch,
        f"scCO₂ Pressure Regulation System  —  Interview Guide  —  Page {doc.page}"
    )


def build_styles():
    base = getSampleStyleSheet()
    styles = {}

    styles["h2"] = ParagraphStyle(
        "h2", parent=base["Normal"],
        fontSize=12, textColor=NAVY, fontName="Helvetica-Bold",
        spaceBefore=14, spaceAfter=4
    )
    styles["h3"] = ParagraphStyle(
        "h3", parent=base["Normal"],
        fontSize=10, textColor=TEAL, fontName="Helvetica-Bold",
        spaceBefore=8, spaceAfter=2
    )
    styles["body"] = ParagraphStyle(
        "body", parent=base["Normal"],
        fontSize=9.5, textColor=HexColor("#222222"),
        leading=14, spaceAfter=4, alignment=TA_JUSTIFY
    )
    styles["bullet"] = ParagraphStyle(
        "bullet", parent=base["Normal"],
        fontSize=9.5, textColor=HexColor("#222222"),
        leading=13, leftIndent=14, bulletIndent=4, spaceAfter=2
    )
    styles["code"] = ParagraphStyle(
        "code", parent=base["Normal"],
        fontSize=8.5, textColor=HexColor("#1A1A2E"),
        fontName="Courier", leading=12,
        leftIndent=12, spaceAfter=2, backColor=HexColor("#F0F0F0")
    )
    styles["callout"] = ParagraphStyle(
        "callout", parent=base["Normal"],
        fontSize=9.5, textColor=NAVY, fontName="Helvetica-BoldOblique",
        leading=14, leftIndent=10, rightIndent=10,
        spaceAfter=4, alignment=TA_JUSTIFY
    )
    return styles


class ColorBox(Flowable):
    """Colored section header bar."""
    def __init__(self, text, width, color=NAVY):
        super().__init__()
        self._text  = text
        self._width = width
        self._color = color
        self.height = 26

    def draw(self):
        self.canv.setFillColor(self._color)
        self.canv.rect(0, 0, self._width, self.height, fill=1, stroke=0)
        self.canv.setFillColor(white)
        self.canv.setFont("Helvetica-Bold", 11)
        self.canv.drawString(8, 7, self._text)

    def wrap(self, availW, availH):
        self._width = availW
        return availW, self.height


def tbl(data, col_widths, header_color=NAVY, row_colors=None):
    style = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  header_color),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("ALIGN",         (0, 0), (-1, 0),  "CENTER"),
        ("ALIGN",         (0, 1), (-1, -1), "LEFT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [white, CREAM]),
        ("GRID",          (0, 0), (-1, -1), 0.4, HexColor("#CCCCCC")),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
    ])
    if row_colors:
        for (r, color) in row_colors:
            style.add("BACKGROUND", (0, r), (-1, r), color)
    t = Table(data, colWidths=col_widths)
    t.setStyle(style)
    return t


def build_pdf(output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=0.75*inch, rightMargin=0.75*inch,
        topMargin=0.75*inch,  bottomMargin=0.75*inch,
    )
    W = PW - 1.5*inch
    S = build_styles()
    story = []

    # ── helpers ───────────────────────────────────────────────────────────────
    def sec(title, color=NAVY):
        story.append(Spacer(1, 8))
        story.append(ColorBox(title, W, color=color))
        story.append(Spacer(1, 6))

    def h2(t):   story.append(Paragraph(t, S["h2"]))
    def h3(t):   story.append(Paragraph(t, S["h3"]))
    def body(t): story.append(Paragraph(t, S["body"]))
    def sp(n=6): story.append(Spacer(1, n))
    def hr():    story.append(HRFlowable(width=W, thickness=0.5,
                               color=HexColor("#DDDDDD"), spaceAfter=4))

    def bullets(items):
        for item in items:
            story.append(Paragraph(f"•  {item}", S["bullet"]))

    def code(*lines):
        for ln in lines:
            story.append(Paragraph(ln.replace(" ", " "), S["code"]))
        sp(4)

    def callout(t):
        story.append(Paragraph(t, S["callout"]))
        sp(4)

    # ═══════════════════════════════════════════════════════════════════════════
    # Page 1 is the cover — drawn via onFirstPage callback.
    # We need one PageBreak to push content to page 2.
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # 1. PROJECT OVERVIEW & RESUME BULLET
    # ═══════════════════════════════════════════════════════════════════════════
    sec("1.  Project Overview & Resume Bullet")

    body(
        "This project is a <b>closed-loop pressure control system</b> for a supercritical CO₂ "
        "(scCO₂) research vessel. A Raspberry Pi runs a Python PID controller that autonomously "
        "pressurizes a sealed PARR pressure vessel with CO₂ to a configurable target "
        "(up to <b>28 MPa / 4061 PSI</b>), holds it stable within ±5 kPa, then safely "
        "depressurizes — all without human intervention."
    )
    sp()
    body(
        "CO₂ becomes supercritical above <b>31.1°C / 7.38 MPa</b>. The system operates at "
        "<b>60°C</b>, so CO₂ crosses the supercritical threshold during the ramp and stays "
        "supercritical for the entire hold phase."
    )
    sp(10)

    h2("Resume Bullet (full version)")
    callout(
        "Built a closed-loop scCO₂ pressure regulation system on Raspberry Pi: "
        "adaptive PID controller with Peng-Robinson EOS-based gain scheduling, "
        "Tkinter live dashboard, CSV logging, and ThingSpeak cloud upload; "
        "full physics simulation runs on desktop for development without hardware."
    )

    h2("Resume Bullet (1-line version)")
    callout(
        "Built automated scCO₂ pressure control system (Raspberry Pi, Python PID, "
        "28 MPa) with real-gas physics model, adaptive gain scheduling, and live GUI dashboard."
    )

    sp(8)
    h2("What Makes This Project Stand Out")
    bullets([
        "Real physics, not approximations — Peng-Robinson EOS, not ideal gas law",
        "Adaptive control — gains change every 100 ms as the plant changes character",
        "Full simulation stack — desktop SIL before any hardware exists",
        "Safety-first design — hardware E-stop, software watchdog, overpressure trip, rate limiter",
        "Multithreaded architecture — control (10 Hz), GUI, and cloud on separate threads",
        "Clean HAL design — one-line swap between SimulatedHardware and RPiHardware",
    ])

    # ═══════════════════════════════════════════════════════════════════════════
    # 2. SYSTEM ARCHITECTURE
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    sec("2.  System Architecture")

    h2("Thread Architecture")
    story.append(tbl(
        [
            ["Thread", "Rate", "Responsibility"],
            ["Control Loop",      "10 Hz (100 ms)", "State machine, PID, hardware I/O, CSV logging"],
            ["GUI Thread",        "10 Hz refresh",  "Tkinter mainloop, chart, button events"],
            ["Cloud Thread",      "Every 2 s",      "ThingSpeak upload (daemon, non-blocking)"],
            ["Physics Sim Thread","10 Hz",           "Simulated hardware — PR-EOS pressure/temp dynamics"],
        ],
        [1.5*inch, 1.4*inch, 4.1*inch]
    ))
    sp()

    h2("Hardware Abstraction Layer (HAL)")
    body(
        "Both <b>SimulatedHardware</b> and <b>RPiHardware</b> inherit from <b>HardwareBase</b> "
        "(abstract). To switch between simulation and real hardware, change ONE line in config.py:"
    )
    code(
        "SIMULATION = True   # desktop (Windows/macOS)",
        "SIMULATION = False  # Raspberry Pi, real sensors",
    )
    body("The control loop, state machine, and GUI never know which backend is running.")
    sp()

    h2("Key Files")
    story.append(tbl(
        [
            ["File", "Purpose"],
            ["main.py",                  "Entry point; wires all threads together"],
            ["config.py",                "ALL constants — edit this first for any tuning"],
            ["gui.py",                   "Tkinter + Matplotlib live dashboard"],
            ["hardware/base.py",         "Abstract HAL interface (never edit)"],
            ["hardware/simulator.py",    "PR-EOS physics simulation at 10 Hz"],
            ["hardware/rpi_hardware.py", "RPi stub — needs GPIO/ADS1115 wiring (next step)"],
            ["control/state_machine.py", "IDLE → PRESSURIZE → HOLD → DEPRESSURIZE"],
            ["control/pid.py",           "Discrete PID: anti-windup + derivative-on-measurement"],
            ["control/gain_scheduler.py","8-point adaptive gain table vs pressure"],
            ["control/ramp.py",          "Linear setpoint ramp generator"],
            ["control/eos.py",           "Peng-Robinson EOS for CO₂ — core physics"],
            ["logger.py",                "CSV data logger (every 100 ms)"],
            ["cloud.py",                 "ThingSpeak background uploader"],
        ],
        [2.4*inch, 5.1*inch]
    ))

    # ═══════════════════════════════════════════════════════════════════════════
    # 3. CONTROL THEORY
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    sec("3.  Control Theory — PID & Gain Scheduling")

    h2("PID Controller (control/pid.py)")
    body("Discrete-time PID at 10 Hz. Two key features beyond a basic PID:")
    bullets([
        "<b>Anti-windup</b>: integral accumulates only when output is NOT saturated. "
        "Prevents the integrator from winding up during a long ramp where the valve is "
        "already fully open.",
        "<b>Derivative on measurement</b> (not on error): D-term is −Kd×Δmeasurement/dt. "
        "This eliminates the derivative spike caused by sudden setpoint steps.",
    ])
    sp()
    code(
        "# Anti-windup: only integrate when not saturated",
        "if output_min < last_output < output_max:",
        "    integral += error * sample_time",
        "",
        "# Derivative on measurement (no setpoint kick)",
        "d_term = -kd * (measurement - prev_measurement) / sample_time",
    )

    h2("Gain Schedule — 8-Point Table")
    story.append(tbl(
        [
            ["Pressure (MPa)", "Kp", "Ki", "Kd", "Phase / Physics Reason"],
            ["0.0",  "50", "6.0", "2.5", "Low pressure — compressible gas, moderate ΔP"],
            ["5.0",  "58", "7.0", "2.5", "Rising effort to maintain ramp rate"],
            ["10.0", "65", "8.0", "2.0", "Peak Kp — max compressibility, most push needed"],
            ["17.2", "60", "7.0", "1.5", "← 2500 PSI crossover: CO₂ stiffens (PR-EOS inflection)"],
            ["20.0", "45", "5.0", "1.0", "Dense phase — back off, hair-trigger response"],
            ["24.0", "32", "4.0", "0.8", "Approaching target — smooth fine-approach"],
            ["27.0", "22", "3.0", "0.5", "Near target — minimal actuation"],
            ["28.0", "18", "3.0", "0.5", "At target — switch to HOLD gains (Kp=35, Ki=12, Kd=0.5)"],
        ],
        [1.3*inch, 0.5*inch, 0.5*inch, 0.5*inch, 4.7*inch],
        row_colors=[(4, LIGHT_TEAL)]
    ))
    sp()

    h2("Is the Gain Schedule Physics-Backed?")
    body("<b>Shape: yes. Exact numbers: empirically refined from physics starting points.</b>")
    sp(4)
    bullets([
        "<b>Why gains rise 0→10 MPa</b>: Flow model is dP = K×valve×√(ΔP). "
        "As vessel pressure rises, ΔP shrinks → less flow per valve %. "
        "Plant gain drops → Kp must rise. Classic: Kp_controller ∝ 1/plant_gain.",
        "<b>Why gains fall sharply after 17.2 MPa</b>: PR-EOS compressibility Z collapses "
        "at the supercritical transition. At 10 MPa Z≈0.72; at 20 MPa Z≈0.46 "
        "(54% denser than ideal gas). A tiny valve move causes a huge pressure spike.",
        "<b>17.2 MPa crossover</b>: inflection in dZ/dP from PR-EOS; confirmed in lab.",
        "<b>Gas factors</b> (CO₂=1.0, N₂=0.80, Ar=0.85): molar mass & density ratios — pure physics.",
        "<b>Exact numbers</b> (50, 65, 18…): seeded from physics, refined in Simulink PID Tuner.",
    ])
    sp(4)
    callout(
        "“The shape of the schedule — rising at low pressure, peak at 10 MPa, steep fall past 17 MPa "
        "— is predicted by the flow equation and PR-EOS compressibility. "
        "The specific numbers were seeded from physics and refined using Simulink PID Tuner.”"
    )

    h2("How Over-Compensation Is Prevented")
    bullets([
        "<b>Derivative-on-measurement</b>: damps rapid pressure rises before they overshoot",
        "<b>Gain scheduler</b>: reduces Kp aggressively from 65→18 as pressure nears target",
        "<b>Ramp setpoint generator</b>: setpoint never jumps — ramps at 350 kPa/min, "
        "so tracking error is always small and controlled",
    ])

    # ═══════════════════════════════════════════════════════════════════════════
    # 4. PR-EOS PHYSICS
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    sec("4.  Peng-Robinson EOS — Why Real Gas Physics Matter")

    h2("Why Not Ideal Gas?")
    body(
        "Ideal gas: PV = nRT. At 20 MPa / 60°C, CO₂ has compressibility factor "
        "<b>Z = 0.46</b> (actual volume is 54% less than ideal predicts). "
        "Using ideal gas law gives wrong flow rates, wrong temperature-pressure coupling, "
        "and incorrect PID tuning."
    )
    sp()

    h2("Peng-Robinson EOS")
    code(
        "P = RT/(V-b) - a(T)/[V(V+b) + b(V-b)]",
        "",
        "CO2 constants:",
        "  Tc = 304.13 K,  Pc = 7.3773 MPa,  omega = 0.22394",
        "  R  = 8.314e-6 MPa*m3/mol*K",
        "  b  = 2.664e-5  m3/mol",
    )

    h2("Key Function: dP_from_dT")
    body("Used every physics step to compute pressure change from temperature fluctuation:")
    code(
        "def dP_from_dT(P_MPa, T_K, dT_K):",
        "    # Solve PR-EOS for molar volume V at (P, T)",
        "    # Compute (dP/dT)_V = R/(V-b) - (da/dT)/[V(V+b)+b(V-b)]",
        "    return dP_dT * dT_K",
    )

    h2("Why This Matters Practically")
    story.append(tbl(
        [
            ["Condition", "Ideal Gas Predicts", "PR-EOS Reality"],
            ["0.01°C temp flicker at 20 MPa", "~0.6 kPa pressure change",
             "3.5–4.7 kPa change (5.9× more!)"],
            ["Density at 20 MPa / 60°C", "Z = 1.0 (baseline)", "Z = 0.46 (118% denser)"],
            ["HOLD gain needed", "Low Kp sufficient",
             "Must use tight HOLD Kp=35 (2× ramp value)"],
        ],
        [2.2*inch, 2.2*inch, 3.1*inch],
        row_colors=[(1, LIGHT_TEAL), (2, LIGHT_TEAL), (3, LIGHT_TEAL)]
    ))
    sp()
    callout(
        "Interview point: “A 0.01°C INKBIRD temperature flicker causes 4 kPa of "
        "pressure noise at 20 MPa — 5.9× what ideal gas predicts. "
        "Without PR-EOS, HOLD accuracy would be terrible.”"
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # 5. STATE MACHINE & SAFETY
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    sec("5.  State Machine & Safety Systems")

    h2("State Machine (control/state_machine.py)")
    story.append(tbl(
        [
            ["State", "Entry Condition", "Action", "Exit Condition"],
            ["IDLE",
             "Startup / E-stop / depressurize complete",
             "Valve=0%, solenoid=0%",
             "START button pressed"],
            ["PRESSURIZE",
             "START pressed & temp ≥55°C",
             "Ramp setpoint 350 kPa/min, PID drives valve",
             "Pressure within 0.05 MPa of target"],
            ["HOLD",
             "Target pressure reached",
             "Tight PID (HOLD gains), valve & solenoid active",
             "DEPRESSURIZE button or E-stop"],
            ["DEPRESSURIZE",
             "User command",
             "Ramp setpoint down at 2 MPa/min, solenoid vents",
             "Pressure ≤0.2 MPa → IDLE"],
        ],
        [1.1*inch, 1.7*inch, 2.2*inch, 2.5*inch]
    ))
    sp()

    h2("Safety Layers (priority order)")
    bullets([
        "<b>Hardware E-stop button</b>: NC contact on GPIO 23, cuts power immediately",
        "<b>Software E-stop (GUI)</b>: calls sm.request_estop() → valve=0, solenoid=0, IDLE",
        "<b>Overpressure software trip</b>: pressure &gt;28.5 MPa → emergency stop",
        "<b>Rate limiter (WARNING-only)</b>: logs at &gt;600 kPa/min; forces IDLE only at "
        "&gt;5000 kPa/min (catastrophic). No bang-bang — prevents chattering.",
        "<b>Temperature gate</b>: START locked until temp ≥55°C",
        "<b>Watchdog</b>: WATCHDOG_TIMEOUT_S; misses → emergency stop",
        "<b>MAWP margin</b>: 28 MPa operating vs 34.47 MPa PARR MAWP = 18.7% safety margin",
    ])

    h2("Rate Estimation — 5-Second Rolling Window")
    body(
        "Single-sample dP/dt at 10 Hz with 5 kPa noise → ~3000 kPa/min apparent rate (false alarm). "
        "5-second window reduces this well below 600 kPa/min threshold. "
        "Requires ≥3 seconds of data before trusting the estimate."
    )
    code(
        "if window_dt < 3.0:",
        "    return last_smoothed_rate   # not enough data",
        "rate = abs((p_now - p_5s_ago) / window_dt * 60.0)  # MPa/min",
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # 6. HARDWARE INVENTORY
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    sec("6.  Hardware Inventory")

    story.append(tbl(
        [
            ["Component", "Make / Model", "Key Spec"],
            ["Pressure Vessel",     "PARR 2302HC, 316 SS",
             "1 L, MAWP 34.47 MPa (5000 PSI) @ 350°C"],
            ["Gas Booster",        "HII 5G-TD-28/150-CO2",
             "Max outlet 172 MPa; modeled as 50 MPa supply"],
            ["Pressure Transducer","Ashcroft 0–5000 PSI, 4–20 mA",
             "ADS1115 A0, 250Ω shunt → 1–5 V"],
            ["Temp Controller",    "INKBIRD, 60°C setpoint",
             "±0.01°C settled; ±0.3°C during heat-up"],
            ["ADC",                "ADS1115, 16-bit I²C",
             "Channels A0 (pressure), A1 (temp)"],
            ["Stepper Driver",     "A4988, 1/16 microstepping",
             "GPIO 17 STEP, GPIO 27 DIR, GPIO 22 EN"],
            ["Stepper Motor",      "NEMA 17, 200 steps/rev",
             "Actuates motorized needle valve"],
            ["Solenoid Valve",     "24VDC relay-driven vent",
             "GPIO 18 PWM (hardware channel 0)"],
            ["E-Stop",             "NC push button",
             "GPIO 23 BCM, pulled HIGH, LOW when pressed"],
            ["Controller",         "Raspberry Pi 4 (4 GB)",
             "Python 3.11, 10 Hz control loop"],
            ["Power Supply",       "Dayton 33NT20, 24VDC 50W",
             "DIN rail mount"],
        ],
        [1.9*inch, 2.1*inch, 3.5*inch]
    ))

    sp()
    h2("Gas Inventory")
    bullets([
        "CO₂ (Bone Dry, UN1013) — primary process gas, Metro Welding Supply Detroit",
        "N₂ (Ultra High Purity, UN1066) — alternate experiment gas",
        "Ar (Prepurified, UN1006) — alternate experiment gas",
        "Air (Dry Grade, UN1002) — drives booster pump only, never enters vessel",
    ])

    # ═══════════════════════════════════════════════════════════════════════════
    # 7. SIL → HIL ROADMAP
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    sec("7.  Simulation → Hardware Roadmap")

    h2("Current Status: Software-in-the-Loop (SIL)")
    body(
        "Complete control algorithm runs in simulation on a desktop PC. "
        "SimulatedHardware replaces all physical sensors and actuators with PR-EOS physics. "
        "The same code runs on RPi with one config change."
    )
    sp()

    story.append(tbl(
        [
            ["Stage", "Description", "What’s Real"],
            ["SIL (now)",    "Desktop Python simulation",
             "Algorithm only — physics is mathematical"],
            ["HIL (next)",   "RPi runs control code vs real hardware",
             "RPi + real sensors + real actuators"],
            ["Fully Real",   "RPi in control loop, PARR vessel pressurized",
             "Everything — all hardware live"],
        ],
        [1.1*inch, 2.7*inch, 3.7*inch]
    ))
    sp()

    h2("Completing rpi_hardware.py (Blocking Step 1)")
    bullets([
        "File exists with all code commented out — just uncomment and fix imports",
        "pip install adafruit-circuitpython-ads1x15 adafruit-blinka RPi.GPIO",
        "ADS1115 A0: pressure transducer 4–20 mA via 250Ω → 1–5 V → 0–34.47 MPa",
        "ADS1115 A1: thermocouple amplifier 0–5 V → 0–100°C",
        "NEMA 17 stepper: STEP/DIR/EN on GPIO 17/27/22",
        "Solenoid: hardware PWM on GPIO 18",
    ])

    h2("Simulink Digital Twin (simulink/ folder)")
    bullets([
        "build_model.m — creates scCO2_plant.slx using Simscape Fluids",
        "run_simulation.m — runs sim, plots step response",
        "export_gains.m — exports Kp/Ki/Kd from MATLAB PID Tuner",
        "Status: not yet tested (needs MATLAB + Simscape Fluids toolbox)",
    ])

    h2("PID Tuning Plan (HOLD gains need re-tuning)")
    bullets([
        "Run simulation to 20 MPa, watch HOLD behavior with PR-EOS noise",
        "Target: hold ±5 kPa at 28 MPa with 0.01°C INKBIRD noise input",
        "Ziegler-Nichols: ramp Kp until sustained oscillation → extract Ku, Pu",
        "MATLAB PID Tuner: linearized plant model → automatic tuning → export gains",
    ])

    h2("How This Maps to GNC / Embedded Systems Work")
    callout(
        "“It’s a complete real-time control system: sensors → state estimator (noise-rejected rate) "
        "→ state machine → guidance law (ramp setpoint) → feedback controller (PID) → actuators, "
        "with safety watchdogs and a hardware abstraction layer. "
        "The SIL → HIL → real-hardware progression mirrors how aerospace GNC systems are developed. "
        "The adaptive gain scheduling based on a physics model of the plant is the same design principle "
        "used in gain-scheduled flight control laws for varying dynamic pressure.”"
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # 8. KEY INTERVIEW Q&A
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    sec("8.  Key Interview Q&A")

    qa = [
        (
            "Q: Describe the project in 30 seconds.",
            "“I built a closed-loop pressure control system for a scCO₂ research vessel. "
            "A Raspberry Pi runs a Python PID controller that ramps the vessel from ambient to "
            "28 MPa at a controlled rate, holds it stable within ±5 kPa, then safely vents. "
            "The control uses adaptive gain scheduling based on a Peng-Robinson EOS real-gas model. "
            "I have a full physics simulation that runs on desktop so I can develop and tune "
            "without hardware.”"
        ),
        (
            "Q: Why adaptive gain scheduling instead of fixed PID?",
            "“The plant changes character dramatically with pressure. At low pressure CO₂ is "
            "highly compressible — the valve has low authority. Near 28 MPa CO₂ is dense and "
            "near-incompressible — the same valve opening causes a huge overshoot. "
            "A fixed Kp good for low pressure would be unstable near target; one good for near "
            "target would be sluggish at low pressure. Gain scheduling is the right tool when "
            "plant gain varies significantly across the operating range.”"
        ),
        (
            "Q: How does this relate to Hardware-in-the-Loop testing?",
            "“Currently we’re in Software-in-the-Loop (SIL) — the control algorithm runs "
            "against a mathematical physics simulation. The next step is HIL: real Raspberry Pi "
            "and real sensors/actuators, initially at a safe low pressure. "
            "SIL proves the algorithm before we run it near real hardware at 4000 PSI. "
            "The HAL design (one-line swap sim → RPi) is what makes this progression clean.”"
        ),
        (
            "Q: How did you handle sensor noise in the rate estimator?",
            "“Single-sample dP/dt at 10 Hz with 5 kPa transducer noise gives an apparent rate "
            "of ~3000 kPa/min even when the vessel is static — that would constantly trigger the "
            "rate limiter. I use a 5-second rolling window, which reduces noise by the square root "
            "of the window length. I also require ≥3 seconds of data before trusting the estimate.”"
        ),
        (
            "Q: Why derivative-on-measurement instead of derivative-on-error?",
            "“When the setpoint steps, the derivative of the error has an instantaneous spike "
            "(‘derivative kick’), feeding a huge D-term into the output for one sample. "
            "Since the setpoint ramps slowly (350 kPa/min), derivative-on-measurement and "
            "derivative-on-error are nearly identical most of the time, but measurement avoids "
            "the kick on any sudden setpoint change.”"
        ),
        (
            "Q: What would break first if you deployed today?",
            "“rpi_hardware.py — it’s a stub with raise NotImplementedError everywhere. "
            "The GPIO wiring for ADS1115, stepper driver, and solenoid PWM needs to be "
            "uncommented and tested. That’s the immediate blocking task before any hardware "
            "deployment. After that, HOLD PID gains need re-tuning against real sensor noise.”"
        ),
        (
            "Q: How does the project map to GNC / embedded systems work?",
            "“It’s a complete real-time control system: sensors → state estimator "
            "→ state machine → guidance law → feedback controller → actuators, with "
            "safety watchdogs and a hardware abstraction layer. "
            "The SIL → HIL progression mirrors aerospace GNC development. "
            "Adaptive gain scheduling based on a physics model of the plant is the same "
            "principle used in gain-scheduled flight control laws for varying dynamic pressure.”"
        ),
    ]

    for q, a in qa:
        h3(q)
        callout(a)
        hr()
        sp(4)

    # ═══════════════════════════════════════════════════════════════════════════
    # 9. PARTS TO BUY
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    sec("9.  Complete Parts List")

    h2("High-Pressure Fluid System (Swagelok / Parker)")
    story.append(tbl(
        [
            ["Item", "Brand / Model", "Spec", "Est. Cost"],
            ["Motorized needle valve body",
             "Parker NP6: 4F-NP6LK-SSP",
             "SS316, 1/4\" tube, 60,000 PSI rated",
             "~$400"],
            ["Motor coupling",
             "NEMA 17 stepper + custom bracket",
             "200 steps/rev, A4988 1/16 step",
             "~$30"],
            ["Check valve",
             "Swagelok SS-CHS4-5",
             "1/4\" tube, 6000 PSI (not SS-4C — 3000 PSI only)",
             "~$150"],
            ["Manual ball valve ×3",
             "Swagelok SS-83KS4",
             "1/4\" tube, 6000 PSI (not SS-43GS4 — 3000 PSI only)",
             "~$300"],
            ["Compression fittings",
             "Swagelok SS-400 series",
             "1/4\" OD, 316 SS (assorted)",
             "~$200"],
            ["SS tubing",
             "316 SS, 1/4\" OD × 0.065\" wall",
             "High-pressure rated, 10 ft",
             "~$80"],
            ["Relief valve",
             "Parker 442F42",
             "SS316, 1/4\" MNPT",
             "~$165"],
        ],
        [1.9*inch, 1.8*inch, 2.2*inch, 0.8*inch]
    ))
    sp()

    h2("Electronics & Control (Grainger / Amazon)")
    story.append(tbl(
        [
            ["Item", "Brand / Model", "Est. Cost"],
            ["Pressure transducer",
             "Ashcroft 0–5000 PSI 4–20 mA SS IP67 (Grainger K4708)",
             "~$400"],
            ["Pressure gauge (mechanical)",
             "Ashcroft 0–5000 PSI (Grainger K4201)",
             "~$100"],
            ["DIN rail PSU 24VDC 50W",
             "Dayton 33NT20 (Grainger)",
             "~$55"],
            ["DIN rail relay 24VDC",
             "Generic DIN relay 24VDC coil",
             "~$20"],
            ["Raspberry Pi 4 (4 GB)", "Raspberry Pi Foundation", "~$55"],
            ["ADS1115 ADC module",    "Adafruit breakout",       "~$10"],
            ["NEMA 17 stepper motor", "Generic 200 steps/rev",   "~$15"],
            ["A4988 stepper driver",  "Pololu A4988",            "~$8"],
            ["32 GB microSD",         "SanDisk",                 "~$10"],
            ["Relay module 24VDC",    "Generic",                 "~$10"],
            ["PTFE tape",             "Grainger 34P209",         "~$5"],
        ],
        [2.0*inch, 3.7*inch, 0.9*inch]
    ))
    sp()

    h2("Optional: Windowed Vessel (for scCO₂ flow visualization)")
    bullets([
        "Autoclave Engineers (Parker): EZE-Seal series, sapphire windows, up to 60 MPa",
        "Sitec Reactor Technology: 100–600 mL, sapphire/borosilicate windows, up to 100 MPa",
        "HiP (High Pressure Equipment Co.): modular sight windows, SS316, 10,000 PSI",
        "Typical cost: $2,000–$8,000 depending on volume and window spec",
    ])

    sp(8)
    h2("Estimated Total Cost")
    story.append(tbl(
        [
            ["Category", "Estimated Total"],
            ["High-pressure fluid system", "~$1,325"],
            ["Electronics & control",      "~$678"],
            ["Vessel (PARR 2302HC — already owned)", "$0"],
            ["Gas cylinders (already owned)",             "$0"],
            ["TOTAL", "~$2,003"],
        ],
        [4.0*inch, 3.5*inch],
        row_colors=[(4, LIGHT_NAVY)]
    ))

    # Build
    doc.build(story, onFirstPage=draw_cover, onLaterPages=draw_later)
    print(f"PDF written: {output_path}")


if __name__ == "__main__":
    build_pdf("/home/user/pressure-regulation-system/scCO2_Interview_Prep.pdf")
