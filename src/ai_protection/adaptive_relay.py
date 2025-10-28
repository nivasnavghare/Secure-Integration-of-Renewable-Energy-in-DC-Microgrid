"""
Adaptive Relay Coordination using Q-Learning

This module implements adaptive relay coordination for
optimal protection of DC microgrid using a simpler Q-learning approach.
"""

import numpy as np
from collections import defaultdict
import random
from typing import Dict, List, Tuple, Optional
import logging
import joblib


class AdaptiveRelayCoordinator:
    """Adaptive Relay Coordination using Q-Learning"""
    
    def __init__(self, config: Dict):
        """
        Initialize adaptive relay coordinator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.learning_rate = config.get('learning_rate', 0.1)
        self.discount_factor = config.get('discount_factor', 0.95)
        self.epsilon = config.get('epsilon', 0.1)  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        
        # State and action space
        self.state_features = [
            'voltage',
            'current',
            'power',
            'battery_soc',
            'fault_severity',
            'fault_location',
            'time_of_day',
            'load_priority'
        ]
        self.action_size = 4  # [trip_relay_1, trip_relay_2, adjust_setting, no_action]
        
        # Q-table using defaultdict for sparse storage
        self.q_table = defaultdict(lambda: np.zeros(self.action_size))
        
        self.logger = logging.getLogger(__name__)
    
    def discretize_state(self, state: np.ndarray) -> str:
        """
        Convert continuous state values to discrete buckets for Q-table.
        
        Args:
            state: Continuous state array
            
        Returns:
            Discretized state string key
        """
        # Define buckets for each feature
        buckets = [
            np.linspace(0, 1.5, 10),  # voltage (normalized)
            np.linspace(0, 2, 10),    # current (normalized)
            np.linspace(0, 2, 10),    # power (normalized)
            np.linspace(0, 1, 5),     # battery_soc
            np.linspace(0, 1, 3),     # fault_severity
            np.linspace(0, 1, 3),     # fault_location
            np.linspace(0, 1, 6),     # time_of_day
            np.linspace(0, 1, 3)      # load_priority
        ]
        
        # Digitize each feature
        discretized = []
        for value, bucket in zip(state.flatten(), buckets):
            idx = np.digitize(value, bucket)
            discretized.append(str(idx))
        
        return '_'.join(discretized)
    
    def get_state(self, system_data: Dict) -> np.ndarray:
        """
        Extract state from system data.
        
        Args:
            system_data: Current system state
            
        Returns:
            State vector
        """
        state = np.array([
            system_data.get('voltage', 380) / 380,  # Normalized voltage
            system_data.get('current', 0) / 100,    # Normalized current
            system_data.get('power', 0) / 100,      # Normalized power
            system_data.get('battery_soc', 0.5),
            system_data.get('fault_severity', 0),   # 0-1 scale
            system_data.get('fault_location', 0),   # 0-1 normalized
            system_data.get('time_of_day', 12) / 24,
            system_data.get('load_priority', 0.5)
        ])
        
        return state.reshape(1, -1)
    
    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        Select action using epsilon-greedy policy.
        
        Args:
            state: Current state
            training: Whether in training mode
            
        Returns:
            Selected action index
        """
        state_key = self.discretize_state(state)
        
        if training and random.random() < self.epsilon:
            # Exploration: random action
            return random.randrange(self.action_size)
        
        # Exploitation: best action from Q-table
        return np.argmax(self.q_table[state_key])
    
    def update_q_table(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray
    ):
        """
        Update Q-table using Q-learning update rule.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
        """
        state_key = self.discretize_state(state)
        next_state_key = self.discretize_state(next_state)
        
        # Q-learning update rule
        current_q = self.q_table[state_key][action]
        next_max_q = np.max(self.q_table[next_state_key])
        
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * next_max_q - current_q
        )
        
        self.q_table[state_key][action] = new_q
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def calculate_reward(
        self,
        action: int,
        system_state: Dict,
        fault_cleared: bool
    ) -> float:
        """
        Calculate reward for taken action.
        
        Args:
            action: Action taken
            system_state: System state after action
            fault_cleared: Whether fault was cleared
            
        Returns:
            Reward value
        """
        reward = 0.0
        
        # Positive reward for clearing fault
        if fault_cleared:
            reward += 100
        
        # Penalty for unnecessary trips
        if action in [0, 1] and not fault_cleared:
            reward -= 50
        
        # Reward for maintaining voltage stability
        voltage_pu = system_state.get('voltage', 380) / 380
        if 0.95 <= voltage_pu <= 1.05:
            reward += 10
        else:
            reward -= abs(voltage_pu - 1.0) * 20
        
        # Reward for protecting critical loads
        if system_state.get('critical_load_protected', True):
            reward += 20
        else:
            reward -= 100
        
        # Penalty for excessive relay operations
        relay_operations = system_state.get('relay_operations', 0)
        if relay_operations > 3:
            reward -= relay_operations * 10
        
        return reward
    
    def coordinate_relays(
        self,
        fault_data: Dict,
        system_state: Dict
    ) -> Dict:
        """
        Determine optimal relay coordination strategy.
        
        Args:
            fault_data: Fault information
            system_state: Current system state
            
        Returns:
            Relay coordination decisions
        """
        # Get current state
        state = self.get_state({**fault_data, **system_state})
        
        # Select action
        action = self.select_action(state, training=False)
        
        # Map action to relay commands
        action_map = {
            0: {'relay': 1, 'command': 'trip', 'time_delay': 0.05},
            1: {'relay': 2, 'command': 'trip', 'time_delay': 0.1},
            2: {'relay': 'all', 'command': 'adjust_settings', 'time_delay': 0},
            3: {'relay': None, 'command': 'monitor', 'time_delay': 0}
        }
        
        decision = action_map[action]
        decision['action_index'] = action
        decision['confidence'] = float(
            self.q_table[self.discretize_state(state)][action] /
            np.max(list(self.q_table.values())) if self.q_table else 0.5
        )
        
        self.logger.info(f"Relay coordination decision: {decision}")
        
        return decision
    
    def save_model(self, filepath: str):
        """Save Q-table to file."""
        # Convert defaultdict to regular dict for saving
        q_table_dict = dict(self.q_table)
        joblib.dump(q_table_dict, filepath)
        self.logger.info(f"Q-table saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load Q-table from file."""
        q_table_dict = joblib.load(filepath)
        # Convert back to defaultdict
        self.q_table = defaultdict(
            lambda: np.zeros(self.action_size),
            q_table_dict
        )
        self.logger.info(f"Q-table loaded from {filepath}")
