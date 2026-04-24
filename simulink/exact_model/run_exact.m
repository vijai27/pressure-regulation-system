% run_exact.m — Single-command runner for the high-fidelity pressure vessel digital twin
%
% Usage: type  run_exact  in the MATLAB Command Window.
%
% ── CONFIGURE YOUR EXPERIMENT HERE ───────────────────────────────────────────
%
%   EXPERIMENT_ID   Gas       TiO2
%   ──────────────────────────────────
%        1          CO2       none
%        2          CO2       1 wt%
%        3          N2        none
%        4          N2        1 wt%
%        5          Ar        none
%        6          Ar        1 wt%
%
EXPERIMENT_ID = 1;   % ← change this line to switch experiment
%
% ── SIMULATION TIME ──────────────────────────────────────────────────────────
%   9000 s = 2.5 h  (covers ~2 min heat-up + ~80 min ramp + hold)
%   Use 600 s for a quick sanity check.
SIM_TIME_S = 9000;
%
% ─────────────────────────────────────────────────────────────────────────────

clc;

% ── 1. BUILD ─────────────────────────────────────────────────────────────────
% build_model_exact reads EXPERIMENT_ID from this workspace (shared scope).
fprintf('=== Building scCO2_exact.slx  (Experiment %d) ===\n', EXPERIMENT_ID);
build_model_exact;

% After build_model_exact runs, all its variables are in our shared workspace:
%   y_CO2, y_N2, y_Ar, TiO2_wt_pct, M_mix, Cv_mix, Cp_mix, b_mix,
%   KP, KI, KD, UA_INKBIRD_W_K, T_PRECOND_C, T_INKBIRD_C,
%   V_VESSEL_L, rho_boost, m0, P_boost_Pa, etc.

MODEL    = 'scCO2_exact';   % declare AFTER build so it is never cleared
EXP_NAMES = {'CO2', 'CO2+TiO2', 'N2', 'N2+TiO2', 'Ar', 'Ar+TiO2'};

% ── 2. PRINT EXPERIMENT PARAMETERS ───────────────────────────────────────────
fprintf('\n');
fprintf('╔══════════════════════════════════════════════════════╗\n');
fprintf('║        Pressure Vessel Digital Twin — Exp %d          ║\n', EXPERIMENT_ID);
fprintf('╠══════════════════════════════════════════════════════╣\n');
fprintf('║  Gas             : %-33s║\n', EXP_NAMES{EXPERIMENT_ID});
fprintf('║  TiO2 loading    :  %.0f wt%%                           ║\n', TiO2_wt_pct);
fprintf('║  Molar mass      :  %.4f g/mol                      ║\n', M_mix*1000);
fprintf('║  Cv (gas phase)  :  %.1f J/(kg·K)                   ║\n', Cv_mix);
fprintf('║  Cp (gas phase)  :  %.1f J/(kg·K)                   ║\n', Cp_mix);
fprintf('╠══════════════════════════════════════════════════════╣\n');
fprintf('║  Vessel volume   :  %.1f L                            ║\n', V_VESSEL_L);
fprintf('║  Booster press.  :  %.1f MPa                         ║\n', P_boost_Pa/1e6);
fprintf('║  Booster rho     :  %.1f kg/m³                       ║\n', rho_boost);
fprintf('║  Initial gas m   :  %.5f kg                       ║\n', m0);
fprintf('╠══════════════════════════════════════════════════════╣\n');
fprintf('║  PID gains       :  Kp=%.0f  Ki=%.0f  Kd=%.0f              ║\n', KP, KI, KD);
fprintf('║  Ramp rate       :  %.0f kPa/min                     ║\n', PRESS_RATE_MPA_MIN*1000);
fprintf('║  Target pressure :  %.0f MPa                          ║\n', P_TARGET_MPA);
fprintf('║  T pre-condition :  %.0f °C  (INKBIRD setpoint: %.0f °C) ║\n', T_PRECOND_C, T_INKBIRD_C);
fprintf('║  UA_INKBIRD      :  %.0f W/K                          ║\n', UA_INKBIRD_W_K);
fprintf('║  Wall UA         :  %.1f W/K                          ║\n', UA_WALL_W_K);
fprintf('╠══════════════════════════════════════════════════════╣\n');
fprintf('║  Sim duration    :  %d s (%.0f min)                   ║\n', SIM_TIME_S, SIM_TIME_S/60);
fprintf('╚══════════════════════════════════════════════════════╝\n\n');

% ── 3. SIMULATE ──────────────────────────────────────────────────────────────
fprintf('=== Running simulation (%d s = %.0f min) ... ===\n', SIM_TIME_S, SIM_TIME_S/60);
set_param(MODEL, 'StopTime', num2str(SIM_TIME_S));
out = sim(MODEL);   %#ok<NASGU>

% ── 4. ANALYSE & PLOT ────────────────────────────────────────────────────────
fprintf('=== Analysing results ===\n');

% analyze_results.m reads workspace variables and the 'out' struct,
% then plots, prints stats, and exports to results/sim_*.csv + .png
% It also has access to EXPERIMENT_ID and EXP_NAMES from this workspace.
analyze_results;
