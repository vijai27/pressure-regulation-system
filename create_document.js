const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, TableOfContents, LevelFormat,
  ExternalHyperlink
} = require("C:/Users/Vijai Venkatesh/AppData/Roaming/npm/node_modules/docx");

// Colors
const NAVY  = "1E2761";
const TEAL  = "028090";
const CORAL = "F96167";
const WHITE = "FFFFFF";
const LIGHT_NAVY = "2A3A8C";

const CELL_BORDER = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const CELL_BORDERS = { top: CELL_BORDER, bottom: CELL_BORDER, left: CELL_BORDER, right: CELL_BORDER };
const HEADER_BORDER = { style: BorderStyle.SINGLE, size: 1, color: "1E2761" };
const HEADER_BORDERS = { top: HEADER_BORDER, bottom: HEADER_BORDER, left: HEADER_BORDER, right: HEADER_BORDER };
const CELL_MARGINS = { top: 80, bottom: 80, left: 120, right: 120 };

function hCell(text, width) {
  return new TableCell({
    borders: HEADER_BORDERS,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: NAVY, type: ShadingType.CLEAR },
    margins: CELL_MARGINS,
    children: [new Paragraph({
      children: [new TextRun({ text, bold: true, color: WHITE, font: "Calibri", size: 20 })]
    })]
  });
}

function dCell(text, width, shade) {
  return new TableCell({
    borders: CELL_BORDERS,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: shade || "F8F8F8", type: ShadingType.CLEAR },
    margins: CELL_MARGINS,
    children: [new Paragraph({
      children: [new TextRun({ text, font: "Calibri", size: 20 })]
    })]
  });
}

function monoCell(text, width) {
  return new TableCell({
    borders: CELL_BORDERS,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: "F0F4F8", type: ShadingType.CLEAR },
    margins: CELL_MARGINS,
    children: [new Paragraph({
      children: [new TextRun({ text, font: "Consolas", size: 18 })]
    })]
  });
}

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 120 },
    children: [new TextRun({ text, bold: true, color: NAVY, font: "Calibri", size: 32 })]
  });
}

function h2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 80 },
    children: [new TextRun({ text, bold: true, color: TEAL, font: "Calibri", size: 26 })]
  });
}

function body(text, opts = {}) {
  return new Paragraph({
    spacing: { before: 80, after: 80 },
    children: [new TextRun({ text, font: "Calibri", size: 22, ...opts })]
  });
}

function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, font: "Calibri", size: 22 })]
  });
}

function numbered(text) {
  return new Paragraph({
    numbering: { reference: "steps", level: 0 },
    spacing: { before: 40, after: 40 },
    children: [new TextRun({ text, font: "Calibri", size: 22 })]
  });
}

function callout(text, color) {
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    border: {
      left: { style: BorderStyle.SINGLE, size: 18, color: color || TEAL, space: 10 }
    },
    shading: { fill: "EEF6F8", type: ShadingType.CLEAR },
    indent: { left: 200 },
    children: [new TextRun({ text, bold: true, color: color || TEAL, font: "Calibri", size: 22 })]
  });
}

function divider() {
  return new Paragraph({
    spacing: { before: 120, after: 120 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 1 } },
    children: []
  });
}

function emptyLine() {
  return new Paragraph({ spacing: { before: 40, after: 40 }, children: [] });
}

// ─── TABLES ───────────────────────────────────────────────────────────────────

function specsTable() {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [3600, 5760],
    rows: [
      new TableRow({ children: [hCell("Parameter", 3600), hCell("Value", 5760)] }),
      new TableRow({ children: [dCell("Maximum Pressure", 3600), dCell("28 MPa (4,000 psi)", 5760)] }),
      new TableRow({ children: [dCell("Operating Temperature", 3600, "FFFFFF"), dCell("60°C (above CO2 critical point)", 5760, "FFFFFF")] }),
      new TableRow({ children: [dCell("Pressurization Rate", 3600), dCell("350 kPa/min (constant, ±5–10%)", 5760)] }),
      new TableRow({ children: [dCell("Depressurization Rate", 3600, "FFFFFF"), dCell("2 MPa/min (constant)", 5760, "FFFFFF")] }),
      new TableRow({ children: [dCell("Hold Accuracy", 3600), dCell("±1–2%", 5760)] }),
      new TableRow({ children: [dCell("Software Cost", 3600, "FFFFFF"), dCell("$0 (Python open source + UMich MATLAB license)", 5760, "FFFFFF")] }),
      new TableRow({ children: [dCell("Implementation Timeline", 3600), dCell("4–6 weeks (parallel with hardware procurement)", 5760)] }),
    ]
  });
}

function pidTable() {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2400, 2400, 4560],
    rows: [
      new TableRow({ children: [hCell("Parameter", 2400), hCell("Initial Value", 2400), hCell("Tuning Direction", 4560)] }),
      new TableRow({ children: [dCell("Kp", 2400), dCell("0.5", 2400), dCell("Increase if sluggish, decrease if oscillating", 4560)] }),
      new TableRow({ children: [dCell("Ki", 2400, "FFFFFF"), dCell("0.1", 2400, "FFFFFF"), dCell("Disable during ramps, enable for hold mode", 4560, "FFFFFF")] }),
      new TableRow({ children: [dCell("Kd", 2400), dCell("0.05", 2400), dCell("Reduce if response is noisy", 4560)] }),
      new TableRow({ children: [dCell("Sample Time", 2400, "FFFFFF"), dCell("100 ms", 2400, "FFFFFF"), dCell("Fixed (10 Hz control loop)", 4560, "FFFFFF")] }),
    ]
  });
}

function modulesTable() {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2800, 6560],
    rows: [
      new TableRow({ children: [hCell("Module", 2800), hCell("Purpose", 6560)] }),
      ...([
        ["main.py", "Entry point — select sim vs. real hardware, start all threads"],
        ["config.py", "All constants: pressures, rates, PID gains, GPIO pin numbers"],
        ["hardware/base.py", "Abstract HAL interface definition"],
        ["hardware/simulator.py", "Simulated hardware with physics model (Windows)"],
        ["hardware/rpi_hardware.py", "Real RPi hardware (ADS1115, TB6600, SSR)"],
        ["control/pid.py", "PID controller class"],
        ["control/ramp.py", "Linear ramp setpoint generator"],
        ["control/state_machine.py", "State machine: IDLE→PRESSURIZE→HOLD→DEPRESSURIZE"],
        ["logger.py", "CSV data logging every 100 ms"],
        ["cloud.py", "ThingSpeak HTTP upload every 2 seconds (background thread)"],
        ["gui.py", "Tkinter GUI with live matplotlib pressure/temperature chart"],
      ]).map(([mod, desc], i) => new TableRow({
        children: [monoCell(mod, 2800), dCell(desc, 6560, i % 2 === 0 ? "F8F8F8" : "FFFFFF")]
      }))
    ]
  });
}

function safetyTable() {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [2200, 3560, 3600],
    rows: [
      new TableRow({ children: [hCell("Interlock", 2200), hCell("Condition", 3560), hCell("Action", 3600)] }),
      new TableRow({ children: [dCell("Pressure limit", 2200), dCell("Measured pressure > 28 MPa", 3560), dCell("Go to IDLE, disable all outputs", 3600)] }),
      new TableRow({ children: [dCell("Rate limit", 2200, "FFFFFF"), dCell("Calculated dP/dt > 600 kPa/min", 3560, "FFFFFF"), dCell("Reduce valve opening immediately", 3600, "FFFFFF")] }),
      new TableRow({ children: [dCell("Watchdog timer", 2200), dCell("Control loop stalls > 1 second", 3560), dCell("Go to IDLE, disable all outputs", 3600)] }),
      new TableRow({ children: [dCell("Temperature check", 2200, "FFFFFF"), dCell("Temperature < 55°C at START", 3560, "FFFFFF"), dCell("Block START button", 3600, "FFFFFF")] }),
      new TableRow({ children: [dCell("Startup validation", 2200), dCell("Pressure reading invalid/out of range", 3560), dCell("Block START button", 3600)] }),
    ]
  });
}

function timelineTable() {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [1440, 2160, 3960, 1800],
    rows: [
      new TableRow({ children: [hCell("Week", 1440), hCell("Phase", 2160), hCell("Key Tasks", 3960), hCell("Deliverable", 1800)] }),
      new TableRow({ children: [dCell("1–2", 1440), dCell("Phase 1: Simulink", 2160), dCell("Build Simscape plant model; tune PID; validate ramp rates", 3960), dCell("Validated Kp, Ki, Kd values", 1800)] }),
      new TableRow({ children: [dCell("3–4", 1440, "FFFFFF"), dCell("Phase 2: Python App", 2160, "FFFFFF"), dCell("Build HAL, PID, state machine, GUI, logging, cloud", 3960, "FFFFFF"), dCell("Full Python app in simulation mode", 1800, "FFFFFF")] }),
      new TableRow({ children: [dCell("5", 1440), dCell("Integration Testing", 2160), dCell("End-to-end Windows simulation test; safety interlock testing", 3960), dCell("Validated software on Windows", 1800)] }),
      new TableRow({ children: [dCell("On hardware arrival", 1440, "FFFFFF"), dCell("RPi Deployment", 2160, "FFFFFF"), dCell("Wire RPiHardware module; N2 test; CO2 commissioning", 3960, "FFFFFF"), dCell("System operational", 1800, "FFFFFF")] }),
    ]
  });
}

// ─── DOCUMENT ─────────────────────────────────────────────────────────────────

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
      {
        reference: "steps",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      }
    ]
  },
  styles: {
    default: {
      document: { run: { font: "Calibri", size: 22 } }
    },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, color: NAVY, font: "Calibri" },
        paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, color: TEAL, font: "Calibri" },
        paragraph: { spacing: { before: 240, after: 80 }, outlineLevel: 1 }
      }
    ]
  },
  sections: [
    // ── Cover page ──────────────────────────────────────────────────────────
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      children: [
        emptyLine(), emptyLine(), emptyLine(),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 720, after: 120 },
          children: [new TextRun({ text: "scCO\u2082 PRESSURE CONTROL SYSTEM", bold: true, color: NAVY, font: "Calibri", size: 52 })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 60, after: 60 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: TEAL, space: 1 } },
          children: [new TextRun({ text: "Software Implementation Plan", bold: false, color: TEAL, font: "Calibri", size: 32 })]
        }),
        emptyLine(),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 40, after: 40 },
          children: [new TextRun({ text: "Automated Pressurization & Depressurization Rate Control", color: "475569", font: "Calibri", size: 24 })]
        }),
        emptyLine(), emptyLine(), emptyLine(), emptyLine(),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 40, after: 40 },
          children: [new TextRun({ text: "Taub Research Group", bold: true, color: NAVY, font: "Calibri", size: 24 })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 40, after: 40 },
          children: [new TextRun({ text: "University of Michigan | Materials Science & Engineering", color: "475569", font: "Calibri", size: 22 })]
        }),
        emptyLine(),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 40, after: 40 },
          children: [
            new TextRun({ text: "Advisor: ", bold: true, color: "475569", font: "Calibri", size: 22 }),
            new TextRun({ text: "Dandan Zhang (zdandan@umich.edu)", color: "475569", font: "Calibri", size: 22 })
          ]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          spacing: { before: 40, after: 40 },
          children: [
            new TextRun({ text: "Version: 1.0  |  Date: March 2026", color: "475569", font: "Calibri", size: 22 })
          ]
        }),
        // Page break before TOC
        new Paragraph({ children: [new TextRun({ break: 1 })] })
      ]
    },
    // ── Main content ────────────────────────────────────────────────────────
    {
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      headers: {
        default: new Header({
          children: [new Paragraph({
            border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: NAVY, space: 1 } },
            children: [
              new TextRun({ text: "scCO\u2082 Pressure Control System \u2014 Software Implementation Plan", color: NAVY, font: "Calibri", size: 18, bold: true }),
              new TextRun({ text: "\t\t", font: "Calibri", size: 18 }),
              new TextRun({ text: "Taub Research Group | UMich MSE", color: "888888", font: "Calibri", size: 18 })
            ],
            tabStops: [{ type: "right", position: 9360 }]
          })]
        })
      },
      footers: {
        default: new Footer({
          children: [new Paragraph({
            border: { top: { style: BorderStyle.SINGLE, size: 4, color: NAVY, space: 1 } },
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: "Page ", color: "888888", font: "Calibri", size: 18 }),
              new TextRun({ children: [PageNumber.CURRENT], color: "888888", font: "Calibri", size: 18 }),
              new TextRun({ text: " | March 2026 | Version 1.0 | Confidential", color: "888888", font: "Calibri", size: 18 })
            ]
          })]
        })
      },
      children: [
        // TOC
        new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "Table of Contents", bold: true, color: NAVY, font: "Calibri", size: 32 })] }),
        new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-2" }),
        new Paragraph({ children: [new TextRun({ break: 1 })] }),

        // ── SECTION 1: Executive Summary ──────────────────────────────────
        h1("1.  Executive Summary"),
        body("This document describes the software implementation plan for an automated pressure control system for a supercritical CO\u2082 (scCO\u2082) research vessel in the Taub Research Group at the University of Michigan. The current system uses fully manual pressure control with no rate regulation, no data logging, and no automated safety protection."),
        emptyLine(),
        body("The proposed software solution consists of two phases:"),
        bullet("Phase 1: A Simulink + Simscape digital twin for PID tuning and validation before hardware arrives"),
        bullet("Phase 2: A Python control application for Raspberry Pi deployment with simulation mode for Windows testing"),
        emptyLine(),
        h2("Key Specifications"),
        emptyLine(),
        specsTable(),
        emptyLine(),

        // ── SECTION 2: Problem Statement ──────────────────────────────────
        h1("2.  Problem Statement"),
        body("The current system has four critical deficiencies:"),
        emptyLine(),
        h2("2.1  No Rate Control"),
        body("Pressurization and depressurization rates vary unpredictably based on manual valve adjustment. This makes experiments irreproducible \u2014 the rate experienced by a sample depends on how quickly an operator turns a valve."),
        emptyLine(),
        h2("2.2  Operator Dependency"),
        body("Results vary based on who runs the experiment. There is no mechanism to ensure consistent procedure between operators or between sessions."),
        emptyLine(),
        h2("2.3  No Data Logging"),
        body("Pressure vs. time data must be recorded manually or not at all. This is error-prone and makes it impossible to correlate pressure history with experimental outcomes."),
        emptyLine(),
        h2("2.4  Safety Deficiencies"),
        body("There is no automated overpressure protection, no emergency stop, and no controlled depressurization \u2014 all of which present safety risks at 28 MPa operating pressure."),
        emptyLine(),
        callout("Research Requirement: Constant, reproducible pressurization rate of 350 kPa/min and depressurization rate of 2 MPa/min.", NAVY),

        // ── SECTION 3: Proposed Solution Overview ─────────────────────────
        h1("3.  Proposed Solution Overview"),
        emptyLine(),
        h2("3.1  Two-Phase Strategy"),
        new Paragraph({
          spacing: { before: 80, after: 80 },
          children: [new TextRun({ text: "Phase 1 \u2014 Simulink Digital Twin (Weeks 1\u20132)", bold: true, color: TEAL, font: "Calibri", size: 22 })]
        }),
        body("Build a validated physics model of the complete system in MATLAB Simulink + Simscape. This allows PID tuning and validation of control algorithms before hardware arrives, eliminating risk and reducing commissioning time."),
        emptyLine(),
        new Paragraph({
          spacing: { before: 80, after: 80 },
          children: [new TextRun({ text: "Phase 2 \u2014 Python Control Application (Weeks 3\u20135)", bold: true, color: NAVY, font: "Calibri", size: 22 })]
        }),
        body("Implement the full runtime control system in Python. Uses a Hardware Abstraction Layer (HAL) so that the same code runs on Windows (with simulated hardware) during development, and on Raspberry Pi (with real hardware) when deployed."),
        emptyLine(),
        h2("3.2  Hardware Abstraction Layer (HAL)"),
        body("The HAL defines a standard interface that all hardware must implement:"),
        bullet("read_pressure() \u2192 returns vessel pressure in MPa"),
        bullet("read_temperature() \u2192 returns vessel temperature in \u00B0C"),
        bullet("set_valve_position(pct) \u2192 0\u2013100% motor valve position"),
        bullet("set_solenoid_pwm(duty) \u2192 0\u2013100% vent solenoid duty cycle"),
        bullet("read_estop() \u2192 True if emergency stop pressed"),
        emptyLine(),
        callout("Two implementations exist: SimulatedHardware (Windows) and RPiHardware (Raspberry Pi). Switching requires changing one line in main.py.", TEAL),

        // ── SECTION 4: System Architecture ────────────────────────────────
        h1("4.  System Architecture"),
        emptyLine(),
        h2("4.1  Pressurization Path"),
        body("CO\u2082 Cylinder (5.9 MPa) \u2192 Victor Regulator (5.5 MPa output) \u2192 Air-Driven Booster (up to 28 MPa) \u2192 Motorized Needle Valve (NEW \u2014 flow control) \u2192 Check Valve \u2192 Pressure Vessel"),
        emptyLine(),
        h2("4.2  Depressurization Path"),
        body("Pressure Vessel \u2192 PWM Vent Solenoid (NEW \u2014 rate-controlled venting) \u2192 Manual Needle Valve (flow limiter) \u2192 Vent to Fume Hood"),
        emptyLine(),
        h2("4.3  Control Loop"),
        body("Pressure Transducer (4-20mA) \u2192 ADS1115 ADC \u2192 Raspberry Pi Controller (PID algorithm) \u2192 Stepper Driver \u2192 Motorized Valve (pressurize) / PWM SSR \u2192 Vent Solenoid (depressurize)"),
        emptyLine(),
        h2("4.4  Non-Linear Booster Behavior"),
        body("The air-driven booster provides output pressure approximately equal to ratio \u00D7 drive_air_pressure, capped at 28 MPa. As vessel pressure rises toward the booster output, the driving pressure differential shrinks:"),
        emptyLine(),
        callout("Flow rate \u221D valve_opening \u00D7 \u221A(P_booster \u2212 P_vessel)", CORAL),
        emptyLine(),
        body("This non-linearity means the PID must open the valve progressively wider as vessel pressure approaches maximum. At 27 MPa vessel / 28 MPa booster, relative flow capacity is only ~19% of maximum. The PID integral term compensates for this, but must be tuned carefully."),

        // ── SECTION 5: Temperature–Pressure Coupling ───────────────────────
        h1("5.  Temperature\u2013Pressure Coupling"),
        body("Temperature is independently controlled by the INKBIRD temperature controller (setpoint: 60\u00B0C). However, temperature directly affects pressure behavior in three important ways:"),
        emptyLine(),
        h2("5.1  Compression Heating During Pressurization"),
        body("When CO\u2082 flows into the vessel under pressure, adiabatic compression raises the gas temperature. This temperature rise creates additional pressure rise on top of the flow-driven pressure:"),
        callout("dP/dT \u2248 P/T \u2248 28 MPa / 333 K \u2248 0.084 MPa/\u00B0C", CORAL),
        body("A 2\u00B0C compression spike adds approximately 0.17 MPa of additional pressure. The pressure PID must not overreact to this transient \u2014 the INKBIRD will correct the temperature back to 60\u00B0C within ~15 seconds."),
        emptyLine(),
        h2("5.2  INKBIRD Controller Lag"),
        body("The INKBIRD has a ~15 second thermal response lag. During rapid pressurization, temperature may overshoot 60\u00B0C by 1\u20133\u00B0C before the INKBIRD corrects. This creates a corresponding pressure overshoot that the pressure PID must accommodate."),
        emptyLine(),
        h2("5.3  Joule-Thomson Cooling During Venting"),
        body("CO\u2082 expanding through the vent valve undergoes Joule-Thomson cooling \u2014 temperature drops as pressure drops. This temperature decrease causes additional pressure drop beyond the mass-vented amount, making the 2 MPa/min depressurization rate harder to maintain consistently."),
        emptyLine(),
        h2("5.4  Pre-Condition Check"),
        body("The software enforces a pre-condition check: the START button is disabled until vessel temperature \u2265 55\u00B0C. Below this temperature, CO\u2082 is not reliably supercritical (critical point: 31.1\u00B0C, 7.38 MPa), and pressurization behavior is different and unpredictable."),

        // ── SECTION 6: Simulink Digital Twin ──────────────────────────────
        h1("6.  Simulink Digital Twin (Phase 1)"),
        emptyLine(),
        h2("6.1  Model Structure"),
        body("The Simulink model uses Simscape Gas and Thermal library blocks to model the physical plant. Key subsystems:"),
        emptyLine(),
        new Paragraph({ spacing: { before: 80, after: 40 }, children: [new TextRun({ text: "Plant Subsystem:", bold: true, color: TEAL, font: "Calibri", size: 22 })] }),
        bullet("CO\u2082 Gas Source (28 MPa regulated booster output)"),
        bullet("Variable Orifice (motorized needle valve \u2014 controlled by stepper PID output)"),
        bullet("Check Valve (one-way flow)"),
        bullet("Gas Accumulator (pressure vessel)"),
        bullet("Thermal Mass (vessel + CO\u2082)"),
        bullet("INKBIRD PID (separate temperature control loop)"),
        bullet("Variable Orifice + PWM (vent solenoid)"),
        emptyLine(),
        new Paragraph({ spacing: { before: 80, after: 40 }, children: [new TextRun({ text: "Controller Subsystem:", bold: true, color: NAVY, font: "Calibri", size: 22 })] }),
        bullet("Ramp Setpoint Generator: P_sp(t) = P_start + (dP/dt_target) \u00D7 t"),
        bullet("PID Controller Block (Simulink built-in)"),
        bullet("State Machine (Simulink Stateflow or switch blocks)"),
        emptyLine(),
        h2("6.2  PID Tuning Process"),
        numbered("Open scCO2_plant.slx in MATLAB Simulink"),
        numbered("Click PID Controller block \u2192 Launch PID Tuner"),
        numbered("Adjust response time slider \u2014 watch pressure ramp respond in real time"),
        numbered("Target: 350 kPa/min ramp with <10% overshoot at full pressure"),
        numbered("Export gains: Kp, Ki, Kd \u2192 saved to config_gains.mat"),
        numbered("Run run_simulation.m to verify full pressurize \u2192 hold \u2192 depressurize cycle"),
        emptyLine(),
        h2("Initial PID Starting Values"),
        emptyLine(),
        pidTable(),

        // ── SECTION 7: Python App ──────────────────────────────────────────
        h1("7.  Python Control Application (Phase 2)"),
        emptyLine(),
        h2("7.1  Software Modules"),
        emptyLine(),
        modulesTable(),
        emptyLine(),
        h2("7.2  State Machine"),
        body("States: IDLE \u2192 PRESSURIZE \u2192 HOLD \u2192 DEPRESSURIZE \u2192 IDLE"),
        emptyLine(),
        bullet("IDLE \u2192 PRESSURIZE: User presses START (requires temp \u2265 55\u00B0C)"),
        bullet("PRESSURIZE \u2192 HOLD: Measured pressure \u2265 target pressure"),
        bullet("HOLD \u2192 DEPRESSURIZE: User presses DEPRESSURIZE button"),
        bullet("DEPRESSURIZE \u2192 IDLE: Measured pressure \u2264 0.1 MPa"),
        bullet("Any \u2192 IDLE: E-stop pressed (all outputs set to 0 immediately)"),
        emptyLine(),
        h2("7.3  Control Strategy"),
        new Paragraph({ spacing: { before: 80, after: 40 }, children: [new TextRun({ text: "Pressurize:", bold: true, color: TEAL, font: "Calibri", size: 22 })] }),
        body("Ramp setpoint = P_start + 0.35 MPa/min \u00D7 t. PID error = setpoint \u2212 measured. Output = valve opening percentage (0\u2013100%)."),
        new Paragraph({ spacing: { before: 80, after: 40 }, children: [new TextRun({ text: "Hold:", bold: true, color: NAVY, font: "Calibri", size: 22 })] }),
        body("Fixed setpoint at target pressure. PID makes small valve adjustments to compensate for thermal drift and minor leakage."),
        new Paragraph({ spacing: { before: 80, after: 40 }, children: [new TextRun({ text: "Depressurize:", bold: true, color: CORAL, font: "Calibri", size: 22 })] }),
        body("Ramp setpoint = P_start \u2212 2.0 MPa/min \u00D7 t. PID output drives vent solenoid PWM duty cycle (0\u2013100% at 1 Hz)."),
        emptyLine(),
        h2("7.4  Data Logging (CSV Format)"),
        body("Columns: timestamp, elapsed_s, pressure_MPa, temperature_C, setpoint_MPa, state, valve_pct, solenoid_pwm_pct"),
        body("Saved to: logs/experiment_YYYYMMDD_HHMMSS.csv (new file per session)"),

        // ── SECTION 8: Cloud Monitoring ────────────────────────────────────
        h1("8.  Remote Cloud Monitoring"),
        callout("Service: ThingSpeak by MathWorks (thingspeak.com) \u2014 free tier, 3 million messages/year", TEAL),
        emptyLine(),
        h2("8.1  Monitored Fields"),
        bullet("Field 1: Vessel pressure (MPa)"),
        bullet("Field 2: Vessel temperature (\u00B0C)"),
        bullet("Field 3: PID setpoint (MPa)"),
        bullet("Field 4: State code (0=IDLE, 1=PRESSURIZE, 2=HOLD, 3=DEPRESSURIZE)"),
        emptyLine(),
        h2("8.2  Alerts"),
        bullet("Email alert when experiment returns to IDLE state (\u201CExperiment complete\u201D)"),
        bullet("Email alert if pressure exceeds 27.5 MPa (\u201CPressure warning\u201D)"),
        emptyLine(),
        h2("8.3  MATLAB Integration"),
        new Paragraph({
          spacing: { before: 80, after: 80 },
          shading: { fill: "F0F4F8", type: ShadingType.CLEAR },
          children: [new TextRun({ text: "Data = thingSpeakRead(CHANNEL_ID, 'NumPoints', 1000, 'Fields', [1,2], 'ReadKey', 'API_KEY')", font: "Consolas", size: 20 })]
        }),
        body("This pulls all experiment data directly into MATLAB for post-processing and analysis."),
        emptyLine(),
        h2("8.4  Setup (One-Time, ~5 Minutes)"),
        numbered("Create free account at thingspeak.com"),
        numbered("Create new channel with 4 fields"),
        numbered("Copy Write API Key into config.py: THINGSPEAK_API_KEY = 'YOUR_KEY_HERE'"),

        // ── SECTION 9: Safety ──────────────────────────────────────────────
        h1("9.  Safety Design"),
        emptyLine(),
        h2("9.1  Software Safety Interlocks"),
        emptyLine(),
        safetyTable(),
        emptyLine(),
        h2("9.2  Emergency Stop"),
        body("The E-stop button immediately:"),
        numbered("Sets valve position to 0% (closes motorized valve)"),
        numbered("Sets solenoid PWM to 0% (closes vent solenoid)"),
        numbered("Transitions state machine to IDLE"),
        numbered("Logs E-stop event with timestamp"),
        numbered("Keeps system in IDLE until manual restart"),
        emptyLine(),
        callout("Note: Hardware E-stop (hardwired NC button cutting 24V power to all actuators) is a separate physical interlock independent of software.", "888888"),
        emptyLine(),
        h2("9.3  Fail-Safe Behavior"),
        body("Power loss \u2192 Booster stops, motorized valve spring-returns to closed, vent solenoid (normally-closed type) closes. Vessel holds pressure safely."),

        // ── SECTION 10: Timeline ───────────────────────────────────────────
        h1("10.  Implementation Timeline"),
        emptyLine(),
        timelineTable(),
        emptyLine(),
        callout("Software development in Weeks 1\u20135 proceeds entirely on Windows and runs in parallel with hardware procurement. No hardware dependency until RPi deployment phase.", TEAL),

        // ── SECTION 11: Dependencies ───────────────────────────────────────
        h1("11.  Dependencies and Setup"),
        emptyLine(),
        h2("11.1  Software Dependencies (Windows)"),
        bullet("Python 3.11+ (already installed)"),
        bullet("pip install matplotlib simple-pid requests"),
        bullet("tkinter (built into Python \u2014 no install needed)"),
        bullet("MATLAB R2023+ with Simulink, Simscape, Simscape Fluids"),
        emptyLine(),
        h2("11.2  Software Dependencies (Raspberry Pi)"),
        bullet("pip install adafruit-ads1x15 RPi.GPIO"),
        bullet("All other dependencies same as Windows"),
        emptyLine(),
        h2("11.3  Repository Structure"),
        new Paragraph({
          spacing: { before: 80, after: 80 },
          shading: { fill: "F0F4F8", type: ShadingType.CLEAR },
          children: [new TextRun({
            text: [
              "simulink/",
              "    scCO2_plant.slx        Main Simulink model",
              "    run_simulation.m       Run and plot results",
              "    export_gains.m         Save Kp, Ki, Kd to file",
              "",
              "pressure_control/",
              "    main.py                Entry point",
              "    config.py              All constants and settings",
              "    hardware/              HAL implementations (sim + RPi)",
              "    control/               PID, ramp, state machine",
              "    logger.py              CSV logging",
              "    cloud.py               ThingSpeak upload",
              "    gui.py                 Tkinter GUI",
              "",
              "logs/                      Auto-generated CSV files"
            ].join("\n"),
            font: "Consolas", size: 18
          })]
        }),

        // ── SECTION 12: Verification ───────────────────────────────────────
        h1("12.  Verification Plan"),
        emptyLine(),
        h2("12.1  Phase 1 Verification (Simulink)"),
        bullet("Scope shows pressure ramp at exactly 350 kPa/min from 0 to 28 MPa"),
        bullet("No pressure overshoot beyond 28 MPa"),
        bullet("Temperature coupling visible \u2014 compression heating spike during pressurization"),
        bullet("HOLD mode maintains \u00B11\u20132% at 28 MPa"),
        bullet("Depressurization follows 2 MPa/min ramp to 0"),
        bullet("E-stop simulation: outputs go to 0 within one control step"),
        emptyLine(),
        h2("12.2  Phase 2 Verification (Python Simulation)"),
        bullet("Run python main.py on Windows"),
        bullet("Press START: pressure rises at 350 kPa/min \u2014 visible on live chart"),
        bullet("Temperature shows ~1\u20132\u00B0C compression spike during pressurization"),
        bullet("Hold at 28 MPa: pressure stable \u00B10.3 MPa"),
        bullet("Press DEPRESSURIZE: pressure drops at 2 MPa/min"),
        bullet("E-stop at any time: all outputs zero immediately"),
        bullet("CSV file written to logs/ with correct columns and data"),
        bullet("ThingSpeak dashboard shows live data (requires account setup)"),
        emptyLine(),
        divider(),
        emptyLine(),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "Prepared by: Taub Research Group Software Team", color: "888888", font: "Calibri", size: 20 })]
        }),
        new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ text: "For: Dandan Zhang (zdandan@umich.edu) | University of Michigan, MSE Department", color: "888888", font: "Calibri", size: 20 })]
        }),
      ]
    }
  ]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync(
    "C:/Users/Vijai Venkatesh/Desktop/Pressure Regulation System/scCO2_Software_Implementation_Plan.docx",
    buffer
  );
  console.log("Document saved successfully.");
}).catch(err => console.error("Error:", err));
