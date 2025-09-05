from flask import Flask, render_template_string, redirect, url_for, request, Response
import subprocess

app = Flask(__name__)

# Store logs here temporarily
last_log = ""

# Function to run the subprocess and return its logs
def run_automation_afwan(arg):
    command = f"python3 automation_Afwan.py {arg}"
    process = subprocess.Popen(
        command, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True
    )
    for line in process.stdout:
        yield line   # just yield to Flask browser
    process.wait()


# Home page with buttons + last log
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
    </head>
    <body style="font-family:Arial; text-align:center; margin-top:50px;">
        <h2>Choose an option to run:</h2>
        {% for text, arg in options %}
            <form action="{{ url_for('run_command', arg=arg) }}" method="post" style="margin:10px;">
                <button type="submit" style="padding:10px 20px; font-size:16px;">{{ text }}</button>
            </form>
        {% endfor %}

        {% if log %}
        <h3>Output:</h3>
        <pre id="log" style="text-align:left; border:1px solid #ccc; padding:10px; width:80%; margin:auto; white-space:pre-wrap;">
{{ log }}
        </pre>
        
        {% endif %}
         <script>
            // Auto-scroll to bottom as new data comes
            const log = document.getElementById("log");
            const evtSource = new EventSource(window.location.href.replace("http", "http")); 
            // (if you later upgrade to SSE, this line will work automatically)

            // Fallback for current streaming
            const es = new TextDecoderStream();
            fetch(window.location.href)
                .then(resp => resp.body.pipeThrough(es).getReader())
                .then(reader => {
                    function read() {
                        reader.read().then(({done, value}) => {
                            if (done) return;
                            log.innerHTML += value;
                            log.scrollTop = log.scrollHeight; // ✅ autoscroll
                            read();
                        });
                    }
                    read();
                });
        </script>
    </body>
    </html>
    """
    return render_template_string(html, options=options, log=last_log)

# Route to run command
@app.route("/run/<arg>", methods=["POST"])
def run_command(arg):
    def generate():
        command = f"python3 automation_Afwan.py {arg}"
        process = subprocess.Popen(
            command, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True
        )

        for line in iter(process.stdout.readline, ""):
            print(line, end="")        # ✅ print to terminal as if normal
            yield line + "<br/>\n"     # ✅ stream to browser
        process.stdout.close()
        process.wait()

    return Response(generate(), mimetype="text/html")



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
