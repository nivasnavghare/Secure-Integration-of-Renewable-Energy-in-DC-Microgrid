"""
AI-based Fault Detection System

This module implements machine learning models for real-time
fault detection in DC microgrids using scikit-learn.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Optional
import logging
import joblib


class FaultDetector:
    """AI-based Fault Detection using Random Forest"""
    
    def __init__(self, config: Dict):
        """
        Initialize fault detector.
        
        Args:
            config: Configuration dictionary for fault detection
        """
        self.config = config
        self.input_features = config.get('input_features', ['voltage', 'current', 'power'])
        self.sequence_length = config.get('sequence_length', 100)
        self.confidence_threshold = config.get('confidence_threshold', 0.85)
        
        self.model = None
        self.scaler = StandardScaler()
        self.logger = logging.getLogger(__name__)
        
        # Fault types
        self.fault_types = [
            'no_fault',
            'short_circuit',
            'open_circuit',
            'ground_fault',
            'overcurrent',
            'undervoltage',
            'overvoltage'
        ]
        
        self._build_model()
        
    def _build_model(self):
        """Build and pre-train Random Forest-based fault detection model."""
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )

        # Create synthetic training data for demonstration
        n_samples = 1000
        
        # Four features: voltage mean, voltage std, current mean, current std
        n_features = 4
        
        # Generate normal operation data
        normal_data = np.random.randn(n_samples // 2, n_features)
        normal_data[:, 0] = 1.0 + 0.05 * normal_data[:, 0]  # Voltage mean around 1.0 pu
        normal_data[:, 1] = 0.02 + 0.01 * abs(normal_data[:, 1])  # Small voltage variation
        normal_data[:, 2] = 0.8 + 0.1 * normal_data[:, 2]  # Current mean around 0.8 pu
        normal_data[:, 3] = 0.05 + 0.02 * abs(normal_data[:, 3])  # Small current variation
        normal_labels = np.zeros(n_samples // 2, dtype=int)  # 0 = no_fault

        # Generate fault data
        fault_data = []
        fault_labels = []
        
        for fault_type in range(1, len(self.fault_types)):
            n_fault_samples = n_samples // (2 * (len(self.fault_types) - 1))
            fault = normal_data[:n_fault_samples].copy()
            
            # Add fault characteristics
            if fault_type == 1:  # short_circuit
                fault[:, 0] *= 3  # Voltage spike
                fault[:, 1] *= 5  # Current spike
            elif fault_type == 2:  # open_circuit
                fault[:, 0] *= 0.1  # Voltage drop
                fault[:, 1] *= 0.1  # Current drop
            elif fault_type == 3:  # ground_fault
                fault[:, 0] *= 0.5  # Voltage drop
                fault[:, 1] *= 2   # Current increase
            elif fault_type == 4:  # overcurrent
                fault[:, 1] *= 4   # Current spike
            elif fault_type == 5:  # undervoltage
                fault[:, 0] *= 0.7  # Voltage drop
            elif fault_type == 6:  # overvoltage
                fault[:, 0] *= 1.3  # Voltage spike

            fault_data.append(fault)
            fault_labels.extend([fault_type] * n_fault_samples)

        # Combine data
        X = np.vstack([normal_data] + fault_data)
        y = np.concatenate([normal_labels, fault_labels])

        # Shuffle data
        idx = np.random.permutation(len(X))
        X = X[idx]
        y = y[idx]

        # Pre-train the model
        self.model.fit(X, y)
        
        self.logger.info("Random Forest fault detection model built and pre-trained")
        
    def preprocess_data(self, data: np.ndarray) -> np.ndarray:
        """
        Preprocess input data for model.
        
        Args:
            data: Raw input data
            
        Returns:
            Preprocessed data
        """
        # Flatten sequence data for Random Forest
        if len(data.shape) == 3:  # (samples, sequence_length, features)
            n_samples, seq_len, n_features = data.shape
            data = data.reshape(n_samples, seq_len * n_features)
        
        return self.scaler.fit_transform(data)
    
    def detect_fault(self, data: np.ndarray) -> Dict:
        """
        Detect fault in real-time data.
        
        Args:
            data: Input data sequence
            
        Returns:
            Detection results with fault type and confidence
        """
        # Preprocess
        if len(data) < self.sequence_length:
            return {
                'fault_detected': False,
                'fault_type': 'no_fault',
                'confidence': 0.0,
                'message': 'Insufficient data for detection'
            }
        
        # Extract relevant features from sequence data
        features = np.array([
            np.mean(data[:, 0]),    # Average voltage
            np.std(data[:, 0]),     # Voltage variation
            np.mean(data[:, 1]),    # Average current
            np.std(data[:, 1])      # Current variation
        ]).reshape(1, -1)
        
        # Fit and transform for demonstration (in real application, this should be pre-trained)
        processed_data = self.scaler.fit_transform(features)
        
        # Predict
        probabilities = self.model.predict_proba(processed_data)
        fault_idx = np.argmax(probabilities[0])
        confidence = probabilities[0][fault_idx]
        
        fault_detected = (
            fault_idx != 0 and  # Not 'no_fault'
            confidence >= self.confidence_threshold
        )
        
        return {
            'fault_detected': fault_detected,
            'fault_type': self.fault_types[fault_idx],
            'confidence': float(confidence),
            'all_probabilities': {
                fault_type: float(prob)
                for fault_type, prob in zip(self.fault_types, probabilities[0])
            }
        }
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray
    ) -> Dict:
        """
        Train the fault detection model.
        
        Args:
            X_train: Training data
            y_train: Training labels
            X_val: Validation data
            y_val: Validation labels
            
        Returns:
            Training metrics
        """
        # Preprocess data
        X_train_processed = self.preprocess_data(X_train)
        X_val_processed = self.scaler.transform(X_val)
        
        # Train
        self.model.fit(X_train_processed, y_train)
        
        # Calculate metrics
        train_score = self.model.score(X_train_processed, y_train)
        val_score = self.model.score(X_val_processed, y_val)
        
        metrics = {
            'train_accuracy': train_score,
            'val_accuracy': val_score
        }
        
        self.logger.info("Model training completed")
        return metrics
    
    def save_model(self, filepath: str):
        """Save model and scaler to file."""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, filepath)
        self.logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load model and scaler from file."""
        saved_data = joblib.load(filepath)
        self.model = saved_data['model']
        self.scaler = saved_data['scaler']
        self.logger.info(f"Model loaded from {filepath}")
