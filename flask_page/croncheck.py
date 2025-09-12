import os
from datetime import datetime, timezone, timedelta
from flask import render_template_string
from flask import Blueprint
from flask_page.publicvar import last_run_times

croncheck_bp = Blueprint('croncheck_bp', __name__)

@croncheck_bp.route("/croncheck")
def croncheck():
    now = datetime.now(timezone.utc)
    gmt8 = timezone(timedelta(hours=8))
    current_time_raw = now.astimezone(gmt8)
    current_time_timestamp = current_time_raw.timestamp()

    timenowKL = current_time_timestamp
    times = {}
    cans = {}

    for key in last_run_times.keys():
        times[key] = datetime.fromtimestamp(last_run_times[key], tz=gmt8).strftime('%Y-%m-%d %I:%M %p')
        if (current_time_timestamp - last_run_times[key]) > ((float(key)*30)-10):
            last_run_times[key] = current_time_timestamp
            cans[key] = True
        else:
            cans[key] = False

    current_time = current_time_raw.strftime('%Y-%m-%d %I:%M %p')

    html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Cron Check</title></head>
        <body>
            <h2>Cron Check</h2>
            <p>Current time: {current_time}</p>
            """ 

    for key in times.keys():
        html += f'<p>Last {key}min: {times[key]}</p>'
    for key in times.keys():
        html += f'<p class="min{key}">{cans[key]}</p>'

    html += f"""
            <p class="timenowKL">{timenowKL}</p>
        </body>
        </html>
    """

    return render_template_string(html)