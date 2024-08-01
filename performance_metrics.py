import can
import time
import threading
import logging
import sqlite3
from adaptive_mechanisms import DRLAgent
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class PerformanceMetrics:
    def __init__(self):
        # Define paths for the databases in the same folder as the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.racing_db_path = os.path.join(script_dir, 'racing_vehicle_db.sqlite')
        self.metrics_db_path = os.path.join(script_dir, 'metrics_db.sqlite')

        self.detection_times = []
        self.response_times = []
        self.threat_detection_rate = []
        self.lock = threading.Lock()
        self.bus = None
        self.drl_agent = DRLAgent(state_dim=8, action_dim=8)  # Initialize DRLAgent

        # Initialize metrics database
        self.setup_metrics_db()

    def setup_metrics_db(self):
        # Create metrics table if it does not exist
        self.metrics_conn = sqlite3.connect(self.metrics_db_path)  # Connect to the metrics_db
        self.metrics_cursor = self.metrics_conn.cursor()
        self.metrics_cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                detection_time REAL,
                response_time REAL,
                threat_detection_rate REAL
            )
        ''')
        self.metrics_conn.commit()

    def start_can_communication(self):
        self.bus = can.interface.Bus(channel='virtual_can', interface='virtual')
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.start()

    def stop_can_communication(self):
        if self.bus:
            self.bus.shutdown()
        if hasattr(self, 'db_conn'):
            self.db_conn.close()  # Close the racing_vehicle_db connection
        if hasattr(self, 'metrics_conn'):
            self.metrics_conn.close()  # Close the metrics_db connection

    def receive_data(self):
        while True:
            msg = self.bus.recv()
            if msg is not None:
                data = list(msg.data)
                can_id = msg.arbitration_id
                if can_id == 0x100:
                    self.update_detection_metrics(data)
                elif can_id == 0x200:
                    self.update_sensor_data(data)
                elif can_id == 0x300:
                    self.update_plot_data(data)

    def update_detection_metrics(self, data):
        with self.lock:
            self.detection_times.append(data[0])
            self.response_times.append(data[1])
            self.threat_detection_rate = data[2]

    def fetch_sensor_data_with_timestamps(self):
        """Fetch sensor data with timestamps from the database."""
        with sqlite3.connect(self.racing_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sensor, value, timestamp FROM sensor_data ORDER BY timestamp")
            return cursor.fetchall()

    def get_response_time_from_adaptive_mechanisms(self, state):
        # Use DRLAgent to get response time
        _, response_time = self.drl_agent.select_action(state)
        return response_time

    def parse_timestamp(self, timestamp):
        """Convert timestamp to Unix timestamp if necessary."""
        if isinstance(timestamp, str):
            try:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                return dt.timestamp()  # Convert to Unix timestamp
            except ValueError:
                return None
        elif isinstance(timestamp, (int, float)):  # Handle cases where timestamp is already a Unix timestamp
            return float(timestamp)
        else:
            return None

    def calculate_detection_rate(self):
        """Calculate detection rate based on sensor value changes over time."""
        data_with_timestamps = self.fetch_sensor_data_with_timestamps()

        if not data_with_timestamps:
            return 0

        # Filter out records with None values
        filtered_data = [(sensor, value, timestamp) for sensor, value, timestamp in data_with_timestamps if sensor is not None and value is not None and timestamp is not None]

        if not filtered_data:
            return 0

        # Convert timestamps to Unix timestamps
        for i in range(len(filtered_data)):
            sensor, value, timestamp = filtered_data[i]
            timestamp = self.parse_timestamp(timestamp)
            if timestamp is not None:
                filtered_data[i] = (sensor, value, timestamp)
            else:
                filtered_data[i] = (sensor, value, float('inf'))  # Handle invalid timestamps

        # Sort data by sensor and timestamp
        sorted_data = sorted(filtered_data, key=lambda x: (x[0], x[2]))  # (sensor, timestamp)
        
        changes = 0
        total_comparisons = 0

        # Track the last known value for each sensor
        last_values = {}

        for sensor, value, timestamp in sorted_data:
            if sensor in last_values:
                if last_values[sensor] != value:
                    changes += 1
                total_comparisons += 1
            
            last_values[sensor] = value

        detection_rate = changes / total_comparisons if total_comparisons > 0 else 0
        return detection_rate

    def update_metrics_from_db(self):
        """Fetch and return metrics from the database."""
        with self.lock:
            detection_times = self.fetch_sensor_data_with_timestamps()
            # Replace `state` with the actual state when calling this method
            state = [0] * 8  # Dummy state, replace with actual state
            response_time = self.get_response_time_from_adaptive_mechanisms(state)
            detection_rate = self.calculate_detection_rate()
            
            # Save metrics to metrics_db.sqlite
            with sqlite3.connect(self.metrics_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO performance_metrics (detection_time, response_time, threat_detection_rate)
                    VALUES (?, ?, ?)
                ''', (response_time, response_time, detection_rate))
                conn.commit()
            
            return {
                'detection_times': detection_times,
                'response_times': response_time,
                'threat_detection_rate': detection_rate
            }

if __name__ == "__main__":
    performance_metrics = PerformanceMetrics()
    performance_metrics.start_can_communication()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        performance_metrics.stop_can_communication()
