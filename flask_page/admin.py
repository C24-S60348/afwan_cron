from flask import Blueprint, render_template_string, request, redirect, url_for, flash
import subprocess
import variables

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

# Set your chosen password here (store securely in production)
ADMIN_PASSWORD = variables.website_pass

# HTML template for restart page
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Admin Restart</title>
</head>
<body style="font-family: Arial; text-align:center; margin-top:50px;">
    <h2>Restart Server</h2>
    {% if message %}
        <p style="color: red;">{{ message }}</p>
    {% endif %}
    <form method="post">
        <input type="password" name="password" placeholder="Enter password" required style="padding:8px;">
        <button type="submit" style="padding:10px 20px; margin-left:10px;">Restart</button>
    </form>
</body>
</html>
"""

@admin_bp.route("/restart", methods=["GET", "POST"])
def restart_server():
    message = ""
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            try:
                subprocess.run(["sudo", "systemctl", "restart", "afwanapp"], check=True)
                message = "✅ Server restarted successfully!"
            except subprocess.CalledProcessError as e:
                message = f"❌ Failed to restart: {e}"
        else:
            message = "❌ Wrong password!"
    return render_template_string(HTML_PAGE, message=message)
