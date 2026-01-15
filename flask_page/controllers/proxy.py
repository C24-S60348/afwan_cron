import requests
from flask import Blueprint, request, Response

proxy_bp = Blueprint("proxy_bp", __name__)

@proxy_bp.route('/proxy')
def proxy():
    target_url = request.args.get('url')

    # Check if the URL contains 'celiktafsir' to allow it
    if 'celiktafsir' in target_url or 'tafseerliterate.wordpress.com' in target_url:
        pass
    else:
        return Response("Domain not whitelisted", status=403)

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