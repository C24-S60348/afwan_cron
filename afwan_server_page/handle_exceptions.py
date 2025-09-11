from functools import wraps
from quart import jsonify
import variables
import httpx
import traceback

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

async def send_telegram_error(error_message):
    try:
        bot_token = variables.tb_token_server
        chat_id = "-1002864663247"

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