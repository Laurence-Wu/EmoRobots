"""
Mental State Analysis Module

This module analyzes mental state metrics from the Emotiv device including:
- Attention, engagement, excitement levels
- Stress and relaxation metrics
- Temporal patterns and correlations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
import os
from typing import Dict, List, Tuple, Optional
from data_loader import DataLoader


class MentalStateAnalyzer:
    """Comprehensive mental state metrics analysis class."""
    
    def __init__(self, data_loader: DataLoader):
        """
        Initialize mental state analyzer.
        
        Args:
            data_loader: DataLoader instance with loaded data
        """
        self.data_loader = data_loader
        self.mental_data = data_loader.loaded_data.get('met', pd.DataFrame())
        self.metrics = data_loader.get_mental_state_metrics()
        
        # Define metric categories
        self.metric_categories = {
            'cognitive': ['attention', 'eng'],  # engagement
            'emotional': ['exc', 'str', 'rel'],  # excitement, stress, relaxation
            'other': ['lex', 'int']  # lexical, interest
        }
        
    def get_basic_statistics(self) -> Dict[str, Dict]:
        """
        Calculate basic statistics for all mental state metrics.
        
        Returns:
            Dictionary with statistics for each metric
        """
        stats_results = {}
        
        for metric in self.metrics:
            if metric in self.mental_data.columns:
                data = self.mental_data[metric].dropna()
                
                if len(data) > 0:
                    stats_results[metric] = {
                        'mean': data.mean(),
                        'median': data.median(),
                        'std': data.std(),
                        'min': data.min(),
                        'max': data.max(),
                        'range': data.max() - data.min(),
                        'cv': data.std() / data.mean() if data.mean() != 0 else 0,
                        'skewness': stats.skew(data),
                        'kurtosis': stats.kurtosis(data),
                        'q25': data.quantile(0.25),
                        'q75': data.quantile(0.75)
                    }
                    
        return stats_results
    
    def analyze_temporal_patterns(self, window_size: str = '30S') -> Dict[str, pd.DataFrame]:
        """
        Analyze temporal patterns in mental state metrics.
        
        Args:
            window_size: Window size for rolling statistics
            
        Returns:
            Dictionary with temporal analysis results
        """
        temporal_results = {}
        
        for metric in self.metrics:
            if metric in self.mental_data.columns:
                data = self.mental_data[metric].dropna()
                
                if len(data) > 0:
                    # Rolling statistics
                    rolling_stats = pd.DataFrame({
                        'mean': data.rolling(window_size).mean(),
                        'std': data.rolling(window_size).std(),
                        'min': data.rolling(window_size).min(),
                        'max': data.rolling(window_size).max()
                    })
                    
                    temporal_results[metric] = rolling_stats
                    
        return temporal_results
    
    def compute_correlations(self) -> pd.DataFrame:
        """
        Compute correlation matrix between mental state metrics.
        
        Returns:
            Correlation matrix DataFrame
        """
        # Select only numeric mental state columns
        metric_data = self.mental_data[self.metrics]
        
        # Remove any non-numeric columns that might have slipped through
        numeric_columns = metric_data.select_dtypes(include=[np.number]).columns
        correlation_matrix = metric_data[numeric_columns].corr()
        
        return correlation_matrix
    
    def detect_state_changes(self, threshold_std: float = 2.0) -> Dict[str, pd.DataFrame]:
        """
        Detect significant changes in mental states.
        
        Args:
            threshold_std: Number of standard deviations for change detection
            
        Returns:
            Dictionary with detected changes for each metric
        """
        changes = {}
        
        for metric in self.metrics:
            if metric in self.mental_data.columns:
                data = self.mental_data[metric].dropna()
                
                if len(data) > 10:  # Need sufficient data
                    # Calculate rolling mean and std
                    rolling_mean = data.rolling(window=10, center=True).mean()
                    rolling_std = data.rolling(window=10, center=True).std()
                    
                    # Detect outliers
                    z_scores = np.abs((data - rolling_mean) / rolling_std)
                    significant_changes = z_scores > threshold_std
                    
                    change_points = data[significant_changes].reset_index()
                    change_points['z_score'] = z_scores[significant_changes].values
                    change_points['change_magnitude'] = np.abs(
                        data[significant_changes] - rolling_mean[significant_changes]
                    ).values
                    
                    changes[metric] = change_points
                    
        return changes
    
    def analyze_state_transitions(self, quantile_bins: int = 3) -> Dict[str, pd.DataFrame]:
        """
        Analyze transitions between different mental state levels.
        
        Args:
            quantile_bins: Number of quantile bins to create (low, medium, high states)
            
        Returns:
            Dictionary with transition matrices for each metric
        """
        transitions = {}
        
        for metric in self.metrics:
            if metric in self.mental_data.columns:
                data = self.mental_data[metric].dropna()
                
                if len(data) > 0:
                    # Create quantile bins
                    data_binned = pd.qcut(data, q=quantile_bins, 
                                        labels=[f'Low', f'Medium', f'High'])
                    
                    # Create transition matrix
                    transition_matrix = pd.DataFrame(
                        index=data_binned.cat.categories,
                        columns=data_binned.cat.categories,
                        dtype=float
                    ).fillna(0)
                    
                    # Count transitions
                    for i in range(len(data_binned) - 1):
                        current_state = data_binned.iloc[i]
                        next_state = data_binned.iloc[i + 1]
                        
                        if pd.notna(current_state) and pd.notna(next_state):
                            transition_matrix.loc[current_state, next_state] += 1
                    
                    # Normalize to get probabilities
                    row_sums = transition_matrix.sum(axis=1)
                    transition_matrix = transition_matrix.div(row_sums, axis=0).fillna(0)
                    
                    transitions[metric] = transition_matrix
                    
        return transitions
    
    def create_timeline_plot(self, metrics_to_plot: List[str] = None) -> go.Figure:
        """
        Create timeline plot of mental state metrics.
        
        Args:
            metrics_to_plot: List of metrics to plot (default: all)
            
        Returns:
            Plotly figure
        """
        if metrics_to_plot is None:
            metrics_to_plot = self.metrics[:6]  # Limit to first 6 for readability
            
        fig = go.Figure()
        
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
        
        for i, metric in enumerate(metrics_to_plot):
            if metric in self.mental_data.columns:
                data = self.mental_data[metric].dropna()
                
                if len(data) > 0:
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data.values,
                        mode='lines',
                        name=metric.capitalize(),
                        line={'color': colors[i % len(colors)]}
                    ))
        
        fig.update_layout(
            title="Mental State Metrics Over Time",
            xaxis_title="Time",
            yaxis_title="Metric Value",
            hovermode='x unified',
            height=600
        )
        
        return fig
    
    def create_correlation_heatmap(self) -> go.Figure:
        """Create correlation heatmap of mental state metrics."""
        correlation_matrix = self.compute_correlations()
        
        if correlation_matrix.empty:
            return go.Figure()
            
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title="Mental State Metrics Correlation Matrix",
            height=600,
            width=800
        )
        
        return fig
    
    def create_distribution_plots(self) -> go.Figure:
        """Create distribution plots for all metrics."""
        n_metrics = len(self.metrics)
        if n_metrics == 0:
            return go.Figure()
            
        # Calculate subplot layout
        cols = min(3, n_metrics)
        rows = (n_metrics + cols - 1) // cols
        
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=[metric.capitalize() for metric in self.metrics],
            vertical_spacing=0.08
        )
        
        for i, metric in enumerate(self.metrics):
            if metric in self.mental_data.columns:
                data = self.mental_data[metric].dropna()
                
                if len(data) > 0:
                    row = i // cols + 1
                    col = i % cols + 1
                    
                    fig.add_trace(
                        go.Histogram(x=data.values, name=metric, nbinsx=30),
                        row=row, col=col
                    )
        
        fig.update_layout(
            title="Distribution of Mental State Metrics",
            height=200 * rows,
            showlegend=False
        )
        
        return fig
    
    def create_state_transition_plot(self, metric: str) -> go.Figure:
        """
        Create transition matrix visualization for a specific metric.
        
        Args:
            metric: Mental state metric to analyze
            
        Returns:
            Plotly figure
        """
        transitions = self.analyze_state_transitions()
        
        if metric not in transitions:
            return go.Figure()
            
        transition_matrix = transitions[metric]
        
        fig = go.Figure(data=go.Heatmap(
            z=transition_matrix.values,
            x=transition_matrix.columns,
            y=transition_matrix.index,
            colorscale='Blues',
            text=transition_matrix.round(3).values,
            texttemplate="%{text}",
            textfont={"size": 12}
        ))
        
        fig.update_layout(
            title=f"State Transition Probabilities - {metric.capitalize()}",
            xaxis_title="Next State",
            yaxis_title="Current State",
            height=500,
            width=500
        )
        
        return fig
    
    def generate_mental_state_report(self, output_dir: str = "output") -> str:
        """
        Generate comprehensive mental state analysis report.
        
        Args:
            output_dir: Directory to save the report
            
        Returns:
            Path to the generated report
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Perform analyses
        basic_stats = self.get_basic_statistics()
        correlations = self.compute_correlations()
        state_changes = self.detect_state_changes()
        
        report_path = os.path.join(output_dir, "mental_state_analysis_report.txt")
        
        with open(report_path, 'w') as f:
            f.write("Mental State Analysis Report\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("Dataset Overview:\n")
            f.write(f"- Number of metrics: {len(self.metrics)}\n")
            f.write(f"- Available metrics: {', '.join(self.metrics)}\n")
            f.write(f"- Data duration: {len(self.mental_data)} samples\n\n")
            
            # Basic statistics
            f.write("Basic Statistics:\n")
            f.write("-" * 20 + "\n")
            for metric, stats in basic_stats.items():
                f.write(f"\n{metric.capitalize()}:\n")
                f.write(f"  Mean: {stats['mean']:.3f}\n")
                f.write(f"  Median: {stats['median']:.3f}\n")
                f.write(f"  Std Dev: {stats['std']:.3f}\n")
                f.write(f"  Range: {stats['min']:.3f} - {stats['max']:.3f}\n")
                f.write(f"  Coefficient of Variation: {stats['cv']:.3f}\n")
            
            # Correlations
            f.write("\n\nStrongest Correlations:\n")
            f.write("-" * 25 + "\n")
            if not correlations.empty:
                # Find strongest correlations (excluding self-correlations)
                correlation_pairs = []
                for i in range(len(correlations.columns)):
                    for j in range(i+1, len(correlations.columns)):
                        corr_value = correlations.iloc[i, j]
                        if not np.isnan(corr_value):
                            correlation_pairs.append((
                                correlations.columns[i],
                                correlations.columns[j],
                                corr_value
                            ))
                
                # Sort by absolute correlation value
                correlation_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
                
                for metric1, metric2, corr in correlation_pairs[:5]:  # Top 5
                    f.write(f"  {metric1} - {metric2}: {corr:.3f}\n")
            
            # State changes
            f.write("\n\nSignificant State Changes Detected:\n")
            f.write("-" * 35 + "\n")
            for metric, changes in state_changes.items():
                if len(changes) > 0:
                    f.write(f"\n{metric.capitalize()}: {len(changes)} significant changes\n")
                    if len(changes) > 0:
                        f.write(f"  Largest change: {changes['change_magnitude'].max():.3f}\n")
                        f.write(f"  Average change: {changes['change_magnitude'].mean():.3f}\n")
        
        return report_path


def main():
    """Main function for standalone execution."""
    from data_loader import load_session_data
    
    # Load data
    data_dir = "../collected_data"
    loader, data = load_session_data(data_dir)
    
    if 'met' not in data or data['met'].empty:
        print("No mental state data found!")
        return
    
    # Create analyzer
    analyzer = MentalStateAnalyzer(loader)
    
    print("Performing mental state analysis...")
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Generate plots
    timeline_fig = analyzer.create_timeline_plot()
    timeline_fig.write_html("output/mental_state_timeline.html")
    print("Timeline plot saved to output/mental_state_timeline.html")
    
    correlation_fig = analyzer.create_correlation_heatmap()
    correlation_fig.write_html("output/mental_state_correlations.html")
    print("Correlation heatmap saved to output/mental_state_correlations.html")
    
    distribution_fig = analyzer.create_distribution_plots()
    distribution_fig.write_html("output/mental_state_distributions.html")
    print("Distribution plots saved to output/mental_state_distributions.html")
    
    # Generate report
    report_path = analyzer.generate_mental_state_report()
    print(f"Mental state analysis report saved to {report_path}")


if __name__ == "__main__":
    main()
