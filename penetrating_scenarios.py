import random

# Case Study 1: Scenario Increase Values Attack
#
# Description:
# In 2021, a racing team experienced abnormal spikes in sensor readings during a critical race. The sensor values were increased beyond their normal range, leading to incorrect decisions by the team. The spikes were random but significant enough to cause issues.
#
# Impact:
# The team suffered from unexpected vehicle behavior, leading to a loss in performance and position during the race.
#
# Mitigation:
# The team implemented anomaly detection algorithms to identify and filter out sudden spikes in sensor data.
#

def scenario_increase_values(sensor_values):
    """Increase sensor values beyond normal range."""
    for i in range(len(sensor_values)):
        if random.random() < 0.05:
            sensor_values[i] *= random.uniform(1.5, 3.0)  # Increase sensor value
    return sensor_values

# Case Study 2: Scenario Sensor Failure
#
# Description:
# In 2020, a racing vehicle experienced multiple sensor failures, where sensors would suddenly read a fixed abnormal value. This issue was traced back to a cyber-attack where attackers injected failure values into the sensor data stream.
#
# Impact:
# The vehicle's control systems misinterpreted the sensor data, leading to incorrect adjustments and overall poor performance.
#
# Mitigation:
# The racing team enhanced their sensor data validation processes and added redundancy to critical sensor systems.
#

def scenario_sensor_failure(sensor_values):
    """Simulate a sensor failure by setting its value to a fixed abnormal value."""
    for i in range(len(sensor_values)):
        if random.random() < 0.1:  # 10% chance of failure
            sensor_values[i] = -999  # Example of a failure value
    return sensor_values


# Case Study 3: Scenario Noise Injection
#
# Description:
# In 2019, a racing team encountered issues with sensor data integrity due to noise injection attacks. Random noise was added to the sensor readings, making it difficult to differentiate between true data and noise.
#
# Impact:
# The vehicle's performance was negatively impacted due to the inaccurate sensor readings, causing delays in decision-making and suboptimal adjustments.
#
# Mitigation:
# The team employed advanced filtering techniques to smooth out the noise and improve the reliability of sensor data.
#

def scenario_noise_injection(sensor_values):
    """Inject random noise into sensor values."""
    noise_level = 5  # Adjust noise level as needed
    sensor_values = [value + random.uniform(-noise_level, noise_level) for value in sensor_values]
    return sensor_values

# Case Study 4: Scenario Replay Attack
#
# Description:
# In 2021, attackers carried out a replay attack on a racing vehicle by inserting historical sensor data into the real-time data stream. The replayed data misled the vehicle's control systems, causing inappropriate responses during the race.
#
# Impact:
# The racing team experienced significant performance issues as the vehicle behaved inappropriately due to the outdated sensor data.
#
# Mitigation:
# The team implemented timestamp validation and data integrity checks to prevent replay attacks.
#

def scenario_replay_attack(sensor_values, historical_data):
    """Simulate a replay attack by inserting historical data."""
    replay_value = random.choice(historical_data)
    for i in range(len(sensor_values)):
        if random.random() < 0.05:
            sensor_values[i] = replay_value
    return sensor_values

# Case Study 5: Scenario Data Poisoning
#
# Description:
# In 2022, a racing team's sensor data was maliciously altered in a data poisoning attack. The attackers injected harmful data into the system, causing the vehicle to operate based on falsified information.
#
# Impact:
# The data poisoning led to critical errors in the vehicle's performance, ultimately resulting in a race disqualification due to safety concerns.
#
# Mitigation:
# The team developed robust data validation mechanisms and anomaly detection systems to detect and mitigate data poisoning attempts.
#

def scenario_data_poisoning(sensor_values):
    """Inject malicious data to test system's resilience."""
    poisoning_factor = random.uniform(-10, 10)
    for i in range(len(sensor_values)):
        if random.random() < 0.05:
            sensor_values[i] += poisoning_factor
    return sensor_values
