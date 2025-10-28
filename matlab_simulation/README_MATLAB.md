# MATLAB/Simulink DC Microgrid Simulation

## 📋 Overview

This directory contains MATLAB scripts and Simulink models for simulating a DC microgrid with renewable energy integration, battery energy storage, and AI-based protection systems.

## 📁 Files

### 1. **dc_microgrid_simulation.m**
Complete MATLAB script-based simulation
- **Purpose**: Standalone simulation without Simulink
- **Features**:
  - PV system modeling with temperature effects
  - Wind turbine power curve implementation
  - Battery SOC management
  - Power flow analysis
  - Automated plot generation
- **Usage**:
  ```matlab
  cd matlab_simulation
  dc_microgrid_simulation
  ```

### 2. **create_dc_microgrid_simulink_blocks.m**
Programmatic Simulink model builder
- **Purpose**: Creates complete Simulink block diagram
- **Features**:
  - Automatic block placement and connection
  - Environmental input blocks (Solar, Wind, Temperature)
  - PV System block with MATLAB Function
  - Wind Turbine block with power curve
  - Battery Management System (BMS) block
  - Power balance and summation blocks
  - Real-time monitoring scopes
  - Display blocks for key parameters
- **Usage**:
  ```matlab
  cd matlab_simulation
  create_dc_microgrid_simulink_blocks
  % This creates: DC_Microgrid_Model.slx
  ```

## 🔧 Simulink Model Components

### Input Blocks
1. **Solar Irradiance** (Signal Generator)
   - Sinusoidal pattern simulating daily solar cycle
   - Amplitude: 1000 W/m²
   - Period: 24 hours

2. **Temperature** (Signal Generator)
   - Ambient temperature variation
   - Base: 25°C, Variation: ±10°C

3. **Wind Speed** (Signal Generator)
   - Wind speed profile
   - Base: 8 m/s, Variation: ±4 m/s

### Generation Blocks
1. **PV System** (MATLAB Function)
   ```matlab
   Inputs: irradiance, temperature
   Output: P_pv (kW)
   Parameters:
   - Panel Area: 600 m²
   - Efficiency: 18%
   - Rated Power: 100 kW
   - Temperature Coefficient: -0.004/°C
   ```

2. **Wind Turbine** (MATLAB Function)
   ```matlab
   Input: wind_speed
   Output: P_wind (kW)
   Parameters:
   - Rated Power: 50 kW
   - Cut-in Speed: 3 m/s
   - Rated Speed: 12 m/s
   - Cut-out Speed: 25 m/s
   ```

### Control Blocks
1. **Total Generation** (Add Block)
   - Sums PV and Wind power
   - Output: Pgen = Ppv + Pwind

2. **Power Balance** (Subtract Block)
   - Calculates power deficit/surplus
   - Output: ΔP = Pgen - Pload

3. **Battery BMS** (MATLAB Function)
   ```matlab
   Inputs: P_deficit, SOC_prev
   Outputs: P_batt, SOC
   Parameters:
   - Capacity: 200 kWh
   - Max Charge: 50 kW
   - Max Discharge: 50 kW
   - SOC Range: 20-90%
   - Efficiency: 95%
   ```

4. **SOC Delay** (Unit Delay)
   - Provides SOC feedback
   - Initial Condition: 0.5 (50%)

### Monitoring Blocks
1. **Power Scope** (4 inputs)
   - PV Power
   - Wind Power
   - Load
   - Battery Power

2. **SOC Scope**
   - Battery State of Charge

3. **Display Blocks**
   - PV Power Display
   - Wind Power Display
   - SOC Display

## 🎯 Running the Simulation

### Method 1: Script-Based Simulation
```matlab
% Navigate to directory
cd matlab_simulation

% Run simulation
dc_microgrid_simulation

% Results are automatically saved to results/ directory
```

### Method 2: Simulink Model
```matlab
% Create Simulink model (one-time)
create_dc_microgrid_simulink_blocks

% Open the model
open_system('DC_Microgrid_Model')

% Run simulation
sim('DC_Microgrid_Model')

% OR click the Run button in Simulink
```

### Method 3: From Command Window
```matlab
% Set simulation parameters
simOut = sim('DC_Microgrid_Model', ...
            'StartTime', '0', ...
            'StopTime', '86400', ...
            'Solver', 'ode45');

% Access results
% simOut contains all scope data
```

## 📊 Output Files

After running `dc_microgrid_simulation.m`:
- `results/matlab_power_balance.png`
- `results/matlab_battery_operation.png`
- `results/matlab_voltage_profile.png`

## 🔬 Simulation Parameters

| Parameter | Value | Unit |
|-----------|-------|------|
| DC Bus Voltage | 380 | V |
| Simulation Time | 24 | hours |
| Time Step | 1 | second |
| PV Rated Power | 100 | kW |
| Wind Rated Power | 50 | kW |
| Battery Capacity | 200 | kWh |
| Battery SOC Min | 20 | % |
| Battery SOC Max | 90 | % |
| Battery Efficiency | 95 | % |

## 🎨 Block Diagram

The Simulink model follows this structure:

```
Environmental Inputs → Renewable Generation → Power Summation
                                                      ↓
                                              Power Balance
                                                      ↓
Load Demand ────────────────────────→ Battery Management System
                                                      ↓
                                               SOC Feedback
                                                      ↓
                                            Monitoring Scopes
```

Visual block diagram: `results/matlab_style/simulink_block_diagram.png`

## 🔍 Key Features

### 1. **Realistic Environmental Modeling**
- Daily solar irradiance patterns
- Temperature variation effects on PV
- Stochastic wind speed profiles

### 2. **Advanced Battery Management**
- State-based charging/discharging logic
- SOC constraints enforcement
- Round-trip efficiency modeling
- Real-time SOC feedback

### 3. **Power Quality Analysis**
- Voltage profile monitoring
- THD estimation
- Power balance verification

### 4. **Modular Design**
- Each component is a separate block
- Easy to modify individual subsystems
- Scalable architecture

## 🛠️ Customization

### Modify PV Parameters
Edit the PV_System MATLAB Function block:
```matlab
Panel_area = 800;      % Increase panel area
efficiency = 0.20;     % Higher efficiency panels
rated_power = 150;     % Increase rated power
```

### Modify Battery Parameters
Edit the Battery_BMS MATLAB Function block:
```matlab
capacity = 300;        % Larger battery
max_charge = 75;       % Higher charge rate
SOC_min = 0.15;        % Lower minimum SOC
```

### Add More Renewable Sources
1. Add new signal generator block
2. Create corresponding generation block
3. Add to Total_Generation sum block

## 📈 Performance Metrics

The simulation calculates:
- Total energy generation (PV + Wind)
- Total load consumption
- System efficiency
- Renewable penetration
- Battery cycle performance
- Average SOC
- Voltage stability metrics

## 🧪 Validation

The model has been validated against:
- IEEE DC microgrid standards
- Published research data
- Real-world microgrid performance

## 📚 References

1. IEEE Standard 1547: Interconnection of Distributed Energy Resources
2. IEC 62786: DC Microgrids for Rural Electrification
3. MATLAB Simscape Electrical Documentation

## 🤝 Support

For issues or questions about the MATLAB simulation:
- Check MATLAB version compatibility (R2020b or later recommended)
- Ensure Simulink is installed
- Verify Signal Processing Toolbox availability

## 📝 Notes

- **MATLAB Version**: Tested on R2020b and later
- **Required Toolboxes**: Simulink, Signal Processing
- **Optional**: Simscape Electrical for advanced power system modeling

## 🎓 Academic Use

Developed for research at COEP Technological University, Pune
- Guide: Dr. Arti V. Tare
- Researcher: Nivas D. Navghare
- Department: Electrical Engineering

---

*Last Updated: October 2025*
