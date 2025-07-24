"""
Data Loader Module for EEG and Sensor Data Analysis

This module provides utilities to load and preprocess data from the collected CSV files.
"""

import pandas as pd
import numpy as np
import os
from typing import Dict, List, Optional, Tuple
import glob
from datetime import datetime


class DataLoader:
    """Unified data loader for all CSV files from the collected_data folder."""
    
    def __init__(self, data_directory: str):
        """
        Initialize the data loader.
        
        Args:
            data_directory: Path to the directory containing CSV files
        """
        self.data_directory = data_directory
        self.data_types = ['eeg', 'met', 'mot', 'pow', 'dev']
        self.loaded_data = {}
        
    def find_csv_files(self) -> Dict[str, List[str]]:
        """
        Find all CSV files in the data directory organized by type.
        
        Returns:
            Dictionary with data types as keys and file paths as values
        """
        files_by_type = {}
        
        for data_type in self.data_types:
            pattern = os.path.join(self.data_directory, f"data_{data_type}_*.csv")
            files = glob.glob(pattern)
            files_by_type[data_type] = sorted(files)
            
        return files_by_type
    
    def load_csv_file(self, file_path: str) -> pd.DataFrame:
        """
        Load a single CSV file with proper preprocessing.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Preprocessed DataFrame
        """
        try:
            df = pd.read_csv(file_path)
            
            # Convert timestamp to datetime if it exists
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
                df.set_index('timestamp', inplace=True)
                
            return df
            
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return pd.DataFrame()
    
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Load all CSV files and return organized data.
        
        Returns:
            Dictionary with data types as keys and DataFrames as values
        """
        files_by_type = self.find_csv_files()
        
        for data_type, file_list in files_by_type.items():
            if file_list:
                # For now, load the first (most recent) file of each type
                # You can modify this to combine multiple sessions
                df = self.load_csv_file(file_list[0])
                self.loaded_data[data_type] = df
                print(f"Loaded {data_type} data: {df.shape}")
            else:
                print(f"No files found for data type: {data_type}")
                
        return self.loaded_data
    
    def get_data_info(self) -> Dict[str, Dict]:
        """
        Get basic information about loaded datasets.
        
        Returns:
            Dictionary with dataset information
        """
        info = {}
        
        for data_type, df in self.loaded_data.items():
            if not df.empty:
                info[data_type] = {
                    'shape': df.shape,
                    'columns': list(df.columns),
                    'time_range': (df.index.min(), df.index.max()) if hasattr(df.index, 'min') else None,
                    'duration': (df.index.max() - df.index.min()).total_seconds() if hasattr(df.index, 'min') else None,
                    'sampling_rate': self._estimate_sampling_rate(df),
                    'missing_values': df.isnull().sum().sum()
                }
                
        return info
    
    def _estimate_sampling_rate(self, df: pd.DataFrame) -> Optional[float]:
        """Estimate sampling rate from timestamp differences."""
        if hasattr(df.index, 'to_series') and len(df) > 1:
            time_diffs = df.index.to_series().diff().dropna()
            if len(time_diffs) > 0:
                avg_interval = time_diffs.mean().total_seconds()
                return 1.0 / avg_interval if avg_interval > 0 else None
        return None
    
    def get_eeg_channels(self) -> List[str]:
        """Get list of EEG channel names."""
        if 'eeg' in self.loaded_data and not self.loaded_data['eeg'].empty:
            # Standard 14-channel Emotiv layout
            channels = [col for col in self.loaded_data['eeg'].columns 
                       if col not in ['COUNTER', 'INTERPOLATED', 'RAW_CQ', 'MARKER_HARDWARE']]
            return channels
        return []
    
    def get_mental_state_metrics(self) -> List[str]:
        """Get list of mental state metric names."""
        if 'met' in self.loaded_data and not self.loaded_data['met'].empty:
            metrics = [col for col in self.loaded_data['met'].columns 
                      if not col.endswith('.isActive')]
            return metrics
        return []
    
    def get_motion_sensors(self) -> List[str]:
        """Get list of motion sensor channels."""
        if 'mot' in self.loaded_data and not self.loaded_data['mot'].empty:
            sensors = [col for col in self.loaded_data['mot'].columns 
                      if col not in ['COUNTER_MEMS', 'INTERPOLATED_MEMS']]
            return sensors
        return []
    
    def synchronize_data(self, tolerance_seconds: float = 0.1) -> pd.DataFrame:
        """
        Synchronize all data types to common timestamps.
        
        Args:
            tolerance_seconds: Maximum time difference for synchronization
            
        Returns:
            Synchronized DataFrame with all data types
        """
        if not self.loaded_data:
            return pd.DataFrame()
            
        # Find common time range
        start_times = []
        end_times = []
        
        for data_type, df in self.loaded_data.items():
            if not df.empty and hasattr(df.index, 'min'):
                start_times.append(df.index.min())
                end_times.append(df.index.max())
        
        if not start_times:
            return pd.DataFrame()
            
        common_start = max(start_times)
        common_end = min(end_times)
        
        print(f"Synchronizing data from {common_start} to {common_end}")
        
        # Use the highest sampling rate as reference
        reference_data = None
        max_samples = 0
        
        for data_type, df in self.loaded_data.items():
            if not df.empty:
                time_filtered = df[(df.index >= common_start) & (df.index <= common_end)]
                if len(time_filtered) > max_samples:
                    max_samples = len(time_filtered)
                    reference_data = time_filtered
        
        if reference_data is None:
            return pd.DataFrame()
            
        # Resample other data to match reference timestamps
        synchronized_df = reference_data.copy()
        
        for data_type, df in self.loaded_data.items():
            if not df.empty and data_type != 'eeg':  # Assuming EEG has highest sampling rate
                time_filtered = df[(df.index >= common_start) & (df.index <= common_end)]
                
                # Resample to match reference timestamps
                resampled = time_filtered.reindex(
                    synchronized_df.index, 
                    method='nearest',
                    tolerance=pd.Timedelta(seconds=tolerance_seconds)
                )
                
                # Add prefix to column names to avoid conflicts
                resampled.columns = [f"{data_type}_{col}" for col in resampled.columns]
                
                # Merge with synchronized data
                synchronized_df = synchronized_df.join(resampled, how='inner')
        
        return synchronized_df


def load_session_data(data_directory: str) -> Tuple[DataLoader, Dict[str, pd.DataFrame]]:
    """
    Convenience function to load session data.
    
    Args:
        data_directory: Path to the collected_data directory
        
    Returns:
        Tuple of (DataLoader instance, loaded data dictionary)
    """
    loader = DataLoader(data_directory)
    data = loader.load_all_data()
    return loader, data


if __name__ == "__main__":
    # Example usage
    data_dir = "../collected_data"
    
    loader, data = load_session_data(data_dir)
    
    # Print data information
    info = loader.get_data_info()
    for data_type, details in info.items():
        print(f"\n{data_type.upper()} Data:")
        print(f"  Shape: {details['shape']}")
        print(f"  Duration: {details.get('duration', 'N/A')} seconds")
        print(f"  Sampling Rate: {details.get('sampling_rate', 'N/A')} Hz")
        print(f"  Missing Values: {details['missing_values']}")
    
    # Show available channels/metrics
    print(f"\nEEG Channels: {loader.get_eeg_channels()}")
    print(f"Mental State Metrics: {loader.get_mental_state_metrics()}")
    print(f"Motion Sensors: {loader.get_motion_sensors()}")
