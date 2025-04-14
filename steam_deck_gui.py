import subprocess
import sys
import json
import os

# Function to check and install required dependencies
def install_dependencies():
    dependencies = [
        "requests",        # Requests for interacting with the Flask API
        "PyQt6",           # PyQt6 for the GUI
    ]
    
    # Install Python dependencies (if not already installed)
    for package in dependencies:
        try:
            __import__(package)
            print(f"{package} is already installed.")
        except ImportError:
            print(f"{package} is not installed. Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Run the dependency installation script
install_dependencies()

# Import the necessary packages after installation
import requests
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel

# Configuration (replace with correct details)
with open('config.json', 'r') as f:
    config = json.load(f)

SERVER = config["server"]
API_TOKEN = config["api_token"]

def call_server(endpoint):
    """Send request to the server API"""
    try:
        response = requests.get(f"{SERVER}/{endpoint}", params={"token": API_TOKEN}, timeout=3)
        if response.status_code == 200:
            return response.json()["message"]
        else:
            return response.json()["error"]
    except Exception as e:
        return f"Error: {str(e)}"

app = QApplication(sys.argv)

# Main window setup
window = QWidget()
window.setWindowTitle("PC Control")

# Layout and status label
layout = QVBoxLayout()
status_label = QLabel("Status: Unknown")
layout.addWidget(status_label)

# Button actions
def create_button(name, endpoint):
    button = QPushButton(name)
    button.clicked.connect(lambda _, e=endpoint: status_label.setText(f"Status: {call_server(e)}"))
    layout.addWidget(button)

# Buttons for controlling PC
create_button("Wake PC", "wake")
create_button("Shutdown PC", "shutdown")
create_button("Check Status", "status")

window.setLayout(layout)
window.resize(400, 300)

window.show()
app.exec()
