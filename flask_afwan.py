from flask import Flask, render_template_string, Response
import subprocess
import sys

app = Flask(__name__)

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
        // autoscroll to bottom
        function scrollToBottom() {
            window.scrollTo(0, document.body.scrollHeight);
        }
        setInterval(scrollToBottom, 1000);
        </script>
    </head>
    <body style="font-family:Arial; text-align:center; margin-top:50px;">
        <h2>Choose an option to run:</h2>
        {% for text, arg in options %}
            <form action="/run/{{ arg }}" method="post" style="margin:10px;">
                <button type="submit" style="padding:10px 20px; font-size:16px;">{{ text }}</button>
            </form>
        {% endfor %}
    </body>
    </html>
    """
    return render_template_string(html, options=options)


@app.route("/run/<arg>", methods=["POST"])
def run_command(arg):
    def generate():
        command = f"python3 automation_Afwan.py {arg}"
        process = subprocess.Popen(
            command, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1  # line-buffered
        )

        for line in iter(process.stdout.readline, ""):
            # ✅ print to Flask server terminal
            sys.stdout.write(line)
            sys.stdout.flush()
            # ✅ also stream to browser
            yield line.replace("\n", "<br/>\n")

        process.stdout.close()
        process.wait()

    return Response(generate(), mimetype="text/html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
