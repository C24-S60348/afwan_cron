from quart import Blueprint, jsonify, request, Response
import requests
from functools import wraps
from afwan_server_page.handle_exceptions import handle_exceptions

proxy_bp = Blueprint("proxy_bp", __name__)

@proxy_bp.route('/')
@handle_exceptions("proxy")
async def proxy():
    target_url = request.args.get('url')

    if not target_url:
        return {"error": "Missing 'url' parameter"}, 400

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    response = requests.get(target_url, headers=headers)

    # Create a response with CORS headers
    proxy_response = Response(response.content, status=response.status_code)
    proxy_response.headers["Access-Control-Allow-Origin"] = "*"
    proxy_response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    proxy_response.headers["Access-Control-Allow-Headers"] = "Content-Type"

    return proxy_response