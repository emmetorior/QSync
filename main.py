import subprocess
from threading import Thread
import time


def start_queue():
    """Start the FastAPI gateway server."""
    subprocess.run(["python", "MQueue8004.py"])


def start_gateway():
    """Start the FastAPI gateway server."""
    subprocess.run(["python", "Gateway8004.py"])

def start_publisher():
    """Start the FastAPI publisher."""
    subprocess.run(["python", "MPublisher8004.py"])

def start_subscriber():
    """Start the Flask subscriber."""
    subprocess.run(["python", "subscriber8004.py"])

if __name__ == "__main__":
    # Start the gateway in a separate thread
    gateway_thread = Thread(target=start_gateway, daemon=True)
    gateway_thread.start()
    print("Gateway server started.")

    # Give the gateway some time to initialize
    time.sleep(2)

    # Start the subscriber in a separate thread
    subscriber_thread = Thread(target=start_subscriber, daemon=True)
    subscriber_thread.start()
    print("Subscriber started.")

    # Give the subscriber some time to initialize
    time.sleep(2)

    # Start the publisher in the main thread
    print("Starting publisher...")
    start_publisher()