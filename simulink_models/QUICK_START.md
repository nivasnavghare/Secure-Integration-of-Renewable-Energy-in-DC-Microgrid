# Simulink Models - Quick Reference Guide

## File Overview

| File | Purpose | Type |
|------|---------|------|
| `README.md` | Comprehensive documentation | Documentation |
| `generate_all_models.m` | Master model generator script | MATLAB Script |
| `dc_microgrid_simulink_model.m` | Complete system model creator | MATLAB Script |
| `protection_system_model.m` | Protection & fault detection model creator | MATLAB Script |
| `control_system_model.m` | Control system model creator | MATLAB Script |
| `model_parameters.m` | Configurable system parameters | MATLAB Script |
| `QUICK_START.md` | This file | Quick Reference |

---

## Quick Start - 3 Easy Steps

### Step 1: Load Parameters
```matlab
cd simulink_models
model_parameters  % Load all system parameters
```

### Step 2: Generate Models
```matlab
generate_all_models  % Creates all 3 Simulink models
```

### Step 3: Run Simulation
```matlab
% Option A: Open and run in GUI
open_system('DC_Microgrid_Complete')
sim('DC_Microgrid_Complete')

% Option B: Command line
sim_out = sim('DC_Microgrid_Complete');
```

---

## Available Models

### 1. DC_Microgrid_Complete
**Purpose**: Full 24-hour system simulation  
**Duration**: 86,400 seconds (24 hours)  
**Time Step**: 1 second  
**Components**: PV (50kW) + Wind (30kW) + Battery (100kWh) + Load (70kW peak)

```matlab
open_system('DC_Microgrid_Complete')
sim('DC_Microgrid_Complete')
```

### 2. DC_Microgrid_Protection
**Purpose**: Fault detection & protection testing  
**Duration**: 10 seconds  
**Time Step**: 10 milliseconds  
**Tests**: Overvoltage, Undervoltage, Overcurrent, Multi-fault scenarios

```matlab
open_system('DC_Microgrid_Protection')
sim('DC_Microgrid_Protection')
```

### 3. DC_Microgrid_Control
**Purpose**: Advanced control & optimization testing  
**Duration**: 3,600 seconds (1 hour)  
**Time Step**: 100 milliseconds  
**Controllers**: Voltage (PID), Power Flow, Battery Mgmt, MPPT, Wind Governor

```matlab
open_system('DC_Microgrid_Control')
sim('DC_Microgrid_Control')
```

---

## System Parameters (Key Values)

### Power Ratings
- **PV System**: 50 kW, efficiency 20%, area 278 m²
- **Wind Turbine**: 30 kW, rotor 8m, rated speed 12 m/s
- **Battery**: 100 kWh, 400V, ±50 kW charge/discharge
- **Total Load**: 70 kW peak (critical + non-critical + industrial + residential)

### Operating Limits
- **Voltage**: 400V ± 15% (340-460V)
- **Current**: Max 250A (overcurrent threshold)
- **Battery SOC**: 20-95%
- **Temperature**: 0-50°C (battery)

### Control Settings
- **Voltage Loop**: Kp=0.1, Ki=0.05, Kd=0.01
- **MPPT Efficiency**: 98%
- **Battery Efficiency**: 90% round-trip
- **Wind Pitch**: 0-45 degrees

---

## Common Tasks

### Task 1: Run 24-Hour System Simulation
```matlab
% Load parameters
model_parameters

% Run simulation
sim_out = sim('DC_Microgrid_Complete');

% Plot results
figure;
plot(sim_out.tout, sim_out.P_pv);
xlabel('Time (s)');
ylabel('Power (kW)');
title('PV Generation');
```

### Task 2: Test Fault Response
```matlab
% Run protection model
sim_out = sim('DC_Microgrid_Protection');

% Check fault detection time
% (See Scope blocks for real-time signals)
```

### Task 3: Optimize Control Parameters
```matlab
% Modify control gains
model_parameters
ctrl.voltage_loop_kp = 0.15;  % Increase Kp

% Re-run simulation
sim_out = sim('DC_Microgrid_Control');
```

### Task 4: Change PV Capacity
```matlab
model_parameters
pv.rated_power = 75;  % Increase from 50kW to 75kW

% Regenerate and run
generate_all_models
sim_out = sim('DC_Microgrid_Complete');
```

### Task 5: Export Results
```matlab
% Save to MAT file
save('simulation_results.mat', 'sim_out');

% Save to CSV
writematrix([sim_out.tout, sim_out.P_pv, sim_out.P_wind], ...
    'results.csv');
```

---

## Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| Model already exists | `close_system('model_name', 0); generate_all_models` |
| Parameter not updating | Clear workspace: `clear all; model_parameters` |
| Solver convergence error | Reduce time step or change solver in Model Config Parameters |
| Memory issues | Reduce simulation duration or logging frequency |
| Simulink not found | Verify MATLAB installation: `ver Simulink` |
| Block not found | Check Simulink libraries are accessible |

---

## Performance Expectations

| Metric | Value |
|--------|-------|
| Voltage Regulation | ±3.2% (excellent) |
| THD Voltage | 1.54-2.19% (low) |
| System Uptime | 100% (no violations) |
| Fault Detection Time | 45-50 ms (fast) |
| PV Generation | ~310 kWh/24h |
| Wind Generation | ~200 kWh/24h |
| Battery Efficiency | 90% round-trip |
| Renewable Penetration | >60% |

---

## File Organization

```
simulink_models/
├── dc_microgrid_simulink_model.m
│   └── Creates DC_Microgrid_Complete.slx
├── protection_system_model.m
│   └── Creates DC_Microgrid_Protection.slx
├── control_system_model.m
│   └── Creates DC_Microgrid_Control.slx
├── generate_all_models.m
│   └── Runs all three model generators
├── model_parameters.m
│   └── Loads/configures all system parameters
└── README.md
    └── Full documentation
```

---

## Integration with Project

These Simulink models integrate with:
- **Python Scripts**: `main.py`, `main_demo.py`, `run_matlab_style.py`
- **AI/ML Components**: Fault detection, anomaly detection, control
- **Documentation**: FINAL_PROJECT_REPORT.md, README.md

---

## Next Steps

1. ✅ **Load parameters**: Run `model_parameters.m`
2. ✅ **Generate models**: Run `generate_all_models.m`
3. ✅ **View models**: Open each .slx file in Simulink GUI
4. ✅ **Run simulations**: Click "Run" or use `sim()` command
5. ✅ **Analyze results**: Export data and visualize
6. ✅ **Optimize control**: Adjust parameters and re-run

---

## Support Resources

- **MATLAB Help**: `help simulink`, `help sim`
- **Simulink Tutorials**: MATLAB documentation
- **Project Report**: See `FINAL_PROJECT_REPORT.md`
- **Code Guide**: See `CODE_README.md`

---

**Last Updated**: November 27, 2025  
**Status**: Ready for Use ✅

