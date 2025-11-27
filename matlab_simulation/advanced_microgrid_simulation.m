%% Advanced DC Microgrid Simulation with AI Protection Systems
% Comprehensive MATLAB implementation with fault detection, cybersecurity,
% power quality analysis, and adaptive protection systems
% Author: Nivas D. Navghare
% Institution: COEP Technological University, Pune
% Date: November 2025

%% Initialize Environment
clear; clc; close all;
format compact;
warning('off', 'all');

% Create results directory if it doesn't exist
if ~exist('results', 'dir')
    mkdir('results');
end

fprintf('=========================================================\n');
fprintf('ADVANCED DC MICROGRID SIMULATION WITH AI PROTECTION\n');
fprintf('=========================================================\n\n');

%% System Configuration Parameters
fprintf('[1/12] Loading system configuration...\n');

% Time parameters
T_sim = 86400;          % 24 hours simulation (seconds)
dt = 1;                 % Time step (seconds)
t = 0:dt:T_sim-dt;      % Time vector
N = length(t);          % Number of samples
hour_of_day = mod(t/3600, 24);

% DC System Parameters (per FINAL_PROJECT_REPORT.md)
Vdc_nominal = 400;      % Nominal DC bus voltage (V) - as per documentation
Vdc_min = 340;          % Minimum voltage (85% of nominal)
Vdc_max = 460;          % Maximum voltage (115% of nominal)
f_switching = 10000;    % Switching frequency (Hz)

% PV System Parameters (per documentation)
PV_rated = 50;          % Total rated power (kW) - as per FINAL_PROJECT_REPORT.md
PV_efficiency = 0.20;   % Module efficiency
Panel_area = 278;       % Total panel area (m²) - calculated for 50kW
Temp_coeff = -0.004;    % Temperature coefficient (/°C) - as per documentation
MPPT_efficiency = 0.98; % MPPT efficiency

% Wind Turbine Parameters (per documentation)
Wind_rated = 30;        % Rated power (kW) - as per FINAL_PROJECT_REPORT.md
rotor_diameter = 8;     % Rotor diameter (m) - as per documentation
hub_height = 30;        % Hub height (m)
v_cutin = 3;            % Cut-in wind speed (m/s) - as per documentation
v_rated = 12;           % Rated wind speed (m/s) - as per documentation
v_cutout = 25;          % Cut-out wind speed (m/s) - as per documentation
Cp_max = 0.42;          % Maximum power coefficient (0.35-0.45 range)

% Battery Energy Storage System (per documentation)
Batt_capacity = 100;    % Total capacity (kWh) - as per FINAL_PROJECT_REPORT.md
Batt_modules = 27;      % Number of battery modules (for 100kWh)
Batt_voltage_nom = 400; % System voltage (V) - DC bus voltage
Batt_charge_max = 50;   % Max charge rate (kW) - 0.5C rate
Batt_discharge_max = 50;% Max discharge rate (kW) - 0.5C rate
SOC_init = 0.6;         % Initial SOC
SOC_min = 0.20;         % Minimum SOC - as per documentation
SOC_max = 0.95;         % Maximum SOC - as per documentation
Batt_efficiency = 0.90; % Round-trip efficiency - as per documentation
calendar_aging = 0.02;  % Annual capacity fade (%)

% Load Parameters (per documentation)
Load_peak = 70;         % Peak load (kW) - as per FINAL_PROJECT_REPORT.md
Load_base = 30;         % Base load (kW) - as per documentation
Load_critical = 50;     % Critical portion of peak load
Load_noncritical = 20;  % Non-critical portion
Load_industrial = 15;   % Industrial load portion (kW)
Load_residential = 10;  % Residential load portion (kW)

% Protection System Parameters
fault_detection_enabled = true;
cybersecurity_enabled = true;
adaptive_protection_enabled = true;

%% Environmental Data Generation
fprintf('[2/12] Generating realistic environmental data...\n');

% Solar irradiance with realistic daily and weather patterns
base_irradiance = 800 * max(0, sin(pi * (hour_of_day - 6) / 12));
weather_variation = 200 * sin(2*pi*t/7200) .* exp(-((hour_of_day-12).^2)/50);
cloud_effects = 150 * randn(size(t)) .* (base_irradiance > 100);
irradiance = base_irradiance + weather_variation + cloud_effects;
irradiance = max(0, min(1200, irradiance));

% Temperature with seasonal and diurnal variations
temp_seasonal = 25;     % Base temperature
temp_diurnal = 15 * sin(pi * (hour_of_day - 6) / 12);
temp_random = 3 * randn(size(t));
temperature = temp_seasonal + temp_diurnal + temp_random;

% Wind speed with realistic turbulence
wind_base = 7 + 5 * sin(pi * (hour_of_day - 6) / 12);
wind_turbulence = 2 * randn(size(t));
wind_gusts = 3 * sin(8*pi*t/3600);
wind_speed = max(0, wind_base + wind_turbulence + wind_gusts);

%% Renewable Energy Generation Models
fprintf('[3/12] Computing renewable energy generation...\n');

% Advanced PV Model with temperature compensation and shading effects
temp_factor = 1 + Temp_coeff * (temperature - 25);
shading_factor = 0.95 + 0.05 * sin(2*pi*t/1800); % Dynamic shading
P_pv = (irradiance / 1000) .* Panel_area * PV_efficiency .* temp_factor .* shading_factor * MPPT_efficiency;
P_pv = min(P_pv, PV_rated);

% Advanced Wind Model with realistic power curve
P_wind = zeros(size(wind_speed));
air_density = 1.225; % kg/m³
swept_area = pi * (rotor_diameter/2)^2;

for i = 1:length(wind_speed)
    v = wind_speed(i);
    if v < v_cutin || v > v_cutout
        P_wind(i) = 0;
    elseif v >= v_rated
        P_wind(i) = Wind_rated;
    else
        % Realistic power curve with Cp variation
        lambda = 5; % Tip speed ratio (simplified)
        Cp = Cp_max * (v/v_rated)^2 * (3 - 2*(v/v_rated));
        P_theoretical = 0.5 * air_density * swept_area * v^3 * Cp / 1000;
        P_wind(i) = min(P_theoretical, Wind_rated);
    end
end

%% Load Profile Generation
fprintf('[4/12] Generating realistic load profiles...\n');

% Critical load (hospitals, data centers) - relatively constant
P_load_critical = Load_critical * (0.95 + 0.1 * sin(2*pi*hour_of_day/24));

% Non-critical load (commercial) - business hours pattern
business_hours = (hour_of_day >= 8) & (hour_of_day <= 18);
P_load_noncritical = Load_noncritical * (0.3 + 0.7 * business_hours + 0.1 * randn(size(t)));

% Industrial load - shift patterns
shift_pattern = 0.8 + 0.4 * sin(pi*hour_of_day/12);
P_load_industrial = Load_industrial * shift_pattern;

% Residential load - typical daily pattern
residential_pattern = 0.4 + 0.3 * sin(pi*(hour_of_day-6)/12) + 0.3 * sin(2*pi*(hour_of_day-19)/24);
P_load_residential = Load_residential * residential_pattern;

% Total load
P_load_total = P_load_critical + P_load_noncritical + P_load_industrial + P_load_residential;
P_load_total = max(0, P_load_total + 5 * randn(size(t)));

%% Advanced Battery Management System
fprintf('[5/12] Simulating advanced battery management system...\n');

SOC = zeros(size(t));
P_battery = zeros(size(t));
V_battery = zeros(size(t));
T_battery = zeros(size(t));
battery_health = zeros(size(t));
SOC(1) = SOC_init;
battery_health(1) = 1.0; % Initial health factor

dt_hours = dt / 3600; % Convert seconds to hours

for i = 2:length(t)
    % Power balance calculation
    P_generation = P_pv(i) + P_wind(i);
    P_deficit = P_load_total(i) - P_generation;
    
    % Battery temperature model (simplified)
    T_ambient = temperature(i);
    T_battery(i) = T_ambient + 5 + abs(P_battery(max(1,i-1))) * 0.1;
    
    % Temperature-dependent efficiency
    temp_eff_factor = 1 - 0.005 * abs(T_battery(i) - 25);
    current_efficiency = Batt_efficiency * temp_eff_factor;
    
    % Battery aging model
    cycle_aging = 0.00001 * abs(P_battery(max(1,i-1)));
    battery_health(i) = battery_health(i-1) - cycle_aging - calendar_aging/365/24/3600;
    battery_health(i) = max(0.7, battery_health(i)); % Minimum 70% health
    
    % Effective capacity based on health
    effective_capacity = Batt_capacity * battery_health(i);
    
    if P_deficit > 0 % Discharge needed
        P_batt_req = min(P_deficit, Batt_discharge_max);
        
        % Check SOC constraints
        energy_available = (SOC(i-1) - SOC_min) * effective_capacity;
        max_discharge = energy_available * current_efficiency / dt_hours;
        
        P_battery(i) = -min(P_batt_req, max_discharge);
        energy_discharged = abs(P_battery(i)) * dt_hours / current_efficiency;
        SOC(i) = SOC(i-1) - energy_discharged / effective_capacity;
        
    elseif P_deficit < 0 % Charge available
        P_batt_req = min(-P_deficit, Batt_charge_max);
        
        % Check SOC constraints
        energy_capacity = (SOC_max - SOC(i-1)) * effective_capacity;
        max_charge = energy_capacity / (current_efficiency * dt_hours);
        
        P_battery(i) = min(P_batt_req, max_charge);
        energy_charged = P_battery(i) * dt_hours * current_efficiency;
        SOC(i) = SOC(i-1) + energy_charged / effective_capacity;
        
    else
        P_battery(i) = 0;
        SOC(i) = SOC(i-1);
    end
    
    % Battery voltage model
    V_cell_base = 3.2 + 0.8 * SOC(i);
    V_battery(i) = V_cell_base * (Batt_capacity / 3.7) * (1 + 0.001 * P_battery(i));
end

%% Power Quality and Harmonic Analysis
fprintf('[6/12] Analyzing power quality and harmonics...\n');

% DC bus voltage calculation with power flow effects
V_bus = zeros(size(t));
THD_voltage = zeros(size(t));
power_factor = zeros(size(t));

for i = 1:length(t)
    % Voltage drop due to current flow
    I_total = (P_pv(i) + P_wind(i) + P_battery(i)) / Vdc_nominal;
    R_line = 0.01; % Line resistance (Ohm)
    V_drop = I_total * R_line;
    
    % Voltage regulation
    V_bus(i) = Vdc_nominal - V_drop + 2*randn(); % Add noise
    V_bus(i) = max(Vdc_min, min(Vdc_max, V_bus(i)));
    
    % THD estimation based on switching activity
    switching_activity = abs(P_battery(i)) / Batt_discharge_max;
    THD_voltage(i) = 1.5 + 2 * switching_activity + 0.5 * randn();
    
    % Power factor (for future AC interface)
    power_factor(i) = 0.95 + 0.05 * sin(2*pi*t(i)/3600);
end

%% Fault Detection and Classification System
fprintf('[7/12] Implementing AI-based fault detection...\n');

% Initialize fault detection arrays
fault_status = zeros(size(t));
fault_type = cell(size(t));
fault_probability = zeros(7, length(t)); % 7 fault types

% Fault types: 1-Overvoltage, 2-Undervoltage, 3-Overcurrent, 
%             4-Ground fault, 5-Arc fault, 6-Insulation, 7-Thermal

for i = 1:length(t)
    % Feature extraction for fault detection
    features = [
        V_bus(i) / Vdc_nominal;
        abs(P_battery(i)) / Batt_discharge_max;
        T_battery(i);
        THD_voltage(i);
        std(V_bus(max(1,i-10):i));
        mean(P_load_total(max(1,i-5):i));
    ];
    
    % Simple rule-based fault detection (in practice, use trained ML model)
    fault_probability(1,i) = sigmoid((V_bus(i) - Vdc_max) / 10); % Overvoltage
    fault_probability(2,i) = sigmoid((Vdc_min - V_bus(i)) / 10); % Undervoltage
    fault_probability(3,i) = sigmoid((abs(P_battery(i)) - Batt_discharge_max*0.9) / 5); % Overcurrent
    fault_probability(4,i) = sigmoid((THD_voltage(i) - 8) / 2); % Ground fault
    fault_probability(5,i) = sigmoid((std(V_bus(max(1,i-10):i)) - 5) / 2); % Arc fault
    fault_probability(6,i) = sigmoid((T_battery(i) - 60) / 10); % Insulation
    fault_probability(7,i) = sigmoid((T_battery(i) - 70) / 5); % Thermal
    
    % Fault classification
    [max_prob, fault_idx] = max(fault_probability(:,i));
    if max_prob > 0.7
        fault_status(i) = fault_idx;
        fault_type{i} = getFaultName(fault_idx);
    else
        fault_status(i) = 0;
        fault_type{i} = 'Normal';
    end
end

%% Cybersecurity Monitoring System
fprintf('[8/12] Implementing cybersecurity monitoring...\n');

% Simulate network traffic and anomaly detection
network_traffic = 100 + 20 * sin(2*pi*t/3600) + 10 * randn(size(t));
cyber_threat_level = zeros(size(t));
security_events = zeros(size(t));

for i = 1:length(t)
    % Anomaly detection using statistical methods
    if i > 100
        traffic_mean = mean(network_traffic(i-100:i-1));
        traffic_std = std(network_traffic(i-100:i-1));
        z_score = abs(network_traffic(i) - traffic_mean) / traffic_std;
        
        if z_score > 3
            cyber_threat_level(i) = min(1, z_score / 5);
            security_events(i) = 1;
        end
    end
end

%% Adaptive Protection System
fprintf('[9/12] Configuring adaptive protection system...\n');

% Protection settings that adapt based on operating conditions
protection_settings = struct();
protection_settings.voltage_trip_time = zeros(size(t));
protection_settings.current_trip_level = zeros(size(t));
protection_settings.frequency_tolerance = zeros(size(t));

for i = 1:length(t)
    % Adapt protection based on system state
    generation_level = (P_pv(i) + P_wind(i)) / (PV_rated + Wind_rated);
    load_level = P_load_total(i) / max(P_load_total);
    
    % Dynamic voltage protection
    protection_settings.voltage_trip_time(i) = 0.1 + 0.4 * generation_level;
    
    % Dynamic current protection
    protection_settings.current_trip_level(i) = 1.2 + 0.3 * load_level;
    
    % Frequency tolerance (for future AC coupling)
    protection_settings.frequency_tolerance(i) = 0.5 + 0.5 * (1 - generation_level);
end

%% Performance Metrics and Analysis
fprintf('[10/12] Computing comprehensive performance metrics...\n');

% Energy calculations (kWh)
E_pv_total = sum(P_pv) * dt_hours;
E_wind_total = sum(P_wind) * dt_hours;
E_renewable_total = E_pv_total + E_wind_total;
E_load_total = sum(P_load_total) * dt_hours;
E_battery_charged = sum(P_battery(P_battery > 0)) * dt_hours;
E_battery_discharged = sum(abs(P_battery(P_battery < 0))) * dt_hours;

% Efficiency metrics
system_efficiency = E_load_total / E_renewable_total * 100;
battery_roundtrip_eff = E_battery_discharged / E_battery_charged * 100;
renewable_utilization = E_renewable_total / (E_renewable_total + E_battery_discharged) * 100;

% Reliability metrics
voltage_violations = sum((V_bus < Vdc_min) | (V_bus > Vdc_max)) / length(t) * 100;
fault_incidents = sum(fault_status > 0);
security_incidents = sum(security_events);
uptime_percentage = (1 - voltage_violations/100) * 100;

% Economic metrics (simplified)
cost_per_kWh = 0.12; % $/kWh
revenue_renewable = E_renewable_total * cost_per_kWh;
cost_battery_degradation = (1 - min(battery_health)) * Batt_capacity * 500; % $500/kWh replacement cost

%% Advanced Visualization
fprintf('[11/12] Generating comprehensive visualizations...\n');

% Create figure with multiple subplots
fig1 = figure('Name', 'Comprehensive System Analysis', 'Position', [50 50 1400 1000]);

% Power Balance Analysis
subplot(3,3,1);
plot(t/3600, P_pv, 'Color', [1 0.8 0], 'LineWidth', 1.5); hold on;
plot(t/3600, P_wind, 'Color', [0 0.7 1], 'LineWidth', 1.5);
plot(t/3600, P_load_total, 'k--', 'LineWidth', 1.5);
plot(t/3600, P_battery, 'Color', [0 0.6 0], 'LineWidth', 1.5);
xlabel('Time (hours)'); ylabel('Power (kW)');
title('Power Balance Analysis');
legend('PV', 'Wind', 'Load', 'Battery', 'Location', 'best');
grid on;

% Battery Operation
subplot(3,3,2);
yyaxis left;
plot(t/3600, SOC*100, 'Color', [0.8 0 0.8], 'LineWidth', 2);
ylabel('SOC (%)');
yyaxis right;
plot(t/3600, battery_health*100, 'Color', [1 0.5 0], 'LineWidth', 1.5);
ylabel('Health (%)');
xlabel('Time (hours)');
title('Battery Management System');
grid on;

% Voltage Quality
subplot(3,3,3);
plot(t/3600, V_bus, 'b-', 'LineWidth', 1.2); hold on;
yline(Vdc_nominal, 'g--', 'Nominal', 'LineWidth', 1.5);
yline(Vdc_min, 'r--', 'Min', 'LineWidth', 1);
yline(Vdc_max, 'r--', 'Max', 'LineWidth', 1);
xlabel('Time (hours)'); ylabel('Voltage (V)');
title('DC Bus Voltage Profile');
grid on;

% Environmental Conditions
subplot(3,3,4);
yyaxis left;
plot(t/3600, irradiance, 'Color', [1 0.7 0], 'LineWidth', 1);
ylabel('Irradiance (W/m²)');
yyaxis right;
plot(t/3600, wind_speed, 'Color', [0 0.8 1], 'LineWidth', 1);
ylabel('Wind Speed (m/s)');
xlabel('Time (hours)');
title('Environmental Conditions');
grid on;

% Fault Detection Heatmap
subplot(3,3,5);
imagesc(t(1:100:end)/3600, 1:7, fault_probability(:,1:100:end));
colorbar;
set(gca, 'YTick', 1:7, 'YTickLabel', {'Overvolt', 'Undervolt', 'Overcurr', 'Ground', 'Arc', 'Insulation', 'Thermal'});
xlabel('Time (hours)'); ylabel('Fault Type');
title('Fault Probability Matrix');

% Power Quality Metrics
subplot(3,3,6);
plot(t/3600, THD_voltage, 'r-', 'LineWidth', 1.2); hold on;
yline(5, 'k--', 'IEEE Limit', 'LineWidth', 1.5);
xlabel('Time (hours)'); ylabel('THD (%)');
title('Total Harmonic Distortion');
grid on;

% Energy Distribution
subplot(3,3,7);
energy_data = [E_pv_total, E_wind_total, E_battery_discharged];
energy_labels = {'PV Energy', 'Wind Energy', 'Battery Energy'};
pie(energy_data, energy_labels);
title('Energy Source Distribution');

% Cybersecurity Monitoring
subplot(3,3,8);
plot(t/3600, network_traffic, 'b-', 'LineWidth', 1); hold on;
plot(t/3600, cyber_threat_level*100, 'r-', 'LineWidth', 1.5);
xlabel('Time (hours)'); ylabel('Level');
title('Cybersecurity Monitoring');
legend('Network Traffic', 'Threat Level (%)', 'Location', 'best');
grid on;

% System Efficiency
subplot(3,3,9);
efficiency_data = [system_efficiency, battery_roundtrip_eff, renewable_utilization];
efficiency_labels = {'System', 'Battery', 'Renewable Util.'};
bar(efficiency_data);
set(gca, 'XTickLabel', efficiency_labels);
ylabel('Efficiency (%)');
title('System Efficiency Metrics');
grid on;

sgtitle('Advanced DC Microgrid Analysis Dashboard', 'FontSize', 16, 'FontWeight', 'bold');

% Save the comprehensive figure
saveas(fig1, 'results/advanced_microgrid_analysis.png');

%% Performance Report Generation
fprintf('[12/12] Generating performance report...\n');

% Display comprehensive results
fprintf('\n=========================================================\n');
fprintf('                  SIMULATION RESULTS\n');
fprintf('=========================================================\n\n');

fprintf('ENERGY ANALYSIS:\n');
fprintf('  PV Generation:           %.2f kWh (%.1f%%)\n', E_pv_total, E_pv_total/E_renewable_total*100);
fprintf('  Wind Generation:         %.2f kWh (%.1f%%)\n', E_wind_total, E_wind_total/E_renewable_total*100);
fprintf('  Total Renewable:         %.2f kWh\n', E_renewable_total);
fprintf('  Total Load Consumption:  %.2f kWh\n', E_load_total);
fprintf('  Battery Charged:         %.2f kWh\n', E_battery_charged);
fprintf('  Battery Discharged:      %.2f kWh\n', E_battery_discharged);
fprintf('\n');

fprintf('EFFICIENCY METRICS:\n');
fprintf('  Overall System:          %.2f%%\n', system_efficiency);
fprintf('  Battery Round-trip:      %.2f%%\n', battery_roundtrip_eff);
fprintf('  Renewable Utilization:   %.2f%%\n', renewable_utilization);
fprintf('  Average Battery SOC:     %.1f%%\n', mean(SOC)*100);
fprintf('  Final Battery Health:    %.1f%%\n', battery_health(end)*100);
fprintf('\n');

fprintf('POWER QUALITY:\n');
fprintf('  Voltage Violations:      %.2f%% of time\n', voltage_violations);
fprintf('  Average THD:             %.2f%%\n', mean(THD_voltage));
fprintf('  System Uptime:           %.2f%%\n', uptime_percentage);
fprintf('\n');

fprintf('RELIABILITY & SECURITY:\n');
fprintf('  Fault Incidents:         %d\n', fault_incidents);
fprintf('  Security Events:         %d\n', security_incidents);
fprintf('  Most Critical Fault:     %s\n', getFaultName(mode(fault_status(fault_status>0))));
fprintf('\n');

fprintf('ECONOMIC ANALYSIS:\n');
fprintf('  Renewable Revenue:       $%.2f\n', revenue_renewable);
fprintf('  Battery Degradation Cost: $%.2f\n', cost_battery_degradation);
fprintf('  Net Economic Benefit:    $%.2f\n', revenue_renewable - cost_battery_degradation);
fprintf('\n');

fprintf('=========================================================\n');
fprintf('Simulation completed successfully!\n');
fprintf('Results and plots saved to results/ directory\n');
fprintf('=========================================================\n');

%% Helper Functions
function y = sigmoid(x)
    y = 1 ./ (1 + exp(-x));
end

function name = getFaultName(idx)
    fault_names = {'Overvoltage', 'Undervoltage', 'Overcurrent', 'Ground Fault', 'Arc Fault', 'Insulation Failure', 'Thermal Fault'};
    if idx >= 1 && idx <= length(fault_names)
        name = fault_names{idx};
    else
        name = 'Unknown';
    end
end