#!/usr/bin/env python3
"""Generate the COMPLETE scCO2 system Bill of Materials as a formatted Excel file.

Covers: high-pressure fluid system, electronics/control, sensors, already-owned
equipment, and optional windowed vessel.

Links use each vendor's standard public search-page URL format (not guessed
deep product URLs), so they keep working even if a vendor reorganizes their
catalog. NOTE: automated link verification was not possible in this sandboxed
environment (outbound fetches return 403 for all sites, including Wikipedia),
so spot-check a few links yourself after opening the file.
"""

from urllib.parse import quote_plus

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

NAVY  = "1E2761"
WHITE = "FFFFFF"
GRAY  = "6C757D"


def search_url(vendor, query):
    q = quote_plus(query)
    vendors = {
        "mcmaster":  f"https://www.mcmaster.com/products/?Ntt={q}",
        "amazon":    f"https://www.amazon.com/s?k={q}",
        "walmart":   f"https://www.walmart.com/search?q={q}",
        "radwell":   f"https://www.radwell.com/en-US/Search?searchTerm={q}",
        "idealvac":  f"https://www.idealvac.com/search.aspx?find={q}",
        "ebay":      f"https://www.ebay.com/sch/i.html?_nkw={q}",
        "swagelok":  f"https://www.swagelok.com/en/search?text={q}",
        "grainger":  f"https://www.grainger.com/search?searchQuery={q}",
        "parker":    f"https://www.parker.com/us/en/search.html?q={q}",
        "adafruit":  f"https://www.adafruit.com/?q={q}",
        "digikey":   f"https://www.digikey.com/en/products/result?keywords={q}",
        "sitec":     f"https://www.sitec-ag.ch/?s={q}",
        "autoclave": f"https://www.autoclaveengineers.com/search/?q={q}",
        "hip":       f"https://www.highpressure.com/?s={q}",
    }
    return vendors[vendor]


ROWS = [
    # ── 1. Motorized Needle Valve ─────────────────────────────────────────────
    dict(section="1. Motorized Needle Valve",
         item="Needle valve body", part="SS-1RS4",
         desc="Swagelok needle valve, regulating stem, 1/4\" tube compression",
         spec="316SS, 5,000 PSI, Cv = 0.37",
         vendor="idealvac.com / Swagelok distributor",
         qty=1, unit_price=300.00,
         search_vendor="idealvac", search_query="Swagelok SS-1RS4 needle valve"),
    dict(section="1. Motorized Needle Valve",
         item="Shaft coupler (NEMA 17 to valve stem)",
         part="5mm to 1/4\" flexible shaft coupler",
         desc="Couples existing NEMA 17 stepper directly to valve stem",
         spec="Aluminum flexible coupling, 5mm x 1/4\"",
         vendor="Amazon",
         qty=1, unit_price=10.00,
         search_vendor="amazon", search_query="flexible shaft coupler 5mm to 1/4 inch NEMA 17"),

    # ── 2. Check Valve ────────────────────────────────────────────────────────
    dict(section="2. Check Valve",
         item="Check valve", part="SS-CHS4-5",
         desc="Swagelok check valve, 1/4\" tube fitting, 5 PSI cracking pressure",
         spec="316SS, 6,000 PSI (NOT SS-4C — that is only 3,000 PSI)",
         vendor="Amazon / Radwell.com",
         qty=1, unit_price=100.00,
         search_vendor="amazon", search_query="Swagelok SS-CHS4-5 check valve"),

    # ── 3. Manual Ball Valves ─────────────────────────────────────────────────
    dict(section="3. Manual Ball Valves",
         item="Ball valve", part="SS-83KS4",
         desc="Swagelok 83 series ball valve, 1/4\" tube fitting, PCTFE seats, CO2 compatible",
         spec="316SS, 6,000 PSI (NOT SS-43GS4 — that is only 3,000 PSI)",
         vendor="Radwell.com / eBay (surplus)",
         qty=3, unit_price=407.00,
         search_vendor="radwell", search_query="Swagelok SS-83KS4 ball valve"),

    # ── 4. Stainless Tubing ───────────────────────────────────────────────────
    dict(section="4. Stainless Tubing",
         item="SS tubing, 1/4\" OD x 0.065\" wall", part="SS-T4-S-065-20",
         desc="Swagelok seamless 316SS tubing, 20 ft minimum order",
         spec="316SS seamless, 1/4\" OD x 0.065\" wall, 20 ft",
         vendor="mcmaster.com",
         qty=1, unit_price=120.00,
         search_vendor="mcmaster", search_query="316SS tubing 1/4 OD 0.065 wall"),

    # ── 5. Compression Fittings ───────────────────────────────────────────────
    dict(section="5. Compression Fittings",
         item="Union (straight)", part="SS-400-6",
         desc="Swagelok union fitting, 1/4\" tube OD",
         spec="316SS, 5,100 PSI rated",
         vendor="Amazon / Walmart",
         qty=4, unit_price=15.00,
         search_vendor="amazon", search_query="Swagelok SS-400-6 union fitting"),
    dict(section="5. Compression Fittings",
         item="90 degree elbow", part="SS-400-9",
         desc="Swagelok 90 degree elbow fitting, 1/4\" tube OD",
         spec="316SS, 5,100 PSI rated",
         vendor="Amazon / Walmart",
         qty=3, unit_price=20.00,
         search_vendor="amazon", search_query="Swagelok SS-400-9 elbow fitting"),
    dict(section="5. Compression Fittings",
         item="Tee", part="SS-400-3",
         desc="Swagelok tee fitting, 1/4\" tube OD",
         spec="316SS, 5,100 PSI rated",
         vendor="Amazon / Walmart",
         qty=2, unit_price=28.00,
         search_vendor="amazon", search_query="Swagelok SS-400-3 tee fitting"),
    dict(section="5. Compression Fittings",
         item="End cap", part="SS-400-C",
         desc="Swagelok end cap fitting, 1/4\" tube OD",
         spec="316SS, 5,100 PSI rated",
         vendor="Amazon",
         qty=3, unit_price=10.00,
         search_vendor="amazon", search_query="Swagelok SS-400-C end cap fitting"),

    # ── 6. Relief / Safety ────────────────────────────────────────────────────
    dict(section="6. Relief Valve",
         item="Relief valve", part="442F42",
         desc="Parker relief valve, spring-loaded, 1/4\" MNPT",
         spec="SS316, set pressure adjustable, protects vessel from overpressure",
         vendor="Grainger",
         qty=1, unit_price=165.00,
         search_vendor="grainger", search_query="Parker 442F42 relief valve"),
    dict(section="6. Relief Valve",
         item="PTFE thread tape", part="34P209",
         desc="PTFE sealing tape for NPT thread connections",
         spec="High-pressure / high-temp rated",
         vendor="Grainger",
         qty=1, unit_price=5.00,
         search_vendor="grainger", search_query="Grainger 34P209 PTFE tape"),

    # ── 7. Sensors ────────────────────────────────────────────────────────────
    dict(section="7. Sensors",
         item="Pressure transducer", part="K4708",
         desc="Ashcroft 0-5000 PSI pressure transducer, 4-20 mA output, SS, IP67",
         spec="4-20 mA → 1-5 V via 250 ohm shunt resistor into ADS1115 A0",
         vendor="Grainger",
         qty=1, unit_price=400.00,
         search_vendor="grainger", search_query="Ashcroft K4708 pressure transducer 0-5000 PSI"),
    dict(section="7. Sensors",
         item="Pressure gauge (mechanical, visual backup)", part="K4201",
         desc="Ashcroft 0-5000 PSI analog pressure gauge",
         spec="Visual reference gauge, independent of electronics",
         vendor="Grainger",
         qty=1, unit_price=100.00,
         search_vendor="grainger", search_query="Ashcroft K4201 pressure gauge 0-5000 PSI"),

    # ── 8. Electronics & Control ──────────────────────────────────────────────
    dict(section="8. Electronics & Control",
         item="Raspberry Pi 4 (4 GB)", part="RPi4-4GB",
         desc="Single-board computer, runs the 10 Hz control loop in Python 3.11",
         spec="4 GB RAM model recommended",
         vendor="Amazon / Adafruit",
         qty=1, unit_price=55.00,
         search_vendor="adafruit", search_query="Raspberry Pi 4 4GB"),
    dict(section="8. Electronics & Control",
         item="ADS1115 16-bit I2C ADC module", part="ADS1115",
         desc="Reads pressure transducer (A0) and temperature sensor (A1)",
         spec="16-bit resolution, I2C interface",
         vendor="Adafruit / Amazon",
         qty=1, unit_price=10.00,
         search_vendor="adafruit", search_query="ADS1115 16-bit ADC breakout"),
    dict(section="8. Electronics & Control",
         item="NEMA 17 stepper motor", part="NEMA17-200",
         desc="Actuates the motorized needle valve via shaft coupler",
         spec="200 steps/rev, standard NEMA 17 frame",
         vendor="Amazon",
         qty=1, unit_price=15.00,
         search_vendor="amazon", search_query="NEMA 17 stepper motor 200 steps per rev"),
    dict(section="8. Electronics & Control",
         item="A4988 stepper driver", part="A4988",
         desc="Drives NEMA 17 at 1/16 microstepping; GPIO 17 STEP, 27 DIR, 22 EN",
         spec="1/16 microstepping driver module",
         vendor="Pololu / Amazon",
         qty=1, unit_price=8.00,
         search_vendor="amazon", search_query="Pololu A4988 stepper motor driver"),
    dict(section="8. Electronics & Control",
         item="32 GB microSD card", part="microSD-32GB",
         desc="Boot media for Raspberry Pi 4",
         spec="Class 10 / A1 rated for reliability",
         vendor="Amazon (SanDisk)",
         qty=1, unit_price=10.00,
         search_vendor="amazon", search_query="SanDisk 32GB microSD card"),
    dict(section="8. Electronics & Control",
         item="Relay module, 24VDC", part="Relay-24VDC",
         desc="Drives vent solenoid from GPIO 18 PWM signal",
         spec="24VDC coil, panel/DIN mountable",
         vendor="Amazon",
         qty=1, unit_price=10.00,
         search_vendor="amazon", search_query="24VDC relay module GPIO"),
    dict(section="8. Electronics & Control",
         item="DIN rail relay, 24VDC coil", part="DIN-Relay-24VDC",
         desc="DIN-rail mounted relay for panel-style wiring",
         spec="24VDC coil",
         vendor="Grainger",
         qty=1, unit_price=20.00,
         search_vendor="grainger", search_query="DIN rail relay 24VDC coil"),
    dict(section="8. Electronics & Control",
         item="DIN rail power supply, 24VDC 50W", part="33NT20",
         desc="Dayton DIN rail PSU — powers relay, solenoid, and sensor circuits",
         spec="24VDC, 50W output",
         vendor="Grainger",
         qty=1, unit_price=55.00,
         search_vendor="grainger", search_query="Dayton 33NT20 DIN rail power supply 24VDC"),
]

ALREADY_OWNED = [
    dict(section="9. Already Owned",
         item="Pressure vessel", part="PARR 2302HC",
         desc="316SS pressure vessel, S/N 4540-1803-78845A, 1 L volume",
         spec="MAWP 5,000 PSI (34.47 MPa) @ 350°C — no purchase needed"),
    dict(section="9. Already Owned",
         item="Gas booster pump", part="HII 5G-TD-28/150-CO2",
         desc="Air-driven, twin-drive CO2 service booster, S/N 1205101",
         spec="Max outlet 25,000 PSIG (172 MPa) — no purchase needed"),
    dict(section="9. Already Owned",
         item="Temperature controller", part="INKBIRD",
         desc="60C setpoint temperature controller",
         spec="±0.01°C settled stability — no purchase needed"),
    dict(section="9. Already Owned",
         item="CO2 gas cylinder", part="UN1013 Bone Dry",
         desc="Primary process gas — Metro Welding Supply, Detroit MI",
         spec="No purchase needed (existing supply)"),
    dict(section="9. Already Owned",
         item="N2 gas cylinder", part="UN1066 Ultra High Purity",
         desc="Alternate experiment gas — Metro Welding Supply, Detroit MI",
         spec="No purchase needed (existing supply)"),
    dict(section="9. Already Owned",
         item="Ar gas cylinder", part="UN1006 Prepurified",
         desc="Alternate experiment gas — Metro Welding Supply, Detroit MI",
         spec="No purchase needed (existing supply)"),
    dict(section="9. Already Owned",
         item="Air gas cylinder (drive air)", part="UN1002 Dry Grade",
         desc="Drives booster pump only — never enters vessel",
         spec="No purchase needed (existing supply)"),
]

OPTIONAL = [
    dict(section="10. Optional: Windowed Vessel",
         item="Windowed pressure vessel (sapphire window)", part="EZE-Seal series",
         desc="Autoclave Engineers (Parker) windowed reactor for flow visualization",
         spec="Sapphire window, up to 60 MPa",
         vendor="Autoclave Engineers (Parker)",
         qty=1, unit_price=5000.00,
         search_vendor="autoclave", search_query="Autoclave Engineers EZE-Seal windowed reactor"),
    dict(section="10. Optional: Windowed Vessel",
         item="Windowed pressure vessel (alternate)", part="Sitec 100-600 mL",
         desc="Sitec Reactor Technology windowed reactor, sapphire/borosilicate",
         spec="Up to 100 MPa, 100-600 mL volume",
         vendor="Sitec Reactor Technology",
         qty=1, unit_price=4500.00,
         search_vendor="sitec", search_query="Sitec windowed pressure reactor sapphire"),
]

SECTION_COLORS = {
    "1. Motorized Needle Valve": "E0F4F7",
    "2. Check Valve": "FFF3E0",
    "3. Manual Ball Valves": "E8EAF6",
    "4. Stainless Tubing": "F1F8E9",
    "5. Compression Fittings": "FCE4EC",
    "6. Relief Valve": "FFEBEE",
    "7. Sensors": "E3F2FD",
    "8. Electronics & Control": "FFF9C4",
    "9. Already Owned": "ECEFF1",
    "10. Optional: Windowed Vessel": "F3E5F5",
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
               "Vendor", "Qty", "Unit Price", "Line Total", "Buy / Search Link"]
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

    purchasable_total = 0.0
    optional_total = 0.0
    row_idx = 2

    # ── Purchasable items (sections 1-8) ───────────────────────────────────────
    for r in ROWS:
        link = search_url(r["search_vendor"], r["search_query"])
        line_total = r["qty"] * r["unit_price"]
        purchasable_total += line_total

        ws.append([
            r["section"], r["item"], r["part"], r["desc"], r["spec"],
            r["vendor"], r["qty"], r["unit_price"], line_total, "Search this part"
        ])
        style_data_row(ws, row_idx, len(headers), SECTION_COLORS[r["section"]], border)
        ws.cell(row=row_idx, column=8).number_format = "$#,##0.00"
        ws.cell(row=row_idx, column=9).number_format = "$#,##0.00"

        link_cell = ws.cell(row=row_idx, column=10)
        link_cell.hyperlink = link
        link_cell.value = "Search this part"
        link_cell.font = Font(size=9.5, name="Calibri", color="0563C1", underline="single")
        row_idx += 1

    # ── Subtotal: purchasable ─────────────────────────────────────────────────
    ws.append(["", "", "", "", "", "", "", "SUBTOTAL (to buy)", purchasable_total, ""])
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=row_idx, column=col)
        cell.font = Font(bold=True, size=10, name="Calibri")
        cell.fill = PatternFill(start_color="D6D9E8", end_color="D6D9E8", fill_type="solid")
        cell.border = border
    ws.cell(row=row_idx, column=9).number_format = "$#,##0.00"
    row_idx += 1

    # ── Already-owned items (section 9) ───────────────────────────────────────
    for r in ALREADY_OWNED:
        ws.append([
            r["section"], r["item"], r["part"], r["desc"], r["spec"],
            "N/A — already owned", "", "", "$0.00", "N/A"
        ])
        style_data_row(ws, row_idx, len(headers), SECTION_COLORS[r["section"]], border)
        row_idx += 1

    # ── Optional items (section 10) ───────────────────────────────────────────
    for r in OPTIONAL:
        link = search_url(r["search_vendor"], r["search_query"])
        line_total = r["qty"] * r["unit_price"]
        optional_total += line_total

        ws.append([
            r["section"], r["item"], r["part"], r["desc"], r["spec"],
            r["vendor"], r["qty"], r["unit_price"], line_total, "Search this part"
        ])
        style_data_row(ws, row_idx, len(headers), SECTION_COLORS[r["section"]], border)
        ws.cell(row=row_idx, column=8).number_format = "$#,##0.00"
        ws.cell(row=row_idx, column=9).number_format = "$#,##0.00"

        link_cell = ws.cell(row=row_idx, column=10)
        link_cell.hyperlink = link
        link_cell.value = "Search this part"
        link_cell.font = Font(size=9.5, name="Calibri", color="0563C1", underline="single")
        row_idx += 1

    # ── Grand total row ───────────────────────────────────────────────────────
    ws.append(["", "", "", "", "", "", "",
               "TOTAL (required, excl. optional window vessel)",
               purchasable_total, ""])
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=row_idx, column=col)
        cell.font = Font(bold=True, size=11, name="Calibri", color=WHITE)
        cell.fill = PatternFill(start_color=NAVY, end_color=NAVY, fill_type="solid")
        cell.border = border
    ws.cell(row=row_idx, column=9).number_format = "$#,##0.00"

    # Column widths
    widths = [24, 30, 18, 42, 36, 24, 6, 12, 12, 18]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.freeze_panes = "A2"
    ws.row_dimensions[1].height = 32

    # ── Notes sheet ────────────────────────────────────────────────────────────
    notes = wb.create_sheet("Notes")
    notes_data = [
        ["scCO2 System — Complete BOM Notes"],
        [""],
        ["LINK VERIFICATION DISCLAIMER:"],
        ["Automated link-checking was not possible in the environment this file was generated in"],
        ["(all outbound web requests returned 403, including to sites like Wikipedia — a sandbox"],
        ["network restriction, not a sign the URLs are wrong). Each link uses the vendor's standard,"],
        ["publicly documented search-page URL format with the part number/description as the query"],
        ["string — not a guessed deep product page. Please click a few to confirm before bulk-ordering."],
        [""],
        ["Why these exact part numbers matter:"],
        ["- SS-CHS4-5 (check valve) is rated 6,000 PSI. SS-4C looks similar but is only 3,000 PSI."],
        ["- SS-83KS4 (ball valve) is rated 6,000 PSI. SS-43GS4 looks similar but is only 3,000 PSI."],
        ["- All fittings are Swagelok SS-400 series, rated 5,100 PSI, matched to 1/4\" tube OD."],
        ["- SS-1RS4 needle valve (5,000 PSI) gives ~23% margin above 4,061 PSI (28 MPa) operating pressure."],
        [""],
        ["Section 9 (Already Owned) lists existing lab equipment for completeness — no purchase needed."],
        ["Section 10 (Optional) is a windowed vessel upgrade for visualizing scCO2 flow — not required"],
        ["for the current closed-vessel system."],
        [""],
        ["Recommended buying order:"],
        ["1. Confirm thread/tube size compatibility with the existing PARR vessel fittings before ordering."],
        ["2. Order Swagelok parts from an authorized distributor when possible (warranty/traceability"],
        ["   matters on a 28 MPa system)."],
        ["3. McMaster-Carr ships fastest for tubing; Grainger for relief valve, gauges, and PSU."],
        ["4. Electronics (Pi, ADC, stepper driver) are low-risk — any reputable seller is fine."],
    ]
    for row in notes_data:
        notes.append(row)
    notes["A1"].font = Font(bold=True, size=14, color=NAVY)
    notes.column_dimensions["A"].width = 110
    for r in range(3, len(notes_data) + 1):
        notes.cell(row=r, column=1).font = Font(size=10)
        notes.cell(row=r, column=1).alignment = Alignment(wrap_text=True)

    wb.save(output_path)
    print(f"Full BOM written to: {output_path}")
    print(f"  Required purchase subtotal: ${purchasable_total:,.2f}")
    print(f"  Optional windowed vessel:   ${optional_total:,.2f}")


if __name__ == "__main__":
    build_bom("/home/user/pressure-regulation-system/scCO2_Full_Bill_of_Materials.xlsx")
