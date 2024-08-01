import subprocess
import threading
import time
import shutil
import os
from cryptography.fernet import Fernet
from performance_metrics import PerformanceMetrics

key = b'RV_e7YpO5KE7jL7buC-k7HrZRVcvFBZ74ZjnTt0MHq0=' 

# Convert key to Fernet format
fernet = Fernet(key)

# Encrypt database file
def encrypt_file(file_path, key):
    print(f"Encrypting file: {file_path}")
    fernet = Fernet(key)
    with open(file_path, 'rb') as file:
        file_data = file.read()
    encrypted_data = fernet.encrypt(file_data)
    with open(file_path + '.enc', 'wb') as file:
        file.write(encrypted_data)

# Decrypt database file
def decrypt_file(file_path, key):
    print(f"Decrypting file: {file_path}")
    fernet = Fernet(key)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    with open(file_path, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    with open(file_path.replace('.enc', ''), 'wb') as file:
        file.write(decrypted_data)

# Backup database and encrypt
def backup_and_encrypt_db(src_path, backup_path, key):
    if not os.path.exists(src_path):
        print(f"Source file not found: {src_path}")
        return
    print(f"Backing up and encrypting database: {src_path}")
    shutil.copy(src_path, backup_path)
    encrypt_file(backup_path, key)

# Function to run a script
def run_script(script_name):
    print(f"Running script: {script_name}")
    subprocess.run(['python', script_name], check=True)

# Encrypt database before running scripts
def encrypt_db(file_path, key):
    if os.path.exists(file_path):
        encrypt_file(file_path, key)
    else:
        print(f"File not found: {file_path}")

# Decrypt database before running scripts
def decrypt_db(file_path, key):
    if os.path.exists(file_path):
        decrypt_file(file_path, key)
    else:
        print(f"File not found: {file_path}")

def monitor_changes(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    last_modified_time = os.path.getmtime(file_path)
    while True:
        time.sleep(10)  # Check every 10 seconds
        new_modified_time = os.path.getmtime(file_path)
        if new_modified_time != last_modified_time:
            print(f"{file_path} has been modified")
            last_modified_time = new_modified_time

# Function to continuously update performance metrics
def continuous_performance_update(metrics):
    while True:
        performance_data = metrics.update_metrics_from_db()
        print("Performance Metrics Updated:")
        print(performance_data)
        time.sleep(5)  # Adjust sleep time as necessary

# Initialize performance metrics
performance_metrics = PerformanceMetrics()

# Start performance metrics update in a separate thread
metrics_thread = threading.Thread(target=continuous_performance_update, args=(performance_metrics,), daemon=True)
metrics_thread.start()

# Paths to database files
racing_vehicle_db_path = 'racing_vehicle_db.sqlite'
metrics_db_path = 'metrics_db.sqlite'

# Backup and encrypt databases
backup_path_racing = 'backup_racing_vehicle_db.sqlite'
backup_path_metrics = 'backup_metrics_db.sqlite'

print(f"Backing up and encrypting databases...")
backup_and_encrypt_db(racing_vehicle_db_path, backup_path_racing, key)
backup_and_encrypt_db(metrics_db_path, backup_path_metrics, key)

# Decrypt databases before using
print(f"Decrypting databases...")
decrypt_db(backup_path_racing + '.enc', key)
decrypt_db(backup_path_metrics + '.enc', key)

# Start plots.py in a separate thread
plots_thread = threading.Thread(target=lambda: run_script('plots.py'), daemon=True)
plots_thread.start()

# Run other scripts
run_script('simulation.py')
run_script('adaptive_mechanisms.py')
run_script('anomaly_detection.py')
run_script('penetrating_scenarios.py')
run_script('communication_module.py')

plots_thread.join()  
metrics_thread.join()  # Wait for performance metrics updates to complete

# Encrypt databases after use
print(f"Encrypting databases...")
encrypt_db(racing_vehicle_db_path, key)
encrypt_db(metrics_db_path, key)

# Backup encrypted databases
print(f"Backing up encrypted databases...")
backup_and_encrypt_db(racing_vehicle_db_path, backup_path_racing, key)
backup_and_encrypt_db(metrics_db_path, backup_path_metrics, key)

# Start monitoring (simplified)
monitor_changes(racing_vehicle_db_path)
monitor_changes(metrics_db_path)
