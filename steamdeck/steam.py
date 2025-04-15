import sys
import requests
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox

# Flask API configurations
API_TOKEN = "token"
FLASK_SERVER_URL = "http://192.168.2.13"  # Updated to your server's IP address

# Function to check and install required dependencies
def install_dependencies():
    dependencies = [
        "wakeonlan",       # Wake-on-LAN utility
        "sshpass",         # SSH password helper for non-interactive SSH
        "flask",           # Flask for the API
        "requests",        # Requests for the Steam Deck GUI
        "PyQt6",           # PyQt6 for the GUI
    ]
    
    # Update apt package list and install each package
    for package in dependencies:
        try:
            print(f"Checking if {package} is installed...")
            subprocess.check_call(["dpkg", "-l", package])
            print(f"{package} is already installed.")
        except subprocess.CalledProcessError:
            print(f"{package} is not installed. Installing...")
            subprocess.check_call(["sudo", "apt-get", "install", "-y", package])
    
    # Install Python dependencies (if not already installed)
    try:
        import flask
    except ImportError:
        print("Flask is not installed. Installing Flask...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    
    try:
        import requests
    except ImportError:
        print("Requests is not installed. Installing Requests...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    
    try:
        import PyQt6
    except ImportError:
        print("PyQt6 is not installed. Installing PyQt6...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6"])

# Install dependencies
install_dependencies()

class PCControlApp(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize the UI
        self.setWindowTitle("PC Control")
        self.setGeometry(100, 100, 400, 300)
        
        self.layout = QVBoxLayout()

        self.status_label = QLabel("PC Status: Unknown", self)
        self.layout.addWidget(self.status_label)

        # Wake Button
        self.wake_button = QPushButton("Wake PC", self)
        self.wake_button.clicked.connect(self.wake_pc)
        self.layout.addWidget(self.wake_button)

        # Shutdown Button
        self.shutdown_button = QPushButton("Shutdown PC", self)
        self.shutdown_button.clicked.connect(self.shutdown_pc)
        self.layout.addWidget(self.shutdown_button)

        # Restart Button
        self.restart_button = QPushButton("Restart PC", self)
        self.restart_button.clicked.connect(self.restart_pc)
        self.layout.addWidget(self.restart_button)

        # Check Status Button
        self.status_button = QPushButton("Check PC Status", self)
        self.status_button.clicked.connect(self.check_pc_status)
        self.layout.addWidget(self.status_button)

        self.setLayout(self.layout)

    def send_request(self, endpoint):
        """Helper method to send requests to the Flask server."""
        url = f"{FLASK_SERVER_URL}/{endpoint}?token={API_TOKEN}"
        try:
            response = requests.get(url)
            return response.json()
        except requests.exceptions.RequestException as e:
            self.show_message("Error", str(e))
            return None

    def wake_pc(self):
        response = self.send_request("wake")
        if response and "message" in response:
            self.show_message("Success", response["message"])

    def shutdown_pc(self):
        response = self.send_request("shutdown")
        if response and "message" in response:
            self.show_message("Success", response["message"])

    def restart_pc(self):
        response = self.send_request("restart")
        if response and "message" in response:
            self.show_message("Success", response["message"])

    def check_pc_status(self):
        response = self.send_request("status")
        if response and "status" in response:
            self.status_label.setText(f"PC Status: {response['status']}")
        else:
            self.status_label.setText("PC Status: Offline")
    
    def show_message(self, title, message):
        """Helper method to show a pop-up message."""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec()

# Main code
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PCControlApp()
    window.show()
    sys.exit(app.exec())
