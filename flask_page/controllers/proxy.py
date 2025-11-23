import requests
from flask import Blueprint, request, Response

proxy_bp = Blueprint("proxy_bp", __name__)

@proxy_bp.route('/proxy')
def proxy():
    target_url = request.args.get('url')

    whitelist_domains = [
        "https://www.celiktafsir.net",
        "https://celiktafsir.net",
    ]

    if target_url not in whitelist_domains:
        return Response("Domain not whitelisted", status=403)

    if not target_url:
        return Response("Missing 'url' parameter", status=400)

    try:
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

    except requests.RequestException as e:
        return Response(f"Error: {e}", status=500)