import time
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import sqlite3
import logging

# Initialize logger
logging.basicConfig(level=logging.DEBUG)

# Define adaptive responses
adaptive_responses = {
    'Temperature': 'Adjust temperature sensor calibration',
    'Speed': 'Notify maintenance team for speed sensor',
    'Engine Sensors': 'Perform engine diagnostics',
    'Brakes': 'Check brake system immediately',
    'Fluid Level': 'Refill fluid levels or check for leaks',
    'Heat': 'Inspect cooling system',
    'Tire Pressure': 'Check tire pressure and adjust',
    'Battery': 'Replace or recharge battery'
}

class DRLAgent:
    def __init__(self, state_dim, action_dim):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Define DNN model for DRL
        self.model = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        ).to(self.device)
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()
    
    def select_action(self, state):
        start_time = time.time()  # Start timing
        state = torch.FloatTensor(state).to(self.device)
        q_values = self.model(state)
        action = torch.argmax(q_values).item()
        end_time = time.time()  # End timing
        
        # Calculate response time
        response_time = end_time - start_time
        
        return action, response_time
    
    def train(self, state, action, reward, next_state, done):
        state = torch.FloatTensor(state).to(self.device)
        next_state = torch.FloatTensor(next_state).to(self.device)
        action = torch.LongTensor([action]).to(self.device)
        reward = torch.FloatTensor([reward]).to(self.device)
        
        # Compute Q-values
        q_values = self.model(state)
        next_q_values = self.model(next_state)
        next_q_value = torch.max(next_q_values)
        
        # Compute expected Q-value
        expected_q_value = reward + 0.99 * next_q_value * (1 - done)
        
        # Compute loss
        loss = self.criterion(q_values.gather(1, action.unsqueeze(1)), expected_q_value.detach())
        
        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

def fetch_latest_sensor_values():
    try:
        conn = sqlite3.connect('racing_vehicle_db.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT sensor, value FROM sensor_data ORDER BY timestamp DESC LIMIT 8")  # Fetch latest 8 sensors
        data = cursor.fetchall()
        conn.close()
        
        # Convert to dict and ensure it matches the expected sensor order
        sensor_values = {sensor: None for sensor in adaptive_responses.keys()}
        for sensor, value in data:
            if sensor in sensor_values:
                sensor_values[sensor] = value
        
        return [sensor_values[sensor] for sensor in adaptive_responses.keys()]
    
    except Exception as e:
        logging.error(f"Error fetching latest sensor values from database: {e}")
        return [None] * len(adaptive_responses)

def apply_adaptive_response(sensor_values):
    try:
        # Initialize DRL agent
        state_dim = len(sensor_values)
        action_dim = len(adaptive_responses)
        agent = DRLAgent(state_dim, action_dim)
        
        # Convert sensor values to state
        state = np.array(sensor_values).astype(float)
        
        # Select action based on state
        action_index, response_time = agent.select_action(state)
        
        # Map action index to adaptive response
        action = list(adaptive_responses.values())[action_index]
        
        # Log and apply the adaptive response
        logging.info(f"Applying adaptive response: {action} with response time: {response_time:.4f} seconds")
        
        return action
    
    except Exception as e:
        logging.error(f"Error applying adaptive response: {e}")
        return "No response applied"

if __name__ == "__main__":
    try:
        # Fetch latest sensor values from the database
        sensor_values = fetch_latest_sensor_values()
        
        # Apply adaptive response based on sensor values
        response = apply_adaptive_response(sensor_values)
        
        # Print result
        print(f"Adaptive Response: {response}")
    
    except KeyboardInterrupt:
        print("\nAdaptive response application stopped by the user.")
