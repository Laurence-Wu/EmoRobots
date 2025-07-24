# Data Analysis Summary

## 📁 Folder Structure

```
data_analysis/
├── README.md                      # Documentation and usage guide
├── requirements.txt               # Python dependencies
├── setup.sh                      # Setup script (run first)
├── run_analysis.py               # Main execution script
├── exploratory_analysis.ipynb    # Interactive Jupyter notebook
├── output/                       # Generated analysis results
│
├── data_loader.py                # Data loading and preprocessing
├── eeg_analysis.py               # EEG signal analysis
├── mental_state_analysis.py      # Mental state metrics analysis
├── motion_analysis.py            # Motion sensor analysis
└── comprehensive_analysis.py     # Integrated multi-modal analysis
```

## 🚀 Quick Start

1. **Setup Environment:**
   ```bash
   ./setup.sh
   ```

2. **Run Complete Analysis:**
   ```bash
   python3 run_analysis.py
   ```

3. **Interactive Exploration:**
   ```bash
   jupyter notebook exploratory_analysis.ipynb
   ```

## 📊 Analysis Modules

### 1. **Data Loader** (`data_loader.py`)
- Loads all CSV files from collected_data folder
- Handles different data types (EEG, mental states, motion, etc.)
- Synchronizes timestamps across data sources
- Provides data quality assessment

### 2. **EEG Analysis** (`eeg_analysis.py`)
- Signal preprocessing (filtering, artifact removal)
- Frequency band analysis (delta, theta, alpha, beta, gamma)
- Power spectral density computation
- Signal quality metrics
- Channel-by-channel analysis

### 3. **Mental State Analysis** (`mental_state_analysis.py`)
- Attention, engagement, excitement analysis
- Stress, relaxation, and interest metrics
- Temporal pattern detection
- State transition analysis
- Correlation between mental states

### 4. **Motion Analysis** (`motion_analysis.py`)
- Head orientation from quaternions
- Acceleration and magnetometer analysis
- Movement detection algorithms
- Head stability assessment
- Motion artifact identification

### 5. **Comprehensive Analysis** (`comprehensive_analysis.py`)
- Integrates all analysis types
- Cross-modal correlations (EEG vs mental states)
- Motion artifact impact on EEG signals
- Unified dashboard and reporting

## 📈 Output Files

### HTML Visualizations (Interactive)
- `eeg_analysis_summary.html` - EEG channel overview
- `mental_state_timeline.html` - Mental metrics over time
- `mental_state_correlations.html` - Correlation heatmaps
- `motion_analysis_timeline.html` - Motion data timeline
- `motion_3d_orientation.html` - 3D head orientation
- `comprehensive_dashboard.html` - Integrated dashboard

### Text Reports (Detailed)
- `eeg_analysis_report.txt` - EEG analysis summary
- `mental_state_analysis_report.txt` - Mental state insights
- `motion_analysis_report.txt` - Motion analysis results
- `comprehensive_analysis_report.txt` - Complete analysis

## 🔍 Data Types Analyzed

### EEG Data (`data_eeg_*.csv`)
- **Channels:** 14 locations (AF3, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8, AF4)
- **Sampling Rate:** ~128 Hz
- **Analysis:** Signal quality, frequency bands, artifacts

### Mental State Data (`data_met_*.csv`)
- **Metrics:** attention, engagement, excitement, stress, relaxation, interest
- **Sampling Rate:** ~2 Hz
- **Analysis:** Temporal patterns, correlations, state transitions

### Motion Data (`data_mot_*.csv`)
- **Sensors:** Quaternions (Q0-Q3), Accelerometer (ACCX-Z), Magnetometer (MAGX-Z)
- **Sampling Rate:** ~10 Hz
- **Analysis:** Head orientation, movement detection, stability

### Power Data (`data_pow_*.csv`)
- **Bands:** Theta, Alpha, Beta (Low/High), Gamma for each channel
- **Sampling Rate:** ~8 Hz
- **Analysis:** Frequency power distributions, brain activity patterns

### Device Data (`data_dev_*.csv`)
- **Metrics:** Signal quality, contact quality for each electrode
- **Sampling Rate:** ~2 Hz
- **Analysis:** Data reliability assessment

## 💡 Key Features

### Signal Processing
- ✅ Digital filtering (high-pass, low-pass, notch)
- ✅ Artifact detection and removal
- ✅ Power spectral density analysis
- ✅ Frequency band extraction

### Machine Learning Ready
- ✅ Feature extraction from all data types
- ✅ Synchronized multi-modal datasets
- ✅ Quality metrics for model training
- ✅ Temporal feature engineering

### Visualization
- ✅ Interactive Plotly dashboards
- ✅ Time series visualizations
- ✅ Correlation heatmaps
- ✅ 3D motion trajectories
- ✅ Statistical distributions

### Research Applications
- ✅ Cognitive load assessment
- ✅ Attention monitoring
- ✅ Stress detection
- ✅ Brain-computer interfaces
- ✅ Neurofeedback systems

## 🛠️ Customization

### Adding New Analysis
1. Create new module following existing patterns
2. Import in `comprehensive_analysis.py`
3. Add to analysis pipeline

### Modifying Parameters
- Filter frequencies in `eeg_analysis.py`
- Window sizes in temporal analysis
- Thresholds for movement detection
- Correlation significance levels

### Custom Visualizations
- Extend plotting functions in each module
- Add new dashboard components
- Create custom report formats

## 📋 Dependencies

- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **matplotlib**: Static plotting
- **seaborn**: Statistical visualization
- **plotly**: Interactive visualizations
- **scipy**: Signal processing and statistics
- **jupyter**: Interactive notebooks
- **scikit-learn**: Machine learning utilities

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**: Run `pip install -r requirements.txt`
2. **No Data Found**: Ensure CSV files are in `../collected_data/`
3. **Memory Issues**: Process data in smaller chunks
4. **Plotting Errors**: Update plotting libraries to latest versions

### Performance Tips

- Use data subsampling for large datasets
- Process channels individually for memory efficiency
- Cache processed results for repeated analysis
- Use background processing for long computations

## 📚 Further Development

### Suggested Enhancements
1. **Real-time Analysis**: Streaming data processing
2. **Advanced ML**: Deep learning models for pattern recognition
3. **Artifact Removal**: ICA-based artifact correction
4. **Connectivity Analysis**: Brain network analysis
5. **Classification**: Automated state classification
6. **Mobile App**: Real-time monitoring interface

### Research Directions
- Cognitive workload prediction
- Emotion recognition from EEG
- Attention training systems
- Sleep quality assessment
- Meditation effectiveness measurement
