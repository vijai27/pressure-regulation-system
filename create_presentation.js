const pptxgen = require("C:/Users/Vijai Venkatesh/AppData/Roaming/npm/node_modules/pptxgenjs");

// Colors
const NAVY    = "1E2761";
const CREAM   = "F8F8F8";
const TEAL    = "028090";
const CORAL   = "F96167";
const WHITE   = "FFFFFF";
const DARK    = "1A1A2E";
const GRAY    = "64748B";
const LIGHT_TEAL = "E0F4F6";
const LIGHT_CORAL = "FFF0F0";

const makeShadow = () => ({ type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.12 });

let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "Taub Research Group";
pres.title = "scCO2 Pressure Control System — Software Implementation Plan";

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 1 — Title (dark)
// ─────────────────────────────────────────────────────────────────────────────
{
  let slide = pres.addSlide();
  slide.background = { color: NAVY };

  // Left teal accent bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: 5.625,
    fill: { color: TEAL }, line: { color: TEAL }
  });

  // Bottom coral bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.1, w: 10, h: 0.525,
    fill: { color: CORAL }, line: { color: CORAL }
  });

  // Decorative circle
  slide.addShape(pres.shapes.OVAL, {
    x: 7.2, y: 0.3, w: 2.8, h: 2.8,
    fill: { color: TEAL, transparency: 80 },
    line: { color: TEAL, width: 1.5 }
  });
  slide.addShape(pres.shapes.OVAL, {
    x: 7.6, y: 0.7, w: 2.0, h: 2.0,
    fill: { color: TEAL, transparency: 70 },
    line: { color: TEAL, width: 1 }
  });

  // scCO₂ label chip
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 0.9, w: 1.8, h: 0.32,
    fill: { color: TEAL }, line: { color: TEAL }, rectRadius: 0.05
  });
  slide.addText("RESEARCH PROJECT", {
    x: 0.4, y: 0.9, w: 1.8, h: 0.32,
    fontSize: 7, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0
  });

  // Title
  slide.addText("scCO\u2082 Pressure", {
    x: 0.38, y: 1.35, w: 7.2, h: 0.85,
    fontSize: 44, bold: true, color: WHITE, fontFace: "Calibri", margin: 0
  });
  slide.addText("Control System", {
    x: 0.38, y: 2.05, w: 7.2, h: 0.85,
    fontSize: 44, bold: true, color: WHITE, fontFace: "Calibri", margin: 0
  });

  // Subtitle
  slide.addText("Automated Control Software — Implementation Plan", {
    x: 0.38, y: 3.05, w: 7.0, h: 0.45,
    fontSize: 16, color: "CADCFC", fontFace: "Calibri", margin: 0
  });

  // Bottom bar text
  slide.addText("Taub Research Group   |   University of Michigan MSE   |   March 2026", {
    x: 0.25, y: 5.12, w: 9.5, h: 0.42,
    fontSize: 11, color: WHITE, fontFace: "Calibri", align: "center", valign: "middle", margin: 0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 2 — The Problem (light)
// ─────────────────────────────────────────────────────────────────────────────
{
  let slide = pres.addSlide();
  slide.background = { color: CREAM };

  // Top navy bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.55,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addText("scCO\u2082 Pressure Control System", {
    x: 0.3, y: 0, w: 9.4, h: 0.55,
    fontSize: 10, color: WHITE, fontFace: "Calibri", valign: "middle", margin: 0
  });

  // Title
  slide.addText("The Problem", {
    x: 0.5, y: 0.7, w: 9, h: 0.6,
    fontSize: 36, bold: true, color: NAVY, fontFace: "Calibri", margin: 0
  });

  // 4 problem cards in 2x2 grid
  const problems = [
    { title: "No Rate Control", body: "Pressurization rates vary unpredictably with manual valve adjustment — irreproducible experiments.", color: CORAL, icon: "✗" },
    { title: "Operator Dependent", body: "Results change based on who runs the experiment and how attentive they are at any given moment.", color: CORAL, icon: "✗" },
    { title: "No Data Logging", body: "Pressure vs. time data must be recorded manually — error-prone, incomplete, hard to reproduce.", color: CORAL, icon: "✗" },
    { title: "Safety Risk", body: "No automated overpressure protection or controlled emergency depressurization procedure.", color: CORAL, icon: "✗" }
  ];

  const positions = [
    { x: 0.4, y: 1.5 }, { x: 5.2, y: 1.5 },
    { x: 0.4, y: 3.15 }, { x: 5.2, y: 3.15 }
  ];

  problems.forEach((p, i) => {
    const pos = positions[i];
    // Card background
    slide.addShape(pres.shapes.RECTANGLE, {
      x: pos.x, y: pos.y, w: 4.4, h: 1.5,
      fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 },
      shadow: makeShadow()
    });
    // Left accent
    slide.addShape(pres.shapes.RECTANGLE, {
      x: pos.x, y: pos.y, w: 0.07, h: 1.5,
      fill: { color: CORAL }, line: { color: CORAL }
    });
    // Title
    slide.addText(p.title, {
      x: pos.x + 0.18, y: pos.y + 0.1, w: 4.0, h: 0.35,
      fontSize: 14, bold: true, color: NAVY, fontFace: "Calibri", margin: 0
    });
    // Body
    slide.addText(p.body, {
      x: pos.x + 0.18, y: pos.y + 0.42, w: 4.0, h: 0.95,
      fontSize: 11, color: "334155", fontFace: "Calibri", margin: 0
    });
  });

  // Research requirement callout
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 4.82, w: 9.2, h: 0.6,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addText("Research Requirement:  Constant, reproducible rates — 350 kPa/min pressurize  /  2 MPa/min depressurize", {
    x: 0.5, y: 4.82, w: 9.0, h: 0.6,
    fontSize: 12, bold: true, color: WHITE, fontFace: "Calibri", align: "center", valign: "middle", margin: 0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 3 — Proposed Software Solution (light)
// ─────────────────────────────────────────────────────────────────────────────
{
  let slide = pres.addSlide();
  slide.background = { color: CREAM };

  // Top bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.55,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addText("scCO\u2082 Pressure Control System", {
    x: 0.3, y: 0, w: 9.4, h: 0.55,
    fontSize: 10, color: WHITE, fontFace: "Calibri", valign: "middle", margin: 0
  });

  slide.addText("Proposed Software Solution", {
    x: 0.5, y: 0.7, w: 9, h: 0.6,
    fontSize: 36, bold: true, color: NAVY, fontFace: "Calibri", margin: 0
  });

  // Phase 1 card
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.5, w: 4.3, h: 3.2,
    fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 },
    shadow: makeShadow()
  });
  // Phase 1 header
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.5, w: 4.3, h: 0.55,
    fill: { color: TEAL }, line: { color: TEAL }
  });
  slide.addText("PHASE 1", {
    x: 0.45, y: 1.5, w: 4.2, h: 0.55,
    fontSize: 13, bold: true, color: WHITE, fontFace: "Calibri", align: "center", valign: "middle", margin: 0
  });
  slide.addText("Simulink Digital Twin", {
    x: 0.5, y: 2.15, w: 4.1, h: 0.4,
    fontSize: 16, bold: true, color: NAVY, fontFace: "Calibri", margin: 0
  });
  slide.addText([
    { text: "Build a validated physics model of the CO\u2082 vessel in MATLAB Simulink + Simscape.\n\n", options: { breakLine: false } },
    { text: "Use the interactive PID Tuner to find optimal control gains before hardware arrives.\n\n", options: { breakLine: false } },
    { text: "No hardware needed — validate everything in software first.", options: {} }
  ], {
    x: 0.5, y: 2.6, w: 4.0, h: 1.8,
    fontSize: 12, color: "334155", fontFace: "Calibri"
  });

  // Phase 2 card
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.3, y: 1.5, w: 4.3, h: 3.2,
    fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 },
    shadow: makeShadow()
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.3, y: 1.5, w: 4.3, h: 0.55,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addText("PHASE 2", {
    x: 5.35, y: 1.5, w: 4.2, h: 0.55,
    fontSize: 13, bold: true, color: WHITE, fontFace: "Calibri", align: "center", valign: "middle", margin: 0
  });
  slide.addText("Python Control Application", {
    x: 5.4, y: 2.15, w: 4.0, h: 0.4,
    fontSize: 16, bold: true, color: NAVY, fontFace: "Calibri", margin: 0
  });
  slide.addText([
    { text: "Full runtime control system running on Raspberry Pi — deployed when hardware arrives.\n\n", options: { breakLine: false } },
    { text: "Simulation mode on Windows for development and testing right now.\n\n", options: { breakLine: false } },
    { text: "One line of code to switch from simulation to real hardware.", options: {} }
  ], {
    x: 5.4, y: 2.6, w: 4.0, h: 1.8,
    fontSize: 12, color: "334155", fontFace: "Calibri"
  });

  // Bottom stats
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 4.85, w: 4.3, h: 0.55,
    fill: { color: LIGHT_TEAL }, line: { color: TEAL, width: 1 }
  });
  slide.addText("Cost: ~$0  (open source Python + free MATLAB license)", {
    x: 0.5, y: 4.85, w: 4.1, h: 0.55,
    fontSize: 11, bold: true, color: TEAL, fontFace: "Calibri", align: "center", valign: "middle", margin: 0
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.3, y: 4.85, w: 4.3, h: 0.55,
    fill: { color: LIGHT_TEAL }, line: { color: TEAL, width: 1 }
  });
  slide.addText("Timeline: 4 \u2013 6 weeks (parallel with hardware procurement)", {
    x: 5.4, y: 4.85, w: 4.1, h: 0.55,
    fontSize: 11, bold: true, color: TEAL, fontFace: "Calibri", align: "center", valign: "middle", margin: 0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 4 — System Architecture (light)
// ─────────────────────────────────────────────────────────────────────────────
{
  let slide = pres.addSlide();
  slide.background = { color: CREAM };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.55,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addText("scCO\u2082 Pressure Control System", {
    x: 0.3, y: 0, w: 9.4, h: 0.55,
    fontSize: 10, color: WHITE, fontFace: "Calibri", valign: "middle", margin: 0
  });

  slide.addText("System Architecture", {
    x: 0.5, y: 0.65, w: 9, h: 0.5,
    fontSize: 36, bold: true, color: NAVY, fontFace: "Calibri", margin: 0
  });

  // Pressurization path label
  slide.addText("PRESSURIZATION PATH", {
    x: 0.4, y: 1.3, w: 9.2, h: 0.3,
    fontSize: 9, bold: true, color: TEAL, fontFace: "Calibri", margin: 0, charSpacing: 2
  });

  // Component boxes — pressurization path
  const pressComp = [
    { label: "CO\u2082\nCylinder\n5.9 MPa", x: 0.35 },
    { label: "Victor\nRegulator\n5.5 MPa", x: 1.85 },
    { label: "Air-Driven\nBooster\n28 MPa max", x: 3.35 },
    { label: "Motorized\nNeedle Valve\n(NEW)", x: 4.85, highlight: true },
    { label: "Check\nValve", x: 6.35 },
    { label: "Pressure\nVessel\n28 MPa", x: 7.85 }
  ];

  pressComp.forEach((c, i) => {
    const isNew = c.highlight;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: c.x, y: 1.65, w: 1.35, h: 0.95,
      fill: { color: isNew ? TEAL : NAVY },
      line: { color: isNew ? TEAL : NAVY },
      shadow: makeShadow()
    });
    slide.addText(c.label, {
      x: c.x, y: 1.65, w: 1.35, h: 0.95,
      fontSize: 8.5, bold: isNew, color: WHITE, fontFace: "Calibri",
      align: "center", valign: "middle", margin: 2
    });
    // Arrow between boxes
    if (i < pressComp.length - 1) {
      slide.addShape(pres.shapes.LINE, {
        x: c.x + 1.35, y: 2.12, w: 0.5, h: 0,
        line: { color: GRAY, width: 1.5 }
      });
      slide.addText("\u25B6", {
        x: c.x + 1.6, y: 2.0, w: 0.25, h: 0.25,
        fontSize: 8, color: GRAY, margin: 0
      });
    }
  });

  // Depressurization path
  slide.addText("DEPRESSURIZATION PATH", {
    x: 0.4, y: 2.75, w: 9.2, h: 0.28,
    fontSize: 9, bold: true, color: CORAL, fontFace: "Calibri", margin: 0, charSpacing: 2
  });

  const ventComp = [
    { label: "Pressure\nVessel", x: 7.85 },
    { label: "PWM Vent\nSolenoid\n(NEW)", x: 6.35, highlight: true },
    { label: "Manual\nNeedle Valve\n(flow limiter)", x: 4.85 },
    { label: "Vent to\nFume Hood", x: 3.35 }
  ];

  ventComp.forEach((c, i) => {
    const isNew = c.highlight;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: c.x, y: 3.08, w: 1.35, h: 0.85,
      fill: { color: isNew ? CORAL : "64748B" },
      line: { color: isNew ? CORAL : "64748B" },
      shadow: makeShadow()
    });
    slide.addText(c.label, {
      x: c.x, y: 3.08, w: 1.35, h: 0.85,
      fontSize: 8, color: WHITE, fontFace: "Calibri",
      align: "center", valign: "middle", margin: 2
    });
    if (i < ventComp.length - 1) {
      slide.addShape(pres.shapes.LINE, {
        x: ventComp[i + 1].x + 1.35, y: 3.5, w: 0.5, h: 0,
        line: { color: GRAY, width: 1.5 }
      });
      slide.addText("\u25C0", {
        x: ventComp[i + 1].x + 1.5, y: 3.38, w: 0.25, h: 0.25,
        fontSize: 8, color: GRAY, margin: 0
      });
    }
  });

  // Vertical connector from vessel to vent
  slide.addShape(pres.shapes.LINE, {
    x: 8.52, y: 2.6, w: 0, h: 0.48,
    line: { color: GRAY, width: 1.5, dashType: "dash" }
  });

  // Control loop label
  slide.addText("CONTROL LOOP", {
    x: 0.4, y: 4.05, w: 9.2, h: 0.28,
    fontSize: 9, bold: true, color: NAVY, fontFace: "Calibri", margin: 0, charSpacing: 2
  });

  // Control loop boxes
  const ctrlComp = [
    { label: "Pressure\nTransducer\n4-20mA", x: 7.85 },
    { label: "Raspberry Pi\nController\n(PID)", x: 5.65, highlight: true },
    { label: "Stepper Motor\nMotorized Valve\n(pressurize)", x: 3.45 },
    { label: "PWM Solenoid\n(depressurize)", x: 1.25 }
  ];

  ctrlComp.forEach((c, i) => {
    const isHighlight = c.highlight;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: c.x, y: 4.38, w: 1.8, h: 0.9,
      fill: { color: isHighlight ? NAVY : WHITE },
      line: { color: isHighlight ? NAVY : TEAL, width: isHighlight ? 0 : 1.5 },
      shadow: makeShadow()
    });
    slide.addText(c.label, {
      x: c.x, y: 4.38, w: 1.8, h: 0.9,
      fontSize: 8.5, color: isHighlight ? WHITE : NAVY, fontFace: "Calibri",
      align: "center", valign: "middle", margin: 2
    });
    if (i < ctrlComp.length - 1) {
      slide.addShape(pres.shapes.LINE, {
        x: ctrlComp[i+1].x + 1.8, y: 4.83, w: 0.45, h: 0,
        line: { color: TEAL, width: 1.5 }
      });
      slide.addText("\u25C0", {
        x: ctrlComp[i+1].x + 1.95, y: 4.73, w: 0.25, h: 0.2,
        fontSize: 8, color: TEAL, margin: 0
      });
    }
  });

  // HAL note
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.3, y: 5.3, w: 9.4, h: 0.22,
    fill: { color: LIGHT_TEAL }, line: { color: TEAL, width: 0.5 }
  });
  slide.addText("Hardware Abstraction Layer: same code runs in Windows simulation or on real Raspberry Pi hardware", {
    x: 0.35, y: 5.3, w: 9.3, h: 0.22,
    fontSize: 9, italic: true, color: TEAL, fontFace: "Calibri", align: "center", valign: "middle", margin: 0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 5 — Phase 1: Simulink Digital Twin (light)
// ─────────────────────────────────────────────────────────────────────────────
{
  let slide = pres.addSlide();
  slide.background = { color: CREAM };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.55,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addText("scCO\u2082 Pressure Control System", {
    x: 0.3, y: 0, w: 9.4, h: 0.55,
    fontSize: 10, color: WHITE, fontFace: "Calibri", valign: "middle", margin: 0
  });

  slide.addText("Phase 1: Simulink Digital Twin", {
    x: 0.5, y: 0.65, w: 9, h: 0.5,
    fontSize: 34, bold: true, color: NAVY, fontFace: "Calibri", margin: 0
  });

  // Purpose banner
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.28, w: 9.2, h: 0.38,
    fill: { color: TEAL }, line: { color: TEAL }
  });
  slide.addText("Purpose: Validate control algorithm and tune PID gains before hardware arrives — no risk, no cost", {
    x: 0.5, y: 1.28, w: 9.0, h: 0.38,
    fontSize: 12, bold: true, color: WHITE, fontFace: "Calibri", align: "center", valign: "middle", margin: 0
  });

  // 4 feature rows
  const features = [
    {
      num: "1",
      title: "Simscape Gas & Thermal Library",
      body: "Pre-built CO\u2082 flow blocks — no need to derive equations manually. Connect components like a P&ID diagram."
    },
    {
      num: "2",
      title: "Non-Linear Booster Model",
      body: "Flow \u221D valve_opening \u00D7 \u221A(P\u2099\u2092\u2092\u209C\u2092\u1D49 \u2212 P\u1D65\u1D49\u209B\u209B\u1D49\u2113). As vessel fills, driving pressure shrinks \u2014 PID must compensate."
    },
    {
      num: "3",
      title: "Temperature\u2013Pressure Coupling",
      body: "Compression heating during pressurization + Joule-Thomson cooling during venting. Both modeled realistically."
    },
    {
      num: "4",
      title: "Interactive PID Tuner",
      body: "Drag a slider, watch the 350 kPa/min pressure ramp respond in real time. Find optimal Kp, Ki, Kd visually."
    }
  ];

  features.forEach((f, i) => {
    const y = 1.85 + i * 0.82;
    // Number circle
    slide.addShape(pres.shapes.OVAL, {
      x: 0.4, y: y + 0.07, w: 0.42, h: 0.42,
      fill: { color: TEAL }, line: { color: TEAL }
    });
    slide.addText(f.num, {
      x: 0.4, y: y + 0.07, w: 0.42, h: 0.42,
      fontSize: 14, bold: true, color: WHITE, fontFace: "Calibri",
      align: "center", valign: "middle", margin: 0
    });
    // Title
    slide.addText(f.title, {
      x: 0.95, y: y + 0.04, w: 4.3, h: 0.28,
      fontSize: 13, bold: true, color: NAVY, fontFace: "Calibri", margin: 0
    });
    // Body
    slide.addText(f.body, {
      x: 0.95, y: y + 0.3, w: 8.7, h: 0.38,
      fontSize: 11, color: "475569", fontFace: "Calibri", margin: 0
    });
    // Separator line (not after last)
    if (i < features.length - 1) {
      slide.addShape(pres.shapes.LINE, {
        x: 0.4, y: y + 0.77, w: 9.2, h: 0,
        line: { color: "E2E8F0", width: 0.5 }
      });
    }
  });

  // Output callout
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 5.1, w: 9.2, h: 0.38,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addText("Output \u2192  Validated Kp, Ki, Kd gains saved and transferred directly to Python deployment", {
    x: 0.5, y: 5.1, w: 9.0, h: 0.38,
    fontSize: 12, bold: true, color: WHITE, fontFace: "Calibri", align: "center", valign: "middle", margin: 0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 6 — Temperature & Physics (light)
// ─────────────────────────────────────────────────────────────────────────────
{
  let slide = pres.addSlide();
  slide.background = { color: CREAM };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.55,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addText("scCO\u2082 Pressure Control System", {
    x: 0.3, y: 0, w: 9.4, h: 0.55,
    fontSize: 10, color: WHITE, fontFace: "Calibri", valign: "middle", margin: 0
  });

  slide.addText("Key Physics: Temperature\u2013Pressure Coupling", {
    x: 0.5, y: 0.65, w: 9, h: 0.5,
    fontSize: 30, bold: true, color: NAVY, fontFace: "Calibri", margin: 0
  });

  // 3 scenarios
  const scenarios = [
    {
      num: "1",
      title: "Compression Heating (Pressurizing)",
      color: CORAL,
      lines: [
        "CO\u2082 flowing into the vessel compresses and heats up (adiabatic compression).",
        "Temperature spike \u2192 additional pressure rise: \u0394P/\u0394T \u2248 0.084 MPa/\u00B0C at operating point.",
        "A 2\u00B0C spike \u2192 +0.17 MPa extra pressure on top of flow-driven rise.",
        "PID must be tuned carefully to avoid overcorrecting and oscillating."
      ]
    },
    {
      num: "2",
      title: "INKBIRD Temperature Controller Lag",
      color: TEAL,
      lines: [
        "INKBIRD PID maintains vessel at 60\u00B0C setpoint but has ~15 second response lag.",
        "During rapid pressurization, vessel temperature temporarily overshoots 60\u00B0C.",
        "This transient causes pressure to rise faster than the flow-driven model predicts.",
        "Simulation models INKBIRD as a lagged PI controller for realistic behavior."
      ]
    },
    {
      num: "3",
      title: "Joule-Thomson Cooling (Venting)",
      color: NAVY,
      lines: [
        "CO\u2082 expanding through the vent valve cools significantly (Joule-Thomson effect).",
        "Temperature drop \u2192 additional pressure drop beyond the vented mass alone.",
        "Creates coupled depressurization behavior \u2014 2 MPa/min rate harder to hold.",
        "Depressurization PID duty cycle must compensate for this coupled cooling."
      ]
    }
  ];

  scenarios.forEach((s, i) => {
    const y = 1.3 + i * 1.35;
    // Left color bar
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y: y, w: 0.07, h: 1.15,
      fill: { color: s.color }, line: { color: s.color }
    });
    // Number chip
    slide.addShape(pres.shapes.OVAL, {
      x: 0.57, y: y + 0.05, w: 0.38, h: 0.38,
      fill: { color: s.color }, line: { color: s.color }
    });
    slide.addText(s.num, {
      x: 0.57, y: y + 0.05, w: 0.38, h: 0.38,
      fontSize: 13, bold: true, color: WHITE, fontFace: "Calibri",
      align: "center", valign: "middle", margin: 0
    });
    // Title
    slide.addText(s.title, {
      x: 1.08, y: y + 0.04, w: 8.5, h: 0.33,
      fontSize: 14, bold: true, color: s.color, fontFace: "Calibri", margin: 0
    });
    // Body lines
    slide.addText(s.lines.join("  \u2022  "), {
      x: 1.08, y: y + 0.38, w: 8.5, h: 0.7,
      fontSize: 10.5, color: "334155", fontFace: "Calibri", margin: 0
    });
  });

  // Pre-condition callout
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 5.12, w: 9.2, h: 0.36,
    fill: { color: LIGHT_TEAL }, line: { color: TEAL, width: 1 }
  });
  slide.addText("Pre-condition check: START button is disabled until vessel temperature \u2265 55\u00B0C (CO\u2082 must be supercritical before pressurization)", {
    x: 0.5, y: 5.12, w: 9.0, h: 0.36,
    fontSize: 10.5, bold: true, color: TEAL, fontFace: "Calibri", align: "center", valign: "middle", margin: 0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 7 — Python Control Application (light)
// ─────────────────────────────────────────────────────────────────────────────
{
  let slide = pres.addSlide();
  slide.background = { color: CREAM };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.55,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addText("scCO\u2082 Pressure Control System", {
    x: 0.3, y: 0, w: 9.4, h: 0.55,
    fontSize: 10, color: WHITE, fontFace: "Calibri", valign: "middle", margin: 0
  });

  slide.addText("Phase 2: Python Control Application", {
    x: 0.5, y: 0.65, w: 9, h: 0.5,
    fontSize: 32, bold: true, color: NAVY, fontFace: "Calibri", margin: 0
  });

  // Left column — software modules
  slide.addText("SOFTWARE MODULES", {
    x: 0.4, y: 1.3, w: 5.3, h: 0.28,
    fontSize: 9, bold: true, color: TEAL, fontFace: "Calibri", margin: 0, charSpacing: 2
  });

  const modules = [
    { file: "config.py", desc: "All constants: pressures, rates, PID gains, GPIO pins" },
    { file: "hardware/", desc: "Simulated (Windows) OR Real RPi hardware \u2014 swap one line" },
    { file: "control/", desc: "PID controller, ramp generator, state machine" },
    { file: "logger.py", desc: "CSV logging: timestamp, pressure, temp, state, valve %" },
    { file: "cloud.py", desc: "ThingSpeak upload every 2 sec \u2014 monitor from anywhere" },
    { file: "gui.py", desc: "Tkinter GUI with live pressure & temperature chart" }
  ];

  modules.forEach((m, i) => {
    const y = 1.68 + i * 0.55;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y: y, w: 5.2, h: 0.46,
      fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 }
    });
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y: y, w: 1.35, h: 0.46,
      fill: { color: NAVY }, line: { color: NAVY }
    });
    slide.addText(m.file, {
      x: 0.42, y: y, w: 1.31, h: 0.46,
      fontSize: 9, bold: true, color: WHITE, fontFace: "Consolas",
      align: "center", valign: "middle", margin: 2
    });
    slide.addText(m.desc, {
      x: 1.82, y: y, w: 3.65, h: 0.46,
      fontSize: 10, color: "334155", fontFace: "Calibri", valign: "middle", margin: 4
    });
  });

  // Right column — state machine
  slide.addText("STATE MACHINE", {
    x: 6.05, y: 1.3, w: 3.6, h: 0.28,
    fontSize: 9, bold: true, color: NAVY, fontFace: "Calibri", margin: 0, charSpacing: 2
  });

  const states = [
    { label: "IDLE", color: "64748B" },
    { label: "PRESSURIZE\n350 kPa/min", color: TEAL },
    { label: "HOLD\n\u00B11\u20132%", color: NAVY },
    { label: "DEPRESSURIZE\n2 MPa/min", color: CORAL }
  ];

  states.forEach((s, i) => {
    const y = 1.65 + i * 0.82;
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 6.05, y: y, w: 3.5, h: 0.55,
      fill: { color: s.color }, line: { color: s.color }, rectRadius: 0.08
    });
    slide.addText(s.label, {
      x: 6.05, y: y, w: 3.5, h: 0.55,
      fontSize: 12, bold: true, color: WHITE, fontFace: "Calibri",
      align: "center", valign: "middle", margin: 0
    });
    if (i < states.length - 1) {
      slide.addText("\u25BC", {
        x: 7.55, y: y + 0.57, w: 0.5, h: 0.25,
        fontSize: 11, color: GRAY, align: "center", margin: 0
      });
    }
  });

  // E-stop
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.05, y: 5.05, w: 3.5, h: 0.38,
    fill: { color: CORAL }, line: { color: CORAL }
  });
  slide.addText("E-STOP: cuts all outputs instantly from any state", {
    x: 6.05, y: 5.05, w: 3.5, h: 0.38,
    fontSize: 9.5, bold: true, color: WHITE, fontFace: "Calibri",
    align: "center", valign: "middle", margin: 0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 8 — Control Interface (light)
// ─────────────────────────────────────────────────────────────────────────────
{
  let slide = pres.addSlide();
  slide.background = { color: CREAM };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.55,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addText("scCO\u2082 Pressure Control System", {
    x: 0.3, y: 0, w: 9.4, h: 0.55,
    fontSize: 10, color: WHITE, fontFace: "Calibri", valign: "middle", margin: 0
  });

  slide.addText("Control Interface", {
    x: 0.5, y: 0.65, w: 9, h: 0.5,
    fontSize: 36, bold: true, color: NAVY, fontFace: "Calibri", margin: 0
  });

  // Mock GUI window
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.25, w: 9.2, h: 4.15,
    fill: { color: "2B2B3B" }, line: { color: "1A1A2E", width: 2 },
    shadow: makeShadow()
  });

  // GUI title bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.25, w: 9.2, h: 0.35,
    fill: { color: "1A1A2E" }, line: { color: "1A1A2E" }
  });
  slide.addText("scCO\u2082 Pressure Control System   \u25CF PRESSURIZING", {
    x: 0.55, y: 1.25, w: 8.9, h: 0.35,
    fontSize: 9, color: TEAL, fontFace: "Calibri", valign: "middle", margin: 0
  });

  // Chart area mock
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 1.65, w: 6.4, h: 2.6,
    fill: { color: "1E1E2E" }, line: { color: "333355", width: 1 }
  });
  slide.addText("[ Live Chart: Pressure (MPa) vs Time ]", {
    x: 0.55, y: 1.72, w: 6.3, h: 0.3,
    fontSize: 8, color: "888899", fontFace: "Calibri", align: "center", margin: 0
  });
  // Simulated pressure ramp line
  const chartX = 0.5, chartY = 4.15, chartW = 6.4, chartH = 2.4;
  const points = [];
  for (let i = 0; i <= 20; i++) {
    const px = chartX + 0.15 + (i / 20) * (chartW - 0.3);
    const py = chartY - 0.1 - (i / 20) * 1.6;
    points.push({ x: px, y: py });
  }
  // Draw simulated ramp as a line (use individual short lines)
  for (let i = 0; i < points.length - 1; i++) {
    const dx = points[i+1].x - points[i].x;
    const dy = points[i+1].y - points[i].y;
    const len = Math.sqrt(dx*dx + dy*dy);
    slide.addShape(pres.shapes.LINE, {
      x: points[i].x, y: points[i].y, w: dx, h: dy,
      line: { color: "028090", width: 2 }
    });
  }
  slide.addText("Measured Pressure (MPa)", {
    x: 0.6, y: 4.07, w: 2.5, h: 0.2,
    fontSize: 7, color: TEAL, fontFace: "Calibri", margin: 0
  });
  slide.addShape(pres.shapes.LINE, {
    x: 0.6, y: 4.0, w: 0.35, h: 0,
    line: { color: TEAL, width: 2 }
  });
  slide.addText("Setpoint Ramp", {
    x: 1.3, y: 4.07, w: 2, h: 0.2,
    fontSize: 7, color: CORAL, fontFace: "Calibri", margin: 0
  });
  slide.addShape(pres.shapes.LINE, {
    x: 1.3, y: 4.0, w: 0.35, h: 0,
    line: { color: CORAL, width: 2, dashType: "dash" }
  });

  // Right panel - readings
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 6.95, y: 1.65, w: 2.55, h: 2.6,
    fill: { color: "1E1E2E" }, line: { color: "333355", width: 1 }
  });

  const readings = [
    { label: "PRESSURE", value: "23.85 MPa", color: TEAL },
    { label: "RATE", value: "352 kPa/min", color: WHITE },
    { label: "TEMPERATURE", value: "61.2 \u00B0C", color: CORAL },
    { label: "VALVE", value: "67% open", color: WHITE }
  ];

  readings.forEach((r, i) => {
    const y = 1.73 + i * 0.59;
    slide.addText(r.label, {
      x: 7.05, y: y, w: 2.35, h: 0.2,
      fontSize: 7.5, color: "888899", fontFace: "Calibri", margin: 0, charSpacing: 1
    });
    slide.addText(r.value, {
      x: 7.05, y: y + 0.2, w: 2.35, h: 0.32,
      fontSize: 16, bold: true, color: r.color, fontFace: "Calibri", margin: 0
    });
  });

  // Button row
  const buttons = [
    { label: "START", color: TEAL },
    { label: "HOLD", color: "4A5568" },
    { label: "DEPRESSURIZE", color: NAVY },
    { label: "\u26D4  E-STOP", color: CORAL }
  ];
  const btnW = [1.55, 1.55, 2.05, 1.8];
  let bx = 0.5;
  buttons.forEach((b, i) => {
    slide.addShape(pres.shapes.RECTANGLE, {
      x: bx, y: 4.52, w: btnW[i], h: 0.55,
      fill: { color: b.color }, line: { color: b.color }
    });
    slide.addText(b.label, {
      x: bx, y: 4.52, w: btnW[i], h: 0.55,
      fontSize: 12, bold: true, color: WHITE, fontFace: "Calibri",
      align: "center", valign: "middle", margin: 0
    });
    bx += btnW[i] + 0.25;
  });

  // Note
  slide.addText("START disabled until vessel temperature \u2265 55\u00B0C", {
    x: 0.5, y: 5.1, w: 9.0, h: 0.25,
    fontSize: 9, italic: true, color: GRAY, fontFace: "Calibri", align: "center", margin: 0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 9 — Cloud Monitoring (light)
// ─────────────────────────────────────────────────────────────────────────────
{
  let slide = pres.addSlide();
  slide.background = { color: CREAM };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.55,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addText("scCO\u2082 Pressure Control System", {
    x: 0.3, y: 0, w: 9.4, h: 0.55,
    fontSize: 10, color: WHITE, fontFace: "Calibri", valign: "middle", margin: 0
  });

  slide.addText("Remote Monitoring \u2014 Free Cloud Dashboard", {
    x: 0.5, y: 0.65, w: 9, h: 0.5,
    fontSize: 30, bold: true, color: NAVY, fontFace: "Calibri", margin: 0
  });

  // Service banner
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 1.28, w: 9.2, h: 0.38,
    fill: { color: TEAL }, line: { color: TEAL }
  });
  slide.addText("ThingSpeak by MathWorks  \u2014  Free Tier: 3 Million Messages/Year  \u2014  No hardware modifications required", {
    x: 0.5, y: 1.28, w: 9.0, h: 0.38,
    fontSize: 12, bold: true, color: WHITE, fontFace: "Calibri", align: "center", valign: "middle", margin: 0
  });

  // Two column layout
  // Left: What you see
  slide.addText("WHAT YOU SEE FROM ANYWHERE", {
    x: 0.4, y: 1.82, w: 4.5, h: 0.28,
    fontSize: 9, bold: true, color: TEAL, fontFace: "Calibri", margin: 0, charSpacing: 2
  });

  const seeItems = [
    { icon: "\u{1F4C8}", label: "Live pressure and temperature charts" },
    { icon: "\u{1F7E2}", label: "Current experiment state (IDLE / PRESSURIZING / HOLDING / DEPRESSURIZING)" },
    { icon: "\u{1F514}", label: "Email alert: \"Experiment complete\" when IDLE state reached" },
    { icon: "\u26A0\uFE0F", label: "Email alert: \"Pressure exceeded limit\" if safety threshold hit" },
    { icon: "\u{1F4BE}", label: "Full data history — download CSV directly from dashboard" }
  ];

  seeItems.forEach((item, i) => {
    const y = 2.2 + i * 0.56;
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y: y, w: 4.4, h: 0.45,
      fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 }
    });
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y: y, w: 0.06, h: 0.45,
      fill: { color: TEAL }, line: { color: TEAL }
    });
    slide.addText(item.label, {
      x: 0.58, y: y, w: 4.1, h: 0.45,
      fontSize: 10.5, color: "334155", fontFace: "Calibri", valign: "middle", margin: 4
    });
  });

  // Right: MATLAB integration + Setup
  slide.addText("MATLAB INTEGRATION", {
    x: 5.2, y: 1.82, w: 4.4, h: 0.28,
    fontSize: 9, bold: true, color: NAVY, fontFace: "Calibri", margin: 0, charSpacing: 2
  });

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 2.2, w: 4.4, h: 1.5,
    fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 },
    shadow: makeShadow()
  });
  slide.addText([
    { text: "Data flows directly from the experiment into MATLAB\n\n", options: { bold: true } },
    { text: "thingSpeakRead() pulls all channels by experiment ID — no CSV export, no manual steps.\n\n", options: {} },
    { text: "Analyze pressure ramp accuracy, temperature correlation, and PID performance directly in MATLAB.", options: {} }
  ], {
    x: 5.3, y: 2.25, w: 4.2, h: 1.4,
    fontSize: 11, color: "334155", fontFace: "Calibri"
  });

  // Setup note
  slide.addText("ONE-TIME SETUP", {
    x: 5.2, y: 3.82, w: 4.4, h: 0.28,
    fontSize: 9, bold: true, color: NAVY, fontFace: "Calibri", margin: 0, charSpacing: 2
  });
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 5.2, y: 4.15, w: 4.4, h: 0.7,
    fill: { color: LIGHT_TEAL }, line: { color: TEAL, width: 1 }
  });
  slide.addText("Create free account at thingspeak.com \u2192 get API key \u2192 paste into config.py\n5 minutes. No credit card. Works in simulation mode on Windows too.", {
    x: 5.3, y: 4.15, w: 4.2, h: 0.7,
    fontSize: 10.5, color: TEAL, fontFace: "Calibri", valign: "middle", margin: 6
  });

  // Big stat
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.4, y: 5.1, w: 4.4, h: 0.35,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addText("$0 cost  \u2022  No hardware changes  \u2022  Works from any device, anywhere", {
    x: 0.5, y: 5.1, w: 4.2, h: 0.35,
    fontSize: 10.5, bold: true, color: WHITE, fontFace: "Calibri", align: "center", valign: "middle", margin: 0
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 10 — Timeline (light)
// ─────────────────────────────────────────────────────────────────────────────
{
  let slide = pres.addSlide();
  slide.background = { color: CREAM };

  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.55,
    fill: { color: NAVY }, line: { color: NAVY }
  });
  slide.addText("scCO\u2082 Pressure Control System", {
    x: 0.3, y: 0, w: 9.4, h: 0.55,
    fontSize: 10, color: WHITE, fontFace: "Calibri", valign: "middle", margin: 0
  });

  slide.addText("Implementation Timeline", {
    x: 0.5, y: 0.65, w: 9, h: 0.5,
    fontSize: 36, bold: true, color: NAVY, fontFace: "Calibri", margin: 0
  });

  // Note
  slide.addText("Software development proceeds in parallel with hardware procurement \u2014 no blocking dependencies.", {
    x: 0.5, y: 1.22, w: 9.0, h: 0.3,
    fontSize: 11, italic: true, color: GRAY, fontFace: "Calibri", margin: 0
  });

  const phases = [
    {
      weeks: "Weeks 1\u20132",
      title: "Phase 1: Simulink Digital Twin",
      items: ["Build Simscape plant model (CO\u2082 vessel, valve, thermal)", "Tune PID using Simulink PID Tuner", "Validate 350 kPa/min ramp and 2 MPa/min depress rates", "Export Kp, Ki, Kd to configuration file"],
      color: TEAL
    },
    {
      weeks: "Weeks 3\u20134",
      title: "Phase 2: Python App Development",
      items: ["Build hardware abstraction layer (sim + RPi)", "Implement PID, state machine, ramp generator", "Develop Tkinter GUI with live pressure/temperature chart", "Add CSV logging and ThingSpeak cloud upload"],
      color: NAVY
    },
    {
      weeks: "Week 5",
      title: "Integration & Testing (Windows Simulation)",
      items: ["Full end-to-end test in simulation mode", "Verify all safety interlocks (E-stop, watchdog, limits)", "Validate cloud monitoring and data logging", "Document setup and operating procedures"],
      color: CORAL
    },
    {
      weeks: "On Hardware Arrival",
      title: "RPi Deployment & CO\u2082 Testing",
      items: ["Wire RPiHardware module to real sensors and actuators", "Initial low-pressure N\u2082 wiring test", "CO\u2082 tests: verify ramp accuracy, fine-tune PID", "Full 28 MPa validation run"],
      color: "64748B"
    }
  ];

  phases.forEach((p, i) => {
    const y = 1.62 + i * 0.95;
    // Week chip
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 0.4, y: y, w: 1.5, h: 0.8,
      fill: { color: p.color }, line: { color: p.color }
    });
    slide.addText(p.weeks, {
      x: 0.4, y: y, w: 1.5, h: 0.8,
      fontSize: 11, bold: true, color: WHITE, fontFace: "Calibri",
      align: "center", valign: "middle", margin: 3
    });
    // Content
    slide.addShape(pres.shapes.RECTANGLE, {
      x: 2.0, y: y, w: 7.6, h: 0.8,
      fill: { color: WHITE }, line: { color: "E2E8F0", width: 1 }
    });
    slide.addText(p.title, {
      x: 2.12, y: y + 0.04, w: 7.3, h: 0.28,
      fontSize: 12, bold: true, color: p.color, fontFace: "Calibri", margin: 0
    });
    slide.addText(p.items.join("   \u2022   "), {
      x: 2.12, y: y + 0.32, w: 7.3, h: 0.38,
      fontSize: 9.5, color: "475569", fontFace: "Calibri", margin: 0
    });
    // Connector line (except last)
    if (i < phases.length - 1) {
      slide.addShape(pres.shapes.LINE, {
        x: 1.15, y: y + 0.8, w: 0, h: 0.15,
        line: { color: GRAY, width: 1, dashType: "dash" }
      });
    }
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// SLIDE 11 — Next Steps (dark)
// ─────────────────────────────────────────────────────────────────────────────
{
  let slide = pres.addSlide();
  slide.background = { color: NAVY };

  // Left accent
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 0.18, h: 5.625,
    fill: { color: TEAL }, line: { color: TEAL }
  });

  // Bottom coral bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.1, w: 10, h: 0.525,
    fill: { color: CORAL }, line: { color: CORAL }
  });

  slide.addText("Next Steps", {
    x: 0.4, y: 0.45, w: 9.2, h: 0.6,
    fontSize: 42, bold: true, color: WHITE, fontFace: "Calibri", margin: 0
  });

  const steps = [
    { num: "1", text: "Create free ThingSpeak account at thingspeak.com and get API key (5 minutes)" },
    { num: "2", text: "Confirm MATLAB Simscape Gas/Thermal toolbox is installed (UMich license)" },
    { num: "3", text: "Begin Simulink model build \u2014 Phase 1 (Weeks 1\u20132)" },
    { num: "4", text: "Order hardware: motorized valve, HP solenoid, pressure transducer (see BOM)" },
    { num: "5", text: "Develop Python app in simulation mode on Windows in parallel (Weeks 3\u20134)" }
  ];

  steps.forEach((s, i) => {
    const y = 1.22 + i * 0.7;
    // Circle
    slide.addShape(pres.shapes.OVAL, {
      x: 0.4, y: y + 0.04, w: 0.48, h: 0.48,
      fill: { color: TEAL }, line: { color: TEAL }
    });
    slide.addText(s.num, {
      x: 0.4, y: y + 0.04, w: 0.48, h: 0.48,
      fontSize: 16, bold: true, color: WHITE, fontFace: "Calibri",
      align: "center", valign: "middle", margin: 0
    });
    slide.addText(s.text, {
      x: 1.05, y: y, w: 8.5, h: 0.55,
      fontSize: 13.5, color: "CADCFC", fontFace: "Calibri", valign: "middle", margin: 0
    });
  });

  slide.addText("Questions?", {
    x: 0.4, y: 4.62, w: 9.2, h: 0.4,
    fontSize: 18, italic: true, color: CORAL, fontFace: "Calibri", margin: 0
  });

  // Bottom bar text
  slide.addText("Taub Research Group   |   University of Michigan MSE   |   March 2026", {
    x: 0.25, y: 5.12, w: 9.5, h: 0.42,
    fontSize: 11, color: WHITE, fontFace: "Calibri", align: "center", valign: "middle", margin: 0
  });
}

// Save
pres.writeFile({ fileName: "C:/Users/Vijai Venkatesh/Desktop/Pressure Regulation System/scCO2_Software_Plan_Presentation.pptx" })
  .then(() => console.log("Presentation saved successfully."))
  .catch(err => console.error("Error:", err));
