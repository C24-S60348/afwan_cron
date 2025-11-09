import os
from datetime import datetime, timezone, timedelta
from flask import render_template_string
from flask import Blueprint

home_bp = Blueprint('home_bp', __name__)

TXT_FILES_DIR = "/home/AfwanProductions/mysite/cron_output/"
@home_bp.route("/")
def index():
    html = """
    <html>
        <body>
            <h1>This is Afwan's server</h1>
        </body>
    </html>
    """
    return render_template_string(html)
    
    # txt_files = [f for f in os.listdir(TXT_FILES_DIR) if f.endswith(".txt")]
    # txt_files.sort(reverse=True)
    # now = datetime.now(timezone.utc)
    # gmt8 = timezone(timedelta(hours=8))
    # current_time = now.astimezone(gmt8).strftime('%Y-%m-%d %I:%M %p')
    # last_run_time = datetime.fromtimestamp(max(last_run_times.values()), tz=gmt8).strftime('%Y-%m-%d %I:%M %p')
    # html = f"""
    #     <!DOCTYPE html>
    #     <html>
    #     <head><title>TXT Files</title></head>
    #     <body>
    #         <h2>TXT Files from afwanhaziq.pythonanywhere.com</h2>
    #         <p>Current time: {current_time}</p>
    #         <p>Last run cron: {last_run_time}</p>
    #         <ul>"""
    
    # for file in txt_files:
    #     html += f"<li><a href='/view/{file}'>{file}</a></li>"
    # html += """
    #         </ul>
    #     </body>
    #     </html>
    # """
    # return render_template_string(html, files=txt_files)


@home_bp.route("/view/<filename>")
def view_file(filename):
    filepath = os.path.join(TXT_FILES_DIR, filename)
    try:
        with open(filepath, "r") as f:
            content = f.read()
        
        html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>{filename}</title></head>
            <body>
                <h1>{filename}</h1>
                <pre>{content}</pre>
            </body>
            </html>
        """
        return render_template_string(html, content=content, filename=filename)
    except FileNotFoundError:
        return "File not found", 404

