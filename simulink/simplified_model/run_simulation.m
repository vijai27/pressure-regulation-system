% run_simulation.m — Build, run, and plot the simplified scCO2 model
%
% Always rebuilds scCO2_plant.slx so code changes take effect immediately.
% Reads results from To Workspace variables (t_log, P_log, SP_log, T_log, V_log)
% that build_model.m adds to the model.
%
% What to check:
%   1. Pressure ramp closely follows 350 kPa/min setpoint
%   2. No overshoot past 28 MPa
%   3. Temperature spike visible during pressurisation (compression heating)
%   4. Hold phase: pressure stable within ±0.5 MPa
%   5. Valve % increases as booster differential drops near 28 MPa

clc;

% ── Always rebuild ────────────────────────────────────────────────────────────
% NOTE: build_model.m uses clc (not clear) so it does NOT wipe this workspace.
fprintf('=== Building scCO2_plant.slx ===\n');
build_model;

% Declare these AFTER build_model so they are never accidentally cleared.
MODEL    = 'scCO2_plant';
SIM_TIME = 6000;   % seconds

% ── Run simulation ────────────────────────────────────────────────────────────
fprintf('=== Running simulation (%d s) ===\n', SIM_TIME);
set_param(MODEL, 'StopTime', num2str(SIM_TIME));

% Capture output explicitly — guarantees To Workspace data is accessible
% regardless of MATLAB version workspace scoping rules.
out = sim(MODEL);

% ── Read logged signals ───────────────────────────────────────────────────────
% Try base workspace first (standard), then fall back to sim output struct.
if exist('t_log','var')
    t      = t_log;
    P_meas = P_log;
    P_sp   = SP_log;
    T_meas = T_log;
    V_pct  = V_log;
elseif isstruct(out) || isobject(out)
    try
        t      = out.t_log;
        P_meas = out.P_log;
        P_sp   = out.SP_log;
        T_meas = out.T_log;
        V_pct  = out.V_log;
    catch
        error(['Simulation did not save t_log/P_log/SP_log/T_log/V_log.\n' ...
               'Delete scCO2_plant.slx, run build_model, then run_simulation.']);
    end
else
    error(['Simulation did not save t_log/P_log/SP_log/T_log/V_log.\n' ...
           'Delete scCO2_plant.slx, run build_model, then run_simulation.']);
end

% ── Plot ──────────────────────────────────────────────────────────────────────
figure('Name','scCO2 Simulation Results','NumberTitle','off', ...
       'Color','w','Position',[100 100 1100 700]);

% -- Pressure --
ax1 = subplot(3,1,1);
plot(t/60, P_meas, 'b-',  'LineWidth',1.8, 'DisplayName','Measured P'); hold on;
plot(t/60, P_sp,   'r--', 'LineWidth',1.5, 'DisplayName','Setpoint P');
yline(28.0,'k:','LineWidth',1,'DisplayName','28 MPa limit');
xlabel('Time (min)'); ylabel('Pressure (MPa)');
title('Vessel Pressure vs Time');
legend('Location','northwest'); grid on; ylim([0 30]);
xline(0,   '--','PRESSURIZE',        'LabelVerticalAlignment','bottom');
xline(50,  '--','HOLD start ~50 min','LabelVerticalAlignment','bottom');

% -- Temperature --
ax2 = subplot(3,1,2);
plot(t/60, T_meas, 'm-','LineWidth',1.5);
yline(60.0,'k:','LineWidth',1);
xlabel('Time (min)'); ylabel('Temperature (°C)');
title('Vessel Temperature (compression heating visible during pressurisation)');
grid on;

% -- Valve % --
ax3 = subplot(3,1,3);
plot(t/60, V_pct, 'g-','LineWidth',1.5);
xlabel('Time (min)'); ylabel('Valve Opening (%)');
title('Motorized Valve Position');
grid on; ylim([0 105]);

linkaxes([ax1 ax2 ax3],'x');

% ── Summary stats ─────────────────────────────────────────────────────────────
fprintf('\n=== Simulation Summary ===\n');
fprintf('Max pressure:    %.3f MPa  (limit: 28.0 MPa)\n', max(P_meas));
fprintf('Final pressure:  %.3f MPa\n', P_meas(end));
fprintf('Max temperature: %.2f degC\n', max(T_meas));
fprintf('Min temperature: %.2f degC\n', min(T_meas));

% Average pressurisation rate (0.15 → 27 MPa window)
rise_idx = find(P_meas >= 0.15 & P_meas <= 27.0);
if numel(rise_idx) > 10
    dp       = diff(P_meas(rise_idx(1:10:end))) * 1000;   % kPa
    dt_s     = diff(t(rise_idx(1:10:end)));
    avg_rate = mean(dp ./ dt_s) * 60;                     % kPa/min
    fprintf('Avg pressurize rate: %.1f kPa/min  (target: 350)\n', avg_rate);
end
fprintf('==========================\n\n');
fprintf('Tip: open scCO2_plant.slx, double-click PID block -> Tune.\n');
