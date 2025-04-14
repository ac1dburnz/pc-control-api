import subprocess
import sys
import os

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

# Run the dependency installation script
install_dependencies()

# Import the necessary packages after installation
from flask import Flask, jsonify, request
import subprocess
import json

app = Flask(__name__)

# Configurations (replace with your own details)
API_TOKEN = "your_secure_token_here"
PC_MAC_ADDRESS = "XX:XX:XX:XX:XX:XX"  # Replace with your PC's MAC address
PC_IP = "192.168.2.56"  # Replace with your PC's IP address
PC_SSH_USER = "your_ssh_user"
PC_SSH_PASSWORD = "your_ssh_password"  # Or better, use key-based authentication

def run_command(command):
    """Execute system commands and return output"""
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return str(e)

@app.route('/wake', methods=['GET'])
def wake():
    """Send Wake-on-LAN magic packet to the PC"""
    if request.args.get('token') != API_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    command = f"wakeonlan {PC_MAC_ADDRESS}"
    result = run_command(command)
    return jsonify({"message": f"Wake command sent: {result}"}), 200

@app.route('/shutdown', methods=['GET'])
def shutdown():
    """Shutdown the PC via SSH"""
    if request.args.get('token') != API_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    # SSH command to shutdown PC
    ssh_command = f"sshpass -p {PC_SSH_PASSWORD} ssh {PC_SSH_USER}@{PC_IP} 'shutdown /s /f /t 0'"
    result = run_command(ssh_command)
    return jsonify({"message": f"Shutdown command sent: {result}"}), 200

@app.route('/status', methods=['GET'])
def status():
    """Check if the PC is online (via ping test)"""
    try:
        result = run_command(f"ping -c 1 {PC_IP}")
        if "1 packets transmitted" in result:
            return jsonify({"status": "PC is online"}), 200
        else:
            return jsonify({"status": "PC is offline"}), 200
    except Exception as e:
        return jsonify({"error": f"Unable to check status: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
