# Data Analysis for EEG and Sensor Data

This folder contains comprehensive analysis tools for the collected EEG and sensor data from the Emotiv device.

## Files Description

### Data Types
- `data_eeg_*.csv`: Raw EEG signals from 14 channels (AF3, F7, F3, FC5, T7, P7, O1, O2, P8, T8, FC6, F4, F8, AF4)
- `data_met_*.csv`: Mental state metrics (attention, engagement, excitement, lexical, stress, relaxation, interest)
- `data_mot_*.csv`: Motion data (quaternions, accelerometer, magnetometer)
- `data_pow_*.csv`: Power spectral density across frequency bands (theta, alpha, beta low/high, gamma)
- `data_dev_*.csv`: Device quality and contact quality metrics

### Analysis Scripts

1. **`data_loader.py`**: Unified data loading and preprocessing utilities
2. **`eeg_analysis.py`**: EEG signal analysis including filtering, spectral analysis, and visualization
3. **`mental_state_analysis.py`**: Analysis of mental state metrics and correlations
4. **`motion_analysis.py`**: Motion data analysis and head movement detection
5. **`power_analysis.py`**: Frequency band power analysis and brain activity patterns
6. **`comprehensive_analysis.py`**: Combined analysis across all data types
7. **`visualization_dashboard.py`**: Interactive dashboard for data exploration

### Jupyter Notebooks
- `exploratory_analysis.ipynb`: Interactive exploration of the dataset
- `signal_processing.ipynb`: Advanced signal processing techniques
- `machine_learning.ipynb`: ML models for emotion/state classification

## Usage

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Run comprehensive analysis:
```python
python comprehensive_analysis.py
```

3. Launch interactive dashboard:
```python
python visualization_dashboard.py
```

4. For interactive exploration, use the Jupyter notebooks:
```bash
jupyter notebook exploratory_analysis.ipynb
```

## Output

Analysis results will be saved in the `output/` directory with:
- Statistical summaries
- Visualizations (plots and charts)
- Processed data files
- Analysis reports
