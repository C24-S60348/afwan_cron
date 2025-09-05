from flask import Flask, render_template_string, redirect, url_for, jsonify
import subprocess
import threading
import socket
import time

app = Flask(__name__)

# Track task state
task_status = {
    "running": False,
    "last": "Idle",
    "start_time": None,
    "elapsed": "0s"
}

# Detect local IP
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # connect to Google DNS
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        ip = "127.0.0.1"
    return ip

local_ip = get_local_ip()

def run_automation_afwan(arg):
    global task_status
    task_status["running"] = True
    task_status["last"] = f"Task {arg} in progress..."
    task_status["start_time"] = time.time()

    process = subprocess.Popen(
        ["python3", "automation_Afwan.py", arg],
        stdout=None, stderr=None  # inherit to terminal
    )
    process.wait()  # wait until done

    task_status["running"] = False
    elapsed = int(time.time() - task_status["start_time"])
    task_status["last"] = f"Task {arg} completed ✅ (Elapsed: {elapsed}s)"
    task_status["elapsed"] = f"{elapsed}s"
    task_status["start_time"] = None

@app.route("/")
def home():
    options = [
        ("A - AutoBooking", "A"),
        ("CB - Check Booking PNR", "CB"),
        ("CT - Celik Tafsir fetch", "CT"),
        ("CSFTP - Check SFTP", "CSFTP"),
        ("BEXPO - Expo assembleDebug", "BEXPO"),
        ("BFT - Flutter assembleDebug", "BFT"),
    ]

    html = """
    <html>
    <head>
        <title>Automation Afwan Runner</title>
        <script>
            async function updateStatus() {
                const res = await fetch("/status");
                const data = await res.json();
                document.getElementById("status").innerText = data.last;
                document.getElementById("elapsed").innerText = data.elapsed;
            }

            // update every 1 second
            setInterval(updateStatus, 1000);
            window.onload = updateStatus;
        </script>
    </head>
    <body style="font-family:Arial; text-align:center; margin-top:50px;">
        <h2>Choose an option to run:</h2>
        {% for text, arg in options %}
            <form action="{{ url_for('run_command', arg=arg) }}" method="post" style="margin:10px;">
                <button type="submit" style="padding:10px 20px; font-size:16px;">{{ text }}</button>
            </form>
        {% endfor %}

        <h3>Status:</h3>
        <p id="status">{{ status }}</p>

        <h3>Elapsed Time:</h3>
        <p id="elapsed">0s</p>

        <h3>Server Info:</h3>
        <p>Access via LAN: <b>http://{{ ip }}:5001</b></p>
    </body>
    </html>
    """
    return render_template_string(html, options=options, status=task_status["last"], ip=local_ip)

@app.route("/status")
def get_status():
    # If running, update elapsed dynamically
    if task_status["running"] and task_status["start_time"]:
        elapsed = int(time.time() - task_status["start_time"])
        task_status["elapsed"] = f"{elapsed}s"
    return jsonify(task_status)

@app.route("/run/<arg>", methods=["POST"])
def run_command(arg):
    # Run in background thread so Flask doesn't block
    threading.Thread(target=run_automation_afwan, args=(arg,), daemon=True).start()
    return redirect(url_for("home"))

if __name__ == "__main__":
    print(f"Server running at: http://{local_ip}:5001")
    app.run(debug=True, host="0.0.0.0", port=5001)
