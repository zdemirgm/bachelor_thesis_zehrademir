import random
import numpy as np
import sqlite3
import time
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from anomaly_detection import detect_anomalies
from communication_module import CANSimulation
from penetrating_scenarios import scenario_increase_values, scenario_sensor_failure, scenario_noise_injection
from adaptive_mechanisms import adaptive_responses, DRLAgent
from performance_metrics import PerformanceMetrics
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Connect to SQLite database
conn = sqlite3.connect('racing_vehicle_db.sqlite')
cursor = conn.cursor()

# Simulated sensor data variables
sensors = ['Temperature', 'Speed', 'Engine Sensors', 'Brakes', 'Fluid Level', 'Heat', 'Tire Pressure', 'Battery']
num_sensors = len(sensors)

# Initialize lists and dictionaries for sensor data, behavioral data, and adaptive response
sensor_data = {sensor: [] for sensor in sensors}
behavioral_data = {sensor: [0] for sensor in sensors}
adaptive_actions = {sensor: None for sensor in sensors}

# Logistic Regression model for predictive analytics
model_lr = LogisticRegression(random_state=42)

# Deep Reinforcement Learning agent
state_dim = num_sensors
action_dim = len(adaptive_responses)
agent = DRLAgent(state_dim, action_dim)

# Initialize Performance Metrics
performance_metrics = PerformanceMetrics()

def simulate_sensor_values():
    sensor_values = [random.uniform(20, 100) for _ in range(num_sensors)]
    
    # Sequentially apply penetration scenarios
    sensor_values = scenario_increase_values(sensor_values)
    sensor_values = scenario_sensor_failure(sensor_values)
    sensor_values = scenario_noise_injection(sensor_values)
    
    return sensor_values

def restore_sensor_values(sensor_values):
    """Restore sensor values to normal after adaptive actions."""
    for i in range(len(sensor_values)):
        if sensor_values[i] < 20 or sensor_values[i] > 100:
            sensor_values[i] = random.uniform(20, 100)
    return sensor_values

def simulate_and_analyze(can_sim):
    start_time = time.time()
    
    sensor_values = simulate_sensor_values()
    
    # Detect anomalies using the imported function from anomaly_detection.py
    anomaly_flags, anomaly_values = detect_anomalies(sensor_values)
    
    # Perform behavioral analysis (example: use mean feature extraction)
    mean_features = {sensor: np.mean(sensor_data[sensor]) if sensor_data[sensor] else 0 for sensor in sensors}
    for sensor in sensors:
        behavioral_data[sensor].append(mean_features[sensor])
    
    # Preprocess data to handle NaN values before training the model
    X_train = np.array(list(behavioral_data.values())).T
    imputer = SimpleImputer(strategy='mean')  # Example: impute NaNs with mean of the column
    X_train = imputer.fit_transform(X_train)
    
    # Check if X_train has valid features for fitting
    if X_train.shape[1] == 0:
        raise ValueError("No valid features available for training.")
    
    # Train logistic regression model if not already fitted
    if not hasattr(model_lr, 'classes_'):
        # Mock training labels with at least two classes
        y_train = np.array([0, 1] * (X_train.shape[0] // 2))
        model_lr.fit(X_train, y_train[:X_train.shape[0]])  # Fit the model with mock data
    
    # Perform predictive analytics (example: logistic regression for threat prediction)
    feature_set = np.array([mean_features[sensor] for sensor in sensors]).reshape(1, -1)
    feature_set = imputer.transform(feature_set)  # Ensure feature_set is also imputed
    threat_probability = model_lr.predict_proba(feature_set)[:, 1]
    
    # Adaptive response mechanism based on anomaly detection
    state = np.array([mean_features[sensor] for sensor in sensors])
    action, response_time = agent.select_action(state)
    
    for i, sensor in enumerate(sensors):
        if anomaly_flags[sensor]:
            adaptive_actions[sensor] = adaptive_responses[sensor]  # Use adaptive response functions
    
    # Insert sensor values into the SQLite database with their respective names
    try:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        for i, sensor in enumerate(sensors):
            cursor.execute('''INSERT INTO sensor_data (timestamp, sensor, value)
                              VALUES (?, ?, ?)''', (timestamp, sensor, sensor_values[i]))
        conn.commit()
    except Exception as e:
        logging.error(f"Error inserting sensor values into database: {e}")
    
    # Record sensor data in memory for behavioral analysis
    for i, sensor in enumerate(sensors):
        sensor_data[sensor].append(sensor_values[i])
    
    # Publish data to CAN bus
    try:
        can_sim.publish_data(can_id=0x200, data=[int(value) for value in sensor_values])
        can_sim.publish_data(can_id=0x100, data=[int(anomaly_flags[sensor]) for sensor in sensors])
    except Exception as e:
        logging.error(f"Error publishing data to CAN bus: {e}")
    
    # Restore sensor values to normal after adaptive actions
    sensor_values = restore_sensor_values(sensor_values)
    
    # Record performance metrics
    end_time = time.time()
    detection_time = end_time - start_time
    performance_metrics.update_detection_metrics([detection_time, response_time, 1.0 if any(anomaly_flags.values()) else 0.0])
    
    return sensor_values, mean_features, threat_probability, adaptive_actions

# Main loop to run the simulation
if __name__ == "__main__":
    can_sim = CANSimulation()
    can_sim.start()
    
    try:
        while True:
            sensor_values, mean_features, threat_prob, actions = simulate_and_analyze(can_sim)
            
            # Print simulated sensor values
            print("\n--- Simulated Sensor Values ---")
            for sensor, value in zip(sensors, sensor_values):
                print(f"{sensor}: {value:.2f}")
            
            # Print behavioral analysis
            print("\n--- Behavioral Analysis - Mean Features ---")
            for sensor, mean_value in mean_features.items():
                print(f"{sensor}: {mean_value:.2f}")
            
            # Print predictive analytics
            print(f"\n--- Predictive Analytics ---")
            print(f"Threat Probability: {threat_prob[0]:.4f}")
            
            # Print adaptive actions
            print("\n--- Adaptive Actions ---")
            for sensor, action in actions.items():
                if action:
                    print(f"{sensor}: {action}")
                else:
                    print(f"{sensor}: No adaptive action required.")
            
            # Wait before the next simulation iteration
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("Simulation interrupted.")
    
    finally:
        can_sim.stop()
        conn.close()
