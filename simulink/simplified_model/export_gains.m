% export_gains.m — Extract tuned PID gains from the Simulink model
%                  and save them to config_gains.mat
%
% Run this AFTER using the interactive PID Tuner to find satisfactory gains.
%
% Workflow:
%   1. Open scCO2_plant.slx
%   2. Double-click the PID block → click "Tune" button
%   3. Adjust response slider until pressure ramp ≈ 350 kPa/min
%      with <5% overshoot at 28 MPa
%   4. Click "Apply" in PID Tuner
%   5. Run this script to save gains
%   6. Copy the printed values into config.py (PRESS_KP, PRESS_KI, PRESS_KD)

clear; clc;

MODEL = 'scCO2_plant';
PID_BLOCK = [MODEL '/PID'];

if ~bdIsLoaded(MODEL)
    load_system(MODEL);
end

% Read gains from PID block
Kp = str2double(get_param(PID_BLOCK, 'P'));
Ki = str2double(get_param(PID_BLOCK, 'I'));
Kd = str2double(get_param(PID_BLOCK, 'D'));
N  = str2double(get_param(PID_BLOCK, 'N'));   % filter coefficient

fprintf('\n=== Tuned PID Gains ===\n');
fprintf('  Kp = %.6f\n', Kp);
fprintf('  Ki = %.6f\n', Ki);
fprintf('  Kd = %.6f\n', Kd);
fprintf('  N  = %.4f  (derivative filter — informational)\n', N);

% Save to mat file
save('config_gains.mat', 'Kp', 'Ki', 'Kd', 'N');
fprintf('\nSaved to config_gains.mat\n');

% Print copy-paste block for config.py
fprintf('\n--- Paste into pressure_control/config.py ---\n');
fprintf('PRESS_KP = %.6f\n', Kp);
fprintf('PRESS_KI = %.6f\n', Ki);
fprintf('PRESS_KD = %.6f\n', Kd);
fprintf('---------------------------------------------\n\n');

% Optional: run a quick validation sim with these gains
response = input('Run validation simulation now? (y/n): ', 's');
if strcmpi(strtrim(response), 'y')
    run_simulation;
end
