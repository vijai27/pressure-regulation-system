% build_model_exact.m  —  High-fidelity pressure vessel digital twin
%
% Physics: Peng-Robinson EOS (pure component) + mass/energy balance
%          + Cv valve flow + INKBIRD heater
%
% STATES:  m_gas (kg total gas),  T_vessel (K)
% OUTPUT:  P_measured (MPa)
%
% ── 6 EXPERIMENTS ────────────────────────────────────────────────────────────
%   Set EXPERIMENT_ID (1-6) then run build_model_exact.
%   Each experiment uses a single pure gas, with or without 1 wt% TiO2.
%
%   ID  Gas       TiO2
%   1   CO2       none
%   2   CO2       1 wt%
%   3   N2        none
%   4   N2        1 wt%
%   5   Ar        none
%   6   Ar        1 wt%
%
% ── HARDWARE PARAMETERS — fill in from your lab ───────────────────────────────
%   V_VESSEL_L      vessel volume (water fill test, mL → L)
%   Cv_VALVE_US     motorized valve Cv from datasheet (gal/min/sqrt(psi))
%   Cv_VENT_US      solenoid vent Cv from datasheet
%   UA_WALL_W_K     vessel wall heat transfer (W/K); ~2-8 for 1L 316SS
%   UA_INKBIRD_W_K  INKBIRD heater coupling (W/K); ~30-80 typical
%   M_VESSEL_THERM  vessel wall + gas thermal mass (J/K); ~200-400 for 1L SS
%   P_DRIVE_AIR_MPA shop air pressure from regulator gauge
%   BOOSTER_RATIO   from pump nameplate (e.g. 62)
%   TAU_VALVE_S     motorized valve full-stroke time (stopwatch)

clc;

MODEL = 'scCO2_exact';

% ── EXPERIMENT SELECTION ──────────────────────────────────────────────────────
% Allow run_exact.m to set EXPERIMENT_ID before calling this script.
% If not already set, default to Experiment 1 (pure CO2).
if ~exist('EXPERIMENT_ID','var')
    EXPERIMENT_ID = 1;   % ← change in run_exact.m (or here if running standalone)
end

% Mole fractions [y_CO2, y_N2, y_Ar] — each experiment is a single pure gas
% Purity ≥ 99.9% assumed; row pairs share the same gas (without / with TiO2)
EXP_COMPS = [1.000, 0.000, 0.000;   % Exp 1: pure CO2 (no TiO2)
             1.000, 0.000, 0.000;   % Exp 2: pure CO2 + TiO2
             0.000, 1.000, 0.000;   % Exp 3: pure N2  (no TiO2)
             0.000, 1.000, 0.000;   % Exp 4: pure N2  + TiO2
             0.000, 0.000, 1.000;   % Exp 5: pure Ar  (no TiO2)
             0.000, 0.000, 1.000];  % Exp 6: pure Ar  + TiO2

EXP_TIO2_WT = [0, 1, 0, 1, 0, 1];  % TiO2 loading wt% (odd=no TiO2, even=1wt%)

% Short name for each experiment (used in plot titles and console output)
EXP_NAMES = {'CO2', 'CO2+TiO2', 'N2', 'N2+TiO2', 'Ar', 'Ar+TiO2'};

y_CO2 = EXP_COMPS(EXPERIMENT_ID, 1);
y_N2  = EXP_COMPS(EXPERIMENT_ID, 2);
y_Ar  = EXP_COMPS(EXPERIMENT_ID, 3);
TiO2_wt_pct = EXP_TIO2_WT(EXPERIMENT_ID);

fprintf('\nExperiment %d: %s  |  TiO2=%.0f wt%%\n', ...
        EXPERIMENT_ID, EXP_NAMES{EXPERIMENT_ID}, TiO2_wt_pct);

% ── HARDWARE PARAMETERS ───────────────────────────────────────────────────────
V_VESSEL_L      = 1.0;     % [L]
Cv_VALVE_US     = 0.005;   % [gal/min/sqrt(psi)]
Cv_VENT_US      = 0.010;   % [gal/min/sqrt(psi)]
UA_WALL_W_K     = 3.0;     % [W/K]  vessel wall → ambient
UA_INKBIRD_W_K  = 50.0;    % [W/K]  INKBIRD heater coupling
T_INKBIRD_C     = 60.0;    % [°C]   INKBIRD setpoint
T_PRECOND_C     = 55.0;    % [°C]   minimum T to start pressurisation
M_VESSEL_THERM  = 250.0;   % [J/K]  vessel wall thermal mass (316SS, ~0.5 kg)
P_DRIVE_AIR_MPA = 1.03;    % [MPa]  150 PSI max drive air → 28×1.03 = 28.8 MPa max output
BOOSTER_RATIO   = 28;      % [-]  HI SG-TD-28/150-CO2 nameplate (ratio=28, max drive 150 PSI)
TAU_VALVE_S     = 5.0;     % [s]
TAU_SENSOR_P_S  = 0.05;    % [s]
TAU_SENSOR_T_S  = 30.0;    % [s]
T_AMBIENT_C     = 25.0;    % [°C]
KP = 40.0;  KI = 5.0;  KD = 2.0;
P_TARGET_MPA    = 28.0;    % [MPa]
PRESS_RATE_MPA_MIN = 0.35; % [MPa/min]
DT              = 0.1;     % [s]
SIM_TIME        = 9000;    % [s]  2.5 h: heat-up + full cycle

% ── COMPONENT PROPERTIES (CO2, N2, Ar) ───────────────────────────────────────
R_M    = 8.314;
Tc_vec = [304.13,  126.192, 150.86 ];   % Critical T  [K]
Pc_vec = [7.377e6, 3.3958e6, 4.898e6];  % Critical P  [Pa]
kp_vec = [0.7080,  0.4316,  0.3746 ];   % PR-EOS kappa
M_vec  = [0.04401, 0.02801, 0.03995];   % Molar mass  [kg/mol]
Cv_vec = [900.0,   742.0,   312.0  ];   % Cv at ~28MPa 60°C [J/(kg·K)]
Cp_vec = [1100.0,  1040.0,  520.0  ];   % Cp at ~28MPa 60°C [J/(kg·K)]

% Binary interaction parameters kij (van der Waals mixing)
kij_12 = 0.028;   % CO2-N2  (literature)
kij_13 = 0.124;   % CO2-Ar  (literature)
kij_23 = 0.000;   % N2-Ar   (non-polar / similar)

% ── DERIVED MIXTURE PROPERTIES ────────────────────────────────────────────────
y_vec = [y_CO2, y_N2, y_Ar];

M_mix  = sum(y_vec .* M_vec);           % mixture molar mass [kg/mol]
x_vec  = y_vec .* M_vec / M_mix;        % mass fractions

% Mass-fraction weighted specific heats (gas phase only)
Cv_gas = sum(x_vec .* Cv_vec);
Cp_gas = sum(x_vec .* Cp_vec);

% TiO2 corrections (1 wt% anatase, rho=4230 kg/m3, Cv≈460, Cp=710 J/(kg·K))
TiO2_wf = TiO2_wt_pct / 100;
Cv_mix   = (1 - TiO2_wf) * Cv_gas + TiO2_wf * 460.0;
Cp_mix   = (1 - TiO2_wf) * Cp_gas + TiO2_wf * 710.0;

% TiO2 volume fraction (using estimated supercritical density ~850 kg/m3)
rho_fluid_est = 850.0;
TiO2_phi = (TiO2_wf/4230) / (TiO2_wf/4230 + (1-TiO2_wf)/rho_fluid_est);

% PR-EOS base parameters
a0_vec = 0.45724 * R_M^2 * Tc_vec.^2 ./ Pc_vec;
b_vec  = 0.07780 * R_M   * Tc_vec    ./ Pc_vec;
b_mix  = sum(y_vec .* b_vec);

fprintf('Mixture: M=%.4f g/mol | Cv=%.1f | Cp=%.1f J/(kg·K)\n', ...
        M_mix*1000, Cv_mix, Cp_mix);
fprintf('TiO2:   wf=%.2f%% | phi=%.4f%%\n', TiO2_wf*100, TiO2_phi*100);

% ── DERIVED HARDWARE CONSTANTS ────────────────────────────────────────────────
V_vessel    = V_VESSEL_L / 1000;                           % [m3]
T_env_K     = T_AMBIENT_C + 273.15;                        % [K]
T_inkbird_K = T_INKBIRD_C + 273.15;                        % [K]
T_precond_K = T_PRECOND_C + 273.15;                        % [K]
UA_wall     = UA_WALL_W_K;
UA_inkbird  = UA_INKBIRD_W_K;
M_therm     = M_VESSEL_THERM;
P_boost_Pa  = min(BOOSTER_RATIO * P_DRIVE_AIR_MPA * 1e6, 28.0e6);
K_valve     = Cv_VALVE_US * 2.404e-5;
K_vent      = Cv_VENT_US  * 2.404e-5;
P0_MPa      = 0.34;    % ~35 PSI gauge — vessel resting pressure

% Initial mass from ambient ideal-gas approximation
rho0 = P0_MPa * 1e6 * M_mix / (0.993 * R_M * T_env_K);
m0   = rho0 * V_vessel;

% Booster density via PR-EOS with mixture parameters
rho_boost = pr_eos_rho_build(P_boost_Pa, T_env_K, ...
    y_vec, Tc_vec, Pc_vec, kp_vec, a0_vec, M_mix, b_mix, kij_12, kij_13, kij_23);

fprintf('Booster: %.1f MPa | rho_boost: %.1f kg/m3 | m0: %.5f kg\n', ...
        P_boost_Pa/1e6, rho_boost, m0);

% ── CREATE MODEL ──────────────────────────────────────────────────────────────
if bdIsLoaded(MODEL), close_system(MODEL, 0); end
if exist([MODEL '.slx'], 'file'), delete([MODEL '.slx']); end
new_system(MODEL);
open_system(MODEL);

add = @(lib, name, pos) add_block(lib, [MODEL '/' name], 'Position', pos);

set_param(MODEL, 'StopTime', num2str(SIM_TIME), ...
          'SolverType', 'Fixed-step', 'Solver', 'ode4', ...
          'FixedStep', num2str(DT));

% ── BLOCKS ────────────────────────────────────────────────────────────────────
% Setpoint ramp
add('simulink/Sources/Clock',              'Clock',    [50  60  80  80]);
add('simulink/Math Operations/Gain',       'RampGain', [130 60 180  80]);
set_param([MODEL '/RampGain'], 'Gain', num2str(PRESS_RATE_MPA_MIN / 60));
add('simulink/Math Operations/Sum',        'RampSum',  [230 60 260  80]);
set_param([MODEL '/RampSum'], 'Inputs', '++');
add('simulink/Sources/Constant',           'P_init',   [130 130 180 150]);
set_param([MODEL '/P_init'], 'Value', num2str(P0_MPa));
add('simulink/Math Operations/MinMax',     'SP_Clamp', [310 55 360  85]);
set_param([MODEL '/SP_Clamp'], 'Function','min','Inputs','2','InputSameDT','off');
add('simulink/Sources/Constant',           'P_target', [230 130 280 150]);
set_param([MODEL '/P_target'], 'Value', num2str(P_TARGET_MPA));

% Temperature pre-condition gate
% Switch: u1=ramp, u2=T_Lag (K), u3=P_hold; pass u1 when T_Lag >= T_precond_K
add('simulink/Signal Routing/Switch',      'TempGate', [395 55 435  85]);
set_param([MODEL '/TempGate'], 'Criteria','u2 >= Threshold', ...
    'Threshold', num2str(T_precond_K));
add('simulink/Sources/Constant',           'P_hold',   [310 130 360 150]);
set_param([MODEL '/P_hold'], 'Value', num2str(P0_MPa));

% Error sum
add('simulink/Math Operations/Sum',        'ErrSum',   [475 55 505  85]);
set_param([MODEL '/ErrSum'], 'Inputs', '+-');

% Adaptive PID — stateless MATLAB Function block (no persistent variables).
% State (integral + prev-error) is held by Unit Delay blocks outside the function.
% This avoids all sample-time issues — the function is purely combinatorial.
% Inputs:  1=e  2=P_meas(MPa)  3=SP(MPa)  4=x_int  5=e_prev
% Outputs: 1=valve_cmd(0-100%)  2=x_int_new  3=e_new
add('simulink/User-Defined Functions/MATLAB Function', 'AdaptivePID', [535 30 680 130]);

% Unit Delay blocks carry the PID state between steps
add('simulink/Discrete/Unit Delay', 'IntDelay', [535 145 600 175]);
set_param([MODEL '/IntDelay'], 'SampleTime', num2str(DT), 'X0', '0');
add('simulink/Discrete/Unit Delay', 'ErrDelay', [535 185 600 215]);
set_param([MODEL '/ErrDelay'], 'SampleTime', num2str(DT), 'X0', '0');

% Valve chain
add('simulink/Discontinuities/Saturation', 'ValveSat', [655 55 700  85]);
set_param([MODEL '/ValveSat'], 'LowerLimit','0','UpperLimit','100');
add('simulink/Continuous/Transfer Fcn',    'ValveAct', [735 55 810  85]);
set_param([MODEL '/ValveAct'], 'Numerator','[1]', ...
    'Denominator', sprintf('[%f 1]', TAU_VALVE_S));

% Vent command (0=closed; set>0 for depressurize)
add('simulink/Sources/Constant',           'VentCmd',  [735 160 790 180]);
set_param([MODEL '/VentCmd'], 'Value','0');

% MATLAB Function plant
add('simulink/User-Defined Functions/MATLAB Function', 'CO2_Plant', [855 30 985 200]);

% State integrators
add('simulink/Continuous/Integrator',      'm_Int',    [1030 50 1070  80]);
set_param([MODEL '/m_Int'], 'InitialCondition', num2str(m0));
add('simulink/Continuous/Integrator',      'T_Int',    [1030 150 1070 180]);
set_param([MODEL '/T_Int'], 'InitialCondition', num2str(T_env_K));

% Sensor lags — State-Space form of 1/(tau*s+1) with InitialCondition support
add('simulink/Continuous/State-Space',     'P_Lag',    [1110 50 1175  80]);
set_param([MODEL '/P_Lag'], ...
    'A', num2str(-1/TAU_SENSOR_P_S), 'B', num2str(1/TAU_SENSOR_P_S), ...
    'C','1','D','0','InitialCondition', num2str(P0_MPa));

add('simulink/Continuous/State-Space',     'T_Lag',    [1110 150 1175 180]);
set_param([MODEL '/T_Lag'], ...
    'A', num2str(-1/TAU_SENSOR_T_S), 'B', num2str(1/TAU_SENSOR_T_S), ...
    'C','1','D','0','InitialCondition', num2str(T_env_K));

% Noise + measured pressure sum
add('simulink/Sources/Band-Limited White Noise', 'Noise', [1110 120 1155 150]);
set_param([MODEL '/Noise'], 'Cov','2.5e-6','Ts',num2str(DT),'seed','12345');
add('simulink/Math Operations/Sum',        'P_meas',   [1215 50 1245  80]);
set_param([MODEL '/P_meas'], 'Inputs','++');

% Scopes
add('simulink/Sinks/Scope', 'PScope', [1320 45  1360  85]);
set_param([MODEL '/PScope'], 'NumInputPorts','2');
add('simulink/Sinks/Scope', 'TScope', [1320 150 1360 180]);
add('simulink/Sinks/Scope', 'VScope', [1320 250 1360 280]);
add('simulink/Sinks/Scope', 'MScope', [1320 350 1360 380]);

% To Workspace logging
TW_LIB  = 'simulink/Sinks/To Workspace';
TW_ARGS = {'SaveFormat','Array','MaxDataPoints','inf','SampleTime',num2str(DT)};

add(TW_LIB, 'Log_t',  [1430 45  1490  75]);
set_param([MODEL '/Log_t'],  'VariableName','t_log',  TW_ARGS{:});
add(TW_LIB, 'Log_P',  [1430 95  1490 125]);
set_param([MODEL '/Log_P'],  'VariableName','P_log',  TW_ARGS{:});
add(TW_LIB, 'Log_SP', [1430 145 1490 175]);
set_param([MODEL '/Log_SP'], 'VariableName','SP_log', TW_ARGS{:});
add(TW_LIB, 'Log_T',  [1430 195 1490 225]);
set_param([MODEL '/Log_T'],  'VariableName','T_log',  TW_ARGS{:});
add(TW_LIB, 'Log_V',  [1430 245 1490 275]);
set_param([MODEL '/Log_V'],  'VariableName','V_log',  TW_ARGS{:});
add(TW_LIB, 'Log_M',  [1430 295 1490 325]);
set_param([MODEL '/Log_M'],  'VariableName','M_log',  TW_ARGS{:});

% ── SET MATLAB FUNCTION SCRIPTS ───────────────────────────────────────────────
% Must be done BEFORE save→close→reload so all ports are registered correctly.
rt = sfroot;

% ── AdaptivePID script ────────────────────────────────────────────────────────
pid_chart = rt.find('-isa','Stateflow.EMChart','Path',[MODEL '/AdaptivePID']);
pid_chart.Script = [ ...
'function [u, x_int_new, e_new] = AdaptivePID(e, P_meas, SP, x_int, e_prev)' newline ...
'% Stateless adaptive gain-scheduled PID — state held by Unit Delay blocks.' newline ...
'% No persistent variables => no sample-time restrictions.' newline ...
'Ts=0.1; N=20; P_TARGET=28.0; Kb=0.1;' newline ...
'% Two-regime gain schedule (2500 psi = 17.2 MPa crossover):' newline ...
'%   0-17.2 MPa: gains RISE  (high compressibility, needs more flow)' newline ...
'%  17.2-28 MPa: gains FALL  (dense fluid, hair-trigger response)' newline ...
'P_bp  = [0,   5,   10,  17.2, 20,  24,  27,  28 ];' newline ...
'Kp_bp = [50,  58,  65,  60,   45,  32,  22,  18 ];' newline ...
'Ki_bp = [6,   7,   8,   7,    5,   4,   3,   3  ];' newline ...
'Kd_bp = [2.5, 2.5, 2.0, 1.5,  1.0, 0.8, 0.5, 0.5];' newline ...
'in_hold = (SP >= P_TARGET - 0.02);' newline ...
'if in_hold' newline ...
'    Kp=35.0; Ki=12.0; Kd=0.5;' newline ...
'else' newline ...
'    P_c = max(0, min(P_meas, P_bp(end)));' newline ...
'    Kp = interp1(P_bp, Kp_bp, P_c, ''linear'');' newline ...
'    Ki = interp1(P_bp, Ki_bp, P_c, ''linear'');' newline ...
'    Kd = interp1(P_bp, Kd_bp, P_c, ''linear'');' newline ...
'end' newline ...
'de = (e - e_prev) / Ts;' newline ...
'de_f = de * N / (1 + N*Ts);' newline ...
'u_raw = Kp*e + Ki*x_int + Kd*de_f;' newline ...
'u = max(min(u_raw, 100), 0);' newline ...
'x_int_new = x_int + Ts*e + Ts*Kb*(u - u_raw);' newline ...
'e_new = e;' newline ...
'end' newline ...
];

% ── CO2_Plant script ──────────────────────────────────────────────────────────
chart = rt.find('-isa','Stateflow.EMChart','Path',[MODEL '/CO2_Plant']);
chart.Script = sprintf([ ...
'function [dm_dt, dT_dt, P_MPa] = CO2_Plant(u_v, u_vent, m_kg, T_K)\n' ...
'%% PR-EOS (van der Waals mixing) + mass/energy balance\n' ...
'%% Pure gas (CO2, N2, or Ar)  |  INKBIRD heater  |  TiO2 nanofluid\n' ...
'R_M=8.314;\n' ...
'%% Component critical properties and kappa\n' ...
'Tc=[304.13,126.192,150.86]; Pc=[7.377e6,3.3958e6,4.898e6]; kp=[0.7080,0.4316,0.3746];\n' ...
'%% Mole fractions (embedded at build time)\n' ...
'y=[%f,%f,%f];\n' ...
'%% Binary interaction params (CO2-N2, CO2-Ar, N2-Ar)\n' ...
'kij_12=%f; kij_13=%f; kij_23=%f;\n' ...
'%% Hardware + mixture constants (embedded at build time)\n' ...
'V_ves=%e; K_valve=%e; K_vent=%e;\n' ...
'UA_wall=%.3f; T_env_K=%.3f; P_boost=%.6e; rho_boost=%.4f;\n' ...
'Cv_sp=%.2f; Cp_sp=%.2f; M_mix=%.6f; b_mix=%.8e;\n' ...
'UA_inkbird=%.3f; T_inkbird_K=%.3f; M_therm=%.3f; TiO2_phi=%f;\n' ...
'a0=[%.6e,%.6e,%.6e];\n' ...
'%% State guards\n' ...
'm=max(m_kg,1e-2); T=max(min(T_K,1200),200);\n' ...
'%% PR-EOS a_mix(T) — van der Waals mixing (unrolled for codegen)\n' ...
'alph=(1+kp.*(1-sqrt(T./Tc))).^2;\n' ...
'a_T=a0.*alph;\n' ...
'a_mix=y(1)^2*a_T(1)+y(2)^2*a_T(2)+y(3)^2*a_T(3)...\n' ...
'     +2*y(1)*y(2)*sqrt(a_T(1)*a_T(2))*(1-kij_12)...\n' ...
'     +2*y(1)*y(3)*sqrt(a_T(1)*a_T(3))*(1-kij_13)...\n' ...
'     +2*y(2)*y(3)*sqrt(a_T(2)*a_T(3))*(1-kij_23);\n' ...
'%% PR-EOS: P from (rho, T) — molar volume from mass density\n' ...
'rho_mol=(m/V_ves)/M_mix;\n' ...
'Vm=1/rho_mol;\n' ...
'Vm_s=max(Vm,b_mix*1.001);\n' ...
'P_Pa=R_M*T/(Vm_s-b_mix)-a_mix/(Vm_s*(Vm_s+b_mix)+b_mix*(Vm_s-b_mix));\n' ...
'P_Pa=max(P_Pa,1e4); P_MPa=P_Pa/1e6;\n' ...
'%% Effective density with TiO2 volume fraction\n' ...
'rho=m/V_ves;\n' ...
'rho_eff=(1-TiO2_phi)*rho+TiO2_phi*4230;\n' ...
'%% Valve flow in\n' ...
'dP_in=max(P_boost-P_Pa,0);\n' ...
'mdot_in=K_valve*(u_v/100)*sqrt(2*rho_boost*dP_in);\n' ...
'%% Vent flow out\n' ...
'dP_out=max(P_Pa-1.013e5,0);\n' ...
'mdot_out=K_vent*(u_vent/100)*sqrt(2*max(rho_eff,0.1)*dP_out);\n' ...
'%% Mass balance\n' ...
'dm_dt=mdot_in-mdot_out;\n' ...
'%% Energy balance: inlet enthalpy + compression work + wall loss + INKBIRD\n' ...
'h_diff=Cp_sp*(T_env_K-T);\n' ...
'Q_wall=UA_wall*(T_env_K-T);\n' ...
'Q_inkbird=UA_inkbird*max(T_inkbird_K-T,0);\n' ...
'comp_W=dm_dt*P_Pa/max(rho_eff,0.1);\n' ...
'denom=max(m*Cv_sp+M_therm,1e-2);\n' ...
'dT_raw=(mdot_in*h_diff+comp_W+Q_wall+Q_inkbird)/denom;\n' ...
'dT_dt=max(min(dT_raw,200),-200);\n' ...
'end\n' ...
], ...
y_CO2, y_N2, y_Ar, ...
kij_12, kij_13, kij_23, ...
V_vessel, K_valve, K_vent, ...
UA_wall, T_env_K, P_boost_Pa, rho_boost, ...
Cv_mix, Cp_mix, M_mix, b_mix, ...
UA_inkbird, T_inkbird_K, M_therm, TiO2_phi, ...
a0_vec(1), a0_vec(2), a0_vec(3));

% ── Save → close → reload (registers CO2_Plant ports) ────────────────────────
save_system(MODEL, [MODEL '.slx']);
close_system(MODEL, 0);
load_system(MODEL);

% ── WIRE ──────────────────────────────────────────────────────────────────────
% Setpoint ramp
add_line(MODEL, 'Clock/1',    'RampGain/1');
add_line(MODEL, 'RampGain/1', 'RampSum/1');
add_line(MODEL, 'P_init/1',   'RampSum/2');
add_line(MODEL, 'RampSum/1',  'SP_Clamp/1');
add_line(MODEL, 'P_target/1', 'SP_Clamp/2');

% Temperature pre-condition gate
add_line(MODEL, 'SP_Clamp/1', 'TempGate/1');   % ramp (pass when T >= T_PRECOND)
add_line(MODEL, 'T_Lag/1',    'TempGate/2');   % control: sensor T in K
add_line(MODEL, 'P_hold/1',   'TempGate/3');   % hold at P0 until pre-cond met

% Error → AdaptivePID → valve chain
add_line(MODEL, 'TempGate/1', 'ErrSum/1');          % gated setpoint (+)
add_line(MODEL, 'P_meas/1',   'ErrSum/2');          % measured (-)
add_line(MODEL, 'ErrSum/1',   'AdaptivePID/1');     % e
add_line(MODEL, 'P_meas/1',   'AdaptivePID/2');     % P_meas (gain scheduling)
add_line(MODEL, 'TempGate/1', 'AdaptivePID/3');     % SP (hold detection)
add_line(MODEL, 'IntDelay/1', 'AdaptivePID/4');     % x_int state feedback
add_line(MODEL, 'ErrDelay/1', 'AdaptivePID/5');     % e_prev state feedback
add_line(MODEL, 'AdaptivePID/1', 'ValveSat/1');     % valve command
add_line(MODEL, 'AdaptivePID/2', 'IntDelay/1');     % x_int_new → delay
add_line(MODEL, 'AdaptivePID/3', 'ErrDelay/1');     % e_new → delay
add_line(MODEL, 'ValveSat/1', 'ValveAct/1');

% Plant: 4 inputs
add_line(MODEL, 'ValveAct/1', 'CO2_Plant/1');  % u_valve
add_line(MODEL, 'VentCmd/1',  'CO2_Plant/2');  % u_vent
add_line(MODEL, 'm_Int/1',    'CO2_Plant/3');  % m_gas
add_line(MODEL, 'T_Int/1',    'CO2_Plant/4');  % T_K

% Plant: 3 outputs → integrators and pressure chain
add_line(MODEL, 'CO2_Plant/1', 'm_Int/1');     % dm_dt
add_line(MODEL, 'CO2_Plant/2', 'T_Int/1');     % dT_dt
add_line(MODEL, 'CO2_Plant/3', 'P_Lag/1');     % P_MPa → sensor lag

% Pressure measurement chain
add_line(MODEL, 'P_Lag/1',    'P_meas/1');
add_line(MODEL, 'Noise/1',    'P_meas/2');

% Temperature lag (display only; also feeds TempGate control input)
add_line(MODEL, 'T_Int/1',    'T_Lag/1');

% Scopes
add_line(MODEL, 'P_meas/1',      'PScope/1');
add_line(MODEL, 'TempGate/1',    'PScope/2');  % gated SP
add_line(MODEL, 'T_Lag/1',       'TScope/1');
add_line(MODEL, 'ValveAct/1',    'VScope/1');
add_line(MODEL, 'm_Int/1',       'MScope/1');

% To Workspace logging
add_line(MODEL, 'Clock/1',       'Log_t/1');
add_line(MODEL, 'P_meas/1',      'Log_P/1');
add_line(MODEL, 'TempGate/1',    'Log_SP/1'); % log gated SP
add_line(MODEL, 'T_Lag/1',       'Log_T/1');
add_line(MODEL, 'ValveAct/1',    'Log_V/1');
add_line(MODEL, 'm_Int/1',       'Log_M/1');

% ── SAVE ──────────────────────────────────────────────────────────────────────
save_system(MODEL, [MODEL '.slx']);
fprintf('\nDone: %s.slx saved  (Experiment %d)\n', MODEL, EXPERIMENT_ID);
fprintf('Next: run_exact\n');

% ── LOCAL FUNCTION: PR-EOS density solver with mixing rules ──────────────────
function rho = pr_eos_rho_build(P_Pa, T_K, y_vec, Tc_vec, Pc_vec, kp_vec, ...
                                 a0_vec, M_mix, b_mix, kij_12, kij_13, kij_23)
    R_M   = 8.314;
    alph  = (1 + kp_vec .* (1 - sqrt(T_K./Tc_vec))).^2;
    a_T   = a0_vec .* alph;
    a_mix = y_vec(1)^2*a_T(1) + y_vec(2)^2*a_T(2) + y_vec(3)^2*a_T(3) ...
          + 2*y_vec(1)*y_vec(2)*sqrt(a_T(1)*a_T(2))*(1-kij_12) ...
          + 2*y_vec(1)*y_vec(3)*sqrt(a_T(1)*a_T(3))*(1-kij_13) ...
          + 2*y_vec(2)*y_vec(3)*sqrt(a_T(2)*a_T(3))*(1-kij_23);
    A = a_mix * P_Pa / (R_M*T_K)^2;
    B = b_mix * P_Pa / (R_M*T_K);
    z_roots = roots([1, -(1-B), (A-3*B^2-2*B), -(A*B-B^2-B^3)]);
    z_real  = real(z_roots(abs(imag(z_roots))<1e-8 & real(z_roots)>B));
    if isempty(z_real), Z=1.0; else, Z=max(z_real); end
    rho = P_Pa * M_mix / (Z * R_M * T_K);
end
