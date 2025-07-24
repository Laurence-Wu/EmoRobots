
# EmoRobots - Emotiv Cortex API Python Framework

A comprehensive and organized Python framework for working with the [Emotiv Cortex API](https://emotiv.gitbook.io/cortex-api). This project provides structured modules and scripts for EEG data collection, processing, and analysis with Emotiv headsets.

## Project Structure

```
EmoRobots/
├── core/                    # Core logic and reusable classes
│   ├── cortex.py           # Main Cortex API wrapper
│   └── data_collector.py   # Data collection utilities
├── scripts/                # Executable scripts and examples
│   ├── data_collector_test.py      # Comprehensive data collection demo
│   ├── sub_data.py                 # Subscribe to data streams
│   ├── record.py                   # Record and export data
│   ├── marker.py                   # Inject markers during recording
│   ├── mental_command_train.py     # Mental command training
│   ├── facial_expression_train.py  # Facial expression training
│   └── live_advance.py             # Advanced live data processing
├── config/                 # Configuration templates and settings
│   └── config_template.py  # Configuration template
├── collected_data/         # Data output directory (auto-created)
├── data_analysis/          # Analysis scripts and tools
└── requirements.txt        # Project dependencies
```

## Requirements

- Python 3.6+
- Emotiv headset (physical or virtual)
- Emotiv Launcher
- Install dependencies: `pip install -r requirements.txt`

## Dependencies

- `websocket-client` - WebSocket communication with Cortex API
- `python-dispatch` - Event handling and dispatching
- `python-dotenv` - Environment variable management

## Getting Started

### 1. Setup Environment

1. **Download EMOTIV Launcher**: Get it from [emotiv.com](https://www.emotiv.com/products/emotiv-launcher)
2. **Create Emotiv Account**: Register at [emotiv.com](https://id.emotivcloud.com/eoidc/account/registration/)
3. **Get API Credentials**: Create a Cortex app in your [Emotiv account](https://www.emotiv.com/my-account/cortex-apps/)
4. **Setup Headset**: Connect a physical headset or create a virtual device in Emotiv Launcher

### 2. Configure Credentials

Create a `.env` file in the project root:
```bash
CLIENT_ID=your_emotiv_client_id
CLIENT_SECRET=your_emotiv_client_secret
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage Examples

### Basic Data Collection
```bash
python scripts/data_collector_test.py
```
Collects EEG, motion, device info, and performance metrics for 30 seconds.

### Subscribe to Live Data Streams
```bash
python scripts/sub_data.py
```
Demonstrates real-time data subscription and processing.

### Record and Export Data
```bash
python scripts/record.py
```
Shows how to create recordings and export to CSV/EDF formats.

### Training Mental Commands
```bash
python scripts/mental_command_train.py
```
Interactive training for mental command detection (push, pull, etc.).

### Training Facial Expressions
```bash
python scripts/facial_expression_train.py
```
Interactive training for facial expression detection (smile, surprise, etc.).

## Core Modules

### `core.cortex.Cortex`
Central API wrapper handling:
- WebSocket connections to Cortex API
- JSON-RPC request/response management
- Event dispatching and error handling
- Session and stream management

### `core.data_collector.DataCollector`
Comprehensive data collection class featuring:
- Multi-stream data collection (EEG, motion, device, etc.)
- Automatic file saving with timestamps
- Event-driven data processing
- Configurable collection parameters

## Data Analysis

The `data_analysis/` directory contains tools for:
- EEG signal analysis and visualization
- Mental state analysis and metrics
- Motion data processing
- Comprehensive reporting and dashboards

Run analysis scripts:
```bash
cd data_analysis
python run_analysis.py
```

## Configuration

- Copy `config/config_template.py` to create your own configuration
- Set environment variables in `.env` file
- Customize data collection parameters in scripts

## Data Output

- **collected_data/**: Raw data files (CSV format)
- **data_analysis/output/**: Analysis results and visualizations
- Files are automatically timestamped and organized by data type

## Development

### Adding New Scripts
1. Place executable scripts in `scripts/`
2. Import core modules: `from core.cortex import Cortex`
3. Follow existing patterns for error handling and logging

### Extending Core Functionality
1. Add reusable classes to `core/`
2. Update `__init__.py` files for proper imports
3. Maintain backward compatibility with existing scripts

## API Documentation

For detailed API information, refer to:
- [Emotiv Cortex API Documentation](https://emotiv.gitbook.io/cortex-api/)
- [Data Subscription Guide](https://emotiv.gitbook.io/cortex-api/data-subscription)
- [BCI Training Guide](https://emotiv.gitbook.io/cortex-api/bci)

## License

This project follows Emotiv's terms of service and API usage guidelines.

## Contributing

1. Follow the existing project structure
2. Add comprehensive docstrings and comments
3. Test with both physical and virtual headsets
4. Update README for any new features

## Troubleshooting

- Ensure Emotiv Launcher is running before executing scripts
- Check headset connection and battery status
- Verify API credentials in `.env` file
- Review Cortex API logs for detailed error information


