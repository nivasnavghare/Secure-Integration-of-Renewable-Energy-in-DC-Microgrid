"""
DC Microgrid Network Model

This module implements the complete DC microgrid network integration
and power balance calculations.
"""

import numpy as np
from typing import Dict, List, Optional
import logging
from .components import PVSystem, WindTurbine, BatteryStorage, Load


class DCMicrogrid:
    """Complete DC Microgrid System Model"""
    
    def __init__(self, config: Dict):
        """
        Initialize DC microgrid system.
        
        Args:
            config: Complete system configuration
        """
        self.config = config
        self.voltage_level = config['system']['voltage_level']
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.pv_system = None
        self.wind_turbine = None
        self.battery = None
        self.loads = {}
        
        self._initialize_components()
        
        # System state
        self.current_voltage = self.voltage_level
        self.current_frequency = config['system']['frequency']
        self.grid_connected = False
        
        # Metrics tracking
        self.metrics = {
            'energy_generated': 0,
            'energy_consumed': 0,
            'energy_stored': 0,
            'energy_losses': 0,
            'reliability_events': []
        }
        
    def _initialize_components(self):
        """Initialize all microgrid components from configuration."""
        # PV System
        if self.config['photovoltaic']['enabled']:
            self.pv_system = PVSystem(self.config['photovoltaic'])
            self.logger.info("PV System initialized")
        
        # Wind Turbine
        if self.config['wind_turbine']['enabled']:
            self.wind_turbine = WindTurbine(self.config['wind_turbine'])
            self.logger.info("Wind Turbine initialized")
        
        # Battery Storage
        if self.config['bess']['enabled']:
            self.battery = BatteryStorage(self.config['bess'])
            self.logger.info("Battery Storage initialized")
        
        # Loads
        for load_name, load_config in self.config['loads'].items():
            self.loads[load_name] = Load(load_config)
            self.logger.info(f"Load '{load_name}' initialized")
    
    def calculate_power_balance(
        self,
        irradiance: float,
        temperature: float,
        wind_speed: float,
        dt: float = 1.0
    ) -> Dict:
        """
        Calculate power balance in the microgrid.
        
        Args:
            irradiance: Solar irradiance in W/m²
            temperature: Temperature in °C
            wind_speed: Wind speed in m/s
            dt: Time step in hours
            
        Returns:
            Dictionary containing power balance results
        """
        # Generation
        pv_power = 0
        if self.pv_system:
            pv_power = self.pv_system.calculate_power(irradiance, temperature)
        
        wind_power = 0
        if self.wind_turbine:
            wind_power = self.wind_turbine.calculate_power(wind_speed)
        
        total_generation = pv_power + wind_power
        
        # Load demand
        total_load = sum(
            load.calculate_power(self.current_voltage, self.voltage_level)
            for load in self.loads.values()
        )
        
        # Power balance
        power_deficit = total_load - total_generation
        
        # Battery operation
        battery_power = 0
        battery_soc = 0
        
        if self.battery:
            if power_deficit > 0:  # Need to discharge
                battery_power, battery_soc = self.battery.discharge(power_deficit, dt)
            elif power_deficit < 0:  # Can charge
                battery_power, battery_soc = self.battery.charge(-power_deficit, dt)
            else:
                battery_soc = self.battery.soc
        
        # Calculate net power (positive = surplus, negative = deficit)
        net_power = total_generation + battery_power - total_load
        
        # Update metrics
        self.metrics['energy_generated'] += total_generation * dt
        self.metrics['energy_consumed'] += total_load * dt
        
        return {
            'pv_power': pv_power,
            'wind_power': wind_power,
            'total_generation': total_generation,
            'total_load': total_load,
            'battery_power': battery_power,
            'battery_soc': battery_soc,
            'net_power': net_power,
            'voltage': self.current_voltage,
            'power_deficit': power_deficit
        }
    
    def check_system_stability(self, power_balance: Dict) -> Dict:
        """
        Check system stability and protection requirements.
        
        Args:
            power_balance: Power balance results
            
        Returns:
            Dictionary containing stability metrics
        """
        protection = self.config['protection']
        
        # Voltage check
        voltage_pu = self.current_voltage / self.voltage_level
        undervoltage = voltage_pu < protection['undervoltage_threshold']
        overvoltage = voltage_pu > protection['overvoltage_threshold']
        
        # Current check (simplified)
        total_current = abs(power_balance['net_power'] * 1000 / self.current_voltage)
        rated_current = 100  # Assumed rated current in A
        overcurrent = total_current > (rated_current * protection['overcurrent_threshold'])
        
        # Stability assessment
        stable = not (undervoltage or overvoltage or overcurrent)
        
        return {
            'stable': stable,
            'voltage_pu': voltage_pu,
            'undervoltage': undervoltage,
            'overvoltage': overvoltage,
            'overcurrent': overcurrent,
            'total_current': total_current
        }
    
    def calculate_reliability_metrics(self) -> Dict:
        """
        Calculate system reliability metrics.
        
        Returns:
            Dictionary containing SAIFI and SAIDI metrics
        """
        events = self.metrics['reliability_events']
        
        if not events:
            return {
                'SAIFI': 0,  # System Average Interruption Frequency Index
                'SAIDI': 0,  # System Average Interruption Duration Index
                'CAIDI': 0   # Customer Average Interruption Duration Index
            }
        
        total_customers = len(self.loads)
        total_interruptions = len(events)
        total_duration = sum(event['duration'] for event in events)
        
        SAIFI = total_interruptions / total_customers if total_customers > 0 else 0
        SAIDI = total_duration / total_customers if total_customers > 0 else 0
        CAIDI = total_duration / total_interruptions if total_interruptions > 0 else 0
        
        return {
            'SAIFI': SAIFI,
            'SAIDI': SAIDI,
            'CAIDI': CAIDI
        }
    
    def get_system_state(self) -> Dict:
        """
        Get current system state.
        
        Returns:
            Dictionary containing complete system state
        """
        return {
            'voltage': self.current_voltage,
            'frequency': self.current_frequency,
            'battery_soc': self.battery.soc if self.battery else 0,
            'grid_connected': self.grid_connected,
            'metrics': self.metrics
        }
    
    def reset_metrics(self):
        """Reset all metrics to initial state."""
        self.metrics = {
            'energy_generated': 0,
            'energy_consumed': 0,
            'energy_stored': 0,
            'energy_losses': 0,
            'reliability_events': []
        }
