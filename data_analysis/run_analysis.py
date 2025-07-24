"""
Simple execution script for data analysis.

Run this script to perform comprehensive analysis of your EEG and sensor data.
"""

import os
import sys
from pathlib import Path

# Add the current directory to the Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

try:
    from comprehensive_analysis import ComprehensiveAnalyzer
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install required dependencies:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def main():
    """Main execution function."""
    print("EEG and Sensor Data Analysis")
    print("=" * 40)
    
    # Determine data directory
    data_dir = "../collected_data"
    
    if not os.path.exists(data_dir):
        print(f"Data directory '{data_dir}' not found!")
        print("Please ensure your CSV files are in the 'collected_data' folder.")
        return
    
    # Check for CSV files
    csv_files = list(Path(data_dir).glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in '{data_dir}'!")
        return
    
    print(f"Found {len(csv_files)} CSV files:")
    for file in csv_files:
        print(f"  - {file.name}")
    
    print("\nStarting analysis...")
    
    try:
        # Create analyzer
        analyzer = ComprehensiveAnalyzer(data_dir)
        
        # Run analysis
        output_files = analyzer.run_full_analysis()
        
        print("\n" + "=" * 40)
        print("Analysis Complete!")
        print("=" * 40)
        
        print("\nGenerated files:")
        for file_type, file_path in output_files.items():
            print(f"  📄 {file_type.replace('_', ' ').title()}: {file_path}")
        
        print("\nTo view results:")
        print("1. Open HTML files in your web browser for interactive visualizations")
        print("2. Read TXT files for detailed analysis reports")
        print("3. Check the 'output' folder for all generated files")
        
    except Exception as e:
        print(f"\nError during analysis: {e}")
        print("Please check that your data files are properly formatted.")
        return


if __name__ == "__main__":
    main()
