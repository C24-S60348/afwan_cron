from flask import Blueprint, jsonify

# Test Route
apitest_bp = Blueprint('apitest_bp', __name__)

@apitest_bp.route('/api/test', methods=['GET', 'POST', 'OPTIONS'])
def test():
    return jsonify({"message": "Query executed successfully"}), 200
