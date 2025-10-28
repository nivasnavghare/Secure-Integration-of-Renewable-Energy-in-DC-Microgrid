"""
Anomaly Detection for Cybersecurity

This module implements anomaly detection for identifying
unusual patterns in microgrid operation that may indicate
cyber attacks or system malfunctions.
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Optional
import logging


class AnomalyDetector:
    """Anomaly Detection System using Isolation Forest"""
    
    def __init__(self, config: Dict):
        """
        Initialize anomaly detector.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.algorithm = config.get('algorithm', 'IsolationForest')
        self.contamination = config.get('contamination', 0.1)
        self.n_estimators = config.get('n_estimators', 100)
        
        self.model = None
        self.scaler = StandardScaler()
        self.logger = logging.getLogger(__name__)
        
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize the anomaly detection model."""
        if self.algorithm == 'IsolationForest':
            self.model = IsolationForest(
                contamination=self.contamination,
                n_estimators=self.n_estimators,
                random_state=42,
                n_jobs=-1
            )
        else:
            # Can add other algorithms like One-Class SVM, Local Outlier Factor
            from sklearn.svm import OneClassSVM
            self.model = OneClassSVM(nu=self.contamination, kernel='rbf')
        
        self.logger.info(f"{self.algorithm} anomaly detector initialized")
    
    def fit(self, X: np.ndarray):
        """
        Fit the anomaly detection model.
        
        Args:
            X: Training data (normal operation data)
        """
        # Normalize data
        X_scaled = self.scaler.fit_transform(X)
        
        # Fit model
        self.model.fit(X_scaled)
        
        self.logger.info("Anomaly detector trained on normal operation data")
    
    def predict(self, X: np.ndarray) -> Dict:
        """
        Predict anomalies in new data.
        
        Args:
            X: Input data to check for anomalies
            
        Returns:
            Dictionary containing anomaly detection results
        """
        # Normalize
        X_scaled = self.scaler.transform(X)
        
        # Predict
        predictions = self.model.predict(X_scaled)
        scores = self.model.score_samples(X_scaled)
        
        # -1 for anomalies, 1 for normal
        anomalies = predictions == -1
        n_anomalies = np.sum(anomalies)
        
        return {
            'anomalies_detected': bool(n_anomalies > 0),
            'n_anomalies': int(n_anomalies),
            'anomaly_indices': np.where(anomalies)[0].tolist(),
            'anomaly_scores': scores.tolist(),
            'severity': self._calculate_severity(scores)
        }
    
    def _calculate_severity(self, scores: np.ndarray) -> str:
        """
        Calculate anomaly severity based on scores.
        
        Args:
            scores: Anomaly scores
            
        Returns:
            Severity level string
        """
        min_score = np.min(scores)
        
        if min_score < -0.5:
            return 'critical'
        elif min_score < -0.3:
            return 'high'
        elif min_score < -0.1:
            return 'medium'
        else:
            return 'low'
    
    def detect_cyber_attacks(self, network_data: Dict) -> Dict:
        """
        Detect potential cyber attacks in network data.
        
        Args:
            network_data: Network traffic and system data
            
        Returns:
            Cyber attack detection results
        """
        # Extract features for cyber attack detection
        features = self._extract_cyber_features(network_data)
        
        # Detect anomalies
        result = self.predict(features)
        
        # Classify attack types
        if result['anomalies_detected']:
            attack_types = self._classify_attack_types(features, result)
            result['potential_attacks'] = attack_types
        
        return result
    
    def _extract_cyber_features(self, network_data: Dict) -> np.ndarray:
        """
        Extract features relevant for cyber attack detection.
        
        Args:
            network_data: Raw network data
            
        Returns:
            Feature array
        """
        # Example features
        features = []
        
        # Network traffic features
        features.append(network_data.get('packet_rate', 0))
        features.append(network_data.get('connection_count', 0))
        features.append(network_data.get('failed_login_attempts', 0))
        
        # System behavior features
        features.append(network_data.get('cpu_usage', 0))
        features.append(network_data.get('memory_usage', 0))
        features.append(network_data.get('command_frequency', 0))
        
        return np.array(features).reshape(1, -1)
    
    def _classify_attack_types(
        self,
        features: np.ndarray,
        detection_result: Dict
    ) -> List[str]:
        """
        Classify types of potential attacks.
        
        Args:
            features: Feature array
            detection_result: Anomaly detection results
            
        Returns:
            List of potential attack types
        """
        attack_types = []
        
        # Simple rule-based classification
        if features[0, 0] > 1000:  # High packet rate
            attack_types.append('DDoS')
        
        if features[0, 2] > 5:  # Failed login attempts
            attack_types.append('Brute Force')
        
        if features[0, 5] > 100:  # High command frequency
            attack_types.append('Command Injection')
        
        if not attack_types:
            attack_types.append('Unknown')
        
        return attack_types
    
    def continuous_monitoring(
        self,
        data_stream: np.ndarray,
        window_size: int = 100
    ) -> List[Dict]:
        """
        Continuously monitor data stream for anomalies.
        
        Args:
            data_stream: Continuous data stream
            window_size: Size of sliding window
            
        Returns:
            List of detection results for each window
        """
        results = []
        n_samples = len(data_stream)
        
        for i in range(0, n_samples - window_size + 1, window_size // 2):
            window = data_stream[i:i + window_size]
            result = self.predict(window)
            result['window_index'] = i
            results.append(result)
        
        return results
