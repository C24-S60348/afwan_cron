from flask import Blueprint, request
import subprocess
import time
import variables

admin_bp = Blueprint("admin_bp", __name__)
ADMIN_SECRET = variables.website_pass


@admin_bp.route("/admin/restart", methods=["GET", "POST"])
def admin_page():
    if request.method == "POST":
        password = request.form.get("password")

        if password == ADMIN_SECRET:
            # Run restart as detached background process
            subprocess.Popen(
                ["/usr/bin/sudo", "systemctl", "restart", "afwanapp"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            # Show restarting page that auto-refreshes every 5 seconds
            return """
            <h1>Restarting server...</h1>
            <p>The server will attempt to come back online soon.</p>
            <script>
                setInterval(() => {
                    fetch("/croncheck")
                        .then(r => {
                            if (r.ok) location.href = "/croncheck";
                        })
                        .catch(() => console.log("Waiting for server..."));
                }, 5000);
            </script>
            """
        else:
            return "<h1>Invalid password</h1>", 403

    # Default GET: show form
    return """
    <h1>Admin Panel</h1>
    <form method="POST">
        <input type="password" name="password" placeholder="Enter password" required/>
        <button type="submit">Restart Server</button>
    </form>
    """
