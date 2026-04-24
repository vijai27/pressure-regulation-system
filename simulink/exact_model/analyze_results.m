% analyze_results.m — Load, plot, and export pressure vessel simulation data
%
% Run AFTER build_model_exact.m and simulating scCO2_exact.slx.
% Workspace variables t_log, P_log, SP_log, T_log, V_log, M_log must exist.
%
% Outputs:
%   - 3-panel figure (Pressure, Temperature, Valve/Mass)
%   - Printed statistics (ramp rate, hold error, peak overshoot)
%   - CSV file: results/sim_YYYYMMDD_HHMMSS.csv

clear_vars = false;   % set true to wipe workspace after export (usually false)

% ── 1. LOAD DATA ──────────────────────────────────────────────────────────────
% In newer MATLAB, sim() stores To Workspace outputs in its return value
% rather than the base workspace.  Check base workspace first, then 'out'.
vars = {'t_log','P_log','SP_log','T_log','V_log','M_log'};

in_base = all(cellfun(@(v) evalin('base',['exist(''' v ''',''var'')']), vars));

if in_base
    % Standard path — variables already in workspace
    t   = evalin('base','t_log');
    P   = evalin('base','P_log');
    SP  = evalin('base','SP_log');
    T_K = evalin('base','T_log');
    V   = evalin('base','V_log');
    M   = evalin('base','M_log');
elseif evalin('base','exist(''out'',''var'')')
    % Newer MATLAB: pull from SimulationOutput object returned by sim()
    try
        out = evalin('base','out');
        t   = out.t_log;
        P   = out.P_log;
        SP  = out.SP_log;
        T_K = out.T_log;
        V   = out.V_log;
        M   = out.M_log;
    catch ME
        error(['Could not read signals from ''out'' struct: %s\n' ...
               'Run:  out = sim(''scCO2_exact'')  then analyze_results.'], ME.message);
    end
else
    error(sprintf(['Missing workspace variables: %s\n' ...
        'Steps to fix:\n' ...
        '  1. Run build_model_exact in the Command Window\n' ...
        '  2. Run:  out = sim(''scCO2_exact'')\n' ...
        '  3. Run analyze_results again'], strjoin(vars, ', ')));
end

% Flatten column vectors if needed
t=t(:); P=P(:); SP=SP(:); T_K=T_K(:); V=V(:); M=M(:);
T_C = T_K - 273.15;             % convert to Celsius for display

% ── 2. IDENTIFY PHASES ────────────────────────────────────────────────────────
P_TARGET   = SP(end);            % final setpoint = hold pressure
HOLD_BAND  = 0.02 * P_TARGET;   % ±2 % of target = hold region

% Pressurize phase: SP is still ramping (SP < P_TARGET - tolerance)
idx_press = SP < (P_TARGET - 0.001);
% Hold phase: SP has reached target
idx_hold  = SP >= (P_TARGET - 0.001);

t_ramp_end = t(find(idx_press, 1, 'last'));
if isempty(t_ramp_end), t_ramp_end = t(end); end

% ── 3. STATISTICS ─────────────────────────────────────────────────────────────
% Ramp rate: linear fit of P vs t during pressurize phase (skip first 5s)
warm = t > 5 & idx_press;
if sum(warm) > 10
    cf = polyfit(t(warm), P(warm), 1);
    ramp_rate_MPa_min = cf(1) * 60;
else
    ramp_rate_MPa_min = NaN;
end

% Hold error: std deviation of (P - SP) in hold phase (after 30s settling)
if sum(idx_hold) > 0
    t_hold_start = t(find(idx_hold, 1, 'first'));
    settled = idx_hold & t > (t_hold_start + 30);
    hold_err = P(settled) - SP(settled);
    hold_rmse = sqrt(mean(hold_err.^2));
    hold_std  = std(hold_err);
    hold_max  = max(abs(hold_err));
else
    hold_rmse = NaN; hold_std = NaN; hold_max = NaN;
end

% Peak overshoot
overshoot = max(P - SP);

% Time to reach 99% of target
idx_99 = find(P >= 0.99 * P_TARGET, 1, 'first');
t_99 = t(idx_99);

% Peak valve opening
valve_peak = max(V);

% Gas mass at hold
M_hold = M(idx_hold);
if ~isempty(M_hold), M_final = M_hold(end); else, M_final = M(end); end

fprintf('\n══════════════════════════════════════════════\n');
fprintf('  Pressure Vessel Simulation Results\n');
fprintf('══════════════════════════════════════════════\n');
fprintf('  Ramp rate (measured):   %.3f MPa/min\n', ramp_rate_MPa_min);
fprintf('  Target setpoint:        %.2f MPa\n', P_TARGET);
fprintf('  Time to 99%% of target:  %.0f s (%.1f min)\n', t_99, t_99/60);
fprintf('  Peak overshoot:         %.4f MPa (%.2f%%)\n', overshoot, overshoot/P_TARGET*100);
fprintf('  Hold RMSE:              %.4f MPa\n', hold_rmse);
fprintf('  Hold Std dev:           %.4f MPa\n', hold_std);
fprintf('  Hold Max deviation:     %.4f MPa\n', hold_max);
fprintf('  Peak valve opening:     %.1f %%\n', valve_peak);
fprintf('  Final gas mass:         %.4f kg\n', M_final);
fprintf('  Temperature range:      %.1f – %.1f °C\n', min(T_C), max(T_C));
fprintf('══════════════════════════════════════════════\n\n');

% ── 4. PLOT ───────────────────────────────────────────────────────────────────
fig = figure('Name','Pressure Vessel Simulation Results','NumberTitle','off', ...
             'Color','w','Position',[100 60 1100 750]);

% -- Panel 1: Pressure --
ax1 = subplot(3,1,1);
plot(t/60, P,  'b-', 'LineWidth',1.5, 'DisplayName','Measured P'); hold on;
plot(t/60, SP, 'r--','LineWidth',1.2, 'DisplayName','Setpoint');
yline(P_TARGET, 'k:', 'LineWidth',0.8, 'DisplayName','Target');
if sum(idx_hold) > 0
    xline(t_ramp_end/60, '--', 'Color',[0.5 0.5 0.5], 'LineWidth',0.8);
    text(t_ramp_end/60 + 0.2, P_TARGET*0.3, 'HOLD', ...
         'Color',[0.4 0.4 0.4], 'FontSize',9);
end
ylabel('Pressure (MPa)','FontSize',11);
title('Pressure vs Setpoint','FontSize',12,'FontWeight','bold');
legend('Location','southeast','FontSize',9);
grid on; box off;
ylim([0, P_TARGET * 1.08]);

% -- Panel 2: Temperature --
ax2 = subplot(3,1,2);
plot(t/60, T_C, 'r-', 'LineWidth',1.5);
yline(60, 'k--', 'LineWidth',0.8);
text(0.5, 62, 'INKBIRD setpoint (60°C)', 'Color','k','FontSize',8);
ylabel('Temperature (°C)','FontSize',11);
title('Vessel Temperature (sensor-lagged)','FontSize',12,'FontWeight','bold');
grid on; box off;

% -- Panel 3: Valve & Mass --
ax3 = subplot(3,1,3);
yyaxis left;
plot(t/60, V,  'b-', 'LineWidth',1.5, 'DisplayName','Valve (%)'); hold on;
ylabel('Valve Opening (%)','FontSize',11);
ylim([0, 110]);

yyaxis right;
plot(t/60, M*1000, 'm-', 'LineWidth',1.2, 'DisplayName','Gas mass (g)');
ylabel('Gas Mass (g)','FontSize',11);

xlabel('Time (min)','FontSize',11);
title('Valve Position & Gas Mass','FontSize',12,'FontWeight','bold');
legend('Location','northeast','FontSize',9);
grid on; box off;

linkaxes([ax1 ax2 ax3], 'x');
xlim([0, t(end)/60]);

% Build a rich title that includes experiment info if run via run_exact.m
if exist('EXPERIMENT_ID','var') && exist('EXP_NAMES','var')
    EXP_NAMES = {'CO2', 'CO2+TiO2', 'N2', 'N2+TiO2', 'Ar', 'Ar+TiO2'};
    gas_str = EXP_NAMES{min(EXPERIMENT_ID, numel(EXP_NAMES))};
    title_str = sprintf('Exp %d: %s  |  Target %.0f MPa  |  Ramp %.3f MPa/min', ...
        EXPERIMENT_ID, gas_str, P_TARGET, ramp_rate_MPa_min);
else
    title_str = sprintf('Pressure Vessel Digital Twin — Target: %.0f MPa | Ramp: %.3f MPa/min', ...
        P_TARGET, ramp_rate_MPa_min);
end
sgtitle(title_str, 'FontSize',13,'FontWeight','bold');

% ── 5. EXPORT TO CSV ──────────────────────────────────────────────────────────
if ~isfolder('results'), mkdir('results'); end
timestamp = datestr(now, 'yyyymmdd_HHMMSS');
csv_file  = fullfile('results', sprintf('sim_%s.csv', timestamp));

% Build table and write
T_table = table(t, P, SP, T_C, V, M, ...
    'VariableNames', {'time_s','pressure_MPa','setpoint_MPa', ...
                      'temperature_C','valve_pct','mass_gas_kg'});
writetable(T_table, csv_file);
fprintf('Data exported to: %s\n', csv_file);
fprintf('Rows: %d  |  Duration: %.0f s (%.1f min)\n\n', ...
        height(T_table), t(end), t(end)/60);

% ── 6. SAVE FIGURE ────────────────────────────────────────────────────────────
fig_file = fullfile('results', sprintf('sim_%s.png', timestamp));
exportgraphics(fig, fig_file, 'Resolution', 150);
fprintf('Figure saved: %s\n', fig_file);
