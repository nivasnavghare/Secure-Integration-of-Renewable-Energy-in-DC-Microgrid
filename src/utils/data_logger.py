"""
Data logging utilities
"""

import h5py
import json
import pandas as pd
from pathlib import Path
from typing import Dict
import logging


class DataLogger:
    """Data logging and persistence"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def save_results(self, results: Dict, metrics: Dict, filepath: str):
        """
        Save simulation results to HDF5 file.
        
        Args:
            results: Simulation time series results
            metrics: Performance metrics
            filepath: Output file path
        """
        # Create directory if not exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        # Save to HDF5
        with h5py.File(filepath, 'w') as f:
            # Save time series data
            for key, value in results.items():
                if isinstance(value, list):
                    f.create_dataset(key, data=value)
            
            # Save metrics as attributes
            for key, value in metrics.items():
                if isinstance(value, (int, float, str)):
                    f.attrs[key] = value
        
        self.logger.info(f"Results saved to {filepath}")
    
    def save_to_csv(self, results: Dict, filepath: str):
        """Save results to CSV file."""
        df = pd.DataFrame(results)
        df.to_csv(filepath, index=False)
        self.logger.info(f"Results exported to CSV: {filepath}")
    
    def save_metrics_json(self, metrics: Dict, filepath: str):
        """Save metrics to JSON file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=4)
        
        self.logger.info(f"Metrics saved to {filepath}")
