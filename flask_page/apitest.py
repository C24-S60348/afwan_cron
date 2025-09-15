from flask import Blueprint, jsonify, request

# Test Route
apitest_bp = Blueprint("apitest", __name__, url_prefix="/apitest")

# Simple health check
@apitest_bp.route("/ping")
def ping():
    return jsonify({"message": "pong 🏓", "status": "ok"})

# Echo test (whatever you POST, it gives back)
@apitest_bp.route("/echo", methods=["POST"])
def echo():
    data = request.json
    return jsonify({"you_sent": data, "status": "ok"})

# Example GET with parameter
@apitest_bp.route("/hello/<name>")
def hello(name):
    return jsonify({"message": f"Hello, {name} 👋"})

@apitest_bp.route('', methods=['GET', 'POST', 'OPTIONS'])
def test():
    return jsonify({"message": "Query executed successfully"}), 200
    
