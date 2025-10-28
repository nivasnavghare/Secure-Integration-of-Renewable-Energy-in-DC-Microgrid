# Secure Integration of Renewable Energy in DC Microgrid

> **Ensuring reliable and safe renewable power delivery**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![University](https://img.shields.io/badge/University-COEP%20Pune-blue)](https://www.coep.org.in/)

## � Quick Start

### Running the Simulation

**Option 1: Demo Version (No ML dependencies - Quick Start)**
```bash
# 1. Install core dependencies
pip install numpy scipy pandas matplotlib scikit-learn pyyaml h5py

# 2. Run demo simulation
python main_demo.py
```

**Option 2: Full Version with AI/ML (Requires Python 3.11/3.12)**
```bash
# 1. Create virtual environment with Python 3.11 or 3.12
python3.11 -m venv .venv
source .venv/bin/activate  # On macOS/Linux

# 2. Install all dependencies
pip install -r requirements.txt

# 3. Run full simulation with AI protection
python main.py
```

**Option 3: MATLAB Simulation**
```matlab
% In MATLAB
cd matlab_simulation
dc_microgrid_simulation
```

### View Results
After running the simulation, check the `results/` directory for:
- `power_balance.png` - Power generation and consumption
- `battery_operation.png` - Battery SOC and charge/discharge
- `renewable_generation.png` - Renewable energy breakdown

### Configuration
Customize simulation parameters by editing `config/microgrid_config.yaml`:
- System voltage and capacity
- PV and wind turbine specifications
- Battery parameters
- Protection thresholds

📖 **Detailed documentation**: See [CODE_README.md](CODE_README.md) for complete setup instructions and API documentation.

---

## �📋 Overview

This research project addresses the critical challenges in integrating renewable energy sources into DC microgrids through AI-driven adaptive protection and control mechanisms. The project focuses on developing a comprehensive framework that ensures security, stability, and reliability in DC microgrid operations.

**Presenter:** Nivas D. Navghare (MIS NO. 712448007)  
**Guide:** Dr. Arti V. Tare  
**Institution:** COEP Technological University, Pune

## 🎯 Research Objectives

1. **Analyze Security and Stability**: Identify and address security and stability challenges in DC microgrids to enhance overall system reliability.

2. **AI-Enabled Protection Framework**: Develop a secure, AI-based framework to effectively protect DC microgrid operations against various threats and faults.

3. **Optimized Distributed Generation**: Enhance system resilience by optimizing the integration of distributed generation sources within the microgrid infrastructure.

4. **Simulation-Based Validation**: Validate the performance of proposed solutions using comprehensive simulation testing methodologies.

## 🔬 Research Scope

### Introduction to DC Microgrids

#### Emergence of DC Microgrids
- Integration of renewable sources (PV, wind turbines, BESS)
- Efficient energy management capabilities
- Modern power distribution solutions

#### Advantages
- **Reduced Conversion Losses**: Minimizes AC-DC conversion inefficiencies
- **Modularity**: Flexible and scalable system design
- **Improved Energy Efficiency**: Enhanced overall system performance
- **Direct Integration**: Native compatibility with renewable sources and modern loads

#### Applications
- Rural electrification programs
- Smart building infrastructure
- Data center power management
- Remote and off-grid installations
- Electric vehicle charging stations

#### Deployment Challenges
- Lack of universal standardization
- Complex protection coordination issues
- Harmonic distortion management
- Cybersecurity vulnerabilities
- System stability concerns

## 🔍 Research Gap

### Current Limitations

1. **Lack of Unified Framework**
   - No universal protection and control framework exists for diverse DC microgrid systems
   - Limited interoperability between different implementations

2. **Limited AI and ML Application**
   - Minimal use of AI/ML for cyber-resilience in DC microgrids
   - Underdeveloped intelligent fault detection systems

3. **Underdeveloped Adaptive Coordination**
   - Real-time adaptive relay coordination mechanisms need advancement
   - Insufficient dynamic response capabilities

4. **Need for Integrated Approaches**
   - Integration of optimization and protection strategies is essential
   - Holistic system design methodologies are lacking

## 💡 Motivation & Necessity

### Key Drivers

- **Renewable Integration Challenges**: Growing renewable energy adoption demands secure, reliable integration tailored to DC characteristics

- **Adaptive Fault Protection**: Traditional protection methods are inadequate for DC systems, requiring AI-driven strategies

- **Cybersecurity Concerns**: Microgrid digitalization introduces new cybersecurity risks requiring robust mitigation strategies

- **Standardization Requirements**: Lack of uniform interoperability standards complicates integration and scaling

## ⚠️ Problem Statement

The research addresses four critical challenges:

1. **Lack of Standardization**: Absence of universal standards impacts interoperability and safety
2. **Inadequate Protection**: Current protection mechanisms and cybersecurity measures are insufficient
3. **Intermittency Issues**: Renewable energy intermittency causes reliability and stability challenges
4. **Control System Limitations**: Existing systems lack adaptability to disturbances and dynamic changes

## 🛠️ Methodology

### Technical Approach

#### 1. Microgrid Modeling
- Integration of PV, wind, energy storage systems, and loads
- MATLAB/Simulink-based simulation environment
- Accurate system representation and analysis

#### 2. AI and ML Applications
- **Fault Detection**: Intelligent anomaly detection algorithms
- **Anomaly Prediction**: Predictive maintenance capabilities
- **Adaptive Relay Coordination**: Dynamic protection coordination

#### 3. Performance Validation
Key performance metrics:
- **THD (Total Harmonic Distortion)**: Power quality assessment
- **SAIFI (System Average Interruption Frequency Index)**: Reliability measurement
- **SAIDI (System Average Interruption Duration Index)**: Service quality indicator

## 🎯 Expected Outcomes

### Deliverables

1. **AI-Based Adaptive Control**
   - Advanced AI-driven protection and control systems
   - Enhanced operational efficiency

2. **Improved Power Quality**
   - Stable and reliable DC microgrid operation
   - Enhanced system resilience

3. **Enhanced Cybersecurity**
   - Robust protection against digital threats
   - Comprehensive vulnerability management

4. **Global Standardization Support**
   - Contributions to international standards development
   - Promotion of widespread DC microgrid adoption

## 📅 Project Timeline

| Phase | Activity | Duration |
|-------|----------|----------|
| Phase 1 | Literature Survey & Research Gaps | Jul 2025 - Sep 2025 |
| Phase 2 | Algorithm Selection & Development | Oct 2025 - Dec 2025 |
| Phase 3 | Simulation Execution | Jan 2026 - Mar 2026 |
| Phase 4 | Results Analysis | Apr 2026 - May 2026 |
| Phase 5 | Dissertation Writing & Submission | Jun 2026 - Jul 2026 |

## 📚 Literature Survey Summary

The research builds upon recent advances in DC microgrid technology:

### Key Areas Covered

1. **AI-Based Adaptive Protection** (Baba et al., 2024)
   - AI/ML algorithms for fault detection
   - Enhanced protection speed and accuracy

2. **Cybersecurity** (Sarangi et al., 2025)
   - Cyber-physical threat analysis
   - AI-driven anomaly detection frameworks

3. **Real-World Deployments** (Adegboyega et al., 2023)
   - Case studies and operational analysis
   - Economic feasibility assessment

4. **Power Quality & Standardization** (Kumar et al., 2024)
   - Harmonics modeling and mitigation
   - Voltage stability analysis

5. **Distributed Generation** (Thippeswamy et al., 2023)
   - DG configuration optimization
   - Performance improvement strategies

6. **Stochastic Optimization** (Dabbaghjamanesh et al., 2024)
   - Renewable uncertainty management
   - Security-constrained optimization

## 🔧 Tools & Technologies

- **Simulation Platform**: MATLAB/Simulink
- **AI/ML Frameworks**: Python-based machine learning libraries
- **Analysis Tools**: Power system analysis software
- **Version Control**: Git

## 📖 References

A comprehensive list of academic references is available in the [Report and Docs](./Report%20and%20Docs/) folder, including:

1. Baba, M., et al. (2024). AI-based adaptive protection for DC microgrids
2. Sarangi, R. R., et al. (2025). Cybersecurity vulnerabilities and AI-based monitoring
3. Adegboyega, A. W., et al. (2023). Real-world DC microgrid deployments
4. Kumar, D., et al. (2024). Power quality and standardization in DC microgrids
5. Thippeswamy, T. G. C., et al. (2023). Distributed generation integration
6. Dabbaghjamanesh, M., et al. (2024). Stochastic optimization for secure operation
7. Anand, S., et al. (2025). Review on distributed generation integration

*For complete reference list, see presentation materials.*

## 📁 Project Structure

```
Secure-Integration-of-Renewable-Energy-in-DC-Microgrid/
├── README.md                           # Project documentation
├── LICENSE                             # MIT License
└── Report and Docs/                    # Project reports and presentations
    ├── DC_Microgrid_Presentation.pdf   # Main presentation slides
    ├── Nivas_Navghare.pdf             # Presenter profile
    └── Slide xplain.pdf               # Detailed slide explanations
```

## 🤝 Contributing

This is an academic research project. For inquiries or collaboration opportunities, please contact:

- **Nivas D. Navghare**
- Email: nivas.navghare@gmail.com
- Mobile: +91-9762454630

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎓 Academic Context

This research is being conducted as part of a Master of Science in Engineering (MSE) program at COEP Technological University, Pune, under the guidance of Dr. Arti V. Tare.

## 🌟 Acknowledgments

- Dr. Arti V. Tare (Research Guide)
- COEP Technological University, Pune
- All researchers whose work contributed to this study

---

**Note**: This is an ongoing research project. Updates will be made as the research progresses through different phases.

*Last Updated: October 2025*
