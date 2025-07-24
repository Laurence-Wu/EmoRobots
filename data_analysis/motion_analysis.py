"""
Motion Analysis Module

This module analyzes motion data from accelerometer, magnetometer, and quaternion sensors.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import signal
import os
from typing import Dict, List, Tuple, Optional
from data_loader import DataLoader


class MotionAnalyzer:
    """Motion sensor data analysis class."""
    
    def __init__(self, data_loader: DataLoader):
        """Initialize motion analyzer."""
        self.data_loader = data_loader
        self.motion_data = data_loader.loaded_data.get('mot', pd.DataFrame())
        self.sensors = data_loader.get_motion_sensors()
        
        # Define sensor groups
        self.sensor_groups = {
            'quaternion': ['Q0', 'Q1', 'Q2', 'Q3'],
            'accelerometer': ['ACCX', 'ACCY', 'ACCZ'],
            'magnetometer': ['MAGX', 'MAGY', 'MAGZ']
        }
    
    def calculate_head_orientation(self) -> pd.DataFrame:
        """Calculate head orientation from quaternions."""
        if not all(q in self.motion_data.columns for q in self.sensor_groups['quaternion']):
            return pd.DataFrame()
            
        q_data = self.motion_data[self.sensor_groups['quaternion']]
        
        # Calculate Euler angles from quaternions
        angles = pd.DataFrame(index=q_data.index)
        
        for i, row in q_data.iterrows():
            q0, q1, q2, q3 = row['Q0'], row['Q1'], row['Q2'], row['Q3']
            
            # Roll (x-axis rotation)
            sinr_cosp = 2 * (q0 * q1 + q2 * q3)
            cosr_cosp = 1 - 2 * (q1 * q1 + q2 * q2)
            roll = np.arctan2(sinr_cosp, cosr_cosp)
            
            # Pitch (y-axis rotation)
            sinp = 2 * (q0 * q2 - q3 * q1)
            sinp = np.clip(sinp, -1, 1)  # Clamp to avoid numerical errors
            pitch = np.arcsin(sinp)
            
            # Yaw (z-axis rotation)
            siny_cosp = 2 * (q0 * q3 + q1 * q2)
            cosy_cosp = 1 - 2 * (q2 * q2 + q3 * q3)
            yaw = np.arctan2(siny_cosp, cosy_cosp)
            
            angles.loc[i, 'roll'] = np.degrees(roll)
            angles.loc[i, 'pitch'] = np.degrees(pitch)
            angles.loc[i, 'yaw'] = np.degrees(yaw)
            
        return angles
    
    def calculate_acceleration_magnitude(self) -> pd.Series:
        """Calculate total acceleration magnitude."""
        if not all(acc in self.motion_data.columns for acc in self.sensor_groups['accelerometer']):
            return pd.Series()
            
        acc_data = self.motion_data[self.sensor_groups['accelerometer']]
        magnitude = np.sqrt(acc_data['ACCX']**2 + acc_data['ACCY']**2 + acc_data['ACCZ']**2)
        
        return magnitude
    
    def detect_head_movements(self, threshold_angle: float = 5.0, 
                            threshold_acceleration: float = 0.1) -> Dict[str, pd.DataFrame]:
        """
        Detect significant head movements.
        
        Args:
            threshold_angle: Minimum angle change (degrees) to consider movement
            threshold_acceleration: Minimum acceleration change to consider movement
            
        Returns:
            Dictionary with detected movements
        """
        movements = {}
        
        # Orientation-based movement detection
        angles = self.calculate_head_orientation()
        if not angles.empty:
            for angle_type in ['roll', 'pitch', 'yaw']:
                if angle_type in angles.columns:
                    angle_diff = angles[angle_type].diff().abs()
                    significant_movements = angle_diff > threshold_angle
                    
                    movement_events = angles[significant_movements].copy()
                    movement_events['magnitude'] = angle_diff[significant_movements]
                    
                    movements[f'{angle_type}_movement'] = movement_events
        
        # Acceleration-based movement detection
        acc_magnitude = self.calculate_acceleration_magnitude()
        if not acc_magnitude.empty:
            # Remove gravity component (assuming 1g = 9.81 m/s²)
            acc_no_gravity = acc_magnitude - acc_magnitude.median()
            acc_changes = acc_no_gravity.diff().abs()
            
            significant_acc = acc_changes > threshold_acceleration
            acc_events = pd.DataFrame({
                'acceleration': acc_magnitude[significant_acc],
                'change_magnitude': acc_changes[significant_acc]
            })
            
            movements['acceleration_movement'] = acc_events
            
        return movements
    
    def analyze_head_stability(self, window_size: str = '10S') -> Dict[str, pd.DataFrame]:
        """
        Analyze head stability over time.
        
        Args:
            window_size: Window size for stability analysis
            
        Returns:
            Dictionary with stability metrics
        """
        stability_metrics = {}
        
        # Orientation stability
        angles = self.calculate_head_orientation()
        if not angles.empty:
            for angle_type in ['roll', 'pitch', 'yaw']:
                if angle_type in angles.columns:
                    rolling_std = angles[angle_type].rolling(window_size).std()
                    rolling_range = (angles[angle_type].rolling(window_size).max() - 
                                   angles[angle_type].rolling(window_size).min())
                    
                    stability_df = pd.DataFrame({
                        'std_deviation': rolling_std,
                        'range': rolling_range,
                        'stability_score': 1 / (1 + rolling_std)  # Higher score = more stable
                    })
                    
                    stability_metrics[f'{angle_type}_stability'] = stability_df
        
        # Acceleration stability
        acc_magnitude = self.calculate_acceleration_magnitude()
        if not acc_magnitude.empty:
            acc_std = acc_magnitude.rolling(window_size).std()
            acc_stability = pd.DataFrame({
                'std_deviation': acc_std,
                'stability_score': 1 / (1 + acc_std)
            })
            
            stability_metrics['acceleration_stability'] = acc_stability
            
        return stability_metrics
    
    def create_motion_timeline(self) -> go.Figure:
        """Create timeline visualization of motion data."""
        if self.motion_data.empty:
            return go.Figure()
            
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=['Head Orientation', 'Acceleration', 'Magnetometer'],
            vertical_spacing=0.08
        )
        
        # Head orientation
        angles = self.calculate_head_orientation()
        if not angles.empty:
            for angle_type in ['roll', 'pitch', 'yaw']:
                if angle_type in angles.columns:
                    fig.add_trace(
                        go.Scatter(x=angles.index, y=angles[angle_type],
                                 name=angle_type.capitalize(), mode='lines'),
                        row=1, col=1
                    )
        
        # Acceleration
        if all(acc in self.motion_data.columns for acc in self.sensor_groups['accelerometer']):
            for acc_axis in ['ACCX', 'ACCY', 'ACCZ']:
                fig.add_trace(
                    go.Scatter(x=self.motion_data.index, y=self.motion_data[acc_axis],
                             name=acc_axis, mode='lines'),
                    row=2, col=1
                )
        
        # Magnetometer
        if all(mag in self.motion_data.columns for mag in self.sensor_groups['magnetometer']):
            for mag_axis in ['MAGX', 'MAGY', 'MAGZ']:
                fig.add_trace(
                    go.Scatter(x=self.motion_data.index, y=self.motion_data[mag_axis],
                             name=mag_axis, mode='lines'),
                    row=3, col=1
                )
        
        fig.update_layout(
            title="Motion Sensor Data Timeline",
            height=900,
            showlegend=True
        )
        
        return fig
    
    def create_3d_orientation_plot(self, sample_rate: int = 10) -> go.Figure:
        """Create 3D visualization of head orientation."""
        angles = self.calculate_head_orientation()
        
        if angles.empty:
            return go.Figure()
            
        # Sample data to avoid overcrowding
        sampled_angles = angles.iloc[::sample_rate]
        
        fig = go.Figure(data=go.Scatter3d(
            x=sampled_angles['roll'],
            y=sampled_angles['pitch'],
            z=sampled_angles['yaw'],
            mode='markers+lines',
            marker={
                'size': 3,
                'color': range(len(sampled_angles)),
                'colorscale': 'Viridis',
                'showscale': True,
                'colorbar': {'title': 'Time Progress'}
            },
            line={'width': 2}
        ))
        
        fig.update_layout(
            title="3D Head Orientation Trajectory",
            scene={
                'xaxis_title': 'Roll (degrees)',
                'yaxis_title': 'Pitch (degrees)',
                'zaxis_title': 'Yaw (degrees)'
            },
            height=700
        )
        
        return fig
    
    def create_stability_plot(self) -> go.Figure:
        """Create visualization of head stability metrics."""
        stability_metrics = self.analyze_head_stability()
        
        if not stability_metrics:
            return go.Figure()
            
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Roll Stability', 'Pitch Stability', 
                          'Yaw Stability', 'Acceleration Stability']
        )
        
        plot_positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        stability_keys = ['roll_stability', 'pitch_stability', 
                         'yaw_stability', 'acceleration_stability']
        
        for i, (key, (row, col)) in enumerate(zip(stability_keys, plot_positions)):
            if key in stability_metrics:
                stability_data = stability_metrics[key]
                
                if 'stability_score' in stability_data.columns:
                    fig.add_trace(
                        go.Scatter(x=stability_data.index, 
                                 y=stability_data['stability_score'],
                                 name=f'{key.replace("_", " ").title()}',
                                 mode='lines'),
                        row=row, col=col
                    )
        
        fig.update_layout(
            title="Head Stability Analysis",
            height=600,
            showlegend=False
        )
        
        return fig
    
    def generate_motion_report(self, output_dir: str = "output") -> str:
        """Generate comprehensive motion analysis report."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Perform analyses
        angles = self.calculate_head_orientation()
        movements = self.detect_head_movements()
        stability = self.analyze_head_stability()
        
        report_path = os.path.join(output_dir, "motion_analysis_report.txt")
        
        with open(report_path, 'w') as f:
            f.write("Motion Analysis Report\n")
            f.write("=" * 30 + "\n\n")
            
            f.write("Dataset Overview:\n")
            f.write(f"- Motion data shape: {self.motion_data.shape}\n")
            f.write(f"- Available sensors: {', '.join(self.sensors)}\n")
            f.write(f"- Data duration: {len(self.motion_data)} samples\n\n")
            
            # Head orientation analysis
            if not angles.empty:
                f.write("Head Orientation Analysis:\n")
                f.write("-" * 30 + "\n")
                for angle_type in ['roll', 'pitch', 'yaw']:
                    if angle_type in angles.columns:
                        angle_data = angles[angle_type].dropna()
                        f.write(f"\n{angle_type.capitalize()}:\n")
                        f.write(f"  Mean: {angle_data.mean():.2f}°\n")
                        f.write(f"  Std: {angle_data.std():.2f}°\n")
                        f.write(f"  Range: {angle_data.min():.2f}° to {angle_data.max():.2f}°\n")
            
            # Movement detection
            f.write("\n\nMovement Detection:\n")
            f.write("-" * 20 + "\n")
            total_movements = 0
            for movement_type, movement_data in movements.items():
                count = len(movement_data)
                total_movements += count
                f.write(f"{movement_type.replace('_', ' ').title()}: {count} events\n")
                
                if count > 0 and 'magnitude' in movement_data.columns:
                    f.write(f"  Average magnitude: {movement_data['magnitude'].mean():.2f}\n")
                    f.write(f"  Max magnitude: {movement_data['magnitude'].max():.2f}\n")
            
            f.write(f"\nTotal movement events: {total_movements}\n")
            
            # Stability analysis
            if stability:
                f.write("\n\nStability Analysis:\n")
                f.write("-" * 20 + "\n")
                for stability_type, stability_data in stability.items():
                    if 'stability_score' in stability_data.columns:
                        scores = stability_data['stability_score'].dropna()
                        if len(scores) > 0:
                            f.write(f"{stability_type.replace('_', ' ').title()}:\n")
                            f.write(f"  Average stability: {scores.mean():.3f}\n")
                            f.write(f"  Min stability: {scores.min():.3f}\n")
                            f.write(f"  Max stability: {scores.max():.3f}\n\n")
        
        return report_path


def main():
    """Main function for standalone execution."""
    from data_loader import load_session_data
    
    # Load data
    data_dir = "../collected_data"
    loader, data = load_session_data(data_dir)
    
    if 'mot' not in data or data['mot'].empty:
        print("No motion data found!")
        return
    
    # Create analyzer
    analyzer = MotionAnalyzer(loader)
    
    print("Performing motion analysis...")
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Generate plots
    timeline_fig = analyzer.create_motion_timeline()
    timeline_fig.write_html("output/motion_timeline.html")
    print("Motion timeline saved to output/motion_timeline.html")
    
    orientation_fig = analyzer.create_3d_orientation_plot()
    orientation_fig.write_html("output/motion_3d_orientation.html")
    print("3D orientation plot saved to output/motion_3d_orientation.html")
    
    stability_fig = analyzer.create_stability_plot()
    stability_fig.write_html("output/motion_stability.html")
    print("Stability plot saved to output/motion_stability.html")
    
    # Generate report
    report_path = analyzer.generate_motion_report()
    print(f"Motion analysis report saved to {report_path}")


if __name__ == "__main__":
    main()
