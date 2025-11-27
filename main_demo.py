#!/usr/bin/env python3
"""
DC Microgrid Simulation - Demo Version (No ML Dependencies)
Simplified demo that runs without TensorFlow/PyTorch for quick testing
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import yaml
import warnings
warnings.filterwarnings('ignore')

# Create results directory
results_dir = Path('results')
results_dir.mkdir(exist_ok=True)

print("="*60)
print("DC MICROGRID SIMULATION - DEMO VERSION")
print("="*60)

# Load configuration
print("\n[1/6] Loading configuration...")
with open('config/microgrid_config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Extract parameters
pv_rated = config['photovoltaic']['rated_power']
wind_rated = config['wind_turbine']['rated_power']
bess_capacity = config['bess']['capacity']
vdc = config['system']['voltage_level']

print(f"✓ System Voltage: {vdc}V DC (400V per documentation)")
print(f"✓ PV Capacity: {pv_rated}kW (50kW per FINAL_PROJECT_REPORT.md)")
print(f"✓ Wind Capacity: {wind_rated}kW (30kW per documentation)")
print(f"✓ Battery Capacity: {bess_capacity}kWh (100kWh per documentation)")
print(f"✓ Wind Capacity: {wind_rated}kW")
print(f"✓ Battery Capacity: {bess_capacity}kWh")

# Generate time series data
print("\n[2/6] Generating synthetic data...")
T = 24 * 3600  # 24 hours in seconds
dt = 60  # 1 minute time step
t = np.arange(0, T, dt)
hours = t / 3600

# Solar irradiance (W/m²) - sinusoidal pattern for day
irradiance = np.maximum(0, 1000 * np.sin(np.pi * (hours - 6) / 12))
irradiance += np.random.normal(0, 50, len(irradiance))
irradiance = np.maximum(0, irradiance)

# Temperature (°C)
temperature = 25 + 10 * np.sin(np.pi * (hours - 6) / 12)

# Wind speed (m/s)
wind_speed = 8 + 4 * np.sin(2 * np.pi * hours / 24) + np.random.normal(0, 1, len(hours))
wind_speed = np.maximum(0, wind_speed)

print(f"✓ Generated {len(t)} time steps ({T/3600:.0f} hours)")
print(f"✓ Average irradiance: {np.mean(irradiance):.1f} W/m²")
print(f"✓ Average wind speed: {np.mean(wind_speed):.1f} m/s")

# Calculate PV power
print("\n[3/6] Calculating renewable generation...")
pv_efficiency = 0.18
panel_area = 600  # m²
temp_coeff = -0.004

temp_factor = 1 + temp_coeff * (temperature - 25)
P_pv = (irradiance / 1000) * panel_area * pv_efficiency * temp_factor
P_pv = np.minimum(P_pv, pv_rated)

# Calculate wind power
v_cutin = 3
v_rated = 12
v_cutout = 25

P_wind = np.zeros_like(wind_speed)
for i, v in enumerate(wind_speed):
    if v < v_cutin or v > v_cutout:
        P_wind[i] = 0
    elif v >= v_rated:
        P_wind[i] = wind_rated
    else:
        P_wind[i] = wind_rated * ((v - v_cutin) / (v_rated - v_cutin)) ** 3

print(f"✓ Average PV power: {np.mean(P_pv):.1f} kW")
print(f"✓ Average Wind power: {np.mean(P_wind):.1f} kW")

# Generate load profile
print("\n[4/6] Simulating load demand...")
load_base = 80  # Base load in kW
load_variation = 0.3 + 0.2 * np.sin(np.pi * (hours - 6) / 12)
P_load = load_base * load_variation + np.random.normal(0, 5, len(hours))

print(f"✓ Average load: {np.mean(P_load):.1f} kW")
print(f"✓ Peak load: {np.max(P_load):.1f} kW")

# Battery simulation
print("\n[5/6] Simulating battery operation...")
SOC = np.zeros(len(t))
P_battery = np.zeros(len(t))
SOC[0] = 0.5  # 50% initial SOC

soc_min = 0.2
soc_max = 0.9
batt_efficiency = 0.95
max_charge = 50  # kW
max_discharge = 50  # kW

dt_hours = dt / 3600

for i in range(1, len(t)):
    P_gen = P_pv[i] + P_wind[i]
    P_deficit = P_load[i] - P_gen
    
    if P_deficit > 0:  # Discharge
        P_batt = min(P_deficit, max_discharge)
        energy = P_batt * dt_hours / batt_efficiency
        new_SOC = SOC[i-1] - energy / bess_capacity
        
        if new_SOC < soc_min:
            P_batt = (SOC[i-1] - soc_min) * bess_capacity * batt_efficiency / dt_hours
            new_SOC = soc_min
        
        P_battery[i] = -P_batt
        SOC[i] = new_SOC
    
    elif P_deficit < 0:  # Charge
        P_batt = min(-P_deficit, max_charge)
        energy = P_batt * dt_hours * batt_efficiency
        new_SOC = SOC[i-1] + energy / bess_capacity
        
        if new_SOC > soc_max:
            P_batt = (soc_max - SOC[i-1]) * bess_capacity / (dt_hours * batt_efficiency)
            new_SOC = soc_max
        
        P_battery[i] = P_batt
        SOC[i] = new_SOC
    else:
        SOC[i] = SOC[i-1]

print(f"✓ Average SOC: {np.mean(SOC)*100:.1f}%")
print(f"✓ Min SOC: {np.min(SOC)*100:.1f}%")
print(f"✓ Max SOC: {np.max(SOC)*100:.1f}%")

# Calculate metrics
print("\n[6/6] Calculating performance metrics...")
E_pv = np.sum(P_pv) * dt_hours
E_wind = np.sum(P_wind) * dt_hours
E_gen = E_pv + E_wind
E_load = np.sum(P_load) * dt_hours
E_batt_charge = np.sum(P_battery[P_battery > 0]) * dt_hours
E_batt_discharge = np.sum(-P_battery[P_battery < 0]) * dt_hours

renewable_penetration = (E_gen / E_load) * 100 if E_load > 0 else 0
batt_efficiency_actual = (E_batt_discharge / E_batt_charge) * 100 if E_batt_charge > 0 else 0

print("\n" + "="*60)
print("SIMULATION RESULTS")
print("="*60)
print(f"\nEnergy Generation:")
print(f"  PV Energy:        {E_pv:8.2f} kWh")
print(f"  Wind Energy:      {E_wind:8.2f} kWh")
print(f"  Total Generated:  {E_gen:8.2f} kWh")
print(f"\nEnergy Consumption:")
print(f"  Total Load:       {E_load:8.2f} kWh")
print(f"\nBattery Performance:")
print(f"  Energy Charged:   {E_batt_charge:8.2f} kWh")
print(f"  Energy Discharged:{E_batt_discharge:8.2f} kWh")
print(f"  Round-trip Eff:   {batt_efficiency_actual:8.1f} %")
print(f"\nSystem Metrics:")
print(f"  Renewable Penetration: {renewable_penetration:.1f}%")
print(f"  Average SOC:           {np.mean(SOC)*100:.1f}%")
print("="*60)

# Create visualizations
print("\nGenerating plots...")

# Plot 1: Power Balance
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(hours, P_pv, label='PV Power', linewidth=2)
ax.plot(hours, P_wind, label='Wind Power', linewidth=2)
ax.plot(hours, P_load, '--', label='Load Demand', linewidth=2)
ax.plot(hours, P_battery, label='Battery Power', linewidth=2, alpha=0.7)
ax.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax.set_xlabel('Time (hours)', fontsize=12)
ax.set_ylabel('Power (kW)', fontsize=12)
ax.set_title('DC Microgrid Power Balance', fontsize=14, fontweight='bold')
ax.legend(loc='best')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('results/power_balance.png', dpi=150)
print(f"✓ Saved: results/power_balance.png")

# Plot 2: Battery Operation
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

ax1.plot(hours, SOC * 100, linewidth=2, color='blue')
ax1.axhline(y=soc_min*100, color='r', linestyle='--', label='Min SOC', linewidth=1.5)
ax1.axhline(y=soc_max*100, color='r', linestyle='--', label='Max SOC', linewidth=1.5)
ax1.set_ylabel('State of Charge (%)', fontsize=12)
ax1.set_title('Battery Energy Storage System', fontsize=14, fontweight='bold')
ax1.legend(loc='best')
ax1.grid(True, alpha=0.3)

ax2.plot(hours, P_battery, linewidth=2, color='green')
ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax2.set_xlabel('Time (hours)', fontsize=12)
ax2.set_ylabel('Battery Power (kW)', fontsize=12)
ax2.set_title('Positive: Charging, Negative: Discharging', fontsize=10, style='italic')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('results/battery_operation.png', dpi=150)
print(f"✓ Saved: results/battery_operation.png")

# Plot 3: Renewable Generation
fig, ax = plt.subplots(figsize=(10, 6))
total_pv_energy = E_pv
total_wind_energy = E_wind
sources = ['Solar PV', 'Wind Turbine']
energies = [total_pv_energy, total_wind_energy]
colors = ['#FDB462', '#80B1D3']

bars = ax.bar(sources, energies, color=colors, edgecolor='black', linewidth=1.5)
ax.set_ylabel('Energy (kWh)', fontsize=12)
ax.set_title('Renewable Energy Generation (24 hours)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f} kWh',
            ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('results/renewable_generation.png', dpi=150)
print(f"✓ Saved: results/renewable_generation.png")

plt.close('all')

print("\n" + "="*60)
print("✓ SIMULATION COMPLETED SUCCESSFULLY!")
print("="*60)
print(f"\nResults saved to: {results_dir.absolute()}")
print("\nGenerated files:")
print("  - power_balance.png")
print("  - battery_operation.png")
print("  - renewable_generation.png")
print("\nNote: This is a demo version without ML components.")
print("For full AI-based fault detection, use Python 3.11/3.12 with TensorFlow.")
print("="*60 + "\n")
