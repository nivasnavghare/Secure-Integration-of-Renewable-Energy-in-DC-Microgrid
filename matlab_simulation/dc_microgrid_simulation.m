%% DC Microgrid Simulation - MATLAB/Simulink
% Main simulation script for DC microgrid modeling
% Author: Nivas D. Navghare
% Institution: COEP Technological University, Pune

%% Clear workspace
clear; clc; close all;

%% Configuration Parameters
fprintf('Initializing DC Microgrid Simulation...\n');

% System Parameters
Vdc = 380;              % DC bus voltage (V)
f_nominal = 50;         % Nominal frequency (Hz)
T_sim = 3600;           % Simulation time (seconds)

% PV System Parameters
PV_rated = 100;         % Rated power (kW)
PV_efficiency = 0.18;   % Panel efficiency
Panel_area = 600;       % Panel area (m²)
Temp_coeff = -0.004;    % Temperature coefficient (per °C)

% Wind Turbine Parameters
Wind_rated = 50;        % Rated power (kW)
v_cutin = 3;            % Cut-in wind speed (m/s)
v_rated = 12;           % Rated wind speed (m/s)
v_cutout = 25;          % Cut-out wind speed (m/s)

% Battery Parameters
Batt_capacity = 200;    % Capacity (kWh)
Batt_charge_max = 50;   % Max charge rate (kW)
Batt_discharge_max = 50;% Max discharge rate (kW)
SOC_init = 0.5;         % Initial SOC
SOC_min = 0.2;          % Minimum SOC
SOC_max = 0.9;          % Maximum SOC
Batt_efficiency = 0.95; % Battery efficiency

% Load Parameters
Load_critical = 80;     % Critical load (kW)
Load_noncritical = 40;  % Non-critical load (kW)

%% Generate Input Data
fprintf('Generating environmental data...\n');

% Time vector
t = 0:1:T_sim;
hour_of_day = mod(t/3600, 24);

% Solar irradiance (W/m²)
irradiance = 1000 * max(0, sin(pi * (hour_of_day - 6) / 12));
irradiance = irradiance + 50 * randn(size(irradiance));
irradiance(irradiance < 0) = 0;

% Temperature (°C)
temperature = 25 + 10 * sin(pi * (hour_of_day - 6) / 12);
temperature = temperature + 2 * randn(size(temperature));

% Wind speed (m/s)
wind_speed = 8 + 4 * sin(2 * pi * hour_of_day / 24);
wind_speed = wind_speed + 1 * randn(size(wind_speed));
wind_speed(wind_speed < 0) = 0;

%% PV Power Calculation
fprintf('Calculating PV power output...\n');

% Temperature effect
temp_factor = 1 + Temp_coeff * (temperature - 25);

% PV power
P_pv = (irradiance / 1000) .* Panel_area * PV_efficiency .* temp_factor;
P_pv = min(P_pv, PV_rated);  % Limit to rated power

%% Wind Power Calculation
fprintf('Calculating wind power output...\n');

P_wind = zeros(size(wind_speed));
for i = 1:length(wind_speed)
    v = wind_speed(i);
    if v < v_cutin || v > v_cutout
        P_wind(i) = 0;
    elseif v >= v_rated
        P_wind(i) = Wind_rated;
    else
        % Simplified power curve
        P_wind(i) = Wind_rated * ((v - v_cutin) / (v_rated - v_cutin))^3;
    end
end

%% Load Profile
fprintf('Generating load profile...\n');

% Variable load based on time of day
load_factor = 0.7 + 0.3 * sin(pi * (hour_of_day - 6) / 12);
P_load = (Load_critical + Load_noncritical) * load_factor;
P_load = P_load + 5 * randn(size(P_load));  % Add variability

%% Battery Operation
fprintf('Simulating battery operation...\n');

SOC = zeros(size(t));
P_battery = zeros(size(t));
SOC(1) = SOC_init;

dt = 1/3600;  % Time step in hours

for i = 2:length(t)
    % Power balance
    P_gen = P_pv(i) + P_wind(i);
    P_deficit = P_load(i) - P_gen;
    
    if P_deficit > 0  % Need to discharge
        P_batt = min(P_deficit, Batt_discharge_max);
        % Check SOC limit
        energy = P_batt * dt / Batt_efficiency;
        new_SOC = SOC(i-1) - energy / Batt_capacity;
        
        if new_SOC < SOC_min
            P_batt = (SOC(i-1) - SOC_min) * Batt_capacity * Batt_efficiency / dt;
            new_SOC = SOC_min;
        end
        
        P_battery(i) = -P_batt;  % Negative for discharge
        SOC(i) = new_SOC;
        
    elseif P_deficit < 0  % Can charge
        P_batt = min(-P_deficit, Batt_charge_max);
        % Check SOC limit
        energy = P_batt * dt * Batt_efficiency;
        new_SOC = SOC(i-1) + energy / Batt_capacity;
        
        if new_SOC > SOC_max
            P_batt = (SOC_max - SOC(i-1)) * Batt_capacity / (dt * Batt_efficiency);
            new_SOC = SOC_max;
        end
        
        P_battery(i) = P_batt;  % Positive for charge
        SOC(i) = new_SOC;
        
    else
        SOC(i) = SOC(i-1);
        P_battery(i) = 0;
    end
end

%% Power Quality Analysis
fprintf('Analyzing power quality...\n');

% Voltage calculation (simplified)
V_bus = Vdc + 5 * randn(size(t));  % Add voltage variations

% Total Harmonic Distortion estimation
THD = 2 + 1 * rand();  % Simplified THD (%)

%% Performance Metrics
fprintf('Calculating performance metrics...\n');

% Energy calculations
E_pv_total = sum(P_pv) * dt;
E_wind_total = sum(P_wind) * dt;
E_gen_total = E_pv_total + E_wind_total;
E_load_total = sum(P_load) * dt;

% Efficiency
system_efficiency = E_load_total / E_gen_total * 100;

% Renewable penetration
renewable_penetration = E_gen_total / E_load_total * 100;

% Average SOC
avg_SOC = mean(SOC);

%% Display Results
fprintf('\n========== SIMULATION RESULTS ==========\n');
fprintf('Total PV Energy: %.2f kWh\n', E_pv_total);
fprintf('Total Wind Energy: %.2f kWh\n', E_wind_total);
fprintf('Total Generation: %.2f kWh\n', E_gen_total);
fprintf('Total Load: %.2f kWh\n', E_load_total);
fprintf('System Efficiency: %.2f%%\n', system_efficiency);
fprintf('Renewable Penetration: %.2f%%\n', renewable_penetration);
fprintf('Average Battery SOC: %.2f%%\n', avg_SOC * 100);
fprintf('Estimated THD: %.2f%%\n', THD);
fprintf('========================================\n\n');

%% Visualization
fprintf('Generating plots...\n');

% Power Balance Plot
figure('Name', 'Power Balance', 'Position', [100 100 1200 600]);
plot(t/3600, P_pv, 'LineWidth', 2, 'DisplayName', 'PV Power');
hold on;
plot(t/3600, P_wind, 'LineWidth', 2, 'DisplayName', 'Wind Power');
plot(t/3600, P_load, '--', 'LineWidth', 2, 'DisplayName', 'Load');
plot(t/3600, P_battery, 'LineWidth', 2, 'DisplayName', 'Battery Power');
hold off;
xlabel('Time (hours)', 'FontSize', 12);
ylabel('Power (kW)', 'FontSize', 12);
title('DC Microgrid Power Balance', 'FontSize', 14, 'FontWeight', 'bold');
legend('Location', 'best');
grid on;
saveas(gcf, 'results/matlab_power_balance.png');

% Battery Operation Plot
figure('Name', 'Battery Operation', 'Position', [100 100 1200 800]);

subplot(2,1,1);
plot(t/3600, SOC * 100, 'LineWidth', 2);
hold on;
yline(SOC_min * 100, 'r--', 'Min SOC', 'LineWidth', 1.5);
yline(SOC_max * 100, 'r--', 'Max SOC', 'LineWidth', 1.5);
hold off;
ylabel('State of Charge (%)', 'FontSize', 12);
title('Battery Energy Storage System', 'FontSize', 14, 'FontWeight', 'bold');
grid on;

subplot(2,1,2);
plot(t/3600, P_battery, 'LineWidth', 2, 'Color', [0 0.5 0]);
yline(0, 'k-', 'LineWidth', 0.5);
xlabel('Time (hours)', 'FontSize', 12);
ylabel('Battery Power (kW)', 'FontSize', 12);
title('Positive: Charging, Negative: Discharging', 'FontSize', 10, 'FontStyle', 'italic');
grid on;
saveas(gcf, 'results/matlab_battery_operation.png');

% Voltage Profile Plot
figure('Name', 'Voltage Profile', 'Position', [100 100 1200 600]);
plot(t/3600, V_bus, 'LineWidth', 2, 'Color', [0.5 0 0.5]);
hold on;
yline(Vdc, 'g--', 'Nominal', 'LineWidth', 1.5);
yline(Vdc * 0.85, 'r--', 'Min Threshold', 'LineWidth', 1.5);
yline(Vdc * 1.15, 'r--', 'Max Threshold', 'LineWidth', 1.5);
hold off;
xlabel('Time (hours)', 'FontSize', 12);
ylabel('DC Bus Voltage (V)', 'FontSize', 12);
title('DC Bus Voltage Profile', 'FontSize', 14, 'FontWeight', 'bold');
legend('Voltage', 'Nominal', 'Min', 'Max', 'Location', 'best');
grid on;
saveas(gcf, 'results/matlab_voltage_profile.png');

fprintf('Simulation completed successfully!\n');
fprintf('Results saved to results/ directory\n');
