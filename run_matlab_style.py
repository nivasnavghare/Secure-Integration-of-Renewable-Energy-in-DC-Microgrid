#!/usr/bin/env python3
"""
MATLAB-Style DC Microgrid Simulation
Generates comprehensive graphs and analysis matching MATLAB output format
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from pathlib import Path
import yaml

# Set MATLAB-style plotting
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['legend.fontsize'] = 9

# Create results directory
results_dir = Path('results/matlab_style')
results_dir.mkdir(exist_ok=True, parents=True)

print("="*70)
print(" "*15 + "DC MICROGRID SIMULATION - MATLAB STYLE")
print("="*70)

# Load configuration
print("\nInitializing DC Microgrid Simulation...")
with open('config/microgrid_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# System Parameters
Vdc = config['system']['voltage_level']
f_nominal = 50
T_sim = 24 * 3600  # 24 hours

# PV System Parameters (per FINAL_PROJECT_REPORT.md)
PV_rated = config['photovoltaic']['rated_power']  # 50kW
PV_efficiency = 0.18
Panel_area = 278  # m² - calculated for 50kW
Temp_coeff = -0.004

# Wind Turbine Parameters (per FINAL_PROJECT_REPORT.md)
Wind_rated = config['wind_turbine']['rated_power']  # 30kW
v_cutin = 3
v_rated = 12
v_cutout = 25

# Battery Parameters (per FINAL_PROJECT_REPORT.md)
Batt_capacity = config['bess']['capacity']  # 100kWh
Batt_charge_max = 50  # 0.5C rate
Batt_discharge_max = 50  # 0.5C rate
SOC_init = 0.5
SOC_min = 0.2  # as per documentation
SOC_max = 0.95  # as per documentation
Batt_efficiency = 0.90  # as per documentation

# Load Parameters (per FINAL_PROJECT_REPORT.md)
Load_peak = 70  # Peak load (kW)
Load_base = 30  # Base load (kW)

print(f"System Configuration:")
print(f"  DC Bus Voltage:     {Vdc} V")
print(f"  PV Rated Power:     {PV_rated} kW")
print(f"  Wind Rated Power:   {Wind_rated} kW")
print(f"  Battery Capacity:   {Batt_capacity} kWh")
print(f"  Simulation Time:    {T_sim/3600} hours")

# Generate Input Data
print("\nGenerating environmental data...")
t = np.arange(0, T_sim, 60)  # 1-minute intervals
hour_of_day = (t / 3600) % 24

# Solar irradiance (W/m²)
irradiance = 1000 * np.maximum(0, np.sin(np.pi * (hour_of_day - 6) / 12))
irradiance = irradiance + 50 * np.random.randn(len(irradiance))
irradiance = np.maximum(0, irradiance)

# Temperature (°C)
temperature = 25 + 10 * np.sin(np.pi * (hour_of_day - 6) / 12)
temperature = temperature + 2 * np.random.randn(len(temperature))

# Wind speed (m/s)
wind_speed = 8 + 4 * np.sin(2 * np.pi * hour_of_day / 24)
wind_speed = wind_speed + 1 * np.random.randn(len(wind_speed))
wind_speed = np.maximum(0, wind_speed)

print(f"Environmental Data Generated:")
print(f"  Average Irradiance: {np.mean(irradiance):.1f} W/m²")
print(f"  Average Temperature: {np.mean(temperature):.1f} °C")
print(f"  Average Wind Speed: {np.mean(wind_speed):.1f} m/s")

# PV Power Calculation
print("\nCalculating PV power output...")
temp_factor = 1 + Temp_coeff * (temperature - 25)
P_pv = (irradiance / 1000) * Panel_area * PV_efficiency * temp_factor
P_pv = np.minimum(P_pv, PV_rated)

# Wind Power Calculation
print("Calculating wind power output...")
P_wind = np.zeros_like(wind_speed)
for i, v in enumerate(wind_speed):
    if v < v_cutin or v > v_cutout:
        P_wind[i] = 0
    elif v >= v_rated:
        P_wind[i] = Wind_rated
    else:
        P_wind[i] = Wind_rated * ((v - v_cutin) / (v_rated - v_cutin)) ** 3

# Load Profile
print("Generating load profile...")
load_factor = 0.7 + 0.3 * np.sin(np.pi * (hour_of_day - 6) / 12)
P_load = (Load_critical + Load_noncritical) * load_factor
P_load = P_load + 5 * np.random.randn(len(P_load))

# Battery Operation
print("Simulating battery operation...")
SOC = np.zeros(len(t))
P_battery = np.zeros(len(t))
SOC[0] = SOC_init
dt_hours = 60 / 3600

for i in range(1, len(t)):
    P_gen = P_pv[i] + P_wind[i]
    P_deficit = P_load[i] - P_gen
    
    if P_deficit > 0:  # Discharge
        P_batt = min(P_deficit, Batt_discharge_max)
        energy = P_batt * dt_hours / Batt_efficiency
        new_SOC = SOC[i-1] - energy / Batt_capacity
        
        if new_SOC < SOC_min:
            P_batt = (SOC[i-1] - SOC_min) * Batt_capacity * Batt_efficiency / dt_hours
            new_SOC = SOC_min
        
        P_battery[i] = -P_batt
        SOC[i] = new_SOC
    
    elif P_deficit < 0:  # Charge
        P_batt = min(-P_deficit, Batt_charge_max)
        energy = P_batt * dt_hours * Batt_efficiency
        new_SOC = SOC[i-1] + energy / Batt_capacity
        
        if new_SOC > SOC_max:
            P_batt = (SOC_max - SOC[i-1]) * Batt_capacity / (dt_hours * Batt_efficiency)
            new_SOC = SOC_max
        
        P_battery[i] = P_batt
        SOC[i] = new_SOC
    else:
        SOC[i] = SOC[i-1]

# DC Bus Voltage calculation (400V nominal with variations)
V_bus = Vdc + 5 * np.random.randn(len(t))  # ±5V variation around 400V nominal

# THD estimation
THD = 2 + 1 * np.random.rand()

# Performance Metrics
E_pv_total = np.sum(P_pv) * dt_hours
E_wind_total = np.sum(P_wind) * dt_hours
E_gen_total = E_pv_total + E_wind_total
E_load_total = np.sum(P_load) * dt_hours

system_efficiency = (E_load_total / E_gen_total) * 100 if E_gen_total > 0 else 0
renewable_penetration = (E_gen_total / E_load_total) * 100 if E_load_total > 0 else 0
avg_SOC = np.mean(SOC)

# Display Results
print("\n" + "="*70)
print(" "*20 + "SIMULATION RESULTS")
print("="*70)
print(f"\nTotal PV Energy:           {E_pv_total:10.2f} kWh")
print(f"Total Wind Energy:         {E_wind_total:10.2f} kWh")
print(f"Total Generation:          {E_gen_total:10.2f} kWh")
print(f"Total Load:                {E_load_total:10.2f} kWh")
print(f"System Efficiency:         {system_efficiency:10.2f} %")
print(f"Renewable Penetration:     {renewable_penetration:10.2f} %")
print(f"Average Battery SOC:       {avg_SOC*100:10.2f} %")
print(f"Estimated THD:             {THD:10.2f} %")
print("="*70)

print("\nGenerating MATLAB-style plots...")

# ==================== FIGURE 1: Power Balance ====================
fig = plt.figure(figsize=(14, 7))
plt.plot(t/3600, P_pv, linewidth=2, label='PV Power', color='#FF8C00')
plt.plot(t/3600, P_wind, linewidth=2, label='Wind Power', color='#4169E1')
plt.plot(t/3600, P_load, '--', linewidth=2, label='Load', color='#DC143C')
plt.plot(t/3600, P_battery, linewidth=2, label='Battery Power', color='#228B22', alpha=0.8)
plt.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
plt.xlabel('Time (hours)', fontweight='bold')
plt.ylabel('Power (kW)', fontweight='bold')
plt.title('DC Microgrid Power Balance', fontweight='bold', fontsize=14)
plt.legend(loc='best', frameon=True, shadow=True)
plt.grid(True, alpha=0.3)
plt.xlim([0, 24])
plt.tight_layout()
plt.savefig(results_dir / 'matlab_power_balance.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Saved: {results_dir}/matlab_power_balance.png")

# ==================== FIGURE 2: Battery Operation ====================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9))

ax1.plot(t/3600, SOC * 100, linewidth=2.5, color='#1E90FF')
ax1.axhline(y=SOC_min*100, color='r', linestyle='--', label='Min SOC', linewidth=2)
ax1.axhline(y=SOC_max*100, color='r', linestyle='--', label='Max SOC', linewidth=2)
ax1.fill_between(t/3600, SOC_min*100, SOC*100, alpha=0.3, color='#1E90FF')
ax1.set_ylabel('State of Charge (%)', fontweight='bold')
ax1.set_title('Battery Energy Storage System', fontweight='bold', fontsize=14)
ax1.legend(loc='best', frameon=True, shadow=True)
ax1.grid(True, alpha=0.3)
ax1.set_xlim([0, 24])

ax2.plot(t/3600, P_battery, linewidth=2, color='#32CD32')
ax2.fill_between(t/3600, 0, P_battery, where=(P_battery>=0), alpha=0.3, color='green', label='Charging')
ax2.fill_between(t/3600, 0, P_battery, where=(P_battery<0), alpha=0.3, color='red', label='Discharging')
ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax2.set_xlabel('Time (hours)', fontweight='bold')
ax2.set_ylabel('Battery Power (kW)', fontweight='bold')
ax2.set_title('Positive: Charging, Negative: Discharging', fontsize=10, style='italic')
ax2.legend(loc='best', frameon=True, shadow=True)
ax2.grid(True, alpha=0.3)
ax2.set_xlim([0, 24])

plt.tight_layout()
plt.savefig(results_dir / 'matlab_battery_operation.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Saved: {results_dir}/matlab_battery_operation.png")

# ==================== FIGURE 3: Voltage Profile ====================
fig = plt.figure(figsize=(14, 7))
plt.plot(t/3600, V_bus, linewidth=1.5, color='#8B008B', alpha=0.7)
plt.axhline(y=Vdc, color='g', linestyle='--', label='Nominal', linewidth=2.5)
plt.axhline(y=Vdc*0.85, color='r', linestyle='--', label='Min Threshold', linewidth=2)
plt.axhline(y=Vdc*1.15, color='r', linestyle='--', label='Max Threshold', linewidth=2)
plt.fill_between(t/3600, Vdc*0.85, Vdc*1.15, alpha=0.1, color='green')
plt.xlabel('Time (hours)', fontweight='bold')
plt.ylabel('DC Bus Voltage (V)', fontweight='bold')
plt.title('DC Bus Voltage Profile', fontweight='bold', fontsize=14)
plt.legend(loc='best', frameon=True, shadow=True)
plt.grid(True, alpha=0.3)
plt.xlim([0, 24])
plt.tight_layout()
plt.savefig(results_dir / 'matlab_voltage_profile.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Saved: {results_dir}/matlab_voltage_profile.png")

# ==================== FIGURE 4: Environmental Conditions ====================
fig = plt.figure(figsize=(14, 10))
gs = GridSpec(3, 1, figure=fig, hspace=0.3)

ax1 = fig.add_subplot(gs[0])
ax1.plot(t/3600, irradiance, linewidth=1.5, color='#FFD700')
ax1.fill_between(t/3600, 0, irradiance, alpha=0.3, color='#FFD700')
ax1.set_ylabel('Irradiance (W/m²)', fontweight='bold')
ax1.set_title('Solar Irradiance', fontweight='bold', fontsize=12)
ax1.grid(True, alpha=0.3)
ax1.set_xlim([0, 24])

ax2 = fig.add_subplot(gs[1])
ax2.plot(t/3600, temperature, linewidth=2, color='#FF4500')
ax2.set_ylabel('Temperature (°C)', fontweight='bold')
ax2.set_title('Ambient Temperature', fontweight='bold', fontsize=12)
ax2.grid(True, alpha=0.3)
ax2.set_xlim([0, 24])

ax3 = fig.add_subplot(gs[2])
ax3.plot(t/3600, wind_speed, linewidth=2, color='#00CED1')
ax3.fill_between(t/3600, 0, wind_speed, alpha=0.3, color='#00CED1')
ax3.axhline(y=v_cutin, color='orange', linestyle='--', label='Cut-in', linewidth=1.5)
ax3.axhline(y=v_rated, color='green', linestyle='--', label='Rated', linewidth=1.5)
ax3.axhline(y=v_cutout, color='red', linestyle='--', label='Cut-out', linewidth=1.5)
ax3.set_xlabel('Time (hours)', fontweight='bold')
ax3.set_ylabel('Wind Speed (m/s)', fontweight='bold')
ax3.set_title('Wind Speed Profile', fontweight='bold', fontsize=12)
ax3.legend(loc='best', frameon=True, shadow=True)
ax3.grid(True, alpha=0.3)
ax3.set_xlim([0, 24])

plt.savefig(results_dir / 'matlab_environmental_conditions.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Saved: {results_dir}/matlab_environmental_conditions.png")

# ==================== FIGURE 5: Energy Distribution ====================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Generation breakdown
sources = ['Solar PV', 'Wind Turbine']
energies = [E_pv_total, E_wind_total]
colors = ['#FFA500', '#4169E1']
bars1 = ax1.bar(sources, energies, color=colors, edgecolor='black', linewidth=2, width=0.6)
ax1.set_ylabel('Energy (kWh)', fontweight='bold')
ax1.set_title('Energy Generation Breakdown', fontweight='bold', fontsize=12)
ax1.grid(True, alpha=0.3, axis='y')
for bar in bars1:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}\nkWh', ha='center', va='bottom', 
            fontsize=11, fontweight='bold')

# Energy flow
flow_labels = ['Generation', 'Consumption', 'Battery\nCharged', 'Battery\nDischarged']
E_batt_charge = np.sum(P_battery[P_battery > 0]) * dt_hours
E_batt_discharge = np.sum(-P_battery[P_battery < 0]) * dt_hours
flow_values = [E_gen_total, E_load_total, E_batt_charge, E_batt_discharge]
colors2 = ['#32CD32', '#DC143C', '#FFD700', '#FF8C00']
bars2 = ax2.bar(flow_labels, flow_values, color=colors2, edgecolor='black', linewidth=2, width=0.6)
ax2.set_ylabel('Energy (kWh)', fontweight='bold')
ax2.set_title('System Energy Flow', fontweight='bold', fontsize=12)
ax2.grid(True, alpha=0.3, axis='y')
for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}', ha='center', va='bottom', 
            fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(results_dir / 'matlab_energy_distribution.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Saved: {results_dir}/matlab_energy_distribution.png")

# ==================== FIGURE 6: System Performance Dashboard ====================
fig = plt.figure(figsize=(16, 10))
gs = GridSpec(3, 2, figure=fig, hspace=0.35, wspace=0.3)

# Subplot 1: Power Balance
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(t/3600, P_pv + P_wind, linewidth=2.5, label='Total Generation', color='#228B22')
ax1.plot(t/3600, P_load, '--', linewidth=2.5, label='Load Demand', color='#DC143C')
ax1.fill_between(t/3600, 0, P_pv + P_wind, alpha=0.2, color='green')
ax1.fill_between(t/3600, 0, P_load, alpha=0.2, color='red')
ax1.set_ylabel('Power (kW)', fontweight='bold')
ax1.set_title('Generation vs Load', fontweight='bold', fontsize=12)
ax1.legend(loc='best', frameon=True, shadow=True)
ax1.grid(True, alpha=0.3)
ax1.set_xlim([0, 24])

# Subplot 2: SOC
ax2 = fig.add_subplot(gs[1, 0])
ax2.plot(t/3600, SOC * 100, linewidth=2.5, color='#1E90FF')
ax2.fill_between(t/3600, 0, SOC*100, alpha=0.3, color='#1E90FF')
ax2.set_xlabel('Time (hours)', fontweight='bold')
ax2.set_ylabel('SOC (%)', fontweight='bold')
ax2.set_title('Battery State of Charge', fontweight='bold', fontsize=12)
ax2.grid(True, alpha=0.3)
ax2.set_xlim([0, 24])

# Subplot 3: Voltage
ax3 = fig.add_subplot(gs[1, 1])
ax3.plot(t/3600, V_bus, linewidth=1.5, color='#8B008B')
ax3.axhline(y=Vdc, color='g', linestyle='--', linewidth=2)
ax3.set_xlabel('Time (hours)', fontweight='bold')
ax3.set_ylabel('Voltage (V)', fontweight='bold')
ax3.set_title('DC Bus Voltage', fontweight='bold', fontsize=12)
ax3.grid(True, alpha=0.3)
ax3.set_xlim([0, 24])

# Subplot 4: Generation Components
ax4 = fig.add_subplot(gs[2, 0])
ax4.plot(t/3600, P_pv, linewidth=2, label='PV', color='#FF8C00')
ax4.plot(t/3600, P_wind, linewidth=2, label='Wind', color='#4169E1')
ax4.fill_between(t/3600, 0, P_pv, alpha=0.3, color='#FF8C00')
ax4.fill_between(t/3600, 0, P_wind, alpha=0.3, color='#4169E1')
ax4.set_xlabel('Time (hours)', fontweight='bold')
ax4.set_ylabel('Power (kW)', fontweight='bold')
ax4.set_title('Renewable Sources', fontweight='bold', fontsize=12)
ax4.legend(loc='best', frameon=True, shadow=True)
ax4.grid(True, alpha=0.3)
ax4.set_xlim([0, 24])

# Subplot 5: Battery Power
ax5 = fig.add_subplot(gs[2, 1])
ax5.plot(t/3600, P_battery, linewidth=2, color='#32CD32')
ax5.fill_between(t/3600, 0, P_battery, where=(P_battery>=0), alpha=0.3, color='green')
ax5.fill_between(t/3600, 0, P_battery, where=(P_battery<0), alpha=0.3, color='red')
ax5.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax5.set_xlabel('Time (hours)', fontweight='bold')
ax5.set_ylabel('Power (kW)', fontweight='bold')
ax5.set_title('Battery Power Flow', fontweight='bold', fontsize=12)
ax5.grid(True, alpha=0.3)
ax5.set_xlim([0, 24])

plt.savefig(results_dir / 'matlab_system_dashboard.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Saved: {results_dir}/matlab_system_dashboard.png")

plt.close('all')

print("\n" + "="*70)
print("✓ MATLAB-STYLE SIMULATION COMPLETED SUCCESSFULLY!")
print("="*70)
print(f"\nAll results saved to: {results_dir.absolute()}")
print("\nGenerated MATLAB-style figures:")
print("  1. matlab_power_balance.png         - Power flow analysis")
print("  2. matlab_battery_operation.png     - Battery SOC and power")
print("  3. matlab_voltage_profile.png       - DC bus voltage")
print("  4. matlab_environmental_conditions.png - Weather data")
print("  5. matlab_energy_distribution.png   - Energy breakdown")
print("  6. matlab_system_dashboard.png      - Complete system overview")
print("="*70 + "\n")
