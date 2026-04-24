% build_model.m — Simplified scCO2 Simulink model
%
% Physics (matching simulator.py heuristics):
%   dP  = K_FLOW * (valve/100) * sqrt(max(P_BOOSTER - P, 0))
%   dT  = K_COMP * dP / P_BOOSTER  -  K_INK * (T - T_SET)
%
% Temperature pre-condition gate (matches Python state machine):
%   SP is held at P0 until T_int >= T_PRECOND (55 °C).
%   Once the pre-condition is met, the ramp starts and runs normally.
%   The INKBIRD model (-K_INK*(T-T_SET)) drives T to 60 °C independently.
%
% Port creation strategy: set chart.Script THEN save→close→reload.
%
% Outputs: scCO2_plant.slx  +  workspace vars t_log P_log SP_log T_log V_log

clc;

MODEL = 'scCO2_plant';

% ── Parameters ────────────────────────────────────────────────────────────────
P_BOOSTER  = 28.0;      % MPa  (max booster pressure)
K_FLOW     = 0.003;     % MPa^0.5/s per 1% valve opening
K_COMP     = 0.8;       % °C per MPa/s  (compression heating)
K_INK      = 0.067;     % 1/s  INKBIRD thermal coupling  (τ ≈ 15 s)
T_SET      = 60.0;      % °C  INKBIRD setpoint
T_PRECOND  = 55.0;      % °C  minimum temperature to start pressurisation
T0         = 25.0;      % °C  initial vessel temperature
P0         = 0.34;      % MPa initial vessel pressure (~35 PSI gauge)
DT         = 0.1;       % s   fixed simulation step
PRESS_RATE = 0.35/60;   % MPa/s  (350 kPa/min)
P_TARGET   = 28.0;      % MPa
SIM_TIME   = 7200;      % s  (2 h covers heat-up + full pressurize + hold)

% ── Create / overwrite model ───────────────────────────────────────────────────
if bdIsLoaded(MODEL), close_system(MODEL, 0); end
if exist([MODEL '.slx'], 'file'), delete([MODEL '.slx']); end

new_system(MODEL);
open_system(MODEL);

add = @(lib, name, pos) add_block(lib, [MODEL '/' name], 'Position', pos);

set_param(MODEL, 'StopTime',   num2str(SIM_TIME), ...
                 'SolverType', 'Fixed-step', ...
                 'Solver',     'ode4', ...
                 'FixedStep',  num2str(DT));

% ── Setpoint ramp:  raw_SP = min( Clock*rate + P0,  P_TARGET ) ───────────────
add('simulink/Sources/Clock',          'Clock',    [ 50  60  80  80]);
add('simulink/Math Operations/Gain',   'RampGain', [130  60 180  80]);
set_param([MODEL '/RampGain'], 'Gain', num2str(PRESS_RATE));

add('simulink/Math Operations/Sum',    'RampSum',  [230  60 260  80]);
set_param([MODEL '/RampSum'], 'Inputs', '++');

add('simulink/Sources/Constant',       'P_start',  [130 120 180 140]);
set_param([MODEL '/P_start'], 'Value', num2str(P0));

add('simulink/Math Operations/MinMax', 'SP_Clamp', [310  55 360  85]);
set_param([MODEL '/SP_Clamp'], 'Function','min','Inputs','2','InputSameDT','off');

add('simulink/Sources/Constant',       'P_target', [230 120 280 140]);
set_param([MODEL '/P_target'], 'Value', num2str(P_TARGET));

% ── Temperature pre-condition gate ────────────────────────────────────────────
% Switch: output = SP_Clamp (ramp) when T >= T_PRECOND, else P0 (hold).
% Inputs: u1=ramp, u2=T_vessel (control), u3=P_hold (ambient).
add('simulink/Signal Routing/Switch',  'TempGate', [390  55 430  85]);
set_param([MODEL '/TempGate'], 'Criteria','u2 >= Threshold', ...
    'Threshold', num2str(T_PRECOND));

add('simulink/Sources/Constant',       'P_hold',   [310 130 360 150]);
set_param([MODEL '/P_hold'], 'Value', num2str(P0));

% ── Error = gated_SP - measured ──────────────────────────────────────────────
add('simulink/Math Operations/Sum',    'ErrSum',   [470  55 500  85]);
set_param([MODEL '/ErrSum'], 'Inputs', '+-');

% ── PID (discrete-time, N=20 avoids stiff derivative filter) ─────────────────
try
    add('simulink/Controllers/PID Controller', 'PID', [530 45 620 95]);
catch
    add('simulink/Continuous/PID Controller',  'PID', [530 45 620 95]);
end
try
    set_param([MODEL '/PID'], ...
        'P','40','I','5','D','2','N','20', ...
        'LowerSaturationLimit','0','UpperSaturationLimit','100', ...
        'AntiWindupMode','clamping', ...
        'TimeDomain','discrete-time','SampleTime',num2str(DT));
catch
    set_param([MODEL '/PID'], ...
        'P','40','I','5','D','2','N','20', ...
        'LowerSaturationLimit','0','UpperSaturationLimit','100', ...
        'AntiWindupMode','clamping','SampleTime',num2str(DT));
end

% ── Valve saturation 0–100 % ──────────────────────────────────────────────────
add('simulink/Discontinuities/Saturation', 'ValveSat', [660 55 710 85]);
set_param([MODEL '/ValveSat'], 'LowerLimit','0','UpperLimit','100');

% ── Plant: single MATLAB Function (3 inputs, 2 outputs) ──────────────────────
%    inputs : valve_pct (%), P_vessel (MPa), T_vessel_C (°C)
%    outputs: dP (MPa/s), dT (°C/s)
add('simulink/User-Defined Functions/MATLAB Function', 'Plant', [760 30 870 160]);

% ── State integrators ─────────────────────────────────────────────────────────
add('simulink/Continuous/Integrator', 'P_int', [940  55 980  85]);
set_param([MODEL '/P_int'], 'InitialCondition', num2str(P0));

add('simulink/Continuous/Integrator', 'T_int', [940 155 980 185]);
set_param([MODEL '/T_int'], 'InitialCondition', num2str(T0));

% ── Scopes ────────────────────────────────────────────────────────────────────
add('simulink/Sinks/Scope', 'PScope', [1080  50 1120  80]);
set_param([MODEL '/PScope'], 'NumInputPorts','2');
add('simulink/Sinks/Scope', 'TScope', [1080 155 1120 185]);
add('simulink/Sinks/Scope', 'VScope', [1080 280 1120 310]);

% ── To Workspace — auto-save all signals during simulation ────────────────────
TW_LIB  = 'simulink/Sinks/To Workspace';
TW_ARGS = {'SaveFormat','Array','MaxDataPoints','inf','SampleTime',num2str(DT)};

add(TW_LIB, 'Log_t',  [1170  45 1230  75]);
set_param([MODEL '/Log_t'],  'VariableName','t_log',  TW_ARGS{:});

add(TW_LIB, 'Log_P',  [1170  95 1230 125]);
set_param([MODEL '/Log_P'],  'VariableName','P_log',  TW_ARGS{:});

add(TW_LIB, 'Log_SP', [1170 145 1230 175]);
set_param([MODEL '/Log_SP'], 'VariableName','SP_log', TW_ARGS{:});

add(TW_LIB, 'Log_T',  [1170 195 1230 225]);
set_param([MODEL '/Log_T'],  'VariableName','T_log',  TW_ARGS{:});

add(TW_LIB, 'Log_V',  [1170 245 1230 275]);
set_param([MODEL '/Log_V'],  'VariableName','V_log',  TW_ARGS{:});

% ── MATLAB Function script ────────────────────────────────────────────────────
rt    = sfroot;
chart = rt.find('-isa','Stateflow.EMChart','Path',[MODEL '/Plant']);
chart.Script = sprintf([ ...
    'function [dP, dT] = Plant(valve_pct, P, T_C)\n' ...
    'P_BOOSTER=%f; K_FLOW=%f; K_COMP=%f; K_INK=%f; T_SET=%f;\n' ...
    'v = valve_pct / 100;\n' ...
    'dP_flow = K_FLOW * v * sqrt(max(P_BOOSTER - P, 0));\n' ...
    'dP = dP_flow;\n' ...
    'dT = K_COMP * dP_flow / P_BOOSTER - K_INK * (T_C - T_SET);\n' ...
    ], P_BOOSTER, K_FLOW, K_COMP, K_INK, T_SET);

% ── Save → close → reload (registers MATLAB Function ports) ──────────────────
save_system(MODEL, [MODEL '.slx']);
close_system(MODEL, 0);
load_system(MODEL);

% ── Wire ──────────────────────────────────────────────────────────────────────
% Setpoint ramp
add_line(MODEL, 'Clock/1',    'RampGain/1');
add_line(MODEL, 'RampGain/1', 'RampSum/1');
add_line(MODEL, 'P_start/1',  'RampSum/2');
add_line(MODEL, 'RampSum/1',  'SP_Clamp/1');
add_line(MODEL, 'P_target/1', 'SP_Clamp/2');

% Temperature pre-condition gate
add_line(MODEL, 'SP_Clamp/1', 'TempGate/1');   % ramp (pass when T >= T_PRECOND)
add_line(MODEL, 'T_int/1',    'TempGate/2');   % control: T_vessel drives switch
add_line(MODEL, 'P_hold/1',   'TempGate/3');   % hold at P0 until pre-cond met

% Error → PID → valve
add_line(MODEL, 'TempGate/1', 'ErrSum/1');     % gated setpoint (+)
add_line(MODEL, 'P_int/1',    'ErrSum/2');     % measured (-)
add_line(MODEL, 'ErrSum/1',   'PID/1');
add_line(MODEL, 'PID/1',      'ValveSat/1');

% Plant: 3 inputs, 2 outputs
add_line(MODEL, 'ValveSat/1', 'Plant/1');      % valve_pct
add_line(MODEL, 'P_int/1',    'Plant/2');      % P_vessel
add_line(MODEL, 'T_int/1',    'Plant/3');      % T_vessel_C

add_line(MODEL, 'Plant/1',    'P_int/1');      % dP → pressure integrator
add_line(MODEL, 'Plant/2',    'T_int/1');      % dT → temperature integrator

% Scopes
add_line(MODEL, 'P_int/1',    'PScope/1');
add_line(MODEL, 'TempGate/1', 'PScope/2');     % show gated SP (not raw ramp)
add_line(MODEL, 'T_int/1',    'TScope/1');
add_line(MODEL, 'ValveSat/1', 'VScope/1');

% To Workspace
add_line(MODEL, 'Clock/1',    'Log_t/1');
add_line(MODEL, 'P_int/1',    'Log_P/1');
add_line(MODEL, 'TempGate/1', 'Log_SP/1');    % log gated SP
add_line(MODEL, 'T_int/1',    'Log_T/1');
add_line(MODEL, 'ValveSat/1', 'Log_V/1');

% ── Final save ────────────────────────────────────────────────────────────────
save_system(MODEL, [MODEL '.slx']);
fprintf('\nDone: %s.slx saved.\n', MODEL);
fprintf('Experiment phases: heat-up (~30s) → pressurize (~80min) → hold\n');
