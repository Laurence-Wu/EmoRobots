# Emotiv Cortex API Configuration
# Copy this file to 'config.py' and fill in your credentials

# Emotiv App Credentials
# Get these from: https://www.emotiv.com/developer/
CLIENT_ID = 'NvmdNGw376WfpmGcvejE7Q83sIbj5HaFM0IZKg8x'
CLIENT_SECRET = 'tWTOn4sGgFK5HCazFvHTO5BKmskpFhowJO9p8X9n93FHQRp8GiHjcdM2muGjU22a6PVV0uKT4X6jMxJficUIN3HVKC11IbScniRjdcIZDJVCd77IAEfM9WuEcjj6jLQj'

# Optional: License key (if using borrowed license)
LICENSE = ''

# Optional: Specific headset ID (leave empty for auto-detect)
HEADSET_ID = ''

# Data Collection Settings
COLLECTION_DURATION = 30  # seconds
SAVE_TO_FILE = True
OUTPUT_DIRECTORY = 'collected_data'

# Data Streams to Collect
# Available streams: 'eeg', 'mot', 'dev', 'met', 'pow', 'fac', 'com', 'sys'
STREAMS = ['eeg', 'mot', 'dev', 'met', 'pow']
