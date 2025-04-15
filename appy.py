from flask import Flask, jsonify, request, render_template
import subprocess
import sys
import os

app = Flask(__name__, template_folder='templates')

# Config
API_TOKEN = "Apitoke"
PC_MAC_ADDRESS = "Adress"
PC_IP = "IP_of_comp"
PC_SSH_USER = "Username"
PC_SSH_PASSWORD = "Password"  # Or better, use key-based authentication

# === HELPERS ===
def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return str(e)


def is_pc_online():
    ssh_check_cmd = f"sshpass -p '{PC_SSH_PASSWORD}' ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no {PC_SSH_USER}@{PC_IP} echo online"
    ssh_result = run_cmd(ssh_check_cmd)
    if "online" in ssh_result.lower():
        return True
    ping_result = run_cmd(f"ping -c 1 {PC_IP}")
    return "1 received" in ping_result or "1 packets transmitted" in ping_result


# === NEW FUNCTION: Install dependencies ===
def install_dependencies():
    dependencies = [
        "wakeonlan",       # Wake-on-LAN utility
        "sshpass",         # SSH password helper for non-interactive SSH
        "flask",           # Flask for the API
        "requests",        # Requests for the Steam Deck GUI
        "PyQt6",           # PyQt6 for the GUI
    ]
    
    installed_packages = []
    # Update apt package list and install each package
    for package in dependencies:
        try:
            print(f"Checking if {package} is installed...")
            subprocess.check_call(["dpkg", "-l", package])
            installed_packages.append(f"{package} is already installed.")
        except subprocess.CalledProcessError:
            print(f"{package} is not installed. Installing...")
            subprocess.check_call(["sudo", "apt-get", "install", "-y", package])
            installed_packages.append(f"{package} has been installed.")

    # Install Python dependencies (if not already installed)
    python_installed = []
    try:
        import flask
    except ImportError:
        print("Flask is not installed. Installing Flask...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
        python_installed.append("Flask has been installed.")
    
    try:
        import requests
    except ImportError:
        print("Requests is not installed. Installing Requests...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        python_installed.append("Requests has been installed.")
    
    try:
        import PyQt6
    except ImportError:
        print("PyQt6 is not installed. Installing PyQt6...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6"])
        python_installed.append("PyQt6 has been installed.")
    
    return installed_packages + python_installed


# === ROUTES ===
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/wake", methods=["GET"])
def wake_pc():
    if request.args.get("token") != API_TOKEN:
        return jsonify({"error": "unauthorized"}), 401

    result = run_cmd(f"wakeonlan {PC_MAC_ADDRESS}")
    return jsonify({"message": "Wake signal sent", "result": result})


@app.route("/status", methods=["GET"])
def pc_status():
    if request.args.get("token") != API_TOKEN:
        return jsonify({"error": "unauthorized"}), 401

    if is_pc_online():
        return jsonify({"status": "online"})
    return jsonify({"status": "offline"})


@app.route("/shutdown", methods=["GET"])
def shutdown_pc():
    if request.args.get("token") != API_TOKEN:
        return jsonify({"error": "unauthorized"}), 401

    if not is_pc_online():
        return jsonify({"status": "offline", "message": "Cannot shutdown"}), 400

    cmd = f"sshpass -p '{PC_SSH_PASSWORD}' ssh -o StrictHostKeyChecking=no {PC_SSH_USER}@{PC_IP} \"shutdown /s /f /t 0\""
    result = run_cmd(cmd)
    return jsonify({"message": "Shutdown sent", "result": result})


@app.route("/restart", methods=["GET"])
def restart_pc():
    if request.args.get("token") != API_TOKEN:
        return jsonify({"error": "unauthorized"}), 401

    if not is_pc_online():
        return jsonify({"status": "offline", "message": "Cannot restart"}), 400

    cmd = f"sshpass -p '{PC_SSH_PASSWORD}' ssh -o StrictHostKeyChecking=no {PC_SSH_USER}@{PC_IP} \"shutdown /r /f /t 0\""
    result = run_cmd(cmd)
    return jsonify({"message": "Restart sent", "result": result})


# === NEW ROUTE: Install Dependencies ===
@app.route("/install_dependencies", methods=["GET"])
def install_dependencies_route():
    if request.args.get("token") != API_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    
    try:
        result = install_dependencies()
        return jsonify({"message": "Dependencies installation completed successfully", "details": result}), 200
    except Exception as e:
        return jsonify({"message": "Error installing dependencies", "error": str(e)}), 500


# === MAIN ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)

