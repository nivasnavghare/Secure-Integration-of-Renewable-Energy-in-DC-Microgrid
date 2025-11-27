%% System Parameters for DC Microgrid Simulink Models
% Contains all configurable parameters for the Simulink models
% Can be loaded before running simulations to override defaults
% Author: Nivas D. Navghare
% Institution: COEP Technological University, Pune
% Date: November 2025

%% System-wide Parameters
fprintf('Loading DC Microgrid System Parameters...\n\n');

%% 1. DC SYSTEM PARAMETERS
fprintf('Loading DC System Parameters...\n');

% DC Bus voltage
sys.Vdc_nominal = 400;      % Nominal voltage (V)
sys.Vdc_min = 340;          % Minimum voltage (85% of nominal)
sys.Vdc_max = 460;          % Maximum voltage (115% of nominal)
sys.f_switching = 10000;    % Switching frequency (Hz)

%% 2. PHOTOVOLTAIC SYSTEM PARAMETERS
fprintf('Loading PV System Parameters...\n');

pv.rated_power = 50;        % Rated power (kW)
pv.efficiency = 0.20;       % Module efficiency
pv.panel_area = 278;        % Total panel area (m²)
pv.temp_coeff = -0.004;     % Temperature coefficient (/°C)
pv.mppt_efficiency = 0.98;  % MPPT efficiency (P&O algorithm)
pv.mppt_scan_rate = 0.1;    % Scan rate (seconds)
pv.irradiance_min = 50;     % Minimum irradiance for operation (W/m²)

% PV Array configuration
pv.modules_series = 10;     % Number of modules in series
pv.modules_parallel = 5;    % Number of parallel strings
pv.v_module = 40;           % Module voltage (V)
pv.i_module = 5;            % Module current (A)

%% 3. WIND TURBINE PARAMETERS
fprintf('Loading Wind Turbine Parameters...\n');

wind.rated_power = 30;      % Rated power (kW)
wind.rotor_diameter = 8;    % Rotor diameter (m)
wind.hub_height = 30;       % Hub height (m)
wind.v_cutin = 3;           % Cut-in wind speed (m/s)
wind.v_rated = 12;          % Rated wind speed (m/s)
wind.v_cutout = 25;         % Cut-out wind speed (m/s)
wind.cp_max = 0.42;         % Maximum power coefficient
wind.gearbox_ratio = 50;    % Gearbox ratio
wind.generator_eff = 0.92;  % Generator efficiency

% Wind turbine control
wind.pitch_min = 0;         % Minimum pitch angle (degrees)
wind.pitch_max = 45;        % Maximum pitch angle (degrees)
wind.rotor_speed_min = 10;  % Minimum rotor speed (rpm)
wind.rotor_speed_max = 20;  % Maximum rotor speed (rpm)

%% 4. BATTERY ENERGY STORAGE PARAMETERS
fprintf('Loading Battery Storage Parameters...\n');

bess.capacity = 100;        % Total capacity (kWh)
bess.voltage_nom = 400;     % Nominal voltage (V)
bess.modules = 27;          % Number of modules
bess.charge_max = 50;       % Maximum charge rate (kW)
bess.discharge_max = 50;    % Maximum discharge rate (kW)
bess.soc_init = 0.6;        % Initial SOC
bess.soc_min = 0.2;         % Minimum SOC (20%)
bess.soc_max = 0.95;        % Maximum SOC (95%)
bess.efficiency = 0.90;     % Round-trip efficiency

% Battery chemistry (Lithium-ion)
bess.chemistry = 'Li-ion';
bess.cell_voltage = 3.7;    % Single cell voltage (V)
bess.energy_density = 250;  % Wh/kg
bess.cycle_life = 5000;     % Number of full cycles
bess.calendar_life = 10;    % Calendar life (years)
bess.calendar_aging = 0.02; % Annual capacity fade (%)

% Thermal model
bess.temp_opt = 25;         % Optimal temperature (°C)
bess.temp_max = 50;         % Maximum temperature (°C)
bess.temp_coeff = -0.01;    % Temperature coefficient (/°C)

%% 5. LOAD PARAMETERS
fprintf('Loading Load Parameters...\n');

load.peak_total = 70;       % Peak total load (kW)
load.base_total = 30;       % Base load (kW)

% Load categories
load.critical = 50;         % Critical load (hospitals, data centers) (kW)
load.noncritical = 20;      % Non-critical load (offices, shops) (kW)
load.industrial = 15;       % Industrial load (factories) (kW)
load.residential = 10;      % Residential load (homes) (kW)

% Load characteristics
load.critical_variability = 0.1;    % ±10% variation
load.noncrit_variability = 0.3;     % ±30% variation
load.industrial_shift_pattern = 'three_shift'; % three_shift, two_shift, continuous
load.residential_pattern = 'diurnal'; % diurnal, bimodal

%% 6. POWER CONVERSION EQUIPMENT
fprintf('Loading Power Converter Parameters...\n');

conv.dc_dc_efficiency = 0.96;   % DC/DC converter efficiency
conv.ac_dc_efficiency = 0.94;   % AC/DC converter (if needed)
conv.dc_bus_resistance = 0.01;  % Bus resistance (Ohm)
conv.cable_loss_percent = 2;    % Cable losses (%)

% Converter ratings
conv.pv_converter_rating = 60;  % kW (>PV rated)
conv.wind_converter_rating = 40; % kW (>Wind rated)
conv.batt_converter_rating = 50; % kW (DC/DC for battery)

%% 7. PROTECTION SYSTEM PARAMETERS
fprintf('Loading Protection Parameters...\n');

prot.voltage_trip_max = 460;       % Overvoltage trip (V)
prot.voltage_trip_min = 340;       % Undervoltage trip (V)
prot.current_trip_max = 250;       % Overcurrent trip (A)

% Protection thresholds
prot.voltage_warn_max = 440;       % Warning level high (V)
prot.voltage_warn_min = 360;       % Warning level low (V)
prot.current_warn_max = 200;       % Warning level (A)

% Time delays
prot.relay_delay_primary = 0.1;    % Primary relay delay (seconds)
prot.relay_delay_backup = 0.2;     % Backup relay delay (seconds)
prot.rms_window = 1;               % RMS calculation window (seconds)
prot.fault_detection_delay = 0.05; % Fault detection delay (seconds)

% Protection settings (adaptive)
prot.adaptive_enabled = true;
prot.voltage_trip_time_min = 0.1;  % Minimum trip time (seconds)
prot.voltage_trip_time_max = 0.5;  % Maximum trip time (seconds)

%% 8. CONTROL SYSTEM PARAMETERS
fprintf('Loading Control System Parameters...\n');

ctrl.voltage_loop_kp = 0.1;     % Proportional gain
ctrl.voltage_loop_ki = 0.05;    % Integral gain
ctrl.voltage_loop_kd = 0.01;    % Derivative gain
ctrl.voltage_loop_ts = 1;       % Sampling time (seconds)
ctrl.voltage_control_max = 100; % Max control signal

% Current control
ctrl.current_loop_kp = 0.2;
ctrl.current_loop_ki = 0.1;
ctrl.current_loop_ts = 0.1;

% Power flow control
ctrl.power_flow_strategy = 'renewable_first'; % renewable_first, load_first, balanced
ctrl.battery_power_ref = 0;     % Battery power reference (kW)
ctrl.renewable_priority = 0.9;  % Renewable priority factor

%% 9. MPPT CONTROLLER PARAMETERS
fprintf('Loading MPPT Parameters...\n');

mppt.algorithm = 'perturb_observe'; % P&O algorithm
mppt.perturbation_step = 1;     % Perturbation step (V)
mppt.perturbation_period = 0.1; % Period (seconds)
mppt.tracking_efficiency = 0.98; % Tracking efficiency
mppt.convergence_time = 10;     % Convergence time (seconds)

%% 10. WIND GOVERNOR PARAMETERS
fprintf('Loading Wind Governor Parameters...\n');

gov.control_type = 'pitch_control'; % pitch_control, stall, active_stall
gov.pitch_rate = 10;            % Pitch rate (degrees/second)
gov.pitch_kp = 0.5;             % Pitch controller Kp
gov.pitch_ki = 0.2;             % Pitch controller Ki
gov.power_ref_margin = 0.95;    % Power reference as % of rated

%% 11. SIMULATION PARAMETERS
fprintf('Loading Simulation Parameters...\n');

sim.complete_system_duration = 86400;   % 24 hours (seconds)
sim.complete_system_step = 1;           % 1 second time step
sim.complete_system_solver = 'ode4';    % Fixed-step solver

sim.protection_duration = 10;           % 10 seconds
sim.protection_step = 0.01;             % 10 ms time step

sim.control_duration = 3600;            % 1 hour
sim.control_step = 0.1;                 % 100 ms time step

%% 12. POWER QUALITY PARAMETERS
fprintf('Loading Power Quality Parameters...\n');

pq.voltage_regulation = 0.032;  % ±3.2%
pq.thd_voltage_max = 0.05;      % 5% THD
pq.thd_current_max = 0.08;      % 8% THD
pq.power_factor_target = 0.97;  % Target power factor
pq.frequency_nominal = 50;      % 50 Hz (for future AC coupling)
pq.frequency_deviation = 0.2;   % ±0.2 Hz

%% 13. ECONOMIC PARAMETERS
fprintf('Loading Economic Parameters...\n');

econ.cost_per_kwh = 0.12;       % Electricity cost ($/kWh)
econ.batt_replacement_cost = 500; % $/kWh
econ.operation_maintenance = 0.02; % % of capex per year
econ.project_life = 20;         % Years

%% 14. ENVIRONMENTAL CONDITIONS
fprintf('Loading Environmental Parameters...\n');

env.temp_ambient_base = 25;     % Base ambient temperature (°C)
env.temp_amplitude = 15;        % Daily temperature variation (°C)
env.irradiance_peak = 1000;     % Peak irradiance (W/m²)
env.wind_speed_average = 8;     % Average wind speed (m/s)
env.wind_speed_variation = 5;   % Wind speed variation (m/s)

%% 15. DATA LOGGING PARAMETERS
fprintf('Loading Data Logging Parameters...\n');

log.save_results = true;
log.save_to_workspace = true;
log.save_to_file = true;
log.output_format = 'mat';      % mat, csv, hdf5
log.log_frequency = 1;          % Log every N seconds
log.compress_data = true;

%% Display Summary
fprintf('\n');
fprintf('╔════════════════════════════════════════════════════════════╗\n');
fprintf('║          SYSTEM PARAMETERS LOADED SUCCESSFULLY            ║\n');
fprintf('╚════════════════════════════════════════════════════════════╝\n\n');

fprintf('System Configuration Summary:\n');
fprintf('─────────────────────────────\n\n');

fprintf('PV System:        %d kW rated capacity\n', pv.rated_power);
fprintf('Wind Turbine:     %d kW rated capacity\n', wind.rated_power);
fprintf('Battery Storage:  %d kWh capacity (%.1f-%d%% SOC limits)\n', ...
    bess.capacity, bess.soc_min*100, ceil(bess.soc_max*100));
fprintf('Peak Load:        %d kW total load\n', load.peak_total);
fprintf('DC Bus Voltage:   %d V nominal (%.0f%% range)\n', ...
    sys.Vdc_nominal, (sys.Vdc_max-sys.Vdc_min)/sys.Vdc_nominal*100);

fprintf('\nControl Parameters:\n');
fprintf('─────────────────────────────\n');
fprintf('Voltage Control:  Kp=%.2f, Ki=%.2f, Kd=%.2f\n', ...
    ctrl.voltage_loop_kp, ctrl.voltage_loop_ki, ctrl.voltage_loop_kd);
fprintf('MPPT Efficiency:  %.0f%%\n', pv.mppt_efficiency*100);
fprintf('Battery Eff:      %.0f%% round-trip\n', bess.efficiency*100);

fprintf('\nSimulation Setup:\n');
fprintf('─────────────────────────────\n');
fprintf('Complete System:  %.0f hours @ %d second steps\n', ...
    sim.complete_system_duration/3600, sim.complete_system_step);
fprintf('Protection Test:  %.1f seconds @ %d ms steps\n', ...
    sim.protection_duration, sim.protection_step*1000);
fprintf('Control Test:     %.1f hours @ %.0f ms steps\n', ...
    sim.control_duration/3600, sim.control_step*1000);

fprintf('\n✅ Parameters ready for simulation\n\n');

%% Save parameters structure
% Uncomment to save parameters
% save('dc_microgrid_parameters.mat', 'sys', 'pv', 'wind', 'bess', 'load', ...
%     'conv', 'prot', 'ctrl', 'mppt', 'gov', 'sim', 'pq', 'econ', 'env', 'log');
