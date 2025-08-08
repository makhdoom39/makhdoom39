from flask import Flask, render_template_string, request, redirect, send_file
from datetime import datetime
import time
import csv
import os

app = Flask(__name__)

# Store requests as (timestamp, IP, unix_time)
request_log = []
LOG_FILE = "request_log.csv"

# HTML + CSS Template with reset/download
html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>DoS Request Tracker</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        .summary { margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #f4f4f4; }
        .actions { margin-top: 10px; }
        button { padding: 8px 12px; font-size: 14px; margin-right: 10px; }
    </style>
</head>
<body>
    <h1>📊 DoS Request Tracker</h1>
    <div class="summary">
        <p><strong>Total Requests:</strong> {{ total }}</p>
        <p><strong>Requests Per Second (RPS):</strong> {{ rps }}</p>
    </div>

    <div class="actions">
        <form method="POST" action="/reset">
            <button type="submit">🔄 Reset Counter</button>
        </form>
        <form method="GET" action="/download">
            <button type="submit">⬇️ Download Log</button>
        </form>
    </div>

    <table>
        <tr><th>#</th><th>Time Received</th><th>Source IP</th></tr>
        {% for idx, log in logs %}
        <tr><td>{{ idx }}</td><td>{{ log[0] }}</td><td>{{ log[1] }}</td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    now = time.time()
    ip = request.remote_addr
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    request_log.append((now_str, ip, now))

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([now_str, ip])

    recent = [r for r in request_log if now - r[2] <= 1]
    rps = len(recent)
    display_log = [(r[0], r[1]) for r in request_log]

    return render_template_string(html_template,
                                  logs=enumerate(display_log, 1),
                                  total=len(display_log),
                                  rps=rps)

@app.route("/reset", methods=["POST"])
def reset():
    global request_log
    request_log = []
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    return redirect("/")

@app.route("/download", methods=["GET"])
def download():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            pass
    return send_file(LOG_FILE, as_attachment=True)

if __name__ == "__main__":
    # Create log file if not exists
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, "w").close()
    app.run(host="0.0.0.0", port=80)
