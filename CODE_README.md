# DC Microgrid Project - Code Documentation

## 📁 Project Structure

```
Secure-Integration-of-Renewable-Energy-in-DC-Microgrid/
├── config/
│   └── microgrid_config.yaml      # System configuration
├── data/                           # Input data directory
├── matlab_simulation/
│   └── dc_microgrid_simulation.m  # MATLAB simulation script
├── notebooks/                      # Jupyter notebooks for analysis
├── results/                        # Simulation results and plots
├── src/
│   ├── __init__.py
│   ├── ai_protection/             # AI-based protection system
│   │   ├── __init__.py
│   │   ├── fault_detection.py    # LSTM/CNN fault detector
│   │   ├── anomaly_detection.py  # Isolation Forest anomaly detector
│   │   └── adaptive_relay.py     # DQN adaptive relay coordinator
│   ├── cybersecurity/            # Cybersecurity modules
│   ├── microgrid_model/          # Microgrid physical models
│   │   ├── __init__.py
│   │   ├── components.py         # PV, Wind, Battery, Load models
│   │   ├── network.py            # Complete microgrid system
│   │   └── power_flow.py         # Power flow analysis
│   ├── optimization/             # Optimization algorithms
│   └── utils/                    # Utility functions
│       ├── __init__.py
│       ├── data_logger.py        # Data persistence
│       ├── visualizer.py         # Plotting utilities
│       └── performance_metrics.py # Metrics calculation
├── tests/                         # Unit tests
├── main.py                        # Main simulation entry point
├── requirements.txt               # Python dependencies
├── .gitignore
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- MATLAB R2020b or higher (optional, for MATLAB simulations)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/nivasnavghare/Secure-Integration-of-Renewable-Energy-in-DC-Microgrid.git
cd Secure-Integration-of-Renewable-Energy-in-DC-Microgrid
```

2. **Create virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## 💻 Usage

### Running Python Simulation

```bash
python main.py
```

This will:
- Load configuration from `config/microgrid_config.yaml`
- Initialize microgrid components
- Run AI-based protection systems
- Generate results and visualizations
- Save outputs to `results/` directory

### Running MATLAB Simulation

```matlab
cd matlab_simulation
dc_microgrid_simulation
```

### Configuration

Edit `config/microgrid_config.yaml` to modify:
- System parameters (voltage, capacity, etc.)
- Component specifications (PV, wind, battery)
- AI/ML algorithm settings
- Protection thresholds
- Simulation parameters

## 📊 Module Descriptions

### 1. Microgrid Model (`src/microgrid_model/`)

#### `components.py`
- **PVSystem**: Photovoltaic system model with MPPT
- **WindTurbine**: Wind turbine with power curve modeling
- **BatteryStorage**: Li-ion battery with SOC management
- **Load**: Load models with voltage dependency

#### `network.py`
- **DCMicrogrid**: Complete system integration
- Power balance calculations
- System stability checks
- Reliability metrics (SAIFI, SAIDI)

#### `power_flow.py`
- **PowerFlowAnalyzer**: DC power flow solver
- Newton-Raphson algorithm
- THD calculation
- Voltage stability analysis

### 2. AI Protection (`src/ai_protection/`)

#### `fault_detection.py`
- **FaultDetector**: LSTM/CNN-based fault detection
- Fault types: short circuit, open circuit, ground fault, over/under voltage
- Real-time classification with confidence scores
- Model training and persistence

#### `anomaly_detection.py`
- **AnomalyDetector**: Isolation Forest for anomaly detection
- Cybersecurity threat identification
- Continuous monitoring capability
- Attack type classification (DDoS, Brute Force, etc.)

#### `adaptive_relay.py`
- **AdaptiveRelayCoordinator**: DQN reinforcement learning
- Adaptive relay coordination
- Experience replay mechanism
- Reward-based optimization

### 3. Utilities (`src/utils/`)

#### `data_logger.py`
- HDF5 data persistence
- CSV export functionality
- JSON metrics storage

#### `visualizer.py`
- Power balance plots
- Battery operation visualization
- Voltage profile graphs
- Renewable generation breakdown

#### `performance_metrics.py`
- Energy calculations
- System efficiency
- Battery cycle counting
- THD estimation
- Voltage quality metrics

## 🔧 Key Features

### Python Implementation

1. **Modular Architecture**: Easily extendable component-based design
2. **AI/ML Integration**: TensorFlow-based deep learning models
3. **Real-time Simulation**: Event-driven simulation engine
4. **Comprehensive Logging**: Detailed logging with multiple verbosity levels
5. **Visualization**: Publication-quality plots and charts
6. **Data Persistence**: HDF5 format for efficient data storage

### MATLAB Implementation

1. **Simulink Models**: Visual modeling of power systems
2. **Power System Toolbox**: Specialized electrical system analysis
3. **Fast Computation**: Optimized numerical algorithms
4. **Built-in Analysis**: THD, power quality, and harmonic analysis

## 📈 Output Files

After running simulations, check the `results/` directory for:

- `simulation_results.h5` - Complete time-series data
- `power_balance.png` - Power generation and load plot
- `battery_operation.png` - Battery SOC and power plot
- `voltage_profile.png` - DC bus voltage over time
- `renewable_generation.png` - Renewable energy breakdown
- `simulation_results.csv` - Exported CSV data (optional)
- `metrics.json` - Performance metrics summary

## 🧪 Testing

Run unit tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## 📝 Configuration Example

```yaml
system:
  voltage_level: 400  # DC voltage in Volts - per FINAL_PROJECT_REPORT.md
  
photovoltaic:
  rated_power: 50  # kW - per documentation
  efficiency: 0.18
  panel_area: 278  # m² - calculated for 50kW
  
wind_turbine:
  rated_power: 30  # kW - per documentation
  cut_in_speed: 3  # m/s
  rotor_diameter: 8  # meters - per documentation
  
bess:
  capacity: 100  # kWh - per documentation
  initial_soc: 0.5
  max_soc: 0.95  # per documentation
  efficiency: 0.90  # per documentation
  
ai_ml:
  fault_detection:
    model_type: "LSTM"
    confidence_threshold: 0.85
```

## 🎓 Academic Use

This code is developed as part of research at COEP Technological University, Pune. If you use this code in your research, please cite:

```
Navghare, N. D. (2025). Secure Integration of Renewable Energy in DC Microgrid.
Master's Thesis, COEP Technological University, Pune.
Guide: Dr. Arti V. Tare
```

## 🤝 Contributing

This is an academic research project. For collaboration opportunities:
- Email: nivas.navghare@gmail.com
- GitHub Issues: Report bugs or request features

## 📄 License

MIT License - See [LICENSE](../LICENSE) file for details

## 🙏 Acknowledgments

- Dr. Arti V. Tare (Research Guide)
- COEP Technological University, Pune
- Department of Electrical Engineering

---

**Note**: This is a research prototype. For production deployment, additional validation and safety measures are required.

*Last Updated: October 2025*
