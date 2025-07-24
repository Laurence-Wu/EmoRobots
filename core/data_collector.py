import os
import time
import csv
from datetime import datetime
from core.cortex import Cortex

class DataCollector:
    """
    A comprehensive data collection class for Emotiv headset data streams.
    
    This class collects and saves multiple data streams:
    - EEG: Raw electroencephalography data
    - Motion: Head motion and orientation data
    - Device: Battery, signal quality, connection status
    - Performance Metrics: Attention, engagement, etc.
    - Band Power: Frequency band analysis
    - Facial Expressions: Eye actions, facial muscle activity
    - Mental Commands: Trained mental command detections
    """
    
    def __init__(self, app_client_id, app_client_secret, **kwargs):
        print("=" * 60)
        print("Initializing Emotiv Data Collector")
        print("=" * 60)
        
        # Initialize data storage
        self.data_buffer = {
            'eeg': [],
            'mot': [],
            'dev': [],
            'met': [],
            'pow': [],
            'fac': [],
            'com': [],
            'sys': []
        }
        
        self.data_labels = {}
        self.collection_start_time = None
        self.collection_duration = 30  # Default 30 seconds
        self.save_to_file = True
        self.output_directory = "collected_data"
        
        # Create output directory if it doesn't exist
        if self.save_to_file and not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        
        # Initialize Cortex connection
        self.c = Cortex(app_client_id, app_client_secret, debug_mode=True, **kwargs)
        
        # Bind event handlers
        self._bind_event_handlers()
        
    def _bind_event_handlers(self):
        self.c.bind(create_session_done=self.on_create_session_done)
        self.c.bind(inform_error=self.on_inform_error)
        self.c.bind(new_data_labels=self.on_new_data_labels)
        self.c.bind(new_eeg_data=self.on_new_eeg_data)
        self.c.bind(new_mot_data=self.on_new_mot_data)
        self.c.bind(new_dev_data=self.on_new_dev_data)
        self.c.bind(new_met_data=self.on_new_met_data)
        self.c.bind(new_pow_data=self.on_new_pow_data)
        self.c.bind(new_fe_data=self.on_new_fe_data)
        self.c.bind(new_com_data=self.on_new_com_data)
        self.c.bind(new_sys_data=self.on_new_sys_data)
        
    def start_collection(self, streams=None, duration=30, headset_id=''):
        if streams is None:
            streams = ['eeg', 'mot', 'dev', 'met', 'pow', 'fac', 'com', 'sys']
        self.streams = streams
        self.collection_duration = duration
        print("\nStarting data collection:")
        print(f"  - Streams: {', '.join(streams)}")
        print(f"  - Duration: {duration} seconds")
        print(f"  - Headset ID: {headset_id if headset_id else 'Auto-detect'}")
        print(f"  - Save to file: {self.save_to_file}")
        if headset_id:
            self.c.set_wanted_headset(headset_id)
        self.c.open()
        
    def subscribe_streams(self):
        print(f"\nSubscribing to data streams: {', '.join(self.streams)}")
        self.c.sub_request(self.streams)
        self.collection_start_time = time.time()
        print(f"Data collection started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        import threading
        stop_timer = threading.Timer(self.collection_duration, self.stop_collection)
        stop_timer.start()
        
    def stop_collection(self):
        print(f"\nStopping data collection after {self.collection_duration} seconds...")
        self.c.unsub_request(self.streams)
        if self.save_to_file:
            self.save_data_to_files()
        self.print_collection_summary()
        self.c.close()
        
    def save_data_to_files(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        for stream_name, data_list in self.data_buffer.items():
            if data_list:
                filename = f"{self.output_directory}/data_{stream_name}_{timestamp}.csv"
                with open(filename, 'w', newline='') as csvfile:
                    if stream_name in self.data_labels:
                        headers = ['timestamp'] + self.data_labels[stream_name]
                    else:
                        headers = ['timestamp'] + [f'value_{i}' for i in range(len(data_list[0]) - 1)]
                    writer = csv.writer(csvfile)
                    writer.writerow(headers)
                    for data_point in data_list:
                        writer.writerow(data_point)
                print(f"  - Saved {len(data_list)} {stream_name} samples to {filename}")
        
    def print_collection_summary(self):
        print("\n" + "=" * 60)
        print("DATA COLLECTION SUMMARY")
        print("=" * 60)
        total_samples = 0
        for stream_name, data_list in self.data_buffer.items():
            count = len(data_list)
            if count > 0:
                total_samples += count
                print(f"  {stream_name.upper():>4}: {count:>6} samples")
        print(f"\n  Total samples collected: {total_samples}")
        print(f"  Collection duration: {self.collection_duration} seconds")
        if total_samples > 0:
            avg_rate = total_samples / self.collection_duration
            print(f"  Average sample rate: {avg_rate:.1f} samples/second")
        
    def on_create_session_done(self, *args, **kwargs):
        print("✓ Session created successfully")
        self.subscribe_streams()
        
    def on_new_data_labels(self, *args, **kwargs):
        data = kwargs.get('data')
        stream_name = data['streamName']
        labels = data['labels']
        self.data_labels[stream_name] = labels
        print(f"✓ Received {stream_name} labels: {len(labels)} channels")
        
    def on_new_eeg_data(self, *args, **kwargs):
        data = kwargs.get('data')
        timestamp = data['time']
        eeg_values = data['eeg']
        row = [timestamp] + eeg_values
        self.data_buffer['eeg'].append(row)
        if len(self.data_buffer['eeg']) % 32 == 0:
            print(f"EEG: {len(self.data_buffer['eeg'])} samples collected")
        
    def on_new_mot_data(self, *args, **kwargs):
        data = kwargs.get('data')
        timestamp = data['time']
        mot_values = data['mot']
        row = [timestamp] + mot_values
        self.data_buffer['mot'].append(row)
        
    def on_new_dev_data(self, *args, **kwargs):
        data = kwargs.get('data')
        timestamp = data['time']
        signal = data['signal']
        dev_values = data['dev']
        battery = data['batteryPercent']
        row = [timestamp, signal, battery] + dev_values
        self.data_buffer['dev'].append(row)
        if len(self.data_buffer['dev']) % 10 == 0:
            print(f"Device: Battery {battery}%, Signal Quality {signal:.1f}")
        
    def on_new_met_data(self, *args, **kwargs):
        data = kwargs.get('data')
        timestamp = data['time']
        met_values = data['met']
        row = [timestamp] + met_values
        self.data_buffer['met'].append(row)
        
    def on_new_pow_data(self, *args, **kwargs):
        data = kwargs.get('data')
        timestamp = data['time']
        pow_values = data['pow']
        row = [timestamp] + pow_values
        self.data_buffer['pow'].append(row)
        
    def on_new_fe_data(self, *args, **kwargs):
        data = kwargs.get('data')
        timestamp = data['time']
        eye_act = data['eyeAct']
        u_act = data['uAct']
        u_pow = data['uPow']
        l_act = data['lAct']
        l_pow = data['lPow']
        row = [timestamp, eye_act, u_act, u_pow, l_act, l_pow]
        self.data_buffer['fac'].append(row)
        
    def on_new_com_data(self, *args, **kwargs):
        data = kwargs.get('data')
        timestamp = data['time']
        action = data['action']
        power = data['power']
        row = [timestamp, action, power]
        self.data_buffer['com'].append(row)
        if action != 'neutral':
            print(f"Mental Command: {action} (power: {power:.2f})")
        
    def on_new_sys_data(self, *args, **kwargs):
        data = kwargs.get('data')
        timestamp = time.time()
        row = [timestamp] + data if isinstance(data, list) else [timestamp, str(data)]
        self.data_buffer['sys'].append(row)
        
    def on_inform_error(self, *args, **kwargs):
        error_data = kwargs.get('error_data')
        print(f"❌ Error: {error_data}") 