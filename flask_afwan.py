from flask import Flask, render_template_string, redirect, url_for, jsonify, send_file, request
import subprocess
import threading
import socket
import time
import mss, mss.tools
import io


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

def run_automation_afwan(arg, project, task):
    global task_status
    task_status["running"] = True
    task_status["last"] = f"Task {arg} in progress..."
    task_status["start_time"] = time.time()

    process = subprocess.Popen(
        ["python3", "automation_Afwan.py", arg, project, task],
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
        # ("A - AutoBooking", "A"),
        ("CB - Check Booking PNR", "CB"),
        ("CT - Celik Tafsir fetch", "CT"),
        ("CSFTP - Check SFTP", "CSFTP"),
        # ("BEXPO - Expo assembleDebug", "BEXPO"),
        ("BEXPO2 - Expo export", "BEXPO2"),  # special case
        # ("BFT - Flutter assembleDebug", "BFT"),
        ("BFT2 - Flutter assembleDebug", "BFT2"),
    ]

    html = """
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Automation Afwan Runner</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin-top: 20px;
                padding: 10px;
            }
            button {
                padding: 12px 24px;
                font-size: 16px;
                border-radius: 8px;
            }
            form {
                margin: 10px 0;
            }
        </style>
    </head>
    <body style="font-family:Arial; text-align:center; margin-top:10px;">
        <script>
            async function updateStatus() {
                const res = await fetch("/status");
                const data = await res.json();
                document.getElementById("status").innerText = data.last;
                document.getElementById("elapsed").innerText = data.elapsed;
            }
            setInterval(updateStatus, 1000);
            window.onload = updateStatus;
        </script>
        <h2>Choose an option to run:</h2>
        {% for text, arg in options %}
            <hr/>
            {% if arg == "BEXPO2" %}
                <form action="{{ url_for('run_command_with_project', arg=arg) }}" 
                method="post" 
                style="margin:10px;"
                onsubmit="return confirm('Are you sure you want to run {{ text }}?');"
                >
                    Project:
                    <select name="project" required>
                        <option value="escabee-mobile">escabee-mobile</option>
                        <option value="purgo-mobile">purgo-mobile</option>
                    </select>

                    Task:
                    <select name="task" required>
                        <option value="bundleRelease">bundleRelease</option>
                        <option value="assembleRelease">assembleRelease</option>
                        <option value="assembleDebug">assembleDebug</option>
                    </select>
                    <br/><br/>

                    <button type="submit" style="padding:10px 20px; font-size:16px;">{{ text }}</button>
                </form>

            
            {% elif arg == "BFT2" %}
                <form action="{{ url_for('run_command_with_project', arg=arg) }}" 
                method="post" 
                style="margin:10px;"
                onsubmit="return confirm('Are you sure you want to run {{ text }}?');"
                >
                    Project:
                    <select name="project" required>
                        <option value="hadis40v2">hadis40v2</option>
                        <option value="celiktafsirv4">celiktafsirv4</option>
                        <option value="habitmultiplayer">habitmultiplayer</option>
                    </select>

                    Task:
                    <select name="task" required>
                        <option value="bundleRelease">bundleRelease</option>
                        <option value="assembleRelease">assembleRelease</option>
                        <option value="assembleDebug">assembleDebug</option>
                    </select>
                    <br/><br/>
                    <button type="submit" style="padding:10px 20px; font-size:16px;">{{ text }}</button>
                </form>
                
            {% else %}
                <form action="{{ url_for('run_command', arg=arg) }}" 
                method="post" 
                style="margin:10px;"
                onsubmit="return confirm('Are you sure you want to run {{ text }}?');"
                >
                    <button type="submit" style="padding:10px 20px; font-size:16px;">{{ text }}</button>
                </form>
            {% endif %}
        {% endfor %}

        <hr/>
        <h3>Status:</h3>
        <p id="status">{{ status }}</p>

        <h3>Elapsed Time:</h3>
        <p id="elapsed">0s</p>

        <h3>Server Info:</h3>
        <p>Access via LAN: <b>http://{{ ip }}:5001</b></p>
        <hr/>
        <h3>Laptop Screen:</h3>
        <img id="screen" src="" width="600">
        <br/><br/>
        <button onclick="refreshScreen()">🔄 Refresh Screen</button>

        <script>
            function refreshScreen() {
                // Add timestamp so browser doesn't use cached image
                document.getElementById("screen").src = "/screenshot?time=" + new Date().getTime();
            }
        </script>


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

from flask import request

@app.route("/run/<arg>", methods=["POST"])
def run_command(arg):
    threading.Thread(target=run_automation_afwan, args=(arg, "", ""), daemon=True).start()
    return redirect(url_for("home"))

@app.route("/run/<arg>/project", methods=["POST"])
def run_command_with_project(arg):
    project = request.form.get("project", "")
    task = request.form.get("task", "")
    threading.Thread(target=run_automation_afwan, args=(arg, project, task), daemon=True).start()
    return redirect(url_for("home"))

@app.route("/screenshot")
def screenshot():
    with mss.mss() as sct:
        img = sct.grab(sct.monitors[1])  # capture full screen
        img_bytes = mss.tools.to_png(img.rgb, img.size)
        return send_file(io.BytesIO(img_bytes), mimetype="image/png")


if __name__ == "__main__":
    print(f"Server running at: http://{local_ip}:5001")
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)   # or logging.CRITICAL to hide almost everything

    app.run(debug=True, host="0.0.0.0", port=5001)
