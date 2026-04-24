# make_schematic.py — scCO2 System Schematic Diagram
# Run: python make_schematic.py
# Output: scCO2_Schematic.png

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

fig, ax = plt.subplots(figsize=(24, 13))
ax.set_xlim(0, 24)
ax.set_ylim(0, 13)
ax.axis('off')
fig.patch.set_facecolor('#0D1B2A')
ax.set_facecolor('#0D1B2A')

# ── Colour palette ────────────────────────────────────────────────────────────
HP   = '#EF4444'      # red    — high-pressure CO₂ line
LP   = '#60A5FA'      # blue   — low-pressure / supply line
SIG  = '#FBBF24'      # amber  — sensor / signal
PWR  = '#34D399'      # green  — 24 V power
CTL  = '#A78BFA'      # purple — GPIO control
TXT  = '#F1F5F9'      # white text
DIM  = '#94A3B8'      # grey   — secondary text
WARN = '#FCA5A5'      # red    — safety note text

# ── Helper functions ──────────────────────────────────────────────────────────

def box(cx, cy, w, h, label, sub='', fc='#1E293B', ec='#0D9488', fs=9, lc=TXT):
    r = patches.FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                               boxstyle='round,pad=0.06',
                               facecolor=fc, edgecolor=ec, linewidth=1.8, zorder=3)
    ax.add_patch(r)
    yo = 0.12 if sub else 0
    ax.text(cx, cy+yo, label, ha='center', va='center',
            fontsize=fs, color=lc, fontweight='bold', zorder=4)
    if sub:
        ax.text(cx, cy-0.28, sub, ha='center', va='center',
                fontsize=6.5, color=DIM, zorder=4)

def cylinder(cx, bot, w, h, fc='#1C3A5E', label='', sub=''):
    r = patches.FancyBboxPatch((cx-w/2, bot), w, h,
                               boxstyle='round,pad=0.08',
                               facecolor=fc, edgecolor='#475569', linewidth=1.5, zorder=3)
    ax.add_patch(r)
    ax.text(cx, bot+h/2+0.08, label, ha='center', va='center',
            fontsize=9, color=TXT, fontweight='bold', zorder=4)
    if sub:
        ax.text(cx, bot-0.3, sub, ha='center', va='top',
                fontsize=7, color=DIM, zorder=4)

def valve_bowtie(cx, cy, color='#374151', label='', label_above=False):
    s = 0.28
    t1 = plt.Polygon([[cx-s, cy-s*0.7],[cx-s, cy+s*0.7],[cx, cy]],
                     fc=color, ec='white', lw=1.2, zorder=4)
    t2 = plt.Polygon([[cx+s, cy-s*0.7],[cx+s, cy+s*0.7],[cx, cy]],
                     fc=color, ec='white', lw=1.2, zorder=4)
    ax.add_patch(t1); ax.add_patch(t2)
    if label:
        yo = cy+(s+0.2) if label_above else cy-(s+0.2)
        va = 'bottom' if label_above else 'top'
        ax.text(cx, yo, label, ha='center', va=va,
                fontsize=7, color=TXT, fontweight='bold', zorder=4)

def instr(cx, cy, tag, color='#F59E0B', sub=''):
    c = patches.Circle((cx, cy), 0.38, fc=color, ec='white', lw=1.5, zorder=4)
    ax.add_patch(c)
    ax.text(cx, cy, tag, ha='center', va='center',
            fontsize=9, color='white', fontweight='bold', zorder=5)
    if sub:
        ax.text(cx, cy-0.6, sub, ha='center', va='top',
                fontsize=6.5, color=SIG, zorder=4)

def seg(x1, y1, x2, y2, col, lw=2.2, ls='-'):
    ax.plot([x1,x2],[y1,y2], color=col, lw=lw, ls=ls,
            solid_capstyle='round', zorder=2)

def arr(x1, y1, x2, y2, col, lw=2.2, ls='-'):
    ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                arrowprops=dict(arrowstyle='->', color=col, lw=lw, linestyle=ls),
                zorder=2)

# ════════════════════════════════════════════════════════════════════════════
# SECTION BACKGROUNDS
# ════════════════════════════════════════════════════════════════════════════
ax.add_patch(patches.FancyBboxPatch((0.15,5.2), 23.7, 7.4,
    boxstyle='round,pad=0.1', fc='#111D2B', ec='#1E3A5F', lw=1.2, zorder=1))
ax.text(0.45, 12.45, 'PROCESS', fontsize=8, color='#334155', fontweight='bold')

ax.add_patch(patches.FancyBboxPatch((0.15,0.15), 23.7, 4.85,
    boxstyle='round,pad=0.1', fc='#0F2020', ec='#134E4A', lw=1.2, zorder=1))
ax.text(0.45, 4.8, 'CONTROL & ELECTRICAL', fontsize=8, color='#334155', fontweight='bold')

# ════════════════════════════════════════════════════════════════════════════
# PROCESS FLOW   main line at Y = 9.0
# ════════════════════════════════════════════════════════════════════════════
MY = 9.0   # main process line y

# CO₂ Cylinder ─────────────────────────────────────────────────────────────
cylinder(1.6, 6.8, 1.1, 2.0, fc='#1A3550',
         label='CO₂', sub='Bone Dry, UN1013\n5.7 MPa @ RT')
seg(1.6, 8.8, 1.6, MY, LP, lw=2)
seg(1.6, MY,  3.0, MY, LP, lw=2)

# BV-1  inlet isolation ───────────────────────────────────────────────────
valve_bowtie(3.0, MY, '#374151', 'BV-1', label_above=False)
seg(3.3, MY, 4.1, MY, LP, lw=2)

# Gas Booster ──────────────────────────────────────────────────────────────
box(4.9, MY, 1.6, 1.0, 'GAS\nBOOSTER', 'HII 5G-TD-28/150-CO₂\n172 MPa max  |  air-driven',
    fc='#162040', ec='#3B82F6', fs=10)
# Air supply line into bottom of booster
cylinder(4.9, 6.0, 1.0, 1.5, fc='#2D3748',
         label='Air\nSupply', sub='~100 PSI drive')
seg(4.9, 7.5, 4.9, 8.5, '#9CA3AF', lw=1.8)
ax.text(5.15, 8.0, 'Air\ndrive', fontsize=6.5, color='#9CA3AF', va='center')

# High-pressure line starts here ──────────────────────────────────────────
seg(5.7, MY, 6.7, MY, HP, lw=3)

# Check Valve ──────────────────────────────────────────────────────────────
valve_bowtie(6.7, MY, '#7C3AED', 'CV-1\n(Check)', label_above=False)
seg(7.0, MY, 8.0, MY, HP, lw=3)

# BV-2 post-booster isolation ─────────────────────────────────────────────
valve_bowtie(8.0, MY, '#374151', 'BV-2', label_above=False)
seg(8.3, MY, 9.3, MY, HP, lw=3)

# Motorized Needle Valve ───────────────────────────────────────────────────
box(9.9, MY, 1.3, 0.85, 'MNV', 'Motorized\nNeedle Valve',
    fc='#064E3B', ec='#10B981', fs=10)
ax.text(9.9, MY+0.65, '▲', ha='center', fontsize=13, color='#10B981', zorder=5)
ax.text(9.9, MY+0.95, 'Stepper\nMotor', ha='center', fontsize=7, color='#6EE7B7', zorder=4)
seg(10.55, MY, 11.5, MY, HP, lw=3)

# PARR Vessel ──────────────────────────────────────────────────────────────
box(12.5, MY, 2.2, 2.6, 'PARR VESSEL', '1 L  |  316SS  |  5000 PSI rated',
    fc='#1C3A5E', ec='#FBBF24', fs=11, lc='#FDE68A')
ax.text(12.5, MY+0.2, '★  28 MPa operating', ha='center',
        fontsize=7.5, color='#FDE68A', zorder=4)

# Relief Valve (branch up from vessel) ────────────────────────────────────
seg(12.5, MY+1.3, 12.5, 11.2, '#EF4444', lw=2)
valve_bowtie(12.5, 11.4, '#EF4444', '', label_above=False)
ax.text(12.5, 11.85, 'PRV-01', ha='center', fontsize=8, color=WARN, fontweight='bold', zorder=5)
ax.text(12.5, 12.1, 'Set: 28.5 MPa', ha='center', fontsize=7, color=WARN, zorder=4)
seg(12.5, 11.7, 14.0, 11.7, '#EF4444', lw=1.8)
ax.text(14.2, 11.7, '→ VENT', fontsize=8, color=WARN, va='center')

# Pressure Transducer (branch off vessel) ─────────────────────────────────
seg(13.6, MY+0.6, 15.0, MY+0.6, SIG, lw=1.6, ls='--')
instr(15.4, MY+0.6, 'PT', '#F59E0B', sub='PT-01\n0–5000 PSI\n4–20 mA')

# Temperature sensor ───────────────────────────────────────────────────────
seg(13.6, MY-0.5, 15.0, MY-0.5, '#EC4899', lw=1.6, ls='--')
instr(15.4, MY-0.5, 'TT', '#BE185D', sub='TT-01\nThermocouple\n0–100°C')

# BV-3 outlet isolation ────────────────────────────────────────────────────
seg(13.6, MY, 16.5, MY, HP, lw=2.5)
valve_bowtie(16.5, MY, '#374151', 'BV-3', label_above=False)
seg(16.8, MY, 17.7, MY, HP, lw=2.5)

# Vent Solenoid ────────────────────────────────────────────────────────────
box(18.3, MY, 1.4, 0.85, 'SV-01', 'Vent Solenoid\n(NC, PWM)',
    fc='#1C1C40', ec='#8B5CF6', fs=10)
seg(19.0, MY, 20.5, MY, '#9CA3AF', lw=2)
arr(20.5, MY, 21.2, MY, '#9CA3AF')
ax.text(21.4, MY, 'EXHAUST\n(safe vent)', ha='left', va='center',
        fontsize=8.5, color='#9CA3AF')

# ════════════════════════════════════════════════════════════════════════════
# CONTROL / ELECTRICAL SECTION
# ════════════════════════════════════════════════════════════════════════════

# 24 V PSU ─────────────────────────────────────────────────────────────────
box(2.0, 2.8, 2.2, 1.2, '24VDC PSU', 'Dayton 33NT20  50W\nDIN Rail mount',
    fc='#0D2D2D', ec=PWR, fs=9)

# ADS1115 ──────────────────────────────────────────────────────────────────
box(7.0, 4.0, 2.2, 1.0, 'ADS1115', '16-bit ADC  |  I²C',
    fc='#1C1A0D', ec=SIG, fs=9)

# Raspberry Pi ─────────────────────────────────────────────────────────────
box(11.2, 2.8, 3.2, 2.2, 'Raspberry Pi 4',
    'Python 3.11  |  10 Hz PID control\nGUI  |  CSV Log  |  ThingSpeak',
    fc='#1D0A40', ec='#8B5CF6', fs=11)

# A4988 Stepper Driver ─────────────────────────────────────────────────────
box(9.9, 4.3, 2.0, 0.95, 'A4988', 'Stepper Driver\n1/16 microstepping',
    fc='#0A2312', ec='#10B981', fs=9)

# INKBIRD ──────────────────────────────────────────────────────────────────
box(15.8, 2.5, 2.2, 1.0, 'INKBIRD', 'Temp Controller\n60°C setpoint  ±0.01°C',
    fc='#1C0A18', ec='#EC4899', fs=9)

# Relay ────────────────────────────────────────────────────────────────────
box(18.3, 4.0, 1.9, 0.95, 'RELAY', '24VDC coil\n10A contacts',
    fc='#150A2D', ec='#8B5CF6', fs=9)

# ── Power connections (PSU → everything) ─────────────────────────────────
# Horizontal power rail
seg(3.1, 2.8, 9.6, 2.8, PWR, lw=1.5, ls='--')
# PSU → ADS1115
seg(3.1, 3.1, 5.9, 3.1, PWR, lw=1.3, ls='--')
seg(5.9, 3.1, 5.9, 4.0, PWR, lw=1.3, ls='--')
seg(5.9, 4.0, 5.9, 4.0, PWR, lw=1.3, ls='--')
# PSU → Stepper Driver
seg(3.1, 2.6, 8.0, 2.6, PWR, lw=1.3, ls='--')
seg(8.0, 2.6, 8.0, 4.3, PWR, lw=1.3, ls='--')
seg(8.0, 4.3, 8.9, 4.3, PWR, lw=1.3, ls='--')
# PSU → Relay
seg(3.1, 2.3, 19.5, 2.3, PWR, lw=1.3, ls='--')
seg(19.5, 2.3, 19.5, 4.0, PWR, lw=1.3, ls='--')
seg(19.5, 4.0, 19.2, 4.0, PWR, lw=1.3, ls='--')
ax.text(7.0, 2.45, '24 V power rail', fontsize=7, color=PWR, ha='center')

# ── Signal: PT → ADS1115 ─────────────────────────────────────────────────
seg(15.4, MY+0.22, 15.4, 4.9, SIG, lw=1.5, ls='--')
seg(15.4, 4.9, 7.0, 4.5, SIG, lw=1.5, ls='--')
ax.text(11.5, 4.85, '4-20 mA signal', fontsize=7, color=SIG, ha='center')

# ── Signal: TT → INKBIRD ─────────────────────────────────────────────────
seg(15.4, MY-0.88, 15.4, 3.0, '#EC4899', lw=1.5, ls='--')
seg(15.4, 3.0, 14.7, 2.5, '#EC4899', lw=1.5, ls='--')

# ── I2C: ADS1115 → RPi ───────────────────────────────────────────────────
arr(8.1, 4.0, 9.6, 3.5, SIG, lw=1.5, ls='--')
ax.text(8.8, 3.9, 'I²C', fontsize=7.5, color=SIG, ha='center')

# ── INKBIRD feedback → RPi ───────────────────────────────────────────────
arr(14.7, 2.5, 12.8, 2.8, '#EC4899', lw=1.5, ls='--')
ax.text(13.8, 2.5, 'Temp\nfeedback', fontsize=7, color='#F9A8D4', ha='center')

# ── GPIO: RPi → A4988 ────────────────────────────────────────────────────
arr(9.6, 3.5, 9.9, 3.82, CTL, lw=1.5, ls='--')
ax.text(9.5, 3.7, 'Step\nDir', fontsize=7, color=CTL, ha='right')

# ── A4988 → Stepper Motor (needle valve) ─────────────────────────────────
seg(9.9, 4.78, 9.9, 6.5, CTL, lw=2)
arr(9.9, 6.5, 9.9, MY+1.05, CTL, lw=2)
ax.text(10.15, 6.2, 'Motor\nphase', fontsize=7, color=CTL, ha='left')

# ── GPIO: RPi → Relay ────────────────────────────────────────────────────
arr(12.8, 3.2, 17.4, 3.8, CTL, lw=1.5, ls='--')
ax.text(15.2, 3.6, 'GPIO', fontsize=7, color=CTL, ha='center')

# ── Relay → Solenoid ─────────────────────────────────────────────────────
seg(18.3, 4.48, 18.3, 5.5, CTL, lw=2)
arr(18.3, 5.5, 18.3, MY-0.43, CTL, lw=2)

# ════════════════════════════════════════════════════════════════════════════
# TITLE & LEGEND
# ════════════════════════════════════════════════════════════════════════════
ax.text(12.0, 12.7,
        'scCO₂ Automated Pressure Regulation System — Schematic',
        ha='center', va='center', fontsize=15, color=TXT, fontweight='bold')
ax.text(12.0, 12.35,
        'Operating range: 0 – 28 MPa  |  Temperature: 60°C  |  P&ID Style Diagram',
        ha='center', va='center', fontsize=9, color=DIM)

legend_items = [
    (HP,      '-',  'High-pressure CO₂ line (>1000 PSI)'),
    (LP,      '-',  'Low-pressure / supply line'),
    (SIG,     '--', 'Sensor / signal (4–20 mA)'),
    (PWR,     '--', '24 VDC power'),
    (CTL,     '--', 'GPIO control signal'),
    ('#EC4899','--', 'Temperature signal'),
]
for i, (col, ls, lbl) in enumerate(legend_items):
    lx, ly = 16.5, 12.72 - i*0.38
    ax.plot([lx, lx+0.7], [ly, ly], color=col, lw=2.0, ls=ls)
    ax.text(lx+0.85, ly, lbl, va='center', fontsize=8, color='#CBD5E1')

# Safety note
ax.text(0.3, 0.25,
        '⚠  HIGH PRESSURE SYSTEM: All process components rated ≥ 5000 PSI. '
        'Relief valve PRV-01 set at 28.5 MPa. '
        'Do not operate without all isolation valves and safety checks completed.',
        fontsize=7.5, color=WARN, va='bottom')

plt.tight_layout(pad=0.3)
plt.savefig('scCO2_Schematic.png', dpi=130, bbox_inches='tight',
            facecolor=fig.get_facecolor())
print('Saved: scCO2_Schematic.png')
plt.close()
