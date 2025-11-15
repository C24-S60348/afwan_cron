import variables
import httpx

def modelsendtelegrammessage(error_message):
    try:
        bot_token = variables.tb_token_server
        chat_id = "-1002864663247"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": f"{error_message}",
            "parse_mode": "HTML"
        }

        with httpx.Client() as client:
            response = client.post(url, data=data)

        if response.status_code != 200:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")