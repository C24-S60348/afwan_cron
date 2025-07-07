#sudo nano /etc/systemd/system/quartapp.service

#edit then
#sudo systemctl daemon-reload
#sudo systemctl restart quartapp
#sudo systemctl status quartapp
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
import requests
import asyncpg
import os
import datetime
import json
import variables
import traceback
import httpx  # async HTTP client
from functools import wraps
from pydantic import BaseModel

class ModelResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str

app = FastAPI(root_path="/api")

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
                    raise HTTPException(status_code=500, detail="Internal server error")
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

@app.get("/")
async def home():
    return {"message": "Hello from FastAPI + Webdock!"}

@app.get(
    "/db-test",
    response_model=ModelResponse,
    responses={
        200: {"description": "Successful Response", "content": {"application/json": {"example": {"db_time": "2025-07-07 21:21:52.703991+00:00"}}}},
        # 500: {"description": "Internal Server Error", "model": ErrorResponse, "content": {"application/json": {"example": {"detail": "Internal server error"}}}},
        # 400: {"description": "Bad Request", "model": ErrorResponse, "content": {"application/json": {"example": {"detail": "Bad request"}}}},
    }
)
@handle_exceptions("db-test")
async def db_test():
    conn = await get_connection()
    result = await conn.fetchval("SELECT NOW()")
    await conn.close()
    return {"db_time": str(result)}

#saje -----
@app.get(
    "/sara",
    response_model=ModelResponse,
    responses={
        200: {"description": "Successful Response", "content": {"application/json": {"example": {"dari afwan": "HAI SARAAAA SAYANGGGGGSS"}}}},
    }
)
@handle_exceptions("sara")
async def sara():
    return {"dari afwan":"HAI SARAAAA SAYANGGGGGSS"}

@app.get(
    "/afwan",
    response_model=ModelResponse,
    responses={
        200: {"description": "Successful Response", "content": {"application/json": {"example": {"dari sara": "HAI AFWAN"}}}},
    }
)
@handle_exceptions("afwan")
async def afwan():
    return {"dari sara":"HAI AFWAN"}

#proxy -----
@app.get('/proxy')
@handle_exceptions("proxy")
async def proxy(request: Request):
    target_url = request.query_params.get('url')

    if not target_url:
        raise HTTPException(status_code=400, detail="Missing 'url' parameter")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(target_url, headers=headers)

    # Create a response with CORS headers
    proxy_response = Response(
        content=response.content,
        status_code=response.status_code,
        media_type=response.headers.get("content-type", "application/octet-stream")
    )
    proxy_response.headers["Access-Control-Allow-Origin"] = "*"
    proxy_response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    proxy_response.headers["Access-Control-Allow-Headers"] = "Content-Type"

    return proxy_response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
