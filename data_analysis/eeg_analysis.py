"""
EEG Signal Analysis Module

This module provides comprehensive analysis of EEG signals including:
- Signal preprocessing and filtering
- Spectral analysis
- Statistical analysis
- Visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import signal, stats
from scipy.fft import fft, fftfreq
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from typing import Dict, List, Tuple, Optional
from data_loader import DataLoader


class EEGAnalyzer:
    """Comprehensive EEG signal analysis class."""
    
    def __init__(self, data_loader: DataLoader):
        """
        Initialize EEG analyzer.
        
        Args:
            data_loader: DataLoader instance with loaded data
        """
        self.data_loader = data_loader
        self.eeg_data = data_loader.loaded_data.get('eeg', pd.DataFrame())
        self.sampling_rate = self._get_sampling_rate()
        self.channels = data_loader.get_eeg_channels()
        
        # Define EEG frequency bands
        self.frequency_bands = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 100)
        }
        
    def _get_sampling_rate(self) -> float:
        """Estimate sampling rate from EEG data."""
        info = self.data_loader.get_data_info()
        if 'eeg' in info and info['eeg']['sampling_rate']:
            return info['eeg']['sampling_rate']
        return 128.0  # Default Emotiv sampling rate
    
    def preprocess_signal(self, channel_data: pd.Series, 
                         lowpass: float = 50.0, 
                         highpass: float = 0.5,
                         notch: float = 60.0) -> pd.Series:
        """
        Preprocess EEG signal with filtering.
        
        Args:
            channel_data: Raw EEG signal
            lowpass: Low-pass filter frequency
            highpass: High-pass filter frequency
            notch: Notch filter frequency (power line noise)
            
        Returns:
            Filtered signal
        """
        # Remove NaN values
        data = channel_data.dropna()
        
        if len(data) < 100:  # Need minimum data for filtering
            return data
            
        # Design filters
        nyquist = self.sampling_rate / 2
        
        # High-pass filter (remove DC and low-frequency drift)
        if highpass > 0:
            high_b, high_a = signal.butter(4, highpass/nyquist, btype='high')
            data = pd.Series(signal.filtfilt(high_b, high_a, data), index=data.index)
        
        # Low-pass filter (anti-aliasing)
        if lowpass < nyquist:
            low_b, low_a = signal.butter(4, lowpass/nyquist, btype='low')
            data = pd.Series(signal.filtfilt(low_b, low_a, data), index=data.index)
        
        # Notch filter (remove power line noise)
        if notch > 0:
            notch_b, notch_a = signal.iirnotch(notch, 30, self.sampling_rate)
            data = pd.Series(signal.filtfilt(notch_b, notch_a, data), index=data.index)
            
        return data
    
    def compute_psd(self, channel_data: pd.Series, 
                    window_length: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute Power Spectral Density using Welch's method.
        
        Args:
            channel_data: EEG signal
            window_length: Window length for Welch's method
            
        Returns:
            Tuple of (frequencies, power spectral density)
        """
        if window_length is None:
            window_length = min(len(channel_data) // 4, int(2 * self.sampling_rate))
            
        frequencies, psd = signal.welch(
            channel_data.dropna(), 
            fs=self.sampling_rate,
            nperseg=window_length,
            overlap=window_length//2
        )
        
        return frequencies, psd
    
    def extract_band_power(self, channel_data: pd.Series) -> Dict[str, float]:
        """
        Extract power in different frequency bands.
        
        Args:
            channel_data: EEG signal
            
        Returns:
            Dictionary with band powers
        """
        frequencies, psd = self.compute_psd(channel_data)
        band_powers = {}
        
        for band_name, (low_freq, high_freq) in self.frequency_bands.items():
            # Find frequency indices
            freq_mask = (frequencies >= low_freq) & (frequencies <= high_freq)
            
            if np.any(freq_mask):
                # Integrate power in the band
                band_power = np.trapz(psd[freq_mask], frequencies[freq_mask])
                band_powers[band_name] = band_power
            else:
                band_powers[band_name] = 0.0
                
        return band_powers
    
    def analyze_all_channels(self) -> Dict[str, Dict]:
        """
        Perform comprehensive analysis on all EEG channels.
        
        Returns:
            Dictionary with analysis results for each channel
        """
        results = {}
        
        for channel in self.channels:
            if channel in self.eeg_data.columns:
                print(f"Analyzing channel: {channel}")
                
                # Get raw data
                raw_data = self.eeg_data[channel]
                
                # Preprocess
                filtered_data = self.preprocess_signal(raw_data)
                
                # Basic statistics
                stats_results = {
                    'mean': raw_data.mean(),
                    'std': raw_data.std(),
                    'min': raw_data.min(),
                    'max': raw_data.max(),
                    'skewness': stats.skew(raw_data.dropna()),
                    'kurtosis': stats.kurtosis(raw_data.dropna())
                }
                
                # Frequency analysis
                band_powers = self.extract_band_power(filtered_data)
                
                # Signal quality metrics
                quality_metrics = self._assess_signal_quality(raw_data)
                
                results[channel] = {
                    'statistics': stats_results,
                    'band_powers': band_powers,
                    'quality': quality_metrics,
                    'filtered_data': filtered_data
                }
                
        return results
    
    def _assess_signal_quality(self, channel_data: pd.Series) -> Dict[str, float]:
        """Assess signal quality metrics."""
        clean_data = channel_data.dropna()
        
        if len(clean_data) == 0:
            return {'snr': 0, 'artifact_ratio': 1}
            
        # Signal-to-noise ratio (simplified)
        signal_power = np.var(clean_data)
        # Use high-frequency content as noise estimate
        if len(clean_data) > 100:
            diff_signal = np.diff(clean_data)
            noise_power = np.var(diff_signal)
            snr = 10 * np.log10(signal_power / noise_power) if noise_power > 0 else 0
        else:
            snr = 0
            
        # Artifact detection (simple threshold-based)
        threshold = 3 * clean_data.std()
        artifacts = np.abs(clean_data - clean_data.mean()) > threshold
        artifact_ratio = artifacts.sum() / len(clean_data)
        
        return {
            'snr': snr,
            'artifact_ratio': artifact_ratio
        }
    
    def plot_channel_overview(self, channel: str, 
                            time_window: int = 10) -> go.Figure:
        """
        Create comprehensive visualization for a single channel.
        
        Args:
            channel: Channel name
            time_window: Time window in seconds to display
            
        Returns:
            Plotly figure
        """
        if channel not in self.eeg_data.columns:
            print(f"Channel {channel} not found")
            return go.Figure()
            
        # Get data
        raw_data = self.eeg_data[channel]
        filtered_data = self.preprocess_signal(raw_data)
        
        # Limit to time window
        end_time = raw_data.index[-1]
        start_time = end_time - pd.Timedelta(seconds=time_window)
        
        raw_windowed = raw_data[raw_data.index >= start_time]
        filtered_windowed = filtered_data[filtered_data.index >= start_time]
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=[
                f'{channel} - Raw Signal', f'{channel} - Filtered Signal',
                'Power Spectral Density', 'Frequency Bands',
                'Signal Statistics', 'Quality Metrics'
            ],
            specs=[
                [{"colspan": 1}, {"colspan": 1}],
                [{"colspan": 1}, {"colspan": 1}],
                [{"colspan": 2}, None]
            ]
        )
        
        # Time domain plots
        fig.add_trace(
            go.Scatter(x=raw_windowed.index, y=raw_windowed.values,
                      name='Raw', line=dict(color='blue')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=filtered_windowed.index, y=filtered_windowed.values,
                      name='Filtered', line=dict(color='red')),
            row=1, col=2
        )
        
        # Frequency domain
        frequencies, psd = self.compute_psd(filtered_data)
        fig.add_trace(
            go.Scatter(x=frequencies, y=10*np.log10(psd),
                      name='PSD', line=dict(color='green')),
            row=2, col=1
        )
        
        # Band powers
        band_powers = self.extract_band_power(filtered_data)
        bands = list(band_powers.keys())
        powers = list(band_powers.values())
        
        fig.add_trace(
            go.Bar(x=bands, y=powers, name='Band Power'),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            title_text=f"EEG Channel Analysis: {channel}",
            showlegend=False
        )
        
        return fig
    
    def plot_all_channels_summary(self) -> go.Figure:
        """Create summary visualization for all channels."""
        analysis_results = self.analyze_all_channels()
        
        if not analysis_results:
            return go.Figure()
            
        # Extract data for plotting
        channels = list(analysis_results.keys())
        
        # Band powers across channels
        band_names = list(self.frequency_bands.keys())
        band_data = {band: [] for band in band_names}
        
        for channel in channels:
            for band in band_names:
                power = analysis_results[channel]['band_powers'].get(band, 0)
                band_data[band].append(power)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[
                'Alpha Power Across Channels',
                'Signal Quality (SNR)',
                'Band Power Comparison',
                'Artifact Levels'
            ]
        )
        
        # Alpha power (most commonly analyzed)
        fig.add_trace(
            go.Bar(x=channels, y=band_data['alpha'], name='Alpha Power'),
            row=1, col=1
        )
        
        # Signal quality
        snr_values = [analysis_results[ch]['quality']['snr'] for ch in channels]
        fig.add_trace(
            go.Bar(x=channels, y=snr_values, name='SNR (dB)'),
            row=1, col=2
        )
        
        # Band power heatmap data
        for i, band in enumerate(band_names):
            fig.add_trace(
                go.Bar(x=channels, y=band_data[band], name=band,
                      offsetgroup=i),
                row=2, col=1
            )
        
        # Artifact levels
        artifact_ratios = [analysis_results[ch]['quality']['artifact_ratio'] 
                          for ch in channels]
        fig.add_trace(
            go.Bar(x=channels, y=artifact_ratios, name='Artifact Ratio'),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text="EEG Analysis Summary - All Channels",
            showlegend=True
        )
        
        return fig
    
    def generate_report(self, output_dir: str = "output") -> str:
        """
        Generate comprehensive analysis report.
        
        Args:
            output_dir: Directory to save the report
            
        Returns:
            Path to the generated report
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Perform analysis
        results = self.analyze_all_channels()
        
        # Generate report
        report_path = os.path.join(output_dir, "eeg_analysis_report.txt")
        
        with open(report_path, 'w') as f:
            f.write("EEG Signal Analysis Report\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Dataset Information:\n")
            f.write(f"- Number of channels: {len(self.channels)}\n")
            f.write(f"- Sampling rate: {self.sampling_rate} Hz\n")
            f.write(f"- Data shape: {self.eeg_data.shape}\n")
            f.write(f"- Duration: {self.eeg_data.shape[0] / self.sampling_rate:.2f} seconds\n\n")
            
            for channel, analysis in results.items():
                f.write(f"Channel: {channel}\n")
                f.write("-" * 20 + "\n")
                
                stats = analysis['statistics']
                f.write(f"Statistics:\n")
                f.write(f"  Mean: {stats['mean']:.2f} µV\n")
                f.write(f"  Std: {stats['std']:.2f} µV\n")
                f.write(f"  Range: {stats['min']:.2f} to {stats['max']:.2f} µV\n")
                f.write(f"  Skewness: {stats['skewness']:.3f}\n")
                f.write(f"  Kurtosis: {stats['kurtosis']:.3f}\n\n")
                
                bands = analysis['band_powers']
                f.write(f"Frequency Band Powers:\n")
                for band, power in bands.items():
                    f.write(f"  {band.capitalize()}: {power:.2e} µV²/Hz\n")
                f.write("\n")
                
                quality = analysis['quality']
                f.write(f"Signal Quality:\n")
                f.write(f"  SNR: {quality['snr']:.2f} dB\n")
                f.write(f"  Artifact Ratio: {quality['artifact_ratio']:.3f}\n\n")
                
        return report_path


def main():
    """Main function for standalone execution."""
    from data_loader import load_session_data
    
    # Load data
    data_dir = "../collected_data"
    loader, data = load_session_data(data_dir)
    
    if 'eeg' not in data or data['eeg'].empty:
        print("No EEG data found!")
        return
    
    # Create analyzer
    analyzer = EEGAnalyzer(loader)
    
    # Generate analysis
    print("Performing EEG analysis...")
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Generate summary plot
    summary_fig = analyzer.plot_all_channels_summary()
    summary_fig.write_html("output/eeg_summary.html")
    print("Summary plot saved to output/eeg_summary.html")
    
    # Generate individual channel plots for first few channels
    for i, channel in enumerate(analyzer.channels[:3]):  # First 3 channels
        fig = analyzer.plot_channel_overview(channel)
        fig.write_html(f"output/eeg_channel_{channel}.html")
        print(f"Channel {channel} plot saved to output/eeg_channel_{channel}.html")
    
    # Generate report
    report_path = analyzer.generate_report()
    print(f"Analysis report saved to {report_path}")


if __name__ == "__main__":
    main()
