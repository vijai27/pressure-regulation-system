# gui.py — Tkinter + Matplotlib control interface
#
# Layout:
#   Top bar:       State indicator (color-coded chip + text)
#   Center chart:  Pressure vs Time (blue=measured, orange dashed=setpoint)
#                  Temperature on right Y-axis (red dashed)
#   Left panel:    Live readings — pressure, rate, temperature, heating status
#   Right panel:   Settings — target pressure, rates, valve bar, solenoid bar
#   Bottom strip:  START | HOLD | DEPRESSURIZE | E-STOP

import platform
import queue
import threading
import time
from collections import deque

import tkinter as tk
from tkinter import ttk, font as tkfont

_IS_MAC = platform.system() == "Darwin"

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

from control.state_machine import State
from config import (
    SOFTWARE_MAX_SETPOINT,
    PRESSURIZE_RATE_MPA_MIN,
    DEPRESSURIZE_RATE_MPA_MIN,
    MIN_START_TEMP_C,
    SAMPLE_TIME_S,
)

# ── Color palette ─────────────────────────────────────────────────────────────
NAVY   = "#1E2761"
TEAL   = "#028090"
CORAL  = "#F96167"
CREAM  = "#F8F9FA"
WHITE  = "#FFFFFF"
GRAY   = "#6C757D"
GREEN  = "#28A745"
AMBER  = "#FFC107"

STATE_COLORS = {
    State.IDLE:         (GRAY,  "IDLE"),
    State.PRESSURIZE:   (TEAL,  "PRESSURIZING"),
    State.HOLD:         (GREEN, "HOLDING"),
    State.DEPRESSURIZE: (CORAL, "DEPRESSURIZING"),
}

CHART_WINDOW_S = 300   # Show last 5 minutes of data on chart


def _btn_kw(bg: str) -> dict:
    """On macOS, highlightbackground is what actually renders as the button color."""
    if _IS_MAC:
        return {"highlightbackground": bg, "highlightthickness": 2}
    return {}

# ── Shared data object (written by control thread, read by GUI) ────────────────
class SharedData:
    """Thread-safe snapshot of latest system state for GUI consumption."""

    def __init__(self):
        self._lock = threading.Lock()
        self.pressure     = 0.0
        self.temperature  = 25.0
        self.setpoint     = 0.0
        self.valve_pct    = 0.0
        self.solenoid_pct = 0.0
        self.state        = State.IDLE
        self.rate_kpa_min = 0.0
        self.status_msg   = "System ready."
        self.t0           = time.monotonic()

    def update(self, **kwargs):
        with self._lock:
            for k, v in kwargs.items():
                setattr(self, k, v)

    def snapshot(self) -> dict:
        with self._lock:
            return {
                "pressure":     self.pressure,
                "temperature":  self.temperature,
                "setpoint":     self.setpoint,
                "valve_pct":    self.valve_pct,
                "solenoid_pct": self.solenoid_pct,
                "state":        self.state,
                "rate_kpa_min": self.rate_kpa_min,
                "status_msg":   self.status_msg,
                "elapsed_s":    time.monotonic() - self.t0,
            }


class App:
    """Main GUI window."""

    def __init__(self, root: tk.Tk, shared: SharedData, sm):
        """
        Args:
            root:   Tkinter root window
            shared: SharedData object populated by the control thread
            sm:     StateMachine — used to dispatch button commands
        """
        self._root   = root
        self._shared = shared
        self._sm     = sm

        root.title("High-Pressure Vessel Control System")
        root.configure(bg=CREAM)
        root.minsize(1000, 680)

        self._build_ui()

        # History buffers for chart
        self._times    = deque(maxlen=int(CHART_WINDOW_S / SAMPLE_TIME_S))
        self._pressures = deque(maxlen=int(CHART_WINDOW_S / SAMPLE_TIME_S))
        self._setpoints = deque(maxlen=int(CHART_WINDOW_S / SAMPLE_TIME_S))
        self._temps     = deque(maxlen=int(CHART_WINDOW_S / SAMPLE_TIME_S))

        # Rate calculation
        self._prev_pressure = None
        self._prev_time     = None

        # Start GUI refresh loop
        self._refresh()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = self._root

        # On macOS the native aqua ttk theme ignores custom colors on Progressbar
        # and other ttk widgets. Switching to 'clam' restores expected behavior.
        if _IS_MAC:
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("TProgressbar", background=TEAL,
                            troughcolor="#D0D4DA", thickness=14)

        # ── Top status bar ────────────────────────────────────────────────────
        top = tk.Frame(root, bg=NAVY, height=50)
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(top, text="High-Pressure Vessel Control",
                 bg=NAVY, fg=WHITE, font=("Calibri", 14, "bold")).pack(side="left", padx=16, pady=10)

        self._state_label = tk.Label(top, text="● IDLE",
                                     bg=NAVY, fg=GRAY, font=("Calibri", 13, "bold"))
        self._state_label.pack(side="right", padx=16)

        self._status_label = tk.Label(top, text="",
                                      bg=NAVY, fg="#AAAAAA", font=("Calibri", 10))
        self._status_label.pack(side="right", padx=8)

        # ── Main body: chart + side panels ────────────────────────────────────
        body = tk.Frame(root, bg=CREAM)
        body.pack(fill="both", expand=True, padx=12, pady=(8, 0))

        left  = self._build_left_panel(body)
        right = self._build_right_panel(body)
        chart = self._build_chart(body)

        left.pack (side="left",  fill="y",    padx=(0, 6))
        chart.pack(side="left",  fill="both", expand=True)
        right.pack(side="right", fill="y",    padx=(6, 0))

        # ── Bottom button strip ───────────────────────────────────────────────
        bottom = tk.Frame(root, bg=CREAM, pady=10)
        bottom.pack(fill="x", padx=12)

        btn_cfg = {"font": ("Calibri", 13, "bold"), "width": 14, "height": 2,
                   "relief": "flat", "cursor": "hand2"}

        self._btn_start = tk.Button(bottom, text="START", bg=TEAL, fg=WHITE,
                                    command=self._on_start, **btn_cfg,
                                    **_btn_kw(TEAL))
        self._btn_start.pack(side="left", padx=6)

        tk.Button(bottom, text="HOLD", bg=NAVY, fg=WHITE,
                  command=self._on_hold, **btn_cfg,
                  **_btn_kw(NAVY)).pack(side="left", padx=6)

        tk.Button(bottom, text="DEPRESSURIZE", bg=AMBER, fg=NAVY,
                  command=self._on_depressurize, **btn_cfg,
                  **_btn_kw(AMBER)).pack(side="left", padx=6)

        tk.Button(bottom, text="⏹ E-STOP", bg=CORAL, fg=WHITE,
                  command=self._on_estop,
                  font=("Calibri", 13, "bold"), width=14, height=2,
                  relief="flat", cursor="hand2",
                  **_btn_kw(CORAL)).pack(side="right", padx=6)

    def _build_left_panel(self, parent) -> tk.Frame:
        f = tk.Frame(parent, bg=WHITE, relief="flat", bd=0, width=160)
        f.pack_propagate(False)

        def label_row(key, unit=""):
            tk.Label(f, text=key, bg=WHITE, fg=GRAY, font=("Calibri", 9)).pack(pady=(8, 0))
            var = tk.StringVar(value="—")
            tk.Label(f, textvariable=var, bg=WHITE, fg=NAVY,
                     font=("Calibri", 22, "bold")).pack()
            if unit:
                tk.Label(f, text=unit, bg=WHITE, fg=GRAY, font=("Calibri", 9)).pack()
            return var

        tk.Label(f, text="LIVE READINGS", bg=WHITE, fg=NAVY,
                 font=("Calibri", 10, "bold")).pack(pady=(12, 4))

        self._var_pressure   = label_row("Pressure", "MPa")
        self._var_rate       = label_row("Rate", "kPa/min")
        self._var_temp       = label_row("Temperature", "°C")
        self._var_heat_status = tk.StringVar(value="")
        tk.Label(f, textvariable=self._var_heat_status, bg=WHITE,
                 font=("Calibri", 9, "bold")).pack()

        ttk.Separator(f, orient="horizontal").pack(fill="x", padx=8, pady=8)

        tk.Label(f, text="State", bg=WHITE, fg=GRAY, font=("Calibri", 9)).pack()
        self._var_state_text = tk.StringVar(value="IDLE")
        tk.Label(f, textvariable=self._var_state_text, bg=WHITE, fg=NAVY,
                 font=("Calibri", 13, "bold")).pack(pady=(2, 12))
        return f

    def _build_right_panel(self, parent) -> tk.Frame:
        f = tk.Frame(parent, bg=WHITE, relief="flat", bd=0, width=200)
        f.pack_propagate(False)

        tk.Label(f, text="SETTINGS", bg=WHITE, fg=NAVY,
                 font=("Calibri", 10, "bold")).pack(pady=(12, 4))

        def setting_row(label, default, unit, min_val, max_val):
            tk.Label(f, text=label, bg=WHITE, fg=GRAY, font=("Calibri", 9)).pack(anchor="w", padx=12)
            row = tk.Frame(f, bg=WHITE)
            row.pack(fill="x", padx=12, pady=(0, 6))
            var = tk.DoubleVar(value=default)
            sb = tk.Spinbox(row, from_=min_val, to=max_val, increment=0.5,
                            textvariable=var, width=7, font=("Calibri", 11),
                            format="%.1f")
            sb.pack(side="left")
            tk.Label(row, text=unit, bg=WHITE, fg=GRAY, font=("Calibri", 9)).pack(side="left", padx=4)
            return var

        self._var_target   = setting_row("Target Pressure", 28.0, "MPa",    0.5, SOFTWARE_MAX_SETPOINT)
        self._var_pr_rate  = setting_row("Pressurize Rate", PRESSURIZE_RATE_MPA_MIN * 1000, "kPa/min", 50, 600)
        self._var_dr_rate  = setting_row("Depressurize Rate", DEPRESSURIZE_RATE_MPA_MIN, "MPa/min",  0.5, 5.0)

        ttk.Separator(f, orient="horizontal").pack(fill="x", padx=8, pady=4)

        def bar_row(label):
            tk.Label(f, text=label, bg=WHITE, fg=GRAY, font=("Calibri", 9)).pack(anchor="w", padx=12)
            var = tk.DoubleVar(value=0)
            bar = ttk.Progressbar(f, variable=var, maximum=100, length=160)
            bar.pack(padx=12, pady=(0, 4))
            pct_var = tk.StringVar(value="0 %")
            tk.Label(f, textvariable=pct_var, bg=WHITE, fg=NAVY,
                     font=("Calibri", 9)).pack(anchor="e", padx=12)
            return var, pct_var

        self._valve_bar,    self._valve_pct_var    = bar_row("Valve Opening")
        self._solenoid_bar, self._solenoid_pct_var = bar_row("Solenoid PWM")

        ttk.Separator(f, orient="horizontal").pack(fill="x", padx=8, pady=4)
        self._temp_warn_label = tk.Label(f, text="", bg=WHITE, fg=CORAL,
                                         font=("Calibri", 9, "bold"), wraplength=180)
        self._temp_warn_label.pack(padx=12, pady=4)
        return f

    def _build_chart(self, parent) -> tk.Frame:
        f = tk.Frame(parent, bg=WHITE)

        self._fig, ax1 = plt.subplots(figsize=(7, 4))
        self._fig.patch.set_facecolor(WHITE)
        ax1.set_facecolor("#F0F4F8")
        ax1.set_xlabel("Time (s)", color=GRAY, fontsize=9)
        ax1.set_ylabel("Pressure (MPa)", color=NAVY, fontsize=9)
        ax1.tick_params(colors=GRAY)
        ax1.set_ylim(0, 30)
        ax1.grid(color="#E0E4EA", linewidth=0.6)

        ax2 = ax1.twinx()
        ax2.set_ylabel("Temperature (°C)", color="#CC3333", fontsize=9)
        ax2.tick_params(colors="#CC3333")
        ax2.set_ylim(0, 100)

        self._line_pressure, = ax1.plot([], [], color=NAVY,  linewidth=1.8, label="Pressure")
        self._line_setpoint, = ax1.plot([], [], color=TEAL, linewidth=1.5,
                                         linestyle="--", label="Setpoint")
        self._line_temp,     = ax2.plot([], [], color="#CC3333", linewidth=1.2,
                                         linestyle="--", label="Temp")

        # Legend
        lines = [self._line_pressure, self._line_setpoint, self._line_temp]
        labels = ["Pressure", "Setpoint", "Temperature"]
        ax1.legend(lines, labels, loc="upper left", fontsize=8,
                   framealpha=0.7, facecolor=WHITE)

        self._ax1 = ax1
        self._ax2 = ax2
        plt.tight_layout(pad=1.5)

        canvas = FigureCanvasTkAgg(self._fig, master=f)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._canvas = canvas
        return f

    # ── Button handlers ───────────────────────────────────────────────────────

    def _on_start(self):
        # Push current settings into state machine before starting
        target = self._var_target.get()
        self._sm.set_target(target)
        self._sm.request_start()

    def _on_hold(self):
        # Freeze ramp at current setpoint — handled by state machine transition
        pass  # PRESSURIZE→HOLD happens automatically when target reached.
              # This button is a no-op for now (HOLD is automatic).

    def _on_depressurize(self):
        self._sm.request_depressurize()

    def _on_estop(self):
        self._sm.request_estop()

    # ── Periodic GUI refresh ──────────────────────────────────────────────────

    def _refresh(self):
        data = self._shared.snapshot()
        state  = data["state"]
        color, state_text = STATE_COLORS[state]

        # State label
        self._state_label.config(text=f"● {state_text}", fg=color)
        self._var_state_text.set(state_text)
        self._status_label.config(text=data["status_msg"][:80])

        # Live readings
        self._var_pressure.set(f"{data['pressure']:.2f}")
        self._var_rate.set(f"{data['rate_kpa_min']:.0f}")
        self._var_temp.set(f"{data['temperature']:.1f}")

        # Heating status
        temp = data["temperature"]
        if temp < MIN_START_TEMP_C:
            self._var_heat_status.set(f"⚠ Heating ({temp:.1f}°C)")
            heat_color = CORAL
            self._temp_warn_label.config(
                text=f"START locked until {MIN_START_TEMP_C}°C reached"
            )
            self._btn_start.config(state="disabled", bg=GRAY, **_btn_kw(GRAY))
        else:
            self._var_heat_status.set("✓ Ready")
            heat_color = GREEN
            self._temp_warn_label.config(text="")
            if state == State.IDLE:
                self._btn_start.config(state="normal", bg=TEAL, **_btn_kw(TEAL))

        # Actuator bars
        self._valve_bar.set(data["valve_pct"])
        self._valve_pct_var.set(f"{data['valve_pct']:.0f} %")
        self._solenoid_bar.set(data["solenoid_pct"])
        self._solenoid_pct_var.set(f"{data['solenoid_pct']:.0f} %")

        # Append chart data
        self._times.append(data["elapsed_s"])
        self._pressures.append(data["pressure"])
        self._setpoints.append(data["setpoint"])
        self._temps.append(data["temperature"])

        # Redraw chart
        if len(self._times) > 1:
            t = list(self._times)
            self._line_pressure.set_data(t, list(self._pressures))
            self._line_setpoint.set_data(t, list(self._setpoints))
            self._line_temp.set_data(t, list(self._temps))
            self._ax1.set_xlim(max(0, t[-1] - CHART_WINDOW_S), t[-1] + 5)
            self._canvas.draw_idle()

        # Reschedule every SAMPLE_TIME_S
        self._root.after(int(SAMPLE_TIME_S * 1000), self._refresh)
