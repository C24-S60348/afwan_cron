#sudo nano /etc/systemd/system/quartapp.service

#edit then
#sudo systemctl daemon-reload
#sudo systemctl restart quartapp
#sudo systemctl status quartapp
from quart import Quart, request, Response
import requests
import asyncpg
import os
import datetime
import json
import variables
import traceback
import httpx  # async HTTP client
from functools import wraps

app = Quart(__name__)

# Error handler ==================================
async def send_telegram_error(error_message):
    try:
        bot_token = variables.tb_token_server
        chat_id = "-4885373674"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": f"🚨 ERROR ALERT 🚨\n\n{error_message}",
            "parse_mode": "HTML"
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)

        if response.status_code != 200:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

# Universal exception handler ====================
def handle_exceptions(route_name="Unknown", type="exception"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_msg = f"Error in {route_name}:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
                await send_telegram_error(error_msg)
                
                if type == "raise":
                    raise  # Re-raise the exception
                else:
                    return {"error": "Internal server error"}, 500
        return wrapper
    return decorator

# DB ==================================
DB_CONFIG = {
    "user": variables.db_user,
    "password": variables.db_pass,
    "database": variables.db_name,
    "host": variables.db_host,
    "port": variables.db_port,
}

@handle_exceptions("database-connection", type="raise")
async def get_connection():
    return await asyncpg.connect(**DB_CONFIG)

@app.route("/")
async def home():
    return {"message": "Hello from Quart + Webdock!"}

@app.route("/db-test")
@handle_exceptions("db-test")
async def db_test():
    conn = await get_connection()
    result = await conn.fetchval("SELECT NOW()")
    await conn.close()
    return {"db_time": str(result)}

#saje -----
@app.route("/sara")
@handle_exceptions("sara")
async def sara():
    return {"dari afwan":"HAI SARAAAA SAYANGGGGGSS"}

@app.route("/afwan")
@handle_exceptions("afwan")
async def afwan():
    return {"dari sara":"HAI AFWAN"}

#proxy -----
@app.route('/proxy')
@handle_exceptions("proxy")
async def proxy():
    target_url = request.args.get('url')

    if not target_url:
        return Response("Missing 'url' parameter", status=400)

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





if __name__ == "__main__":
    app.run()