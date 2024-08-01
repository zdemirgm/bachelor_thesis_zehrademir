import time
import can
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class CANSimulation:
    def __init__(self):
        self.bus = None
        self.running = False

    def start(self):
        # Start the CAN bus simulation
        try:
            self.bus = can.interface.Bus(channel='virtual_can', interface='virtual')
            self.running = True
            logging.info("CAN bus simulation started.")
        except Exception as e:
            logging.error(f"Error starting CAN bus simulation: {e}")
            self.running = False

    def stop(self):
        # Stop the CAN bus simulation
        if self.bus:
            self.bus.shutdown()
        self.running = False
        logging.info("CAN bus simulation stopped.")

    def publish_data(self, can_id, data):
        # Publish CAN message
        try:
            data = [min(max(0, int(value)), 255) for value in data]  # Ensure data values are in range
            msg = can.Message(arbitration_id=can_id, data=bytearray(data))
            self.bus.send(msg)
            logging.debug(f"Published CAN message: ID={can_id}, Data={data}")
        except ValueError as e:
            logging.error(f"ValueError in publish_data: {e}")
        except can.CanError as e:
            logging.error(f"CANError in publish_data: {e}")

    def receive_data(self):
        # Receive data from the CAN bus (simulated)
        while self.running:
            try:
                msg = self.bus.recv(timeout=1)
                if msg is not None:
                    logging.debug(f"Received CAN message: ID={msg.arbitration_id}, Data={msg.data}")
            except can.CanError as e:
                logging.error(f"CANError in receive_data: {e}")

    def run(self):
        # Run the CAN communication
        try:
            # Start receiving thread
            receive_thread = threading.Thread(target=self.receive_data)
            receive_thread.start()

            # Keep running to maintain communication
            while self.running:
                self.publish_data(can_id=0x100, data=[0, 0, 0, 0])  # Modify or remove as needed

                # Sleep to prevent excessive CPU usage
                time.sleep(1)  # Adjust interval as needed

        except KeyboardInterrupt:
            logging.info("CAN communication simulation stopped by user.")
        finally:
            self.stop()

if __name__ == "__main__":
    try:
        can_sim = CANSimulation()
        can_sim.start()

        # Start CAN communication
        can_sim.run()

    except Exception as e:
        logging.error(f"Error in CAN simulation: {e}")
    finally:
        logging.info("Exiting CAN communication simulation.")
