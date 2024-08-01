import numpy as np
import sqlite3
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging
import datetime

# Initialize logger
logging.basicConfig(level=logging.DEBUG)

# Simulated sensor data variables
sensors = ['Temperature', 'Speed', 'Engine Sensors', 'Brakes', 'Fluid Level', 'Heat', 'Tire Pressure', 'Battery']
num_sensors = len(sensors)

# Placeholder for StandardScaler and IsolationForest
scaler = StandardScaler()
model_if = None

def fetch_historical_data():
    try:
        conn = sqlite3.connect('racing_vehicle_db.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM sensor_data ORDER BY timestamp DESC LIMIT 1000")
        data = cursor.fetchall()
        conn.close()
        return np.array([row[0] for row in data])  # Convert to NumPy array
    except Exception as e:
        logging.error(f"Error fetching historical data from database: {e}")
        return []

def fetch_latest_sensor_values():
    try:
        conn = sqlite3.connect('racing_vehicle_db.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT sensor, value FROM sensor_data ORDER BY timestamp DESC LIMIT ?", (num_sensors,))
        data = cursor.fetchall()
        conn.close()
        
        # Convert to dict and ensure it matches the expected sensor order
        sensor_values = {sensor: None for sensor in sensors}
        for sensor, value in data:
            if sensor in sensor_values:
                sensor_values[sensor] = value
        
        return [sensor_values[sensor] for sensor in sensors]
    
    except Exception as e:
        logging.error(f"Error fetching latest sensor values from database: {e}")
        return [None] * num_sensors

def fit_model():
    global scaler, model_if
    
    try:
        # Fetch historical data from database
        historical_values = fetch_historical_data()
        
        if not historical_values.size:
            logging.warning("No historical data fetched from the database")
            return False
        
        # Scale the historical data
        scaled_values = scaler.fit_transform(historical_values.reshape(-1, 1))
        
        # Initialize Isolation Forest model
        model_if = IsolationForest(contamination=0.05, random_state=42)
        
        # Fit the Isolation Forest model with scaled historical data
        model_if.fit(scaled_values)
        
        logging.info("StandardScaler and IsolationForest fitted successfully.")
        return True
        
    except Exception as e:
        logging.error(f"Error fitting model: {e}")
        return False

def save_anomalies_to_db(anomaly_data):
    try:
        conn = sqlite3.connect('racing_vehicle_db.sqlite')
        cursor = conn.cursor()
        
        # Insert anomalies into the database
        for timestamp, sensor, value, detection_time in anomaly_data:
            cursor.execute("""
                INSERT INTO anomalies (timestamp, sensor, value, detection_time)
                VALUES (?, ?, ?, ?)
            """, (timestamp, sensor, value, detection_time))
        
        conn.commit()
        conn.close()
        logging.info("Anomalies saved to database successfully.")
        
    except Exception as e:
        logging.error(f"Error saving anomalies to database: {e}")

def detect_anomalies(sensor_values):
    try:
        global model_if
        
        # Ensure the model is fitted
        if not model_if:
            fit_success = fit_model()
            if not fit_success:
                return {sensor: False for sensor in sensors}, {sensor: None for sensor in sensors}
        
        anomaly_flags = {}
        anomaly_values = {}
        anomaly_data = []
        
        # Get current timestamp
        current_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Scale each sensor value individually
        for i, sensor_value in enumerate(sensor_values):
            if sensor_value is not None:
                scaled_value = scaler.transform(np.array(sensor_value).reshape(1, -1))
                anomaly_score = model_if.decision_function(scaled_value)  # Use decision_function for anomaly score
                is_anomaly = anomaly_score[0] < 0
                anomaly_flags[sensors[i]] = is_anomaly
                anomaly_values[sensors[i]] = sensor_value if is_anomaly else None
                
                if is_anomaly:
                    anomaly_data.append((current_timestamp, sensors[i], sensor_value, current_timestamp))
            else:
                anomaly_flags[sensors[i]] = False
                anomaly_values[sensors[i]] = None
        
        # Save anomalies to the database
        if anomaly_data:
            save_anomalies_to_db(anomaly_data)
        
        return anomaly_flags, anomaly_values
    
    except Exception as e:
        logging.error(f"Error in anomaly detection: {e}")
        return {sensor: False for sensor in sensors}, {sensor: None for sensor in sensors}

if __name__ == "__main__":
    try:
        # Fetch historical data and fit the model
        fit_model()
        
        # Fetch latest sensor values from the database and detect anomalies
        sensor_values = fetch_latest_sensor_values()
        detected_flags, detected_values = detect_anomalies(sensor_values)
        
        # Print results
        print("Detected Anomalies:")
        for sensor in sensors:
            if detected_flags[sensor]:
                print(f"{sensor}: {detected_values[sensor]:.2f}")
            else:
                print(f"{sensor}: No anomaly detected")
    
    except KeyboardInterrupt:
        print("\nAnomaly detection stopped by the user.")
