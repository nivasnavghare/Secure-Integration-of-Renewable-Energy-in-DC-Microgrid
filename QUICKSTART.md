# Quick Start Guide

## Running Your First Simulation

### Option 1: Python Simulation (Recommended)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run simulation:**
   ```bash
   python main.py
   ```

3. **Check results:**
   ```bash
   ls results/
   ```

### Option 2: MATLAB Simulation

1. **Open MATLAB**

2. **Navigate to project:**
   ```matlab
   cd matlab_simulation
   ```

3. **Run script:**
   ```matlab
   dc_microgrid_simulation
   ```

## Expected Output

```
Starting DC Microgrid Simulation
PV System initialized
Wind Turbine initialized
Battery Storage initialized
AI protection systems initialized
Running simulation for 3600 seconds
...
Simulation completed successfully!
```

## Troubleshooting

**Issue**: Import errors
```bash
pip install --upgrade -r requirements.txt
```

**Issue**: MATLAB path errors
```matlab
addpath(genpath('.'))
```

## Next Steps

1. Modify `config/microgrid_config.yaml` to customize your simulation
2. Explore Jupyter notebooks in `notebooks/` directory
3. Review code documentation in `CODE_README.md`

---
For detailed documentation, see [CODE_README.md](CODE_README.md)
