#!/usr/bin/env python3
"""
Data Collector Test Script for Emotiv Cortex API

This script demonstrates how to collect various data streams from an Emotiv headset
including EEG, motion, device info, performance metrics, band power, facial expressions,
and mental commands.

Usage:
    python data_collector_test.py

Requirements:
    - Emotiv headset connected via Bluetooth or USB dongle
    - Emotiv Launcher running
    - Valid app credentials (client ID and secret)
"""

import sys
import time
import json
import csv
import os
from datetime import datetime
from data_collector import DataCollector
from dotenv import load_dotenv


def main():
    """Main function to run the data collection test."""
    print("EMOTIV CORTEX DATA COLLECTION TEST")
    print("=" * 60)

    # Load environment variables
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
    your_app_client_id = os.getenv('CLIENT_ID')
    your_app_client_secret = os.getenv('CLIENT_SECRET')
    
    # Validate credentials
    if not your_app_client_id or not your_app_client_secret:
        print("❌ ERROR: Please fill in your app credentials before running the script")
        print("   - Edit this file and set your_app_client_id and your_app_client_secret")
        print("   - Get credentials from: https://www.emotiv.com/developer/")
        sys.exit(1)
    
    try:
        # Create data collector
        collector = DataCollector(your_app_client_id, your_app_client_secret)
        
        # Configuration options
        streams_to_collect = ['eeg', 'mot', 'dev', 'met', 'pow']  # Basic streams
        # For all streams including facial expressions and mental commands:
        # streams_to_collect = ['eeg', 'mot', 'dev', 'met', 'pow', 'fac', 'com']
        
        collection_duration = 30  # seconds
        
        # Start collection
        collector.start_collection(
            streams=streams_to_collect,
            duration=collection_duration,
            headset_id=''  # Auto-detect headset
        )
        
    except KeyboardInterrupt:
        print("\n⚠️ Collection interrupted by user")
    except Exception as e:
        print(f"❌ Error during collection: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
