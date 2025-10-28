"""
Power Flow Analysis for DC Microgrid

This module implements power flow calculations and analysis
for DC microgrid systems.
"""

import numpy as np
from typing import Dict, List, Tuple
import logging


class PowerFlowAnalyzer:
    """DC Power Flow Analyzer"""
    
    def __init__(self, voltage_base: float = 380):
        """
        Initialize power flow analyzer.
        
        Args:
            voltage_base: Base voltage in V
        """
        self.voltage_base = voltage_base
        self.logger = logging.getLogger(__name__)
        
    def calculate_dc_power_flow(
        self,
        voltages: np.ndarray,
        admittance_matrix: np.ndarray,
        power_injections: np.ndarray,
        max_iterations: int = 100,
        tolerance: float = 1e-6
    ) -> Tuple[np.ndarray, bool]:
        """
        Calculate DC power flow using Newton-Raphson method.
        
        Args:
            voltages: Initial voltage guess
            admittance_matrix: System admittance matrix
            power_injections: Power injections at each bus
            max_iterations: Maximum iterations
            tolerance: Convergence tolerance
            
        Returns:
            Tuple of (final voltages, convergence status)
        """
        V = voltages.copy()
        n_buses = len(V)
        
        for iteration in range(max_iterations):
            # Calculate power mismatch
            P_calc = np.zeros(n_buses)
            for i in range(n_buses):
                for j in range(n_buses):
                    P_calc[i] += admittance_matrix[i, j] * (V[i] - V[j])
            
            mismatch = power_injections - P_calc
            
            # Check convergence
            if np.max(np.abs(mismatch)) < tolerance:
                self.logger.info(f"Power flow converged in {iteration} iterations")
                return V, True
            
            # Update voltages (simplified Newton-Raphson)
            jacobian = self._calculate_jacobian(admittance_matrix, V)
            delta_V = np.linalg.solve(jacobian, mismatch)
            V += delta_V
        
        self.logger.warning("Power flow did not converge")
        return V, False
    
    def _calculate_jacobian(
        self,
        admittance_matrix: np.ndarray,
        voltages: np.ndarray
    ) -> np.ndarray:
        """
        Calculate Jacobian matrix for Newton-Raphson.
        
        Args:
            admittance_matrix: System admittance matrix
            voltages: Current voltage vector
            
        Returns:
            Jacobian matrix
        """
        n = len(voltages)
        jacobian = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i == j:
                    jacobian[i, j] = sum(admittance_matrix[i, :])
                else:
                    jacobian[i, j] = -admittance_matrix[i, j]
        
        return jacobian
    
    def calculate_line_losses(
        self,
        voltages: np.ndarray,
        admittance_matrix: np.ndarray
    ) -> Dict:
        """
        Calculate power losses in transmission lines.
        
        Args:
            voltages: Voltage at each bus
            admittance_matrix: System admittance matrix
            
        Returns:
            Dictionary containing loss information
        """
        n_buses = len(voltages)
        total_losses = 0
        line_losses = {}
        
        for i in range(n_buses):
            for j in range(i + 1, n_buses):
                if admittance_matrix[i, j] != 0:
                    V_diff = voltages[i] - voltages[j]
                    loss = admittance_matrix[i, j] * (V_diff ** 2)
                    total_losses += loss
                    line_losses[f"line_{i}_{j}"] = loss
        
        return {
            'total_losses': total_losses,
            'line_losses': line_losses,
            'loss_percentage': (total_losses / sum(voltages ** 2)) * 100
        }
    
    def calculate_thd(self, signal: np.ndarray, fundamental_freq: float) -> float:
        """
        Calculate Total Harmonic Distortion.
        
        Args:
            signal: Time-domain signal
            fundamental_freq: Fundamental frequency
            
        Returns:
            THD in percentage
        """
        # FFT of signal
        fft_signal = np.fft.fft(signal)
        fft_magnitude = np.abs(fft_signal)
        
        # Fundamental component
        fundamental = fft_magnitude[1]
        
        # Harmonic components
        harmonics = fft_magnitude[2:20]  # Up to 20th harmonic
        
        # THD calculation
        if fundamental == 0:
            return 0
        
        thd = np.sqrt(np.sum(harmonics ** 2)) / fundamental * 100
        
        return thd
    
    def analyze_voltage_stability(
        self,
        voltages: np.ndarray,
        power_injections: np.ndarray
    ) -> Dict:
        """
        Analyze voltage stability margins.
        
        Args:
            voltages: Bus voltages
            power_injections: Power injections
            
        Returns:
            Stability analysis results
        """
        voltage_pu = voltages / self.voltage_base
        
        # Voltage deviation
        voltage_deviation = np.abs(voltage_pu - 1.0)
        max_deviation = np.max(voltage_deviation)
        
        # Stability margin
        margin = 1.0 - max_deviation
        
        # Voltage sensitivity
        dV_dP = np.gradient(voltages) / np.gradient(power_injections)
        
        return {
            'voltage_pu': voltage_pu,
            'max_deviation': max_deviation,
            'stability_margin': margin,
            'voltage_sensitivity': dV_dP,
            'stable': margin > 0.1  # 10% margin threshold
        }
