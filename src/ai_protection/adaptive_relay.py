"""
Adaptive Relay Coordination using Reinforcement Learning

This module implements adaptive relay coordination for
optimal protection of DC microgrid.
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from collections import deque
import random
from typing import Dict, List, Tuple, Optional
import logging


class AdaptiveRelayCoordinator:
    """Adaptive Relay Coordination using Deep Q-Network (DQN)"""
    
    def __init__(self, config: Dict):
        """
        Initialize adaptive relay coordinator.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.learning_rate = config.get('learning_rate', 0.001)
        self.discount_factor = config.get('discount_factor', 0.95)
        self.epsilon = config.get('epsilon', 0.1)  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        
        # State and action space
        self.state_size = 8  # [V, I, P, SOC, fault_type, location, time, priority]
        self.action_size = 4  # [trip_relay_1, trip_relay_2, adjust_setting, no_action]
        
        # Experience replay
        self.memory = deque(maxlen=2000)
        self.batch_size = 32
        
        # Models
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()
        
        self.logger = logging.getLogger(__name__)
        
    def _build_model(self) -> keras.Model:
        """
        Build Deep Q-Network model.
        
        Returns:
            Keras model
        """
        model = keras.Sequential([
            keras.layers.Dense(64, input_dim=self.state_size, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(self.action_size, activation='linear')
        ])
        
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=self.learning_rate),
            loss='mse'
        )
        
        return model
    
    def update_target_model(self):
        """Update target model with current model weights."""
        self.target_model.set_weights(self.model.get_weights())
    
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
        if training and random.random() < self.epsilon:
            # Exploration: random action
            return random.randrange(self.action_size)
        
        # Exploitation: best action from Q-network
        q_values = self.model.predict(state, verbose=0)
        return np.argmax(q_values[0])
    
    def remember(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool
    ):
        """
        Store experience in replay memory.
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
        """
        self.memory.append((state, action, reward, next_state, done))
    
    def replay(self):
        """Train the model using experience replay."""
        if len(self.memory) < self.batch_size:
            return
        
        # Sample mini-batch
        minibatch = random.sample(self.memory, self.batch_size)
        
        states = np.vstack([sample[0] for sample in minibatch])
        actions = np.array([sample[1] for sample in minibatch])
        rewards = np.array([sample[2] for sample in minibatch])
        next_states = np.vstack([sample[3] for sample in minibatch])
        dones = np.array([sample[4] for sample in minibatch])
        
        # Current Q-values
        current_q = self.model.predict(states, verbose=0)
        
        # Target Q-values
        next_q = self.target_model.predict(next_states, verbose=0)
        
        # Update Q-values
        for i in range(self.batch_size):
            if dones[i]:
                current_q[i][actions[i]] = rewards[i]
            else:
                current_q[i][actions[i]] = rewards[i] + \
                    self.discount_factor * np.max(next_q[i])
        
        # Train model
        self.model.fit(states, current_q, epochs=1, verbose=0)
        
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
        decision['confidence'] = float(np.max(
            self.model.predict(state, verbose=0)[0]
        ))
        
        self.logger.info(f"Relay coordination decision: {decision}")
        
        return decision
    
    def save_model(self, filepath: str):
        """Save model to file."""
        self.model.save(filepath)
        self.logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load model from file."""
        self.model = keras.models.load_model(filepath)
        self.update_target_model()
        self.logger.info(f"Model loaded from {filepath}")
