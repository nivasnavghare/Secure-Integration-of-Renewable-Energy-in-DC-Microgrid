"""
Visualization utilities for results
"""

import matplotlib.pyplot as plt
import numpy as np
from typing import Dict
from pathlib import Path
import logging


class Visualizer:
    """Visualization tools for simulation results"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def plot_power_balance(self, results: Dict, save_path: str = 'results/power_balance.png'):
        """Plot power generation and consumption."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        time_hours = np.array(results['time']) / 3600
        
        ax.plot(time_hours, results['pv_power'], label='PV Generation', linewidth=2)
        ax.plot(time_hours, results['wind_power'], label='Wind Generation', linewidth=2)
        ax.plot(time_hours, results['total_load'], label='Total Load', linewidth=2, linestyle='--')
        ax.plot(time_hours, results['battery_power'], label='Battery Power', linewidth=2)
        
        ax.set_xlabel('Time (hours)', fontsize=12)
        ax.set_ylabel('Power (kW)', fontsize=12)
        ax.set_title('DC Microgrid Power Balance', fontsize=14, fontweight='bold')
        ax.legend(loc='best', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Power balance plot saved to {save_path}")
    
    def plot_battery_operation(self, results: Dict, save_path: str = 'results/battery_operation.png'):
        """Plot battery state of charge."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        time_hours = np.array(results['time']) / 3600
        
        # SOC plot
        ax1.plot(time_hours, np.array(results['battery_soc']) * 100, 
                linewidth=2, color='blue')
        ax1.axhline(y=20, color='r', linestyle='--', label='Min SOC')
        ax1.axhline(y=90, color='r', linestyle='--', label='Max SOC')
        ax1.set_ylabel('State of Charge (%)', fontsize=12)
        ax1.set_title('Battery Energy Storage System Operation', fontsize=14, fontweight='bold')
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        
        # Power plot
        ax2.plot(time_hours, results['battery_power'], linewidth=2, color='green')
        ax2.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
        ax2.set_xlabel('Time (hours)', fontsize=12)
        ax2.set_ylabel('Battery Power (kW)', fontsize=12)
        ax2.set_title('Positive: Charging, Negative: Discharging', fontsize=10, style='italic')
        ax2.grid(True, alpha=0.3)
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Battery operation plot saved to {save_path}")
    
    def plot_voltage_profile(self, results: Dict, save_path: str = 'results/voltage_profile.png'):
        """Plot voltage profile over time."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        time_hours = np.array(results['time']) / 3600
        voltage_pu = np.array(results['voltage']) / self.config['system']['voltage_level']
        
        ax.plot(time_hours, voltage_pu, linewidth=2, color='purple')
        ax.axhline(y=1.0, color='g', linestyle='--', label='Nominal Voltage')
        ax.axhline(y=0.85, color='r', linestyle='--', label='Min Threshold')
        ax.axhline(y=1.15, color='r', linestyle='--', label='Max Threshold')
        
        ax.set_xlabel('Time (hours)', fontsize=12)
        ax.set_ylabel('Voltage (per unit)', fontsize=12)
        ax.set_title('DC Bus Voltage Profile', fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Voltage profile plot saved to {save_path}")
    
    def plot_renewable_generation(self, results: Dict, save_path: str = 'results/renewable_generation.png'):
        """Plot renewable energy generation breakdown."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        total_pv = sum(results['pv_power'])
        total_wind = sum(results['wind_power'])
        
        labels = ['Solar PV', 'Wind Turbine']
        sizes = [total_pv, total_wind]
        colors = ['#FDB462', '#80B1D3']
        explode = (0.1, 0)
        
        ax.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=90)
        ax.set_title('Renewable Energy Generation Distribution', 
                    fontsize=14, fontweight='bold')
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"Renewable generation plot saved to {save_path}")
