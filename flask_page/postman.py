from flask import Blueprint, request, render_template_string
import requests

postman_bp = Blueprint("postman", __name__, url_prefix="/postman")

# Simple HTML template (inline, no need for separate file)
HTML_FORM = """
<!doctype html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Mini Postman 🧪</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 10px;
      padding: 0;
      background: #fafafa;
    }
    h2 { text-align: center; }
    form {
      background: #fff;
      padding: 15px;
      border-radius: 10px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    label {
      font-weight: bold;
      margin-top: 10px;
      display: block;
    }
    input, button, select, textarea {
      width: 100%;
      font-size: 16px;
      padding: 10px;
      margin-top: 5px;
      margin-bottom: 15px;
      border-radius: 8px;
      border: 1px solid #ccc;
      box-sizing: border-box;
    }
    button {
      background: #007BFF;
      color: white;
      border: none;
      cursor: pointer;
      font-size: 18px;
    }
    button:hover {
      background: #0056b3;
    }
    pre {
      background: #f4f4f4;
      padding: 15px;
      border-radius: 10px;
      white-space: pre-wrap;
      word-wrap: break-word;
      font-size: 14px;
      overflow-x: auto;
    }
  </style>
</head>
<body>
  <h2>Mini Postman 🧪</h2>
  <form method="post">
    <label>Method:</label>
    <select name="method">
      <option value="GET">GET</option>
      <option value="POST">POST</option>
    </select>

    <label>URL:</label>
    <input type="text" name="url" value="{{url}}" placeholder="http://127.0.0.1:5000/apitest/ping"/>

    <label>Body (JSON for POST):</label>
    <textarea name="body">{{body}}</textarea>

    <button type="submit">Submit</button>
  </form>

  {% if response %}
  <h3>Response:</h3>
  <pre>{{response}}</pre>
  {% endif %}
</body>
</html>
"""

@postman_bp.route("/", methods=["GET", "POST"])
def index():
    url = ""
    body = ""
    response_text = None

    if request.method == "POST":
        url = request.form.get("url", "")
        method = request.form.get("method", "GET")
        body = request.form.get("body", "")

        try:
            if method == "GET":
                r = requests.get(url)
            else:  # POST
                import json
                data = {}
                if body.strip():
                    data = json.loads(body)
                r = requests.post(url, json=data)

            response_text = r.text
        except Exception as e:
            response_text = f"Error: {e}"

    return render_template_string(HTML_FORM, url=url, body=body, response=response_text)