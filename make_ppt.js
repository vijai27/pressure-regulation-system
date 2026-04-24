// make_ppt.js — scCO2 Pressure Regulation System presentation
// Run: node make_ppt.js

const pptxgen = require("pptxgenjs");
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "Automated scCO2 Pressure Regulation System";

// ── Palette ──────────────────────────────────────────────────────────────────
const C = {
  navy:     "0A2342",
  teal:     "0D9488",
  tealLt:   "14B8A6",
  tealPale: "CCFBF1",
  white:    "FFFFFF",
  offWhite: "F0F9FF",
  slate:    "64748B",
  dark:     "1E293B",
  mid:      "334155",
};

const makeShadow = () => ({ type: "outer", blur: 8, offset: 2, angle: 135, color: "000000", opacity: 0.12 });

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 1 — Title
// ════════════════════════════════════════════════════════════════════════════
{
  const sl = pres.addSlide();
  sl.background = { color: C.navy };

  // Teal accent bar left
  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 0.18, h: 5.625, fill: { color: C.teal }, line: { color: C.teal } });

  // Teal bottom strip
  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 4.9, w: 10, h: 0.725, fill: { color: C.teal }, line: { color: C.teal } });

  // Title
  sl.addText("Automated scCO₂", {
    x: 0.5, y: 0.7, w: 9, h: 0.9, margin: 0,
    fontFace: "Calibri", fontSize: 44, bold: true, color: C.white, align: "left",
  });
  sl.addText("Pressure Regulation System", {
    x: 0.5, y: 1.55, w: 9, h: 0.8, margin: 0,
    fontFace: "Calibri", fontSize: 36, bold: false, color: C.tealLt, align: "left",
  });

  // Divider
  sl.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 2.45, w: 4.5, h: 0.04, fill: { color: C.tealLt }, line: { color: C.tealLt } });

  // Subtitle
  sl.addText("Closed-loop computer control for supercritical CO₂ research\nRaspberry Pi · Python PID · Peng-Robinson EOS", {
    x: 0.5, y: 2.6, w: 8.5, h: 1.1, margin: 0,
    fontFace: "Calibri", fontSize: 16, color: "CADCFC", align: "left",
  });

  // Bottom bar text
  sl.addText("Mechanical Engineering Research  |  University of Michigan–Dearborn  |  2025", {
    x: 0.3, y: 4.92, w: 9.4, h: 0.5, margin: 0,
    fontFace: "Calibri", fontSize: 13, color: C.white, align: "left",
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 2 — What is scCO₂?
// ════════════════════════════════════════════════════════════════════════════
{
  const sl = pres.addSlide();
  sl.background = { color: C.offWhite };

  // Header bar
  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: C.navy }, line: { color: C.navy } });
  sl.addText("What is Supercritical CO₂?", {
    x: 0.4, y: 0, w: 9.2, h: 0.75, margin: 0,
    fontFace: "Calibri", fontSize: 24, bold: true, color: C.white, valign: "middle",
  });

  // Left — explanation
  const bullets = [
    "CO₂ becomes supercritical above 31.1°C and 7.38 MPa",
    "Acts like a liquid and a gas at the same time — high density, low viscosity",
    "Dissolves materials like a liquid but flows like a gas",
    "Used in extraction, sterilization, and materials processing",
    "Non-toxic, non-flammable, and leaves no residue",
  ];
  sl.addText(bullets.map((t, i) => ({
    text: t,
    options: { bullet: true, breakLine: i < bullets.length - 1, fontSize: 15, color: C.dark, fontFace: "Calibri", paraSpaceAfter: 8 }
  })), { x: 0.4, y: 1.0, w: 5.2, h: 4.0 });

  // Right — Phase diagram drawn with shapes
  // Background box
  sl.addShape(pres.shapes.RECTANGLE, { x: 6.0, y: 0.9, w: 3.6, h: 4.3,
    fill: { color: C.white }, line: { color: "CBD5E1", width: 1 }, shadow: makeShadow() });

  // Phase regions (simplified)
  sl.addShape(pres.shapes.RECTANGLE, { x: 6.0, y: 0.9, w: 1.8, h: 2.15, fill: { color: "DBEAFE" }, line: { color: "DBEAFE" } }); // solid
  sl.addShape(pres.shapes.RECTANGLE, { x: 7.8, y: 0.9, w: 1.8, h: 2.15, fill: { color: "E0F2FE" }, line: { color: "E0F2FE" } }); // liquid
  sl.addShape(pres.shapes.RECTANGLE, { x: 6.0, y: 3.05, w: 1.8, h: 2.15, fill: { color: "FEF3C7" }, line: { color: "FEF3C7" } }); // gas
  sl.addShape(pres.shapes.RECTANGLE, { x: 7.8, y: 3.05, w: 1.8, h: 2.15, fill: { color: C.tealPale }, line: { color: C.tealPale } }); // supercritical

  // Labels
  sl.addText("SOLID",       { x: 6.0,  y: 1.7,  w: 1.8, h: 0.35, margin: 0, fontFace: "Calibri", fontSize: 11, bold: true, color: "1D4ED8", align: "center" });
  sl.addText("LIQUID",      { x: 7.8,  y: 1.7,  w: 1.8, h: 0.35, margin: 0, fontFace: "Calibri", fontSize: 11, bold: true, color: "0369A1", align: "center" });
  sl.addText("GAS",         { x: 6.0,  y: 3.85, w: 1.8, h: 0.35, margin: 0, fontFace: "Calibri", fontSize: 11, bold: true, color: "B45309", align: "center" });
  sl.addText("SUPERCRITICAL\nFLUID ★", { x: 7.8, y: 3.7, w: 1.8, h: 0.6, margin: 0, fontFace: "Calibri", fontSize: 11, bold: true, color: C.teal, align: "center" });

  // Axis labels
  sl.addText("← Pressure", { x: 6.0, y: 5.1, w: 3.6, h: 0.3, margin: 0, fontFace: "Calibri", fontSize: 11, color: C.slate, align: "center" });
  sl.addText("Tc = 31.1°C  Pc = 7.38 MPa", {
    x: 6.0, y: 0.92, w: 3.6, h: 0.3, margin: 0,
    fontFace: "Calibri", fontSize: 10, italic: true, color: C.slate, align: "center"
  });

  // Dividing lines
  sl.addShape(pres.shapes.LINE, { x: 7.8, y: 0.9, w: 0, h: 4.3, line: { color: "94A3B8", width: 1 } });
  sl.addShape(pres.shapes.LINE, { x: 6.0, y: 3.05, w: 3.6, h: 0, line: { color: "94A3B8", width: 1 } });

  // Caption
  sl.addText("Our system operates at 60°C, up to 28 MPa — deep in the supercritical zone", {
    x: 0.4, y: 5.2, w: 9.2, h: 0.35, margin: 0,
    fontFace: "Calibri", fontSize: 13, italic: true, color: C.teal, align: "left",
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 3 — System Goals (key numbers)
// ════════════════════════════════════════════════════════════════════════════
{
  const sl = pres.addSlide();
  sl.background = { color: C.navy };

  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: C.teal }, line: { color: C.teal } });
  sl.addText("System Performance Targets", {
    x: 0.4, y: 0, w: 9.2, h: 0.75, margin: 0,
    fontFace: "Calibri", fontSize: 24, bold: true, color: C.white, valign: "middle",
  });

  const stats = [
    { val: "28 MPa",       sub: "Max Operating\nPressure",     note: "4,061 PSI — vessel\nrated to 34.5 MPa" },
    { val: "350 kPa/min",  sub: "Pressurization\nRate",        note: "Controlled ramp\nto avoid thermal shock" },
    { val: "±0.30 MPa",    sub: "Hold Accuracy\nBand",         note: "Maintained by\ndedicated hold PID" },
    { val: "60°C",         sub: "Operating\nTemperature",      note: "Above Tc to ensure\nsupercritical phase" },
  ];

  stats.forEach((s, i) => {
    const x = 0.3 + i * 2.38;
    sl.addShape(pres.shapes.RECTANGLE, { x, y: 1.0, w: 2.1, h: 3.8,
      fill: { color: C.mid }, line: { color: C.teal, width: 1.5 }, shadow: makeShadow() });
    sl.addText(s.val, { x, y: 1.25, w: 2.1, h: 0.8, margin: 0,
      fontFace: "Calibri", fontSize: 26, bold: true, color: C.tealLt, align: "center" });
    sl.addText(s.sub, { x, y: 2.1, w: 2.1, h: 0.75, margin: 0,
      fontFace: "Calibri", fontSize: 13, bold: true, color: C.white, align: "center" });
    sl.addShape(pres.shapes.RECTANGLE, { x: x + 0.4, y: 2.9, w: 1.3, h: 0.03, fill: { color: C.teal }, line: { color: C.teal } });
    sl.addText(s.note, { x, y: 3.0, w: 2.1, h: 0.9, margin: 0,
      fontFace: "Calibri", fontSize: 11, color: "94A3B8", align: "center" });
  });

  sl.addText("All controlled autonomously — operator sets target, system handles the rest", {
    x: 0.5, y: 5.1, w: 9, h: 0.4, margin: 0,
    fontFace: "Calibri", fontSize: 13, italic: true, color: C.tealLt, align: "center",
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 4 — System Architecture (flow diagram)
// ════════════════════════════════════════════════════════════════════════════
{
  const sl = pres.addSlide();
  sl.background = { color: C.offWhite };

  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: C.navy }, line: { color: C.navy } });
  sl.addText("System Architecture", {
    x: 0.4, y: 0, w: 9.2, h: 0.75, margin: 0,
    fontFace: "Calibri", fontSize: 24, bold: true, color: C.white, valign: "middle",
  });

  // Flow: CO2 Cylinder → Booster → Needle Valve → Vessel → Vent Solenoid
  const boxes = [
    { label: "CO₂\nCylinder",     sub: "Bone Dry\n5.7 MPa",       x: 0.2 },
    { label: "Air-Driven\nBooster", sub: "HII 5G-TD\n172 MPa max", x: 2.1 },
    { label: "Needle\nValve",      sub: "Stepper motor\ncontrolled", x: 4.0 },
    { label: "PARR\nVessel",       sub: "1L, 316SS\n34.5 MPa rated", x: 5.9 },
    { label: "Vent\nSolenoid",     sub: "PWM\ncontrolled",          x: 7.8 },
  ];

  boxes.forEach((b, i) => {
    const isVessel = b.label.includes("PARR");
    sl.addShape(pres.shapes.RECTANGLE, { x: b.x, y: 1.05, w: 1.7, h: 1.5,
      fill: { color: isVessel ? C.teal : C.navy }, line: { color: C.teal, width: 1.5 }, shadow: makeShadow() });
    sl.addText(b.label, { x: b.x, y: 1.1, w: 1.7, h: 0.85, margin: 0,
      fontFace: "Calibri", fontSize: 14, bold: true, color: C.white, align: "center", valign: "middle" });
    sl.addText(b.sub, { x: b.x, y: 2.0, w: 1.7, h: 0.55, margin: 0,
      fontFace: "Calibri", fontSize: 10, color: isVessel ? C.white : C.tealLt, align: "center" });
    // Arrow to next
    if (i < boxes.length - 1) {
      sl.addShape(pres.shapes.LINE, { x: b.x + 1.7, y: 1.8, w: 0.4, h: 0, line: { color: C.teal, width: 2 } });
      sl.addText("▶", { x: b.x + 1.95, y: 1.68, w: 0.25, h: 0.25, margin: 0,
        fontFace: "Calibri", fontSize: 12, color: C.teal, align: "center" });
    }
  });

  // RPi control box below
  sl.addShape(pres.shapes.RECTANGLE, { x: 3.5, y: 3.15, w: 3.0, h: 1.0,
    fill: { color: C.dark }, line: { color: C.tealLt, width: 2 }, shadow: makeShadow() });
  sl.addText("Raspberry Pi 4", { x: 3.5, y: 3.2, w: 3.0, h: 0.4, margin: 0,
    fontFace: "Calibri", fontSize: 15, bold: true, color: C.tealLt, align: "center" });
  sl.addText("Python PID Control  |  10 Hz  |  GUI + Logging", { x: 3.5, y: 3.6, w: 3.0, h: 0.45, margin: 0,
    fontFace: "Calibri", fontSize: 11, color: "94A3B8", align: "center" });

  // Control arrows (up from RPi to Needle Valve and Solenoid)
  sl.addShape(pres.shapes.LINE, { x: 5.0, y: 3.15, w: 0, h: -0.6, line: { color: C.tealLt, width: 1.5 } });
  sl.addShape(pres.shapes.LINE, { x: 8.65, y: 3.15, w: 0, h: -0.6, line: { color: C.tealLt, width: 1.5 } });

  // Sensor feedback arrow
  sl.addShape(pres.shapes.LINE, { x: 5.9, y: 2.75, w: 0, h: 0.5, line: { color: "F59E0B", width: 1.5 } });
  sl.addText("Pressure\nSensor", { x: 5.9, y: 3.28, w: 1.0, h: 0.45, margin: 0,
    fontFace: "Calibri", fontSize: 10, color: "F59E0B", align: "center" });

  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 4.9, w: 10, h: 0.725, fill: { color: C.navy }, line: { color: C.navy } });
  sl.addText("Yellow = sensor feedback  |  Teal = control signal  |  White arrows = gas flow", {
    x: 0.3, y: 4.92, w: 9.4, h: 0.5, margin: 0,
    fontFace: "Calibri", fontSize: 12, color: "94A3B8", align: "left",
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 5 — Parts List
// ════════════════════════════════════════════════════════════════════════════
{
  const sl = pres.addSlide();
  sl.background = { color: C.offWhite };

  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: C.navy }, line: { color: C.navy } });
  sl.addText("Parts List", {
    x: 0.4, y: 0, w: 9.2, h: 0.75, margin: 0,
    fontFace: "Calibri", fontSize: 24, bold: true, color: C.white, valign: "middle",
  });

  const hdr = { fill: { color: C.teal }, color: C.white, bold: true, fontSize: 11, fontFace: "Calibri", align: "center", valign: "middle" };
  const rows = [
    [{ text: "Component",    options: hdr }, { text: "Specification",  options: hdr }, { text: "Purpose",            options: hdr }],
    ["PARR Pressure Vessel",   "1L, 316SS, 5000 PSI, Model 2302HC",      "Contains experiment"],
    ["HII Gas Booster",        "5G-TD-28/150-CO2, 25,000 PSI max out",   "Amplifies CO₂ to operating pressure"],
    ["CO₂ Cylinder",           "Bone Dry, UN1013, 50 lb",                "Process gas supply (≥99.8% pure)"],
    ["Motorized Needle Valve", "Stepper-driven, high pressure rated",     "Controls pressurization flow rate"],
    ["Vent Solenoid Valve",    "PWM-controlled, normally closed",         "Controls depressurization rate"],
    ["Safety Relief Valve",    "Parker SS316, 1/4\" MNPT",               "Hardware overpressure protection"],
    ["Pressure Transducer",    "Ashcroft 0–5000 PSI, 4–20 mA, IP67",    "Real-time pressure feedback"],
    ["INKBIRD Controller",     "Setpoint 60°C, stable ±0.01°C",          "Vessel temperature control"],
    ["Raspberry Pi 4",         "Python 3.11, 10 Hz control loop",        "Main controller"],
    ["ADS1115 ADC",            "16-bit, I²C, 4-channel",                 "Reads 4–20 mA transducer signal"],
    ["Stepper Motor + Driver", "NEMA 17, A4988, 1/16 microstepping",     "Actuates needle valve"],
    ["DIN Rail PSU",           "Dayton 33NT20, 24VDC 50W",              "24V system power"],
    ["Relay Module",           "24VDC coil, 10A contacts",               "GPIO drives solenoid valve"],
  ];

  const odd  = { fill: { color: C.white },   fontSize: 10, fontFace: "Calibri", color: C.dark, valign: "middle" };
  const even = { fill: { color: "F0F9FF" },  fontSize: 10, fontFace: "Calibri", color: C.dark, valign: "middle" };

  const tableData = rows.map((r, i) => {
    if (i === 0) return r;
    const style = i % 2 === 1 ? odd : even;
    return r.map(cell => ({ text: cell, options: style }));
  });

  sl.addTable(tableData, {
    x: 0.3, y: 0.85, w: 9.4, h: 4.65,
    colW: [2.4, 3.4, 3.6],
    border: { pt: 0.5, color: "CBD5E1" },
    rowH: 0.32,
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 6 — Control Logic (State Machine)
// ════════════════════════════════════════════════════════════════════════════
{
  const sl = pres.addSlide();
  sl.background = { color: C.navy };

  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: C.teal }, line: { color: C.teal } });
  sl.addText("Automated Control Logic", {
    x: 0.4, y: 0, w: 9.2, h: 0.75, margin: 0,
    fontFace: "Calibri", fontSize: 24, bold: true, color: C.white, valign: "middle",
  });

  // State boxes
  const states = [
    { name: "IDLE",          desc: "Valves closed\nAwaiting start\nTemp check ≥55°C",  x: 0.3,  col: C.mid },
    { name: "PRESSURIZE",    desc: "PID ramps pressure\n350 kPa/min\nKp=40 Ki=5 Kd=2", x: 2.55, col: C.teal },
    { name: "HOLD",          desc: "PID holds setpoint\n±0.30 MPa band\nKp=20 Ki=2",   x: 4.8,  col: C.teal },
    { name: "DEPRESSURIZE",  desc: "PID vents slowly\n2 MPa/min\nKp=60 Ki=8",          x: 7.05, col: C.mid },
  ];

  states.forEach((s, i) => {
    sl.addShape(pres.shapes.RECTANGLE, { x: s.x, y: 1.05, w: 2.1, h: 2.1,
      fill: { color: s.col }, line: { color: C.tealLt, width: 1.5 }, shadow: makeShadow() });
    sl.addText(s.name, { x: s.x, y: 1.1, w: 2.1, h: 0.5, margin: 0,
      fontFace: "Calibri", fontSize: 15, bold: true, color: C.tealLt, align: "center" });
    sl.addShape(pres.shapes.RECTANGLE, { x: s.x + 0.3, y: 1.62, w: 1.5, h: 0.03, fill: { color: C.teal }, line: { color: C.teal } });
    sl.addText(s.desc, { x: s.x, y: 1.7, w: 2.1, h: 1.35, margin: 0,
      fontFace: "Calibri", fontSize: 11, color: "94A3B8", align: "center" });

    if (i < states.length - 1) {
      sl.addShape(pres.shapes.LINE, { x: s.x + 2.1, y: 2.1, w: 0.45, h: 0, line: { color: C.tealLt, width: 2 } });
      sl.addText("▶", { x: s.x + 2.25, y: 1.98, w: 0.25, h: 0.25, margin: 0,
        fontFace: "Calibri", fontSize: 12, color: C.tealLt, align: "center" });
    }
  });

  // Safety interlocks box
  sl.addShape(pres.shapes.RECTANGLE, { x: 0.3, y: 3.5, w: 9.4, h: 1.6,
    fill: { color: C.dark }, line: { color: "EF4444", width: 1.5 }, shadow: makeShadow() });
  sl.addText("Safety Interlocks (active in ALL states)", { x: 0.5, y: 3.55, w: 9.0, h: 0.4, margin: 0,
    fontFace: "Calibri", fontSize: 13, bold: true, color: "EF4444", align: "left" });

  const safetyItems = [
    "Overpressure cutoff at 28.5 MPa — forces IDLE immediately",
    "Rate limiter: closes all valves if pressure rises > 5 MPa/min",
    "Temperature gate: pressurization blocked below 55°C",
    "Watchdog: forces IDLE if control loop stalls for > 1 second",
  ];
  sl.addText(safetyItems.map((t, i) => ({
    text: t, options: { bullet: true, breakLine: i < safetyItems.length - 1, fontSize: 12, color: C.white, fontFace: "Calibri" }
  })), { x: 0.6, y: 3.95, w: 9.0, h: 1.1 });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 7 — Physics Model
// ════════════════════════════════════════════════════════════════════════════
{
  const sl = pres.addSlide();
  sl.background = { color: C.offWhite };

  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: C.navy }, line: { color: C.navy } });
  sl.addText("Physics Model — Real CO₂ Behavior", {
    x: 0.4, y: 0, w: 9.2, h: 0.75, margin: 0,
    fontFace: "Calibri", fontSize: 24, bold: true, color: C.white, valign: "middle",
  });

  // Left column — explanation
  sl.addText("Peng-Robinson Equation of State", { x: 0.4, y: 0.9, w: 4.8, h: 0.45, margin: 0,
    fontFace: "Calibri", fontSize: 17, bold: true, color: C.navy });
  sl.addShape(pres.shapes.RECTANGLE, { x: 0.4, y: 1.35, w: 4.8, h: 0.04, fill: { color: C.teal }, line: { color: C.teal } });

  const pts = [
    "At 20+ MPa, CO₂ is up to 118% denser than ideal gas predicts",
    "The simulator uses PR-EOS so pressure predictions are physically accurate",
    "A 0.01°C temperature flicker moves pressure by 3.5 kPa at 20 MPa — not 0.6 kPa as ideal gas predicts",
    "This matters most in the HOLD phase where stability is critical",
  ];
  sl.addText(pts.map((t, i) => ({
    text: t, options: { bullet: true, breakLine: i < pts.length - 1, fontSize: 13, color: C.dark, fontFace: "Calibri", paraSpaceAfter: 7 }
  })), { x: 0.4, y: 1.5, w: 4.8, h: 3.8 });

  // Right column — Z-factor table
  sl.addText("Z-factor & Density at 60°C", { x: 5.5, y: 0.9, w: 4.1, h: 0.45, margin: 0,
    fontFace: "Calibri", fontSize: 15, bold: true, color: C.navy, align: "center" });

  const hdr = { fill: { color: C.teal }, color: C.white, bold: true, fontSize: 11, fontFace: "Calibri", align: "center", valign: "middle" };
  const c1  = { fill: { color: C.white },   color: C.dark, fontSize: 11, fontFace: "Calibri", align: "center", valign: "middle" };
  const c2  = { fill: { color: "F0F9FF" },  color: C.dark, fontSize: 11, fontFace: "Calibri", align: "center", valign: "middle" };
  const hi  = { fill: { color: "CCFBF1" },  color: C.teal, fontSize: 11, fontFace: "Calibri", align: "center", valign: "middle", bold: true };

  const tdata = [
    [{ text: "Pressure",  options: hdr }, { text: "Z-factor", options: hdr }, { text: "Density vs Ideal", options: hdr }],
    [{ text: "0.34 MPa",  options: c1  }, { text: "0.99",     options: c1  }, { text: "≈ same",           options: c1  }],
    [{ text: "5 MPa",     options: c2  }, { text: "0.79",     options: c2  }, { text: "+26% denser",      options: c2  }],
    [{ text: "10 MPa",    options: c1  }, { text: "0.54",     options: c1  }, { text: "+84% denser",      options: c1  }],
    [{ text: "20 MPa",    options: hi  }, { text: "0.46",     options: hi  }, { text: "+118% denser ★",   options: hi  }],
    [{ text: "28 MPa",    options: c2  }, { text: "0.55",     options: c2  }, { text: "+82% denser",      options: c2  }],
  ];
  sl.addTable(tdata, {
    x: 5.5, y: 1.42, w: 4.1, h: 2.8, colW: [1.4, 1.3, 1.4],
    border: { pt: 0.5, color: "CBD5E1" }, rowH: 0.42,
  });

  sl.addText("★ At 20 MPa, ideal gas is off by 2× — PR-EOS corrects this", {
    x: 5.5, y: 4.35, w: 4.1, h: 0.45, margin: 0,
    fontFace: "Calibri", fontSize: 11, italic: true, color: C.teal, align: "center",
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 8 — Software Stack
// ════════════════════════════════════════════════════════════════════════════
{
  const sl = pres.addSlide();
  sl.background = { color: C.navy };

  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: C.teal }, line: { color: C.teal } });
  sl.addText("Software Stack", {
    x: 0.4, y: 0, w: 9.2, h: 0.75, margin: 0,
    fontFace: "Calibri", fontSize: 24, bold: true, color: C.white, valign: "middle",
  });

  const modules = [
    { name: "main.py",           role: "Entry point, control thread, watchdog" },
    { name: "control/pid.py",    role: "PID with anti-windup, derivative on measurement" },
    { name: "control/ramp.py",   role: "Linear ramp setpoint generator" },
    { name: "control/eos.py",    role: "Peng-Robinson EOS — real CO₂ physics" },
    { name: "control/state_machine.py", role: "IDLE/PRESSURIZE/HOLD/DEPRESSURIZE logic" },
    { name: "hardware/simulator.py",    role: "Windows physics simulation (10 Hz)" },
    { name: "hardware/rpi_hardware.py", role: "Raspberry Pi GPIO/ADS1115 (hardware stub)" },
    { name: "gui.py",            role: "Tkinter + Matplotlib live dashboard" },
    { name: "logger.py",         role: "CSV timestamped experiment logs" },
    { name: "cloud.py",          role: "ThingSpeak real-time cloud monitoring" },
  ];

  modules.forEach((m, i) => {
    const col = i % 2 === 0 ? 0.3 : 5.15;
    const row = Math.floor(i / 2);
    const y = 0.95 + row * 0.88;
    sl.addShape(pres.shapes.RECTANGLE, { x: col, y, w: 4.6, h: 0.72,
      fill: { color: C.dark }, line: { color: C.teal, width: 1 }, shadow: makeShadow() });
    sl.addShape(pres.shapes.RECTANGLE, { x: col, y, w: 0.1, h: 0.72, fill: { color: C.teal }, line: { color: C.teal } });
    sl.addText(m.name, { x: col + 0.18, y: y + 0.04, w: 4.3, h: 0.3, margin: 0,
      fontFace: "Consolas", fontSize: 12, bold: true, color: C.tealLt });
    sl.addText(m.role, { x: col + 0.18, y: y + 0.35, w: 4.3, h: 0.32, margin: 0,
      fontFace: "Calibri", fontSize: 11, color: "94A3B8" });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 9 — Next Steps
// ════════════════════════════════════════════════════════════════════════════
{
  const sl = pres.addSlide();
  sl.background = { color: C.offWhite };

  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: C.navy }, line: { color: C.navy } });
  sl.addText("Next Steps", {
    x: 0.4, y: 0, w: 9.2, h: 0.75, margin: 0,
    fontFace: "Calibri", fontSize: 24, bold: true, color: C.white, valign: "middle",
  });

  const steps = [
    { num: "01", title: "Complete RPi Hardware Driver",  body: "Wire ADS1115 for pressure transducer, stepper GPIO for needle valve, relay for solenoid — the final step before real hardware runs.", status: "In Progress", col: "EF4444" },
    { num: "02", title: "PID Gain Re-Tuning",            body: "PR-EOS shows CO₂ is 5-6× more pressure-sensitive to temperature at 20+ MPa. Hold PID gains need verification in updated simulation.", status: "Pending",     col: "F59E0B" },
    { num: "03", title: "Valve Cv Calibration",          body: "Run timed pressurization at fixed valve opening, back-calculate Cv from pressure rise + PR-EOS density to remove last empirical constant.", status: "Pending",     col: "F59E0B" },
    { num: "04", title: "Simulink Digital Twin",         body: "Use build_model.m + PID Tuner with Simscape Fluids to get analytically-tuned gains. Export to config.py via export_gains.m.", status: "Planned",      col: "0D9488" },
  ];

  steps.forEach((s, i) => {
    const x = (i % 2 === 0) ? 0.3 : 5.15;
    const y = i < 2 ? 0.95 : 3.15;
    sl.addShape(pres.shapes.RECTANGLE, { x, y, w: 4.55, h: 1.95,
      fill: { color: C.white }, line: { color: "E2E8F0", width: 1 }, shadow: makeShadow() });
    sl.addShape(pres.shapes.RECTANGLE, { x, y, w: 4.55, h: 0.06, fill: { color: s.col }, line: { color: s.col } });
    // Number circle (drawn as square)
    sl.addShape(pres.shapes.RECTANGLE, { x: x + 0.12, y: y + 0.18, w: 0.45, h: 0.45,
      fill: { color: s.col }, line: { color: s.col } });
    sl.addText(s.num, { x: x + 0.12, y: y + 0.18, w: 0.45, h: 0.45, margin: 0,
      fontFace: "Calibri", fontSize: 14, bold: true, color: C.white, align: "center", valign: "middle" });
    sl.addText(s.title, { x: x + 0.65, y: y + 0.2, w: 3.7, h: 0.4, margin: 0,
      fontFace: "Calibri", fontSize: 13, bold: true, color: C.dark });
    sl.addText(s.body, { x: x + 0.12, y: y + 0.7, w: 4.2, h: 1.1, margin: 0,
      fontFace: "Calibri", fontSize: 11, color: C.slate });
    sl.addShape(pres.shapes.RECTANGLE, { x: x + 3.3, y: y + 0.2, w: 1.05, h: 0.35,
      fill: { color: s.col, transparency: 80 }, line: { color: s.col, width: 1 } });
    sl.addText(s.status, { x: x + 3.3, y: y + 0.2, w: 1.05, h: 0.35, margin: 0,
      fontFace: "Calibri", fontSize: 10, bold: true, color: s.col, align: "center", valign: "middle" });
  });
}

// ════════════════════════════════════════════════════════════════════════════
// SLIDE 10 — Summary
// ════════════════════════════════════════════════════════════════════════════
{
  const sl = pres.addSlide();
  sl.background = { color: C.navy };

  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.75, fill: { color: C.teal }, line: { color: C.teal } });
  sl.addText("Summary", {
    x: 0.4, y: 0, w: 9.2, h: 0.75, margin: 0,
    fontFace: "Calibri", fontSize: 24, bold: true, color: C.white, valign: "middle",
  });

  const pts = [
    "Designed and built a fully automated scCO₂ pressure control system from scratch",
    "Implemented 3-PID state machine (PRESSURIZE / HOLD / DEPRESSURIZE) running at 10 Hz on Raspberry Pi",
    "Physics simulator uses Peng-Robinson EOS — captures real CO₂ behavior at 20–28 MPa with 5–6× better accuracy than ideal gas",
    "Hardware abstraction layer allows the same Python code to run in Windows simulation or on real RPi hardware",
    "Real-time GUI dashboard + CSV logging + ThingSpeak cloud monitoring",
    "System validated in simulation against PARR vessel (1L, 34.5 MPa rated) and HII booster (172 MPa max output)",
  ];

  sl.addText(pts.map((t, i) => ({
    text: t, options: { bullet: true, breakLine: i < pts.length - 1, fontSize: 14, color: C.white, fontFace: "Calibri", paraSpaceAfter: 10 }
  })), { x: 0.5, y: 0.95, w: 9.0, h: 4.0 });

  sl.addShape(pres.shapes.RECTANGLE, { x: 0, y: 4.9, w: 10, h: 0.725, fill: { color: C.teal }, line: { color: C.teal } });
  sl.addText("Questions?", {
    x: 0.3, y: 4.92, w: 9.4, h: 0.5, margin: 0,
    fontFace: "Calibri", fontSize: 20, bold: true, color: C.white, align: "center", valign: "middle",
  });
}

// ── Write file ───────────────────────────────────────────────────────────────
const outPath = "scCO2_System_Presentation.pptx";
pres.writeFile({ fileName: outPath })
  .then(() => console.log("Saved: " + outPath))
  .catch(e => { console.error(e); process.exit(1); });
