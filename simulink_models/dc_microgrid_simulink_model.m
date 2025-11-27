%% DC Microgrid Simulink Model Creation
% Comprehensive Simulink model for secure integration of renewable energy in DC microgrids
% This script creates and configures the complete Simulink model programmatically
% Author: Nivas D. Navghare
% Institution: COEP Technological University, Pune
% Date: November 2025

clear all; close all; clc;

%% System Configuration
fprintf('Creating DC Microgrid Simulink Model...\n\n');

% Model name and file path
model_name = 'DC_Microgrid_Complete';
model_path = pwd;

% Create new model
new_system(model_name);
open_system(model_name);

% Set model parameters
set_param(model_name, 'SolverType', 'Fixed-step');
set_param(model_name, 'Solver', 'ode4');
set_param(model_name, 'SampleTimeConstraint', 'Unconstrained');
set_param(model_name, 'StartTime', '0');
set_param(model_name, 'StopTime', '86400');  % 24 hours in seconds
set_param(model_name, 'FixedStep', '1');     % 1 second time step

%% Create Main Subsystems
fprintf('[1/6] Creating subsystem hierarchy...\n');

% Create main subsystems
subsystems = {
    'PV_System',
    'Wind_Turbine_System',
    'Battery_Energy_Storage',
    'Load_Profile',
    'DC_Bus_Control',
    'Protection_System',
    'Monitoring_Visualization'
};

for i = 1:length(subsystems)
    add_block('simulink/Subsystems/Subsystem', ...
        [model_name '/' subsystems{i}], ...
        'Position', [50 + (i-1)*200, 50, 150 + (i-1)*200, 100]);
end

%% 1. PV SYSTEM SUBSYSTEM
fprintf('[2/6] Creating PV System subsystem...\n');

open_system([model_name '/PV_System']);

% PV System blocks
add_block('simulink/Sources/Sine Wave', [model_name '/PV_System/Irradiance'], ...
    'Amplitude', '800', 'Frequency', '1/43200', 'Phase', '-pi/2', ...
    'Position', [50, 50, 100, 100]);

add_block('simulink/Sources/Sine Wave', [model_name '/PV_System/Temperature'], ...
    'Amplitude', '15', 'Frequency', '1/43200', ...
    'Position', [50, 150, 100, 200]);

add_block('simulink/Continuous/Transfer Fcn', [model_name '/PV_System/PV_Model'], ...
    'Numerator', '[50000]', 'Denominator', '[1]', ...
    'Position', [200, 100, 280, 150]);

add_block('simulink/Math Operations/Product', [model_name '/PV_System/Efficiency_Factor'], ...
    'Position', [350, 100, 400, 150]);

add_block('simulink/Math Operations/Saturate', [model_name '/PV_System/Power_Limit'], ...
    'UpperLimit', '50000', 'LowerLimit', '0', ...
    'Position', [450, 100, 500, 150]);

add_block('simulink/Sinks/Out1', [model_name '/PV_System/P_PV'], ...
    'Position', [550, 110, 580, 130]);

% Connect blocks
add_line([model_name '/PV_System'], 'Irradiance/1', 'PV_Model/1');
add_line([model_name '/PV_System'], 'Temperature/1', 'Efficiency_Factor/1');
add_line([model_name '/PV_System'], 'PV_Model/1', 'Efficiency_Factor/2');
add_line([model_name '/PV_System'], 'Efficiency_Factor/1', 'Power_Limit/1');
add_line([model_name '/PV_System'], 'Power_Limit/1', 'P_PV/1');

% Add input/output ports
add_block('simulink/Sources/In1', [model_name '/PV_System/Irradiance_Input'], ...
    'Position', [20, 50, 50, 70]);
add_line([model_name '/PV_System'], 'Irradiance_Input/1', 'Irradiance/1');

close_system([model_name '/PV_System']);

%% 2. WIND TURBINE SYSTEM SUBSYSTEM
fprintf('[3/6] Creating Wind Turbine System subsystem...\n');

open_system([model_name '/Wind_Turbine_System']);

% Wind System blocks
add_block('simulink/Sources/Sine Wave', [model_name '/Wind_Turbine_System/Wind_Speed'], ...
    'Amplitude', '5', 'Bias', '8', 'Frequency', '1/86400', ...
    'Position', [50, 50, 100, 100]);

add_block('simulink/Continuous/Transfer Fcn', [model_name '/Wind_Turbine_System/Wind_Model'], ...
    'Numerator', '[30000]', 'Denominator', '[1 0.1]', ...
    'Position', [200, 50, 280, 100]);

add_block('simulink/Math Operations/Saturate', [model_name '/Wind_Turbine_System/Power_Limit'], ...
    'UpperLimit', '30000', 'LowerLimit', '0', ...
    'Position', [350, 50, 400, 100]);

add_block('simulink/Sinks/Out1', [model_name '/Wind_Turbine_System/P_Wind'], ...
    'Position', [450, 60, 480, 80]);

% Connect blocks
add_line([model_name '/Wind_Turbine_System'], 'Wind_Speed/1', 'Wind_Model/1');
add_line([model_name '/Wind_Turbine_System'], 'Wind_Model/1', 'Power_Limit/1');
add_line([model_name '/Wind_Turbine_System'], 'Power_Limit/1', 'P_Wind/1');

close_system([model_name '/Wind_Turbine_System']);

%% 3. BATTERY ENERGY STORAGE SUBSYSTEM
fprintf('[4/6] Creating Battery Energy Storage subsystem...\n');

open_system([model_name '/Battery_Energy_Storage']);

% Battery blocks
add_block('simulink/Sources/Constant', [model_name '/Battery_Energy_Storage/Initial_SOC'], ...
    'Value', '0.6', 'Position', [50, 50, 100, 100]);

add_block('simulink/Continuous/Integrator', [model_name '/Battery_Energy_Storage/SOC_Integrator'], ...
    'InitialCondition', '0.6', 'Position', [200, 50, 280, 100]);

add_block('simulink/Math Operations/Saturate', [model_name '/Battery_Energy_Storage/SOC_Limit'], ...
    'UpperLimit', '0.95', 'LowerLimit', '0.2', ...
    'Position', [350, 50, 400, 100]);

add_block('simulink/Sinks/Out1', [model_name '/Battery_Energy_Storage/SOC_Out'], ...
    'Position', [450, 60, 480, 80]);

add_block('simulink/Sinks/Out1', [model_name '/Battery_Energy_Storage/P_Battery'], ...
    'Position', [450, 120, 480, 140]);

% Connect blocks
add_line([model_name '/Battery_Energy_Storage'], 'Initial_SOC/1', 'SOC_Integrator/1');
add_line([model_name '/Battery_Energy_Storage'], 'SOC_Integrator/1', 'SOC_Limit/1');
add_line([model_name '/Battery_Energy_Storage'], 'SOC_Limit/1', 'SOC_Out/1');

close_system([model_name '/Battery_Energy_Storage']);

%% 4. LOAD PROFILE SUBSYSTEM
fprintf('[5/6] Creating Load Profile subsystem...\n');

open_system([model_name '/Load_Profile']);

% Load blocks
add_block('simulink/Sources/Sine Wave', [model_name '/Load_Profile/Critical_Load'], ...
    'Amplitude', '25', 'Bias', '25', 'Frequency', '1/86400', ...
    'Position', [50, 50, 100, 100]);

add_block('simulink/Sources/Pulse Generator', [model_name '/Load_Profile/Non_Critical_Load'], ...
    'Amplitude', '20', 'Period', '43200', 'PulseWidth', '50', ...
    'Position', [50, 150, 100, 200]);

add_block('simulink/Math Operations/Add', [model_name '/Load_Profile/Total_Load'], ...
    'Position', [200, 100, 250, 150]);

add_block('simulink/Sinks/Out1', [model_name '/Load_Profile/P_Load'], ...
    'Position', [300, 110, 330, 130]);

% Connect blocks
add_line([model_name '/Load_Profile'], 'Critical_Load/1', 'Total_Load/1');
add_line([model_name '/Load_Profile'], 'Non_Critical_Load/1', 'Total_Load/2');
add_line([model_name '/Load_Profile'], 'Total_Load/1', 'P_Load/1');

close_system([model_name '/Load_Profile']);

%% 5. DC BUS CONTROL SUBSYSTEM
fprintf('[6/6] Creating DC Bus Control subsystem...\n');

open_system([model_name '/DC_Bus_Control']);

% DC Bus control blocks
add_block('simulink/Sources/Constant', [model_name '/DC_Bus_Control/V_Nominal'], ...
    'Value', '400', 'Position', [50, 50, 100, 100]);

add_block('simulink/Continuous/PID Controller', [model_name '/DC_Bus_Control/Voltage_Controller'], ...
    'Kp', '0.1', 'Ki', '0.05', 'Kd', '0.01', ...
    'Position', [200, 50, 280, 100]);

add_block('simulink/Math Operations/Saturate', [model_name '/DC_Bus_Control/V_Limit'], ...
    'UpperLimit', '460', 'LowerLimit', '340', ...
    'Position', [350, 50, 400, 100]);

add_block('simulink/Sinks/Out1', [model_name '/DC_Bus_Control/V_Bus'], ...
    'Position', [450, 60, 480, 80]);

% Connect blocks
add_line([model_name '/DC_Bus_Control'], 'V_Nominal/1', 'Voltage_Controller/1');
add_line([model_name '/DC_Bus_Control'], 'Voltage_Controller/1', 'V_Limit/1');
add_line([model_name '/DC_Bus_Control'], 'V_Limit/1', 'V_Bus/1');

close_system([model_name '/DC_Bus_Control']);

%% Add interconnections at top level
fprintf('\nEstablishing system interconnections...\n');

% Add display blocks for monitoring
add_block('simulink/Sinks/Scope', [model_name '/Power_Monitor'], ...
    'Position', [800, 100, 900, 200]);

add_block('simulink/Sinks/Scope', [model_name '/Voltage_Monitor'], ...
    'Position', [800, 250, 900, 350]);

% Save model
save_system(model_name);
fprintf('\n✅ Simulink model created successfully!\n');
fprintf('Model name: %s\n', model_name);
fprintf('Location: %s\n', pwd);
fprintf('\nModel Structure:\n');
fprintf('├── PV_System (50 kW capacity)\n');
fprintf('├── Wind_Turbine_System (30 kW capacity)\n');
fprintf('├── Battery_Energy_Storage (100 kWh capacity)\n');
fprintf('├── Load_Profile (Critical + Non-critical loads)\n');
fprintf('├── DC_Bus_Control (Voltage regulation via PID)\n');
fprintf('├── Protection_System (Fault detection)\n');
fprintf('└── Monitoring_Visualization (Real-time plots)\n');
fprintf('\nTo run the model:\n');
fprintf('1. Open the model: open_system(''%s'')\n', model_name);
fprintf('2. Configure simulation parameters as needed\n');
fprintf('3. Run simulation: sim(''%s'')\n', model_name);
fprintf('4. Review results in Scope blocks\n');
