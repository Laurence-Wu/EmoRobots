"""
Comprehensive Analysis Module

This module combines all analysis types to provide integrated insights.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime
from typing import Dict, List, Optional

from data_loader import DataLoader, load_session_data
from eeg_analysis import EEGAnalyzer
from mental_state_analysis import MentalStateAnalyzer
from motion_analysis import MotionAnalyzer


class ComprehensiveAnalyzer:
    """Integrated analysis across all data types."""
    
    def __init__(self, data_directory: str):
        """
        Initialize comprehensive analyzer.
        
        Args:
            data_directory: Path to collected_data folder
        """
        self.data_directory = data_directory
        self.loader, self.data = load_session_data(data_directory)
        
        # Initialize individual analyzers
        self.analyzers = {}
        
        if 'eeg' in self.data and not self.data['eeg'].empty:
            self.analyzers['eeg'] = EEGAnalyzer(self.loader)
            
        if 'met' in self.data and not self.data['met'].empty:
            self.analyzers['mental'] = MentalStateAnalyzer(self.loader)
            
        if 'mot' in self.data and not self.data['mot'].empty:
            self.analyzers['motion'] = MotionAnalyzer(self.loader)
    
    def synchronize_all_data(self) -> pd.DataFrame:
        """Synchronize all data types to common timebase."""
        return self.loader.synchronize_data()
    
    def analyze_eeg_mental_correlations(self) -> Dict[str, pd.DataFrame]:
        """
        Analyze correlations between EEG and mental state data.
        
        Returns:
            Dictionary with correlation results
        """
        correlations = {}
        
        if 'eeg' not in self.analyzers or 'mental' not in self.analyzers:
            return correlations
            
        # Get synchronized data
        sync_data = self.synchronize_all_data()
        
        if sync_data.empty:
            return correlations
            
        # Extract EEG channels and mental metrics
        eeg_columns = [col for col in sync_data.columns if not col.startswith('met_')]
        mental_columns = [col for col in sync_data.columns if col.startswith('met_')]
        
        # Calculate correlations between EEG and mental states
        if eeg_columns and mental_columns:
            eeg_data = sync_data[eeg_columns]
            mental_data = sync_data[mental_columns]
            
            # Cross-correlation matrix
            cross_corr = pd.DataFrame(
                index=eeg_columns,
                columns=mental_columns,
                dtype=float
            )
            
            for eeg_col in eeg_columns:
                for mental_col in mental_columns:
                    if not sync_data[eeg_col].isna().all() and not sync_data[mental_col].isna().all():
                        corr = sync_data[eeg_col].corr(sync_data[mental_col])
                        cross_corr.loc[eeg_col, mental_col] = corr
            
            correlations['eeg_mental_correlation'] = cross_corr
            
        return correlations
    
    def analyze_motion_artifact_impact(self) -> Dict[str, Dict]:
        """
        Analyze how motion affects EEG signal quality.
        
        Returns:
            Dictionary with motion artifact analysis
        """
        results = {}
        
        if 'eeg' not in self.analyzers or 'motion' not in self.analyzers:
            return results
            
        sync_data = self.synchronize_all_data()
        
        if sync_data.empty:
            return results
            
        # Get motion magnitude
        motion_analyzer = self.analyzers['motion']
        motion_data = motion_analyzer.motion_data
        
        if not motion_data.empty:
            acc_magnitude = motion_analyzer.calculate_acceleration_magnitude()
            
            # Find motion artifacts in synchronized data
            if not acc_magnitude.empty and len(sync_data) > 0:
                # Resample motion data to match sync_data
                try:
                    acc_resampled = acc_magnitude.reindex(
                        sync_data.index, 
                        method='nearest',
                        tolerance=pd.Timedelta(seconds=0.1)
                    )
                    
                    # Analyze EEG quality vs motion
                    eeg_columns = [col for col in sync_data.columns 
                                 if not col.startswith(('met_', 'mot_', 'pow_', 'dev_'))]
                    
                    motion_impact = {}
                    
                    for eeg_channel in eeg_columns[:5]:  # Limit to first 5 channels
                        if eeg_channel in sync_data.columns:
                            eeg_signal = sync_data[eeg_channel].dropna()
                            
                            if len(eeg_signal) > 10 and not acc_resampled.isna().all():
                                # Calculate correlation with motion
                                common_idx = eeg_signal.index.intersection(acc_resampled.index)
                                if len(common_idx) > 10:
                                    eeg_common = eeg_signal.loc[common_idx]
                                    motion_common = acc_resampled.loc[common_idx]
                                    
                                    # Remove NaN values
                                    valid_mask = ~(eeg_common.isna() | motion_common.isna())
                                    if valid_mask.sum() > 10:
                                        correlation = eeg_common[valid_mask].corr(motion_common[valid_mask])
                                        
                                        # Calculate signal variability during high motion
                                        high_motion_threshold = motion_common.quantile(0.8)
                                        high_motion_mask = motion_common > high_motion_threshold
                                        
                                        if high_motion_mask.sum() > 0:
                                            high_motion_std = eeg_common[high_motion_mask].std()
                                            low_motion_std = eeg_common[~high_motion_mask].std()
                                            
                                            motion_impact[eeg_channel] = {
                                                'motion_correlation': correlation,
                                                'high_motion_variability': high_motion_std,
                                                'low_motion_variability': low_motion_std,
                                                'variability_ratio': high_motion_std / low_motion_std if low_motion_std > 0 else np.nan
                                            }
                    
                    results['motion_artifact_impact'] = motion_impact
                    
                except Exception as e:
                    print(f"Error in motion artifact analysis: {e}")
                    
        return results
    
    def create_integrated_dashboard(self) -> go.Figure:
        """Create comprehensive dashboard with all analysis types."""
        # Calculate number of available analyzers
        n_analyzers = len(self.analyzers)
        
        if n_analyzers == 0:
            return go.Figure()
            
        # Create subplots based on available analyzers
        if n_analyzers == 1:
            rows, cols = 1, 1
        elif n_analyzers == 2:
            rows, cols = 1, 2
        else:
            rows, cols = 2, 2
            
        subplot_titles = []
        
        if 'eeg' in self.analyzers:
            subplot_titles.append('EEG Alpha Power')
        if 'mental' in self.analyzers:
            subplot_titles.append('Mental State Metrics')
        if 'motion' in self.analyzers:
            subplot_titles.append('Head Motion')
        if len(self.analyzers) > 3:
            subplot_titles.append('Cross-Correlations')
            
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=subplot_titles[:rows*cols]
        )
        
        plot_idx = 0
        
        # EEG plot
        if 'eeg' in self.analyzers:
            plot_idx += 1
            row = ((plot_idx - 1) // cols) + 1
            col = ((plot_idx - 1) % cols) + 1
            
            eeg_analyzer = self.analyzers['eeg']
            if eeg_analyzer.channels:
                # Show alpha band power for first channel
                channel = eeg_analyzer.channels[0]
                if channel in eeg_analyzer.eeg_data.columns:
                    eeg_data = eeg_analyzer.eeg_data[channel].dropna()
                    if len(eeg_data) > 100:
                        filtered_data = eeg_analyzer.preprocess_signal(eeg_data)
                        
                        # Calculate alpha power in windows
                        window_size = min(len(filtered_data) // 10, 1000)
                        if window_size > 100:
                            alpha_power = []
                            timestamps = []
                            
                            for i in range(0, len(filtered_data) - window_size, window_size // 2):
                                window_data = filtered_data.iloc[i:i + window_size]
                                band_powers = eeg_analyzer.extract_band_power(window_data)
                                alpha_power.append(band_powers.get('alpha', 0))
                                timestamps.append(window_data.index[len(window_data) // 2])
                            
                            fig.add_trace(
                                go.Scatter(x=timestamps, y=alpha_power,
                                         name=f'Alpha Power ({channel})', mode='lines'),
                                row=row, col=col
                            )
        
        # Mental state plot
        if 'mental' in self.analyzers:
            plot_idx += 1
            row = ((plot_idx - 1) // cols) + 1
            col = ((plot_idx - 1) % cols) + 1
            
            mental_analyzer = self.analyzers['mental']
            if mental_analyzer.metrics:
                # Show first few metrics
                for i, metric in enumerate(mental_analyzer.metrics[:3]):
                    if metric in mental_analyzer.mental_data.columns:
                        data = mental_analyzer.mental_data[metric].dropna()
                        if len(data) > 0:
                            fig.add_trace(
                                go.Scatter(x=data.index, y=data.values,
                                         name=metric.capitalize(), mode='lines'),
                                row=row, col=col
                            )
        
        # Motion plot
        if 'motion' in self.analyzers:
            plot_idx += 1
            row = ((plot_idx - 1) // cols) + 1
            col = ((plot_idx - 1) % cols) + 1
            
            motion_analyzer = self.analyzers['motion']
            angles = motion_analyzer.calculate_head_orientation()
            
            if not angles.empty:
                for angle_type in ['roll', 'pitch', 'yaw']:
                    if angle_type in angles.columns:
                        fig.add_trace(
                            go.Scatter(x=angles.index, y=angles[angle_type],
                                     name=angle_type.capitalize(), mode='lines'),
                            row=row, col=col
                        )
        
        fig.update_layout(
            title="Comprehensive Data Analysis Dashboard",
            height=600 if rows == 1 else 800,
            showlegend=True
        )
        
        return fig
    
    def generate_comprehensive_report(self, output_dir: str = "output") -> str:
        """Generate comprehensive analysis report."""
        os.makedirs(output_dir, exist_ok=True)
        
        report_path = os.path.join(output_dir, "comprehensive_analysis_report.txt")
        
        with open(report_path, 'w') as f:
            f.write("Comprehensive EEG and Sensor Data Analysis Report\n")
            f.write("=" * 60 + "\n\n")
            
            # Session information
            f.write("Session Information:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Data Directory: {self.data_directory}\n")
            
            data_info = self.loader.get_data_info()
            for data_type, info in data_info.items():
                f.write(f"\n{data_type.upper()} Data:\n")
                f.write(f"  Shape: {info['shape']}\n")
                f.write(f"  Duration: {info.get('duration', 'N/A')} seconds\n")
                f.write(f"  Sampling Rate: {info.get('sampling_rate', 'N/A')} Hz\n")
            
            # Individual analysis summaries
            f.write("\n\nAnalysis Summary:\n")
            f.write("-" * 20 + "\n")
            
            if 'eeg' in self.analyzers:
                f.write("\nEEG Analysis:\n")
                eeg_analyzer = self.analyzers['eeg']
                f.write(f"  Channels analyzed: {len(eeg_analyzer.channels)}\n")
                
                # Quick EEG summary
                if eeg_analyzer.channels:
                    sample_channel = eeg_analyzer.channels[0]
                    if sample_channel in eeg_analyzer.eeg_data.columns:
                        data = eeg_analyzer.eeg_data[sample_channel].dropna()
                        f.write(f"  Sample channel ({sample_channel}) statistics:\n")
                        f.write(f"    Mean: {data.mean():.2f} µV\n")
                        f.write(f"    Std: {data.std():.2f} µV\n")
            
            if 'mental' in self.analyzers:
                f.write("\nMental State Analysis:\n")
                mental_analyzer = self.analyzers['mental']
                f.write(f"  Metrics analyzed: {len(mental_analyzer.metrics)}\n")
                
                # Mental state summary
                basic_stats = mental_analyzer.get_basic_statistics()
                if basic_stats:
                    avg_attention = basic_stats.get('attention', {}).get('mean', 0)
                    avg_engagement = basic_stats.get('eng', {}).get('mean', 0)
                    f.write(f"  Average attention: {avg_attention:.3f}\n")
                    f.write(f"  Average engagement: {avg_engagement:.3f}\n")
            
            if 'motion' in self.analyzers:
                f.write("\nMotion Analysis:\n")
                motion_analyzer = self.analyzers['motion']
                angles = motion_analyzer.calculate_head_orientation()
                
                if not angles.empty:
                    f.write("  Head orientation variability:\n")
                    for angle_type in ['roll', 'pitch', 'yaw']:
                        if angle_type in angles.columns:
                            std_dev = angles[angle_type].std()
                            f.write(f"    {angle_type.capitalize()}: {std_dev:.2f}°\n")
            
            # Cross-analysis insights
            correlations = self.analyze_eeg_mental_correlations()
            if correlations:
                f.write("\n\nCross-Analysis Insights:\n")
                f.write("-" * 25 + "\n")
                
                if 'eeg_mental_correlation' in correlations:
                    corr_matrix = correlations['eeg_mental_correlation']
                    # Find strongest correlations
                    max_corr = 0
                    max_pair = None
                    
                    for eeg_col in corr_matrix.index:
                        for mental_col in corr_matrix.columns:
                            corr_val = corr_matrix.loc[eeg_col, mental_col]
                            if not pd.isna(corr_val) and abs(corr_val) > abs(max_corr):
                                max_corr = corr_val
                                max_pair = (eeg_col, mental_col)
                    
                    if max_pair:
                        f.write(f"Strongest EEG-Mental correlation: {max_corr:.3f}\n")
                        f.write(f"  Between {max_pair[0]} and {max_pair[1].replace('met_', '')}\n")
            
            motion_impact = self.analyze_motion_artifact_impact()
            if motion_impact and 'motion_artifact_impact' in motion_impact:
                f.write("\nMotion Artifact Impact:\n")
                impact_data = motion_impact['motion_artifact_impact']
                
                avg_correlation = np.mean([
                    data['motion_correlation'] 
                    for data in impact_data.values() 
                    if not pd.isna(data['motion_correlation'])
                ])
                
                f.write(f"  Average motion-EEG correlation: {avg_correlation:.3f}\n")
                
                avg_ratio = np.mean([
                    data['variability_ratio'] 
                    for data in impact_data.values() 
                    if not pd.isna(data['variability_ratio'])
                ])
                
                f.write(f"  Average variability increase during motion: {avg_ratio:.2f}x\n")
        
        return report_path
    
    def run_full_analysis(self, output_dir: str = "output") -> Dict[str, str]:
        """
        Run complete analysis pipeline and save all outputs.
        
        Args:
            output_dir: Directory to save analysis outputs
            
        Returns:
            Dictionary with paths to generated files
        """
        os.makedirs(output_dir, exist_ok=True)
        output_files = {}
        
        print("Running comprehensive analysis...")
        
        # Generate individual analysis reports
        if 'eeg' in self.analyzers:
            print("- EEG analysis...")
            eeg_report = self.analyzers['eeg'].generate_report(output_dir)
            output_files['eeg_report'] = eeg_report
            
            # EEG visualizations
            summary_fig = self.analyzers['eeg'].plot_all_channels_summary()
            eeg_summary_path = os.path.join(output_dir, "eeg_analysis_summary.html")
            summary_fig.write_html(eeg_summary_path)
            output_files['eeg_summary'] = eeg_summary_path
        
        if 'mental' in self.analyzers:
            print("- Mental state analysis...")
            mental_report = self.analyzers['mental'].generate_mental_state_report(output_dir)
            output_files['mental_report'] = mental_report
            
            # Mental state visualizations
            timeline_fig = self.analyzers['mental'].create_timeline_plot()
            mental_timeline_path = os.path.join(output_dir, "mental_state_timeline.html")
            timeline_fig.write_html(mental_timeline_path)
            output_files['mental_timeline'] = mental_timeline_path
        
        if 'motion' in self.analyzers:
            print("- Motion analysis...")
            motion_report = self.analyzers['motion'].generate_motion_report(output_dir)
            output_files['motion_report'] = motion_report
            
            # Motion visualizations
            motion_fig = self.analyzers['motion'].create_motion_timeline()
            motion_timeline_path = os.path.join(output_dir, "motion_analysis_timeline.html")
            motion_fig.write_html(motion_timeline_path)
            output_files['motion_timeline'] = motion_timeline_path
        
        # Generate integrated analysis
        print("- Integrated analysis...")
        dashboard_fig = self.create_integrated_dashboard()
        dashboard_path = os.path.join(output_dir, "comprehensive_dashboard.html")
        dashboard_fig.write_html(dashboard_path)
        output_files['dashboard'] = dashboard_path
        
        # Generate comprehensive report
        comprehensive_report = self.generate_comprehensive_report(output_dir)
        output_files['comprehensive_report'] = comprehensive_report
        
        print(f"Analysis complete! Results saved to {output_dir}")
        
        return output_files


def main():
    """Main function for standalone execution."""
    import sys
    
    # Get data directory from command line or use default
    data_dir = sys.argv[1] if len(sys.argv) > 1 else "../collected_data"
    
    if not os.path.exists(data_dir):
        print(f"Data directory {data_dir} not found!")
        return
    
    # Create comprehensive analyzer
    analyzer = ComprehensiveAnalyzer(data_dir)
    
    # Run full analysis
    output_files = analyzer.run_full_analysis()
    
    # Print summary of generated files
    print("\nGenerated files:")
    for file_type, file_path in output_files.items():
        print(f"  {file_type}: {file_path}")


if __name__ == "__main__":
    main()
