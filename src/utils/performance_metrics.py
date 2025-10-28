"""
Performance metrics calculation
"""

import numpy as np
from typing import Dict


class PerformanceMetrics:
    """Calculate various performance metrics for the microgrid"""
    
    @staticmethod
    def calculate_all_metrics(results: Dict, config: Dict) -> Dict:
        """
        Calculate all performance metrics.
        
        Args:
            results: Simulation results
            config: System configuration
            
        Returns:
            Dictionary of metrics
        """
        dt = config['simulation']['output_interval'] / 3600  # hours
        
        # Energy metrics
        total_generation = (
            sum(results['pv_power']) + sum(results['wind_power'])
        ) * dt
        total_consumption = sum(results['total_load']) * dt
        
        # Battery metrics
        avg_battery_soc = np.mean(results['battery_soc'])
        battery_cycles = PerformanceMetrics._calculate_battery_cycles(
            results['battery_soc']
        )
        
        # Efficiency
        system_efficiency = total_consumption / total_generation if total_generation > 0 else 0
        
        # Renewable penetration
        renewable_penetration = total_generation / total_consumption if total_consumption > 0 else 0
        
        # Voltage quality
        voltage_pu = np.array(results['voltage']) / config['system']['voltage_level']
        voltage_deviation = np.std(voltage_pu)
        voltage_regulation = (np.max(voltage_pu) - np.min(voltage_pu)) / np.mean(voltage_pu) * 100
        
        # Power quality
        thd = PerformanceMetrics._estimate_thd(results['net_power'])
        
        return {
            'total_generation': total_generation,
            'total_consumption': total_consumption,
            'avg_battery_soc': avg_battery_soc,
            'battery_cycles': battery_cycles,
            'system_efficiency': system_efficiency,
            'renewable_penetration': renewable_penetration,
            'voltage_deviation': voltage_deviation,
            'voltage_regulation': voltage_regulation,
            'thd': thd
        }
    
    @staticmethod
    def _calculate_battery_cycles(soc_data: list) -> float:
        """
        Calculate equivalent battery cycles.
        
        Args:
            soc_data: State of charge time series
            
        Returns:
            Number of equivalent cycles
        """
        # Simple cycle counting: sum of absolute SOC changes
        soc_array = np.array(soc_data)
        soc_changes = np.abs(np.diff(soc_array))
        total_cycles = np.sum(soc_changes) / 2  # Full cycle = 2 half cycles
        
        return total_cycles
    
    @staticmethod
    def _estimate_thd(power_data: list) -> float:
        """
        Estimate Total Harmonic Distortion.
        
        Args:
            power_data: Power time series
            
        Returns:
            Estimated THD percentage
        """
        # Simplified THD estimation using FFT
        power_array = np.array(power_data)
        
        if len(power_array) < 10:
            return 0.0
        
        # FFT
        fft_result = np.fft.fft(power_array)
        fft_magnitude = np.abs(fft_result)
        
        # Fundamental (assume first harmonic)
        fundamental = fft_magnitude[1]
        
        # Harmonics (2nd to 10th)
        harmonics = fft_magnitude[2:11]
        
        if fundamental == 0:
            return 0.0
        
        thd = np.sqrt(np.sum(harmonics**2)) / fundamental * 100
        
        return min(thd, 100)  # Cap at 100%
