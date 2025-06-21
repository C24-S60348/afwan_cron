#sudo nano /etc/systemd/system/quartapp.service

#edit then
#sudo systemctl daemon-reload
#sudo systemctl restart quartapp
#sudo systemctl status quartapp

from quart import Quart, Response, request
import requests
import asyncpg
import os
import datetime
import json
import variables
import traceback

# ENV VARS or hardcoded configs
DB_CONFIG = {
    "user": variables.db_user,
    "password": variables.db_pass,
    "database": variables.db_name,
    "host": variables.db_host,
    "port": variables.db_port,
}

async def send_telegram_error(error_message):
    """Send error message to Telegram group"""
    try:
        bot_token = variables.tb_token_server
        chat_id = "-4885373674"  # Replace with your actual group chat ID
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": f"🚨 ERROR ALERT 🚨\n\n{error_message}",
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

async def get_connection():
    try:
        return await asyncpg.connect(**DB_CONFIG)
    except Exception as e:
        error_msg = f"Database connection error:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        await send_telegram_error(error_msg)
        raise

app = Quart(__name__)

if __name__ == "__main__":
    app.run()

@app.route("/")
async def home():
    try:
        return {"message": "Hello from Quart + Webdock!!!"}
    except Exception as e:
        error_msg = f"Error in home route:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        await send_telegram_error(error_msg)
        return {"error": "Internal server error"}, 500

#db test -----
@app.route("/db-test")
async def db_test():
    try:
        conn = await get_connection()
        result = await conn.fetchval("SELECT NOW()")  # Just fetch current time
        await conn.close()
        return {"db_time": str(result)}
    except Exception as e:
        error_msg = f"Error in db-test route:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        await send_telegram_error(error_msg)
        return {"error": "DB test failed"}, 500


#saje -----
@app.route("/sara")
async def sara():
    try:
        return {"dari afwan":"HAI SARAAAA SAYANGGGGGSS"}
    except Exception as e:
        error_msg = f"Error in sara route:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        await send_telegram_error(error_msg)
        return {"error": "Internal server error"}, 500

@app.route("/afwan")
async def afwan():
    try:
        return {"dari sara":"HAI AFWAN"}
    except Exception as e:
        error_msg = f"Error in afwan route:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        await send_telegram_error(error_msg)
        return {"error": "Internal server error"}, 500

#proxy -----
@app.route('/proxy')
async def proxy():
    try:
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

    except requests.RequestException as e:
        error_msg = f"Proxy request error:\n{str(e)}\n\nTarget URL: {target_url}\n\nTraceback:\n{traceback.format_exc()}"
        await send_telegram_error(error_msg)
        return Response(f"Error: {e}", status=500)
    except Exception as e:
        error_msg = f"Unexpected error in proxy route:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        await send_telegram_error(error_msg)
        return Response(f"Error: {e}", status=500)
