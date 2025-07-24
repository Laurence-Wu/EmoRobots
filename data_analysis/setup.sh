#!/bin/bash

# Setup script for EEG Data Analysis
echo "Setting up EEG Data Analysis Environment"
echo "========================================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

echo "✓ Python 3 found"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    exit 1
fi

echo "✓ pip3 found"

# Install required packages
echo ""
echo "Installing required Python packages..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ All packages installed successfully"
else
    echo "✗ Error installing packages"
    exit 1
fi

# Check if data directory exists
if [ ! -d "../collected_data" ]; then
    echo ""
    echo "⚠️  Warning: '../collected_data' directory not found"
    echo "   Please ensure your CSV files are in the collected_data folder"
else
    echo "✓ Data directory found"
    
    # Count CSV files
    csv_count=$(find ../collected_data -name "*.csv" | wc -l)
    echo "✓ Found $csv_count CSV files"
fi

# Create output directory if it doesn't exist
mkdir -p output
echo "✓ Output directory ready"

echo ""
echo "Setup complete! 🎉"
echo ""
echo "To run the analysis:"
echo "  python3 run_analysis.py"
echo ""
echo "To explore data interactively:"
echo "  jupyter notebook exploratory_analysis.ipynb"
echo ""
echo "Generated files will be saved in the 'output' directory."
