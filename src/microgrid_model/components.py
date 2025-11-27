"""
DC Microgrid Component Models

This module contains models for different microgrid components:
- Photovoltaic (PV) System
- Wind Turbine
- Battery Energy Storage System (BESS)
- Loads
"""

import numpy as np
from typing import Dict, Optional, Tuple


class PVSystem:
    """Photovoltaic System Model"""
    
    def __init__(self, config: Dict):
        """
        Initialize PV system.
        
        Args:
            config: Configuration dictionary containing PV parameters
        """
        self.rated_power = config.get('rated_power', 50)  # kW - as per FINAL_PROJECT_REPORT.md
        self.efficiency = config.get('efficiency', 0.18)
        self.temp_coefficient = config.get('temperature_coefficient', -0.004)
        self.panel_area = config.get('panel_area', 278)  # m² - calculated for 50kW
        self.reference_temp = 25  # °C
        
    def calculate_power(self, irradiance: float, temperature: float) -> float:
        """
        Calculate PV power output.
        
        Args:
            irradiance: Solar irradiance in W/m²
            temperature: Panel temperature in °C
            
        Returns:
            Power output in kW
        """
        # Temperature effect
        temp_factor = 1 + self.temp_coefficient * (temperature - self.reference_temp)
        
        # Power calculation
        power = (irradiance / 1000) * self.panel_area * self.efficiency * temp_factor
        
        # Limit to rated power
        return min(power, self.rated_power)
    
    def get_mppt_voltage(self, irradiance: float) -> float:
        """
        Calculate Maximum Power Point Tracking voltage.
        
        Args:
            irradiance: Solar irradiance in W/m²
            
        Returns:
            MPPT voltage in V
        """
        # Simplified MPPT voltage calculation - 400V DC bus
        return 400 * (1 + 0.05 * np.log(irradiance / 1000))


class WindTurbine:
    """Wind Turbine Generator Model"""
    
    def __init__(self, config: Dict):
        """
        Initialize wind turbine.
        
        Args:
            config: Configuration dictionary containing wind turbine parameters
        """
        self.rated_power = config.get('rated_power', 30)  # kW - as per FINAL_PROJECT_REPORT.md
        self.cut_in_speed = config.get('cut_in_speed', 3)  # m/s
        self.rated_speed = config.get('rated_speed', 12)  # m/s
        self.cut_out_speed = config.get('cut_out_speed', 25)  # m/s
        self.rotor_diameter = config.get('rotor_diameter', 8)  # m - as per documentation
        self.air_density = 1.225  # kg/m³
        self.power_coefficient = 0.4
        
    def calculate_power(self, wind_speed: float) -> float:
        """
        Calculate wind turbine power output.
        
        Args:
            wind_speed: Wind speed in m/s
            
        Returns:
            Power output in kW
        """
        if wind_speed < self.cut_in_speed or wind_speed > self.cut_out_speed:
            return 0.0
        
        if wind_speed >= self.rated_speed:
            return self.rated_power
        
        # Power calculation using wind speed
        swept_area = np.pi * (self.rotor_diameter / 2) ** 2
        power = 0.5 * self.air_density * swept_area * self.power_coefficient * (wind_speed ** 3)
        power_kw = power / 1000  # Convert to kW
        
        return min(power_kw, self.rated_power)
    
    def get_tip_speed_ratio(self, wind_speed: float, rotor_speed: float) -> float:
        """
        Calculate tip speed ratio.
        
        Args:
            wind_speed: Wind speed in m/s
            rotor_speed: Rotor angular velocity in rad/s
            
        Returns:
            Tip speed ratio
        """
        if wind_speed == 0:
            return 0
        return (rotor_speed * self.rotor_diameter / 2) / wind_speed


class BatteryStorage:
    """Battery Energy Storage System Model"""
    
    def __init__(self, config: Dict):
        """
        Initialize battery storage system.
        
        Args:
            config: Configuration dictionary containing battery parameters
        """
        self.capacity = config.get('capacity', 100)  # kWh - as per FINAL_PROJECT_REPORT.md
        self.max_charge_rate = config.get('max_charge_rate', 50)  # kW - 0.5C rate
        self.max_discharge_rate = config.get('max_discharge_rate', 50)  # kW - 0.5C rate
        self.efficiency = config.get('efficiency', 0.90)  # as per documentation
        self.min_soc = config.get('min_soc', 0.2)  # as per documentation
        self.max_soc = config.get('max_soc', 0.95)  # as per documentation
        self.soc = config.get('initial_soc', 0.5)  # State of Charge
        
        # Battery degradation parameters
        self.cycle_count = 0
        self.capacity_fade_rate = 0.0001  # per cycle
        
    def charge(self, power: float, dt: float) -> Tuple[float, float]:
        """
        Charge the battery.
        
        Args:
            power: Charging power in kW
            dt: Time step in hours
            
        Returns:
            Tuple of (actual_power_charged, new_soc)
        """
        # Limit charging power
        actual_power = min(power, self.max_charge_rate)
        
        # Calculate energy and new SOC
        energy = actual_power * dt * self.efficiency
        new_soc = self.soc + (energy / self.capacity)
        
        # Limit SOC
        if new_soc > self.max_soc:
            actual_power = (self.max_soc - self.soc) * self.capacity / (dt * self.efficiency)
            new_soc = self.max_soc
        
        self.soc = new_soc
        return actual_power, self.soc
    
    def discharge(self, power: float, dt: float) -> Tuple[float, float]:
        """
        Discharge the battery.
        
        Args:
            power: Discharging power in kW
            dt: Time step in hours
            
        Returns:
            Tuple of (actual_power_discharged, new_soc)
        """
        # Limit discharging power
        actual_power = min(power, self.max_discharge_rate)
        
        # Calculate energy and new SOC
        energy = actual_power * dt / self.efficiency
        new_soc = self.soc - (energy / self.capacity)
        
        # Limit SOC
        if new_soc < self.min_soc:
            actual_power = (self.soc - self.min_soc) * self.capacity * self.efficiency / dt
            new_soc = self.min_soc
        
        self.soc = new_soc
        self.cycle_count += dt / 2  # Half cycle
        
        return actual_power, self.soc
    
    def get_available_capacity(self) -> float:
        """
        Get available energy capacity.
        
        Returns:
            Available energy in kWh
        """
        return (self.soc - self.min_soc) * self.capacity
    
    def get_remaining_capacity(self) -> float:
        """
        Get remaining charging capacity.
        
        Returns:
            Remaining capacity in kWh
        """
        return (self.max_soc - self.soc) * self.capacity


class Load:
    """Load Model"""
    
    def __init__(self, config: Dict):
        """
        Initialize load.
        
        Args:
            config: Configuration dictionary containing load parameters
        """
        self.power = config.get('power', 50)  # kW
        self.priority = config.get('priority', 2)  # 1=critical, 2=non-critical
        self.power_factor = config.get('power_factor', 0.95)
        self.voltage_dependency = config.get('voltage_dependency', 1.5)
        
    def calculate_power(self, voltage: float, base_voltage: float = 400) -> float:
        """
        Calculate load power considering voltage dependency.
        
        Args:
            voltage: Actual voltage in V
            base_voltage: Base voltage in V
            
        Returns:
            Actual power consumption in kW
        """
        voltage_ratio = voltage / base_voltage
        return self.power * (voltage_ratio ** self.voltage_dependency)
    
    def get_current(self, voltage: float) -> float:
        """
        Calculate load current.
        
        Args:
            voltage: Voltage in V
            
        Returns:
            Current in A
        """
        if voltage == 0:
            return 0
        return (self.power * 1000) / voltage  # Convert kW to W
    
    def is_critical(self) -> bool:
        """
        Check if load is critical.
        
        Returns:
            True if critical load
        """
        return self.priority == 1
