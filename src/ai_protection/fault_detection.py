"""
AI-based Fault Detection System

This module implements machine learning models for real-time
fault detection in DC microgrids.
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from typing import Dict, List, Tuple, Optional
import logging


class FaultDetector:
    """AI-based Fault Detection using LSTM Neural Network"""
    
    def __init__(self, config: Dict):
        """
        Initialize fault detector.
        
        Args:
            config: Configuration dictionary for fault detection
        """
        self.config = config
        self.model_type = config.get('model_type', 'LSTM')
        self.input_features = config.get('input_features', ['voltage', 'current', 'power'])
        self.sequence_length = config.get('sequence_length', 100)
        self.confidence_threshold = config.get('confidence_threshold', 0.85)
        
        self.model = None
        self.scaler = None
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
        """Build LSTM-based fault detection model."""
        n_features = len(self.input_features)
        n_classes = len(self.fault_types)
        
        if self.model_type == 'LSTM':
            model = keras.Sequential([
                keras.layers.LSTM(
                    128,
                    return_sequences=True,
                    input_shape=(self.sequence_length, n_features)
                ),
                keras.layers.Dropout(0.3),
                keras.layers.LSTM(64, return_sequences=False),
                keras.layers.Dropout(0.3),
                keras.layers.Dense(32, activation='relu'),
                keras.layers.Dense(n_classes, activation='softmax')
            ])
        elif self.model_type == 'CNN':
            model = keras.Sequential([
                keras.layers.Conv1D(
                    filters=64,
                    kernel_size=3,
                    activation='relu',
                    input_shape=(self.sequence_length, n_features)
                ),
                keras.layers.MaxPooling1D(pool_size=2),
                keras.layers.Conv1D(filters=32, kernel_size=3, activation='relu'),
                keras.layers.MaxPooling1D(pool_size=2),
                keras.layers.Flatten(),
                keras.layers.Dense(64, activation='relu'),
                keras.layers.Dropout(0.3),
                keras.layers.Dense(n_classes, activation='softmax')
            ])
        else:  # Hybrid CNN-LSTM
            model = keras.Sequential([
                keras.layers.Conv1D(
                    filters=64,
                    kernel_size=3,
                    activation='relu',
                    input_shape=(self.sequence_length, n_features)
                ),
                keras.layers.MaxPooling1D(pool_size=2),
                keras.layers.LSTM(64, return_sequences=False),
                keras.layers.Dropout(0.3),
                keras.layers.Dense(32, activation='relu'),
                keras.layers.Dense(n_classes, activation='softmax')
            ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        self.logger.info(f"{self.model_type} fault detection model built")
        
    def preprocess_data(self, data: np.ndarray) -> np.ndarray:
        """
        Preprocess input data for model.
        
        Args:
            data: Raw input data
            
        Returns:
            Preprocessed data
        """
        # Normalize data
        if self.scaler is None:
            from sklearn.preprocessing import StandardScaler
            self.scaler = StandardScaler()
            return self.scaler.fit_transform(data)
        return self.scaler.transform(data)
    
    def create_sequences(
        self,
        data: np.ndarray,
        sequence_length: Optional[int] = None
    ) -> np.ndarray:
        """
        Create sequences from time series data.
        
        Args:
            data: Time series data
            sequence_length: Length of sequences
            
        Returns:
            Sequenced data
        """
        if sequence_length is None:
            sequence_length = self.sequence_length
        
        n_samples = len(data) - sequence_length + 1
        n_features = data.shape[1] if len(data.shape) > 1 else 1
        
        sequences = np.zeros((n_samples, sequence_length, n_features))
        
        for i in range(n_samples):
            sequences[i] = data[i:i + sequence_length]
        
        return sequences
    
    def detect_fault(self, data: np.ndarray) -> Dict:
        """
        Detect fault in real-time data.
        
        Args:
            data: Input data sequence
            
        Returns:
            Detection results with fault type and confidence
        """
        # Preprocess
        processed_data = self.preprocess_data(data)
        
        # Create sequence
        if len(processed_data) < self.sequence_length:
            return {
                'fault_detected': False,
                'fault_type': 'no_fault',
                'confidence': 0.0,
                'message': 'Insufficient data for detection'
            }
        
        sequence = self.create_sequences(processed_data)
        
        # Predict
        predictions = self.model.predict(sequence[-1:], verbose=0)
        fault_idx = np.argmax(predictions[0])
        confidence = predictions[0][fault_idx]
        
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
                for fault_type, prob in zip(self.fault_types, predictions[0])
            }
        }
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        epochs: int = 50,
        batch_size: int = 32
    ) -> Dict:
        """
        Train the fault detection model.
        
        Args:
            X_train: Training data
            y_train: Training labels
            X_val: Validation data
            y_val: Validation labels
            epochs: Number of training epochs
            batch_size: Batch size
            
        Returns:
            Training history
        """
        # Callbacks
        early_stopping = keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        )
        
        reduce_lr = keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-6
        )
        
        # Train
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stopping, reduce_lr],
            verbose=1
        )
        
        self.logger.info("Model training completed")
        
        return history.history
    
    def save_model(self, filepath: str):
        """Save model to file."""
        self.model.save(filepath)
        self.logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load model from file."""
        self.model = keras.models.load_model(filepath)
        self.logger.info(f"Model loaded from {filepath}")
