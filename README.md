# bachelor_thesis_zehrademir
IU Bachelor Thesis - Zehra Demir. Scripts and database files for Adaptive Security Framework for Racing Vehicle IoT Systems.

Bachelor Thesis: Adaptive Security Framework for Racing Vehicle IoT Systems
Overview
This repository contains scripts, databases, and examples related to the implementation and evaluation of the Adaptive Security Framework (ASF) for racing vehicle IoT systems. The ASF is designed to enhance security and performance by addressing various cybersecurity threats through adaptive mechanisms and predictive analytics.

Contents
Scripts: Contains Python scripts for simulating sensor data, detecting anomalies, implementing adaptive mechanisms, and evaluating performance.
Database: Includes SQLite database schema and example data for storing sensor readings and performance metrics.
Example Files: Provides examples and sample data for testing and demonstrating the functionality of the ASF.
Installation Guide
Prerequisites
Ensure you have the following installed on your system:

Python 3.6 or higher
pip (Python package installer)
Clone the Repository
Clone this repository to your local machine using the following command:

bash
Copy code
git clone https://github.com/zdemirgm/bachelor_thesis_zehrademir.git
Install Required Python Packages
Navigate to the cloned repository directory:

bash
Copy code
cd bachelor_thesis_zehrademir
Install the required Python packages using pip. You can install them individually or create a requirements.txt file and use it:

bash
Copy code
pip install -r requirements.txt
If you do not have a requirements.txt file, you can manually install the dependencies:

bash
Copy code
pip install numpy scipy scikit-learn sqlite3 logging
Note: sqlite3 is included with Python's standard library, so you may not need to install it separately.

Database Setup
Initialize the SQLite Database:

The repository includes a database schema for storing sensor data and performance metrics. You need to set up the database schema before running the scripts.

Execute the following SQL commands to create the necessary tables:

sql
Copy code
CREATE TABLE sensor_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    sensor TEXT,
    value REAL
);

CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    detection_time REAL,
    response_time REAL,
    anomaly_detected INTEGER
);
Populate Example Data:

Insert example data into the database if required for testing. Example data files are provided in the repository.

Running the Scripts
Simulate and Analyze:

To run the main simulation script, use the following command:

bash
Copy code
python main_script.py
This script simulates sensor values, detects anomalies, and applies adaptive responses based on the ASF. Make sure to replace main_script.py with the actual script name you are using.

Modify Configuration:

You can modify the script configurations (such as sensor types and simulation parameters) according to your needs. Refer to the script comments and documentation for guidance on customization.

Usage
Simulate Sensor Values: Generates and processes sensor data, applying penetration scenarios.
Detect Anomalies: Identifies anomalies in sensor data using predefined detection methods.
Apply Adaptive Responses: Implements adaptive mechanisms based on detected anomalies.
Record Metrics: Logs performance metrics and updates the database.
Example Usage
Here’s a brief example of how to run the main simulation script:

bash
Copy code
python main_script.py
The script will generate simulated sensor data, apply adaptive security mechanisms, and log the results to the database.

Troubleshooting
If you encounter issues, check the following:

Ensure all required Python packages are installed.
Verify that the database schema is correctly set up.
Review script comments and logs for error details.
License
This project is licensed under the MIT License.
