"""
Main Simulation Script for DC Microgrid

This script runs the complete DC microgrid simulation with
AI-based protection and cybersecurity features.

Author: Nivas D. Navghare
"""

import yaml
import numpy as np
import logging
from pathlib import Path
import matplotlib.pyplot as plt
from datetime import datetime

from src.microgrid_model import DCMicrogrid, PowerFlowAnalyzer
from src.ai_protection import FaultDetector, AnomalyDetector, AdaptiveRelayCoordinator
from src.utils import DataLogger, Visualizer, PerformanceMetrics


def setup_logging(config: dict):
    """Setup logging configuration."""
    log_level = config['logging']['level']
    log_file = config['logging']['log_file']
    
    # Create logs directory
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def load_configuration(config_path: str = 'config/microgrid_config.yaml') -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


def generate_synthetic_data(config: dict, duration: int = 3600) -> dict:
    """
    Generate synthetic environmental and load data for simulation.
    
    Args:
        config: System configuration
        duration: Simulation duration in seconds
        
    Returns:
        Dictionary containing time series data
    """
    time_steps = np.arange(0, duration, config['simulation']['output_interval'])
    n_steps = len(time_steps)
    
    # Solar irradiance (W/m²) - sinusoidal pattern
    hour_of_day = (time_steps / 3600) % 24
    irradiance = 1000 * np.maximum(0, np.sin(np.pi * (hour_of_day - 6) / 12))
    irradiance += np.random.normal(0, 50, n_steps)  # Add noise
    irradiance = np.maximum(0, irradiance)
    
    # Temperature (°C)
    temperature = 25 + 10 * np.sin(np.pi * (hour_of_day - 6) / 12)
    temperature += np.random.normal(0, 2, n_steps)
    
    # Wind speed (m/s)
    wind_speed = 8 + 4 * np.sin(2 * np.pi * hour_of_day / 24)
    wind_speed += np.random.normal(0, 1, n_steps)
    wind_speed = np.maximum(0, wind_speed)
    
    return {
        'time': time_steps,
        'irradiance': irradiance,
        'temperature': temperature,
        'wind_speed': wind_speed
    }


def run_simulation(config: dict):
    """
    Run the main DC microgrid simulation.
    
    Args:
        config: System configuration
    """
    logger = logging.getLogger(__name__)
    logger.info("Starting DC Microgrid Simulation")
    
    # Initialize system
    microgrid = DCMicrogrid(config)
    power_flow_analyzer = PowerFlowAnalyzer(config['system']['voltage_level'])
    
    # Initialize AI components
    if config['protection']['ai_protection_enabled']:
        fault_detector = FaultDetector(config['ai_ml']['fault_detection'])
        anomaly_detector = AnomalyDetector(config['ai_ml']['anomaly_detection'])
        relay_coordinator = AdaptiveRelayCoordinator(config['ai_ml']['adaptive_control'])
        logger.info("AI protection systems initialized")
    
    # Generate simulation data
    sim_data = generate_synthetic_data(config, config['system']['simulation_time'])
    
    # Data logger
    data_logger = DataLogger()
    
    # Simulation loop
    logger.info(f"Running simulation for {config['system']['simulation_time']} seconds")
    
    results = {
        'time': [],
        'pv_power': [],
        'wind_power': [],
        'battery_power': [],
        'battery_soc': [],
        'total_load': [],
        'net_power': [],
        'voltage': [],
        'faults_detected': [],
        'anomalies_detected': []
    }
    
    dt = config['simulation']['output_interval'] / 3600  # Convert to hours
    
    for i, t in enumerate(sim_data['time']):
        # Calculate power balance
        power_balance = microgrid.calculate_power_balance(
            irradiance=sim_data['irradiance'][i],
            temperature=sim_data['temperature'][i],
            wind_speed=sim_data['wind_speed'][i],
            dt=dt
        )
        
        # Check system stability
        stability = microgrid.check_system_stability(power_balance)
        
        # AI-based fault detection
        if config['protection']['ai_protection_enabled'] and i > 100:
            # Prepare data for fault detection
            recent_data = np.column_stack([
                results['voltage'][-100:],
                [power_balance['total_load']] * min(100, len(results['voltage'])),
                [power_balance['net_power']] * min(100, len(results['voltage']))
            ])
            
            if len(recent_data) == 100:
                fault_result = fault_detector.detect_fault(recent_data)
                results['faults_detected'].append(fault_result['fault_detected'])
                
                if fault_result['fault_detected']:
                    logger.warning(
                        f"Fault detected at t={t}s: {fault_result['fault_type']} "
                        f"(confidence: {fault_result['confidence']:.2f})"
                    )
        else:
            results['faults_detected'].append(False)
        
        # Store results
        results['time'].append(t)
        results['pv_power'].append(power_balance['pv_power'])
        results['wind_power'].append(power_balance['wind_power'])
        results['battery_power'].append(power_balance['battery_power'])
        results['battery_soc'].append(power_balance['battery_soc'])
        results['total_load'].append(power_balance['total_load'])
        results['net_power'].append(power_balance['net_power'])
        results['voltage'].append(power_balance['voltage'])
        
        # Log progress
        if i % 100 == 0:
            logger.info(
                f"t={t}s: PV={power_balance['pv_power']:.2f}kW, "
                f"Wind={power_balance['wind_power']:.2f}kW, "
                f"Load={power_balance['total_load']:.2f}kW, "
                f"SOC={power_balance['battery_soc']:.2%}"
            )
    
    # Calculate performance metrics
    logger.info("Calculating performance metrics")
    metrics = PerformanceMetrics.calculate_all_metrics(results, config)
    
    # Print summary
    print("\n" + "="*60)
    print("SIMULATION RESULTS SUMMARY")
    print("="*60)
    print(f"Total Energy Generated: {metrics['total_generation']:.2f} kWh")
    print(f"Total Energy Consumed: {metrics['total_consumption']:.2f} kWh")
    print(f"Average Battery SOC: {metrics['avg_battery_soc']:.2%}")
    print(f"System Efficiency: {metrics['system_efficiency']:.2%}")
    print(f"Renewable Penetration: {metrics['renewable_penetration']:.2%}")
    
    if 'thd' in metrics:
        print(f"Average THD: {metrics['thd']:.2f}%")
    
    reliability = microgrid.calculate_reliability_metrics()
    print(f"\nReliability Metrics:")
    print(f"SAIFI: {reliability['SAIFI']:.4f}")
    print(f"SAIDI: {reliability['SAIDI']:.4f} hours")
    print("="*60 + "\n")
    
    # Visualize results
    logger.info("Generating visualizations")
    visualizer = Visualizer(config)
    visualizer.plot_power_balance(results)
    visualizer.plot_battery_operation(results)
    visualizer.plot_voltage_profile(results)
    
    # Save results
    data_logger.save_results(results, metrics, 'results/simulation_results.h5')
    logger.info("Results saved to results/simulation_results.h5")
    
    logger.info("Simulation completed successfully")
    
    return results, metrics


def main():
    """Main entry point."""
    # Load configuration
    config = load_configuration()
    
    # Setup logging
    setup_logging(config)
    
    # Run simulation
    try:
        results, metrics = run_simulation(config)
        print("\n✓ Simulation completed successfully!")
        print(f"Check 'results/' directory for output files")
        print(f"Check '{config['logging']['log_file']}' for detailed logs")
        
    except Exception as e:
        logging.error(f"Simulation failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
