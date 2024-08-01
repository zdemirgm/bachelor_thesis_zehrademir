import dash
from dash import dcc, html, Input, Output
import plotly.graph_objects as go
import sqlite3
import pandas as pd
from performance_metrics import PerformanceMetrics
import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = dash.Dash(__name__)

# Initialize lists for sensor data and performance metrics
sensors = ['Temperature', 'Speed', 'Engine Sensors', 'Brakes', 'Fluid Level', 'Heat', 'Tire Pressure', 'Battery']
num_sensors = len(sensors)

# Create initial figure layout for each sensor
figs = [go.Figure() for _ in range(num_sensors)]
for i, sensor in enumerate(sensors):
    figs[i].add_trace(go.Scatter(x=[], y=[], mode='lines', name=sensor))
    figs[i].update_layout(title=f'Real-Time {sensor} Readings', xaxis_title='Time', yaxis_title='Value')

# Create anomaly motion plot figure
anomaly_fig = go.Figure()
for sensor in sensors:
    anomaly_fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name=sensor))
anomaly_fig.update_layout(title='Anomaly Detection Motion Plot', xaxis_title='Time', yaxis_title='Value')

# Create performance metrics plot figures
performance_figs = {
    'detection_time': go.Figure(),
    'response_time': go.Figure(),
    'detection_rate': go.Figure()
}

for key, fig in performance_figs.items():
    fig.add_trace(go.Scatter(x=[], y=[], mode='lines', name=key.replace('_', ' ').title()))
    fig.update_layout(title=f'{key.replace("_", " ").title()}', xaxis_title='Time', yaxis_title='Value')

# Define paths for the databases in the same folder as the script
script_dir = os.path.dirname(os.path.abspath(__file__))
racing_db_path = os.path.join(script_dir, 'racing_vehicle_db.sqlite')
metrics_db_path = os.path.join(script_dir, 'metrics_db.sqlite')

def fetch_data_from_db():
    try:
        conn = sqlite3.connect(racing_db_path)
        cursor = conn.cursor()
        
        # Fetch sensor data
        query = """
        SELECT timestamp, sensor, value
        FROM sensor_data
        WHERE timestamp >= datetime('now', '-5 minutes')
        ORDER BY timestamp ASC
        """
        cursor.execute(query)
        sensor_data = cursor.fetchall()
        
        # Fetch anomaly data
        query = """
        SELECT timestamp, sensor, value
        FROM anomalies
        WHERE timestamp >= datetime('now', '-5 minutes')
        ORDER BY timestamp ASC
        """
        cursor.execute(query)
        anomaly_data = cursor.fetchall()
        
        conn.close()
        
        logging.debug(f"Fetched sensor data: {sensor_data}")
        logging.debug(f"Fetched anomaly data: {anomaly_data}")
        
        return sensor_data, anomaly_data
    
    except sqlite3.Error as e:
        logging.error(f"SQLite error fetching data: {e}")
        return [], []

def fetch_performance_metrics_from_db():
    try:
        conn = sqlite3.connect(metrics_db_path)
        cursor = conn.cursor()
        
        # Fetch performance metrics
        query = """
        SELECT timestamp, detection_time, response_time, threat_detection_rate
        FROM performance_metrics
        WHERE timestamp >= datetime('now', '-5 minutes')
        ORDER BY timestamp ASC
        """
        cursor.execute(query)
        performance_data = cursor.fetchall()
        
        conn.close()
        
        logging.debug(f"Fetched performance data: {performance_data}")
        
        return performance_data
    
    except sqlite3.Error as e:
        logging.error(f"SQLite error fetching performance metrics: {e}")
        return []

def process_data(sensor_data, anomaly_data, performance_data):
    df_sensor = pd.DataFrame(sensor_data, columns=['timestamp', 'sensor', 'value'])
    df_anomaly = pd.DataFrame(anomaly_data, columns=['timestamp', 'sensor', 'value'])
    df_performance = pd.DataFrame(performance_data, columns=['timestamp', 'detection_time', 'response_time', 'threat_detection_rate'])
    
    # Convert timestamps to datetime format
    df_sensor['timestamp'] = pd.to_datetime(df_sensor['timestamp'])
    df_anomaly['timestamp'] = pd.to_datetime(df_anomaly['timestamp'])
    df_performance['timestamp'] = pd.to_datetime(df_performance['timestamp'])
    
    logging.debug(f"Processed sensor DataFrame:\n{df_sensor}")
    logging.debug(f"Processed anomaly DataFrame:\n{df_anomaly}")
    logging.debug(f"Processed performance DataFrame:\n{df_performance}")
    
    return df_sensor, df_anomaly, df_performance

# Define app layout with tabs and graphs
app.layout = html.Div([
    html.H1("Real-Time Racing Vehicle Sensor Data"),
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Sensor Readings', value='tab-1', children=[
            *[dcc.Graph(id=f'live-update-graph-{i}', figure=fig) for i, fig in enumerate(figs)]
        ]),
        dcc.Tab(label='Anomalies', value='tab-2', children=[
            dcc.Graph(id='anomaly-motion-plot', figure=anomaly_fig)
        ]),
        dcc.Tab(label='Performance Metrics', value='tab-3', children=[
            dcc.Graph(id='performance-detection-time', figure=performance_figs['detection_time']),
            dcc.Graph(id='performance-response-time', figure=performance_figs['response_time']),
            dcc.Graph(id='performance-detection-rate', figure=performance_figs['detection_rate']),
        ]),
    ]),
    dcc.Interval(
        id='interval-component',
        interval=1000,  # in milliseconds
        n_intervals=0
    )
])

# Callback to update sensor readings
@app.callback(
    [Output(f'live-update-graph-{i}', 'figure') for i in range(num_sensors)],
    [Input('interval-component', 'n_intervals')]
)
def update_sensor_graph(n):
    sensor_data, _ = fetch_data_from_db()
    df_sensor, _, _ = process_data(sensor_data, [], [])
    
    fig_list = []
    for i, sensor in enumerate(sensors):
        fig = go.Figure()
        if sensor in df_sensor['sensor'].unique():
            sensor_df = df_sensor[df_sensor['sensor'] == sensor]
            if not sensor_df.empty:
                fig.add_trace(go.Scatter(x=sensor_df['timestamp'], y=sensor_df['value'], mode='lines', name=sensor))
                
                # Add log for debugging
                logging.debug(f"Updating {sensor} plot: X={sensor_df['timestamp'].tolist()}, Y={sensor_df['value'].tolist()}")
        fig.update_layout(title=f'Real-Time {sensor} Readings', xaxis_title='Time', yaxis_title='Value')
        fig_list.append(fig)
    
    return fig_list

# Callback to update anomaly motion plot
@app.callback(
    Output('anomaly-motion-plot', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_anomaly_plot(n):
    _, anomaly_data = fetch_data_from_db()
    _, df_anomaly, _ = process_data([], anomaly_data, [])
    
    anomaly_fig = go.Figure()
    for sensor in sensors:
        if not df_anomaly[df_anomaly['sensor'] == sensor].empty:
            sensor_df = df_anomaly[df_anomaly['sensor'] == sensor]
            anomaly_fig.add_trace(go.Scatter(x=sensor_df['timestamp'], y=sensor_df['value'], mode='lines', name=sensor))
            
            # Add annotation for anomaly
            anomaly_fig.add_annotation(
                x=sensor_df['timestamp'].iloc[-1],
                y=sensor_df['value'].iloc[-1],
                text=f'Anomaly Detected: {sensor}, Value: {sensor_df["value"].iloc[-1]:.2f}',
                showarrow=True,
                arrowhead=1,
                ax=-50,
                ay=-50
            )
    
    anomaly_fig.update_layout(title='Anomaly Detection Motion Plot', xaxis_title='Time', yaxis_title='Value')
    
    return anomaly_fig

# Callback to update performance metrics plots
@app.callback(
    [Output('performance-detection-time', 'figure'),
     Output('performance-response-time', 'figure'),
     Output('performance-detection-rate', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_performance_metrics_graph(n):
    # Fetch metrics data from the database
    performance_data = fetch_performance_metrics_from_db()
    
    # Process the fetched data
    df_performance = pd.DataFrame(performance_data, columns=['timestamp', 'detection_time', 'response_time', 'threat_detection_rate'])
    df_performance['timestamp'] = pd.to_datetime(df_performance['timestamp'])
    
    # Create figures
    fig_detection_time = go.Figure()
    fig_response_time = go.Figure()
    fig_detection_rate = go.Figure()
    
    if not df_performance.empty:
        fig_detection_time.add_trace(go.Scatter(x=df_performance['timestamp'], y=df_performance['detection_time'], mode='lines', name='Detection Time'))
        fig_response_time.add_trace(go.Scatter(x=df_performance['timestamp'], y=df_performance['response_time'], mode='lines', name='Response Time'))
        fig_detection_rate.add_trace(go.Scatter(x=df_performance['timestamp'], y=df_performance['threat_detection_rate'], mode='lines', name='Detection Rate'))
        
        # Add logs for debugging
        logging.debug(f"Updating Detection Time plot: X={df_performance['timestamp'].tolist()}, Y={df_performance['detection_time'].tolist()}")
        logging.debug(f"Updating Response Time plot: X={df_performance['timestamp'].tolist()}, Y={df_performance['response_time'].tolist()}")
        logging.debug(f"Updating Detection Rate plot: X={df_performance['timestamp'].tolist()}, Y={df_performance['threat_detection_rate'].tolist()}")
    
    fig_detection_time.update_layout(title='Detection Time', xaxis_title='Time', yaxis_title='Time (s)')
    fig_response_time.update_layout(title='Response Time', xaxis_title='Time', yaxis_title='Time (s)')
    fig_detection_rate.update_layout(title='Detection Rate', xaxis_title='Time', yaxis_title='Rate')

    return fig_detection_time, fig_response_time, fig_detection_rate

if __name__ == '__main__':
    app.run_server(debug=True)
