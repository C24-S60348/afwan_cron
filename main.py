#sudo nano /etc/systemd/system/quartapp.service


from quart import Quart, Response, request
import requests

app = Quart(__name__)

if __name__ == "__main__":
    app.run()

@app.route("/")
async def home():
    return {"message": "Hello from Quart + Webdock!!!"}

@app.route("/sara")
async def sara():
    return {"dari afwan":"HAI SARAAAA SAYANGGGGGSS"}

@app.route('/proxy')
async def proxy():
    target_url = request.args.get('url')

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