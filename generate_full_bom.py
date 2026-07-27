#!/usr/bin/env python3
"""Generate the scCO2 system Bill of Materials as a formatted Excel file.

Items to purchase only — already-owned equipment and optional windowed vessel
are excluded. All links are direct product page URLs (July 2026).

Key safety notes:
  - Tubing: must be 0.065" wall seamless annealed (0.035" wall ~3,200 PSI — insufficient)
  - Relief valve: SS-4R3A (HIGH pressure, 6,000 PSI). SS-RL3S4 is LOW pressure (225 PSI max)
  - Relay: must accept 3.3V GPIO trigger (RPi optocoupler module)
  - Ball valves: only 1 needed (HiP valve on booster + SS-3NRM4 on vessel already owned)
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

NAVY  = "1E2761"
WHITE = "FFFFFF"


ROWS = [
    # ── 1. Motorized Needle Valve ─────────────────────────────────────────────
    dict(section="1. Motorized Needle Valve",
         item="Needle valve body", part="SS-1RS4",
         link_label="SS-1RS4",
         desc="Swagelok needle valve, regulating stem, 1/4\" tube compression",
         spec="316SS, 5,000 PSI @ 100°F, Cv = 0.37",
         vendor="Swagelok authorized distributor",
         qty=1, unit_price=300.00,
         link="https://products.swagelok.com/en/c/straight-pattern-regulating-stem/p/SS-1RS4?q=SS-1RS4"),
    dict(section="1. Motorized Needle Valve",
         item="Shaft coupler (NEMA 17 to valve stem)",
         part="5mm × 6.35mm flexible shaft coupler",
         link_label="Flexible Shaft Coupler",
         desc="Couples NEMA 17 stepper motor (5mm shaft) to SS-1RS4 valve stem (1/4\" = 6.35mm)",
         spec="Aluminum flexible coupling, 5mm × 6.35mm bores",
         vendor="Amazon",
         qty=1, unit_price=9.99,
         link="https://www.amazon.com/s?k=5mm+to+6.35mm+flexible+shaft+coupler"),

    # ── 2. Check Valve ────────────────────────────────────────────────────────
    dict(section="2. Check Valve",
         item="Check valve", part="SS-CHS4-5",
         link_label="SS-CHS4-5",
         desc="Swagelok check valve, 1/4\" tube fitting, 5 PSI cracking pressure",
         spec="316SS, 6,000 PSI (NOT SS-4C — that is only 3,000 PSI)",
         vendor="Swagelok authorized distributor",
         qty=1, unit_price=120.00,
         link="https://products.swagelok.com/en/c/fixed-pressure/p/SS-CHS4-5"),

    # ── 3. Manual Ball Valve ──────────────────────────────────────────────────
    dict(section="3. Manual Ball Valve",
         item="Ball valve — vessel inlet isolation", part="SS-83KS4",
         link_label="SS-83KS4",
         desc="Swagelok 83 series ball valve, 1/4\" tube fitting, PCTFE seats, CO2 compatible\n"
              "Only 1 needed — HiP valve on booster covers supply shutoff;\n"
              "SS-3NRM4 already on vessel outlet covers vent isolation",
         spec="316SS, 6,000 PSI (NOT SS-43GS4 — that is only 3,000 PSI)",
         vendor="Swagelok authorized distributor",
         qty=1, unit_price=407.00,
         link="https://products.swagelok.com/en/c/2-way-straight-pattern/p/SS-83KS4"),

    # ── 4. Stainless Tubing ───────────────────────────────────────────────────
    dict(section="4. Stainless Tubing",
         item="SS tubing, 1/4\" OD × 0.065\" wall", part="5LVR1",
         link_label="5LVR1 Seamless SS Tubing",
         desc="Seamless 316SS tubing, 6 ft length — ASTM A213 + A269, annealed\n"
              "Buy 3 pieces (18 ft total); system needs ~10 ft\n"
              "Must be seamless annealed (NOT welded) for Swagelok compression fittings\n"
              "Amazon FITOK B0BB1122VJ is only 0.035\" wall (~3,200 PSI) — NOT safe",
         spec="316SS seamless annealed, 1/4\" OD × 0.065\" wall, 6 ft per piece\n"
              "Rated 8,125 PSI @ 72°F — 2x safety margin over 4,061 PSI operating pressure",
         vendor="Grainger",
         qty=3, unit_price=36.43,
         link="https://www.grainger.com/search?searchQuery=5LVR1"),

    # ── 5. Compression Fittings ───────────────────────────────────────────────
    dict(section="5. Compression Fittings",
         item="Union (straight)", part="SS-400-6",
         link_label="SS-400-6",
         desc="Swagelok union fitting, 1/4\" tube OD",
         spec="316SS, 5,100 PSI rated",
         vendor="Swagelok authorized distributor",
         qty=4, unit_price=15.00,
         link="https://products.swagelok.com/en/c/straights/p/SS-400-6?q=SS-400-6"),
    dict(section="5. Compression Fittings",
         item="90 degree elbow", part="SS-400-9",
         link_label="SS-400-9",
         desc="Swagelok 90 degree elbow fitting, 1/4\" tube OD",
         spec="316SS, 5,100 PSI rated",
         vendor="Swagelok authorized distributor",
         qty=3, unit_price=20.00,
         link="https://products.swagelok.com/en/c/90-degree-elbows/p/SS-400-9?q=SS-400-9"),
    dict(section="5. Compression Fittings",
         item="Tee", part="SS-400-3",
         link_label="SS-400-3",
         desc="Swagelok tee fitting, 1/4\" tube OD",
         spec="316SS, 5,100 PSI rated",
         vendor="Swagelok authorized distributor",
         qty=2, unit_price=28.00,
         link="https://products.swagelok.com/en/c/tees/p/SS-400-3?q=SS-400-3"),
    dict(section="5. Compression Fittings",
         item="End cap", part="SS-400-C",
         link_label="SS-400-C",
         desc="Swagelok end cap fitting, 1/4\" tube OD",
         spec="316SS, 5,100 PSI rated",
         vendor="Swagelok authorized distributor",
         qty=3, unit_price=10.00,
         link="https://products.swagelok.com/en/c/caps/p/SS-400-C?q=SS-400-C"),

    # ── 6. Relief Valve & Vent ────────────────────────────────────────────────
    dict(section="6. Relief Valve & Vent",
         item="Relief valve", part="SS-4R3A",
         link_label="SS-4R3A",
         desc="Swagelok HIGH-PRESSURE proportional relief valve, 1/4\" tube compression\n"
              "Specify set pressure ~4,350 PSI (30 MPa) when ordering from distributor\n"
              "SS-RL3S4 is LOW-PRESSURE only (max 225 PSI) — DANGEROUS for this system",
         spec="316SS, 1/4\" tube, rated to 6,000 PSI\n"
              "Set pressure: 4,350 PSI (30 MPa) — between operating P (4,061 PSI) and MAWP (4,999 PSI)",
         vendor="Swagelok authorized distributor",
         qty=1, unit_price=250.00,
         link="https://products.swagelok.com/en/c/high-pressure-relief-valve/p/SS-4R3A?q=SS-4R3A"),
    dict(section="6. Relief Valve & Vent",
         item="Vent solenoid valve (automated depressurization)",
         part="Parker Series 34 HP / Asco 8290 HP",
         link_label="HP Solenoid Valve",
         desc="Normally-closed 24VDC solenoid valve, 1/4\" tube or NPT, HIGH-pressure rated\n"
              "Driven by RPi GPIO 18 via relay — opens automatically during DEPRESSURIZE state\n"
              "MUST be rated >= 6,000 PSI — standard solenoids (150-300 PSI) will fail catastrophically",
         spec="316SS body, NC (fail-safe closed), 24VDC coil, 1/4\" process connection\n"
              "Candidates: Parker Series 34 HP, Asco 8290 HP, HiP solenoid valve",
         vendor="Parker / Asco / High Pressure Equipment",
         qty=1, unit_price=500.00,
         link="https://www.parker.com/us/en/search.html?q=high+pressure+solenoid+valve+24VDC+NC+6000+PSI"),
    dict(section="6. Relief Valve & Vent",
         item="PTFE thread tape", part="34P209",
         link_label="34P209 PTFE Tape",
         desc="PTFE sealing tape for NPT thread connections",
         spec="High-pressure / high-temp rated",
         vendor="Grainger",
         qty=1, unit_price=5.00,
         link="https://www.grainger.com/search?searchQuery=34P209"),

    # ── 7. Sensors ────────────────────────────────────────────────────────────
    dict(section="7. Sensors",
         item="Pressure transducer", part="5DEK9",
         link_label="5DEK9 Pressure Transducer",
         desc="Ashcroft G2, 0-5000 PSI, 4-20 mA output, 316SS wetted parts, IP67\n"
              "Grainger item 5DEK9 — Mfr model G17M0242F25000#\n"
              "Do NOT order K4708 — that is the 1-5V DC output version, wrong for 4-20mA wiring",
         spec="4-20 mA → 1-5 V via 250 ohm shunt resistor into ADS1115 A0",
         vendor="Grainger",
         qty=1, unit_price=230.00,
         link="https://www.grainger.com/product/ASHCROFT-Pressure-Transmitter-0-psi-5DEK9"),

    # ── 8. Electronics & Control ──────────────────────────────────────────────
    dict(section="8. Electronics & Control",
         item="Raspberry Pi 4 — CanaKit Starter Pro Kit (4 GB)", part="B07V5JTMV9",
         link_label="CanaKit RPi 4 Starter Kit",
         desc="CanaKit Starter Pro Kit: RPi4 4GB + case + 3.5A PSU + 32GB SD card + heatsinks\n"
              "SD card is INCLUDED — do NOT buy separate microSD",
         spec="4 GB RAM, includes 32GB pre-loaded SD card, case, power supply",
         vendor="Amazon — CanaKit",
         qty=1, unit_price=99.99,
         link="https://www.amazon.com/CanaKit-Raspberry-4GB-Starter-Kit/dp/B07V5JTMV9"),
    dict(section="8. Electronics & Control",
         item="ADS1115 16-bit I2C ADC module", part="B0DP43DDZG",
         link_label="ADS1115 ADC Module",
         desc="Reads pressure transducer (A0) and temperature sensor (A1) via I2C\n"
              "Qoroos 3-pack — only 1 needed, extras are spares",
         spec="16-bit resolution, I2C interface, Raspberry Pi compatible",
         vendor="Amazon — Qoroos (3-pack)",
         qty=1, unit_price=12.99,
         link="https://www.amazon.com/Qoroos-Converter-Programmable-Amplifier-Development/dp/B0DP43DDZG"),
    dict(section="8. Electronics & Control",
         item="NEMA 17 stepper motor", part="B00PNEQKC0",
         link_label="NEMA 17 Stepper Motor",
         desc="Actuates the motorized needle valve via shaft coupler",
         spec="200 steps/rev, bipolar, NEMA 17 frame, 5mm shaft",
         vendor="Amazon — STEPPERONLINE",
         qty=1, unit_price=15.99,
         link="https://www.amazon.com/STEPPERONLINE-Stepper-Bipolar-Connector-compatible/dp/B00PNEQKC0"),
    dict(section="8. Electronics & Control",
         item="A4988 stepper driver", part="B07BND65C8",
         link_label="A4988 Stepper Driver",
         desc="Drives NEMA 17 at 1/16 microstepping; GPIO 17 STEP, 27 DIR, 22 EN",
         spec="1/16 microstepping driver module",
         vendor="Amazon — HiLetgo",
         qty=1, unit_price=7.99,
         link="https://www.amazon.com/HiLetgo-Stepstick-Stepper-Printer-Compatible/dp/B07BND65C8"),
    dict(section="8. Electronics & Control",
         item="Relay module — RPi-compatible (3.3V trigger)", part="B095YD3732",
         link_label="AEDIKO Relay Module",
         desc="AEDIKO 1-channel optocoupler-isolated relay module\n"
              "RPi GPIO 18 (3.3V) triggers relay → switches 24VDC to solenoid\n"
              "GAEYAELE B07DYLKH74 requires 24VDC trigger — NOT compatible with RPi 3.3V GPIO",
         spec="5V coil, optocoupler isolated, accepts 3.3V RPi GPIO trigger, 1-channel",
         vendor="Amazon — AEDIKO",
         qty=1, unit_price=9.99,
         link="https://www.amazon.com/AEDIKO-Channel-Optocoupler-Isolation-Support/dp/B095YD3732"),
    dict(section="8. Electronics & Control",
         item="Jumper wires assorted kit", part="Dupont Jumper Wires",
         link_label="Jumper Wires Kit",
         desc="Male-to-female and male-to-male jumper wires for GPIO connections",
         spec="120-piece assorted: male-to-male + male-to-female",
         vendor="Amazon",
         qty=1, unit_price=6.99,
         link="https://www.amazon.com/s?k=120+piece+jumper+wire+kit+male+female"),
    dict(section="8. Electronics & Control",
         item="DIN rail power supply, 24VDC 50W", part="33NT20",
         link_label="33NT20 DIN Rail PSU",
         desc="Dayton DIN rail PSU — powers relay, solenoid, and sensor circuits",
         spec="24VDC, 50W output",
         vendor="Grainger",
         qty=1, unit_price=58.00,
         link="https://www.grainger.com/search?searchQuery=33NT20"),
]

SECTION_COLORS = {
    "1. Motorized Needle Valve": "E0F4F7",
    "2. Check Valve": "FFF3E0",
    "3. Manual Ball Valve": "E8EAF6",
    "4. Stainless Tubing": "F1F8E9",
    "5. Compression Fittings": "FCE4EC",
    "6. Relief Valve & Vent": "FFEBEE",
    "7. Sensors": "E3F2FD",
    "8. Electronics & Control": "FFF9C4",
}


def style_data_row(ws, row_idx, n_cols, fill_color, border):
    fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
    for col in range(1, n_cols + 1):
        cell = ws.cell(row=row_idx, column=col)
        cell.fill = fill
        cell.border = border
        cell.font = Font(size=9.5, name="Calibri")
        cell.alignment = Alignment(vertical="center", wrap_text=True)


def build_bom(output_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Full BOM"

    headers = ["Section", "Item", "Part Number", "Description", "Spec / Rating",
               "Vendor", "Qty", "Unit Price", "Line Total", "Direct Product Link"]
    ws.append(headers)

    header_fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
    header_font = Font(color=WHITE, bold=True, size=10, name="Calibri")
    for col in range(1, len(headers) + 1):
        c = ws.cell(row=1, column=col)
        c.fill = header_fill
        c.font = header_font
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    thin = Side(style="thin", color="CCCCCC")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)

    total = 0.0
    row_idx = 2

    for r in ROWS:
        line_total = r["qty"] * r["unit_price"]
        total += line_total

        ws.append([
            r["section"], r["item"], r["part"], r["desc"], r["spec"],
            r["vendor"], r["qty"], r["unit_price"], line_total,
            r.get("link_label", r["part"])
        ])
        style_data_row(ws, row_idx, len(headers), SECTION_COLORS[r["section"]], border)
        ws.cell(row=row_idx, column=8).number_format = "$#,##0.00"
        ws.cell(row=row_idx, column=9).number_format = "$#,##0.00"

        link_cell = ws.cell(row=row_idx, column=10)
        link_cell.hyperlink = r["link"]
        link_cell.value = r.get("link_label", r["part"])
        link_cell.font = Font(size=9.5, name="Calibri", color="0563C1", underline="single")
        row_idx += 1

    # ── Total row ─────────────────────────────────────────────────────────────
    ws.append(["", "", "", "", "", "", "", "TOTAL", total, ""])
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=row_idx, column=col)
        cell.font = Font(bold=True, size=11, name="Calibri", color=WHITE)
        cell.fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
        cell.border = border
    ws.cell(row=row_idx, column=9).number_format = "$#,##0.00"

    # Column widths
    widths = [24, 32, 20, 44, 38, 26, 6, 12, 12, 28]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.freeze_panes = "A2"
    ws.row_dimensions[1].height = 32

    # ── Notes sheet ────────────────────────────────────────────────────────────
    notes = wb.create_sheet("Notes & Safety")
    notes_data = [
        ["scCO2 System — Purchase List Notes & Safety Corrections"],
        [""],
        ["This BOM lists only items to purchase. Already-owned equipment:"],
        ["  HiP valve on booster outlet — covers supply shutoff position (saves ~$407)"],
        ["  Swagelok SS-3NRM4 on vessel outlet — covers vent isolation (saves ~$407)"],
        ["  Duro United 0-5000 PSI gauge on vessel — visual reference (saves ~$100+)"],
        ["  PARR 2302HC vessel, HII 5G-TD booster, INKBIRD temp controller, gas cylinders"],
        [""],
        ["IMPORTANT: SS-3NRM4 MUST remain OPEN during automated operation."],
        ["  Solenoid SV-1 controls automated venting. Closing SS-3NRM4 blocks it."],
        [""],
        ["CRITICAL SAFETY CORRECTIONS:"],
        [""],
        ["1. RELIEF VALVE — SS-4R3A, not SS-RL3S4"],
        ["   SS-RL3S4 max set pressure = 225 PSI. System operates at 4,061 PSI."],
        ["   SS-4R3A is rated 6,000 PSI. Specify set pressure 4,350 PSI when ordering."],
        [""],
        ["2. TUBING — Grainger 5LVR1 (seamless, 0.065\" wall, 8,125 PSI)"],
        ["   Amazon FITOK B0BB1122VJ is 0.035\" wall (~3,200 PSI) — NOT safe."],
        ["   Must be SEAMLESS (not welded) for Swagelok compression fittings."],
        [""],
        ["3. RELAY — AEDIKO B095YD3732 (optocoupler, 3.3V trigger compatible)"],
        ["   GAEYAELE B07DYLKH74 requires 24VDC trigger — will NOT work with RPi GPIO."],
        [""],
        ["4. PRESSURE TRANSDUCER — 5DEK9 (4-20 mA output)"],
        ["   K4708 has 1-5V DC output — wrong type for the 250-ohm shunt wiring."],
        [""],
        ["5. VENT SOLENOID — Must be rated >= 6,000 PSI"],
        ["   Standard solenoids (150-300 PSI) will rupture at 28 MPa operating pressure."],
        [""],
        ["Why exact Swagelok part numbers matter:"],
        ["  SS-CHS4-5: 6,000 PSI. SS-4C looks similar but is only 3,000 PSI."],
        ["  SS-83KS4: 6,000 PSI. SS-43GS4 looks similar but is only 3,000 PSI."],
        ["  SS-1RS4: 5,000 PSI @ 100F — confirmed suitable for 4,061 PSI at 60C."],
        [""],
        ["Swagelok and Parker/Asco prices are estimates — get distributor quotes."],
        ["Amazon and Grainger prices are as of July 2026."],
    ]
    for row in notes_data:
        notes.append(row)
    notes["A1"].font = Font(bold=True, size=14, color=NAVY)
    notes.column_dimensions["A"].width = 115
    for r in range(3, len(notes_data) + 1):
        notes.cell(row=r, column=1).font = Font(size=10)
        notes.cell(row=r, column=1).alignment = Alignment(wrap_text=True)

    wb.save(output_path)
    print(f"BOM written to: {output_path}")
    print(f"  Total (items to purchase): ${total:,.2f}")


if __name__ == "__main__":
    build_bom("/home/user/pressure-regulation-system/scCO2_Full_Bill_of_Materials.xlsx")
